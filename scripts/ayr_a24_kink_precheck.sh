#!/bin/bash
# Design 14 Phase 3 PRE-CHECK (not the formal gate) -- ayr-solo, orchestrate
# --maxn 24 --kernel kink, correctness-only. The formal Phase 3 (dalby-scale
# retune + full per-height cell diff) still runs on dalby once a(29) frees up
# -- this is just an early kink-kernel correctness read at a24 scale, using
# ayr while it's idle.
#
# Predicted cost: a(24)'s dominant real height (H16) measured 285979 cpu_s /
# 4870.3s wall on dalby's 80 cores (~73% parallel efficiency). Scaled to
# ayr's 32 cores at similar efficiency: ~12200s (~3.4h) wall for H16, plus
# small change for the rest. This is an extrapolation, not a measurement --
# real wall may differ.
#
# RAM: 32 cores x 1 GiB/worker = 32 GiB cap, well inside ayr's 78 GiB
# (matches the a26-a29 precedent: total*margin/cores ~ 78*0.4/32 ~ 1GiB).
#
# Validation: kink kernel's own a(24) total vs the banked, certified
# results/ns_a24/a_n.txt value (2194666793369310473). This is a total-value
# check only, not per-height, per-cell diff -- that stronger cell-by-cell
# gate (like scripts/kink_gate_a20.sh) is deferred to the real dalby Phase 3
# run, which also re-runs the column kernel fresh to diff against.
#
# Resume: re-run with --resume (checkpoints every 300s at column boundaries).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a24_kink_precheck

mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"

echo "=== a24 kink precheck starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

T0=$(date +%s)
./build/ns/orchestrate --maxn 24 --kernel kink --cores 32 --ram 1073741824 \
  --unit-mult 4 --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a24 kink precheck exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="

echo "=== combine total ==="
./build/ns/combine -in "$RUNDIR/perheight" -maxn 24 -out "$RUNDIR/a_n.txt"
echo "=== diff vs banked results/ns_a24/a_n.txt ==="
diff "$RUNDIR/a_n.txt" results/ns_a24/a_n.txt && echo "A24_KINK_PRECHECK_MATCH" || echo "A24_KINK_PRECHECK_MISMATCH"
