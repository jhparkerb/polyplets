#!/bin/bash
# ayr_a27.sh -- a(27) frontier run, AYR HALF of a dalby+ayr split.
# Companion: scripts/dalby_a27.sh. Per docs/a26-a30-diagonal-plan.md.
#
# STAGED, not yet launched. Launch alongside dalby_a27.sh (after a26 lands +
# rebalance). ayr is built native at rev 246cb09 (go1.26 in $HOME/go/bin;
# /usr/bin/go 1.19.8 is the decoy -- do NOT use it). Binary smoke-tested:
# a(1)-a(18) match the b-file at both u64 and u128.
#
# ayr sweeps the tail H3..H15 (all real). H16 + all closed-form heights are
# dalby's (see dalby_a27.sh). Est. ~4.0h @ 32 cores.
#
# REBALANCE: if this half is the long pole vs dalby's H16, move H14/H15 to
# dalby_a27.sh --heights and drop them from here.
#
# counter=u128 (verified cross-ISA on ayr). RAM: (78GiB*0.6)/32 ~ 1.46GiB;
# using 1GiB/worker (proven safe on the a25 ayr job), spill covers overflow.
# ayr-job-budget-rule: 32c x 1GiB = 32GiB, fits 78GiB, ayr otherwise idle.
set -e
cd ~/src/polyominoes-ns
export PATH=$HOME/go/bin:$PATH   # modern go, not /usr/bin/go 1.19.8
RUNDIR=runs/ns_a27/ayr
mkdir -p "$RUNDIR/spill" runs/ns_a27/perheight

echo "=== a27 ayr-half starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# ayr: swept tail H3..H15 (13 heights), overlapped to hide merge idle.
T0=$(date +%s)
./build/ns/orchestrate --maxn 27 --counter u128 --ram 1073741824 \
  --heights 3-15 \
  --overlap-heights 13 --cores 32 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a27/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a27 ayr-half exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
echo "NOTE: rsync this perheight to the combine host after BOTH halves finish."
