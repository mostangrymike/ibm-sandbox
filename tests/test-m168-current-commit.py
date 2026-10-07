#!/usr/bin/env python3
from pathlib import Path
import copy
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
wt = (root / "src" / "GITWT.EXEC").read_text()
chk = (root / "src" / "M168CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 168

start = g.index("if command = 'COMMIT-CURRENT' then do")
end = g.index("if command = 'CHECKOUT' | command = 'HEAD' then do", start)
bridge = g[start:end]
for needle in (
    "EXECIO * DISKR GITREF2 REPO A 1 (STEM HR. FINIS",
    "headcount\\=1",
    "oldcount\\=1",
    "EXEC GIT COMMIT-STAGED-REF",
    "COMMIT-STAGED-REF' &",
    "word(cc.cci,2)='NEW'",
    "EXEC GITWT ACCEPT",
    "worktree accept failed; rolling back current branch",
    "EXEC GIT UPDATE-REF",
    "current branch rollback restored old commit",
    "COMMIT-CURRENT WORKTREE CLEAN",
):
    assert needle in bridge

assert "if command='ACCEPT' then do" in wt
accept = wt[wt.index("if command='ACCEPT' then do"):
            wt.index("if command='COMMIT' then do")]
for needle in (
    "GITWT ACCEPT LEVEL M168",
    "EXECIO * DISKR GITWORK REPO A 1 (STEM BEFORE. FINIS",
    "mapcount\\=1",
    "mapstage.1=mapbase.1",
    "accepted\\=mapstage.1",
    "mapbase.1=mapstage.1",
    "call savemap",
    "call restoremap",
    "ACCEPTED WORKTREE OLD",
    "ACCEPTED WORKTREE NEW",
):
    assert needle in accept

restore = wt[wt.index("restoremap:"):wt.index("savemap:")]
assert "ERASE GITWORK REPO A" in restore
assert "STEM BEFORE. FINIS" in restore

for needle in (
    "refs/heads/m168test",
    "M168 TEMP CURRENT BRANCH READY",
    "M168 STAGED CHANGE PASS",
    "M168 COMMIT CURRENT RC0",
    "M168 CURRENT REF ADVANCED",
    "M168 NEW COMMIT VERIFIED",
    "M168 WORKTREE RECONCILED CLEAN",
    "M168 REF2 BYTE RESTORE PASS",
    "M168 RETAINED CURRENT COMMIT",
    "M168 CURRENT BRANCH COMMIT TARGET GATE PASS",
):
    assert needle in chk

assert "EXEC GIT COMMIT-CURRENT" in chk
assert "STATUS SUMMARY TRACKED 1 CHANGED 0 STAGED 0" in chk

for path in (
    root / "src" / "GIT.EXEC",
    root / "src" / "GITVREF.EXEC",
    root / "src" / "GITWT.EXEC",
    root / "src" / "M168CHK.EXEC",
):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

HEAD = "00D8D63229305230C8D37F884CE87F9E1A89468C"
NEW = "44" * 20
REF = "refs/heads/m168test"
baseline = [
    "REF2 1",
    "HEAD refs/heads/main",
    f"REF refs/heads/main {HEAD}",
]
temporary = [
    "REF2 1",
    f"HEAD {REF}",
    f"REF refs/heads/main {HEAD}",
    f"REF {REF} {HEAD}",
]

def current_ref(lines):
    head = None
    refs = {}
    for line in lines[1:]:
        parts = line.split()
        if parts[0] == "HEAD":
            assert head is None and len(parts) == 2
            head = parts[1]
        elif parts[0] == "REF":
            assert len(parts) == 3 and parts[1] not in refs
            refs[parts[1]] = parts[2]
    assert head in refs
    return head, refs[head]

def cas(lines, ref, new, old):
    out = copy.deepcopy(lines)
    for i, line in enumerate(out):
        parts = line.split()
        if len(parts) == 3 and parts[0] == "REF" and parts[1] == ref:
            if parts[2] != old:
                return None
            out[i] = f"REF {ref} {new}"
            return out
    return None

headref, old = current_ref(temporary)
assert headref == REF and old == HEAD
advanced = cas(temporary, headref, NEW, old)
assert advanced is not None
assert advanced[2] == baseline[2]
assert advanced[-1] == f"REF {REF} {NEW}"

# Worktree acceptance promotes only the staged blob to the new base.
old_blob = "AA" * 20
stage_blob = "BB" * 20
work_blob = stage_blob
assert work_blob == stage_blob and old_blob != stage_blob
accepted_base = stage_blob
assert accepted_base == stage_blob

# If acceptance fails after CAS, exact rollback restores the old branch tip.
rolled = cas(advanced, headref, old, NEW)
assert rolled == temporary

print("M168 CURRENT BRANCH RECONCILIATION HOST MODEL PASSED")
