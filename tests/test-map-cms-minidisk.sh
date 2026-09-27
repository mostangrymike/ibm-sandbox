#!/usr/bin/env bash
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd -P)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/run"
printf 'SYNTHETIC TEST DATA' > "$tmp/run/dasd3"
cat > "$tmp/hercules.cnf" <<'EOF'
# 0125 3390 wrong
0123 3390 dasd1
0124 3390 dasd2
0125 3390 dasd3
0126 3390 dasd4
EOF
bash "$repo/scripts/map-cms-minidisk.sh" 125 "$tmp/hercules.cnf" "$tmp/run" > "$tmp/result"
grep -q 'CP REAL DEVICE: 0125' "$tmp/result"
grep -q "CONFIGURED BASE IMAGE: $tmp/run/dasd3" "$tmp/result"
grep -q 'NOT YET VERIFIED' "$tmp/result"
if bash "$repo/scripts/map-cms-minidisk.sh" 0123 "$tmp/hercules.cnf" "$tmp/run" > /dev/null 2>&1; then
  echo "FAIL: accepted missing backing image" >&2
  exit 1
fi
if bash "$repo/scripts/map-cms-minidisk.sh" not-hex "$tmp/hercules.cnf" "$tmp/run" > /dev/null 2>&1; then
  echo "FAIL: accepted invalid Rdev" >&2
  exit 1
fi
echo '0125 3390 another-disk' >> "$tmp/hercules.cnf"
if bash "$repo/scripts/map-cms-minidisk.sh" 0125 "$tmp/hercules.cnf" "$tmp/run" > /dev/null 2>&1; then
  echo "FAIL: accepted duplicate mapping" >&2
  exit 1
fi
echo 'CP/HERCULES REAL DEVICE READ-ONLY MAPPING GUARDS PASSED'
