#!/usr/bin/env bash
# Whole-row Redelmeier a(N) via g2 --split on the fleet (dalby, 80 cores).
#
# PURPOSE: independent whole-row confirmation of the polyplet count a(N)=A006770(N)
#   (and, with --per-box, the h-resolved triangle T(N,w,h)). g2 is the standalone
#   Redelmeier enumerator -- a different algorithm from the transfer-matrix engine --
#   so a match is a two-algorithm confirmation. See docs/redelmeier-tall-plan.md sec.5.
#
# Each worker enumerates a deterministic 1/K share of the size>=S subtrees (worker 0
# also counts the size<S nodes); summing all workers elementwise == the unsplit run
# (g2 --split contract, gate-g2 check C). RAM per worker is tiny (~3 MB), so K=80 is
# ~250 MB total -- cores, not RAM, are the constraint.
#
# USAGE:  scripts/g2_wholerow.sh N [S] [K] [--per-box]
#   N         target size (whole row: computes a(1..N))
#   S         split size (default 10; a(S) subtrees round-robined over K workers)
#   K         worker count (default nproc)
#   --per-box emit "n w h count" and combine the full (w,h) histogram
#
# RESULT:   runs/g2row_N<N>[_perbox]/combined.txt   (a(N) is the n==N line[s])
# RESUMABLE: per shard. A worker that finishes writes w<IDX>.done; re-running the
#   same command reuses completed shards and only relaunches missing ones.
# KILL:     kill $(cat runs/g2row_N<N>.../driver.pid)
# COST:     predict from a smaller-N calibration run first (job-checklist item 1);
#   the measured wall/ETA is written to driver.log.
set -uo pipefail
cd "$(dirname "$0")/.."

N="${1:?N}"; S="${2:-10}"; K="${3:-$(nproc)}"
PERBOX=""; TAG=""
for a in "${@:4}"; do [ "$a" = "--per-box" ] && { PERBOX="--per-box"; TAG="_perbox"; }; done

DIR="runs/g2row_N${N}${TAG}"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"
LOG="$DIR/driver.log"
echo ">>> g2 whole-row N=$N S=$S K=$K perbox=${PERBOX:-no} @ $(date +%FT%T%z)" | tee -a "$LOG"
echo ">>> g2 rev: $(build/g2 square8 1 2>&1 | grep -o 'git=[^ ]*' | head -1)" | tee -a "$LOG"
START=$(date +%s)

launched=0
for IDX in $(seq 0 $((K - 1))); do
  if [ -f "$DIR/w$IDX.done" ]; then continue; fi        # resume: skip completed shard
  while [ "$(jobs -rp | wc -l)" -ge "$K" ]; do wait -n; done
  ( build/g2 square8 "$N" $PERBOX --split "$S" "$K" "$IDX" > "$DIR/w$IDX.out" 2> "$DIR/w$IDX.log" \
      && touch "$DIR/w$IDX.done" ) &
  launched=$((launched + 1))
done
wait
WALL=$(( $(date +%s) - START ))
echo ">>> $launched shards ran, ${WALL}s wall; combining @ $(date +%FT%T%z)" | tee -a "$LOG"

# every shard must have completed, or the sum is wrong
missing=0
for IDX in $(seq 0 $((K - 1))); do [ -f "$DIR/w$IDX.done" ] || { echo "!!! shard $IDX INCOMPLETE" | tee -a "$LOG"; missing=1; }; done
[ "$missing" = 1 ] && { echo "!!! re-run to finish missing shards before trusting combined.txt" | tee -a "$LOG"; exit 3; }

python3 - "$DIR" "$PERBOX" > "$DIR/combined.txt" <<'PYEOF'
import sys, glob, os
from collections import defaultdict
d, perbox = sys.argv[1], sys.argv[2]
agg = defaultdict(int)
for f in glob.glob(os.path.join(d, "w*.out")):
    for ln in open(f):
        if ln.startswith("#") or not ln.strip(): continue
        p = ln.split()
        if perbox:                      # "n w h count"
            agg[(int(p[0]), int(p[1]), int(p[2]))] += int(p[3])
        else:                           # "n count"
            agg[(int(p[0]),)] += int(p[1])
for key in sorted(agg):
    print(*key, agg[key])
PYEOF
echo ">>> combined -> $DIR/combined.txt @ $(date +%FT%T%z)" | tee -a "$LOG"
echo ">>> a($N) =" $(awk -v n="$N" '$1==n{s+=$NF} END{print s}' "$DIR/combined.txt") | tee -a "$LOG"
