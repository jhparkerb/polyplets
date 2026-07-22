#!/bin/bash
# run_strip_h14.sh — independent strip-TM full sweep, Hmax=14, vs banked triangle.
#
# Purpose: extend the second-source per-cell confirmation from H<=13 to H<=14
#   (flips PinGrand anchors T(26,14)/T(27,14) to multi-source; fix 7 of
#   docs/lean-hostile-witness.md). The 2026-07-10 Hmax=14 run was stopped after
#   C_13, so its end-of-run banked compare never executed; this run re-prints
#   the per-height match counts for ALL H<=14 in one log.
# Machine: gympie (local). Predicted cost: ~70 min wall (measured C_13=606s,
#   ~5.7x/height => C_14~3450s), <2 GB RAM, 1 core.
# Command: build/strip_tm 14 36 results/ns_a36/perheight
# Kill/resume: plain kill of the strip_tm PID; single-unit job, no checkpoint —
#   a kill costs the whole run (~70 min), accepted for a one-off validation run.
set -e
cd ~/src/polyominoes
g++ -O3 -std=c++17 -o build/strip_tm cpp/strip_tm.cpp
echo "=== strip full Hmax=14 N=36 host=$(hostname -s) rev=$(git rev-parse --short HEAD) $(date -u +%FT%TZ) ==="
echo "=== cpp/strip_tm.cpp blob $(git hash-object cpp/strip_tm.cpp) (file unmodified since 2026-07-10 run) ==="
exec ./build/strip_tm 14 36 results/ns_a36/perheight
