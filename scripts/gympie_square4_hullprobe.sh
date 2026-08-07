#!/usr/bin/env bash
# The two square4 frames that the 128-cell mask used to block, both aimed at the
# unresolved 6-corner / 8-corner factorisation in results/perimeter-both-ends.md.
#
#   W=16 parity 0 (128 cells) -- third point of the 6-corner family (12, 14, 16)
#   W=17 parity 1 (144 cells) -- third point of the 8-corner family (13, 15, 17)
#
# Both families' j=6 terms are currently UNCONVERGED (W=13 gave 2896 against
# W=15's 2924 for the 8-corner one), which is the leading explanation for why
# neither fits a product P^a C^b.  These settle it.
#
# --only runs ONE frame, and the thread pool is over frames, so each of these is
# single-threaded by construction; --threads would do nothing.
set -euo pipefail
cd "$(dirname "$0")/.."

run () {                        # W H parity rmax
  local W=$1 H=$2 par=$3 rmax=$4
  local out="results/perimmin_free_${W}_${H}_${par}.txt"
  echo "=== W=$W H=$H parity=$par rmax=$rmax -> $out"
  ./build/perimeter_min square4 999 "$rmax" --only "$W" "$H" "$par" \
      > "$out" 2> "results/perimmin_free_${W}_${H}_${par}.log"
  grep '^# box' "$out"
}

run 16 16 0 6
run 17 17 1 6
echo "HULLPROBE_DONE"
