#!/bin/bash
# dalby_tmpfs_probe.sh N [SECS] -- BOUNDED tmpfs-vs-NVMe probe at disk-bound
# scale. Does NOT finish the job: it runs maxn=N for a fixed window on each of
# NVMe and /dev/shm, samples iowait + progress, then SIGTERMs and compares.
# Purpose: learn whether putting the intermediate run-dir on tmpfs relieves the
# disk-write wait that shows up at a34/a35 scale (60-69% iowait on the md3 NVMe
# mirror during a(35)) -- and stop the moment we know it does or doesn't.
#
# WHY N=34: a(35)'s run-dir (>58 GB) won't fit /dev/shm (63 GB); a(34)'s peaks
# ~30 GB and DOES fit, and is (expected) disk-bound -- the largest scale we can
# test on the no-root tmpfs. If a34 turns out NOT to be disk-bound in the
# window, that itself is the answer: the disk wait is an a35-only regime and
# tmpfs can't be tested for it without a bigger (root) tmpfs.
#
# METRIC: each arm runs SECS seconds (default 1500 = 25 min), enough to enter
# the disk-bound regime if a34 has one. We compare, over the identical window:
#   - mean iowait (whole + last third): is the NVMe arm disk-bound at all?
#   - columns completed (rows in cost_profile.tsv): throughput. Same
#     deterministic column order both arms, so more-columns-in-same-wall = faster.
# tmpfs "works" iff the NVMe arm is disk-bound (high iowait) AND the tmpfs arm
# both drops iowait to ~0 AND completes more columns in the same window.
#
# TARGET: dalby. COST: 2 x SECS (~50 min default) + teardown. a34 run-dir peak
# ~30 GB fits /dev/shm; a guard aborts the tmpfs arm if the NVMe arm's measured
# peak would risk filling it. Not a keeper -- a tuning probe, logged under
# runs/ns_a${N}_tmpfsprobe/. Recoverable: each arm is independent + SIGTERMed.
#
# RUN:  scripts/dalby_tmpfs_probe.sh 34
# KILL: kill the orchestrate PID; rm -rf /dev/shm/ns_a${N}_tmpfsprobe
set -e
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N="${1:?usage: dalby_tmpfs_probe.sh N [SECS]}"
SECS="${2:-1500}"
LOG="runs/ns_a${N}_tmpfsprobe"
NVME="$LOG/nvme_rundir"
SHM="/dev/shm/ns_a${N}_tmpfsprobe"
mkdir -p "$LOG"

# vmstat 'wa' is field 16 (r b swpd free buff cache si so bi bo in cs us sy id wa st ...).
arm() {
  local label="$1" rundir="$2"
  rm -rf "$rundir"; mkdir -p "$rundir/spill"
  local prof="$rundir/cost_profile.tsv"
  local samp="$LOG/samples_$label.tsv"; : > "$samp"

  ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
    --cores 80 --ram 1073741824 --overlap-heights "$N" \
    --run-dir "$rundir" --spill-dir "$rundir/spill" \
    --cost-profile-out "$prof" > "$LOG/run_$label.log" 2>&1 &
  local pid=$!

  local i=0
  while [ "$i" -lt "$SECS" ] && kill -0 "$pid" 2>/dev/null; do
    local wa cols rmb
    wa=$(LC_ALL=C vmstat 1 2 | tail -1 | awk '{print $16}')
    cols=$(wc -l < "$prof" 2>/dev/null || echo 0)
    rmb=$(du -sm "$rundir" 2>/dev/null | awk '{print $1}')
    printf "%d\t%s\t%s\t%s\n" "$i" "$wa" "$cols" "$rmb" >> "$samp"
    sleep 10; i=$((i+10))
  done
  kill "$pid" 2>/dev/null || true
  sleep 4; kill -9 "$pid" 2>/dev/null || true

  local meanwa lastwa cols peak
  meanwa=$(awk '{s+=$2;n++} END{if(n)printf "%.1f",s/n}' "$samp")
  lastwa=$(awk '{a[NR]=$2} END{k=int(NR/3); s=0;n=0; for(i=NR-k+1;i<=NR;i++){s+=a[i];n++} if(n)printf "%.1f",s/n}' "$samp")
  cols=$(awk 'END{print $3}' "$samp")
  peak=$(awk 'BEGIN{m=0}{if($4>m)m=$4}END{print m}' "$samp")
  echo "ARM_RESULT label=$label secs=$SECS mean_iowait=$meanwa last3rd_iowait=$lastwa cols_done=$cols peak_rundir_MB=$peak" | tee -a "$LOG/summary.txt"
  rm -rf "$rundir"
}

echo "=== tmpfs PROBE a($N), ${SECS}s/arm: $(date -Iseconds), rev $(git rev-parse --short HEAD) ===" | tee "$LOG/summary.txt"

arm nvme "$NVME"

PEAK=$(awk '/label=nvme/{for(i=1;i<=NF;i++) if($i ~ /^peak_rundir_MB=/){split($i,a,"="); print a[2]}}' "$LOG/summary.txt")
SHMFREE=$(df -m /dev/shm | awk 'NR==2{print $4}')
echo "nvme peak run-dir ${PEAK}MB vs /dev/shm free ${SHMFREE}MB" | tee -a "$LOG/summary.txt"
if [ "${PEAK:-0}" -gt $(( SHMFREE * 8 / 10 )) ]; then
  echo "ABORT tmpfs arm: peak ${PEAK}MB > 80% of /dev/shm free ${SHMFREE}MB -- needs a bigger (root) tmpfs." | tee -a "$LOG/summary.txt"
  exit 3
fi

arm tmpfs "$SHM"
rm -rf "$SHM"

echo "=== VERDICT ===" | tee -a "$LOG/summary.txt"
grep ARM_RESULT "$LOG/summary.txt" | tee -a "$LOG/summary.txt"
echo "TMPFS_PROBE_DONE" | tee -a "$LOG/summary.txt"
