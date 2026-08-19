#!/bin/bash
# dalby_two_media_cal.sh N TOPH -- calibrate the two-media plan
# (docs/a35-two-media-plan.md) at scale N. Runs the tallest real height TOPH on
# /dev/shm concurrently with the other real heights (H3..TOPH-1) on the NVMe
# mirror, both --cores 80 (oversubscribed; the OS co-schedules the CPU-bound
# tmpfs job A against the I/O-bound NVMe job B). Measures the TOTAL wall-clock
# vs the single-run baseline, samples the co-schedule (cpu/iowait), and
# validates every produced height byte-identical to results/ns_a{N}/perheight.
#
# Purpose: pin the real two-media wall and confirm oversubscription works,
# before committing to the a(35) config + a root tmpfs mount. a34 fits /dev/shm
# for the tall height (~40 GB); a(35)'s tall height would need a bigger (root)
# tmpfs -- this a34 run is the no-root proxy.
#
# COST: ~ one Job-B wall (the non-tall real heights), ~30-70 min at N=34.
# Not a keeper -- a calibration, logged under runs/ns_a{N}_2media/.
#
# RUN:  scripts/dalby_two_media_cal.sh 34 18
# KILL: kill the two orchestrate PIDs (jobA.log/jobB.log name them); rm -rf /dev/shm/a{N}_2mA
set -e
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="${1:?usage: dalby_two_media_cal.sh N TOPH}"
TOPH="${2:?need TOPH (tallest real-swept height)}"
LOG="runs/ns_a${N}_2media"
A_SHM="/dev/shm/a${N}_2mA"
rm -rf "$A_SHM" "$LOG/nvme"
mkdir -p "$LOG/perheight" "$A_SHM/spill" "$LOG/nvme/spill"
rm -f "$LOG/perheight"/*.out

echo "=== two-media cal a($N): tall H$TOPH on tmpfs + H3-$((TOPH-1)) on NVMe, $(date -Iseconds) ===" | tee "$LOG/summary.txt"
T0=$(date +%s)

./build/ns/orchestrate --maxn "$N" --heights "$TOPH" --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --run-dir "$A_SHM" --spill-dir "$A_SHM/spill" \
  --per-height-out "$LOG/perheight" --cost-profile-out "$LOG/costA.tsv" \
  > "$LOG/jobA.log" 2>&1 &
PA=$!

./build/ns/orchestrate --maxn "$N" --heights "3-$((TOPH-1))" --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --overlap-heights "$TOPH" --run-dir "$LOG/nvme" --spill-dir "$LOG/nvme/spill" \
  --per-height-out "$LOG/perheight" --cost-profile-out "$LOG/costB.tsv" \
  > "$LOG/jobB.log" 2>&1 &
PB=$!
echo "Job A (H$TOPH tmpfs) pid=$PA ; Job B (H3-$((TOPH-1)) nvme) pid=$PB" | tee -a "$LOG/summary.txt"

# Sample the co-schedule: us sy id wa (vmstat fields 13-16).
( while kill -0 "$PA" 2>/dev/null || kill -0 "$PB" 2>/dev/null; do
    LC_ALL=C vmstat 1 2 | tail -1 | awk '{print $13,$14,$15,$16}'; sleep 15
  done ) > "$LOG/vmstat.log" 2>&1 &
VS=$!

# Report which job finishes first (the co-schedule limiter).
wait "$PA"; RA=$?; TA=$(( $(date +%s) - T0 )); echo "Job A done at ${TA}s rc=$RA" | tee -a "$LOG/summary.txt"
wait "$PB"; RB=$?; TB=$(( $(date +%s) - T0 )); echo "Job B done at ${TB}s rc=$RB" | tee -a "$LOG/summary.txt"
kill "$VS" 2>/dev/null || true
T1=$(date +%s)
rm -rf "$A_SHM"

echo "=== TWO-MEDIA a$N total wall=$((T1-T0))s vs single-run baseline ~13300s ===" | tee -a "$LOG/summary.txt"

echo "--- per-height correctness vs banked ---" | tee -a "$LOG/summary.txt"
ok=1
for h in $(seq 3 "$TOPH"); do
  f="$LOG/perheight/h$h.out"; b="results/ns_a${N}/perheight/h$h.out"
  if [ -f "$f" ] && [ -f "$b" ]; then
    diff -q "$f" "$b" >/dev/null 2>&1 && echo "h$h PASS" || { echo "h$h DIFFERS"; ok=0; }
  else
    echo "h$h MISSING (produced=$([ -f "$f" ]&&echo y||echo n) banked=$([ -f "$b" ]&&echo y||echo n))"; ok=0
  fi
done | tee -a "$LOG/summary.txt"
[ "$ok" = 1 ] && echo "TWO_MEDIA_CORRECT PASS" | tee -a "$LOG/summary.txt" || echo "TWO_MEDIA_CORRECT FAIL" | tee -a "$LOG/summary.txt"

awk '{us+=$1;sy+=$2;id+=$3;wa+=$4;n++} END{if(n)printf "mean cpu over run: user=%.0f%% sys=%.0f%% idle=%.0f%% iowait=%.0f%%\n",us/n,sy/n,id/n,wa/n}' "$LOG/vmstat.log" | tee -a "$LOG/summary.txt"
echo "TWO_MEDIA_CAL_DONE" | tee -a "$LOG/summary.txt"
