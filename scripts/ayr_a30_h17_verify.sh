#!/bin/bash
# ayr_a30_h17_verify.sh -- independent cross-kernel validation of a(30)'s top
# real height H17. ayr runs the COLUMN kernel on H17 only (--heights 17) while
# dalby computes a(30) with the KINK kernel; the two kernels' per-column
# boundary frontier counts (frontier_in/frontier_out, the H+2 between-column
# states) must match column-by-column, and the final T(n,17) row (h17.out)
# must match dalby's kink h17.out. Column vs kink are independent transition
# implementations, so this is the independent-reimplementation check for H17.
#
# Runs incrementally: each completed column adds a matched frontier count, so
# the rising columns give confidence within hours even though the full H17
# sweep is long. Checkpointed -- kill/resume with --resume; safe to stop early.
#
# Cost: column H17 at maxn=30 is heavy (~33h full on ayr's 32 cores; column is
# ~50-100x the cpu of kink at this height). Spill peaks large (~200GB uncompressed);
# spill dir is under ~/src (/home, 395GB free) NOT /tmp (56GB). RAM 32c x 1GiB
# = 32GiB cap, fits 78GiB (ram-budget-per-worker). counter=u128.
#
# ayr uses modern go from $HOME/go/bin (the /usr/bin/go 1.19.8 is too old).
set -e
cd ~/src/polyominoes-ns
export PATH=$HOME/go/bin:$PATH
RUNDIR=runs/ns_a30_h17verify
mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"

echo "=== a30 H17 column-kernel verify starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

T0=$(date +%s)
./build/ns/orchestrate --maxn 30 --heights 17 --counter u128 \
  --cores 32 --ram 1073741824 --unit-mult 4 --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a30 H17 verify exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
echo "H17_VERIFY_DONE rc=$RC"
