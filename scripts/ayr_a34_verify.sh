#!/bin/bash
# ayr_a34_verify.sh -- INDEPENDENT cross-ISA re-computation of a(34) on ayr
# (x86-64, gcc/native-Go build) to cross-check the dalby (aarch64) result.
#
# Same kink algorithm + config as dalby_term.sh 34, only the hardware/compiler
# differ (ARM Neoverse-N1 + dalby-Go  vs  x86-64 + ayr ~/go/bin/go 1.24 native).
# The triangle is exact integer counting, so a correct run must reproduce the
# banked results/ns_a34/triangle.txt BYTE-FOR-BYTE (n=1..34). This catches
# compiler/UB/platform-deterministic and transient/hardware faults; it does NOT
# catch a deterministic bug shared by the kink algorithm itself (that needs the
# column kernel, infeasible at n=34).
#
# ayr = 32 cores / 78 GB. kink is RAM-light (~6.4 GB peak); 2 GiB/worker spill
# threshold => no spill. Expect ~9h (dalby's 80-core ~3.7h * 80/32 * arch).
# Resume: ayr_a34_verify.sh --resume
set -e
cd ~/src/polyominoes-ns
RUNDIR=runs/ns_a34_ayrverify
mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"
RESUME_FLAG=""
[ "$1" = "--resume" ] && RESUME_FLAG="--resume"

echo "=== a34 ayr cross-ISA verify starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)  host: $(hostname)  arch: $(uname -m)"

T0=$(date +%s)
./build/ns/orchestrate --maxn 34 --kernel kink --counter u128 \
  --cores 32 --ram 2147483648 --unit-mult 4 --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a34 ayr verify run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
[ "$RC" = 0 ] || exit "$RC"

echo "=== combine ==="
./build/ns/combine -in "$RUNDIR/perheight" -maxn 34 -out "$RUNDIR/a_n.txt" 2>&1 | tee "$RUNDIR/combine.log"

echo "=== byte-compare full triangle vs banked results/ns_a34/triangle.txt ==="
if diff <(awk '{print $1,$2}' "$RUNDIR/a_n.txt") <(awk '{print $1,$2}' results/ns_a34/triangle.txt); then
  echo "A34_VERIFY_PASS: ayr (x86) triangle n=1..34 byte-identical to banked dalby (ARM)"
else
  echo "A34_VERIFY_FAIL: MISMATCH between ayr and banked — investigate immediately"
fi
echo "A34_VERIFY_DONE a(34)=$(awk '$1==34{print $2}' "$RUNDIR/a_n.txt")"
