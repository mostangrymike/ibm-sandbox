#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
imp = (root / "src" / "GITIMP.EXEC").read_text()
wt = (root / "src" / "GITWT.EXEC").read_text()
chk = (root / "src" / "M164CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 164

for needle in (
    "if command = 'IMPORT-OBJECT' then do",
    "if command = 'CHECKOUT-FILE' then do",
    "if command = 'STATUS' then do",
    "if command = 'ADD' then do",
    "command = 'HASH-WORKFILE'",
    "command = 'WRITE-WORKFILE'",
):
    assert needle in g

assert "'EXEC GITIMP' rest" in g
assert "'EXEC GITWT CHECKOUT' rest" in g
assert "'EXEC GITWT STATUS' rest" in g
assert "'EXEC GITWT ADD' rest" in g
assert "text = strip(wline.i,'T')" in g
assert "if final = '1' then hex = hex || '0A'" in g

for needle in (
    "GITREC CATHEX GITFIX M15NEW",
    "OBJECT DATA BEGIN",
    "OBJECT DATA END",
    "IMPORTED",
    "GIT VERIFY-OBJECT",
):
    assert needle in imp

for protected in ("GITFIX STAGE", "GITFIX INDEX", "GITFIX SEEK",
                  "GITFIX GEN", "M15NEW STAGE", "M15NEW INDEX",
                  "M15NEW SEEK", "M15NEW GEN"):
    assert f"DISKW {protected}" not in imp
    assert f"ERASE {protected}" not in imp

for needle in (
    "M164 CHECKOUT DIRECT RC0",
    "M164 INITIAL CLEAN MAP PASS",
    "M164 VERIFIED IMPORT PASS",
    "M164 MODIFIED HASH PASS",
    "M164 STAGED MAP PASS",
    "M164 LOOSE OBJECT PASS",
    "M164 DISPOSABLE CLEANUP PASS",
    "M164 PRACTICAL PORCELAIN TARGET GATE PASS",
):
    assert needle in chk
assert "ERASE M164TST DATA A" in chk
assert "ERASE GITWORK REPO A" in chk
assert "if rc=28 then return 0" in chk
assert "if rc\\=28 then return 0" not in chk
assert "cmd='EXEC GIT CHECKOUT-FILE HEAD" in chk
assert "grc=rc" in chk
assert "M164 CHECKOUT FAIL RC' grc" in chk
assert "address command 'EXEC GIT STATUS'" in chk
assert "address command 'EXEC GIT ADD src/GIT.EXEC'" in chk
assert "expected='0FCE3C85DD9335CA7A4868E806F09B890D115F80'" in chk
assert "word(m.2,6)\\='0'" in chk
assert "cmd='EXEC GIT IMPORT-OBJECT' base" in chk
assert "cmd='EXEC GIT VERIFY-OBJECT' base" in chk
assert "address command 'GIT " not in chk
assert "cmd='GIT " not in chk

for needle in (
    "GITREC PATHFULLCAT GITFIX M15NEW",
    "checkout target exists; M164 refuses overwrite",
    "WORKTREE OID",
    "STATUS SUMMARY TRACKED",
    "ADDED",
    "GITWORK REPO A",
    "COMMIT ROOT FULL CLOSURE VERIFIED",
    "PATH DATA BEGIN",
    "PATH DATA END",
):
    assert needle in wt

for path in (root / "src" / "GIT.EXEC",
             root / "src" / "GITVREF.EXEC",
             root / "src" / "GITIMP.EXEC",
             root / "src" / "GITWT.EXEC",
             root / "src" / "M164CHK.EXEC"):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

def git_blob_oid(data: bytes) -> str:
    preimage = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(preimage).hexdigest().upper()

def workfile_oid(records, final_lf):
    data = b"\n".join(line.rstrip(b" ") for line in records)
    if final_lf:
        data += b"\n"
    return git_blob_oid(data)

source = b"alpha\n  beta\n"
source_oid = git_blob_oid(source)
cms_records = [b"alpha" + b" " * 75, b"  beta" + b" " * 74]
assert workfile_oid(cms_records, 1) == source_oid
assert workfile_oid(cms_records, 0) != source_oid

modified = [b"alpha" + b" " * 75, b"  BETA" + b" " * 74]
modified_oid = workfile_oid(modified, 1)
assert modified_oid != source_oid

base = source_oid
stage = base
work = source_oid
assert work == stage == base
work = modified_oid
assert work != stage and stage == base
stage = work
assert work == stage and stage != base

body = b"tree test\n"
oid = git_blob_oid(body)
hex_body = body.hex().upper()
cathex = [
    f"SEEK OBJECT OID {oid} OBJ 1 TYPE 3 SIZE {len(body)} PREFIX 74726565",
    "OBJECT DATA BEGIN",
    "HEX " + hex_body,
    "OBJECT DATA END",
]
meta = cathex[0].split()
assert meta[0:3] == ["SEEK", "OBJECT", "OID"]
assert meta[3] == oid and meta[6] == "TYPE" and meta[7] == "3"
assert meta[8] == "SIZE" and int(meta[9]) == len(body)
rebuilt = bytes.fromhex(cathex[2].split()[1])
assert git_blob_oid(rebuilt) == oid

print("M164 PRACTICAL WORKTREE HOST MODEL PASSED")


# Model the exact GITWT EBCDIC<->ASCII table on the sealed checkout fixture.
e2a_hex = (
    "000102031A091A7F1A1A1A0B0C0D0E0F"
    "101112131A1A081A18191A1A1C1D1E1F"
    "1A1A1C1A1A0A171B1A1A1A1A1A050607"
    "1A1A161A1A1E1A041A1A1A1A14151A1A"
    "20A6E180EB909FE2AB8B9B2E3C282B7C"
    "26A9AA9CDBA599E3A89E21242A293B5E"
    "2D2FDFDC9ADDDE989DACBA2C255F3E3F"
    "D78894B0B1B2FCD6FB603A2340273D22"
    "F861626364656667686996A4F3AFAEC5"
    "8C6A6B6C6D6E6F7071729787CE93F1FE"
    "C87E737475767778797AEFC0DA5BF2F9"
    "B5B6FDB7B8B9E6BBBCBD8DD9BF5DD8C4"
    "7B414243444546474849CBCABEE8ECED"
    "7D4A4B4C4D4E4F505152A1ADF5F4A38F"
    "5CE7535455565758595AA0858EE9E4D1"
    "30313233343536373839B3F7F0FAA7FF"
)
e2a = bytes.fromhex(e2a_hex)
assert len(e2a) == 256

def ascii_to_ebcdic(data: bytes) -> bytes:
    out = bytearray()
    for b in data:
        hits = [i for i, x in enumerate(e2a) if x == b]
        assert hits, hex(b)
        out.append(hits[0])
    return bytes(out)

def ebcdic_to_ascii(data: bytes) -> bytes:
    return bytes(e2a[b] for b in data)

fixture = (root / "src" / "GIT.EXEC").read_bytes()
# Current file is a superset of the sealed text repertoire; validate all
# non-LF bytes used by the real source.
for line in fixture.splitlines():
    cms = ascii_to_ebcdic(line)
    assert ebcdic_to_ascii(cms) == line

assert "verify(translate(ah)" not in wt
assert "do ai=1 to length(ah)" in wt
assert "pos(substr(ah,ai,1),'0123456789ABCDEF')" in wt
assert "FILEDEF WTOUT" not in wt
assert "'EXECIO 0 DISKW' wfn wft wfm '1 F 80 (FINIS'" in wt
assert "'EXECIO' rec.0 'DISKW' wfn wft wfm" in wt
assert "'1 F 80 (STEM REC. FINIS'" in wt
print("M164 EBCDIC TABLE ROUND TRIP PASSED")
