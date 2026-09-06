#!/usr/bin/env python3
"""Kill or keep idea 3 of results/closed-doors.md (the bridge-credit
sketch for a lambda UPPER bound).

The sketch, in three steps:

  1. Cut an animal into horizontal bands of height H.  Encode each band as its
     left-to-right sequence of component SHAPES plus the GAP LENGTHS between
     them.  Shapes cost mu_H^cells.
  2. A gap of length g in band i exists only because those components connect
     through band i +/- 1, which needs >= g cells bridging it there.  A cell can
     be charged by at most two gaps (one above, one below), so sum(gaps) <= 2n
     and gap entropy is ~4^n -- a constant per cell, not n^Theta(n).
  3. Credit: a bridging run of g cells has ONE shape, but mu_H^g was paid for it
     in step 1.  Since mu_13 = 6.306 > 4, the credit beats the cost.

The plan named step 2 as load-bearing and "asserted, not proved", and named the
fastest kill as: write the charging map for a two-band example with nested
bridges and see whether a cell can be charged more than twice.

This probe tests step 2 directly by brute force, and tests something the plan
did not think to test -- whether the step-1 ENCODING is injective at all, which
is a precondition for any of it being an over-count.

Usage: python3 experiments/band_charge_probe.py [MAXN]
"""

import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from g1_naive import NEIGHBORS, normalize  # noqa: E402

NBRS = NEIGHBORS["square8"]


def animals(maxn):
    """All fixed king animals with exactly maxn cells, as frozensets."""
    cur = {frozenset([(0, 0)])}
    for _ in range(2, maxn + 1):
        grown = set()
        for a in cur:
            for (x, y) in a:
                for (dx, dy) in NBRS:
                    c = (x + dx, y + dy)
                    if c not in a:
                        grown.add(normalize(a | {c}))
        cur = grown
    return cur


def components(cells):
    """King-connected components of a cell set."""
    todo, out = set(cells), []
    while todo:
        seed = todo.pop()
        comp, stack = {seed}, [seed]
        while stack:
            (x, y) = stack.pop()
            for (dx, dy) in NBRS:
                c = (x + dx, y + dy)
                if c in todo:
                    todo.remove(c)
                    comp.add(c)
                    stack.append(c)
        out.append(frozenset(comp))
    return out


def band_code(cells, H):
    """The idea-3 code: per band, the left-to-right sequence of component
    shapes (translation-normalised) plus the gap lengths between consecutive
    components.  Deliberately faithful to the sketch as written, including its
    assumption that a band's components are x-ordered."""
    bands = defaultdict(set)
    for (x, y) in cells:
        bands[y // H].add((x, y))
    code = []
    for b in sorted(bands):
        comps = components(bands[b])
        # "left-to-right": order by leftmost column, as the sketch says.
        comps.sort(key=lambda c: (min(x for x, _ in c), min(y for _, y in c)))
        shapes = tuple(normalize(c) for c in comps)
        gaps = tuple(min(x for x, _ in comps[i + 1])
                     - max(x for x, _ in comps[i]) - 1
                     for i in range(len(comps) - 1))
        code.append((b - min(bands), shapes, gaps))
    return tuple(code)


def gap_total(cells, H):
    """sum of gap lengths over all bands, counting only POSITIVE gaps (an
    overlapping pair contributes a negative number under the sketch's formula,
    which is itself the tell that the components are not x-ordered)."""
    bands = defaultdict(set)
    for (x, y) in cells:
        bands[y // H].add((x, y))
    tot, overlapping = 0, 0
    for b in bands:
        comps = components(bands[b])
        comps.sort(key=lambda c: min(x for x, _ in c))
        for i in range(len(comps) - 1):
            g = (min(x for x, _ in comps[i + 1])
                 - max(x for x, _ in comps[i]) - 1)
            if g < 0:
                overlapping += 1
            else:
                tot += g
    return tot, overlapping


def main():
    maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"king animals, n = {maxn}")
    pool = animals(maxn)
    print(f"  fixed animals: {len(pool)}")

    print("\n-- step 1: is the (shapes, gaps) code injective? --")
    print(f"{'H':>3} {'codes':>9} {'animals':>9} {'collisions':>11} "
          f"{'worst class':>12}")
    for H in (1, 2, 3, 4, 5):
        buckets = defaultdict(list)
        for a in pool:
            buckets[band_code(a, H)].append(a)
        worst = max(len(v) for v in buckets.values())
        coll = len(pool) - len(buckets)
        print(f"{H:>3} {len(buckets):>9} {len(pool):>9} {coll:>11} {worst:>12}")

    print("\n-- step 2: does sum(gaps) <= 2n hold? --")
    print(f"{'H':>3} {'max sum(gaps)':>14} {'2n':>5} {'holds':>7} "
          f"{'bands w/ x-overlap':>19}")
    for H in (1, 2, 3, 4, 5):
        mx, ov = 0, 0
        for a in pool:
            t, o = gap_total(a, H)
            mx = max(mx, t)
            ov += o
        print(f"{H:>3} {mx:>14} {2 * maxn:>5} "
              f"{'yes' if mx <= 2 * maxn else 'NO':>7} {ov:>19}")

    # The smallest collision, printed explicitly -- this is the deliverable.
    print("\n-- smallest H=1 collision, printed --")
    for n in range(2, maxn + 1):
        buckets = defaultdict(list)
        for a in animals(n):
            buckets[band_code(a, 1)].append(a)
        bad = [v for v in buckets.values() if len(v) > 1]
        if bad:
            print(f"  first at n = {n}")
            for a in sorted(bad, key=len, reverse=True)[0]:
                cells = sorted(a, key=lambda c: (c[1], c[0]))
                h = max(y for _, y in a) + 1
                w = max(x for x, _ in a) + 1
                grid = [["." for _ in range(w)] for _ in range(h)]
                for (x, y) in a:
                    grid[y][x] = "#"
                print("    " + " / ".join("".join(r) for r in grid)
                      + f"   cells={cells}")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
