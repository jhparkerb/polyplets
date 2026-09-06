#!/usr/bin/env python3
"""Brute-force enumerator of diagonal-mirror-symmetric king animals.

Grows connected sets by symmetric orbits {(x,y),(y,x)}, canonicalizes by
diagonal translation, classifies by (S, n) with box exactly SxS. Validated
against the banked dm diagonal law (d(S,S)=2; d(S,S+1)=S+6/S+7; the k=2
quadratics) for S <= 10. Ground truth for results/symmetry-classes.md.
"""
from collections import deque, defaultdict


def neighbors(c):
    x, y = c
    return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if dx or dy]


def enumerate_sym(nmax):
    """All diagonal-mirror-symmetric king animals with <= nmax cells,
    up to diagonal translation."""
    def canon(cells):
        m = min(min(x for x, _ in cells), min(y for _, y in cells))
        return frozenset((x - m, y - m) for x, y in cells)

    seen = set()
    frontier = [canon({(0, 0)}), canon({(0, 1), (1, 0)})]
    seen.update(frontier)
    out = []
    while frontier:
        new = []
        for A in frontier:
            out.append(A)
            if len(A) >= nmax:
                continue
            cand = set()
            for c in A:
                for nb in neighbors(c):
                    if nb not in A:
                        cand.add(nb)
            done = set()
            for (x, y) in cand:
                orb = frozenset({(x, y), (y, x)})
                if orb in done:
                    continue
                done.add(orb)
                if len(A) + len(orb) > nmax:
                    continue
                B = set(A) | set(orb)
                if not all(any(nb in B and nb != c2 for nb in neighbors(c2))
                           for c2 in orb):
                    continue
                Bc = canon(B)
                if Bc in seen:
                    continue
                cells = set(Bc)
                s0 = next(iter(cells))
                vis = {s0}
                q = deque([s0])
                while q:
                    c2 = q.popleft()
                    for nb in neighbors(c2):
                        if nb in cells and nb not in vis:
                            vis.add(nb)
                            q.append(nb)
                if len(vis) != len(cells):
                    continue
                seen.add(Bc)
                new.append(Bc)
        frontier = new
    return out


def d_counts(nmax):
    counts = defaultdict(int)
    for A in enumerate_sym(nmax):
        xs = [x for x, _ in A]
        ys = [y for _, y in A]
        S = max(xs) - min(xs) + 1
        if max(ys) - min(ys) + 1 != S:
            continue
        counts[(S, len(A))] += 1
    return counts


if __name__ == "__main__":
    counts = d_counts(12)
    for S in range(2, 11):
        assert counts[(S, S)] == 2, (S, counts[(S, S)])
    for S in range(4, 10):
        law = S + 6 if S % 2 == 0 else S + 7
        if S >= (4 if S % 2 == 0 else 5):
            assert counts[(S, S + 1)] == law, (S, counts[(S, S + 1)], law)
    for S in range(6, 10):
        law = (S * S) // 2 + 7 * S + 12 if S % 2 == 0 else (S * S + 12 * S + 27) // 2
        if S >= (6 if S % 2 == 0 else 7):
            assert counts[(S, S + 2)] == law, (S, counts[(S, S + 2)], law)
    print("dm enumerator matches the banked diagonal law (S<=9, k<=2)  OK")
