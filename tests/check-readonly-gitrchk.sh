#!/bin/sh
# Guard M20 CMS smoke batch against persistence mutations.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
f="$root/src/GITRCHK.EXEC"
hold="$root/src/GITRUN.EXEC"
test -s "$f"
test -s "$hold"
grep -q "^say 'GITRCHK M20 READ-ONLY" "$f"
grep -q "^'GITREC CATHEX GITFIX M15NEW' oid$" "$f"
grep -q "^'GITREC GET GITFIX M15NEW' oid$" "$f"
grep -q "^'FILEDEF C1GEN DISK M15BAD GEN A'$" "$f"
grep -q "^'FILEDEF C0GEN DISK M15BAD GEN A'$" "$f"
grep -q '^exit 12$' "$hold"
if grep -Ei "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD|SELOUT|FILEDEF (IDXOUT|FIDXOUT|GENOUT))([[:space:]]|'|$)" "$f"; then
  echo "FAIL: persistent or output-producing CMS command in read-only gate" >&2
  exit 1
fi
if grep -E "^[[:space:]]*'?(ERASE|COPYFILE|GENWRITE|FORMAT|GENMOD)([[:space:]]|'|$)" "$hold"; then
  echo "FAIL: safety-hold GITRUN would modify CMS A disk" >&2
  exit 1
fi
echo "READ-ONLY GITRCHK AND GITRUN HOLD GUARDS PASSED"
