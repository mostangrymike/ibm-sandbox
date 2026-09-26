#!/bin/sh
# Host-only test: does not replace GCCCMS compilation or target tests.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
${CC:-cc} -x c -std=c89 -O2 -Wall -Wextra \
    -o "$tmp/native_stage_host" "$root/tests/native_stage_host.c"
(
 cd "$tmp"
 ./native_stage_host > host.log
)
actual=$(sed -n 's/^HOST ABC OID //p' "$tmp/host.log")
expected=$(printf abc | git hash-object --stdin)
if [ "$actual" != "$expected" ]; then
 echo "Expected Git OID: $expected" >&2
 echo "Native Git OID:   $actual" >&2
 exit 1
fi
${CC:-cc} -x c -std=c89 -D_POSIX_C_SOURCE=200809L \
    -O2 -Wall -Wextra -o "$tmp/native_index_host" \
    "$root/tests/native_index_host.c"
(
 cd "$tmp"
 ./native_index_host > index.log
)
for type in commit tree blob tag; do
 for fixture in ABC EMPTY; do
  actual=$(sed -n "s/^HOST OID $type $fixture //p" "$tmp/host.log")
  if [ "$fixture" = ABC ]; then
   expected=$(printf abc | git hash-object -t "$type" \
     --literally --stdin)
  else
   expected=$(printf '' | git hash-object -t "$type" \
     --literally --stdin)
  fi
  if [ "$actual" != "$expected" ]; then
   echo "OID mismatch: $type $fixture" >&2
   echo "Native: $actual Git: $expected" >&2
   exit 1
  fi
 done
done
# Native full PACK integration (host zlib only, not CMS inflater).
python3 "$root/tests/make-native-ref-pack.py" "$tmp" > "$tmp/ref-fixtures.log"
${CC:-cc} -x c -std=c89 -O2 -Wall -Wextra \
    -o "$tmp/native_ref_pack_host" \
    "$root/tests/native_ref_pack_host.c" -lz
(
 cd "$tmp"
 cp REFPACK.PACK 'dd:PACKIN'
 ./native_ref_pack_host > ref-positive.log
 grep -q '^PASS 3 OBJECTS NEXT OFFSET ' ref-positive.log
 grep -q '^OFS DELTAS APPLIED 0
echo "HOST STAGING, INDEX AND GIT OID TEST PASSED"
 ref-positive.log
 grep -q '^REF DELTAS APPLIED 2
echo "HOST STAGING, INDEX AND GIT OID TEST PASSED"
 ref-positive.log
 for entry in 'REFBAD.PACK:2' 'REFFWD.PACK:1'; do
  filename=${entry%%:*}; object=${entry##*:}
  cp "$filename" 'dd:PACKIN'
  if ./native_ref_pack_host > ref-negative.log; then
   echo "Unexpected REF acceptance: $filename" >&2
   exit 1
  fi
  grep -q "^UNRESOLVED REF BASE OBJ $object$" ref-negative.log
 done
 cp REFSHA.PACK 'dd:PACKIN'
 if ./native_ref_pack_host > ref-negative.log; then
  echo 'Accepted corrupted PACK trailer' >&2
  exit 1
 fi
 grep -q '^FAIL NATIVE PACK SHA1
echo "HOST STAGING, INDEX AND GIT OID TEST PASSED"
 ref-negative.log
)
for pair in '1:abc' '2:abcd' '3:abcde'; do
 number=${pair%%:*}; body=${pair##*:}
 expected=$(printf %s "$body" | git hash-object --stdin)
 oid=$(sed -n "s/^OID OBJ $number TYPE 3 SIZE [0-9]* //p" \
     "$tmp/ref-positive.log")
 if [ "$(printf %s "$oid" | tr 'A-F' 'a-f')" != "$expected" ]; then
  echo "Native REF OID $number differs from Git" >&2
  exit 1
 fi
done
ref_oid=$(sed -n 's/^REFTEST OID //p' "$tmp/host.log")
expected_ref=$(printf abcde | git hash-object --stdin)
test "$ref_oid" = "$expected_ref"
cat "$tmp/ref-positive.log"
echo "HOST REF PACK INTEGRATION AND NEGATIVE GATES PASSED"
cat "$tmp/host.log"
cat "$tmp/index.log"
echo "HOST STAGING, INDEX AND GIT OID TEST PASSED"
