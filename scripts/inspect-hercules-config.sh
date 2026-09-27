#!/usr/bin/env bash
# Read-only inventory aid: NEVER assumes CMS virtual 191 equals
# a Hercules channel/device address or a particular backing file.
set -euo pipefail
if [[ $# -ne 1 || ! -f $1 || -L $1 ]]; then
  echo "Usage: bash scripts/inspect-hercules-config.sh /actual/hercules.cfg" >&2
  echo "Supply the verified active Hercules configuration, not a guess." >&2
  exit 2
fi
cfg=$(realpath -- "$1")
echo "CONFIGURATION: $cfg"
echo "HERCULES DEVICE DECLARATIONS (inventory ONLY):"
# Print CKD/CCKD filenames only. Do NOT dump arbitrary configuration
# records, which may embed network credentials or access tokens.
awk '
  /^[[:space:]]*([*#]|$)/ {next}
  {
    addr=$1
    type=toupper($2)
    if (type ~ /^(3330|3340|3350|3375|3380|3390|9345|CKD|CCKD)$/) {
      print "CONFIG LINE " NR ": " addr " " type " " $3
      found=1
    }
  }
  END {if (!found) print "No simple CKD declarations found; inspect includes and CP directory"}
' "$cfg"
echo
echo "IMPORTANT: Hercules channel addresses do NOT establish the"
echo "host image containing a particular CP minidisk. Correlate"
echo "the actual VM directory MDISK 191 entry, volume serial"
echo "MNT191, attached real device and Hercules configuration."
echo "Inventory is read-only and does not establish quiescence."
