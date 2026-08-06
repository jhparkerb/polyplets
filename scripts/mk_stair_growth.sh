#!/bin/sh
# Purpose: the numerical arm of results/hv-growth-sandwich.md. Generate the two
# new rungs of the growth sandwich
#
#     staircase  <=  (HV-convex, b nondecreasing)  <=  (dir4, HV-convex)  <=  HV-convex
#
# by area to n = 700, and measure their growth constants against the banked
# 199-digit HV-convex mu (results/convex-polyplets.md). The proposition in
# results/hv-growth-sandwich.md predicts all four constants are equal; this is
# what would falsify it.
#
# Command:        scripts/mk_stair_growth.sh
# Target machine: gympie (laptop), 1 core.
# Predicted cost: ~3 s and <= 70 MB per series -- same PROFILE engine and the
#                 same n = 700 as the `hv` / `hvdir4` runs measured at 1.5-2.9 s
#                 and <= 65 MB in cpp/middle_kingdom_tm.cpp's header.
# Resume/kill:    no checkpointing needed at seconds of runtime; plain SIGINT.
set -e
cd "$(dirname "$0")/.."

for mode in stair hvmono; do
  /usr/bin/time -l build/middle_kingdom_tm "$mode" 700 \
      > "results/mk_${mode}_terms_n700.txt" 2> "results/mk_${mode}_n700.log"
  echo "== $mode: $(grep -c . results/mk_${mode}_terms_n700.txt) terms"
  grep -E 'real|maximum resident' "results/mk_${mode}_n700.log" || true
done

for mode in stair hvmono; do
  echo "===== growth: $mode"
  python3 experiments/convex_growth.py "results/mk_${mode}_terms_n700.txt" \
      --prec 500 --algdeg 12 --maxcoeff 100000000
done
