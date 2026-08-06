#!/bin/bash
# Enlarged PSLQ sweep for the (dir4, HV-convex)/HV-convex amplitude ratio.
#
# Purpose: docs/middle-kingdom-followups-plan.md Table B excluded integer
# relations at 54 trusted digits.  experiments/amplitude_feed_vectors.py raised
# the trusted count, and PSLQ box size scales with digits, so every box Table B
# could afford is now enlarged by the same capacity rule
# ((degree+1)*log10(height) < half the trusted digits).
#
# Command:  scripts/amplitude_pslq_sweep.sh <digits> <logfile>
# Target machine: gympie (laptop), ONE core.  The boxes run cheapest first so a
# kill leaves every completed box on disk.
# Predicted cost: the top box dominates -- PSLQ cost grows like degree^3 x
# digits, and the 12-degree box at 54 digits is ~1 s, so degree 45 at 185
# digits is order 10 min and degree 122 at 492 digits is hours.  Watch the
# per-degree heartbeat and stop if it outgrows the budget.
# Resume/kill: no checkpointing.  SIGINT, then rerun with a shorter --boxes
# list; boxes already printed to the log need not be redone.
set -u
DIGITS="${1:?usage: amplitude_pslq_sweep.sh <digits> <logfile> [boxes] [field]}"
LOG="${2:?usage: amplitude_pslq_sweep.sh <digits> <logfile> [boxes] [field]}"
BOXES="${3:-2:1e30,3:1e20,6:1e12,10:1e8,14:1e6,22:1e4,45:1e2}"
FIELD="${4:-2:4:1e6,3:4:1e4,5:6:1e2}"

cd "$(dirname "$0")/.."
exec python3 -u experiments/amplitude_pslq.py \
    --digits "$DIGITS" --boxes "$BOXES" --field "$FIELD" 2>&1 | tee "$LOG"
