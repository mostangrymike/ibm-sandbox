#!/usr/bin/env python3
"""Production C89 large-object CATHEX integration, entirely on host."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
MAX = 65536
BIG = bytes((i * 17 + 13) % 256 for i in range(MAX))
BINARY = bytes(range(256)) + b"\x00"
ABC = b"abc"
OBJECTS = [BIG, b"", BINARY] + [ABC] * 1805


def oid(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii")
                        + b"\x00" + data).hexdigest().upper()


def run(binary, *args, cwd, expected=0):
    result = subprocess.run([str(binary), *args], cwd=cwd,
                            text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError((args, result.returncode,
                              result.stdout[-2400:],
                              result.stderr[-1000:]))
    return result.stdout


def selector(seq, name, digest):
    payload = f"SEL1 {seq} {name} {digest}"
    return f"{payload} {zlib.crc32(payload.encode('ascii')):08X}\n"


def write_stage(path):
    with path.open("w", encoding="ascii", newline="\n") as f:
        for number, data in enumerate(OBJECTS, 1):
            f.write(f"OBJ {number} 3 {len(data)} {oid(data)}\n")
            if not data:
                f.write("\n")
            for pos in range(0, len(data), 32):
                f.write(data[pos:pos + 32].hex().upper() + "\n")


def parse_cathex(text, expected_data, name):
    lines = text.splitlines()
    assert any(line.startswith(f"SELECTED 52 {name} ") for line in lines), lines[:3]
    begin = lines.index("OBJECT DATA BEGIN")
    end = lines.index("OBJECT DATA END")
    assert end > begin, (begin, end)
    assert end == len(lines) - 1, lines[-3:]
    chunks = lines[begin + 1:end]
    for chunk in chunks:
        assert re.fullmatch(r"HEX [0-9A-F]{2,64}", chunk), chunk
        assert len(chunk[4:]) % 2 == 0, chunk
    actual = bytes.fromhex("".join(chunk[4:] for chunk in chunks))
    assert actual == expected_data, (len(actual), len(expected_data))
    assert any(" SIZE " + str(len(expected_data)) + " PREFIX " in line
               for line in lines), lines[:4]
    return actual


def main():
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        idx = cwd / "GITCIDX"
        rec = cwd / "GITREC"
        cc = os.environ.get("CC", "cc")
        for source, target in (("GITCIDX.C", idx), ("GITREC.C", rec)):
            subprocess.run([cc, "-x", "c", "-std=c89", "-O2",
                            "-Wall", "-Wextra", "-Werror", "-o",
                            str(target), str(ROOT / "src" / source)],
                           check=True)
        write_stage(cwd / "dd:STGIN")
        run(idx, "BUILD", cwd=cwd)
        (cwd / "dd:IDXOUT").rename(cwd / "dd:IDXIN")
        run(idx, "SBUILD", cwd=cwd)
        (cwd / "dd:FIDXOUT").rename(cwd / "dd:FIDXIN")
        run(idx, "GENWRITE", cwd=cwd)
        (cwd / "dd:GENOUT").rename(cwd / "dd:GENIN")
        check = run(idx, "GENCHECK", cwd=cwd)
        assert "GENERATION VERIFIED 1808 UNIQUE 4" in check, check
        manifest = (cwd / "dd:GENIN").read_text(encoding="ascii").splitlines()
        digest = manifest[1].split()[1]
        assert re.fullmatch(r"[0-9A-F]{40}", digest)
        for prefix in ("C0", "C1"):
            for typ, source in (("STG", "STGIN"), ("IDX", "IDXIN"),
                                ("SEEK", "FIDXIN"), ("GEN", "GENIN")):
                shutil.copyfile(cwd / ("dd:" + source),
                                cwd / ("dd:" + prefix + typ))
        (cwd / "dd:SEL0").write_text(selector(51, "GITFIX", digest),
                                    encoding="ascii")
        (cwd / "dd:SEL1").write_text(selector(52, "M15NEW", digest),
                                    encoding="ascii")
        for data in (BIG, b"", BINARY, ABC):
            output = run(rec, "CATHEX", "GITFIX", "M15NEW", oid(data),
                         cwd=cwd)
            parse_cathex(output, data, "M15NEW")
        assert len(BIG) == MAX
        assert len(BINARY) == 257 and 0 in BINARY
        print("CATHEX MAX-65536, ZERO-LENGTH, BINARY AND ABC PASSED")

        # A valid newer selector cannot authorize a corrupt newer body.
        new_stage = cwd / "dd:C1STG"
        original = new_stage.read_bytes()
        pos = original.index(BIG[:32].hex().upper().encode("ascii"))
        mutated = bytearray(original)
        mutated[pos] = ord("0") if mutated[pos] != ord("0") else ord("1")
        new_stage.write_bytes(mutated)
        fallback = run(rec, "CATHEX", "GITFIX", "M15NEW", oid(BIG),
                       cwd=cwd)
        assert any(line.startswith("RECOVERED 51 GITFIX ")
                   for line in fallback.splitlines())
        assert "OBJECT DATA BEGIN" in fallback
        assert bytes.fromhex("".join(line[4:] for line
                              in fallback.splitlines()
                              if line.startswith("HEX "))) == BIG
        (cwd / "dd:C0GEN").rename(cwd / "missing-old")
        closed = run(rec, "CATHEX", "GITFIX", "M15NEW", oid(BIG),
                     cwd=cwd, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in closed
        assert "OBJECT DATA BEGIN" not in closed
        (cwd / "missing-old").rename(cwd / "dd:C0GEN")
        new_stage.write_bytes(original)
        recovered = run(rec, "CATHEX", "GITFIX", "M15NEW", oid(BIG),
                        cwd=cwd)
        parse_cathex(recovered, BIG, "M15NEW")
        print("CATHEX CORRUPT-NEW FALLBACK, BOTH INVALID FAIL-CLOSED "
              "AND FULL RESTORATION PASSED")


if __name__ == "__main__":
    main()
