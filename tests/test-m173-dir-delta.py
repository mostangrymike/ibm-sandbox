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

# A host model independently exercises acceptance/rejection rules.
def audit(original, backup, candidate):
    if len(original) != 4282 or len(backup) != len(original):
        return False
    if len(candidate) != len(original) + 1 or backup != original:
        return False
    matches = [i for i, line in enumerate(candidate)
               if line.strip().upper() == expected]
    if len(matches) != 1:
        return False
    at = matches[0]
    if at < 1 or original[at-1].split()[:2] != ["USER", "MAINT"]:
        return False
    return (candidate[:at] == original[:at]
            and candidate[at+1:] == original[at:])

original = ["COMMENT"] * 4282
original[120] = "USER MAINT NOT-A-REAL-PASSWORD"
backup = original[:]
candidate = original[:121] + [expected] + original[121:]
assert audit(original, backup, candidate)
assert not audit(original, backup, original)
assert not audit(original, backup, original[:121]+[expected]*2+original[121:])
assert not audit(original, backup, original[:120]+[expected]+original[120:])
assert not audit(original, backup, original[:121]+[
    "MDISK 0600 3390 6000 1600 VMCOM1 MR"]+original[121:])
bad = candidate[:]
bad[400] = "changed unrelated source record"
assert not audit(original, backup, bad)
badbak = backup[:]
badbak[222] = "changed backup"
assert not audit(original, badbak, candidate)
# Source may contain more than one heading candidate. The edit
# must still be one exact insertion after an actual MAINT heading.
ambiguous = original[:]
ambiguous[10] = "USER MAINT another"
assert not audit(ambiguous, ambiguous, candidate)
candidate2 = ambiguous[:121] + [expected] + ambiguous[121:]
assert audit(ambiguous, ambiguous, candidate2)
noheading = original[:]
noheading[120] = "USER OTHER"
assert not audit(noheading, noheading,
                 noheading[:121]+[expected]+noheading[121:])
assert not audit(original, backup, [expected]+original)
assert not audit(original, backup, original+[expected])

# Approved entry can appear after an earlier unrelated modification,
# but must still fail the full alignment proof.
modified_earlier = candidate[:]
modified_earlier[5] = "UNRELATED MODIFICATION"
assert not audit(original, backup, modified_earlier)
no_approved_entry = candidate[:]
no_approved_entry[121] = "MDISK 0600 3390 6000 1600 VMCOM1 MR"
assert not audit(original, backup, no_approved_entry)
duplicate_approved = candidate[:]
duplicate_approved[200] = expected
assert not audit(original, backup, duplicate_approved)
assert "M173 DIR APPROVED LINE COUNT" in source
assert "M173 DIR MDISK 0600 PREFIX COUNT" in source

assert "XEDIT M173NEW DIRECT C" in plan
assert "INPUT MDISK 0600 3390 6000 1600 VMCOM1 W" in plan
assert "M173DCHK" in plan
assert "QQUIT" in plan
assert "STOP after XEDIT and M173DCHK" in plan
print("M173 DIR DELTA SOURCE/SAFETY HOST GATES PASSED")
