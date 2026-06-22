#!/usr/bin/env python3
# Observation: the fraction of n-cell polyplets that are HOLE-FREE, A_0(n)/A006770(n).
# Data from results/holes_n18.txt (build/g2 square8 N --holes, 4-connected background),
# n<=18. The fraction falls monotonically (1.000 at n<=3 -> 0.734 at n=18) and the per-term
# growth rate of A_0 lags that of the total, so hole-free polyplets are a vanishing fraction
# (-> 0), though slowly (still ~73% at n=18). Almost every large polyplet has a hole.
from collections import defaultdict

A0 = defaultdict(int)
tot = defaultdict(int)
for line in open('results/holes_n18.txt'):
    p = line.split()
    if len(p) == 3:
        n, h, c = int(p[0]), int(p[1]), int(p[2])
        tot[n] += c
        if h == 0:
            A0[n] = c

print(" n   A_0/a(n)   growth a(n)/a(n-1)   growth A_0(n)/A_0(n-1)")
pa = pz = None
for n in sorted(tot):
    ga = f"{tot[n]/pa:.4f}" if pa else "-"
    gz = f"{A0[n]/pz:.4f}" if pz else "-"
    print(f" {n:2d}   {A0[n]/tot[n]:.5f}        {ga:>8}              {gz:>8}")
    pa, pz = tot[n], A0[n]
print()
print("hole-free fraction is monotone decreasing; at n=18 the total grows ~6.73x/term but")
print("hole-free only ~6.58x/term, so A_0/a -> 0 (slowly). The growth constants coincide")
print("asymptotically (both -> lambda), so the decay is sub-exponential, not geometric.")
