#!/bin/sh
# Static checks only: actual GCCCMS compilation remains a CMS gate.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
file="$root/src/CMSCLNK.EXEC"
test -f "$file"
awk 'length($0)>80 {
 printf "CMSCLNK line %d too long: %d\n",NR,length($0)
 bad=1
} END {exit bad}' "$file"
grep -Fq "if mode='' then mode='NAPI'" "$file"
grep -Fq "if mode='NAPI' then do" "$file"
grep -Fq "'ASSEMBLE GITCAPI'" "$file"
grep -Fq "'ASSEMBLE GITINFA'" "$file"
grep -Fq "'GLOBAL TXTLIB PDPCLIB'" "$file"
grep -Fq "'LOAD' name 'GITCAPI GITINFA (NOAUTO NOMAP'" "$file"
grep -Fq "'LOAD' name '(NOAUTO NOMAP'" "$file"
grep -Fq "'GENMOD' name" "$file"
grep -Fq 'COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F' \
 "$root/docs/BUILD.md"
grep -Fq 'QUERY DISK F' "$root/docs/BUILD.md"
echo 'CMSCLNK source and F-disk installation checks passed'
