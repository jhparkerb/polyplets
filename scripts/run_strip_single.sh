#!/bin/bash
# run_strip_single.sh H N — build the independent strip TM and compute a single
# height's C_H(0..N), writing results/strip_C/CH_<H>.txt. Used to split the
# heavy heights across machines (H=15 ayr, H=16 dalby); compose by differencing.
set -e
H=$1
N=$2
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git pull --ff-only
# native build (g++ -O3); strip_tm is standalone, no repo build deps
g++ -O3 -std=c++17 -o build/strip_tm cpp/strip_tm.cpp
mkdir -p results/strip_C
echo "=== strip single H=$H N=$N on $(hostname) rev $(git rev-parse --short HEAD) ==="
./build/strip_tm single "$H" "$N" "results/strip_C/CH_${H}.txt" 2>&1 \
  | tee "results/strip_C/CH_${H}.log"
echo "=== done H=$H ==="
