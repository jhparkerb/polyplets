#!/usr/bin/env python3
"""The below-onset defect of the diagonal law is ONE square-root singularity.

Depth-j amplitudes measured in experiments/defect_amplitude_family.py:
   A_j = (sqrt6/27) * (25/81)^(j-1) * binom(2j-2,j-1)/2^(j-1)
and sum_j A_j t^(j-1) = (sqrt6/27)/sqrt(1 - 50t/81).  Combined with the
per-depth singularity A_j (1-9z)^-(2j-1)/2 this resums to

   Dhat(z,t) ~ (sqrt6/27) * ( 1 - 9z - (50/81) t )^(-1/2)

i.e. the defect at depth j, surplus k, is asymptotically

   D_j(k) ~ (sqrt6/27) * binom(2N,N)/4^N * binom(N,k) * 9^k * (50/81)^(j-1),
   N = k + j - 1.

That formula was pinned from j<=7 near the onset line.  Below it is tested
POINTWISE against every banked below-onset cell, including deep ones
(x = H/k down to 0.1) that had no part in fitting it.
"""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
P, tri = read_pk(), read_tri()

SQ6_27 = math.sqrt(6)/27.0
ALPHA  = 50.0/81.0

def lbinom(a,b):
    return math.lgamma(a+1)-math.lgamma(b+1)-math.lgamma(a-b+1)

def pred(k, j):
    N = k + j - 1
    lg = (math.log(SQ6_27) + lbinom(2*N,N) - 2*N*math.log(2.0)
          + lbinom(N,k) + k*math.log(9.0) + (j-1)*math.log(ALPHA))
    return lg

print("== pointwise test: ln(D_measured) - ln(D_predicted)")
print("   (fit used only j<=7 near x=1; deep-x cells are pure prediction)")
print("  %3s %3s %6s %10s %14s %10s" % ("k","j","H","x=H/k","ln D","resid"))
rows=[]
for k in range(4,20):
    for j in range(1, k+1):
        n = 2*k+1-j; H = n-k
        if H < 2 or (n,H) not in tri or k not in P: continue
        D = F(tri[(n,H)]) - law(n,k,P)
        if D <= 0: continue
        lD = math.log(float(D)) if float(D) not in (0.0, float('inf')) else None
        if lD is None:
            # big ints: use exact log
            num = D.numerator; den = D.denominator
            lD = math.log(num.bit_length()) # placeholder, replaced below
        lD = (math.log(D.numerator) if D.numerator < 10**300
              else D.numerator.bit_length()*math.log(2)
                   + math.log(D.numerator >> (D.numerator.bit_length()-60))
                   - 60*math.log(2)) - math.log(D.denominator)
        rows.append((k,j,H,H/float(k), lD, lD - pred(k,j)))

for r in rows:
    if r[0] in (8,13,19) and (r[1] <= 3 or r[1] % 4 == 0):
        print("  %3d %3d %6d %10.3f %14.4f %10.4f" % r)

print()
print("== residual by x band (resid should -> 0 if the form is right;")
print("   a WRONG exponential rate would make it grow linearly in k)")
bands = [(0.10,0.25),(0.25,0.40),(0.40,0.55),(0.55,0.70),(0.70,0.85),(0.85,1.01)]
print("  %14s %6s %10s %10s %10s" % ("x band","n","resid@k_min","resid@k_max","slope/k"))
for lo,hi in bands:
    sel = sorted([r for r in rows if lo <= r[3] < hi])
    if len(sel) < 3: continue
    first, last = sel[0], sel[-1]
    slope = (last[5]-first[5])/(last[0]-first[0]) if last[0]!=first[0] else 0
    print("  %6.2f-%4.2f %6d %10.4f %10.4f %10.5f"
          % (lo,hi,len(sel),first[5],last[5],slope))

print()
print("== g(x) predicted from the singularity vs the measured table")
print("   d(x) = ln9 + (1-x)ln(50/81) + nu*Hent(1/nu),  nu = 2-x")
def dofx(x):
    nu = 2.0-x; p = 1.0/nu
    Hent = -p*math.log(p)-(1-p)*math.log(1-p)
    return math.log(9.0) + (1-x)*math.log(ALPHA) + nu*Hent
# measured t(x) = (1/k) ln T along the ray, from the banked triangle
print("  %6s %10s %10s %10s %10s" % ("x","d(x)","t(x)meas","g pred","g meas"))
GMEAS = {0.35:-0.2232, 0.50:-0.3326, 0.65:-0.5416, 0.80:-0.8587, 0.95:-1.3084}
for x,gm in sorted(GMEAS.items()):
    # ray: H = round(x k); use largest k with data
    best=None
    for k in range(6,41):
        H = int(round(x*k)); n = H+k
        if H>=2 and (n,H) in tri: best=(k,H,n)
    if not best: continue
    k,H,n = best
    lT = math.log(tri[(n,H)]) if tri[(n,H)] < 10**300 else None
    if lT is None:
        v = tri[(n,H)]; b = v.bit_length()
        lT = b*math.log(2) + math.log(v >> (b-60)) - 60*math.log(2)
    t = lT/k
    print("  %6.2f %10.4f %10.4f %10.4f %10.4f  (k=%d)"
          % (x, dofx(x), t, dofx(x)-t, gm, k))
