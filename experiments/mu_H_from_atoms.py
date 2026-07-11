#!/usr/bin/env python3
"""Exact strip growth constants mu_H = 1/(smallest positive root of Q_H),
from the banked fixed-height GF denominators (results/fixed_height_gfs.txt),
then extrapolate mu_H -> lambda. No count-ratio convergence issue: mu_H is an
exact algebraic number (dominant singularity of the height-H GF)."""
import ast, re
from mpmath import mp, mpf
mp.dps = 50

Q = {}
with open("results/fixed_height_gfs.txt") as f:
    H = None
    for line in f:
        m = re.match(r"H=(\d+)", line)
        if m: H = int(m.group(1))
        if line.startswith("Q:") and H is not None:
            Q[H] = ast.literal_eval(line[2:].strip())

def polyval(q, x):
    s = mpf(0)
    for c in reversed(q):          # Horner, q low->high
        s = s * x + c
    return s

def mu_of(q):
    # smallest positive real root of Q (radius of convergence); Q(0)=1>0.
    # scan for first sign change, then bisect.
    step = mpf("0.0002"); x = step; prev = polyval(q, mpf(0))
    while x < mpf("0.6"):
        cur = polyval(q, x)
        if cur == 0: return 1 / x
        if (prev > 0) != (cur > 0):
            lo, hi = x - step, x
            for _ in range(200):
                mid = (lo + hi) / 2
                if (polyval(q, lo) > 0) == (polyval(q, mid) > 0): lo = mid
                else: hi = mid
            return 1 / ((lo + hi) / 2)
        prev = cur; x += step
    raise ValueError("no root found in (0,0.6)")

mu = {H: mu_of(Q[H]) for H in sorted(Q) if H >= 2}
print(" H   mu_H (exact strip growth constant)")
for H in sorted(mu):
    print(f"{H:2d}   {mu[H]:.6f}")

xs = sorted(mu); seq = [mu[H] for H in xs]

# Repeated Richardson assuming mu_H = lambda - c/H^p (+ higher), for p=1,2.
def richardson(xs, seq, p):
    cur = list(seq); H = list(xs)
    while len(cur) > 1:
        nxt = []
        for i in range(len(cur) - 1):
            h1, h2 = H[i], H[i + 1]
            nxt.append((cur[i + 1] * h2**p - cur[i] * h1**p) / (h2**p - h1**p))
        cur = nxt; H = H[1:]
    return cur[0]

print("\nExtrapolations mu_H -> lambda:")
for p in (1, 2):
    print(f"  full Richardson, 1/H^{p}:  lambda ~ {richardson(xs, seq, p):.4f}")

# Neville/Aitken on last few points, and a simple 1/H^2 two-point on top pairs
for i in range(len(xs) - 3, len(xs) - 1):
    h1, h2 = xs[i], xs[i + 1]; f1, f2 = seq[i], seq[i + 1]
    lam2 = (f2 * h2**2 - f1 * h1**2) / (h2**2 - h1**2)
    print(f"  two-point 1/H^2 on H={h1},{h2}:  lambda ~ {lam2:.4f}")

print("\n a(n)-ratio fit (paper): lambda ~ 7.111")
