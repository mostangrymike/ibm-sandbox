#!/usr/bin/env python3
from pathlib import Path
import hashlib
import subprocess
import tempfile
import zlib

root = Path(__file__).resolve().parents[1]
src = root / "src" / "GITPCENS.C"
stub = root / "tests" / "m172_gitcapi_host.c"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M172CHK.EXEC").read_text()

import re
gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 172
assert "if command = 'PACK-CENSUS' then do" in g
assert "'GITPCENS'" in g

for needle in (
    "M172 PACK VERIFY CROSSCHECK PASS",
    "M172 CENSUS CROSSCHECK PASS",
    "M172 RETAINED PACK UNCHANGED",
    "M172 GENERALIZED PACK CENSUS TARGET GATE PASS",
):
    assert needle in chk

for forbidden in (
    "ERASE M171NET",
    "GITFIX STAGE",
    "M15NEW STAGE",
):
    assert forbidden not in chk

for number, line in enumerate(src.read_text().splitlines(), 1):
    assert len(line) <= 80, (number, len(line))
text = src.read_text()
assert 'pack[0]!=0x50' in text
assert 'memcmp(pack,"PACK",4)' not in text
assert "#define PACKMAX (16UL*1024UL*1024UL)" in text
assert "#define OBJMAX 100000UL" in text
assert "CENSUS ORDINARY %lu OFS %lu REF %lu" in text
assert "M172 PACK CENSUS PASS" in text


def objhdr(kind, size):
    first = (kind << 4) | (size & 15)
    size >>= 4
    out = bytearray()
    while size:
        out.append(first | 0x80)
        first = size & 0x7F
        size >>= 7
    out.append(first)
    return bytes(out)


def ofsenc(distance):
    assert distance > 0
    out = bytearray([distance & 0x7F])
    distance >>= 7
    while distance:
        distance -= 1
        out.insert(0, 0x80 | (distance & 0x7F))
        distance >>= 7
    return bytes(out)


def make_pack():
    delta1 = bytes((3, 4, 0x90, 3, 1, ord("d")))
    delta2 = bytes((4, 5, 0x90, 4, 1, ord("e")))
    one = objhdr(3, 3) + zlib.compress(b"abc")
    start1 = 12
    start2 = start1 + len(one)
    two = objhdr(6, len(delta1))
    two += ofsenc(start2 - start1) + zlib.compress(delta1)
    base = hashlib.sha1(b"blob 4\0abcd").digest()
    three = objhdr(7, len(delta2)) + base + zlib.compress(delta2)
    payload = (
        b"PACK" + (2).to_bytes(4, "big") + (3).to_bytes(4, "big")
        + one + two + three
    )
    return payload + hashlib.sha1(payload).digest()


def write_hex(path, data):
    h = data.hex().upper()
    path.write_text(
        "\n".join(h[i:i + 128] for i in range(0, len(h), 128)) + "\n"
    )


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    exe = td / "gitpcens"
    subprocess.run(
        [
            "gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra", "-Werror",
            str(src), str(stub), "-lz", "-o", str(exe),
        ],
        check=True,
    )

    good = make_pack()
    write_hex(td / "dd:PACKIN", good)
    ok = subprocess.run(
        [str(exe)], cwd=td, text=True, capture_output=True
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert f"CENSUS PACK BYTES {len(good)} VERSION 2 OBJECTS 3" in ok.stdout
    assert "CENSUS ORDINARY 1 OFS 1 REF 1" in ok.stdout
    assert "M172 PACK CENSUS PASS" in ok.stdout

    core = good[:-20] + b"\x00"
    bad = core + hashlib.sha1(core).digest()
    write_hex(td / "dd:PACKIN", bad)
    no = subprocess.run(
        [str(exe)], cwd=td, text=True, capture_output=True
    )
    assert no.returncode == 8
    assert "CENSUS END MISMATCH" in no.stdout

    broken = bytearray(good)
    broken[0] ^= 1
    write_hex(td / "dd:PACKIN", bytes(broken))
    no = subprocess.run(
        [str(exe)], cwd=td, text=True, capture_output=True
    )
    assert no.returncode == 8
    assert "CENSUS PACK SIGNATURE FAIL" in no.stdout

print("M172 GENERALIZED PACK CENSUS HOST MODEL PASSED")
