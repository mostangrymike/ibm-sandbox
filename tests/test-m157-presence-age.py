#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M157CHK.EXEC").read_text()

assert "GIT EXEC LEVEL M157" in g
assert "GITVREF EXEC LEVEL M157" in v
assert "HISTORYFIRSTPRESENCEAGE-REF-FULL" in g
assert "EXEC GITVREF HISTFPAGE" in g
assert "statefirstpresenceage:" in v
assert "call preparefirstpresencecurrent" in v
assert "HISTORYFIRSTPRESENCEAGE AUTHOR SECONDS" in v
assert "HISTORYFIRSTPRESENCEAGE COMMITTER SECONDS" in v
assert "M157 COMPACT TARGET GATE PASS" in c

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
