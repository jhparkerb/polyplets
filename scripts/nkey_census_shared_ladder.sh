#!/bin/bash
# TODO(2026-08-24, /simplify): this is a ~46-line copy of
# scripts/nkey_census_ladder.sh differing in four lines (OUT default, H
# defaults, BATCH arg, the --shared --batch flags). scripts/nkey_census_h17_postfix.sh
# already shows the cheaper pattern in this same campaign: set env and exec the
# other script. Left as a copy for now because a ladder driver cannot be tested
# from here without a box and a multi-hour run.
# The frontier census under the SHARED-partial-fill engine, H = 13 up.
#
# WHY.  results/nkey-census.md measures H = 14, 15, 16 at 293 s, 1,960 s and
# 10,454 s and names the reason it stops: "successors are generated per source
# state, so a partial fill that could serve many sources is rebuilt for each of
# them", which prices H = 18 at three days and puts 21 out of reach.  The
# shared engine (nkey_census --shared) sweeps a whole batch of sources
# together, one row at a time, so the partial fills are built once.  This
# ladder is the measurement of what that buys -- and H = 13..16 are all banked,
# so it is a re-derivation of four known numbers before it is anything else.
#
# WHAT IT COSTS.  Unknown above H = 16 and that is the point; each height
# prints as it lands and the ladder is killable between heights at no cost.
# On gympie the whole gate suite -- both engines' king and rook ladders plus
# the per-source cross-check -- is 24 s against 84 s for the per-source ladder
# alone on dalby, which is the only speed evidence there is before this runs.
# --batch caps how many sources are swept at once, and the default is set high
# on purpose.  MEASURED on dalby at H = 17: batch 131072 took 519.55 s and
# 1,463 MB; unbatched took 249.87 s and 1,483 MB.  Twice the speed for 1.4%
# more memory, because the RAM is the reachable key SET and not the sweep
# front -- so capping the batch throws away sharing and buys nothing.  Lower it
# only if a height actually runs out of memory.
#
# THE BANKED VALUES it must reproduce: 21,355 / 53,763 / 136,145 / 346,539 at
# H = 13, 14, 15, 16.  The binary re-runs the king ladder, the rook RED
# control and the cross-engine successor-set check before any height.
#
# Target: ayr or dalby.  Kill: kill the PID in ~/var/nkey-shared/pid.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/build/nkey_census"
OUT=${SHARED_OUT:-$HOME/var/nkey-shared}
H1=${1:-13}
H2=${2:-16}
BATCH=${3:-1000000000}
[ -x "$BIN" ] || { echo "no binary at $BIN -- make build/nkey_census" >&2; exit 1; }
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
{
  echo "=== nkey census SHARED H=$H1..$H2 batch=$BATCH: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} >> "$OUT/census.txt"
for H in $(seq "$H1" "$H2"); do
  /usr/bin/time -f "H=$H wall=%e rss_kb=%M" "$BIN" --shared "--batch=$BATCH" "$H" \
    >> "$OUT/census.txt" 2>> "$OUT/events.txt"
  echo "-- H=$H done $(date -Is)" >> "$OUT/census.txt"
done
echo "LADDER COMPLETE H=$H1..$H2" >> "$OUT/census.txt"
