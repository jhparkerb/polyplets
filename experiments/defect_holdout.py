#!/usr/bin/env python3
"""Holdout: does the onset-defect law add real digits to cells it never saw?

Constants fitted on k <= 14 ONLY (or taken as the recognized exact value), then
used to predict T(2k, k) for k = 15..19 -- banked cells excluded from the fit.
Reported as digits of T correct, law alone vs law + defect estimate.
"""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT,"experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
from defect_amplitude import richardson
P, tri = read_pk(), read_tri()

pts = [(k, float(F(tri[(2*k,k)])-law(2*k,k,P))*9.0**-k*math.sqrt(k))
       for k in range(2,15) if (2*k,k) in tri and k in P]
C_fit = richardson(pts, 4)
C_rec = math.sqrt(6)/(27*math.sqrt(math.pi))
print("C_1 fitted on k<=14 : %.10f" % C_fit)
print("C_1 recognized      : %.10f   (rel diff %+.2e)"
      % (C_rec, (C_fit-C_rec)/C_rec))
print()
print("  %3s %12s %12s %14s" % ("k","law alone","law+defect","gain (digits)"))
for k in range(15, 20):
    if (2*k,k) not in tri or k not in P: continue
    T = tri[(2*k,k)]
    Lv = law(2*k,k,P)
    d0 = -math.log10(abs(float(F(T)-Lv)/T))
    Dp = F(C_rec).limit_denominator(10**15) * F(9)**k / F(math.sqrt(k)).limit_denominator(10**15)
    err = abs(float(F(T)-Lv-Dp)/T)
    d1 = -math.log10(err) if err > 0 else float('inf')
    print("  %3d %12.1f %12.1f %14.1f" % (k, d0, d1, d1-d0))
