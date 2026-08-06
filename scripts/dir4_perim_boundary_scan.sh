#!/bin/bash
# Phase 2b: locate the exact (order, degree) boundary at which the dir4
# semiperimeter series stops being EXCLUDED, and report the built-in holdout
# at every box on that boundary. The holdout is what separates "a relation
# that exists" from "a relation the fit absorbed": prec_guess trains on the
# first C+4 rows and tests the fitted nullspace against every later row, so
# a box with many spare rows and best_consecutive_pass == holdout rows is a
# genuine prediction, not a fit.
#
# Same scan on the null control (199 terms of the by-area series, known
# non-D-finite) at every box, so each line is a matched pair.
#
#   target: gympie, local, single-threaded
#   cost:   ~10 s (measured 8 ms - 200 ms per box)
#   usage:  scripts/dir4_perim_boundary_scan.sh 2>&1 \
#             | tee results/dir4_perim_boundary.log
set -u
cd "$(dirname "$0")/.."

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
HV=results/convex_perim_terms_s200.txt
NULL=build/dir4_perim_null199.txt
SRC=results/convex_area_terms_n700_king.txt   # the null control's real source

[ -f "$SRC" ] || { echo "missing $SRC (results/convex-polyplets.md)" >&2; exit 1; }
head -199 "$SRC" > "$NULL"   # re-cut every run; never reuse a stale copy

# one <file> <mode> <J> <D> -> "VERDICT unknowns rows nullity holdpass/holdrows"
one() {
  "$G" "$2" "$1" "$3" "$4" 2>/dev/null | awk -v J="$3" -v D="$4" '
    /^mode=/{for(i=1;i<=NF;i++){split($i,kv,"="); m[kv[1]]=kv[2]}}
    /^UNDERDETERMINED/{u=1}
    /^holdout rows=/{split($2,a,"="); hr=a[2]; split($3,b,"="); hp=b[2]}
    /^full rank=/{split($0,z," "); split(z[2],y,"="); rk=y[2];
                  n=$NF; sub(/^nullity=/,"",n)}
    /^VERDICT/{v=$2}
    END{ if(u) printf "UNDERDET  unk=%s rows=%s\n", m["unknowns"], m["rows"];
         else printf "%-9s unk=%-4s rows=%-4s nullity=%-4s holdout=%s/%s\n",
                     v, m["unknowns"], m["rows"], n, hp, hr }'
}

echo "### boundary scan: smallest order J with a CANDIDATE at each degree D"
echo "### (dir4 first, then the null control at the SAME box)"
for D in 2 3 4 5 6 7 8 9 10 11 12; do
  echo "-- degree $D"
  for J in $(seq 5 60); do
    unk=$(( (J+1)*(D+1) )); rows=$(( 199 - J ))
    [ "$unk" -ge "$rows" ] && { echo "   D=$D: no decidable box left (J=$J)"; break; }
    out=$(one "$DIR4" prec "$J" "$D")
    case "$out" in
      CANDIDATE*)
        printf '   dir4  J=%-3s %s\n' "$J" "$out"
        printf '   null  J=%-3s %s\n' "$J" "$(one "$NULL" prec "$J" "$D")"
        printf '   hv    J=%-3s %s\n' "$J" "$(one "$HV" prec "$J" "$D")"
        break ;;
    esac
  done
done

echo
echo "### the same, algebraic mode"
for L in 4 6 8 10 12 14 16 20 24; do
  for K in $(seq 1 40); do
    unk=$(( (K+1)*(L+1) ))
    [ "$unk" -ge 200 ] && { echo "   L=$L: no decidable box left (K=$K)"; break; }
    out=$(one "$DIR4" alg "$K" "$L")
    case "$out" in
      CANDIDATE*)
        printf '   dir4  K=%-3s L=%-3s %s\n' "$K" "$L" "$out"
        printf '   null  K=%-3s L=%-3s %s\n' "$K" "$L" "$(one "$NULL" alg "$K" "$L")"
        break ;;
    esac
  done
done

echo "BOUNDARY SCAN DONE"
