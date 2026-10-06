#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
x="$root/src/M155CHK.EXEC"
test -s "$x"
grep -Fq "EXEC GIT HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL" "$x"
grep -Fq "EXEC GIT HISTORYFIRSTPRESENCEEVENTS-REF-FULL" "$x"
grep -Fq "M155 CHRONOLOGY DIRECT RC0" "$x"
grep -Fq "M155 EVENTS DIRECT RC0" "$x"
grep -Fq "path='src/GITPBWALK.EXEC'" "$x"
grep -Fq "M155 CHECKER STAMP C4" "$x"
grep -Fq "M155 GIT STAMP PASS C4" "$x"
grep -Fq "M155 GITREC STAMP PASS S2" "$x"
grep -Fq "GITREC STATEPATH S2" "$x"
grep -Fq "M155 CASE PROBE PASS C6" "$x"
grep -Fq "M155 PARENT PATH PASS" "$x"
grep -Fq "M155 CHILD ABSENT PASS RC4" "$x"
grep -Fq "91913EA4028B795707AA67EDB1ED17A74D1B896E" "$x"
grep -Fq "EXEC GIT READ-REF-FULL" "$x"
grep -Fq "GITVREF CASE C6 7372632F474954504257414C4B2E45584543" "$x"
grep -Fq "M155 COMPACT TARGET GATE PASS" "$x"
test "$(grep -c '^address command cmd$' "$x")" -eq 2
if grep -Fq "| STEM chr." "$x" || grep -Fq "| STEM evt." "$x" ||
   grep -Fq "| STEM sta." "$x"; then
 echo "FAIL: M155 history command is still pipeline-captured" >&2
 exit 1
fi
if grep -Ei "(DISKW|ERASE|COPYFILE|GENWRITE|SELOUT|IDXOUT|FIDXOUT|GENOUT)" "$x"; then
 echo "FAIL: M155 compact gate contains persistent write path" >&2
 exit 1
fi
awk 'length($0)>80 {print "FAIL: M155CHK record >80:",NR; bad=1}
     END {exit bad}' "$x"
echo "M155 DIRECT CMS TARGET GATE SOURCE CHECK PASSED"
