#!/usr/bin/env bash
# exact_mt_scaling.sh [N] [H] [THREADS...] -- exact-vs-modp MT scaling for one strip height.
#
# DECIDES a pre-a(21)-launch question: the exact u64 MT path (sweep8.h) takes a
# lock_guard<mutex> per state-insert and ignores TMA_SHARD_MULT, whereas the modp path
# (sweep8_modp.h) is the lock-free two-pass that bought 3.16x on gympie. The a(21) launch
# uses the EXACT folded path. If it scales to T=20 as well as modp does, the mutex is NOT
# the bottleneck (enumeration is) and no port is needed. If exact plateaus below modp, the
# gap is the wall-time the two-pass port would buy on a(21).
#
# Both engines run the SAME height, folded, so the comparison is apples-to-apples. Times
# externally (date) because the modp path's own wall_s field is unreliable. Prints wall_s
# and speedup-vs-T1 per (engine, threads); reads VmHWM peak too where /proc exists.
#
# USAGE (run on ayr/dalby, where high T is meaningful): scripts/exact_mt_scaling.sh 17 13
set -u
cd "$(dirname "$0")/.."
N=${1:-17}; H=${2:-13}; shift 2 2>/dev/null || true
THREADS="${*:-1 12 20}"
P=2147483647
out="runs/exact_mt_scaling/N${N}_H${H}.log"; mkdir -p "$(dirname "$out")"

echo "=== exact-vs-modp MT scaling  N=$N H=$H  rev=$(git rev-parse --short HEAD)  $(date -Is) ===" | tee "$out"
printf "%-7s %-4s %9s %7s %9s\n" engine T wall_s spdup peakRSS_MB | tee -a "$out"

run_one() {  # engine T extra-flags...
  local eng=$1 T=$2; shift 2
  ./build/tma square8 "$N" --only-height "$H" --fold --threads "$T" "$@" \
      >"$out.tmp" 2>&1 &
  local pid=$! hwm=0 v
  while kill -0 "$pid" 2>/dev/null; do
    v=$(awk '/VmHWM/{print $2}' /proc/$pid/status 2>/dev/null)
    [ -n "$v" ] && [ "$v" -gt "$hwm" ] 2>/dev/null && hwm=$v
    sleep 0.5
  done
  wait "$pid"
  awk -v rss="$hwm" 'BEGIN{printf "%.1f", rss/1024}'
}

for eng in exact modp; do
  flags=(); [ "$eng" = modp ] && flags=(--modp "$P")
  base=""
  for T in $THREADS; do
    t0=$(date +%s.%N)
    rss=$(run_one "$eng" "$T" "${flags[@]}")
    t1=$(date +%s.%N)
    w=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.1f", b-a}')
    [ -z "$base" ] && base=$w
    sp=$(awk -v base="$base" -v w="$w" 'BEGIN{printf "%.2f", base/w}')
    printf "%-7s %-4s %9s %7s %9s\n" "$eng" "$T" "$w" "$sp" "$rss" | tee -a "$out"
  done
done
rm -f "$out.tmp"
echo "=== done $(date -Is) ===" | tee -a "$out"
