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
# The kink real-SIGTERM + resume over-count bug is FIXED (2026-07-09,
# results/kink-resume-sigterm-bug.md: seed contributions are now folded into
# hTri only after a column fully completes, so mid-column checkpoints are
# consistent). This script runs overlap mode, whose height-set resume was
# never affected anyway. Gated by TestKinkResumeMidColumn +
# overlap_resume_test.go. Resume is safe again.
set -e
cd ~/src/polyominoes
N="$1"
[ -n "$N" ] || { echo "usage: dalby_term.sh N [--resume]"; exit 2; }
RUNDIR=runs/ns_a${N}/dalby
mkdir -p "$RUNDIR/spill" runs/ns_a${N}/perheight

RESUME_FLAG=""
[ "$2" = "--resume" ] && RESUME_FLAG="--resume"

# Disk-IO levers (results/fanin-tax.md ladder section), opt-in via
# FRONTIER_LEVERS=1 until a(39) validates them at production scale:
#  - POLY_FRONTIER_ZSTD=1: block-framed zstd on map/merge outputs (~1.85x
#    fewer bytes through the saturated NVMe mirror, measured on a(38) H20).
#  - --fast-map-dir /dev/shm/ns_aN: transient map outputs never touch NVMe
#    (they are ~half of all device reads+writes); per-round headroom check
#    falls back to the run dir automatically.
FASTMAP_FLAG=""
if [ "${FRONTIER_LEVERS:-0}" = "1" ]; then
  export POLY_FRONTIER_ZSTD=1
  # RAM co-budget (the a(40) OOM lesson, 2x): worker spill budgets + tmpfs
  # pages + zstd contexts all share the same 125GB. 40GB floor caps /dev/shm
  # admission at ~22GB; with --ram 768MiB x 80 workers (60GB) + capped pools
  # the sum stays ~90GB, leaving real page-cache headroom.
  export POLY_FASTMAP_FLOOR_GB=${POLY_FASTMAP_FLOOR_GB:-40}
  FASTMAP_FLAG="--fast-map-dir /dev/shm/ns_a${N}"
  echo "frontier levers ON: POLY_FRONTIER_ZSTD=1 $FASTMAP_FLAG floor=${POLY_FASTMAP_FLOOR_GB}GB"
fi

# cost_profile.tsv is append-only (orchestrator/telemetry.go), so a fresh
# (non-resume) run into a reused RUNDIR would silently mix stale rows from
# any earlier run into this run's utilization numbers (bit us once this
# round: a stale a33 cost_profile.tsv from before P13-15 closed-form were
# wired made a genuinely-fixed height look like it was still real-swept --
# docs/utilization-bottleneck-log.md). Resume must NOT touch it (or the
# checkpoint/spill state); only clear it on a fresh start.
[ -z "$RESUME_FLAG" ] && rm -f "$RUNDIR/cost_profile.tsv"

echo "=== a${N} KINK run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

# --persistent-workers: a pool of long-lived --persistent map_worker/
# merge_worker processes fed one request per work item over a pipe, instead
# of a fresh fork+exec per unit (thousands of sub-second spawns per real
# run). Bottleneck #5. Validated real dalby A/B, maxn=30/overlap=15/
# merge-mult=1/GOGC=1000: 282.5s/7755.3 cpu_s -> 265.0s/7155.8 cpu_s --
# 6.2% faster wall, 7.7% fewer CPU-seconds, correct a(30), zero orphaned
# processes after normal exit or a real SIGTERM.
#
# --unit-mult 8: Bottleneck #6 (Kink-Stage Concurrency Collapse). A prior
# "finer unit-mult rejected" finding in memory was from the OLD engine
# (pre-kink-carry, a18/a23), not re-verified against kink -- this session's
# own coarser-unit-mult test (2, rejected) never tested RAISING it either.
# Real dalby A/B, maxn=30: unit-mult=8 gives 215.4s vs unit-mult=4's 265.0s
# (18.7% faster); unit-mult=16 regresses to 252.0s (sweet spot is 8, not
# monotonic). REAL maxn=33 production confirmation: 6798.6s -> 5674.2s
# (16.5% faster), utilization 10.2%->12.4% (the first real-scale
# utilization GAIN this whole round), correct a(33). The best win of the
# whole session, and the first fix that actually moves the H17 dominant
# floor instead of only helping smaller/secondary costs.
# unit-mult=8, merge-mult=1, steal-grain=0.05, persistent-workers, GOGC=1000
# are now the ENGINE DEFAULTS (baked into orchestrate) -- no longer passed
# here. --overlap-heights "$N" (all owned heights) stays: it is run-specific.
# The commentary above records WHY those values were chosen.
# maxn>=40: halve the merge fan-in (unit-mult 4 -> ~320 map outputs/round
# instead of ~640) and trim to 72 cores — the reader-army RSS term scales
# with (workers x inputs) and the third a(40) OOM was exactly that spike
# (see dalby.mem.log + results/fanin-tax.md). ~19% wall cost at maxn=30
# scales smaller at the IO-bound pole; a dead run costs a day.
BIGN_FLAGS=""
[ "$N" -ge 40 ] && BIGN_FLAGS="--unit-mult 4 --cores 72"
T0=$(date +%s)
# --ram 768MiB (was 1GiB): jasonp's RAM-budget rule with the levers' tmpfs
# and zstd terms subtracted — (125*0.8 - shm - pools)/80. Kink is RAM-light;
# the budget is a spill trigger, not a working-set need.
./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
  --cores 80 --ram 805306368 --overlap-heights "$N" $BIGN_FLAGS \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" $FASTMAP_FLAG \
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
