#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M163CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 163
assert "HISTORYFIRSTPRESENCEHORIZON-REF-FULL" in g
assert "EXEC GITVREF HISTFPHORIZ" in g
assert "address command 'EXEC GITVREF HISTFPHORIZ' rest" in g
assert "preparepresencehorizon:" in v
assert "statefirstpresencehorizon:" in v
assert "call preparepresencefrontierdistance" in v
assert "pccnodes\=phstep" in v
assert "phstepdist=phstep-1" in v
assert "phdepthdist=phdepth-sdepth.hn" in v
assert "phauthspan=sauthorwhen.hn-sauthorwhen.cn" in v
assert "phcommspan=scommitwhen.hn-scommitwhen.cn" in v
assert "HFPH P1 S" in v
assert "HFPH P1 F" in v
assert "M163 HORIZON DIRECT RC0" in c
assert "M163 COMPACT TARGET GATE PASS" in c
assert "gn\=vn | gn<163" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M163CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

author = [1789695393, 1789695390, 1789695386,
          1789695346, 1789695343, 1789695288]
committer = list(author)
depths = [0, 1, 2, 3, 4, 5]
complete_nodes = 5
frontier_start_step = 6
frontier_edge = 5
frontier_status = "ADDED"

complete_step = complete_nodes
head_index = 0
complete_index = complete_step - 1

step_distance = complete_step - 1
depth_distance = depths[complete_index] - depths[head_index]
author_span = author[head_index] - author[complete_index]
committer_span = committer[head_index] - committer[complete_index]

assert complete_step == 5
assert depths[complete_index] == 4
assert (step_distance, depth_distance) == (4, 4)
assert (author_span, committer_span) == (50, 50)
assert frontier_start_step == complete_step + 1
assert frontier_edge == complete_step
assert frontier_status == "ADDED"
print("M163 COMPLETE PRESENCE HORIZON HOST MODEL PASSED")
