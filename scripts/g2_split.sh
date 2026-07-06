#!/usr/bin/env bash
# Parallel g2 --split runner + combine, for the big statistics sweeps (dalby, 80 cores).
# Each worker enumerates a deterministic 1/K share of the size>=S subtrees (worker 0 also
# does the size<S nodes); the outputs combine by SUM (count distributions) or MAX (maxhole).
#
# USAGE:  scripts/g2_split.sh N FLAG COMBINE [S] [K]
#   FLAG     a g2 stat flag, e.g. --maxhole-strat | --contacts | --holes
#   COMBINE  sum  -> "n key count" lines, summed per (n,key)
#            max  -> "n v1 v2 ..." lines, elementwise max per n
# Result lands in runs/gsplit_<flag>_N<N>/combined.txt . Resumable-ish: re-run re-does all.
set -uo pipefail
cd "$(dirname "$0")/.."
N="${1:?N}"; FLAG="${2:?FLAG e.g. --maxhole-strat}"; COMBINE="${3:?sum|max}"
S="${4:-10}"; K="${5:-$(nproc)}"
DIR="runs/gsplit_$(echo "$FLAG" | tr -dc 'a-z')_N$N"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"
echo ">>> g2 $FLAG N=$N split S=$S K=$K combine=$COMBINE @ $(date -Is)" | tee "$DIR/driver.log"

for IDX in $(seq 0 $((K - 1))); do
  while [ "$(jobs -rp | wc -l)" -ge "$K" ]; do wait -n; done
  build/g2 square8 "$N" "$FLAG" --split "$S" "$K" "$IDX" > "$DIR/w$IDX.out" 2> "$DIR/w$IDX.log" &
done
wait
echo ">>> $K workers done, combining @ $(date -Is)" | tee -a "$DIR/driver.log"

python3 - "$DIR" "$COMBINE" > "$DIR/combined.txt" <<'PYEOF'
import sys, glob, os
from collections import defaultdict
d, combine = sys.argv[1], sys.argv[2]
files = glob.glob(os.path.join(d, "w*.out"))
if combine == "sum":
    agg = defaultdict(int)
    for f in files:
        for ln in open(f):
            if ln.startswith("#"): continue
            p = ln.split()
            if len(p) == 3:
                agg[(int(p[0]), int(p[1]))] += int(p[2])
    for n, k in sorted(agg):
        print(n, k, agg[(n, k)])
else:  # max (elementwise, variable column count)
    agg = {}
    for f in files:
        for ln in open(f):
            if ln.startswith("#") or not ln.strip():
                continue
            p = list(map(int, ln.split()))
            n, vals = p[0], p[1:]
            cur = agg.get(n, [])
            agg[n] = [max(cur[i] if i < len(cur) else 0, vals[i] if i < len(vals) else 0)
                      for i in range(max(len(cur), len(vals)))]
    for n in sorted(agg):
        print(n, *agg[n])
PYEOF
echo ">>> combined -> $DIR/combined.txt @ $(date -Is)" | tee -a "$DIR/driver.log"
head -40 "$DIR/combined.txt"
