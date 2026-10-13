#!/bin/bash
# term.sh N -- compute a(N) on the kink kernel, then validate.
#
# Reads its core count from the machine it is on and its repository root from
# its own location.  maxn=N: the wired closed-form diagonals cover
# H(N-2)..H(N-12); the real sweep is H3..H(N-13) (top real height grows +1
# per term).  counter=u128; --ram 1 GiB per worker (kink is RAM-light).
#
# Production settings and the A/B measurements behind them are in
# docs/engine-record.md.  In short: --overlap-heights N sweeps all owned
# heights concurrently in one core pool (overlap = number of swept heights
# owned; overshooting is harmless, and the co-resident RAM for all real-swept
# heights is <100 MB), which took a maxn=30 run from 689.6 s to 378.2 s at
# near-identical CPU-seconds.  unit-mult=8, merge-mult=1, steal-grain=0.05,
# persistent workers and GOGC=1000 are the orchestrator's defaults and are not
# passed here; the reasons for each are in the body comments below.
#
# Resume: term.sh N --resume.  Checkpoints are at height boundaries
# (orchestrator/overlap_resume_test.go), and seed contributions are folded
# into hTri only after a column fully completes, so a mid-column checkpoint is
# consistent (TestKinkResumeMidColumn).  For N >= 40 each phase has its own
# checkpoint and only phases that have started are resumed.
#
# VALIDATE_ONLY=1 [RUNDIR=...] term.sh N runs the post-run validation
# block against an existing $RUNDIR/a_n.txt and exits -- no sweep, no combine,
# so the chain check can be exercised without an N-hour run.
set -e
# Repo root from the script's own location, not a hardcoded path: a fresh
# clone lands wherever the reader put it.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="$1"
[ -n "$N" ] || { echo "usage: term.sh N [--resume]   (or VALIDATE_ONLY=1 term.sh N)"; exit 2; }

# Core count from the box. CORES=n overrides. The measurements quoted in this
# file were taken at 80 cores, so the validated configuration is unchanged on
# that box; elsewhere the run fits the machine instead of oversubscribing it.
CORES=${CORES:-$(nproc 2>/dev/null || sysctl -n hw.ncpu)}
RUNDIR=${RUNDIR:-runs/ns_a${N}}

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
  # RAM co-budget: worker spill budgets + tmpfs pages + zstd contexts all
  # share the same 125GB. Derived from the flags this script actually passes
  # (--ram 1073741824 = 1 GiB):
  #   phase A  --ram 1GiB x 80 workers  = 80GB
  #   phase B  --ram 1GiB x 48 workers  = 48GB
  #   phase C  --ram 1GiB x 32 workers  = 32GB
  # plus tmpfs admission, which the 40GB floor caps at ~85GB free minus the
  # floor, i.e. ~22GB in practice. Phase A is the binding case: 80 + ~22 =
  # ~102GB of the 125GB, leaving ~23GB for page cache, zstd context pools and
  # the orchestrator itself. Phases B/C are far under.
  #
  # Caveat: the floor is enforced against statfs on /dev/shm -- tmpfs
  # headroom -- not against system RAM. The two coincide only while nothing
  # else is resident, so this budget is an arithmetic argument, not something
  # the guard enforces.
  export POLY_FASTMAP_FLOOR_GB=${POLY_FASTMAP_FLOOR_GB:-40}
  FASTMAP_FLAG="--fast-map-dir /dev/shm/ns_a${N}"
  echo "frontier levers ON: POLY_FRONTIER_ZSTD=1 $FASTMAP_FLAG floor=${POLY_FASTMAP_FLOOR_GB}GB"
fi

# cost_profile.tsv is append-only (orchestrator/telemetry.go), so a fresh
# (non-resume) run into a reused RUNDIR would silently mix stale rows from
# any earlier run into this run's utilization numbers (a stale a33
# cost_profile.tsv from before P13-15 were wired once made an injected height
# look real-swept). Resume must not touch it (or the checkpoint/spill state);
# only clear it on a fresh start.
[ -z "$RESUME_FLAG" ] && rm -f "$RUNDIR/cost_profile.tsv" "$RUNDIR/run.log"

echo "=== a${N} KINK run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

