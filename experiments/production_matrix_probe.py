#!/usr/bin/env python3
"""Production-matrix probe for the polyplet height triangle T(n,H).

Directly computes P = L^{-1} L-bar (the Stieltjes/production matrix) from the
banked triangle and inspects it for the structure the Riordan/production-matrix
framework would need: banded? Toeplitz (columns = shifts, i.e. Riordan)?
polynomial-in-position entries? Or dense/structureless (matching the atom-ledger
prediction that no fixed production rule exists).

T(n,H) read from results/ns_a36/perheight/h{H}.out  (lines: "n  T(n,H)").
"""
from fractions import Fraction as F
import os

PER = "results/ns_a36/perheight"
N = 18  # we have columns H=1..18

# T[n][H] for n,H in 1..N (+ one extra row n=N+1 for L-bar)
T = {}
for H in range(1, N + 1):
    with open(os.path.join(PER, f"h{H}.out")) as f:
        for line in f:
            n, v = line.split()
            T[(int(n), H)] = int(v)

def t(n, H):
    return T.get((n, H), 0)

# L (N x N), lower-triangular, L[i,j] = T(i+1, j+1)
L = [[F(t(i + 1, j + 1)) for j in range(N)] for i in range(N)]
# L-bar: shift rows up, Lb[i,j] = T(i+2, j+1)  (row n+1)
Lb = [[F(t(i + 2, j + 1)) for j in range(N)] for i in range(N)]

# Solve L P = Lb  ->  P = L^{-1} Lb, column by column (L lower-triangular).
def solve_lower(L, b):
    n = len(b)
    x = [F(0)] * n
    for i in range(n):
        s = b[i] - sum(L[i][k] * x[k] for k in range(i))
        x[i] = s / L[i][i]
    return x

P = [[F(0)] * N for _ in range(N)]
for col in range(N):
    b = [Lb[i][col] for i in range(N)]
    x = solve_lower(L, b)
    for i in range(N):
        P[i][col] = x[i]

# ---- Inspect ----
def nz(x): return x != 0

print("=== P = L^{-1} L-bar, entries (blank=0), rows m=1..%d, cols H=1..%d ===" % (N, N))
for i in range(N):
    row = "  ".join((str(P[i][j]) if nz(P[i][j]) else ".") for j in range(N))
    print(f"m={i+1:2d} | {row}")

print("\n=== band structure: nonzero column range per row m ===")
for i in range(N):
    cols = [j + 1 for j in range(N) if nz(P[i][j])]
    if cols:
        print(f"m={i+1:2d}: H in [{min(cols)},{max(cols)}]  (count {len(cols)})")

print("\n=== Riordan signature: is P Toeplitz, P[m,H]==P[m-1,H-1]? ===")
bad = 0
for i in range(1, N):
    for j in range(1, N):
        if P[i][j] != P[i - 1][j - 1]:
            bad += 1
print("Toeplitz violations:", bad, "of", (N - 1) * (N - 1), "-> Riordan iff 0")

print("\n=== are the entries integers? (unit-diagonal Riordan would give ints) ===")
nonint = sum(1 for i in range(N) for j in range(N) if P[i][j].denominator != 1)
print("non-integer entries:", nonint, "of", N * N,
      "(expected nonzero: diagonal T(n,n)=3^{n-1} makes L^{-1} carry 3-power denominators)")
