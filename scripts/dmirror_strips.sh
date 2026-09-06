#!/usr/bin/env bash
# Farmed dmirror strip driver (Hall of Mirrors): run each exact-bbox strip S
# as its own symtm process, one after another, so RSS returns to the OS
# between strips and a failure costs one strip, not the range.
#
#   scripts/dmirror_strips.sh MAXN THREADS S1 [S2 ...]
#
# Writes runs/sym${MAXN}/dmirror.S${S}.out (+ .err heartbeats) per strip;
# combine with scripts/dmirror_sum.py. Machines: dalby (fat strips) + ayr
# (tails) for the n=32 push, 2026-07-04. Predicted n=32 total ~3.0M cpu-s
# (~830 cpu-h) across both; peak strip RSS is the binding resource — see
# docs/handoff.md. Kill = kill the symtm PID printed per strip; resume = rerun
# with the not-yet-done strips.
set -euo pipefail
cd "$(dirname "$0")/.."
MAXN=$1; THREADS=$2; shift 2
mkdir -p "runs/sym${MAXN}"
for S in "$@"; do
  out="runs/sym${MAXN}/dmirror.S${S}.out"
  err="runs/sym${MAXN}/dmirror.S${S}.err"
  echo "=== strip S=${S} start $(date +%FT%T%z)"
  ./build/symtm dmirror "${MAXN}" "${THREADS}" "${S}" "${S}" \
    > "${out}" 2> >(tee "${err}" >&2) &
  pid=$!
  echo "=== strip S=${S} pid ${pid}"
  wait "${pid}"
  echo "=== strip S=${S} done rc=$? $(date +%FT%T%z)"
done
echo "DMIRROR_STRIPS_DONE maxn=${MAXN} strips=$*"
