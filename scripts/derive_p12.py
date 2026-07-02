#!/usr/bin/env python3
"""Derive P_12(n), extending the derive_p11.py bootstrap one diagonal further.

The validated P_9, P_10 AND P_11 fits now pin the shared universal series
symbols {a7..a11, b8..b11} exactly (b7 is known). So all but two of P_12's
coefficients come clean from theory; only a12,b12 (degrees n^0,n^1) need new
data. Diagonal-12 real points, all at n >= 2*12+1 = 25:
  T(25,13) = 1573134737210737385   (results/ns_a25/swept_rows.txt)
  T(26,14) = 8490578913536448064   (results/ns_a26/perheight/h14.out)
  T(27,15) = 44416775012217775973  (results/ns_a27/perheight/h15.out)
Fit a12,b12 from the two newest (n=26,27); hold out the a25 point (n=25),
which fed neither the fit nor the shared-symbol solve.

Wiring P_12 keeps a(29)'s top real height at H=maxn-12 (same tier as a28's
H=maxn-11) instead of climbing a ~3x column tier.
"""
from fractions import Fraction as F
import re
import sympy as sp

y, n = sp.symbols("y n")
a = {j: sp.Symbol(f"a{j}") for j in range(7, 13)}
b = {j: sp.Symbol(f"b{j}") for j in range(8, 13)}

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


def Pk_poly(K, syms_a, syms_b):
    """Symbolic P_K(n) with the given higher a_j (j>=7) / b_j (j>=8) symbols."""
    la = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + sum(syms_a[j] * y**j for j in syms_a)
    bs = (sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7_val * y**7
          + sum(syms_b[j] * y**j for j in syms_b))
    A = sp.series(sp.exp(la), y, 0, K + 1).removeO()
    S = sp.series(A * sp.exp(n * bs), y, 0, K + 1).removeO()
    return sp.Poly(sp.expand(S.coeff(y, K)), n)


def load_swept(k, min_n):
    """Real T(n,n-k) points from a25 swept rows with n>=min_n."""
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
    return {h + k: rows_by_h[h][h + k] for h in rows_by_h
            if (h + k) in rows_by_h[h] and (h + k) >= min_n}


def P_from_T(nval, Tval, k):
    """T(n,n-k) = P_k(n) * 3^(n-1-3k)."""
    return sp.Rational(Tval) * sp.Integer(3) ** (1 + 3 * k - nval)


def fit_unclean(poly, k, unknown_syms, data):
    """Fit the unclean coefficients from real data; return {degree: value}."""
    unclean, clean = [], {}
    for p in range(k, -1, -1):
        c = sp.expand(poly.coeff_monomial(n**p) if p > 0 else poly.coeff_monomial(1))
        if c.free_symbols & unknown_syms:
            unclean.append(p)
        else:
            clean[p] = c
    unclean = sorted(unclean)
    known_part = sum(sp.nsimplify(clean[p]) * n**p for p in clean)
    csyms = {p: sp.Symbol(f"c{p}") for p in unclean}
    unknown_part = sum(csyms[p] * n**p for p in unclean)
    nodes = sorted(data)[: len(unclean)]
    eqs = [sp.Eq(unknown_part.subs(n, nv),
                 P_from_T(nv, data[nv], k) - known_part.subs(n, nv)) for nv in nodes]
    sol = sp.solve(eqs, list(csyms.values()), dict=True)[0]
    return {p: sol[csyms[p]] for p in unclean}


print("=" * 72)
print("Stage 1: banked equations from validated P_9, P_10, P_11 fits")
print("=" * 72)

banked_specs = [
    (9, {7: a[7], 8: a[8], 9: a[9]}, {8: b[8], 9: b[9]}),
    (10, {7: a[7], 8: a[8], 9: a[9], 10: a[10]}, {8: b[8], 9: b[9], 10: b[10]}),
    (11, {7: a[7], 8: a[8], 9: a[9], 10: a[10], 11: a[11]},
         {8: b[8], 9: b[9], 10: b[10], 11: b[11]}),
]
new_pts = {11: {26: 5614506356004078534, 27: 27798973373501478242}}  # diag-11 fitting pts

all_eqs = []
for K, sa, sb in banked_specs:
    poly = Pk_poly(K, sa, sb)
    usyms = set(sa.values()) | set(sb.values())
    data = load_swept(K, 2 * K + 1)
    data.update(new_pts.get(K, {}))
    fit = fit_unclean(poly, K, usyms, data)
    for p, val in fit.items():
        expr = sp.expand(poly.coeff_monomial(n**p) if p > 0 else poly.coeff_monomial(1))
        all_eqs.append(sp.Eq(expr, val))
    print(f"  P_{K}: {len(fit)} unclean-coeff equations added")

