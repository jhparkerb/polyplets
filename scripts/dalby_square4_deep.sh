#!/usr/bin/env bash
# The deep square4 free-removal campaign, sharded across dalby's cores.
#
# The cone/phi_2 model (results/perimeter.md) predicts the diamond's
# free-removal series as phi_2^4 = 1, 4, 18, 60, 187, 524, 1388, 3452, 8229.
# Measured through j=6 = 1388.  These runs reach j=7 and j=8, each at TWO hull
# radii, which is the standard this campaign has used for "converged" ever
# since W=13 and W=15 agreeing at 1388 refuted A120452.
#
#   W=15 rmax=8  (113 cells)  j<=8 at radius 15
#   W=17 rmax=8  (145 cells)  j<=8 at radius 17
#
# Sequential, not concurrent: the second is ~8x the first and there is no gain
# in starting it late.  Threads shard the removal DFS within the single frame
# (--only has one frame, so the frame pool cannot help); see check D in
# scripts/perimeter_min_gate.sh for what keeps that honest.
set -euo pipefail
cd "$(dirname "$0")/.."

T=${THREADS:-56}
echo "=== deep square4, threads=$T, started $(date -Is)"

for spec in "15 15 0 8" "17 17 0 8"; do
  set -- $spec
  W=$1 H=$2 PAR=$3 RMAX=$4
  out="results/perimmin_free_${W}_${H}_${PAR}_r${RMAX}.txt"
  echo "--- W=$W parity=$PAR rmax=$RMAX -> $out  ($(date -Is))"
  ./build/perimeter_min square4 999 "$RMAX" --only "$W" "$H" "$PAR" \
      --threads "$T" > "$out" 2> "${out%.txt}.log"
  grep '^# box' "$out"
done
echo "DEEP_DONE $(date -Is)"
