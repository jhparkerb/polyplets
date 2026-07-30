#!/usr/bin/env python3
"""Audit the wired diagonal formulas P_k against REAL swept cells only.

Question answered: how much of each banked a(n) rests on fitted P_k, and
which P_k are pinned by real data alone vs conditional on the defect-gas
structure theorem?

Real cells = results/triangle.txt restricted to H <= REAL_HMAX.  H21 is the
tallest height the project ever swept for real (results/ns_a40 phase C);
every H >= 22 cell in the banked triangle was injected from the very
formulas under audit and is deliberately EXCLUDED as evidence here.
(Was pinned at results/ns_a36/perheight/h{1..19}.out, which froze the real
set four terms and two real heights behind the bank.)

Checks (all fail-closed):
  A. Each production P_k (parsed from orchestrator/sweep.go diagCoeffTable,
     k = 1..19) matches every real in-onset diagonal point (n >= 2k+1,
     H = n-k <= REAL_HMAX).  Reports how many of those points exist vs the
     k+1 needed to pin a degree-k polynomial.
  B. For k <= KPIN there are >= k+1 real points, so by the Lean shape theorem
     (polyplets/Polyplets/Shape.lean: T(n,n-k) = P(n)*3^(n-1-3k), deg <= k,
     n >= 2k+1) interpolation through real data determines P_k uniquely.
     Verifies the interpolant equals the production polynomial identically.
     KPIN is derived from the real point counts, not hardcoded.
  C. Decomposes each a(n), n = 29..40, into real-swept cells, formula cells
     pinned by B (k <= KPIN), and formula cells conditional on the defect-gas
     structure (k > KPIN, docs/proofs/diagonal-law.md Corollary).  This is
     the project's circularity map: it says exactly what share of each
     banked term rests on a fitted formula.
"""
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NMAX = 40        # tallest banked row
REAL_HMAX = 21   # tallest REAL engine sweep (results/ns_a40 phase C)
KMAX = 19        # highest wired P_k in orchestrator/sweep.go


def parse_coeff_table():
    src = (ROOT / "orchestrator/sweep.go").read_text()
    tbl = {}
    for m in re.finditer(r'\n\t(\d+): \{\[\]string\{([^}]*)\}, (\d+)\}', src):
        k = int(m.group(1))
        coeffs = [int(x) for x in re.findall(r'"(-?\d+)"', m.group(2))]
        if len(coeffs) != k + 1:
            sys.exit(f"parse error: k={k} has {len(coeffs)} coefficients")
        tbl[k] = (coeffs, int(m.group(3)))  # numerator desc in n, k!
    if sorted(tbl) != list(range(1, KMAX + 1)):
        sys.exit(f"parse error: found k = {sorted(tbl)}, expected 1..{KMAX}")
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


def load_triangle():
    tri = {}
    for line in (ROOT / "results/triangle.txt").read_text().split("\n"):
        f = line.split()
        if len(f) == 3 and not line.startswith("#"):
            tri[(int(f[0]), int(f[1]))] = int(f[2])
    if not tri:
        sys.exit("results/triangle.txt parsed empty")
    return tri


def load_real(tri):
    """Real-swept subset of the banked triangle: every cell with H <= 21."""
    real = {(n, H): t for (n, H), t in tri.items() if H <= REAL_HMAX}
    if not real:
        sys.exit("no real-swept cells found")
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
    tri = load_triangle()
    real = load_real(tri)
    failures = 0

    print(f"== A: production P_k vs every real in-onset point "
          f"(H <= {REAL_HMAX}) ==")
    npts = {}
    for k in range(1, KMAX + 1):
        pts = [(n, real[(n, n - k)]) for n in range(2 * k + 1, NMAX + 1)
               if (n, n - k) in real]
        npts[k] = len(pts)
        bad = [(n, t) for n, t in pts if T_formula(k, n) != t]
        failures += len(bad)
        status = "MISMATCH " + str(bad[:2]) if bad else "all match"
        print(f"  k={k:2d}: {len(pts):2d} real points "
              f"(deg-{k} needs {k + 1:2d}; 2 were fit, "
              f"{max(0, len(pts) - 2):2d} out-of-sample)  {status}")

    # KPIN = largest k for which every level up to k has >= k+1 real points.
    KPIN = 0
    while KPIN + 1 <= KMAX and npts[KPIN + 1] >= KPIN + 2:
        KPIN += 1

    print()
    print(f"== B: k <= {KPIN} pinned by real data alone "
          "(interpolant == production, given the Lean shape theorem) ==")
    for k in range(0, KPIN + 1):
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
    print(f"== C: a(n) decomposition, n = 29..{NMAX} ==")
    print(f"   n   real H<={REAL_HMAX}   formula k<={KPIN}   "
          f"formula k>{KPIN} (conditional)")
    for n in range(29, NMAX + 1):
        an = sum(tri[(n, H)] for H in range(1, n + 1))
        lo = REAL_HMAX + 1
        r = sum(tri[(n, H)] for H in range(1, lo))
        safe = sum(tri[(n, H)] for H in range(lo, n + 1) if n - H <= KPIN)
        cond = sum(tri[(n, H)] for H in range(lo, n + 1) if n - H > KPIN)
        if r + safe + cond != an:
            sys.exit(f"row decomposition mismatch at n={n}")
        print(f"  {n}   {100 * r / an:8.4f}%     {100 * safe / an:8.4f}%     "
              f"{100 * cond / an:8.4f}%")

    fresh = all(tri[(n, H)] == T_formula(n - H, n)
                for n in range(29, NMAX + 1)
                for H in range(REAL_HMAX + 1, n + 1) if n - H <= KMAX)
    print()
    print(f"  banked triangle H>{REAL_HMAX} cells (n=29..{NMAX}) == fresh "
          f"eval from sweep.go coefficients: {fresh}")
    failures += 0 if fresh else 1

    if failures:
        sys.exit(f"{failures} FAILURES")
    print("  ALL CHECKS PASS")


if __name__ == "__main__":
    main()
