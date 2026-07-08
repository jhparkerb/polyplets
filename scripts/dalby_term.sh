#!/bin/bash
# dalby_term.sh N -- compute a(N) dalby-solo on the kink kernel, then validate.
# Generalizes dalby_a30.sh for the successive-term loop (a31, a32, ...).
# Config = the a29-cell-validated kink config. maxn=N: P9-P12 closed-form
# diagonals cover H(N-2)..H(N-12); real sweep is H3..H(N-13) (top real height
# grows +1 per term). counter=u128. RAM 80c x 1GiB (kink is RAM-light).
#
# --overlap-heights N: sweeps ALL owned heights concurrently in one core pool
# (results/scheduling.md's own recommendation -- "overlap = number of swept
# heights owned"; overshooting the real count is harmless, RAM co-resident
# for all real-swept heights is <100MB, see docs/utilization-bottleneck-log.md
# Bottleneck #1). Validated real dalby maxn=30 A/B on identical code+range
# (H3-H15 real sweep): overlap=1 689.6s/21.6% util vs overlap=15 378.2s/38.8%
# util, near-identical CPU-seconds (11926.6 vs 11742.2), byte-identical
# a(30)=227969227118066423789154 both configs. Checkpoints at height
# boundaries (gated: orchestrator/overlap_resume_test.go), not per-column.
#
# --merge-mult 1: caps merge fan-out at 1 range/core (80) instead of
# following --unit-mult (320). Per-merge-range wall_s barely correlates with
# record count (Pearson r=0.24 on real data) -- most of each ~37ms range is
# fixed process-spawn overhead, not proportional work (Bottleneck #2).
# Validated real dalby A/B, maxn=30/overlap=15, identical code: merge-mult=4
# (implicit default) 377.7s wall/11670.5 cpu_s vs merge-mult=1 305.7s
# wall/7291.7 cpu_s -- 19% faster wall, 37% less total CPU-seconds, correct
# a(30) both. (Utilization ratio itself dips slightly, 38.6%->29.8%: fewer
# concurrent ranges fill the pool less densely even though there's less
# total waste -- a real net win on wall-clock and CPU-seconds, not a
# regression despite the lower ratio.)
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
  --cores 80 --ram 1073741824 --unit-mult 4 --merge-mult 1 --steal-grain 0.05 \
  --overlap-heights "$N" \
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
  bank=""
  # Not every n has its own results/ns_a{n}/ dir (e.g. a22 has none). And a
  # few (ns_a23, ns_a24) store the detailed n/H/T(n,H) triangle instead of
  # the plain "n a(n)" format -- summing that safely needs bigint (awk's
  # $3+=... silently loses precision past ~16 digits, confirmed: a23 comes
  # out ...768 instead of the correct ...732), so only trust the plain
  # 2-column format here; anything else skips gracefully rather than risk a
  # false MISMATCH from a precision-lossy sum, or `set -e` tripping on a
  # missing file.
  if [ -f "results/ns_a${n}/triangle.txt" ] && [ "$(awk 'NR==1{print NF; exit}' "results/ns_a${n}/triangle.txt")" = "2" ]; then
    bank=$(awk -v n=$n '$1==n{print $2}' "results/ns_a${n}/triangle.txt")
  fi
  [ -z "$bank" ] && { echo "a($n): no banked value"; continue; }
  if [ "$got" = "$bank" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (banked=$bank)"; MISMATCH=1; fi
done

aN=$(awk -v n=$N '$1==n{print $2}' "$RUNDIR/a_n.txt")
aP=$(awk -v n=$((N-1)) '$1==n{print $2}' "$RUNDIR/a_n.txt")
echo "a($N) = $aN"
python3 -c "print('growth a${N}/a$((N-1)) =', $aN/$aP)"
if [ "$MISMATCH" = 0 ]; then echo "A${N}_VALIDATE_PASS"; else echo "A${N}_VALIDATE_FAIL"; fi
echo "A${N}_DONE"
