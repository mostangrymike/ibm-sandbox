#!/usr/bin/env python3
"""M178 host equivalence against target-proven M176 on a native fixture."""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
idxsrc = root / "src" / "GITPIDX.C"
treesrc = root / "src" / "GITPTRE.C"
fastsrc = root / "src" / "GITPFST.C"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M176CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 176
assert "if command = 'PACK-TREE' then do" in g
assert "'GITPTRE WALK' oid" in g

for needle in (
    "M176 ROOT TREE",
    "M176 TREE CLOSURE CROSSCHECK PASS",
    "M176 LIVE ROOT TREE CLOSURE TARGET GATE PASS",
):
    assert needle in chk
for forbidden in ("GITFIX", "M15NEW", "ERASE M173NET", "ERASE M174NET"):
    assert forbidden not in chk

text = treesrc.read_text()
for number, line in enumerate(text.splitlines(), 1):
    assert len(line) <= 80, (number, len(line))
assert "#define DEPTHMAX 256UL" in text
assert "#define MEMMAX (64UL*1024UL*1024UL)" in text
assert "mode==160000UL" in text
assert "TREE CLOSURE CHILD MISSING" in text
assert "M176 TREE CLOSURE PASS" in text


def oid(kind, data):
    head = f"{kind} {len(data)}".encode() + b"\0"
    return hashlib.sha1(head + data).hexdigest().upper()


def entry(mode, name, object_id):
    return (
        str(mode).encode() + b" " + name + b"\0"
        + bytes.fromhex(object_id)
    )


