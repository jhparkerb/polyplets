#!/usr/bin/env bash
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
# RESUME: re-run the identical command -- finished heights (h$H.out present) skip,
#   an interrupted height resumes from its fold-guarded checkpoint (DIR/ckpt_h$H).
# KILL:   kill "$(cat runs/aNfold/driver.pid)"; children are checkpointed (one
#   cadence interval lost, not the height).  Never pkill.
set -uo pipefail
cd "$(dirname "$0")/.."

N="${1:?usage: an_fold_parallel.sh N [MAXJOBS] [THREADS] [MIN_FREE_GB]}"
MAXJOBS="${2:-5}"; THREADS="${3:-12}"; MIN_FREE_GB="${4:-25}"
DIR="runs/a${N}fold"; mkdir -p "$DIR"
echo $$ > "$DIR/driver.pid"
log() { echo ">>> $* @ $(date -Is)" | tee -a "$DIR/driver.log"; }

freeGB() { free -g | awk '/^Mem:/{print $7}'; }

log "a($N) FOLDED start: MAXJOBS=$MAXJOBS THREADS=$THREADS MIN_FREE=${MIN_FREE_GB}GB rev=$(git rev-parse --short HEAD)"

# Heaviest heights first (front-load the long pole). h~N is trivial (width 1);
# the memory/compute peak is high-but-not-top H, so descending order is a fine heuristic.
for H in $(seq "$N" -1 1); do
  if [ -s "$DIR/h$H.out" ]; then log "h$H already done, skip"; continue; fi
  # gate on a free slot
  while [ "$(jobs -rp | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
  # gate on free RAM (block until a running stratum frees enough)
  while [ "$(freeGB)" -lt "$MIN_FREE_GB" ] && [ "$(jobs -rp | wc -l)" -gt 0 ]; do wait -n; done
  log "launch h$H (free $(freeGB)GB, $(jobs -rp | wc -l) running)"
  (
    if build/tma square8 "$N" --only-height "$H" --threads "$THREADS" --fold \
         --checkpoint "$DIR/ckpt_h$H" > "$DIR/h$H.out" 2> "$DIR/h$H.log"; then
      log "h$H DONE B_$H($N)=$(awk -v n="$N" '$1==n{print $2}' "$DIR/h$H.out")"
    else
      log "h$H FAILED (see $DIR/h$H.log)"
    fi
  ) &
done
wait

TOT=$(awk -v n="$N" '$1==n{s+=$2} END{printf "%d", s}' "$DIR"/h*.out)
log "ALL HEIGHTS DONE: a($N) = $TOT"
echo "$TOT" > "$DIR/a${N}.value"
