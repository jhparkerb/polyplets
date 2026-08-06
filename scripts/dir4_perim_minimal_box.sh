#!/bin/bash
# Phase 2b: pin the minimal boxes, both modes, and re-run the headline ones on
# the second prime.
#
# scripts/dir4_perim_boundary_scan.sh found the (order, degree) frontier from
# the degree side; this completes it (degree 0, 1 and 13+ for prec; minimal
# t-degree per algebraic degree for alg) and repeats every headline box on
# prec_guess's second, unrelated prime -- a rank DEFECT mod one prime can be an
# accident of that prime, which is exactly the branch this verdict sits in
# (cpp/prec_guess.cpp header).
#
#   target: gympie, local, single-threaded
#   cost:   ~30 s (measured)
#   usage:  scripts/dir4_perim_minimal_box.sh 2>&1 \
#             | tee results/dir4_perim_minimal_box.log
set -u
cd "$(dirname "$0")/.."

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
NULL=build/dir4_perim_null199.txt
SRC=results/convex_area_terms_n700_king.txt   # the null control's real source
[ -f "$SRC" ] || { echo "missing $SRC (results/convex-polyplets.md)" >&2; exit 1; }
head -199 "$SRC" > "$NULL"   # re-cut every run; never reuse a stale copy

one() {  # one <file> <mode> <A> <B> [prime_idx]
  "$G" "$2" "$1" "$3" "$4" ${5:-0} 2>/dev/null | awk '
    /^mode=/{for(i=1;i<=NF;i++){split($i,kv,"="); m[kv[1]]=kv[2]}}
    /^UNDERDETERMINED/{u=1}
    /^holdout rows=/{split($2,a,"="); hr=a[2]; split($3,b,"="); hp=b[2]}
    /^full rank=/{n=$NF; sub(/^nullity=/,"",n)}
    /^VERDICT/{v=$2}
    END{ if(u) printf "UNDERDET  unk=%s rows=%s\n", m["unknowns"], m["rows"];
         else printf "%-9s unk=%-4s rows=%-4s nullity=%-4s holdout=%s/%s\n",
                     v, m["unknowns"], m["rows"], n, hp, hr }'
}

echo "### prec: the low-degree and high-degree ends of the frontier"
for D in 0 1 13 14 15; do
  for J in $(seq 5 70); do
    unk=$(( (J+1)*(D+1) )); rows=$(( 199 - J ))
    [ "$unk" -ge "$rows" ] && { echo "  D=$D: no decidable box left (J=$J)"; break; }
    out=$(one "$DIR4" prec "$J" "$D")
    case "$out" in CANDIDATE*)
      printf '  dir4 D=%-3s J=%-3s %s\n' "$D" "$J" "$out"
      printf '  null D=%-3s J=%-3s %s\n' "$D" "$J" "$(one "$NULL" prec "$J" "$D")"
      break ;;
    esac
  done
done

echo
echo "### alg: minimal t-degree L at each algebraic degree K"
for K in 2 3 4 5 6 7 8; do
  for L in $(seq 1 99); do
    unk=$(( (K+1)*(L+1) ))
    [ "$unk" -ge 200 ] && { echo "  K=$K: no decidable box left (L=$L)"; break; }
    out=$(one "$DIR4" alg "$K" "$L")
    case "$out" in CANDIDATE*)
      printf '  dir4 K=%-3s L=%-3s %s\n' "$K" "$L" "$out"
      printf '  null K=%-3s L=%-3s %s\n' "$K" "$L" "$(one "$NULL" alg "$K" "$L")"
      break ;;
    esac
  done
done

echo
echo "### headline boxes on the SECOND prime (1152921504606846883)"
for spec in "prec 27 2" "prec 19 3" "prec 17 4" "prec 15 5" "prec 13 9" "alg 4 24"; do
  set -- $spec
  printf '  p0 %-5s (%s,%s) %s' "$1" "$2" "$3" "$(one "$DIR4" "$1" "$2" "$3" 0)"
  printf '  p1 %-5s (%s,%s) %s' "$1" "$2" "$3" "$(one "$DIR4" "$1" "$2" "$3" 1)"
done

echo
echo "### headline boxes with the first 20 rows dropped (holds EVENTUALLY?)"
for spec in "prec 27 2" "prec 19 3" "prec 13 9"; do
  set -- $spec
  printf '  skip20 %-5s (%s,%s) ' "$1" "$2" "$3"
  "$G" "$1" "$DIR4" "$2" "$3" 0 4 20 2>/dev/null | awk '
    /^holdout rows=/{split($2,a,"="); hr=a[2]; split($3,b,"="); hp=b[2]}
    /^full rank=/{n=$NF; sub(/^nullity=/,"",n)}
    /^VERDICT/{v=$2}
    END{printf "%-9s nullity=%-4s holdout=%s/%s\n", v, n, hp, hr}'
done

echo "MINIMAL BOX DONE"
