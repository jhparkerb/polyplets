#!/usr/bin/env python3
"""Four structural probes of the MAXIMUM-perimeter defect classes.

Reads `build/perimeter_defect` census rows (`n k c H count`) and asks:

  1. ONSET LAW.  results/perimeter-defect-diagonals.md records onsets
     2, 3, 6, 9, 13, 18 for k = 0..5 and says "no law found".  Test
     onset(k) = k(k+1)/2 + 3 for k >= 2 (the two smallest k being degenerate),
     which reproduces 6, 9, 13, 18 and predicts 24 at k=6.  The onset is
     RE-DERIVED here from the census -- the largest n at which the fitted closed
     form fails, plus one -- not copied from the write-up, so this checks the
     law against data rather than against a table someone typed.

  2. RECENTRED BASIS.  The partial-fraction basis 1/Phi_1^j expands the plain
     part in C(n+j-1, j-1), i.e. centred at n = 0, which is why its coefficients
     are ugly rationals.  Re-expand each residue class in C(m, j) where
     m = (n - n0)/period steps ALONG the class from its first in-regime point.
     Non-negative integers there would be evidence of a direct combinatorial
     decomposition (j free gaps along a backbone) rather than an interpolation.

  3. NUMERATOR POSITIVITY, done on the right object.  G_k carries a polynomial
     part R_k holding the pre-onset holdouts, and R_k has no reason to be
     positive -- so the numerator of the FULL G_k is the wrong thing to test
     (its degree is onset + deg D, which is what gave the first, meaningless,
     negative answer).  Test instead the tail series from the onset:
     Ntilde_k = (sum_{n>=onset} A(n,k) x^n) * D_k / x^onset, which is a
     polynomial of degree < deg D_k.  That it IS one, with the predicted
     cyclotomic D_k, is itself a check.

  4. BIVARIATE RATIONALITY.  The denominator exponents are linear in k
     (k+1, k-1, k-4), the signature of F(x,y) = sum_k G_k(x) y^k being rational
     in y over Q(x).  Report deg Ntilde_k and look for a short linear recurrence
     in k over Q(x).

Exact arithmetic throughout: Fraction, never float.  A degree-5 interpolation on
n up to 70 has entries around 70^5, and a float solve there silently returns a
fit that misses the holdouts by a rounding error rather than by a real
disagreement -- which is indistinguishable, from the outside, from "no closed
form exists".

    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n70_k5.txt --lattice square8

results/perimeter-defect-diagonals.md is the companion write-up.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from fractions import Fraction
from math import comb

PMAX = {"square4": lambda n: 2 * n + 2, "square8": lambda n: 4 * n + 4}

# Cyclotomic polynomials as coefficient lists, low order first.
PHI = {1: [1, -1], 2: [1, 1], 3: [1, 1, 1], 4: [1, 0, 1], 6: [1, -1, 1]}

HOLDOUTS = 2            # spare points required per residue class


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


def solve_exact(rows):
    """Gauss-Jordan over Fraction. rows = augmented matrix. Returns the column."""
    m = len(rows)
    A = [list(r) for r in rows]
    for c in range(m):
        piv = next((r for r in range(c, m) if A[r][c] != 0), None)
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [A[r][m] for r in range(m)]


def poly_at(coeffs, n):
    return sum(c * Fraction(n) ** j for j, c in enumerate(coeffs))


def quasi_fit(pts, period, degree):
    """Fit a period-`period`, degree-`degree` quasi-polynomial to {n: v}.

    Returns {residue: coeffs} or None if any class is underdetermined or any
    holdout disagrees.
    """
    out = {}
    for r in range(period):
        sub = sorted((n, v) for n, v in pts.items() if n % period == r)
        if len(sub) < degree + 1 + HOLDOUTS:
            return None
        rows = [[Fraction(n) ** j for j in range(degree + 1)] + [Fraction(v)]
                for n, v in sub[:degree + 1]]
        co = solve_exact(rows)
        if co is None:
            return None
        for n, v in sub[degree + 1:]:
            if poly_at(co, n) != v:
                return None
        out[r] = co
    return out


def fit_class(pts, kdeg):
    """Find the cheapest (period, degree) closed form, then its onset.

    The fit window is the TOP of the range (certainly inside the regime); the
    onset is then the largest n anywhere in the census where the form fails,
    plus one.
    """
    ns = sorted(pts)
    for period in (1, 2, 3, 6):
        for degree in range(0, kdeg + 1):
            need = period * (degree + 1 + HOLDOUTS)
            if len(ns) < need:
                continue
            tail = {n: pts[n] for n in ns[-need:]}
            fit = quasi_fit(tail, period, degree)
            if fit is None:
                continue
            worst = 0
            for n in ns:
                if poly_at(fit[n % period], n) != pts[n]:
                    worst = max(worst, n)
            return period, degree, worst + 1, fit
    return None


def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def denominator(k):
    """The predicted cyclotomic denominator Phi_1^(k+1) Phi_2^(k-1) Phi_3^(k-4)."""
    d = [1]
    for base, e in ((1, k + 1), (2, k - 1), (3, k - 4)):
        for _ in range(max(0, e)):
            d = polymul(d, PHI[base])
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--lattice", required=True, choices=sorted(PMAX))
    ap.add_argument("--kmax", type=int, default=5)
    args = ap.parse_args()

    by_k = read_defect_census(args.census)
    nmax = max(max(d) for d in by_k.values())
    print("census %s  lattice %s  n<=%d" % (args.census, args.lattice, nmax))
    print()

    fits = {}
    print("== 1. ONSET LAW:  onset(k) =?= k(k+1)/2 + 3 for k >= 2")
    print("   k | period degree | onset (from census) | T_k+3 | match")
    for k in range(0, args.kmax + 1):
        if k not in by_k:
            continue
        got = fit_class(by_k[k], k)
        if got is None:
            print("   %d | NO FIT" % k)
            continue
        period, degree, onset, fit = got
        fits[k] = (period, degree, onset, fit)
        pred = k * (k + 1) // 2 + 3
        tag = "(k<2 exempt)" if k < 2 else ("yes" if onset == pred else "NO")
        print("   %d | %6d %6d | %19d | %5d | %s"
              % (k, period, degree, onset, pred, tag))
    if fits:
        ks = sorted(fits)
        print("   observed onsets: %s" % [fits[k][2] for k in ks])
        print("   T_k+3 predicts:  %s" % [k * (k + 1) // 2 + 3 for k in ks])
        print("   PREDICTS onset(6)=%d  onset(7)=%d" % (24, 31))
    print()

    print("== 2. RECENTRED BASIS: class r in C(m, j), m = (n - n0)/period")
    for k in sorted(fits):
        period, degree, onset, fit = fits[k]
        for r in sorted(fit):
            n0 = onset + ((r - onset) % period)          # first in-regime n
            rows = []
            for i in range(degree + 1):
                n = n0 + i * period
                rows.append([Fraction(comb(i, j)) for j in range(degree + 1)]
                            + [poly_at(fit[r], n)])
            co = solve_exact(rows)
            if co is None:
                continue
            ints = all(c.denominator == 1 for c in co)
            pos = all(c >= 0 for c in co)
            print("   k=%d r=%d n0=%-3d %-46s int=%s pos=%s"
                  % (k, r, n0, [str(c) for c in co], ints, pos))
    print()

    # Is the onset the POSITIVITY THRESHOLD?  The C(m,j) coefficients are the
    # forward differences of Q_k along its residue class, so "all non-negative"
    # says the class counts are built by choosing j things out of m from the
    # onset on.  If the least n0 with that property IS the onset, the onset law
    # stops being a fitted number and becomes a statement about the polynomial.
    print("== 2b. Least n0 (per class) with all forward differences >= 0")
    print("   k | r | least n0 | onset+offset | equal?")
    for k in sorted(fits):
        period, degree, onset, fit = fits[k]
        for r in sorted(fit):
            here = onset + ((r - onset) % period)
            least = None
            for cand in range(here + 4 * period, -1, -period):
                rows = []
                for i in range(degree + 1):
                    rows.append([Fraction(comb(i, j)) for j in range(degree + 1)]
                                + [poly_at(fit[r], cand + i * period)])
                co = solve_exact(rows)
                if co is None or not all(c >= 0 for c in co):
                    break
                least = cand
            print("   %d | %d | %8s | %12d | %s"
                  % (k, r, least, here,
                     "yes" if least == here else "no (%s)" % least))
    print()

    print("== 3. NUMERATOR of the TAIL series over the predicted denominator")
    print("   Ntilde_k = (sum_{n>=onset} A(n,k) x^n) * D_k / x^onset")
    nums = {}
    for k in sorted(fits):
        period, degree, onset, fit = fits[k]
        den = denominator(k)
        ser = [0] * (nmax + 1)
        for n in range(onset, nmax + 1):
            ser[n] = by_k[k].get(n, 0)
        prod = polymul(ser, den)
        cut = nmax                       # coefficients above this are truncation
        want = len(den) - 1              # deg Ntilde must be < deg D_k
        head = prod[onset:onset + want]
        junk = [i for i in range(onset + want, cut + 1) if prod[i] != 0]
        nums[k] = head
        print("   k=%d  deg D=%2d  Ntilde=%s" % (k, len(den) - 1, head))
        print("        vanishes above deg D: %s%s"
              % ("yes" if not junk else "NO at n=%s" % junk[:5],
                 "   nonneg=%s" % all(c >= 0 for c in head)))
    print()
    print("== 4. BIVARIATE: deg Ntilde_k = %s"
          % [len(nums[k]) - 1 for k in sorted(nums)])
    print("   (linear growth is necessary for F(x,y) = sum_k G_k(x) y^k to be")
    print("    rational; the Ntilde_k must also satisfy a recurrence in k.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
