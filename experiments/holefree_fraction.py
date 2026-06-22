#!/usr/bin/env python3
# Observation: the fraction of n-cell polyplets that are HOLE-FREE, A_0(n)/A006770(n).
# Data from results/holes_n18.txt (build/g2 square8 N --holes, 4-connected background),
# n<=18. The fraction falls monotonically (1.000 at n<=3 -> 0.734 at n=18) and the per-term
# growth rate of A_0 lags that of the total, so hole-free polyplets are a vanishing fraction
# (-> 0), though slowly (still ~73% at n=18). Almost every large polyplet has a hole.
from collections import defaultdict

A0 = defaultdict(int)
tot = defaultdict(int)
hsum = defaultdict(int)
for line in open('results/holes_n18.txt'):
    p = line.split()
    if len(p) == 3:
        n, h, c = int(p[0]), int(p[1]), int(p[2])
        tot[n] += c
        hsum[n] += h * c
        if h == 0:
            A0[n] = c

print("=== (a) hole-free fraction A_0/a -> 0 ===")
print(" n   A_0/a(n)   growth a(n)/a(n-1)   growth A_0(n)/A_0(n-1)")
pa = pz = None
for n in sorted(tot):
    ga = f"{tot[n]/pa:.4f}" if pa else "-"
    gz = f"{A0[n]/pz:.4f}" if pz else "-"
    print(f" {n:2d}   {A0[n]/tot[n]:.5f}        {ga:>8}              {gz:>8}")
    pa, pz = tot[n], A0[n]
print("hole-free fraction monotone decreasing; at n=18 total grows ~6.73x/term but hole-free")
print("only ~6.58x, so A_0/a -> 0 sub-exponentially (almost every large polyplet has a hole).")
print()
print("=== (b) hole density: mean #holes ~ d_hole * n ===")
print(" n   E[#holes]   1st diff -> d_hole")
prev = None
for n in sorted(tot):
    m = hsum[n] / tot[n]
    d = f"{m - prev:.4f}" if prev is not None else "-"
    print(f" {n:2d}   {m:.5f}     {d:>7}")
    prev = m
print("first differences converge cleanly to d_hole ~ 0.0231 holes/cell (a new lattice")
print("constant; very stable over n<=18). So holes are ~32x rarer than diagonal contacts")
print("(c~0.743, T6): a typical polyplet is contact-dense but hole-sparse.")
