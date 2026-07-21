#!/usr/bin/env python3
"""Audit the wired diagonal formulas P_k against REAL swept cells only.

Question answered: how much of each banked a(n) rests on fitted P_k, and
which P_k are pinned by real data alone vs conditional on the defect-gas
structure theorem?

Real cells = results/ns_a36/perheight/h{1..19}.out — heights 1-19 were
genuine engine sweeps (results/ns_a36/PROVENANCE.md); h20+ are
formula-generated and are deliberately EXCLUDED as evidence here.

Checks (all fail-closed):
  A. Each production P_k (parsed from orchestrator/sweep.go diagCoeffTable)
     matches every real in-onset diagonal point (n >= 2k+1, H = n-k <= 19).
     Reports how many of those points exist vs the k+1 needed to pin a
     degree-k polynomial.
  B. For k <= 9 there are >= k+1 real points, so by the Lean shape theorem
     (polyplets/Polyplets/Shape.lean: T(n,n-k) = P(n)*3^(n-1-3k), deg <= k,
     n >= 2k+1) interpolation through real data determines P_k uniquely.
     Verifies the interpolant equals the production polynomial identically.
  C. Decomposes each a(n), n = 29..36, into real-swept cells, formula cells
     pinned by B (k <= 9), and formula cells conditional on the defect-gas
     structure (k >= 10, docs/proofs/diagonal-law.md Corollary).
"""
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_coeff_table():
    src = (ROOT / "orchestrator/sweep.go").read_text()
    tbl = {}
    for m in re.finditer(r'\n\t(\d+): \{\[\]string\{([^}]*)\}, (\d+)\}', src):
        k = int(m.group(1))
        coeffs = [int(x) for x in re.findall(r'"(-?\d+)"', m.group(2))]
        if len(coeffs) != k + 1:
            sys.exit(f"parse error: k={k} has {len(coeffs)} coefficients")
        tbl[k] = (coeffs, int(m.group(3)))  # numerator desc in n, k!
    if sorted(tbl) != list(range(1, 17)):
        sys.exit(f"parse error: found k = {sorted(tbl)}")
    return tbl


TBL = parse_coeff_table()


def Pk(k, n):
    """P_k(n) as an exact Fraction."""
    if k == 0:
        return F(1)
    coeffs, kfact = TBL[k]
    num = 0
    for c in coeffs:
        num = num * n + c
    return F(num, kfact)


def T_formula(k, n):
    """T(n, n-k) = P_k(n) * 3^(n-1-3k); must be a whole number."""
    e = n - 1 - 3 * k
    v = Pk(k, n) * (F(3) ** e if e >= 0 else F(1, 3 ** -e))
    if v.denominator != 1:
        sys.exit(f"non-integer formula value at k={k} n={n}")
    return v.numerator


def load_real():
    real = {}
    for H in range(1, 20):
        p = ROOT / f"results/ns_a36/perheight/h{H}.out"
        for line in p.read_text().split("\n"):
            f = line.split()
            if len(f) == 2:
                real[(int(f[0]), H)] = int(f[1])
    return real


def solve_interp(xs, ys):
    """Exact-fraction coefficients (ascending) of the poly through (xs, ys)."""
    m = len(xs)
    A = [[F(x) ** p for p in range(m)] + [y] for x, y in zip(xs, ys)]
    for col in range(m):
        piv = next(r for r in range(col, m) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        inv = F(1) / A[col][col]
        A[col] = [a * inv for a in A[col]]
        for r in range(m):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * c for a, c in zip(A[r], A[col])]
    return [A[r][m] for r in range(m)]


def main():
    real = load_real()
    failures = 0

    print("== A: production P_k vs every real in-onset point (H <= 19) ==")
    for k in range(1, 17):
        pts = [(n, real[(n, n - k)]) for n in range(2 * k + 1, 37)
               if (n, n - k) in real]
        bad = [(n, t) for n, t in pts if T_formula(k, n) != t]
        failures += len(bad)
        status = "MISMATCH " + str(bad[:2]) if bad else "all match"
        print(f"  k={k:2d}: {len(pts):2d} real points "
              f"(deg-{k} needs {k + 1:2d}; 2 were fit, "
              f"{len(pts) - 2:2d} out-of-sample)  {status}")

    print()
    print("== B: k <= 9 pinned by real data alone "
          "(interpolant == production, given the Lean shape theorem) ==")
    for k in range(0, 10):
        xs = list(range(max(2 * k + 1, 1), max(2 * k + 1, 1) + k + 1))
        ys = [F(real[(n, n - k)]) / F(3) ** (n - 1 - 3 * k) for n in xs]
        interp = solve_interp(xs, ys)
        prod = ([F(1)] if k == 0 else
                [F(c, TBL[k][1]) for c in reversed(TBL[k][0])])
        same = interp == prod
        failures += 0 if same else 1
        print(f"  k={k}: degree-{k} interpolant through {k + 1} real points "
              f"== production polynomial: {same}")

    print()
    print("== C: a(n) decomposition, n = 29..36 ==")
    tri = {}
    for line in (ROOT / "results/triangle.txt").read_text().split("\n"):
        f = line.split()
        if len(f) == 3 and not line.startswith("#"):
            tri[(int(f[0]), int(f[1]))] = int(f[2])
    print("   n   real H<=19   formula k<=9   formula k>=10 (conditional)")
    for n in range(29, 37):
        an = sum(tri[(n, H)] for H in range(1, n + 1))
        r = sum(tri[(n, H)] for H in range(1, 20))
        safe = sum(tri[(n, H)] for H in range(20, n + 1) if n - H <= 9)
        cond = sum(tri[(n, H)] for H in range(20, n + 1) if n - H >= 10)
        if r + safe + cond != an:
            sys.exit(f"row decomposition mismatch at n={n}")
        print(f"  {n}   {100 * r / an:8.4f}%     {100 * safe / an:8.4f}%     "
              f"{100 * cond / an:8.4f}%")

    fresh = all(tri[(36, H)] == T_formula(36 - H, 36) for H in range(20, 37))
    print()
    print(f"  banked triangle H>=20 row-36 cells == fresh eval from "
          f"sweep.go coefficients: {fresh}")
    failures += 0 if fresh else 1

    if failures:
        sys.exit(f"{failures} FAILURES")
    print("  ALL CHECKS PASS")


if __name__ == "__main__":
    main()
