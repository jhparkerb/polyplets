#!/usr/bin/env python3
"""Honest error budget for the below-onset defect estimators.

The old controls were vacuous: `defect_amplitude.py` used a control whose
correction series TERMINATES at 1/k^2, so any Richardson of order >= 2
interpolates it exactly and reports ~1e-15 "error".  That measures floating
point, not truncation of a real asymptotic series.  `defect_nine_exponent.py`
had no control at all on the fitted rate r.

This script supplies:

  1. a control SUITE of non-terminating flavours with KNOWN amplitude C, run
     through the identical Richardson pipeline over the same k window the real
     data has -> the achievable digit count per Richardson order;
  2. the C_1 extraction redone in mpmath at 60 digits from the exact Fractions,
     so float noise is not in the budget;
  3. a control for the fitted exponential rate r (true rates 9, 8.9, 8.95,
     9.1), with and without a realistic 1/k correction;
  4. a theta-coherence scan: for candidate theta, the SPREAD of C across
     Richardson orders is minimised at the true theta; calibrated against an
     exactly-built sequence of known theta;
  5. per-j amplitude-family table with error bars taken from (1) at that j's
     window, plus the theta-misspecification term.

Run: python3 experiments/defect_controls.py
"""
import os
import sys
from fractions import Fraction as F

import mpmath as mp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law  # noqa: E402

mp.mp.dps = 60


def mpf_frac(x):
    """Exact Fraction -> mpf at the current working precision."""
    return mp.mpf(x.numerator) / mp.mpf(x.denominator)


def richardson_mp(pts, order):
    """pts = [(k, A_k)] with A_k an mpf.  Fit A = C + c1/k + ... + c_order/k^order
    on the LAST order+1 points and return C.  Solved with mpmath at mp.dps."""
    n = order + 1
    if len(pts) < n:
        return None
    use = pts[-n:]
    A = mp.matrix(n, n)
    b = mp.matrix(n, 1)
    for r, (k, v) in enumerate(use):
        for c in range(n):
            A[r, c] = mp.mpf(1) / mp.mpf(k) ** c
        b[r] = v
    return mp.lu_solve(A, b)[0]


# ---------------------------------------------------------------- control suite

def ctrl_terminating(C, k, th):
    """(old, vacuous) terminating correction series."""
    return C * mp.mpf(9) ** k * mp.mpf(k) ** th * (1 + mp.mpf("0.7") / k
                                                   - mp.mpf(2) / k ** 2)


def ctrl_smooth(C, k, th):
    """(a) smooth infinite 1/k series: (1+0.7/k)/(1-0.3/k)."""
    return (C * mp.mpf(9) ** k * mp.mpf(k) ** th
            * (1 + mp.mpf("0.7") / k) / (1 - mp.mpf("0.3") / k))


def ctrl_geom(C, k, th):
    """(a') geometric tail sum_{m>=1} (0.8/k)^m = 1/(1-0.8/k)."""
    return (C * mp.mpf(9) ** k * mp.mpf(k) ** th / (1 - mp.mpf("0.8") / k))


def ctrl_halfpow(C, k, th):
    """(b) half-power contaminant 1 + 0.5/k^1.5."""
    return (C * mp.mpf(9) ** k * mp.mpf(k) ** th
            * (1 + mp.mpf("0.5") / mp.mpf(k) ** mp.mpf("1.5")))


def ctrl_log(C, k, th):
    """(c) log contaminant 1 + 0.4 log k / k."""
    return (C * mp.mpf(9) ** k * mp.mpf(k) ** th
            * (1 + mp.mpf("0.4") * mp.log(k) / k))


FLAVOURS = [
    ("terminating (old)", ctrl_terminating),
    ("(a) smooth 1/k", ctrl_smooth),
    ("(a') geometric tail", ctrl_geom),
    ("(b) half-power 1/k^1.5", ctrl_halfpow),
    ("(c) log k / k", ctrl_log),
]

CTRL_C = mp.mpf("0.0512345")


# ------------------------------------------------- data-matched control
def fit_coeffs(pts, order):
    """Fit A_k = C(1 + a1/k + ... + a_order/k^order) on the last order+1 points.
    Returns (C, [a1..a_order])."""
    n = order + 1
    use = pts[-n:]
    A = mp.matrix(n, n)
    b = mp.matrix(n, 1)
    for r, (k, v) in enumerate(use):
        for c in range(n):
            A[r, c] = mp.mpf(1) / mp.mpf(k) ** c
        b[r] = v
    x = mp.lu_solve(A, b)
    C = x[0]
    return C, [x[i] / C for i in range(1, n)]


