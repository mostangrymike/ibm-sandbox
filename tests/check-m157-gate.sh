#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
x="$root/src/M157GATE.EXEC"
test -s "$x"
grep -Fq "'M155CHK'" "$x"
grep -Fq "'M156CHK'" "$x"
grep -Fq "'M157CHK'" "$x"
grep -Fq "M157GATE M155 FAIL RC" "$x"
grep -Fq "M157GATE M156 FAIL RC" "$x"
grep -Fq "M157GATE M157 FAIL RC" "$x"
grep -Fq "M157GATE COMBINED TARGET GATE PASS" "$x"
if grep -Fq "PIPE " "$x"; then
 echo "FAIL: M157GATE must execute compact checkers directly" >&2
 exit 1
fi
if grep -Ei "(DISKW|ERASE|COPYFILE|GENWRITE|SELOUT|IDXOUT|FIDXOUT|GENOUT)" "$x"; then
 echo "FAIL: M157 combined gate contains persistent write path" >&2
 exit 1
fi
awk 'length($0)>80 {print "FAIL: M157GATE record >80:",NR; bad=1}
     END {exit bad}' "$x"
echo "M157 DIRECT TARGET GATE SOURCE CHECK PASSED"
