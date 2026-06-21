#!/usr/bin/env bash
# a(20) REMAINING heights, per-height PARALLEL on ayr (gcc/x86). The sequential
# a20_remaining.sh ran heights one-at-a-time, each memory-bound to ~6 of 32 cores ->
# 26 cores idle, projecting multi-day. This runs heights 15,16,17,18,20 CONCURRENTLY
# (RAM-budgeted to 78 GB), reusing h15's existing checkpoint (~5 h of progress).
# Heights 1-14 already complete (runs/a20/h*.out) and are skipped.
#
# USAGE: a20_remaining_parallel.sh [MAXJOBS] [THREADS] [HEIGHTS]
#   MAXJOBS  : concurrent heights (default 4). RAM = sum of concurrent heights' peaks;
#              est for n=20: h18~33-50, h17~15, h16~6, h15~3, h20~0 GB (from h19=60GB/
#              23.9M states ~ 2.5 KB/state). 4 heaviest ~57-74 GB < 78 -> MONITOR RSS,
#              drop to 3 if it heads past ~72 GB (no swap).
#   THREADS  : per height (default 8). Within-height is memory-bound to ~6 cores, so
#              concurrency ACROSS heights fills the box; 4 x ~6 ~= 24 of 32 cores.
# OBSERVABILITY: each height -> runs/a20/h<H>.{out,log} (start/heartbeat/done+ETA);
#   driver echoes height events. RESUME: re-run; done heights skip, in-progress resume
#   via --checkpoint (h15 reuses runs/a20/ckpt_h15). Heaviest-first so h18 isn't last.
set -uo pipefail
cd "$(dirname "$0")/.."
MAXJOBS="${1:-4}"; THREADS="${2:-8}"; HEIGHTS="${3:-18 17 16 15 20}"
mkdir -p runs/a20
echo $$ > runs/a20/parallel.pid
echo ">>> a(20) per-height parallel: [$HEIGHTS] MAXJOBS=$MAXJOBS THREADS=$THREADS pid=$$  $(date -Is)"
for H in $HEIGHTS; do
  if [ -s "runs/a20/h$H.out" ]; then echo ">>> h$H already complete, skip"; continue; fi
  while [ "$(jobs -rp | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
  echo ">>> launch h$H  $(date -Is)"
  ( build/tma square8 20 --only-height "$H" --threads "$THREADS" \
        --checkpoint "runs/a20/ckpt_h$H" > "runs/a20/h$H.out" 2> "runs/a20/h$H.log" \
    && echo ">>> h$H DONE: $(awk '$1==20{print $2}' runs/a20/h$H.out)  $(date -Is)" \
    || echo ">>> h$H FAILED rc=$?  $(date -Is)" ) &
done
wait
echo ">>> all remaining heights done  $(date -Is)"
echo ">>> next: assemble Sum_H byHeight[H][20] (H=1..20) and diff vs 1,025,573,519,362,016"
