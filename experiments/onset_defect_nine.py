#!/usr/bin/env python3
"""Does the onset-line defect T(2H,H) - law grow like exactly 9^H?

The slope-2 line n=2H is the onset line (k=H, depth 1 below the proved region
n>=2k+1).  experiments/slope2_law_vs_truth.py measures the RELATIVE defect
decaying with rate exp(-1.5515 H) against a slice growing as mu_2^H with
mu_2 = 42.3946 -- so the ABSOLUTE defect grows as (mu_2 * e^-1.5515)^H = 8.99^H.
Nine is suspicious: everything in this law is a power of 3.

Tested exactly (Fractions), plus the same question one and two steps deeper.
"""
import math, os, re, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law

P, tri = read_pk(), read_tri()

for j in (1, 2, 3, 4):
    # depth j below onset: n = 2k+1-j, H = n-k = k+1-j
    print("== depth j=%d below onset  (n = 2k+1-j, H = k+1-j)" % j)
    print("  %3s %3s %10s %14s %14s %12s" % ("k","H","digits","D_k/D_{k-1}",
                                             "/9","D/(9^k)"))
    prev = None
    for k in range(2, 20):
        n = 2*k+1-j; H = n-k
        if H < 1 or (n,H) not in tri or k not in P: continue
        T = tri[(n,H)]; D = F(T) - law(n,k,P)
        if D == 0: continue
        r = float(D/prev) if prev else float('nan')
        print("  %3d %3d %10.1f %14.6f %14.6f %12.4e"
              % (k,H,-math.log10(abs(float(D)/T)), r, r/9.0,
                 float(D)/9.0**k))
        prev = D
    print()
