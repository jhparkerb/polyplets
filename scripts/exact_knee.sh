#!/usr/bin/env bash
# exact_knee.sh N H -- find the THREADS knee for a pole-class (heavy) height. eff is a
# steady-state RATE, so each config runs only CAP seconds (it need NOT finish): pick a height
# heavy enough that every config is still in column 1 at the cap, then read the last
# heartbeat's states/s. Highest rate = most useful parallelism. SM fixed at 32 (tune-best).
# Emits per config so partials survive a kill. USAGE (on the box): scripts/exact_knee.sh 20 19
set -u
cd "$(dirname "$0")/.."
N=${1:?}; H=${2:?}
TLIST="${TLIST:-13 20 26 40 52 64}"
CAP="${CAP:-100}"
out="runs/exact_knee/N${N}_H${H}.log"; mkdir -p "$(dirname "$out")"
echo $$ > runs/exact_knee/knee.pid

echo "=== exact threads-knee  N=$N H=$H SM=32 cap=${CAP}s  $(date -Is)  rev=$(git rev-parse --short HEAD) ===" | tee "$out"
printf "%-4s %12s %6s   %s\n" T "rate_st/s" "col" "(last heartbeat)" | tee -a "$out"
for T in $TLIST; do
  d=$(timeout "$CAP" env TMA_SHARD_MULT=32 TMA_PROGRESS=1 TMA_PROGRESS_SECS=25 \
        ./build/tma square8 "$N" --only-height "$H" --fold --threads "$T" 2>&1 >/dev/null)
  last=$(echo "$d" | grep "PROGRESS" | tail -1)
  rate=$(echo "$last" | grep -oE "rate=[0-9]+" | cut -d= -f2)
  col=$(echo "$last" | grep -oE "col=[0-9]+" | cut -d= -f2)
  printf "%-4s %12s %6s   %s\n" "$T" "${rate:-?}" "${col:-?}" "${last:-<no heartbeat in ${CAP}s>}" | tee -a "$out"
done
echo "=== done $(date -Is) ===" | tee -a "$out"
