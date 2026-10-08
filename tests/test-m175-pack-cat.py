#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
idxsrc = root / "src" / "GITPIDX.C"
catsrc = root / "src" / "GITPCAT.C"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M175CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 175
assert "if command = 'PACK-CAT' then do" in g
assert "'GITPCAT CAT' oid" in g

for needle in (
    "M175 MAIN COMMIT VERIFIED",
    "M175 ROOT TREE VERIFIED",
    "M175 PARENT VERIFIED",
    "M175 LIVE COMMIT TREE CLOSURE PASS",
    "M175 VERIFIED RANDOM ACCESS TARGET GATE PASS",
):
    assert needle in chk

for forbidden in ("GITFIX", "M15NEW", "ERASE M173NET", "ERASE M174NET"):
    assert forbidden not in chk

text = catsrc.read_text()
for number, line in enumerate(text.splitlines(), 1):
    assert len(line) <= 80, (number, len(line))
assert 'memcmp(p+start,"tree "' not in text
assert 'memcmp(p+start,"parent "' not in text
assert "0x74,0x72,0x65,0x65,0x20" in text
assert "0x70,0x61,0x72,0x65,0x6e,0x74,0x20" in text
assert "M175 PACK CAT PASS" in text
assert "M175 PACK INFO PASS" in text


def oid(kind, data):
    head = f"{kind} {len(data)}".encode() + b"\0"
    return hashlib.sha1(head + data).hexdigest().upper()


def stage_text(objects):
    lines = []
    for number, (kind, typ, data) in enumerate(objects, 1):
        obj = oid(kind, data)
        lines.append(f"OBJ {number} {typ} {len(data)} {obj}")
        if not data:
            lines.append("")
        else:
            h = data.hex().upper()
            lines.extend(h[i:i + 64] for i in range(0, len(h), 64))
    return "\n".join(lines) + "\n"


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    idxexe = td / "gitpidx"
    catexe = td / "gitpcat"
    common = ["gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra", "-Werror"]
    subprocess.run(common + [str(idxsrc), "-o", str(idxexe)], check=True)
    subprocess.run(common + [str(catsrc), "-o", str(catexe)], check=True)

    tree = b""
    tree_oid = oid("tree", tree)
    parent = (
        f"tree {tree_oid}\n"
        "author A <a@b> 1 +0000\n"
        "committer A <a@b> 1 +0000\n"
        "\nparent\n"
    ).encode()
    parent_oid = oid("commit", parent)
    child = (
        f"tree {tree_oid}\n"
        f"parent {parent_oid}\n"
        "author B <b@c> 2 +0000\n"
        "committer B <b@c> 2 +0000\n"
        "\nchild\n"
    ).encode()
    child_oid = oid("commit", child)
    big = b"0123456789ABCDEF" * 4375
    objects = [
        ("tree", 2, tree),
        ("commit", 1, parent),
        ("commit", 1, child),
        ("blob", 3, big),
    ]
    (td / "dd:STGIN").write_text(stage_text(objects))
    built = subprocess.run(
        [str(idxexe), "BUILD"], cwd=td, text=True, capture_output=True
    )
    assert built.returncode == 0, built.stdout + built.stderr
    shutil.copy(td / "dd:IDXOUT", td / "dd:IDXIN")

    info = subprocess.run(
        [str(catexe), "INFO", child_oid],
        cwd=td, text=True, capture_output=True,
    )
    assert info.returncode == 0, info.stdout + info.stderr
    assert f"PACKOBJ OID {child_oid}" in info.stdout
    assert "TYPE 1" in info.stdout
    assert f"PACKOBJ COMMIT TREE {tree_oid}" in info.stdout
    assert f"PACKOBJ COMMIT PARENT {parent_oid}" in info.stdout
    assert "PACKOBJ COMMIT PARENTS 1" in info.stdout
    assert "PACKOBJ HEX " not in info.stdout
    assert "M175 PACK INFO PASS" in info.stdout

    tree_info = subprocess.run(
        [str(catexe), "INFO", tree_oid],
        cwd=td, text=True, capture_output=True,
    )
    assert tree_info.returncode == 0
    assert "TYPE 2 SIZE 0" in tree_info.stdout

    parent_info = subprocess.run(
        [str(catexe), "INFO", parent_oid],
        cwd=td, text=True, capture_output=True,
    )
    assert parent_info.returncode == 0
    assert "TYPE 1" in parent_info.stdout
    assert "PACKOBJ COMMIT PARENTS 0" in parent_info.stdout

    cat = subprocess.run(
        [str(catexe), "CAT", child_oid],
        cwd=td, text=True, capture_output=True,
    )
    assert cat.returncode == 0
    body_hex = child.hex().upper()
    for i in range(0, len(body_hex), 64):
        assert f"PACKOBJ HEX {body_hex[i:i + 64]}" in cat.stdout
    assert "M175 PACK CAT PASS" in cat.stdout

    large = subprocess.run(
        [str(catexe), "INFO", oid("blob", big)],
        cwd=td, text=True, capture_output=True,
    )
    assert large.returncode == 0
    assert "TYPE 3 SIZE 70000" in large.stdout

    bad_stage = (td / "dd:STGIN").read_text().splitlines()
    child_header = next(
        i for i, line in enumerate(bad_stage)
        if line.startswith("OBJ 3 ")
    )
    bad_stage[child_header + 1] = (
        ("0" if bad_stage[child_header + 1][0] != "0" else "1")
        + bad_stage[child_header + 1][1:]
    )
    (td / "dd:STGIN").write_text("\n".join(bad_stage) + "\n")
    bad = subprocess.run(
        [str(catexe), "INFO", child_oid],
        cwd=td, text=True, capture_output=True,
    )
    assert bad.returncode == 8
    assert "PACKOBJ STAGE VERIFY FAIL" in bad.stdout

print("M175 VERIFIED RANDOM ACCESS HOST MODEL PASSED")
