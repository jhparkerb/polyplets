#!/usr/bin/env python3
"""The test results/growth-constant.md names and has never run: refit the 40
banked terms admitting a stretched-exponential factor as a fourth parameter,
and see whether mu_1 is driven to 1.

Conway-Guttmann-Zinn-Justin 2018 found that 1324-avoiders have

    a(n) ~ B mu^n mu_1^sqrt(n) n^g

and a differential approximant is structurally blind to the mu_1^sqrt(n)
factor: it fits a D-finite ansatz, the factor is not in that ansatz, so the
fitted exponent absorbs it and looks stable while being wrong.  Our
theta = -1.000(1) rests on DAs plus a confluent 3-parameter fit, neither of
which admits mu_1.  This makes mu_1 a parameter and looks at it.

Taking logs makes the ansatz LINEAR in the four unknowns:

    ln a(n) = ln B + n ln(lambda) + sqrt(n) ln(mu_1) + theta ln n

so a 4-term window has an exact solve, and a sliding window shows drift -- the
same shape as the exact 3-point triple solves used for the mu_H ladder in
results/growth-constant.md.

THE CONTROL IS THE POINT, TWICE OVER.

  (a) On data of exactly this form the solve is exact to 55 digits.  That
      calibrates the arithmetic and nothing else.
  (b) The real series carries corrections this 4-parameter ansatz cannot hold,
      and they get absorbed into mu_1 -- which is why the raw windows drift.
      So the honest control plants a stretched exponential UNDERNEATH a
      confluent correction (1 + c/n) and asks whether the pipeline, Richardson
      extrapolation included, can still separate mu_1 = 1 from mu_1 = 0.99 with
      only 40 terms.  If it cannot, the verdict on the real series is "cannot
      tell", not "no stretched exponential".

Usage: python3 experiments/stretched_exponential_fit.py
"""

import os
import sys

from mpmath import mp, mpf, log, sqrt, matrix, lu_solve

mp.dps = 60

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BFILE = os.path.join(ROOT, "results", "b006770_upload.txt")


def read_terms():
    terms = {}
    with open(BFILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            n, v = line.split()
            terms[int(n)] = int(v)
    return terms


def solve4(ns, logs):
    """Exact 4-point solve for (lnB, ln lambda, ln mu_1, theta)."""
    A = matrix(4, 4)
    b = matrix(4, 1)
    for i, n in enumerate(ns):
        A[i, 0] = mpf(1)
        A[i, 1] = mpf(n)
        A[i, 2] = sqrt(mpf(n))
        A[i, 3] = log(mpf(n))
        b[i] = logs[i]
    return lu_solve(A, b)


def windows(terms, ns_all):
    """4-point solves on consecutive windows: (midpoint, lambda, mu_1, theta)."""
    out = []
    for i in range(len(ns_all) - 3):
        ns = ns_all[i:i + 4]
        logs = [log(mpf(terms[n])) for n in ns]
        x = solve4(ns, logs)
        out.append((mpf(sum(ns)) / 4, mp.e ** x[1], mp.e ** x[2], x[3]))
    return out


def richardson(rows, col):
    """Assume f(n) = f_inf - A/n and eliminate A from the top two windows."""
    if len(rows) < 2:
        return None
    (n1, *v1), (n2, *v2) = rows[-2], rows[-1]
    f1, f2 = v1[col], v2[col]
    return (n2 * f2 - n1 * f1) / (n2 - n1)


def report(terms, ns_all, label, stride=4, show=True):
    rows = windows(terms, ns_all)
    if show:
        print(f"\n  {label}")
        print(f"    {'window':>12} {'lambda':>13} {'mu_1':>13} {'theta':>11}")
        for i in range(0, len(rows), stride):
            mid, lam, mu1, th = rows[i]
            lo = ns_all[i]
            print(f"    {f'[{lo},{lo + 3}]':>12} {mp.nstr(lam, 8):>13} "
                  f"{mp.nstr(mu1, 8):>13} {mp.nstr(th, 6):>11}")
        mid, lam, mu1, th = rows[-1]
        lo = ns_all[len(rows) - 1]
        print(f"    {f'[{lo},{lo + 3}]':>12} {mp.nstr(lam, 8):>13} "
              f"{mp.nstr(mu1, 8):>13} {mp.nstr(th, 6):>11}   <- top")
    rlam = richardson(rows, 0)
    rmu = richardson(rows, 1)
    rth = richardson(rows, 2)
    if show:
        print(f"    Richardson (f = f_inf - A/n) on the top two windows:")
        print(f"      lambda -> {mp.nstr(rlam, 8)}   "
              f"mu_1 -> {mp.nstr(rmu, 8)}   theta -> {mp.nstr(rth, 6)}")
    return rlam, rmu, rth


def synth(lam, mu1, theta, c, N):
    """B lambda^n mu_1^sqrt(n) n^theta (1 + c/n) -- a planted stretched
    exponential sitting under a confluent correction."""
    return {n: (mpf(lam) ** n * mpf(mu1) ** sqrt(mpf(n)) * mpf(n) ** mpf(theta)
                * (1 + mpf(c) / n)) for n in range(1, N + 1)}


def main():
    terms = read_terms()
    N = max(terms)
    print("stretched-exponential refit: "
          "a(n) = B lambda^n mu_1^sqrt(n) n^theta")
    print(f"banked terms: n = 1..{N}")

    print("\n=== CONTROL (a): exact-form data, calibrates arithmetic only ===")
    for mu1 in ("1.0", "0.99"):
        _, got, _ = report(synth("7.11", mu1, "-1", "0", N),
                           list(range(4, N + 1)),
                           f"planted mu_1 = {mu1}, no correction", show=False)
        print(f"  planted {mu1:>5} -> recovered {mp.nstr(got, 10)}")

    print("\n=== CONTROL (b): planted UNDER a confluent correction 1 + 1/n ===")
    print("    (does the method still have teeth at 40 terms?)")
    seen = {}
    for mu1 in ("1.0", "0.99", "0.95"):
        _, got, gth = report(synth("7.11", mu1, "-1", "1", N),
                             list(range(20, N + 1)),
                             f"planted mu_1 = {mu1}", show=False)
        seen[mu1] = got
        print(f"  planted mu_1 = {mu1:>5}  ->  Richardson mu_1 = "
              f"{mp.nstr(got, 8):>12}   theta = {mp.nstr(gth, 6)}")
    sep = abs(seen["1.0"] - seen["0.99"])
    print(f"\n  separation between planted 1.00 and 0.99 after extrapolation:"
          f" {mp.nstr(sep, 4)}")
    print(f"  -> the method {'CAN' if sep > mpf('0.003') else 'CANNOT'} "
          f"distinguish a 1% stretched exponential at 40 terms")

    print("\n=== THE REAL SERIES ===")
    report(terms, list(range(4, N + 1)), "A006770, n = 4..40", stride=4)
    report(terms, list(range(20, N + 1)), "A006770, n = 20..40", stride=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
