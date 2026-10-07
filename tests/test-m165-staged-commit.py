#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
wt = (root / "src" / "GITWT.EXEC").read_text()
chk = (root / "src" / "M165CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1) == "165"
assert "'EXEC GITWT COMMIT' rest" in g
assert "WRITE-TREE-HEXFILE" in g
assert "call hashstored 'TREE',datahex" in g
assert "call storeobject treeoid,'TREE',datahex" in g

start = wt.index("if command='COMMIT' then do")
end = wt.index("say 'GITWT: unknown command'", start)
commit = wt[start:end]
for needle in (
    "GITWT COMMIT LEVEL M165",
    "mapcount\\=1",
    "mapstage.1=mapbase.1",
    "work\\=mapstage.1",
    "call readrefs",
    "call resolve 'HEAD'",
    "call bindnative",
    "call rootfor parent",
    "call splitpath mappath.1",
    "childoid.pcnt\\=mapbase.1",
    "call rewritetree",
    "'EXEC GIT IMPORT-OBJECT' parent",
    "'GIT COMMIT-TREE'",
    "'-T' stamp '-Z' zone '-M' message",
    "'EXEC GIT VERIFY-OBJECT' commit",
    "COMMIT-STAGED REFS UNCHANGED",
):
    assert needle in commit
assert "UPDATE-REF" not in commit
assert "GITUPD" not in commit

for needle in (
    "GITREC SHOWFULL GITFIX M15NEW",
    "SHOW FULL ROOT CLOSURE VERIFIED",
    "GITREC TREE GITFIX M15NEW",
    "TREE DATA BEGIN",
    "TREE NAMEHEX",
    "TREE DATA END",
    "WRITE-TREE-HEXFILE GITTREE REPO A",
):
    assert needle in wt

for protected in ("GITFIX STAGE", "GITFIX INDEX", "GITFIX SEEK",
                  "GITFIX GEN", "M15NEW STAGE", "M15NEW INDEX",
                  "M15NEW SEEK", "M15NEW GEN"):
    assert f"DISKW {protected}" not in wt
    assert f"ERASE {protected}" not in wt

for needle in (
    "M165 STAGED CHANGE PASS",
    "M165 COMMIT DIRECT RC0",
    "M165 VERIFIED REFS UNCHANGED",
    "M165 LOOSE COMMIT CANDIDATE RETAINED FOR REF CAS",
    "M165 STAGED COMMIT TARGET GATE PASS",
):
    assert needle in chk

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "GITWT.EXEC",
             root / "src" / "M165CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

def oid(kind, data):
    head = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(head + data).hexdigest().upper()

def entry(mode, name, object_id):
    return (mode.encode("ascii") + b" " + name.encode("ascii") + b"\0" +
            bytes.fromhex(object_id))

base_blob = oid("blob", b"old")
stage_blob = oid("blob", b"new")
other_blob = oid("blob", b"other")
readme_blob = oid("blob", b"readme")

src_base_raw = (
    entry("100644", "GIT.EXEC", base_blob) +
    entry("100644", "OTHER", other_blob)
)
src_base = oid("tree", src_base_raw)
root_base_raw = (
    entry("100644", "README.md", readme_blob) +
    entry("40000", "src", src_base)
)
root_base = oid("tree", root_base_raw)

src_new_raw = (
    entry("100644", "GIT.EXEC", stage_blob) +
    entry("100644", "OTHER", other_blob)
)
src_new = oid("tree", src_new_raw)
root_new_raw = (
    entry("100644", "README.md", readme_blob) +
    entry("40000", "src", src_new)
)
root_new = oid("tree", root_new_raw)

assert src_new != src_base
assert root_new != root_base
assert other_blob in src_new_raw.hex().upper()
assert readme_blob in root_new_raw.hex().upper()

parent = "11" * 20
body = (
    f"tree {root_new.lower()}\n"
    f"parent {parent.lower()}\n"
    "author CMS Git <cms@example.invalid> 1 +0000\n"
    "committer CMS Git <cms@example.invalid> 1 +0000\n"
    "\nM165 test\n"
).encode("ascii")
commit_oid = oid("commit", body)
assert len(commit_oid) == 40
assert commit_oid != parent
print("M165 STAGED COMMIT HOST MODEL PASSED")
