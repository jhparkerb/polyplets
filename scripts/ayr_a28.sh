#!/bin/bash
# ayr_a28.sh -- the a(28) record run, ayr-solo (FIRST SEXTILLION term,
# a(28) ~4.8e21). Runs CONCURRENTLY with dalby_a29.sh (dalby does a(29) solo);
# one self-contained term per box, no cross-machine combine.
#
# ayr is built native (go1.26 in $HOME/go/bin; /usr/bin/go 1.19.8 is the decoy
# -- do NOT use it). maxn=28 with P9..P12 wired (case 9..12): diagonalStripValid
# covers k=2..12, i.e. H=16..26 closed form, pole H27, top H28, low H1,H2. Real
# sweep is only H3..H15 (top real H=15 -- the same height a26 swept dalby-solo
# in ~68min, and the same tail ayr already swept in the a27 split, so this is
# proven-feasible on ayr's 78GiB).
#
# counter=u128: a(28) ~4.8e21 overflows u64.
# RAM: 32c x 1GiB = 32GiB in-RAM cap (semaphore bounds concurrent workers),
# fits 78GiB with wide margin; spill covers overflow. ayr otherwise idle
# (ayr-job-budget-rule).
#
# Resume: re-run with --resume (checkpoints every 300s at column boundaries).
set -e
cd ~/src/polyominoes-ns
export PATH=$HOME/go/bin:$PATH   # modern go, not /usr/bin/go 1.19.8
RUNDIR=runs/ns_a28/ayr
mkdir -p "$RUNDIR/spill" runs/ns_a28/perheight

echo "=== a28 run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

# No --compare (b-file only extends to a20). Post-run: combine --maxn 28 then
# validate a1-20 vs b-file + a21-27 vs results/ns_a2{1..7}/ + growth ~6.86.
T0=$(date +%s)
./build/ns/orchestrate --maxn 28 --counter u128 --ram 1073741824 \
  --overlap-heights 13 --cores 32 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a28/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a28 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
