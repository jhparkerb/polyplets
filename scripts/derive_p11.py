#!/usr/bin/env python3
"""Derive P_11(n) fully, closing the last diagonal needed for a(28).

Methodology continues derive_p9.py / derive_p10.py. The a_j, b_j are the
universal log-A / B series coefficients shared across ALL diagonals, so the
already-validated P_9 and P_10 fits are exact linear equations on the shared
unknowns {a7,a8,a9,a10,b8,b9,b10} (b7 was recovered exactly from P_9).

Stage 0: b7 known (derive_p10.py Stage 0).
Stage 1: re-fit P_9 and P_10 unclean coefficients from real diagonal data,
         producing 8 exact equations in the 7 shared unknowns. Solve them;
         the system is OVER-determined (8 eqns, 7 unknowns) -> its consistency
         is itself an independent check of P_9/P_10.
Stage 2: substitute the solved shared symbols into P_11's symbolic
         coefficients. Only a11 (degree n^0) and b11 (degree n^1) remain
         unknown -> just 2 genuinely new numbers needed.
Stage 3: fit a11,b11 from the two NEW real points T(26,15), T(27,16); then
         HELD-OUT validate against the three a25 diagonal-11 points
         (n=23,24,25) which fed neither the fit nor the shared-symbol solve.
Stage 4: integer-numerator (Horner) form + full self-check + wiring block.
"""
from fractions import Fraction as F
import re
import sympy as sp

y, n = sp.symbols("y n")
a7, a8, a9, a10, a11 = sp.symbols("a7 a8 a9 a10 a11")
b7, b8, b9, b10, b11 = sp.symbols("b7 b8 b9 b10 b11")

a_known = {
    1: F(-45), 2: F(-891, 2), 3: F(-10350),
    4: F(-846963, 4), 5: F(-3781134), 6: F(-119091015),
}
b_known = {
    1: F(25), 2: F(-209, 2), 3: F(4474, 3),
    4: F(-22701, 4), 5: F(16144), 6: F(15126941, 3),
}
b7_val = sp.Rational(-687296991, 7)  # recovered in derive_p10.py Stage 0


def rat(f):
    return sp.Rational(f.numerator, f.denominator)


def base(K):
    """log A series and B series (with b7 numeric) truncated for diagonal K."""
    la = sum(rat(a_known[j]) * y**j for j in range(1, 7))
    bs = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7_val * y**7
    return la, bs


def Pk_poly(K, a_syms, b_syms):
    """Symbolic P_K(n) with the given higher a_j (j>=7) / b_j (j>=8) symbols."""
    la, bs = base(K)
    la = la + sum(a_syms[j] * y**j for j in a_syms)
    bs = bs + sum(b_syms[j] * y**j for j in b_syms)
    A = sp.series(sp.exp(la), y, 0, K + 1).removeO()
    S = sp.series(A * sp.exp(n * bs), y, 0, K + 1).removeO()
    return sp.Poly(sp.expand(S.coeff(y, K)), n)


def load_diag(k, min_n):
    """Real T(n,n-k) points from a25 swept rows with n>=min_n (structurally valid)."""
    rows_by_h, cur = {}, None
    with open("results/ns_a25/swept_rows.txt") as f:
        for line in f:
            line = line.rstrip("\r\n")
            m = re.match(r"^===H(\d+)===$", line)
            if m:
                cur = int(m.group(1)); rows_by_h[cur] = {}; continue
            m = re.match(r"^(\d+)\s+(\d+)$", line)
            if m and cur is not None:
                rows_by_h[cur][int(m.group(1))] = int(m.group(2))
    out = {}
    for h, rows in rows_by_h.items():
        nv = h + k
        if nv in rows and nv >= min_n:
            out[nv] = rows[nv]
    return out


def P_from_T(nval, Tval, k):
    """T(n,n-k) = P_k(n) * 3^(n-1-3k)  ->  P_k(n) = T * 3^(1+3k-n)."""
    e = 1 + 3 * k - nval
    return sp.Rational(Tval) * sp.Integer(3) ** e


