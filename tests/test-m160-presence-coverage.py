#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M160CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 160
assert "HISTORYFIRSTPRESENCECOVERAGE-REF-FULL" in g
assert "EXEC GITVREF HISTFPCOV" in g
assert "address command 'EXEC GITVREF HISTFPCOV' rest" in g
assert "preparepresencecoverage:" in v
assert "statefirstpresencecoverage:" in v
assert "call preparepresencetime" in v
assert "pccnodes+pcinodes\=fpcount" in v
assert "pcrunbp=(ptcompletecount*10000)%prruns" in v
assert "pcnodebp=(pccnodes*10000)%fpcount" in v
assert "HFPC P1 S" in v
assert "HFPC P1 B" in v
assert "M160 COVERAGE DIRECT RC0" in c
assert "M160 COMPACT TARGET GATE PASS" in c
assert "gn\=vn | gn<160" in c
assert "address command cmd" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M160CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

complete_runs = 2
incomplete_runs = 1
complete_nodes = 5
incomplete_nodes = 1
runs = complete_runs + incomplete_runs
nodes = complete_nodes + incomplete_nodes

run_complete_bp = complete_runs * 10000 // runs
run_incomplete_bp = 10000 - run_complete_bp
node_complete_bp = complete_nodes * 10000 // nodes
node_incomplete_bp = 10000 - node_complete_bp

assert (runs, complete_runs, incomplete_runs) == (3, 2, 1)
assert (nodes, complete_nodes, incomplete_nodes) == (6, 5, 1)
assert (run_complete_bp, run_incomplete_bp) == (6666, 3334)
assert (node_complete_bp, node_incomplete_bp) == (8333, 1667)
assert run_complete_bp + run_incomplete_bp == 10000
assert node_complete_bp + node_incomplete_bp == 10000
print("M160 PRESENCE COVERAGE HOST MODEL PASSED")
