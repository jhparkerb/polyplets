#!/usr/bin/env python3
"""SPECTRAL EDGE (docs/onset-defect-plans.md §3), with its premise corrected.

FRAMING CORRECTION FOUND WHILE RUNNING THIS. `results/onset-defect-law.md` §4
reads the defect rate as "9 = the square of the thin-diagonal growth 3". But on
the depth-j line n = 2k+1-j, so 9^k = 3^(n+j-1): measured PER CELL the defect
rate is exactly 3, the thin-diagonal rate itself, not its square. The two
readings are the same measured fact in different variables and the data cannot
separate them, because n and 2k differ by a constant on every line we can reach.
The per-cell statement is the simpler one and is the one to test here: the strip
transfer operator's spectrum should show something at 3, not at 9.

This also removes an impossibility: 9 exceeds every mu_H (which climb to
lambda = 7.11), so no eigenvalue could ever sit there. 3 is inside the range.

Method: the fixed-height GF G_H(x) = P_H(x)/Q_H(x) has poles at 1/eigenvalue, so
the reciprocal roots of Q_H ARE the strip spectrum. Read them for H = 1..8 and
ask whether anything accumulates at 3.

Controls: the dominant reciprocal root must reproduce mu_2 = 1+sqrt(2) and
mu_3 = 3.4437 (results/boundary-push-recurrence.md), which validates the whole
extraction independently.
"""
import os, sys, math
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_gfs(hmax=8):
    out = {}
    H = None; Q = None
    for line in open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")):
        if line.startswith("H="):
            H = int(line.split()[0][2:])
        elif line.startswith("Q:") and H is not None and H <= hmax:
            out[H] = [int(t) for t in line[2:].strip().strip("[]").split(",")]
            H = None
    return out

Q = read_gfs()
print("== control: dominant reciprocal root vs known mu_H")
print("  %3s %7s %16s %16s" % ("H", "order", "mu_H (roots)", "known"))
known = {2: 1 + math.sqrt(2), 3: 3.4437}
spec = {}
for H in sorted(Q):
    c = np.array(Q[H], dtype=float)
    r = np.roots(c[::-1])                 # numpy wants high->low
    ev = 1.0 / r[np.abs(r) > 1e-12]
    ev = ev[np.isfinite(ev)]
    spec[H] = ev
    mu = np.max(np.abs(ev))
    print("  %3d %7d %16.6f %16s"
          % (H, len(Q[H]) - 1, mu,
             ("%.6f" % known[H]) if H in known else ""))

print()
print("== is there anything at 3?  (density of |eigenvalue| by band)")
bands = [(0,1),(1,2),(2,2.5),(2.5,2.9),(2.9,3.1),(3.1,3.5),(3.5,4.5),(4.5,9)]
print("  %3s %6s" % ("H","n") + "".join("%12s" % ("%.1f-%.1f"%b) for b in bands))
for H in sorted(spec):
    a = np.abs(spec[H])
    row = "".join("%12d" % int(((a>=lo)&(a<hi)).sum()) for lo,hi in bands)
    print("  %3d %6d" % (H, len(a)) + row)

print()
print("== fraction of the spectrum within 2% of 3, vs a null band of equal width")
for H in sorted(spec):
    a = np.abs(spec[H])
    near3 = ((a>=2.94)&(a<=3.06)).sum()
    near4 = ((a>=3.92)&(a<=4.08)).sum()
    near2 = ((a>=1.96)&(a<=2.04)).sum()
    print("  H=%d  n=%5d   |ev|~3: %4d    |ev|~2: %4d    |ev|~4: %4d"
          % (H, len(a), near3, near2, near4))

print()
print("== exact check: does Q_H(1/3) = 0 for any H?  (3 an exact eigenvalue)")
from fractions import Fraction as Fr
for H in sorted(Q):
    v = sum(Fr(c) * Fr(1,3)**i for i, c in enumerate(Q[H]))
    print("  H=%d  Q_H(1/3) = %s" % (H, "0  <-- YES" if v == 0 else "nonzero"))
