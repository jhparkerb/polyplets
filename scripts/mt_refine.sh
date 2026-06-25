#!/usr/bin/env bash
# Fine bracket-search for the true optimum thread count of the lock-free modp sweep,
# around the coarse power-of-two basin (ayr: best ~T=16, T=32 regressed). Dense integer
# grid, 2 reps each, report min (min = cleanest estimate, least polluted by transient
# interference on an otherwise-idle box). NUMA nodes are 8 cores wide, so node boundaries
# (8/16/24) are included as candidates.
set -uo pipefail
cd "$(dirname "$0")/.."
H=${1:-11}; N=${2:-21}
ERR=runs/mt_refine.err
echo ">>> refine H=$H N=$N $(date -Is)"
for T in 8 10 12 14 16 18 20 24; do
  best=""
  for rep in 1 2; do
    /usr/bin/time -v ./build/tma square8 "$N" --only-height "$H" --modp 2147483647 \
        --fold --threads "$T" >/dev/null 2>"$ERR"
    s=$(awk -F': ' '/Elapsed .wall clock/{print $2}' "$ERR")
    # seconds as float for min-tracking (mm:ss.xx or ss.xx)
    sec=$(awk -F: '{ if (NF==2) print $1*60+$2; else print $1 }' <<<"$s")
    echo "  T=$T rep=$rep wall=$s"
    if [ -z "$best" ] || awk "BEGIN{exit !($sec < $best)}"; then best=$sec; fi
  done
  echo "T=$T  min=${best}s"
done
echo ">>> done $(date -Is)"
