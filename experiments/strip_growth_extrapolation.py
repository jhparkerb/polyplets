#!/usr/bin/env python3
"""Independent lambda estimate from strip growth constants mu_H.

For fixed H, T(n,H) ~ C * mu_H^n, so mu_H = lim T(n,H)/T(n-1,H) is the dominant
eigenvalue of the height-H transfer matrix (top root of atom q_H). mu_H increases
to lambda as H -> infinity. This is a route to lambda from the strip spectra,
orthogonal to the a(n)-ratio fit (which uses the row sums). Data:
results/ns_a36/perheight/h{H}.out.
"""
import os

PER = "results/ns_a36/perheight"
HMAX = 18
T = {}
maxn = {}
for H in range(1, HMAX + 1):
    with open(os.path.join(PER, f"h{H}.out")) as f:
        for line in f:
            n, v = line.split()
            n, v = int(n), int(v)
            if v:
                T[(n, H)] = v
                maxn[H] = max(maxn.get(H, 0), n)

def ratio(n, H):
    a, b = T.get((n, H)), T.get((n - 1, H))
    return a / b if a and b else None

print(" H  maxn   mu_H (raw ratio)   mu_H (1/n-accelerated)")
mu = {}
for H in range(2, HMAX + 1):
    N = maxn[H]
    r1 = ratio(N, H)
    r2 = ratio(N - 1, H)
    if r1 and r2:
        # r_n ~ mu + b/n  ->  mu ~ r_n + n*(r_n - r_{n-1})*(n-1)/... ; simple Richardson:
        acc = r1 + (r1 - r2) * (N - 1)  # cancels leading 1/n term
        mu[H] = acc
        print(f"{H:2d}  {N:3d}   {r1:.5f}          {acc:.5f}")

# Extrapolate mu_H -> lambda as H -> inf. Try Neville/Richardson on the sequence
# assuming mu_H ~ lambda - c/H^p for p in {1,2}.
print("\nExtrapolating mu_H -> lambda (accelerated mu):")
xs = sorted(mu)
seq = [mu[H] for H in xs]
for p in (1, 2):
    # one Richardson step across consecutive H using 1/H^p
    best = None
    for i in range(len(xs) - 1):
        h1, h2 = xs[i], xs[i + 1]
        f1, f2 = seq[i], seq[i + 1]
        # lambda ~ (f2*h2^p - f1*h1^p)/(h2^p - h1^p)
        lam = (f2 * h2**p - f1 * h1**p) / (h2**p - h1**p)
        best = lam
    print(f"  assuming 1/H^{p}: last pair -> lambda ~ {best:.4f}")

print("\n a(n)-ratio fit gives lambda ~ 7.111 (paper). Compare above.")
print(" NOTE: high-H mu are under-converged (need n >> H); treat as indicative.")
