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
EMPTY = b""
BINARY = bytes(range(256)) + b"\x00"
BIG = bytes((n * 17 + 13) % 256 for n in range(65536))
SUBTREE = b"100644 nested.txt\x00" + BLOB_OID
ENTRIES = [
    (b"100644", b"README.md", BLOB_OID),
    (b"100644", b"empty.bin", bytes.fromhex(git_oid("blob", EMPTY))),
    (b"100644", b"bytes.bin", bytes.fromhex(git_oid("blob", BINARY))),
    (b"100644", b"big.bin", bytes.fromhex(git_oid("blob", BIG))),
    (b"100755", b"shell.sh", BLOB_OID),
    (b"120000", b"link", BLOB_OID),
    (b"160000", b"submodule", BLOB_OID),
    (b"40000", b"subdir", bytes.fromhex(git_oid("tree", SUBTREE))),
    (b"100644", b"nonascii-\xff", BLOB_OID),
]
TREE = b"".join(mode + b" " + name + b"\x00" + oid
                for mode, name, oid in ENTRIES)
MALFORMED = b"100644 good-name\x00" + BLOB_OID + b"100644 truncated\x00" + b"\x01"
# Exact historical first-commit root-tree record and README blob.
# This is a pinned immutable Git object, never the current main branch.
HIST_README = (ROOT / "tests/fixtures/first-commit-README.md").read_bytes()
HIST_ENTRIES = [
    (b"100644", b"CHAT_STATE.md",
     bytes.fromhex("6DC1BFE370142E89C2DB239E12BA08A565C2CC62")),
    (b"100644", b"README.md",
     bytes.fromhex("1BA7AE466BB0A16C294D52A8642E527B07D4D1F5")),
    (b"40000", b"docs",
     bytes.fromhex("980E3417BEF3170BF6CCEDFECEB81EDF1C830477")),
    (b"40000", b"src",
     bytes.fromhex("A41B3EA7758F301B7E30BD3CFDF264300C02AE35")),
]
HIST_TREE = b"".join(m + b" " + n + b"\x00" + oid
                     for m, n, oid in HIST_ENTRIES)

FIRST_COMMIT = (b"tree " + git_oid("tree", TREE).lower().encode("ascii")
        + b"\nauthor A <a@b> 123 +0000\n"
        + b"committer A <a@b> 123 +0000\n\nhello\n")
MERGE = (b"tree " + git_oid("tree", TREE).lower().encode("ascii")
         + b"\nparent " + git_oid("commit", FIRST_COMMIT).lower().encode("ascii")
         + b"\nparent " + b"1"*40
         + b"\nauthor A <a@b> 123 +0000\n"
         + b"committer A <a@b> 123 +0000\n\nmerge\n")
REAL_COMMIT = bytes.fromhex(
    "7472656520323034653164363936386662383163333562663833306436336136"
    "313161633634633037323934350A706172656E74203264353033386335353133"
    "31383939376238363534393765303463663463303337646534313335650A6175"
    "74686F72206D6F7374616E6772796D696B65203C6D696B65776F6D6D61636B38"
    "3640676D61696C2E636F6D3E2031373839363935393839202D303530300A636F"
    "6D6D6974746572206D6F7374616E6772796D696B65203C6D696B65776F6D6D61"
    "636B383640676D61696C2E636F6D3E2031373839363935393839202D30353030"
    "0A0A416464204D394A206F626A6563742D6F757470757420696E746567726174"
    "696F6E2072656772657373696F6E"
)
BAD_LINK = (b"tree " + git_oid("blob", BLOB).lower().encode("ascii")
            + b"\nauthor A <a@b> 123 +0000\n"
            + b"committer A <a@b> 123 +0000\n\nlink\n")
BAD_TREE_LINK = (
    b"tree " + git_oid("tree", MALFORMED).lower().encode("ascii")
    + b"\nauthor A <a@b> 123 +0000\n"
    + b"committer A <a@b> 123 +0000\n\ninvalid tree\n")
BAD_PARENT = MERGE.replace(b"parent " + b"1"*40,
                           b"parent " + b"Z"*40)
BAD_COMMIT = FIRST_COMMIT.replace(b"committer ", b"othername ")
SAMPLES = [(2, TREE), (2, b""), (2, MALFORMED),
           (2, SUBTREE), (3, BLOB),
           (1, FIRST_COMMIT), (1, MERGE), (1, BAD_PARENT), (1, BAD_COMMIT),
           (1, REAL_COMMIT), (1, BAD_LINK), (1, BAD_TREE_LINK),
           (3, EMPTY), (3, BINARY), (3, BIG),
           (2, HIST_TREE), (3, HIST_README)]
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


