#!/usr/bin/env python3
from pathlib import Path
import copy
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
wt = (root / "src" / "GITWT.EXEC").read_text()
upd = (root / "src" / "GITUPD.EXEC").read_text()
chk = (root / "src" / "M167CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 167

start = g.index("if command = 'COMMIT-STAGED-REF' then do")
end = g.index("if command = 'CHECKOUT' | command = 'HEAD' then do", start)
bridge = g[start:end]

for needle in (
    "PIPE CMS EXEC GITWT COMMIT",
    "COMMIT-STAGED' &",
    "word(cr.cri,2)='PARENT'",
    "word(cr.cri,2)='COMMIT'",
    "parent\\=expected",
    "EXEC GIT UPDATE-REF",
    "post-CAS ref verification failed; rolling back",
    "post-CAS rollback restored expected old",
    "COMMIT-STAGED-REF CAS PASS",
):
    assert needle in bridge

assert bridge.count("EXEC GIT UPDATE-REF") >= 2
assert "EXECIO * DISKR GITREF2 REPO A 1 (STEM VR. FINIS" in bridge
assert "vr.1='REF2 1'" in bridge
assert "headseen\\=1" in bridge
assert "word(vr.vri,2)=cref" in bridge
assert "translate(word(vr.vri,3))=newcommit" in bridge
assert "PIPE CMS EXEC GIT VERIFY-REF" not in bridge
assert "COMMIT-STAGED-REF REF" in bridge
assert "COMMIT-STAGED-REF OLD" in bridge
assert "COMMIT-STAGED-REF NEW" in bridge
assert "'EXEC GITWT COMMIT' rest" in g
assert "COMMIT-STAGED REFS UNCHANGED" in wt

for needle in (
    "STATE GITREF2 REPO A",
    "ERASE GITREF2 REPO A",
    "REF2 rollback restored prior snapshot",
):
    assert needle in upd

for needle in (
    "refs/heads/m167test",
    "M167 REF2 BASELINE PASS",
    "M167 DISPOSABLE REF INITIALIZED",
    "M167 STAGED CHANGE PASS",
    "M167 INTEGRATED COMMIT RC0",
    "M167 DISPOSABLE REF ADVANCED",
    "M167 NEW COMMIT VERIFIED",
    "M167 HEAD WORKTREE REMAINS STAGED",
    "M167 REF2 BYTE RESTORE PASS",
    "M167 RETAINED INTEGRATED COMMIT",
    "M167 COMMIT TO REF TARGET GATE PASS",
):
    assert needle in chk

assert "EXEC GIT COMMIT-STAGED-REF" in chk
assert "last=post.0" in chk
assert "line=post.last" in chk
assert "line=post.post.0" not in chk
assert "EXEC GIT UPDATE-REF' testref head zeros" in chk
assert "EXEC GIT UPDATE-REF' testref zeros newcommit" in chk

for path in (
    root / "src" / "GIT.EXEC",
    root / "src" / "GITVREF.EXEC",
    root / "src" / "GITWT.EXEC",
    root / "src" / "GITUPD.EXEC",
    root / "src" / "M167CHK.EXEC",
):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

ZERO = "0" * 40
HEAD = "00D8D63229305230C8D37F884CE87F9E1A89468C"
NEW = "22" * 20
REF = "refs/heads/m167test"
baseline = [
    "REF2 1",
    "HEAD refs/heads/main",
    f"REF refs/heads/main {HEAD}",
]

def cas(lines, ref, new, old):
    out = copy.deepcopy(lines)
    current = None
    slot = None
    for index, line in enumerate(out):
        parts = line.split()
        if len(parts) == 3 and parts[0] == "REF" and parts[1] == ref:
            assert current is None
            current = parts[2]
            slot = index
    if old == ZERO:
        if current is not None or new == ZERO:
            return None
        out.append(f"REF {ref} {new}")
        return out
    if current != old:
        return None
    if new == ZERO:
        assert slot is not None
        return out[:slot] + out[slot + 1:]
    out[slot] = f"REF {ref} {new}"
    return out

setup = cas(baseline, REF, HEAD, ZERO)
assert setup is not None
assert setup[:3] == baseline
assert setup[-1] == f"REF {REF} {HEAD}"

# The integrated commit must be parented by the exact expected old ref OID.
def commit_to_ref(lines, parent, expected, new_commit):
    if parent != expected:
        return None
    return cas(lines, REF, new_commit, expected)

advanced = commit_to_ref(setup, HEAD, HEAD, NEW)
assert advanced is not None
assert advanced[:3] == baseline
assert advanced[-1] == f"REF {REF} {NEW}"

assert commit_to_ref(setup, HEAD, "11" * 20, NEW) is None
assert cas(advanced, REF, "33" * 20, HEAD) is None

restored = cas(advanced, REF, ZERO, NEW)
assert restored == baseline

print("M167 INTEGRATED COMMIT TO REF HOST MODEL PASSED")
