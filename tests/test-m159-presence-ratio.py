#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M159CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 159
assert "HISTORYFIRSTPRESENCERATIO-REF-FULL" in g
assert "EXEC GITVREF HISTFPRATIO" in g
assert "address command 'EXEC GITVREF HISTFPRATIO' rest" in g
assert "preparepresenceratio:" in v
assert "statefirstpresenceratio:" in v
assert "call preparepresencetime" in v
assert "prauthpbp=(ptpresentauth*10000)%prauthtotal" in v
assert "prcommpbp=(ptpresentcomm*10000)%prcommtotal" in v
assert "HFPR P1 S" in v
assert "HFPR P1 A" in v
assert "HFPR P1 C" in v
assert "M159 RATIO DIRECT RC0" in c
assert "M159 COMPACT TARGET GATE PASS" in c
assert "gn\=vn | gn<159" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M159CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

def ratio(present, absent):
    total = present + absent
    if present < 0 or absent < 0 or total <= 0:
        return (0, total, present, absent, -1, -1)
    present_bp = (present * 10000) // total
    absent_bp = 10000 - present_bp
    return (1, total, present, absent, present_bp, absent_bp)

assert ratio(50, 0) == (1, 50, 50, 0, 10000, 0)
assert ratio(30, 70) == (1, 100, 30, 70, 3000, 7000)
assert ratio(1, 2) == (1, 3, 1, 2, 3333, 6667)
assert ratio(0, 0) == (0, 0, 0, 0, -1, -1)
assert ratio(-1, 10) == (0, 9, -1, 10, -1, -1)
print("M159 PRESENCE RATIO HOST MODEL PASSED")
