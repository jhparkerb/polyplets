#!/usr/bin/env bash
# ns_overlap_ayr.sh — re-test cross-height OVERLAP utilization on ayr (x86).
#
# Runs a(20) again with --overlap-heights K: K heights sweep concurrently
# sharing one cores-wide pool, so a height's low-utilization merge phase runs
# behind another height's map phase instead of idling the box. Compare the
# overall effective cores (cpu_s/wall_s, from the event=column telemetry) and
# total wall against the sequential a(20) run (runs/ns_a20) to measure the
# utilization win. --compare still validates the answer = a(20).
#
# Run AFTER the sequential a(20) (ns_a20_ayr.sh) finishes, with the overlap-
# enabled engine deployed (cross-compile orchestrate on gympie + ship; workers
# are unchanged). Separate run-dir so it doesn't clobber the sequential run.
#
# Target: ayr 32c / 78 GB. NOTE: K concurrent heights => ~K x the per-height RAM;
# size K so K*peak fits 78 GB (a(20) per-height peak is small, K=4 is safe).
# No mid-run checkpoint in overlap mode (test path) — on a kill, re-run.
#
# Usage: ns_overlap_ayr.sh [OVERLAP_K] [CORES] [MULT] [RAM_PER_WORKER_GB]
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K="${1:-4}"; CORES="${2:-30}"; MULT="${3:-4}"; RAMW_GB="${4:-1}"
RAM=$(( RAMW_GB * 1024 * 1024 * 1024 ))

ROOT="$REPO/runs/ns_a20_overlap"; RUNDIR="$ROOT/run"; SPILL="$RUNDIR/spill"; PERH="$ROOT/perheight"
mkdir -p "$SPILL" "$PERH"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
echo "ns_overlap_ayr rev=$REV host=$(hostname -s) overlap=$K cores=$CORES mult=$MULT ram_gb=$RAMW_GB start=$(date -Is)" | tee "$ROOT/overlap.log"

"$REPO/build/ns/orchestrate" --maxn 20 --cores "$CORES" --unit-mult "$MULT" \
  --overlap-heights "$K" --ram "$RAM" --run-dir "$RUNDIR" --spill-dir "$SPILL" \
  --per-height-out "$PERH" --compare \
  --cost-profile-out "$ROOT/profile.tsv" 2>&1 | tee -a "$ROOT/overlap.log"

echo "ns_overlap_ayr done=$(date -Is)" | tee -a "$ROOT/overlap.log"
