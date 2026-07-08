#!/bin/bash
# dalby_term.sh N -- compute a(N) dalby-solo on the kink kernel, then validate.
# Generalizes dalby_a30.sh for the successive-term loop (a31, a32, ...).
# Config = the a29-cell-validated kink config. maxn=N: P9-P12 closed-form
# diagonals cover H(N-2)..H(N-12); real sweep is H3..H(N-13) (top real height
# grows +1 per term). counter=u128. RAM 80c x 1GiB (kink is RAM-light).
#
# --overlap-heights 2: sweeps 2 heights concurrently in one core pool, hiding
# a straggler height's idle tail behind another height's map work. Measured
# real dalby H16+H17 win: 24.7%->33.0% utilization, byte-identical CPU-seconds
# (results/utilization-fix-and-ceiling.md). Checkpoints at height boundaries
# (gated: orchestrator/overlap_resume_test.go), not per-column.
#
# Resume: dalby_term.sh N --resume
set -e
cd ~/src/polyominoes-ns
N="$1"
[ -n "$N" ] || { echo "usage: dalby_term.sh N [--resume]"; exit 2; }
RUNDIR=runs/ns_a${N}/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a${N}/perheight

echo "=== a${N} KINK run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

RESUME_FLAG=""
[ "$2" = "--resume" ] && RESUME_FLAG="--resume"

T0=$(date +%s)
./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --unit-mult 4 --steal-grain 0.05 \
  --overlap-heights 2 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out runs/ns_a${N}/perheight \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a${N} run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
[ "$RC" = 0 ] || exit "$RC"

echo "=== combine ==="
./build/ns/combine -in runs/ns_a${N}/perheight -maxn "$N" -out "$RUNDIR/a_n.txt" 2>&1 | tee "$RUNDIR/combine.log"

MISMATCH=0
echo "=== validate a(1)-a(20) vs b-file ==="
for n in $(seq 1 20); do
  got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
  known=$(awk -v n=$n '$1==n{print $2}' fixtures/b006770.txt)
  if [ "$got" = "$known" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (b=$known)"; MISMATCH=1; fi
done
echo "=== validate a(21)-a($((N-1))) vs banked ==="
for n in $(seq 21 $((N-1))); do
  got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
  bank=$(awk -v n=$n '$1==n{print $2}' results/ns_a${n}/triangle.txt 2>/dev/null)
  [ -z "$bank" ] && { echo "a($n): no banked value"; continue; }
  if [ "$got" = "$bank" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (banked=$bank)"; MISMATCH=1; fi
done

aN=$(awk -v n=$N '$1==n{print $2}' "$RUNDIR/a_n.txt")
aP=$(awk -v n=$((N-1)) '$1==n{print $2}' "$RUNDIR/a_n.txt")
echo "a($N) = $aN"
python3 -c "print('growth a${N}/a$((N-1)) =', $aN/$aP)"
if [ "$MISMATCH" = 0 ]; then echo "A${N}_VALIDATE_PASS"; else echo "A${N}_VALIDATE_FAIL"; fi
echo "A${N}_DONE"
