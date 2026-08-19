#!/bin/bash
# a40_h20_recheck.sh -- clean H20-only re-sweep to reconfirm the
# Zero-Harvest-recovered T(n,20) column of a(40), especially T(40,20)
# (the one row with no independent cross-check; incident in
# results/ns_a40/PROVENANCE.md).
#
# Target: dalby, 48 cores (phase B's exact validated config: kink,
# u128, 1GiB/worker, levers on). Predicted from phase B measured:
# ~34.5ks sweep (~9.6h), rss ~1GB/worker, disk far under free space.
#
# Zero-Harvest safety: FRESH run dir + FRESH checkpoint; never touches
# runs/ns_a40/ or results/. Diff target is the banked (in-repo) column.
# Resume: scripts/a40_h20_recheck.sh --resume
# Kill: kill <orchestrate PID> (ps -Ao pid,command | grep '[o]rchestrate')
# Verdict line: A40_H20_RECHECK_MATCH or A40_H20_RECHECK_MISMATCH.
set -e
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNDIR=runs/a40_h20_recheck
mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"

RESUME_FLAG=""
[ "$1" = "--resume" ] && [ -f "$RUNDIR/POLYCKPT.RECHECK" ] && RESUME_FLAG="--resume"

export POLY_FRONTIER_ZSTD=1
export POLY_FASTMAP_FLOOR_GB=${POLY_FASTMAP_FLOOR_GB:-40}

echo "=== a40 H20 recheck starting: $(date -Iseconds) rev=$(git rev-parse --short HEAD) resume=${RESUME_FLAG:-no} ==="
./build/ns/orchestrate --maxn 40 --kernel kink --counter u128 \
  --cores 48 --ram 1073741824 --overlap-heights 1 \
  --heights 20 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --fast-map-dir /dev/shm/a40_h20_recheck \
  --checkpoint "$RUNDIR/POLYCKPT.RECHECK" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee -a "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
[ "$RC" = 0 ] || { echo "orchestrate rc=$RC"; exit "$RC"; }

echo "=== diff vs banked (checkpoint-recovered) column ==="
if diff results/ns_a40/perheight/h20.out "$RUNDIR/perheight/h20.out"; then
  echo A40_H20_RECHECK_MATCH
else
  echo A40_H20_RECHECK_MISMATCH
fi
echo "=== done: $(date -Iseconds) ==="
