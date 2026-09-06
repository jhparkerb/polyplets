#!/bin/bash
# gympie_bench_phase.sh -- SHORT local phase-split benchmark (Second Wind thread).
#
# Purpose: measure the per-column map/merge/serialization wall split of the
# production kink kernel post-Even-Keel at gympie scale, to rank a(37) engine
# levers before building anything. Not a --compare run; correctness rests on
# the gate suite.
#
# Target machine: gympie (Apple Silicon laptop), 10 perf cores HARD cap.
# Predicted cost: ~3-6 min wall, 10 cores, <4 GB RAM, <1 GB disk under
# runs/bench_phase/<LABEL>. Basis: dalby ran the same H15/maxn30 sweep in
# 141s at 80 cores / 4554 cpu-s (docs/engine-record.md D5);
# gympie cores are ~3x a dalby core, so ~4554/30 =~ 150-450s here.
# Kill: kill $(cat runs/bench_phase/<LABEL>/orchestrate.pid). No resume
# (throwaway benchmark).
#
# Usage: gympie_bench_phase.sh LABEL MAXN HEIGHTS [OVERLAP]
# Flags mirror the dalby production baseline (bench_util.sh) except --cores
# and --ram, resized for gympie per the RAM-budget rule ((24GB*0.6)/10).
export GOGC=1000
set -e
cd "$(dirname "$0")/.."
LABEL="$1"; MAXN="$2"; HEIGHTS="$3"; OVERLAP="${4:-1}"
[ -n "$HEIGHTS" ] || { echo "usage: gympie_bench_phase.sh LABEL MAXN HEIGHTS [OVERLAP]"; exit 2; }

RUNDIR="runs/bench_phase/${LABEL}"
rm -rf "$RUNDIR"
mkdir -p "$RUNDIR/spill"

echo "=== bench $LABEL: maxn=$MAXN heights=$HEIGHTS overlap=$OVERLAP rev=$(git rev-parse --short HEAD) $(date -Iseconds) ==="
T0=$(date +%s)
./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 \
  --cores 10 --ram 1503238553 --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
  --overlap-heights "$OVERLAP" --persistent-workers \
  --heights "$HEIGHTS" \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 60 \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log" &
ORCH_PID=$!
echo "$ORCH_PID" > "$RUNDIR/orchestrate.pid"
wait "$ORCH_PID"
RC=$?
T1=$(date +%s)
echo "=== bench $LABEL exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
exit "$RC"
