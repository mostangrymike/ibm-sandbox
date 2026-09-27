#!/usr/bin/env python3
"""Host-only two-slot selector prototype. Never promotes CMS data.

The injected check_generation callback MUST do the equivalent of
the complete CMS GENCHECK, not just check for a filename.
"""
import re
import zlib

_RECORD = re.compile(r"SEL1 ([1-9][0-9]*) ([A-Z0-9]{1,8}) ([0-9A-F]{40})")


def encode(sequence, name, digest):
    if not isinstance(sequence, int) or not 0 < sequence <= 4294967295:
        raise ValueError("selector sequence out of range")
    if not re.fullmatch(r"[A-Z0-9]{1,8}", name):
        raise ValueError("invalid CMS generation basename")
    if not re.fullmatch(r"[0-9A-F]{40}", digest):
        raise ValueError("expected canonical 40-character digest")
    payload = f"SEL1 {sequence} {name} {digest}"
    checksum = zlib.crc32(payload.encode("ascii")) & 0xffffffff
    record = f"{payload} {checksum:08X}\n"
    if len(record.rstrip("\n")) > 80:
        raise ValueError("CMS LRECL 80 exceeded")
    return record


def decode(text):
    if not isinstance(text, str) or not text.endswith("\n"):
        return None
    if text.count("\n") != 1:
        return None
    record = text[:-1]
    if len(record) > 80 or not record.isascii():
        return None
    payload, separator, stored = record.rpartition(" ")
    if not separator or not re.fullmatch(r"[0-9A-F]{8}", stored):
        return None
    match = _RECORD.fullmatch(payload)
    if not match:
        return None
    sequence = int(match[1])
    if not 0 < sequence <= 4294967295:
        return None
    checksum = zlib.crc32(payload.encode("ascii")) & 0xffffffff
    if stored != f"{checksum:08X}":
        return None
    return sequence, match[2], match[3]


def choose(slot0, slot1, check_generation):
    """Only choose a completed, independently verified generation.

    A duplicate sequence with conflicting slots is ambiguous and
    fails closed. An unreadable candidate cannot mask an older
    independently valid slot.
    """
    candidates = [item for item in
                  (decode(slot0), decode(slot1)) if item is not None]
    if len(candidates) == 2 and candidates[0][0] == candidates[1][0]:
        if candidates[0] != candidates[1]:
            return None
    for candidate in sorted(set(candidates), reverse=True):
        _, name, digest = candidate
        if check_generation(name, digest) is True:
            return candidate
    return None
