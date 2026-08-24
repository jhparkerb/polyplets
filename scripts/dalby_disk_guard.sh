#!/bin/bash
# dalby_disk_guard.sh RUNDIR PID FLOOR_GB [INTERVAL] -- stop a sweep CLEANLY
# before it fills the filesystem, rather than after.
#
# WHY.  docs/five-terms-plan.md makes this a precondition for any run past
# Nmax 43: "Nmax 44/45 only after the run dirs are cleared and with a disk
# guard that aborts phase C rather than filling the filesystem."  No such guard
# existed.  The orchestrator has a fast-map reserver (orchestrator/fastmap.go)
# that respects a floor for ITS OWN scratch, but nothing watches the run dir as
# a whole, and nothing stops the sweep.
#
# WHAT IT DOES.  Samples the filesystem holding RUNDIR.  When available space
# falls below FLOOR_GB it sends ONE SIGTERM to PID and exits nonzero.  SIGTERM,
# not SIGKILL: the orchestrator checkpoints at column boundaries and the
# kink resume-over-count bug is fixed and gated (TestKinkResumeMidColumn), so a
# clean stop costs one column and the run resumes with --resume.  A filesystem
# that hits 0 costs the whole run and can take the box's other users with it.
#
# It never deletes anything.  Stopping is the only action it takes.
#
# FAIL-CLOSED.  If `df` cannot read the filesystem, that is treated as a stop
# condition, not as "probably fine" -- a guard that cannot see is a guard that
# is not guarding.  It also refuses to start against a dead PID or a floor of
# zero, so a mistyped invocation does not silently produce an unguarded run.
#
# Predicted cost: one df per INTERVAL. Negligible.
# Usage: dalby_disk_guard.sh runs/foo 12345 80 &
# Kill:  kill the PID in RUNDIR.diskguard.pid (it also exits when PID does).
set -u
RUNDIR=${1:?usage: dalby_disk_guard.sh RUNDIR PID FLOOR_GB [INTERVAL]}
PID=${2:?need a pid to guard}
FLOOR_GB=${3:?need a floor in GB}
INTERVAL=${4:-60}
LOG="${RUNDIR%/}.diskguard.log"
echo $$ > "${RUNDIR%/}.diskguard.pid"

[ "$FLOOR_GB" -gt 0 ] 2>/dev/null || {
  echo "$(date -Iseconds) REFUSING: floor '$FLOOR_GB' is not a positive integer" | tee -a "$LOG" >&2
  exit 2; }
kill -0 "$PID" 2>/dev/null || {
  echo "$(date -Iseconds) REFUSING: pid $PID is not alive -- nothing to guard" | tee -a "$LOG" >&2
  exit 2; }

echo "$(date -Iseconds) guarding pid $PID on $RUNDIR, floor ${FLOOR_GB} GB, every ${INTERVAL}s" >> "$LOG"
while kill -0 "$PID" 2>/dev/null; do
  avail=$(df -BG --output=avail "$RUNDIR" 2>/dev/null | tail -1 | tr -dc '0-9')
  if [ -z "$avail" ]; then
    echo "$(date -Iseconds) STOP: df could not read $RUNDIR -- treating as a stop condition" >> "$LOG"
    kill -TERM "$PID" 2>/dev/null
    exit 1
  fi
  echo "$(date -Iseconds) avail=${avail}G floor=${FLOOR_GB}G" >> "$LOG"
  if [ "$avail" -lt "$FLOOR_GB" ]; then
    echo "$(date -Iseconds) STOP: ${avail} GB available < ${FLOOR_GB} GB floor -- SIGTERM to $PID" >> "$LOG"
    echo "$(date -Iseconds) resume with the run script's --resume once space exists" >> "$LOG"
    kill -TERM "$PID" 2>/dev/null
    exit 1
  fi
  sleep "$INTERVAL"
done
echo "$(date -Iseconds) guarded process exited on its own; guard stands down" >> "$LOG"
