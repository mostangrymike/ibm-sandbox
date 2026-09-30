#!/bin/sh
# M67 verified-ref bridge must stay read-only and CMS-record-safe.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
v="$root/src/GITVREF.EXEC"
g="$root/src/GIT.EXEC"
r="$root/src/GITREF2.REPO"
test -s "$v"
test -s "$g"
test -s "$r"
grep -Fxq "REF2 1" "$r"
grep -Fxq "HEAD refs/heads/main" "$r"
grep -Fxq "REF refs/heads/main 00D8D63229305230C8D37F884CE87F9E1A89468C" "$r"
grep -Fq "GITREC SHOWFULL GITFIX M15NEW" "$v"
grep -Fq "SHOW FULL ROOT CLOSURE VERIFIED" "$v"
grep -Fq "'FILEDEF SEL0 DISK M15SL0 PTR A'" "$v"
grep -Fq "'FILEDEF SEL1 DISK M15SL1 PTR A'" "$v"
grep -Fq "command = 'VERIFY-REF'" "$g"
grep -Fq "'EXEC GITVREF RESOLVE' rest" "$g"
grep -Fq "command = 'SHOW-REF-FULL'" "$g"
grep -Fq "'EXEC GITVREF SHOW' rest" "$g"
grep -Fq "command = 'LOG-REF-FULL'" "$g"
grep -Fq "'EXEC GITVREF LOG' rest" "$g"
grep -Fq "command = 'LOGDAG-REF-FULL'" "$g"
grep -Fq "'EXEC GITVREF DAG' rest" "$g"
grep -Fq "GITREC LOGDAGFULL GITFIX M15NEW" "$v"
grep -Fq "LOGDAG FULL SNAPSHOTS VERIFIED" "$v"
grep -Fq "GITREC LOGFULL GITFIX M15NEW" "$v"
grep -Fq "LOG FULL SNAPSHOTS VERIFIED" "$v"
grep -Fq "command='READ'" "$v"
grep -Fq "GITREC PATHFULLCAT GITFIX M15NEW" "$v"
grep -Fq "COMMIT ROOT FULL CLOSURE VERIFIED" "$v"
grep -Fq "command = 'READ-REF-FULL'" "$g"
grep -Fq "'EXEC GITVREF READ' rest" "$g"
grep -Fq "pathasciihex:" "$v"
grep -Fq "command='DIR'" "$v"
grep -Fq "GITREC PATHFULLDIR GITFIX M15NEW" "$v"
grep -Fq "command = 'DIR-REF-FULL'" "$g"
grep -Fq "'EXEC GITVREF DIR' rest" "$g"
if grep -Ei "(DISKW|ERASE|COPYFILE|GENWRITE|SELOUT|IDXOUT|FIDXOUT|GENOUT)" "$v"; then
 echo "FAIL: verified-ref bridge contains persistent write path" >&2
 exit 1
fi
awk 'length($0)>80 {print "FAIL: GITVREF record >80 columns:", NR; bad=1}
     END {exit bad}' "$v"
awk 'length($0)>80 {print "FAIL: GITREF2 record >80 columns:", NR; bad=1}
     END {exit bad}' "$r"
echo "M67 VERIFIED REF2 SHOW/LOG/DAG/PATH/DIR BRIDGE GUARDS PASSED"
