#!/usr/bin/env bash
# Measure the multithreaded modp sweep's scaling knee: wall time of a heavy strip
# height at increasing thread counts. The serial path saturated nothing (1 thread);
# within-height MT is expected to be memory-bandwidth bound, so this finds where
# adding threads stops helping -- the number that sizes jobs x threads per box.
set -uo pipefail
cd "$(dirname "$0")/.."
ERR=runs/mt_scaling.err
echo ">>> MT scaling: build/tma square8, modp+fold, $(date -Is)"
for spec in "11 21" "13 20" "13 21"; do
  set -- $spec; H=$1; N=$2
  prev=""
  for T in 1 4 8 16 32; do
    /usr/bin/time -v ./build/tma square8 "$N" --only-height "$H" --modp 2147483647 \
        --fold --threads "$T" >/dev/null 2>"$ERR"
    secs=$(awk -F': ' '/Elapsed .wall clock/{print $2}' "$ERR")
    rss=$(awk -F': ' '/Maximum resident/{print $2}' "$ERR")
    echo "H=$H N=$N T=$T  wall=$secs  rss_kb=$rss"
  done
done
echo ">>> done $(date -Is)"
