#!/usr/bin/env bash
# ns_probe.sh — calibration probe for the new engine on an idle big box.
#
# Purpose: measure real core utilization + per-term scaling, validate the
# a-priori predictor, and decide unit-mult / work-stealing BEFORE committing to
# a(21). Runs a(19) at several unit-mult values, picks the fastest, then runs
# a(20) at that mult with a predicted reference profile loaded (so we can compare
# predicted vs actual wall). Both a(19) and a(20) are known → --compare checks
# correctness too.
#
# Target: dalby (80c / 125 GB), idle. Predicted cost: a(19) a few minutes x3
# mults; a(20) ~tens of minutes. Peak RAM ~= cores * per-worker budget (~80 GB
# at 1 GB/worker), independent of unit-mult (concurrency stays = cores).
# Resume: each run checkpoints (--checkpoint-every 300); re-run orchestrate with
# --resume on its run-dir. Kill: kill the orchestrate pid (writes a checkpoint).
#
# Usage: scripts/ns_probe.sh [ROOT] [CORES] [RAM_PER_WORKER_GB] [MULTS] [APRIORI_R]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${1:-$REPO/runs/ns_probe}"
CORES="${2:-80}"
RAMW_GB="${3:-1}"
MULTS="${4:-1 4 8}"
APRIORI_R="${5:-6.76}"   # a-priori per-term work ratio (a20/a19 count ratio)
RAM=$(( RAMW_GB * 1024 * 1024 * 1024 ))

mkdir -p "$ROOT"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
LOG="$ROOT/probe.log"
echo "ns_probe rev=$REV host=$(hostname -s) cores=$CORES ram_per_worker_gb=$RAMW_GB mults='$MULTS' start=$(date -Is)" | tee "$LOG"

run() { # maxn mult extra-args...
  local maxn="$1" mult="$2"; shift 2
  local d="$ROOT/n${maxn}_m${mult}"; rm -rf "$d"; mkdir -p "$d/spill"
  echo "=== run maxn=$maxn mult=$mult $* ===" | tee -a "$LOG"
  "$REPO/build/ns/orchestrate" --maxn "$maxn" --cores "$CORES" --unit-mult "$mult" \
    --ram "$RAM" --run-dir "$d" --spill-dir "$d/spill" \
    --checkpoint "$d/POLYCKPT" --checkpoint-every 300 \
    --cost-profile-out "$d/profile.tsv" --compare "$@" 2>&1 | tee "$d/run.log"
  grep -E "wall=|gate_parallel" "$d/run.log" | tee -a "$LOG"
}

wall_of() { grep -oE "wall=[0-9.]+s" "$1/run.log" | head -1 | tr -dc '0-9.'; }

# 1) a(19) unit-mult sweep — find the fastest mult (the merge-fan-in knee).
best_mult=""; best_wall=""
for m in $MULTS; do
  run 19 "$m"
  w="$(wall_of "$ROOT/n19_m${m}")"
  echo "a19 mult=$m wall=${w}s" | tee -a "$LOG"
  if [ -n "$w" ] && { [ -z "$best_wall" ] || awk "BEGIN{exit !($w < $best_wall)}"; }; then
    best_wall="$w"; best_mult="$m"
  fi
done
echo "BEST a19 mult=$best_mult wall=${best_wall}s" | tee -a "$LOG"

# 2) Predict a(20) wall from the best a(19) profile (a-priori R).
"$REPO/build/ns/predict" --profile "$ROOT/n19_m${best_mult}/profile.tsv" --to 20 \
  --ratio "$APRIORI_R" --out "$ROOT/p20ref.tsv" | tee -a "$LOG"

# 3) a(20) at best mult with the predicted reference loaded — validates both the
#    predictor (predicted vs actual wall) and correctness at n=20.
run 20 "$best_mult" --cost-profile-ref "$ROOT/p20ref.tsv"
a20w="$(wall_of "$ROOT/n20_m${best_mult}")"
echo "a20 actual wall=${a20w}s (best mult=$best_mult)" | tee -a "$LOG"
echo "measured a19->a20 wall ratio R = $(awk "BEGIN{printf \"%.3f\", $a20w/$best_wall}")" | tee -a "$LOG"
echo "ns_probe done=$(date -Is)" | tee -a "$LOG"
