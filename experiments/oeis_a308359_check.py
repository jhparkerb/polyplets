#!/usr/bin/env python3
"""OEIS A308359's open conjecture is a corollary of the universal diagonal law.

A308359 (R. J. Mathar, 2019) is the triangle of FIXED polyominoes with n cells
by bounding-box width, height free -- the transpose of our own T(n, H). It
records

    T(n, n-1) = 4n - 8          for n >= 3      (proved there)
    T(n, n-2) = 8n^2 - 51n + 86 for n >= 5      (CONJECTURE)

docs/proofs/universal-diagonal-law.md Theorem A says that for every row-local
lattice, T(n, n-k) = P_k(n) * b^(n-1-3k) for n >= 2k+1 with deg P_k <= k. The
square lattice is the b = 1 case, so the diagonals are plain polynomials of
degree <= k from onset n >= 2k+1. For k = 2 that is: a quadratic, valid from
n = 5. Three values then pin it, and the conjecture follows.

This script does the pinning from our own enumeration rather than from OEIS's
numbers, and checks the theorem's teeth:

  1. Enumerate fixed polyominoes to NMAX by bounding-box height. Totals must
     equal A001168 (the enumeration is not assumed correct).
  2. k = 1: the diagonal equals 4n - 8 from n = 3 = 2k+1, matching A308359's
     proved formula -- a check that our triangle IS their triangle transposed.
  3. k = 2: interpolate a quadratic through the FIRST three on-onset values
     (n = 5, 6, 7) and confirm it reproduces every later value. This is the
     proof step: degree <= 2 is a theorem, so three points determine it.
  4. RED control on degree: a LINEAR fit through n = 5, 6 must fail at n = 7,
     else "degree 2" is vacuous.
  5. RED control on onset: the quadratic must FAIL at n = 2k = 4, since the
     onset n >= 2k+1 is sharp. If it happened to hold there, the onset claim
     would be untested by this data.

Usage: python3 -m experiments.oeis_a308359_check
"""
import sys
from collections import defaultdict
from fractions import Fraction

NMAX = 11
A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268]
STEPS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def enumerate_by_height(nmax):
    """T[(n, H)] = fixed n-cell polyominoes whose bounding box has height H."""
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        return frozenset((x - mx, y - my) for x, y in cells)

    T = defaultdict(int)
    totals = defaultdict(int)
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    T[(1, 1)] = 1
    totals[1] = 1
    while frontier:
        nxt = []
        for a in frontier:
            if len(a) >= nmax:
                continue
            for (x, y) in a:
                for dx, dy in STEPS4:
                    c = (x + dx, y + dy)
                    if c in a:
                        continue
                    q = canon(a | {c})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.append(q)
                    h = max(b for _, b in q) - min(b for _, b in q) + 1
                    T[(len(q), h)] += 1
                    totals[len(q)] += 1
        frontier = nxt
    return T, totals


def interpolate(points):
    """Exact Lagrange interpolation; returns coefficients, highest degree first.

    Works in lowest-degree-first order internally (so multiplying by (x - xj)
    is a shift minus a scale) and reverses once at the end.
    """
    n = len(points)
    acc = [Fraction(0)] * n
    for i, (xi, yi) in enumerate(points):
        basis = [Fraction(1)]                      # the constant 1
        denom = Fraction(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            shifted = [Fraction(0)] + basis        # * x
            scaled = [Fraction(xj) * c for c in basis] + [Fraction(0)]
            basis = [s - t for s, t in zip(shifted, scaled)]
            denom *= Fraction(xi - xj)
        scale = Fraction(yi) / denom
        for idx, b in enumerate(basis):
            acc[idx] += b * scale
    return acc[::-1]


def evaluate(coeffs, x):
    v = Fraction(0)
    for c in coeffs:
        v = v * x + c
    return v


def fmt(coeffs):
    deg = len(coeffs) - 1
    parts = []
    for i, c in enumerate(coeffs):
        p = deg - i
        if c == 0:
            continue
        parts.append(f"{c}" + ("" if p == 0 else f"n^{p}" if p > 1 else "n"))
    return " + ".join(parts) if parts else "0"


def main():
    T, totals = enumerate_by_height(NMAX)

    print(f"[1] enumeration to n = {NMAX} against A001168")
    bad = [n for n in range(1, NMAX + 1) if totals[n] != A001168[n - 1]]
    if bad:
        print(f"    FAIL: totals wrong at n = {bad}")
        return 1
    print(f"    OK, {NMAX} rows")

    print("\n[2] k = 1 against A308359's proved formula 4n - 8, onset n >= 3")
    print("      n   T(n,n-1)   4n-8")
    ok = True
    for n in range(3, NMAX + 1):
        got, want = T[(n, n - 1)], 4 * n - 8
        ok &= got == want
        print(f"    {n:>3} {got:>10} {want:>6}   {'' if got == want else 'MISMATCH'}")
    if not ok:
        print("    FAIL: our triangle is not theirs")
        return 1
    print("    OK -- our T(n,H) is A308359 transposed")

    print("\n[3] k = 2: Theorem A gives deg <= 2 from n >= 5, so three values pin it")
    pts = [(n, T[(n, n - 2)]) for n in (5, 6, 7)]
    quad = interpolate(pts)
    print(f"    interpolated through n = 5,6,7: T(n,n-2) = {fmt(quad)}")
    conj = [Fraction(8), Fraction(-51), Fraction(86)]
    if quad != conj:
        print(f"    FAIL: does not match the conjecture 8n^2 - 51n + 86")
        return 1
    print("    == 8n^2 - 51n + 86, A308359's conjecture, verbatim")
    print("      n   T(n,n-2)   poly")
    for n in range(5, NMAX + 1):
        got, want = T[(n, n - 2)], evaluate(quad, n)
        ok &= got == want
        print(f"    {n:>3} {got:>10} {int(want):>6}   {'' if got == want else 'MISMATCH'}")
    if not ok:
        print("    FAIL: the quadratic does not reproduce later values")
        return 1
    print(f"    OK on every n = 5..{NMAX}")

    print("\n[4] RED control -- a linear fit must NOT survive")
    lin = interpolate([(n, T[(n, n - 2)]) for n in (5, 6)])
    if evaluate(lin, 7) == T[(7, 5)]:
        print("    FAIL: degree 1 also fits, so 'degree 2' is untested here")
        return 1
    print(f"    OK, linear fit {fmt(lin)} gives {int(evaluate(lin, 7))} at n = 7, "
          f"actual {T[(7, 5)]}")

    print("\n[5] RED control -- the onset n >= 2k+1 is sharp, so n = 4 must FAIL")
    got, want = T[(4, 2)], evaluate(quad, 4)
    if got == want:
        print("    FAIL: the formula also holds at n = 2k, so the onset is untested")
        return 1
    print(f"    OK, T(4,2) = {got} but the quadratic gives {int(want)}")

    print("\nMathar's conjecture (A308359, 2019) is a corollary of Theorem A:\n"
          "degree <= 2 and onset n >= 5 are proved there, three enumerated\n"
          "values determine the polynomial, and it is 8n^2 - 51n + 86.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
