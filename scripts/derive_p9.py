#!/usr/bin/env python3
"""Derive as much of P_9(n) as possible from the KNOWN a_1..a_6, b_1..b_6
series (docs/proofs/T-n-nm2-and-general.md Section 2), keeping a_7,a_8,a_9
and b_7,b_8,b_9 as symbolic unknowns. Coefficients of P_9(n) that come out
free of all six unknown symbols are fully determined by existing, already-
validated data -- no new engine sweep required. Coefficients that retain
any unknown symbol are NOT determined and still need real data or further
cluster-weight theory.

Method validated in scripts/derive_p9_calibrate.py (exact match against
diagonalCell's hardcoded P_3..P_6 for the k<=6 case).
"""
from fractions import Fraction as F
import sympy as sp

y, n = sp.symbols("y n")
a7, a8, a9 = sp.symbols("a7 a8 a9")
b7, b8, b9 = sp.symbols("b7 b8 b9")

a_known = {
    1: F(-45), 2: F(-891, 2), 3: F(-10350),
    4: F(-846963, 4), 5: F(-3781134), 6: F(-119091015),
}
b_known = {
    1: F(25), 2: F(-209, 2), 3: F(4474, 3),
    4: F(-22701, 4), 5: F(16144), 6: F(15126941, 3),
}

def rat(f):
    return sp.Rational(f.numerator, f.denominator)

logA = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9
Bser = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7*y**7 + b8*y**8 + b9*y**9

K = 9
A = sp.series(sp.exp(logA), y, 0, K + 1).removeO()
S = sp.series(A * sp.exp(n * Bser), y, 0, K + 1).removeO()
S = sp.expand(S)

P9 = sp.expand(S.coeff(y, K))
P9_poly = sp.Poly(P9, n)

unknowns = {a7, a8, a9, b7, b8, b9}

print("P_9(n) coefficients by degree in n, and whether each is free of")
print("the unknown symbols a7,a8,a9,b7,b8,b9:")
print("=" * 70)
coeffs_clean = {}
for p in range(9, -1, -1):
    c = P9_poly.coeff_monomial(n**p) if p > 0 else P9_poly.coeff_monomial(1)
    c = sp.expand(c)
    free_syms = c.free_symbols & unknowns
    clean = len(free_syms) == 0
    if clean:
        coeffs_clean[p] = sp.nsimplify(c)
    tag = "CLEAN" if clean else f"depends on {sorted(s.name for s in free_syms)}"
    print(f"  degree n^{p}: {tag}")
    if clean:
        print(f"    value = {coeffs_clean[p]}  =  {float(coeffs_clean[p]):.6f}")

print()
print("=" * 70)
print(f"Clean (fully determined) degrees: {sorted(coeffs_clean, reverse=True)}")
print(f"Unresolved degrees: {sorted(set(range(10)) - set(coeffs_clean), reverse=True)}")

# ---------------------------------------------------------------------------
# Stage 2: solve the 4 remaining unknown coefficients (n^3, n^2, n^1, n^0)
# from real T(n,n-9) data (n=19..25, results/ns_a25/swept_rows.txt), then
# check the fit against the held-out points.
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Stage 2: solve remaining coefficients from real data, validate held-out")
print("=" * 70)

T_data = {
    19: 24014057424024,
    20: 132107598093637,
    21: 694918765309300,
    22: 3521085234178586,
    23: 17278818571437182,
    24: 82463515269090962,
    25: 384025992867882686,
}

def P9_from_T(nval, Tval):
    e = 28 - nval  # T(n,n-9) = P_9(n) * 3^(n-28)
    return sp.Rational(Tval) * sp.Integer(3) ** e

P9_data = {nv: P9_from_T(nv, Tv) for nv, Tv in T_data.items()}
print("\nP_9(n) values recovered from real T(n,n-9) (exact rationals):")
for nv in sorted(P9_data):
    print(f"  n={nv}: P_9({nv}) = {P9_data[nv]}")

# Known clean part (degrees 9..4)
known_part = sum(coeffs_clean[p] * n**p for p in range(4, 10))

c3, c2, c1, c0 = sp.symbols("c3 c2 c1 c0")
unknown_part = c3*n**3 + c2*n**2 + c1*n + c0

fit_nodes = [19, 20, 21, 22]
holdout_nodes = [23, 24, 25]

eqs = []
for nv in fit_nodes:
    residual = P9_data[nv] - known_part.subs(n, nv)
    eqs.append(sp.Eq(unknown_part.subs(n, nv), residual))

sol = sp.solve(eqs, [c3, c2, c1, c0], dict=True)
assert len(sol) == 1, f"expected unique solution, got {sol}"
sol = sol[0]
print("\nSolved unknown coefficients (from n=19..22):")
for sym in (c3, c2, c1, c0):
    print(f"  {sym} = {sol[sym]}")

P9_full = sp.expand(known_part + unknown_part.subs(sol))
print(f"\nFull P_9(n) = {P9_full}")

print("\nHeld-out validation (n=23,24,25 -- NOT used in the fit):")
all_holdout_ok = True
for nv in holdout_nodes:
    predicted = P9_full.subs(n, nv)
    actual = P9_data[nv]
    ok = sp.simplify(predicted - actual) == 0
    all_holdout_ok &= ok
    print(f"  n={nv}: predicted P_9 = {predicted}, actual = {actual}, match = {ok}")

print()
print(f"ALL HELD-OUT POINTS MATCH: {all_holdout_ok}")

# ---------------------------------------------------------------------------
# Stage 3: integer-numerator (Horner) form, full self-check across all 7
# real points (not just the 3 held out), mirroring diagonalCell case 7/8.
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Stage 3: integer numerator form + full self-check (all 7 points)")
print("=" * 70)

kfact = sp.factorial(9)
P9_poly_full = sp.Poly(P9_full, n)
num_coeffs = []  # ascending c0..c9
for p in range(10):
    c = P9_poly_full.coeff_monomial(n**p) if p > 0 else P9_poly_full.coeff_monomial(1)
    nc = sp.nsimplify(c) * kfact
    assert nc.is_integer, f"c{p}*9! not integer: {nc}"
    num_coeffs.append(int(nc))

print(f"\nP_9 * 9! numerator coefficients c0..c9:")
for i, c in enumerate(num_coeffs):
    print(f"  c{i}*9! = {c}")

print("\nHorner check: numerator/9! * 3^(n-28) reproduces T(n,n-9) for n=19..25")
print("(all 7 real points, including the 4 used in the fit):")
all_self_ok = True
for nv in sorted(T_data):
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * nv + c
    e = nv - 28
    if e >= 0:
        t = sp.Rational(val, kfact) * (sp.Integer(3) ** e)
    else:
        t = sp.Rational(val, kfact) / (sp.Integer(3) ** (-e))
    assert t.is_integer, f"non-integer at n={nv}: {t}"
    ok = int(t) == T_data[nv]
    all_self_ok &= ok
    print(f"  n={nv}: computed T={int(t)} vs actual T={T_data[nv]}  match={ok}")

print()
print(f"ALL 7 SELF-CHECK POINTS MATCH: {all_self_ok}")

print()
print("Falsifiable predictions for future validation (not yet checked against")
print("a real sweep -- if either is later computed for real, it must match):")
for nv, H in ((26, 17), (27, 18)):
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * nv + c
    e = nv - 28
    t = sp.Rational(val, kfact) / (sp.Integer(3) ** (-e)) if e < 0 else sp.Rational(val, kfact) * sp.Integer(3) ** e
    assert t.is_integer
    print(f"  predicted T({nv},{H}) = {int(t)}")
