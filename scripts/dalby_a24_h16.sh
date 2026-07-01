#!/bin/bash
# dalby_a24_h16.sh -- the real a(24) record run, dalby-only.
#
# Reuses H1-15 from the perf-audit probe (scripts/perf_audit_run.sh,
# 2026-06-30, rev 5fadde3, byte-verified: T(22,15)=1035856891052731 matches
# the value pinned in results/ns_a23/RESULT.md's k=7 derivation). Rather than
# resweep the already-computed cheap heights (the a24-launch-plan.md 3-box
# split), this run does ONLY the swept work that's actually still needed:
#
#   - H16, the monster (~81 core-h / 34.5 dalby-eff = ~2.35h floor, per
#     docs/a24-launch-plan.md) -- the one height the probe didn't reach.
#   - H1,H2 (closed form, instant) -- recomputed here as a free cross-check
#     against the probe's swept H1,H2 (should be byte-identical).
#   - H17-H24 (closed-form k<=7 diagonals + pole + top, all instant) -- the
#     injected strips a24-launch-plan.md calls for.
#
# H3-H15 are NOT in --heights here; they come from the probe's
# runs/ns_a24/perheight/h{3..15}.out (copied in before combine).
#
# No ayr needed: with H1-15 already in hand, H16 alone is the wall-clock
# floor regardless -- adding a second machine wouldn't shorten it, only add
# combine-coordination risk. Single box, single real sweep height.
#
# Predicted: ~2.35h wall, cores=80, ram=1GiB/worker (per feedback memory
# ram-budget-divide-by-cores: (125GiB*0.6)/80 ~ 0.94GiB), disk: negligible
# (H16 frontier ~0.45GB per a24-launch-plan.md, well under the 346GB free).
# Resume: --resume with the same command if it crashes (checkpoints at
# column boundaries via --checkpoint-every 0).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a24/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a24/perheight

echo "=== a24 H16 run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

T0=$(date +%s)
./build/ns/orchestrate --maxn 24 --counter u64 --ram 1073741824 \
  --heights 1,2,16-24 --overlap-heights 1 --cores 80 --unit-mult 4 \
  --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 30 $RESUME_FLAG \
  --per-height-out runs/ns_a24/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a24 H16 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
