#!/bin/bash
# dalby_mem_monitor.sh RUNDIR PID [INTERVAL] -- sample RAM + tmpfs state once
# per INTERVAL (default 60s) into RUNDIR-adjacent mem.log while process PID is
# alive, then exit. Purpose: the a(40) OOM kills (results/fanin-tax.md) were
# diagnosed blind — the kernel journal needs root and the du monitor only sees
# disk. This leaves a used/available/shm timeline for the next post-mortem.
# Kill: exits by itself when PID does; or kill its own PID
# (written to RUNDIR.memmon.pid).
set -u
RUNDIR=$1; PID=$2; INTERVAL=${3:-60}
LOG="${RUNDIR%/}.mem.log"
echo $$ > "${RUNDIR%/}.memmon.pid"
while kill -0 "$PID" 2>/dev/null; do
  TOP=$(ps -Ao rss,comm --sort=-rss 2>/dev/null | awk 'NR>1&&NR<=4{printf "%s:%dM ", $2, $1/1024}')
  echo "$(date -Iseconds) $(free -m | awk 'NR==2{printf "used=%sM avail=%sM", $3, $7}') shm=$(du -sm /dev/shm 2>/dev/null | cut -f1)M top: $TOP" >> "$LOG"
  sleep "$INTERVAL"
done