def matched_control(pts, ks, order=5, ntail=80, rho_cap=mp.mpf(4)):
    """Build a NON-terminating control whose leading 1/k coefficients are those
    the real data actually has, continued by a geometric tail.  This is the
    self-calibrated error bar: same window, same correction magnitudes."""
    C, a = fit_coeffs(pts, order)
    rho = a[-1] / a[-2] if a[-2] != 0 else mp.mpf(1)
    if abs(rho) > rho_cap:
        rho = mp.sign(rho) * rho_cap
    if abs(rho) < mp.mpf("0.25"):
        rho = mp.sign(rho) * mp.mpf("0.25") if rho != 0 else mp.mpf("0.25")
    out = []
    for k in ks:
        s = mp.mpf(1)
        for m, am in enumerate(a, start=1):
            s += am / mp.mpf(k) ** m
        cur = a[-1]
        for t in range(1, ntail + 1):
            cur = cur * rho
            s += cur / mp.mpf(k) ** (order + t)
        out.append((k, C * s))
    return C, out, rho


def control_points(fn, ks, th, C=CTRL_C, th_used=None):
    """Build A_k = value * 9^-k * k^-th_used for the control flavour fn."""
    if th_used is None:
        th_used = th
    return [(k, fn(C, k, th) * mp.mpf(9) ** (-k) * mp.mpf(k) ** (-th_used))
            for k in ks]


# ---------------------------------------------------------------- real data

P, tri = read_pk(), read_tri()


def defect_points(j, th, kmax=19):
    """[(k, D_j(k) * 9^-k * k^-th)] as mpf, from exact Fractions."""
    out = []
    for k in range(2, kmax + 1):
        n = 2 * k + 1 - j
        H = n - k
        if H < 1 or (n, H) not in tri or k not in P:
            continue
        D = F(tri[(n, H)]) - law(n, k, P)
        if D <= 0:
            continue
        out.append((k, mpf_frac(D) * mp.mpf(9) ** (-k) * mp.mpf(k) ** (-th)))
    return out


def defect_raw(j, kmax=19):
    out = []
    for k in range(2, kmax + 1):
        n = 2 * k + 1 - j
        H = n - k
        if H < 1 or (n, H) not in tri or k not in P:
            continue
        D = F(tri[(n, H)]) - law(n, k, P)
        if D <= 0:
            continue
        out.append((k, D))
    return out


A1_EXACT = mp.sqrt(6) / 27
C1_PRED = A1_EXACT / mp.sqrt(mp.pi)


def relerr(a, b):
    return float((a - b) / b)


