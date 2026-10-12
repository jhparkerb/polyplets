#!/bin/bash
# lean-decide-trials.sh: for each remaining native_decide fact in the Report
# cone, try kernel `decide` on the same statement under scripts/lean-guard.sh
# (4 GB RSS, 240 s). One trial file per fact under polyplets/build/nd/, run
# serially; the verdict table goes to polyplets/build/nd/results.txt.
cd "$(dirname "$0")/.." || exit 1
PAT="$1"  # optional glob over trial names; the generation loops below reuse $1
D=polyplets/build/nd; mkdir -p $D; [ -n "$PAT" ] || : > $D/results.txt
trial() {  # name module statement
  cat > $D/$1.lean <<EOF
import Polyplets.$2
open Polyplets
set_option maxRecDepth 100000 in
example : $3 := by $4
EOF
}
trial T_2_1 Compute 'T 2 1 = 1' 'rw [← Tc_eq_T]; decide +kernel'
trial T_2_2 Compute 'T 2 2 = 3' 'rw [← Tc_eq_T]; decide +kernel'
trial T_3_1 Compute 'T 3 1 = 1' 'rw [← Tc_eq_T]; decide +kernel'
trial T_3_3 Compute 'T 3 3 = 9' 'rw [← Tc_eq_T]; decide +kernel'
trial T_5_4 Compute 'T 5 4 = 240' 'rw [← Tc_eq_T]; decide +kernel'
trial a_1 Sequence 'a 1 = 1' 'rw [← ac_eq_a 1]; decide +kernel'
trial a_2 Sequence 'a 2 = 4' 'rw [← ac_eq_a 2]; decide +kernel'
trial a_3 Sequence 'a 3 = 20' 'rw [← ac_eq_a 3]; decide +kernel'
trial a_4 Sequence 'a 4 = 110' 'rw [← ac_eq_a 4]; decide +kernel'
for w in 'V_1_2 V 1 2 = 49' 'Vt_1_2 Vt 1 2 = 7' 'V_2_2 V 2 2 = 339' 'Vt_2_2 Vt 2 2 = 66' \
         'd_0_2 d 0 2 = 3' 'd_0_3 d 0 3 = 9' 'd_0_4 d 0 4 = 27' 'd_1_2 d 1 2 = 5' \
         'd_1_3 d 1 3 = 40' 'd_2_3 d 2 3 = 136' 'd_2_4 d 2 4 = 1019'; do
  set -- $w; n=$1; shift; trial $n Weights "$*" 'decide +kernel'
done
for w in 'V_1_3 V 1 3 = 81' 'Vt_1_3 Vt 1 3 = 9' 'Vt_2_3 Vt 2 3 = 307' 'V_2_3 V 2 3 = 1860'; do
  set -- $w; n=$1; shift; trial $n Weights "$*" 'decide +kernel'
done
for n in 1 2 3 4; do
  for g in 'R90 r1' 'R180 r2' 'Hm h' 'Dm d'; do
    set -- $g; f=$1; e=$2
    v=$(awk -v f=$f -v n=$n '$0 ~ "^theorem "f"_"n" " {match($0, /= [0-9]+ :=/); print substr($0, RSTART+2, RLENGTH-5)}' polyplets/Polyplets/Symmetry.lean)
    trial ${f}_$n Symmetry "$f $n = $v" "change fixCount $n D4.$e = $v; rw [← fixCountC_eq]; decide +kernel"
  done
done
cd polyplets
for f in build/nd/${PAT:-*}.lean; do
  n=$(basename $f .lean)
  echo "=== $n $(date +%T)"
  out=$(LEAN_NUM_THREADS=1 nice -n 10 ../scripts/lean-guard.sh ${CAP:-4} ${TMO:-240} ~/.elan/bin/lake env lean $f 2>&1)
  echo "$out" | tail -3
  if echo "$out" | grep -q 'GUARD: exit=0'; then v=PASS; else v=FAIL; fi
  echo "$n $v $(echo "$out" | grep -o 'peak_rss=[0-9]*MB wall=[0-9]*s')" | tee -a build/nd/results.txt
done
echo DONE
