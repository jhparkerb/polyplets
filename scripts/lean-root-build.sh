#!/bin/bash
# Serial root build of the polyplets Lean tree, logged to build/lean-root2.log.
cd /Users/jasonp/src/polyominoes/polyplets || exit 1
LEAN_NUM_THREADS=1 nice -n 10 ~/.elan/bin/lake build 2>&1 | tee /Users/jasonp/src/polyominoes/build/lean-root2.log
echo "EXIT ${PIPESTATUS[0]}" | tee -a /Users/jasonp/src/polyominoes/build/lean-root2.log
