#!/bin/bash
# run_strip_h14_n40.sh — strip-TM second source extended to the a(40) close.
#
# Purpose: AUDIT-2026-07-30 S4 ("Coverage Counted in Cells") — the banked strip
#   run (results/strip_C14_run.log) stopped at N=36, so a(37)-a(40) carry ~0%
#   second-sourced mass. This re-runs the full H<=14 sweep at N=40 against
#   results/ns_a40/perheight, lifting second-sourced mass on the final four
#   terms to ~45-54% and adding ~110 second-sourced cells to rows 37-40.
# Machine: dalby (125 GB). Predicted cost: ~8.3 h wall, ~42 GB RAM peak,
#   1 core. Basis: MEASURED N=36 run = 26,930 s total (C_14 alone 22,919 s)
#   at ~38 GB measured footprint; cost ~linear in N => x40/36.
# Command: build/strip_tm 14 40 results/ns_a40/perheight
# Kill/resume: plain kill of the strip_tm PID; single-unit job, no checkpoint —
#   a kill costs the whole run (~8 h), accepted for a one-off validation run
#   (same posture as the N=36 run in run_strip_h14.sh).
set -euo pipefail
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# native build (g++ -O3); strip_tm is standalone, no repo build deps
g++ -O3 -std=c++17 -o build/strip_tm cpp/strip_tm.cpp
{
  echo "=== strip full Hmax=14 N=40 host=$(hostname -s) rev=$(git rev-parse --short HEAD) $(date -u +%FT%TZ) ==="
  echo "=== cpp/strip_tm.cpp blob $(git hash-object cpp/strip_tm.cpp) ==="
  ./build/strip_tm 14 40 results/ns_a40/perheight
} 2>&1 | tee results/strip_C14_n40_run.log
