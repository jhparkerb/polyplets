#!/usr/bin/env bash
# Per-height PARALLEL holes distribution on dalby -- fills the 80-core box, unlike the
# all-heights sweep (`square8 N --holes`) which runs heights serially at ~3 cores
# because the within-height MT doesn't scale across the whole machine. Here each height
# is a separate `--holes --only-height H` process; running several concurrently is what
# uses the cores. Then sum the per-height (height,n,#holes,count) outputs into the
# (n,#holes,count) distribution. clang/ARM here = cross-ISA companion to ayr gcc/x86.
#
# USAGE: dalby_holes_perheight.sh N [MAXJOBS] [THREADS]
#   N        : max size (18, 19)
#   MAXJOBS  : concurrent heights (default 3). RAM = up to MAXJOBS x heaviest-height
#              peak; keep under 125 GiB with NO swap. Heaviest single height (kmax13
#              hdrop) est ~15-35 GB for n=18 -> 3 concurrent ~45-105 GB. START LOW,
#              measure real RSS from the heartbeats, then bump MAXJOBS if headroom.
#   THREADS  : threads per height (default 16). Within-height MT is the weak axis;
#              concurrency ACROSS heights (MAXJOBS) is what fills the box.
# RAM bounded by --kmax 13 --hdrop. OBSERVABILITY: each height -> runs/holes_nN_ph/
#   h<H>.{out,log} with start/heartbeat/done+ETA+peak_rss; driver echoes height events.
# RESUME: re-run; finished heights (non-empty hH.out) skip; in-progress resume via
#   each height's --checkpoint. Safe to bump MAXJOBS and re-run.
set -uo pipefail
cd "$(dirname "$0")/.."
N="${1:?usage: dalby_holes_perheight.sh N [MAXJOBS] [THREADS]}"
MAXJOBS="${2:-3}"; THREADS="${3:-16}"
OUT="runs/holes_n${N}_ph"; mkdir -p "$OUT"
echo $$ > "$OUT/driver.pid"   # for a reliable completion waiter (avoids pgrep transients)
echo ">>> per-height holes N=$N MAXJOBS=$MAXJOBS THREADS=$THREADS pid=$$  $(date -Is)"
for H in $(seq "$N" -1 1); do
  if [ -s "$OUT/h$H.out" ]; then echo ">>> h$H already complete, skip"; continue; fi
  while [ "$(jobs -rp | wc -l)" -ge "$MAXJOBS" ]; do wait -n; done
  echo ">>> launch h$H  $(date -Is)"
  ( build/tma_holes square8 "$N" --holes --only-height "$H" --kmax 13 --hdrop \
        --threads "$THREADS" --checkpoint "$OUT/ckpt_h$H" \
        > "$OUT/h$H.out" 2> "$OUT/h$H.log" \
    && echo ">>> h$H DONE  $(date -Is)" \
    || echo ">>> h$H FAILED rc=$?  $(date -Is)" ) &
done
wait
echo ">>> all heights done; combining -> results/holes_n${N}.dalby.txt  $(date -Is)"
# per-height lines are "H n k count"; sum count grouped by (n,k) -> "n k count"
cat "$OUT"/h*.out | awk 'NF==4{c[$2" "$3]+=$4} END{for(key in c) print key, c[key]}' \
  | sort -n -k1,1 -k2,2 > "results/holes_n${N}.dalby.txt"
echo ">>> wrote results/holes_n${N}.dalby.txt ($(wc -l < "results/holes_n${N}.dalby.txt") rows)  $(date -Is)"
