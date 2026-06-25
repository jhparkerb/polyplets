#!/usr/bin/env bash
# TODO(simplify): shares its per-height launch / slot-gate / resume / combine-awk
# skeleton with scripts/dalby_holes_perheight.sh and an_modp_crt.sh; the genuinely-new
# bit is the RAM-floor gate. Could be one parameterized driver (engine + flags + combine).
# Per-height PARALLEL a(N), R1-FOLDED.  Computes B_H(N) for every strip height H
# with the vertical-mirror state fold (--fold: ~2x less RAM and ~2x faster, gated
# folded==unfolded), checkpointed per height.  a(N) = sum_H B_H(N).
#
# TARGET: dalby (122 GB, 80 cores).  PREDICTED COST (checklist item 1):
#   per-state ~580 B (measured: 237846528 B / 409624 states, incl. double-buffer);
#   heaviest folded stratum ~17 GB (a20 h19 23.9M states x2.42/2 x580B); MAXJOBS
#   concurrent peaks well under the MIN_FREE guard.  Wall ~ longest height, <1 day.
# BUDGET FIT (item 2): MAXJOBS caps concurrency AND a free-RAM floor (MIN_FREE_GB)
#   blocks a launch until a stratum frees memory -- so the sum of live peaks cannot
#   drive the box into swap even if a per-height peak exceeds the estimate.
#
# USAGE:  scripts/an_fold_parallel.sh N [MAXJOBS] [THREADS] [MIN_FREE_GB]
#   Keep MAXJOBS*THREADS <= physical cores (oversubscription is a net loss here), and
#   AVOID power-of-2 THREADS (8/16/32 measure ~2x slower than 12/20 on this DP -- the
#   documented thread anomaly). Recommended:
#     dalby (80c): MAXJOBS=4 THREADS=20     ayr (32c): MAXJOBS=2 THREADS=14  (or 1x20 for a pole)
# SPLIT across machines: set HEIGHTS to a subset so two boxes share the heights with no
#   overlap, e.g. ayr runs the light tail and dalby the heavy heads, in parallel:
#     ayr:   HEIGHTS="$(seq 13 -1 1)"  scripts/an_fold_parallel.sh 21 2 14
#     dalby: HEIGHTS="$(seq 21 -1 14)" scripts/an_fold_parallel.sh 21 4 20
#   Each box writes per-height DIR/h$H.out (the source of truth) and a DIR/a$N.partial
#   subtotal over ITS heights. Final a(N) = sum of all h*.out across both run dirs (the
#   per-height outs simply concatenate; combine by rsync'ing both DIRs together and
#   awk-summing column 2 at row n=N). A full (unset HEIGHTS) run writes DIR/a$N.value.
# RESUME: re-run the identical command -- finished heights (h$H.out present) skip,
#   an interrupted height resumes from its fold-guarded checkpoint (DIR/ckpt_h$H).
# KILL:   kill "$(cat runs/aNfold/driver.pid)"; children are checkpointed (one
#   cadence interval lost, not the height).  Never pkill.
set -uo pipefail
cd "$(dirname "$0")/.."

N="${1:?usage: an_fold_parallel.sh N [MAXJOBS] [THREADS] [MIN_FREE_GB]}"
MAXJOBS="${2:-4}"; THREADS="${3:-20}"; MIN_FREE_GB="${4:-25}"
# HEIGHTS: which strip heights this box computes (default all, heaviest first). Override to
# a subset to split the work across machines without overlap. See header.
HEIGHTS="${HEIGHTS:-$(seq "$N" -1 1)}"
DIR="runs/a${N}fold"; mkdir -p "$DIR"
echo $$ > "$DIR/driver.pid"
log() { echo ">>> $* @ $(date -Is)" | tee -a "$DIR/driver.log"; }

freeGB() { free -g | awk '/^Mem:/{print $7}'; }

# Interleave allocations across NUMA nodes when there's more than one (ayr is 4-node:
# first-touch roulette otherwise costs throughput). Single-node boxes (dalby) get no prefix.
NUMA=""
if [ -z "${NO_NUMA:-}" ] && command -v numactl >/dev/null 2>&1 &&
   [ "$(numactl --hardware 2>/dev/null | awk '/^available:/{print $2}')" -gt 1 ] 2>/dev/null; then
  NUMA="numactl --interleave=all"
fi

log "a($N) FOLDED start: MAXJOBS=$MAXJOBS THREADS=$THREADS MIN_FREE=${MIN_FREE_GB}GB ${NUMA:+NUMA-interleave }heights=[$(echo $HEIGHTS | tr '\n' ' ')] rev=$(git rev-parse --short HEAD)"

# Heaviest heights first (front-load the long pole). h~N is trivial (width 1);
# the memory/compute peak is high-but-not-top H, so descending order is a fine heuristic.
for H in $HEIGHTS; do
  if [ -s "$DIR/h$H.out" ]; then log "h$H already done, skip"; continue; fi
  # gate on a free slot
  while [ "$(jobs -rp | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
  # gate on free RAM (block until a running stratum frees enough)
  while [ "$(freeGB)" -lt "$MIN_FREE_GB" ] && [ "$(jobs -rp | wc -l)" -gt 0 ]; do wait -n; done
  log "launch h$H (free $(freeGB)GB, $(jobs -rp | wc -l) running)"
  (
    if $NUMA build/tma square8 "$N" --only-height "$H" --threads "$THREADS" --fold \
         --checkpoint "$DIR/ckpt_h$H" > "$DIR/h$H.out" 2> "$DIR/h$H.log"; then
      log "h$H DONE B_$H($N)=$(awk -v n="$N" '$1==n{print $2}' "$DIR/h$H.out")"
    else
      log "h$H FAILED (see $DIR/h$H.log)"
    fi
  ) &
done
wait

# Subtotal over the h*.out THIS box produced. For a full run that's a(N); for a split run
# it's a partial that must be added to the other box's partial(s) for the true a(N).
TOT=$(awk -v n="$N" '$1==n{s+=$2} END{printf "%d", s}' "$DIR"/h*.out)
if [ "$(echo $HEIGHTS | wc -w)" -eq "$N" ]; then
  log "ALL HEIGHTS DONE: a($N) = $TOT"
  echo "$TOT" > "$DIR/a${N}.value"
else
  log "SUBTOTAL over heights [$(echo $HEIGHTS | tr '\n' ' ')]: $TOT  (PARTIAL -- add other boxes' partials for a($N))"
  echo "$TOT" > "$DIR/a${N}.partial"
fi
