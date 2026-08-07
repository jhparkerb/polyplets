#!/usr/bin/env bash
# Gate for build/perimeter_min (cpp/perimeter_min.cpp).
#
# The enumerator is complete only under hypothesis (H1) -- every animal has
# perimeter at least that of its own filled frame bounding box -- and only for
# removal counts within RMAX.  Both are checked here where they CAN be checked:
# run with RMAX unbounded on small boxes, where the program degenerates to a
# complete brute force, and compare cell for cell against build/g2's --siteperim
# census, an entirely different search (growth, not complementation).
#
# A missing animal is what an (H1) violation would look like from outside, so
# this is the real test of the completeness argument, not the runtime assert.
#
#   scripts/perimeter_min_gate.sh          # prints GATE PASSED or exits nonzero
set -euo pipefail
cd "$(dirname "$0")/.."

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

make -s build/perimeter_min build/g2

fail=0

check () {                      # lattice pmax census
  local lat=$1 pmax=$2 census=$3
  ./build/perimeter_min "$lat" "$pmax" -1 2>"$TMP/$lat.log" >"$TMP/$lat.txt"
  python3 - "$TMP/$lat.txt" "$census" "$pmax" <<'PY'
import sys
from collections import defaultdict
enum_path, census_path, pmax = sys.argv[1], sys.argv[2], int(sys.argv[3])

def read(path):
    t = defaultdict(int)
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        n, p, c = (int(f) for f in line.split())
        t[(n, p)] += c
    return t

e, g = read(enum_path), read(census_path)
nmax = max(n for n, _ in g)
keys = {k for k in set(e) | set(g) if k[1] <= pmax and k[0] <= nmax}
bad = [(k, e.get(k, 0), g.get(k, 0)) for k in sorted(keys) if e.get(k, 0) != g.get(k, 0)]
if bad:
    print("  MISMATCH (n,p): enum vs g2")
    for k, a, b in bad[:20]:
        print("   ", k, a, b)
    sys.exit(1)
print("  %d (n,p) cells agree, p<=%d n<=%d" % (len(keys), pmax, nmax))
PY
}

echo "== square8 (king) vs results/siteperim_square8_n14.txt"
check square8 18 results/siteperim_square8_n14.txt || fail=1

echo "== square4 (rook, rotated frame) vs results/siteperim_square4_n20.txt"
check square4 14 results/siteperim_square4_n20.txt || fail=1

echo "== tri6 (hex, 3-functional hexagonal hull) vs results/siteperim_tri6_n12.txt"
check tri6 16 results/siteperim_tri6_n12.txt || fail=1

# RED control: the rotated square4 frame is a genuinely different lattice from
# square8, not a relabelling.  Comparing square4's enumeration against the KING
# census must FAIL -- if it passes, the two modes are computing the same thing
# and the square4 path is not doing what its header claims.
echo "== RED control: square4 enumeration vs the KING census (must mismatch)"
if check square4 14 results/siteperim_square8_n14.txt >/dev/null 2>&1; then
  echo "  RED CONTROL DID NOT FIRE -- square4 mode matched the king census"
  fail=1
else
  echo "  fired as expected (square4 != square8)"
fi

# Wide boxes.  The connectivity mask used to be a u128, so any frame with more
# than 128 cells was dropped by build() -- and dropped SILENTLY, indistinguishably
# from "not a legal frame bounding box", which in a full sweep is a missing
# animal rather than an error.  W=17 is the diamond that carries the j=7
# free-removal term (145 cells), so it is the case that mattered.
#
# The free-removal prefix is checked, not just the cell count: 1, 4, 18 is
# phi_2^4, which is what a working wide mask must reproduce.  RMAX=2 keeps it
# to C(145,2) subsets, so this costs nothing.
echo "== wide box: square4 W=17 (145 cells) must enumerate, not be skipped"
wide=$(./build/perimeter_min square4 999 2 --only 17 17 0 2>/dev/null | grep '^# box' || true)
echo "  $wide"
case "$wide" in
  *"cells=145"*"free: 1 4 18"*) echo "  ok  145-cell frame enumerated, free prefix is phi_2^4" ;;
  *) echo "  WIDE BOX FAILED -- got: ${wide:-<no box line at all>}"; fail=1 ;;
esac

# RED control, and the fail-closed half of the same bug: a frame that exceeds
# the mask must be REFUSED LOUDLY.  Silently returning nothing is what the u128
# limit used to do, and it is the failure mode this gate exists to prevent.
echo "== RED control: a frame over the mask limit must fail closed, not silently"
if ./build/perimeter_min square4 999 1 --only 33 33 0 >/dev/null 2>"$TMP/toobig.log"; then
  echo "  RED CONTROL DID NOT FIRE -- an over-limit frame exited 0"
  fail=1
elif ! grep -q "over the connectivity mask" "$TMP/toobig.log"; then
  echo "  RED CONTROL DID NOT FIRE -- nonzero exit but no explanatory message"
  fail=1
else
  echo "  fired as expected (refused, with a reason)"
fi

# The runtime (H1) assert must not have tripped in either real run.
if grep -q "hypothesis=H1" "$TMP"/square8.log "$TMP"/square4.log "$TMP"/tri6.log; then
  echo "  (H1) VIOLATION reported at runtime"
  fail=1
fi

if [ "$fail" -ne 0 ]; then echo "GATE FAILED"; exit 1; fi
echo "GATE PASSED"
