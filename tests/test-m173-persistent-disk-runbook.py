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
# The live DirMaint autolog did not remain running. Keep the
# read-only 2CC source discovery ahead of any map-writing command.
for evidence in (
    "HCPCLS6056I",
    "USER DSC LOGOFF AS DIRMAINT",
    "STATE USER DIRECT C",
    "LISTFILE * DIRECT C (ALLOC",
    "LISTFILE ACCESS DATADVH *",
    "LISTFILE CONFIG* DATADVH *",
    "LISTFILE WHERETO DATADVH *",
    "not fully read-only",
    "current",
    "CP directory",
):
    assert evidence.lower() in runbook.lower(), evidence
# A user directory was found on the known MAINT 2CC source disk.
# Use DIRMAP's explicit C output filemode; DISKMAP would write to A.
for evidence in (
    "USER DIRECT C1 F 80, 4282 records",
    "QUERY DISK C",
    "STATE USER MDISKMAP C",
    "DIRMAP USER DIRECT C C",
    "not on A",
    "DIRECTXA",
    "PIPE < USER MDISKMAP C | LOCATE /M01RES/ | CONSOLE",
    "not independently",
):
    assert evidence.lower() in runbook.lower(), evidence
# The first real M01RES filter omitted all blank-volser continuation
# rows and most minidisks. Require entire C-only map to be inspected.
for evidence in (
    "USER MDISKMAP C1 written - no errors",
    "392 records and ten allocated 4K blocks",
    "10017-cylinder inferred model",
    "11000 cylinders",
    "omits other",
    "PIPE < USER MDISKMAP C | TAKE 100 | CONSOLE",
    "PIPE < USER MDISKMAP C | DROP 100 | TAKE 100 | CONSOLE",
    "PIPE < USER MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE",
    "PIPE < USER MDISKMAP C | DROP 300 | CONSOLE",
    "NOT the entire M01RES",
):
    assert evidence.lower() in runbook.lower(), evidence
# The second DIRMAP chunk revealed a small and a possibly extended gap.
for evidence in (
    "9413-9419",
    "9420-9439",
    "9440-10016",
    "9440-10999",
    "1560 consecutive cylinders",
    "280800 blocks",
    "CP QUERY DASD DETAILS 0123",
    "CP QUERY MDISK 0123 LOCATION",
    "FULLPACK DEFINES",
    "3390 10999",
    "df -h /home/admin/vm630",
):
    assert evidence.lower() in runbook.lower(),evidence
# A second directory map section exposed the independent VMCOM1 gap.
# Its candidate must fit the 3390-9 inferred ceiling, without assuming
# any additional cylinders beyond 10016.
vmcom_gap_start, vmcom_gap_end = 5936, 10016
vmcom_start, vmcom_end = 6000, 7599
assert vmcom_gap_end - vmcom_gap_start + 1 == 4081
assert vmcom_gap_start <= vmcom_start <= vmcom_end <= vmcom_gap_end
assert vmcom_end - vmcom_start + 1 == target_cyl
for evidence in (
    "VMCOM1 is the preferred candidate",
    "6VMHCD20 0300",
    "5756–5935",
    "5936–10016",
    "4081 cylinders",
    "6000",
    "7599",
    "0127",
    "dasd5",
    "both VMCOM1 (the proposed target and MAINT 2CC source)",
    "M01RES (which contains the active CP directory)",
    "CP QUERY DASD DETAILS 0127",
    "CP QUERY MDISK 02CC LOCATION",
    "CP QUERY MDISK 049E LOCATION",
    "CP QUERY MDISK 0551 LOCATION",
    "readlink -f /proc/ACTUAL_HERCULES_PID/cwd",
    "independently",
    "No `USER DIRECT` source edits",
):
    assert evidence.lower() in runbook.lower(),evidence
# Physical CP, not just DIRMAP, verified all three volumes at 11000 CYL.
# Candidate must fit known real bounds and the explicit mapped free interval.
cp_cylinders = 11000
assert cp_cylinders > vmcom_gap_end >= vmcom_end
for evidence in (
    "REAL CP DASD GEOMETRY VERIFIED",
    "0123 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER M01RES CYLS 11000",
    "0126 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER M01W01 CYLS 11000",
    "0127 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER VMCOM1 CYLS 11000",
    "MAINT 0123 MAINT 0123 3390 M01RES 0123 start0 size11000",
    "MAINT 0124 MAINT 0124 3390 M01W01 0126 start0 size11000",
    "scripts/map-cms-minidisk.sh",
    "REAL RDEV",
    "not yet live confirmations",
    "new MDISK",
    "are all still pending",
):
    assert evidence.lower() in runbook.lower(), evidence
print("M173 PERMANENT CMS DATA DISK EVIDENCE AND SAFETY GATES PASSED")
