#!/bin/bash
# even_keel_d6_ab.sh H MAXN -- Even Keel D6 confound-controlled A/B:
# fused-stage worker (current even-keel HEAD) vs the pre-D6 even-keel
# map+merge baseline (934f8c0a). Mirrors scripts/even_keel_ab.sh's D1/D2
# tightener script exactly, one binary generation later: OLD there
# (aa4bbd29, SampleKeysMulti) is retired; the baseline here is what THAT
# script called NEW (BalancedCutsMulti, map+merge) -- D6's whole point is
# the round-trip elimination on top of that, so it's the only fair
# baseline. Each orchestrate uses its OWN worktree's workers
# (--workers-dir); NEW additionally passes --require-fusion so a missing/
# stale fused_stage build fails loud instead of silently degrading to the
# map+merge path and reporting a false confirmation.
set -u
H=${1:-16}; MAXN=${2:-34}
BASE=$HOME/src/polyominoes
PREV6_WT=$HOME/src/poly-pre-d6

run() {
  local label=$1 wt=$2 dir=$3 extra=$4
  rm -rf "$dir"; mkdir -p "$dir/spill" "$dir/ph"
  export GOGC=1000
  local T0 T1 RC
  T0=$(date +%s)
  ( cd "$wt" && ./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 \
    --cores 80 --ram 1073741824 --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
    --overlap-heights 1 --persistent-workers --heights "$H" \
    --workers-dir "$wt/build/ns" $extra \
    --run-dir "$dir" --spill-dir "$dir/spill" \
    --checkpoint "$dir/CK" --checkpoint-every 3000 \
    --per-height-out "$dir/ph" --cost-profile-out "$dir/cp.tsv" ) > "$dir/log" 2>&1
  RC=$?; T1=$(date +%s)
  echo "$label rc=$RC wall=$((T1-T0))s $(grep -o 'rev=[^ ]*' "$dir/log" | head -1)"
}

echo "=== Even Keel D6 A/B  H=$H maxn=$MAXN  $(date -Iseconds) ==="
run PRED6 "$PREV6_WT" "$BASE/runs/ek_d6_pre" ""
run FUSED "$BASE"     "$BASE/runs/ek_d6_fused" "--require-fusion"

echo "=== per-column effective cores (cpu_s/wall_s), H=$H ==="
printf "%-3s %10s | %7s %8s %6s (PRE-D6) | %7s %8s %6s (FUSED)\n" col front wall cpu eff wall cpu eff
paste \
  <(awk -v H=$H 'NR>2&&$1==H{print $2,$3,$5,$6}' "$BASE/runs/ek_d6_pre/cp.tsv") \
  <(awk -v H=$H 'NR>2&&$1==H{print $5,$6}' "$BASE/runs/ek_d6_fused/cp.tsv") \
| awk '{printf "%-3d %10d | %7.1f %8.1f %6.2f | %7.1f %8.1f %6.2f\n",$1,$2,$3,$4,$4/$3,$5,$6,$6/$5}'

echo "=== whole-height totals ==="
for d in ek_d6_pre ek_d6_fused; do awk -v D=$d 'NR>2&&$1=='"$H"'{w+=$5;c+=$6} END{printf "%-9s wall=%.1fs cpu=%.1fs eff=%.2f\n",D,w,c,c/w}' "$BASE/runs/$d/cp.tsv"; done

echo "=== correctness: FUSED vs PRE-D6 per-height T(n,$H) ==="
( cd "$BASE" && ./build/ns/combine --in runs/ek_d6_fused/ph --diff-b runs/ek_d6_pre/ph --maxn "$MAXN" 2>&1 | tail -4 )
echo "=== EK_D6_AB_DONE ==="
