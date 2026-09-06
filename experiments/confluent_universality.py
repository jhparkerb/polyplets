#!/usr/bin/env python3
"""The correction-to-scaling exponent, king against square, one method, matched
length -- docs/time-at-the-bar.md (deleted) A1.5.

WHAT THIS IS FOR.  results/growth-constant.md compared the LEADING exponents
of the two lattices (theta_king = -0.9997, theta_square = -0.9995 at N = 40)
and found them equal to the resolution the method has.  A leading exponent is
the weakest thing universality predicts: -1 is a round number that several
mechanisms would produce.  The sharper test is the CONFLUENT exponent Delta_1,
the power of the first correction to scaling, which universality also says must
match.  This measures it on both lattices with one script, one grid, and the
same number of terms on each side.

WHAT THE TREE SAYS BEFORE THIS RUNS, stated so the item is not oversold.
docs/time-at-the-bar.md (deleted) A1.5 says results/growth-constant.md "already fits a
confluent term on the king side (Delta_1 = 1/2)".  That is not quite what that
file says, and the difference matters:

  - the Delta_1 = 1/2 in it is the PAPER's, from a ratio-method fit in the
    literature, not this project's measurement;
  - series-analysis-da.md:60 is explicit -- "The DA does not independently pin
    Delta_1 (that needs sub-dominant-singularity analysis); it is consistent
    with the paper's Delta_1 = 1/2 picture, not an independent test of it."

So there is no banked king Delta_1 to compare a square one against.  This script
measures BOTH from scratch, which is the only way the comparison means anything.

THE ANSATZ, and why the fit is a scan and not a solve.

    a(n) = B * lambda^n * n^theta * exp(c * n^(-Delta))

is nonlinear in Delta but exactly LINEAR in (ln B, ln lambda, theta, c) once
Delta is fixed:

    ln a(n) = ln B + n*ln(lambda) + theta*ln(n) + c*n^(-Delta)

So: put Delta on a grid, least-squares the other four at each grid point, and
take the Delta that minimises the residual.

The exponentiated form is deliberate and it is not the textbook one, which is
(1 + c*n^-Delta).  The two agree to first order and differ at O(c^2 n^-2Delta),
i.e. inside the next correction the ansatz does not model either way.  Writing
it as exp() makes the solve EXACT for its own ansatz instead of carrying a
linearisation error that the fit then pays for by moving Delta.  That is not a
hypothetical: the first version of this script planted (1 + c*n^-Delta) and
fitted the linearised log, and control (a) below caught it -- planted Delta of
0.5 and 1.0 came back as 0.290 and 0.860, a bias of the same size as the
effect being measured.  The control did its job on the script before the script
was used on anything.

The shape of the residual curve is the answer to the real question -- a sharp
minimum means 40 terms resolve Delta_1, a flat valley means they do not, and the
honest report in the flat case is "cannot tell", not a number.

THE CONTROLS ARE THE POINT, as in experiments/stretched_exponential_fit.py.

  (a) EXACTNESS.  On data of exactly this form the scan must return the planted
      Delta and a residual at the arithmetic floor.  Calibrates the solver and
      nothing else.
  (b) RESOLVING POWER, which is what decides whether the real answer is
      reportable.  Plant Delta = 0.5 and Delta = 1.0 UNDER a second, unmodelled
      correction of the size the real series carries, and ask whether the scan
      can still tell them apart from 40 terms.  If it cannot separate 0.5 from
      1.0 on synthetic data, then no king-vs-square agreement measured here is
      evidence of anything, and this script must say so.
  (c) IDENTIFIABILITY.  theta and Delta trade against each other.  With theta
      free the scan must not be able to buy a better residual by moving theta
      onto the correction; the control plants theta = -1, Delta = 1 and checks
      both come back.
  (d) PROVENANCE.  A square series whose head is not A001168, or a king series
      whose head is not A006770, is refused rather than analysed.

Usage:
    python3 experiments/confluent_universality.py            # controls + both lattices
    python3 experiments/confluent_universality.py --selftest # controls only

Target machine: ayr or dalby (project code does not run on gympie).  Cost:
seconds, a few MB.  No compute budget needed.
"""

import argparse
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KING_HEAD = [1, 4, 20, 110, 638, 3832]      # A006770
SQUARE_HEAD = [1, 2, 6, 19, 63, 216]        # A001168

KING_PATH = os.path.join(ROOT, "results", "b006770_upload.txt")
SQUARE_PATH = os.path.join(ROOT, "results", "b001168_external.txt")

