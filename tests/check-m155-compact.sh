#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
x="$root/src/M155CHK.EXEC"
test -s "$x"
grep -Fq "GIT HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL" "$x"
grep -Fq "GIT HISTORYFIRSTPRESENCEEVENTS-REF-FULL" "$x"
grep -Fq "HISTORYFIRSTPRESENCECHRONOLOGY FULL SNAPSHOTS VERIFIED" "$x"
grep -Fq "HISTORYFIRSTPRESENCEEVENTS FULL SNAPSHOTS VERIFIED" "$x"
grep -Fq "HISTORYFIRSTPRESENCECHRONOLOGY DATA END" "$x"
grep -Fq "HISTORYFIRSTPRESENCEEVENTS DATA END" "$x"
grep -Fq "M155 CHRONOLOGY FAIL MARKERS' cm cend" "$x"
grep -Fq "M155 EVENTS FAIL MARKERS' em done" "$x"
grep -Fq "M155 CHRONOLOGY PASS" "$x"
grep -Fq "M155 EVENTS PASS" "$x"
grep -Fq "line=strip(chr.i)" "$x"
grep -Fq "line=strip(evt.i)" "$x"
grep -Fq "M155 COMPACT TARGET GATE PASS" "$x"
if grep -Ei "(DISKW|ERASE|COPYFILE|GENWRITE|SELOUT|IDXOUT|FIDXOUT|GENOUT)" "$x"; then
 echo "FAIL: M155 compact gate contains persistent write path" >&2
 exit 1
fi
awk 'length($0)>80 {print "FAIL: M155CHK record >80:",NR; bad=1}
     END {exit bad}' "$x"
echo "M155 COMPACT CMS TARGET GATE SOURCE CHECK PASSED"
