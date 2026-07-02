#!/bin/bash
# dalby_a27.sh -- a(27) frontier run, DALBY HALF of a dalby+ayr split.
# Companion: scripts/ayr_a27.sh. Per docs/a26-a30-diagonal-plan.md.
#
# STAGED, not yet launched. Launch AFTER a26 lands and AFTER rebalancing the
# height split against a26's real cost profile (see "REBALANCE" below).
#
# a27 = maxn 27, top real height H16 (k=11 = P11 not needed; diagonalStripValid
# caps at k<=10 = P10, all wired). Real-swept heights: H3..H16. Closed-form
# (instant): H1,H2 (low) + H17..H27 (k=0..10 diagonals + pole + top).
#
# SPLIT RATIONALE: H16 is ~68% of total cpu-s (a25 profile: H16=68%, H15=23%,
# H<=14~9%), and only dalby (80c) is fast enough to keep H16 off the critical
# path. dalby takes H16 + ALL the closed-form heights (instant); ayr takes the
# swept tail H3..H15. Est. wall: dalby H16 ~3.4h, ayr H3-15 ~4.0h -> ~4h wall
# (vs ~5h dalby-solo). The split is also the rehearsal for the a28-a30 splits
# where the wall-time win is large.
#
# REBALANCE BEFORE LAUNCH: a26 sweeps H1..H15 at maxn=26 -- its
# runs/ns_a26/dalby/cost_profile.tsv gives near-exact per-height costs that
# a27's H3..H15 match within a few %. If ayr(H3-15) wall > dalby(H16) wall,
# move H14 (and/or H15) from ayr_a27.sh to this file's --heights to tighten.
#
# counter=u128 (a27 total ~7e20 overflows u64; verified cross-ISA on ayr).
# RAM: (125GiB*0.6)/80 ~ 1GiB/worker.
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a27/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a27/perheight

echo "=== a27 dalby-half starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# dalby: H16 (the monster, swept) + H1,H2,H17-27 (closed-form, instant).
# --overlap-heights 1: H16 is the only real sweep; closed-forms need no pool.
T0=$(date +%s)
./build/ns/orchestrate --maxn 27 --counter u128 --ram 1073741824 \
  --heights 1,2,16,17-27 \
  --overlap-heights 1 --cores 80 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a27/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a27 dalby-half exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
echo "NOTE: combine with ayr's perheight after BOTH halves finish (see ayr_a27.sh)."
