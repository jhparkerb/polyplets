#!/usr/bin/env bash
# gate_ns_resume.sh — AC-2 kill+resume gate for the orchestrator.
# Usage: bash tests/gate_ns_resume.sh [TRIALS [MAXN [CORES]]]
# Runs TRIALS random-timing kill+resume cycles.
# Each trial: start orchestrator, SIGTERM after a random delay, resume to completion
# with --compare, expect gate_parallel PASS.
set -euo pipefail

TRIALS=${1:-25}
MAXN=${2:-8}
CORES=${3:-4}
RAM=4194304
ORC=./build/ns/orchestrate

pass=0; fail=0; skip=0
for i in $(seq 1 "$TRIALS"); do
    TDIR=/tmp/ns_resume_$$_$i
    mkdir -p "$TDIR/spill"

    # Random delay 0.05..0.60 s (run takes ~0.7 s total, so this reliably kills mid-run)
    delay=$(python3 -c "import random; print(f'{random.uniform(0.05,0.60):.3f}')")

    # First run — kill after random delay
    "$ORC" --maxn "$MAXN" --cores "$CORES" --ram "$RAM" \
        --run-dir "$TDIR" --spill-dir "$TDIR/spill" \
        --checkpoint "$TDIR/POLYCKPT" \
        --checkpoint-every 0 >/dev/null 2>&1 &
    PID=$!
    sleep "$delay"
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true

    # No checkpoint → first run completed before the kill; skip this trial
    if [ ! -f "$TDIR/POLYCKPT" ]; then
        rm -rf "$TDIR"
        skip=$((skip+1))
        continue
    fi

    H=$(awk '/^H /{print $2}' "$TDIR/POLYCKPT")
    COL=$(awk '/^col /{print $2}' "$TDIR/POLYCKPT")
    CKPT="H${H}col${COL}"

    # Resume to completion (no second kill)
    OUT=$("$ORC" --maxn "$MAXN" --cores "$CORES" --ram "$RAM" \
        --run-dir "$TDIR" --spill-dir "$TDIR/spill" \
        --checkpoint "$TDIR/POLYCKPT" \
        --checkpoint-every 0 --resume --compare 2>&1) || true

    rm -rf "$TDIR"

    if echo "$OUT" | grep -q "gate_parallel PASS"; then
        echo "pass i=$i delay=$delay ckpt=$CKPT"
        pass=$((pass+1))
    else
        echo "FAIL i=$i delay=$delay ckpt=$CKPT result='gate_parallel FAIL'"
        fail=$((fail+1))
    fi
done

echo "pass=$pass fail=$fail skip=$skip"
[ "$fail" -eq 0 ]