def stage_text(objects):
    lines = []
    for number, (kind, typ, data) in enumerate(objects, 1):
        object_id = oid(kind, data)
        lines.append(f"OBJ {number} {typ} {len(data)} {object_id}")
        if not data:
            lines.append("")
        else:
            h = data.hex().upper()
            lines.extend(h[i:i + 64] for i in range(0, len(h), 64))
    return "\n".join(lines) + "\n"


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    idxexe = td / "gitpidx"
    treeexe = td / "gitptre"
    fastexe = td / "gitpfst"
    common = ["gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra", "-Werror"]
    subprocess.run(common + [str(idxsrc), "-o", str(idxexe)], check=True)
    subprocess.run(common + [str(treesrc), "-o", str(treeexe)], check=True)
    subprocess.run(common + [str(fastsrc), "-o", str(fastexe)], check=True)

    a = b"hello\n"
    b = b"world\n"
    link = b"target"
    big = b"0123456789ABCDEF" * 4375
    aoid = oid("blob", a)
    boid = oid("blob", b)
    loid = oid("blob", link)
    bigoid = oid("blob", big)
    subtree = entry(100644, b"sub.txt", boid)
    suboid = oid("tree", subtree)
    gitlink = "11" * 20
    root_tree = b"".join(
        (
            entry(100644, b"a.txt", aoid),
            entry(100644, b"big.bin", bigoid),
            entry(160000, b"ext", gitlink),
            entry(120000, b"link", loid),
            entry(100755, b"run.sh", aoid),
            entry(40000, b"sub", suboid),
        )
    )
    rootoid = oid("tree", root_tree)
    objects = [
        ("blob", 3, a),
        ("blob", 3, b),
        ("blob", 3, link),
        ("blob", 3, big),
        ("tree", 2, subtree),
        ("tree", 2, root_tree),
    ]
    original = stage_text(objects)
    (td / "dd:STGIN").write_text(original)
    built = subprocess.run(
        [str(idxexe), "BUILD"], cwd=td, text=True, capture_output=True
    )
    assert built.returncode == 0, built.stdout + built.stderr
    shutil.copy(td / "dd:IDXOUT", td / "dd:IDXIN")

    walked = subprocess.run(
        [str(treeexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert walked.returncode == 0, walked.stdout + walked.stderr
    assert f"TREE CLOSURE ROOT {rootoid}" in walked.stdout
    assert "TREE CLOSURE TREES 2 BLOBS 4 GITLINKS 1" in walked.stdout
    assert "TREE CLOSURE ENTRIES 7 VERIFIED 6" in walked.stdout
    assert "TREE CLOSURE MAX OBJECT 70000" in walked.stdout
    assert "M176 TREE CLOSURE PASS" in walked.stdout


    faster = subprocess.run(
        [str(fastexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert faster.returncode == 0, faster.stdout + faster.stderr
    for line in (
        f"TREE CLOSURE ROOT {rootoid}",
        "TREE CLOSURE TREES 2 BLOBS 4 GITLINKS 1",
        "TREE CLOSURE ENTRIES 7 VERIFIED 6",
        "TREE CLOSURE MAX OBJECT 70000",
        "TREE CLOSURE INDEX TOTAL 6 UNIQUE 6",
    ):
        assert line in faster.stdout, (line, faster.stdout)
        assert line in walked.stdout, (line, walked.stdout)
    assert "M178 FORWARD SCANS 2 RECORDS " in faster.stdout
    assert " SEEKS 0" in faster.stdout
    assert "M178 AUTHENTICATED BLOBS 4" in faster.stdout
    assert "M178 TREE CLOSURE PASS" in faster.stdout

    bad_oid = subprocess.run(
        [str(fastexe), "WALK", "Q" * 40], cwd=td,
        text=True, capture_output=True,
    )
    assert bad_oid.returncode == 4

    bad_lines = original.splitlines()
    first_body = next(
        i for i, line in enumerate(bad_lines)
        if line.startswith("OBJ 1 ")
    ) + 1
    bad_lines[first_body] = (
        ("0" if bad_lines[first_body][0] != "0" else "1")
        + bad_lines[first_body][1:]
    )
    (td / "dd:STGIN").write_text("\n".join(bad_lines) + "\n")
    bad = subprocess.run(
        [str(treeexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert bad.returncode == 8
    assert "TREE CLOSURE STAGE VERIFY FAIL" in bad.stdout

    fast_bad = subprocess.run(
        [str(fastexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert fast_bad.returncode == 8
    assert "M178 OBJECT SHA1 FAIL" in fast_bad.stdout
    assert "M178 TREE CLOSURE PASS" not in fast_bad.stdout

    (td / "dd:STGIN").write_text(original)

    (td / "dd:IDXOUT").unlink()
    missing_objects = objects[1:]
    (td / "dd:STGIN").write_text(stage_text(missing_objects))
    rebuilt = subprocess.run(
        [str(idxexe), "BUILD"], cwd=td, text=True, capture_output=True
    )
    assert rebuilt.returncode == 0, rebuilt.stdout + rebuilt.stderr
    shutil.copy(td / "dd:IDXOUT", td / "dd:IDXIN")
    missing = subprocess.run(
        [str(treeexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert missing.returncode == 8
    assert "TREE CLOSURE CHILD MISSING" in missing.stdout

    fast_missing = subprocess.run(
        [str(fastexe), "WALK", rootoid],
        cwd=td, text=True, capture_output=True,
    )
    assert fast_missing.returncode == 8
    assert "M178 TREE CLOSURE PASS" not in fast_missing.stdout




text = fastsrc.read_text()
assert max(map(len,text.splitlines())) <= 80
assert "fseek(" not in text
assert "scan(1)" in text and "scan(2)" in text
assert "M178 TREE CLOSURE PASS" in text
for unsafe in ("fopen(\"dd:IDXOUT\"", "fopen(\"dd:OBJOUT\"", "ERASE"):
    assert unsafe not in text

wrapper = (root / "src/GITPFAST.EXEC").read_text()
for required in (
    "address cms",
    "parse upper arg datafm oid extra",
    "M178 FILEMODE INVALID",
    "M178 OID INVALID",
    "'STATE M173NET STAGE' datafm",
    "'STATE M174NET INDEX' datafm",
    "'STATE GITPFST MODULE A'",
    "'PIPE CMS QUERY FILEDEF | STEM f.'",
    "M178 DD ALREADY DEFINED",
    "'PIPE CMS GITPFST WALK' oid '| STEM o.'",
    "'FILEDEF IDXIN CLEAR'",
    "'FILEDEF STGIN CLEAR'",
    "M178 VERIFIED FAST TREE TARGET GATE PASS",
):
    assert required in wrapper, required
assert max(map(len,wrapper.splitlines())) <= 80
assert "do i=1 to o.0" in wrapper
assert "for i=1" not in wrapper
assert wrapper.index("'PIPE CMS QUERY FILEDEF") < wrapper.index(
    "'FILEDEF STGIN DISK M173NET"
)
for forbidden in (
    "ERASE", "FORMAT ", "DIRECTXA", "COPYFILE",
    "GITPIMP IMPORT", "GITPIDX BUILD", "FILEDEF * CLEAR",
    "FILEDEF OBJOUT", "FILEDEF IDXOUT",
):
    assert forbidden not in wrapper, forbidden

print("M178 TWO-PASS FORWARD TREE HOST PARITY PASS")