# Delta grid.  0.05 is finer than anything 40 terms could resolve, which is
# deliberate: the point is to see the WIDTH of the minimum, not to land on a
# grid point.
DELTA_GRID = np.arange(0.10, 3.001, 0.005)


def load_bfile(path, head, name):
    """[None, a(1), a(2), ...] from an OEIS-style b-file, head-checked."""
    banked = {}
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            p = ln.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit():
                banked[int(p[0])] = int(p[1])
    if not banked:
        raise ValueError("%s: no terms parsed" % path)
    nmax = max(banked)
    seq = [None] + [banked[n] for n in range(1, nmax + 1)]
    got = seq[1:1 + len(head)]
    if got != head:
        raise ValueError("not %s: head is %s, expected %s" % (name, got, head))
    return seq


def fit_at_delta(seq, lo, hi, delta):
    """Least-squares (lnB, lnlam, theta, c) at fixed Delta over n in [lo, hi].

    Returns (rss, lam, theta, c).  rss is the sum of squared residuals in
    ln a(n), which is the natural scale: a residual of 1e-6 means the ansatz
    reproduces every term to about a part in 10^6.
    """
    ns = np.arange(lo, hi + 1, dtype=float)
    y = np.array([math.log(seq[int(n)]) for n in ns])
    A = np.column_stack([np.ones_like(ns), ns, np.log(ns), ns ** (-delta)])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    return float(resid @ resid), math.exp(coef[1]), float(coef[2]), float(coef[3])


def scan(seq, lo, hi):
    """Minimise the residual over the Delta grid.  Returns the best fit and the
    grid, so callers can report the width of the valley rather than a point."""
    rows = []
    for d in DELTA_GRID:
        try:
            rows.append((d,) + fit_at_delta(seq, lo, hi, float(d)))
        except (ValueError, np.linalg.LinAlgError):
            continue
    if not rows:
        return None, []
    best = min(rows, key=lambda r: r[1])
    return best, rows


def valley(rows, best, factor=2.0):
    """The Delta interval over which the residual stays within `factor` of its
    minimum.  This is the honest error bar: it is what the data cannot
    distinguish, not a standard deviation from a model nobody verified."""
    lo, hi = None, None
    for d, rss, *_ in rows:
        if rss <= factor * best[1]:
            lo = d if lo is None else min(lo, d)
            hi = d if hi is None else max(hi, d)
    return lo, hi


def synth(lam, theta, c, delta, N, extra=None):
    """B=1 series of exactly the modelled form, optionally with a second,
    UNMODELLED correction `extra(n)` multiplied in.

    Integers, because a real series is integers and the rounding is part of
    what 40 terms can resolve."""
    out = [None]
    for n in range(1, N + 1):
        v = lam ** n * n ** theta * math.exp(c * n ** (-delta))
        if extra is not None:
            v *= extra(n)
        out.append(max(1, int(round(v))))
    return out


def calibrate(lam, theta, c, N, lo, extra):
    """Recovered Delta as a function of planted Delta.

    The scan is BIASED -- an unmodelled higher correction pushes the recovered
    exponent around -- so a recovered number is not a Delta and must not be
    read as one.  What it is, is a monotone image of one.  This maps the image
    so a real measurement can be inverted through it, and so the report can say
    what real interval of Delta the data actually excludes."""
    rows = []
    for d in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
        s = synth(lam, theta, c, d, N, extra=extra)
        best, _ = scan(s, lo, N)
        rows.append((d, best[0] if best else float('nan')))
    return rows


def controls():
    ok = True

    # (a) EXACTNESS -- exact form, no unmodelled correction.
    for lam, th, c, d in ((7.11, -1.0, 0.8, 0.5), (4.06, -1.0, 0.8, 1.0)):
        s = synth(lam, th, c, d, 40)
        best, _ = scan(s, 8, 40)
        good = best is not None and abs(best[0] - d) < 0.10
        print("RED  exact form lam=%.2f Delta=%.1f recovered as %.3f   %s"
              % (lam, d, best[0] if best else float('nan'),
                 "OK" if good else "FAILED"))
        ok &= good

    # (b) RESOLVING POWER -- the control that decides whether the real answer
    #     is reportable.  A second correction the ansatz does not model, of the
    #     size a real series carries, sits underneath the planted Delta.
    got = {}
    for d in (0.5, 1.0):
        s = synth(7.11, -1.0, 0.8, d, 40, extra=lambda n: 1.0 + 0.5 / n ** 2)
        best, _ = scan(s, 8, 40)
        got[d] = best[0] if best else float('nan')
        print("     planted Delta=%.1f under an unmodelled 0.5/n^2 -> %.3f"
              % (d, got[d]))
    separates = abs(got[0.5] - got[1.0]) > 0.20
    print("RED  0.5 and 1.0 stay distinguishable under an unmodelled "
          "correction (gap %.3f)   %s"
          % (abs(got[0.5] - got[1.0]), "OK" if separates else "FAILED"))
    ok &= separates

    # (c) IDENTIFIABILITY -- theta must not absorb the correction.
    s = synth(7.11, -1.0, 0.8, 1.0, 40)
    best, _ = scan(s, 8, 40)
    good = best is not None and abs(best[3] + 1.0) < 0.05
    print("RED  theta is recovered as %.4f, not traded against Delta   %s"
          % (best[3] if best else float('nan'), "OK" if good else "FAILED"))
    ok &= good

    # (d) PROVENANCE -- a wrong head is refused.
    try:
        load_bfile(SQUARE_PATH, KING_HEAD, "A006770")
        print("RED  a wrong-head series is refused   FAILED")
        ok = False
    except ValueError:
        print("RED  a wrong-head series is refused   OK")

    return ok


