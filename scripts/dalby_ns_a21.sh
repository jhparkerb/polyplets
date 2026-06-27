#!/bin/bash
# dalby_ns_a21.sh — new next-system engine, a(21) cross-check run on dalby
#
# Purpose:  T3.2 gate — new engine a(21) vs old engine a(21) T(n,H)
# Machine:  dalby.jhpb.org (80-core Neoverse N1, 128 GB RAM)
# Predicted cost: ~8h wall (range 6-12h), ~80 GB peak RAM, ~15 GB disk
# Resume:   re-run this script; orchestrator picks up from POLYCKPT
# Kill:     kill $(cat $RUNDIR/orchestrate.pid)

set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
BIN=$REPO/build/ns/orchestrate
RUNDIR=$REPO/runs/ns_a21
SPILL=$RUNDIR/spill
CKPT=$RUNDIR/POLYCKPT
LOG=$RUNDIR/run.log

mkdir -p "$SPILL"

echo "=== dalby_ns_a21.sh start $(date -Iseconds) ==="
echo "binary: $BIN"
$BIN --version 2>/dev/null || true

exec $BIN \
    --maxn 21 \
    --counter u64 \
    --cores 80 \
    --ram 1073741824 \
    --run-dir "$RUNDIR" \
    --spill-dir "$SPILL" \
    --checkpoint "$CKPT" \
    --checkpoint-every 900 \
    --compare \
    2>&1 | tee "$LOG"
