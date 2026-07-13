#!/usr/bin/env python3
"""Square-lattice (b = 1) instance of the universal diagonal law
(docs/proofs/universal-diagonal-law.md): polyomino diagonals are plain
polynomials of degree k from onset n >= 2k+1, with density 4 = 2^2.
King (b=3) and hex (b=2) instances are checked by
diagonal_law_proof_check.py and hex_gas.py respectively.
"""
from collections import defaultdict

A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446]


def main():
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        return frozenset((x - mx, y - my) for x, y in cells)

    def neighbors(c):
        x, y = c
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    NMAX = 10
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    T = defaultdict(int)
    T[(1, 1)] = 1
    tot = {1: 1}
    while frontier:
        new = []
        for A in frontier:
            if len(A) >= NMAX:
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
            n = len(new[0])
            tot[n] = len(new)
            for A in new:
                H = max(y for _, y in A) - min(y for _, y in A) + 1
                T[(n, H)] += 1
    assert [tot[n] for n in sorted(tot)] == A001168
    for k in range(4):
        vals = [T[(H + k, H)] for H in range(k + 1, NMAX + 1 - k)]
        d = vals[:]
        for _ in range(k):
            d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
        assert len(set(d)) == 1, (k, d)
    assert [T[(H + 1, H)] for H in range(2, 9)] == [4 * (H - 1)
                                                    for H in range(2, 9)]
    print("square lattice (b=1): totals == A001168; diagonals polynomial "
          "deg k from onset; P_1(n) = 4(n-2)  OK")


def polyiamond_probe():
    """Periodic extension: triangular lattice diagonal structure."""
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        dx = mx - ((mx + my) % 2)
        return frozenset((x - dx, y - my) for x, y in cells)

    def neighbors(c):
        x, y = c
        out = [(x - 1, y), (x + 1, y)]
        out.append((x, y - 1) if (x + y) % 2 == 0 else (x, y + 1))
        return out

    NMAX = 12
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    T = defaultdict(int)
    T[(1, 1)] = 1
    tot = {1: 1}
    while frontier:
        new = []
        for A in frontier:
            if len(A) >= NMAX:
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
            n = len(new[0])
            tot[n] = len(new)
            for A in new:
                H = max(y for _, y in A) - min(y for _, y in A) + 1
                T[(n, H)] += 1
    # A001420 from n=2 (single-triangle orientation seed difference at n=1)
    assert [tot[n] for n in range(2, 13)] == [3, 6, 14, 36, 94, 250, 675,
                                              1838, 5053, 14016, 39169]
    assert all(T[(2 * H - 2, H)] == 2 ** (H - 2) for H in range(2, 7))
    assert all(T[(2 * H - 1, H)] == H * 2 ** (H - 1) for H in range(2, 7))
    from fractions import Fraction as F
    q = [F(T[(2 * H + 2 - 2 + 0, H)], 1) for H in range(3, 7)]
    vals = [F(T[(2 * H, H)], 2 ** H) for H in range(3, 7)]
    d2 = [vals[i + 2] - 2 * vals[i + 1] + vals[i] for i in range(2)]
    assert len(set(d2)) == 1, d2
    print("polyiamond periodic extension: T(2H-2,H)=2^(H-2), "
          "T(2H-1,H)=H*2^(H-1), k=2 quadratic in T/2^H  OK")


if __name__ == "__main__":
    main()
    polyiamond_probe()
