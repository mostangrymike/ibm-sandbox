#!/usr/bin/env python3
"""M173 z/VM 6.3 non-mutating CP directory inventory source guard."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / "src/M173VQ.ASSEMBLE").read_text()
plan = (root / "docs/M173_DIRECTORY_CHANGE_PLAN.md").read_text()
runbook = (root / "docs/M173_PERSISTENT_DISK_RUNBOOK.md").read_text()
state = (root / "CHAT_STATE.md").read_text()

assert max(map(len, src.splitlines())) <= 71
assert src.startswith("M173VQ   CSECT")
# IBM z/VM CP Programming Services: DIAGNOSE has NO mnemonic.
# The CMS XF assembler rejects an unresolved DIAG macro as IFO078.
# Parse the exact encoded S-format instruction that IBM documents.
import re
m = re.search(r"DC\s+X'([0-9A-F]{2})',X'([0-9A-F]{2})',"
              r"XL2'([0-9A-F]{4})'", src)
assert m is not None
machine = bytes.fromhex("".join(m.groups()))
assert machine == bytes.fromhex("8324025C")
assert machine[0] == 0x83
assert (machine[1] >> 4) == 2       # Rx = parameter-list pointer
assert (machine[1] & 0x0F) == 4     # Ry = data-buffer pointer
base_disp = int.from_bytes(machine[2:], "big")
assert (base_disp >> 12) == 0       # base=0, no register addition
assert (base_disp & 0x0FFF) == 0x25C
assert "         DIAG  " not in src
assert "DIAGNOSE has no instruction mnemonic" in src
assert "BNZ   DFAIL" in src
assert "LTR   5,5" in src
assert "L     5,=F'65520'" in src
assert "C     2,=F'65520'" in src
assert "C     7,=F'60'" in src
assert "LINEWRT DATA=((8),60),ERROR=OUTERR" in src
assert "LINEWRT DATA=(OKMSG,L'OKMSG),ERROR=DFAIL" in src
assert "DC    F'48'" in src
assert "DC    F'0'" in src
assert "DC    CL8'LSTMDISK'" in src
assert src.count("DC    CL8'*'") == 3  # all owners/devices/systems
assert "DC    CL8'VMCOM1'" in src
assert "DS    0D\nPARMS" in src
assert "DS    CL65520" in src
assert "QUERY COMPLETE NOT ACTIVATION APPROVAL" in src
assert "QUERY FAILED NO COMPLETE INVENTORY" in src
for forbidden in ("FILEDEF", "DISKW", "ERASE ", "DIRECTXA ",
                  "FORMAT ", "LINK ", "ACCESS ", "SPOOL ",
                  "CP SET", "CP DEFINE", "STOR="):
    assert forbidden not in src.upper(), forbidden

# Ensure a mock page of the documented 60-byte VMUDQ rows fits,
# while truncation/incomplete records fail closed in assembler.
def make_row(owner, vdev, volser, dtype, start, size, system=""):
    row = (f"{owner:<8} {vdev:<4} {volser:<6} {dtype:<8} "
           f"{start:<10} {size:<10} {system:<8}")
    assert len(row) == 60
    return row

rows = [
    make_row("PMAINT", "0141", "VMCOM1", "3390", "0000000000", "END"),
    make_row("6VMHCD20", "0300", "VMCOM1", "3390", "0000005756",
             "0000000180", "SYS1"),
    make_row("PMAINT", "0551", "VMCOM1", "3390", "0000000572",
             "0000000040"),
]
assert len("".join(rows)) == 180
assert 65520 // 60 == 1092
assert 65520 % 60 == 0
assert 65580 // 60 == 1093
assert "VMCOM1" in rows[0] and "END" in rows[0]
assert rows[1][0:8].strip() == "6VMHCD20"
assert rows[1][9:13] == "0300"
assert rows[1][14:20].strip() == "VMCOM1"
# An END/fullpack entry is not a disjoint allocation, nor
# permission to ignore all other ordinary physical conflicts.
assert "END" in rows[0][41:51] and "END" not in rows[1][41:51]

for text, expected in (
    (plan, ("Gate 5e", "PMAINT 0141", "M173VQ", "CP QUERY PRIVCLASS",
            "6.3", "No non-EDIT DIRECTXA")),
    (runbook, ("PMAINT 0141", "VMUDQ", "M173VQ", "6.3",
               "not an activation approval")),
    (state, ("2026-10-09", "ABCDEFG", "PMAINT 0141", "M173VQ",
             "NOT target-tested")),
):
    for marker in expected:
        assert marker.lower() in text.lower(), marker


# Latest real CMS MAINT: active CP fullpack is 11000 cylinders,
# NOT source DIRMAP's model-inferred 10017 cylinders.
for marker in (
    "2026-10-09 08:55 CDT",
    "PMAINT 0141",
    "11000",
    "IFO078 UNDEFINED OP CODE",
    "Ready(00008)",
    "X'83',X'24',XL2'025C'",
    "compile-only",
):
    assert marker.lower() in plan.lower(), marker
for marker in (
    "full physical cylinders 0–10999",
    "IFO078 UNDEFINED OP CODE",
    "only",
):
    assert marker.lower() in runbook.lower(), marker
assert "ASSEMBLE M173VQ" in state
assert "COMPILE-ONLY" in state
assert "No successful" in state
assert 11000 - 1 == 10999
assert 6000 >= 0 and 7599 <= 10999


# CP DIAG X'25C' allows a 48-byte 8-aligned parameter list only if
# it resides entirely inside one 4096-byte page. Host-model every
# possible 8-byte aligned offset, including the last safe position.
for offset in range(0, 4096, 8):
    accepted = offset <= 4048
    in_one_page = (offset + 48 <= 4096)
    assert accepted == in_one_page
assert "         LA    2,PARMS" in src
assert "         LR    3,2" in src
assert "         N     3,=X'00000FFF'" in src
assert "         C     3,=F'4048'" in src
assert "         BH    DFAIL" in src
assert src.index("         LR    3,2") < src.index(
    "         DC    X'83',X'24',XL2'025C'")
assert "         DS    0D\nPARMS" in src
# CP documented raw DIAG interface: Rx=2 receives bytes moved,
# Ry+1=5 receives a status code, and nonzero CC must fail.
assert "         BNZ   DFAIL" in src
assert "         LTR   5,5" in src
assert "         BNZ   DFAIL\n         LTR   5,5" in src
assert "         C     2,=F'65520'" in src
assert "         BH    DFAIL" in src


# Final page-guarded version compiled on real CMS; querying remains untested.
for marker in (
    "2026-10-09 09:17:04 CDT",
    "NO STATEMENTS FLAGGED IN THIS ASSEMBLY",
    "LOAD M173VQ (NOAUTO NOMAP",
    "START",
    "GCCCMS",
    "CMSCLNK",
    "QUERY COMPLETE NOT ACTIVATION APPROVAL",
    "NO VMUDQ",
    "HARD STOP",
):
    assert marker.lower() in plan.lower() + state.lower(), marker
assert "FINAL GUARDED SOURCE" in runbook.upper()
assert "no diag execution yet" in runbook.lower()
assert "user reminds us installed GCCCMS C compiler" in state.lower()
assert "No non-EDIT DIRECTXA" in plan
# Host source checks cannot be counted as CP LSTMDISK target proof.
assert "NO VMUDQ" in state
assert "NO DIAG execution" in runbook.upper()

print("M173 VMUDQ READONLY SOURCE AND HOST MODEL PASS")
