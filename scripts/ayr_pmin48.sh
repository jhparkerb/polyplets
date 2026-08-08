#!/usr/bin/env bash
# PURPOSE: restart the square8 (king) min-end site-perimeter census at p=48 that
#   the 2026-08-07 power cut destroyed, on the resumable per-frame driver rather
#   than the monolithic run that lost 3.9 h and wrote a 0-byte file.
#   Feeds the minimum end of results/perimeter-both-ends.md -- the king partner
#   to the square4 deep boxes running on dalby -- and through it paper L6.
#
# COMMAND:  scripts/ayr_pmin48.sh          (THREADS=32 by default)
# TARGET:   ayr, 32 cores / 78 GB. RAM is a few MB per thread; pure CPU.
# COST:     5-8 h at 32 threads, extrapolated from p=44 (3885 s, 9.3e9 nodes)
#           and the dead p=48 run (16.6e9 nodes at 14092 s). Unmeasured beyond
#           that -- p=48 has never finished.
#
# It runs three things in order and stops at the first failure:
#   1. both perimeter_min gates, so the native ayr build is checked here and not
#      assumed from gympie;
#   2. a REPRODUCTION CHECK -- the sharded driver re-derives the banked p=40
#      census, and git itself is the diff: the tracked file may change in its
#      git= stamp line and nowhere else. A sharded run that cannot reproduce a
#      banked census has no business producing a new one;
#   3. the p=48 census.
#
# RESUME: re-run this script. Step 3 skips every frame already complete. Steps
#   1 and 2 are cheap and are deliberately re-run each time.
set -euo pipefail
cd "$(dirname "$0")/.."

T=${THREADS:-32}
BANKED=results/perimmin_square8_p40_r6.txt
echo "=== ayr p48 restart, threads=$T, $(date -Is)"

echo "=== [1/3] gates"
make gate-perimeter-min gate-perimeter-min-shard

echo "=== [2/3] reproduction check: sharded p=40 vs the banked census"
./scripts/perimeter_min_sharded.sh square8 40 6 "$T"
changed=$(git diff -U0 -- "$BANKED" | grep -c "^[+-][^+-]" || true)
offending=$(git diff -U0 -- "$BANKED" | grep "^[+-][^+-]" | grep -vc "perimeter_min lattice=" || true)
if [ "$changed" != 2 ] || [ "$offending" != 0 ]; then
  echo "FATAL: sharded p=40 does not reproduce the banked census"
  git diff -- "$BANKED" | head -40
  exit 6
fi
echo "--- p=40 reproduced exactly (only the git= stamp differs)"
git checkout -- "$BANKED"

echo "=== [3/3] p=48 census"
./scripts/perimeter_min_sharded.sh square8 48 6 "$T"
echo "AYR_PMIN48_DONE $(date -Is)"
