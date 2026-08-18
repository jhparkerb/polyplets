#!/usr/bin/env python3
"""Does the Prony spectrum of the convex-polyplet area series equal 1/zeros(K)?

K(q) = sum_{m>=0} (-1)^m (2 - q^m) q^{m(m+1)/2} / (q;q)_m^2 is the Temperley
denominator of the area generating function (results/convex-polyplets.md, the
2026-08-17 salvage).  Its smallest positive zero q_1 gives mu = 1/q_1.  L7
measures the next exponentials by Prony's method, without any kernel:

    lambda_2 = 1.50504922775900...,  lambda_3 = 1.28433727098118...,
    lambda_4 = -1.25776216033063...

The first two positive zeros already account for lambda_1 and lambda_2.  This
scans both signs for the rest, so the identification is tested rather than
assumed -- lambda_4 is negative and can only come from a negative zero.

    python3 experiments/convex_kernel_zeros.py
"""
from __future__ import annotations

from mpmath import mp, mpf, nstr

mp.dps = 60

PRONY = {
    "lambda_1": mpf("3.12894326973088625227744799538775416053"),
    "lambda_2": mpf("1.50504922775900"),
    "lambda_3": mpf("1.28433727098118"),
    "lambda_4": mpf("-1.25776216033063"),
}


def K(q, terms=400):
    """The king kernel.  (q;q)_m is built incrementally."""
    total = mpf(0)
    poch = mpf(1)
    for m in range(terms):
        if m:
            poch *= (1 - q ** m)
        term = (-1) ** m * (2 - q ** m) * q ** (m * (m + 1) // 2) / poch ** 2
        total += term
        if m > 8 and abs(term) < mpf(10) ** (-mp.dps - 10):
            break
    return total


def bisect(lo, hi, iters=400):
    """Plain bisection.  One K evaluation per step, not two -- K is a 400-term
    series at 60 digits and this loop runs a few hundred times per zero."""
    flo = K(lo)
    for _ in range(iters):
        mid = (lo + hi) / 2
        fmid = K(mid)
        if fmid * flo > 0:
            lo, flo = mid, fmid
        else:
            hi = mid
    return (lo + hi) / 2


def zeros_on(lo, hi, step):
    """Sign changes of K on a grid, refined by bisection."""
    out = []
    x = lo
    prev = K(x)
    while x < hi:
        x2 = x + step
        cur = K(x2)
        if prev * cur < 0:
            out.append(bisect(x, x2))
        x, prev = x2, cur
    return out


def main() -> int:
    pos = zeros_on(mpf("0.05"), mpf("0.9"), mpf("0.005"))
    neg = zeros_on(mpf("-0.95"), mpf("-0.05"), mpf("0.005"))
    cand = sorted(pos + neg, key=lambda q: -abs(1 / q))
    print("zeros of K found: %d positive, %d negative" % (len(pos), len(neg)))
    print()
    print("  1/q, by decreasing modulus        nearest Prony lambda   agreement")
    for q in cand[:6]:
        lam = 1 / q
        best, digits = None, -1
        for name, val in PRONY.items():
            if val == 0:
                continue
            rel = abs(lam - val) / abs(val)
            d = 99 if rel == 0 else int(-mp.log10(rel))
            if d > digits:
                best, digits = name, d
        print("  %-32s %-22s %d digits"
              % (nstr(lam, 20), best, digits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
