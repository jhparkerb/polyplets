#!/usr/bin/env python3
"""Rational generating functions for the site-perimeter defect classes.

Takes `build/perimeter_defect` output and, for each defect k, produces
G_k(x) = sum_n A(n, pmax(n)-k) x^n in three forms: the single reduced fraction,
the cyclotomic factorisation of its denominator, and the partial-fraction
decomposition into one block per cyclotomic factor.

The denominator is not fitted -- it is predicted from the measured period/degree
structure (results/perimeter.md) as

    Phi_1^(k+1) . Phi_2^(k-1) . Phi_3^(k-4)      (nonpositive exponents dropped)

and then *checked*: dividing the series by it must leave a polynomial, i.e. all
coefficients past deg(N) must vanish, and gcd(N, D) must be 1 so no factor is
spurious. With terms to n=70 that is ~30 consecutive exact zeros the fit never
saw, a far harder test than the interpolation bar in perimeter_defect_fit.py.

The partial-fraction form is the useful one. Each block maps to one piece of the
quasi-polynomial: a_j/Phi_1^j contributes a_j*C(n+j-1, j-1), the plain part;
b_j/Phi_2^j contributes (-1)^n times the same, the parity part; the Phi_3 block a
bounded period-3 wobble. Reading the top coefficient off each block is how the
lattice-independence in results/perimeter.md was found.

    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n70_k5.txt
    python3 experiments/perimeter_defect_gf.py A.txt B.txt --compare
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict

import sympy as sp

x, u = sp.symbols("x u")

PHI = {1: 1 - x, 2: 1 + x, 3: 1 + x + x**2}


def load(path):
    """-> ({k: {n: count}}, nmax), summing out the c and H coordinates."""
    seq = defaultdict(lambda: defaultdict(int))
    nmax = 0
    with open(path) as fh:
        for line in fh:
            p = line.split()
            if len(p) != 5 or not p[0].isdigit():
                continue
            n, k, c, H, v = map(int, p)
            seq[k][n] += v
            nmax = max(nmax, n)
    return seq, nmax


def denominator(k):
    """The predicted denominator, as (expression, human-readable exponents)."""
    exps = {1: k + 1}
    if k >= 3:
        exps[2] = k - 1
    if k >= 5:
        exps[3] = k - 4
    D = sp.Integer(1)
    for d, e in exps.items():
        D *= PHI[d] ** e
    return sp.expand(D), exps


def gf(seq, nmax, k):
    """-> dict with the reduced fraction, its check data, and the block form."""
    a = [seq[k].get(n, 0) for n in range(nmax + 1)]
    D, exps = denominator(k)
    dc = sp.Poly(D, x).all_coeffs()[::-1]
    N = [sum(dc[j] * a[i - j] for j in range(len(dc)) if i - j >= 0)
         for i in range(nmax + 1)]
    nz = [i for i, v in enumerate(N) if v != 0]
    if not nz:
        return None
    last = max(nz)
    # every coefficient past deg(N) that the division can see must vanish
    horizon = nmax - len(dc)
    residual = [i for i in range(last + 1, horizon + 1) if N[i] != 0]
    Np = sp.Poly(list(reversed(N[: last + 1])), x)
    common = sp.gcd(Np, sp.Poly(D, x))

    q, r = sp.div(Np, sp.Poly(D, x), x)
    F = sp.cancel(r.as_expr() / D)

    def principal(center, m):
        """Coefficients of 1/(1-x)^j or 1/(1+x)^j, j = 1..m, at that pole."""
        g = sp.simplify(u**m * F.subs(x, center))
        pol = sp.Poly(sp.expand(sp.series(g, u, 0, m + 1).removeO()), u)
        return {j: pol.coeff_monomial(u ** (m - j)) for j in range(1, m + 1)}

    A = principal(1 - u, exps[1])
    B = principal(-1 + u, exps[2]) if 2 in exps else {}
    rest = sp.cancel(F - sum(A[j] / PHI[1] ** j for j in A)
                       - sum(B[j] / PHI[2] ** j for j in B))
    C = sp.expand(sp.cancel(rest * PHI[3])) if 3 in exps else sp.Integer(0)

    assert sp.simplify(q.as_expr() + sum(A[j] / PHI[1] ** j for j in A)
                       + sum(B[j] / PHI[2] ** j for j in B)
                       + (C / PHI[3] if 3 in exps else 0)
                       - sp.cancel(Np.as_expr() / D)) == 0, "blocks do not reassemble"

    return dict(k=k, num=Np.as_expr(), den=D, exps=exps, degN=last,
                residual=residual, horizon=horizon, gcd=common.as_expr(),
                poly=q.as_expr(), A=A, B=B, C=C)


def show(g):
    k = g["k"]
    dstr = " ".join(f"Phi_{d}^{e}" if e > 1 else f"Phi_{d}"
                    for d, e in sorted(g["exps"].items()))
    print(f"=== k = {k} ===")
    print(f"  denominator  {dstr}   (Phi_1 = 1-x, Phi_2 = 1+x, Phi_3 = 1+x+x^2)")
    print(f"  check        deg(N) = {g['degN']}, gcd(N,D) = {g['gcd']}, "
          f"{len(g['residual'])} nonzero coeffs in deg {g['degN']+1}..{g['horizon']} "
          f"{'-- FAILED' if g['residual'] or g['gcd'] != 1 else '(all zero, as required)'}")
    print(f"  G_{k}(x) = {sp.factor(g['num'])} / ({sp.factor(g['den'])})")
    terms = [f"{g['poly']}"] if g["poly"] != 0 else []
    terms += [f"({g['A'][j]})/Phi_1^{j}" for j in sorted(g["A"], reverse=True)]
    terms += [f"({g['B'][j]})/Phi_2^{j}" for j in sorted(g["B"], reverse=True)]
    if g["C"] != 0:
        terms.append(f"({g['C']})/Phi_3")
    print("  blocks:  R(x)  +  " + "  +  ".join(terms[1:] if g["poly"] != 0 else terms))
    print()


def compare(paths, kmax):
    """Which cyclotomic block coefficients agree across two lattices?"""
    runs = [gfs(p, kmax) for p in paths]
    print(f"Block coefficients: '*' = identical across {len(paths)} inputs\n")
    for blk, name in ((("A"), "Phi_1"), (("B"), "Phi_2")):
        print(f"  {name} block, row k, offset d from the top of the block:")
        for k in sorted(runs[0]):
            g0 = runs[0][k]
            if g0 is None or not g0[blk]:
                continue
            top = max(g0[blk])
            cells = []
            for d in range(top):
                j = top - d
                vals = [r[k][blk][j] for r in runs if r.get(k)]
                same = all(v == vals[0] for v in vals)
                cells.append(f"{vals[0]}{'*' if same else ''}")
            print(f"    k={k}: " + "  ".join(cells))
        print()


def gfs(path, kmax):
    seq, nmax = load(path)
    return {k: gf(seq, nmax, k) for k in range(kmax + 1) if k in seq}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tables", nargs="+")
    ap.add_argument("--kmax", type=int, default=5)
    ap.add_argument("--compare", action="store_true",
                    help="tabulate which block coefficients agree across inputs")
    args = ap.parse_args(argv)

    if args.compare:
        if len(args.tables) < 2:
            sys.exit("--compare needs at least two tables")
        compare(args.tables, args.kmax)
        return 0

    bad = 0
    for path in args.tables:
        print(f"# {path}\n")
        for k, g in sorted(gfs(path, args.kmax).items()):
            if g is None:
                continue
            if g["residual"] or g["gcd"] != 1:
                bad += 1
            show(g)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