def report(name, seq, N, lo):
    best, rows = scan(seq, lo, N)
    if best is None:
        print("  %-8s N=%-3d  NO FIT" % (name, N))
        return None
    d, rss, lam, th, c = best
    vlo, vhi = valley(rows, best)
    print("  %-8s N=%-3d  Delta=%.3f  [%.2f, %.2f]  lambda=%.5f  "
          "theta=%+.4f  c=%+.3f  rss=%.2e"
          % (name, N, d, vlo, vhi, lam, th, c, rss))
    return d, vlo, vhi, lam, th


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    print("confluent exponent, king vs square -- controls first")
    ok = controls()
    if not ok:
        print("\nCONTROLS FAILED -- no measurement below is worth reading")
        return 1
    if args.selftest:
        print("\ncontrols GREEN")
        return 0

    king = load_bfile(KING_PATH, KING_HEAD, "A006770")
    square = load_bfile(SQUARE_PATH, SQUARE_HEAD, "A001168")
    print("\nking terms: %d   square terms: %d" % (len(king) - 1, len(square) - 1))

    print("\ncalibration -- recovered Delta as a function of planted Delta,")
    print("with an unmodelled 0.5/n^2 underneath (N=40, window from n=8):")
    for lat, lam in (("king", 7.11), ("square", 4.06)):
        rows = calibrate(lam, -1.0, 0.8, 40, 8, lambda n: 1.0 + 0.5 / n ** 2)
        print("  %-8s " % lat
              + "  ".join("%.2f->%.2f" % (a, b) for a, b in rows))
    print("  A recovered value is an IMAGE of Delta, not Delta -- and note the")
    print("  map is NOT monotone at the bottom: 0.25 lands above 0.50 on both")
    print("  lattices, so below about 0.75 it cannot be inverted at all.")

    print("\nmatched length, the comparison A1.5 asks for:")
    k = report("king", king, 40, 8)
    s = report("square", square, 40, 8)

    print("\nthe square series at full length, as a convergence check:")
    for N in (50, 60, 70):
        if len(square) - 1 >= N:
            report("square", square, N, 8)

    # The residual valley is NOT the error bar.  It measures how sharply the
    # grid resolves Delta at one fixed window, and the window sweep below moves
    # the answer well outside it -- king's [0.57, 0.58] against a sweep that
    # runs to 0.625.  The spread across windows is the honest uncertainty,
    # because choosing a window start is a free parameter nobody has pinned.
    print("\nwindow sensitivity (start of the fit window, matched N=40) --")
    print("this spread, not the residual valley, is the error bar:")
    kd, sd = [k[0]] if k else [], [s[0]] if s else []
    for lo in (6, 10, 12, 15):
        rk = report("king", king, 40, lo)
        rs = report("square", square, 40, lo)
        if rk:
            kd.append(rk[0])
        if rs:
            sd.append(rs[0])

    if kd and sd:
        print("\nking   Delta over windows: %s -> %.2f .. %.2f"
              % (" ".join("%.3f" % d for d in kd), min(kd), max(kd)))
        print("square Delta over windows: %s -> %.2f .. %.2f"
              % (" ".join("%.3f" % d for d in sd), min(sd), max(sd)))
        overlap = not (max(kd) < min(sd) or max(sd) < min(kd))
        print("the window ranges %s"
              % ("OVERLAP" if overlap else "DO NOT overlap"))
        print("\nRead this against the calibration above before calling it a")
        print("measurement of Delta_1: the bias depends on the size and SIGN of")
        print("the corrections the ansatz does not model, and the real series")
        print("have c < 0 where the calibration planted c > 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
