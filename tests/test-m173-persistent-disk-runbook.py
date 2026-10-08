#!/usr/bin/env python3
"""Cross-check real CMS geometry and non-destructive GATE requirements."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
runbook = (root / "docs" / "M173_PERSISTENT_DISK_RUNBOOK.md").read_text()
a = (root / "src" / "M173CHK.EXEC").read_text()
b = (root / "src" / "M174CHK.EXEC").read_text()
c = (root / "src" / "M175CHK.EXEC").read_text()
d = (root / "src" / "M176CHK.EXEC").read_text()

# All sizes are 4 KiB CMS blocks on 3390; independent of host CCKD
# compressed backing-file size.
blocks_per_cyl = 180
target_cyl = 1600
minimum_free = 180000
assert target_cyl * blocks_per_cyl == 288000
assert target_cyl * blocks_per_cyl > minimum_free
assert minimum_free // blocks_per_cyl == 1000
for check in (a, b, c, d):
    assert "parse upper arg datafm extra" in check
    assert "verify(datafm,'BCDEFGHIJKLMNOPQRSTUVWXYZ')" in check
    assert "'STAGE' datafm" in check
    assert "'ERASE'" not in check, "Target checks must not erase failed files"
for check, minimum in ((a,180000),(b,4096)):
    assert f"if avail<{minimum}" in check
    assert "word(d.di,4)='R/W'" in check
    assert "word(d.di,7)='4096'" in check
    assert "FAILED OUTPUT RETAINED FOR DIAGNOSIS" in check
assert "M171NET" in a and "'PACK A'" in a
assert "M171NET" in b and "META A 1 (STEM" in b
assert "M171NET" in c and "META A 1 (STEM" in c
assert "M171NET" in d and "META A 1 (STEM" in d
for phrase in (
    "CP QUERY VIRTUAL DASD",
    "CP QUERY MDISK 191 LOCATION",
    "CP QUERY DASD ALL",
    "CP QUERY ALLOC MAP ALL",
    "DIRM USEDEXT V=M01RES",
    "DIRM FREEXT V=M01RES",
    "Never infer usable cylinder gaps",
    "1600",
    "180,000",
    "22841",
):
    assert phrase.lower() in runbook.lower(),phrase
assert "FORMAT" in runbook
assert "Never choose VDEV 0192" in runbook
assert "not been provisioned" in runbook.lower()
for evidence in (
    "real CP extent inventory",
    "CP QUERY DIRMAINT",
    "CP XAUTOLOG DIRMAINT",
    "WHERETO DATADVH",
    "DIRM USEDEXT V=M01RES",
    "DIRM FREEXT V=M01RES",
    "cylinders **1–10999**",
    "cylinders **1–20**",
    "not**\n  number of free cylinders",
    "NO PERMANENT MINIDISK EXTENT CONFIRMED",
):
    assert evidence.lower() in runbook.lower(), evidence

assert "MDISK <VDEV> 3390 <START> <CYLINDERS> <VOLSER> <MODE>" in runbook
print("M173 PERMANENT CMS DATA DISK EVIDENCE AND SAFETY GATES PASSED")
