#!/usr/bin/env python3
"""Free removals from a square4 diamond, counted directly.

A SECOND SOURCE for the free-removal row of cpp/perimeter_min.cpp, which reaches
size j by enumerating every subset of size <= j and filtering.  This grows the
removal set one cell at a time and keeps only what stays free, so the two share
no code and no strategy; agreement is a real cross-check, and check E of
scripts/perimeter_min_gate.sh holds them to it.

Growing rather than filtering is also what makes deep radii affordable.  It is
what settled the j=8 term: W=15 measured 8193 against the cone model's 8229, and
the question was whether the model was wrong or the box too small.  This script
reproduces both C++ rows exactly and then reaches W=19, where j=8 is 8229 again
-- so the box was too small.  A radius-r diamond holds free removals through
j = r and undercuts from j = r+1 on.  See results/perimeter.md.

Removing cell c from animal A changes the site perimeter by

    delta = [c still has a filled neighbor]  -  #{empty q adjacent to A only
                                                  through c}

so the removal is FREE exactly when delta = 0.  That is O(1), where recounting
the perimeter is O(cells), and it is the whole speed difference.

    python3 experiments/diamond_free_removals.py JMAX RADIUS [RADIUS ...]
"""
import sys
from collections import deque

NBR = ((1, 0), (-1, 0), (0, 1), (0, -1))


def diamond(r):
    return frozenset((x, y) for x in range(-r, r + 1)
                     for y in range(-r, r + 1) if abs(x) + abs(y) <= r)


def siteperim(cells):
    e = set()
    for (x, y) in cells:
        for dx, dy in NBR:
            q = (x + dx, y + dy)
            if q not in cells:
                e.add(q)
    return len(e)


def connected(cells):
    it = iter(cells)
    s = next(it)
    seen = {s}
    q = deque([s])
    while q:
        x, y = q.popleft()
        for dx, dy in NBR:
            p = (x + dx, y + dy)
            if p in cells and p not in seen:
                seen.add(p)
                q.append(p)
    return len(seen) == len(cells)


def free(A, c):
    """Is removing c from A perimeter-neutral?"""
    keeps = 0
    lost = 0
    for dx, dy in NBR:
        q = (c[0] + dx, c[1] + dy)
        if q in A:
            keeps = 1
        else:
            # q is empty: does it touch A anywhere but c?
            other = False
            for ex, ey in NBR:
                s = (q[0] + ex, q[1] + ey)
                if s != c and s in A:
                    other = True
                    break
            if not other:
                lost += 1
    return keeps == lost


def run(r, jmax, verbose=True):
    D = diamond(r)
    P0 = siteperim(D)
    level = {frozenset()}
    counts = [1]
    for j in range(1, jmax + 1):
        nxt = set()
        for S in level:
            A = D - S
            for c in A:
                if not free(A, c):
                    continue
                A2 = A - {c}
                if not A2 or not connected(A2):
                    continue
                nxt.add(S | {c})
        level = nxt
        counts.append(len(level))
        if verbose:
            print("  r=%d j=%d -> %d" % (r, j, len(level)), flush=True)
    return len(D), P0, counts


if __name__ == "__main__":
    jmax = int(sys.argv[1])
    for r in [int(a) for a in sys.argv[2:]]:
        n, p, c = run(r, jmax)
        print("r=%d W=%d cells=%d pbox=%d: %s"
              % (r, 2 * r + 1, n, p, " ".join(str(v) for v in c)), flush=True)
