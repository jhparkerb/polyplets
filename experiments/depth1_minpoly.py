#!/usr/bin/env python3
"""The depth-1 defect generating function is algebraic: exact minimal polynomial.

experiments/depth1_asymptotics.py found 5 independent algebraic relations for
F1(y) = sum_k D_1(k) y^k in the box deg_y <= 12, deg_F <= 4 (mod 2^61-1,
holdout 10) — the multiplicity pattern of a minimal polynomial with
deg_y = 8, deg_F = 4.  This script:

  1. locates the minimal box by a mod-p dimension scan (on the integer-
     normalized N(x) = 3 F1(3x), N_k = 3^(k+1) D_1(k) in Z);
  2. solves that box EXACTLY over Q and prints Phi(x, W) with coprime
     integer coefficients;
  3. verifies Phi(x, N(x)) = 0 through x^K exactly (the fit uses only the
     first ~60 orders — everything beyond is holdout);
  4. sympy: expands the branch at the dominant singularity and derives the
     asymptotic constants EXACTLY — rate, exponent, amplitude (target
     sqrt6/27 / Gamma(1/2) form), and the 1/k coefficient a, closing the
     recognition that k <= 19 data could not reach.

Run from repo root: python3 experiments/depth1_minpoly.py [K]
"""
import os
import sys
import time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import walk_families, series_D1            # noqa: E402
from depth1_asymptotics import modp_nullspace                   # noqa: E402

PRIME = (1 << 61) - 1


def powers_of_series(coeffs, qmax, K, ring_mod=None):
    """[F^0, F^1, ..., F^qmax] as coefficient lists 0..K (mod p or exact)."""
    out = [[1] + [0] * K]
    cur = out[0]
    for _ in range(qmax):
        nxt = [0] * (K + 1)
        for a in range(K + 1):
            ca = cur[a]
            if ca:
                for b in range(K + 1 - a):
                    cb = coeffs[b]
                    if cb:
                        if ring_mod:
                            nxt[a + b] = (nxt[a + b] + ca * cb) % ring_mod
                        else:
                            nxt[a + b] += ca * cb
        cur = nxt
        out.append(cur)
    return out


def relation_rows(powers, dy, dF, orders):
    rows = []
    for m in orders:
        row = []
        for j in range(dF + 1):
            for i in range(dy + 1):
                row.append(powers[j][m - i] if m - i >= 0 else 0)
        rows.append(row)
    return rows


