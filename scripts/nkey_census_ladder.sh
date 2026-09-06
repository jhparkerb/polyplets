#!/bin/bash
# The reach-merged frontier census, H = 14 up, one height at a time.
#
# WHY.  results/closed-doors.md forbids quoting a class count at
# H = 21 and is right to: the ratio compounds ~1.087x/height from nine points
# with no closed form, no OEIS match, and no recurrence with surplus.  The two
# soft spots results/confidence.md names -- the H = 20 sweep that would turn
# P_21 into a holdout, and the H = 21 cell that never fitted -- are both priced
# against this frontier, so the number decides whether they are affordable.
# docs/time-at-the-bar.md (deleted) A1.1 is the item; this is its measurement.
#
# WHAT IT COSTS.  Unknown above H = 14 and that is the point.  Measured on
# dalby: the whole gate ladder (king H = 4..13, rook H = 2..10) is 1 m 24 s, so
# H = 13 itself is well under a minute.  The extrapolated class counts are
# 53,777 at H = 14 rising to ~4e7 at H = 21; memory is the key set at roughly
# 40 B per class plus hash overhead, i.e. single-digit GB at the top, against
# dalby's 125 GB.  WALL TIME IS NOT PREDICTED -- each height prints as it lands
# and the ladder can be killed between heights at no cost.
#
# The binary re-runs both gates before every height it reports, so a number in
# this log is never from a binary that has not just reproduced the banked
# ladder and its rook control.
#
# Target: dalby (running alongside the emax5 K-ladder, which is 8 threads and
# ~15 GB; this is single-threaded).
#
# Kill: kill the PID in ~/var/nkey-census/pid.  Heights already printed are
# banked in census.txt; resume by rerunning from the next height.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/build/nkey_census"
OUT=${NKEY_OUT:-$HOME/var/nkey-census}
H1=${1:-14}
H2=${2:-21}
[ -x "$BIN" ] || { echo "no binary at $BIN -- make build/nkey_census" >&2; exit 1; }
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
{
  echo "=== nkey census H=$H1..$H2: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} >> "$OUT/census.txt"
for H in $(seq "$H1" "$H2"); do
  /usr/bin/time -f "H=$H wall=%e rss_kb=%M" "$BIN" "$H" \
    >> "$OUT/census.txt" 2>> "$OUT/events.txt"
  echo "-- H=$H done $(date -Is)" >> "$OUT/census.txt"
done
echo "LADDER COMPLETE H=$H1..$H2" >> "$OUT/census.txt"
