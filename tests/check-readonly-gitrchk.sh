#!/bin/sh
# Guard M20 and standard compact M26Q GITRUN CMS batches against disk mutation.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
f="$root/src/GITRCHK.EXEC"
run="$root/src/GITRUN.EXEC"
test -s "$f"
test -s "$run"
grep -q "^say 'GITRCHK M20 READ-ONLY" "$f"
grep -q "^'GITREC CATHEX GITFIX M15NEW' oid$" "$f"
grep -q "^'GITREC GET GITFIX M15NEW' oid$" "$f"
grep -q "^'FILEDEF C1GEN DISK M15BAD GEN A'$" "$f"
grep -q "^'FILEDEF C0GEN DISK M15BAD GEN A'$" "$f"
grep -q "^say 'GITRUN M26Q COMPACT REPORT'$" "$run"
grep -Fq "'PIPE CMS' cmd '| STEM out.'" "$run"
grep -Fq "'PIPE CMS STATE M15BAD GEN A | STEM out.'" "$run"
grep -Fq "'GITCIDX GENCHECK',0," "$run"
grep -q "FAST AUDIT VERIFIED 1808 UNIQUE 1808" "$run"
grep -q "GENERATION VERIFIED 1808 UNIQUE 1808" "$run"
grep -Fq "'GITREC LSDIR GITFIX M15NEW' commit docs" "$run"
grep -q "D4BE895844FECE160E31411ABB2ECDD6ACAECC17" "$run"
grep -q "46135A22C7394D8090619C6C70453C58A24F5239" "$run"
grep -Fq "'RECOVERED 51 GITFIX'" "$run"
grep -Fq "'NO FULLY VERIFIED GENERATION'" "$run"
grep -q "^say 'GITRUN M26Q ALL READ ONLY NATIVE GIT TESTS PASSED'$" "$run"
if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$f"; then
  echo "FAIL: persistent or output-producing CMS command in read-only gate" >&2
  exit 1
fi
if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$run"; then
  echo "FAIL: GITRUN would modify CMS A disk" >&2
  exit 1
fi
echo "READ-ONLY GITRCHK AND COMPACT GITRUN M26Q GUARDS PASSED"
