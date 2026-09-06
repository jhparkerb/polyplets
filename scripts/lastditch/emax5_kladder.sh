#!/bin/bash
# Settle depth 6's cost the way depth 5's was settled: an emax=5 K-ladder at
# FIXED thread count.
#
# WHY.  docs/time-at-the-bar-report.md (deleted)'s B2 re-price found that disk is no
# longer what caps the five terms -- done at the target Nmax, the Hs=20 poles
# are 252 GB (n<=44) and 277 GB (n<=45) against Hs=21's 580 GB, and dalby has
# 563 GB free.  What binds instead is that J=6 is ASSERTED: ~20-60 h and
# ~50-100 GB, obtained by applying the per-excess ladder's ~6x RSS and ~7-9x
# wall once to J=5's projection.  That is exactly the kind of number depth 5
# had (16 h / 103 GB) before five rungs measured it at 3.1 h / 8.5 GB, an order
# of magnitude out.  This is those rungs, for depth 6.
#
# FIXED THREADS IS NOT A DETAIL.  The family DP builds per-thread private maps
# and merges after, so RSS scales with thread count and a K-slope that mixes
# thread counts is not a slope (results/undertow.md, methodology
# note).  8 threads throughout, matching results/undertow.md so the
# two ladders are comparable rung for rung.
#
# Target: dalby, 8 threads.  Predicted from the emax=4 ladder at 8 threads
# (K=8 6.52s/129MB, K=10 48.16s/463MB, K=12 219.2s/1150MB, K=14 731.86s/2459MB)
# times the asserted ~7-9x wall and ~6x RSS per unit of emax:
#
#     K=8    ~45 s      ~0.8 GB
#     K=10   ~6 min     ~2.8 GB
#     K=12   ~25 min    ~7 GB
#     K=14   ~1.4 h     ~15 GB        <- EXTRAPOLATED, and the point of the run
#
# Total ~2 h, peak ~15 GB, against dalby's 125 GB.  Every one of those four
# numbers is what this ladder exists to replace.  Four rungs is what depth 5
# needed before its K=16 holdout came in within 8% on both axes; if the ratio
# decelerates the same way, K=21 will land far under the asserted 50-100 GB.
#
# Decision it changes: whether Hs=20 + J=6 -> n<=45 is a real option, which is
# the row of B2's table that reaches the same n as the H=21 pole for a third of
# the disk.
#
# Kill/resume: kill the PID in ~/var/emax5-k/pid.  No resume -- each rung is
# independent and rerunning one costs only that rung.
set -euo pipefail
BIN=$HOME/src/polyominoes/build/severance_w3_families
OUT=$HOME/var/emax5-k
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/kladder.txt"
echo "start $(date -Is) rev=$(cd $HOME/src/polyominoes && git rev-parse --short HEAD)" \
  >> "$OUT/kladder.txt"
for K in 8 10 12 14; do
  timeout 21600 /usr/bin/time -f "K=$K emax=5 threads=8 wall=%e rss_kb=%M" \
    "$BIN" families "$K" 5 8 > "$OUT/K${K}_e5.txt" 2>>"$OUT/kladder.txt" \
    || { echo "K=$K emax=5 TIMED OUT or failed" >> "$OUT/kladder.txt"; break; }
  echo "-- K=$K done $(date -Is)" >> "$OUT/kladder.txt"
done
echo DONE >> "$OUT/kladder.txt"
