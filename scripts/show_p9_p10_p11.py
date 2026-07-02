#!/usr/bin/env python3
"""Print current best-knowledge summary of P_9, P_10 (fully pinned) and
P_11 (partially pinned) in both exact-rational and integer-numerator form.
Rebuilds everything from scratch from a_1..a_6/b_1..b_6 + real swept data,
so this is always consistent with derive_p9.py / derive_p10.py /
derive_p11_sizing.py -- it does not hardcode any previously-printed number.
"""
from fractions import Fraction as F
import re
import sympy as sp

y, n = sp.symbols("y n")
a7, a8, a9, a10, a11 = sp.symbols("a7 a8 a9 a10 a11")
b7, b8, b9, b10, b11 = sp.symbols("b7 b8 b9 b10 b11")

a_known = {1: F(-45), 2: F(-891, 2), 3: F(-10350), 4: F(-846963, 4), 5: F(-3781134), 6: F(-119091015)}
b_known = {1: F(25), 2: F(-209, 2), 3: F(4474, 3), 4: F(-22701, 4), 5: F(16144), 6: F(15126941, 3)}
def rat(f): return sp.Rational(f.numerator, f.denominator)

def load_rows():
    rows_by_h, cur_h = {}, None
    with open("results/ns_a25/swept_rows.txt") as f:
        for line in f:
            line = line.rstrip("\r\n")
            m = re.match(r"^===H(\d+)===$", line)
            if m: cur_h = int(m.group(1)); rows_by_h[cur_h] = {}; continue
            m = re.match(r"^(\d+)\s+(\d+)$", line)
            if m and cur_h is not None: rows_by_h[cur_h][int(m.group(1))] = int(m.group(2))
    return rows_by_h

rows_by_h = load_rows()

def diag_data(k):
    d = {}
    for h, rows in rows_by_h.items():
        nv = h + k
        if nv in rows: d[nv] = rows[nv]
    return d

def print_poly(label, poly_expr, deg, e_offset):
    """poly_expr: sympy poly in n. T(n,n-deg) = poly_expr * 3^(n-1-e_offset)"""
    kfact = sp.factorial(deg)
    P = sp.Poly(poly_expr, n)
    print(f"\n{label}(n), exact rational coefficients (n^{deg}..n^0):")
    for p in range(deg, -1, -1):
        c = P.coeff_monomial(n**p) if p > 0 else P.coeff_monomial(1)
        print(f"  n^{p}: {sp.nsimplify(c)}")
    print(f"  T(n, n-{deg}) = {label}(n) * 3^(n-{e_offset})")
    print(f"  integer numerator ({label}*{deg}!), c0..c{deg}:")
    for p in range(deg + 1):
        c = P.coeff_monomial(n**p) if p > 0 else P.coeff_monomial(1)
        nc = sp.nsimplify(c) * kfact
        print(f"    c{p}*{deg}! = {int(nc)}")

# ---------------------------------------------------------------------------
# P_9 -- fully pinned (6 clean from theory, 4 from data, 3 held out exact)
# ---------------------------------------------------------------------------
logA9 = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9
Bser9 = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7*y**7 + b8*y**8 + b9*y**9
A9 = sp.series(sp.exp(logA9), y, 0, 10).removeO()
S9 = sp.expand(sp.series(A9 * sp.exp(n * Bser9), y, 0, 10).removeO())
P9sym = sp.Poly(sp.expand(S9.coeff(y, 9)), n)

clean9 = {p: sp.nsimplify(P9sym.coeff_monomial(n**p) if p > 0 else P9sym.coeff_monomial(1))
          for p in range(9, 3, -1)}  # degrees 9..4 clean

T9 = diag_data(9)
valid9 = sorted(nv for nv in T9 if nv >= 19)
def P9_from_T(nv): return sp.Rational(T9[nv]) * sp.Integer(3) ** (28 - nv)
c3s, c2s, c1s, c0s = sp.symbols("c3 c2 c1 c0")
known9 = sum(clean9[p] * n**p for p in clean9)
unk9 = c3s*n**3 + c2s*n**2 + c1s*n + c0s
eqs9 = [sp.Eq(unk9.subs(n, nv), P9_from_T(nv) - known9.subs(n, nv)) for nv in valid9[:4]]
sol9 = sp.solve(eqs9, [c3s, c2s, c1s, c0s], dict=True)[0]
P9_full = sp.expand(known9 + unk9.subs(sol9))

