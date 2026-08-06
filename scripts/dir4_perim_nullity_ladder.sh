#!/bin/bash
# Phase 2b: the nullity ladder, a consistency test the sweep's high-order
# CANDIDATE boxes have to pass before they mean anything.
#
# A nullvector of the (J,D) ansatz, zero-padded, is a nullvector of (J+1,D)
# (whose row set is a SUBSET of (J,D)'s rows: n = 1..M-J-1 vs 1..M-J) and of
# (J,D+1) (same rows, extra columns). So nullity is mathematically
# NON-DECREASING in J at fixed D, and in D at fixed J -- over Q and mod p
# alike. Any measured drop is a defect in the measurement, not a fact about
# the sequence. A genuine order-J0 degree-D0 relation also has to show a
# nullity that GROWS like (J-J0+1)(D-D0+1) as the box opens up, not one that
# appears in a single box and vanishes on either side of it.
#
#   target: gympie, local, single-threaded
#   cost:   ~3 s total (measured 8 ms - 200 ms per box)
#   usage:  scripts/dir4_perim_nullity_ladder.sh 2>&1 \
#             | tee results/dir4_perim_nullity_ladder.log
set -u
cd "$(dirname "$0")/.."

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
NULL=build/dir4_perim_null199.txt
SRC=results/convex_area_terms_n700_king.txt   # the null control's real source

[ -f "$SRC" ] || { echo "missing $SRC (results/convex-polyplets.md)" >&2; exit 1; }
head -199 "$SRC" > "$NULL"   # re-cut every run; never reuse a stale copy

row() {  # row <file> <mode> <J> <D>
  printf '  J=%-3s D=%-3s ' "$3" "$4"
  "$G" "$2" "$1" "$3" "$4" 2>/dev/null | awk '
    /^mode=/{split($4,b,"="); u=$5; r=$6}
    /^UNDERDETERMINED/{und=1}
    /^full rank/{split($3,x,"="); rk=x[2]}
    /^VERDICT/{v=$2}
    END{if(und) printf "%-14s %s %s\n","UNDERDET",u,r;
        else{split($0,_); printf "%-14s %s %s rank=%s\n", v, u, r, rk}}'
}

for f in "$DIR4" "$NULL"; do
  echo "##### $(basename "$f") #####"
  for D in 2 3 4 9 12; do
    echo "-- prec, degree $D, order ladder"
    case $D in
      2)  Js="40 42 44 46 47 48 49 50" ;;
      3)  Js="34 35 36 37 38 39 40" ;;
      4)  Js="26 27 28 29 30 31 32" ;;
      9)  Js="11 12 13 14 15 16 17 18" ;;
      12) Js="10 11 12 13 14" ;;
    esac
    for J in $Js; do row "$f" prec "$J" "$D"; done
  done
  echo "-- prec, degree ladder at fixed order 13"
  for D in 8 9 10 11 12 13; do row "$f" prec 13 "$D"; done
  echo
done

echo "LADDER DONE"
