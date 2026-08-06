#!/bin/bash
# Phase 4a of docs/middle-kingdom-followups-plan.md: the grid-mode min-reduce
# of site perimeter, at the same depth/thread count as the 512 s baseline
# (results/middle-kingdom-grid.md, results/middle-kingdom-phase3.md).
#
# Purpose: measure whether adding the two site-perimeter min-reduce columns
# (minSPKing, minSPRook) moves the grid pass's wall time or peak RSS
# materially away from the 512.1 s / 1.9 MB baseline it was riding on.
#
# Exact command: build/directed_cone_anchor grid 14 8
# Target machine: local laptop (gympie), 8 threads -- well under the 10-perf-
#   core self-imposed cap.
# Predicted cost: ~512 s wall (the baseline), RSS unchanged (O(n^2) bytes/
#   thread, nil) -- the min-reduce is O(size) extra work per animal already
#   being visited, same order as the reachability/convexity checks already
#   in the pass.
# Resume/kill: no checkpointing (matches the existing grid mode -- runs are
#   minutes and restart from scratch). Kill = plain SIGINT/SIGTERM; safe any
#   time, nothing written until the process exits normally.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="results/mk_siteperim_n14.txt"
TIMELOG="results/mk_siteperim_n14.time.txt"
/usr/bin/time -l build/directed_cone_anchor grid 14 8 \
  > "$OUT" 2> "$TIMELOG.tmp"
# obs.h's start/heartbeat/done stream and /usr/bin/time -l's summary are both
# on stderr; split them apart so the timing summary is easy to grep.
grep -v '^event=' "$TIMELOG.tmp" > "$TIMELOG"
grep '^event=' "$TIMELOG.tmp" >> "$OUT.obs.log"
rm -f "$TIMELOG.tmp"
echo "wrote $OUT and $TIMELOG"
