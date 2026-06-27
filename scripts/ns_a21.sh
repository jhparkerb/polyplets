#!/usr/bin/env bash
# ns_a21.sh — launch the new-engine a(21) on this host (dalby).
#
# Gated on the probe passing. Predicts the a(21) cost profile from the a(20)
# probe run (drives the live ETA), runs the full sweep with per-height output
# (for the old-engine cross-check vs salvaged h1..h16.out) and 15-min
# checkpoints, then combines the per-height rows into a(21) + the full triangle.
#
# No --compare on the sweep: a(21) is not in fixtures, so a compare would report
# the n=21 row as FAIL. Correctness is established instead by (a) the growth-ratio
# gate (a21/a20 ~ 6.78), (b) combine --require-cover, and (c) cell-by-cell
# comparison of h1..h16.out against the old engine's salvaged rows.
#
# Target: dalby 80c / 125 GB idle. Predicted cost: from the probe (printed by the
# predict step below before the sweep starts). Resume: orchestrate --resume on the
# run-dir. Kill: kill the orchestrate pid (writes a checkpoint first).
#
# Usage: ns_a21.sh MULT A20_PROFILE [CORES] [RAM_PER_WORKER_GB] [APRIORI_R]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MULT="${1:?usage: ns_a21.sh MULT A20_PROFILE [CORES] [RAM_GB] [R]}"
A20_PROFILE="${2:?path to the a(20) cost profile from the probe}"
CORES="${3:-80}"
RAMW_GB="${4:-1}"
R="${5:-6.76}"
RAM=$(( RAMW_GB * 1024 * 1024 * 1024 ))

ROOT="$REPO/runs/ns_a21"
RUNDIR="$ROOT/run"; SPILL="$RUNDIR/spill"; PERH="$ROOT/perheight"
mkdir -p "$SPILL" "$PERH"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
echo "ns_a21 rev=$REV host=$(hostname -s) mult=$MULT cores=$CORES ram_gb=$RAMW_GB start=$(date -Is)" | tee "$ROOT/a21.log"

# 1) Predict the a(21) reference profile from a(20) (a-priori wall + live ETA basis).
"$REPO/build/ns/predict" --profile "$A20_PROFILE" --to 21 --ratio "$R" --out "$ROOT/a21ref.tsv" | tee -a "$ROOT/a21.log"

# 2) Full a(21) sweep, per-height output + checkpointing + live ETA.
"$REPO/build/ns/orchestrate" --maxn 21 --cores "$CORES" --unit-mult "$MULT" \
  --ram "$RAM" --run-dir "$RUNDIR" --spill-dir "$SPILL" \
  --per-height-out "$PERH" --cost-profile-ref "$ROOT/a21ref.tsv" \
  --cost-profile-out "$ROOT/profile.tsv" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 900 2>&1 | tee -a "$ROOT/a21.log"

# 3) Combine per-height rows -> a(21) + full triangle.
"$REPO/build/ns/combine" --in "$PERH" --maxn 21 --require-cover --out "$ROOT/triangle.txt" 2>&1 | tee -a "$ROOT/a21.log"
echo "ns_a21 done=$(date -Is)" | tee -a "$ROOT/a21.log"