def fit_unclean(poly, k, unknown_syms, data):
    """Fit the coefficients that still depend on unknown_syms from real data.
    Returns {degree: numeric value} for the unclean degrees."""
    unclean = []
    clean = {}
    for p in range(k, -1, -1):
        c = sp.expand(poly.coeff_monomial(n**p) if p > 0 else poly.coeff_monomial(1))
        if c.free_symbols & unknown_syms:
            unclean.append(p)
        else:
            clean[p] = sp.nsimplify(c)
    unclean = sorted(unclean)
    known_part = sum(clean[p] * n**p for p in clean)
    csyms = {p: sp.Symbol(f"c{p}") for p in unclean}
    unknown_part = sum(csyms[p] * n**p for p in unclean)
    nodes = sorted(data)[: len(unclean)]
    assert len(nodes) == len(unclean), f"need {len(unclean)} points, have {len(data)}"
    eqs = [sp.Eq(unknown_part.subs(n, nv),
                 P_from_T(nv, data[nv], k) - known_part.subs(n, nv)) for nv in nodes]
    sol = sp.solve(eqs, list(csyms.values()), dict=True)[0]
    return {p: sol[csyms[p]] for p in unclean}, unclean


print("=" * 72)
print("Stage 1: banked equations from the validated P_9 and P_10 fits")
print("=" * 72)

# --- P_9: unknowns a7,a8,a9,b8,b9 (b7 numeric) ---
p9 = Pk_poly(9, {7: a7, 8: a8, 9: a9}, {8: b8, 9: b9})
u9 = {a7, a8, a9, b8, b9}
d9 = load_diag(9, 2 * 9 + 1)
fit9, unc9 = fit_unclean(p9, 9, u9, d9)
print(f"P_9 unclean degrees {unc9} fitted; deriving symbolic equations...")
eqs9 = []
for p, val in fit9.items():
    expr = sp.expand(p9.coeff_monomial(n**p) if p > 0 else p9.coeff_monomial(1))
    eqs9.append(sp.Eq(expr, val))

# --- P_10: unknowns a7,a8,a9,a10,b8,b9,b10 ---
p10 = Pk_poly(10, {7: a7, 8: a8, 9: a9, 10: a10}, {8: b8, 9: b9, 10: b10})
u10 = {a7, a8, a9, a10, b8, b9, b10}
d10 = load_diag(10, 2 * 10 + 1)
fit10, unc10 = fit_unclean(p10, 10, u10, d10)
print(f"P_10 unclean degrees {unc10} fitted; deriving symbolic equations...")
eqs10 = []
for p, val in fit10.items():
    expr = sp.expand(p10.coeff_monomial(n**p) if p > 0 else p10.coeff_monomial(1))
    eqs10.append(sp.Eq(expr, val))

shared = [a7, a8, a9, a10, b8, b9, b10]
all_eqs = eqs9 + eqs10
print(f"\n{len(all_eqs)} equations in {len(shared)} shared unknowns "
      f"(OVER-determined by {len(all_eqs) - len(shared)}).")
# The shared symbols enter every y^K coefficient LINEARLY (any product lands at
# y-degree >= 14, above the K<=12 truncation), so this is a linear system —
# linsolve is far faster than the general solver on these large rationals, and
# returns EmptySet if the (over-determined) system is inconsistent.
sol_set = sp.linsolve(all_eqs, shared)
assert len(sol_set) == 1, f"shared system not uniquely solvable/consistent: {sol_set}"
sol_shared = dict(zip(shared, next(iter(sol_set))))
# consistency: every equation must hold under the solution
consistent = all(sp.expand(e.lhs.subs(sol_shared) - e.rhs) == 0 for e in all_eqs)
print(f"All {len(all_eqs)} equations consistent under the unique solution: {consistent}")
assert consistent, "P_9/P_10 banked equations are INCONSISTENT -- stop."
print("\nSolved shared symbols (universal series coefficients):")
for s in shared:
    print(f"  {s} = {sol_shared[s]}")

print()
print("=" * 72)
print("Stage 2: substitute shared symbols into P_11; only a11,b11 remain")
print("=" * 72)

p11 = Pk_poly(11, {7: a7, 8: a8, 9: a9, 10: a10, 11: a11},
              {8: b8, 9: b9, 10: b10, 11: b11})
