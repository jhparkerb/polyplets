#!/usr/bin/env bash
# a22_ram_threads.sh H N -- peak RSS vs thread count for one sweep, to size the heavy
# primes so 2-3 of them fit dalby's RAM concurrently (the 3-prime schedule lever).
# The MT shard structure loc[nthreads][S] adds per-thread overhead; fewer threads -> less
# RAM but ~same speed (per-sweep parallelism caps ~6x). USAGE: a22_ram_threads.sh 16 17
set -u
cd "$(dirname "$0")/.."
H=${1:?}; N=${2:?}; P=2147483647
echo "=== RAM vs threads  H=$H N=$N  $(date -Is) ==="
echo "threads  peak_rss_GB  wall_s  result"
for T in 40 20 12 6; do
  out=$(TMA_SHARD_MULT=32 /usr/bin/time -v ./build/tma square8 $N --only-height $H \
        --modp $P --fold --threads $T 2>&1)
  rss=$(echo "$out" | grep -oE "Maximum resident set size \(kbytes\): [0-9]+" | grep -oE "[0-9]+$")
  ela=$(echo "$out" | grep -oE "Elapsed .*: [0-9:.]+" | grep -oE "[0-9:.]+$")
  res=$(echo "$out" | grep -oE "result=[0-9]+")
  printf "%-7s  %6.1f       %7s  %s\n" "$T" "$(awk "BEGIN{print $rss/1048576}")" "$ela" "$res"
done
echo "=== done $(date -Is) ==="
