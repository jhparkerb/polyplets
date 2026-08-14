#!/bin/bash
# Motley step 0 — the provenance re-run (docs/motley-plan.md §"Step 0").
#
# Purpose: reproduce the banked C_H(n) rows, H = 1..16, Nmax = 40, using the
# COMMITTED fail-closed engine (second-source 48ac108) instead of the dirty
# 59e90660 working copy that produced them.  Product: a(n) rule-independent and
# citable for all n <= 30.
#
# Target machine: dalby.  Binary: ~/src/pm-b1-step0/build/cutcount_b1, a clean
# worktree at 48ac108 so the obs stamp reads git=48ac1089 with no -dirty.
#
# Predicted cost (measured, results/cutcount_b1/calib_run.log):
#   H=16  4.58 h  60.8 GB      H=15  1.43 h  20.4 GB      H<=14  0.68 h  6.9 GB
# Run as three concurrent streams (16 | 15 | 14..1): 4.6 h wall, 88 GB peak
# against dalby's 122 GB available.  Single-stream it is 6.7 core-hours.
#
# Exact command (one tmux window per stream):
#   ./dalby_motley_step0.sh 16
#   ./dalby_motley_step0.sh 15
#   ./dalby_motley_step0.sh 14 13 12 11 10 9 8 7 6 5 4 3 2 1
# Then the compare, which is the actual product:
#   ./dalby_motley_step0.sh --assemble
#
# Kill/resume: each height is an independent process writing one row file; kill
# any stream by PID and re-run it with the heights that have no C<H>.out.
#
# Fail-closed: set -e plus the engine's own exit codes (2 = mismatch or failed
# self-check, 3 = zero cells compared).  A stream that dies leaves no row file.

set -euo pipefail

BIN="$HOME/src/pm-b1-step0/build/cutcount_b1"
OUT="$HOME/var/motley-step0"
# rows/ compares against the banked C rows; the T assembly compares against
# the banked TRIANGLE, which is a different directory in a different format
# (hN.out).  Pointing --assemble at the row directory makes it compare nothing,
# which the engine correctly treats as a failure (exit 3).
BANKED="$OUT/banked"
TRIANGLE="$HOME/src/pm-b1-step0/results/ns_a40/perheight"
NMAX=40
HMAX=16

mkdir -p "$OUT/rows" "$OUT/logs"

if [ "${1:-}" = "--assemble" ]; then
  for H in $(seq 1 $HMAX); do
    [ -s "$OUT/rows/C$H.out" ] || { echo "MISSING $OUT/rows/C$H.out" >&2; exit 1; }
  done
  for H in $(seq 1 $HMAX); do
    cmp "$OUT/rows/C$H.out" "$BANKED/C$H.out" || exit 2
  done
  echo "all $HMAX rows byte-identical to the banked C rows"
  exec "$BIN" --assemble $HMAX $NMAX "$OUT/rows" "$TRIANGLE" 2>&1 \
       | tee "$OUT/logs/assemble.log"
fi

[ $# -ge 1 ] || { echo "usage: $0 <H> [H...] | --assemble" >&2; exit 1; }

for H in "$@"; do
  echo "=== C_$H start $(date -Is) host=$(hostname)" >> "$OUT/logs/H$H.log"
  "$BIN" --height "$H" $NMAX "$OUT/rows/C$H.out.tmp" >> "$OUT/logs/H$H.log" 2>&1
  mv "$OUT/rows/C$H.out.tmp" "$OUT/rows/C$H.out"
  echo "=== C_$H done $(date -Is)" >> "$OUT/logs/H$H.log"
done
