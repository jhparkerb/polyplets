#!/usr/bin/env python3
"""Can T4 be tested at k = 6?  -- docs/time-at-the-bar.md A3.3.

T4 (results/open-conjectures.md) is N_k(+-1) = (+-2)^k for the diagonal-mirror
numerators, and it was REDUCED on 2026-07-31 to a pair of leading-coefficient
statements about the quasi-polynomials themselves:

    N_k(1)  = 2^k      <=>  lead(P_even_k) = lead(P_odd_k) = S^k / k!
    N_k(-1) = (-2)^k   <=>  lead(P_even_k - P_odd_k) = (-1)^k / (k-1)!

Both are verified exactly for k = 1..5 and neither is verified at k = 6.  The
reduction is the useful part here: testing T4 at k = 6 needs only the two
quasi-polynomials, NOT the numerator N_6, so the whole question is whether P_6
can be pinned on both parity classes with something left over to check it
against.

WHY IT WAS THOUGHT TO REFUSE.  results/dmirror-diagonals.md measures the onset
at S >= 2k+2.  At k = 6 that is S >= 14, and the banked dmirror strip data in
results/sym_counts.txt gives seven even points and six odd ones above it.
Degree k = 6 needs k+1 = 7 points to pin, so the even class pins with ZERO
holdout and the odd class does not pin at all.  A fit with no holdout is not
evidence and the level was correctly refused.

WHAT THIS PROBE ASKS.  S >= 2k+2 is a MEASURED onset, not a proved one -- it is
the smallest S from which the pinned polynomial happened to reproduce every
exact value at k <= 5.  If the true onset is lower, k = 6 gains points at both
parities and the test becomes possible.  So: pin each level from its deepest
points, walk BACKWARD to the smallest S the polynomial still reproduces, and
report the true onset per level and parity.  Then say whether k = 6 is
reachable, and if it is, run the T4 test there.

Every value used is exact integer input and every fit is exact rational
arithmetic (Fraction), so a "reproduces" is bit-exact and not a tolerance.

CONTROLS.
  (a) The pinned polynomials must reproduce the BANKED leading coefficients at
      k <= 5 -- lead = 1/k! per parity, and lead(P_even - P_odd) = (-1)^k/(k-1)!
      -- or the pinning is not producing the objects the reduction is about.
  (b) A level pinned on n points must be reported as having no holdout when it
      has none.  The script must never call a zero-holdout fit a measurement.
  (c) Degree detection must refuse a level whose differences do not flatten,
      rather than fitting the degree it was told to expect.

Usage: python3 experiments/dmirror_onset_probe.py

Target machine: ayr or dalby.  Cost: instant, exact rational arithmetic on a
tracked 423-row table.
"""

import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYM = os.path.join(ROOT, "results", "sym_counts.txt")


def load():
    """d[(S, k)] = number of dmirror animals, bbox SxS, S+k cells."""
    d = {}
    for ln in open(SYM):
        p = ln.split()
        if len(p) == 4 and p[0] == "dmirror_strip":
            S, n, v = int(p[1]), int(p[2]), int(p[3])
            d[(S, n - S)] = v
    return d


def newton_fit(pts):
    """Exact interpolating polynomial through (x, y) pairs, as a coefficient
    list in the monomial basis, highest degree last.  Fractions throughout."""
    xs = [Fraction(x) for x, _ in pts]
    ys = [Fraction(y) for _, y in pts]
    n = len(pts)
    # divided differences
    coef = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    # expand Newton form into monomial coefficients
    mono = [Fraction(0)] * n
    mono[0] = coef[0]
    basis = [Fraction(1)]          # product (x - x0)...(x - x_{j-1})
    for j in range(1, n):
        basis = [Fraction(0)] + basis            # multiply by x
        shifted = [c * (-xs[j - 1]) for c in ([Fraction(0)] + basis)[1:]]
        basis = [a + b for a, b in zip(basis, shifted + [Fraction(0)] * n)][:n + 1]
        for i, c in enumerate(basis):
            if i < n:
                mono[i] += coef[j] * c
    return mono


def evalpoly(mono, x):
    v = Fraction(0)
    for i, c in enumerate(mono):
        v += c * Fraction(x) ** i
    return v


def degree_of(pts, want_flat=3):
    """Smallest D whose D-th finite difference has want_flat equal tail values,
    on equally spaced points.  Returns None if nothing flattens."""
    ys = [Fraction(y) for _, y in pts]
    cur = ys
    for D in range(0, len(ys)):
        if len(cur) >= want_flat and len(set(cur[-want_flat:])) == 1:
            return D
        cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
    return None


