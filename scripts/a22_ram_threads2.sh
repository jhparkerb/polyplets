#!/usr/bin/env bash
# a22_ram_threads2.sh H N -- peak RSS (GB) vs thread count for one sweep, robustly.
# Determines how the per-thread shard-map overhead scales, so we can size the 3 heavy
# H21 primes to fit 2-3 concurrently in 122 GB (the dominant lever on the a(22) job wall).
# Reads VmHWM from /proc after the run (more robust than parsing /usr/bin/time).
# USAGE: scripts/a22_ram_threads2.sh 16 17  2>&1 | tee runs/a22_forecast/ram_threads2.log
set -u
cd "$(dirname "$0")/.."
mkdir -p runs/a22_forecast   # this script writes runs/a22_forecast/.rt_out_$$ directly
H=${1:?}; N=${2:?}; P=2147483647
echo "=== RAM(GB) vs threads  H=$H N=$N  $(date -Is) ==="
echo "threads  peak_rss_GB  wall_s  bytes_per_state(KB)"
for T in 40 24 16 8; do
  t0=$(date +%s)
  TMA_SHARD_MULT=32 ./build/tma square8 "$N" --only-height "$H" --modp $P --fold \
      --threads "$T" >runs/a22_forecast/.rt_out_$$ 2>&1 &
  pid=$!
  hwm=0
  while kill -0 $pid 2>/dev/null; do
    v=$(awk "/VmHWM/{print \$2}" /proc/$pid/status 2>/dev/null)
    [ -n "$v" ] && [ "$v" -gt "$hwm" ] 2>/dev/null && hwm=$v
    sleep 0.5
  done
  wait $pid
  t1=$(date +%s)
  st=$(grep -oE "peak_states=[0-9]+" runs/a22_forecast/.rt_out_$$ | grep -oE "[0-9]+$")
  gb=$(awk "BEGIN{printf \"%.2f\", $hwm/1048576}")
  bps=$(awk "BEGIN{if($st>0)printf \"%.3f\", $hwm/$st; else print \"-\"}")
  printf "%-7s  %9s  %6s  %s\n" "$T" "$gb" "$((t1-t0))" "$bps"
done
rm -f runs/a22_forecast/.rt_out_$$
echo "=== done $(date -Is) ==="
