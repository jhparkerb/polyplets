#!/usr/bin/env python3
"""Solvable-subfamily sweep of the king lattice; see results/subclasses.md."""
from collections import deque


def neighbors(c):
    x, y = c
    return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if dx or dy]


def canon(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def enumerate_all(nmax):
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    groups = [list(frontier)]
    while frontier:
        new = []
        for A in frontier:
            if len(A) >= nmax:
                continue
            cand = set()
            for c in A:
                for nb in neighbors(c):
                    if nb not in A:
                        cand.add(nb)
            for c in cand:
                B = canon(set(A) | {c})
                if B not in seen:
                    seen.add(B)
                    new.append(B)
        frontier = new
        if new:
            groups.append(new)
    return groups


def unimodal(h):
    i = 0
    while i + 1 < len(h) and h[i] <= h[i + 1]:
        i += 1
    while i + 1 < len(h) and h[i] >= h[i + 1]:
        i += 1
    return i == len(h) - 1


def main():
    NMAX = 8
    groups = enumerate_all(NMAX)
    counts = {k: [0] * (NMAX + 1) for k in
              ('colconvex', 'bargraph', 'stack', 'dcc', 'staircase', 'ferrers')}
    for group in groups:
        for A in group:
            d = {}
            for x, y in A:
                d.setdefault(x, []).append(y)
            c = {x: sorted(v) for x, v in d.items()}
            xs = sorted(c)
            if not all(v[-1] - v[0] + 1 == len(v) for v in c.values()):
                continue
            n = len(A)
            counts['colconvex'][n] += 1
            bots = [c[x][0] for x in xs]
            tops = [c[x][-1] for x in xs]
            hs = [len(c[x]) for x in xs]
            grounded = all(b == 0 for b in bots)
            if grounded:
                counts['bargraph'][n] += 1
                if unimodal(hs):
                    counts['stack'][n] += 1
                if all(hs[i] >= hs[i + 1] for i in range(len(xs) - 1)):
                    counts['ferrers'][n] += 1
            if all(bots[i] <= bots[i + 1] for i in range(len(xs) - 1)):
                counts['dcc'][n] += 1
                if all(tops[i] <= tops[i + 1] for i in range(len(xs) - 1)):
                    counts['staircase'][n] += 1
    assert counts['colconvex'][1:] == [1, 4, 18, 83, 385, 1788, 8305, 38575]
    assert counts['bargraph'][1:] == [2 ** i for i in range(8)]
    assert counts['ferrers'][1:] == [1, 2, 3, 5, 7, 11, 15, 22]      # A000041
    assert counts['stack'][1:] == [1, 2, 4, 8, 15, 27, 47, 79]       # A001523
    assert counts['dcc'][1:] == [1, 3, 10, 34, 116, 396, 1352, 4616]  # A007052
    assert counts['staircase'][1:] == [1, 3, 9, 28, 87, 272, 850, 2659]  # A225114
    # dcc GF check: a(n) = 4a(n-1) - 2a(n-2)
    a = counts['dcc']
    assert all(a[n] == 4 * a[n - 1] - 2 * a[n - 2] for n in range(3, NMAX + 1))
    print("king subfamily sweep: all six identities verified  OK")


if __name__ == "__main__":
    main()
