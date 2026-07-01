#!/bin/bash
# dalby_a25.sh -- the a(25) record run, dalby-solo.
#
# a(25) is the current Go result-pipeline ceiling (CheckResultWidth caps
# maxn at 25; a(26)+ needs the pipeline widened to big.Int first -- see
# BUGS-OF-SHAME A2). With P8 now pinned and wired (diagonalCell case 8,
# commit 2a520ea), a(25) injects H17-25 (k=2..8 diagonals + pole + top) via
# closed form and sweeps only H<=16 -- same swept range as a(24)'s ORIGINAL
# 3-box plan (docs/a24-launch-plan.md), just at maxn=25 instead of 24. H1,H2
# are also closed-form (contributeLowHeight fires automatically for those,
# same as every other run this project).
#
# Not resuming/extending a(24)'s reused H1-15 data here: that data is
# maxn=24-specific (columns run col=0..maxn, so a different maxn needs a
# genuinely fresh sweep, not a checkpoint-continuation -- the checkpoint
# format ties Maxn to the run and checkResumeConfig would reject a mismatch
# anyway). H3-16 are swept fresh in this one run.
#
# Dalby-solo (no ayr): avoids cross-machine combine risk for a job we're not
# actively racing against a deadline -- a background tail --pid waiter costs
# nothing while it runs, so there's no strong reason to add split complexity
# just to shave wall time. docs/a24-launch-plan.md's own "dalby solo
# fallback" for the H3-16 range at maxn=24 predicted ~3.7h; expect a similar
# order of magnitude here (one column deeper). Explicitly agreed by the user
# this session (multiple times, emphatically).
#
# RAM: (125GiB*0.6)/80 ~ 0.94GiB -> 1GiB/worker (feedback memory
# ram-budget-divide-by-cores; proven safe on the H1-15 probe and the a(24)
# H16 run). Resume: --resume with the same command if it crashes
# (checkpoints at column boundaries).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a25/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a25/perheight

echo "=== a25 run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# No --compare: fixtures/b006770.txt only extends to a(20), so orchestrate's
# built-in CompareToKnown would report a21-25 as FAIL (known=0) and exit 1 --
# a false failure, same benign artifact seen on the a(24) probe. Validate
# a21-24 by hand against results/ns_a23/RESULT.md and results/ns_a24/RESULT.md
# after the run, same as a(24) did.
T0=$(date +%s)
./build/ns/orchestrate --maxn 25 --counter u64 --ram 1073741824 \
  --overlap-heights 14 --cores 80 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 30 $RESUME_FLAG \
  --per-height-out runs/ns_a25/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a25 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
