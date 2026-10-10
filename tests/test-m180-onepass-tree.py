#!/usr/bin/env python3
"""M180 isolated one-pass native closure: strict C89 and fail-closed."""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
native = root / "src" / "GITPONE.C"
wrapper = root / "src" / "GITPONCE.EXEC"
base = root / "src" / "GITPFST.C"
index = root / "src" / "GITPIDX.C"

def oid(typ, body):
    header = (typ + " " + str(len(body))).encode() + b"\0"
    return hashlib.sha1(header + body).hexdigest().upper()

def edge(mode, name, child):
    return (str(mode).encode() + b" " + name + b"\0"
            + bytes.fromhex(child))

def stage(objects):
    lines = []
    for number, (typ, code, body) in enumerate(objects, 1):
        lines.append("OBJ %d %d %d %s" %
                     (number, code, len(body), oid(typ, body)))
        hexd = body.hex().upper()
        if not hexd:
            lines.append("")
        else:
            lines += [hexd[i:i + 64] for i in range(0, len(hexd), 64)]
    return "\n".join(lines) + "\n", len(lines)

def run(exe, folder, tree):
    return subprocess.run([str(exe), "WALK", tree], cwd=folder,
                          capture_output=True, text=True)

for path in (native, wrapper):
    assert max(map(len, path.read_text().splitlines())) <= 80, path
code = native.read_text()
rexx = wrapper.read_text()
for required in ("M180 STAGE LINES", "M180 TREE CLOSURE PASS",
                 "scan()", "sha_blobs++", "M180 SHA1 BLOBS TOTAL"):
    assert required in code, required
assert "fseek(" not in code
for forbidden in ("ERASE", "FORMAT ", "DIRECTXA", "GITPIMP IMPORT",
                  "GITPIDX BUILD", "FILEDEF * CLEAR", "FILEDEF OBJOUT",
                  "FILEDEF IDXOUT"):
    assert forbidden not in rexx
for required in ("'STATE GITPONE MODULE A'",
                 "'PIPE CMS GITPONE WALK' oid '| STEM o.'",
                 "'PIPE CMS QUERY FILEDEF | STEM f.'",
                 "'FILEDEF IDXIN CLEAR'", "'FILEDEF STGIN CLEAR'",
                 "M180 VERIFIED FAST TREE TARGET GATE PASS"):
    assert required in rexx, required

