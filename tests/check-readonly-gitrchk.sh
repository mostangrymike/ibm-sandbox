#!/bin/sh
# Protect historical M20 and compact M54 Git CMS regressions.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
f="$root/src/GITRCHK.EXEC"
run="$root/src/GITRUN.EXEC"
test -s "$f"
test -s "$run"
grep -q "^say 'GITRCHK M20 READ-ONLY" "$f"
grep -Fq "'GITREC CATHEX GITFIX M15NEW' oid" "$f"
grep -Fq "'GITREC GET GITFIX M15NEW' oid" "$f"
grep -q "^say 'GITRUN M54 COMPACT REPORT'$" "$run"
grep -Fq "'PIPE CMS' cmd '| STEM out.'" "$run"
grep -Fq "'PIPE CMS STATE M15BAD GEN A | STEM out.'" "$run"
grep -Fq "call gate name 'FULL AUDIT','GITCIDX GENCHECK',0,fast,pair,gen" "$run"
# Every positive original-data feature runs after one selector audit.
grep -Fq "call gate 'M54 ONE SELECTION ALL POSITIVES'," "$run"
grep -Fq "cmd='GITREC RUNBATCH GITFIX M15NEW' commit tree" "$run"
grep -Fq "say 'PASS SELECT SEQ52 FROM VERIFIED BATCH'" "$run"
if grep -Fq "GITREC SELECT GITFIX M15NEW" "$run"; then
 echo "FAIL: separate redundant seq52 full audit" >&2
 exit 1
fi
if grep -Eq "call gate 'M54 (SINGLE|SRC|FULL|TREE|README)" "$run"; then
 echo "FAIL: redundant separate positive full-audit calls" >&2
 exit 1
fi
grep -Fq "call gate 'INVALID DEPTH',cmd,4," "$run"
grep -Fq "BATCH NON COMMIT CHILD RC8 VERIFIED" "$run"
grep -Fq "BATCH MISSING CHILD RC4 VERIFIED" "$run"
if grep -Eq "call gate '(NON COMMIT CHILD|MISSING CHILD)'" "$run"; then
 echo "FAIL: separate full selector audit for expected negative" >&2
 exit 1
fi
grep -Fq "call gate 'RECOVERED BATCH',cmd,0," "$run"
grep -Fq "call gate 'BOTH INVALID FAIL CLOSED',cmd,8," "$run"
grep -Fq "call gate 'RESTORED BATCH',cmd,0," "$run"
grep -q "^say 'GITRUN M54 ALL READ ONLY NATIVE GIT TESTS PASSED'$" "$run"
if grep -E '^[[:space:]]*call gate .*,$' "$run"; then
 echo "FAIL: split REXX CALL arguments" >&2
 exit 1
fi
for file in "$f" "$run"; do
 if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$file"; then
  echo "FAIL: persistent CMS command in read-only gate $file" >&2
  exit 1
 fi
done
echo "READ-ONLY GITRCHK AND COMPACT GITRUN M54 GUARDS PASSED"
