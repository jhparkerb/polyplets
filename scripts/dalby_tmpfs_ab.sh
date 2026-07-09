#!/bin/bash
# dalby_tmpfs_ab.sh N -- A/B experiment: does putting the intermediate run-dir
# on tmpfs (/dev/shm, NO root needed) cut the disk-write bottleneck vs the NVMe
# RAID1 mirror (md3)?
#
# WHY. During a(35) the box sat at 60-69% iowait with both NVMes ~93% util
# writing ~780 MB/s, while the SPILL dir was empty -- i.e. it wasn't spill
# thrash but the normal inter-round churn: the kink sweep writes map/merge
# run files to --run-dir between every one of its H+1 barriered rounds, then
# reads and deletes them. buff/cache held ~83 GB, so the files were largely in
# RAM already; the disk traffic was writeback flushing short-lived files that
# never needed to be durable. tmpfs run-dir eliminates that writeback entirely.
#
# WHAT. Run maxn=N twice on the deployed kink config, identical except --run-dir:
#   nvme : run-dir on the md3 NVMe mirror (baseline, today's behavior)
#   tmpfs: run-dir on /dev/shm
# Measure wall + mean iowait for each, and PROVE the two produce byte-identical
# per-height output (correctness must not depend on where scratch files live).
#
# TARGET: dalby only (has /dev/shm 63 GB + the md3 mirror). Pick N so its peak
# run-dir working set fits /dev/shm with margin -- a(35)'s own run-dir peaks
# >58 GB and would NOT fit (that needs a bigger tmpfs = root, a separate ask).
# N=31 is a good default: disk-active enough to show the effect, small enough
# to fit and to finish in ~15-40 min/arm. A runtime guard aborts the tmpfs arm
# if the measured baseline peak would risk filling /dev/shm (ENOSPC = crash).
#
# PREDICTED COST: 2 x one maxn=N run (~15-40 min each at N=31), 80 cores,
# ~1 GiB/worker RAM, run-dir peak must fit /dev/shm. Recoverable: each arm is
# independent and cheap; a killed arm just re-runs. Not a keeper result -- a
# tuning measurement, logged under runs/ns_a${N}_tmpfsab/.
#
# RUN:  scripts/dalby_tmpfs_ab.sh 31
# KILL: kill the orchestrate PID; then rm -rf /dev/shm/ns_a${N}_tmpfsab
set -e
cd ~/src/polyominoes
N="${1:?usage: dalby_tmpfs_ab.sh N}"
LOG="runs/ns_a${N}_tmpfsab"
NVME="$LOG/nvme_rundir"
SHM="/dev/shm/ns_a${N}_tmpfsab"
mkdir -p "$LOG"

# One arm: $1=label $2=rundir. Samples iowait (vmstat wa column) and run-dir
# size in the background for the arm's duration, runs the sweep, reports.
arm() {
  local label="$1" rundir="$2"
  rm -rf "$rundir"; mkdir -p "$rundir/spill"
  local iolog="$LOG/iowait_$label.log"; : > "$iolog"
  local szlog="$LOG/rundirMB_$label.log"; : > "$szlog"
  ( while :; do LC_ALL=C vmstat 1 2 | tail -1 | awk '{print $16}'; done ) > "$iolog" &
  local iop=$!
  ( while :; do du -sm "$rundir" 2>/dev/null | awk '{print $1}'; sleep 10; done ) > "$szlog" &
  local szp=$!

  local t0; t0=$(date +%s)
  ./build/ns/orchestrate --maxn "$N" --kernel kink --counter u128 \
    --cores 80 --ram 1073741824 --overlap-heights "$N" \
    --run-dir "$rundir" --spill-dir "$rundir/spill" \
    --per-height-out "$LOG/perheight_$label" 2>&1 | tee "$LOG/run_$label.log"
  local rc=${PIPESTATUS[0]}
  local t1; t1=$(date +%s)
  kill "$iop" "$szp" 2>/dev/null || true

  local peak; peak=$(sort -n "$szlog" | tail -1)
  local avgio; avgio=$(awk '{s+=$1;n++} END{if(n) printf "%.1f", s/n}' "$iolog")
  echo "ARM_RESULT label=$label wall_s=$((t1-t0)) rc=$rc peak_rundir_MB=$peak mean_iowait_pct=$avgio" | tee -a "$LOG/summary.txt"
  rm -rf "$rundir"
  return "$rc"
}

echo "=== tmpfs A/B for a($N): $(date -Iseconds), rev $(git rev-parse --short HEAD) ===" | tee "$LOG/summary.txt"

# Baseline arm (NVMe) first -- also measures the real peak working set.
arm nvme "$NVME"

PEAK=$(sort -n "$LOG/rundirMB_nvme.log" | tail -1)
SHMFREE=$(df -m /dev/shm | awk 'NR==2{print $4}')
echo "peak run-dir ${PEAK}MB vs /dev/shm free ${SHMFREE}MB" | tee -a "$LOG/summary.txt"
if [ "${PEAK:-0}" -gt $(( SHMFREE * 8 / 10 )) ]; then
  echo "ABORT tmpfs arm: peak ${PEAK}MB > 80% of /dev/shm free ${SHMFREE}MB -- would risk ENOSPC. A larger tmpfs (root) is needed for this N." | tee -a "$LOG/summary.txt"
  exit 3
fi

# tmpfs arm.
arm tmpfs "$SHM"
rm -rf "$SHM"

# Correctness: the two arms' per-height output must be byte-identical.
echo "=== byte-identical check (nvme vs tmpfs per-height output) ===" | tee -a "$LOG/summary.txt"
if diff -rq "$LOG/perheight_nvme" "$LOG/perheight_tmpfs" >/dev/null 2>&1; then
  echo "PER_HEIGHT_IDENTICAL PASS" | tee -a "$LOG/summary.txt"
else
  echo "PER_HEIGHT_IDENTICAL FAIL -- run-dir location changed the result (bug!)" | tee -a "$LOG/summary.txt"
fi

echo "=== SUMMARY ===" | tee -a "$LOG/summary.txt"
grep ARM_RESULT "$LOG/summary.txt"
echo "TMPFS_AB_DONE" | tee -a "$LOG/summary.txt"
