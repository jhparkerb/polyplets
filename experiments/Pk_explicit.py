#!/usr/bin/env python3
"""Explicit diagonal polynomials P_k and the anti-diagonal sequences.
T(n,n-k) = P_k(n)*3^n, P_k degree 2k. Prints:
  (a) the anti-diagonal integer sequence T(n,n-k) for OEIS lookup,
  (b) P_k(n) in monomial form (fractions),
  (c) the Newton-basis integer numerators  Delta^j P_k(n0) * 3^{3k+1}."""
from fractions import Fraction as F
from math import comb, lcm
import os

PER = "results/ns_a36/perheight"
T = {}
for H in range(1, 19):
    for line in open(os.path.join(PER, f"h{H}.out")):
        n, v = line.split(); T[(int(n), H)] = int(v)
def t(n, H): return T.get((n, H), 0)

def solve(V, y):
    n = len(y); M = [row[:] + [y[i]] for i, row in enumerate(V)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]; M[c] = [x / M[c][c] for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                M[r] = [a - M[r][c] * b for a, b in zip(M[r], M[c])]
    return [M[r][n] for r in range(n)]

for k in range(1, 6):
    pts = [(n, t(n, n - k)) for n in range(k + 1, 19 + k) if t(n, n - k)]
    seq = [v for (_, v) in pts]
    print(f"\n===== k={k}  (diagonal T(n,n-{k}), n={pts[0][0]}..{pts[-1][0]}) =====")
    print("  seq:", ", ".join(map(str, seq[:12])), "...")
    # fit P_k on largest 2k+1 points (past n=k+1 transient)
    d = 2 * k
    fit = [(F(n), F(v) / F(3) ** n) for (n, v) in pts if n >= k + 2][-(d + 1):]
    coef = solve([[x ** j for j in range(d + 1)] for (x, _) in fit], [y for (_, y) in fit])
    D = lcm(*[c.denominator for c in coef if c])
    def v3(x):
        e = 0
        while x % 3 == 0: x //= 3; e += 1
        return e
    print(f"  P_{k}(n) * {D} = " +
          " + ".join(f"{int(c*D)}*n^{j}" for j, c in enumerate(coef) if c) )
    print(f"  (common denom {D} = 3^{v3(D)}{'' if 3**v3(D)==D else ' * non-3'}, expect 3^{3*k+1})")
    # Newton integer numerators
    n0 = k + 2
    p = [F(t(n0 + i, n0 + i - k)) / F(3) ** (n0 + i) for i in range(d + 1)]
    deltas = [sum((-1)**(j-i)*comb(j, i)*p[i] for i in range(j+1)) for j in range(d + 1)]
    scale = F(3) ** (3 * k + 1)
    nums = [dj * scale for dj in deltas]
    print("  Newton nums (Delta^j P_k * 3^{3k+1}):", [int(x) if x.denominator == 1 else str(x) for x in nums])
