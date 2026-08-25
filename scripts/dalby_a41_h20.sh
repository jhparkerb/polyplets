#!/bin/bash
# a(41), the H = 20 pole: the real sweep of height 20 at maxn = 41.
#
# Why run it at all when Undertow covers H >= 20 from the tower: because a
# swept T(41,20) is a genuine HOLDOUT for P_21.  P_21 is pinned from
# T(40,19) and T(39,18) and predicts T(41,20) through the depth-2 identity;
# nothing else on its diagonal can check it, since every in-onset cell of
# level 21 needs n >= 43.  With this run a(41) also stops depending on P_21
# at all -- the tower only has to reach k = 20, which is pinned three ways.
#
# Target machine: dalby, 76 cores, 125 GB RAM.  Run ALONE: the a(40) phase
# profile has H<=19 peaking at 69 GB of disk and H=20 at 172 GB at maxn=40.
# At maxn=41, on the MEASURED Nmax scaling below (~1.08x for 40->41, not the
# ~2.6x an earlier version of this paragraph assumed), those become roughly
# 75 GB and 185-190 GB.  They still run phased -- a(40) did, and there is no
# reason to change that -- but the reason is caution, not arithmetic.
# Predicted cost -- CORRECTED 2026-08-20 after the Nmax-scaling measurement,
# and after Lane B of the review called the earlier figure out as ASSERTED:
# a(40)'s H20-solo phase was 9.6 h on 48 cores with a 172 GB disk peak at
# maxn=40 (results/ns_a40/rundir_size.log, 2026-07-26 11:00 = 172,314 MB).
# Fixed-height cost in Nmax is MEASURED at 1.442x/1.466x for 40->45
# (scripts/nmax_scaling.sh, heights 14 and 15, CPU-seconds), i.e. ~1.08x for
# 40->41.  So: ~10-11 h on 48 cores and ~185-190 GB, NOT the 20-30 h and
# ~450 GB this comment asserted before anything was measured.
# Read the orchestrator's own per-column profile, not this comment.
# Resume: dalby_a41_h20.sh --resume    Kill: kill the orchestrate PID.
set -e
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNDIR=runs/a41_h20
mkdir -p "$RUNDIR/spill" "$RUNDIR/perheight"
RESUME_FLAG=""
[ "$1" = "--resume" ] && [ -f "$RUNDIR/POLYCKPT" ] && RESUME_FLAG="--resume"
export POLY_FRONTIER_ZSTD=1
export POLY_FASTMAP_FLOOR_GB=${POLY_FASTMAP_FLOOR_GB:-40}
echo "=== a41 H20 sweep: $(date -Iseconds) rev=$(git rev-parse --short HEAD) resume=${RESUME_FLAG:-no} ==="
./build/ns/orchestrate --maxn 41 --kernel kink --counter u128 \
  --cores 76 --ram 1073741824 --overlap-heights 1 \
  --heights 20 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 $RESUME_FLAG \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  2>&1 | tee -a "$RUNDIR/run.log"
echo "=== a41 H20 done: $(date -Iseconds) rc=${PIPESTATUS[0]} ==="
