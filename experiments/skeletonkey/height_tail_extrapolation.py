#!/usr/bin/env python3
"""How much of a(n) sits above a given height, and how far that can be extrapolated.

Motivation (Skeleton Key, 2026-08-20).  An exact a(n) needs every cell of the
T(n,H) triangle.  An a(n) good to a few significant digits does not: the sweep
covers H <= Hsweep exactly, the Undertow tower covers H >= (n-3)/2 exactly, and
only the band between them has to be estimated.  This script prices that band.

The extrapolation is validated before it is used: the height-distribution
collapse measured at row n0 is used to PREDICT the tail shares of row n1, and
the prediction is compared against the exact row n1.  Only then is the same
step applied past the data.

Input: results/ns_a40/perheight/hH.out, one "n count" pair per line.
"""
import sys, os


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERHEIGHT = os.path.join(ROOT, "results", "ns_a40", "perheight")
NMAX, HMAX = 40, 40


def load():
    T = {}
    for h in range(1, HMAX + 1):
        path = os.path.join(PERHEIGHT, "h%d.out" % h)
        with open(path) as f:
            for line in f:
                parts = line.split()
                if len(parts) != 2:
                    continue
                n, c = int(parts[0]), int(parts[1])
                if n <= NMAX:
                    T[(n, h)] = c
    return T


def row(T, n):
    return [T.get((n, h), 0) for h in range(1, HMAX + 1)]


def mean_height(r):
    tot = sum(r)
    return sum((h + 1) * c for h, c in enumerate(r)) / tot


def quantile(r, q):
    """smallest H with at least a q-fraction of the row's animals at height <= H.

    A statement about the height distribution of an n-cell animal, not about
    a(n): see docs/engineering-standards.md 3b, cells are never weighed against
    the term they sum to.
    """
    tot = sum(r)
    run = 0
    for h, c in enumerate(r, start=1):
        run += c
        if run * 1.0 >= q * tot:
            return h
    return len(r)


def predict_quantile(r_from, mh_to, q):
    """Predict a quantile of row n_to from row n_from's collapsed shape."""
    mh_from = mean_height(r_from)
    return quantile(r_from, q) / mh_from * mh_to


def fit_nu(T, ns):
    """<H> ~ C n^nu, least squares in log-log."""
    import math
    xs = [math.log(n) for n in ns]
    ys = [math.log(mean_height(row(T, n))) for n in ns]
    k = len(ns)
    mx, my = sum(xs) / k, sum(ys) / k
    nu = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return nu, math.exp(my - nu * mx)


def red_gate(T):
    """RED: a perturbed triangle must not reproduce the exact quantiles."""
    r = row(T, 40)
    exact = quantile(r, 0.99)
    bad = list(r)
    bad[5] = bad[5] * 10 ** 6
    perturbed = quantile(bad, 0.99)
    if perturbed == exact:
        print("RED FAIL: perturbed row reproduced the exact 99% height")
        sys.exit(1)
    print("# RED ok: inflating T(40,6) moves the 99%% height %d -> %d" % (exact, perturbed))


QS = [0.5, 0.9, 0.99, 0.999, 0.9999]


def main():
    T = load()
    for n in range(8, NMAX + 1):
        if sum(row(T, n)) == 0:
            print("FAIL: row %d empty" % n)
            sys.exit(1)
    red_gate(T)

    nu, C = fit_nu(T, list(range(20, 41)))
    print("# <H> = %.5f n^%.5f   (collapse doc: nu -> 0.6407)" % (C, nu))
    print()

    print("## Height distribution of an n-cell animal: mean and quantiles (exact)")
    print("n     <H>     " + "".join("q%-7s" % q for q in QS))
    for n in (20, 25, 30, 35, 40):
        r = row(T, n)
        print("%-5d %-7.2f " % (n, mean_height(r))
              + "".join("%-8d" % quantile(r, q) for q in QS))
    print()

    print("## Validation: predict row 40's quantiles from row 30's collapsed shape")
    r30, r40 = row(T, 30), row(T, 40)
    mh40 = mean_height(r40)
    print("q         exact   predicted")
    for q in QS:
        print("%-9s %-7d %.1f" % (q, quantile(r40, q), predict_quantile(r30, mh40, q)))
    print()

    print("## The same collapse step applied past the data")
    for n_to in (60, 80):
        mh = C * n_to ** nu
        print("n = %d:  <H> = %.2f   sweep ceiling H = 19   tower floor H = %d"
              % (n_to, mh, (n_to - 2) // 2))
        for q in QS:
            print("   predicted q%-8s H = %.1f" % (q, predict_quantile(r40, mh, q)))
        print()


if __name__ == "__main__":
    main()
