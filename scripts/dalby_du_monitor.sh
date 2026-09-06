#!/bin/bash
# dalby_du_monitor.sh RUNDIR PID [INTERVAL] -- sample `du -sm RUNDIR` once per
# INTERVAL (default 60s) into RUNDIR-adjacent rundir_size.log while process
# PID is alive, then exit. Purpose: measured disk-footprint telemetry for the
# a(37)+ ladder runs (docs/engine-record.md ladder section) -- each term's
# measured peak calibrates the next term's disk prediction (H20 -> H21 -> H22
# feasibility). Predicted cost of the monitor itself: one du walk/min,
# negligible. Kill: it exits by itself when PID does; or kill its own PID
# (written to RUNDIR.dumon.pid).
set -u
RUNDIR=$1; PID=$2; INTERVAL=${3:-60}
LOG="${RUNDIR%/}.rundir_size.log"
echo $$ > "${RUNDIR%/}.dumon.pid"
while kill -0 "$PID" 2>/dev/null; do
  echo "$(date -Iseconds) $(du -sm "$RUNDIR" 2>/dev/null | cut -f1) MB" >> "$LOG"
  sleep "$INTERVAL"
done
