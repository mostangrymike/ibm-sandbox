#!/usr/bin/env python3
"""Host integration: production GITREC validates Git binary tree records."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def git_oid(typ, data):
    return hashlib.sha1(
        typ.encode("ascii") + b" " + str(len(data)).encode("ascii")
        + b"\x00" + data
    ).hexdigest().upper()


BLOB = b"abc"
BLOB_OID = bytes.fromhex(git_oid("blob", BLOB))
ENTRIES = [
    (b"100644", b"README.md", BLOB_OID),
    (b"100755", b"shell.sh", BLOB_OID),
    (b"120000", b"link", BLOB_OID),
    (b"160000", b"submodule", BLOB_OID),
    (b"40000", b"subdir", bytes.fromhex(git_oid("tree", b""))),
    (b"100644", b"nonascii-\xff", BLOB_OID),
]
TREE = b"".join(mode + b" " + name + b"\x00" + oid
                for mode, name, oid in ENTRIES)
MALFORMED = b"100644 good-name\x00" + BLOB_OID + b"100644 truncated\x00" + b"\x01"
ROOT = (b"tree " + git_oid("tree", TREE).lower().encode("ascii")
        + b"\nauthor A <a@b> 123 +0000\n"
        + b"committer A <a@b> 123 +0000\n\nhello\n")
MERGE = (b"tree " + git_oid("tree", TREE).lower().encode("ascii")
         + b"\nparent " + git_oid("commit", ROOT).lower().encode("ascii")
         + b"\nparent " + b"1"*40
         + b"\nauthor A <a@b> 123 +0000\n"
         + b"committer A <a@b> 123 +0000\n\nmerge\n")
BAD_PARENT = MERGE.replace(b"parent " + b"1"*40,
                           b"parent " + b"Z"*40)
BAD_COMMIT = ROOT.replace(b"committer ", b"othername ")
SAMPLES = [(2, TREE), (2, b""), (2, MALFORMED), (3, BLOB),
           (1, ROOT), (1, MERGE), (1, BAD_PARENT), (1, BAD_COMMIT)]
OBJECTS = SAMPLES + [(3, BLOB)] * (1808 - len(SAMPLES))


def run(exe, *args, cwd, expected=0):
    p = subprocess.run([str(exe), *args], cwd=cwd,
                       capture_output=True, text=True)
    assert p.returncode == expected, (args, p.returncode,
                                      p.stdout[-1500:], p.stderr)
    return p.stdout


def selector(seq, name, digest):
    payload = f"SEL1 {seq} {name} {digest}"
    return f"{payload} {zlib.crc32(payload.encode('ascii')):08X}\n"


def make_stage(path):
    with path.open("w", encoding="ascii", newline="\n") as out:
        for i, (typ, data) in enumerate(OBJECTS, 1):
            object_type = {1: "commit", 2: "tree", 3: "blob"}[typ]
            out.write(f"OBJ {i} {typ} {len(data)} {git_oid(object_type, data)}\n")
            if not data:
                out.write("\n")
            for at in range(0, len(data), 32):
                out.write(data[at:at + 32].hex().upper() + "\n")


def verify_tree(text, expected_name, rows):
    lines = text.splitlines()
    assert f"{expected_name} " in text, lines[:3]
    a = lines.index("TREE DATA BEGIN")
    b = lines.index("TREE DATA END")
    assert a < b and b == len(lines) - 1
    got = lines[a + 1:b]
    assert got[-1] == f"TREE ENTRIES {len(rows)}", got[-1]
    got = got[:-1]
    pos = 0
    for mode, name, raw_oid in rows:
        expected = f"TREE ENTRY MODE {mode.decode()} NAMELEN {len(name)} OID {raw_oid.hex().upper()}"
        assert got[pos] == expected, (got[pos], expected)
        pos += 1
        count = (len(name) + 31) // 32
        chunks = got[pos:pos + count]
        assert all(re.fullmatch(r"TREE NAMEHEX [0-9A-F]{2,64}", x)
                   for x in chunks), chunks
        assert b"".join(bytes.fromhex(x[13:]) for x in chunks) == name
        pos += count
    assert pos == len(got), got[pos:]


def main():
    with tempfile.TemporaryDirectory() as directory:
        d = Path(directory)
        cc = os.environ.get("CC", "cc")
        idx, rec = d / "GITCIDX", d / "GITREC"
        for name, exe in (("GITCIDX", idx), ("GITREC", rec)):
            subprocess.run(
                [cc, "-x", "c", "-std=c89", "-O2", "-Wall",
                 "-Wextra", "-Werror", "-o", str(exe),
                 str(ROOT / "src" / (name + ".C"))], check=True
            )
        make_stage(d / "dd:STGIN")
        run(idx, "BUILD", cwd=d)
        (d / "dd:IDXOUT").rename(d / "dd:IDXIN")
        run(idx, "SBUILD", cwd=d)
        (d / "dd:FIDXOUT").rename(d / "dd:FIDXIN")
        run(idx, "GENWRITE", cwd=d)
        (d / "dd:GENOUT").rename(d / "dd:GENIN")
        assert "GENERATION VERIFIED 1808 UNIQUE 8" in run(idx, "GENCHECK", cwd=d)
        digest = (d / "dd:GENIN").read_text().splitlines()[1].split()[1]
        for prefix in ("C0", "C1"):
            for kind, name in (("STG", "STGIN"), ("IDX", "IDXIN"),
                               ("SEEK", "FIDXIN"), ("GEN", "GENIN")):
                shutil.copyfile(d / ("dd:" + name),
                                d / ("dd:" + prefix + kind))
        (d / "dd:SEL0").write_text(selector(51, "GENOLD", digest))
        (d / "dd:SEL1").write_text(selector(52, "GENNEW", digest))
        tree_oid = git_oid("tree", TREE)
        result = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(result, "SELECTED 52 GENNEW", ENTRIES)
        empty = run(rec, "TREE", "GENOLD", "GENNEW",
                    git_oid("tree", b""), cwd=d)
        verify_tree(empty, "SELECTED 52 GENNEW", [])
        wrong_type = run(rec, "TREE", "GENOLD", "GENNEW",
                         git_oid("blob", BLOB), cwd=d, expected=8)
        assert "OBJECT IS NOT A TREE" in wrong_type
        assert "TREE DATA BEGIN" not in wrong_type
        malformed = run(rec, "TREE", "GENOLD", "GENNEW",
                        git_oid("tree", MALFORMED), cwd=d, expected=8)
        assert "TREE STRUCTURE INVALID" in malformed
        assert "TREE DATA BEGIN" not in malformed

        # M23: selected-generation Git commit header extraction.
        root = run(rec, "COMMIT", "GENOLD", "GENNEW",
                   git_oid("commit", ROOT), cwd=d)
        assert "SELECTED 52 GENNEW" in root
        assert "COMMIT TREE " + git_oid("tree", TREE) in root
        assert "COMMIT PARENTS 0" in root
        assert "COMMIT MESSAGE BYTES 6" in root
        assert root.strip().endswith("COMMIT DATA END")
        merge = run(rec, "COMMIT", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE), cwd=d)
        assert "COMMIT PARENTS 2" in merge
        assert "COMMIT PARENT " + git_oid("commit", ROOT) in merge
        assert "COMMIT PARENT " + "1"*40 in merge
        assert "COMMIT MESSAGE BYTES 6" in merge
        for bad in (BAD_PARENT, BAD_COMMIT):
            broken = run(rec, "COMMIT", "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d, expected=8)
            assert "COMMIT STRUCTURE INVALID" in broken
            assert "COMMIT DATA BEGIN" not in broken
        not_commit = run(rec, "COMMIT", "GENOLD", "GENNEW",
                         tree_oid, cwd=d, expected=8)
        assert "OBJECT IS NOT A COMMIT" in not_commit
        assert "COMMIT DATA BEGIN" not in not_commit

        (d / "dd:C1GEN").rename(d / "held-new")
        commit_recovered = run(rec, "COMMIT", "GENOLD", "GENNEW",
                               git_oid("commit", MERGE), cwd=d)
        assert "RECOVERED 51 GENOLD" in commit_recovered
        assert "COMMIT PARENTS 2" in commit_recovered
        recovered = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(recovered, "RECOVERED 51 GENOLD", ENTRIES)
        (d / "dd:C0GEN").rename(d / "held-old")
        failed = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid,
                     cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in failed
        assert "TREE DATA BEGIN" not in failed
        commit_failed = run(rec, "COMMIT", "GENOLD", "GENNEW",
                            git_oid("commit", ROOT), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in commit_failed
        assert "COMMIT DATA BEGIN" not in commit_failed
        (d / "held-old").rename(d / "dd:C0GEN")
        (d / "held-new").rename(d / "dd:C1GEN")
        restored = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(restored, "SELECTED 52 GENNEW", ENTRIES)
        final_commit = run(rec, "COMMIT", "GENOLD", "GENNEW",
                           git_oid("commit", ROOT), cwd=d)
        assert "SELECTED 52 GENNEW" in final_commit
        assert "COMMIT TREE " + git_oid("tree", TREE) in final_commit
        print("NATIVE C89 TREE BINARY NAMEHEX, EMPTY, MALFORMED, "
              "NON-TREE, COMMIT HEADERS, FALLBACK AND FAIL-CLOSED TESTS PASSED")


if __name__ == "__main__":
    main()