# --persistent-workers: a pool of long-lived --persistent map_worker/
# merge_worker processes fed one request per work item over a pipe, instead
# of a fresh fork+exec per unit (thousands of sub-second spawns per real
# run). A/B at maxn=30, overlap=15, merge-mult=1, GOGC=1000: 282.5s/7755.3
# cpu_s -> 265.0s/7155.8 cpu_s, correct a(30), zero orphaned processes after
# normal exit or a SIGTERM.
#
# --merge-mult 1 caps merge fan-out at 1 range/core instead of following
# --unit-mult. Per-merge-range wall barely correlates with record count
# (Pearson r=0.24): most of each ~37ms range is fixed process-spawn overhead.
# A/B at maxn=30, overlap=15: merge-mult=4 377.7s/11670.5 cpu_s vs merge-mult=1
# 305.7s/7291.7 cpu_s, correct a(30) both.
#
# --unit-mult 8: A/B at maxn=30, unit-mult=8 gives 215.4s vs unit-mult=4's
# 265.0s; unit-mult=16 regresses to 252.0s (the optimum is 8, not monotonic).
# Confirmed at maxn=33: 6798.6s -> 5674.2s, utilization 10.2% -> 12.4%,
# correct a(33). An older "finer unit-mult rejected" finding was from the
# column engine and did not carry over to kink.
#
# Those four values plus steal-grain=0.05 are the orchestrator's defaults and
# are not passed here. --overlap-heights "$N" (all owned heights) stays: it is
# run-specific.
#
# banked_value N -- resolve n's previously banked a(n), setting BANK (the
# value, "" if none found) and BANK_SRC (the file it came from).
#
# The banked terms live in several files (n=22,23,24,25 are not under
# results/ns_a{n}/triangle.txt), and a link with no banked value is a failure,
# not a skipped comparison. Sources, in order:
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
# failure, not a printed shrug: the whole point of recomputing the chain
# is that a fresh a(N) run re-derives every earlier term, and a link nobody
# compared is a link nobody checked.
validate_chain() {
  local MISMATCH=0 COVERED=0 LINKS=0 n got known aN aP
  local NB=$(( N < 20 ? N : 20 ))
  echo "=== validate a(1)-a($NB) vs b-file ==="
  for n in $(seq 1 $NB); do
    got=$(awk -v n=$n '$1==n{print $2}' "$RUNDIR/a_n.txt")
    known=$(awk -v n=$n '$1==n{print $2}' fixtures/b006770.txt)
    if [ "$got" = "$known" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (b=$known)"; MISMATCH=1; fi
  done
  # Below N = 22 every earlier term is in the b-file and there is no link here.
  [ "$N" -ge 22 ] && echo "=== validate a(21)-a($((N-1))) vs banked ==="
  for n in $( [ "$N" -ge 22 ] && seq 21 $((N-1)) ); do
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
  [ "$N" -ge 22 ] && echo "chain coverage: $COVERED/$LINKS"

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
# Phased execution for N>=40 (docs/engine-record.md): maxn>=40 with full
# --overlap-heights does not fit 125GB of RAM; worker RSS alone hits 90-120GB
# when the H19+H20+H21 rounds co-reside (four measured OOM kills).
# Single-height phases bound RAM at one height's working set by construction;
# the tall poles are disk-bound (eff_cores ~14) so fewer cores there cost
# little wall. Same mechanism as a two-machine --heights split; perheight
# accumulates across phases; each phase has its own checkpoint (resume reruns
# only the phase that died). N<40: a single all-heights invocation.
#
# PHASE_DIAG_CAP: the diagonal index is k = N - H, and the phase split is
# defined by fixed offsets from N, so each phase's k range is the same for
# every N >= 40:
#   phase A  H = 1..N-21   -> k = 21..N-1  (past the k<=19 fence: real)
#            H = N-18..N   -> k = 0..18    (the injected closed-form tail)
#   phase B  H = N-20      -> k = 20       (past the fence: real)
#   phase C  H = N-19      -> k = 19       (P_19 is wired -- would inject)
# Without the cap, phase C would inject the H=N-19 cell from the very formula
# that cell was fitted to instead of sweeping it, destroying the P_0..P_18
# holdout and the statement that P_19 is used for no banked term. Capping at
# 18 forces phase C back to a real sweep while leaving phase A's k<=18 tail
# untouched. Pinned on all three phases: on A and B it is a no-op today
# (neither owns a k=19 height) and stays correct if the fence or the split
# ever moves.
PHASE_DIAG_CAP=18
run_phase() {  # run_phase LABEL HEIGHTS CORES OVERLAP
  local LABEL=$1 HEIGHTS=$2 CORES=$3 OVERLAP=$4
  # --resume is per-phase: orchestrate --resume exits 1 when the checkpoint
  # file is missing, and a phase that has never started has none (a driver
  # resumed after phase B completed would kill phase C at launch). Resume only
  # phases with a checkpoint; later ones run fresh.
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
  # B/C core counts: 48/32 of 80. Both persistent fleets (map + merge = 2x
  # cores processes) were measured retaining ~1GB+ each; malloc_trim returns
  # freed pages between requests, and the smaller fleets bound the sum even
  # at retained peaks. The poles are disk-bound (eff_cores ~14), so the wall
  # cost is small. Held as the same proportions of whatever CORES is.
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
