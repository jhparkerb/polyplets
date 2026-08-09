#!/usr/bin/env python3
"""Can lambda be read off the grand form?

experiments/grand_form_saddle.py gives, for the ray n = sH (kappa = s-1),
   ln mu_s = (1-2 kappa) ln3 + (1+kappa) B(y*) - kappa ln y*,   y* B'(y*) = kappa/(1+kappa).
A ray contributes exp(n * ln(mu_s)/s) animals, so lambda = sup_s mu_s^(1/s).
As s -> infinity the saddle condition tends to y_c B'(y_c) = 1 and

   ln lambda = B(y_c) - ln y_c - 2 ln 3.

Tested against lambda = 7.110(1) (results/series-analysis-da.md).  The honest
question is whether the 19-term truncation of B reaches y_c at all -- printed.
"""
import math, os, re, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT,"experiments"))
from grand_form_saddle import read_pk, ymul, padd, pmul, pscale, ptrim

KMAX = 19
P = read_pk()
S = [[F(0)] for _ in range(KMAX+1)]; S[0] = [F(1)]
for k in range(1, KMAX+1): S[k] = list(P[k])
U = [list(c) for c in S]; U[0] = [F(0)]
L = [[F(0)] for _ in range(KMAX+1)]
Up = [[F(0)] for _ in range(KMAX+1)]; Up[0] = [F(1)]
for m in range(1, KMAX+1):
    Up = ymul(Up, U)
    sg = F(1,m) if m % 2 else F(-1,m)
    for j in range(KMAX+1): L[j] = padd(L[j], pscale(Up[j], sg))
b = [0.0]*(KMAX+1)
for j in range(1, KMAX+1):
    c = ptrim(L[j]); b[j] = float(c[1]) if len(c) > 1 else 0.0

def B(y, J=KMAX):  return sum(b[j]*y**j for j in range(1, J+1))
def dB(y, J=KMAX): return sum(j*b[j]*y**(j-1) for j in range(1, J+1))

def solve_yc(target, J=KMAX, hi=0.20):
    lo = 1e-9
    f = lambda y: y*dB(y, J)
    # find first crossing by scanning, the series is not monotone far out
    xs = [lo + (hi-lo)*i/20000 for i in range(20001)]
    prev = f(xs[0]); 
    for x in xs[1:]:
        cur = f(x)
        if (prev-target)*(cur-target) < 0:
            a, c = x - (hi-lo)/20000, x
            for _ in range(200):
                m = 0.5*(a+c)
                if (f(a)-target)*(f(m)-target) <= 0: c = m
                else: a = m
            return 0.5*(a+c)
        prev = cur
    return None

print("== y B'(y) as y grows (target 1 for the s->inf limit; 0.5 was s=2)")
for y in [0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.10,0.12]:
    print("   y=%.3f   yB'=%12.5f   B=%10.5f   b_19 y^19 = %9.2e"
          % (y, y*dB(y), B(y), b[19]*y**19))

print()
print("== mu_s^(1/s) along the ray family (lambda = 7.110(1))")
print("  %6s %10s %12s %16s %12s" % ("s","y*","tail term","mu_s","mu_s^(1/s)"))
for s in [2,3,4,5,6,8,10,15,20,40]:
    kap = float(s-1); tgt = kap/(1+kap)
    ys = solve_yc(tgt)
    if ys is None:
        print("  %6d  no saddle within truncation" % s); continue
    lm = (1-2*kap)*math.log(3) + (1+kap)*B(ys) - kap*math.log(ys)
    print("  %6d %10.6f %12.2e %16.4f %12.6f"
          % (s, ys, abs(b[19]*ys**19), math.exp(lm), math.exp(lm/s)))

print()
print("== the s->infinity form:  ln lambda = B(y_c) - ln y_c - 2 ln 3,  y_c B'(y_c)=1")
print("  %4s %12s %14s %10s" % ("J","y_c","tail term","lambda"))
for J in range(10, KMAX+1):
    yc = solve_yc(1.0, J)
    if yc is None:
        print("  %4d   no solution within scan" % J); continue
    lam = math.exp(B(yc, J) - math.log(yc) - 2*math.log(3))
    print("  %4d %12.7f %14.2e %10.5f" % (J, yc, abs(b[J]*yc**J), lam))
