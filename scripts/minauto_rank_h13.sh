#!/bin/bash
# The H = 13 characteristic-2 rank -- the legitimacy test for the A034299
# identification.
#
# WHY.  results/char2-basis-status.md: the strip automaton's GF(2)
# observability rank matches A034299 at every height H = 4..12 (6, 15, 27, 58,
# 112, 229, 453, 912, 1818), nine consecutive terms against a four-term linear
# recurrence.  A034299 predicts r(13) = 3643.  The H = 13 *state* count is now
# measured independently by the census (21,355, results/nkey-census.md); it is
# the RANK that tests the identification, and an explicit basis for that
# collapse is the largest open technical question left in the reach mission.
#
# HONEST LIMIT, stated before the run rather than after.  This is minauto-only.
# results/exactchange-probes.md section 7 says a single-source rank does not
# count until a second implementation reproduces it, and that stands whatever
# this returns.  A match is a fifth confirmation of an identification; it is
# not a proof and it does not make king counting easy.
#
# WHAT IT COSTS.  H = 12 on ayr was build 148.5 s + rank 874.7 s, ~17 min at
# 3.9 GB.  Rank cost has run ~8x per height, so H = 13 is ~2 h; RAM at the
# same factor is ~31 GB, and 8x is the number to watch -- ayr has 78 GB and
# 119 GB of swap behind it, but swapping is not fitting.  Single-core Python.
#
# The script is its own gate: it asserts the brute-force anchors at
# (H,W) = (2,3), (3,3), (3,4), then every banked Nerode count and every banked
# rank up to H = 12, before it reports 13.  A wrong build cannot print a 13.
#
# Target: ayr.  Kill: kill the PID in ~/var/minauto-h13/pid; no checkpoint,
# a kill costs the whole run.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/experiments/tristruct/exactchange_minauto.py"
OUT=${MINAUTO_OUT:-$HOME/var/minauto-h13}
MAXH=${1:-13}
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
{
  echo "=== exactchange_minauto MAXH=$MAXH: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} >> "$OUT/rank.txt"
/usr/bin/time -f "MAXH=$MAXH wall=%e rss_kb=%M" \
  python3 "$SCRIPT" "$MAXH" >> "$OUT/rank.txt" 2>> "$OUT/events.txt"
echo "-- done $(date -Is)" >> "$OUT/rank.txt"
