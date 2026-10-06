#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M156CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 156
assert "HISTORYFIRSTPRESENCEDURATION-REF-FULL" in g
assert "EXEC GITVREF HISTFPDUR" in g
assert "address command 'EXEC GITVREF HISTFPDUR' rest" in g
assert "preparepresenceduration:" in v
assert "statefirstpresenceduration:" in v
assert "pdauth.ri=sauthorwhen.en-sauthorwhen.bn" in v
assert "pdcomm.ri=scommitwhen.en-scommitwhen.bn" in v
assert "HISTORYFIRSTPRESENCEDURATION PROOF RUN" in v
assert "GITVREF INTERNAL STAMP P2" in v
assert "HFPD P2 S" in v
assert "HFPD P2 R" in v
assert "M156 COMPACT TARGET GATE PASS" in c
assert "gn\\=vn | gn<156" in c
assert "M156 DURATION FAIL PROOF" in c
assert "M156 GITVREF STAMP PASS P2" in c
assert "HFPD P2 S 3 1 1 1 0 3 4 2" in c
assert "HFPD P2 R 2 PRESENT 5 ADDED 1 DELETED 50 50" in c
assert "address command 'PIPE COMMAND' cmd '| STEM out.'" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M156CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

states = [0, 1, 1, 1, 1, 0]
author = [1789695393, 1789695390, 1789695386,
          1789695346, 1789695343, 1789695288]
committer = list(author)
runs = [(0, 0), (1, 4), (5, 5)]
status = {1: "DELETED", 5: "ADDED"}

closed = []
for ri in range(1, len(runs) - 1):
    end_edge = runs[ri - 1][1] + 1
    begin_edge = runs[ri][1] + 1
    begin_node = begin_edge - 1
    end_node = end_edge - 1
    closed.append((ri + 1, states[runs[ri][0]],
                   begin_edge, status[begin_edge],
                   end_edge, status[end_edge],
                   author[end_node] - author[begin_node],
                   committer[end_node] - committer[begin_node]))

assert closed == [(2, 1, 5, "ADDED", 1, "DELETED", 50, 50)]
print("M156 PRESENCE DURATION HOST MODEL PASSED")
