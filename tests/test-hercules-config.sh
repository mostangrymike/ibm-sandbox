#!/bin/sh
# Read-only config parser test on synthetic, harmless fixture.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
cat > "$tmp/example.cnf" <<'EOF'
# A commented out CKD must be ignored:
# 0123 3390 /not/an/image
0123 3390 /synthetic/disks/system.cckd
0A00 CCKD /synthetic/disks/backup.cckd
0A01 3270
CONSOLE 001F
INCLUDE /synthetic/disks/extra.cfg
EOF
bash "$root/scripts/inspect-hercules-config.sh" "$tmp/example.cnf" > "$tmp/result"
grep -q 'CONFIG LINE 3: 0123 3390 /synthetic/disks/system.cckd' "$tmp/result"
grep -q 'CONFIG LINE 4: 0A00 CCKD /synthetic/disks/backup.cckd' "$tmp/result"
! grep -q '/not/an/image' "$tmp/result"
grep -q 'does not establish quiescence' "$tmp/result"
if bash "$root/scripts/inspect-hercules-config.sh" "$tmp/missing.cnf" >/dev/null 2>&1; then
  echo "FAIL: accepted nonexistent configuration" >&2
  exit 1
fi
ln -s "$tmp/example.cnf" "$tmp/link.cnf"
if bash "$root/scripts/inspect-hercules-config.sh" "$tmp/link.cnf" >/dev/null 2>&1; then
  echo "FAIL: accepted symlink configuration" >&2
  exit 1
fi
echo 'HERCULES CONFIG READ-ONLY INVENTORY GUARDS PASSED'
