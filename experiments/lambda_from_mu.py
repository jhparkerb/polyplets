#!/usr/bin/env python3
"""Extrapolate the strip growth constants mu_H -> lambda, using the exact ladder
now extended to H=13 (strip_mu power iteration). Sliding 3-point power-law fit
mu_H = lambda - c*H^(-p): each triple (H-1,H,H+1) pins one lambda estimate; watch
them converge."""
import math

mu = {2:2.4142136, 3:3.4437184, 4:4.1823214, 5:4.7178013, 6:5.1153245,
      7:5.4178476, 8:5.6533728, 9:5.8404579, 10:5.9916958, 11:6.1158416,
      12:6.2191246, 13:6.3060713}

def solve_lambda(H):
    f1, f2, f3 = mu[H-1], mu[H], mu[H+1]
    # mu_H = lam - c/H^p  =>  (lam-f1)/(lam-f2) = (H/(H-1))^p , etc.
    def g(lam):
        return (math.log((lam-f1)/(lam-f2)) * math.log((H+1)/H)
                - math.log((lam-f2)/(lam-f3)) * math.log(H/(H-1)))
    lo, hi = f3 + 1e-6, 12.0
    if g(lo) * g(hi) > 0: return None
    for _ in range(200):
        m = 0.5*(lo+hi)
        if g(lo)*g(m) <= 0: hi = m
        else: lo = m
    lam = 0.5*(lo+hi)
    # recover p at this lambda
    p = math.log((lam-f1)/(lam-f2)) / math.log(H/(H-1))
    return lam, p

print(" center H | lambda est | p (power)")
for H in range(3, 13):
    r = solve_lambda(H)
    if r: print(f"    {H:2d}    |  {r[0]:.4f}   | {r[1]:.3f}")

# also: increments and their ratios (diagnostic of decay type)
print("\n increments Delta_H = mu_H - mu_{H-1}, and ratios:")
ds = {H: mu[H]-mu[H-1] for H in range(3,14)}
for H in range(4,14):
    print(f"  H={H:2d}: Delta={ds[H]:.5f}  ratio={ds[H]/ds[H-1]:.4f}")
