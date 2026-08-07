#!/usr/bin/env bash
# THE j=7 test: square4's diamond free-removal term at j=7.
#
# The cone/phi_2 model predicts 3452 with no free parameters (phi_2^4, see
# results/perimeter-both-ends.md).  The convergence rule is W = 2j+1, verified
# at j=4 -> W=9, j=5 -> W=11 and j=6 -> W=13 (W=13 and W=15 both gave 1388), so
# j=7 needs W=15 -- which is the frame we already have.  W=17 would give a
# second radius and cost 10.4h; this is the 1.76h single-radius test.
#
# Single-threaded by construction: --only runs ONE frame and the thread pool is
# over frames.  ~1.76h estimated from a measured 72.6s at W=13 rmax=6.
set -euo pipefail
cd "$(dirname "$0")/.."
out=results/perimmin_free_15_15_0_r7.txt
./build/perimeter_min square4 999 7 --only 15 15 0 > "$out" 2> "${out%.txt}.log"
grep '^# box' "$out"
echo "J7_DONE"
