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
#   scripts/perimeter_min_gate.sh --deep   # + the W=13 second-source case
set -euo pipefail
cd "$(dirname "$0")/.."

DEEP=""
case "${1:-}" in --deep) DEEP=1 ;; esac

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

make -s build/perimeter_min build/g2

fail=0

# Enumerate once per (lattice, pmax) and cache.  The RED control below compares
# the SQUARE4 enumeration against the KING census, which is the same enumeration
# the real square4 check already ran -- running it twice bought nothing but a
# second full brute force.
enum_file () {                  # lattice pmax -> path to the enumeration
  local lat=$1 pmax=$2 f="$TMP/enum.$lat.$pmax.txt"
  if [ ! -s "$f" ]; then
    ./build/perimeter_min "$lat" "$pmax" -1 2>"$TMP/$lat.log" >"$f"
  fi
  printf '%s\n' "$f"
}

check () {                      # lattice pmax census
  local lat=$1 pmax=$2 census=$3 enum
  enum=$(enum_file "$lat" "$pmax")
  python3 - "$enum" "$census" "$pmax" <<'PY'
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

# Check D: sharding ONE frame's removal DFS must change nothing.  --only has a
# single frame, so the frame-level thread pool cannot help it; --threads there
# instead splits by the first two removals.  That is a second code path through
# the same dfs(), and the only thing standing between it and a silently wrong
# count is this comparison.  Same frame, same RMAX, sharded against unsharded,
# byte for byte -- the tally, the free-removal series and the header all.
echo "== check D: --only sharded == --only unsharded"
for spec in "square4 9 9 0 5" "square4 11 11 0 4" "square8 7 7 -1 4"; do
  set -- $spec
  lat=$1 w=$2 h=$3 par=$4 rm=$5
  ./build/perimeter_min "$lat" 999 "$rm" --only "$w" "$h" "$par" \
      >"$TMP/uns.txt" 2>/dev/null
  ./build/perimeter_min "$lat" 999 "$rm" --only "$w" "$h" "$par" --threads 6 \
      >"$TMP/shd.txt" 2>/dev/null
  if cmp -s "$TMP/uns.txt" "$TMP/shd.txt"; then
    echo "  ok  $lat W=$w H=$h parity=$par rmax=$rm"
  else
    echo "  SHARD MISMATCH $lat W=$w H=$h parity=$par rmax=$rm"
    diff "$TMP/uns.txt" "$TMP/shd.txt" | head -5
    fail=1
  fi
done

# RED control for check D: it must be able to SEE a difference.  Comparing two
# different RMAX values through the same comparison has to fail, else the check
# is vacuous (both files empty, cmp trivially happy).
echo "== RED control: check D must notice a real difference"
./build/perimeter_min square4 999 5 --only 9 9 0 >"$TMP/r5.txt" 2>/dev/null
./build/perimeter_min square4 999 4 --only 9 9 0 --threads 6 >"$TMP/r4.txt" 2>/dev/null
if cmp -s "$TMP/r5.txt" "$TMP/r4.txt"; then
  echo "  RED CONTROL DID NOT FIRE -- rmax=5 and rmax=4 compared equal"
  fail=1
else
  echo "  fired as expected (rmax=5 != rmax=4)"
fi

# Check E: the free-removal row against a SECOND IMPLEMENTATION.
# experiments/diamond_free_removals.py counts the same diamonds by growing the
# removal set one cell at a time and keeping what stays perimeter-neutral --
# different language, different algorithm, no shared code.  It is what confirmed
# that W=15's 8193 at j=8 was the box running out and not the model failing
# (results/perimeter.md), so it needs to stay honest.  r=5 and r=6 are
# small enough to cost a second each.
#
# Depth.  The comment above says r=5 and r=6 "cost a second each"; that was
# measured on the PYTHON side.  The C++ side of the W=13 case --
# `perimeter_min square4 999 6 --only 13 13 0` -- is ~195 s (dalby, 2026-08-24,
# traced), and the RED control below used to run that identical command a
# SECOND time: 390 s of this gate's 417 s, for one extra box width.  W=11 makes
# the same second-source statement, at 16.8 s.  --deep adds W=13 back.
echo "== check E: free-removal row == experiments/diamond_free_removals.py"
SPECS=("11 5 6")
if [ -n "$DEEP" ]; then SPECS+=("13 6 6"); fi
red_cpp="" red_jm="" red_r=""
for spec in "${SPECS[@]}"; do
  set -- $spec
  w=$1 r=$2 jm=$3
  cpp=$(./build/perimeter_min square4 999 "$jm" --only "$w" "$w" 0 2>/dev/null \
        | sed -n 's/.*free: //p')
  py=$(python3 experiments/diamond_free_removals.py "$jm" "$r" \
       | sed -n 's/^r=.*pbox=[0-9]*: //p')
  if [ -n "$cpp" ] && [ "$cpp" = "$py" ]; then
    echo "  ok  W=$w  $cpp"
  else
    echo "  SECOND-SOURCE MISMATCH W=$w"
    echo "    cpp: $cpp"
    echo "    py : $py"
    fail=1
  fi
  if [ -z "$red_cpp" ]; then red_cpp=$cpp; red_jm=$jm; red_r=$((r - 1)); fi
done

# RED control for check E: the comparison must be able to fail.  The two
# implementations agree on the diamond of radius r, so pointing the Python at
# radius r-1 has to disagree -- if it does not, the sed above is producing empty
# strings and the check is comparing nothing to nothing.
# Reuses the row check E just computed -- re-running that enumeration to compare
# it against a different radius bought nothing but a second brute force.
echo "== RED control: check E against the wrong radius (must mismatch)"
py=$(python3 experiments/diamond_free_removals.py "$red_jm" "$red_r" \
     | sed -n 's/^r=.*pbox=[0-9]*: //p')
if [ -z "$red_cpp" ]; then
  echo "  RED CONTROL CANNOT RUN -- check E produced no row"
  fail=1
elif [ "$red_cpp" = "$py" ]; then
  echo "  RED CONTROL DID NOT FIRE -- r=$((red_r + 1)) and r=$red_r compared equal"
  fail=1
else
  echo "  fired as expected (r=$((red_r + 1)) != r=$red_r)"
fi

# The runtime (H1) assert must not have tripped in either real run.
if grep -q "hypothesis=H1" "$TMP"/square8.log "$TMP"/square4.log "$TMP"/tri6.log; then
  echo "  (H1) VIOLATION reported at runtime"
  fail=1
fi

if [ "$fail" -ne 0 ]; then echo "GATE FAILED"; exit 1; fi
echo "GATE PASSED"
