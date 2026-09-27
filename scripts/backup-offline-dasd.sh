#!/usr/bin/env bash
# Make a byte-exact, checked copy of ONE offline Hercules DASD backing file.
# Operator must identify actual CMS 191 backing image and quiesce VM first.
# Does not modify source. Not suitable for live/distributed storage snapshots.
set -euo pipefail
if [[ $# -ne 2 || "${OFFLINE_CONFIRMED:-}" != YES ]]; then
  printf '%s\n' \
    "Usage: OFFLINE_CONFIRMED=YES bash scripts/backup-offline-dasd.sh" \
    "       /verified/path/to/source-dasd /different/volume/backup-file" \
    "Run ONLY after the actual guest and emulator accessing the image" \
    "are stopped, and all overlay/dependent DASD files identified." >&2
  exit 2
fi
src=$1
dest=$2
[[ -f $src && ! -L $src ]] || {
  echo 'STOP: source must be a verified, regular, non-symlink file' >&2
  exit 3
}
[[ ! -e $dest && ! -L $dest ]] || {
  echo 'STOP: destination already exists; will never replace it' >&2
  exit 3
}
command -v sha256sum >/dev/null || {
  echo 'STOP: sha256sum is required' >&2; exit 3;
}
src=$(realpath -- "$src")
dir=$(dirname -- "$dest")
[[ -d $dir && -w $dir ]] || {
  echo 'STOP: backup destination directory is not writable' >&2
  exit 3
}
dest="$(cd "$dir" && pwd -P)/$(basename -- "$dest")"
[[ $src != "$dest" ]] || {
  echo 'STOP: source and destination identical' >&2; exit 3;
}
if command -v fuser >/dev/null 2>&1; then
  if fuser -s -- "$src" 2>/dev/null; then
    echo 'STOP: source in use; do not copy a running DASD' >&2
    exit 3
  fi
else
  echo 'NOTE: fuser unavailable; confirm source is OFFLINE yourself' >&2
fi
# Do not try to infer whether the source is a whole pack, overlay,
# CKD image or ordinary file. Verify dependencies before using script.
srcbytes=$(stat -c %s -- "$src")
echo "COPYING verified offline source: $src"
echo "Source bytes: $srcbytes"
tmp="$dest.incomplete.$$"
if [[ -e $tmp || -L $tmp ]]; then
  echo 'STOP: temporary backup name already exists' >&2; exit 3
fi
cleanup() {
  if [[ -e $tmp ]]; then
    echo "INCOMPLETE backup retained for inspection: $tmp" >&2
  fi
}
trap cleanup EXIT
cp --reflink=never --sparse=never -- "$src" "$tmp"
sync -- "$tmp"
destbytes=$(stat -c %s -- "$tmp")
[[ $srcbytes = "$destbytes" ]] || {
  echo 'STOP: backup length does not match' >&2; exit 4;
}
echo 'COMPARE SOURCE AND DESTINATION:'
cmp -- "$src" "$tmp" || {
  echo 'STOP: backup bytes do not match' >&2; exit 4;
}
echo 'SOURCE SHA256:'
sha256sum -- "$src"
echo 'BACKUP SHA256:'
sha256sum -- "$tmp"
mv -n -- "$tmp" "$dest"
[[ -f $dest && ! -e $tmp ]] || {
  echo 'STOP: could not finalize backup' >&2; exit 4;
}
sync -- "$dest"
trap - EXIT
echo "OFFLINE COPY AND BYTE COMPARISON PASSED: $dest"
