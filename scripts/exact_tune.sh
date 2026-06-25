#!/usr/bin/env bash
# exact_tune.sh [N] [H] -- find the best (THREADS, SHARD_MULT) for the EXACT two-pass on
# this box. The two-pass keeps nthreads*S private dest shards (S = SHARD_MULT*nthreads), so
# high SHARD_MULT at high THREADS thrashes tens of thousands of mostly-empty hash tables
# every column -- overhead-bound. This sweeps LOW->HIGH (cheap configs first) so partial
# results are useful if killed, and caps each run with `timeout` so a bad config can't hang
# the sweep. Metric: wall_s (lower=better) and eff_cores = cpu_s/wall_s (higher=better, <=T).
#
# USAGE (run on the target box): scripts/exact_tune.sh 16 13
set -u
cd "$(dirname "$0")/.."
N=${1:-16}; H=${2:-13}
TLIST="${TLIST:-20 40}"
SMLIST="${SMLIST:-2 4 8 16 32}"
TIMEOUT="${TIMEOUT:-150}"
out="runs/exact_tune/N${N}_H${H}.log"; mkdir -p "$(dirname "$out")"
echo $$ > "runs/exact_tune/tune.pid"

echo "=== exact two-pass tune  N=$N H=$H  $(date -Is)  rev=$(git rev-parse --short HEAD) ===" | tee "$out"
printf "%-4s %-4s %10s %9s %9s %s\n" T SM wall_s cpu_s eff_cores peak_states | tee -a "$out"
for SM in $SMLIST; do
  for T in $TLIST; do
    d=$(timeout "$TIMEOUT" env TMA_SHARD_MULT="$SM" ./build/tma square8 "$N" \
          --only-height "$H" --fold --threads "$T" 2>&1 >/dev/null)
    w=$(echo "$d" | grep -oE "wall_s=[0-9.]+" | cut -d= -f2)
    c=$(echo "$d" | grep -oE "cpu_s=[0-9.]+" | cut -d= -f2)
    ps=$(echo "$d" | grep -oE "peak_states=[0-9]+" | cut -d= -f2)
    if [ -z "$w" ]; then
      printf "%-4s %-4s %10s\n" "$T" "$SM" ">${TIMEOUT}s/err" | tee -a "$out"; continue
    fi
    eff=$(awk -v c="$c" -v w="$w" 'BEGIN{if(w>0)printf "%.1f", c/w; else print "-"}')
    printf "%-4s %-4s %10s %9s %9s %s\n" "$T" "$SM" "$w" "$c" "$eff" "$ps" | tee -a "$out"
  done
done
echo "=== done $(date -Is) ===" | tee -a "$out"
