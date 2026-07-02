#!/bin/bash
# combine_a27.sh -- assemble a(27) from the dalby+ayr split halves.
# Run ON dalby AFTER both scripts/dalby_a27.sh and scripts/ayr_a27.sh finish.
#
# dalby owns H1,H2,H16,H17-27; ayr owns H3-15. combine --require-cover fails
# unless H1..27 are each present exactly once, so a missing/overlapping height
# is caught here rather than silently mis-summed.
#
# --compare will FALSE-FAIL past a20 (b-file stops at a20); ignore its verdict
# for a21-27 and validate by hand (below) like a24/a25/a26 did.
set -e
cd ~/src/polyominoes-ns
DALBY_PERH=runs/ns_a27/perheight            # dalby wrote here directly
AYR_PERH=runs/ns_a27/ayr_perheight          # rsync target for ayr's rows
OUT=results/ns_a27
mkdir -p "$AYR_PERH" "$OUT"

echo "=== pulling ayr's per-height rows: $(date -Iseconds) ==="
rsync -av ayr:~/src/polyominoes-ns/runs/ns_a27/perheight/ "$AYR_PERH/"

echo "=== combine (require-cover H1..27): $(date -Iseconds) ==="
./build/ns/combine --in "$DALBY_PERH,$AYR_PERH" --maxn 27 --require-cover \
  --out "$OUT/triangle.txt" 2>&1 | tee "$OUT/combine.log"

echo "=== a(27) = $(awk '$1==27{print $2}' "$OUT/triangle.txt") ==="
echo "VALIDATE BY HAND: a1-20 vs fixtures/b006770.txt; a21-26 vs"
echo "results/ns_a2{1,2,3,4,5,6}/ ; growth a27/a26 should be ~6.7-6.8."
