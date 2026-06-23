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
#              peak. With the PER-HEIGHT kmax schedule below, every height's peak is
#              ~10-11 GiB even at n=19, so MAXJOBS=3 ~33 GiB (73% headroom on 125 GiB).
#   THREADS  : threads per height (default 16). Within-height MT is the weak axis;
#              concurrency ACROSS heights (MAXJOBS) is what fills the box.
# RAM bounded by a PER-HEIGHT --kmax schedule: kmax(H) = min(13, (N-H)+2). The state
# row is (maxn+1)*(kmax+1) u64 (sweep8_holes.h), and the TALL heights -- which have
# the most signatures D_H, hence dominate RAM -- can hold almost no holes
# (max_holes(H,n) = n-H, measured exact at n=18: h18->0, h17->1, ...). So the +2-margin
# schedule is EXACT (hdrop drops only unreachable k) yet collapses the heaviest heights
# ~5-7x vs the old flat kmax=13. Global check: sum over (H,n=N,k) == a(N).
# OBSERVABILITY: each height -> runs/holes_nN_ph/
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
  KH=$(( N - H + 2 )); [ "$KH" -gt 13 ] && KH=13; [ "$KH" -lt 2 ] && KH=2
  echo ">>> launch h$H (kmax=$KH)  $(date -Is)"
  ( build/tma_holes square8 "$N" --holes --only-height "$H" --kmax "$KH" --hdrop \
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