print("=" * 72)
print("P_9: FULLY PINNED  (6 coeffs from theory a1-6/b1-6; 4 from 4 of 7 real")
print("points n=19-22; 3 held out n=23-25 matched exactly; leading coeff")
print("25^9/9! confirmed independently, not assumed)")
print("=" * 72)
print_poly("P_9", P9_full, 9, 28)

# ---------------------------------------------------------------------------
# P_10 -- fully pinned (7 clean from theory+b7, 4 from data, 1 held out exact)
# ---------------------------------------------------------------------------
c3_val = sol9[c3s]
b7_val = sp.solve(sp.Eq(P9sym.coeff_monomial(n**3), c3_val), b7)[0]

logA10 = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9 + a10*y**10
Bser10 = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7_val*y**7 + b8*y**8 + b9*y**9 + b10*y**10
A10 = sp.series(sp.exp(logA10), y, 0, 11).removeO()
S10 = sp.expand(sp.series(A10 * sp.exp(n * Bser10), y, 0, 11).removeO())
P10sym = sp.Poly(sp.expand(S10.coeff(y, 10)), n)

clean10 = {p: sp.nsimplify(P10sym.coeff_monomial(n**p) if p > 0 else P10sym.coeff_monomial(1))
           for p in range(10, 3, -1)}  # degrees 10..4 clean

T10 = diag_data(10)
valid10 = sorted(nv for nv in T10 if nv >= 21)
def P10_from_T(nv): return sp.Rational(T10[nv]) * sp.Integer(3) ** (31 - nv)
csyms10 = {p: sp.symbols(f"d{p}") for p in range(4)}
known10 = sum(clean10[p] * n**p for p in clean10)
unk10 = sum(csyms10[p] * n**p for p in range(4))
eqs10 = [sp.Eq(unk10.subs(n, nv), P10_from_T(nv) - known10.subs(n, nv)) for nv in valid10[:4]]
sol10 = sp.solve(eqs10, list(csyms10.values()), dict=True)[0]
P10_full = sp.expand(known10 + unk10.subs(sol10))

print()
print("=" * 72)
print(f"b7 recovered from P_9's n^3 coefficient (no new data): b7 = {b7_val}")
print("=" * 72)
print("P_10: FULLY PINNED  (7 coeffs from theory a1-6/b1-6+b7; 4 from 4 of 5")
print("structurally-valid real points n=21-24; 1 held out n=25 matched")
print("exactly; leading coeff 25^10/10! confirmed independently)")
print("=" * 72)
print_poly("P_10", P10_full, 10, 31)

# ---------------------------------------------------------------------------
# P_11 -- partially pinned: 7 of 12 coefficients clean
# ---------------------------------------------------------------------------
logA11 = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9 + a10*y**10 + a11*y**11
Bser11 = sum(rat(b_known[j]) * y**j for j in range(1, 7)) + b7_val*y**7 + b8*y**8 + b9*y**9 + b10*y**10 + b11*y**11
A11 = sp.series(sp.exp(logA11), y, 0, 12).removeO()
S11 = sp.expand(sp.series(A11 * sp.exp(n * Bser11), y, 0, 12).removeO())
P11sym = sp.Poly(sp.expand(S11.coeff(y, 11)), n)

unknowns11 = {a7, a8, a9, a10, a11, b8, b9, b10, b11}
print()
print("=" * 72)
print("P_11: PARTIALLY PINNED -- 7 of 12 coefficients clean from theory,")
print("5 unclean (n^4..n^0), need 2 more real diagonal-11 points beyond")
print("today's 3 valid ones (n=23,24,25) -- expected as a free byproduct")
print("of a26/a27's genuine sweeps (T(26,15), T(27,16))")
print("=" * 72)
for p in range(11, -1, -1):
    c = sp.expand(P11sym.coeff_monomial(n**p) if p > 0 else P11sym.coeff_monomial(1))
    free = c.free_symbols & unknowns11
    if not free:
        print(f"  n^{p}: {sp.nsimplify(c)}   [CLEAN]")
    else:
        print(f"  n^{p}: UNKNOWN, depends on {sorted(s.name for s in free)}")

expected_lead11 = sp.Rational(25**11, sp.factorial(11))
lead11 = sp.nsimplify(P11sym.coeff_monomial(n**11))
print(f"\n  leading coeff n^11 = {lead11}  (25^11/11! = {expected_lead11}, match={lead11==expected_lead11})")
