#!/bin/bash
# dalby_a30.sh -- the a(30) record run, dalby-solo, KINK kernel.
# First production frontier term on the kink-carry engine (validated at a29
# scale: orchestrate --kernel kink cell-matched every T(n,H) vs the column
# production per-height, 2026-07-03).
#
# Config is EXACTLY the a29 kink-validation config (scripts/kink_validate.sh,
# which passed the full cell-diff) -- do not add --overlap-heights or change
# unit-mult/steal-grain: that config is what was validated. maxn=30 with
# P9..P12 closed-form diagonals (diagonalStripValid k=2..12): H18..28 closed
# form + pole H29 + top H30 + low H1,H2; real sweep is H3..H17 (top real H17).
#
# counter=u128: a(30) ~3.3e23 overflows u64.
# RAM: 80c x 1GiB = 80GiB cap (ram-budget-per-worker: 125GiB*0.6/80 ~ 0.94).
#   kink is RAM-light in practice (a29 kink rss_max was 181MB; intermediates
#   stay in RAM but the frontier is small and spill is barely touched).
# Predicted cost: a29 kink was wall 1932s (~32min) at top real H16; a30's top
#   real height is H17 (~2.5x more states) -> est ~70-90min wall, ~100k cpu_s.
#   Extrapolated, not measured at H17.
#
# Resume: re-run with --resume (checkpoints every 300s at column boundaries).
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a30/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a30/perheight

echo "=== a30 KINK run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
if [ "$1" = "--resume" ]; then
  RESUME_FLAG="--resume"
fi

T0=$(date +%s)
./build/ns/orchestrate --maxn 30 --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --unit-mult 4 --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a30/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a30 run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
[ "$RC" = 0 ] || exit "$RC"

# ---- combine + validate ----
echo "=== combine (all 30 heights present exactly once) ==="
./build/ns/combine -in runs/ns_a30/perheight -maxn 30 -out "$RUNDIR/a_n.txt" 2>&1 | tee "$RUNDIR/combine.log"

MISMATCH=0
echo "=== validate a(1)-a(20) vs b-file (matched by n) ==="
for n in $(seq 1 20); do
  got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
  known=$(awk -v n=$n '$1==n{print $2}' fixtures/b006770.txt)
  if [ "$got" = "$known" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (b-file=$known)"; MISMATCH=1; fi
done

echo "=== validate a(21)-a(29) vs banked results ==="
for n in 21 22 23 24 25 26 27 28 29; do
  got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
  bank=$(awk -v n=$n '$1==n{print $2}' results/ns_a${n}/triangle.txt 2>/dev/null)
  if [ -z "$bank" ]; then echo "a($n): no banked value"; continue; fi
  if [ "$got" = "$bank" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (banked=$bank)"; MISMATCH=1; fi
done

echo "=== a(30) + growth ratio ==="
a30=$(awk '$1==30{print $2}' "$RUNDIR/a_n.txt")
a29=$(awk '$1==29{print $2}' "$RUNDIR/a_n.txt")
echo "a(30) = $a30"
python3 -c "print('growth a30/a29 =', $a30/$a29)"

if [ "$MISMATCH" = 0 ]; then echo "A30_VALIDATE_PASS"; else echo "A30_VALIDATE_FAIL"; fi
echo "A30_DONE"
