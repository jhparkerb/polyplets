#!/usr/bin/env python3
"""SECOND TERM (docs/onset-defect-plans.md (deleted) §1).

D_1(k) = C_1 * 9^k * k^(-1/2) * (1 + a/k + b/k^2 + ...) with
C_1 = sqrt(6)/(27 sqrt(pi)).  Extract `a` and try to recognise it.

Two things fall out for free:

  * Dividing by the CONJECTURED exact C_1 turns the amplitude identification
    into a much sharper test than any Richardson limit.  Put
        B_k = D_1(k) * 9^-k * k^(1/2) / C_1 - 1
    If C_1 is exactly right, B_k -> 0 like a/k, so k*B_k -> a, a constant.
    If C_1 is wrong by a relative eps, k*B_k ~ eps*k, DIVERGING linearly.
    Linear divergence would be visible at k=19 for eps as small as ~1e-7.

  * The same pipeline on j=2 gives a_2, testable against a_1.

All arithmetic: exact Fractions -> mpmath at 60 dps.  Bars come from
NON-terminating controls, per the review; the terminating control that shipped
earlier could never fire.
"""
import os, sys
from mpmath import mp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
mp.dps = 60
from defect_controls import (mpf_frac, richardson_mp, defect_raw, C1_PRED,
                             A1_EXACT, matched_control, sec)

def bseq(j, C_exact, th):
    """[(k, k*B_k)] where B_k = D_j*9^-k*k^-th/C_exact - 1."""
    out = []
    for k, D in defect_raw(j):
        A = mpf_frac(D) * mp.mpf(9) ** (-k) * mp.mpf(k) ** (-th)
        out.append((k, mp.mpf(k) * (A / C_exact - 1)))
    return out

def main():
    sec("1. Is k*B_k bounded?  (a divergence means C_1 is not exactly sqrt6/(27 sqrt pi))")
    pts = bseq(1, C1_PRED, mp.mpf(-1) / 2)
    print("  %3s %22s %18s" % ("k", "k*B_k", "ratio to prev"))
    prev = None
    for k, v in pts:
        r = (v / prev) if prev not in (None, 0) else mp.mpf('nan')
        print("  %3d %22s %18s" % (k, mp.nstr(v, 12), mp.nstr(r, 8)))
        prev = v
    print("  A constant tail => C_1 exact and the constant IS `a`.")
    print("  A tail growing ~linearly => C_1 is wrong; slope would be the rel error.")

    sec("2. Richardson on k*B_k  ->  a")
    for o in range(0, 7):
        r = richardson_mp(pts, o)
        if r is not None:
            print("   order %d: a = %s" % (o, mp.nstr(r, 14)))

    sec("3. Bars from non-terminating controls (known a, same window)")
    print("  Build an exact C_1*9^k*k^-1/2*(1 + a/k + tail) with a KNOWN, run the")
    print("  identical pipeline, and report the recovered a.")
    def synth(a_true, tail, ks):
        out = []
        for k in ks:
            s = mp.mpf(1) + mp.mpf(a_true) / k + tail(k)
            out.append((k, mp.mpf(k) * ((C1_PRED * s) / C1_PRED - 1)))
        return out
    ks = [k for k, _ in pts]
    tails = {
        "geometric  b/k^2 chain": lambda k: sum(mp.mpf("0.6") ** t / mp.mpf(k) ** (t + 1)
                                                for t in range(1, 60)),
        "half-power 0.3/k^1.5":   lambda k: mp.mpf("0.3") / mp.mpf(k) ** mp.mpf("1.5"),
        "log        0.2 log k/k^2": lambda k: mp.mpf("0.2") * mp.log(k) / mp.mpf(k) ** 2,
    }
    for a_true in ("-1.5", "0.75"):
        for nm, tl in tails.items():
            sp = synth(a_true, tl, ks)
            rec = [richardson_mp(sp, o) for o in (3, 4, 5)]
            errs = [abs(float(x - mp.mpf(a_true))) for x in rec if x is not None]
            print("   a_true=%6s  %-24s recovered %s   |err| max %.2e"
                  % (a_true, nm, mp.nstr(rec[-1], 10), max(errs)))

    sec("4. j = 2")
    pts2 = bseq(2, None or (A1_EXACT * mp.mpf(25) / 81 / mp.gamma(mp.mpf(3) / 2)),
                mp.mpf(1) / 2)
    print("  (C_2 taken as A_2/Gamma(3/2) with A_2 = A_1*25/81)")
    print("  %3s %22s" % ("k", "k*B_k"))
    for k, v in pts2[-6:]:
        print("  %3d %22s" % (k, mp.nstr(v, 12)))
    for o in range(2, 6):
        r = richardson_mp(pts2, o)
        if r is not None:
            print("   order %d: a_2 = %s" % (o, mp.nstr(r, 12)))


if __name__ == "__main__":       # was import-time execution; fixed 2026-08-09
    main()                       # (handoff §5: second_term_recognise re-ran it)
