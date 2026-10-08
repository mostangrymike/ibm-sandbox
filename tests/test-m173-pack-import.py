#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile
import zlib

root = Path(__file__).resolve().parents[1]
src = root / "src" / "GITPIMP.C"
stub = root / "tests" / "m172_gitcapi_host.c"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M173CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 173
assert "if command = 'PACK-IMPORT' then do" in g
assert "'GITPIMP IMPORT'" in g

for needle in (
    "M173 PACK VERIFY CROSSCHECK PASS",
    "M173 IMPORT CROSSCHECK PASS",
    "M173 STAGE READBACK PASS",
    "M173 GENERALIZED OFS PACK IMPORT TARGET GATE PASS",
):
    assert needle in chk

for forbidden in (
    "GITFIX STAGE",
    "M15NEW STAGE",
    "ERASE M171NET",
):
    assert forbidden not in chk

text = src.read_text()
for number, line in enumerate(text.splitlines(), 1):
    assert len(line) <= 80, (number, len(line))
assert "#define OBJMAX 100000UL" in text
assert "#define OBJMAXSZ (16UL*1024UL*1024UL)" in text
assert "#define RESMAX (64UL*1024UL*1024UL)" in text
assert "IMPORT REF DELTA UNSUPPORTED OBJ" in text
assert "M173 PACK IMPORT PASS" in text
assert "M173 STAGE VERIFY PASS" in text


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


def finish(entries):
    payload = (
        b"PACK"
        + (2).to_bytes(4, "big")
        + len(entries).to_bytes(4, "big")
        + b"".join(entries)
    )
    return payload + hashlib.sha1(payload).digest()


def good_pack():
    d1 = bytes((3, 4, 0x90, 3, 1, ord("d")))
    d2 = bytes((4, 5, 0x90, 4, 1, ord("e")))
    one = objhdr(3, 3) + zlib.compress(b"abc")
    start1 = 12
    start2 = start1 + len(one)
    two = (
        objhdr(6, len(d1))
        + ofsenc(start2 - start1)
        + zlib.compress(d1)
    )
    start3 = start2 + len(two)
    three = (
        objhdr(6, len(d2))
        + ofsenc(start3 - start2)
        + zlib.compress(d2)
    )
    return finish((one, two, three))


def ref_pack():
    delta = bytes((3, 4, 0x90, 3, 1, ord("d")))
    one = objhdr(3, 3) + zlib.compress(b"abc")
    base = hashlib.sha1(b"blob 3\\0abc").digest()
    two = objhdr(7, len(delta)) + base + zlib.compress(delta)
    return finish((one, two))


def write_hex(path, data):
    h = data.hex().upper()
    path.write_text(
        "\\n".join(h[i:i + 128] for i in range(0, len(h), 128)) + "\\n"
    )


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    exe = td / "gitpimp"
    subprocess.run(
        [
            "gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra", "-Werror",
            str(src), str(stub), "-lz", "-o", str(exe),
        ],
        check=True,
    )

    pack = good_pack()
    write_hex(td / "dd:PACKIN", pack)
    ok = subprocess.run(
        [str(exe), "IMPORT"], cwd=td, text=True, capture_output=True
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "IMPORT ORDINARY 1 OFS 2 REF 0" in ok.stdout
    assert "IMPORT MAX RESULT 5" in ok.stdout
    assert "IMPORT STAGED 3" in ok.stdout
    assert "M173 PACK IMPORT PASS" in ok.stdout

    stage = (td / "dd:OBJOUT").read_text()
    assert "F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F" in stage
    assert "85DF50785D62D3B05AB03D9CBF7E4A0B49449730" in stage
    assert "6A8165460570531A1247BD99A73B53A5A6E500D5" in stage

    shutil.copy(td / "dd:OBJOUT", td / "dd:STGIN")
    verify = subprocess.run(
        [str(exe), "VERIFY", "3"], cwd=td, text=True, capture_output=True
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert "IMPORT VERIFY OBJECTS 3" in verify.stdout
    assert "M173 STAGE VERIFY PASS" in verify.stdout

    again = subprocess.run(
        [str(exe), "IMPORT"], cwd=td, text=True, capture_output=True
    )
    assert again.returncode == 8
    assert "IMPORT OUTPUT EXISTS" in again.stdout
    assert (td / "dd:OBJOUT").read_text() == stage

    (td / "dd:OBJOUT").unlink()
    write_hex(td / "dd:PACKIN", ref_pack())
    no = subprocess.run(
        [str(exe), "IMPORT"], cwd=td, text=True, capture_output=True
    )
    assert no.returncode == 8
    assert "IMPORT REF DELTA UNSUPPORTED OBJ 2" in no.stdout
    assert not (td / "dd:OBJOUT").exists()

    broken = bytearray(pack)
    broken[-1] ^= 1
    write_hex(td / "dd:PACKIN", bytes(broken))
    no = subprocess.run(
        [str(exe), "IMPORT"], cwd=td, text=True, capture_output=True
    )
    assert no.returncode == 8
    assert "IMPORT PACK SHA1 FAIL" in no.stdout
    assert not (td / "dd:OBJOUT").exists()

print("M173 GENERALIZED OFS PACK IMPORT HOST MODEL PASSED")
