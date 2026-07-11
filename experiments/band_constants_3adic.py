#!/usr/bin/env python3
"""Extract the settled band constants c_k of the production matrix P (offset -k
from the main diagonal) and test Other-Claude's conjecture that their NATURAL
(unreduced) denominator is 3^{3k+2} -- i.e. c_k * 3^{3k+2} is an integer."""
from fractions import Fraction as F
import os

PER, N = "results/ns_a36/perheight", 18
T = {}
for H in range(1, N + 1):
    for line in open(os.path.join(PER, f"h{H}.out")):
        n, v = line.split(); T[(int(n), H)] = int(v)
def t(n, H): return T.get((n, H), 0)

L  = [[F(t(i + 1, j + 1)) for j in range(N)] for i in range(N)]
Lb = [[F(t(i + 2, j + 1)) for j in range(N)] for i in range(N)]
def sol_low(Lm, b):
    x = [F(0)] * len(b)
    for i in range(len(b)):
        x[i] = (b[i] - sum(Lm[i][k] * x[k] for k in range(i))) / Lm[i][i]
    return x
P = [[F(0)] * N for _ in range(N)]
for c in range(N):
    x = sol_low(L, [Lb[i][c] for i in range(N)])
    for i in range(N): P[i][c] = x[i]

def v3(n):  # 3-adic valuation of a positive int
    e = 0
    while n % 3 == 0: n //= 3; e += 1
    return e

print("offset k | settled c_k (last rows) | constant? | c_k*3^(3k+2) integer? | reduced den = 3^?")
for k in range(0, 8):                       # offset -k: entry P[m][m-k], main diagonal H=m
    vals = []
    for m in range(N):
        j = m - k
        if 0 <= j < N and P[m][j] != 0: vals.append((m, P[m][j]))
    tail = [v for (m, v) in vals if m >= 2 * k + 3]   # after it settles
    if len(tail) < 2:
        print(f"  -{k:2d}   | (too few settled rows)"); continue
    const = all(v == tail[-1] for v in tail)
    ck = tail[-1]
    natural = ck * F(3) ** (3 * k + 2)
    ok = natural.denominator == 1
    rden_v3 = v3(ck.denominator) if ck.denominator > 1 else 0
    print(f"  -{k:2d}   | {str(ck):<22} | {str(const):5} | {str(ok):5} (=> {natural if ok else natural})"
          f" | 3^{rden_v3}  (natural 3^{3*k+2})")
