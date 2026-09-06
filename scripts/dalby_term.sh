#!/bin/bash
# dalby_term.sh N -- compute a(N) dalby-solo on the kink kernel, then validate.
# Generalizes dalby_a30.sh for the successive-term loop (a31, a32, ...).
# Config = the a29-cell-validated kink config. maxn=N: P9-P12 closed-form
# diagonals cover H(N-2)..H(N-12); real sweep is H3..H(N-13) (top real height
# grows +1 per term). counter=u128. RAM 80c x 1GiB (kink is RAM-light).
#
# --overlap-heights N: sweeps ALL owned heights concurrently in one core pool
# (docs/engine-record.md's own recommendation -- "overlap = number of swept
# heights owned"; overshooting the real count is harmless, RAM co-resident
# for all real-swept heights is <100MB, see docs/engine-record.md
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
# docs/engine-record.md: seed contributions are now folded into
# hTri only after a column fully completes, so mid-column checkpoints are
# consistent). This script runs overlap mode, whose height-set resume was
# never affected anyway. Gated by TestKinkResumeMidColumn +
# overlap_resume_test.go. Resume is safe again.
#
# VALIDATE_ONLY=1 [RUNDIR=...] dalby_term.sh N runs the post-run validation
# block against an existing $RUNDIR/a_n.txt and exits -- no sweep, no combine.
# It exists so the chain check can be exercised without an N-hour run
# (AUDIT-2026-07-30 P4).
set -e
# Repo root from the script's own location, not a hardcoded ~/src/polyominoes:
# a fresh clone lands wherever the reader put it, and the acceptance-queue
# item-2 run found this line was the first thing that broke outside our tree.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="$1"
[ -n "$N" ] || { echo "usage: dalby_term.sh N [--resume]   (or VALIDATE_ONLY=1 dalby_term.sh N)"; exit 2; }

# Core count from the box, not from dalby's 80. CORES=n overrides. Every
# measurement quoted in this header was taken at 80 on dalby, which is what
# nproc returns there, so the validated configuration is unchanged where it was
# validated; elsewhere the run fits the machine instead of oversubscribing it.
CORES=${CORES:-$(nproc 2>/dev/null || sysctl -n hw.ncpu)}
RUNDIR=${RUNDIR:-runs/ns_a${N}/dalby}

RESUME_FLAG=""
[ "$2" = "--resume" ] && RESUME_FLAG="--resume"

# Disk-IO levers (docs/engine-record.md ladder section), opt-in via
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
  # pages + zstd contexts all share the same 125GB. Derived from the flags
  # THIS script actually passes (AUDIT-2026-07-30 E7: the old comment quoted
  # "--ram 768MiB x 80 workers (60GB) ... ~90GB", but the invocations below
  # pass --ram 1073741824 = 1 GiB):
  #   phase A  --ram 1GiB x 80 workers  = 80GB
  #   phase B  --ram 1GiB x 48 workers  = 48GB
  #   phase C  --ram 1GiB x 32 workers  = 32GB
  # plus tmpfs admission, which the 40GB floor caps at ~85GB free minus the
  # floor, i.e. ~22GB in practice. Phase A is the binding case: 80 + ~22 =
  # ~102GB of the 125GB, leaving ~23GB for page cache, zstd context pools and
  # the orchestrator itself. Phases B/C are far under.
  #
  # CAVEAT (AUDIT-2026-07-30 O5, floor redesign DEFERRED): the floor is
  # enforced against statfs on /dev/shm -- tmpfs headroom -- not against
  # system RAM. The two coincide only while nothing else is resident, so this
  # budget is an arithmetic argument, not something the guard enforces.
  export POLY_FASTMAP_FLOOR_GB=${POLY_FASTMAP_FLOOR_GB:-40}
  FASTMAP_FLAG="--fast-map-dir /dev/shm/ns_a${N}"
  echo "frontier levers ON: POLY_FRONTIER_ZSTD=1 $FASTMAP_FLAG floor=${POLY_FASTMAP_FLOOR_GB}GB"
fi

