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
assert "M173 DIR MAINT INSERT VERIFIED 1" in source
assert "M173 DIR BACKUP CONTENT MISMATCH" in source
assert "M173 DIR CANDIDATE EXTRA CHANGE" in source
assert "M173 DIR INSERT POSITION INVALID" in source
assert "M173 DIR RECORD COUNT FAIL" in source
assert "if u.0\\=4282 | b.0\\=u.0 | n.0\\=u.0+1" in source
assert "if u.i\\==b.i" in source
assert "if u.i\\==n.j" in source
assert "if translate(strip(n.k))\\=expected" in source
assert "j=i+1" in source
assert "if i>at then j=i+1" in source
assert "if maint\\=1" in source

expected = "MDISK 0600 3390 6000 1600 VMCOM1 W"
assert f"expected='{expected}'" in source
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
    positions = [i for i, s in enumerate(original)
                 if s.split()[:2] == ["USER", "MAINT"]]
    if len(positions) != 1:
        return False
    i = positions[0]
    return (candidate[i+1].strip().upper() == expected
            and candidate[:i+1] == original[:i+1]
            and candidate[i+2:] == original[i+1:])

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
ambiguous = original[:]
ambiguous[10] = "USER MAINT another"
assert not audit(ambiguous, ambiguous, candidate)

assert "XEDIT M173NEW DIRECT C" in plan
assert "INPUT MDISK 0600 3390 6000 1600 VMCOM1 W" in plan
assert "M173DCHK" in plan
assert "QQUIT" in plan
assert "STOP after XEDIT and M173DCHK" in plan
print("M173 DIR DELTA SOURCE/SAFETY HOST GATES PASSED")
