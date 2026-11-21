#!/usr/bin/env python3
"""Check the printed formulas of Asinowski, Barequet & Zheng, "Polycubes with
small perimeter defect", Ann. Comb. 26 (2022) 997-1020, against each other and
against a direct count.  Serves the perimeter-defect note in
literature/MISSING.md ("Searches on record"); results/perimeter.md uses only
their Proposition 2.4, which passes.

    python3 experiments/abz_defect_formula_check.py [N3]     # N3 = 3D size, default 13 (~30 s)

B_d(n,k) = number of fixed d-dimensional polycubes of n cells whose site
perimeter is 2(d-1)n + 2 - k.  The count is Redelmeier's enumeration, cut off
when the defect passes 3: adding a cell fills one perimeter cell and creates at
most 2d-1, so the defect never decreases along a growth path.
"""
import sys
from fractions import Fraction as F
from math import comb


def P(c0=0, c1=0, c2=0, c3=0, s0=0, s1=0):
    """c0 + c1 n + c2 n^2 + c3 n^3 + (-1)^n (s0 + s1 n)."""
    return [F(c0), F(c1), F(c2), F(c3), F(s0), F(s1)]


def add(*ps):
    return [sum(x) for x in zip(*ps)]


def mul(k, p):
    return [k * x for x in p]


def ev(p, n):
    return p[0] + p[1] * n + p[2] * n * n + p[3] * n ** 3 + (-1) ** n * (p[4] + p[5] * n)


# Table 1 (cases for B_2(n,3)), rows (a.1)-(h.3) in their n >= 9 form.
TABLE1 = [
    P(F(-471, 2), F(481, 6), -9, F(1, 3), F(-9, 2), F(1, 2)), P(F(111, 2), -15, 1, 0, F(-15, 2), 1),
    P(F(-67, 2), F(211, 12), -3, F(1, 6), F(3, 2), F(-1, 4)), P(-64, 8), P(8),
    P(-32, F(104, 3), -12, F(4, 3)), P(8), P(-16, F(52, 3), -6, F(2, 3)),
    P(-160, F(296, 3), -20, F(4, 3)), P(-40, 8), P(-48, 8),
    P(-160, F(296, 3), -20, F(4, 3)), P(-48, 8), P(-42, 8),
    P(-160, F(296, 3), -20, F(4, 3)), P(-48, 8), P(-42, 8)]
PROP24 = P(F(-2107, 2), F(1947, 4), -89, F(13, 2), F(-21, 2), F(5, 4))
# Table 2 (cases for B_3(n,3)), rows (i)-(xxvii) in their n >= 12 form.
TABLE2 = [
    P(F(-1413, 2), F(481, 2), -27, 1, F(-27, 2), F(3, 2)), P(F(333, 2), -45, 3, 0, F(-45, 2), 3),
    P(F(-201, 2), F(211, 4), -9, F(1, 2), F(9, 2), F(-3, 4)), P(-192, 24), P(0),
    P(-480, 296, -60, 4), P(-120, 24), P(-144, 24), P(24), P(-96, 104, -36, 4),
    P(-480, 296, -60, 4), P(-144, 24), P(-120, 24), P(24), P(-48, 52, -18, 2),
    P(-480, 296, -60, 4), P(-144, 24), P(-120, 24), P(-960, 592, -120, 8), P(-240, 48),
    P(-288, 48), P(-96, 104, -36, 4), P(-96, 104, -36, 4), P(-192, 208, -72, 8),
    P(-192, 208, -72, 8), P(-96, 104, -36, 4), P(24, -20, 4)]
PROP26 = P(F(-10593, 2), F(11425, 4), -635, F(111, 2), F(-63, 2), F(15, 4))
# Proposition 2.7(4): the d-choose-2, d-choose-3 terms as printed.
P27_D2 = P(F(-2091, 2), F(1947, 4), -89, F(13, 2), F(-21, 2), F(5, 4))
P27_D3 = P(-2328, 1460, -356, 32)


def census(d, N, K):
    """{(n, k): count} for fixed d-dimensional polycubes, n <= N, defect k <= K."""
    dirs = [tuple((s if i == j else 0) for i in range(d)) for j in range(d) for s in (1, -1)]
    origin = (0,) * d

    def nb(c):
        return [tuple(a + b for a, b in zip(c, v)) for v in dirs]

    res, occ, seen = {}, set(), {origin}

    def rec(untried, n):
        while untried:
            c = untried.pop()
            occ.add(c)
            k = 2 * (d - 1) * (n + 1) + 2 - len({q for x in occ for q in nb(x) if q not in occ})
            if k <= K:
                res[(n + 1, k)] = res.get((n + 1, k), 0) + 1
                if n + 1 < N:
                    new = [q for q in nb(c) if q not in seen and q > origin]
                    seen.update(new)
                    rec(untried + new, n + 1)
                    seen.difference_update(new)
            occ.discard(c)

    rec([origin], 0)
    return res


def main():
    n3 = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    fails = []
    assert [sum(v for (n, _), v in census(3, 7, 10 ** 9).items() if n == m) for m in range(1, 8)] \
        == [1, 3, 15, 86, 534, 3481, 23502], "census does not reproduce A001931"

    r2 = census(2, 16, 3)
    print("d=2, k=3:  n  count  Prop 2.4  Table 1 sum  Prop 2.7(4)")
    for n in range(9, 17):
        b = r2[(n, 3)]
        print(f"  {n:2d} {b:6d} {ev(PROP24, n)!s:>6} {ev(add(*TABLE1), n)!s:>6} {ev(P27_D2, n)!s:>6}")
        if b != ev(PROP24, n):
            fails.append(f"Prop 2.4 at n={n}")
    r3 = census(3, n3, 3)
    print("d=3, k=2:  n  count  Prop 2.5(3)  Prop 2.7(3) as printed")
    for n in range(6, n3 + 1):
        printed = 3 * (8 * comb(n - 2, 2) + 4 * comb(n - 4, 2) + 8) + 24 * comb(n - 4, 2)
        print(f"  {n:2d} {r3[(n, 2)]:6d} {288 - 174 * n + 30 * n * n:6d} {printed:6d}")
        if r3[(n, 2)] != 288 - 174 * n + 30 * n * n:
            fails.append(f"Prop 2.5(3) at n={n}")
    print("d=3, k=3:  n  count  Prop 2.6  excess  24(n-4)  Prop 2.7(4)")
    for n in range(9, n3 + 1):
        b, f = r3[(n, 3)], ev(PROP26, n)
        print(f"  {n:2d} {b:6d} {f!s:>6} {f - b!s:>4} {24 * (n - 4):4d} {ev(add(mul(3, P27_D2), P27_D3), n)!s:>6}")
        if f - b != 24 * (n - 4):
            fails.append(f"Prop 2.6 excess is not 24(n-4) at n={n}")
    print("Table 2 sum == Prop 2.6:", add(*TABLE2) == PROP26,
          "  Table 1 sum - Prop 2.4 (constant):", add(*TABLE1)[0] - PROP24[0])
    print("FAIL: " + "; ".join(fails) if fails else
          "OK: Prop 2.4 and 2.5(3) match the count; Prop 2.6 exceeds it by 24(n-4)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
