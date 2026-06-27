#!/usr/bin/env bash
# ns_probe.sh — unit-mult utilization + scaling probe on an idle big box.
#
# Runs a(N) (a known term) at each unit-mult in MULTS, measuring total wall and
# (via the per-column event=column lines: cores ~ cpu_s/wall_s) how well finer
# slicing fills the cores on the heavy columns. Finds the best mult and a per-
# term wall to extrapolate a(21). --compare checks correctness at n=N.
#
# No a(N+1) step and no inlined predict: the sweep is just a loop, so any single
# mult run is independently killable and there's no 7h tail to chase.
#
# Target: idle big box (dalby 80c/125GB). a(18) at 80 cores is ~tens of minutes
# per mult. Resume: orchestrate --resume on a run-dir. Kill: kill the orchestrate
# pid (it checkpoints) or this script's pid between runs.
#
# Usage: ns_probe.sh N "MULTS" [ROOT] [CORES] [RAM_PER_WORKER_GB]
#   e.g. ns_probe.sh 18 "4 2 1"
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="${1:?usage: ns_probe.sh N \"MULTS\" [ROOT] [CORES] [RAM_GB]}"
MULTS="${2:?mult list, e.g. \"4 2 1\"}"
ROOT="${3:-$REPO/runs/ns_probe}"
CORES="${4:-80}"
RAMW_GB="${5:-1}"
RAM=$(( RAMW_GB * 1024 * 1024 * 1024 ))

mkdir -p "$ROOT"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
LOG="$ROOT/probe.log"
echo "ns_probe rev=$REV host=$(hostname -s) N=$N cores=$CORES ram_per_worker_gb=$RAMW_GB mults='$MULTS' start=$(date -Is)" | tee "$LOG"

run() { # mult
  local m="$1"
  local d="$ROOT/n${N}_m${m}"; rm -rf "$d"; mkdir -p "$d/spill"
  echo "=== run a($N) mult=$m start=$(date -Is) ===" | tee -a "$LOG"
  "$REPO/build/ns/orchestrate" --maxn "$N" --cores "$CORES" --unit-mult "$m" \
    --ram "$RAM" --run-dir "$d" --spill-dir "$d/spill" \
    --checkpoint "$d/POLYCKPT" --checkpoint-every 300 \
    --cost-profile-out "$d/profile.tsv" --compare 2>&1 | tee "$d/run.log"
  grep -E "wall=|gate_parallel" "$d/run.log" | tee -a "$LOG"
}

for m in $MULTS; do run "$m"; done

echo "=== summary (wall per mult) ===" | tee -a "$LOG"
for m in $MULTS; do
  w=$(grep -oE "wall=[0-9.]+s" "$ROOT/n${N}_m${m}/run.log" 2>/dev/null | head -1)
  echo "a($N) mult=$m ${w:-<incomplete>}" | tee -a "$LOG"
done
echo "ns_probe done=$(date -Is)" | tee -a "$LOG"
