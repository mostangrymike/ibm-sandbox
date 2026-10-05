#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
x="$root/src/M157GATE.EXEC"
test -s "$x"
grep -Fq "PIPE CMS EXEC M155CHK" "$x"
grep -Fq "PIPE CMS EXEC M156CHK" "$x"
grep -Fq "PIPE CMS EXEC M157CHK" "$x"
grep -Fq "M155 COMPACT TARGET GATE PASS" "$x"
grep -Fq "M156 COMPACT TARGET GATE PASS" "$x"
grep -Fq "M157 COMPACT TARGET GATE PASS" "$x"
grep -Fq "M157GATE COMBINED TARGET GATE PASS" "$x"
if grep -Ei "(DISKW|ERASE|COPYFILE|GENWRITE|SELOUT|IDXOUT|FIDXOUT|GENOUT)" "$x"; then
 echo "FAIL: M157 combined gate contains persistent write path" >&2
 exit 1
fi
awk 'length($0)>80 {print "FAIL: M157GATE record >80:",NR; bad=1}
     END {exit bad}' "$x"
echo "M157 COMBINED COMPACT TARGET GATE SOURCE CHECK PASSED"
