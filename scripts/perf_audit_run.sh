#!/bin/bash
# perf_audit_run.sh — instrumented production-shaped run for the dalby perf
# audit (results/dalby-perf-audit.md). NOT a record run: maxn=24, heights 1-15
# (excludes H16 to stay safely under an hour). Output IS real, reusable partial
# a(24) progress (per-height H1-15 rows), just not the full a(24) answer.
#
# Purpose: exercise the production engine at real scale on dalby (Neoverse-N1,
# 80 cores) while sampling vmstat/iostat/mpstat/pidstat/perf/PSI concurrently,
# to look for OS/hardware-level headroom beyond what app-level telemetry shows.
#
# Target: dalby. Predicted cost: ~30-40 min wall (calibrated from a maxn=22
# run: 470.8s wall, 67% utilization, peak orchestrate RSS 76MB), peak disk:
# spill dir, generous margin on 346GB free. Resume: re-run is idempotent
# (RunDir is fresh each invocation; no checkpoint needed for a probe this
# size). Kill: SIGTERM the orchestrate PID; harmless, this is a throwaway probe.
set -e
cd ~/src/polyominoes-ns
RUNDIR=/tmp/perfaudit_run
LOGDIR=/tmp/perfaudit_logs
rm -rf "$RUNDIR" "$LOGDIR"
mkdir -p "$RUNDIR/spill" "$LOGDIR"

echo "=== perf_audit_run starting: $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)"

# Launch the instrumented sampling tools, all backgrounded, all logging to files.
vmstat 2 > "$LOGDIR/vmstat.log" &
VMPID=$!
iostat -xz 2 > "$LOGDIR/iostat.log" &
IOPID=$!
mpstat -P ALL 2 > "$LOGDIR/mpstat.log" &
MPPID=$!
pidstat -h -u -w -r 2 > "$LOGDIR/pidstat.log" &
PSPID=$!
( while sleep 2; do
    echo "--- $(date -Iseconds) ---"
    cat /proc/pressure/cpu /proc/pressure/io /proc/pressure/memory 2>/dev/null
  done ) > "$LOGDIR/psi.log" &
PSIPID=$!

# perf stat: test access ONCE before looping. NOTE: probe with the EXACT event
# list we intend to use, not perf's bare default group -- on dalby the bare
# default group fails ("No supported events found", even at paranoid=0)
# because one event in perf's default set isn't available, but the explicit
# list below (generic hw-event aliases, which perf maps onto whatever PMU the
# host exposes -- here, ARM PMUv3) works fine at paranoid=0. Looping a failing
# perf call is pointless spam, not a real busy-wait (the loop itself would
# never block on anything), but still wasteful -- skip if the probe fails.
PERFPID=""
if timeout 2 perf stat -a -e cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses -- sleep 1 >/dev/null 2>"$LOGDIR/perf_probe.log"; then
  ( while true; do
      timeout 30 perf stat -a -e cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses -- sleep 30 2>>"$LOGDIR/perf_stat.log" || true
    done ) &
  PERFPID=$!
else
  echo "perf stat: hardware counters unavailable (see perf_probe.log) -- skipped" | tee "$LOGDIR/perf_stat.log"
fi

echo "monitors: vmstat=$VMPID iostat=$IOPID mpstat=$MPPID pidstat=$PSPID psi=$PSIPID perf=${PERFPID:-none}"
echo "$VMPID $IOPID $MPPID $PSPID $PSIPID $PERFPID" > "$LOGDIR/monitor_pids.txt"

T0=$(date +%s)
./build/ns/orchestrate --maxn 24 --cores 80 --ram 8589934592 --unit-mult 4 \
  --heights 1-15 --overlap-heights 15 --steal-grain 0.05 \
  --run-dir "$RUNDIR" --spill-dir "$RUNDIR/spill" \
  --per-height-out "$RUNDIR/perheight" \
  --cost-profile-out "$RUNDIR/cost_profile.tsv" \
  > "$LOGDIR/orchestrate.log" 2>&1
RC=$?
T1=$(date +%s)
echo "=== orchestrate exited rc=$RC after $((T1-T0))s : $(date -Iseconds) ==="

# Stop the monitors.
kill $VMPID $IOPID $MPPID $PSPID $PSIPID ${PERFPID:-} 2>/dev/null || true
wait 2>/dev/null || true

echo "=== done. logs in $LOGDIR, run output in $RUNDIR ==="
tail -5 "$LOGDIR/orchestrate.log"
