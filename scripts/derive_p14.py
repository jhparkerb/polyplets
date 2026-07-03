#!/usr/bin/env python3
"""Derive P_14(n), extending derive_p13.py one diagonal further.

Bootstrap: the validated P_9,P_10,P_11 fits pin the shared universal series
symbols {a7..a11,b8..b11} exactly (Stage 1); P_12's fit then pins a12,b12
(Stage 2). With {a7..a12,b8..b12} all numeric, all but two of P_13's
coefficients come clean from theory; only a13,b13 (degrees n^0,n^1) need new
data. Diagonal-13 real points, all at n >= 2*13+1 = 27:
  T(27,14) = 63986427407097237332   (results/ns_a27/perheight/h14.out)
  T(28,15) = 343733831675681363476  (results/ns_a28/perheight/h15.out)
  T(29,16) = 1795111626265027715356 (results/ns_a29/perheight/h16.out)
  T(30,17) = 9142099138689979555656 (results/ns_a30/perheight/h17.out)
  T(31,18) = 45518261981941858305944(results/ns_a31/perheight/h18.out)
Fit a13,b13 from the two newest (n=30,31); hold out n=27,28,29 (fed neither
the fit nor the shared-symbol solve).

Wiring P_13 makes H=maxn-13 a closed-form diagonal. For a(32) that is H19 --
its top real height -- so a(32)'s dominant sweep drops one tier (H19->H18),
roughly a31's cost instead of a fresh ~3x tier.
"""
from fractions import Fraction as F
import sympy as sp

y, n = sp.symbols("y n")
a = {j: sp.Symbol(f"a{j}") for j in range(7, 15)}
b = {j: sp.Symbol(f"b{j}") for j in range(8, 15)}

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
print("Stage 1: solve shared {a7..a11,b8..b11} from validated P_9,P_10,P_11")
print("=" * 72)

banked_specs = [
    (9, {7: a[7], 8: a[8], 9: a[9]}, {8: b[8], 9: b[9]}),
    (10, {7: a[7], 8: a[8], 9: a[9], 10: a[10]}, {8: b[8], 9: b[9], 10: b[10]}),
    (11, {7: a[7], 8: a[8], 9: a[9], 10: a[10], 11: a[11]},
         {8: b[8], 9: b[9], 10: b[10], 11: b[11]}),
]
# diag-9,10 points come from a25 swept_rows via load_swept; diag-11 fitting
# points are the two real sweeps that closed P_11 (T(26,15), T(27,16)).
new_pts = {11: {26: 5614506356004078534, 27: 27798973373501478242}}


def load_swept(k, min_n):
    import re
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
sol_set = sp.linsolve(all_eqs, shared)
assert len(sol_set) == 1, f"shared system not uniquely solvable/consistent: {sol_set}"
sol_shared = dict(zip(shared, next(iter(sol_set))))
assert all(sp.expand(e.lhs.subs(sol_shared) - e.rhs) == 0 for e in all_eqs)
print(f"  shared {len(shared)} symbols solved, all {len(all_eqs)} eqns consistent")

print()
print("=" * 72)
print("Stage 2: pin a12,b12 from P_12 diagonal-12 fit (n=26,27), hold out n=25")
print("=" * 72)

p12 = Pk_poly(12, {j: a[j] for j in range(7, 13)}, {j: b[j] for j in range(8, 13)})
unknowns12 = {a[12], b[12]}
known12, unclean12 = sp.Integer(0), {}
for p in range(12, -1, -1):
    c = sp.expand((p12.coeff_monomial(n**p) if p > 0 else p12.coeff_monomial(1)).subs(sol_shared))
    if c.free_symbols & unknowns12:
        unclean12[p] = c
    else:
        known12 += sp.nsimplify(c) * n**p
T12 = {25: 1573134737210737385, 26: 8490578913536448064, 27: 44416775012217775973}
up12 = sum(unclean12[p] * n**p for p in unclean12)
eqs12 = [sp.Eq(up12.subs(n, nv), P_from_T(nv, T12[nv], 12) - known12.subs(n, nv)) for nv in (26, 27)]
sol12 = sp.solve(eqs12, [a[12], b[12]], dict=True)[0]
P12_full = sp.expand(known12 + up12.subs(sol12))
assert sp.nsimplify(P12_full.subs(n, 25)) - P_from_T(25, T12[25], 12) == 0, "P12 a25 holdout FAILED"
print(f"  a12,b12 pinned; a25 diagonal-12 holdout matches")
sol_all = dict(sol_shared); sol_all.update(sol12)

print()
print("=" * 72)
print("Stage 3: substitute {a7..a12,b8..b12} into P_13; fit a13,b13 (n=30,31)")
print("=" * 72)

p13 = Pk_poly(13, {j: a[j] for j in range(7, 14)}, {j: b[j] for j in range(8, 14)})
unknowns13 = {a[13], b[13]}
known13, unclean13 = sp.Integer(0), {}
for p in range(13, -1, -1):
    c = sp.expand((p13.coeff_monomial(n**p) if p > 0 else p13.coeff_monomial(1)).subs(sol_all))
    if c.free_symbols & unknowns13:
        unclean13[p] = c
        print(f"  degree n^{p}: depends on {sorted(s.name for s in c.free_symbols & unknowns13)}")
    else:
        known13 += sp.nsimplify(c) * n**p
print(f"  genuinely unknown: {sorted(unclean13)} -> a13,b13")

