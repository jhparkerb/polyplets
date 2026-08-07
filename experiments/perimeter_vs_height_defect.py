#!/usr/bin/env python3
"""Two defect gradings of the same sequence: perimeter vs bounding-box height.

Barequet, Magal, Asinowski and Zheng grade fixed polyominoes by SITE-PERIMETER
defect: p <= 2n + 2 always, and k := 2n + 2 - p. They produce a rational
generating function for each fixed k, hence a quasi-polynomial count -- their
k = 3 formula carries a (-1)^n term.

We grade the same polyominoes by BOUNDING-BOX HEIGHT defect: H <= n always, and
k := n - H, giving T(n, n-k) = P_k(n), a plain polynomial from the sharp onset
n >= 2k+1 (docs/proofs/universal-diagonal-law.md, and OEIS A308359).

Both are refinements of A001168, so both marginals sum to it. This script asks
the obvious next question -- do the DIAGONALS agree? -- by computing both
statistics on the same enumeration.

Answer: no, except at k <= 1.

  k = 0  differs by convention only: 2 sticks by perimeter (horizontal and
         vertical), 1 by height (only the vertical one has H = n).
  k = 1  agrees exactly, both 4(n-2), at every n. Different sets: theirs is
         the one-bend paths, ours is the vertical near-sticks with one doubled
         row. Same count, no bijection offered here.
  k = 2  agrees only at n = 4 and diverges after: 28 vs 31, 60 vs 68, ...
  k = 3  diverges immediately.

So the two gradings are genuinely different statistics that happen to share a
low-order coincidence, not two views of one array. The interesting asymmetry is
that the height grading gives plain polynomials where the perimeter grading
gives quasi-polynomials.

Usage: python3 -m experiments.perimeter_vs_height_defect
"""
import sys
from collections import defaultdict

STEPS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
NMAX = 11
A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268]


def main():
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        return frozenset((x - mx, y - my) for x, y in cells)

    def stats(q):
        per = len({(x + dx, y + dy) for x, y in q for dx, dy in STEPS4} - set(q))
        h = max(y for _, y in q) - min(y for _, y in q) + 1
        return per, h

    A = defaultdict(int)          # by site perimeter
    T = defaultdict(int)          # by bounding-box height
    start = frozenset({(0, 0)})
    p, h = stats(start)
    A[(1, p)] += 1
    T[(1, h)] += 1
    seen = {canon(start)}
    frontier = list(seen)
    while frontier:
        nxt = []
        for a in frontier:
            if len(a) >= NMAX:
                continue
            for c in a:
                for dx, dy in STEPS4:
                    b = (c[0] + dx, c[1] + dy)
                    if b in a:
                        continue
                    q = canon(a | {b})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.append(q)
                    per, hh = stats(q)
                    A[(len(q), per)] += 1
                    T[(len(q), hh)] += 1
        frontier = nxt

    print("[1] both gradings refine A001168")
    ok = True
    for n in range(1, NMAX + 1):
        sa = sum(v for (m, _), v in A.items() if m == n)
        st = sum(v for (m, _), v in T.items() if m == n)
        if not (sa == st == A001168[n - 1]):
            print(f"    FAIL at n = {n}: {sa}, {st}, want {A001168[n - 1]}")
            ok = False
    if ok:
        print(f"    OK, n <= {NMAX}, both marginals sum to A001168")

    print("\n[2] the diagonals side by side")
    print("      n |   perimeter defect A(n, 2n+2-k)   |   height defect T(n, n-k)")
    print("        |   k=0    k=1     k=2     k=3      |   k=0    k=1     k=2     k=3")
    agree = defaultdict(list)
    for n in range(3, NMAX + 1):
        a = [A[(n, 2 * n + 2 - k)] for k in range(4)]
        t = [T[(n, n - k)] for k in range(4)]
        for k in range(4):
            agree[k].append(a[k] == t[k])
        print(f"     {n:>2} | {a[0]:>5} {a[1]:>6} {a[2]:>7} {a[3]:>7}   | "
              f"{t[0]:>5} {t[1]:>6} {t[2]:>7} {t[3]:>7}")

    print("\n[3] where they agree")
    for k in range(4):
        rows = agree[k]
        n0 = 3
        which = [n0 + i for i, v in enumerate(rows) if v]
        if all(rows):
            print(f"    k={k}: agree at EVERY n in 3..{NMAX}")
        elif not which:
            print(f"    k={k}: agree nowhere")
        else:
            print(f"    k={k}: agree only at n = {which}")

    # the k=1 coincidence, stated as a formula rather than a table
    bad = [n for n in range(3, NMAX + 1)
           if not (A[(n, 2 * n + 1)] == T[(n, n - 1)] == 4 * (n - 2))]
    if bad:
        print(f"    FAIL: k=1 is not 4(n-2) at {bad}")
        ok = False
    else:
        print(f"    k=1 is 4(n-2) under BOTH gradings, every n in 3..{NMAX}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
