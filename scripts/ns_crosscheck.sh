#!/usr/bin/env bash
# ns_crosscheck.sh — cell-by-cell compare new-engine per-height rows against the
# old engine's salvaged h<H>.out. This is the independent T(n,H) cross-check that
# validates a(21)'s lower rows: for every height in the overlap the two engines
# must be byte-identical, cell for cell, at every n.
#
# Both engines write h<H>.out as "n value" lines (n=1..maxn). The old rows live
# on ayr at runs/a21fold/h1..h16.out (complete H1-16; H17/H18 land when ayr's old
# run finishes, extending the overlap). Stage them next to the new run first:
#   rsync -a ayr:~/src/polyominoes/runs/a21fold/h{1..16}.out  old_rows/
# then point this at the new run's --per-height-out dir and old_rows/.
#
# Usage: ns_crosscheck.sh NEW_DIR OLD_DIR [HEIGHTS_LO HEIGHTS_HI]   (default 1 16)
set -euo pipefail

NEW="${1:?usage: ns_crosscheck.sh NEW_DIR OLD_DIR [LO HI]}"
OLD="${2:?old-rows dir}"
LO="${3:-1}"
HI="${4:-16}"

fail=0; checked=0; missing=0
for H in $(seq "$LO" "$HI"); do
  n="$NEW/h${H}.out"; o="$OLD/h${H}.out"
  if [ ! -f "$n" ]; then echo "H=$H  SKIP (no new $n)"; missing=$((missing+1)); continue; fi
  if [ ! -f "$o" ]; then echo "H=$H  SKIP (no old $o)"; missing=$((missing+1)); continue; fi
  checked=$((checked+1))
  if diff -q "$n" "$o" >/dev/null; then
    echo "H=$H  MATCH"
  else
    echo "H=$H  MISMATCH (< old, > new):"
    diff "$o" "$n" | sed 's/^/    /'
    fail=$((fail+1))
  fi
done

echo "---"
echo "crosscheck heights $LO..$HI: checked=$checked mismatch=$fail missing=$missing"
if [ "$fail" -eq 0 ] && [ "$missing" -eq 0 ]; then
  echo "CROSSCHECK PASS"
  exit 0
fi
echo "CROSSCHECK FAIL"
exit 1
