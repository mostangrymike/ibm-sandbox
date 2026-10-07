#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M162CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 162
assert "HISTORYFIRSTPRESENCEFRONTIERDISTANCE-REF-FULL" in g
assert "EXEC GITVREF HISTFPFDIST" in g
assert "address command 'EXEC GITVREF HISTFPFDIST' rest" in g
assert "preparepresencefrontierdistance:" in v
assert "statefirstpresencefrontierdistance:" in v
assert "call preparepresencefrontier" in v
assert "pfdstepdist=pfstart-1" in v
assert "pfddepthdist=sdepth.fn-sdepth.hn" in v
assert "pfdauthspan=sauthorwhen.hn-sauthorwhen.fn" in v
assert "pfdcommspan=scommitwhen.hn-scommitwhen.fn" in v
assert "pfdauthdelta=sauthorwhen.cn-sauthorwhen.fn" in v
assert "pfdcommdelta=scommitwhen.cn-scommitwhen.fn" in v
assert "HFPG P1 S" in v
assert "HFPG P1 E" in v
assert "M162 DISTANCE DIRECT RC0" in c
assert "M162 COMPACT TARGET GATE PASS" in c
assert "gn\=vn | gn<162" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M162CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

author = [1789695393, 1789695390, 1789695386,
          1789695346, 1789695343, 1789695288]
committer = list(author)
depths = [0, 1, 2, 3, 4, 5]
frontier_start_step = 6
complete_step = 5

head_index = 0
frontier_index = frontier_start_step - 1
complete_index = complete_step - 1

step_distance = frontier_start_step - 1
depth_distance = depths[frontier_index] - depths[head_index]
author_span = author[head_index] - author[frontier_index]
committer_span = committer[head_index] - committer[frontier_index]
edge_author = author[complete_index] - author[frontier_index]
edge_committer = committer[complete_index] - committer[frontier_index]

assert (step_distance, depth_distance) == (5, 5)
assert (author_span, committer_span) == (105, 105)
assert (edge_author, edge_committer) == (55, 55)
print("M162 PRESENCE FRONTIER DISTANCE HOST MODEL PASSED")
