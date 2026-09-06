#!/usr/bin/env bash
# PURPOSE: the k=6 site-perimeter defect census, which tests four live
#   predictions of results/perimeter.md and
#   results/perimeter.md at once:
#     onset(6) = 24                     (the triangular onset law T_k + 3)
#     the Phi_2 leading diagonal's 15/4 (5(k-2)!/2^(k-1) at k=6)
#     the Phi_3 exponent k-4            (today that slope rests on ONE point)
#     Phi_4 absent until k=7            (the "Phi_d first appears at k=2d-1" law)
#
# COMMAND:
#   scripts/dalby_perimeter_defect_k6.sh LATTICE NMAX SHARDS [SPLITS]
#   scripts/dalby_perimeter_defect_k6.sh square8 80 76
#
# TARGET: dalby (80 cores, 125 GB, otherwise idle). RAM is a non-issue -- the
#   n=70 k=5 runs peaked at 2.5 MB and the census array grows like
#   n*k*(k/2)*n, so k=6 at n=80 is a few MB per shard.
#
# WHY SHARDED: --split S K IDX partitions the search deterministically at animal
#   size S; the shards sum elementwise to the unsplit run, which is check D of
#   scripts/perimeter_defect_gate.sh and is the only reason this run's output is
#   worth anything. Unsharded, k=6 to n=80 is ~180 core-hours.
#
# PREDICTED COST (measured on dalby, git=6473890c, single core):
#   king k=6 n=30 = 254 s. For fixed kmax the pruned search visits a
#   POLYNOMIALLY bounded set, and the k=5 series (n=40 51 s, n=60 718 s,
#   n=70 2017 s on gympie) fits time ~ n^7; k=6 should go as ~n^8. That puts
#   king n=80 at ~650000 core-s = 180 core-hours, so ~2.4 h wall on 76 shards.
#   square4 runs about half that. STAGE THIS: n=60 first (~18 core-hours, ~15
#   min) is a cheap decisive test of the DENOMINATOR alone -- dividing the
#   series by the predicted Phi product must leave a polynomial -- and only the
#   n=80 run can fit the closed form, because a period-6 degree-6 fit with two
#   holdouts per class needs 54 points above the onset, i.e. n to 77.
#
# RESUME/KILL: no checkpointing. Shard PIDs are in $OUT.pids; kill them by
#   number. A killed run leaves partial shard files and the merge refuses to
#   run unless every shard reported success.
set -euo pipefail
cd "$(dirname "$0")/.."

LAT=${1:?lattice}
NMAX=${2:?nmax}
SHARDS=${3:?shards}
SPLITS=${4:-8}
KMAX=6

OUT=results/perimdefect_${LAT}_n${NMAX}_k${KMAX}
mkdir -p "$OUT.parts"
rm -f "$OUT.parts"/*.txt "$OUT.pids"

make -s build/perimeter_defect
STAMP=$(./build/perimeter_defect "$LAT" 6 2 2>&1 >/dev/null | grep -o 'git=[^ ]*' || true)
echo "=== $LAT n<=$NMAX k<=$KMAX shards=$SHARDS splitS=$SPLITS $STAMP"
case "$STAMP" in
  *dirty*) echo "REFUSING: binary is stamped dirty; commit first"; exit 1;;
esac

START=$(date +%s)
for ((i = 0; i < SHARDS; i++)); do
  ./build/perimeter_defect "$LAT" "$NMAX" "$KMAX" --split "$SPLITS" "$SHARDS" "$i" \
      > "$OUT.parts/$i.txt" 2> "$OUT.parts/$i.log" &
  echo "$! $i" >> "$OUT.pids"
done
echo "launched $SHARDS shards; pids in $OUT.pids"

rc=0
wait || rc=$?
END=$(date +%s)
echo "all shards done in $((END - START)) s (rc=$rc)"

# Fail closed: every shard must have emitted a done line with result=ok.
ok=$(grep -l "result=ok" "$OUT.parts"/*.log 2>/dev/null | wc -l)
if [ "$ok" -ne "$SHARDS" ]; then
  echo "REFUSING TO MERGE: only $ok/$SHARDS shards reported result=ok"
  exit 1
fi

python3 - "$OUT.parts" "$OUT.txt" "$SHARDS" <<'MERGEPY'
import sys, glob, os
from collections import defaultdict
parts, out, shards = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = sorted(glob.glob(os.path.join(parts, "*.txt")))
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
