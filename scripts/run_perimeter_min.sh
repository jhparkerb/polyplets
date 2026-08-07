#!/usr/bin/env bash
# PURPOSE: production census for the isoperimetric end of the site-perimeter
#   table -- the counts A(n,p) for p up to PMAX and area deficit i <= RMAX,
#   which is exactly the domain build/perimeter_min is complete on. Feeds
#   experiments/perimeter_min_ladder.py and results/perimeter-min-ladder.md.
#
# COMMAND (both lattices, in order):
#   scripts/run_perimeter_min.sh
#
# TARGET: gympie, 10 threads (the box's hard perf-core cap). One job at a time,
#   never both concurrently -- 10 threads each would be 20 on a 10-core budget.
#
# PREDICTED COST, from measured single-core points on gympie
#   (git=167dd4e, ~2.9e6 nodes/s/core):
#     square8: P=24 0.08 s / 6.6e5 nodes;  P=28 1.56 s / 8.2e6;  P=32 23.2 s /
#              6.8e7.  Node count grows ~8x per +4 in P, so P=40 ~ 4e9 nodes
#              ~ 1400 core-s; at 10 threads expect 200-400 s wall. The 9x9 box
#              alone is C(81,6) = 3.2e8 nodes ~ 110 s and is SERIAL (one box,
#              one thread), so that is the wall-clock floor.
#     square4: P=16 0.15 s / 1.8e6;  P=20 12.4 s / 6.1e7. Steeper (~33x per +4);
#              P=24 ~ 2e9 nodes ~ 700 core-s, at 10 threads expect 150-400 s.
#   Peak RSS is a few MB per thread (a <=128-cell box plus a small map), so RAM
#   is a non-issue on a 24 GB box -- this is pure CPU.
#
# RESUME/KILL: no checkpointing and none needed at these runtimes. To kill, read
#   the PID off the `event=start` line in the log and `kill` that number.
set -euo pipefail
cd "$(dirname "$0")/.."

THREADS=${THREADS:-10}
KING_P=${KING_P:-40}
ROOK_P=${ROOK_P:-24}
RMAX=${RMAX:-6}

make -s build/perimeter_min

run () {                        # lattice pmax
  local lat=$1 pmax=$2
  local out="results/perimmin_${lat}_p${pmax}_r${RMAX}.txt"
  local log="results/perimmin_${lat}_p${pmax}_r${RMAX}.log"
  echo "=== $lat PMAX=$pmax RMAX=$RMAX threads=$THREADS -> $out"
  ./build/perimeter_min "$lat" "$pmax" "$RMAX" --threads "$THREADS" \
      > "$out" 2> >(tee "$log" >&2)
  echo "--- wrote $out ($(grep -vc '^#' "$out") rows)"
}

# LATTICES selects which runs to do, so a follow-up pass that only needs one
# lattice does not redo the other at production size.
for lat in ${LATTICES:-square8 square4}; do
  case $lat in
    square8) run square8 "$KING_P" ;;
    square4) run square4 "$ROOK_P" ;;
    *) echo "unknown lattice $lat"; exit 2 ;;
  esac
done
echo "ALL RUNS DONE"
