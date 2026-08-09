#!/usr/bin/env python3
"""The below-onset defect as a square-root singularity family.

D_j(k) ~ C_j 9^k k^(j-3/2) is the coefficient asymptotics of a generating
function singular at z=1/9 like  A_j (1-9z)^-(2j-1)/2 , since
   [z^k](1-9z)^-a ~ 9^k k^(a-1)/Gamma(a).
So A_j = C_j * Gamma(j-1/2).  This script extracts C_j, converts to A_j, and
looks for the pattern in A_j / A_1.
"""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
from defect_amplitude import richardson
P, tri = read_pk(), read_tri()

A1_EXACT = math.sqrt(6)/27.0

print("== C_1 vs sqrt(6)/(27 sqrt(pi))")
pts = [(k, float(F(tri[(2*k,k)])-law(2*k,k,P))*9.0**-k*math.sqrt(k))
       for k in range(2,20) if (2*k,k) in tri and k in P]
pred = A1_EXACT/math.sqrt(math.pi)
for o in (2,3,4,5):
    r = richardson(pts,o)
    print("   order %d: %.10f   pred %.10f   rel %+.2e" % (o,r,pred,(r-pred)/pred))

print()
print("  %3s %14s %16s %14s %16s"
      % ("j","C_j","A_j=C_j G(j-1/2)","A_j/A_1","*(81/25)^(j-1)"))
As = {}
for j in range(1,8):
    th = j-1.5
    pts=[]
    for k in range(2,20):
        n=2*k+1-j; H=n-k
        if H<1 or (n,H) not in tri or k not in P: continue
        D=F(tri[(n,H)])-law(n,k,P)
        if D<=0: continue
        pts.append((k,float(D)*9.0**-k*k**-th))
    if len(pts)<6: continue
    C = richardson(pts, min(4, len(pts)-1))
    A = C*math.gamma(j-0.5)
    As[j]=A
    print("  %3d %14.8f %16.8f %14.6f %16.6f"
          % (j, C, A, A/As[1], A/As[1]*(81.0/25.0)**(j-1)))

print()
print("== rational recognition of R_j = A_j/A_1 * (81/25)^(j-1)")
print("   The tolerance is NOT a hand-picked 2e-4: it is the estimator's own")
print("   order-to-order spread in R_j across Richardson orders 3,4,5, which")
print("   is what experiments/defect_controls.py shows the data supports.")
print("   ALL rationals with q <= 32 inside that tolerance are listed, so the")
print("   output shows whether the binomial value is uniquely selected.")


def R_at(j, o):
    def C_at(jj):
        th = jj-1.5
        pts=[]
        for k in range(2,20):
            n=2*k+1-jj; H=n-k
            if H<1 or (n,H) not in tri or k not in P: continue
            D=F(tri[(n,H)])-law(n,k,P)
            if D<=0: continue
            pts.append((k,float(D)*9.0**-k*k**-th))
        return richardson(pts, o) if len(pts) > o else None
    cj, c1 = C_at(j), C_at(1)
    if cj is None or c1 is None: return None
    return (cj*math.gamma(j-0.5))/(c1*math.gamma(0.5))*(81.0/25.0)**(j-1)


from math import gcd
for j in sorted(As):
    v = As[j]/As[1]*(81.0/25.0)**(j-1)
    rs = [R_at(j, o) for o in (3, 4, 5)]
    rs = [x for x in rs if x is not None]
    tol = (max(rs)-min(rs)) if len(rs) > 1 else 0.0
    hits = ["%d/%d" % (round(v*q), q) for q in range(1, 33)
            if round(v*q) and abs(v-round(v*q)/q) <= tol
            and gcd(round(v*q), q) == 1]
    binom = math.comb(2*j-2, j-1)/2.0**(j-1)
    print("   j=%d  R_j = %.6f  tol %.2e   binom %.6f (dev %+.1e, %s)"
          % (j, v, tol, binom, v-binom,
             "inside" if abs(v-binom) <= tol else "OUTSIDE"))
    print("        rationals q<=32 inside tol: %s"
          % (", ".join(hits) if hits else "none"))