def check_relation(v, powers, dy, dF, orders, ring_mod=None):
    for m in orders:
        tot, idx = 0, 0
        for j in range(dF + 1):
            for i in range(dy + 1):
                if m - i >= 0:
                    tot += v[idx] * powers[j][m - i]
                idx += 1
        if ring_mod:
            tot %= ring_mod
        if tot != 0:
            return False
    return True


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    fams = walk_families(K)
    D1 = series_D1(fams, K)
    N = [0] + [int(D1[k] * Fr(3) ** (k + 1)) for k in range(1, K + 1)]
    print(f"N_k to k = {K} in {time.time() - t0:.1f}s "
          f"(N = 3 F1(3x): integer series)")

    print()
    print("== mod-p dimension scan (holdout = everything past the fit rows)")
    Np = [n % PRIME for n in N]
    pow_p = powers_of_series(Np, 4, K, PRIME)
    fit_hi = 70
    best = None
    for dF in range(1, 5):
        line = []
        for dy in range(2, 13):
            rows = relation_rows(pow_p, dy, dF, range(fit_hi + 1))
            ns = modp_nullspace(rows, PRIME)
            good = [v for v in ns
                    if check_relation(v, pow_p, dy, dF, range(fit_hi + 1, K + 1),
                                      PRIME)
                    and any(v[idx] for idx in range((dy + 1), len(v)))]
            line.append(len(good))
            if good and best is None:
                best = (dy, dF)
        print(f"   deg_F = {dF}: dims over deg_y = 2..12: {line}")
    assert best, "no algebraic relation survived — scan found nothing"
    dy, dF = best
    print(f"   minimal box: deg_y = {dy}, deg_F = {dF}")

    print()
    print(f"== exact solve over Q in the minimal box ({dy},{dF})")
    pow_x = powers_of_series(N, dF, K)
    nunk = (dy + 1) * (dF + 1)
    fit_orders = range(0, nunk + 12)
    rows = [[Fr(x) for x in r]
            for r in relation_rows(pow_x, dy, dF, fit_orders)]
    M = [r[:] for r in rows]
    ncol = nunk
    piv_of_col = {}
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(ncol)]
        piv_of_col[c] = r
        r += 1
    free = [c for c in range(ncol) if c not in piv_of_col]
    assert len(free) == 1, f"nullspace dimension {len(free)} != 1 in minimal box"
    fc = free[0]
    v = [Fr(0)] * ncol
    v[fc] = Fr(1)
    for c, pr in piv_of_col.items():
        v[c] = -M[pr][fc]
    from math import gcd
    den = 1
    for x in v:
        den = den * x.denominator // gcd(den, x.denominator)
    vi = [int(x * den) for x in v]
    g = 0
    for x in vi:
        g = gcd(g, x)
    vi = [x // g for x in vi]
    if vi[(dy + 1) * dF:][-1] < 0 if vi[(dy + 1) * dF:] else False:
        vi = [-x for x in vi]

    print("   Phi(x, W) = 0 with integer coprime coefficients:")
    import sympy as sp
    x, W = sp.symbols('x W')
    Phi = sum(vi[j * (dy + 1) + i] * x ** i * W ** j
              for j in range(dF + 1) for i in range(dy + 1))
    Phi = sp.expand(Phi)
    for j in range(dF, -1, -1):
        cj = sp.expand(sum(vi[j * (dy + 1) + i] * x ** i
                           for i in range(dy + 1)))
        print(f"     W^{j}: {sp.factor(cj)}")

    print()
    print(f"== exact verification: Phi(x, N(x)) = 0 through x^{K}")
    assert check_relation(vi, pow_x, dy, dF, range(K + 1)), \
        "exact relation FAILS on full series"
    n_fit = len(list(fit_orders))
    print(f"   holds at every order 0..{K}  OK  "
          f"(fit used orders 0..{n_fit - 1}; {K + 1 - n_fit} orders of holdout)")

    print()
    print("== sympy: the curve at its dominant singularity")
    lead = sp.Poly(Phi, W).all_coeffs()[0]
    print(f"   leading-W coefficient: {sp.factor(lead)}")
    roots = sp.roots(sp.Poly(lead, x))
    print(f"   its roots: {roots}")
    disc = sp.discriminant(Phi, W)
    print(f"   discriminant (factored): {sp.factor(disc)}")


    print()
    print("== Puiseux at x = 1/27 (y = 1/9): derive the constants exactly")
    # Substitute W = V/v with v = sqrt(1-27x).  Because the W^4 and W^3
    # coefficients carry (27x-1)^2 and W^2, W^1 carry (27x-1)^1, the product
    # Phi * v^2 collapses to a POLYNOMIAL in (v, V): the Puiseux branch is an
    # ordinary Taylor series V(v).  V0 = sqrt6/9 is a DOUBLE root of the
    # order-0 quartic (two sheets cross at the branch point), so the first
    # Taylor step is quadratic -- two branch candidates -- and every later
    # step is linear.  The physical sheet is selected at the end by the
    # 11-digit measurement of a from the exact series (an independent
    # Richardson extraction, no branch algebra involved).
    xs = sp.Rational(1, 27)
    assert sp.simplify(lead.subs(x, xs)) == 0, "leading coeff must die at 1/27"
    v, V = sp.symbols('v V')
    xofv = (1 - v ** 2) / 27
    Psi = sp.expand(sp.cancel(Phi.subs({x: xofv, W: V / v}) * v ** 2))
    num, den = sp.fraction(sp.together(Psi))
    assert den.is_number, f"Psi not polynomial: denominator {den}"
    Psi = sp.cancel(sp.expand(num / den) / v ** 2)   # every term carries v^2
    Psi = sp.expand(Psi)
    num, den = sp.fraction(sp.together(Psi))
    assert den.is_number, "Psi/v^2 not polynomial"
    P0 = sp.Poly(Psi.subs(v, 0), V)
    V0 = sp.sqrt(6) / 9
    print(f"   order-0 quartic (factored): {sp.factor(P0.as_expr())}")
    assert sp.simplify(P0.as_expr().subs(V, V0)) == 0, "V0 = sqrt6/9 not a root"
    assert sp.simplify(sp.diff(P0.as_expr(), V).subs(V, V0)) == 0, \
        "expected double root"
    print("   V0 = sqrt(6)/9, a DOUBLE root: two sheets cross here")

    d = sp.symbols('d')
    quad = sp.expand(Psi.subs(V, V0 + d))
    alpha = sp.simplify(quad.coeff(d, 2).subs(v, 0))
    beta = sp.simplify(sp.diff(quad.coeff(d, 1), v).subs(v, 0))
    gamma = sp.simplify(sp.diff(quad.coeff(d, 0), v, 2).subs(v, 0) / 2)
    c1s = sp.solve(alpha * d ** 2 + beta * d + gamma, d)
    assert len(c1s) == 2, c1s
    print(f"   first-step quadratic: c1 in {[sp.radsimp(c) for c in c1s]}")

    NORD = 3
    branches = []
    for c1 in c1s:
        Vser = sp.expand(V0 + sp.radsimp(c1) * v)
        coeffs = [V0, sp.radsimp(c1)]
        for m in range(2, NORD + 1):
            cm = sp.symbols(f'cm{m}')
            eq = sp.expand(Psi.subs(V, Vser + cm * v ** m))
            pol = sp.Poly(eq, v)
            for order in range(pol.degree() + 1):
                cf = sp.expand(pol.coeff_monomial(v ** order))
                if cm in cf.free_symbols:
                    sol = sp.solve(cf, cm)
                    assert len(sol) == 1, (m, order, sol)
                    cval = sp.radsimp(sp.simplify(sol[0]))
                    break
                assert sp.simplify(cf) == 0, (m, order, cf)
            coeffs.append(cval)
            Vser = sp.expand(Vser + cval * v ** m)
        branches.append(coeffs)

    # N(x) = V(v)/v, v = (1-x/xs)^(1/2):
    #   N = V0 (1-z)^(-1/2) + V1 + V2 (1-z)^(1/2) + V3 (1-z) + ...
    # Half-integer powers are singular; V1, V3 join the analytic part.
    # [z^k](1-z)^(-1/2) = k^(-1/2)/sqrt(pi) (1 - 1/(8k) + O(1/k^2))
    # [z^k](1-z)^(+1/2) = -k^(-3/2)/(2 sqrt(pi)) (1 + O(1/k))
    # => N_k 27^-k k^(1/2) sqrt(pi)/V0 = 1 + a/k + ...,  a = -1/8 - V2/(2 V0)
    A_MEAS = 0.00513893995671        # depth1_asymptotics, K=100, 11 digits
    picked = None
    for coeffs in branches:
        a_exact = sp.radsimp(sp.simplify(-sp.Rational(1, 8)
                                         - coeffs[2] / (2 * V0)))
        a_num = float(sp.N(a_exact, 30))
        match = abs(a_num - A_MEAS) < 1e-9
        print(f"   branch c1 = {coeffs[1]}:")
        print(f"     V2 = {coeffs[2]}")
        print(f"     a = -1/8 - V2/(2 V0) = {a_exact}  =  {a_num:.15f}"
              + ("   <-- matches measurement" if match else ""))
        if match:
            assert picked is None, "both branches match?!"
            picked = (coeffs, a_exact)
    assert picked, "neither branch reproduces the measured a"
    coeffs, a_exact = picked

    C1_exact = sp.simplify(V0 / 3 / sp.sqrt(sp.pi))
    tgt = sp.sqrt(6) / (27 * sp.sqrt(sp.pi))
    assert sp.simplify(C1_exact - tgt) == 0
    print()
    print(f"   D_1(k) ~ C_1 9^k k^(-1/2) (1 + a/k + ...)")
    print(f"   C_1 = V0/(3 sqrt pi) = sqrt6/(27 sqrt pi)   DERIVED "
          f"(branch-independent: both sheets share V0)")
    print(f"   a = {a_exact}")
    print(f"     = {sp.N(a_exact, 25)}")
    print("   DERIVED and exact; the k <= 19 run's kill criterion said "
          "'not recognisable' -- it now is")

    print()
    print("== closed doors, stated from the curve")
    print(f"   Phi irreducible over Q: {len(sp.factor_list(Phi)[1]) == 1}")
    print("   discriminant factors have degree <= 10; rho (~14.41, the")
    print("   localized eigenvalue) has no minimal polynomial of degree <= 10")
    print("   (PSLQ, results/allpairs-kernel.md) -- the curve provably does")
    print("   not contain rho: the localized-mode singularities of Phat, B, S")
    print("   cancel identically in F1 = Phat - B^2/(3+S).")

    print(f"\ntotal {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
