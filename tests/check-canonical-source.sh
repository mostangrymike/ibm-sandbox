#!/bin/sh
# Guard against host-only tests missing the CMS EBCDIC hash bug.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
walk="$root/src/GITCWALK.C"
index="$root/src/GITCIDX.C"
for path in "$walk" "$index"; do
 awk 'length($0)>80 {print FNR ": width " length($0);bad=1}
      END {exit bad}' "$path"
 grep -Fq '0x62,0x6c,0x6f,0x62' "$path"
 grep -Fq 'dst[i++]=0x20;' "$path"
 grep -Fq '0x30+rem%10' "$path"
done
grep -Fq 'k=canonical_head(type,n,hashbuf)' "$walk"
grep -Fq 'k=canonical_head(type,n,head)' "$walk"
grep -Fq 'memcmp(objoid[0],shaabc,20)' "$walk"
grep -Fq 'memcmp(missing,shafive,20)' "$walk"
grep -Fq 'head=idx_head(type,n,idx_hashbuf)' "$index"
grep -Fq 'INDEX CANONICAL ASCII ABC PASSED' "$index"
grep -Fq 'sscanf(line,"IDX2 ' "$index"
grep -Fq 'sscanf(line,"SIDX2 ' "$index"
if grep -Eq 'sprintf\(\(char \*\)(hashbuf|head|idx_hashbuf)'    "$walk" "$index"; then
 echo 'CMS-native formatted text in a canonical Git SHA header' >&2
 exit 1
fi
echo 'Canonical ASCII header and CMS C source guards passed'
