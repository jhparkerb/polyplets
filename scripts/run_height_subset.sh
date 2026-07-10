#!/bin/bash
# run_height_subset.sh N HEIGHTS CORES RAM -- compute the a(N) contribution of a
# HEIGHTS subset on the kink engine, writing per-height shards for a later
# combine. For multi-machine splits that separate DISKS (each machine's heights
# hit only its own disk -> no cross-machine I/O contention). e.g. a35:
#   dalby: run_height_subset.sh 35 "1-2,19-35" 80 1073741824   # H19 (long pole) + closed forms
#   ayr:   run_height_subset.sh 35 "3-18"       32 1500000000  # the rest
# then gather every machine's perheight/*.out into one dir and:
#   ./build/ns/combine -in <dir> -maxn 35 -out a_n.txt         # errors on a missing shard
# Standard a29-cell-validated kink config. RAM is per-worker spill bytes; keep
# it (total_RAM*margin)/cores (dalby 80c/1GiB, ayr 32c/~1.5GiB).
set -e
cd ~/src/polyominoes
N="${1:?usage: run_height_subset.sh N HEIGHTS CORES RAM}"
HEIGHTS="${2:?need HEIGHTS (e.g. 3-18 or 1-2,19-35)}"
CORES="${3:?need CORES}"
RAM="${4:?need RAM bytes/worker}"
TAG=$(echo "$HEIGHTS" | tr ',-' '__')
RUNDIR="runs/ns_a${N}_split/h${TAG}"
PH="runs/ns_a${N}_split/perheight"
mkdir -p "$RUNDIR/spill" "$PH"

echo "=== a$N heights=$HEIGHTS on $(hostname), cores=$CORES ram=$RAM ==="
echo "rev $(git rev-parse --short HEAD), $(date -Iseconds)"
T0=$(date +%s)
./build/ns/orchestrate --maxn "$N" --heights "$HEIGHTS" --kernel kink --counter u128 \
  --cores "$CORES" --ram "$RAM" --overlap-heights "$N" \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --per-height-out "$PH" --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 300 \
  2>&1 | tee "$RUNDIR/run.log"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "=== a$N heights=$HEIGHTS done rc=$RC wall=$((T1-T0))s : $(date -Iseconds) ==="
[ "$RC" = 0 ] && echo "SHARDS_OK heights=$HEIGHTS in $PH" || echo "SHARDS_FAIL heights=$HEIGHTS rc=$RC"
exit "$RC"
