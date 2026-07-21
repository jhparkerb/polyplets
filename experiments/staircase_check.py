#!/usr/bin/env python3
"""Numeric validation for the staircase route to Lean grand-form pinning.

The planned Lean proof (polyplets/GRANDFORM-PLAN.md) rests on:

  mu-recursion   d k (H+1) = sum_{i<=k} mu_i * d (k-i) H          (H >= k+1)
  staircase      T(H+1+k, H+1) = sum_{i<=k} mu_i * T(H+k-i, H)    (H >= k+1)
  P-staircase    P_k(n+1) = sum_{i<=k} mu_i * 3^(2i-1) * P_{k-i}(n-i)

with mu_0 = 3 and mu_k solved level-by-level from ONE banked real cell
(T(2k+2, k+2)), the level base being T(2k+1, k+1). This script:

  1. solves mu_1..mu_16 from the staircase exactly as the Lean pinning will;
  2. verifies the staircase at EVERY other real banked instance
     (H <= 18, n+1 <= 36) — the overdetermination check;
  3. cross-checks mu_1..mu_3 against the weight-side fixed point
     mu = 3*eps + sum_l v_l * mu^(*-l) built from the Lean-verified
     aggregated weights V(l,j), j <= 3;
  4. verifies the P-staircase polynomial identity for the production
     polynomials (orchestrator/sweep.go diagCoeffTable) at k+2 points per k
     (> deg, so identity), k <= 16 — the norm_num obligation of the plan;
  5. verifies each level's two banked anchors match production P_k values;
  6. prints the exact mu table for the plan's generator to consume.

All arithmetic exact (Fraction). Run: python3 experiments/staircase_check.py
"""
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMAX = 16

# Lean-verified aggregated weights (Weights.lean, Weights3.lean, heavy build)
V = {(1, 1): 25, (1, 2): 49, (2, 2): 339, (1, 3): 81, (2, 3): 1860,
     (3, 3): 4778}

real = {}
for H in range(1, 20):
    with open(os.path.join(ROOT, f"results/ns_a36/perheight/h{H}.out")) as f:
        for line in f:
            p = line.split()
            if len(p) == 2:
                real[(int(p[0]), H)] = int(p[1])


def T(n, H):
    if n == H:
        return 3 ** (n - 1)          # king chain, proven (T_diag_pow)
    return real[(n, H)]


fails = 0


def check(name, ok):
    global fails
    print(f"  {name}: {'ok' if ok else '*** FAIL ***'}")
    if not ok:
        fails += 1


# ---- 1. solve mu level by level from the pinning cells ----
mu = {0: F(3)}
for k in range(1, KMAX + 1):
    # staircase at H = k+1: T(2k+2, k+2) = sum_i mu_i T(2k+1-i, k+1)
    rhs_known = sum(mu[i] * T(2 * k + 1 - i, k + 1) for i in range(k))
    mu[k] = (F(T(2 * k + 2, k + 2)) - rhs_known) / T(k + 1, k + 1)

# ---- 2. overdetermination: every other real instance ----
total, bad = 0, []
for k in range(0, KMAX + 1):
    for H in range(k + 1, 19):
        if H + 1 + k > 36:
            continue
        lhs = F(T(H + 1 + k, H + 1))
        rhs = sum(mu[i] * T(H + k - i, H) for i in range(k + 1))
        total += 1
        if lhs != rhs:
            bad.append((k, H))
check(f"staircase holds at all {total} real instances (k<=16, H<=18)",
      not bad)
if bad:
    print(f"    first failures: {bad[:5]}")

# sharpness probe: H = k should generically fail (onset content), report only
sharp = sum(1 for k in range(1, KMAX + 1)
            if k + 1 + k <= 36 and k + 1 <= 19 and
            F(T(2 * k + 1, k + 1)) != sum(mu[i] * T(2 * k - i, k)
                                          for i in range(k + 1)))
print(f"  (onset sharpness: staircase FAILS at H=k for {sharp}/{KMAX} "
      f"levels — expected nonzero)")

# ---- 3. weight-side fixed point, j <= 3 ----
nu = {0: F(1, 3)}                     # mu^(-1) coefficients


def conv(a, b, m):
    return sum(a.get(i, F(0)) * b.get(m - i, F(0)) for i in range(m + 1))


def conv_pow(a, e, m):
    r = {0: F(1)}
    for _ in range(e):
        r = {i: conv(r, a, i) for i in range(m + 1)}
    return r


mu_w = {0: F(3)}
for m in range(1, 4):
    acc = F(0)
    for l in range(1, m + 1):
        vl = {j: F(V[(l, j)]) for j in (1, 2, 3) if (l, j) in V and l <= j}
        nupow = conv_pow(nu, l, m)
        acc += conv(vl, nupow, m)
    mu_w[m] = acc
    # extend nu to order m (needs mu up to m: mu*nu = eps)
    nu[m] = -sum(mu_w.get(i, F(0)) * nu[m - i] for i in range(1, m + 1)) / 3
