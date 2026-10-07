#!/usr/bin/env python3
from pathlib import Path
import copy
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
upd = (root / "src" / "GITUPD.EXEC").read_text()
chk = (root / "src" / "M166CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm
assert gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 166
assert "if command = 'UPDATE-REF' then do" in g
assert "'EXEC GITUPD' rest" in g

for needle in (
    "STATE GITREF2 REPO A",
    "DISKR GITREF2 REPO A",
    "DISKW GITREF2 REPO A",
    "rr.1\\='REF2 1'",
    "wr.1='REF2 1'",
    "wr.2='HEAD' headref",
    "oldoid=zeros",
    "newoid=zeros",
    "GITUPD: stale ref",
    "GITUPD: refusing to delete symbolic HEAD target",
    "address command 'EXEC GIT VERIFY-OBJECT' oid",
    "GITUPD: branch target is not a COMMIT object",
    "bak.0=rr.0",
    "call restore",
    "GITUPD: REF2 rollback restored prior snapshot",
):
    assert needle in upd

assert "GITREFS REPO" not in upd
assert "BRANCH' name" not in upd
assert "expected-old-oid" in upd
assert "if newoid=zeros & oldoid=zeros then do" in upd
assert "ni=i+1" in upd
assert "refname.i=refname.ni" in upd
assert "refoid.i=refoid.ni" in upd

for needle in (
    "D6FB8432692CF8EFBDC2DDA354425D8DCDC3A008",
    "refs/heads/m166test",
    "M166 CREATE CAS PASS",
    "M166 STALE CAS REJECTED RC8",
    "M166 STALE CAS LEFT REF2 UNCHANGED",
    "M166 DELETE CAS PASS",
    "M166 REF2 BYTE RESTORE PASS",
    "M166 RETAINED COMMIT STILL PRESENT",
    "M166 REF CAS TARGET GATE PASS",
):
    assert needle in chk

assert "refs/heads/main" not in re.sub(
    r"testref='refs/heads/m166test'", "", chk
)
assert "EXEC GIT UPDATE-REF' testref" in chk
assert "DISKW GITREF2 REPO A" in chk

for path in (
    root / "src" / "GIT.EXEC",
    root / "src" / "GITVREF.EXEC",
    root / "src" / "GITUPD.EXEC",
    root / "src" / "M166CHK.EXEC",
):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

ZERO = "0" * 40
MAIN = "00D8D63229305230C8D37F884CE87F9E1A89468C"
CAND = "D6FB8432692CF8EFBDC2DDA354425D8DCDC3A008"
TEST = "refs/heads/m166test"

original = [
    "REF2 1",
    "HEAD refs/heads/main",
    f"REF refs/heads/main {MAIN}",
]

def cas(lines, ref, new, old):
    out = copy.deepcopy(lines)
    refs = {}
    for line in out[2:]:
        tag, name, oid = line.split()
        assert tag == "REF"
        assert name not in refs
        refs[name] = oid
    current = refs.get(ref)
    if old == ZERO:
        if current is not None or new == ZERO:
            return None
        out.append(f"REF {ref} {new}")
        return out
    if current != old:
        return None
    if new == ZERO:
        head = out[1].split()[1]
        if ref == head:
            return None
        return [line for line in out
                if not line.startswith(f"REF {ref} ")]
    return [
        f"REF {ref} {new}" if line.startswith(f"REF {ref} ") else line
        for line in out
    ]

created = cas(original, TEST, CAND, ZERO)
assert created is not None
assert created[:3] == original
assert created[-1] == f"REF {TEST} {CAND}"

stale = cas(created, TEST, CAND, "1" * 40)
assert stale is None
assert created[:3] == original

restored = cas(created, TEST, ZERO, CAND)
assert restored == original
assert cas(original, "refs/heads/main", ZERO, MAIN) is None

print("M166 REF2 COMPARE-AND-SWAP HOST MODEL PASSED")
