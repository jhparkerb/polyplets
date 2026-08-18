#!/bin/sh
# Exact Change — extend the minimized-automaton rank ladder to H = 13.
#
# Purpose: the A034299 identification of the strip-automaton GF(2) rank rests
# on 9 banked terms against an order-4 recurrence.  H = 13 predicts rank 3643;
# a match is one more term, a miss kills the identification outright.
# Result tier: single-source planning input.  H = 13 is minauto-only --- it
# does NOT count as banked until a second source (cross-automaton random-word
# equality) agrees.  See results/exactchange-probes.md sections 7 and 9.
#
# Target machine: ayr (32 cores / 78 GB) --- single core, ~1 GB.
# Predicted cost: ~5-6 h wall single-core, off the measured H = 12 wall
#   (1696 s) and the ~2.4x/height state growth.
# Command:  tmux new-window -t 0 -n ec-h13 'sh ~/src/polyominoes/scripts/ayr_exactchange_h13.sh'
# Resume:   none --- restart from H = 13; the H <= 12 anchors re-run in minutes.
# Kill:     ps to find the python3 PID, then kill <pid>.
#
# Runs H = 4..13 so every banked anchor (Nerode counts, ranks, A034299,
# brute-force counts at H <= 3) is re-checked on this machine before the new
# term is produced.  Script asserts on any anchor mismatch.
set -e
LOG=$HOME/var/exactchange/ayr_h13.log
mkdir -p "$(dirname "$LOG")"
cd "$HOME/src/polyominoes"
echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(hostname) rev=$(git rev-parse --short HEAD)" >> "$LOG"
python3 experiments/tristruct/exactchange_minauto.py 13 4 >> "$LOG" 2>&1
echo "done $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$?" >> "$LOG"
