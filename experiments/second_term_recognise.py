#!/usr/bin/env python3
"""SECOND TERM, part 2: how many digits of `a` do we actually have, and is it
recognisable?

The pipeline's error on `a` is ABSOLUTE (set by the correction tail), not
relative, so with a ~ 0.005 the controls must be run at a comparable magnitude
or the digit count is fiction.  Then a recognition sweep, honestly scoped.
"""
import os, sys, math
from itertools import product
from mpmath import mp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
mp.dps = 60
from defect_controls import richardson_mp, C1_PRED, A1_EXACT, sec
from second_term import bseq

pts = bseq(1, C1_PRED, mp.mpf(-1) / 2)
ks = [k for k, _ in pts]
est = {o: richardson_mp(pts, o) for o in (3, 4, 5, 6)}
a_hat = est[4]

sec("1. Bar on `a`, from controls at the RIGHT magnitude")
def synth(a_true, tail):
    return [(k, mp.mpf(k) * (mp.mpf(a_true) / k + tail(k))) for k in ks]
tails = {
 "geometric":  lambda k: sum(mp.mpf("0.6")**t / mp.mpf(k)**(t+1) for t in range(1,60)),
 "half-power": lambda k: mp.mpf("0.3") / mp.mpf(k)**mp.mpf("1.5"),
 "log":        lambda k: mp.mpf("0.2")*mp.log(k) / mp.mpf(k)**2,
 "small tail": lambda k: mp.mpf("0.01") / mp.mpf(k)**2,
}
print("  %-12s %14s %14s %14s" % ("tail", "a_true", "recovered(o4)", "abs err"))
worst = 0.0
for nm, tl in tails.items():
    for at in ("0.005", "-0.005"):
        sp = synth(at, tl)
        r = richardson_mp(sp, 4)
        e = abs(float(r - mp.mpf(at)))
        worst = max(worst, e)
        print("  %-12s %14s %14s %14.2e" % (nm, at, mp.nstr(r, 8), e))
spread = max(abs(float(est[o] - est[4])) for o in (3, 5, 6))
print("  order-to-order spread (o3,5,6 vs o4): %.2e" % spread)
BAR = max(worst, spread)
print()
print("  a = %s  +/- %.1e   =>  %.1f significant digits"
      % (mp.nstr(a_hat, 10), BAR, -math.log10(BAR / abs(float(a_hat)))))

sec("2. Recognition sweep, scoped to the bar")
a = float(a_hat)
hits = []
for q in range(1, 4001):
    p = round(a * q)
    if p and abs(a - p / q) < BAR:
        hits.append(("%d/%d" % (p, q), p / q))
print("  rationals p/q, q <= 4000, inside the bar: %d" % len(hits))
for h in hits[:12]:
    print("     %-14s %.10f" % h)
consts = {"1": 1.0, "sqrt6": math.sqrt(6), "pi": math.pi, "1/pi": 1/math.pi,
          "sqrt6/27": math.sqrt(6)/27, "ln3": math.log(3), "sqrt2": math.sqrt(2),
          "sqrt3": math.sqrt(3), "1/sqrt(pi)": 1/math.sqrt(math.pi)}
print()
print("  a / c for simple constants c, looking for a simple rational:")
for nm, c in consts.items():
    v = a / c
    best = None
    for q in range(1, 400):
        p = round(v * q)
        if p and abs(v - p / q) < BAR / c:
            best = "%d/%d" % (p, q); break
    print("     a/%-11s = %-14.9f %s" % (nm, v, best or ""))

sec("3. What the smallness of `a` means")
print("  |a| = %.6f, so the 1/k correction to D_1 is only %.3f%% at k=19."
      % (abs(a), 100*abs(a)/19))
print("  The leading term C_1*9^k*k^-1/2 is therefore accurate to ~3e-4 relative")
print("  by k=19 on its own -- unusually clean, and the reason `a` is hard to")
print("  measure: there is very little of it to see.")
