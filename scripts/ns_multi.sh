#!/usr/bin/env bash
# ns_multi.sh — concurrent multi-instance --heights experiment on one box.
#
# Tests the across-height load-balancing idea: launch several orchestrate
# instances, each over a disjoint height subset, sharing the box, to soak up the
# cores left idle by within-column starvation. It also answers the thundering-
# herd question directly: run the SAME heights one-instance vs split-across-N and
# compare batch wall. Faster split => idle cores genuinely filled (parallelism-
# limited, the idea works). Same/slower => bandwidth-bound herd (idle cores were
# a mirage). The aggregate effective-cores number (sum cpu_s / batch wall) shows
# how full the box actually got.
#
# Each instance is independent (a(n)=Σ_H T(n,H)); they share --per-height-out so
# a final combine validates correctness when the subsets cover 1..N.
#
# Usage: ns_multi.sh N RAMW_GB ROOT spec1 [spec2 ...]
#   spec = "HEIGHTS:CORES", e.g.
#     ns_multi.sh 18 1 runs/ns_multi/split 7-10:40 11-14:40   # middle split 2x40
#     ns_multi.sh 18 1 runs/ns_multi/solo  7-14:80            # same heights, 1x80
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="${1:?usage: ns_multi.sh N RAMW_GB ROOT spec...}"
RAMW_GB="${2:?ram per worker GB}"
ROOT="${3:?run root}"
shift 3
[ "$#" -ge 1 ] || { echo "need at least one HEIGHTS:CORES spec"; exit 2; }
RAM=$(awk "BEGIN{printf \"%d\", $RAMW_GB * 1024 * 1024 * 1024}")  # GB (fractional ok, e.g. 0.5 for oversubscription)

rm -rf "$ROOT"; mkdir -p "$ROOT/perheight"
REV="$(git -C "$REPO" rev-parse --short HEAD)"
LOG="$ROOT/multi.log"
echo "ns_multi rev=$REV host=$(hostname -s) N=$N ram_per_worker_gb=$RAMW_GB instances=$# start=$(date -Is)" | tee "$LOG"

pids=(); labels=()
i=0
for spec in "$@"; do
  H="${spec%%:*}"; C="${spec##*:}"
  d="$ROOT/inst${i}"; mkdir -p "$d/spill"
  echo "launch inst$i heights=$H cores=$C" | tee -a "$LOG"
  "$REPO/build/ns/orchestrate" --maxn "$N" --heights "$H" --cores "$C" \
    --unit-mult "${MULT:-4}" --ram "$RAM" \
    --run-dir "$d" --spill-dir "$d/spill" --per-height-out "$ROOT/perheight" \
    --checkpoint "$d/CK" --checkpoint-every 300 --cost-profile-out "$d/profile.tsv" \
    > "$d/run.log" 2>&1 &
  pids+=($!); labels+=("inst$i:$H@$C")
  i=$((i+1))
done

t0=$(date +%s)
fail=0
for j in "${!pids[@]}"; do
  if wait "${pids[$j]}"; then echo "${labels[$j]} done" | tee -a "$LOG"
  else echo "${labels[$j]} FAILED (exit $?)" | tee -a "$LOG"; fail=1; fi
done
t1=$(date +%s)
batch=$(( t1 - t0 ))

echo "=== batch_wall_s=$batch ===" | tee -a "$LOG"
# Aggregate cpu across all instances; effective cores = total cpu / batch wall.
# (Per-instance map/merge split lives in each inst*/run.log event=column lines.)
awk -F'\t' -v bw="$batch" '!/^#/{c+=$6}
  END{if(bw>0) printf "aggregate sum_cpu_s=%.0f  eff_cores=%.1f/80\n", c, c/bw}' \
  "$ROOT"/inst*/profile.tsv 2>/dev/null | tee -a "$LOG"

# Correctness when the subsets cover 1..N.
echo "=== combine (correctness if covered) ===" | tee -a "$LOG"
"$REPO/build/ns/combine" --in "$ROOT/perheight" --maxn "$N" --compare 2>&1 | tail -3 | tee -a "$LOG"
echo "ns_multi done=$(date -Is) fail=$fail" | tee -a "$LOG"
exit "$fail"
