#!/bin/bash
# Serial root build of the polyplets Lean tree, logged to build/lean-root2.log.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/polyplets" || exit 1
mkdir -p "$ROOT/build"
LEAN_NUM_THREADS=1 nice -n 10 ~/.elan/bin/lake build 2>&1 | tee "$ROOT/build/lean-root2.log"
echo "EXIT ${PIPESTATUS[0]}" | tee -a "$ROOT/build/lean-root2.log"
