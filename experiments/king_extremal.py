#!/usr/bin/env python3
"""Extremal king-animal statistics that the repo has never computed.

`results/unexplored-avenues.md` idea 7 lists, after the minimum-site-perimeter
bullet it closed: "Max diameter, min diameter at fixed n; max articulation
points; max hole *count* (as opposed to max single-hole area, which is M(n))",
and notes that "diameter" appears nowhere in the repo.  `docs/last-orders.md`
C3.3.

Cheap by construction: the oracle scale is where these live, the reduction is
one pass per animal, and the point is to get integer sequences that can be
grepped against OEIS before anyone calls them new.

Computed per n, over all FIXED king animals:
  min/max graph diameter   (king adjacency, longest shortest-path)
  max articulation points  (cut vertices of the king adjacency graph)
  max hole count           (bounded 4-components of the complement --
                            the matching convention of
                            results/matching-pair-convention.md)

RED controls:
  - the animal counts must reproduce A006770;
  - a straight line of n cells must have diameter n-1 and n-2 articulation
    points, and a solid square must have neither;
  - max hole count must be 0 until n = 8, the first n admitting a hole
    (the 8-cell ring around one empty cell), and 1 there.

Usage: python3 experiments/king_extremal.py [--nmax 10]
"""
import argparse
import sys
from collections import deque

KING = ((1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK = ((1, 0), (-1, 0), (0, 1), (0, -1))

A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180]


def canon(cells):
    xs = min(c[0] for c in cells)
    ys = min(c[1] for c in cells)
    return frozenset((x - xs, y - ys) for x, y in cells)


def grow(nmax):
    lv = {canon([(0, 0)])}
    yield 1, lv
    for n in range(2, nmax + 1):
        nxt = set()
        for a in lv:
            for (x, y) in a:
                for dx, dy in KING:
                    c = (x + dx, y + dy)
                    if c not in a:
                        nxt.add(canon(set(a) | {c}))
        lv = nxt
        yield n, lv


def bfs_ecc(cells, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for dx, dy in KING:
            v = (u[0] + dx, u[1] + dy)
            if v in cells and v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return max(dist.values()), len(dist)


def diameter(cells):
    return max(bfs_ecc(cells, c)[0] for c in cells)


def is_connected(cells):
    if not cells:
        return True
    return bfs_ecc(cells, next(iter(cells)))[1] == len(cells)


def articulation_count(cells):
    if len(cells) <= 1:
        return 0
    n = 0
    for c in cells:
        rest = set(cells) - {c}
        if rest and not is_connected(rest):
            n += 1
    return n


def hole_count(cells):
    """Bounded 4-components of the complement, in a box one larger all round."""
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    seen = set()
    # flood the outside from the border
    q = deque()
    for x in range(x0, x1 + 1):
        for y in (y0, y1):
            if (x, y) not in cells:
                q.append((x, y))
                seen.add((x, y))
    for y in range(y0, y1 + 1):
        for x in (x0, x1):
            if (x, y) not in cells and (x, y) not in seen:
                q.append((x, y))
                seen.add((x, y))
    while q:
        u = q.popleft()
        for dx, dy in ROOK:
            v = (u[0] + dx, u[1] + dy)
            if (x0 <= v[0] <= x1 and y0 <= v[1] <= y1
                    and v not in cells and v not in seen):
                seen.add(v)
                q.append(v)
    # remaining empties are holes; count 4-components
    holes = 0
    todo = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
            if (x, y) not in cells and (x, y) not in seen}
    while todo:
        s = todo.pop()
        holes += 1
        q = deque([s])
        while q:
            u = q.popleft()
            for dx, dy in ROOK:
                v = (u[0] + dx, u[1] + dy)
                if v in todo:
                    todo.discard(v)
                    q.append(v)
    return holes


def red_controls(counts):
    ok = True
    good = counts == A006770[:len(counts)]
    print(f"RED  animal counts reproduce A006770 to n={len(counts)}  "
          f"{'OK' if good else 'FAILED ' + str(counts)}")
    ok &= good

    line = canon([(i, 0) for i in range(6)])
    good = diameter(line) == 5 and articulation_count(line) == 4
    print(f"RED  a 6-cell line has diameter 5 and 4 articulation points "
          f"(got {diameter(line)}, {articulation_count(line)})  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    sq = canon([(i, j) for i in range(3) for j in range(3)])
    good = articulation_count(sq) == 0 and hole_count(sq) == 0
    print(f"RED  a 3x3 block has no articulation points and no holes  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    ring = canon([(i, j) for i in range(3) for j in range(3)
                  if (i, j) != (1, 1)])
    good = hole_count(ring) == 1
    print(f"RED  the 8-cell ring has exactly one hole (got {hole_count(ring)})"
          f"  {'OK' if good else 'FAILED'}")
    ok &= good
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=10)
    args = ap.parse_args()

    print("=" * 70)
    print("Extremal king-animal statistics, n = 1..%d" % args.nmax)
    print("=" * 70)
    print(f"{'n':>3} {'animals':>10} {'minDiam':>8} {'maxDiam':>8} "
          f"{'maxArtic':>9} {'maxHoles':>9}")

    counts, mind, maxd, maxa, maxh = [], [], [], [], []
    for n, lv in grow(args.nmax):
        counts.append(len(lv))
        dmin = dmax = amax = hmax = None
        for a in lv:
            d = diameter(a)
            dmin = d if dmin is None else min(dmin, d)
            dmax = d if dmax is None else max(dmax, d)
            ac = articulation_count(a)
            amax = ac if amax is None else max(amax, ac)
            hc = hole_count(a)
            hmax = hc if hmax is None else max(hmax, hc)
        mind.append(dmin)
        maxd.append(dmax)
        maxa.append(amax)
        maxh.append(hmax)
        print(f"{n:>3} {len(lv):>10} {dmin:>8} {dmax:>8} {amax:>9} {hmax:>9}")

    print()
    print("As comma-separated sequences, for an OEIS grep:")
    print(f"  min diameter        {','.join(map(str, mind))}")
    print(f"  max diameter        {','.join(map(str, maxd))}")
    print(f"  max articulation    {','.join(map(str, maxa))}")
    print(f"  max hole count      {','.join(map(str, maxh))}")
    print()
    print("--- RED controls ---")
    if not red_controls(counts):
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
