#!/usr/bin/env python3
"""Derive as much of P_10(n) as possible, continuing the P_9 methodology
(scripts/derive_p9.py, scripts/derive_p9_calibrate.py).

Stage 0: recover b7 EXACTLY from the P_9 fit. P_9's n^3 coefficient was
shown (derive_p9.py) to depend on b7 alone among the unknown symbols
a7,a8,a9,b7,b8,b9 -- so equating the symbolic n^3-coefficient formula to the
numeric value already solved from real data (c3) gives b7 in closed form,
no new data needed.

Stage 1: with b7 now numeric, expand S(y)=A(y)*exp(n*B(y)) to y^10 with
a7,a8,a9,a10,b8,b9,b10 symbolic (7 unknowns, down from 9 naively). Partition
P_10's coefficients into clean (data-free) vs unclean (depend on unknowns).

Stage 2: pull real T(n,n-10) diagonal data out of results/ns_a25/swept_rows.txt
(block H=h contributes the n=h+10 diagonal-10 point).

Stage 3: fit the unclean coefficients from real data, validate on held-out
points, and (if the linear system separates) try to also recover a7, b8
individually the way b7 was recovered from P_9, for reuse in a future P_11
attempt.

Stage 4: integer-Horner self-check across ALL real diagonal-10 points.
"""
from fractions import Fraction as F
import re
import sympy as sp

y, n = sp.symbols("y n")
a7, a8, a9, a10 = sp.symbols("a7 a8 a9 a10")
b7, b8, b9, b10 = sp.symbols("b7 b8 b9 b10")

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

# ---------------------------------------------------------------------------
# Stage 0: recover b7 exactly from the P_9 fit.
# ---------------------------------------------------------------------------
print("=" * 70)
print("Stage 0: recover b7 exactly from the already-solved P_9 fit")
print("=" * 70)

logA9 = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9
Bser9 = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7*y**7 + b8*y**8 + b9*y**9

A9 = sp.series(sp.exp(logA9), y, 0, 10).removeO()
S9 = sp.expand(sp.series(A9 * sp.exp(n * Bser9), y, 0, 10).removeO())
P9 = sp.expand(S9.coeff(y, 9))
P9_poly = sp.Poly(P9, n)

c3_coeff_expr = sp.expand(P9_poly.coeff_monomial(n**3))
free = c3_coeff_expr.free_symbols & {a7, a8, a9, b7, b8, b9}
print(f"P_9's n^3 coefficient, symbolically: {c3_coeff_expr}")
print(f"free unknown symbols in it: {sorted(s.name for s in free)}")
assert free == {b7}, f"expected only b7, got {free}"

c3_numeric = sp.Rational(-1119607849058443, 9072)  # from derive_p9.py Stage 2
b7_sol = sp.solve(sp.Eq(c3_coeff_expr, c3_numeric), b7)
assert len(b7_sol) == 1
b7_val = sp.nsimplify(b7_sol[0])
print(f"\nP_9's n^3 coefficient (fit value) = {c3_numeric}")
print(f"=> b7 = {b7_val}")

# ---------------------------------------------------------------------------
# Stage 1: expand to y^10 with b7 now numeric, 7 unknowns remaining.
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Stage 1: expand S(y) to y^10 with b7 known, partition P_10 coefficients")
print("=" * 70)

logA10 = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9 + a10*y**10
Bser10 = (sum(rat(b_known[j]) * y**j for j in range(1, 7))
          + b7_val*y**7 + b8*y**8 + b9*y**9 + b10*y**10)

K = 10
A10 = sp.series(sp.exp(logA10), y, 0, K + 1).removeO()
S10 = sp.expand(sp.series(A10 * sp.exp(n * Bser10), y, 0, K + 1).removeO())

P10 = sp.expand(S10.coeff(y, K))
P10_poly = sp.Poly(P10, n)

