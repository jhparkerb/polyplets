#!/bin/bash
# Design 14 Phase 3 PRE-CHECK (not the formal gate) -- ayr-solo, orchestrate
# --maxn 24 --kernel kink, correctness-only. The formal Phase 3 (dalby-scale
# retune + full per-height cell diff) still runs on dalby once a(29) frees up
# -- this is just an early kink-kernel correctness read at a24 scale, using
# ayr while it's idle.
#
# Predicted cost: current code's closed-form diagonal covers k=2..11 at
# maxn=24 (diagonalStripValid, orchestrator/sweep.go), so the real column
# sweep only needs to reach H=12 (not H=16, which was the dominant height in
# a24's ORIGINAL run before P8-P11 were wired). The a(20) kink gate already
# measured this code's cost at a comparable top real height (H=10): 30s
# total wall on ayr. H=12 is two heights taller; expect low minutes, not
# hours. Measured (not extrapolated from the stale historical a24 H16 run).
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