unknowns11 = {a11, b11}
known_part11 = sp.Integer(0)
unclean11 = {}
for p in range(11, -1, -1):
    c = sp.expand((p11.coeff_monomial(n**p) if p > 0 else p11.coeff_monomial(1)).subs(sol_shared))
    free = c.free_symbols & unknowns11
    if free:
        unclean11[p] = c
        print(f"  degree n^{p}: depends on {sorted(s.name for s in free)}")
    else:
        known_part11 += sp.nsimplify(c) * n**p
        print(f"  degree n^{p}: CLEAN")
print(f"\nGenuinely unknown after banked theory: {sorted(unclean11)} "
      f"({len(unclean11)} degrees -> {len(unknowns11)} new numbers a11,b11)")

print()
print("=" * 72)
print("Stage 3: fit a11,b11 from the 2 NEW points, hold out the a25 points")
print("=" * 72)

T11 = load_diag(11, 2 * 11 + 1)          # a25 diagonal-11: n=23,24,25
T11[26] = 5614506356004078534           # T(26,15), from results/ns_a26
T11[27] = 27798973373501478242          # T(27,16), from results/ns_a27
fit_nodes = [26, 27]
holdout_nodes = [23, 24, 25]
print(f"fit nodes (the 2 new sweeps): {fit_nodes}")
print(f"held-out nodes (a25, independent of the shared-symbol solve): {holdout_nodes}")

unknown_part11 = sum(unclean11[p] * n**p for p in unclean11)
eqs11 = []
for nv in fit_nodes:
    resid = P_from_T(nv, T11[nv], 11) - known_part11.subs(n, nv)
    eqs11.append(sp.Eq(unknown_part11.subs(n, nv), resid))
sol11 = sp.solve(eqs11, [a11, b11], dict=True)[0]
print(f"\n  a11 = {sol11[a11]}")
print(f"  b11 = {sol11[b11]}")

P11_full = sp.expand(known_part11 + unknown_part11.subs(sol11))

print("\nHeld-out validation (a25 diagonal-11, used nowhere in the derivation):")
all_ok = True
for nv in holdout_nodes:
    predicted = sp.nsimplify(P11_full.subs(n, nv))
    actual = P_from_T(nv, T11[nv], 11)
    ok = sp.simplify(predicted - actual) == 0
    all_ok &= ok
    print(f"  n={nv}: match={ok}")
print(f"\nALL HELD-OUT POINTS MATCH: {all_ok}")
assert all_ok, "held-out validation FAILED"

print()
print("=" * 72)
print("Stage 4: integer numerator (P_11 * 11!) + full self-check + wiring")
print("=" * 72)

kfact = sp.factorial(11)
P11_poly = sp.Poly(P11_full, n)
num_coeffs = []
for p in range(12):
    c = P11_poly.coeff_monomial(n**p) if p > 0 else P11_poly.coeff_monomial(1)
    nc = sp.nsimplify(c) * kfact
    assert nc.is_integer, f"c{p}*11! not integer: {nc}"
    num_coeffs.append(int(nc))

print("P_11 * 11! numerator coefficients c0..c11:")
for i, c in enumerate(num_coeffs):
    print(f"  c{i} = {c}")

print("\nLeading-coefficient check (25^11/11! conjecture):")
lead = sp.Rational(25**11, sp.factorial(11))
print(f"  match = {P11_poly.coeff_monomial(n**11) == lead}")

print("\nHorner self-check across ALL real diagonal-11 points:")
all_self_ok = True
for nv in sorted(T11):
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * nv + c
    e = nv - (1 + 3 * 11)  # 3^(n-34)
    t = sp.Rational(val, kfact) * sp.Integer(3) ** e if e >= 0 else \
        sp.Rational(val, kfact) / sp.Integer(3) ** (-e)
    ok = t.is_integer and int(t) == T11[nv]
    all_self_ok &= ok
    print(f"  n={nv}: computed T={int(t) if t.is_integer else t}  match={ok}")
print(f"\nALL SELF-CHECK POINTS MATCH: {all_self_ok}")
assert all_self_ok

print()
print("Go wiring block (diagonalCell case 11), c0..c11 then denom 11!:")
print("  num := []*big.Int{")
for c in num_coeffs:
    print(f"    big.NewInt(0).SetString(\"{c}\", 10),")
print("  }")
print(f"  denom 11! = {int(kfact)}")
