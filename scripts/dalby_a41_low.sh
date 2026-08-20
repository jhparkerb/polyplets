#!/bin/bash
# a(41), the cheap half: real sweep of heights 1..19 at maxn=41.
#
# Why only 19: Undertow (experiments/undertow_pin.py, VERIFY GREEN on 18
# levels) pins P_20 and P_21 from BELOW-onset cells that are already banked,
# so the tower covers k <= 21, i.e. every T(41,H) with H >= 20.  The old rule
# needed onset anchors and so needed the H = 20 and H = 21 poles -- 9.6 h/48c
# and 36.4 h/32c with a 363 GB disk peak on the a(40) run.  This run replaces
# both.
#
# Target machine: dalby, 40 of 80 cores (the family-table job has the rest),
# 125 GB RAM, 563 GB free disk.
# Predicted cost: UNMEASURED at maxn=41 -- that is partly what this run is.
# Anchor: a(40) phase A (H1-19 + the H22-40 injections, 80 cores) was 6.3 h
# with rss_max 827 MB and a small disk footprint; per-term growth on the pole
# column is ~4.4x, less at fixed height.  Expect single-digit hours to ~2 days
# on 40 cores, RAM ~1 GB, disk well under 100 GB.  The orchestrator prints a
# live ETA from its own cost profile -- read that, do not trust this comment.
# Resume: dalby_a41_low.sh --resume     Kill: kill the orchestrate PID.
set -e
cd ~/src/polyominoes
RUNDIR=runs/a41_low
mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"
RESUME_FLAG=""
[ "$1" = "--resume" ] && [ -f "$RUNDIR/POLYCKPT" ] && RESUME_FLAG="--resume"
export POLY_FRONTIER_ZSTD=1
echo "=== a41 low sweep: $(date -Iseconds) rev=$(git rev-parse --short HEAD) resume=${RESUME_FLAG:-no} ==="
./build/ns/orchestrate --maxn 41 --kernel kink --counter u128 \
  --cores 40 --ram 1073741824 --overlap-heights 19 \
  --heights 1-19 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee -a "$RUNDIR/run.log"
echo "=== a41 low sweep done: $(date -Iseconds) rc=${PIPESTATUS[0]} ==="
