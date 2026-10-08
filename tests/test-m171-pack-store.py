#!/usr/bin/env python3
from pathlib import Path
import hashlib
import subprocess
import tempfile
import re

root = Path(__file__).resolve().parents[1]
post = (root / "src" / "GITPOST.EXEC").read_text()
check = root / "src" / "GITPCHK.C"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M171CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 171
assert "EXEC GITPOST STORE" in g
assert "M171 FETCH STORE PASS" in post
for needle in (
    "M171 META CROSSCHECK PASS",
    "M171 PACK CROSSCHECK PASS",
    "M171 RETAINED PACK",
    "M171 GENERALIZED PACK STORE TARGET GATE PASS",
):
    assert needle in chk

for path in (root / "src" / "GITPOST.EXEC", check):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

for forbidden in (
    "GITPBUF PACK",
    "GITPMETA PACK",
    "M11BODY DATA",
    "M12BODY DATA",
):
    assert forbidden not in post

for needle in (
    "wantoid=translate(oid,'abcdef','ABCDEF')",
    "storemode=cmd='STORE'",
    "GITPOST STORE bridge port host repo oid fn",
    "storefn 'PACK A'",
    "storefn 'META A'",
    "call storefeed ppiece",
    "call storefinal",
    "call storeclean",
    "sbuf=sbuf||shex",
    "srecs=64",
):
    assert needle in post

src = check.read_text()
for needle in (
    'fopen(argc==2?argv[1]:"dd:PACKIN","r")',
    "PACK VERIFY SIGNATURE FAIL",
    "PACK VERIFY SHA1 FAIL",
    "PACK VERIFY VERSION",
    "M171 PACK VERIFY PASS",
):
    assert needle in src

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    exe = td / "gitpchk"
    subprocess.run(
        ["gcc", "-std=c89", "-Wall", "-Wextra", "-Werror",
         str(check), "-o", str(exe)],
        check=True,
    )

    header = b"PACK" + (2).to_bytes(4, "big") + (7665).to_bytes(4, "big")
    body = bytes((i * 37 + 11) & 0xFF for i in range(200000))
    pre = header + body
    pack = pre + hashlib.sha1(pre).digest()

    good = td / "good.packhex"
    hexed = pack.hex().upper()
    good.write_text("\n".join(
        hexed[i:i+128] for i in range(0, len(hexed), 128)
    ) + "\n")
    ok = subprocess.run([str(exe), str(good)],
                        text=True, capture_output=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert f"PACK VERIFY BYTES {len(pack)}" in ok.stdout
    assert "PACK VERIFY VERSION 2 OBJECTS 7665" in ok.stdout
    assert "M171 PACK VERIFY PASS" in ok.stdout

    corrupt = bytearray(pack)
    corrupt[-1] ^= 1
    bad = td / "bad.packhex"
    hx = bytes(corrupt).hex().upper()
    bad.write_text("\n".join(
        hx[i:i+128] for i in range(0, len(hx), 128)
    ) + "\n")
    no = subprocess.run([str(exe), str(bad)],
                        text=True, capture_output=True)
    assert no.returncode == 8
    assert "PACK VERIFY SHA1 FAIL" in no.stdout

    malformed = td / "malformed.packhex"
    malformed.write_text("5041434B0Z\n")
    no = subprocess.run([str(exe), str(malformed)],
                        text=True, capture_output=True)
    assert no.returncode == 8

print("M171 GENERALIZED PACK STORE/VERIFY HOST MODEL PASSED")