check("mu_1..mu_3 from weights == mu_1..mu_3 from data",
      all(mu_w[m] == mu[m] for m in (1, 2, 3)))

# ---- 4. P-staircase polynomial identity for production P_k ----
src = open(os.path.join(ROOT, "orchestrator/sweep.go")).read()
tbl = {0: ([1], 1)}
for mm in re.finditer(r'\n\t(\d+): \{\[\]string\{([^}]*)\}, (\d+)\}', src):
    k = int(mm.group(1))
    tbl[k] = ([int(x) for x in re.findall(r'"(-?\d+)"', mm.group(2))],
              int(mm.group(3)))


def P(k, n):
    c, kf = tbl[k]
    num = 0
    for co in c:
        num = num * n + co
    return F(num, kf)


ok = True
for k in range(1, KMAX + 1):
    for n in range(0, k + 2):        # k+2 points > deg k => identity
        lhs = P(k, n + 1)
        rhs = sum(mu[i] * F(3) ** (2 * i - 1) * P(k - i, n - i)
                  for i in range(k + 1))
        if lhs != rhs:
            ok = False
check("P-staircase identity for production P_1..P_16 (k+2 pts each)", ok)

# ---- 5. banked anchors match production values ----
ok = True
for k in range(1, KMAX + 1):
    for n in (2 * k + 1, 2 * k + 2):
        e = n - 1 - 3 * k
        want = P(k, n) * (F(3) ** e if e >= 0 else F(1, 3 ** -e))
        if want != T(n, n - k):
            ok = False
check("anchors T(2k+1,k+1), T(2k+2,k+2) == production P_k values", ok)

# ---- 6. exp-form corollary objects (plan module GF-6) ----
# W solves 1 = sum_i m_i y^i W^(i+1) with m_i = mu_i 3^(2i-1); b = -log W;
# a_k solved level-wise from P_k at n = 2k+1. Cross-checked against
# scripts/derive_pk_fast.py's fitted a_k, b_k (spot anchors below).
m = {i: mu[i] * F(3) ** (2 * i - 1) for i in range(KMAX + 1)}
W = {0: F(1)}
for t in range(1, KMAX + 1):
    acc = F(0)
    for i in range(1, t + 1):
        wp = conv_pow(W, i + 1, t - i)
        acc += m[i] * wp.get(t - i, F(0))
    W[t] = -acc
logW = {0: F(0)}
for t in range(1, KMAX + 1):
    logW[t] = W[t] - sum(F(s, t) * logW[s] * W[t - s] for s in range(1, t))
b = {j: -logW[j] for j in range(1, KMAX + 1)}
check("b_1 == 25 (leading-coeff mechanism) and b_2 == -209/2 (deriver)",
      b[1] == 25 and b[2] == F(-209, 2))


def expcoeff(a, b, k, n):
    E = {0: F(1)}
    for t in range(1, k + 1):
        E[t] = sum(F(j, t) * (a.get(j, F(0)) + b.get(j, F(0)) * n) * E[t - j]
                   for j in range(1, t + 1))
    return E[k]


a = {}
for k in range(1, KMAX + 1):
    n0 = 2 * k + 1
    a[k] = F(0)
    a[k] = P(k, n0) - expcoeff(a, b, k, n0)   # a_k enters with coefficient 1
ok = all(expcoeff(a, b, k, n) == P(k, n)
         for k in range(1, KMAX + 1) for n in range(0, k + 2))
check("expCoeff(a,b) == production P_k identically, k <= 16", ok)
check("a_1 == -45; a_16 matches deriver",
      a[1] == -45 and a[16] == F(-48607562060310698638155, 16))
lead_ok = all(b[1] ** k / __import__("math").factorial(k) ==
              (lambda c=tbl[k]: F(c[0][0], c[1]))() for k in range(1, KMAX + 1))
check("leading coeff of P_k == b_1^k/k! == 25^k/k!", lead_ok)

# ---- 7. the mu table ----
print()
print("exact mu_k (for the Lean generator; denominators are powers of 3):")
for k in range(0, KMAX + 1):
    d = mu[k].denominator
    p3 = d == 1 or (d & (d - 1) == 0 and False) or True
    # denominator as power of 3?
    dd, e = d, 0
    while dd % 3 == 0:
        dd //= 3
        e += 1
    tag = f"3^{e}" if dd == 1 else f"NOT a 3-power ({d})"
    print(f"  mu_{k:2d} = {mu[k].numerator}/{tag}" if d > 1
          else f"  mu_{k:2d} = {mu[k].numerator}")

print()
if fails:
    sys.exit(f"{fails} FAILURES")
print("ALL CHECKS PASS")
