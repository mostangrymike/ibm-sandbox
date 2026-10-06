#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M157CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 157
assert "HISTORYFIRSTPRESENCEAGE-REF-FULL" in g
assert "EXEC GITVREF HISTFPAGE" in g
assert "address command 'EXEC GITVREF HISTFPAGE' rest" in g
assert "statefirstpresenceage:" in v
assert "call preparefirstpresencecurrent" in v
assert "HISTORYFIRSTPRESENCEAGE AUTHOR SECONDS" in v
assert "HISTORYFIRSTPRESENCEAGE COMMITTER SECONDS" in v
assert "HISTORYFIRSTPRESENCEAGE PROOF" in v
assert "GITVREF INTERNAL STAMP P2" in v
assert "HFPA P2 S" in v
assert "HFPA P2 R" in v
assert "M157 COMPACT TARGET GATE PASS" in c
assert "gn\\=vn | gn<157" in c
assert "M157 GITVREF STAMP PASS P2" in c
assert "M157 AGE DIRECT RC0" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M157CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

states = [0, 0, 0, 0, 0, 0, 1]
author = [1789695661, 1789695576, 1789695516,
          1789695510, 1789695462, 1789695393, 1789695390]
committer = list(author)

end = 0
while end + 1 < len(states) and states[end + 1] == states[0]:
    end += 1
assert end == 5
begin_edge = end + 1
assert begin_edge == 6
assert states[end] == 0 and states[end + 1] == 1
assert author[0] - author[end] == 268
assert committer[0] - committer[end] == 268
print("M157 CURRENT PRESENCE AGE HOST MODEL PASSED")
