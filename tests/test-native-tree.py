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
GRANDCHILD = (b"tree " + git_oid("tree", TREE).lower().encode("ascii")
              + b"\nparent " + git_oid("commit", MERGE).lower().encode("ascii")
              + b"\nauthor A <a@b> 123 +0000\n"
              + b"committer A <a@b> 123 +0000\n\nthird\n")
SECOND_PARENT = FIRST_COMMIT.replace(b"hello\n", b"other\n")
MERGE2 = MERGE.replace(
    b"parent " + b"1"*40,
    b"parent " + git_oid("commit", SECOND_PARENT).lower().encode("ascii"))
# M32: all parent commits may be valid while their trees are not.
MISSING_ROOT_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"), b"2"*40, 1)
MISSING_ROOT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", MISSING_ROOT_COMMIT).lower().encode("ascii"))
BLOB_ROOT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", BAD_LINK).lower().encode("ascii"))
MALFORMED_ROOT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", BAD_TREE_LINK).lower().encode("ascii"))
# M34: valid root syntax with invalid referenced entry objects.
MISSING_ENTRY_TREE = TREE.replace(BLOB_OID, b"3"*20, 1)
WRONG_ENTRY_TREE = TREE.replace(
    BLOB_OID, bytes.fromhex(git_oid("tree", TREE)), 1)
INVALID_SUBTREE_TREE = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", MALFORMED)), 1)
MISSING_ENTRY_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", MISSING_ENTRY_TREE).lower().encode("ascii"))
WRONG_ENTRY_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", WRONG_ENTRY_TREE).lower().encode("ascii"))
INVALID_SUBTREE_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", INVALID_SUBTREE_TREE).lower().encode("ascii"))
MISSING_ENTRY_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", MISSING_ENTRY_COMMIT).lower().encode("ascii"))
# M35: structurally valid subtrees with invalid *nested* Git links.
NEST_MISSING = b"100644 nested.txt\x00" + b"\x04"*20
NEST_WRONG = (b"100644 nested.txt\x00"
              + bytes.fromhex(git_oid("tree", TREE)))
NEST_MISSING_TREE = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", NEST_MISSING)), 1)
NEST_WRONG_TREE = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", NEST_WRONG)), 1)
NEST_MISSING_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", NEST_MISSING_TREE).lower().encode("ascii"))
NEST_WRONG_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", NEST_WRONG_TREE).lower().encode("ascii"))
NEST_PARENT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", NEST_MISSING_COMMIT).lower().encode("ascii"))
# M36: the *second* nested level is corrupt, but shallower walks pass.
DEEP_GOOD = (b"40000 inner\x00"
             + bytes.fromhex(git_oid("tree", SUBTREE)))
DEEP_MISSING = (b"40000 inner\x00"
                + bytes.fromhex(git_oid("tree", NEST_MISSING)))
DEEP_WRONG = (b"40000 inner\x00"
              + bytes.fromhex(git_oid("tree", NEST_WRONG)))
DEEP_ROOT_GOOD = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", DEEP_GOOD)), 1)
DEEP_ROOT_MISSING = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", DEEP_MISSING)), 1)
DEEP_ROOT_WRONG = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", DEEP_WRONG)), 1)
DEEP_COMMIT_GOOD = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", DEEP_ROOT_GOOD).lower().encode("ascii"))
DEEP_COMMIT_MISSING = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", DEEP_ROOT_MISSING).lower().encode("ascii"))
DEEP_COMMIT_WRONG = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", DEEP_ROOT_WRONG).lower().encode("ascii"))
DEEP_PARENT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", DEEP_COMMIT_MISSING).lower().encode("ascii"))
LARGE_ROOT = b"".join(
    b"100644 f" + ("%03d" % i).encode("ascii") + b"\x00" + BLOB_OID
    for i in range(257))
LARGE_ROOT_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", LARGE_ROOT).lower().encode("ascii"))
# M43: external Gitlinks are still counted for bounded tree walks.
GITLINK_256 = b"".join(
    b"160000 ext" + ("%03d" % i).encode("ascii") + b"\x00" + BLOB_OID
    for i in range(256))
GITLINK_257 = GITLINK_256 + b"160000 ext256\x00" + BLOB_OID
GITLINK_256_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", GITLINK_256).lower().encode("ascii"))
GITLINK_257_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", GITLINK_257).lower().encode("ascii"))
GITLINK_257_SUBDIR = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", GITLINK_257)), 1)
GITLINK_257_SUBDIR_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", GITLINK_257_SUBDIR).lower().encode("ascii"))
# M44: genuine full closure sees referenced objects beyond depth four.
def six_level_tree(leaf):
    levels = []
    for n in range(6):
        leaf = (b"40000 level" + str(n).encode("ascii") + b"\x00"
                + bytes.fromhex(git_oid("tree", leaf)))
        levels.append(leaf)
    return levels


CHAIN_GOOD = six_level_tree(SUBTREE)
CHAIN_MISSING = six_level_tree(NEST_MISSING)
CHAIN_WRONG = six_level_tree(NEST_WRONG)
CHAIN_ROOT_GOOD = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", CHAIN_GOOD[-1])), 1)
CHAIN_ROOT_MISSING = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", CHAIN_MISSING[-1])), 1)
CHAIN_ROOT_WRONG = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", CHAIN_WRONG[-1])), 1)
CHAIN_GOOD_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", CHAIN_ROOT_GOOD).lower().encode("ascii"))
CHAIN_MISSING_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", CHAIN_ROOT_MISSING).lower().encode("ascii"))
CHAIN_WRONG_COMMIT = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", CHAIN_ROOT_WRONG).lower().encode("ascii"))
CHAIN_MISSING_PARENT = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", CHAIN_MISSING_COMMIT).lower().encode("ascii"))
# Exact M44 1024-tree-visit budget boundary.
BUDGET_TREES = []
budget_leaf = SUBTREE
for budget_n in range(1023):
    budget_leaf = (b"40000 b" + str(budget_n).encode("ascii")
                   + b"\x00"
                   + bytes.fromhex(git_oid("tree", budget_leaf)))
    BUDGET_TREES.append(budget_leaf)
BUDGET_ROOT_OK = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", BUDGET_TREES[1021])), 1)
BUDGET_ROOT_OVER = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", BUDGET_TREES[1022])), 1)
BUDGET_COMMIT_OK = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", BUDGET_ROOT_OK).lower().encode("ascii"))
BUDGET_COMMIT_OVER = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", BUDGET_ROOT_OVER).lower().encode("ascii"))
# M37: third-level missing/wrong links remain valid at depths 0-2.
LEVEL3_GOOD = (b"40000 next\x00"
               + bytes.fromhex(git_oid("tree", DEEP_GOOD)))
LEVEL3_MISSING = (b"40000 next\x00"
                  + bytes.fromhex(git_oid("tree", DEEP_MISSING)))
LEVEL3_WRONG = (b"40000 next\x00"
                + bytes.fromhex(git_oid("tree", DEEP_WRONG)))
LEVEL3_ROOT_GOOD = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", LEVEL3_GOOD)), 1)
LEVEL3_ROOT_MISSING = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", LEVEL3_MISSING)), 1)
LEVEL3_ROOT_WRONG = TREE.replace(
    bytes.fromhex(git_oid("tree", SUBTREE)),
    bytes.fromhex(git_oid("tree", LEVEL3_WRONG)), 1)
LEVEL3_COMMIT_GOOD = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", LEVEL3_ROOT_GOOD).lower().encode("ascii"))
LEVEL3_COMMIT_MISSING = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", LEVEL3_ROOT_MISSING).lower().encode("ascii"))
LEVEL3_COMMIT_WRONG = FIRST_COMMIT.replace(
    git_oid("tree", TREE).lower().encode("ascii"),
    git_oid("tree", LEVEL3_ROOT_WRONG).lower().encode("ascii"))
LEVEL3_PARENT_MERGE = MERGE2.replace(
    git_oid("commit", SECOND_PARENT).lower().encode("ascii"),
    git_oid("commit", LEVEL3_COMMIT_MISSING).lower().encode("ascii"))
BAD_PARENT = MERGE.replace(b"parent " + b"1"*40,
                           b"parent " + b"Z"*40)
BAD_COMMIT = FIRST_COMMIT.replace(b"committer ", b"othername ")
MISSING_FIRST = MERGE.replace(
    b"parent " + git_oid("commit", FIRST_COMMIT).lower().encode("ascii"),
    b"parent " + b"1"*40, 1)
BLOB_FIRST = MERGE.replace(
    b"parent " + git_oid("commit", FIRST_COMMIT).lower().encode("ascii"),
    b"parent " + git_oid("blob", BLOB).lower().encode("ascii"), 1)
MALFORMED_FIRST = MERGE.replace(
    b"parent " + git_oid("commit", FIRST_COMMIT).lower().encode("ascii"),
    b"parent " + git_oid("commit", BAD_COMMIT).lower().encode("ascii"), 1)
SAMPLES = [(2, TREE), (2, b""), (2, MALFORMED),
           (2, SUBTREE), (3, BLOB),
           (1, FIRST_COMMIT), (1, MERGE), (1, BAD_PARENT), (1, BAD_COMMIT),
           (1, REAL_COMMIT), (1, BAD_LINK), (1, BAD_TREE_LINK),
           (3, EMPTY), (3, BINARY), (3, BIG),
           (2, HIST_TREE), (3, HIST_README),
           (1, MISSING_FIRST), (1, BLOB_FIRST), (1, MALFORMED_FIRST),
           (1, GRANDCHILD), (1, SECOND_PARENT), (1, MERGE2),
           (1, MISSING_ROOT_COMMIT), (1, MISSING_ROOT_MERGE),
           (1, BLOB_ROOT_MERGE), (1, MALFORMED_ROOT_MERGE),
           (2, MISSING_ENTRY_TREE), (2, WRONG_ENTRY_TREE),
           (2, INVALID_SUBTREE_TREE), (1, MISSING_ENTRY_COMMIT),
           (1, WRONG_ENTRY_COMMIT), (1, INVALID_SUBTREE_COMMIT),
           (1, MISSING_ENTRY_MERGE),
           (2, NEST_MISSING), (2, NEST_WRONG),
           (2, NEST_MISSING_TREE), (2, NEST_WRONG_TREE),
           (1, NEST_MISSING_COMMIT), (1, NEST_WRONG_COMMIT),
           (1, NEST_PARENT_MERGE),
           (2, DEEP_GOOD), (2, DEEP_MISSING), (2, DEEP_WRONG),
           (2, DEEP_ROOT_GOOD), (2, DEEP_ROOT_MISSING),
           (2, DEEP_ROOT_WRONG), (1, DEEP_COMMIT_GOOD),
           (1, DEEP_COMMIT_MISSING), (1, DEEP_COMMIT_WRONG),
           (1, DEEP_PARENT_MERGE), (2, LARGE_ROOT),
           (1, LARGE_ROOT_COMMIT),
           (2, GITLINK_256), (2, GITLINK_257),
           (1, GITLINK_256_COMMIT), (1, GITLINK_257_COMMIT),
           (2, GITLINK_257_SUBDIR),
           (1, GITLINK_257_SUBDIR_COMMIT),
           (2, LEVEL3_GOOD), (2, LEVEL3_MISSING),
           (2, LEVEL3_WRONG), (2, LEVEL3_ROOT_GOOD),
           (2, LEVEL3_ROOT_MISSING), (2, LEVEL3_ROOT_WRONG),
           (1, LEVEL3_COMMIT_GOOD), (1, LEVEL3_COMMIT_MISSING),
           (1, LEVEL3_COMMIT_WRONG), (1, LEVEL3_PARENT_MERGE)]
