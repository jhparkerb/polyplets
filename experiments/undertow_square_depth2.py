#!/usr/bin/env python3
"""Square-lattice Undertow at depth 2 -- docs/time-at-the-bar.md A1.4.

results/undertow-square-validation.md put an EXTERNAL oracle under Undertow for
the first time, at depth 1 only: the square lattice's counts are published by
other people, so a shared conceptual error in this project's king machinery
cannot hide there.  One depth is one height of saving.  This measures the
depth-2 defect the same way depth 1 was measured -- ab initio, from the banked
square bounding-box triangle -- and then uses it, so the external check covers
two heights instead of one.

THE SETUP, with the king machinery stripped out.  On the square lattice
b = |D| = 1, so the diagonal law is a plain polynomial:

    T_sq(n, n-k) = P_k(n)      for n >= 2k+1, degree k

Below the onset the identity acquires a defect.  Depth j is the cell at
n = 2k+1-j:

    depth 1   n = 2k     D_1(k) = T_sq(2k,   k)   - P_k(2k)
    depth 2   n = 2k-1   D_2(k) = T_sq(2k-1, k-1) - P_k(2k-1)

results/onset-defect-law.md measured D_1(k) = (-1)^(k+1) from five levels.
D_2 has never been measured on this lattice.

WHAT LIMITS THE RANGE.  P_k has to be pinned from in-onset cells alone, which
needs n up to 3k+1, and results/bbox_square4_n21.txt stops at n = 21.  So
k <= 6, and the depth-2 cell at n = 2k-1 exists for every one of them.  That is
five levels for D_2 at k = 2..6, the same number D_1 was measured from -- not a
coincidence, the same wall.

THE PAYOFF, if D_2 has a law.  Undertow's saving is that the TALLEST in-onset
cell can be dropped and replaced by a cell below the onset.  Depth 1 drops one
height; depth 2 drops two, using both n = 2k and n = 2k-1 and keeping only
n = 2k+1 .. 3k-1.  The test is whether that fit reproduces the classical
polynomial exactly, in exact rational arithmetic.

CONTROLS.
  (a) The classical and depth-1 fits must still agree at every k, or this
      script disagrees with the file it is extending.
  (b) A WRONG D_2 must break the depth-2 fit.  If the fit survives a corrupted
      defect the test is vacuous, and the script says so and fails.
  (c) The depth-2 fit must reproduce the tallest TWO in-onset cells it never
      saw -- a genuine holdout, not a re-derivation of its own inputs.

Usage: python3 experiments/undertow_square_depth2.py

Target machine: ayr or dalby.  Cost: instant, exact rational arithmetic.
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from undertow_square import (  # noqa: E402
    load_triangle, lagrange, peval, D1, fit_classical, fit_undertow, same)

KMAX = 6


def D2_measured(tri, k):
    """T_sq(2k-1, k-1) - P_k(2k-1), with P_k pinned from in-onset cells only."""
    P = fit_classical(tri, k)
    if P is None:
        return None, None
    cell = (2 * k - 1, k - 1)
    if cell not in tri:
        return None, None
    return tri[cell] - peval(P, 2 * k - 1), P


def fit_depth2(tri, k, d1=None, d2=None):
    """P_k from the two below-onset cells plus the in-onset cells n = 2k+1..3k-1.

    Point count: 2 + (3k-1 - (2k+1) + 1) = k + 1, exactly enough for degree k.
    The two tallest in-onset cells (n = 3k, 3k+1) are never seen and are the
    holdout.
    """
    if d1 is None:
        d1 = D1(k)
    if d2 is None:
        return None
    pts = []
    if (2 * k - 1, k - 1) not in tri or (2 * k, k) not in tri:
        return None
    pts.append((2 * k - 1, tri[(2 * k - 1, k - 1)] - d2))
    pts.append((2 * k, tri[(2 * k, k)] - d1))
    for n in range(2 * k + 1, 3 * k):
        if (n, n - k) not in tri:
            return None
        pts.append((n, tri[(n, n - k)]))
    if len(pts) != k + 1:
        return None
    return lagrange(pts)


def main():
    tri = load_triangle()
    print("Square-lattice Undertow, depth 2.  Exact rational arithmetic.\n")

    # ---- control (a): depth 1 still reproduces the file it extends
    ok = True
    for k in range(1, KMAX + 1):
        P, U = fit_classical(tri, k), fit_undertow(tri, k)
        if P is None or U is None:
            continue
        if not same(P, U):
            print("  control (a) FAILED at k=%d: depth-1 fit disagrees" % k)
            ok = False
    print("RED  (a) depth-1 Undertow still reproduces the classical fit, "
          "k=1..%d   %s" % (KMAX, "OK" if ok else "FAILED"))

    # ---- the measurement
    print("\nD_2(k), measured ab initio:")
    print("  %-4s %-16s %-16s %-12s" % ("k", "T(2k-1, k-1)", "P_k(2k-1)", "D_2"))
    d2 = {}
    for k in range(2, KMAX + 1):
        val, P = D2_measured(tri, k)
        if val is None:
            print("  k=%d  no data" % k)
            continue
        d2[k] = val
        print("  %-4d %-16s %-16s %-12s"
              % (k, tri[(2 * k - 1, k - 1)], peval(P, 2 * k - 1), val))

    if not d2:
        print("\nno levels measurable -- stop")
        return 1

    vals = [d2[k] for k in sorted(d2)]
    print("\n  D_2 at k = %s:  %s"
          % (list(sorted(d2)), [str(v) for v in vals]))

    # ---- does it have a law?  Report, do not assert.
    integral = all(v.denominator == 1 for v in vals)
    print("  all integers: %s" % integral)
    if integral:
        ints = [int(v) for v in vals]
        alt = all(abs(ints[i]) == abs(ints[0]) for i in range(len(ints)))
        print("  constant magnitude: %s" % alt)
        diffs = [ints[i + 1] - ints[i] for i in range(len(ints) - 1)]
        print("  first differences: %s" % diffs)

    # ---- controls (b) and (c), and the payoff
    print("\nDepth-2 fit: drop the TWO tallest in-onset cells, use n=2k-1 and")
    print("n=2k instead.  The dropped cells are the holdout.")
    print("  %-4s %-10s %-24s %-24s"
          % ("k", "agrees", "predicts T(3k, 2k)", "predicts T(3k+1, 2k+1)"))
    good_all, vacuous = True, False
    for k in sorted(d2):
        P = fit_classical(tri, k)
        Q = fit_depth2(tri, k, d2=d2[k])
        if Q is None:
            print("  k=%d  not enough cells" % k)
            continue
        agrees = same(P, Q)
        good_all &= agrees
        h1 = peval(Q, 3 * k)
        h2 = peval(Q, 3 * k + 1)
        t1 = tri.get((3 * k, 2 * k))
        t2 = tri.get((3 * k + 1, 2 * k + 1))
        print("  %-4d %-10s %-24s %-24s"
              % (k, "yes" if agrees else "NO",
                 "%s %s" % (h1, "ok" if t1 is not None and h1 == t1 else "MISS"),
                 "%s %s" % (h2, "ok" if t2 is not None and h2 == t2 else "MISS")))
        # control (b): a wrong D_2 must break it
        bad = fit_depth2(tri, k, d2=d2[k] + 1)
        if bad is not None and same(P, bad):
            print("     control (b) FAILED at k=%d: a wrong D_2 still fits" % k)
            vacuous = True

    print("\nRED  (b) a corrupted D_2 breaks the depth-2 fit at every k   %s"
          % ("FAILED" if vacuous else "OK"))
    print("RED  (c) the depth-2 fit reproduces the two cells it never saw   %s"
          % ("OK" if good_all else "FAILED"))
    print("\nVERDICT: depth-2 Undertow on the square lattice %s"
          % ("HOLDS at k = 2..%d" % max(d2) if good_all and not vacuous
             else "DOES NOT hold"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
