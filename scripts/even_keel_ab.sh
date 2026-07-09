#!/bin/bash
# even_keel_ab.sh H MAXN -- confound-controlled A/B of the OLD (SampleKeysMulti)
# vs NEW (BalancedCutsMulti) partition sampler on ONE real-swept height.
# OLD binary = /tmp/poly-old (rev aa4bbd29), NEW = ~/src/polyominoes (even-keel).
# Each orchestrate uses ITS OWN worktree's workers (--workers-dir). Identical
# production flags, --overlap-heights 1 --heights H (single height, sequential,
# clean per-column cpu/wall). Verifies the rev banner of each run so we can
# never silently benchmark one binary against itself (the landmine from D5).
set -u
H=${1:-16}; MAXN=${2:-34}
BASE=$HOME/src/polyominoes
OLD_WT=/tmp/poly-old

run() {
  local label=$1 wt=$2 dir=$3
  rm -rf "$dir"; mkdir -p "$dir/spill" "$dir/ph"
  export GOGC=1000
  local T0 T1 RC
  T0=$(date +%s)
  ( cd "$wt" && ./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 \
    --cores 80 --ram 1073741824 --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
    --overlap-heights 1 --persistent-workers --heights "$H" \
    --workers-dir "$wt/build/ns" \
    --run-dir "$dir" --spill-dir "$dir/spill" \
    --checkpoint "$dir/CK" --checkpoint-every 3000 \
    --per-height-out "$dir/ph" --cost-profile-out "$dir/cp.tsv" ) > "$dir/log" 2>&1
  RC=$?; T1=$(date +%s)
  echo "$label rc=$RC wall=$((T1-T0))s $(grep -o 'rev=[^ ]*' "$dir/log" | head -1) (expect $([ "$label" = OLD ] && echo aa4bbd29 || echo 934f8c0a))"
}

echo "=== Even Keel A/B  H=$H maxn=$MAXN  $(date -Iseconds) ==="
run OLD "$OLD_WT" "$BASE/runs/ek_old"
run NEW "$BASE"   "$BASE/runs/ek_new"

echo "=== per-column effective cores (cpu_s/wall_s), H=$H ==="
printf "%-3s %10s | %7s %8s %6s (OLD) | %7s %8s %6s (NEW)\n" col front wall cpu eff wall cpu eff
paste \
  <(awk -v H=$H 'NR>2&&$1==H{print $2,$3,$5,$6}' "$BASE/runs/ek_old/cp.tsv") \
  <(awk -v H=$H 'NR>2&&$1==H{print $5,$6}' "$BASE/runs/ek_new/cp.tsv") \
| awk '{printf "%-3d %10d | %7.1f %8.1f %6.2f | %7.1f %8.1f %6.2f\n",$1,$2,$3,$4,$4/$3,$5,$6,$6/$5}'

echo "=== whole-height totals ==="
for d in ek_old ek_new; do awk -v D=$d 'NR>2&&$1=='"$H"'{w+=$5;c+=$6} END{printf "%-7s wall=%.1fs cpu=%.1fs eff=%.2f\n",D,w,c,c/w}' "$BASE/runs/$d/cp.tsv"; done

echo "=== correctness: NEW vs OLD per-height T(n,$H) ==="
( cd "$BASE" && ./build/ns/combine --in runs/ek_new/ph --diff-b runs/ek_old/ph --maxn "$MAXN" 2>&1 | tail -4 )
echo "=== EK_AB_DONE ==="
