#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
src = root / "src" / "GITPIDX.C"

g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
chk = (root / "src" / "M174CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 174
assert "command = 'PACK-INDEX' then do" in g
assert "'GITPIDX BUILD'" in g
assert "'GITPIDX BUILD CHECKED'" in g
assert "'PIPE CMS GITPIDX BUILD CHECKED | STEM b.'" in chk
assert "'FILEDEF IDXOUT DISK' idx" in chk
assert "'FILEDEF IDXOUT CLEAR'" in chk
assert "'PIPE CMS GIT PACK-INDEX' idx" not in chk

for needle in (
    "M174 INDEX BUILD CROSSCHECK PASS",
    "M174 INDEX CHECK CROSSCHECK PASS",
    "M174 INDEX AUDIT CROSSCHECK PASS",
    "M174 TIP COMMIT LOOKUP PASS",
    "M174 GENERALIZED STAGE INDEX TARGET GATE PASS",
):
    assert needle in chk

for forbidden in (
    "GITFIX",
    "M15NEW",
    "ERASE M173NET",
):
    assert forbidden not in chk

text = src.read_text()
for number, line in enumerate(text.splitlines(), 1):
    assert len(line) <= 80, (number, len(line))
assert "#define OBJMAX 100000UL" in text
assert "#define OBJMAXSZ (16UL*1024UL*1024UL)" in text
assert "PIDX1" in text and "PEND1" in text
assert "INDEX OUTPUT EXISTS" in text
assert "M174 INDEX AUDIT PASS" in text


def blob_oid(data):
    head = f"blob {len(data)}".encode() + b"\0"
    return hashlib.sha1(head + data).hexdigest().upper()


def stage_text(objects):
    lines = []
    for number, data in enumerate(objects, 1):
        oid = blob_oid(data)
        lines.append(f"OBJ {number} 3 {len(data)} {oid}")
        if not data:
            lines.append("")
        else:
            h = data.hex().upper()
            lines.extend(h[i:i + 64] for i in range(0, len(h), 64))
    return "\n".join(lines) + "\n"


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    exe = td / "gitpidx"
    subprocess.run(
        [
            "gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra", "-Werror",
            str(src), "-o", str(exe),
        ],
        check=True,
    )

    big = b"0123456789ABCDEF" * 4375
    assert len(big) == 70000
    objects = [b"abc", b"abcd", b"abc", big]
    original_stage = stage_text(objects)
    (td / "dd:STGIN").write_text(original_stage)

    built = subprocess.run(
        [str(exe), "BUILD"], cwd=td, text=True, capture_output=True
    )
    assert built.returncode == 0, built.stdout + built.stderr
    assert "INDEX WRITTEN 4 UNIQUE 3" in built.stdout
    assert "M174 INDEX BUILD PASS" in built.stdout
    index = (td / "dd:IDXOUT").read_text()
    assert "PIDX1 4 3" in index
    assert "PEND1 4 3" in index
    assert blob_oid(big) in index

    shutil.copy(td / "dd:IDXOUT", td / "dd:IDXIN")
    checked = subprocess.run(
        [str(exe), "CHECK"], cwd=td, text=True, capture_output=True
    )
    assert checked.returncode == 0
    assert "INDEX VERIFIED 4 UNIQUE 3" in checked.stdout

    audited = subprocess.run(
        [str(exe), "AUDIT"], cwd=td, text=True, capture_output=True
    )
    assert audited.returncode == 0, audited.stdout + audited.stderr
    assert "INDEX AUDIT VERIFIED 4 UNIQUE 3" in audited.stdout
    assert "M174 INDEX AUDIT PASS" in audited.stdout

    got = subprocess.run(
        [str(exe), "GET", blob_oid(b"abc")],
        cwd=td, text=True, capture_output=True,
    )
    assert got.returncode == 0
    assert "OBJ 1 TYPE 3 SIZE 3" in got.stdout
    assert "M174 INDEX GET PASS" in got.stdout

    large = subprocess.run(
        [str(exe), "GET", blob_oid(big)],
        cwd=td, text=True, capture_output=True,
    )
    assert large.returncode == 0
    assert "TYPE 3 SIZE 70000" in large.stdout

    again = subprocess.run(
        [str(exe), "BUILD"], cwd=td, text=True, capture_output=True
    )
    assert again.returncode == 8
    assert "INDEX OUTPUT EXISTS" in again.stdout
    assert (td / "dd:IDXOUT").read_text() == index

    (td / "dd:IDXOUT").unlink()
    checked = subprocess.run(
        [str(exe), "BUILD", "CHECKED"], cwd=td,
        text=True, capture_output=True
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert (td / "dd:IDXOUT").read_text() == index

    lines = original_stage.splitlines()
    lines[1] = ("0" if lines[1][0] != "0" else "1") + lines[1][1:]
    (td / "dd:STGIN").write_text("\n".join(lines) + "\n")
    bad = subprocess.run(
        [str(exe), "AUDIT"], cwd=td, text=True, capture_output=True
    )
    assert bad.returncode == 8
    assert "INDEX AUDIT FAIL" in bad.stdout
    (td / "dd:STGIN").write_text(original_stage)

    saved = (td / "dd:IDXIN").read_text()
    (td / "dd:IDXIN").write_text(
        "\n".join(saved.splitlines()[:-1]) + "\n"
    )
    truncated = subprocess.run(
        [str(exe), "CHECK"], cwd=td, text=True, capture_output=True
    )
    assert truncated.returncode == 8
    assert "INDEX RECORD FAIL" in truncated.stdout

print("M174 GENERALIZED STAGE INDEX HOST MODEL PASSED")
