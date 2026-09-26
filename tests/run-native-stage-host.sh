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
cat "$tmp/host.log"
cat "$tmp/index.log"
echo "HOST STAGING, INDEX AND GIT OID TEST PASSED"
