#!/bin/bash
# dalby_a29.sh -- the a(29) record run, dalby-solo. Runs CONCURRENTLY with
# ayr_a28.sh (ayr does a(28) solo); one self-contained term per box, no
# cross-machine combine. Per docs/a26-a30-diagonal-plan.md.
#
# maxn=29 with P9..P12 wired (diagonalCell case 9..12, commits 2ddd474/3ec68de;
# simplify cleanup ee60e07) and the n>=2k+1 dispatch threshold:
# diagonalStripValid covers k=2..12, i.e. H=17..27 by closed form, plus pole
# H28 + top H29 + low H1,H2. Real sweep is only H3..H16 (top real H=16, ~a27's
# H16 profile: ~3.4h for that height on dalby; est ~4-5h wall total).
#
# counter=u128: a(29) ~3.3e22 overflows u64 (u128ExactMaxN=48). Big.Int result
# pipeline handles maxn>=26.
#
# RAM: (125GiB*0.6)/80 ~ 0.94GiB -> 1GiB/worker (ram-budget-divide-by-cores).
# Peak in-RAM is bounded by cores x ram ~80GiB (semaphore caps concurrent
# workers at --cores regardless of --overlap-heights); spill covers overflow.
# Proven safe on a21/a26/a27.
#
# Resume: re-run with --resume (checkpoints at column boundaries every 300s).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a29/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a29/perheight

echo "=== a29 run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# No --compare (b-file only extends to a20). Post-run: combine --maxn 29 then
# validate a1-20 vs b-file + a21-27 vs results/ns_a2{1..7}/ + growth ~6.86.
T0=$(date +%s)
./build/ns/orchestrate --maxn 29 --counter u128 --ram 1073741824 \
  --overlap-heights 14 --cores 80 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a29/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a29 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
