#!/bin/bash
# Per-cell mod 4 on the a(40) triangle, as far as the existing engines reach.
#
# PURPOSE: `results/subgroup-mod4.md` ships T(n,H) = I_H(D2ax) (mod 2) on all
# 820 cells. The mod-4 refinement
#
#   T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax)   (mod 4)
#
# is currently confirmed on 78 cells (n<=12) only. This is NOT an attempt to
# reach n=40 -- that needs a vmirror sweep mode that does not exist, and r180's
# cost peaks at exactly the H=15..19 band (results/symtm_strip_profile_n40.txt).
# It runs the identity out to n=32 to check the ALGEBRA at scale, which is
# worth doing because the mod-8 companion shipped with a wrong coefficient and
# was caught only by printing it against 33 rows of banked data.
#
# The two inputs come from one hmirror sweep: summing its (n,H,W) rows over W
# gives I_H(<h>), and grouping by W instead gives I_W(<v>), since transposing
# an h-symmetric W x H animal yields a v-symmetric H x W one.
#
# COMMAND:  bash scripts/percell_mod4.sh [N] [THREADS]     (default 32, 8)
# MACHINE:  gympie, laptop-scale.
#
# PREDICTED COST at N=32, extrapolated from MEASURED full sweeps at N=24 and
# N=28 (hmirror 3.36s -> 64.09s, 2.09x/n; r180 2.83s -> 35.77s, 1.88x/n, both
# 8 threads):  hmirror ~20 min, r180 ~8 min, ~30 min total. Extrapolation over
# 4 terms, so treat it as a ballpark: the same style of estimate for
# symcount_fast underpredicted by 4.5x.
#
# KILL/RESUME: no checkpointing. Kill the numeric PID of the symtm child;
# rerun to redo only what is missing (per-mode outputs are reused).
set -euo pipefail
cd "$(dirname "$0")/.."

N=${1:-32}
THREADS=${2:-8}
BIN=build/symtm
RAW=results/percell_raw

[ -x "$BIN" ] || { echo "missing $BIN (run: make build/symtm)" >&2; exit 1; }
mkdir -p "$RAW"

for mode in hmirror r180; do
  f="$RAW/$mode.byheight.n$N.out"
  if [ -s "$f" ]; then
    echo "reusing $f"
  else
    echo "=== $mode to n=$N on $THREADS threads --byheight ==="
    "$BIN" "$mode" "$N" "$THREADS" --byheight > "$f.tmp"
    mv "$f.tmp" "$f"
  fi
done

python3 experiments/percell_mod4.py "$N"
