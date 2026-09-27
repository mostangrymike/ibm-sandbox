#!/bin/sh
# Validate guarded offline DASD backup helper on harmless synthetic data.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
printf 'DASD TEST DATA\000\377\002' > "$tmp/source.ckd"
mkdir "$tmp/snapshots"
if bash "$root/scripts/backup-offline-dasd.sh" \
   "$tmp/source.ckd" "$tmp/snapshots/copy.ckd" > "$tmp/unconfirmed.log" 2>&1; then
  echo "FAIL: allowed backup without explicit offline confirmation" >&2
  exit 1
fi
OFFLINE_CONFIRMED=YES bash "$root/scripts/backup-offline-dasd.sh" \
  "$tmp/source.ckd" "$tmp/snapshots/copy.ckd" > "$tmp/backup.log"
cmp "$tmp/source.ckd" "$tmp/snapshots/copy.ckd"
if OFFLINE_CONFIRMED=YES bash "$root/scripts/backup-offline-dasd.sh" \
   "$tmp/source.ckd" "$tmp/snapshots/copy.ckd" > "$tmp/overwrite.log" 2>&1; then
  echo "FAIL: allowed overwrite of existing backup" >&2
  exit 1
fi
if OFFLINE_CONFIRMED=YES bash "$root/scripts/backup-offline-dasd.sh" \
   "$tmp/missing.ckd" "$tmp/snapshots/missing.ckd" > "$tmp/missing.log" 2>&1; then
  echo "FAIL: allowed nonexistent source" >&2
  exit 1
fi
test ! -e "$tmp/snapshots/missing.ckd"
test -f "$tmp/source.ckd"
ln -s "$tmp/source.ckd" "$tmp/source-symlink.ckd"
if OFFLINE_CONFIRMED=YES bash "$root/scripts/backup-offline-dasd.sh" \
   "$tmp/source-symlink.ckd" "$tmp/snapshots/symlink.ckd" > "$tmp/symlink.log" 2>&1; then
  echo "FAIL: accepted symbolic-link source" >&2
  exit 1
fi
test ! -e "$tmp/snapshots/symlink.ckd"
printf 'DO NOT OVERWRITE' > "$tmp/keep.ckd"
ln -s "$tmp/keep.ckd" "$tmp/snapshots/link.ckd"
if OFFLINE_CONFIRMED=YES bash "$root/scripts/backup-offline-dasd.sh" \
   "$tmp/source.ckd" "$tmp/snapshots/link.ckd" > "$tmp/destlink.log" 2>&1; then
  echo "FAIL: accepted symbolic-link destination" >&2
  exit 1
fi
test "$(cat "$tmp/keep.ckd")" = 'DO NOT OVERWRITE'
test -f "$tmp/source.ckd"
test "$(find "$tmp/snapshots" -type f | wc -l)" -eq 1
grep -q 'OFFLINE COPY AND BYTE COMPARISON PASSED' "$tmp/backup.log"
echo "OFFLINE DASD BACKUP HELPER GUARDS PASSED"