SAMPLES.extend((2, tree) for tree in BUDGET_TREES)
SAMPLES.extend([(2, BUDGET_ROOT_OK), (2, BUDGET_ROOT_OVER),
                (1, BUDGET_COMMIT_OK), (1, BUDGET_COMMIT_OVER)])
SAMPLES.extend(
    [(2, tree) for group in (CHAIN_GOOD, CHAIN_MISSING,
                            CHAIN_WRONG) for tree in group])
SAMPLES.extend([(2, CHAIN_ROOT_GOOD), (2, CHAIN_ROOT_MISSING),
                (2, CHAIN_ROOT_WRONG),
                (1, CHAIN_GOOD_COMMIT), (1, CHAIN_MISSING_COMMIT),
                (1, CHAIN_WRONG_COMMIT), (1, CHAIN_MISSING_PARENT)])
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
        disk = d
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
        expected_unique = len({git_oid({1: "commit", 2: "tree",
                                         3: "blob"}[typ], body)
                               for typ, body in OBJECTS})
        expected_gen = ("GENERATION VERIFIED 1808 UNIQUE "
                        + str(expected_unique))
        assert expected_gen in run(idx, "GENCHECK", cwd=d)
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
        # M26: list a nested directory from its commit-relative path.
        listed = run(rec, "LSDIR", "GENOLD", "GENNEW",
                     git_oid("commit", FIRST_COMMIT),
                     b"subdir".hex().upper(), cwd=d)
        verify_tree(listed, "SELECTED 52 GENNEW",
                    [(b"100644", b"nested.txt", BLOB_OID)])
        for name, expected_rc in ((b"README.md", 8),
                                  (b"submodule", 8),
                                  (b"missing", 4),
                                  (b"subdir/missing", 4),
                                  (b"README.md/child", 8)):
            bad_dir = run(rec, "LSDIR", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          name.hex().upper(), cwd=d, expected=expected_rc)
            assert "TREE DATA BEGIN" not in bad_dir
        for malformed_dir in ("00", "2F61", "612F", "612F2F62", "GG"):
            bad_dir = run(rec, "LSDIR", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT), malformed_dir,
                          cwd=d, expected=4)
            assert "TREE DATA BEGIN" not in bad_dir
        # M41: stricter directory listing authenticates every
        # immediate local blob/tree reference before ANY output.
        verified_dir = run(rec, "LSDIRV", "GENOLD", "GENNEW",
                           git_oid("commit", FIRST_COMMIT),
                           b"subdir".hex().upper(), cwd=d)
        verify_tree(verified_dir, "SELECTED 52 GENNEW",
                    [(b"100644", b"nested.txt", BLOB_OID)])
        assert "DIRECTORY LINKS VERIFIED" in verified_dir
        for bad, expected, marker in (
                (NEST_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (NEST_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            # The original LSDIR lists a structurally valid tree.
            plain = run(rec, "LSDIR", "GENOLD", "GENNEW",
                        git_oid("commit", bad),
                        b"subdir".hex().upper(), cwd=d)
            assert "TREE DATA END" in plain
            strict = run(rec, "LSDIRV", "GENOLD", "GENNEW",
                         git_oid("commit", bad),
                         b"subdir".hex().upper(), cwd=d,
                         expected=expected)
            assert marker in strict
            for leaked in ("DIRECTORY LINKS VERIFIED",
                           "PATH OBJECT TYPE", "TREE DATA BEGIN"):
                assert leaked not in strict
        malformed_verified = run(
            rec, "LSDIRV", "GENOLD", "GENNEW",
            git_oid("commit", INVALID_SUBTREE_COMMIT),
            b"subdir".hex().upper(), cwd=d, expected=8)
        assert "ROOT LINK TREE INVALID" in malformed_verified
        assert "PATH OBJECT TYPE" not in malformed_verified
        # M47: even a valid requested path must not leak metadata
        # if an unrelated sibling branch is incomplete.
        for path in (b"README.md", b"subdir", b"submodule"):
            complete = run(
                rec, "PATHFULL", "GENOLD", "GENNEW",
                git_oid("commit", CHAIN_GOOD_COMMIT),
                path.hex().upper(), cwd=d)
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" in complete
            assert ("PATH OID " in complete if path==b"submodule"
                    else "PATH OBJECT TYPE " in complete)
            assert "TREE DATA BEGIN" not in complete
            assert "PATH DATA BEGIN" not in complete
        for bad, code, reason in (
                (CHAIN_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            ordinary = run(
                rec, "PATH", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"README.md".hex().upper(), cwd=d)
            assert "PATH OBJECT TYPE 3" in ordinary
            full = run(
                rec, "PATHFULL", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"README.md".hex().upper(), cwd=d, expected=code)
            assert reason in full
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in full
            assert "PATH OBJECT TYPE" not in full
            assert "PATH OID " not in full
        nonexistent = run(
            rec, "PATHFULL", "GENOLD", "GENNEW",
            git_oid("commit", CHAIN_GOOD_COMMIT),
            b"missing".hex().upper(), cwd=d, expected=4)
        assert "PATH NOT FOUND" in nonexistent
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in nonexistent
        assert "PATH OBJECT TYPE" not in nonexistent
        for invalid in ("", "2", "00", "2F61", "612F", "612F2F62"):
            rejected = run(
                rec, "PATHFULL", "GENOLD", "GENNEW",
                git_oid("commit", CHAIN_GOOD_COMMIT),
                invalid, cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in rejected
            assert "GENERATION VERIFIED" not in rejected
        # M47: the limit applies even when the requested path
        # is present and uncorrupted elsewhere in the root.
        for commit_oid, path, rc, diagnostic in (
                (git_oid("commit", GITLINK_257_COMMIT),
                 b"ext000", 8, "ROOT LINK LIMIT EXCEEDED"),
                (git_oid("commit", BUDGET_COMMIT_OVER),
                 b"README.md", 8, "NESTED LINK BUDGET EXCEEDED")):
            ordinary_path = run(
                rec, "PATH", "GENOLD", "GENNEW",
                commit_oid, path.hex().upper(), cwd=d)
            assert ("PATH OID " in ordinary_path or
                    "PATH OBJECT TYPE " in ordinary_path)
            rejected = run(
                rec, "PATHFULL", "GENOLD", "GENNEW",
                commit_oid, path.hex().upper(), cwd=d,
                expected=rc)
            assert diagnostic in rejected
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in rejected
            assert "PATH OBJECT TYPE" not in rejected
            assert "PATH OID " not in rejected
        for commit_oid, path in (
                (git_oid("commit", GITLINK_256_COMMIT), b"ext000"),
                (git_oid("commit", BUDGET_COMMIT_OK), b"README.md")):
            accepted = run(
                rec, "PATHFULL", "GENOLD", "GENNEW",
                commit_oid, path.hex().upper(), cwd=d)
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" in accepted
        # M45: full commit-relative directory closure is distinct
        # from depth-four directory checks, with atomic listing.
        complete_dir = run(
            rec, "LSDIRFULL", "GENOLD", "GENNEW",
            git_oid("commit", CHAIN_GOOD_COMMIT),
            b"subdir".hex().upper(), cwd=d)
        assert "DIRECTORY FULL CLOSURE VERIFIED" in complete_dir
        assert "TREE DATA END" in complete_dir
        for bad, code, marker in (
                (CHAIN_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            shallow_dir = run(
                rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), "4", cwd=d)
            assert "DIRECTORY LINK DEPTH 4 VERIFIED" in shallow_dir
            broken_dir = run(
                rec, "LSDIRFULL", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), cwd=d, expected=code)
            assert marker in broken_dir
            for leaked in ("DIRECTORY FULL CLOSURE VERIFIED",
                           "PATH OBJECT TYPE", "TREE DATA BEGIN"):
                assert leaked not in broken_dir
        over_dir = run(
            rec, "LSDIRFULL", "GENOLD", "GENNEW",
            git_oid("commit", GITLINK_257_SUBDIR_COMMIT),
            b"subdir".hex().upper(), cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in over_dir
        assert "PATH OBJECT TYPE" not in over_dir
        assert "TREE DATA BEGIN" not in over_dir
        for bad_name in ("", "00", "2F61", "612F"):
            invalid_path = run(
                rec, "LSDIRFULL", "GENOLD", "GENNEW",
                git_oid("commit", CHAIN_GOOD_COMMIT),
                bad_name, cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in invalid_path
        # M42: caller-chosen depth 0..4 must validate all
        # referenced descendant objects without partial output.
        for n in range(5):
            listing = run(
                rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
                git_oid("commit", LEVEL3_COMMIT_GOOD),
                b"subdir".hex().upper(), str(n), cwd=d)
            assert "DIRECTORY LINK DEPTH " + str(n) in listing
            assert "TREE DATA END" in listing
            assert "DIRECTORY LINKS VERIFIED" not in listing
        for bad, code, reason in (
                (DEEP_COMMIT_MISSING, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (DEEP_COMMIT_WRONG, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            shallow = run(
                rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), "0", cwd=d)
            assert "DIRECTORY LINK DEPTH 0 VERIFIED" in shallow
            deeper = run(
                rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), "1", cwd=d,
                expected=code)
            assert reason in deeper
            assert "DIRECTORY LINK DEPTH" not in deeper
            assert "PATH OBJECT TYPE" not in deeper
            assert "TREE DATA BEGIN" not in deeper
        depth_one = run(
            rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
            git_oid("commit", LEVEL3_COMMIT_MISSING),
            b"subdir".hex().upper(), "1", cwd=d)
        assert "DIRECTORY LINK DEPTH 1 VERIFIED" in depth_one
        depth_two = run(
            rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
            git_oid("commit", LEVEL3_COMMIT_MISSING),
            b"subdir".hex().upper(), "2", cwd=d, expected=4)
        assert "ROOT ENTRY OBJECT NOT FOUND" in depth_two
        assert "PATH OBJECT TYPE" not in depth_two
        for invalid in ("", "5", "10", "-1", "X"):
            rejected = run(
                rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                b"subdir".hex().upper(), invalid,
                cwd=d, expected=4)
            assert "DIRECTORY DEPTH MUST BE 0 THROUGH 4" in rejected
            assert "GENERATION VERIFIED" not in rejected
        # M40: a canonical OID is insufficient when a terminal
        # directory is itself malformed. Never expose partial
        # PATH metadata or a partial directory listing.
        for command in ("PATH", "LSDIR"):
            corrupt = run(
                rec, command, "GENOLD", "GENNEW",
                git_oid("commit", INVALID_SUBTREE_COMMIT),
                b"subdir".hex().upper(), cwd=d, expected=8)
            assert "DIRECTORY TREE STRUCTURE INVALID" in corrupt
            assert "PATH OBJECT TYPE" not in corrupt
            assert "TREE DATA BEGIN" not in corrupt
            assert "TREE ENTRY MODE" not in corrupt
        subtree = run(rec, "PATH", "GENOLD", "GENNEW",
                      git_oid("commit", FIRST_COMMIT),
                      b"subdir".hex().upper(), cwd=d)
        assert "PATH OBJECT TYPE 2 SIZE " + str(len(SUBTREE)) in subtree
        gitlink = run(rec, "PATH", "GENOLD", "GENNEW",
                      git_oid("commit", FIRST_COMMIT),
                      b"submodule".hex().upper(), cwd=d)
        assert "PATH GITLINK (EXTERNAL COMMIT)" in gitlink
        assert "PATH OID " + BLOB_OID.hex().upper() in gitlink

        # M52: one selected generation for eleven positive
        # production checks; retain a distinct final success gate.
        batch_args = ("RUNBATCH", "GENOLD", "GENNEW",
               git_oid("commit", MERGE2),
               git_oid("tree", TREE),
               b"subdir".hex().upper(),
               b"README.md".hex().upper())
        batch = run(rec, *batch_args, cwd=d)
        assert "SELECTED 52 GENNEW" in batch
        assert "BATCH ALL POSITIVE CHECKS PASSED" in batch
        assert "BATCH ROOT CLOSURE REUSES " in batch
        assert "BATCH SEEK INDEX REUSES " in batch
        for marker in (
                "NESTED ROOT LINKS VERIFIED",
                "DEEP ROOT LINKS VERIFIED",
                "LINK DEPTH 2 VERIFIED",
                "DIRECTORY LINK DEPTH 1 VERIFIED",
                "DIRECTORY FULL CLOSURE VERIFIED",
                "FULL ROOT CLOSURE VERIFIED",
                "TREE FULL CLOSURE VERIFIED",
                "COMMIT ROOT FULL CLOSURE VERIFIED",
                "TREE ROOT FULL CLOSURE VERIFIED",
                "HISTORY FULL ROOT CLOSURE VERIFIED",
                "HISTORY HOPS 1",
                "PATH DATA END",
                "TREE DATA END",
                "BATCH NON COMMIT CHILD RC8 VERIFIED",
                "BATCH MISSING CHILD RC4 VERIFIED",
                "BATCH ALL POSITIVE CHECKS PASSED"):
            assert marker in batch
        assert batch.count("GENERATION VERIFIED 1808") <= 1
        for bad, expected in (
                ("0"*40, 4),
                (git_oid("blob", BLOB), 8)):
            failed = run(
                rec, "RUNBATCH", "GENOLD", "GENNEW",
                git_oid("commit", MERGE2), bad,
                b"subdir".hex().upper(),
                b"README.md".hex().upper(),
                cwd=d, expected=expected)
            assert "BATCH ALL POSITIVE CHECKS PASSED" not in failed
        # M55: a bad raw root cannot enter or benefit from cache.
        for raw, rc, reason in (
                (BUDGET_ROOT_OVER, 8,
                 "NESTED LINK BUDGET EXCEEDED"),
                (GITLINK_257, 8,
                 "ROOT LINK LIMIT EXCEEDED"),
                (CHAIN_ROOT_MISSING, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_ROOT_WRONG, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            invalid_root = run(
                rec, "RUNBATCH", "GENOLD", "GENNEW",
                git_oid("commit", MERGE2),
                git_oid("tree", raw),
                b"subdir".hex().upper(),
                b"README.md".hex().upper(),
                cwd=d, expected=rc)
            assert reason in invalid_root
            assert "BATCH ROOT CLOSURE REUSES " not in invalid_root
            assert "BATCH SEEK INDEX REUSES " not in invalid_root
            assert "BATCH ALL POSITIVE CHECKS PASSED" not in invalid_root
        # The optimization must never leak into separate commands.
        standalone = run(
            rec, "TREEPATHDIR", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"subdir".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in standalone
        assert "BATCH ROOT CLOSURE REUSES " not in standalone
        assert "BATCH SEEK INDEX REUSES " not in standalone
        for malformed in ("", "00", "2F61"):
            invalid = run(
                rec, "RUNBATCH", "GENOLD", "GENNEW",
                git_oid("commit", MERGE2),
                git_oid("tree", TREE),
                malformed, b"README.md".hex().upper(),
                cwd=d, expected=4)
            assert "BATCH REQUIRES TREE40 DIRHEX FILEHEX" in invalid
            assert "GENERATION VERIFIED" not in invalid
        # M51: metadata from raw tree roots after whole-tree
        # attestation, for blobs, directories and Gitlinks.
        for name, expected in (
                (b"README.md", "PATH OBJECT TYPE 3"),
                (b"subdir", "PATH OBJECT TYPE 2"),
                (b"submodule", "PATH GITLINK (EXTERNAL COMMIT)"),
                (b"subdir/nested.txt", "PATH OBJECT TYPE 3")):
            meta = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                       git_oid("tree", TREE), name.hex().upper(),
                       cwd=d)
            assert "TREE ROOT FULL CLOSURE VERIFIED" in meta
            assert expected in meta
            assert "TREE DATA BEGIN" not in meta
            assert "PATH DATA BEGIN" not in meta
        for bad_tree, code, reason in (
                (CHAIN_ROOT_MISSING, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_ROOT_WRONG, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            normal = run(rec, "PATH", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         b"README.md".hex().upper(), cwd=d)
            assert "PATH OBJECT TYPE 3" in normal
            refused = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                          git_oid("tree", bad_tree),
                          b"README.md".hex().upper(),
                          cwd=d, expected=code)
            assert reason in refused
            assert "TREE ROOT FULL CLOSURE VERIFIED" not in refused
            assert "PATH OBJECT TYPE" not in refused
            assert "PATH GITLINK" not in refused
        absent = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                     "0"*40, b"README.md".hex().upper(),
                     cwd=d, expected=4)
        assert "ROOT LINK TREE NOT FOUND" in absent
        wrong_root = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                         git_oid("blob", BLOB),
                         b"README.md".hex().upper(), cwd=d,
                         expected=8)
        assert "ROOT LINK OBJECT NOT TREE" in wrong_root
        for invalid in ("", "00", "2F61", "612F", "612F2F62"):
            bad = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                      git_oid("tree", TREE), invalid,
                      cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in bad
            assert "GENERATION VERIFIED" not in bad
        for tree, code, reason in (
                (BUDGET_ROOT_OVER, 8,
                 "NESTED LINK BUDGET EXCEEDED"),
                (GITLINK_257, 8,
                 "ROOT LINK LIMIT EXCEEDED")):
            refused = run(
                rec, "TREEPATH", "GENOLD", "GENNEW",
                git_oid("tree", tree),
                (b"README.md" if tree==BUDGET_ROOT_OVER
                 else b"ext000").hex().upper(),
                cwd=d, expected=code)
            assert reason in refused
            assert "TREE ROOT FULL CLOSURE VERIFIED" not in refused
            assert "PATH OBJECT TYPE" not in refused
        within = run(rec, "TREEPATH", "GENOLD", "GENNEW",
                     git_oid("tree", BUDGET_ROOT_OK),
                     b"README.md".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in within
        # M50: raw tree roots can serve full-closure binary paths.
        for filename, body in (
                (b"README.md", BLOB), (b"empty.bin", EMPTY),
                (b"bytes.bin", BINARY), (b"big.bin", BIG),
                (b"subdir/nested.txt", BLOB)):
            raw = run(rec, "TREEPATHCAT", "GENOLD", "GENNEW",
                      git_oid("tree", TREE), filename.hex().upper(),
                      cwd=d)
            assert "TREE ROOT FULL CLOSURE VERIFIED" in raw
            verify_pathcat(raw, body)
        raw_dir = run(rec, "TREEPATHDIR", "GENOLD", "GENNEW",
                      git_oid("tree", TREE),
                      b"subdir".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in raw_dir
        assert "TREE DATA END" in raw_dir
        for tree, code, reason in (
                (CHAIN_ROOT_MISSING, 4, "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_ROOT_WRONG, 8, "ROOT ENTRY TYPE MISMATCH")):
            for command, path in (("TREEPATHCAT", b"README.md"),
                                  ("TREEPATHDIR", b"subdir")):
                failed = run(rec, command, "GENOLD", "GENNEW",
                             git_oid("tree", tree), path.hex().upper(),
                             cwd=d, expected=code)
                assert reason in failed
                assert "TREE ROOT FULL CLOSURE VERIFIED" not in failed
                assert "PATH OBJECT TYPE" not in failed
                assert "TREE DATA BEGIN" not in failed
                assert "PATH DATA BEGIN" not in failed
        # M50: absent/incorrect roots, terminal type errors,
        # malformed paths and exact bounded subtree visits.
        for command, path in (("TREEPATHCAT", b"README.md"),
                              ("TREEPATHDIR", b"subdir")):
            no_root = run(rec, command, "GENOLD", "GENNEW",
                          "0"*40, path.hex().upper(),
                          cwd=d, expected=4)
            assert "ROOT LINK TREE NOT FOUND" in no_root
            not_tree = run(rec, command, "GENOLD", "GENNEW",
                           git_oid("blob", BLOB), path.hex().upper(),
                           cwd=d, expected=8)
            assert "ROOT LINK OBJECT NOT TREE" in not_tree
            for invalid in ("", "00", "2F61", "612F"):
                rejected = run(rec, command, "GENOLD", "GENNEW",
                               git_oid("tree", TREE), invalid,
                               cwd=d, expected=4)
                assert "PATH REQUIRES VALID NONEMPTY HEX" in rejected
                assert "GENERATION VERIFIED" not in rejected
        for command, path in (
                ("TREEPATHCAT", b"subdir"),
                ("TREEPATHCAT", b"submodule"),
                ("TREEPATHDIR", b"README.md"),
                ("TREEPATHDIR", b"submodule")):
            wrong = run(rec, command, "GENOLD", "GENNEW",
                        git_oid("tree", TREE), path.hex().upper(),
                        cwd=d, expected=8)
            assert "TREE ROOT FULL CLOSURE VERIFIED" not in wrong
            assert "TREE DATA BEGIN" not in wrong
            assert "PATH DATA BEGIN" not in wrong
        exact = run(rec, "TREEPATHCAT", "GENOLD", "GENNEW",
                    git_oid("tree", BUDGET_ROOT_OK),
                    b"README.md".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in exact
        over = run(rec, "TREEPATHCAT", "GENOLD", "GENNEW",
                   git_oid("tree", BUDGET_ROOT_OVER),
                   b"README.md".hex().upper(), cwd=d, expected=8)
        assert "NESTED LINK BUDGET EXCEEDED" in over
        assert "PATH DATA BEGIN" not in over
        for command, path in (
                ("TREEPATHCAT", b"ext000"),
                ("TREEPATHDIR", b"subdir")):
            over_links = run(
                rec, command, "GENOLD", "GENNEW",
                git_oid("tree", GITLINK_257 if
                        command=="TREEPATHCAT" else
                        GITLINK_257_SUBDIR),
                path.hex().upper(), cwd=d, expected=8)
            assert "ROOT LINK LIMIT EXCEEDED" in over_links
            assert "TREE ROOT FULL CLOSURE VERIFIED" not in over_links
            assert "TREE DATA BEGIN" not in over_links
            assert "PATH DATA BEGIN" not in over_links
        # M49: complete-snapshot authenticated directory listing.
        good_dir = run(
            rec, "PATHFULLDIR", "GENOLD", "GENNEW",
            git_oid("commit", CHAIN_GOOD_COMMIT),
            b"subdir".hex().upper(), cwd=d)
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in good_dir
        assert "PATH OBJECT TYPE 2" in good_dir
        assert "TREE DATA END" in good_dir
        for bad, rc, reason in (
                (CHAIN_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            ordinary = run(
                rec, "LSDIR", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), cwd=d)
            assert "TREE DATA END" in ordinary
            refused = run(
                rec, "PATHFULLDIR", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"subdir".hex().upper(), cwd=d, expected=rc)
            assert reason in refused
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in refused
            assert "PATH OBJECT TYPE" not in refused
            assert "TREE DATA BEGIN" not in refused
        for name, rc in ((b"README.md", 8),
                         (b"submodule", 8),
                         (b"missing", 4)):
            refused = run(
                rec, "PATHFULLDIR", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                name.hex().upper(), cwd=d, expected=rc)
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in refused
            assert "TREE DATA BEGIN" not in refused
        for invalid in ("", "00", "2F61", "612F"):
            refused = run(
                rec, "PATHFULLDIR", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                invalid, cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in refused
            assert "GENERATION VERIFIED" not in refused
        # M49: snapshot-wide bounds include branches unrelated
        # to the chosen directory; no listing on exhaustion.
        for commit, rc, diagnostic in (
                (GITLINK_257_SUBDIR_COMMIT, 8,
                 "ROOT LINK LIMIT EXCEEDED"),
                (BUDGET_COMMIT_OVER, 8,
                 "NESTED LINK BUDGET EXCEEDED")):
            broken = run(
                rec, "PATHFULLDIR", "GENOLD", "GENNEW",
                git_oid("commit", commit),
                b"subdir".hex().upper(), cwd=d, expected=rc)
            assert diagnostic in broken
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in broken
            assert "PATH OBJECT TYPE" not in broken
            assert "TREE DATA BEGIN" not in broken
        bounded = run(
            rec, "PATHFULLDIR", "GENOLD", "GENNEW",
            git_oid("commit", BUDGET_COMMIT_OK),
            b"subdir".hex().upper(), cwd=d)
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in bounded
        assert "TREE DATA END" in bounded
        # M48: full-root verified binary blob reading, including
        # all 65536 bytes, zero length, and a nested path.
        for filename, data in (
                (b"README.md", BLOB),
                (b"empty.bin", EMPTY),
                (b"bytes.bin", BINARY),
                (b"big.bin", BIG),
                (b"subdir/nested.txt", BLOB)):
            verified = run(
                rec, "PATHFULLCAT", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                filename.hex().upper(), cwd=d)
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" in verified
            verify_pathcat(verified, data)
        for bad, rc, reason in (
                (CHAIN_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH")):
            ordinary = run(
                rec, "PATHCAT", "GENOLD", "GENNEW",
                git_oid("commit", bad), b"README.md".hex().upper(),
                cwd=d)
            verify_pathcat(ordinary, BLOB)
            refused = run(
                rec, "PATHFULLCAT", "GENOLD", "GENNEW",
                git_oid("commit", bad),
                b"README.md".hex().upper(), cwd=d, expected=rc)
            assert reason in refused
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in refused
            assert "PATH OBJECT TYPE" not in refused
            assert "PATH DATA BEGIN" not in refused
            assert "PATH HEX " not in refused
        for invalid_name, rc in (
                (b"subdir", 8), (b"submodule", 8),
                (b"missing", 4)):
            rejected = run(
                rec, "PATHFULLCAT", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                invalid_name.hex().upper(), cwd=d, expected=rc)
            assert "PATH DATA BEGIN" not in rejected
            assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in rejected
        for broken_hex in ("", "00", "612F", "2F61"):
            invalid = run(
                rec, "PATHFULLCAT", "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                broken_hex, cwd=d, expected=4)
            assert "PATH REQUIRES VALID NONEMPTY HEX" in invalid
            assert "GENERATION VERIFIED" not in invalid
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

        # M27 first-parent verification traverses the SAME sealed generation.
        first = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE), cwd=d)
        assert "SELECTED 52 GENNEW" in first
        assert "FIRST PARENT VERIFIED" in first
        assert "FIRST PARENT OID " + git_oid("commit", FIRST_COMMIT) in first
        assert "FIRST PARENT TREE " + git_oid("tree", TREE) in first
        root_first = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         cwd=d, expected=4)
        assert "ROOT COMMIT HAS NO FIRST PARENT" in root_first
        assert "FIRST PARENT VERIFIED" not in root_first
        for bad, rc, reason in (
                (MISSING_FIRST, 4, "FIRST PARENT OBJECT NOT FOUND"),
                (BLOB_FIRST, 8, "FIRST PARENT IS NOT A COMMIT"),
                (MALFORMED_FIRST, 8, "FIRST PARENT STRUCTURE INVALID")):
            result = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d, expected=rc)
            assert reason in result
            assert "FIRST PARENT VERIFIED" not in result
        first_wrong = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                          tree_oid, cwd=d, expected=8)
        assert "OBJECT IS NOT A COMMIT" in first_wrong
        assert "FIRST PARENT VERIFIED" not in first_wrong
        # M37: user-selected verification depth 0..4.
        for dnum in range(5):
            depth_success = run(
                rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                git_oid("commit", LEVEL3_COMMIT_GOOD),
                str(dnum), cwd=d)
            assert "LINK DEPTH " + str(dnum) + " VERIFIED" in depth_success
            assert "PARENTS COUNT 0" in depth_success
            assert all(len(x) <= 80 for x in depth_success.splitlines())
        for bad, rc, marker in (
                (LEVEL3_COMMIT_MISSING, 4, "ROOT ENTRY OBJECT NOT FOUND"),
                (LEVEL3_COMMIT_WRONG, 8, "ROOT ENTRY TYPE MISMATCH"),
                (LEVEL3_PARENT_MERGE, 4, "ROOT ENTRY OBJECT NOT FOUND")):
            for shallow_depth in ("0", "1", "2"):
                shallow_result = run(
                    rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                    git_oid("commit", bad), shallow_depth, cwd=d)
                assert "LINK DEPTH " + shallow_depth + " VERIFIED" in shallow_result
            failed_deep = run(
                rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                git_oid("commit", bad), "3", cwd=d, expected=rc)
            assert marker in failed_deep
            assert "PARENTS DATA BEGIN" not in failed_deep
            assert "LINK DEPTH 3 VERIFIED" not in failed_deep
        for invalid in ("", "5", "10", "-1", "X", "1A"):
            invalid_depth = run(
                rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                git_oid("commit", MERGE2), invalid,
                cwd=d, expected=4)
            assert "LINK DEPTH MUST BE 0 THROUGH 4" in invalid_depth
        for wrong, code in ((git_oid("tree", TREE), 8),
                            ("0"*40, 4)):
            bad_child = run(
                rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                wrong, "2", cwd=d, expected=code)
            assert "PARENTS DATA BEGIN" not in bad_child

        # M46: full closure can start at any known tree OID;
        # no synthetic commit or commit-relative path is needed.
        direct = run(rec, "TREECLOSURE", "GENOLD", "GENNEW",
                     git_oid("tree", CHAIN_ROOT_GOOD), cwd=d)
        assert "TREE FULL CLOSURE VERIFIED" in direct
        assert "TREE DATA BEGIN" in direct
        assert "TREE DATA END" in direct
        for tree, code, diagnostic in (
                (CHAIN_ROOT_MISSING, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_ROOT_WRONG, 8,
                 "ROOT ENTRY TYPE MISMATCH"),
                (MALFORMED, 8, "ROOT LINK TREE INVALID"),
                (GITLINK_257, 8, "ROOT LINK LIMIT EXCEEDED")):
            output = run(rec, "TREECLOSURE", "GENOLD",
                         "GENNEW", git_oid("tree", tree),
                         cwd=d, expected=code)
            assert diagnostic in output
            assert "TREE FULL CLOSURE VERIFIED" not in output
            assert "TREE DATA BEGIN" not in output
        missing_tree = run(rec, "TREECLOSURE", "GENOLD",
                           "GENNEW", "0"*40, cwd=d, expected=4)
        assert "ROOT LINK TREE NOT FOUND" in missing_tree
        non_tree = run(rec, "TREECLOSURE", "GENOLD",
                       "GENNEW", git_oid("blob", BLOB),
                       cwd=d, expected=8)
        assert "ROOT LINK OBJECT NOT TREE" in non_tree
        gitlinks_ok = run(rec, "TREECLOSURE", "GENOLD",
                          "GENNEW", git_oid("tree", GITLINK_256),
                          cwd=d)
        assert "TREE FULL CLOSURE VERIFIED" in gitlinks_ok
        assert "TREE DATA END" in gitlinks_ok
        limit_ok = run(rec, "TREECLOSURE", "GENOLD",
                       "GENNEW", git_oid("tree", BUDGET_ROOT_OK),
                       cwd=d)
        assert "TREE FULL CLOSURE VERIFIED" in limit_ok
        limit_failed = run(rec, "TREECLOSURE", "GENOLD",
                           "GENNEW", git_oid("tree", BUDGET_ROOT_OVER),
                           cwd=d, expected=8)
        assert "NESTED LINK BUDGET EXCEEDED" in limit_failed
        assert "TREE DATA BEGIN" not in limit_failed
        # M44: fixed depth four cannot validate a deeper link,
        # but iterative full closure must authenticate all of it.
        closure = run(rec, "CLOSURE", "GENOLD", "GENNEW",
                      git_oid("commit", CHAIN_GOOD_COMMIT),
                      cwd=d)
        assert "FULL ROOT CLOSURE VERIFIED" in closure
        assert "PARENTS COUNT 0" in closure
        for bad, rc, marker in (
                (CHAIN_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (CHAIN_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH"),
                (CHAIN_MISSING_PARENT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND")):
            limited = run(rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                          git_oid("commit", bad), "4", cwd=d)
            assert "LINK DEPTH 4 VERIFIED" in limited
            broken = run(rec, "CLOSURE", "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d,
                         expected=rc)
            assert marker in broken
            assert "FULL ROOT CLOSURE VERIFIED" not in broken
            assert "PARENTS DATA BEGIN" not in broken
        # M44 resource boundary: root plus 1022 nested trees
        # plus the final SUBTREE uses exactly 1024 visits.
        exact_budget = run(rec, "CLOSURE", "GENOLD", "GENNEW",
                           git_oid("commit", BUDGET_COMMIT_OK),
                           cwd=d)
        assert "FULL ROOT CLOSURE VERIFIED" in exact_budget
        assert "PARENTS COUNT 0" in exact_budget
        # One additional visited tree exceeds the shared budget.
        exhausted = run(rec, "CLOSURE", "GENOLD", "GENNEW",
                        git_oid("commit", BUDGET_COMMIT_OVER),
                        cwd=d, expected=8)
        assert "NESTED LINK BUDGET EXCEEDED" in exhausted
        assert "FULL ROOT CLOSURE VERIFIED" not in exhausted
        assert "PARENTS DATA BEGIN" not in exhausted
        too_many = run(rec, "CLOSURE", "GENOLD", "GENNEW",
                       git_oid("commit", GITLINK_257_COMMIT),
                       cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in too_many
        assert "PARENTS DATA BEGIN" not in too_many

        # M38: one full audit and one depth-two graph pass. All
        # three success markers must be committed together.
        batch = run(rec, "LINKBATCH", "GENOLD", "GENNEW",
                    git_oid("commit", DEEP_COMMIT_GOOD), cwd=d)
        for marker in ("NESTED ROOT LINKS VERIFIED",
                       "DEEP ROOT LINKS VERIFIED",
                       "LINK DEPTH 2 VERIFIED"):
            assert marker in batch
        assert "PARENTS COUNT 0" in batch
        # Compare complete authenticated metadata with legacy M37.
        legacy = run(rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                     git_oid("commit", DEEP_COMMIT_GOOD),
                     "2", cwd=d)
        assert batch.split("PARENTS DATA BEGIN", 1)[1] == (
            legacy.split("PARENTS DATA BEGIN", 1)[1])
        # Every single LINKBATCH command audits only one selected
        # generation; its three markers do not trigger extra audits.
        assert len(re.findall(r"^GENERATION VERIFIED [0-9]+ UNIQUE "
                              r"[0-9]+$", batch, re.M)) == 1
        assert batch.count("NESTED ROOT LINKS VERIFIED") == 1
        assert batch.count("DEEP ROOT LINKS VERIFIED") == 1
        assert batch.count("LINK DEPTH 2 VERIFIED") == 1
        for bad, code, marker in (
                (DEEP_COMMIT_MISSING, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (DEEP_COMMIT_WRONG, 8,
                 "ROOT ENTRY TYPE MISMATCH"),
                (DEEP_PARENT_MERGE, 4,
                 "ROOT ENTRY OBJECT NOT FOUND")):
            broken = run(rec, "LINKBATCH", "GENOLD",
                         "GENNEW", git_oid("commit", bad),
                         cwd=d, expected=code)
            assert marker in broken
            assert "NESTED ROOT LINKS VERIFIED" not in broken
            assert "DEEP ROOT LINKS VERIFIED" not in broken
            assert "LINK DEPTH 2 VERIFIED" not in broken
            assert "PARENTS DATA BEGIN" not in broken
        for bad, code in ((tree_oid, 8), ("0"*40, 4)):
            broken = run(rec, "LINKBATCH", "GENOLD", "GENNEW",
                         bad, cwd=d, expected=code)
            assert "LINK DEPTH 2 VERIFIED" not in broken
        # M39: when a subtree read is deferred to recursion,
        # errors in child and parent subtrees must still fail.
        for bad, code, reason in (
                (NEST_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (NEST_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH"),
                (NEST_PARENT_MERGE, 4,
                 "ROOT ENTRY OBJECT NOT FOUND")):
            corrupt_nested = run(
                rec, "LINKBATCH", "GENOLD", "GENNEW",
                git_oid("commit", bad), cwd=d, expected=code)
            assert reason in corrupt_nested
            assert "NESTED ROOT LINKS VERIFIED" not in corrupt_nested
            assert "DEEP ROOT LINKS VERIFIED" not in corrupt_nested
            assert "PARENTS DATA BEGIN" not in corrupt_nested
        # M43: Gitlinks are external, but count toward the same
        # 256-entry bound so all-Gitlink trees cannot evade it.
        at_limit = run(
            rec, "LINKBATCH", "GENOLD", "GENNEW",
            git_oid("commit", GITLINK_256_COMMIT), cwd=d)
        assert "LINK DEPTH 2 VERIFIED" in at_limit
        over_gitlinks = run(
            rec, "LINKBATCH", "GENOLD", "GENNEW",
            git_oid("commit", GITLINK_257_COMMIT),
            cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in over_gitlinks
        for leaked in ("NESTED ROOT LINKS VERIFIED",
                       "DEEP ROOT LINKS VERIFIED",
                       "LINK DEPTH 2 VERIFIED",
                       "PARENTS DATA BEGIN"):
            assert leaked not in over_gitlinks
        over_nested = run(
            rec, "LSDIRDEPTH", "GENOLD", "GENNEW",
            git_oid("commit", GITLINK_257_SUBDIR_COMMIT),
            b"subdir".hex().upper(), "0", cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in over_nested
        for leaked in ("DIRECTORY LINK DEPTH",
                       "PATH OBJECT TYPE", "TREE DATA BEGIN"):
            assert leaked not in over_nested
        # A 257-entry root must fail without partial batch output.
        over_limit = run(rec, "LINKBATCH", "GENOLD", "GENNEW",
                         git_oid("commit", LARGE_ROOT_COMMIT),
                         cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in over_limit
        for marker in ("NESTED ROOT LINKS VERIFIED",
                       "DEEP ROOT LINKS VERIFIED",
                       "LINK DEPTH 2 VERIFIED",
                       "PARENTS DATA BEGIN"):
            assert marker not in over_limit

        # M36: one deeper level: both shallower commands must pass
        # even when the deepest nested blob is missing or wrong type.
        deep_valid = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                         git_oid("commit", DEEP_COMMIT_GOOD), cwd=d)
        assert "DEEP ROOT LINKS VERIFIED" in deep_valid
        assert "PARENTS COUNT 0" in deep_valid
        assert all(len(x) <= 80 for x in deep_valid.splitlines())
        deep_merge = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                         git_oid("commit", MERGE2), cwd=d)
        assert "DEEP ROOT LINKS VERIFIED" in deep_merge
        assert "PARENTS COUNT 2" in deep_merge
        for bad, rc, marker in (
                (DEEP_COMMIT_MISSING, 4, "ROOT ENTRY OBJECT NOT FOUND"),
                (DEEP_COMMIT_WRONG, 8, "ROOT ENTRY TYPE MISMATCH"),
                (DEEP_PARENT_MERGE, 4, "ROOT ENTRY OBJECT NOT FOUND")):
            for shallow in ("ROOTLINKS", "NESTLINKS"):
                ok = run(rec, shallow, "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d)
                assert "PARENTS DATA BEGIN" in ok
            bad_deep = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                           git_oid("commit", bad), cwd=d, expected=rc)
            assert marker in bad_deep
            assert "DEEP ROOT LINKS VERIFIED" not in bad_deep
            assert "PARENTS DATA BEGIN" not in bad_deep
        many = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                   git_oid("commit", LARGE_ROOT_COMMIT),
                   cwd=d, expected=8)
        assert "ROOT LINK LIMIT EXCEEDED" in many
        assert "PARENTS DATA BEGIN" not in many

        # M35: authenticate entries inside each direct root subtree.
        nested = run(rec, "NESTLINKS", "GENOLD", "GENNEW",
                     git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in nested
        assert "NESTED ROOT LINKS VERIFIED" in nested
        assert "PARENTS COUNT 2" in nested
        assert all(len(line) <= 80 for line in nested.splitlines())
        for bad, code, marker in (
                (NEST_MISSING_COMMIT, 4,
                 "ROOT ENTRY OBJECT NOT FOUND"),
                (NEST_WRONG_COMMIT, 8,
                 "ROOT ENTRY TYPE MISMATCH"),
                (NEST_PARENT_MERGE, 4,
                 "ROOT ENTRY OBJECT NOT FOUND")):
            # M34 only checks direct root links, so these must pass.
            direct = run(rec, "ROOTLINKS", "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d)
            assert "ROOT DIRECT LINKS VERIFIED" in direct
            failed_nested = run(rec, "NESTLINKS", "GENOLD",
                                "GENNEW", git_oid("commit", bad),
                                cwd=d, expected=code)
            assert marker in failed_nested
            assert "NESTED ROOT LINKS VERIFIED" not in failed_nested
            assert "PARENTS DATA BEGIN" not in failed_nested
        root_nested = run(rec, "NESTLINKS", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "NESTED ROOT LINKS VERIFIED" in root_nested
        assert "PARENTS COUNT 0" in root_nested

        # M34: verify each direct blob/tree link in own and parent roots.
        links = run(rec, "ROOTLINKS", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in links
        assert "ROOT DIRECT LINKS VERIFIED" in links
        assert "PARENTS COUNT 2" in links
        assert all(len(line) <= 80 for line in links.splitlines())
        for bad, code, marker in (
                (MISSING_ENTRY_COMMIT, 4, "ROOT ENTRY OBJECT NOT FOUND"),
                (WRONG_ENTRY_COMMIT, 8, "ROOT ENTRY TYPE MISMATCH"),
                (INVALID_SUBTREE_COMMIT, 8,
                 "ROOT ENTRY SUBTREE INVALID"),
                (MISSING_ENTRY_MERGE, 4,
                 "ROOT ENTRY OBJECT NOT FOUND")):
            fail_links = run(rec, "ROOTLINKS", "GENOLD",
                             "GENNEW", git_oid("commit", bad),
                             cwd=d, expected=code)
            assert marker in fail_links
            assert "ROOT DIRECT LINKS VERIFIED" not in fail_links
            assert "PARENTS DATA BEGIN" not in fail_links
        zero_links = run(rec, "ROOTLINKS", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "ROOT DIRECT LINKS VERIFIED" in zero_links
        assert "PARENTS COUNT 0" in zero_links

        # M33: authenticate selected commit root AND every parent root.
        graph = run(rec, "COMMITROOTS", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE2), cwd=d)
        assert "COMMIT ROOTS VERIFIED" in graph
        assert "PARENTS COUNT 2" in graph
        assert graph.strip().endswith("PARENTS DATA END")
        for n, obj in ((1, FIRST_COMMIT), (2, SECOND_PARENT)):
            assert ("PARENTS ORDINAL " + str(n) + " OID "
                    + git_oid("commit", obj)) in graph
            assert ("PARENTS ORDINAL " + str(n) + " TREE "
                    + git_oid("tree", TREE)) in graph
        assert all(len(line) <= 80 for line in graph.splitlines())
        graph_root = run(rec, "COMMITROOTS", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "COMMIT ROOTS VERIFIED" in graph_root
        assert "PARENTS COUNT 0" in graph_root
        for bad, rc, reason in (
                (MISSING_ROOT_COMMIT, 4, "CHILD ROOT TREE NOT FOUND"),
                (BAD_LINK, 8, "CHILD ROOT OBJECT NOT TREE"),
                (BAD_TREE_LINK, 8, "CHILD ROOT TREE INVALID"),
                (MISSING_ROOT_MERGE, 4, "PARENT ROOT TREE NOT FOUND"),
                (BLOB_ROOT_MERGE, 8, "PARENT ROOT OBJECT NOT TREE"),
                (MALFORMED_ROOT_MERGE, 8, "PARENT ROOT TREE INVALID"),
                (MERGE, 4, "PARENTS OBJECT NOT FOUND")):
            invalid_graph = run(rec, "COMMITROOTS", "GENOLD",
                                "GENNEW", git_oid("commit", bad),
                                cwd=d, expected=rc)
            assert reason in invalid_graph
            assert "COMMIT ROOTS VERIFIED" not in invalid_graph
            assert "PARENTS DATA BEGIN" not in invalid_graph
        bad_child_graph = run(rec, "COMMITROOTS", "GENOLD",
                              "GENNEW", git_oid("tree", TREE),
                              cwd=d, expected=8)
        assert "PARENTS CHILD NOT COMMIT" in bad_child_graph
        assert "PARENTS DATA BEGIN" not in bad_child_graph

        # M32: no parent list until every parent's Git root tree
        # independently rehashes and parses in the selected generation.
        roots = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                    git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in roots
        assert "PARENT ROOT TREES VERIFIED" in roots
        assert "PARENTS COUNT 2" in roots
        for n, parent_data in ((1, FIRST_COMMIT), (2, SECOND_PARENT)):
            assert ("PARENTS ORDINAL " + str(n) + " OID "
                    + git_oid("commit", parent_data)) in roots
            assert ("PARENTS ORDINAL " + str(n) + " TREE "
                    + git_oid("tree", TREE)) in roots
        rootzero = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                       git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "PARENTS COUNT 0" in rootzero
        for commit_data, code, reason in (
                (MISSING_ROOT_MERGE, 4, "PARENT ROOT TREE NOT FOUND"),
                (BLOB_ROOT_MERGE, 8, "PARENT ROOT OBJECT NOT TREE"),
                (MALFORMED_ROOT_MERGE, 8, "PARENT ROOT TREE INVALID"),
                (MERGE, 4, "PARENTS OBJECT NOT FOUND")):
            bad_roots = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                            git_oid("commit", commit_data), cwd=d,
                            expected=code)
            assert reason in bad_roots
            assert "PARENTS DATA BEGIN" not in bad_roots
            assert "PARENT ROOT TREES VERIFIED" not in bad_roots
        assert all(len(line) <= 80 for line in roots.splitlines())

        # M31: emit no partial merge-parent list on an invalid link.
        allparents = run(rec, "PARENTS", "GENOLD", "GENNEW",
                         git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in allparents
        assert "PARENTS DATA BEGIN" in allparents
        assert "PARENTS COUNT 2" in allparents
        assert allparents.strip().endswith("PARENTS DATA END")
        for n, parent_data in ((1, FIRST_COMMIT), (2, SECOND_PARENT)):
            assert ("PARENTS ORDINAL " + str(n) + " OID "
                    + git_oid("commit", parent_data)) in allparents
            assert ("PARENTS ORDINAL " + str(n) + " TREE "
                    + git_oid("tree", TREE)) in allparents
        assert all(len(line) <= 80 for line in allparents.splitlines())
        rootparents = run(rec, "PARENTS", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "PARENTS COUNT 0" in rootparents
        assert "PARENTS DATA BEGIN" in rootparents
        for child, rc, reason in (
                (MERGE, 4, "PARENTS OBJECT NOT FOUND"),
                (BLOB_FIRST, 8, "PARENTS OBJECT NOT COMMIT"),
                (MALFORMED_FIRST, 8, "PARENTS OBJECT INVALID")):
            badparents = run(rec, "PARENTS", "GENOLD", "GENNEW",
                             git_oid("commit", child), cwd=d,
                             expected=rc)
            assert reason in badparents
            assert "PARENTS DATA BEGIN" not in badparents
            assert "PARENTS ORDINAL " not in badparents
        invalid_child = run(rec, "PARENTS", "GENOLD", "GENNEW",
                            git_oid("tree", TREE), cwd=d, expected=8)
        assert "PARENTS CHILD NOT COMMIT" in invalid_child
        assert "PARENTS DATA BEGIN" not in invalid_child

        # M30: validate numbered merge parents, not just first-parent.
        for number, parent_data in ((1, FIRST_COMMIT),
                                    (2, SECOND_PARENT)):
            selected_parent = run(
                rec, "PARENT", "GENOLD", "GENNEW",
                git_oid("commit", MERGE2), str(number), cwd=d)
            assert "PARENT VERIFIED ORDINAL " + str(number) in selected_parent
            assert "PARENT OID " + git_oid("commit", parent_data) in selected_parent
            assert "PARENT TREE " + git_oid("tree", TREE) in selected_parent
        for child, number, rc, reason in (
                (MERGE2, "3", 4, "PARENT ORDINAL NOT FOUND"),
                (FIRST_COMMIT, "1", 4, "PARENT ORDINAL NOT FOUND"),
                (MERGE, "2", 4, "PARENT OBJECT NOT FOUND"),
                (BLOB_FIRST, "1", 8, "PARENT OBJECT NOT COMMIT"),
                (MALFORMED_FIRST, "1", 8, "PARENT OBJECT INVALID")):
            missing_parent = run(rec, "PARENT", "GENOLD", "GENNEW",
                                 git_oid("commit", child), number,
                                 cwd=d, expected=rc)
            assert reason in missing_parent
            assert "PARENT VERIFIED" not in missing_parent
        wrong_child = run(rec, "PARENT", "GENOLD", "GENNEW",
                          git_oid("tree", TREE), "1",
                          cwd=d, expected=8)
        assert "PARENT CHILD NOT COMMIT" in wrong_child
        for bad in ("0", "17", "-1", "xyz", ""):
            fail_parent = run(rec, "PARENT", "GENOLD", "GENNEW",
                              git_oid("commit", MERGE2), bad,
                              cwd=d, expected=4)
            assert "ANCESTOR DEPTH MUST BE 1 THROUGH 16" in fail_parent

        # M29: verify entire chain before printing any HISTORY records.
        history = run(rec, "HISTORY", "GENOLD", "GENNEW",
                      git_oid("commit", GRANDCHILD), "2", cwd=d)
        assert "SELECTED 52 GENNEW" in history
        for hop, obj in enumerate((GRANDCHILD, MERGE, FIRST_COMMIT)):
            assert ("HISTORY HOP " + str(hop) + " OID "
                    + git_oid("commit", obj)) in history
            assert ("HISTORY HOP " + str(hop) + " TREE "
                    + git_oid("tree", TREE)) in history
            for line in history.splitlines():
                assert len(line) <= 80
        assert "HISTORY HOPS 2" in history
        assert history.strip().endswith("HISTORY DATA END")
        # M57: all ancestor commit roots close before any records.
        fullhistory = run(
            rec, "HISTORYFULL", "GENOLD", "GENNEW",
            git_oid("commit", GRANDCHILD), "2", cwd=d)
        assert "SELECTED 52 GENNEW" in fullhistory
        assert "HISTORY FULL ROOT CLOSURE VERIFIED" in fullhistory
        assert "HISTORY HOPS 2" in fullhistory
        assert fullhistory.strip().endswith("HISTORY DATA END")
        for hop, obj in enumerate(
                (GRANDCHILD, MERGE, FIRST_COMMIT)):
            assert ("HISTORY HOP " + str(hop) + " OID "
                    + git_oid("commit", obj)) in fullhistory
        # Depth zero checks one commit's entire root snapshot.
        missing_snapshot = run(
            rec, "HISTORYFULL", "GENOLD", "GENNEW",
            git_oid("commit", MISSING_ROOT_COMMIT), "0",
            cwd=d, expected=4)
        assert "ROOT LINK TREE NOT FOUND" in missing_snapshot
        assert "HISTORY DATA BEGIN" not in missing_snapshot
        assert "HISTORY HOP " not in missing_snapshot
        wrong_snapshot = run(
            rec, "HISTORYFULL", "GENOLD", "GENNEW",
            git_oid("commit", BAD_LINK), "0",
            cwd=d, expected=8)
        assert "ROOT LINK OBJECT NOT TREE" in wrong_snapshot
        assert "HISTORY DATA BEGIN" not in wrong_snapshot
        for bad in ("-1", "17", "foo", ""):
            rejected = run(
                rec, "HISTORYFULL", "GENOLD", "GENNEW",
                git_oid("commit", GRANDCHILD), bad,
                cwd=d, expected=4)
            assert "HISTORY DATA BEGIN" not in rejected

        for data, hops, code, reason in (
                (GRANDCHILD, "3", 4, "HISTORY ROOT REACHED"),
                (MISSING_FIRST, "1", 4, "HISTORY COMMIT NOT FOUND"),
                (BLOB_FIRST, "1", 8,
                 "HISTORY OBJECT IS NOT A COMMIT"),
                (MALFORMED_FIRST, "1", 8,
                 "HISTORY COMMIT STRUCTURE INVALID")):
            failhist = run(rec, "HISTORY", "GENOLD", "GENNEW",
                           git_oid("commit", data), hops,
                           cwd=d, expected=code)
            assert reason in failhist
            assert "HISTORY DATA BEGIN" not in failhist
            assert "HISTORY HOP " not in failhist
        for badval in ("0", "17", "-1", "X", ""):
            failhist = run(rec, "HISTORY", "GENOLD", "GENNEW",
                           git_oid("commit", GRANDCHILD), badval,
                           cwd=d, expected=4)
            assert "ANCESTOR DEPTH MUST BE 1 THROUGH 16" in failhist
            assert "HISTORY DATA BEGIN" not in failhist

        # M28: full first-parent ancestry chain, no partial output.
        for depth, obj in ((1, MERGE), (2, FIRST_COMMIT)):
            history = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                          git_oid("commit", GRANDCHILD),
                          str(depth), cwd=disk)
            assert "ANCESTOR VERIFIED DEPTH " + str(depth) in history
            assert "ANCESTOR OID " + git_oid("commit", obj) in history
            assert "ANCESTOR TREE " + git_oid("tree", TREE) in history
        exhausted = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                        git_oid("commit", GRANDCHILD),
                        "3", cwd=disk, expected=4)
        assert "ANCESTOR ROOT REACHED" in exhausted
        assert "ANCESTOR VERIFIED" not in exhausted
        for value in ("0", "17", "-1", "A", "1A", "999", ""):
            bad_depth = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                            git_oid("commit", GRANDCHILD),
                            value, cwd=disk, expected=4)
            assert "ANCESTOR DEPTH MUST BE 1 THROUGH 16" in bad_depth
        for bad, rc, reason in (
                (MISSING_FIRST, 4, "ANCESTOR COMMIT NOT FOUND"),
                (BLOB_FIRST, 8, "ANCESTOR OBJECT IS NOT A COMMIT"),
                (MALFORMED_FIRST, 8, "ANCESTOR COMMIT STRUCTURE INVALID")):
            out = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                      git_oid("commit", bad), "1", cwd=disk, expected=rc)
            assert reason in out
            assert "ANCESTOR VERIFIED" not in out
        for bad in (BAD_PARENT, BAD_COMMIT):
            broken = run(rec, "COMMIT", "GENOLD", "GENNEW",
                         git_oid("commit", bad), cwd=d, expected=8)
            assert "COMMIT STRUCTURE INVALID" in broken
            assert "COMMIT DATA BEGIN" not in broken
        not_commit = run(rec, "COMMIT", "GENOLD", "GENNEW",
                         tree_oid, cwd=d, expected=8)
        assert "OBJECT IS NOT A COMMIT" in not_commit
        assert "COMMIT DATA BEGIN" not in not_commit

        initial_batch = run(rec, "LINKBATCH", "GENOLD",
                            "GENNEW", git_oid("commit", MERGE2),
                            cwd=d)
        assert "LINK DEPTH 2 VERIFIED" in initial_batch
        assert "SELECTED 52 GENNEW" in initial_batch
        (d / "dd:C1GEN").rename(d / "held-new")
        commit_recovered = run(rec, "COMMIT", "GENOLD", "GENNEW",
                               git_oid("commit", MERGE), cwd=d)
        assert "RECOVERED 51 GENOLD" in commit_recovered
        first_recovered = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                              git_oid("commit", MERGE), cwd=d)
        assert "RECOVERED 51 GENOLD" in first_recovered
        assert "FIRST PARENT VERIFIED" in first_recovered
        ancestor_recovered = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                                 git_oid("commit", GRANDCHILD),
                                 "2", cwd=d)
        assert "RECOVERED 51 GENOLD" in ancestor_recovered
        history_recovered = run(rec, "HISTORY", "GENOLD", "GENNEW",
                                git_oid("commit", GRANDCHILD),
                                "2", cwd=d)
        assert "RECOVERED 51 GENOLD" in history_recovered
        parent_recovered = run(rec, "PARENT", "GENOLD", "GENNEW",
                               git_oid("commit", MERGE2), "2", cwd=d)
        assert "RECOVERED 51 GENOLD" in parent_recovered
        assert "PARENT OID " + git_oid("commit", SECOND_PARENT) in parent_recovered
        parents_recovered = run(rec, "PARENTS", "GENOLD", "GENNEW",
                                git_oid("commit", MERGE2), cwd=d)
        assert "RECOVERED 51 GENOLD" in parents_recovered
        assert "PARENTS COUNT 2" in parents_recovered
        roots_recovered = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                              git_oid("commit", MERGE2), cwd=d)
        assert "RECOVERED 51 GENOLD" in roots_recovered
        assert "PARENT ROOT TREES VERIFIED" in roots_recovered
        graph_recovered = run(rec, "COMMITROOTS", "GENOLD",
                              "GENNEW", git_oid("commit", MERGE2), cwd=d)
        assert "RECOVERED 51 GENOLD" in graph_recovered
        assert "COMMIT ROOTS VERIFIED" in graph_recovered
        links_recovered = run(rec, "ROOTLINKS", "GENOLD",
                              "GENNEW", git_oid("commit", MERGE2),
                              cwd=d)
        assert "RECOVERED 51 GENOLD" in links_recovered
        assert "ROOT DIRECT LINKS VERIFIED" in links_recovered
        nested_recovered = run(rec, "NESTLINKS", "GENOLD",
                               "GENNEW", git_oid("commit", MERGE2),
                               cwd=d)
        assert "RECOVERED 51 GENOLD" in nested_recovered
        assert "NESTED ROOT LINKS VERIFIED" in nested_recovered
        deep_recovered = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                             git_oid("commit", DEEP_COMMIT_GOOD), cwd=d)
        assert "RECOVERED 51 GENOLD" in deep_recovered
        assert "DEEP ROOT LINKS VERIFIED" in deep_recovered
        depth_recovered = run(rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                              git_oid("commit", LEVEL3_COMMIT_GOOD),
                              "3", cwd=d)
        assert "RECOVERED 51 GENOLD" in depth_recovered
        assert "LINK DEPTH 3 VERIFIED" in depth_recovered
        assert "HISTORY HOPS 2" in history_recovered
        assert "ANCESTOR OID " + git_oid("commit", FIRST_COMMIT) in ancestor_recovered
        lsroot_recovered = run(rec, "LSROOT", "GENOLD", "GENNEW",
                               git_oid("commit", FIRST_COMMIT), cwd=d)
        verify_tree(lsroot_recovered, "RECOVERED 51 GENOLD", ENTRIES)
        dir_recovered = run(rec, "LSDIR", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT),
                            b"subdir".hex().upper(), cwd=d)
        verify_tree(dir_recovered, "RECOVERED 51 GENOLD",
                    [(b"100644", b"nested.txt", BLOB_OID)])
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
        # M46: direct tree closure must recover independently.
        direct_recovered = run(
            rec, "TREECLOSURE", "GENOLD", "GENNEW",
            git_oid("tree", TREE), cwd=d)
        assert "RECOVERED 51 GENOLD" in direct_recovered
        assert "TREE FULL CLOSURE VERIFIED" in direct_recovered
        assert "TREE DATA END" in direct_recovered
        fullpath_recovered = run(
            rec, "PATHFULL", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d)
        assert "RECOVERED 51 GENOLD" in fullpath_recovered
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in fullpath_recovered
        assert "PATH OBJECT TYPE 3" in fullpath_recovered
        cat_recovered = run(
            rec, "PATHFULLCAT", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d)
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in cat_recovered
        verify_pathcat(cat_recovered, BLOB, "RECOVERED 51 GENOLD")
        dir_recovered = run(
            rec, "PATHFULLDIR", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"subdir".hex().upper(), cwd=d)
        assert "RECOVERED 51 GENOLD" in dir_recovered
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in dir_recovered
        assert "TREE DATA END" in dir_recovered
        raw_recovered = run(
            rec, "TREEPATHCAT", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"README.md".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in raw_recovered
        verify_pathcat(raw_recovered, BLOB, "RECOVERED 51 GENOLD")
        raw_dir_recovered = run(
            rec, "TREEPATHDIR", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"subdir".hex().upper(), cwd=d)
        assert "RECOVERED 51 GENOLD" in raw_dir_recovered
        assert "TREE ROOT FULL CLOSURE VERIFIED" in raw_dir_recovered
        assert "TREE DATA END" in raw_dir_recovered
        meta_recovered = run(
            rec, "TREEPATH", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"submodule".hex().upper(), cwd=d)
        assert "RECOVERED 51 GENOLD" in meta_recovered
        assert "TREE ROOT FULL CLOSURE VERIFIED" in meta_recovered
        assert "PATH GITLINK (EXTERNAL COMMIT)" in meta_recovered
        recovered_batch = run(rec, *batch_args, cwd=d)
        assert "RECOVERED 51 GENOLD" in recovered_batch
        assert "BATCH ALL POSITIVE CHECKS PASSED" in recovered_batch
        assert "BATCH ROOT CLOSURE REUSES " in recovered_batch
        assert "BATCH SEEK INDEX REUSES " in recovered_batch
        assert "BATCH NON COMMIT CHILD RC8 VERIFIED" in recovered_batch
        assert "BATCH MISSING CHILD RC4 VERIFIED" in recovered_batch
        batch_recovered = run(rec, "LINKBATCH", "GENOLD",
                              "GENNEW", git_oid("commit", MERGE2),
                              cwd=d)
        assert "RECOVERED 51 GENOLD" in batch_recovered
        assert "LINK DEPTH 2 VERIFIED" in batch_recovered
        # M41/M42: the same strict local-directory proof must
        # operate against an independently verified older slot.
        for cmd, marker, extra in (
                ("LSDIRV", "DIRECTORY LINKS VERIFIED", []),
                ("LSDIRDEPTH", "DIRECTORY LINK DEPTH 1 VERIFIED",
                 ["1"]),
                ("LSDIRFULL", "DIRECTORY FULL CLOSURE VERIFIED",
                 [])):
            check = run(
                rec, cmd, "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                b"subdir".hex().upper(), *extra, cwd=d)
            assert "RECOVERED 51 GENOLD" in check
            assert marker in check
            assert "TREE DATA END" in check
        (d / "dd:C0GEN").rename(d / "held-old")
        failed = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid,
                     cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in failed
        assert "TREE DATA BEGIN" not in failed
        commit_failed = run(rec, "COMMIT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in commit_failed
        assert "COMMIT DATA BEGIN" not in commit_failed
        first_failed = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                           git_oid("commit", MERGE), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in first_failed
        assert "FIRST PARENT VERIFIED" not in first_failed
        ancestor_failed = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                              git_oid("commit", GRANDCHILD),
                              "2", cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in ancestor_failed
        assert "ANCESTOR VERIFIED" not in ancestor_failed
        history_failed = run(rec, "HISTORY", "GENOLD", "GENNEW",
                             git_oid("commit", GRANDCHILD),
                             "2", cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in history_failed
        assert "HISTORY DATA BEGIN" not in history_failed
        parent_failed = run(rec, "PARENT", "GENOLD", "GENNEW",
                            git_oid("commit", MERGE2), "2",
                            cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in parent_failed
        assert "PARENT VERIFIED" not in parent_failed
        parents_failed = run(rec, "PARENTS", "GENOLD", "GENNEW",
                             git_oid("commit", MERGE2),
                             cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in parents_failed
        assert "PARENTS DATA BEGIN" not in parents_failed
        roots_failed = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                           git_oid("commit", MERGE2), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in roots_failed
        assert "PARENTS DATA BEGIN" not in roots_failed
        graph_failed = run(rec, "COMMITROOTS", "GENOLD",
                           "GENNEW", git_oid("commit", MERGE2),
                           cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in graph_failed
        assert "PARENTS DATA BEGIN" not in graph_failed
        links_failed = run(rec, "ROOTLINKS", "GENOLD",
                           "GENNEW", git_oid("commit", MERGE2),
                           cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in links_failed
        assert "PARENTS DATA BEGIN" not in links_failed
        nested_failed = run(rec, "NESTLINKS", "GENOLD",
                            "GENNEW", git_oid("commit", MERGE2),
                            cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in nested_failed
        assert "PARENTS DATA BEGIN" not in nested_failed
        deep_failed = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                          git_oid("commit", DEEP_COMMIT_GOOD),
                          cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in deep_failed
        assert "PARENTS DATA BEGIN" not in deep_failed
        depth_failed = run(rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                           git_oid("commit", LEVEL3_COMMIT_GOOD),
                           "3", cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in depth_failed
        assert "PARENTS DATA BEGIN" not in depth_failed
        lsroot_failed = run(rec, "LSROOT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT),
                            cwd=d, expected=8)
        assert "TREE DATA BEGIN" not in lsroot_failed
        dir_failed = run(rec, "LSDIR", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         b"subdir".hex().upper(), cwd=d, expected=8)
        assert "TREE DATA BEGIN" not in dir_failed
        path_failed = run(rec, "PATH", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          b"README.md".hex().upper(), cwd=d, expected=8)
        assert "PATH OBJECT TYPE" not in path_failed
        full_failed = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                          git_oid("commit", FIRST_COMMIT),
                          b"README.md".hex().upper(), cwd=d, expected=8)
        assert "PATH DATA BEGIN" not in full_failed
        direct_failed = run(
            rec, "TREECLOSURE", "GENOLD", "GENNEW",
            git_oid("tree", TREE), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in direct_failed
        assert "TREE FULL CLOSURE VERIFIED" not in direct_failed
        assert "TREE DATA BEGIN" not in direct_failed
        fullpath_failed = run(
            rec, "PATHFULL", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in fullpath_failed
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in fullpath_failed
        assert "PATH OBJECT TYPE" not in fullpath_failed
        cat_failed = run(
            rec, "PATHFULLCAT", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in cat_failed
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in cat_failed
        assert "PATH DATA BEGIN" not in cat_failed
        dir_failed = run(
            rec, "PATHFULLDIR", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"subdir".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in dir_failed
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" not in dir_failed
        assert "TREE DATA BEGIN" not in dir_failed
        raw_failed = run(
            rec, "TREEPATHCAT", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"README.md".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in raw_failed
        assert "TREE ROOT FULL CLOSURE VERIFIED" not in raw_failed
        assert "PATH DATA BEGIN" not in raw_failed
        raw_dir_failed = run(
            rec, "TREEPATHDIR", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"subdir".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in raw_dir_failed
        assert "TREE ROOT FULL CLOSURE VERIFIED" not in raw_dir_failed
        assert "TREE DATA BEGIN" not in raw_dir_failed
        meta_failed = run(
            rec, "TREEPATH", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"submodule".hex().upper(), cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in meta_failed
        assert "TREE ROOT FULL CLOSURE VERIFIED" not in meta_failed
        assert "PATH GITLINK" not in meta_failed
        invalid_batch = run(rec, *batch_args, cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in invalid_batch
        assert "BATCH ALL POSITIVE CHECKS PASSED" not in invalid_batch
        assert "BATCH ROOT CLOSURE REUSES " not in invalid_batch
        assert "BATCH SEEK INDEX REUSES " not in invalid_batch
        assert "BATCH NON COMMIT CHILD RC8 VERIFIED" not in invalid_batch
        assert "BATCH MISSING CHILD RC4 VERIFIED" not in invalid_batch
        assert "TREE DATA BEGIN" not in invalid_batch
        batch_failed = run(rec, "LINKBATCH", "GENOLD",
                           "GENNEW", git_oid("commit", MERGE2),
                           cwd=d, expected=8)
        assert "NO FULLY VERIFIED GENERATION" in batch_failed
        assert "NESTED ROOT LINKS VERIFIED" not in batch_failed
        assert "PARENTS DATA BEGIN" not in batch_failed
        for cmd, extra in (("LSDIRV", []),
                           ("LSDIRDEPTH", ["1"]),
                           ("LSDIRFULL", [])):
            check = run(
                rec, cmd, "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                b"subdir".hex().upper(), *extra,
                cwd=d, expected=8)
            assert "NO FULLY VERIFIED GENERATION" in check
            assert "DIRECTORY LINKS VERIFIED" not in check
            assert "DIRECTORY LINK DEPTH" not in check
            assert "DIRECTORY FULL CLOSURE VERIFIED" not in check
            assert "PATH OBJECT TYPE" not in check
            assert "TREE DATA BEGIN" not in check
        (d / "held-old").rename(d / "dd:C0GEN")
        (d / "held-new").rename(d / "dd:C1GEN")
        restored = run(rec, "TREE", "GENOLD", "GENNEW", tree_oid, cwd=d)
        verify_tree(restored, "SELECTED 52 GENNEW", ENTRIES)
        final_commit = run(rec, "COMMIT", "GENOLD", "GENNEW",
                           git_oid("commit", FIRST_COMMIT), cwd=d)
        assert "SELECTED 52 GENNEW" in final_commit
        assert "COMMIT TREE " + git_oid("tree", TREE) in final_commit
        first_restored = run(rec, "FIRSTPAR", "GENOLD", "GENNEW",
                             git_oid("commit", MERGE), cwd=d)
        assert "SELECTED 52 GENNEW" in first_restored
        assert "FIRST PARENT VERIFIED" in first_restored
        ancestor_restored = run(rec, "ANCESTOR", "GENOLD", "GENNEW",
                                git_oid("commit", GRANDCHILD),
                                "2", cwd=d)
        assert "SELECTED 52 GENNEW" in ancestor_restored
        history_restored = run(rec, "HISTORY", "GENOLD", "GENNEW",
                               git_oid("commit", GRANDCHILD),
                               "2", cwd=d)
        assert "SELECTED 52 GENNEW" in history_restored
        assert "HISTORY HOPS 2" in history_restored
        parent_restored = run(rec, "PARENT", "GENOLD", "GENNEW",
                              git_oid("commit", MERGE2), "2", cwd=d)
        assert "SELECTED 52 GENNEW" in parent_restored
        assert "PARENT OID " + git_oid("commit", SECOND_PARENT) in parent_restored
        parents_restored = run(rec, "PARENTS", "GENOLD", "GENNEW",
                               git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in parents_restored
        assert "PARENTS COUNT 2" in parents_restored
        roots_restored = run(rec, "PARENTROOTS", "GENOLD", "GENNEW",
                             git_oid("commit", MERGE2), cwd=d)
        assert "SELECTED 52 GENNEW" in roots_restored
        assert "PARENT ROOT TREES VERIFIED" in roots_restored
        graph_restored = run(rec, "COMMITROOTS", "GENOLD",
                             "GENNEW", git_oid("commit", MERGE2),
                             cwd=d)
        assert "SELECTED 52 GENNEW" in graph_restored
        assert "COMMIT ROOTS VERIFIED" in graph_restored
        links_restored = run(rec, "ROOTLINKS", "GENOLD",
                             "GENNEW", git_oid("commit", MERGE2),
                             cwd=d)
        assert "SELECTED 52 GENNEW" in links_restored
        assert "ROOT DIRECT LINKS VERIFIED" in links_restored
        nested_restored = run(rec, "NESTLINKS", "GENOLD",
                              "GENNEW", git_oid("commit", MERGE2),
                              cwd=d)
        assert "SELECTED 52 GENNEW" in nested_restored
        assert "NESTED ROOT LINKS VERIFIED" in nested_restored
        deep_restored = run(rec, "DEEPLINKS", "GENOLD", "GENNEW",
                            git_oid("commit", DEEP_COMMIT_GOOD), cwd=d)
        assert "SELECTED 52 GENNEW" in deep_restored
        assert "DEEP ROOT LINKS VERIFIED" in deep_restored
        depth_restored = run(rec, "DEPTHLINKS", "GENOLD", "GENNEW",
                             git_oid("commit", LEVEL3_COMMIT_GOOD),
                             "3", cwd=d)
        assert "SELECTED 52 GENNEW" in depth_restored
        assert "LINK DEPTH 3 VERIFIED" in depth_restored
        assert "ANCESTOR OID " + git_oid("commit", FIRST_COMMIT) in ancestor_restored
        final_path = run(rec, "PATH", "GENOLD", "GENNEW",
                         git_oid("commit", FIRST_COMMIT),
                         b"subdir/nested.txt".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in final_path
        assert "PATH OBJECT TYPE 3 SIZE 3" in final_path
        final_dir = run(rec, "LSDIR", "GENOLD", "GENNEW",
                        git_oid("commit", FIRST_COMMIT),
                        b"subdir".hex().upper(), cwd=d)
        verify_tree(final_dir, "SELECTED 52 GENNEW",
                    [(b"100644", b"nested.txt", BLOB_OID)])
        for cmd, marker, extra in (
                ("LSDIRV", "DIRECTORY LINKS VERIFIED", []),
                ("LSDIRDEPTH", "DIRECTORY LINK DEPTH 1 VERIFIED",
                 ["1"]),
                ("LSDIRFULL", "DIRECTORY FULL CLOSURE VERIFIED",
                 [])):
            check = run(
                rec, cmd, "GENOLD", "GENNEW",
                git_oid("commit", FIRST_COMMIT),
                b"subdir".hex().upper(), *extra, cwd=d)
            assert "SELECTED 52 GENNEW" in check
            assert marker in check
            assert "TREE DATA END" in check
        direct_restored = run(
            rec, "TREECLOSURE", "GENOLD", "GENNEW",
            git_oid("tree", TREE), cwd=d)
        assert "SELECTED 52 GENNEW" in direct_restored
        assert "TREE FULL CLOSURE VERIFIED" in direct_restored
        assert "TREE DATA END" in direct_restored
        fullpath_restored = run(
            rec, "PATHFULL", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in fullpath_restored
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in fullpath_restored
        assert "PATH OBJECT TYPE 3" in fullpath_restored
        cat_restored = run(
            rec, "PATHFULLCAT", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"README.md".hex().upper(), cwd=d)
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in cat_restored
        verify_pathcat(cat_restored, BLOB)
        dir_restored = run(
            rec, "PATHFULLDIR", "GENOLD", "GENNEW",
            git_oid("commit", FIRST_COMMIT),
            b"subdir".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in dir_restored
        assert "COMMIT ROOT FULL CLOSURE VERIFIED" in dir_restored
        assert "TREE DATA END" in dir_restored
        raw_restored = run(
            rec, "TREEPATHDIR", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"subdir".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in raw_restored
        assert "TREE ROOT FULL CLOSURE VERIFIED" in raw_restored
        assert "TREE DATA END" in raw_restored
        raw_cat_restored = run(
            rec, "TREEPATHCAT", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"README.md".hex().upper(), cwd=d)
        assert "TREE ROOT FULL CLOSURE VERIFIED" in raw_cat_restored
        verify_pathcat(raw_cat_restored, BLOB)
        meta_restored = run(
            rec, "TREEPATH", "GENOLD", "GENNEW",
            git_oid("tree", TREE),
            b"submodule".hex().upper(), cwd=d)
        assert "SELECTED 52 GENNEW" in meta_restored
        assert "TREE ROOT FULL CLOSURE VERIFIED" in meta_restored
        assert "PATH GITLINK (EXTERNAL COMMIT)" in meta_restored
        restored_batch = run(rec, *batch_args, cwd=d)
        assert "SELECTED 52 GENNEW" in restored_batch
        assert "BATCH ALL POSITIVE CHECKS PASSED" in restored_batch
        assert "BATCH ROOT CLOSURE REUSES " in restored_batch
        assert "BATCH SEEK INDEX REUSES " in restored_batch
        assert "BATCH NON COMMIT CHILD RC8 VERIFIED" in restored_batch
        assert "BATCH MISSING CHILD RC4 VERIFIED" in restored_batch
        restored_full = run(rec, "PATHCAT", "GENOLD", "GENNEW",
                            git_oid("commit", FIRST_COMMIT),
                            b"big.bin".hex().upper(), cwd=d)
        verify_pathcat(restored_full, BIG)
        print("NATIVE C89 TREE BINARY NAMEHEX, EMPTY, MALFORMED, "
              "NON-TREE, COMMIT, LSROOT, NESTED PATH AND FAIL-CLOSED TESTS PASSED")


if __name__ == "__main__":
    main()
