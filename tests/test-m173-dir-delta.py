#!/usr/bin/env python3
"""Static CMS delta-verifier gate plus independent host model."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "src" / "M173DCHK.EXEC").read_text()
plan = (root / "docs" / "M173_DIRECTORY_CHANGE_PLAN.md").read_text()
lines = source.splitlines()
assert all(len(s) <= 80 for s in lines)
assert "address cms" in source
assert "parse upper arg extra" in source
assert "M173 DIR DELTA CHECK PASS" in source
assert "M173 DIR MAINT-1 SUBCONFIG VERIFIED" in source
assert "M173 DIR BACKUP CONTENT MISMATCH" in source
assert "M173 DIR CANDIDATE EXTRA CHANGE" in source
assert "M173 DIR INSERT POSITION INVALID" in source
assert "M173 DIR MDISK FIELDS INVALID" in source
assert "M173 DIR VDEV 0600 ENTRY COUNT" in source
assert "if u.0\\=4282 | b.0\\=u.0 | n.0\\=u.0+1" in source
assert "if u.i\\==b.i" in source
assert "if u.i\\==n.j" in source
assert "if i>=added then j=i+1" in source
assert "if found\\=1" in source
assert "w2=='600' | w2=='0600'" in source
assert "v\\=='600' & v\\=='0600'" in source
assert "if words(n.added)\\=7" in source
assert "if sect\\=='SUBCONFIG' | sid\\=='MAINT-1'" in source
assert "if builds\\=1" in source

expected = "MDISK 0600 3390 6000 1600 VMCOM1 W"
assert "if translate(word(n.added,1))\\=='MDISK'" in source
assert "if translate(word(n.added,6))\\=='VMCOM1'" in source
assert "if translate(word(n.added,7))\\=='W'" in source
for target, stem in (("USER DIRECT C", "U."),
                     ("M173BAK DIRECT C", "B."),
                     ("M173NEW DIRECT C", "N.")):
    assert f"'STATE {target}'" in source
    assert f"'EXECIO * DISKR {target} 1 (STEM {stem} FINIS'" in source
    assert f"(STEM {stem.lower()} FINIS" not in source
# IBM EXECIO communicates with REXX through EXECCOMM: REXX stem
# symbols must be UPPERCASE in the literal command, else rc8.
assert "STEM U. FINIS" in source
assert "STEM B. FINIS" in source
assert "STEM N. FINIS" in source
for forbidden in ("DISKW", "ERASE ", "COPYFILE ", "FILEDEF ",
                  "DIRECTXA ", "FORMAT ", "SAY U.", "SAY B.", "SAY N."):
    assert forbidden not in source.upper(), forbidden

# Independent host model of one additional MDISK inside MAINT-1.
def audit(original, backup, candidate):
    if len(original) != 4282 or backup != original or len(candidate) != 4283:
        return False
    inds = [i for i, line in enumerate(candidate) if
            len(line.split()) > 1 and line.upper().split()[0] == "MDISK"
            and line.split()[1] in ("600", "0600")]
    if len(inds) != 1:
        return False
    i = inds[0]
    if i < 1 or i >= len(original):
        return False
    fields = candidate[i].upper().split()
    if len(fields) != 7 or fields[0] != "MDISK":
        return False
    if fields[2:] != ["3390", "6000", "1600", "VMCOM1", "W"]:
        return False
    if candidate[:i] != original[:i] or candidate[i+1:] != original[i:]:
        return False
    active = ""
    build = 0
    in_identity = False
    for line in original[:i]:
        words = line.upper().split()
        if not words:
            continue
        if words[0] in ("USER", "IDENTITY", "SUBCONFIG", "PROFILE"):
            active = " ".join(words[:2])
            in_identity = active == "IDENTITY MAINT"
        if in_identity and words == [
            "BUILD", "ON", "*", "USING", "SUBCONFIG", "MAINT-1"
        ]:
            build += 1
    return active == "SUBCONFIG MAINT-1" and build == 1

original = ["* unchanged"] * 4282
original[161] = "IDENTITY MAINT PLACEHOLDER"
original[162] = "BUILD ON * USING SUBCONFIG MAINT-1"
original[180] = "SUBCONFIG MAINT-1"
backup = original[:]
candidate = original[:212] + ["MDISK 600 3390 6000 1600 VMCOM1 W"] + original[212:]
assert audit(original, backup, candidate)
assert audit(original, backup, original[:212] + [expected] + original[212:])
for badline in (
    "MDISK 600 3390 6000 1600 VMCOM1 MR",
    "MDISK 600 3390 6000 1601 VMCOM1 W",
    "MDISK 600 3390 6000 1600 VMCOM2 W",
    "MDISK 600 3390 6000 1600 VMCOM1 W EXTRA",
):
    assert not audit(original, backup,
                     original[:212] + [badline] + original[212:])
bad = candidate[:]
bad[100] = "changed"
assert not audit(original, backup, bad)
bad = candidate[:]
bad[300] = "changed"
assert not audit(original, backup, bad)
assert not audit(original, backup, [expected] + original)
assert not audit(original, backup, original + [expected])
changed_backup = backup[:]
changed_backup[120] = "changed"
assert not audit(original, changed_backup, candidate)

assert "XEDIT M173NEW DIRECT C" in plan
assert "INPUT MDISK 0600 3390 6000 1600 VMCOM1 W" in plan
assert "M173DCHK" in plan
assert "QQUIT" in plan
assert "STOP after XEDIT and M173DCHK" in plan
print("M173 DIR DELTA SOURCE/SAFETY HOST GATES PASSED")
