#!/usr/bin/env python3
"""BOUNDARY LAYER (docs/onset-defect-plans.md (deleted) §2).

The near-onset resummation  D ~ (sqrt6/27)*binom(2N,N)/4^N*binom(N,k)*9^k*(50/81)^(j-1),
N = k+j-1, holds near the onset line and degrades with depth.  Degradation is
smooth, so there should be a scaling variable: find p with

    residual  =  ln D_measured - ln D_predicted   =   f( j / k^p )

p = 1/2 Gaussian crossover, 2/3 Airy-type coalescing saddle, 1 = no boundary
layer at all.  Scored by how tightly the residual collapses onto a single curve.

Control: a synthetic surface with a KNOWN crossover exponent, same (k,j) extent,
must be recovered.  Without it the scan returns its favourite p regardless.
"""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
P, tri = read_pk(), read_tri()
SQ6_27, ALPHA = math.sqrt(6)/27.0, 50.0/81.0

def lbinom(a, b):
    return math.lgamma(a+1)-math.lgamma(b+1)-math.lgamma(a-b+1)

def lpred(k, j):
    N = k+j-1
    return (math.log(SQ6_27) + lbinom(2*N,N) - 2*N*math.log(2.0)
            + lbinom(N,k) + k*math.log(9.0) + (j-1)*math.log(ALPHA))

def surface():
    """[(k, j, residual)] over every banked below-onset cell."""
    out = []
    for k in range(4, 20):
        for j in range(1, k+1):
            n = 2*k+1-j; H = n-k
            if H < 2 or (n,H) not in tri or k not in P: continue
            D = F(tri[(n,H)]) - law(n,k,P)
            if D <= 0: continue
            num = D.numerator; b = num.bit_length()
            lD = (math.log(num) if num < 10**300 else
                  b*math.log(2) + math.log(num >> (b-60)) - 60*math.log(2))
            lD -= math.log(D.denominator)
            out.append((k, j, lD - lpred(k, j)))
    return out

def collapse_score(rows, p, nbin=12):
    """Spread of residual within bins of u = j/k^p, normalised by total spread.
    0 = perfect collapse onto one curve, 1 = no collapse."""
    pts = [(j/float(k)**p, r) for k, j, r in rows]
    lo = min(u for u,_ in pts); hi = max(u for u,_ in pts)
    if hi <= lo: return 1.0
    tot = max(r for _,r in pts) - min(r for _,r in pts)
    if tot == 0: return 1.0
    num = den = 0.0
    for b in range(nbin):
        a0 = lo + (hi-lo)*b/nbin; a1 = lo + (hi-lo)*(b+1)/nbin
        vs = [r for u,r in pts if (a0 <= u < a1 or (b==nbin-1 and u==a1))]
        if len(vs) < 3: continue
        m = sum(vs)/len(vs)
        num += sum((v-m)**2 for v in vs); den += len(vs)
    return math.sqrt(num/den)/tot if den else 1.0

def scan(rows, label):
    best = min(((collapse_score(rows,p), p) for p in
                [x/200.0 for x in range(20, 401)]), key=lambda t: t[0])
    print("  %-34s best p = %.3f   score %.4f" % (label, best[1], best[0]))
    for p in (0.5, 2.0/3, 1.0, 1.5, 2.0):
        print("       p=%-5.3f score %.4f" % (p, collapse_score(rows,p)))
    return best

print("== CONTROLS: synthetic surfaces with a known crossover exponent")
rows = surface()
ext = [(k,j) for k,j,_ in rows]
for p_true in (0.5, 2.0/3, 1.0):
    syn = [(k, j, -1.7*(j/float(k)**p_true)**2 - 0.4*(j/float(k)**p_true))
           for k,j in ext]
    scan(syn, "known p = %.3f" % p_true)
print()
print("== MEASURED residual surface, %d cells" % len(rows))
scan(rows, "polyplets below-onset defect")
print()
print("== the residual as a function of the best variable")
b = min(((collapse_score(rows,p), p) for p in [x/200.0 for x in range(20,401)]),
        key=lambda t: t[0])[1]
pts = sorted((j/float(k)**b, r, k, j) for k,j,r in rows)
print("   u = j/k^%.3f" % b)
print("   %8s %10s %6s %4s" % ("u","residual","k","j"))
for i in range(0, len(pts), max(1,len(pts)//18)):
    u,r,k,j = pts[i]
    print("   %8.4f %10.4f %6d %4d" % (u,r,k,j))

# ---------------------------------------------------------------------------
# Family B: large-deviation form.  Section 3's band table showed the residual's
# slope per unit k depends on x = H/k, which means residual ~ k * phi(x), i.e.
# a scaling in j/k with a k PREFACTOR -- a different family from f(j/k^p).
def collapse_score_B(rows, q, nbin=12):
    pts = [(j/float(k), r/float(k)**q) for k, j, r in rows]
    lo = min(u for u,_ in pts); hi = max(u for u,_ in pts)
    tot = max(r for _,r in pts) - min(r for _,r in pts)
    if hi <= lo or tot == 0: return 1.0
    num = den = 0.0
    for b in range(nbin):
        a0 = lo+(hi-lo)*b/nbin; a1 = lo+(hi-lo)*(b+1)/nbin
        vs = [r for u,r in pts if (a0 <= u < a1 or (b==nbin-1 and u==a1))]
        if len(vs) < 3: continue
        m = sum(vs)/len(vs); num += sum((v-m)**2 for v in vs); den += len(vs)
    return math.sqrt(num/den)/tot if den else 1.0

if __name__ == "__main__":
    print()
    print("== FAMILY CALIBRATION: what does the family-A scan return for known p?")
    for pt in (0.35, 0.40, 0.45, 0.50, 0.60):
        syn = [(k, j, -1.7*(j/float(k)**pt)**2 - 0.4*(j/float(k)**pt))
               for k, j in ext]
        b = min(((collapse_score(syn,p), p) for p in
                 [x/200.0 for x in range(20,401)]), key=lambda t: t[0])
        print("   p_true %.3f  ->  scan returns %.3f  (score %.4f)"
              % (pt, b[1], b[0]))

    print()
    print("== FAMILY B: residual = k^q * phi(j/k)")
    print("   controls (surfaces built exactly in this family):")
    for qt in (0.5, 1.0):
        syn = [(k, j, float(k)**qt * (-1.9*(j/float(k))**2 - 0.3*(j/float(k))))
               for k, j in ext]
        bq = min(((collapse_score_B(syn,q), q) for q in
                  [x/200.0 for x in range(0,401)]), key=lambda t: t[0])
        print("      q_true %.2f -> scan returns %.3f (score %.4f)" % (qt, bq[1], bq[0]))
    bq = min(((collapse_score_B(rows,q), q) for q in
              [x/200.0 for x in range(0,401)]), key=lambda t: t[0])
    print("   MEASURED: best q = %.3f   score %.4f" % (bq[1], bq[0]))
    for q in (0.0, 0.5, 1.0, 1.5):
        print("      q=%-4.2f score %.4f" % (q, collapse_score_B(rows,q)))
    print()
    print("   Family A best score %.4f  vs  Family B best score %.4f"
          % (min(collapse_score(rows,p) for p in [x/200.0 for x in range(20,401)]),
             bq[0]))
