#!/usr/bin/env python3
"""Extract the amplitude C_j in  D_j(k) ~ C_j * 9^k * k^(j-3/2)  and try to
recognise it.  Richardson in 1/k to several orders; the control is the same
pipeline run on an exactly-built sequence with a KNOWN amplitude, so the number
of trustworthy digits is measured rather than assumed."""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
P, tri = read_pk(), read_tri()

def richardson(pts, order):
    """pts = [(k, A_k)]; fit A = C + c1/k + ... + c_order/k^order, return C."""
    n = order + 1
    use = pts[-n:]
    if len(use) < n: return None
    M = [[1.0] + [1.0/p[0]**i for i in range(1, n)] + [p[1]] for p in use]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        M[c] = [x/M[c][c] for x in M[c]]
        for r in range(n):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][i] - f*M[c][i] for i in range(n+1)]
    return M[0][n]

CC = 0.0512345
CONTROLS = [
    # NOT a terminating series: a terminating one is interpolated exactly by
    # any Richardson of order >= its length, which measures float noise rather
    # than truncation.  See experiments/defect_controls.py for the full budget.
    ("(a) smooth 1/k   (1+0.7/k)/(1-0.3/k)",
     lambda k: (1 + 0.7/k) / (1 - 0.3/k)),
    ("(a') geometric tail 1/(1-0.8/k)",
     lambda k: 1.0 / (1 - 0.8/k)),
    ("(b) half-power   1+0.5/k^1.5",
     lambda k: 1 + 0.5/k**1.5),
    ("(c) log          1+0.4 log k/k",
     lambda k: 1 + 0.4*math.log(k)/k),
]
print("== control suite, C=%.7f, k=2..19 (same window as the j=1 data)" % CC)
print("   %-38s %s" % ("flavour", "".join("  order %d " % o for o in range(2,6))))
for name, f in CONTROLS:
    pts = [(k, CC*f(k)) for k in range(2, 20)]
    row = "   %-38s" % name
    for o in range(2, 6):
        r = richardson(pts, o)
        row += "  %8.1e" % abs((r-CC)/CC) if r else "  %8s" % "-"
    print(row)
print("   -> a smooth 1/k series is recovered to ~1e-8 at order 4; a half-power")
print("      or log contaminant of amplitude ~0.5 stalls at 1e-4 / 1e-3.")

for j in (1,2,3):
    th = j - 1.5
    pts = []
    for k in range(2,20):
        n = 2*k+1-j; H = n-k
        if H < 1 or (n,H) not in tri or k not in P: continue
        D = F(tri[(n,H)]) - law(n,k,P)
        if D <= 0: continue
        pts.append((k, float(D)*9.0**-k*k**-th))
    print()
    print("== j=%d  A_k = D * 9^-k * k^-(%.1f),  %d points" % (j, th, len(pts)))
    print("   raw tail:", " ".join("%.7f" % v for _,v in pts[-4:]))
    for o in range(0,5):
        r = richardson(pts,o)
        if r: print("   order %d: %.9f" % (o, r))

C1 = richardson([(k, float(F(tri[(2*k,k)])-law(2*k,k,P))*9.0**-k*math.sqrt(k))
                 for k in range(2,20) if (2*k,k) in tri and k in P], 3)
print()
print("== recognition attempts on C_1 = %.9f" % C1)
cands = {
 "1/(9 sqrt(pi))": 1/(9*math.sqrt(math.pi)),
 "1/(2 pi)^?": None,
 "5/(27 sqrt(pi))": 5/(27*math.sqrt(math.pi)),
 "sqrt(3)/(2 pi) /9": math.sqrt(3)/(2*math.pi)/9,
 "1/(6 pi)": 1/(6*math.pi),
 "2/(27 sqrt(3 pi))": 2/(27*math.sqrt(3*math.pi)),
 "1/(4 sqrt(3 pi))/2": 1/(8*math.sqrt(3*math.pi)),
 "25/(486)": 25/486.0,
 "1/(3^2 * 2)/sqrt(pi)": 1/(18*math.sqrt(math.pi)),
}
for nm, v in cands.items():
    if v is None: continue
    print("   %-24s %.9f   ratio %.6f" % (nm, v, C1/v))
print("   C1*sqrt(pi)   = %.9f" % (C1*math.sqrt(math.pi)))
print("   1/C1          = %.6f" % (1/C1))
print("   C1*27         = %.9f    C1*81 = %.9f" % (C1*27, C1*81))
print("   C1*sqrt(pi)*27= %.9f" % (C1*math.sqrt(math.pi)*27))