with tempfile.TemporaryDirectory() as temp:
    folder = Path(temp)
    binaries = {}
    for name, source in (("old", base), ("new", native), ("idx", index)):
        binaries[name] = folder / name
        cmd = ["gcc", "-x", "c", "-std=c89", "-Wall", "-Wextra",
               "-Werror", str(source), "-o", str(binaries[name])]
        subprocess.run(cmd, check=True)
    big = b"ABCdef0123456789" * 4700
    small = b"tiny"
    other = b"not reached"
    sub = edge(100644, b"part.bin", oid("blob", big))
    rootbody = (edge(40000, b"dir", oid("tree", sub))
                + edge(100644, b"test.txt", oid("blob", small))
                + edge(160000, b"external", "11" * 20))
    unused = edge(100644, b"no", oid("blob", other))
    objects = [("blob", 3, big), ("blob", 3, small),
               ("blob", 3, other), ("tree", 2, sub),
               ("tree", 2, unused), ("tree", 2, rootbody)]
    txt, count = stage(objects)
    (folder / "dd:STGIN").write_text(txt)
    built = subprocess.run([str(binaries["idx"]), "BUILD"], cwd=folder,
                           text=True, capture_output=True)
    assert built.returncode == 0, built.stdout + built.stderr
    shutil.copy(folder / "dd:IDXOUT", folder / "dd:IDXIN")
    originalidx = (folder / "dd:IDXIN").read_text()
    rootoid = oid("tree", rootbody)
    old = run(binaries["old"], folder, rootoid)
    new = run(binaries["new"], folder, rootoid)
    assert old.returncode == 0, old.stdout + old.stderr
    assert new.returncode == 0, new.stdout + new.stderr
    for expected in (f"TREE CLOSURE ROOT {rootoid}",
                     "TREE CLOSURE TREES 2 BLOBS 2 GITLINKS 1",
                     "TREE CLOSURE ENTRIES 4 VERIFIED 4",
                     "TREE CLOSURE MAX OBJECT 75200",
                     "TREE CLOSURE INDEX TOTAL 6 UNIQUE 6"):
        assert expected in old.stdout and expected in new.stdout, expected
    assert f"M180 STAGE LINES {count}" in new.stdout
    assert "M180 FORWARD SCANS 1 RECORDS 6 SEEKS 0" in new.stdout
    assert "M180 AUTHENTICATED BLOBS 2" in new.stdout
    assert "M180 SHA1 BLOBS TOTAL 3" in new.stdout
    assert "M180 TREE CLOSURE PASS" in new.stdout
    assert (folder / "dd:STGIN").read_text() == txt
    assert (folder / "dd:IDXIN").read_text() == originalidx

    malformed = run(binaries["new"], folder, "Z" * 40)
    assert malformed.returncode == 4

    # Authentication failure in reached blob (byte remains valid hex).
    lines = txt.splitlines()
    lines[1] = ("0" if lines[1][0] != "0" else "1") + lines[1][1:]
    (folder / "dd:STGIN").write_text("\n".join(lines) + "\n")
    invalid = run(binaries["new"], folder, rootoid)
    assert invalid.returncode == 8
    assert "M180 OBJECT SHA1 FAIL" in invalid.stdout
    assert "M180 TREE CLOSURE PASS" not in invalid.stdout

    # Stage structure error in indexed but unreachable blob fails closed.
    lines = txt.splitlines()
    unrelated_header = next(i for i, line in enumerate(lines)
                            if line.startswith("OBJ 3 "))
    lines[unrelated_header + 1] = "G" + lines[unrelated_header + 1][1:]
    (folder / "dd:STGIN").write_text("\n".join(lines) + "\n")
    invalid = run(binaries["new"], folder, rootoid)
    assert invalid.returncode == 8
    assert "M180 TREE CLOSURE PASS" not in invalid.stdout

    # An unreachable indexed blob is SHA-authenticated as well.
    lines = txt.splitlines()
    other_pos = next(i for i, line in enumerate(lines)
                     if line.startswith("OBJ 3 ")) + 1
    lines[other_pos] = ("0" if lines[other_pos][0] != "0" else "1") + lines[other_pos][1:]
    (folder / "dd:STGIN").write_text("\n".join(lines) + "\n")
    unrelated = run(binaries["new"], folder, rootoid)
    assert unrelated.returncode == 8
    assert "M180 OBJECT SHA1 FAIL" in unrelated.stdout
    assert "M180 TREE CLOSURE PASS" not in unrelated.stdout

    (folder / "dd:STGIN").write_text(txt)
    (folder / "dd:IDXIN").write_text(
        "\n".join(originalidx.splitlines()[:-1]) + "\n")
    truncated = run(binaries["new"], folder, rootoid)
    assert truncated.returncode == 8
    assert "M180 TREE CLOSURE PASS" not in truncated.stdout

    # Duplicate stage object: the index chooses one canonical blob
    # occurrence; closure must count repeated references only once.
    (folder / "dd:IDXOUT").unlink()
    shared = b"identical"
    emptytree = b""
    duplicate_root = (
        edge(40000, b"empty", oid("tree", emptytree))
        + edge(100644, b"first", oid("blob", shared))
        + edge(100644, b"second", oid("blob", shared))
    )
    dup_oid = oid("tree", duplicate_root)
    duplicate_objects = [
        ("blob", 3, shared),
        ("blob", 3, shared),
        ("tree", 2, emptytree),
        ("tree", 2, duplicate_root),
    ]
    dup_text, dup_lines = stage(duplicate_objects)
    (folder / "dd:STGIN").write_text(dup_text)
    rebuilt = subprocess.run(
        [str(binaries["idx"]), "BUILD"], cwd=folder,
        text=True, capture_output=True
    )
    assert rebuilt.returncode == 0, rebuilt.stdout + rebuilt.stderr
    assert "INDEX WRITTEN 4 UNIQUE 3" in rebuilt.stdout
    shutil.copy(folder / "dd:IDXOUT", folder / "dd:IDXIN")
    before_index = (folder / "dd:IDXIN").read_text()
    older = run(binaries["old"], folder, dup_oid)
    newer = run(binaries["new"], folder, dup_oid)
    assert older.returncode == 0, older.stdout + older.stderr
    assert newer.returncode == 0, newer.stdout + newer.stderr
    for marker in (
        "TREE CLOSURE TREES 2 BLOBS 1 GITLINKS 0",
        "TREE CLOSURE ENTRIES 3 VERIFIED 3",
        "TREE CLOSURE INDEX TOTAL 4 UNIQUE 3",
    ):
        assert marker in older.stdout and marker in newer.stdout
    assert "M180 AUTHENTICATED BLOBS 1" in newer.stdout
    assert "M180 SHA1 BLOBS TOTAL 1" in newer.stdout
    assert f"M180 STAGE LINES {dup_lines}" in newer.stdout
    assert "M180 FORWARD SCANS 1 RECORDS 4 SEEKS 0" in newer.stdout
    assert (folder / "dd:STGIN").read_text() == dup_text
    assert (folder / "dd:IDXIN").read_text() == before_index

print("M180 ONE PASS TREE HOST PARITY PASS")
