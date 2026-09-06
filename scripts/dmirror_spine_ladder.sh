#!/bin/bash
# The spine split at the lengths c_3 needs: S = 15..18, cells n <= S+6.
#
# WHY.  results/symmetry-classes.md pins levels k <= 2 on both parities of
# both families and finds c_2 linear for each -- the discriminator that kills
# the summed family.  c_3 needs k = 3 pinned, which is five points per parity:
# S = 16 on the even class and S = 17 on the odd.  S = 18 is the first holdout
# above that.
#
# COST, measured on dalby 2026-08-23: the gate (S <= 11, uncapped, 191 banked
# cells) is 47 s and runs before every S; S = 14 itself is 19 s, against
# 6 h 38 min for the pure-Python enumerator, and its every value agrees.
# Growth is roughly 4-6x per S, so S = 15 is minutes and S = 18 is the one that
# could be hours.  Memory is the hook state map, tens of MB at S = 14.
#
# Target: dalby, single-threaded, alongside the emax5 ladder and the nkey
# census.  Kill: kill the PID in ~/var/dmirror-spine/pid.  Each S is
# independent, so a kill costs only the S in flight.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/build/dmirror_spine"
OUT=${SPINE_OUT:-$HOME/var/dmirror-spine}
S1=${1:-15}
S2=${2:-18}
KMAX=${3:-6}
[ -x "$BIN" ] || { echo "no binary at $BIN -- make build/dmirror_spine" >&2; exit 1; }
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
{
  echo "=== dmirror spine split S=$S1..$S2 kmax=$KMAX: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} >> "$OUT/split.txt"
for S in $(seq "$S1" "$S2"); do
  /usr/bin/time -f "S=$S kmax=$KMAX wall=%e rss_kb=%M" "$BIN" "$S" "$KMAX" \
    >> "$OUT/split.txt" 2>> "$OUT/events.txt"
  echo "-- S=$S done $(date -Is)" >> "$OUT/split.txt"
done
echo "LADDER COMPLETE S=$S1..$S2" >> "$OUT/split.txt"
