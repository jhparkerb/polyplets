#!/usr/bin/env python3
"""Pin P_8 for real, using a(24)'s T(24,16) -- the point scripts/pin_diagonal_k8.py
identified as the one missing piece (see results/k8-pinning.md).

T(n, n-k) = P_k(n) * 3^(n-1-3k), P_k degree k, leading coeff [n^k]P_k = 25^k/k!
(confirmed exactly for k=0..7; this script pins k=8 using n=17..24, 8 points,
with the leading coefficient fixed by the same conjecture -- an 8-point exact
fit for the 8 remaining unknowns, no shortcut needed now that a(24) exists).

Usage: python3 scripts/pin_diagonal_k8_final.py <triangle.txt>
triangle.txt: lines "n H v" (T(n,H)=v). Built by concatenating
runs/ns_a24/perheight/h<H>.out (n V pairs) across all H.
"""
from fractions import Fraction as F
from math import factorial
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "results/ns_a24/triangle.txt"
TRI = {}
with open(path) as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        n, h, v = line.split()
        TRI[(int(n), int(h))] = int(v)


def pk_values(k):
    out = {}
    for n in range(2 * k + 1, 25):
        cell = TRI.get((n, n - k))
        if cell is None:
            continue
        e = 3 * k + 1 - n
        val = F(cell) * (F(3) ** e) if e >= 0 else F(cell) / (F(3) ** (-e))
        assert val.denominator == 1, f"P_{k}({n}) not integer: {val}"
        out[n] = int(val)
    return out


def gauss(A, b):
    n = len(A)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pivval = M[col][col]
        M[col] = [x / pivval for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][j] - f * M[col][j] for j in range(n + 1)]
    return [M[i][n] for i in range(n)]


def fit_fixed_lead(points, deg, fixed_lead):
    pts = sorted(points.items())[:deg]
    xs = [F(x) for x, _ in pts]
    ys = [F(y) for _, y in pts]
    A = [[x ** j for j in range(deg)] for x in xs]
    b = [ys[i] - fixed_lead * (xs[i] ** deg) for i in range(deg)]
    lo = gauss(A, b)
    return lo + [fixed_lead]


def poly_eval(coeffs, x):
    return sum(c * (F(x) ** i) for i, c in enumerate(coeffs))


k = 8
p8 = pk_values(k)
print(f"P_8 data points: n={sorted(p8)} ({len(p8)} points)")
assert len(p8) == 8, f"expected exactly 8 points (n=17..24), got {len(p8)}"

lead8 = F(25 ** k, factorial(k))
coeffs = fit_fixed_lead(p8, k, lead8)
consistent = all(poly_eval(coeffs, n) == v for n, v in p8.items())
print(f"leading coeff (conjectured 25^8/8!) = {lead8}")
print(f"P_8 coefficients c0..c8: {coeffs}")
print(f"all 8 points reproduced by the fit: {consistent}")
assert consistent, "P_8 fit does not reproduce its own defining points -- bug"

# Falsifiable prediction check: results/k8-pinning.md predicted T(24,16) via the
# sum-of-roots shortcut BEFORE a(24) ran. Confirm it against the real value.
predicted_T2416 = 42594477635772598
actual_T2416 = TRI[(24, 16)]
print(f"pre-a(24) falsifiable prediction T(24,16) = {predicted_T2416}")
print(f"actual (measured, this run)    T(24,16) = {actual_T2416}")
print(f"prediction confirmed exactly: {predicted_T2416 == actual_T2416}")

print()
print(f"P_8 * {k}! numerator coefficients (c0..c8, must be integers -- the")
print(f"quantity diagonalCell's big.Int Horner path actually builds):")
kfact = factorial(k)
num_coeffs = []
for i, c in enumerate(coeffs):
    nc = c * kfact
    assert nc.denominator == 1, f"c{i}*{k}! is not an integer: {nc}"
    num_coeffs.append(int(nc))
    print(f"  c{i}*{k}! = {int(nc)}")

print()
print("Horner check: does numerator/8! * 3^(n-25) reproduce the antidiagonal")
print("points for n=17..24 (n<25 needs division direction, not diagonalCell's")
print("own multiply-only code path, but confirms the coefficients are right)?")
for n in sorted(p8):
    num = 0
    for c in reversed(num_coeffs):  # ascending c0..c8 -> Horner needs descending
        pass
    # Horner in descending order (c8 first)
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * n + c
    e = n - 25
    if e >= 0:
        t = F(val, kfact) * (F(3) ** e)
    else:
        t = F(val, kfact) / (F(3) ** (-e))
    assert t.denominator == 1
    ok = int(t) == TRI[(n, n - 8)]
    print(f"  n={n}: computed T={int(t)} vs actual T={TRI[(n, n-8)]}  match={ok}")
    assert ok
