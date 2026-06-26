#!/usr/bin/env bash
# ram_guard.sh FLOOR_GB POLE [PERIOD_S] -- overnight OOM guard for the a(21) heavy heights.
#
# Samples free RAM every PERIOD_S and logs it (so we get the whole-night trend, not a
# point sample). If free ever drops below FLOOR_GB, it does the controlled version of an
# OOM instead of letting the kernel's OOM-killer cascade (which took down the driver AND
# both sweeps on 2026-06-25): kill the DRIVER (stops the MAXJOBS refill) and every running
# a(21) tma whose height != POLE, leaving the pole to finish ALONE with the freed RAM.
# Killed heights resume from their column checkpoint on the next launch. One-shot: exits
# after protecting (so the morning state is "pole running solo, rest to be relaunched").
#
# Frequent sampling (default 10s) to catch a grow transient before the kernel does; FLOOR
# is set so the clean kill fires with headroom to spare. USAGE (on dalby, in a tmux window):
#   scripts/ram_guard.sh 12 20
set -u
cd "$(dirname "$0")/.."
FLOOR_GB="${1:?floor GB}"; POLE="${2:?pole height to keep}"; PERIOD="${3:-10}"
log="runs/a21fold/ram_guard.log"
echo $$ > runs/a21fold/ram_guard.pid
echo "$(date -Is) guard up: floor=${FLOOR_GB}GB  keep=H${POLE}  period=${PERIOD}s" | tee -a "$log"

while :; do
  free=$(free -g | awk '/^Mem:/{print $7}')
  printf '%s free=%sGB\n' "$(date -Is)" "${free:-?}" >> "$log"
  if [ -n "${free:-}" ] && [ "$free" -lt "$FLOOR_GB" ]; then
    echo "$(date -Is) !! free=${free}GB < ${FLOOR_GB}GB -- PROTECT: keep H${POLE}, drop the rest" | tee -a "$log"
    dpid=$(cat runs/a21fold/driver.pid 2>/dev/null)
    [ -n "$dpid" ] && { echo "  kill driver $dpid (stop refill)" | tee -a "$log"; kill "$dpid" 2>/dev/null; }
    ps -eo pid=,args= | grep "tma a(21)" | grep -v grep | sed 's/^ *//' | while read -r pid rest; do
      h=$(printf '%s' "$rest" | grep -oE 'H[0-9]+' | head -1 | tr -d H)
      if [ -n "$h" ] && [ "$h" != "$POLE" ]; then
        echo "  kill H${h} pid ${pid} (frees its RAM)" | tee -a "$log"; kill "$pid" 2>/dev/null
      fi
    done
    echo "$(date -Is) PROTECTED: H${POLE} now solo. Relaunch the rest (they resume) in the AM." | tee -a "$log"
    break
  fi
  sleep "$PERIOD"
done