def sec(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ================================================================= 1. suite
def task1():
    sec("1. CONTROL SUITE: achieved relative error in C, by Richardson order")
    ks = [k for k, _ in defect_points(1, -0.5)]
    print("  k window = %d..%d (%d points), same as the j=1 data. True C = %s"
          % (ks[0], ks[-1], len(ks), mp.nstr(CTRL_C, 8)))
    print()
    hdr = "  %-24s" % "flavour" + "".join("  order %d " % o for o in range(2, 7))
    print(hdr)
    for name, fn in FLAVOURS:
        pts = control_points(fn, ks, -0.5)
        row = "  %-24s" % name
        for o in range(2, 7):
            r = richardson_mp(pts, o)
            row += "  %8.1e" % abs(relerr(r, CTRL_C)) if r is not None else "  %8s" % "-"
        print(row)
    print()
    print("  Same suite, float64 pipeline (the shipped one), for comparison:")
    for name, fn in FLAVOURS:
        pts = [(k, float(v)) for k, v in control_points(fn, ks, -0.5)]
        row = "  %-24s" % name
        for o in range(2, 7):
            n = o + 1
            use = pts[-n:]
            M = [[1.0] + [1.0 / p[0] ** i for i in range(1, n)] + [p[1]]
                 for p in use]
            for c in range(n):
                piv = max(range(c, n), key=lambda r: abs(M[r][c]))
                M[c], M[piv] = M[piv], M[c]
                M[c] = [x / M[c][c] for x in M[c]]
                for r in range(n):
                    if r != c:
                        f = M[r][c]
                        M[r] = [M[r][i] - f * M[c][i] for i in range(n + 1)]
            row += "  %8.1e" % abs((M[0][n] - float(CTRL_C)) / float(CTRL_C))
        print(row)
    print()
    print("  Data-MATCHED control: same k window, leading 1/k coefficients")
    print("  taken from the real D_j data itself, continued by a geometric")
    print("  tail (so it does NOT terminate).  This is the self-calibrated bar.")
    print("  %3s %10s %8s" % ("j", "tail rho", "") + "".join(
        "  order %d " % o for o in range(2, 7)))
    for j in range(1, 8):
        kk = [k for k, _ in defect_raw(j)]
        if len(kk) < 7:
            continue
        dp = defect_points(j, mp.mpf(j) - mp.mpf("1.5"))
        Ctrue, cpts, rho = matched_control(dp, kk)
        row = "  %3d %10.3f %8s" % (j, float(rho), "")
        for o in range(2, 7):
            r = richardson_mp(cpts, o)
            row += "  %8.1e" % abs(relerr(r, Ctrue)) if r is not None \
                else "  %8s" % "-"
        print(row)


# ================================================================= 2/3. C_1
def task23():
    sec("2/3. C_1 IN EXACT/HIGH PRECISION ARITHMETIC, AND ITS HONEST DIGITS")
    pts = defect_points(1, -0.5)
    print("  mpmath (dps=%d) from exact Fractions; predicted "
          "sqrt(6)/(27 sqrt(pi)) = %s" % (mp.mp.dps, mp.nstr(C1_PRED, 15)))
    print("  %6s %26s %14s %14s" % ("order", "C_1 (mp)", "rel vs pred",
                                    "step vs prev"))
    prev = None
    vals = {}
    for o in range(1, 8):
        r = richardson_mp(pts, o)
        if r is None:
            continue
        vals[o] = r
        step = "" if prev is None else "%14.1e" % abs(float((r - prev) / r))
        print("  %6d %26s %14.2e %14s"
              % (o, mp.nstr(r, 14), relerr(r, C1_PRED), step))
        prev = r
    print()
    print("  float64 pipeline, same orders (shipped defect_amplitude.py):")
    fpts = [(k, float(v)) for k, v in pts]
    for o in range(2, 8):
        n = o + 1
        use = fpts[-n:]
        M = [[1.0] + [1.0 / p[0] ** i for i in range(1, n)] + [p[1]]
             for p in use]
        for c in range(n):
            piv = max(range(c, n), key=lambda r: abs(M[r][c]))
            M[c], M[piv] = M[piv], M[c]
            M[c] = [x / M[c][c] for x in M[c]]
            for r in range(n):
                if r != c:
                    f = M[r][c]
                    M[r] = [M[r][i] - f * M[c][i] for i in range(n + 1)]
        v = M[0][n]
        print("     order %d: %.12f  rel vs pred %+.2e   (mp - float = %.1e)"
              % (o, v, (v - float(C1_PRED)) / float(C1_PRED),
                 abs(float(vals[o]) - v)))
    print()
    print("  Signature test: how does |C(o) - C(o-1)| behave with order?")
    print("  A convergent smooth 1/k series shrinks it; a half-power or log")
    print("  contaminant stalls it.  Real data vs the three flavours,")
    print("  each normalised to its own order-2 step:")
    ks = [k for k, _ in pts]
    rows = [("real data", vals)]
    for name, fn in FLAVOURS[1:]:
        cv = {}
        cp = control_points(fn, ks, -0.5)
        for o in range(1, 8):
            r = richardson_mp(cp, o)
            if r is not None:
                cv[o] = r
        rows.append((name, cv))
    print("  %-24s" % "" + "".join("  o%d->%d " % (o - 1, o)
                                   for o in range(3, 8)))
    for name, cv in rows:
        row = "  %-24s" % name
        base = abs(cv[2] - cv[1])
        for o in range(3, 8):
            if o in cv and o - 1 in cv:
                row += "  %7.1e" % float(abs(cv[o] - cv[o - 1]) / base)
            else:
                row += "  %7s" % "-"
        print(row)
    print()
    print("  The real data's step ratios turn UP after order 5, which none of")
    print("  the pure-1/k controls do.  How big a half-power contaminant")
    print("  eps/k^1.5 on top of the matched control reproduces that turn-up,")
    print("  and what error in C does it then cause at order 4/5?")
    _, cpts, _ = matched_control(pts, ks)
    Ctrue, _ = fit_coeffs(pts, 5)
    print("  %8s %12s %12s %12s"
          % ("eps", "|C6-C5|/|C3-C2|", "err C(4)", "err C(5)"))
    for eps in ("0", "0.0005", "0.002", "0.01", "0.05"):
        e = mp.mpf(eps)
        cp = [(k, v * (1 + e / mp.mpf(k) ** mp.mpf("1.5")))
              for k, v in cpts]
        cv = {o: richardson_mp(cp, o) for o in range(1, 8)}
        ratio = float(abs(cv[6] - cv[5]) / abs(cv[3] - cv[2]))
        print("  %8s %12.1e %12.1e %12.1e"
              % (eps, ratio, abs(relerr(cv[4], Ctrue)),
                 abs(relerr(cv[5], Ctrue))))
    dv = vals
    print("  real data                 |C6-C5|/|C3-C2| = %.1e"
          % float(abs(dv[6] - dv[5]) / abs(dv[3] - dv[2])))
    print()
    print("  Uniqueness of the recognition: constants sqrt(m)/(n sqrt(pi)),")
    print("  m<=200, n<=400, within 1e-6 relative of the measured C_1:")
    seen = []
    Cm = vals[4]
    for m in range(1, 201):
        for n in range(1, 401):
            v = mp.sqrt(m) / n / mp.sqrt(mp.pi)
            if abs(v / Cm - 1) < mp.mpf("1e-6"):
                if not any(abs(v / s - 1) < mp.mpf("1e-30") for s in seen):
                    seen.append(v)
                    print("     sqrt(%d)/(%d sqrt(pi)) = %s" % (m, n, mp.nstr(v, 12)))
    print("     -> %d distinct value(s)" % len(seen))


# ================================================================= 4. rate
def rate_est(seq, th):
    """The shipped rate estimator: r_k = (v/v0)(k0/k)^th, one Richardson step."""
    R = [(k, (v / v0) * (mp.mpf(k0) / mp.mpf(k)) ** th)
         for (k0, v0), (k, v) in zip(seq, seq[1:])]
    (k1, r1), (k2, r2) = R[-2], R[-1]
    return R[-1][1], (k2 * r2 - k1 * r1) / (k2 - k1)


def rate_est_hi(seq, th, order):
    """Higher-order Richardson on the same r_k sequence."""
    R = [(k, (v / v0) * (mp.mpf(k0) / mp.mpf(k)) ** th)
         for (k0, v0), (k, v) in zip(seq, seq[1:])]
    return richardson_mp(R, order)


def task4():
    sec("4. CONTROL FOR THE FITTED EXPONENTIAL RATE r")
    ks = list(range(2, 20))
    print("  (i) clean controls: exactly C r^k k^th, theta known and used.")
    print("  %8s %6s %12s %14s %14s"
          % ("true r", "theta", "raw r(19)", "Rich (order1)", "Rich order3"))
    for r_true in ("9", "8.9", "8.95", "9.1"):
        for th in (mp.mpf("-0.5"), mp.mpf("0.5")):
            seq = [(k, mp.mpf(r_true) ** k * mp.mpf(k) ** th) for k in ks]
            raw, rich = rate_est(seq, th)
            r3 = rate_est_hi(seq, th, 3)
            print("  %8s %6s %12.6f %14.6f %14.6f"
                  % (r_true, mp.nstr(th, 3), float(raw), float(rich),
                     float(r3)))
    print()
    print("  (ii) realistic controls: same rates times the flavour-(a) smooth")
    print("       1/k series -- i.e. what a real asymptotic sequence looks like.")
    print("  %8s %6s %12s %14s %14s"
          % ("true r", "theta", "raw r(19)", "Rich (order1)", "Rich order3"))
    for r_true in ("9", "8.9", "8.95", "9.1"):
        for th in (mp.mpf("-0.5"), mp.mpf("0.5")):
            seq = [(k, mp.mpf(r_true) ** k * mp.mpf(k) ** th
                    * (1 + mp.mpf("0.7") / k) / (1 - mp.mpf("0.3") / k))
                   for k in ks]
            raw, rich = rate_est(seq, th)
            r3 = rate_est_hi(seq, th, 3)
            print("  %8s %6s %12.6f %14.6f %14.6f"
                  % (r_true, mp.nstr(th, 3), float(raw), float(rich),
                     float(r3)))
    print()
    print("  (iii) theta misspecified by delta, true rate exactly 9,")
    print("        flavour-(a) correction present:")
    print("  %8s %12s %14s %14s" % ("delta", "raw r(19)", "Rich order1",
                                    "Rich order3"))
    for d in ("-0.2", "-0.1", "0", "0.1", "0.2"):
        th_true = mp.mpf("-0.5")
        th_used = th_true + mp.mpf(d)
        seq = [(k, mp.mpf(9) ** k * mp.mpf(k) ** th_true
                * (1 + mp.mpf("0.7") / k) / (1 - mp.mpf("0.3") / k))
               for k in ks]
        raw, rich = rate_est(seq, th_used)
        r3 = rate_est_hi(seq, th_used, 3)
        print("  %8s %12.6f %14.6f %14.6f"
              % (d, float(raw), float(rich), float(r3)))
    print()
    print("  (ii-b) half-power and log corrections, true rate exactly 9:")
    print("  %-22s %12s %14s %14s"
          % ("correction", "raw r(19)", "Rich order1", "Rich order3"))
    for name, fn in FLAVOURS[1:]:
        th = mp.mpf("-0.5")
        seq = [(k, fn(mp.mpf(1), k, th)) for k in ks]
        raw, rich = rate_est(seq, th)
        r3 = rate_est_hi(seq, th, 3)
        print("  %-22s %12.6f %14.6f %14.6f"
              % (name, float(raw), float(rich), float(r3)))
    print()
    print("  (ii-c) DATA-MATCHED control, true rate exactly 9, per j:")
    print("  %3s %12s %14s %14s %12s"
          % ("j", "raw r(19)", "Rich order1", "Rich order3", "bias(ord3)"))
    for j in range(1, 7):
        kk = [k for k, _ in defect_raw(j)]
        if len(kk) < 7:
            continue
        th = mp.mpf(j) - mp.mpf("1.5")
        dp = defect_points(j, th)
        _, cpts, _ = matched_control(dp, kk)
        seq = [(k, v * mp.mpf(9) ** k * mp.mpf(k) ** th) for k, v in cpts]
        raw, rich = rate_est(seq, th)
        r3 = rate_est_hi(seq, th, 3)
        print("  %3d %12.6f %14.6f %14.6f %12.1e"
              % (j, float(raw), float(rich), float(r3), abs(float(r3) - 9.0)))
    print()
    print("  (iv) the real data, mpmath, at theta = j-3/2:")
    print("  %3s %6s %12s %14s %14s %14s %12s"
          % ("j", "pts", "raw r(19)", "Rich order1", "Rich order3",
             "bias-corr r3", "bar"))
    for j in range(1, 7):
        seq = [(k, mpf_frac(D)) for k, D in defect_raw(j)]
        if len(seq) < 5:
            continue
        th = mp.mpf(j) - mp.mpf("1.5")
        raw, rich = rate_est(seq, th)
        r3 = rate_est_hi(seq, th, 3)
        kk = [k for k, _ in defect_raw(j)]
        _, cpts, _ = matched_control(defect_points(j, th), kk)
        cseq = [(k, v * mp.mpf(9) ** k * mp.mpf(k) ** th) for k, v in cpts]
        cb = float(rate_est_hi(cseq, th, 3)) - 9.0
        print("  %3d %6d %12.6f %14.6f %14.6f %14.6f %12.1e"
              % (j, len(seq), float(raw), float(rich), float(r3),
                 float(r3) - cb, abs(cb)))
    print("  bias-corr r3 = order-3 Richardson minus the matched control's own")
    print("  offset from 9; 'bar' is that offset, the resolution at that j.")


# ================================================================= 5. theta
def coherence(pts_fn, thetas, orders=(2, 3, 4, 5)):
    """For each candidate theta: spread of C across Richardson orders,
    relative to the mean C.  Returns [(theta, spread, Cmean)]."""
    out = []
    for th in thetas:
        pts = pts_fn(th)
        cs = [richardson_mp(pts, o) for o in orders]
        cs = [c for c in cs if c is not None]
        if len(cs) < 2:
            continue
        m = sum(cs) / len(cs)
        if m == 0:
            continue
        out.append((th, float((max(cs) - min(cs)) / abs(m)), m))
    return out


def locate_min(res):
    """Parabolic refinement of the minimum of a spread scan."""
    i = min(range(len(res)), key=lambda i: res[i][1])
    if i == 0 or i == len(res) - 1:
        return res[i][0], None
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = res[i - 1], res[i], res[i + 1]
    d = (y0 - 2 * y1 + y2)
    if d == 0:
        return x1, None
    return x1 + 0.5 * (y0 - y2) / d * (x1 - x0), y1


def width_at(res, factor=10.0):
    """Width of the theta interval where spread <= factor * min spread."""
    mn = min(r[1] for r in res)
    good = [r[0] for r in res if r[1] <= factor * mn]
    return min(good), max(good)


def task5():
    sec("5. THETA-COHERENCE SCAN (spread of C across Richardson orders)")

    print("  Reported band: theta values whose spread is <= 3x the minimum")
    print("  spread.  Calibration = does the TRUE theta of a control land in")
    print("  its own band, and how wide is that band.")
    print()

    def scan(label, pts_fn, centre, half=0.12, step=0.001, truth=None):
        thetas = [centre - half + i * step
                  for i in range(int(round(2 * half / step)) + 1)]
        res = coherence(pts_fn, thetas)
        if not res:
            print("  %s: no data" % label)
            return
        xm, _ = locate_min(res)
        lo3, hi3 = width_at(res, 3.0)
        lo10, hi10 = width_at(res, 10.0)
        mn = min(r[1] for r in res)
        extra = ""
        if truth is not None:
            inb = "IN" if lo3 - 1e-9 <= truth <= hi3 + 1e-9 else "OUT"
            extra = "  true %+.3f err %+.4f (%s 3x band)" % (
                truth, xm - truth, inb)
        print("  %-30s min %+.4f  spread %.1e  3x[%+.4f,%+.4f] w=%.4f"
              "  10x w=%.4f%s"
              % (label, xm, mn, lo3, hi3, hi3 - lo3, hi10 - lo10, extra))

    ks = [k for k, _ in defect_points(1, -0.5)]
    print("  -- calibration controls (known theta, k window = %d..%d) --"
          % (ks[0], ks[-1]))
    for cname, cfn in FLAVOURS[1:]:
        scan("ctrl %s" % cname,
             lambda th, f=cfn: control_points(f, ks, mp.mpf("-0.5"),
                                              th_used=mp.mpf(th)),
             -0.5, truth=-0.5)
    print()
    print("  -- bias-calibrated theta per depth --")
    print("  The matched control has theta EXACTLY j-3/2 by construction, so")
    print("  wherever its own minimum lands is pure estimator bias.  Subtract")
    print("  that bias from the data's minimum and quote the 3x band as the")
    print("  half-width.")
    print("  %3s %10s %10s %9s %11s %8s   %s"
          % ("j", "data min", "ctrl min", "bias", "corrected", "half", "interval"))
    for j in range(1, 8):
        kk = [k for k, _ in defect_raw(j)]
        if len(kk) < 7:
            continue
        th_true = mp.mpf(j) - mp.mpf("1.5")
        half = 0.12 if j <= 4 else 0.20
        step = 0.001
        thetas = [float(th_true) - half + i * step
                  for i in range(int(round(2 * half / step)) + 1)]
        res_d = coherence(lambda th: defect_points(j, mp.mpf(th)), thetas)
        xd, _ = locate_min(res_d)
        lo, hi = width_at(res_d, 3.0)
        dp = defect_points(j, th_true)
        _, cpts, _ = matched_control(dp, kk)
        vals = {k: v * mp.mpf(9) ** k * mp.mpf(k) ** th_true for k, v in cpts}
        res_c = coherence(
            lambda th: [(k, vals[k] * mp.mpf(9) ** (-k)
                         * mp.mpf(k) ** (-mp.mpf(th))) for k in kk], thetas)
        xc, _ = locate_min(res_c)
        bias = xc - float(th_true)
        corr = xd - bias
        hw = max((hi - lo) / 2, step)
        print("  %3d %10.4f %10.4f %+9.4f %11.4f %8.4f   %.4f +- %.4f"
              % (j, xd, xc, bias, corr, hw, corr, hw))


# ================================================================= 6. family
def task6():
    sec("6. THE AMPLITUDE FAMILY, WITH ERROR BARS")
    print("  R_j := A_j/A_1 * (81/25)^(j-1),  A_j = C_j Gamma(j-1/2),")
    print("  C_j extracted by Richardson (order = min(4, pts-1)) at theta=j-3/2.")
    print()
    # error budget: per-j, run the control suite over that j's k window and take
    # the worst relative error across flavours (a),(b),(c) at the same order.
    print("  (a) control-suite relative error in C over each j's own k window")
    print("  %3s %6s %8s %10s %10s %10s %10s"
          % ("j", "pts", "order", "(a)", "(a')", "(b)", "(c)"))
    budget = {}
    for j in range(1, 8):
        kk = [k for k, _ in defect_raw(j)]
        if len(kk) < 6:
            continue
        o = min(4, len(kk) - 1)
        errs = []
        for name, fn in FLAVOURS[1:]:
            pts = control_points(fn, kk, mp.mpf(j) - mp.mpf("1.5"))
            r = richardson_mp(pts, o)
            errs.append(abs(relerr(r, CTRL_C)))
        budget[j] = max(errs)
        print("  %3d %6d %8d %10.1e %10.1e %10.1e %10.1e"
              % (j, len(kk), o, errs[0], errs[1], errs[2], errs[3]))
    print()
    print("  (a2) DATA-MATCHED control error in C, per j (non-terminating tail")
    print("       whose leading coefficients are the data's own):")
    print("  %3s %8s %12s" % ("j", "order", "rel err"))
    matched = {}
    for j in sorted(budget):
        kk = [k for k, _ in defect_raw(j)]
        o = min(4, len(kk) - 1)
        dp = defect_points(j, mp.mpf(j) - mp.mpf("1.5"))
        Ctrue, cpts, _ = matched_control(dp, kk)
        matched[j] = abs(relerr(richardson_mp(cpts, o), Ctrue))
        print("  %3d %8d %12.1e" % (j, o, matched[j]))
    print()
    print("  (b) theta-sensitivity dC/C per unit theta shift, at each j's")
    print("      window (matched control), so a theta band converts to a C bar")
    print("  %3s %14s" % ("j", "|dlnC/dtheta|"))
    dCdth = {}
    for j in sorted(budget):
        kk = [k for k, _ in defect_raw(j)]
        o = min(4, len(kk) - 1)
        th_true = mp.mpf(j) - mp.mpf("1.5")
        dp = defect_points(j, th_true)
        Ctrue, cpts, _ = matched_control(dp, kk)
        vals = {k: v * mp.mpf(9) ** k * mp.mpf(k) ** th_true for k, v in cpts}
        d = mp.mpf("0.01")
        out = []
        for sgn in (-1, 1):
            thu = th_true + sgn * d
            pts = [(k, vals[k] * mp.mpf(9) ** (-k) * mp.mpf(k) ** (-thu))
                   for k in kk]
            out.append(relerr(richardson_mp(pts, o), Ctrue))
        dCdth[j] = abs(out[1] - out[0]) / (2 * float(d))
        print("  %3d %14.2f" % (j, dCdth[j]))
    print()
    print("  (c) measured R_j vs binom(2j-2,j-1)/2^(j-1).")
    print("      bar_spread = spread of R_j over Richardson orders 3,4,5")
    print("      (the estimator's own order-to-order disagreement);")
    print("      bar_theta  = dlnC/dtheta * (half 3x-band from section 5).")
    THETA_HALF = {1: 0.0005, 2: 0.003, 3: 0.005, 4: 0.010,
                  5: 0.020, 6: 0.030, 7: 0.040}
    print("  %3s %13s %11s %11s %10s %10s %10s %s"
          % ("j", "R_j (ord 4)", "binom", "rel dev", "bar_spr",
             "bar_theta", "bar_tot", "verdict"))
    As = {}
    for j in range(1, 8):
        kk = [k for k, _ in defect_raw(j)]
        if len(kk) < 6:
            continue
        pts = defect_points(j, mp.mpf(j) - mp.mpf("1.5"))
        As[j] = (richardson_mp(pts, min(4, len(pts) - 1))
                 * mp.gamma(mp.mpf(j) - mp.mpf("0.5")))

    def R_at_order(j, o):
        Cj = richardson_mp(defect_points(j, mp.mpf(j) - mp.mpf("1.5")), o)
        A1 = richardson_mp(defect_points(1, mp.mpf("-0.5")), o)
        return (Cj * mp.gamma(mp.mpf(j) - mp.mpf("0.5"))
                / (A1 * mp.gamma(mp.mpf("0.5"))) * (mp.mpf(81) / 25) ** (j - 1))

    bars = {}
    for j in sorted(As):
        R = As[j] / As[1] * (mp.mpf(81) / 25) ** (j - 1)
        pred = mp.binomial(2 * j - 2, j - 1) / mp.mpf(2) ** (j - 1)
        rel = float((R - pred) / pred)
        rs = [float(R_at_order(j, o)) for o in (3, 4, 5)]
        bar_spr = (max(rs) - min(rs)) / float(R) if float(R) else 0.0
        bar_th = dCdth[j] * THETA_HALF[j] + dCdth[1] * THETA_HALF[1]
        bar = max(bar_spr, matched[j] + matched[1]) + bar_th
        bars[j] = bar
        verdict = ("supported" if abs(rel) <= bar / 3
                   else "consistent" if abs(rel) <= bar else "OUTSIDE BAR")
        print("  %3d %13.6f %11.6f %+10.2e %10.1e %10.1e %10.1e  %s"
              % (j, float(R), float(pred), rel, bar_spr, bar_th, bar, verdict))
    print()
    print("  (c3) CONDITIONAL bar -- assuming theta_j = j-3/2 exactly (which is")
    print("       what the extraction assumes anyway).  bar = max(order-spread,")
    print("       matched-control truncation).")
    print("  %3s %13s %10s %10s   %s"
          % ("j", "R_j", "rel dev", "cond bar", "verdict"))
    condbar = {}
    from math import gcd as _gcd
    for j in sorted(As):
        R = As[j] / As[1] * (mp.mpf(81) / 25) ** (j - 1)
        pred = mp.binomial(2 * j - 2, j - 1) / mp.mpf(2) ** (j - 1)
        rel = float((R - pred) / pred)
        rs = [float(R_at_order(j, o)) for o in (3, 4, 5)]
        b = max((max(rs) - min(rs)) / float(R), matched[j] + matched[1])
        condbar[j] = b
        # Verdict per the doc's scoping (onset-defect-law.md §2): "supported"
        # means the binomial value is the UNIQUE simple rational (q <= 32)
        # inside the bar, not that the deviation is comfortably small.  The
        # old labels here used |rel| <= bar/3, which called j = 5..7
        # "supported" while the (c4) census shows 8-20 rivals inside the bar
        # — inverted relative to the doc.  Fixed 2026-08-09 (handoff §5).
        Rf, tol = float(R), b * abs(float(R))
        rivals = [(round(Rf * q), q) for q in range(1, 33)
                  if round(Rf * q) and abs(Rf - round(Rf * q) / q) <= tol
                  and _gcd(round(Rf * q), q) == 1]
        if abs(rel) > b:
            verdict = "OUTSIDE BAR"
        elif len(rivals) == 1:
            verdict = "supported (unique rational in bar)"
        else:
            verdict = "consistent (%d rationals in bar)" % len(rivals)
        print("  %3d %13.6f %+10.2e %10.1e   %s"
              % (j, float(R), rel, b, verdict))
    print()
    print("  (c4) simple rationals p/q (q<=32) inside the CONDITIONAL bar:")
    from math import gcd
    for j in sorted(As):
        R = float(As[j] / As[1] * (mp.mpf(81) / 25) ** (j - 1))
        tol = condbar[j] * abs(R)
        hits = [("%d/%d" % (round(R * q), q)) for q in range(1, 33)
                if round(R * q) and abs(R - round(R * q) / q) <= tol
                and gcd(round(R * q), q) == 1]
        print("  j=%d  R=%.6f  tol=%.2e   %s"
              % (j, R, tol, ", ".join(hits) if hits else "none"))
    print()
    print("  (c2) how many simple rationals p/q (q<=32) sit inside R_j's")
    print("       UNCONDITIONAL bar (theta band folded in)?")
    for j in sorted(As):
        R = float(As[j] / As[1] * (mp.mpf(81) / 25) ** (j - 1))
        tol = bars[j] * abs(R)
        hits = []
        for q in range(1, 33):
            p = round(R * q)
            if p and abs(R - p / q) <= tol:
                g = mp.mpf(1)
                from math import gcd
                if gcd(int(p), q) == 1:
                    hits.append("%d/%d" % (p, q))
                del g
        print("  j=%d  R=%.6f  tol=%.2e   %s"
              % (j, R, tol, ", ".join(hits[:8]) if hits else "none"))
    print()
    print("  (d) the competing rational recognitions the shipped script printed")
    print("      (118/27 etc.), scored against the same bar:")
    alt = {5: (118, 27), 6: (118, 15), 7: (130, 9)}
    for j in sorted(alt):
        if j not in As:
            continue
        R = As[j] / As[1] * (mp.mpf(81) / 25) ** (j - 1)
        p, q = alt[j]
        v = mp.mpf(p) / q
        pred = mp.binomial(2 * j - 2, j - 1) / mp.mpf(2) ** (j - 1)
        bar = bars[j]
        print("  j=%d  R=%.6f   %d/%d=%.6f (rel %+.2e)   binom=%.6f "
              "(rel %+.2e)   bar %.1e"
              % (j, float(R), p, q, float(v), float((R - v) / v),
                 float(pred), float((R - pred) / pred), bar))
    print()
    print("  (e) sensitivity of R_j to the Richardson order actually used")
    print("  %3s" % "j" + "".join("  order %d " % o for o in range(2, 6)))
    for j in sorted(As):
        kk = [k for k, _ in defect_raw(j)]
        row = "  %3d" % j
        for o in range(2, 6):
            if len(kk) < o + 1:
                row += "  %8s" % "-"
                continue
            Cj = richardson_mp(defect_points(j, mp.mpf(j) - mp.mpf("1.5")), o)
            A1 = richardson_mp(defect_points(1, mp.mpf("-0.5")), o)
            Rj = (Cj * mp.gamma(mp.mpf(j) - mp.mpf("0.5"))
                  / (A1 * mp.gamma(mp.mpf("0.5")))
                  * (mp.mpf(81) / 25) ** (j - 1))
            row += "  %8.4f" % float(Rj)
        print(row)


def main():
    task1()
    task23()
    task4()
    task5()
    task6()
    return 0


if __name__ == "__main__":
    sys.exit(main())