def verify_pathcat(result, data, expected="SELECTED 52 GENNEW"):
    lines = result.splitlines()
    assert expected in result
    assert any("PATH OBJECT TYPE 3 SIZE " + str(len(data)) + " OID "
               + git_oid("blob", data) in line for line in lines)
    start = lines.index("PATH DATA BEGIN")
    end = lines.index("PATH DATA END")
    assert end == len(lines) - 1
    chunks = lines[start + 1:end]
    assert all(re.fullmatch(r"PATH HEX [0-9A-F]{2,64}", x)
               for x in chunks)
    assert all(len(x[9:]) % 2 == 0 for x in chunks)
    assert bytes.fromhex("".join(x[9:] for x in chunks)) == data


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
        assert "GENERATION VERIFIED 1808 UNIQUE 17" in run(idx, "GENCHECK", cwd=d)
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
        # M24: follow an authenticated commit into its root tree.
        lsroot = run(rec, "LSROOT", "GENOLD", "GENNEW",
                     git_oid("commit", FIRST_COMMIT), cwd=d)
        verify_tree(lsroot, "SELECTED 52 GENNEW", ENTRIES)
        assert len(HIST_README) == 567
        assert git_oid("blob", HIST_README) == (
            "1BA7AE466BB0A16C294D52A8642E527B07D4D1F5")
        assert git_oid("tree", HIST_TREE) == (
            "204E1D6968FB81C35BF830D63A611AC64C072945"
        )
        real_root = run(rec, "LSROOT", "GENOLD", "GENNEW",
                        git_oid("commit", REAL_COMMIT), cwd=d)
        verify_tree(real_root, "SELECTED 52 GENNEW", HIST_ENTRIES)
        real_readme = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                          git_oid("commit", REAL_COMMIT),
                          b"README.md".hex().upper(), cwd=d)
        verify_pathcat(real_readme, HIST_README)
        for bad, reason in (
                (BAD_LINK, "OBJECT IS NOT A TREE"),
                (BAD_TREE_LINK, "TREE STRUCTURE INVALID")):
            no_tree = run(rec, "LSROOT", "GENOLD", "GENNEW",
                          git_oid("commit", bad), cwd=d, expected=8)
            assert reason in no_tree
            assert "TREE DATA BEGIN" not in no_tree
            bad_path = run(rec, "PATH", "GENOLD", "GENNEW",
                           git_oid("commit", bad),
                           b"README.md".hex().upper(), cwd=d, expected=8)
            assert "PATH OBJECT TYPE" not in bad_path
        readme = run(rec, "PATH", "GENOLD", "GENNEW",
                     git_oid("commit", FIRST_COMMIT),
                     b"README.md".hex().upper(), cwd=d)
        assert "PATH OBJECT TYPE 3 SIZE 3 OID " + git_oid("blob", BLOB) in readme
        nested = run(rec, "PATH", "GENOLD", "GENNEW",
                     git_oid("commit", FIRST_COMMIT),
                     b"subdir/nested.txt".hex().upper(), cwd=d)
        assert "PATH OBJECT TYPE 3 SIZE 3 OID " + git_oid("blob", BLOB) in nested
        subtree = run(rec, "PATH", "GENOLD", "GENNEW",
                      git_oid("commit", FIRST_COMMIT),
                      b"subdir".hex().upper(), cwd=d)
        assert "PATH OBJECT TYPE 2 SIZE " + str(len(SUBTREE)) in subtree
        gitlink = run(rec, "PATH", "GENOLD", "GENNEW",
                      git_oid("commit", FIRST_COMMIT),
                      b"submodule".hex().upper(), cwd=d)
        assert "PATH GITLINK (EXTERNAL COMMIT)" in gitlink
        assert "PATH OID " + BLOB_OID.hex().upper() in gitlink

        # M25: full raw blob bytes only after the linked path is verified.
        for filename, data in ((b"README.md", BLOB),
                               (b"subdir/nested.txt", BLOB),
                               (b"empty.bin", EMPTY),
                               (b"bytes.bin", BINARY),
                               (b"big.bin", BIG)):
            full = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                       git_oid("commit", FIRST_COMMIT),
                       filename.hex().upper(), cwd=d)
            verify_pathcat(full, data)
        assert len(BIG) == 65536
        for filename, expected in ((b"subdir", 8),
                                   (b"submodule", 8),
                                   (b"missing", 4),
                                   (b"README.md/child", 8)):
            output = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         filename.hex().upper(), cwd=d, expected=expected)
            assert "PATH DATA BEGIN" not in output
            assert "PATH HEX " not in output
        malformed_cat = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT), "612F2F62",
                            cwd=d, expected=4)
        assert "PATH DATA BEGIN" not in malformed_cat
        for bad in (b"missing", b"README.md/child", b"subdir/missing"):
            failure = run(rec, "PATH", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          bad.hex().upper(), cwd=d,
                          expected=8 if bad == b"README.md/child" else 4)
            assert "PATH OBJECT TYPE" not in failure
        for bad in ("", "2", "00", "2F61", "612F", "612F2F62", "GG"):
            failure = run(rec, "PATH", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT), bad,
                          cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in failure

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
        # Exact 270-byte real first-commit body captured from CMS CATHEX.
        # This fixture catches host-only parsing assumptions before target
        # compilation and protects the established canonical first OID.
        assert len(REAL_COMMIT) == 270
        assert git_oid("commit", REAL_COMMIT) == (
            "00D8D63229305230C8D37F884CE87F9E1A89468C"
        )
        real = run(rec, "COMMIT", "GENOLD", "GENNEW",
                   git_oid("commit", REAL_COMMIT), cwd=d)
        assert "COMMIT TREE 204E1D6968FB81C35BF830D63A611AC64C072945" in real
        assert "COMMIT PARENT 2D5038C551318997B865497E04CF4C037DE4135E" in real
        assert "COMMIT PARENTS 1" in real
        assert "COMMIT MESSAGE BYTES " + str(
            len(REAL_COMMIT.split(b"\n\n", 1)[1])
        ) in real

        root = run(rec, "COMMIT", "GENOLD", "GENNEW",
                   git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "SELECTED 52 GENNEW" in root
        assert "COMMIT TREE " + git_oid("tree", TREE) in root
        assert "COMMIT PARENTS 0" in root
        assert "COMMIT MESSAGE BYTES 6" in root
        assert root.strip().endswith("COMMIT DATA END")
        merge = run(rec, "COMMIT", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE), cwd=d)
        assert "COMMIT PARENTS 2" in merge
        assert "COMMIT PARENT " + git_oid("commit", FIRST_COMMIT) in merge
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
        lsroot_recovered = run(rec, "LSROOT", "GENOLD", "GENNEW",
                               git_oid("commit", FIRST_COMMIT), cwd=d)
        verify_tree(lsroot_recovered, "RECOVERED 51 GENOLD", ENTRIES)
        path_recovered = run(rec, "PATH", "GENOLD", "GENNEW",
                             git_oid("commit", FIRST_COMMIT),
                             b"README.md".hex().upper(), cwd=d)
        assert "RECOVERED 51 GENOLD" in path_recovered
        assert "PATH OBJECT TYPE 3 SIZE 3" in path_recovered
        full_recovered = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                             git_oid("commit", FIRST_COMMIT),
                             b"bytes.bin".hex().upper(), cwd=d)
        verify_pathcat(full_recovered, BINARY, "RECOVERED 51 GENOLD")
        assert "COMMIT PARENTS 2" in commit_recovered
        recovered = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(recovered, "RECOVERED 51 GENOLD", ENTRIES)
        (d / "dd:C0GEN").rename(d / "held-old")
        failed = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid,
                     cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in failed
        assert "TREE DATA BEGIN" not in failed
        commit_failed = run(rec, "COMMIT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in commit_failed
        assert "COMMIT DATA BEGIN" not in commit_failed
        lsroot_failed = run(rec, "LSROOT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT),
                            cwd=d, expected=8)
        assert "TREE DATA BEGIN" not in lsroot_failed
        path_failed = run(rec, "PATH", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          b"README.md".hex().upper(), cwd=d, expected=8)
        assert "PATH OBJECT TYPE" not in path_failed
        full_failed = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          b"README.md".hex().upper(), cwd=d, expected=8)
        assert "PATH DATA BEGIN" not in full_failed
        (d / "held-old").rename(d / "dd:C0GEN")
        (d / "held-new").rename(d / "dd:C1GEN")
        restored = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(restored, "SELECTED 52 GENNEW", ENTRIES)
        final_commit = run(rec, "COMMIT", "GENOLD", "GENNEW",
                           git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "SELECTED 52 GENNEW" in final_commit
        assert "COMMIT TREE " + git_oid("tree", TREE) in final_commit
        final_path = run(rec, "PATH", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         b"subdir/nested.txt".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in final_path
        assert "PATH OBJECT TYPE 3 SIZE 3" in final_path
        restored_full = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT),
                            b"big.bin".hex().upper(), cwd=d)
        verify_pathcat(restored_full, BIG)
        print("NATIVE C89 TREE BINARY NAMEHEX, EMPTY, MALFORMED, "
              "NON-TREE, COMMIT, LSROOT, NESTED PATH AND FAIL-CLOSED TESTS PASSED")


if __name__ == "__main__":
    main()
