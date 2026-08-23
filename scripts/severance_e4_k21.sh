#!/bin/bash
# The depth-5 excess<=4 family table at K = 21 -- the thing review row B13 is
# waiting for.
#
# WHY.  results/undertow-review-queue.md B13 refuses the depth-5 route until
# experiments/severance_w3_depth5_gate.py passes against the 15 banked cells
# T(2k-4, k-4), k = 5..19.  That gate is correctly RED in production today for
# one reason only: _load_table(19, 4) finds no
# results/severance_w3_families_K*_e4.txt with K >= 19, so D_series(5,19) has
# no table and the gate refuses to fall back to the hours-long pure-Python DP.
# B13 is the stated blocker on the five-terms decision
# (docs/state-2026-08-23.md section 5).  This run produces the table; it does
# not license using D_5 at k = 21 -- that is what the gate is for, and the
# gate runs after this lands.
#
# WHAT IT COSTS.  results/depth5-cost-settled.md, from a five-rung ladder at
# 8 threads throughout with K = 16 held out and predicted to 6.9% / 8.0%:
# ~3.1 h and ~8.5 GB decelerating, ~6.7 h and ~16.1 GB if the deceleration is
# assumed to stop dead.  8 threads is not a detail -- the family DP's RSS
# scales with thread count, so a run at another width is not comparable to
# that ladder.
#
# Target: dalby (125 GB, 80 cores).  Fits either end with two orders of
# magnitude of core headroom and an order of magnitude of RAM headroom.
#
# Kill: kill the PID in ~/var/severance-e4/pid.  There is no checkpoint --
# a kill costs the whole run, which is why it is priced before it is started.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/build/severance_w3_families"
OUT=${SEV_OUT:-$HOME/var/severance-e4}
K=${1:-21}
THREADS=${2:-8}
[ -x "$BIN" ] || { echo "no binary at $BIN -- make build/severance_w3_families" >&2; exit 1; }
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
TABLE="$ROOT/results/severance_w3_families_K${K}_e4.txt"
[ -e "$TABLE" ] && { echo "$TABLE already exists -- refusing to overwrite" >&2; exit 1; }
{
  echo "=== severance_w3_families families $K 4 $THREADS: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} >> "$OUT/run.txt"
/usr/bin/time -f "K=$K emax=4 threads=$THREADS wall=%e rss_kb=%M" \
  "$BIN" families "$K" 4 "$THREADS" > "$TABLE.partial" 2>> "$OUT/events.txt"
mv "$TABLE.partial" "$TABLE"
echo "-- done $(date -Is) -> $TABLE" >> "$OUT/run.txt"
