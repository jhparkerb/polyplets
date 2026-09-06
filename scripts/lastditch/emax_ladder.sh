#!/bin/bash
# Per-EXCESS cost ratio of the bounded-excess family DP, at fixed K.
#
# Lane C (results/undertow.md, C-R1) asks whether depths 8-9 are
# reachable, which decides whether the tower can be pinned entirely from
# strip-confirmed H<=14 cells.  Depth j needs emax = j-1.  Lane C requested
# K=22 at EMAX=4,5,6; the lead reshaped it, because emax=4 at K=22 alone
# extrapolates to ~46 h and ~220 GB from the MEASURED K=8/10/12 ladder
# (138 MB, 577 MB, 1.54 GB) and does not fit the box.
#
# What actually decides it is the ratio per unit of e, and that is visible at
# small K in minutes.  Fixed K=10; e = 0..7.  If the per-e RAM ratio is >= 7x,
# e=7 at K=21 is hopeless and Lane C's route dies on arithmetic; if it is
# ~2-3x, it is an engineering question and worth pricing properly.
#
# Target: ayr (dalby is running the H=18 release gate).  NOT gympie -- Lane C
# ran ~20 s of this on gympie against the ban, and these numbers replace those.
# Predicted: seconds to a few minutes per point at K=10; RSS under 10 GB at
# e<=7 EXTRAPOLATED from 577 MB at e=4.  Decision it changes: whether C-R1
# gets a real dalby run at all.
# Kill: kill the PID in ~/var/emax-ladder/pid.
set -euo pipefail
BIN=$HOME/src/polyominoes/build/severance_w3_families
OUT=$HOME/var/emax-ladder
mkdir -p "$OUT"; echo $$ > "$OUT/pid"; : > "$OUT/ladder.txt"
for E in 0 1 2 3 4 5 6 7; do
  timeout 3600 /usr/bin/time -f "K=10 emax=$E wall=%e rss_kb=%M" \
    "$BIN" families 10 "$E" 16 > "$OUT/K10_e$E.txt" 2>>"$OUT/ladder.txt" \
    || { echo "K=10 emax=$E TIMED OUT or failed" >> "$OUT/ladder.txt"; break; }
done
echo DONE >> "$OUT/ladder.txt"
