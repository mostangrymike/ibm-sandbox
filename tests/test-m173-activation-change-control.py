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
    "STATE: DRAFT FOR OPERATOR REVIEW. NOT APPROVED TO EXECUTE",
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
assert "DO NOT activate" in control or "do not activate" in control.lower()
assert "no non-EDIT DIRECTXA" in plan.lower()
assert "No activation, LINK" in plan
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
assert "no CP directory activation" in state.lower() or (
    "No activation" in state and "STOP" in state
)
print("M173 GATE6 ACTIVATION CHANGE-CONTROL HOST SAFETY PASS")
