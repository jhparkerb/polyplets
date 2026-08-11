#!/usr/bin/env bash
# run_atoms_h9.sh — scaling-exploration probe (Teammate B): C_9(n) mod two
# primes to n=3000, for the atom degree q_9 via Berlekamp-Massey.
#
# Purpose: third new point of the Hankel-rank growth sequence (q_7=181,
#   q_8=462 measured today; expect q_9 ~ 1200, needs ~2.2x terms + holdout).
# Command: bash scripts/run_atoms_h9.sh   (repo root, gympie, tmux window)
# Machine: gympie. Predicted cost: measured H=8 N=1400 = 65 s/prime; scale
#   x2.97 (transitions) x(3000/1400)^2 (areas x columns) => ~15 min/prime,
#   2 primes in parallel = 2 cores (my full budget), ~400 MB each.
# Resume: rerun; per-prime output files are atomic (tmp+mv). Kill: kill PIDs.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p results/atoms_ext
./build/cutcount_b1 --modp 9 3000 2147483629 results/atoms_ext/C9.p1.txt.tmp 2>results/atoms_ext/C9.p1.log &
P1=$!
./build/cutcount_b1 --modp 9 3000 2147483587 results/atoms_ext/C9.p2.txt.tmp 2>results/atoms_ext/C9.p2.log &
P2=$!
wait $P1 $P2
mv results/atoms_ext/C9.p1.txt.tmp results/atoms_ext/C9.p1.txt
mv results/atoms_ext/C9.p2.txt.tmp results/atoms_ext/C9.p2.txt
python3 scripts/atoms_bm.py 9 2147483629 results/atoms_ext/C9.p1.txt 2147483587 results/atoms_ext/C9.p2.txt | tee results/atoms_ext/q9_verdict.txt