T13 = {27: 63986427407097237332, 28: 343733831675681363476,
       29: 1795111626265027715356, 30: 9142099138689979555656,
       31: 45518261981941858305944}
fit_nodes, holdout = [30, 31], [27, 28, 29]
up13 = sum(unclean13[p] * n**p for p in unclean13)
eqs13 = [sp.Eq(up13.subs(n, nv), P_from_T(nv, T13[nv], 13) - known13.subs(n, nv)) for nv in fit_nodes]
sol13 = sp.solve(eqs13, [a[13], b[13]], dict=True)[0]
print(f"  a13 = {sol13[a[13]]}")
print(f"  b13 = {sol13[b[13]]}")
P13_full = sp.expand(known13 + up13.subs(sol13))

print("\nHeld-out validation (diagonal-13 points used nowhere in derivation):")
all_ok = True
for nv in holdout:
    ok = sp.simplify(sp.nsimplify(P13_full.subs(n, nv)) - P_from_T(nv, T13[nv], 13)) == 0
    all_ok &= ok
    print(f"  n={nv}: match={ok}")
assert all_ok, "HELD-OUT VALIDATION FAILED"
print("ALL HELD-OUT POINTS MATCH")
sol_all.update(sol13)  # a13,b13 now pinned for P_14


print()
print("=" * 72)
print("Stage 4: substitute {a7..a13,b8..b13} into P_14; fit a14,b14 (n=31,32)")
print("=" * 72)

p14 = Pk_poly(14, {j: a[j] for j in range(7, 15)}, {j: b[j] for j in range(8, 15)})
unknowns14 = {a[14], b[14]}
known14, unclean14 = sp.Integer(0), {}
for p in range(14, -1, -1):
    c = sp.expand((p14.coeff_monomial(n**p) if p > 0 else p14.coeff_monomial(1)).subs(sol_all))
    if c.free_symbols & unknowns14:
        unclean14[p] = c
        print(f"  degree n^{p}: depends on {sorted(s.name for s in c.free_symbols & unknowns14)}")
    else:
        known14 += sp.nsimplify(c) * n**p
print(f"  genuinely unknown: {sorted(unclean14)} -> a14,b14")

# Diagonal-14 points T(n,n-14), all from banked per-height sweeps
# (results/ns_a{n}/perheight/h{n-14}.out). Valid n >= 2*14+1 = 29.
T14 = {28: 474128250726563452491, 29: 2611110015255604740530,
       30: 13969442417594351366268, 31: 72837427176953272756444,
       32: 371092643133615870167145}
fit_nodes, holdout = [31, 32], [29, 30]
up14 = sum(unclean14[p] * n**p for p in unclean14)
eqs14 = [sp.Eq(up14.subs(n, nv), P_from_T(nv, T14[nv], 14) - known14.subs(n, nv)) for nv in fit_nodes]
sol14 = sp.solve(eqs14, [a[14], b[14]], dict=True)[0]
print(f"  a14 = {sol14[a[14]]}")
print(f"  b14 = {sol14[b[14]]}")
P14_full = sp.expand(known14 + up14.subs(sol14))

print("\nHeld-out validation (diagonal-14 points used nowhere in derivation):")
all_ok = True
for nv in holdout:
    ok = sp.simplify(sp.nsimplify(P14_full.subs(n, nv)) - P_from_T(nv, T14[nv], 14)) == 0
    all_ok &= ok
    print(f"  n={nv}: match={ok}")
assert all_ok, "HELD-OUT VALIDATION FAILED"
print("ALL HELD-OUT POINTS MATCH")
ok28 = sp.simplify(sp.nsimplify(P14_full.subs(n, 28)) - P_from_T(28, T14[28], 14)) == 0
print(f"  [n=28 = 2k, below validity n>=29: match={ok28}]")

print()
print("=" * 72)
print("Stage 5: integer numerator (P_14 * 14!) + checks + wiring block")
print("=" * 72)

kfact = sp.factorial(14)
P14_poly = sp.Poly(P14_full, n)
num_coeffs = []
for p in range(15):
    c = P14_poly.coeff_monomial(n**p) if p > 0 else P14_poly.coeff_monomial(1)
    nc = sp.nsimplify(c) * kfact
    assert nc.is_integer, f"c{p}*14! not integer: {nc}"
    num_coeffs.append(int(nc))

lead_ok = P14_poly.coeff_monomial(n**14) == sp.Rational(25**14, sp.factorial(14))
print(f"Leading-coefficient check (25^14/14!): {lead_ok}")
assert lead_ok

print("Horner self-check across real diagonal-14 points (n>=29):")
all_self_ok = True
for nv in sorted(T14):
    if nv < 29:
        continue
    val = num_coeffs[-1]
    for c in reversed(num_coeffs[:-1]):
        val = val * nv + c
    e = nv - (1 + 3 * 14)
    t = sp.Rational(val, kfact) * sp.Integer(3) ** e if e >= 0 else \
        sp.Rational(val, kfact) / sp.Integer(3) ** (-e)
    ok = t.is_integer and int(t) == T14[nv]
    all_self_ok &= ok
    print(f"  n={nv}: match={ok}")
assert all_self_ok

print("\nGo wiring block (diagCoeffTable case 14), c14..c0 then denom 14!:")
print("  14: {[]string{")
desc = list(reversed(num_coeffs))
for i in range(0, len(desc), 4):
    print("    " + ", ".join(f'"{c}"' for c in desc[i:i + 4]) + ",")
print(f"  }}, {int(kfact)}}},")
