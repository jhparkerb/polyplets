#!/bin/bash
# Motley single-thread baseline: --modp wall + peak RSS per height, Nmax=40.
#
# Purpose: anchor the per-height wall/RSS growth ratio of the CURRENT
# single-threaded engine, so the parallel rewrite has a measured speedup
# denominator and the H=19/20 projections in docs/b1-closure-plan.md get a
# fresh check.  Target machine: dalby (idle).  One core, sequential heights.
# Predicted cost: H=10..15 ~ 40 min total, peak RSS < 20 GB (H=15 measured
# 20.4 GB for the I256 payload; modp u32 is 328 B/window vs 8142, so < 2 GB).
# Kill: kill the PID in ~/var/motley-bench/pid.  Resume: re-run, it skips
# heights whose .out exists.
set -euo pipefail
BIN=$HOME/src/pm-halfmeasure/build/cutcount_b1
OUT=$HOME/var/motley-bench
P=2147483647
mkdir -p "$OUT"
echo $$ > "$OUT/pid"
: > "$OUT/timings.txt"
for H in 10 11 12 13 14 15; do
  f="$OUT/C$H.p$P.out"
  if [ -s "$f" ]; then echo "skip H=$H" >> "$OUT/timings.txt"; continue; fi
  /usr/bin/time -v "$BIN" --modp "$H" 40 "$P" "$f" > "$OUT/H$H.log" 2> "$OUT/H$H.time"
  w=$(grep 'Elapsed (wall clock)' "$OUT/H$H.time" | awk '{print $NF}')
  m=$(grep 'Maximum resident set size' "$OUT/H$H.time" | awk '{print $NF}')
  echo "H=$H wall=$w rss_kb=$m" >> "$OUT/timings.txt"
done
echo DONE >> "$OUT/timings.txt"
