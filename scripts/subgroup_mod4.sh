#!/bin/bash
# Subgroup-invariant polyplet counts to N=40, and the a(n) mod 4 check.
#
# PURPOSE: an independent second source for a(n) mod 4 at every n <= 40.  The
# banked a(40) has rows H15-19 (43.8% of the term) computed once, by the column
# engine, with no second source (ns_a40/PROVENANCE.md).  The three order-4
# subgroups of D4 give a(n) mod 4 from quotient-domain families of size
# ~lambda^(n/4), by orbit-graph Redelmeier -- a different algorithm on a
# different domain, so a shared bug is not the explanation if the bits agree.
#
# COMMAND:  bash scripts/subgroup_mod4.sh [N] [THREADS]     (default 40, 8)
# MACHINE:  laptop-scale.  No remote box, no ask needed.
#
# COST AT N=40, MEASURED 2026-08-07 on gympie, 8 threads:
#     c4       7.3 min
#     d2ax    15.0 min   (--byheight; this is the only d2ax sweep)
#     d2diag   8.2 min
#     d4       instant (the family is ~lambda^(n/8))
#   total ~31 min wall, peak RSS 4.6 MB (the grid is (2N+7)^2 cells).
#
# Do NOT extrapolate this by the growth of the COUNTS: the search also visits
# orbit-subsets whose lift is disconnected, so cost grows faster than I(H).
# Extrapolating the n=34 timings by the count ratio underpredicted N=40 by
# 4.5x. Time a smaller N and scale from that instead.
#
# KILL/RESUME: no checkpointing and none needed -- each type is a few minutes
# and independent.  Kill the numeric PID of the symcount_fast child; rerun the
# script to redo only what is missing (existing per-type outputs are reused).
set -euo pipefail
cd "$(dirname "$0")/.."

N=${1:-40}
THREADS=${2:-8}
BIN=build/symcount_fast
OUT=results/subgroup_counts.txt
RAW=results/subgroup_raw

[ -x "$BIN" ] || { echo "missing $BIN (run: make build/symcount_fast)" >&2; exit 1; }
mkdir -p "$RAW"

run() {  # run TYPE OUTFILE [extra flags...]
  local t=$1 f=$2; shift 2
  if [ -s "$f" ]; then
    echo "reusing $f"
  else
    echo "=== $t to n=$N on $THREADS threads $* ==="
    "$BIN" "$t" "$N" "$THREADS" "$@" > "$f.tmp"
    mv "$f.tmp" "$f"
  fi
}

for t in c4 d2diag d4; do
  run "$t" "$RAW/$t.n$N.out"
done

# Height-graded D2ax: D2ax is exactly the height-preserving subgroup of D4, so
# these give T(n,H) mod 2 -- one independent bit per triangle CELL, which
# localises the check to a height band instead of only the row total.
#
# This is the ONLY d2ax sweep. The flat counts are just its rows summed over
# H, so running d2ax twice (the 2026-08-07 run did, costing 15 wasted minutes)
# buys nothing.
run d2ax "$RAW/d2ax.byheight.n$N.out" --byheight
cp "$RAW/d2ax.byheight.n$N.out" results/subgroup_d2ax_byheight.txt
awk '{s[$1] += $3} END {for (n in s) print n, s[n]}' \
  "$RAW/d2ax.byheight.n$N.out" | sort -n > "$RAW/d2ax.n$N.out"

{
  echo "# Subgroup-invariant fixed-animal counts I(H) for the king (polyplet) lattice."
  echo "# Columns: <subgroup> <n> <value>.  Absent row means exactly 0."
  echo "#"
  echo "# I(H) = number of fixed (translation-class) animals invariant under EVERY"
  echo "# element of H.  This is NOT results/sym_counts.txt's per-element Fix(g):"
  echo "# I(d2ax) is fixed by both axis mirrors, Fix(h) by one.  Needed for the"
  echo "# D4 orbit-SIZE distribution, hence a(n) mod 4 (experiments/subgroup_mod4.py)."
  echo "#"
  echo "#   c4     = <r90>            order 4    I(C4) = Fix(r90)"
  echo "#   d2ax   = {e,h,v,r180}     order 4"
  echo "#   d2diag = {e,d,ad,r180}    order 4"
  echo "#   d4     = the full group   order 8"
  echo "#"
  echo "# Produced by scripts/subgroup_mod4.sh $N $THREADS"
  echo "# Source: $RAW/{c4,d2ax,d2diag,d4}.n$N.out"
  for t in c4 d2ax d2diag d4; do
    awk -v t="$t" '{print t, $1, $2}' "$RAW/$t.n$N.out"
  done
} > "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
echo "wrote $OUT"

python3 experiments/subgroup_mod4.py
