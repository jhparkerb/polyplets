#!/usr/bin/env python3
"""Holdout-validated P-recurrence guesser (exact rational arithmetic).

Same methodology as convex-mirage's discriminator: fit
sum_{i=0..ORD} p_i(n) a(n-i) = 0 with deg p_i <= DEG on a training prefix,
then REQUIRE it to predict >= HOLDOUT further terms exactly.

Reads a sequence of integers from argv (comma string) or stdin.
Reports the minimal (order, degree) recurrence found, or NONE.
"""
import sys
from fractions import Fraction
from itertools import product


def nullspace(rows, ncols):
    """Exact rational nullspace basis vector (first free one) or None."""
    m = [list(map(Fraction, r)) for r in rows]
    nr = len(m)
    piv = []  # (row, col)
    r = 0
    for c in range(ncols):
        pr = next((i for i in range(r, nr) if m[i][c] != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = m[r][c]
        m[r] = [x / inv for x in m[r]]
        for i in range(nr):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == nr:
            break
    pivset = set(piv)
    free = [c for c in range(ncols) if c not in pivset]
    if not free:
        return None
    # basis vector for first free column
    fc = free[0]
    v = [Fraction(0)] * ncols
    v[fc] = Fraction(1)
    for i, c in enumerate(piv):
        v[c] = -m[i][fc]
    return v


def check(seq, coeffs, order, deg, start):
    """Check recurrence on all n from start..len(seq)-1. coeffs[i][d]."""
    for n in range(start, len(seq)):
        tot = 0
        for i in range(order + 1):
            p = sum(coeffs[i][d] * n ** d for d in range(deg + 1))
            tot += p * seq[n - i]
        if tot != 0:
            return False
    return True


def guess(seq, max_order=6, max_deg=5, holdout=5, verbose=True):
    N = len(seq)
    for order in range(1, max_order + 1):
        for deg in range(0, max_deg + 1):
            nvars = (order + 1) * (deg + 1)
            ntrain = N - holdout - order
            if ntrain < nvars + 2:  # need overdetermined training
                continue
            rows = []
            for n in range(order, N - holdout):
                row = []
                for i in range(order + 1):
                    for d in range(deg + 1):
                        row.append(seq[n - i] * n ** d)
                rows.append(row)
            v = nullspace(rows, nvars)
            if v is None:
                continue
            coeffs = [[v[i * (deg + 1) + d] for d in range(deg + 1)]
                      for i in range(order + 1)]
            if check(seq, coeffs, order, deg, order):
                if verbose:
                    print(f"FOUND recurrence order={order} deg={deg} "
                          f"(trained on {ntrain} eqs, holdout {holdout} OK)")
                    # clear denominators
                    from math import lcm, gcd
                    dens = [c.denominator for cs in coeffs for c in cs]
                    L = 1
                    for d in dens:
                        L = lcm(L, d)
                    ic = [[int(c * L) for c in cs] for cs in coeffs]
                    g = 0
                    for cs in ic:
                        for c in cs:
                            g = gcd(g, c)
                    if g > 1:
                        ic = [[c // g for c in cs] for cs in ic]
                    for i, cs in enumerate(ic):
                        terms = " + ".join(f"{c}*n^{d}" for d, c in enumerate(cs) if c)
                        print(f"  p_{i}(n) = {terms if terms else '0'}")
                return order, deg, coeffs
    if verbose:
        print(f"NONE up to order {max_order} deg {max_deg} "
              f"(holdout {holdout}) on {N} terms")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        seq = [int(x) for x in sys.argv[1].replace(",", " ").split()]
    else:
        seq = [int(x) for x in sys.stdin.read().replace(",", " ").split()]
    print(f"{len(seq)} terms")
    guess(seq)
