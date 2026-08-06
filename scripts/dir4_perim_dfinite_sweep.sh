#!/bin/bash
# Phase 2b of docs/middle-kingdom-followups-plan.md: is the "area wild,
# perimeter tame" D-finiteness lever robust to the dir4 restriction?
#
# Runs build/prec_guess over the (dir4, HV-convex)-by-semiperimeter series
# (results/mk_dir4_perim_terms_s200.txt, 199 terms, Phase 2a) in every
# maximal box 199 terms can decide, in both `prec` (P-recurrence) and `alg`
# (algebraic) mode, alongside the four control arms of
# tests/gate_convex_dfinite.py plus a same-box, same-length power arm.
#
# Boxes are chosen on the decidability frontier: a box is decided only when
# rows > unknowns, i.e. (J+1)(D+1) < 199-J for prec and < 200 for alg.
# Boxes NEST (cpp/prec_guess.cpp header), so each maximal box excludes every
# box inside it; the frontier is swept because these maximal boxes do NOT
# contain one another (high order / low degree vs low order / high degree).
#
#   target: gympie, local, single-threaded
#   cost:   measured 8 ms per box at (5,2); the largest boxes here are
#           ~190 unknowns x ~195 rows, O(R C^2) ~ 7e6 field ops -- under a
#           second each, whole sweep well under a minute. Nothing to resume.
#   usage:  scripts/dir4_perim_dfinite_sweep.sh 2>&1 | tee results/dir4_perim_dfinite.log
set -u
cd "$(dirname "$0")/.."

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
HV=results/convex_perim_terms_s200.txt
A005436=results/a005436_perim_s100.txt

run() {  # run <label> <mode> <file> <A> <B> [prime_idx] [train_extra] [skip]
  local label=$1; shift
  echo "=== $label :: $G $*"
  "$G" "$@" 2>/dev/null
  echo "rc=$?"
  echo
}

echo "##### CONTROL ARMS (tests/gate_convex_dfinite.py discipline) #####"
echo
run "prec +  HV-convex by semiperimeter, banked (5,2) recurrence: must be CANDIDATE" \
    prec "$HV" 5 2
run "prec -  same series, (2,1) too small: must be EXCLUDED" \
    prec "$HV" 2 1
run "alg +   A005436 algebraic (Delest-Viennot) at (2,8): must be CANDIDATE" \
    alg "$A005436" 2 8
run "alg -   A005436 at (2,4) too small: must be EXCLUDED" \
    alg "$A005436" 2 4

echo "##### POWER ARM: same series length, same maximal boxes as the dir4 sweep #####"
echo "# If the guesser still finds the known HV recurrence inside the very boxes"
echo "# that exclude dir4, an unpowered guesser is not the explanation."
echo
for box in "12 12" "13 12" "9 17" "17 9" "6 26" "4 37" "2 62" "38 3"; do
  run "power prec HV-convex (known D-finite) box ($box)" prec "$HV" $box
done
run "power alg  HV-convex at (12,14)" alg "$HV" 12 14

echo "##### THE QUESTION: dir4 x HV-convex by semiperimeter #####"
echo
for box in "5 2" "12 12" "13 12" "11 14" "9 17" "17 9" "14 11" "6 26" "4 37" "3 46" "2 62" "1 97" "30 4" "38 3" "48 2"; do
  run "dir4 prec box ($box)" prec "$DIR4" $box
done
for box in "12 14" "13 13" "14 12" "9 18" "18 9" "6 27" "3 48" "2 65" "1 98" "30 5" "45 3"; do
  run "dir4 alg box ($box)" alg "$DIR4" $box
done

echo "##### ROBUSTNESS ON THE HEADLINE BOX #####"
echo
run "dir4 prec (12,12), second prime" prec "$DIR4" 12 12 1
run "dir4 prec (12,12), skip 20 leading rows" prec "$DIR4" 12 12 0 4 20
run "dir4 alg  (12,14), second prime" alg "$DIR4" 12 14 1
run "dir4 prec (5,2), second prime" prec "$DIR4" 5 2 1
run "dir4 prec (5,2), skip 20 leading rows" prec "$DIR4" 5 2 0 4 20

echo "SWEEP DONE"
