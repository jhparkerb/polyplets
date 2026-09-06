#!/bin/bash
# How does a FIXED-height sweep's DISK footprint grow in Nmax?
#
# WHY.  docs/five-terms-plan.md (deleted) prices the Nmax-45 sweep's disk peak at ~580 GB
# by taking the MEASURED CPU factor for Nmax 40->45 (1.442x at H=14, 1.466x at
# H=15, from results/nmax-scaling.txt) and applying it to the a(40) run's
# measured 363.4 GB disk peak.  Disk is not CPU, and nothing has ever checked
# that the two scale alike.  That single assumption is what decides the run:
# 580 GB against dalby's 563 GB free means the plan's own headline target does
# not fit, and the gap is 3% of the projection.  Worth measuring before
# committing 3.5 days to it.
#
# scripts/nmax_scaling.sh, which produced the CPU factors, recorded wall/cpu/
# rss only and `rm -rf`'d its spill dir at the end of each run -- so the disk
# number it was standing on was never taken.  This is the same ladder with the
# disk kept and sampled.
#
# WHAT IT DOES.  Heights 14, 15, 16 at maxn 40, 42, 45.  Three heights, not two,
# because the CPU exponent was measured to CLIMB with height (+0.14/height from
# H=14 to H=15) and a two-point disk factor could not show the same drift.  Peak
# rundir size is sampled by scripts/dalby_du_monitor.sh at 10 s; the spill dir
# is kept until after the sample, which is the whole point.
#
# TARGET: dalby, 40 cores.  Box is idle.
# PREDICTED COST.  From results/nmax-scaling.txt's cpu-seconds, which are the
# core-count-invariant quantity: H=14 sums to 6044 cpu-s over the three Nmax,
# H=15 to 17,040, H=16 projected ~57,500 at the measured ~3.4x per height.
# Total ~80,600 cpu-s / 40 cores = ~34 min wall plus per-run startup.  Budget
# under an hour.  RAM ~100 MB per run (measured, and it FALLS with Nmax).
# Disk: unknown by construction, but H<=19 totalled 69 GB on the whole a(40)
# run, so three heights at H<=16 is single-digit GB against 563 GB free.
#
# NOT A PRODUCTION RUN.  Nothing here is banked; it produces one ratio.
#
# Usage: scripts/dalby_nmax_disk.sh
# Kill:  kill the PID in ~/var/nmax-disk/pid   (no checkpointing wanted -- the
#        longest single run is ~10 min, so a kill costs one rung, not a run.)
set -euo pipefail
cd ~/src/polyominoes
OUT=$HOME/var/nmax-disk
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/disk.txt"
CORES=${CORES:-40}
{
  echo "=== nmax disk ladder: $(date -Iseconds)"
  echo "=== rev $(git rev-parse --short HEAD) cores=$CORES"
} >> "$OUT/disk.txt"
for H in 14 15 16; do
  for N in 40 42 45; do
    R="$OUT/run.H$H.N$N"
    rm -rf "$R"; mkdir -p "$R/spill" "$R/perheight"
    ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
        --cores "$CORES" --ram 1073741824 --overlap-heights 1 --heights "$H" \
        --run-dir "$R" --spill-dir "$R/spill" \
        --checkpoint "$R/POLYCKPT" --checkpoint-every 3600 \
        --per-height-out "$R/perheight" \
      > "$R/run.log" 2>&1 &
    OPID=$!
    ./scripts/dalby_du_monitor.sh "$R" "$OPID" 10 &
    wait "$OPID"; rc=$?
    peak=$(awk '{print $2}' "$R.rundir_size.log" 2>/dev/null | sort -n | tail -1)
    final=$(du -sm "$R" | cut -f1)
    echo "H=$H maxn=$N rc=$rc peak_mb=${peak:-NA} final_mb=$final" >> "$OUT/disk.txt"
    rm -rf "$R"
  done
done
echo DONE >> "$OUT/disk.txt"
