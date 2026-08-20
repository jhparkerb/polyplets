#!/bin/bash
# Settle depth 5's cost: emax=4 at K=14 and K=16.
#
# The per-K ratio at emax=4 is DECELERATING -- 4.18x per +2K from K=8->10,
# 2.68x from K=10->12 -- so emax=4 at K=21 lands anywhere from ~110 GB (trust
# the later slope) to ~390 GB (trust the geometric mean), against dalby's
# 121 GB.  Every plan in the tree that quotes "depth 5, ~16 h, ~103 GB" is
# resting on the optimistic end of that.  K=14 and K=16 pin the slope.
#
# Target: ayr, 16 threads.  Predicted from the measured ladder (138 MB / 577 MB
# / 1.54 GB at K=8/10/12): K=14 ~4 GB and ~15 min, K=16 ~11 GB and ~50 min,
# both EXTRAPOLATED one and two steps.  Decision it changes: whether depth 5
# is a launchable job at all, and therefore whether the "depth 5 or Motley
# C_19" choice for closing T(40,19) has two options or one.
# Kill: kill the PID in ~/var/emax4-k/pid.
set -euo pipefail
BIN=$HOME/src/polyominoes/build/severance_w3_families
OUT=$HOME/var/emax4-k
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/kladder.txt"
for K in 14 16; do
  timeout 14400 /usr/bin/time -f "K=$K emax=4 wall=%e rss_kb=%M" \
    "$BIN" families "$K" 4 16 > "$OUT/K${K}_e4.txt" 2>>"$OUT/kladder.txt" \
    || { echo "K=$K emax=4 TIMED OUT or failed" >> "$OUT/kladder.txt"; break; }
done
echo DONE >> "$OUT/kladder.txt"
