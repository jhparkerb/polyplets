#!/usr/bin/env python3
"""Size up P_12 and P_13, given everything pinned so far (b7 only, today's
state) versus everything that becomes pinned automatically once P_11 fully
closes (a7,a8,a9,a10,a11,b8,b9,b10,b11 -- expected as a free byproduct of
computing a26 and a27 for real, see derive_p11_sizing.py / a26-a30-diagonal-plan.md).

Does NOT claim to derive P_12/P_13 -- sizes the gap in both scenarios, and
checks how many structurally-valid real diagonal-12/13 points would be
needed vs. available from swept_rows.txt (or from a26/a27/a28's own sweeps).

Uses the standard exp-of-power-series recurrence (k*g_k = sum_j j*c_j*g_{k-j})
instead of sympy's series()/O() machinery, which is far faster for symbolic
coefficients with many unknowns.
"""
from fractions import Fraction as F
import re
import sympy as sp

n = sp.symbols("n")
a_syms = sp.symbols("a7 a8 a9 a10 a11 a12 a13")
b_syms = sp.symbols("b8 b9 b10 b11 b12 b13")
a7, a8, a9, a10, a11, a12, a13 = a_syms
b8, b9, b10, b11, b12, b13 = b_syms

a_known = {1: F(-45), 2: F(-891, 2), 3: F(-10350), 4: F(-846963, 4), 5: F(-3781134), 6: F(-119091015)}
b_known = {1: F(25), 2: F(-209, 2), 3: F(4474, 3), 4: F(-22701, 4), 5: F(16144), 6: F(15126941, 3)}
b7_val = sp.Rational(-687296991, 7)  # recovered in derive_p10.py Stage 0, no new data


def rat(f):
    return sp.Rational(f.numerator, f.denominator)


def series_coeffs(K, symbolic_a=True, symbolic_b=True, known_subs=None):
    """Return (a_coef, b_coef) dicts: a_coef[j] for j=1..K, b_coef[j] for j=1..K."""
    a_coef = dict(a_known)
    b_coef = dict(b_known)
    b_coef[7] = b7_val
    for j in range(7, K + 1):
        a_coef[j] = a_syms[j - 7]
    for j in range(8, K + 1):
        b_coef[j] = b_syms[j - 8]
    if known_subs:
        a_coef = {j: sp.expand(sp.sympify(v).subs(known_subs)) for j, v in a_coef.items()}
        b_coef = {j: sp.expand(sp.sympify(v).subs(known_subs)) for j, v in b_coef.items()}
    return a_coef, b_coef


def exp_series(c_coef, K):
    """g = exp(f), f = sum_{k=1}^K c_coef[k] y^k. Returns g_coef dict 0..K."""
    g = {0: sp.Integer(1)}
    for k in range(1, K + 1):
        s = sp.Integer(0)
        for j in range(1, k + 1):
            cj = c_coef.get(j, 0)
            if cj == 0:
                continue
            s += j * cj * g[k - j]
        g[k] = sp.expand(s / k)
    return g


def poly_mul_trunc(f, g, K):
    """f,g: dict degree->coef, truncate to degree K."""
    h = {}
    for i, fi in f.items():
        if fi == 0 or i > K:
            continue
        for j, gj in g.items():
            if gj == 0 or i + j > K:
                continue
            h[i + j] = h.get(i + j, 0) + fi * gj
    return {k: sp.expand(v) for k, v in h.items()}


def build_P(K, known_subs=None):
    a_coef, b_coef = series_coeffs(K, known_subs=known_subs)
    A = exp_series(a_coef, K)  # A(y) = exp(sum a_j y^j)
    # exp(n*B(y)): treat as exp of series with coefficients n*b_coef[j]
    nb_coef = {j: n * v for j, v in b_coef.items()}
    EnB = exp_series(nb_coef, K)
    S = poly_mul_trunc(A, EnB, K)
    PK = sp.expand(S[K])
    return sp.Poly(PK, n)


allsyms = set(a_syms) | set(b_syms)


def load_rows():
    rows_by_h, cur_h = {}, None
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
    return rows_by_h


rows_by_h = load_rows()


def valid_points(k):
    thresh = 2 * k + 1
    pts = sorted(h + k for h, rows in rows_by_h.items() if (h + k) in rows)
    return thresh, [p for p in pts if p >= thresh], [p for p in pts if p < thresh]


def report(K, P, label):
    unclean = []
    for p in range(K, -1, -1):
        c = P.coeff_monomial(n**p) if p > 0 else P.coeff_monomial(1)
        free = c.free_symbols & allsyms
        if free:
            unclean.append((p, sorted(s.name for s in free)))
    total_syms = sorted(set(s for _, fr in unclean for s in fr))
    thresh, valid, sub = valid_points(K)
    print(f"\n{label}: P_{K}")
    print(f"  clean degrees: {K+1 - len(unclean)} of {K+1}")
    print(f"  unclean degrees: {[p for p,_ in unclean]}")
    print(f"  distinct new unknown symbols required: {total_syms}  ({len(total_syms)})")
    print(f"  validity threshold n>={thresh}; real data in hand: valid={valid} sub-threshold(unusable)={sub}")
    shortfall = len(total_syms) - len(valid)
    if shortfall <= 0:
        print(f"  => already have enough valid real data in hand ({-shortfall} spare for holdout)")
    else:
        print(f"  => SHORT by {shortfall} equations/points beyond what's in hand today")
    return total_syms, valid


print("=" * 72)
print("SCENARIO A: today's state (only b7 known; a7-a11,b8-b11 still symbolic)")
print("=" * 72)
for K in (12, 13):
    report(K, build_P(K), "today")

print()
print("=" * 72)
print("SCENARIO B: post-P11-solve state (a7,a8,a9,a10,a11,b8,b9,b10,b11 all")
print("numeric -- expected free once a26+a27 land and P_11 fully closes)")
print("=" * 72)
dummy = {a7: F(1), a8: F(2), a9: F(3), a10: F(4), a11: F(5), b8: F(6), b9: F(7), b10: F(8), b11: F(9)}
for K in (12, 13):
    report(K, build_P(K, known_subs=dummy), "post-P11")
