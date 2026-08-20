#!/bin/bash
# Family tables Undertow needs to pin levels k = 20, 21, plus the emax=4
# ladder that prices DEPTH 5.
#
# Purpose: D_j(k) at k <= 21 needs excess <= j-1 families with K >= 21.
# Depths 1-4 => emax 0..3.  Depth 5 => emax 4, whose cost is being measured:
# measured emax=4 at K=8/10/12 = 12.2 s/138 MB, 71.4 s/577 MB, 265 s/1.54 GB,
# i.e. ~1.82x per unit K in time and ~1.6x in RSS.  So K=22 emax=3 projects
# to ~35 min and single-digit GB; the K=16/18 emax=4 points below are the
# ladder that decides whether `families 21 4` (projected ~15 h, ~100 GB) is
# launchable at all -- it is NOT launched here.
# Target machine: dalby, 80 cores, 121 GB available, otherwise idle.
# Kill: kill the PID in ~/var/w3fam/pid2.  Resume: re-run, existing .txt skipped.
set -euo pipefail
BIN=$HOME/src/pm-lastditch/build/severance_w3_families
OUT=$HOME/var/w3fam
mkdir -p "$OUT"; echo $$ > "$OUT/pid2"
run() {
  f="$OUT/K$1_e$2.txt"
  [ -s "$f" ] && { echo "skip K=$1 e=$2" >> "$OUT/price.txt"; return; }
  /usr/bin/time -f "K=$1 emax=$2 wall=%e rss_kb=%M" "$BIN" families "$1" "$2" 40 \
    > "$f" 2>>"$OUT/price.txt"
}
for E in 0 1 2 3; do run 22 "$E"; done
echo TABLES_DONE >> "$OUT/price.txt"
for K in 16 18; do run "$K" 4; done
echo DONE >> "$OUT/price.txt"
