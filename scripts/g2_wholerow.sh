#!/usr/bin/env bash
# Whole-row Redelmeier a(N) via g2 --split on the fleet (dalby, 80 cores).
#
# PURPOSE: independent whole-row confirmation of the polyplet count a(N)=A006770(N)
#   (and, with --per-box, the h-resolved triangle T(N,w,h)). g2 is the standalone
#   Redelmeier enumerator -- a different algorithm from the transfer-matrix engine --
#   so a match is a two-algorithm confirmation. See docs/redelmeier-tall-plan.md (deleted) sec.5.
#
# Each worker enumerates a deterministic 1/K share of the size>=S subtrees (worker 0
# also counts the size<S nodes); summing all workers elementwise == the unsplit run
# (g2 --split contract, gate-g2 check C). RAM per worker is tiny (~3 MB), so K=80 is
# ~250 MB total -- cores, not RAM, are the constraint.
#
# USAGE:  scripts/g2_wholerow.sh N [S] [K] [JOBS] [--per-box]
#   N         target size (whole row: computes a(1..N))
#   S         split size (default 10; a(S) subtrees round-robined over K shards)
#   K         shard count (default nproc). Oversplit K > cores for finer resume and
#             a wave-by-wave progress signal (each shard is 1/K of the work).
#   JOBS      max concurrent shards (default nproc) -- the actual core load
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

N="${1:?N}"; S="${2:-10}"; K="${3:-$(nproc)}"; JOBS="${4:-$(nproc)}"
case "$JOBS" in ''|*[!0-9]*) JOBS="$(nproc)";; esac   # if arg 4 was a flag, fall back
# Flags (any order after the positionals):
#   --per-box            emit "n w h count", combine the full (w,h) histogram
#   --range FROM TO      run only shards [FROM,TO) of the K split (fleet: give each
#                        box a disjoint IDX range of the SAME N/S/K; split-sum
#                        invariance makes the union exact regardless of which box
#                        ran which shard). Default 0..K.
#   --no-combine         run the shards but skip combine/verify (fleet: combine
#                        centrally after gathering every box's w*.out; see
#                        scripts/g2_combine.sh).
PERBOX=""; TAG=""; NOCOMBINE=0; FROM=0; TO="$K"
args=("$@"); i=0
while [ $i -lt ${#args[@]} ]; do
  case "${args[$i]}" in
    --per-box)    PERBOX="--per-box"; TAG="_perbox";;
    --no-combine) NOCOMBINE=1;;
    --range)      FROM="${args[$((i+1))]}"; TO="${args[$((i+2))]}"; i=$((i+2));;
  esac
  i=$((i+1))
done
RANGE=$((TO - FROM))

DIR="runs/g2row_N${N}${TAG}"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"
LOG="$DIR/driver.log"
echo ">>> g2 whole-row N=$N S=$S K=$K range=[$FROM,$TO) jobs=$JOBS perbox=${PERBOX:-no} host=$(hostname -s) @ $(date +%FT%T%z)" | tee -a "$LOG"
echo ">>> g2 rev: $(build/g2 square8 1 2>&1 | grep -o 'git=[^ ]*' | head -1)" | tee -a "$LOG"
START=$(date +%s)

# Background ETA monitor: shards are near-uniform work, so done-count over elapsed
# gives a real rate and a real eta (memory: surface-job-etas, no elapsed-only guesses).
( while :; do
    sleep 120
    D=$(ls "$DIR"/w*.done 2>/dev/null | wc -l | tr -d ' ')
    E=$(( $(date +%s) - START )); [ "$D" -gt 0 ] || continue
    ETA=$(awk -v d="$D" -v e="$E" -v r="$RANGE" 'BEGIN{printf "%d", (r-d)*e/d}')
    echo ">>> progress=$D/$RANGE elapsed=${E}s eta=${ETA}s @ $(date +%FT%T%z)" | tee -a "$LOG"
  done ) &
MONPID=$!

launched=0
for IDX in $(seq "$FROM" $((TO - 1))); do
  if [ -f "$DIR/w$IDX.done" ]; then continue; fi        # resume: skip completed shard
  while [ "$(jobs -rp | wc -l)" -ge "$((JOBS + 1))" ]; do wait -n; done   # +1 for the monitor
  ( build/g2 square8 "$N" $PERBOX --split "$S" "$K" "$IDX" > "$DIR/w$IDX.out" 2> "$DIR/w$IDX.log" \
      && touch "$DIR/w$IDX.done" ) &
  launched=$((launched + 1))
done
while [ "$(jobs -rp | wc -l)" -gt 1 ]; do wait -n; done   # all shards done (monitor still up)
kill "$MONPID" 2>/dev/null; wait "$MONPID" 2>/dev/null
WALL=$(( $(date +%s) - START ))
echo ">>> $launched shards ran, ${WALL}s wall @ $(date +%FT%T%z)" | tee -a "$LOG"

# every shard in this box's range must have completed, or its partial sum is wrong
missing=0
for IDX in $(seq "$FROM" $((TO - 1))); do [ -f "$DIR/w$IDX.done" ] || { echo "!!! shard $IDX INCOMPLETE" | tee -a "$LOG"; missing=1; }; done
[ "$missing" = 1 ] && { echo "!!! re-run to finish missing shards" | tee -a "$LOG"; exit 3; }

if [ "$NOCOMBINE" = 1 ]; then
  echo ">>> range [$FROM,$TO) complete; --no-combine (combine centrally with scripts/g2_combine.sh) @ $(date +%FT%T%z)" | tee -a "$LOG"
  exit 0
fi
echo ">>> combining @ $(date +%FT%T%z)" | tee -a "$LOG"

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
