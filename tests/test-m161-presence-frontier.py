#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M161CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 161
assert "HISTORYFIRSTPRESENCEFRONTIER-REF-FULL" in g
assert "EXEC GITVREF HISTFPFRONT" in g
assert "address command 'EXEC GITVREF HISTFPFRONT' rest" in g
assert "preparepresencefrontier:" in v
assert "statefirstpresencefrontier:" in v
assert "call preparepresencecoverage" in v
assert "pfincrun=prruns" in v
assert "pfcompletestep=pfstart-1" in v
assert "pffrontieredge=pfcompletestep" in v
assert "pffrontierstatus=fdstatus.fe" in v
assert "HFPF P1 S" in v
assert "HFPF P1 B" in v
assert "M161 FRONTIER DIRECT RC0" in c
assert "M161 COMPACT TARGET GATE PASS" in c
assert "gn\=vn | gn<161" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M161CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

states = [0, 1, 1, 1, 1, 0]
runs = [(0, 0), (1, 4), (5, 5)]
depths = [0, 1, 2, 3, 4, 5]
status = {1: "DELETED", 5: "ADDED"}
truncated = 1

assert truncated == 1
incomplete_run = len(runs)
first, last = runs[-1]
state = states[first]
kind = "TRUNCATED"
nodes = last - first + 1
start_step = first + 1
end_step = last + 1
complete_step = start_step - 1
frontier_edge = complete_step

assert (incomplete_run, state, kind, nodes,
        start_step, end_step) == (3, 0, "TRUNCATED", 1, 6, 6)
assert depths[first] == 5
assert depths[complete_step - 1] == 4
assert frontier_edge == 5
assert status[frontier_edge] == "ADDED"
print("M161 PRESENCE FRONTIER HOST MODEL PASSED")
