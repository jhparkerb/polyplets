#!/bin/bash
# Phase 2b: does the nullity GROW the way a genuine minimal relation forces?
#
# If P(t, F) = 0 is a genuine algebraic relation of degree K0 in F and t-degree
# L0, then in the box (K, L) the relation space contains F^i t^j P for
# 0 <= i <= K-K0, 0 <= j <= L-L0, so nullity >= (K-K0+1)(L-L0+1) and it must
# rise by exactly that pattern as the box opens. Same for a P-recurrence:
# shifting n and multiplying the coefficients by n both stay inside a larger
# box. Spurious rank defects do not do this. This grid is the internal
# consistency check on the (4,22) algebraic candidate and the (19,3) /
# (27,2) P-recurrence candidates.
#
#   target: gympie, local, single-threaded
#   cost:   ~15 s (measured)
#   usage:  scripts/dir4_perim_nullity_grid.sh 2>&1 \
#             | tee results/dir4_perim_nullity_grid.log
set -u
cd "$(dirname "$0")/.."

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
HV=results/convex_perim_terms_s200.txt
NULL=build/dir4_perim_null199.txt
SRC=results/convex_area_terms_n700_king.txt   # the null control's real source
[ -f "$SRC" ] || { echo "missing $SRC (results/convex-polyplets.md)" >&2; exit 1; }
head -199 "$SRC" > "$NULL"   # re-cut every run; never reuse a stale copy

nul() {  # nul <file> <mode> <A> <B> -> nullity, or "-" if undecidable
  "$G" "$2" "$1" "$3" "$4" 2>/dev/null | awk '
    /^UNDERDETERMINED/{u=1}
    /^full rank=/{n=$NF; sub(/^nullity=/,"",n)}
    END{ if(u) print "-"; else print n }'
}

echo "### alg mode: nullity(K,L) for the dir4 series"
echo "### predicted by a minimal (K0,L0)=(4,22) relation: (K-3)(L-21), else -"
printf '%6s' "K\\L"; for L in 20 21 22 23 24 25 26 27 28; do printf '%6s' "$L"; done; echo
for K in 3 4 5 6 7; do
  printf '%6s' "$K"
  for L in 20 21 22 23 24 25 26 27 28; do printf '%6s' "$(nul "$DIR4" alg "$K" "$L")"; done
  echo
done
echo "predicted:"
printf '%6s' "K\\L"; for L in 20 21 22 23 24 25 26 27 28; do printf '%6s' "$L"; done; echo
for K in 3 4 5 6 7; do
  printf '%6s' "$K"
  for L in 20 21 22 23 24 25 26 27 28; do
    p=$(( (K-3)*(L-21) )); [ "$p" -lt 0 ] && p=0
    unk=$(( (K+1)*(L+1) )); [ "$unk" -ge 200 ] && p="-"
    printf '%6s' "$p"
  done
  echo
done

echo
echo "### same grid on the null control (must be all zero)"
printf '%6s' "K\\L"; for L in 20 21 22 23 24 25 26 27 28; do printf '%6s' "$L"; done; echo
for K in 3 4 5 6 7; do
  printf '%6s' "$K"
  for L in 20 21 22 23 24 25 26 27 28; do printf '%6s' "$(nul "$NULL" alg "$K" "$L")"; done
  echo
done

echo
echo "### prec mode: nullity(J,D) around the frontier, dir4 / null / hv"
printf '%8s %6s %6s %6s\n' "box" "dir4" "null" "hv"
for spec in "18 3" "19 3" "20 3" "21 3" "22 3" "19 2" "19 4" "19 5" \
            "26 2" "27 2" "28 2" "29 2" "12 9" "13 9" "14 9" "15 9"; do
  set -- $spec
  printf '%8s %6s %6s %6s\n' "($1,$2)" "$(nul "$DIR4" prec "$1" "$2")" \
    "$(nul "$NULL" prec "$1" "$2")" "$(nul "$HV" prec "$1" "$2")"
done

echo
echo "### is the UNRESTRICTED HV series algebraic in the same boxes?"
echo "### (separate question, reported for contrast -- not a Phase 2b claim)"
for spec in "4 22" "4 24" "6 22" "2 40" "3 30"; do
  set -- $spec
  printf '  alg (%s,%s)  hv nullity=%s   dir4 nullity=%s\n' "$1" "$2" \
    "$(nul "$HV" alg "$1" "$2")" "$(nul "$DIR4" alg "$1" "$2")"
done

echo "NULLITY GRID DONE"
