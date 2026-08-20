#!/bin/bash
# How does a FIXED-height sweep cost grow in Nmax?
#
# Purpose: the whole reach claim turns on this and nobody has measured it.
# The ladder's 4.4x per term is the cost of raising Nmax AND H_sweep together.
# Undertow lowers H_sweep by two, so what matters now is the cost of raising
# Nmax alone -- if that is polynomial and mild, one sweep at a fixed height
# covers several new rows, and if it is not, it covers one.
# Heights 14 and 15 are chosen because they are minutes, not hours, and the
# exponent is a ratio, not an absolute.
# Target: dalby, 8 cores (small on purpose -- the box has three other jobs and
# this needs a STABLE core count more than it needs speed).
# Predicted cost: H=14/maxn=40 is minutes; six runs, well under an hour, RSS
# ~1 GB, disk a few GB.  Kill: kill the PID in ~/var/nmax-scale/pid.
set -euo pipefail
cd ~/src/polyominoes
OUT=$HOME/var/nmax-scale
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/scaling.txt"
for H in 14 15; do
  for N in 40 42 45; do
    R="$OUT/run.H$H.N$N"
    rm -rf "$R"; mkdir -p "$R/spill" "$R/perheight"
    /usr/bin/time -f "H=$H maxn=$N wall=%e cpu=%U rss_kb=%M" \
      ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
        --cores 8 --ram 1073741824 --overlap-heights 1 --heights "$H" \
        --run-dir "$R" --spill-dir "$R/spill" \
        --checkpoint "$R/POLYCKPT" --checkpoint-every 3600 \
        --per-height-out "$R/perheight" \
      > "$R/run.log" 2>> "$OUT/scaling.txt"
    rm -rf "$R/spill"
  done
done
echo DONE >> "$OUT/scaling.txt"
