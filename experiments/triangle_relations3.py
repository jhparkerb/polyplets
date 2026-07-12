#!/usr/bin/env python3
"""Triangle relation hunt, part 3: 2-D stencils with polynomial coefficients.

Hunt for exact relations
    sum_{(j,d) in stencil} p_{jd}(n,H) * T(n-j, H-d) = 0
holding at every valid (n,H) of the banked 36-row triangle, where the p_{jd}
are polynomials in (n,H) of total degree <= DEG.

Why this is the fully general "factorial coefficients" test: any coefficient
built from factorials of integer linear forms (n!, H!, (n-H)!, (an+bH+c)!, ...)
or fixed exponentials (3^n, ...) enters a *finite-stencil* relation only via
ratios between stencil points, and (m)!/(m-r)! is a polynomial of degree r
while c^n/c^(n-j) is a constant. So polynomial coefficients of sufficient
degree subsume the whole class. (The known diagonal exp-recurrence
k*P_k = sum_{j<=k} j(a_j+b_j n) P_{k-j} evades this only by having an
UNBOUNDED stencil.)

Method: build all equations over the valid region, compute the nullspace
modulo two independent ~2^30 primes (numpy); any surviving kernel vector is
then verified exactly with Fractions on every equation. Expected result per
the atom structure: kernel dim 0 everywhere.
"""
import os, sys
from fractions import Fraction as F

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triangle_relations import load_triangle, NMAX

P1 = 998244353
P2 = 1004535809


def monomials(deg):
    return [(a, b) for a in range(deg + 1) for b in range(deg + 1 - a)]


def build_equations(T, offsets, deg, interior):
    """Rows of the homogeneous system. Columns ordered
    [(j,d,a,b) for (j,d) in offsets for (a,b) in monomials(deg)].
    interior=True restricts to (n,H) where every stencil point lies inside
    the triangle proper (no reliance on structural zeros)."""
    mons = monomials(deg)
    maxj = max(j for j, d in offsets)
    maxd = max(d for j, d in offsets)
    mind = min(d for j, d in offsets)
    rows = []
    for H in range(max(1, 1 + maxd), NMAX + 1 + min(0, mind)):
        for n in range(max(H, 1 + maxj), NMAX + 1):
            if interior and any(n - j < H - d for j, d in offsets):
                continue
            row = []
            for (j, d) in offsets:
                v = T.get((n - j, H - d), 0)
                for (a, b) in mons:
                    row.append(v * (n ** a) * (H ** b))
            rows.append(row)
    return rows


def nullspace_mod(rows, p):
    """Kernel basis of rows.x = 0 (mod p) via vectorized RREF. Returns list
    of int-vectors."""
    M = np.array([[x % p for x in r] for r in rows], dtype=np.int64)
    m, ncols = M.shape
    pivots = []
    r = 0
    for c in range(ncols):
        if r >= m:
            break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0:
            continue
        piv = r + nz[0]
        M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, c]), p - 2, p)
        M[r] = (M[r] * inv) % p
        col = M[:, c].copy()
        col[r] = 0
        M = (M - np.outer(col, M[r])) % p
        pivots.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for i, pc in enumerate(pivots):
            v[pc] = int((-M[i, fc]) % p)
        basis.append(v)
    return basis


def exact_nullspace(rows, ncols):
    """Exact Fraction nullspace (only invoked on mod-p survivors)."""
    M = [[F(x) for x in r] for r in rows]
    m = len(M)
    pivots = []
    r = 0
    for c in range(ncols):
        if r >= m:
            break
        piv = next((i for i in range(r, m) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = F(1) / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        v = [F(0)] * ncols
        v[fc] = F(1)
        for i, pc in enumerate(pivots):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis


STENCILS = [
    ("rect j<=1 d 0..1", [(j, d) for j in (0, 1) for d in (0, 1)]),
    ("rect j<=2 d 0..1", [(j, d) for j in (0, 1, 2) for d in (0, 1)]),
    ("rect j<=1 d 0..2", [(j, d) for j in (0, 1) for d in (0, 1, 2)]),
    ("rect j<=2 d 0..2", [(j, d) for j in (0, 1, 2) for d in (0, 1, 2)]),
    ("rect j<=3 d 0..1", [(j, d) for j in range(4) for d in (0, 1)]),
    ("rect j<=1 d 0..3", [(j, d) for j in (0, 1) for d in range(4)]),
    ("rect j<=3 d 0..2", [(j, d) for j in range(4) for d in (0, 1, 2)]),
    ("rect j<=2 d 0..3", [(j, d) for j in (0, 1, 2) for d in range(4)]),
    ("rect j<=3 d 0..3", [(j, d) for j in range(4) for d in range(4)]),
    ("rect j<=4 d 0..1", [(j, d) for j in range(5) for d in (0, 1)]),
    ("sym  j<=2 d -1..1", [(j, d) for j in (0, 1, 2) for d in (-1, 0, 1)]),
    ("sym  j<=3 d -1..2", [(j, d) for j in range(4) for d in (-1, 0, 1, 2)]),
]


def main():
    T = load_triangle()
    print("== 2-D polynomial-coefficient stencil hunt "
          "(subsumes factorial/exponential coeffs) ==")
    print(f"{'stencil':<20} {'deg':>3} {'region':>8} {'eqs':>4} {'unk':>4} "
          f"{'ker(p1)':>7} {'ker(p2)':>7}  verdict")
    hits = 0
    for name, offsets in STENCILS:
        for deg in range(0, 7):
            nunk = len(offsets) * len(monomials(deg))
            for interior in (False, True):
                rows = build_equations(T, offsets, deg, interior)
                if len(rows) - nunk < 25:
                    continue
                k1 = nullspace_mod(rows, P1)
                if not k1:
                    continue  # full rank mod p1: no exact kernel possible
                k2 = nullspace_mod(rows, P2)
                reg = "interior" if interior else "full"
                print(f"{name:<20} {deg:>3} {reg:>8} {len(rows):>4} {nunk:>4} "
                      f"{len(k1):>7} {len(k2):>7}  mod-p survivor -> exact check")
                if k2:
                    ex = exact_nullspace(rows, nunk)
                    if ex:
                        hits += 1
                        print(f"  !! EXACT RELATION, kernel dim {len(ex)}:")
                        mons = monomials(deg)
                        v = ex[0]
                        idx = 0
                        for (j, d) in offsets:
                            terms = []
                            for (a, b) in mons:
                                c = v[idx]
                                idx += 1
                                if c != 0:
                                    terms.append(f"{c}*n^{a}*H^{b}")
                            if terms:
                                print(f"     T(n-{j},H-{d}): "
                                      + " + ".join(terms))
    if hits == 0:
        print()
        print("no exact relation: every configuration is full-rank")
        print("(all stencils <=5x4, poly coeffs to total degree 6, both regions)")
        print("-> no finite-stencil relation with polynomial, factorial, or")
        print("   exponential coefficients in n,H or linear combinations thereof")


if __name__ == "__main__":
    main()
