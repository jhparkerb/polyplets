#!/bin/bash
# Motley rung 1 (Half Measure) production run: C_17(n), n <= 40.
#
# Purpose: the first height above the banked ladder.  Product is
# T(n,17) = C_17(n) - 2*C_16(n) + C_15(n), which closes a(n) for n <= 33
# rule-independently, and -- the point of the height -- the first MEASURED
# wall, RSS and state census above H = 16, which every RAM projection in
# results/second-sources.md currently rests on.
#
# Target machine: dalby.  Binary: ~/src/pm-halfmeasure/build/cutcount_b1,
# stamped b9d725be, clean worktree, gate-cutcount-b1 GREEN on that build.
#
# Predicted cost, from the measured H<=16 ladder (RSS x2.984/height, wall
# x3.209/height, results/cutcount_b1/calib_run.log) times Half Measure's
# measured payload factor 0.514 and its measured wall factor ~1/1.5:
#     peak RSS  ~91 GB   (I256 would have been 177 GB)
#     wall      ~7-10 h  on one core
# against dalby's 122 GB available.  The +-20% band on the census-ratio
# extrapolation puts the RSS at 73-109 GB; 109 GB still fits, with 13 GB to
# spare, which is why this launches without waiting for the check-split.
#
# NOT RESUMABLE: the engine checkpoints nothing, so a kill costs the whole
# attempt.  The unit is one height; nothing else is lost.
#
# Exact command:  ./dalby_motley_h17.sh
# Kill:           kill <pid of cutcount_b1>
#
# Fail-closed.  Three independent checks, all of which must pass:
#   1. the engine's own per-height self-checks (q0_zero, q1eval_binomial)
#      and the fits_pay bound, which exit 2 rather than write a wrapped row;
#   2. T(n,17) against results/triangle.txt for every n <= 40 -- the
#      incumbent's independently computed values, and the real oracle here;
#   3. C_15 and C_16 re-read from the step-0 rows, so the T assembly is
#      built only from rows that reproduced the banked ladder.

set -euo pipefail

BIN="$HOME/src/pm-halfmeasure/build/cutcount_b1"
OUT="$HOME/var/motley-h17"
ROWS="$HOME/var/motley-step0/rows"
TRIANGLE="$HOME/var/motley-h17/triangle.txt"
NMAX=40

mkdir -p "$OUT"

for H in 15 16; do
  [ -s "$ROWS/C$H.out" ] || { echo "MISSING $ROWS/C$H.out -- step 0 first" >&2; exit 1; }
done
[ -s "$TRIANGLE" ] || { echo "MISSING $TRIANGLE" >&2; exit 1; }

if [ ! -s "$OUT/C17.out" ]; then
  echo "=== C_17 start $(date -Is) host=$(hostname)" >> "$OUT/run.log"
  "$BIN" --height 17 $NMAX "$OUT/C17.out.tmp" 2>&1 | tee -a "$OUT/run.log"
  mv "$OUT/C17.out.tmp" "$OUT/C17.out"
  echo "=== C_17 done $(date -Is)" >> "$OUT/run.log"
fi

python3 - "$OUT/C17.out" "$ROWS/C16.out" "$ROWS/C15.out" "$TRIANGLE" <<'PY'
import sys

def rows(p):
    d = {}
    for line in open(p):
        n, v = line.split()
        d[int(n)] = int(v)
    return d

c17, c16, c15, tri = sys.argv[1:5]
C17, C16, C15 = rows(c17), rows(c16), rows(c15)
want = {}
for line in open(tri):
    if line.startswith('#'):
        continue
    n, H, v = line.split()
    if int(H) == 17:
        want[int(n)] = int(v)

match = mismatch = 0
for n in sorted(C17):
    t = C17[n] - 2 * C16[n] + C15[n]
    if n in want:
        if t == want[n]:
            match += 1
        else:
            mismatch += 1
            print(f"MISMATCH T({n},17): motley {t}  incumbent {want[n]}")
    elif t:
        print(f"NOTE T({n},17) = {t} with no banked value")

print(f"T(n,17) vs results/triangle.txt: {match} match, {mismatch} mismatch")
if mismatch or match == 0:
    sys.exit(2)
print("HALF MEASURE H=17: GREEN")
PY
