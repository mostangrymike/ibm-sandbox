#!/usr/bin/env bash
# Read-only helper: match CP QUERY MDISK ... LOCATION Rdev to an
# explicitly supplied Hercules CKD config and verified process cwd.
# DO NOT infer that the CMS virtual device is the Hercules real device.
set -euo pipefail
if [[ $# != 3 ]]; then
  echo "Usage: bash scripts/map-cms-minidisk.sh <CP-Rdev-hex> <active.cfg> <verified-Hercules-cwd>" >&2
  echo "Example (addresses/paths are illustrative only):" >&2
  echo "  bash scripts/map-cms-minidisk.sh 0125 /path/hercules.cnf /path/hercules-working-dir" >&2
  exit 2
fi
rdev=${1^^}
cfg=$2
cwd=$3
if [[ ! $rdev =~ ^[0-9A-F]{1,4}$ ]]; then
  echo "STOP: expected the real Rdev from CP QUERY MDISK LOCATION (1-4 hex digits)" >&2
  exit 2
fi
printf -v rdev '%04X' "$((16#$rdev))"
if [[ ! -f $cfg || -L $cfg || ! -d $cwd ]]; then
  echo "STOP: supply an existing regular config and verified Hercules cwd" >&2
  exit 2
fi
cfg=$(realpath -- "$cfg")
cwd=$(realpath -- "$cwd")
echo "CP REAL DEVICE: $rdev"
echo "ACTIVE CONFIG: $cfg"
echo "VERIFIED HERCULES CWD: $cwd"
# Match only straightforward, uncommented CKD config statements.
# This helper intentionally refuses ambiguity and INCLUDE, aliases,
# dynamically attached devices and unexpanded environment variables.
mapfile -t candidates < <(awk -v needle="$rdev" '
  /^[[:space:]]*([*#]|$)/ {next}
  {
    addr=toupper($1)
    gsub(/^0+/, "", addr)
    if (addr == "") addr="0"
    target=needle
    gsub(/^0+/, "", target)
    if (target=="") target="0"
    type=toupper($2)
    if (addr==target && type ~ /^(3330|3340|3350|3375|3380|3390|9345|CKD|CCKD)$/)
      print $3
  }
' "$cfg")
if [[ ${#candidates[@]} != 1 ]]; then
  echo "STOP: found ${#candidates[@]} simple CKD declaration(s) for $rdev" >&2
  echo "Check all INCLUDE files, dynamic device changes and CP mapping manually." >&2
  exit 4
fi
raw=${candidates[0]}
if [[ -z $raw || $raw == *'$'* || $raw == *'%'* || $raw == *'*'* ]]; then
  echo "STOP: unresolved or globbed backing-image filename" >&2
  exit 4
fi
if [[ $raw == /* ]]; then
  image=$raw
else
  image=$cwd/$raw
fi
if [[ ! -f $image || -L $image ]]; then
  echo "STOP: resolved image does not exist as a regular non-symlink file: $image" >&2
  exit 4
fi
image=$(realpath -- "$image")
echo "CONFIGURED BASE IMAGE: $image"
stat -c 'IMAGE BYTES: %s' -- "$image"
echo "NOT YET VERIFIED: real disk VOLSER, minidisk offset and image overlays."
echo "DO NOT COPY until the CP LOCATION Vol-ID/StartLoc/Size agree,"
echo "all INCLUDE and shadow files are inspected, and storage is quiesced."
