#!/usr/bin/env python3
"""Session 07: fit exact radical closed forms for the area-moment
generating functions

  A_r(t) = sum_s a_r(s) t^s,   a_r(s) = sum area^r over convex king
                               animals of semiperimeter s  (r=1,2),

with the s01/s02-established ansatz field Q(t, sqrt(1-4t)):

  A_r(t) = [P(t) + Q(t) * S] / ((2+t)^a * (1-4t)^b),  S = sqrt(1-4t)

(a,b integers >= 0; half-integer singularity exponents are covered by the
Q*S numerator).  Exact Fraction linear algebra; the fit uses the minimal
prefix of terms and EVERY remaining term is holdout.  Control mode
(convex polyominoes) fitted with denominator (1-4t)^b (no (2+t): s02
showed K=1 there).

Input: out_s07_area_moments.json.  Output: out_s07_moment_fit.txt.
"""
import json, os, sys
from fractions import Fraction
from math import comb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATAFILE = (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".json")
            else "out_s07_area_moments.json")
DATA = json.load(open(os.path.join(ROOT, DATAFILE)))
NTRUNC = DATA["smax"] + 1  # series truncation: coefficients t^0..t^smax


def series_mul(u, v, n=None):
    n = n or NTRUNC
    w = [Fraction(0)] * n
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j, vj in enumerate(v):
            if i + j >= n:
                break
            if vj:
                w[i + j] += ui * vj
    return w


def sqrt_1m4t(n=None):
    """series of sqrt(1-4t): coeff of t^k is -2/(2k-1) * C(2k,k) ... use
    binomial(1/2,k)(-4)^k = -C(2k,k)/(2k-1)."""
    n = n or NTRUNC
    return [Fraction(-comb(2 * k, k), 2 * k - 1) for k in range(n)]


def poly_pow_series(base, e, n=None):
    n = n or NTRUNC
    out = [Fraction(0)] * n
    out[0] = Fraction(1)
    for _ in range(e):
        out = series_mul(out, base, n)
    return out


def solve_exact(rows, rhs):
    """Gaussian elimination over Q; returns solution or None."""
    m, ncol = len(rows), len(rows[0])
    A = [row[:] + [rhs[i]] for i, row in enumerate(rows)]
    piv = []
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        inv = 1 / A[r][c]
        A[r] = [v * inv for v in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [vi - f * vr for vi, vr in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == m:
            break
    # consistency
    for i in range(r, m):
        if A[i][ncol] != 0:
            return None
    if len(piv) < ncol:
        return None  # demand unique solution
    x = [Fraction(0)] * ncol
    for i, c in enumerate(piv):
        x[c] = A[i][ncol]
    return x


def try_fit(seq, start, a, b, dP, dQ, king):
    """seq[k] = coefficient of t^(start+k).  Fit
    (P + Q*S) == A(t) * (2+t)^a * (1-4t)^b  as series, P deg dP, Q deg dQ.
    Uses ALL available terms as equations => any solution is
    simultaneously fit+holdout consistent; we additionally report the
    number of equations beyond the unknown count."""
    n = NTRUNC
    A = [Fraction(0)] * n
    for k, v in enumerate(seq):
        if start + k < n:
            A[start + k] = Fraction(v)
    den = [Fraction(1)]
    if king:
        two_t = [Fraction(2), Fraction(1)]
        for _ in range(a):
            den = series_mul(den, two_t, n)
    one4 = [Fraction(1), Fraction(-4)]
    for _ in range(b):
        den = series_mul(den, one4, n)
    lhs_target = series_mul(A, den, n)
    S = sqrt_1m4t(n)
    nunk = (dP + 1) + (dQ + 1)
    rows, rhs = [], []
    for k in range(n):
        row = [Fraction(0)] * nunk
        if k <= dP:
            row[k] = Fraction(1)
        for j in range(dQ + 1):
            if j <= k:
                row[dP + 1 + j] = S[k - j]
        rows.append(row)
        rhs.append(lhs_target[k])
    sol = solve_exact(rows, rhs)
    if sol is None:
        return None
    P = sol[:dP + 1]
    Q = sol[dP + 1:]
    return P, Q, n - nunk


def fmt_poly(c, var="t"):
    terms = []
    for k, v in enumerate(c):
        if v == 0:
            continue
        terms.append(f"({v})*{var}^{k}")
    return " + ".join(terms) if terms else "0"


def main():
    out = []
    results = {}
    for mode, king in (("king", True), ("poly", False)):
        for r in (1, 2):
            seq = DATA[mode][f"a{r}"]
            start = DATA["start"]
            found = None
            # search smallest (a+b, then unknowns) that fits ALL terms
            cands = []
            amax = 5 if king else 0
            for a in range(0, amax + 1):
                for b in range(0, 10):
                    for d in range(0, 18):
                        cands.append((a + b + d, a, b, d))
            cands.sort()
            for _, a, b, d in cands:
                nunk = 2 * (d + 1)
                if NTRUNC - nunk < 8:
                    continue  # demand >= 8 surplus equations
                got = try_fit(seq, start, a, b, d, d, king)
                if got:
                    found = (a, b, d, got)
                    break
            tag = f"[{mode}] A_{r}(t)"
            if not found:
                out.append(f"{tag}: NO FIT in search box")
                continue
            a, b, d, (P, Q, surplus) = found
            denom = (f"(2+t)^{a} * (1-4t)^{b}" if king
                     else f"(1-4t)^{b}")
            out.append(f"{tag} = [P + Q*sqrt(1-4t)] / {denom}")
            out.append(f"  P = {fmt_poly(P)}")
            out.append(f"  Q = {fmt_poly(Q)}")
            out.append(f"  unknowns = {2*(d+1)}, equations = {NTRUNC}, "
                       f"surplus(holdout-equivalent) = {surplus}")
            results[(mode, r)] = (a, b, P, Q)
    print("\n".join(out))
    with open(os.path.join(ROOT, "out_s07_moment_fit.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(out) + "\n")
    return results


if __name__ == "__main__":
    main()
