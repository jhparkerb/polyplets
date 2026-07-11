#!/usr/bin/env python3
"""Intrinsic 3-adic content of the diagonal polynomials P_k, in the Newton
(finite-difference / binomial) basis -- which introduces no factorial
denominators, unlike the monomial basis. P_k(n) = T(n,n-k)/3^n. The Newton
coefficients are Delta^j P_k(n0); their common denominator is a pure power of 3
= the intrinsic 3-adic valuation, free of interpolation artifacts."""
from fractions import Fraction as F
from math import lcm, comb
import os

PER = "results/ns_a36/perheight"
T = {}
for H in range(1, 19):
    for line in open(os.path.join(PER, f"h{H}.out")):
        n, v = line.split(); T[(int(n), H)] = int(v)
def t(n, H): return T.get((n, H), 0)

def v3(x):
    e = 0
    while x % 3 == 0: x //= 3; e += 1
    return e

print(" k | Newton-basis (Delta^j P_k) common denom | v3 | pure 3-power?")
val = {}
for k in range(0, 9):
    # P_k(n) = T(n,n-k)/3^n on the polynomial regime n >= 2k+1 (bulk; boundary terms below)
    n0 = k + 2
    need = 2 * k + 1
    ns = [n0 + i for i in range(need)]
    if any(t(n, n - k) == 0 for n in ns):    # off the end of the H<=18 data
        print(f"{k:2d} | (insufficient consecutive data)"); continue
    p = [F(t(n, n - k), 1) / F(3) ** n for n in ns]
    # forward differences Delta^j p[0]
    deltas = []
    for j in range(need):
        dj = sum((-1) ** (j - i) * comb(j, i) * p[i] for i in range(j + 1))
        deltas.append(dj)
    dens = [d.denominator for d in deltas if d != 0]
    D = lcm(*dens) if dens else 1
    pure = (3 ** v3(D) == D)
    val[k] = v3(D)
    print(f"{k:2d} | {D:<22} | {v3(D):2d} | {pure}")

ks = sorted(val)
seq = [val[k] for k in ks]
print("\n v3 sequence:", seq)
print(" first differences:", [seq[i+1]-seq[i] for i in range(len(seq)-1)])
