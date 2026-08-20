#!/bin/bash
# motley_par thread-scaling at H=13/14, Nmax=40, one 31-bit prime.
# Purpose: the speedup denominator for the H=19/20 pricing.  Target: dalby,
# idle.  Predicted cost: < 10 min total, peak RSS ~1.1 GB (H=14 serial
# measured 1.05 GB).  Kill: kill the PID in ~/var/motley-scale/pid.
set -euo pipefail
cd ~/src/pm-lastditch
OUT=$HOME/var/motley-scale
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/scale.txt"
for H in 13 14; do
  for T in 1 8 32 80; do
    /usr/bin/time -f "H=$H threads=$T wall=%e rss_kb=%M" \
      ./build/motley_par --modp "$H" 40 2147483647 "$OUT/p$H.$T.out" --threads "$T" \
      2>>"$OUT/scale.txt" >/dev/null
  done
  # every thread count must give the identical row
  for T in 8 32 80; do
    cmp -s "$OUT/p$H.1.out" "$OUT/p$H.$T.out" || { echo "H=$H T=$T DIFFERS" >> "$OUT/scale.txt"; exit 2; }
  done
  echo "H=$H all thread counts byte-identical" >> "$OUT/scale.txt"
done
echo DONE >> "$OUT/scale.txt"
