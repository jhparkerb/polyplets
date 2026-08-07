#!/usr/bin/env bash
# PURPOSE: pin the per-box PERIMETER-PRESERVING ("free") removal counts, which
#   are the factor the whole stable minimum-perimeter ladder convolves.
#   On king these converge to the 4-coloured partition numbers
#   1, 4, 14, 40, 105, 252, 574 (four corner Young diagrams). On square4 they
#   converge to something else -- 1, 4, 18, 60, 187 so far -- and pinning the
#   next terms needs a box far larger than any full PMAX sweep can afford,
#   because a box only gets term j right once its side exceeds j.
#
# COMMAND: scripts/perimeter_min_free_probe.sh
#
# TARGET: gympie, one core per box, <=10 at a time (the box's hard cap).
#
# PREDICTED COST (measured, ~1.8e6 nodes/s/core): the run is sum_{r<=6} C(M,r)
#   nodes for a box of M cells, so
#     square4 W=H=13 -> 85 cells,  C(85,6)=4.5e8  -> ~4 min
#     square4 W=H=15 -> 113 cells, C(113,6)=3.5e9 -> ~33 min   <- sets the wall
#     square4 W=H=12 -> 72 cells,  C(72,6)=1.6e8  -> ~2 min
#     square4 W=H=14 -> 98 cells,  C(98,6)=1.1e9  -> ~10 min
#   RAM is a couple of MB per process.
#
# RESUME/KILL: independent one-shot probes; kill any by PID, rerun that spec.
set -euo pipefail
cd "$(dirname "$0")/.."

make -s build/perimeter_min
OUT=results/perimmin_free_probe.txt
: > "$OUT"

# W H parity -- odd W is the diamond family (parity 0 is the exact diamond),
# even W the near-diamond family where both parity classes coincide.
SPECS=${SPECS:-"13 13 0|13 13 1|15 15 0|15 15 1|12 12 0|14 14 0"}

pids=()
IFS='|' read -ra LIST <<< "$SPECS"
for spec in "${LIST[@]}"; do
  tag=$(echo "$spec" | tr ' ' '_')
  ./build/perimeter_min square4 999 6 --only $spec \
      > "results/perimmin_free_$tag.txt" 2>/dev/null &
  pids+=($!)
  echo "launched $spec pid=${pids[-1]}"
done
wait

for spec in "${LIST[@]}"; do
  tag=$(echo "$spec" | tr ' ' '_')
  grep "^# box" "results/perimmin_free_$tag.txt" | sed 's/^# box //' >> "$OUT"
done
echo "--- $OUT"
cat "$OUT"
