#!/usr/bin/env python3
"""Converse sweep (jasonp, 2026-07-31): for open universal claims, hunt exact
counterexamples in banked data — a refutation needs one exact witness.

  1. Onset sharpness: does T(2k,k) ever EQUAL the diagonal-law value
     P_k(2k)*3^(2k-1-3k)?  (Sharpness says it never does; ab initio checked
     only k<=5.  P_k pinned here by exact Lagrange interpolation from the
     banked triangle, k<=13, holdout-verified on every other in-regime cell.)
  2. Denominator minimality: is the minimal common denominator of P_k's
     coefficients EXACTLY k!  (guarded fact is only that it divides k!).
  3. Companion log-convexity + ratio log-concavity: exact triple tests on the
     staged b-files (A006770, A030222, A030233, A030234, A030235, A194596).

Cost: <5 s, pure exact arithmetic on banked files.  No enumeration.
Usage: python3 experiments/converse_sweep.py
"""
from fractions import Fraction
from math import factorial, lcm
from collections import defaultdict
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def load_triangle():
    T, a = {}, defaultdict(int)
    for line in open(os.path.join(ROOT, "results/triangle.txt")):
        p = line.split()
        if len(p) == 3 and p[0].isdigit():
            n, H, v = int(p[0]), int(p[1]), int(p[2])
            T[(n, H)] = v
            a[n] += v
    return T, a


def lagrange(points):
    """Exact Lagrange interpolation -> coefficient list (Fractions), low->high."""
    k = len(points) - 1
    coeffs = [Fraction(0)] * (k + 1)
    for i, (xi, yi) in enumerate(points):
        num = [Fraction(1)]
        den = Fraction(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            num = [c * (-xj) + (num[m - 1] if m else 0)
                   for m, c in enumerate(num)] + [num[-1]]
            # polynomial multiply by (x - xj): rebuild properly below
        # simpler: multiply step by step
        num = [Fraction(1)]
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            den *= (xi - xj)
            new = [Fraction(0)] * (len(num) + 1)
            for m, c in enumerate(num):
                new[m] += c * (-xj)
                new[m + 1] += c
            num = new
        w = Fraction(yi) / den
        for m, c in enumerate(num):
            coeffs[m] += w * c
    return coeffs


def peval(coeffs, x):
    v = Fraction(0)
    for c in reversed(coeffs):
        v = v * x + c
    return v


def main():
    T, a = load_triangle()
    nmax = max(a)

    print("== 1. onset sharpness: formula value at n=2k vs banked T(2k,k) ==")
    for k in range(1, 14):
        pts = [(n, Fraction(T[(n, n - k)]) * Fraction(3) ** (3 * k + 1 - n))
               for n in range(2 * k + 1, 3 * k + 2)]
        P = lagrange(pts)
        # holdout: every other in-regime banked cell must match
        for n in range(2 * k + 1, nmax + 1):
            if (n, n - k) in T:
                want = Fraction(T[(n, n - k)])
                got = peval(P, n) * Fraction(3) ** (n - 1 - 3 * k)
                assert got == want, f"interp holdout FAIL k={k} n={n}"
        v = peval(P, 2 * k) * Fraction(3) ** (2 * k - 1 - 3 * k)
        actual = T.get((2 * k, k))
        if actual is None:
            print(f"  k={k:2d}: T(2k,k) not banked")
            continue
        if v == actual:
            print(f"  k={k:2d}: FORMULA HOLDS AT n=2k — SHARPNESS REFUTED  "
                  f"(both {actual})")
        else:
            tag = "non-integer" if v.denominator != 1 else f"{v}"
            print(f"  k={k:2d}: sharp (formula {tag} vs actual {actual})")

    print("== 2. minimal denominator of P_k vs k! ==")
    for k in range(1, 14):
        pts = [(n, Fraction(T[(n, n - k)]) * Fraction(3) ** (3 * k + 1 - n))
               for n in range(2 * k + 1, 3 * k + 2)]
        P = lagrange(pts)
        D = 1
        for c in P:
            D = lcm(D, c.denominator)
        f = factorial(k)
        if D == f:
            print(f"  k={k:2d}: minimal denominator == k!  (= {f})")
        else:
            print(f"  k={k:2d}: MINIMAL DENOMINATOR {D} != k! = {f} "
                  f"(ratio k!/D = {Fraction(f, D)}) — 'exactly k!' REFUTED")

    print("== 3. companions: log-convexity and ratio log-concavity ==")
    seqs = {
        "A006770(fixed)": "results/b006770_upload.txt",
        "A030222(free)": "results/b030222_upload.txt",
        "A030233(one-sided)": "results/b030233_upload.txt",
        "A030234(bilateral)": "results/b030234_upload.txt",
        "A030235(asymmetric)": "results/b030235_upload.txt",
        "A194596(free non-pomino)": "results/b194596_upload.txt",
    }
    for name, path in seqs.items():
        s = {}
        for line in open(os.path.join(ROOT, path)):
            p = line.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit():
                s[int(p[0])] = int(p[1])
        ns = sorted(s)
        lc_viol = [n for n in ns[1:-1] if s[n] ** 2 > s[n - 1] * s[n + 1]]
        # ratio log-convexity at n needs a(n)^3 a(n-2) <= a(n-1)^3 a(n+1)
        rl = [n for n in ns[2:-1]
              if s[n] ** 3 * s[n - 2] > s[n - 1] ** 3 * s[n + 1]]
        rl_all = len(rl) == len(ns) - 3
        print(f"  {name}: log-convexity violations at n={lc_viol or 'NONE'}; "
              f"ratio NOT-log-convex witnesses: "
              f"{'ALL n (log-concave throughout)' if rl_all else rl or 'NONE'}")


if __name__ == "__main__":
    main()
