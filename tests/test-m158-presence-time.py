#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
c = (root / "src" / "M158CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 158
assert "HISTORYFIRSTPRESENCETIME-REF-FULL" in g
assert "EXEC GITVREF HISTFPTIME" in g
assert "address command 'EXEC GITVREF HISTFPTIME' rest" in g
assert "preparepresencetime:" in v
assert "statefirstpresencetime:" in v
assert "call preparefirstpresencecurrent" in v
assert "call preparepresenceduration" in v
assert "ptcompletecount\=prruns-truncated" in v
assert "ptincomplete\=truncated" in v
assert "HFPT P1 S" in v
assert "HFPT P1 T" in v
assert "HFPT P1 R" in v
assert "M158 TIME DIRECT RC0" in c
assert "M158 COMPACT TARGET GATE PASS" in c
assert "address command cmd" in c
assert "gn\=vn | gn<158" in c
assert "path='src/GITPBWALK.EXEC'" in c

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "M158CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

states = [0, 1, 1, 1, 1, 0]
author = [1789695393, 1789695390, 1789695386,
          1789695346, 1789695343, 1789695288]
committer = list(author)
status = {1: "DELETED", 5: "ADDED"}
truncated = 1

runs = []
start = 0
for i in range(1, len(states) + 1):
    if i == len(states) or states[i] != states[start]:
        runs.append((start, i - 1))
        start = i

assert runs == [(0, 0), (1, 4), (5, 5)]
ledger = []
present_author = 0
present_committer = 0
absent_author = 0
absent_committer = 0
complete = 0
incomplete = 0

for ri, (first, last) in enumerate(runs):
    state = states[first]
    observed_a = author[first] - author[last]
    observed_c = committer[first] - committer[last]
    if ri == 0:
        kind = "CURRENT"
        is_complete = len(runs) > 1 or not truncated
        auth = observed_a
        comm = observed_c
    elif ri < len(runs) - 1:
        kind = "CLOSED"
        is_complete = True
        end_edge = runs[ri - 1][1] + 1
        begin_edge = runs[ri][1] + 1
        assert status[begin_edge] == ("ADDED" if state else "DELETED")
        assert status[end_edge] == ("DELETED" if state else "ADDED")
        auth = author[end_edge - 1] - author[begin_edge - 1]
        comm = committer[end_edge - 1] - committer[begin_edge - 1]
    else:
        kind = "TRUNCATED" if truncated else "ROOT"
        is_complete = not truncated
        auth = observed_a
        comm = observed_c

    ledger.append((ri + 1, state, kind, int(is_complete), auth, comm))
    if is_complete:
        complete += 1
        if state:
            present_author += auth
            present_committer += comm
        else:
            absent_author += auth
            absent_committer += comm
    else:
        incomplete += 1

assert ledger == [
    (1, 0, "CURRENT", 1, 0, 0),
    (2, 1, "CLOSED", 1, 50, 50),
    (3, 0, "TRUNCATED", 0, 0, 0),
]
assert (complete, incomplete) == (2, 1)
assert (present_author, present_committer) == (50, 50)
assert (absent_author, absent_committer) == (0, 0)
print("M158 PRESENCE TIME HOST MODEL PASSED")
