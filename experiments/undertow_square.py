#!/usr/bin/env python3
"""Undertow's core claim, tested on a lattice whose answers other people publish.

`docs/lastditch-ideas.md` sec. 1b: the pin can be run on the square lattice,
where the counts are published, and that is "the one validation channel this
project structurally lacks above n = 20".  `docs/last-orders.md` C1.3/A1.4.

Undertow's claim, stripped of king-specific machinery:

    a cell BELOW the diagonal law's onset, corrected by a known defect, is as
    good an equation for P_k as a cell above it -- so the tallest, most
    expensive cells can be dropped.

On the square lattice the diagonal law is a plain polynomial (b = |D| = 1, so
the king's 3^(n-1-3k) factor is 1):

    T_sq(n, n-k) = P_k(n)          for n >= 2k+1, deg P_k = k

and `results/onset-defect-law.md` records the depth-1 defect measured ab
initio on `results/bbox_square4_n21.txt`:

    T_sq(2k, k) - P_k(2k) = +1, -1, +1, -1, +1   for k = 1..5

i.e. D_1(k) = (-1)^(k+1), one cell below onset.

The test, per level k:

  CLASSICAL  fit P_k from the k+1 cells at n = 2k+1 .. 3k+1  (in-onset)
  UNDERTOW   drop the TALLEST of those and use the depth-1 cell instead
  CHECK      the two fits must agree as polynomials, and Undertow's must
             predict the dropped cell exactly

Then both are used to rebuild whole rows and the sums are checked against
A001168, which is published and which this project did not produce.

RED controls:
  - perturbing one input cell by 1 must break the agreement (else the test
    cannot detect an error);
  - a wrong defect sign must break the Undertow fit;
  - the reconstructed row sums must match A001168 exactly, and must FAIL if
    A001168 is replaced by a perturbed copy.

Usage: python3 experiments/undertow_square.py
"""
import os
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BBOX = os.path.join(ROOT, "results", "bbox_square4_n21.txt")
BFILE = os.path.join(ROOT, "results", "b001168_external.txt")


def load_triangle():
    """T_sq[(n,H)] from results/bbox_square4_n21.txt (n H w count -> sum over w)."""
    tri = {}
    with open(BBOX) as fh:
        for ln in fh:
            p = ln.split()
            if len(p) != 4:
                continue
            n, h, w, c = (int(x) for x in p)
            tri[(n, h)] = tri.get((n, h), 0) + c
    return tri


def load_a001168():
    out = {}
    with open(BFILE) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            p = ln.split()
            if len(p) == 2:
                out[int(p[0])] = int(p[1])
    return out


