#!/bin/bash
# Reproduce Confetti's five banked H=18 residue rows with the PARALLEL engine.
#
# Purpose: the decisive production check on cpp/motley_par.cpp.  Confetti took
# 399,700 s of wall on dalby -- five sequential single-core passes over
# results/cutcount_b1/residues/C18.p*.out.  If the parallel engine reproduces
# all five byte for byte in an hour, it is the same engine and the H=19 run is
# launchable.  Anything else and it is not.
# Target machine: ayr, 32 cores, 76 GB available, idle.
# Predicted cost: H=14/Nmax=40 measured 13.1 s at 32 threads on dalby and the
# per-height wall ratio is ~3.4x, so ~25 min per prime, ~2 h for five; peak RSS
# ~50 GB (H=14 was 718 MB, RSS ratio ~2.9x/height) -- fits, with margin, but it
# is the first time this engine has been run anywhere near this size, so the
# first pass IS the measurement.
# Kill: kill the PID in ~/var/motley-h18-par/pid.
# Resume: re-run; passes whose output file exists are skipped.
set -euo pipefail
BIN=$HOME/src/polyominoes/build/motley_par
OUT=$HOME/var/motley-h18-par
REF=$HOME/src/polyominoes/results/cutcount_b1/residues
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
for P in 2147483647 2147483629 2147483587 2147483579 2147483563; do
  f="$OUT/C18.p$P.out"
  if [ ! -s "$f" ]; then
    /usr/bin/time -f "p=$P wall=%e rss_kb=%M" "$BIN" --modp 18 40 "$P" "$f" \
      --threads 32 >> "$OUT/console.log" 2>> "$OUT/timings.txt"
  fi
  if cmp -s "$f" "$REF/C18.p$P.out"; then
    echo "p=$P IDENTICAL to banked Confetti row" >> "$OUT/timings.txt"
  else
    echo "p=$P MISMATCH vs banked Confetti row" >> "$OUT/timings.txt"
    exit 2
  fi
done
echo "ALL FIVE BANKED H=18 RESIDUE ROWS REPRODUCED" >> "$OUT/timings.txt"
