#!/bin/bash
# lean-decide-trials-universal.sh: kernel-decide trials for the native_decide
# sites of the restored L-paper modules (Universal/{King,Hex,Square}, Upper/
# BuiData3), under scripts/lean-guard.sh (CAP GB, default 4; 240 s each).
# Trial files under polyplets/build/ndu/, verdicts in polyplets/build/ndu/results.txt.
cd "$(dirname "$0")/.." || exit 1
PAT="$1"
D=polyplets/build/ndu; mkdir -p $D; [ -n "$PAT" ] || : > $D/results.txt
trial() {  # name module statement tactic
  case $2 in Universal.*) OPENS="Polyplets Polyplets.Universal";; *) OPENS="Polyplets";; esac
  cat > $D/$1.lean <<EOF
import Polyplets.$2
open $OPENS
set_option maxRecDepth 100000 in
example : $3 := by $4
EOF
}
for L in king hex square; do
  case $L in
    king)   M=King;   LAT=kingLattice;   MLE=M_king_le;   A="3 2 = 10"; B="4 3 = 55"; C="5 4 = 240"; R3=20; R4=110; R5=638;;
    hex)    M=Universal.Hex;    LAT=hexLattice;    MLE=M_hex_le;    A="3 2 = 6";  B="4 3 = 21"; C="5 4 = 60";  R3=11; R4=44;  R5=186;;
    square) M=Universal.Square; LAT=squareLattice; MLE=M_square_le; A="3 2 = $(grep -o 'T squareLattice 3 2 = [0-9]*' polyplets/Polyplets/Universal/Square.lean | head -1 | awk '{print $NF}')"; B="4 3 = $(grep -o 'T squareLattice 4 3 = [0-9]*' polyplets/Polyplets/Universal/Square.lean | head -1 | awk '{print $NF}')"; C="5 4 = $(grep -o 'T squareLattice 5 4 = [0-9]*' polyplets/Polyplets/Universal/Square.lean | head -1 | awk '{print $NF}')"; R3=6; R4=19; R5=63;;
  esac
  trial T_${L}_3_2 $M "T $LAT $A" "rw [← Tc_eq_T_of_M_le_one $MLE]; decide +kernel"
  trial T_${L}_4_3 $M "T $LAT $B" "rw [← Tc_eq_T_of_M_le_one $MLE]; decide +kernel"
  trial T_${L}_5_4 $M "T $LAT $C" "rw [← Tc_eq_T_of_M_le_one $MLE]; decide +kernel"
  trial rowSum_${L}_3 $M "rowSum $LAT 3 3 = $R3" "decide +kernel"
  trial rowSum_${L}_4 $M "rowSum $LAT 4 4 = $R4" "decide +kernel"
  trial rowSum_${L}_5 $M "rowSum $LAT 5 5 = $R5" "decide +kernel"
done
trial buiRD3_valid Upper.BuiData3 "buiRD3.valid = true" "decide +kernel"
trial buiRD2_valid Upper.BuiData2 "buiRD2.valid = true" "decide +kernel"
cd polyplets
for f in build/ndu/${PAT:-*}.lean; do
  n=$(basename $f .lean)
  echo "=== $n $(date +%T)"
  out=$(LEAN_NUM_THREADS=1 nice -n 10 ../scripts/lean-guard.sh ${CAP:-4} ${TMO:-240} ~/.elan/bin/lake env lean $f 2>&1)
  echo "$out" | tail -3
  if echo "$out" | grep -q 'GUARD: exit=0'; then v=PASS; else v=FAIL; fi
  echo "$n $v $(echo "$out" | grep -o 'peak_rss=[0-9]*MB wall=[0-9]*s')" | tee -a build/ndu/results.txt
done
echo DONE
