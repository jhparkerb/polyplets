#!/bin/bash
# Design 14 Phase 2.8 gate: orchestrate --maxn 20 --kernel kink --compare
# (byte-matches the b-file) plus combine --diff-b, a per-height CELL diff
# (every T(n,H)) against a --kernel column a(20) run. Run from repo root.
set -e -x

RUNDIR="${1:-runs/kink_gate}"
RAM="${2:-2147483648}"
CORES="${3:-32}"

rm -rf "$RUNDIR"
mkdir -p "$RUNDIR/column_run" "$RUNDIR/kink_run" "$RUNDIR/column" "$RUNDIR/kink"

./build/ns/orchestrate --maxn 20 --cores "$CORES" --ram "$RAM" \
  --run-dir "$RUNDIR/column_run" --spill-dir "$RUNDIR/column_run/spill" \
  --checkpoint "$RUNDIR/column_run/POLYCKPT" \
  --per-height-out "$RUNDIR/column" --compare 2>&1 | tee "$RUNDIR/column.log"

./build/ns/orchestrate --maxn 20 --kernel kink --cores "$CORES" --ram "$RAM" \
  --run-dir "$RUNDIR/kink_run" --spill-dir "$RUNDIR/kink_run/spill" \
  --checkpoint "$RUNDIR/kink_run/POLYCKPT" \
  --per-height-out "$RUNDIR/kink" --compare 2>&1 | tee "$RUNDIR/kink.log"

./build/ns/combine --in "$RUNDIR/kink" --diff-b "$RUNDIR/column" --maxn 20 2>&1 | tee "$RUNDIR/diff.log"

echo KINK28GATE_DONE
