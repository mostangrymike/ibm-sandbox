#!/bin/sh
# Guard M20 and standard M22 GITRUN CMS batches against disk mutation.
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
grep -q "^say 'GITRUN M22 READ ONLY NATIVE GIT REGRESSION'" "$run"
grep -Eq "^[[:space:]]*'GITCIDX GENCHECK'$" "$run"
grep -q "^'GITREC SELECT GITFIX M15NEW'$" "$run"
grep -q "^'GITREC GET GITFIX M15NEW' commit$" "$run"
grep -q "^'GITREC TREE GITFIX M15NEW' tree$" "$run"
grep -q "^'FILEDEF C1GEN DISK M15BAD GEN A'$" "$run"
grep -q "^'FILEDEF C0GEN DISK M15BAD GEN A'$" "$run"
if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$f"; then
  echo "FAIL: persistent or output-producing CMS command in read-only gate" >&2
  exit 1
fi
if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$run"; then
  echo "FAIL: GITRUN would modify CMS A disk" >&2
  exit 1
fi
echo "READ-ONLY GITRCHK AND GITRUN M22 GUARDS PASSED"
