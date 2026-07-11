#!/usr/bin/env python3
"""Do the diagonal polynomials P_k (T(n,n-k) = P_k(n)*3^n, deg 2k) have
coefficient denominators following 3^{3k+2} like the production-matrix band
constants? Fit P_k exactly from banked T(n,H) and report the 3-adic structure."""
from fractions import Fraction as F
from math import lcm
import os

PER = "results/ns_a36/perheight"
T = {}
for H in range(1, 19):
    for line in open(os.path.join(PER, f"h{H}.out")):
        n, v = line.split(); T[(int(n), H)] = int(v)
def t(n, H): return T.get((n, H), 0)

def solve(V, y):  # exact Gaussian elimination, V square over Fraction
    n = len(y); M = [row[:] + [y[i]] for i, row in enumerate(V)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        M[c] = [x / M[c][c] for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                M[r] = [a - M[r][c] * b for a, b in zip(M[r], M[c])]
    return [M[r][n] for r in range(n)]

def v3(x):
    e = 0
    while x % 3 == 0: x //= 3; e += 1
    return e

print("k | deg | #pts | fits all? | common denom of P_k coeffs | v3 | 3^{3k+2}?")
for k in range(0, 8):
    pts = [(H + k, t(H + k, H)) for H in range(1, 19) if t(H + k, H)]
    # P_k(n) = T(n,n-k)/3^n
    data = [(F(n), F(v) / F(3) ** n) for (n, v) in pts]
    d = 2 * k
    if len(data) < d + 1:
        print(f"{k:2d}| too few points"); continue
    fit = data[-(d + 1):]                       # largest n (past transient)
    V = [[x ** j for j in range(d + 1)] for (x, _) in fit]
    coef = solve(V, [y for (_, y) in fit])
    # verify against ALL points; report first n where it breaks (transient)
    def Pk(n): return sum(coef[j] * n ** j for j in range(d + 1))
    breaks = [int(n) for (n, y) in data if Pk(n) != y]
    dens = [c.denominator for c in coef if c != 0]
    D = lcm(*dens) if dens else 1
    is3 = (3 ** v3(D) == D)
    print(f"{k:2d}| {d:2d}  | {len(data):3d}  | {'yes' if not breaks else 'no@'+str(min(breaks))}"
          f"       | {D}{' (=3^%d)'%v3(D) if is3 else ' (NOT pure 3-power)'} | {v3(D)} | 3k+2={3*k+2}")
