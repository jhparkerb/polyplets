#!/bin/bash
# Phase 2b null control: are the high-order CANDIDATE boxes in
# scripts/dir4_perim_dfinite_sweep.sh real, or an artifact of 199 terms?
#
# The reference series is HV-convex king animals BY AREA truncated to 199
# terms. That series is known non-D-finite -- rigorously EXCLUDED at (20,20)
# and (24,24) on its full 700 terms (results/convex-polyplets.md, Phase 2a/2b).
# So any CANDIDATE it returns at 199 terms is, by construction, spurious:
# a box that 199 terms cannot decide. Run the same boxes on it and on the
# dir4 series and compare.
#
#   target: gympie, local, single-threaded
#   cost:   ~2 s total (measured: the full 40-box sweep ran in 1.96 s)
#   usage:  scripts/dir4_perim_dfinite_nullcontrol.sh 2>&1 \
#             | tee results/dir4_perim_nullcontrol.log
set -u
cd "$(dirname "$0")/.."

. "$(dirname "$0")/dir4_perim_lib.sh"
cut_null_control
echo "null control: $(wc -l < "$NULL") terms of convex polyplets by area"
echo "  (non-D-finite, EXCLUDED at (24,24) on 700 terms)"
echo

for box in "5 2" "12 12" "13 12" "11 14" "9 17" "17 9" "14 11" "6 26" \
           "4 37" "3 46" "2 62" "1 97" "30 4" "38 3" "48 2"; do
  echo "=== prec box ($box)"
  for f in "$NULL" "$DIR4"; do
    printf '  %-40s ' "$(basename "$f")"
    guess prec "$f" $box \
      | awk '/^full rank/{r=$0} /^VERDICT/{v=$2} END{print v" ("r")"}'
  done
done

for box in "12 14" "13 13" "6 27" "3 48" "30 5"; do
  echo "=== alg box ($box)"
  for f in "$NULL" "$DIR4"; do
    printf '  %-40s ' "$(basename "$f")"
    guess alg "$f" $box \
      | awk '/^full rank/{r=$0} /^VERDICT/{v=$2} END{print v" ("r")"}'
  done
done

echo "NULL CONTROL DONE"