unknowns10 = {a7, a8, a9, a10, b8, b9, b10}
coeffs_clean10 = {}
print("P_10(n) coefficients by degree, clean = free of {a7,a8,a9,a10,b8,b9,b10}:")
for p in range(10, -1, -1):
    c = P10_poly.coeff_monomial(n**p) if p > 0 else P10_poly.coeff_monomial(1)
    c = sp.expand(c)
    free_syms = c.free_symbols & unknowns10
    clean = len(free_syms) == 0
    if clean:
        coeffs_clean10[p] = sp.nsimplify(c)
    tag = "CLEAN" if clean else f"depends on {sorted(s.name for s in free_syms)}"
    print(f"  degree n^{p}: {tag}")
    if clean:
        print(f"    value = {coeffs_clean10[p]}")

print()
print(f"Clean degrees: {sorted(coeffs_clean10, reverse=True)}")
print(f"Unresolved degrees: {sorted(set(range(11)) - set(coeffs_clean10), reverse=True)}")

# ---------------------------------------------------------------------------
# Stage 2: pull real diagonal-10 data, T(n,n-10), out of swept_rows.txt.
# block H=h has lines "n value" for n=1..25; the diagonal-10 point at that
# H is n=h+10 (since j=n-H=10).
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Stage 2: real diagonal-10 data T(n,n-10) from results/ns_a25/swept_rows.txt")
print("=" * 70)

rows_by_h = {}
cur_h = None
with open("results/ns_a25/swept_rows.txt") as f:
    for line in f:
        line = line.rstrip("\r\n")
        m = re.match(r"^===H(\d+)===$", line)
        if m:
            cur_h = int(m.group(1))
            rows_by_h[cur_h] = {}
            continue
        m = re.match(r"^(\d+)\s+(\d+)$", line)
        if m and cur_h is not None:
            rows_by_h[cur_h][int(m.group(1))] = int(m.group(2))

T10_data = {}
for h, rows in rows_by_h.items():
    nv = h + 10
    if nv in rows:
        T10_data[nv] = rows[nv]

print(f"Diagonal-10 points recovered: n = {sorted(T10_data)}")
for nv in sorted(T10_data):
    print(f"  T({nv},{nv-10}) = {T10_data[nv]}")

def P10_from_T(nval, Tval):
    # T(n,n-10) = P_10(n) * 3^(n-1-30) = P_10(n) * 3^(n-31)
    e = 31 - nval
    return sp.Rational(Tval) * sp.Integer(3) ** e

P10_data = {nv: P10_from_T(nv, Tv) for nv, Tv in T10_data.items()}

# ---------------------------------------------------------------------------
# Stage 3: fit the unclean coefficients (degrees not in coeffs_clean10).
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Stage 3: fit unclean P_10 coefficients from real data, validate held-out")
print("=" * 70)

unclean_degrees = sorted(set(range(11)) - set(coeffs_clean10))
print(f"Unclean degrees to fit: {unclean_degrees} ({len(unclean_degrees)} unknowns)")

csyms = {p: sp.symbols(f"c{p}") for p in unclean_degrees}
known_part10 = sum(coeffs_clean10[p] * n**p for p in coeffs_clean10)
unknown_part10 = sum(csyms[p] * n**p for p in unclean_degrees)

MIN_VALID_N = 2 * 10 + 1  # structural threshold n >= 2k+1 (docs/proofs/T-n-nm2-and-general.md)
all_nodes = sorted(nv for nv in P10_data if nv >= MIN_VALID_N)
print(f"Restricting to structurally-valid n >= {MIN_VALID_N} (docs' n>=2k+1 threshold):")
print(f"  valid nodes: {all_nodes}  (dropped as sub-threshold: {sorted(nv for nv in P10_data if nv < MIN_VALID_N)})")
n_unknowns = len(unclean_degrees)
if len(all_nodes) < n_unknowns:
    print(f"NOT ENOUGH DATA: need {n_unknowns} points, have {len(all_nodes)}. Stopping.")
