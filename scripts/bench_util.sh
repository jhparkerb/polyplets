#!/bin/bash
# bench_util.sh -- bounded utilization benchmark: sweep a SUBSET of heights of
# a known maxn (real frontier-scale columns, no full triangle) and report
# per-height wall/cpu/utilization from the cost profile. Not a --compare run
# (a heights-subset triangle is intentionally incomplete); correctness rests
# on the gate suite (make ns-gates), not this script.
#
# Usage: bench_util.sh LABEL MAXN HEIGHTS [OVERLAP] [STEAL_GRAIN] [MERGE_MULT]
#   LABEL       tag for the run dir / log (e.g. baseline-h17, fixed-h17)
#   MAXN        e.g. 34 (reuses the real P9-P15 diagonal injection config)
#   HEIGHTS     e.g. "17" or "16,17"
#   OVERLAP     --overlap-heights value (default 1 = sequential)
#   STEAL_GRAIN default 0.05 (0 = steal off)
#   MERGE_MULT  default 1, matching term.sh's deployed default
#               (docs/engine-record.md Bottleneck #2) -- pass a
#               different value deliberately to A/B against it, not by
#               omission, so a benchmark run doesn't silently diverge from
#               the production config it's meant to be compared against.
#
# unit-mult 8, --persistent-workers, GOGC=1000: same reasoning as MERGE_MULT
# above -- these are the term.sh-validated production baseline
# (docs/engine-record.md Bottlenecks #3, #5, #6), not
# parameters this script varies, so they're hardcoded rather than left at
# stale pre-fix defaults. A future A/B of one of these specifically should
# edit the script deliberately, the same way MERGE_MULT's comment asks for.
export GOGC=1000
set -e
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="$1"; MAXN="$2"; HEIGHTS="$3"; OVERLAP="${4:-1}"; GRAIN="${5:-0.05}"; MERGE_MULT="${6:-1}"
[ -n "$HEIGHTS" ] || { echo "usage: bench_util.sh LABEL MAXN HEIGHTS [OVERLAP] [STEAL_GRAIN] [MERGE_MULT]"; exit 2; }

RUNDIR="runs/bench_util/${LABEL}"
rm -rf "$RUNDIR"
mkdir -p "$RUNDIR/spill"

echo "=== bench $LABEL: maxn=$MAXN heights=$HEIGHTS overlap=$OVERLAP grain=$GRAIN merge_mult=$MERGE_MULT unitlog=${POLY_UNIT_LOG:-0} rev=$(git rev-parse --short HEAD) $(date -Iseconds) ==="
T0=$(date +%s)
./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --unit-mult 8 --merge-mult "$MERGE_MULT" --steal-grain "$GRAIN" \
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
[ "$RC" = 0 ] || exit "$RC"

echo "=== $LABEL utilization by height ==="
awk 'NR>2{wall[$1]+=$5; cpu[$1]+=$6} END{
  tw=0;tc=0; for(h in wall){tw+=wall[h]; tc+=cpu[h]}
  printf "%-4s %10s %10s %8s\n","H","wall_s","cpu_s","util%"
  for(h=1;h<=40;h++) if(h in wall) printf "%-4d %10.1f %10.1f %8.1f\n", h, wall[h], cpu[h], 100*cpu[h]/wall[h]/80
  printf "TOTAL %10.1f %10.1f %8.1f\n", tw, tc, 100*tc/tw/80
}' "$RUNDIR/cost_profile.tsv"
echo "=== BENCH_${LABEL}_DONE ==="
