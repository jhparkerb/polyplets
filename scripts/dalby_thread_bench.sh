#!/usr/bin/env bash
# Thread-scaling benchmark for the holes sweep (sweepSquare8HeightHolesMT).
# Within-height MT is the "weak axis" (sharded per-column parallel-for with per-shard
# mutexes -> contention grows with thread count). This finds the efficiency knee so we
# pick THREADS for the n=19 production run that maximizes total throughput
# (= MAXJOBS x per-height rate), not just raw thread count.
#
# USAGE: dalby_thread_bench.sh H MAXN KMAX "T1 T2 T3 ..."
#   runs `build/tma_holes square8 MAXN --holes --only-height H --kmax KMAX --hdrop
#   --threads T` once per T (fresh, no checkpoint), prints wall_s, peak_rss_mb,
#   speedup vs the first T, and parallel efficiency.
set -uo pipefail
cd "$(dirname "$0")/.."
H="${1:?H}"; MAXN="${2:?MAXN}"; KMAX="${3:?KMAX}"; THREADS="${4:?\"T1 T2 ...\"}"
OUT="runs/threadbench"; mkdir -p "$OUT"
echo ">>> thread-bench H=$H maxn=$MAXN kmax=$KMAX threads=[$THREADS]  $(date -Is)"
base_wall=""
for T in $THREADS; do
  log="$OUT/h${H}_n${MAXN}_t${T}.log"
  build/tma_holes square8 "$MAXN" --holes --only-height "$H" --kmax "$KMAX" --hdrop \
      --threads "$T" > /dev/null 2> "$log"
  w=$(grep -ohE "wall_s=[0-9.]+" "$log" | cut -d= -f2)
  r=$(grep -ohE "peak_rss_mb=[0-9.]+" "$log" | cut -d= -f2)
  [ -z "$base_wall" ] && base_wall="$w" && base_t="$T"
  spd=$(awk -v b="$base_wall" -v w="$w" 'BEGIN{printf "%.2f", b/w}')
  eff=$(awk -v b="$base_wall" -v w="$w" -v bt="$base_t" -v t="$T" 'BEGIN{printf "%.0f%%", 100*(b/w)/(t/bt)}')
  printf "  T=%-3d  wall=%8ss  rss=%8s MB  speedup(vs T=%s)=%-5s  eff=%s\n" \
         "$T" "$w" "$r" "$base_t" "$spd" "$eff"
done
echo ">>> done  $(date -Is)"
