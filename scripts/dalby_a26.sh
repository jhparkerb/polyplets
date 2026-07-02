#!/bin/bash
# dalby_a26.sh -- the a(26) record run, dalby-solo, per docs/a26-a30-diagonal-plan.md.
#
# maxn=26 with P9/P10 wired (diagonalCell case 9/10, commit 20852f5) and the
# true n>=2k+1 dispatch threshold (commit e2473f8): diagonalStripValid covers
# k=2..10, i.e. H=16..24 by closed form, plus H=25,26 (pole/top) and H0,H1,H2
# via the usual low-height/pole/top paths. Real sweep is only H1-15 (top real
# H=15, matching the plan's cost table: ~303K cpu-s, ~1.1h @ 80 cores).
#
# counter=u128: u64 overflows past a25 (BUGS-OF-SHAME A2 / u128ExactMaxN=48).
# resultPipelineMaxN already widened to big.Int (commit 1a0ac2d) so maxn=26
# is accepted.
#
# RAM: (125GiB*0.6)/80 ~ 0.94GiB -> 1GiB/worker, same budget proven safe on
# the a25 run (feedback memory ram-budget-divide-by-cores).
#
# Byproduct: this run's real T(26,15) feeds P11's final closing equation
# (plan section "P_11 partially pinned" -- 2 short, T(26,15) is one of them).
#
# Resume: --resume with the same command if it crashes (checkpoints at
# column boundaries, --checkpoint-every 30s).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a26/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a26/perheight

echo "=== a26 run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# No --compare: known b-file only extends to a(20); validate a21-25 by hand
# against results/ns_a2{1,2,3,4,5}/RESULT.md after the run, same as a24/a25.
T0=$(date +%s)
./build/ns/orchestrate --maxn 26 --counter u128 --ram 1073741824 \
  --overlap-heights 14 --cores 80 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 30 $RESUME_FLAG \
  --per-height-out runs/ns_a26/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a26 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
