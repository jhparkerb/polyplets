#!/usr/bin/env bash
# ns_steal_ab.sh — A/B measurement of map work-stealing (DESIGN 08, T2.3).
#
# Runs the SAME a(n) twice with identical config except --steal-grain: once OFF
# (the pull-queue baseline) and once ON, both --compare (must byte-match the
# known a(n)) and both with POLY_UNIT_LOG so per-unit costs and steal events land
# in the logs. Then job_stats.py rolls each up to per-column map-wall/util, and
# we print the headline: total map-wall OFF vs ON and the recovered fraction.
#
# Forced spill (--ram small) reproduces the spill-driven straggler tail design 08
# measured (a(18): ~18% of map-wall wasted, makespan 1.215x ideal). The design
# predicts steal closes ~86-97% of that gap. This is the at-scale confirmation
# of that prediction before the engine is trusted for the a(22) ladder run.
#
# Usage: ns_steal_ab.sh [N] [CORES] [MULT] [RAM_MB] [GRAIN]
#   defaults: N=18 CORES=8 MULT=4 RAM_MB=128 GRAIN=0.05  (design 08's a(18) point)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="${1:-18}"; CORES="${2:-8}"; MULT="${3:-4}"; RAM_MB="${4:-128}"; GRAIN="${5:-0.05}"
RAM=$(( RAM_MB * 1024 * 1024 ))
REV="$(git -C "$REPO" rev-parse --short HEAD)"
ROOT="$REPO/runs/ns_steal_ab"; mkdir -p "$ROOT"
RESULTS="$REPO/results/steal_ab"; mkdir -p "$RESULTS"

run_one() {  # $1=label  $2=grain
  local label="$1" grain="$2" rd="$ROOT/$1"
  rm -rf "$rd"; mkdir -p "$rd/spill"
  echo "steal_ab $label rev=$REV host=$(hostname -s) n=$N cores=$CORES mult=$MULT ram_mb=$RAM_MB grain=$grain start=$(date -Is)" | tee "$ROOT/$label.log"
  POLY_UNIT_LOG=1 "$REPO/build/ns/orchestrate" --maxn "$N" --cores "$CORES" \
    --unit-mult "$MULT" --steal-grain "$grain" --ram "$RAM" \
    --run-dir "$rd" --spill-dir "$rd/spill" \
    --checkpoint "$rd/POLYCKPT" --checkpoint-every 0 --compare 2>&1 | tee -a "$ROOT/$label.log"
  echo "steal_ab $label done=$(date -Is)" | tee -a "$ROOT/$label.log"
}

run_one off 0
run_one on "$GRAIN"

echo "================ per-column rollup ================"
python3 "$REPO/scripts/job_stats.py" "$ROOT/off.log" --cores "$CORES" --label "steal-OFF" --tsv "$RESULTS/off.tsv"
python3 "$REPO/scripts/job_stats.py" "$ROOT/on.log"  --cores "$CORES" --label "steal-ON"  --tsv "$RESULTS/on.tsv"

echo "================ headline ================"
OFF_MAP=$(awk -F'map_wall_s=' '/event=column/{split($2,a," "); s+=a[1]} END{printf "%.1f", s}' "$ROOT/off.log")
ON_MAP=$( awk -F'map_wall_s=' '/event=column/{split($2,a," "); s+=a[1]} END{printf "%.1f", s}' "$ROOT/on.log")
STEALS=$(grep -c 'event=steal' "$ROOT/on.log" || true)
echo "total map-wall  OFF=${OFF_MAP}s  ON=${ON_MAP}s  steals=${STEALS}"
awk -v o="$OFF_MAP" -v n="$ON_MAP" 'BEGIN{ if(o>0) printf "map-wall ON/OFF = %.3f  (%.1f%% reduction)\n", n/o, 100*(o-n)/o }'