def series(d, k, parity):
    pts = sorted((S, v) for (S, kk), v in d.items()
                 if kk == k and S % 2 == parity)
    # longest gap-free run in steps of 2, taken from the deep end
    if not pts:
        return []
    out = [pts[-1]]
    for S, v in reversed(pts[:-1]):
        if S == out[0][0] - 2:
            out.insert(0, (S, v))
        else:
            break
    return out


def analyse(d, k, parity, verbose=True):
    pts = series(d, k, parity)
    if len(pts) < k + 2:
        return None, "only %d contiguous points, need %d to pin with a " \
                     "holdout" % (len(pts), k + 2)
    D = degree_of(pts)
    if D is None:
        return None, "differences never flatten -- no polynomial regime"
    if D != k:
        return None, "degree came out %s, expected %d" % (D, k)
    pin = pts[-(D + 1):]
    mono = newton_fit(pin)
    # walk backward: smallest S the polynomial still reproduces exactly
    onset = pin[0][0]
    hold = 0
    for S, v in reversed(pts[:-(D + 1)]):
        if evalpoly(mono, S) == v:
            onset = S
            hold += 1
        else:
            break
    return (mono, onset, hold, pin[0][0], len(pts)), None


def main():
    d = load()
    print("dmirror diagonals -- true onset per level and parity")
    print("(pinned on the deepest k+1 points, then walked backward)\n")
    print("  %-4s %-7s %-7s %-9s %-9s %-8s" %
          ("k", "parity", "points", "pinned@S", "onset", "holdouts"))

    fits = {}
    for k in range(0, 8):
        for parity, pname in ((0, "even"), (1, "odd")):
            res, err = analyse(d, k, parity)
            if res is None:
                print("  %-4d %-7s %s" % (k, pname, err))
                continue
            mono, onset, hold, pinat, npts = res
            fits[(k, parity)] = mono
            print("  %-4d %-7s %-7d %-9d %-9d %-8d%s"
                  % (k, pname, npts, pinat, onset, hold,
                     "   <- 2k+2 = %d" % (2 * k + 2)))

    print("\nControl (a): the banked leading coefficients, k <= 5.")
    ok = True
    for k in range(1, 6):
        me = fits.get((k, 0))
        mo = fits.get((k, 1))
        if me is None or mo is None:
            print("  k=%d  NOT PINNED -- control cannot run" % k)
            ok = False
            continue
        import math
        want_lead = Fraction(1, math.factorial(k))
        le, lo = me[k], mo[k]
        diff = [a - b for a, b in zip(me, mo)]
        want_diff = Fraction((-1) ** k, math.factorial(k - 1))
        got_diff = diff[k - 1]
        good = (le == want_lead and lo == want_lead and got_diff == want_diff)
        print("  k=%d  lead_even=%s lead_odd=%s (want %s)   "
              "lead(diff)=%s (want %s)   %s"
              % (k, le, lo, want_lead, got_diff, want_diff,
                 "OK" if good else "MISMATCH"))
        ok &= good
    print("  control (a): %s" % ("OK" if ok else "FAILED"))
    if not ok:
        print("\nCONTROL FAILED -- the k=6 verdict below is not worth reading")

    print("\nT4 at k = 6, if it is reachable:")
    me, mo = fits.get((6, 0)), fits.get((6, 1))
    if me is None or mo is None:
        print("  NOT REACHABLE on banked data -- ", end="")
        print("even pinned: %s, odd pinned: %s"
              % (me is not None, mo is not None))
        print("  T4 stands verified to k = 5 and untested at k = 6.")
        return 0
    import math
    want_lead = Fraction(1, math.factorial(6))
    diff = [a - b for a, b in zip(me, mo)]
    want_diff = Fraction(1, math.factorial(5))
    print("  lead(P_even_6) = %s   (T4 wants %s)" % (me[6], want_lead))
    print("  lead(P_odd_6)  = %s   (T4 wants %s)" % (mo[6], want_lead))
    print("  lead(P_even_6 - P_odd_6) = %s   (T4 wants %s)"
          % (diff[5], want_diff))
    verdict = (me[6] == want_lead and mo[6] == want_lead
               and diff[5] == want_diff)
    print("  T4 at k=6: %s" % ("CONFIRMED" if verdict else "REFUTED"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