shared = [a[7], a[8], a[9], a[10], a[11], b[8], b[9], b[10], b[11]]
print(f"\n{len(all_eqs)} equations in {len(shared)} shared unknowns.")
# The shared symbols enter every y^K coefficient LINEARLY (any product lands at
# y-degree >= 14, above the K<=12 truncation), so this is a linear system —
# linsolve is far faster than the general solver on these large rationals, and
# returns EmptySet if the (over-determined) system is inconsistent.
sol_set = sp.linsolve(all_eqs, shared)
assert len(sol_set) == 1, f"shared system not uniquely solvable/consistent: {sol_set}"
sol_shared = dict(zip(shared, next(iter(sol_set))))
consistent = all(sp.expand(e.lhs.subs(sol_shared) - e.rhs) == 0 for e in all_eqs)
print(f"All {len(all_eqs)} equations consistent under the unique solution: {consistent}")
assert consistent
print("Shared symbols solved (a7..a11, b8..b11).")

print()
print("=" * 72)
print("Stage 2: substitute shared symbols into P_12; only a12,b12 remain")
print("=" * 72)

p12 = Pk_poly(12, {j: a[j] for j in range(7, 13)},
              {j: b[j] for j in range(8, 13)})
unknowns12 = {a[12], b[12]}
known_part12 = sp.Integer(0)
unclean12 = {}
for p in range(12, -1, -1):
    c = sp.expand((p12.coeff_monomial(n**p) if p > 0 else p12.coeff_monomial(1)).subs(sol_shared))
    free = c.free_symbols & unknowns12
    if free:
        unclean12[p] = c
        print(f"  degree n^{p}: depends on {sorted(s.name for s in free)}")
    else:
        known_part12 += sp.nsimplify(c) * n**p
        print(f"  degree n^{p}: CLEAN")
print(f"\nGenuinely unknown after banked theory: {sorted(unclean12)} "
      f"-> {len(unknowns12)} new numbers a12,b12")

print()
print("=" * 72)
print("Stage 3: fit a12,b12 from the 2 newest points, hold out the a25 point")
print("=" * 72)

T12 = {25: 1573134737210737385,   # T(25,13), a25 (held out)
       26: 8490578913536448064,   # T(26,14), a26 (fit)
       27: 44416775012217775973}  # T(27,15), a27 (fit)
fit_nodes, holdout_nodes = [26, 27], [25]
unknown_part12 = sum(unclean12[p] * n**p for p in unclean12)
eqs12 = [sp.Eq(unknown_part12.subs(n, nv),
               P_from_T(nv, T12[nv], 12) - known_part12.subs(n, nv)) for nv in fit_nodes]
sol12 = sp.solve(eqs12, [a[12], b[12]], dict=True)[0]
print(f"  a12 = {sol12[a[12]]}")
print(f"  b12 = {sol12[b[12]]}")

P12_full = sp.expand(known_part12 + unknown_part12.subs(sol12))
print("\nHeld-out validation (a25 diagonal-12, used nowhere in the derivation):")
all_ok = True
for nv in holdout_nodes:
    ok = sp.simplify(sp.nsimplify(P12_full.subs(n, nv)) - P_from_T(nv, T12[nv], 12)) == 0
    all_ok &= ok
    print(f"  n={nv}: match={ok}")
print(f"\nALL HELD-OUT POINTS MATCH: {all_ok}")
assert all_ok

print()
print("=" * 72)
print("Stage 4: integer numerator (P_12 * 12!) + self-check + wiring block")
print("=" * 72)

kfact = sp.factorial(12)
P12_poly = sp.Poly(P12_full, n)
num_coeffs = []
for p in range(13):
    c = P12_poly.coeff_monomial(n**p) if p > 0 else P12_poly.coeff_monomial(1)
    nc = sp.nsimplify(c) * kfact
    assert nc.is_integer, f"c{p}*12! not integer: {nc}"
    num_coeffs.append(int(nc))

print("Leading-coefficient check (25^12/12! conjecture):")
print(f"  match = {P12_poly.coeff_monomial(n**12) == sp.Rational(25**12, sp.factorial(12))}")

print("\nHorner self-check across ALL real diagonal-12 points:")
all_self_ok = True
for nv in sorted(T12):
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * nv + c
    e = nv - (1 + 3 * 12)
    t = sp.Rational(val, kfact) * sp.Integer(3) ** e if e >= 0 else \
        sp.Rational(val, kfact) / sp.Integer(3) ** (-e)
    ok = t.is_integer and int(t) == T12[nv]
    all_self_ok &= ok
    print(f"  n={nv}: computed T={int(t) if t.is_integer else t}  match={ok}")
print(f"\nALL SELF-CHECK POINTS MATCH: {all_self_ok}")
assert all_self_ok

print("\nGo wiring block (diagCoeffTable case 12), c12..c0 then denom 12!:")
print("  12: {[]string{")
desc = list(reversed(num_coeffs))  # highest degree first, matching the table
for i in range(0, len(desc), 4):
    print("    " + ", ".join(f'"{c}"' for c in desc[i:i + 4]) + ",")
print(f"  }}, {int(kfact)}}},")