# cost_profile.tsv is append-only (orchestrator/telemetry.go), so a fresh
# (non-resume) run into a reused RUNDIR would silently mix stale rows from
# any earlier run into this run's utilization numbers (bit us once this
# round: a stale a33 cost_profile.tsv from before P13-15 closed-form were
# wired made a genuinely-fixed height look like it was still real-swept --
# docs/engine-record.md). Resume must NOT touch it (or the
# checkpoint/spill state); only clear it on a fresh start.
[ -z "$RESUME_FLAG" ] && rm -f "$RUNDIR/cost_profile.tsv" "$RUNDIR/run.log"

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
# banked_value N -- resolve n's previously banked a(n), setting BANK (the
# value, "" if none found) and BANK_SRC (the file it came from).
#
# AUDIT-2026-07-30 P4 "Ungated Chain": the chain check used to consult ONLY
# results/ns_a{n}/triangle.txt in 2-column form, print "a(n): no banked value"
# and continue -- never counting coverage, never failing. At N=40 it silently
# skipped n=22,23,24,25 (four of the nineteen chain links) even though every
# one of them IS banked, just in a different file. Sources, in order:
#   results/ns_a{n}/a_n.txt              (ns_a23, ns_a24)
#   results/ns_a{n}/triangle.txt         (2-column form: a21, a26..a39)
#   results/redelmeier_row{n}/combined.txt  (n=22, no ns_a22 dir exists)
#   results/b006770_upload.txt           (the banked A006770 chain; the only
#                                         source for n=25, whose run banked a
#                                         provenance triangle, not a row file)
# Only the plain "n a(n)" 2-column form is read: the detailed n/H/T(n,H)
# triangles would need a bigint row-sum, and awk's $3+=... silently loses
# precision past ~16 digits (confirmed: a23 comes out ...768 instead of the
# correct ...732). A file in any other shape is skipped, not mis-summed.
banked_value() {
  local n=$1 f
  BANK=""; BANK_SRC=""
  for f in "results/ns_a${n}/a_n.txt" \
           "results/ns_a${n}/triangle.txt" \
           "results/redelmeier_row${n}/combined.txt" \
           "results/b006770_upload.txt"; do
    [ -f "$f" ] || continue
    [ "$(awk '/^[[:space:]]*#/{next} NF{print NF; exit}' "$f")" = "2" ] || continue
    BANK=$(awk -v n="$n" '$1==n{print $2; exit}' "$f")
    if [ -n "$BANK" ]; then BANK_SRC=$f; return 0; fi
  done
  return 0
}