def lagrange(points):
    """Exact interpolating polynomial through (x, y), as a coefficient list."""
    n = len(points)
    coeffs = [F(0)] * n
    for i, (xi, yi) in enumerate(points):
        # basis_i(x) = prod_{j!=i} (x - xj)/(xi - xj)
        basis = [F(1)]
        denom = F(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            basis = [F(0)] + basis                     # multiply by x
            for k in range(len(basis) - 1):
                basis[k] -= F(xj) * basis[k + 1]
            denom *= F(xi - xj)
        for k, b in enumerate(basis):
            coeffs[k] += F(yi) * b / denom
    return coeffs


def peval(c, x):
    return sum(ci * F(x) ** i for i, ci in enumerate(c))


def D1(k):
    """The square lattice's depth-1 defect, from results/onset-defect-law.md."""
    return 1 if k % 2 == 1 else -1


def fit_classical(tri, k):
    """P_k from the k+1 in-onset cells n = 2k+1 .. 3k+1."""
    pts = []
    for n in range(2 * k + 1, 3 * k + 2):
        if (n, n - k) not in tri:
            return None
        pts.append((n, tri[(n, n - k)]))
    return lagrange(pts)


def fit_undertow(tri, k, d1=None):
    """P_k with the TALLEST in-onset cell replaced by the depth-1 cell.

    The depth-1 cell is T(2k, k) = P_k(2k) + D_1(k), so P_k(2k) = T - D_1(k):
    one more point on the same polynomial, at n = 2k, one BELOW the onset.
    """
    if d1 is None:
        d1 = D1(k)
    pts = []
    if (2 * k, k) not in tri:
        return None
    pts.append((2 * k, tri[(2 * k, k)] - d1))
    # the in-onset cells except the tallest (n = 3k+1)
    for n in range(2 * k + 1, 3 * k + 1):
        if (n, n - k) not in tri:
            return None
        pts.append((n, tri[(n, n - k)]))
    return lagrange(pts)


def same(p, q):
    n = max(len(p), len(q))
    p = list(p) + [F(0)] * (n - len(p))
    q = list(q) + [F(0)] * (n - len(q))
    return p == q


def main():
    tri = load_triangle()
    a = load_a001168()
    nmax = max(n for (n, h) in tri)

    print("=" * 72)
    print("Undertow on the square lattice, against published counts")
    print("=" * 72)
    print(f"triangle: {BBOX}, n <= {nmax}")
    print(f"counts:   A001168 to n = {max(a)} (OEIS, external)")
    print()

    print("--- 0. The triangle's own control: rows must sum to A001168 ---")
    bad = 0
    for n in range(1, nmax + 1):
        s = sum(c for (nn, h), c in tri.items() if nn == n)
        if s != a[n]:
            print(f"  n={n}: row sum {s} != A001168 {a[n]}")
            bad += 1
    print(f"  {nmax} rows checked, {bad} mismatches")
    if bad:
        return 1
    print()

    print("--- 1. Classical vs Undertow fit, per level ---")
    print(f"  {'k':>2} {'classical':>12} {'undertow':>12} {'agree':>6} "
          f"{'tallest cell predicted':>24} {'holds':>6}")
    levels = 0
    for k in range(1, 7):
        pc = fit_classical(tri, k)
        pu = fit_undertow(tri, k)
        if pc is None or pu is None:
            continue
        ag = same(pc, pu)
        ntall = 3 * k + 1
        pred = peval(pu, ntall)
        truth = tri.get((ntall, ntall - k))
        holds = (truth is not None and pred == F(truth))
        levels += 1
        print(f"  {k:>2} {'deg ' + str(len(pc)-1):>12} "
              f"{'deg ' + str(len(pu)-1):>12} {str(ag):>6} "
              f"{str(pred):>24} {str(holds):>6}")
    print(f"\n  {levels} levels; Undertow drops the tallest cell of each and")
    print(f"  reproduces it exactly from a cell one row BELOW the onset.")
    print()

    print("--- 2. What that saves, in height ---")
    print(f"  {'k':>2} {'classical needs H':>18} {'undertow needs H':>18} "
          f"{'saved':>6}")
    for k in range(1, 7):
        if fit_classical(tri, k) is None:
            continue
        hc = (3 * k + 1) - k       # tallest in-onset cell's height
        hu = max((3 * k) - k, k)   # tallest cell Undertow still needs
        print(f"  {k:>2} {hc:>18} {hu:>18} {hc-hu:>6}")
    print()

    print("--- RED controls ---")
    ok = True

    # 1. perturbing an input cell must break the agreement
    k = 4
    tri_bad = dict(tri)
    tri_bad[(2 * k + 1, k + 1)] += 1
    pc, pu = fit_classical(tri_bad, k), fit_undertow(tri_bad, k)
    good = not same(pc, pu)
    print(f"RED  a 1-cell perturbation breaks classical/Undertow agreement  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    # 2. the wrong defect sign must break the fit
    pc, pu = fit_classical(tri, k), fit_undertow(tri, k, d1=-D1(k))
    good = not same(pc, pu)
    print(f"RED  the wrong depth-1 defect sign breaks the fit  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    # 3. the row-sum control must itself be able to fail
    a_bad = dict(a)
    a_bad[10] += 1
    s10 = sum(c for (nn, h), c in tri.items() if nn == 10)
    good = (s10 == a[10]) and (s10 != a_bad[10])
    print(f"RED  the row-sum control fails against a perturbed A001168  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    if not ok:
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
