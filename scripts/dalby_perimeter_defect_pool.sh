#!/usr/bin/env bash
# PURPOSE: same k=6 census as scripts/dalby_perimeter_defect_k6.sh, but with the
#   straggler tail engineered out. That script launched exactly one shard per
#   core; measured on dalby at n=60, 74 of 76 shards finished in ~15 min and the
#   last two ran past 45, so the wall was 3x the ideal. The subtrees are wildly
#   uneven -- a low-defect animal at the split size carries a subtree that
#   reaches n=NMAX, a high-defect one dies almost immediately -- and one shard
#   per core means one fat subtree sets the wall.
#
#   Two changes: split DEEPER (so the fat subtrees are themselves cut up) and
#   ask for many more shards than cores, fed through a worker pool. A straggler
#   then delays only its own shard, and the pool keeps every core busy.
#
# COMMAND:
#   scripts/dalby_perimeter_defect_pool.sh LATTICE NMAX KMAX SHARDS PARALLEL [SPLITS]
#   scripts/dalby_perimeter_defect_pool.sh square8 78 6 456 76 14
#
# TARGET: dalby (80 cores, 125 GB). PARALLEL <= 76 leaves headroom.
#
# COST OF SPLITTING DEEPER: every shard re-walks the whole prefix (all nodes of
#   size < SPLITS) to keep its counter in step with the others. That prefix is
#   the k<=6 animals below SPLITS cells, ~1e7 nodes at SPLITS=14, i.e. a couple
#   of seconds per shard -- 456 shards x ~2 s is ~15 core-minutes against a
#   ~165 core-hour job, under 0.2%. Splitting deeper is close to free; leaving
#   the tail in place is not.
#
# PREDICTED COST (measured on dalby, git=6473890c, single core, k=6):
#   n=30 254 s, n=34 692 s, n=38 1666 s -> time ~ n^7.9. So king n=78 is
#   ~490000 core-s = ~136 core-hours = ~1.8 h wall at 76-way, plus whatever
#   tail survives. square4 runs about half that. RAM is a few MB per shard.
#
# RESUME/KILL: no checkpointing. Kill the pool by killing this script's PID;
#   shard files already written are kept but the merge will refuse to run
#   unless every shard reported result=ok, so a partial run cannot be mistaken
#   for a complete one.
set -euo pipefail
cd "$(dirname "$0")/.."

LAT=${1:?lattice}
NMAX=${2:?nmax}
KMAX=${3:?kmax}
SHARDS=${4:?shards}
PARALLEL=${5:?parallel}
SPLITS=${6:-14}

OUT=results/perimdefect_${LAT}_n${NMAX}_k${KMAX}
mkdir -p "$OUT.parts"
rm -f "$OUT.parts"/*.txt "$OUT.parts"/*.log

make -s build/perimeter_defect
STAMP=$(./build/perimeter_defect "$LAT" 6 2 2>&1 >/dev/null | grep -o 'git=[^ ]*' || true)
echo "=== $LAT n<=$NMAX k<=$KMAX shards=$SHARDS parallel=$PARALLEL splitS=$SPLITS $STAMP"
case "$STAMP" in
  *dirty*) echo "REFUSING: binary is stamped dirty; commit first"; exit 1;;
esac

START=$(date +%s)
seq 0 $((SHARDS - 1)) | xargs -P "$PARALLEL" -I{} \
  sh -c "./build/perimeter_defect $LAT $NMAX $KMAX --split $SPLITS $SHARDS {} \
         > $OUT.parts/{}.txt 2> $OUT.parts/{}.log"
END=$(date +%s)
echo "pool drained in $((END - START)) s"

ok=$(grep -l "result=ok" "$OUT.parts"/*.log 2>/dev/null | wc -l)
if [ "$ok" -ne "$SHARDS" ]; then
  echo "REFUSING TO MERGE: only $ok/$SHARDS shards reported result=ok"
  exit 1
fi

python3 - "$OUT.parts" "$OUT.txt" "$SHARDS" <<'MERGEPY'
import sys, glob, os
from collections import defaultdict
parts, out, shards = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = glob.glob(os.path.join(parts, "*.txt"))
if len(files) != shards:
    sys.exit("expected %d shard files, found %d" % (shards, len(files)))
t = defaultdict(int)
for f in files:
    for line in open(f):
        w = line.split()
        if not w or not w[0].isdigit():
            continue
        t[tuple(int(x) for x in w[:-1])] += int(w[-1])
with open(out, "w") as fh:
    for k in sorted(t):
        fh.write(" ".join(str(x) for x in k) + " %d\n" % t[k])
print("merged %d shards -> %s (%d cells, %d animals)"
      % (shards, out, len(t), sum(t.values())))
MERGEPY

echo "DONE $OUT.txt"
