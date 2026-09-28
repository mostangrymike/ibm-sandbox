#!/bin/sh
# Protect historical M20 and compact M42 Git CMS regressions.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
f="$root/src/GITRCHK.EXEC"
run="$root/src/GITRUN.EXEC"
test -s "$f"
test -s "$run"
grep -q "^say 'GITRCHK M20 READ-ONLY" "$f"
grep -Fq "'GITREC CATHEX GITFIX M15NEW' oid" "$f"
grep -Fq "'GITREC GET GITFIX M15NEW' oid" "$f"
grep -q "^say 'GITRUN M42 COMPACT REPORT'$" "$run"
grep -Fq "'PIPE CMS' cmd '| STEM out.'" "$run"
grep -Fq "'PIPE CMS STATE M15BAD GEN A | STEM out.'" "$run"
grep -Fq "call gate name 'FULL AUDIT','GITCIDX GENCHECK',0,fast,pair,gen" "$run"
# One audited depth-two LINKBATCH replaces three positive audits.
grep -Fq "call gate 'M42 SINGLE AUDIT M35-M37',cmd,0," "$run"
grep -Fq "call gate 'M42 SRC DEPTH1',cmd,0," "$run"
grep -Fq "cmd='GITREC LSDIRDEPTH GITFIX M15NEW' commit '737263' '1'" "$run"
grep -Fq "dirv='DIRECTORY LINK DEPTH 1 VERIFIED'" "$run"
grep -Fq "rootok='NESTED ROOT LINKS VERIFIED'" "$run"
grep -Fq "deepok='DEEP ROOT LINKS VERIFIED'" "$run"
grep -Fq "linkok='LINK DEPTH 2 VERIFIED'" "$run"
if grep -Eq "call gate 'M(35|36|37) " "$run"; then
 echo "FAIL: redundant positive full-audit calls" >&2
 exit 1
fi
grep -Fq "call gate 'INVALID DEPTH',cmd,4," "$run"
grep -Fq "call gate 'NON COMMIT CHILD',cmd,8," "$run"
grep -Fq "call gate 'MISSING CHILD',cmd,4," "$run"
grep -Fq "call gate 'RECOVERED BATCH',cmd,0," "$run"
grep -Fq "call gate 'BOTH INVALID FAIL CLOSED',cmd,8," "$run"
grep -Fq "call gate 'RESTORED BATCH',cmd,0," "$run"
grep -q "^say 'GITRUN M42 ALL READ ONLY NATIVE GIT TESTS PASSED'$" "$run"
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
echo "READ-ONLY GITRCHK AND COMPACT GITRUN M42 GUARDS PASSED"
