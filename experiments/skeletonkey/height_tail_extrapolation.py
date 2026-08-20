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
from fractions import Fraction

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


def tail_share(r, c):
    """share of the row at height >= c, as a float."""
    tot = sum(r)
    return sum(r[c - 1:]) / tot


def collapse_tail(r, x):
    """G(x) = share of the row with H/<H> >= x, linearly interpolated in H."""
    mh = mean_height(r)
    tot = sum(r)
    hstar = x * mh
    lo = int(hstar)
    if lo >= HMAX:
        return 0.0
    frac = hstar - lo               # weight of the partial cell at H = lo+1
    whole = sum(r[lo + 1:]) if lo + 1 <= HMAX else 0
    partial = r[lo] * (1.0 - frac) if lo < HMAX else 0
    return (whole + partial) / tot


def predict(T, n_from, n_to, thresholds):
    """Predict row n_to's tail shares from row n_from's collapsed shape."""
    r_from = row(T, n_from)
    mh_from, mh_to = mean_height(r_from), mean_height(row(T, n_to))
    return {c: collapse_tail(r_from, c / mh_to) for c in thresholds}


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
    """RED: a perturbed triangle must not reproduce the exact tail shares."""
    r = row(T, 40)
    exact = tail_share(r, 20)
    bad = list(r)
    bad[25] = bad[25] * 3 // 2
    tot = sum(bad)
    perturbed = sum(bad[19:]) / tot
    if abs(perturbed - exact) < 1e-9:
        print("RED FAIL: perturbed row reproduced the exact tail share")
        sys.exit(1)
    print("# RED ok: perturbing T(40,26) moves the H>=20 share %.6f -> %.6f"
          % (exact, perturbed))


def main():
    T = load()
    for n in range(8, NMAX + 1):
        if sum(row(T, n)) == 0:
            print("FAIL: row %d empty" % n)
            sys.exit(1)
    red_gate(T)

    nu, C = fit_nu(T, list(range(20, 41)))
    print("# <H> = %.5f n^%.5f   (collapse doc: nu -> 0.6407)" % (C, nu))
    print("# <H>(40) = %.3f   <H>(60) predicted = %.3f   <H>(80) = %.3f"
          % (mean_height(row(T, 40)), C * 60 ** nu, C * 80 ** nu))
    print()

    print("## Exact tail shares, share of a(n) at height >= c")
    ths = [12, 14, 16, 18, 20, 22, 25, 30]
    print("n    " + "".join("H>=%-2d      " % c for c in ths))
    for n in (20, 25, 30, 35, 38, 40):
        r = row(T, n)
        print("%-4d " % n + "".join("%-10.3e " % tail_share(r, c) for c in ths))
    print()

    print("## Validation: predict row 40 from row 30's collapsed shape")
    pred = predict(T, 30, 40, ths)
    r40 = row(T, 40)
    print("c     exact        predicted    ratio")
    for c in ths:
        e, p = tail_share(r40, c), pred[c]
        print("%-5d %-12.4e %-12.4e %.3f" % (c, e, p, (p / e) if e else float("nan")))
    print()

    print("## Same step applied to n = 60 and n = 80 (H thresholds on the real lattice)")
    r40 = row(T, 40)
    for n_to in (60, 80):
        mh = C * n_to ** nu
        sweep_ceiling = 19
        tower_floor = (n_to - 3 + 1) // 2      # Undertow covers H >= this
        print("n = %d:  <H> = %.2f   sweep exact H<=%d   tower exact H>=%d"
              % (n_to, mh, sweep_ceiling, tower_floor))
        band = collapse_tail(r40, (sweep_ceiling + 1) / mh) - collapse_tail(r40, tower_floor / mh)
        print("   band H in [%d, %d] carries share %.4e of a(%d)"
              % (sweep_ceiling + 1, tower_floor - 1, band, n_to))
        for c in (20, 22, 25, 30):
            print("   share at H >= %-3d = %.4e" % (c, collapse_tail(r40, c / mh)))
        print()


if __name__ == "__main__":
    main()
