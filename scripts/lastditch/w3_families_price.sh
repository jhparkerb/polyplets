#!/bin/bash
# Bounded-excess family tables: (a) the K=22 e<=3 table Undertow needs to pin
# levels k=20,21, and (b) an emax=4 cost ladder to price DEPTH 5.
#
# Purpose: depth j needs excess <= j-1 families.  D_1..D_4 at k<=21 need
# (K=22, emax=3); depth 5 needs emax=4, whose cost is unmeasured.  Each two
# extra depths buys one height of sweep, and a height is ~3x compute.
# Target machine: dalby (idle, 80 cores).  Predicted cost: (a) K=19/e=3 was
# 146 s at K=19, so K=22 ~ 10-30 min; (b) the ladder is K=8..14 at emax=4,
# deliberately small because the growth rate is the unknown being measured.
# Kill: kill the PID in ~/var/w3fam/pid.  Resume: re-run; existing .txt skipped.
set -euo pipefail
BIN=$HOME/src/pm-lastditch/build/severance_w3_families
OUT=$HOME/var/w3fam
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/price.txt"
run() {  # K EMAX
  f="$OUT/K$1_e$2.txt"
  [ -s "$f" ] && { echo "skip K=$1 e=$2" >> "$OUT/price.txt"; return; }
  /usr/bin/time -f "K=$1 emax=$2 wall=%e rss_kb=%M" "$BIN" families "$1" "$2" 40 \
    > "$f" 2>>"$OUT/price.txt"
}
# (b) first: the cheap ladder, so the emax=4 growth is known early
for K in 8 10 12 14; do run "$K" 4; done
# (a) the table Undertow actually needs
run 22 3
# (b) continued, only if the ladder said it is affordable
for K in 16 18; do run "$K" 4; done
echo DONE >> "$OUT/price.txt"
