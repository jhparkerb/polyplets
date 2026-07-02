#!/usr/bin/env python3
"""Size up what P_11(n) would require, given everything pinned so far:
a_1..a_6, b_1..b_6 (known), b7 (recovered from the P_9 fit, see
derive_p10.py Stage 0), and the four linear equations recovered from the
P_10 fit (P_10's n^3..n^0 coefficients, each an affine function of
a7,a8,a9,a10,b8,b9,b10 -- see derive_p10.py Stage 3).

This does NOT claim to derive P_11 -- it sizes the gap: how many
coefficients of P_11 come out clean from theory + the P_9/P_10 equations
already banked, versus how many genuinely new numbers (real data or new
theory) would still be needed, and whether enough valid real data exists
in results/ns_a25/swept_rows.txt to supply them.
"""
from fractions import Fraction as F
import re
import sympy as sp

y, n = sp.symbols("y n")
a7, a8, a9, a10, a11 = sp.symbols("a7 a8 a9 a10 a11")
b8, b9, b10, b11 = sp.symbols("b8 b9 b10 b11")

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

logA = sum(rat(a_known[j]) * y**j for j in range(1, 7)) + a7*y**7 + a8*y**8 + a9*y**9 + a10*y**10 + a11*y**11
Bser = (sum(rat(b_known[j]) * y**j for j in range(1, 7))
        + b7_val*y**7 + b8*y**8 + b9*y**9 + b10*y**10 + b11*y**11)

K = 11
A = sp.series(sp.exp(logA), y, 0, K + 1).removeO()
S = sp.expand(sp.series(A * sp.exp(n * Bser), y, 0, K + 1).removeO())
P11 = sp.expand(S.coeff(y, K))
P11_poly = sp.Poly(P11, n)

unknowns11 = {a7, a8, a9, a10, a11, b8, b9, b10, b11}
coeffs_clean11 = {}
print("=" * 70)
print("P_11(n) coefficients by degree (b7 known; a7,a8,a9,a10,a11,b8,b9,b10,b11 symbolic)")
print("=" * 70)
for p in range(11, -1, -1):
    c = P11_poly.coeff_monomial(n**p) if p > 0 else P11_poly.coeff_monomial(1)
    c = sp.expand(c)
    free_syms = c.free_symbols & unknowns11
    clean = len(free_syms) == 0
    if clean:
        coeffs_clean11[p] = sp.nsimplify(c)
    tag = "CLEAN" if clean else f"depends on {sorted(s.name for s in free_syms)}"
    print(f"  degree n^{p}: {tag}")

print()
print(f"Clean degrees: {sorted(coeffs_clean11, reverse=True)} ({len(coeffs_clean11)} of 12)")
unclean_degrees = sorted(set(range(12)) - set(coeffs_clean11), reverse=True)
print(f"Unclean degrees: {unclean_degrees} ({len(unclean_degrees)} of 12)")

print()
print("Leading-coefficient check (25^11/11! conjecture):")
expected_lead = sp.Rational(25**11, sp.factorial(11))
print(f"  P_11 n^11 coeff = {coeffs_clean11.get(11)}")
print(f"  25^11/11!       = {expected_lead}")
print(f"  match = {coeffs_clean11.get(11) == expected_lead}")

# ---------------------------------------------------------------------------
# How many real, structurally-valid (n >= 2*11+1 = 23) diagonal-11 points
# exist in the already-swept a25 data?
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Real diagonal-11 data available (results/ns_a25/swept_rows.txt)")
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

T11_data = {}
for h, rows in rows_by_h.items():
    nv = h + 11
    if nv in rows:
        T11_data[nv] = rows[nv]

MIN_VALID_N = 2 * 11 + 1
valid_nodes = sorted(nv for nv in T11_data if nv >= MIN_VALID_N)
subthresh_nodes = sorted(nv for nv in T11_data if nv < MIN_VALID_N)
print(f"All diagonal-11 points present: n = {sorted(T11_data)}")
print(f"Structurally valid (n >= {MIN_VALID_N}): n = {valid_nodes}  ({len(valid_nodes)} points)")
print(f"Sub-threshold, unusable for fitting: n = {subthresh_nodes}")

print()
print(f"Unknowns needed to pin P_11's unclean tail: {len(unclean_degrees)}")
print(f"Valid real data points available: {len(valid_nodes)}")
shortfall = len(unclean_degrees) - len(valid_nodes)
if shortfall <= 0:
    print(f"=> Enough real data exists in-hand; no new sweep needed to pin P_11 from a25 data alone.")
    print(f"   ({-shortfall} points would be free for held-out validation.)")
else:
    print(f"=> SHORT by {shortfall} equations if solved from a25 data alone (no extra structure used).")

# ---------------------------------------------------------------------------
# Do the four already-solved P_10 equations (in a7,a8,a9,a10,b8,b9,b10) help
# close the gap? They don't introduce new real data, but they ARE additional
# independent linear constraints on symbols P_11 also depends on -- so a
# *joint* solve of (P_10's 4 equations) + (P_11's unclean-degree equations
# from valid real data) uses fewer NET new numbers than solving P_11 in
# isolation, if the symbol sets overlap.
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Do P_10's already-solved equations help close the P_11 gap?")
print("=" * 70)
p10_unknowns = {a7, a8, a9, a10, b8, b9, b10}
p11_new_symbol = b11 if any(True for _ in [0]) else None
print(f"P_10 fit gave 4 independent linear equations in: {sorted(s.name for s in p10_unknowns)}")
print(f"P_11's unclean degrees introduce how many symbols each:")
for p in unclean_degrees:
    c = sp.expand(P11_poly.coeff_monomial(n**p) if p > 0 else P11_poly.coeff_monomial(1))
    free_syms = c.free_symbols & unknowns11
    overlap = free_syms & p10_unknowns
    new_syms = free_syms - p10_unknowns
    print(f"  n^{p}: symbols={sorted(s.name for s in free_syms)}  "
          f"(overlap w/ P_10 unknowns: {sorted(s.name for s in overlap)}; "
          f"genuinely new: {sorted(s.name for s in new_syms)})")

total_symbols_involved = set()
for p in unclean_degrees:
    c = sp.expand(P11_poly.coeff_monomial(n**p) if p > 0 else P11_poly.coeff_monomial(1))
    total_symbols_involved |= (c.free_symbols & unknowns11)
print()
print(f"Total distinct unknown symbols across P_11's unclean tail: {sorted(s.name for s in total_symbols_involved)} ({len(total_symbols_involved)})")
print(f"Of these, already have 4 independent equations (from P_10) constraining: {sorted(s.name for s in (total_symbols_involved & p10_unknowns))}")
print(f"Net new equations needed = {len(total_symbols_involved)} symbols - 4 (P_10 eqns) = {len(total_symbols_involved) - 4}, "
      f"available valid real diagonal-11 data points = {len(valid_nodes)}")
