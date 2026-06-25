#!/usr/bin/env bash
# Separate "threads" from "shard count" as the scaling lever. ayr's fine bracket showed a
# sharp drop at T=20/24 (23s) vs T=16 (40s); shard count = next_pow2(SHARD_MULT*threads),
# so T=16->256 but T=20->512. If shards are the lever, more shards should make LOW thread
# counts fast too (better: frees cores for more concurrent jobs). 2-D grid, min of 2 reps.
set -uo pipefail
cd "$(dirname "$0")/.."
H=${1:-11}; N=${2:-21}
ERR=runs/mt_shardsweep.err
echo ">>> shardsweep H=$H N=$N $(date -Is)  (cols = TMA_SHARD_MULT)"
printf "%-6s" "T\\M"
for M in 16 32 64 128; do printf "%10d" "$M"; done; echo
for T in 8 12 16 20; do
  printf "%-6s" "$T"
  for M in 16 32 64 128; do
    best=""
    for rep in 1 2; do
      TMA_SHARD_MULT=$M /usr/bin/time -v ./build/tma square8 "$N" --only-height "$H" \
          --modp 2147483647 --fold --threads "$T" >/dev/null 2>"$ERR"
      s=$(awk -F': ' '/Elapsed .wall clock/{print $2}' "$ERR")
      sec=$(awk -F: '{ if (NF==2) print $1*60+$2; else print $1 }' <<<"$s")
      if [ -z "$best" ] || awk "BEGIN{exit !($sec < $best)}"; then best=$sec; fi
    done
    printf "%10s" "${best}"
  done
  echo
done
echo ">>> done $(date -Is)"
