#!/bin/bash
# dalby_ns_a23.sh — next-system engine, a(23) frontier run on dalby
#
# Purpose:  compute a(23) (A006770) — new frontier term. a(21),a(22) come free as
#           byproducts of the maxn=23 sweep; a(1)..a(21) are recomputed and must
#           match known values (built-in consistency gate via --per-height-out).
# Machine:  dalby.jhpb.org (80-core Neoverse N1, 128 GB RAM), ~/src/polyominoes.
# Binary:   build/ns/orchestrate — MUST be a CLEAN rev that contains the diagonal
#           injection (k<=4) + work-stealing + A1 fix. Verify --version before go.
#
# Predicted cost (FILL FROM a(20) VALIDATION before launch — see
#   docs/a23-job-checklist.md): wall ~= clean_a20_wall * 4.4^3 (~85x, 3 terms);
#   peak RAM ~120 GB (disk/spill-bound, scales slower than compute); disk spill
#   large — provision >= 300 GB free on $SPILL. Re-confirm against measured a(20).
#
# Resume:   re-run this script with --resume; orchestrator picks up from POLYCKPT.
# Kill:     kill $(cat $RUNDIR/orchestrate.pid)

set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
BIN=$REPO/build/ns/orchestrate
RUNDIR=$REPO/runs/ns_a23
SPILL=$RUNDIR/spill
CKPT=$RUNDIR/POLYCKPT
PERH=$RUNDIR/perheight
LOG=$RUNDIR/run.log

# spill budget (bytes) — RAISE if dalby has headroom (less disk spill); LOWER if
# peak RAM crowds 128 GB. 4 GiB default; tune from a(20) validation peak RAM.
RAM_SPILL=${RAM_SPILL:-$((4 * 1024 * 1024 * 1024))}
RESUME=${RESUME:-0}

mkdir -p "$SPILL" "$PERH"

echo "=== dalby_ns_a23.sh start $(date -Iseconds) ==="
echo "binary: $BIN"
$BIN --version 2>/dev/null || true
echo "spill budget: $RAM_SPILL bytes   resume: $RESUME"

ARGS=(
    --maxn 23
    --counter u64
    --cores 80
    --ram "$RAM_SPILL"
    --steal-grain 0.05
    --overlap-heights 1
    --run-dir "$RUNDIR"
    --spill-dir "$SPILL"
    --checkpoint "$CKPT"
    --checkpoint-every 900
    --per-height-out "$PERH"
)
[ "$RESUME" = "1" ] && ARGS+=(--resume)

exec "$BIN" "${ARGS[@]}" 2>&1 | tee -a "$LOG"