# validate_chain compares this run's a_n.txt against the b-file (n<=20) and
# every banked term (21..N-1), then reports coverage. An uncovered link is a
# FAILURE now, not a printed shrug: the whole point of recomputing the chain
# is that a fresh a(N) run re-derives every earlier term, and a link nobody
# compared is a link nobody checked.
validate_chain() {
  local MISMATCH=0 COVERED=0 LINKS=0 n got known aN aP
  echo "=== validate a(1)-a(20) vs b-file ==="
  for n in $(seq 1 20); do
    got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
    known=$(awk -v n=$n '$1==n{print $2}' fixtures/b006770.txt)
    if [ "$got" = "$known" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (b=$known)"; MISMATCH=1; fi
  done
  echo "=== validate a(21)-a($((N-1))) vs banked ==="
  for n in $(seq 21 $((N-1))); do
    LINKS=$((LINKS+1))
    got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
    banked_value "$n"
    if [ -z "$BANK" ]; then
      echo "a($n): NO BANKED VALUE FOUND -- chain link UNCHECKED"
      MISMATCH=1
      continue
    fi
    COVERED=$((COVERED+1))
    if [ "$got" = "$BANK" ]; then
      echo "a($n)=$got OK [$BANK_SRC]"
    else
      echo "a($n)=$got MISMATCH (banked=$BANK from $BANK_SRC)"
      MISMATCH=1
    fi
  done
  echo "chain coverage: $COVERED/$LINKS"

  aN=$(awk -v n=$N '$1==n{print $2}' "$RUNDIR/a_n.txt")
  aP=$(awk -v n=$((N-1)) '$1==n{print $2}' "$RUNDIR/a_n.txt")
  echo "a($N) = $aN"
  python3 -c "print('growth a${N}/a$((N-1)) =', $aN/$aP)"
  if [ "$MISMATCH" = 0 ]; then echo "A${N}_VALIDATE_PASS"; else echo "A${N}_VALIDATE_FAIL"; fi
  echo "A${N}_DONE"
  return "$MISMATCH"
}

if [ "${VALIDATE_ONLY:-0}" = "1" ]; then
  validate_chain
  exit
fi

mkdir -p "$RUNDIR/spill" runs/ns_a${N}/perheight
T0=$(date +%s)
# PHASED EXECUTION for N>=40 (Overcommit Hydra, docs/engine-record.md):
# maxn>=40 with full --overlap-heights does NOT fit dalby's 125GB — worker
# RSS alone hits 90-120GB when H19+H20+H21 rounds co-reside (four measured
# OOM kills 2026-07-25). Single-height phases bound RAM at ONE height's
# working set by construction; the tall poles are disk-bound (eff_cores ~14)
# so fewer cores there cost little wall. Same mechanism as the a(36)
# ayr/dalby --heights split; perheight accumulates across phases; each phase
# has its own checkpoint (resume reruns only the phase that died).
# N<40: the classic single all-heights invocation, unchanged.
#
# PHASE_DIAG_CAP (AUDIT-2026-07-30 D1 "Phase C Phantom"): the diagonal index
# is k = N - H, and the phase split is defined by fixed offsets from N, so
# each phase's k range is the same for every N >= 40:
#   phase A  H = 1..N-21   -> k = 21..N-1  (past the k<=19 fence: real)
#            H = N-18..N   -> k = 0..18    (the INJECTED closed-form tail)
#   phase B  H = N-20      -> k = 20       (past the fence: real)
#   phase C  H = N-19      -> k = 19       (P_19 is wired -- would INJECT)
# With P_19 wired and the fence at k<=19, phase C stopped performing the real
# H=N-19 sweep and injected it from the very formula that cell was fitted to:
# a re-run silently destroys the P_0..P_18 mass holdout, the project's
# strongest validation artifact, and falsifies the shipped "P_19 is used for
# no banked term" claims. Capping at 18 forces phase C back to a real sweep
# while leaving phase A's k<=18 tail untouched. Pinned on ALL THREE phases:
# on A and B it is a no-op today (neither owns a k=19 height) and stays
# correct if the fence or the split ever moves.
PHASE_DIAG_CAP=18
run_phase() {  # run_phase LABEL HEIGHTS CORES OVERLAP
  local LABEL=$1 HEIGHTS=$2 CORES=$3 OVERLAP=$4
  # --resume is per-phase: orchestrate --resume exits 1 when the checkpoint
  # file is missing, and a phase that has never started has none — a driver
  # resumed after phase B completed killed phase C at launch (a(40),
  # 2026-07-26). Resume only phases with a checkpoint; later ones run fresh.
  local PHASE_RESUME=$RESUME_FLAG
  [ -f "$RUNDIR/POLYCKPT.$LABEL" ] || PHASE_RESUME=""
  echo "=== phase $LABEL: heights=$HEIGHTS cores=$CORES resume=${PHASE_RESUME:-no} $(date -Iseconds) ==="
  ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
    --cores "$CORES" --ram 1073741824 --overlap-heights "$OVERLAP" \
    --heights "$HEIGHTS" --max-diag-k "$PHASE_DIAG_CAP" \
    --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" $FASTMAP_FLAG \
    --checkpoint "$RUNDIR/POLYCKPT.$LABEL" --checkpoint-every 300 $PHASE_RESUME \
    --per-height-out runs/ns_a${N}/perheight \
    --cost-profile-out "$RUNDIR/cost_profile.tsv" \
    2>&1 | tee -a "$RUNDIR/run.log"
  return "${PIPESTATUS[0]}"
}
if [ "$N" -ge 40 ]; then
  RC=0
  # B/C core counts: 48/32 (were 64/48). The 5th OOM measured BOTH
  # persistent fleets (map + merge = 2x cores processes) retaining ~1GB+
  # each; malloc_trim now returns freed pages between requests, and the
  # smaller fleets bound the sum even at retained peaks. The poles are
  # disk-bound (eff_cores ~14), so the wall cost is small.
  # 80/48/32 on dalby, held as the same proportions of whatever CORES is.
  run_phase A "1-$((N-21)),$((N-18))-$N" "$CORES" "$N" && \
  run_phase B "$((N-20))" "$(( CORES * 6 / 10 ))" 1 && \
  run_phase C "$((N-19))" "$(( CORES * 4 / 10 ))" 1 || RC=$?
else
  ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
    --cores "$CORES" --ram 1073741824 --overlap-heights "$N" \
    --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" $FASTMAP_FLAG \
    --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
    --per-height-out runs/ns_a${N}/perheight \
    --cost-profile-out "$RUNDIR/cost_profile.tsv" \
    2>&1 | tee "$RUNDIR/run.log"
  RC=${PIPESTATUS[0]}
fi
T1=$(date +%s)
echo "=== a${N} run exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="
[ "$RC" = 0 ] || exit "$RC"

echo "=== combine ==="
./build/ns/combine -in runs/ns_a${N}/perheight -maxn "$N" -out "$RUNDIR/a_n.txt" 2>&1 | tee "$RUNDIR/combine.log"

validate_chain