else:
    fit_nodes = all_nodes[:n_unknowns]
    holdout_nodes = all_nodes[n_unknowns:]
    print(f"fit nodes (n): {fit_nodes}")
    print(f"holdout nodes (n): {holdout_nodes}")

    eqs = []
    for nv in fit_nodes:
        residual = P10_data[nv] - known_part10.subs(n, nv)
        eqs.append(sp.Eq(unknown_part10.subs(n, nv), residual))

    sol = sp.solve(eqs, list(csyms.values()), dict=True)
    assert len(sol) == 1, f"expected unique solution, got {sol}"
    sol = sol[0]
    print("\nSolved unknown coefficients:")
    for p in unclean_degrees:
        print(f"  c{p} = {sol[csyms[p]]}")

    P10_full = sp.expand(known_part10 + unknown_part10.subs(sol))

    print("\nHeld-out validation:")
    all_holdout_ok = True
    for nv in holdout_nodes:
        predicted = P10_full.subs(n, nv)
        actual = P10_data[nv]
        ok = sp.simplify(predicted - actual) == 0
        all_holdout_ok &= ok
        print(f"  n={nv}: predicted={predicted}, actual={actual}, match={ok}")
    print(f"\nALL HELD-OUT POINTS MATCH: {all_holdout_ok}")

    # -----------------------------------------------------------------------
    # Stage 3b: try to recover individual a7,a8,b8 from the P_10 fit, the way
    # b7 was recovered from P_9 -- check which of P_10's unclean coefficients
    # depend on a SINGLE unknown symbol (fully separable, no ambiguity).
    # -----------------------------------------------------------------------
    print()
    print("-" * 70)
    print("Stage 3b: which individual a7,a8,a9,a10,b8,b9,b10 can be isolated?")
    print("-" * 70)
    for p in unclean_degrees:
        c_expr = sp.expand(P10_poly.coeff_monomial(n**p) if p > 0 else P10_poly.coeff_monomial(1))
        free_syms = c_expr.free_symbols & unknowns10
        if len(free_syms) == 1:
            sym = next(iter(free_syms))
            val_sol = sp.solve(sp.Eq(c_expr, sol[csyms[p]]), sym)
            if val_sol:
                print(f"  degree n^{p} depends ONLY on {sym.name} => {sym.name} = {sp.nsimplify(val_sol[0])}")
        else:
            print(f"  degree n^{p} depends on {sorted(s.name for s in free_syms)} (not separable alone)")

    # -----------------------------------------------------------------------
    # Stage 4: integer-Horner self-check across ALL real diagonal-10 points.
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("Stage 4: integer numerator form + full self-check (all real points)")
    print("=" * 70)

    kfact = sp.factorial(10)
    P10_poly_full = sp.Poly(P10_full, n)
    num_coeffs = []
    for p in range(11):
        c = P10_poly_full.coeff_monomial(n**p) if p > 0 else P10_poly_full.coeff_monomial(1)
        nc = sp.nsimplify(c) * kfact
        assert nc.is_integer, f"c{p}*10! not integer: {nc}"
        num_coeffs.append(int(nc))

    print("P_10 * 10! numerator coefficients c0..c10:")
    for i, c in enumerate(num_coeffs):
        print(f"  c{i}*10! = {c}")

    print("\nHorner check across all real diagonal-10 points:")
    all_self_ok = True
    for nv in all_nodes:
        val = num_coeffs[-1]
        for c in reversed(num_coeffs[:-1]):
            val = val * nv + c
        e = nv - 31
        if e >= 0:
            t = sp.Rational(val, kfact) * (sp.Integer(3) ** e)
        else:
            t = sp.Rational(val, kfact) / (sp.Integer(3) ** (-e))
        ok = t.is_integer and int(t) == T10_data[nv]
        all_self_ok &= ok
        print(f"  n={nv}: computed T={t} vs actual T={T10_data[nv]}  match={ok}")
    print(f"\nALL SELF-CHECK POINTS MATCH: {all_self_ok}")

    print()
    print("Leading-coefficient check (25^10/10! conjecture):")
    expected_lead = sp.Rational(25**10, sp.factorial(10))
    print(f"  P_10 n^10 coeff = {coeffs_clean10.get(10)}")
    print(f"  25^10/10!       = {expected_lead}")
    print(f"  match = {coeffs_clean10.get(10) == expected_lead}")
