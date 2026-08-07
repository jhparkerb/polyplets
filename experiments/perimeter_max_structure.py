#!/usr/bin/env python3
"""Four structural probes of the MAXIMUM-perimeter defect classes.

Reads `build/perimeter_defect` census rows (`n k c H count`) and asks:

  1. ONSET LAW.  results/perimeter-defect-diagonals.md records onsets
     2, 3, 6, 9, 13, 18 for k = 0..5 and says "no law found".  Test
     onset(k) = k(k+1)/2 + 3 for k >= 2 (the two small k being degenerate),
     which reproduces 6, 9, 13, 18 exactly and predicts 24 at k=6.  The onset
     is RE-DERIVED here from the census -- the largest n at which the fitted
     closed form fails -- not copied from the write-up, so this is a check of
     the law against data, not against a table someone typed.

  2. RECENTRED BASIS.  The partial-fraction basis 1/Phi_1^j expands the plain
     part in C(n+j-1, j-1), i.e. centred at n = 0, which is why the
     coefficients are ugly rationals.  Re-expand Q_k(n) in C(n - onset_k, j).
     Non-negative integers there would be evidence of a direct combinatorial
     decomposition (j free gaps along a backbone) rather than an interpolation.

  3. NUMERATOR POSITIVITY.  G_k = N_k(x)/D_k(x) with D_k the predicted
     cyclotomic product.  Are the N_k coefficients non-negative?  Do square and
     king numerators differ by a simple factor?

  4. BIVARIATE RATIONALITY.  The denominator exponents are linear in k
     (k+1, k-1, k-4), which is the signature of F(x,y) = sum_k G_k(x) y^k being
     rational in y over Q(x).  Test whether the sequence (N_k) satisfies a
     short linear recurrence in k with polynomial-in-x coefficients.

    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n70_k5.txt --lattice square8

results/perimeter-defect-diagonals.md is the companion write-up.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from fractions import Fraction

import sympy as sp

x = sp.Symbol("x")
PHI = {1: 1 - x, 2: 1 + x, 3: 1 + x + x**2, 4: 1 + x**2, 6: 1 - x + x**2}

PMAX = {"square4": lambda n: 2 * n + 2, "square8": lambda n: 4 * n + 4}


def read_defect_census(path):
    """`n k c H count` -> {k: {n: total count}}."""
    by_k = defaultdict(dict)
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        n, k, count = int(f[0]), int(f[1]), int(f[-1])
        by_k[k][n] = by_k[k].get(n, 0) + count
    return by_k


def quasi_fit(pts, period, degree):
    """Fit a period-`period` quasi-polynomial of degree `degree` to {n: v}.

    Returns {residue: [coeffs]} or None if any residue class is underdetermined.
    Uses exact rational linear solve, no floats.
    """
    out = {}
    for r in range(period):
        sub = sorted((n, v) for n, v in pts.items() if n % period == r)
        if len(sub) < degree + 1:
            return None
        A = sp.Matrix([[sp.Integer(n) ** j for j in range(degree + 1)]
                       for n, _ in sub[:degree + 1]])
        b = sp.Matrix([[sp.Integer(v)] for _, v in sub[:degree + 1]])
        try:
            sol = A.solve(b)
        except Exception:
            return None
        coeffs = [sp.nsimplify(c) for c in sol]
        for n, v in sub[degree + 1:]:                    # holdouts
            got = sum(c * sp.Integer(n) ** j for j, c in enumerate(coeffs))
            if sp.simplify(got - v) != 0:
                return None
        out[r] = coeffs
    return out


def onset_of(pts, period, degree):
    """Largest n where the (period, degree) form FAILS; onset = that + 1.

    Fit on the top of the range (guaranteed inside the regime), then walk down.
    """
    ns = sorted(pts)
    # the fit window must sit entirely inside the regime AND leave every
    # residue class spare points: (degree+1) to interpolate + 2 holdouts.
    need = period * (degree + 3)
    if len(ns) < need + 2:
        return None, None
    tail = {n: pts[n] for n in ns[-need:]}
    fit = quasi_fit(tail, period, degree)
    if fit is None:
        return None, None
    def val(n):
        c = fit[n % period]
        return sum(ci * sp.Integer(n) ** j for j, ci in enumerate(c))
    worst = 0
    for n in ns:
        if val(n) != pts[n]:
            worst = max(worst, n)
    return worst + 1, fit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--lattice", required=True, choices=sorted(PMAX))
    ap.add_argument("--kmax", type=int, default=5)
    args = ap.parse_args()

    by_k = read_defect_census(args.census)
    nmax = max(max(d) for d in by_k.values())
    print("census %s  lattice %s  n<=%d  k<=%d"
          % (args.census, args.lattice, nmax, max(by_k)))
    print()

    # ---- 1. onset law -------------------------------------------------------
    print("== 1. ONSET LAW:  onset(k) =?= k(k+1)/2 + 3 for k >= 2")
    print("  k | period degree | onset (from census) | T_k+3 | match")
    onsets, fits = {}, {}
    for k in range(0, args.kmax + 1):
        pts = by_k.get(k)
        if not pts:
            continue
        got = None
        for period in (1, 2, 3, 6):
            for degree in range(0, k + 1):
                o, f = onset_of(pts, period, degree)
                if o is not None and degree == k:
                    got = (period, degree, o, f)
                    break
            if got:
                break
        if not got:
            print("  %d | NO FIT" % k)
            continue
        period, degree, o, f = got
        onsets[k], fits[k] = o, f
        pred = k * (k + 1) // 2 + 3
        print("  %d | %6d %6d | %19d | %5d | %s"
              % (k, period, degree, o, pred,
                 "yes" if o == pred else ("(k<2 exempt)" if k < 2 else "NO")))
    if onsets:
        print("  observed onsets: %s" % [onsets[k] for k in sorted(onsets)])
        print("  T_k+3 predicts:  %s" % [k * (k + 1) // 2 + 3
                                         for k in sorted(onsets)])
        print("  predictions: onset(6)=%d  onset(7)=%d"
              % (6 * 7 // 2 + 3, 7 * 8 // 2 + 3))
    print()

    # ---- 2. recentred binomial basis ---------------------------------------
    print("== 2. RECENTRED BASIS:  Q_k(n) in C(n - onset_k, j)")
    print("   (per residue class; integrality/non-negativity is the signal)")
    n_ = sp.Symbol("n")
    for k in sorted(fits):
        o = onsets[k]
        for r in sorted(fits[k]):
            poly = sum(c * n_ ** j for j, c in enumerate(fits[k][r]))
            # Expand in the basis C(n-o, j), j = 0..k.  Evaluating at
            # n = o, o+1, ... makes the system unit-triangular, so this is an
            # exact rational solve with no cancellation worries.
            js = list(range(k + 1))
            M = sp.Matrix([[sp.binomial(sp.Integer(o + m) - o, j) for j in js]
                           for m in range(k + 1)])
            v = sp.Matrix([[poly.subs(n_, o + m)] for m in range(k + 1)])
            try:
                sol = M.solve(v)
            except Exception:
                print("  k=%d r=%d  singular" % (k, r))
                continue
            vals = [sp.nsimplify(s) for s in sol]
            allint = all(val.is_integer for val in vals)
            allpos = all(val >= 0 for val in vals)
            print("  k=%d r=%d  %s   int=%s pos=%s"
                  % (k, r, [str(v_) for v_ in vals], allint, allpos))
    print()

    # ---- 3/4. numerators ----------------------------------------------------
    print("== 3. NUMERATORS over the predicted cyclotomic denominator")
    nums = {}
    for k in sorted(by_k):
        if k > args.kmax:
            continue
        pts = by_k[k]
        ser = sum(sp.Integer(pts.get(n, 0)) * x ** n for n in range(nmax + 1))
        den = sp.Integer(1)
        for d, e in ((1, k + 1), (2, k - 1), (3, k - 4)):
            if e > 0:
                den *= PHI[d] ** e
        prod = sp.Poly(sp.expand(ser * den), x)
        cs = prod.all_coeffs()[::-1]
        # the series is truncated at nmax, so only coefficients up to
        # nmax - deg(den) are trustworthy
        cut = nmax - sp.Poly(den, x).degree()
        head = cs[:cut + 1]
        tail_zero = all(c == 0 for c in cs[cut + 1:len(cs)])
        # strip trailing zeros of the head to find the true numerator degree
        deg = max([i for i, c in enumerate(head) if c != 0] or [0])
        nums[k] = head[:deg + 1]
        print("  k=%d  deg N=%2d  nonneg=%s  N = %s"
              % (k, deg, all(c >= 0 for c in nums[k]), nums[k]))
        if deg > cut - 4:
            print("      WARNING: numerator degree close to the trustworthy cut"
                  " (%d); series may be too short." % cut)
    print()
    print("== 4. BIVARIATE: does N_k satisfy a short recurrence in k?")
    print("   (reported as the numerator degree sequence; a rational F(x,y)")
    print("    needs deg N_k to grow linearly and the N_k to satisfy one.)")
    print("   deg N_k = %s" % [len(nums[k]) - 1 for k in sorted(nums)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
