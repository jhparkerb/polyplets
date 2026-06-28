#!/usr/bin/env bash
# ns_a20_ayr.sh — at-scale validation of the seek-index merge fix on ayr (x86).
#
# Purpose: prove the seek-index (commit de4e183) is correct at a(20) scale —
# multi-GB run files, >2GB fseek offsets, the large sparse index — BEFORE it is
# trusted to (re)produce the a(21) record. The gates only cover a14..a17 (small
# files); this is the missing at-scale, byte-exact check. Bonus: cross-ISA
# validation (x86 here vs dalby arm) + an x86 re-benchmark of the new engine.
#
# Validation = --compare: the computed a(1..20) totals must byte-match
# fixtures/b006770.txt, including a(20) = 1,025,573,519,362,016. Any corruption
# from the seek path makes a(20) mismatch -> FAIL. --per-height-out also lets us
# cross-check h1..h17 against the old engine's salvaged rows.
#
# Target: ayr 32c / 78 GB (sole compute job after old-engine H18 was killed).
# Predicted: ~15-20 h wall, ~12 GB peak RAM, a few GB disk (a(21)/~6.7, plus the
# ~3x seek-index speedup, on 30 of 32 cores). Resume: re-run this script (it
# resumes from runs/ns_a20/run/POLYCKPT). Kill: kill the orchestrate pid (it
# checkpoints first).
#
# Usage: ns_a20_ayr.sh [CORES] [MULT] [RAM_PER_WORKER_GB]
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORES="${1:-30}"; MULT="${2:-4}"; RAMW_GB="${3:-1}"
RAM=$(( RAMW_GB * 1024 * 1024 * 1024 ))

ROOT="$REPO/runs/ns_a20"; RUNDIR="$ROOT/run"; SPILL="$RUNDIR/spill"; PERH="$ROOT/perheight"
mkdir -p "$SPILL" "$PERH"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
RESUME=""; [ -f "$RUNDIR/POLYCKPT" ] && RESUME="--resume"
echo "ns_a20_ayr rev=$REV host=$(hostname -s) cores=$CORES mult=$MULT ram_gb=$RAMW_GB resume='${RESUME}' start=$(date -Is)" | tee "$ROOT/a20.log"

"$REPO/build/ns/orchestrate" --maxn 20 --cores "$CORES" --unit-mult "$MULT" \
  --ram "$RAM" --run-dir "$RUNDIR" --spill-dir "$SPILL" \
  --per-height-out "$PERH" --compare \
  --cost-profile-out "$ROOT/profile.tsv" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 900 $RESUME 2>&1 | tee -a "$ROOT/a20.log"

echo "ns_a20_ayr done=$(date -Is)" | tee -a "$ROOT/a20.log"
