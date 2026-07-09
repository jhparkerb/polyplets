#!/bin/bash
# even_keel_unitmult.sh -- D6 diagnosis: with BALANCED cuts, does lowering
# --unit-mult (fewer, larger map units => smaller merge fan-in) lift
# merge_eff_cores without hurting map_eff_cores? NEW (even-keel) binary only.
# H16 maxn34, overlap-off. Reports whole-height eff + a fat column's
# map_eff/merge_eff for each unit-mult.
set -u
BASE=$HOME/src/polyominoes
H=16; MAXN=34
export GOGC=1000
echo "=== D6 unit-mult sweep (NEW/balanced) H=$H maxn=$MAXN $(date -Iseconds) ==="
for UM in 1 2 4 8; do
  dir="$BASE/runs/d6_um${UM}"
  rm -rf "$dir"; mkdir -p "$dir/spill" "$dir/ph"
  T0=$(date +%s)
  ( cd "$BASE" && ./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 \
    --cores 80 --ram 1073741824 --unit-mult "$UM" --merge-mult 1 --steal-grain 0.05 \
    --overlap-heights 1 --persistent-workers --heights "$H" \
    --run-dir "$dir" --spill-dir "$dir/spill" \
    --checkpoint "$dir/CK" --checkpoint-every 3000 \
    --per-height-out "$dir/ph" --cost-profile-out "$dir/cp.tsv" ) > "$dir/log" 2>&1
  RC=$?; T1=$(date +%s)
  # whole-height eff + fat col=5 map/merge eff (median over its rounds)
  whole=$(awk -v H=$H 'NR>2&&$1==H{w+=$5;c+=$6} END{printf "wall=%.1f eff=%.2f",w,c/w}' "$dir/cp.tsv")
  meff=$(grep "kink_round" "$dir/log" | grep " col=5 " | grep -oE "map_eff_cores=[0-9.]+" | cut -d= -f2 | sort -n | awk '{a[NR]=$1} END{print a[int(NR/2)]}')
  geff=$(grep "kink_round" "$dir/log" | grep " col=5 " | grep -oE "merge_eff_cores=[0-9.]+" | cut -d= -f2 | sort -n | awk '{a[NR]=$1} END{print a[int(NR/2)]}')
  echo "unit-mult=$UM rc=$RC $whole | col5 map_eff~$meff merge_eff~$geff"
done
echo "=== D6_UM_DONE ==="
