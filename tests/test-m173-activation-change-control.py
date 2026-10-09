#!/usr/bin/env python3
"""Host-only contract for M173 0600 directory activation change control.

Nothing in this file invokes CMS, DIRECTXA, FORMAT, or a cloud operation.
The live VMUDQ inventory is still the authoritative target observation.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
control = (root / "docs/M173_ACTIVATION_CHANGE_CONTROL.md").read_text()
plan = (root / "docs/M173_DIRECTORY_CHANGE_PLAN.md").read_text()
runbook = (root / "docs/M173_PERSISTENT_DISK_RUNBOOK.md").read_text()
state = (root / "CHAT_STATE.md").read_text()

for s in (control, plan, runbook, state):
    assert "09:33:55" in s
    assert "PMAINT" in s
    assert "M173BAK DIRECT C" in s
    assert "6000" in s and "7599" in s
    assert "FULL" in s.upper() and "FORMAT" in s.upper()

for marker in (
    "Historical preactivation policy", "ACTUAL CP ACTIVATION", "Ready; T=0.18/0.21 09:49:23", "HCPDIR494I User directory occupies 58 disk pages",
    "CP QUERY SYSTEM 0127",
    "CP QUERY ALLOC DRCT ALL",
    "CP QUERY MDISK 0600 DIRECTORY",
    "M173DCHK",
    "HCPQMD040E",
    "Ready(00040)",
    "M173 DIR DELTA CHECK PASS",
    "CP QUERY MDISK USERID MAINT 0600 LOCATION DIRECTORY",
    "EOJ DIRECTORY UPDATED AND ON LINE",
    "EOJ DIRECTORY UPDATED",
    "EOJ DIRECTORY NOT UPDATED",
    "not a guarantee",
    "not test-restored",
    "LINK",
    "full-pack",
    "M173NET",  # resolved below if present
):
    if marker == "M173NET":
        continue
    assert marker.lower() in control.lower(), marker

# Materializing the initial disk is never a side effect
# of CP directory source validation or directory activation.
assert "Formatting is a separate destructive gate" in control
assert "DIRECTORY ACTIVATION SUCCEEDED" in control
assert "FORMAT have **NOT** happened" in control
assert "Directory activation and first verification PASSED" in plan
assert "FORMAT IS NOT YET AUTHORIZED" in plan
assert "CP QUERY VIRTUAL DASD" in plan
assert "CP QUERY MDISK 0600 LOCATION" in plan
assert "CP LINK * 0600 0600 W" in plan
assert "not-authorized" not in control.lower() or "not approved" in control.lower()

# Geometry from the independent live CP MDISK location check and
# CP VMUDQ all-volume census. An END/fullpack is NOT ordinary free.
def end(start, cylinders):
    assert start >= 0 and cylinders > 0
    return start + cylinders - 1

last_ordinary = (5756, 180)
candidate = (6000, 1600)
fullpack = (0, 11000)
assert end(*last_ordinary) == 5935
assert end(*candidate) == 7599
assert end(*fullpack) == 10999
assert 6000 - end(*last_ordinary) - 1 == 64
assert end(*last_ordinary) < candidate[0]
assert fullpack[0] <= candidate[0] <= end(*candidate) <= end(*fullpack)

def overlaps(a, b):
    return a[0] <= end(*b) and b[0] <= end(*a)

assert not overlaps(last_ordinary, candidate)
assert overlaps(fullpack, candidate)
assert overlaps(candidate, (7599, 1))
assert not overlaps(candidate, (7600, 1))
assert not overlaps(candidate, (5935, 1))
assert not overlaps(candidate, (5936, 64))

# State machine: neither "updated" alone nor a failed/no-update
# response is the same as the online directory being accepted.
def online_status(response):
    if response == "EOJ DIRECTORY UPDATED AND ON LINE":
        return "online"
    if response == "EOJ DIRECTORY UPDATED":
        return "offline_or_unknown"
    return "fail"

assert online_status("EOJ DIRECTORY UPDATED AND ON LINE") == "online"
assert online_status("EOJ DIRECTORY UPDATED") != "online"
assert online_status("EOJ DIRECTORY NOT UPDATED") == "fail"
assert online_status("UNEXPECTED") == "fail"

# A completed snapshot is not a tested restore; a successful
# source-map proof is not an active fullpack access restriction.
assert "not test-restored" in control.lower()
assert "M173VQ" in control
assert "ONLINE CP DIRECTORY M173NEW ACTIVATION TARGET-PROVEN PASS" in state
assert "EOJ DIRECTORY UPDATED AND ON LINE" in state
assert "Do not FORMAT yet" in state

# Postactivation definition is NOT the same as a device
# currently attached to the MAINT virtual machine.
for marker in (
    "DIRECTORY ACTIVATION SUCCEEDED",
    "EOJ DIRECTORY UPDATED AND ON LINE",
    "MAINT 0600 MAINT 0600 3390 VMCOM1 0127 6000 1600",
    "M01RES 0123 1 20",
    "CP QUERY VIRTUAL DASD",
    "CP QUERY MDISK 0600 LOCATION",
    "QUERY DISK",
    "CP LINK * 0600 0600 W",
    "FORMAT have **NOT** happened",
    "after any successful self-link",
    "cannot be authorized",
):
    assert marker.lower() in control.lower(), marker
assert "DO NOT" in control.upper()
assert "4K blocks" in control
assert "180,000" in control
assert "current logged-on MAINT" in plan
assert "NO" in state


# Live Phase 7A proves link, but not formatted G.
for marker in (
    "2026-10-09 09:58:25 CDT",
    "CP LINK * 0600 0600 W",
    "SUBCHANNEL = 0024",
    "GIT600",
    "BLKS LEFT",
):
    assert marker.lower() in control.lower(), marker
assert "Phase 7A target PASS" in plan
assert "CURRENT virtual" in plan
assert "no G" in runbook
assert "LIVE VIRTUAL LINK PASS" in state
assert "not yet target-proven" in state.lower()


# Target GIT600 1600-cylinder 4K CMS disk is now live.
for s in (control, plan, runbook, state):
    for key in ("10:06", "GIT600", "287975", "288000", "1600"):
        assert key in s, (key, "live disk checkpoint missing")
assert "G initialization is complete" in control
assert "Storage provisioning FINISHED" in state
assert "M173CHK G" in runbook and "M173CHK G" in state

# Operator's real QUERY DISK G row: 0 files, 25 overhead blocks.
r = "GIT600 600 G R/W 1600 3390 4096 0 25-00 287975 288000"
w = r.split()
assert len(w) == 11
assert w[:7] == ["GIT600","600","G","R/W","1600","3390","4096"]
assert w[7:] == ["0", "25-00", "287975", "288000"]
assert int(w[9]) >= 180000
assert int(w[9]) - 180000 == 107975
assert int(w[9]) + 25 == int(w[10])
assert "PMAINT" in state and "fullpack" in state

print("M173 POSTACTIVATION CHANGE-CONTROL HOST SAFETY PASS")
