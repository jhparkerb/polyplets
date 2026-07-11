#!/usr/bin/env bash
# Central combine for a fleet whole-row g2 run (dalby + ayr + gympie).
#
# Each box runs scripts/g2_wholerow.sh with a disjoint --range and --no-combine,
# so every shard IDX in [0,K) is computed exactly once across the fleet (split-sum
# invariance, gate-g2 check C). Gather every box's w*.out AND w*.done into one DIR,
# then this script verifies all K shards are present and sums them.
#
# USAGE:  scripts/g2_combine.sh DIR N K [--per-box]
#   DIR        directory holding the gathered w<IDX>.out / w<IDX>.done from all boxes
#   N          target size (a(N) is read off the n==N line[s])
#   K          shard count of the split (all of 0..K-1 must be present)
#   --per-box  inputs are "n w h count"; combine the full (w,h) histogram
#
# RESULT:  DIR/combined.txt  (+ prints a(N)). Exits non-zero if any shard missing.
set -uo pipefail
cd "$(dirname "$0")/.."

DIR="${1:?DIR}"; N="${2:?N}"; K="${3:?K}"; PERBOX=""
[ "${4:-}" = "--per-box" ] && PERBOX="--per-box"
LOG="$DIR/combine.log"

# completeness: every shard 0..K-1 must have landed (a missing shard silently
# undercounts, which would look like a real mismatch -- fail loudly instead)
missing=0
for IDX in $(seq 0 $((K - 1))); do
  [ -f "$DIR/w$IDX.done" ] || { echo "!!! shard $IDX MISSING (no w$IDX.done)" | tee -a "$LOG"; missing=1; }
done
[ "$missing" = 1 ] && { echo "!!! gather all boxes' shards before combining" | tee -a "$LOG"; exit 3; }

python3 - "$DIR" "$PERBOX" > "$DIR/combined.txt" <<'PYEOF'
import sys, glob, os
from collections import defaultdict
d, perbox = sys.argv[1], sys.argv[2]
agg = defaultdict(int)
for f in glob.glob(os.path.join(d, "w*.out")):
    for ln in open(f):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.split()
        if perbox:                       # "n w h count"
            agg[(int(p[0]), int(p[1]), int(p[2]))] += int(p[3])
        else:                            # "n count"
            agg[(int(p[0]),)] += int(p[1])
for key in sorted(agg):
    print(*key, agg[key])
PYEOF

echo ">>> combined $K shards -> $DIR/combined.txt @ $(date +%FT%T%z)" | tee -a "$LOG"
echo ">>> a($N) =" $(awk -v n="$N" '$1==n{s+=$NF} END{print s}' "$DIR/combined.txt") | tee -a "$LOG"
