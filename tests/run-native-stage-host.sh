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
cat "$tmp/host.log"
echo "HOST STAGING AND GIT OID TEST PASSED"
