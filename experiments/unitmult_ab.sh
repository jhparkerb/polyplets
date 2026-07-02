#!/bin/bash
# unitmult_ab.sh -- isolated single-height A/B: does --unit-mult 1 recover the
# map straggler tail that --unit-mult 4 leaves on the floor?
#
# Single height, --overlap-heights 1 -> no pool sharing, so per-column
# util = map_cpu/(map_wall*cores) is the TRUE core utilization and the tail is
# real (unlike the a26 overlap trace, where heights share the pool). Steal is
# always allowed (sole occupant). Audit claim (designs/08 Finding 4): at
# unit-mult 4 the pull queue stays full so the stealer nominates a victim only
# ~0.3% as often as ideal; unit-mult 1 drains the queue -> stealing fires.
#
# Usage: ./unitmult_ab.sh <maxn> <height> <cores>
# Run on ayr (idle). Foreground, short. Reports per-run total map-wall + tail util.
set -e
cd ~/src/polyominoes-ns
export PATH=$HOME/go/bin:$PATH
MAXN=${1:-20}; H=${2:-9}; CORES=${3:-32}
BASE=experiments/unitmult_ab/m${MAXN}h${H}
mkdir -p "$BASE"

run() {
  local mult=$1 tag=$2
  local rd="$BASE/$tag"
  mkdir -p "$rd/spill"
  echo "=== run $tag: unit-mult=$mult H=$H maxn=$MAXN cores=$CORES : $(date -Iseconds) ==="
  POLY_UNIT_LOG="$rd/units.log" ./build/ns/orchestrate --maxn "$MAXN" --counter u64 \
    --heights "$H" --overlap-heights 1 --cores "$CORES" --unit-mult "$mult" \
    --steal-grain 0.05 --ram 1073741824 \
    --run-dir "$rd" --spill-dir "$rd/spill" \
    --per-height-out "$rd/perheight" \
    2>&1 | tee "$rd/run.log" | grep -E "event=column" || true
}

run 4 mult4
run 1 mult1

echo ""
echo "=== SUMMARY: total map-wall + steal counts ==="
for tag in mult4 mult1; do
  awk -v t="$tag" -v C="$CORES" '
    /event=column/ {
      for(i=1;i<=NF;i++){split($i,a,"="); if(a[1]=="map_wall_s")mw+=a[2]; if(a[1]=="map_cpu_s")mc+=a[2]}
    }
    END{ printf "%-6s  sum_map_wall=%8.1fs  sum_map_cpu=%9.1fs  avg_util=%.0f%%\n", t, mw, mc, (mw>0?mc/(mw*C)*100:0) }
  ' "$BASE/$tag/run.log"
  s=$(grep -c "event=steal" "$BASE/$tag/run.log" 2>/dev/null || echo 0)
  echo "        steal events logged: $s"
done
