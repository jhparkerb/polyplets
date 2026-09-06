#!/usr/bin/env python3
"""Ternary Spine: the mod-3 structure of the height triangle's diagonal family.

Verifies every link in the chain of results/arithmetic-structure.md:

  Setup (the diagonal cumulant law, empirically exact, holdout-validated k<=17):
    T(n, n-k) = P_k(n) * 3^(n-1-3k)  for n >= 2k+1, with
    sum_k P_k(n) y^k = G(y) * H(y)^n  (cumulants linear in n).

  Proved from the law:  P_k integer-valued (Polya); G, H integer series.
  Ladder (verified here to y^17, conjectural beyond):
    (*a) G == 1 (mod 9)
    (*b) H == W (mod 3),  W the unique root of W^3 = W^2 + t, W(0)=1
    (*c) (H^3 - H(t^3))/3 == t^2 + tW (mod 3)
  Theorems under the ladder (proofs in the .md; verified numerically here):
    digit product   P_k(n) mod 3 = [y^k] prod_i W(y^{3^i})^{n_i}
    odd spine       T(3k+1, 2k+1) == 1 (mod 3)          [Lagrange inversion]
    even spine      P_k(3k) == 3 (mod 9), T(3k,2k) == 1 (mod 3)
    self-similarity P_{3m}(9m) == P_m(3m) (mod 9)
    SNF count       nullity(T_N mod 3) = ceil((N-1)/3)
  Bonus depth (measured):
    H^3 - H^2 == 25t (mod 27);  (H^3-H^2-25t)/27 == t*(W(t^3)-1) (mod 3).

Run: python3 -m experiments.ternary_spine   (needs results/ns_a36/perheight/)
"""
import os, io, types, contextlib
from fractions import Fraction as F
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = 17          # depth of fitted diagonal data (P_k pinned for k <= 17)
KK = 60         # working depth for the cubic root W

ok_all = True
def chk(name, cond):
    global ok_all
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    ok_all &= bool(cond)

# ---- load P_k from the fitted diagonal law --------------------------------
src = open(os.path.join(ROOT, "scripts", "derive_pk_fast.py")).read()
mod = types.ModuleType("dpk")
mod.__dict__.update({'__name__': 'x', '__file__': os.path.join(ROOT, "scripts", "derive_pk_fast.py")})
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "x", "exec"), mod.__dict__)
    P, _ = mod.derive(K)

def peval(poly, n):
    r = F(0)
    for c in reversed(poly):
        r = r * n + c
    return r

# ---- G, H integer series --------------------------------------------------
def sinv(a, KX):
    inv = [0] * (KX + 1); inv[0] = 1
    for m in range(1, KX + 1):
        inv[m] = -sum(a[j] * inv[m - j] for j in range(1, m + 1))
    return inv

def smul(a, b, KX):
    return [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(KX + 1)]

F0 = [peval(P[k], 0) if k else F(1) for k in range(K + 1)]
F1 = [peval(P[k], 1) if k else F(1) for k in range(K + 1)]
chk("P_k(0), P_k(1) all integers (Polya integer-valuedness)",
    all(v.denominator == 1 for v in F0 + F1))
G = [int(v) for v in F0]
H = smul([int(v) for v in F1], sinv(G, K), K)

def v3(x):
    if x == 0:
        return 99
    e = 0; x = abs(x)
    while x % 3 == 0:
        x //= 3; e += 1
    return e

chk("(*a) G == 1 (mod 9): v3(G_j) >= 2 for j=1..17", all(v3(g) >= 2 for g in G[1:]))

# ---- the cubic root W over F3 ---------------------------------------------
def f3mul(a, b, KX):
    return [sum(a[i] * b[m - i] for i in range(m + 1)) % 3 for m in range(KX + 1)]

def f3inv(a, KX):
    inv = [0] * (KX + 1); inv[0] = 1
    for m in range(1, KX + 1):
        inv[m] = (-sum(a[j] * inv[m - j] for j in range(1, m + 1))) % 3
    return inv

def f3pow(a, n, KX):
    r = [1] + [0] * KX; b = a[:]
    while n:
        if n & 1:
            r = f3mul(r, b, KX)
        b = f3mul(b, b, KX); n >>= 1
    return r

x = [0] * (KK + 1)
for _ in range(KK + 2):                     # x = t(1-x)^3 fixed point
    omx = [(1 if i == 0 else (-x[i]) % 3) for i in range(KK + 1)]
    cube = f3mul(f3mul(omx, omx, KK), omx, KK)
    newx = [0] + cube[:KK]
    if newx == x:
        break
    x = newx
W = f3inv([(1 if i == 0 else (-x[i]) % 3) for i in range(KK + 1)], KK)

W2 = f3mul(W, W, KK)
Wt3 = [0] * (KK + 1)
for i, c in enumerate(W):
    if 3 * i <= KK:
        Wt3[3 * i] = c
chk("W satisfies W(t)^2 == W(t^3) - t to t^60",
    all(W2[m] == (Wt3[m] - (1 if m == 1 else 0)) % 3 for m in range(KK + 1)))
chk("(*b) H == W (mod 3), all 18 known coefficients",
    [h % 3 for h in H] == W[:K + 1])

# ---- (*c): S = (H^3 - H(t^3))/3, S mod 3 == t^2 + tW ----------------------
H3 = smul(smul(H, H, K), H, K)
Ht3 = [0] * (K + 1)
for i, c in enumerate(H):
    if 3 * i <= K:
        Ht3[3 * i] = c
S = [(a - b) for a, b in zip(H3, Ht3)]
chk("S = (H^3 - H(t^3))/3 is an integer series", all(s % 3 == 0 for s in S))
Sb = [(s // 3) % 3 for s in S]
target = [0] * (K + 1)
target[2] = 1                                # t^2
for m in range(K):                           # + t*W
    target[m + 1] = (target[m + 1] + W[m]) % 3
chk("(*c) S == t^2 + tW (mod 3), to t^17", Sb == target)

# ---- digit product vs banked triangle (uses only the cubic) ---------------
T = {}
for f in os.listdir(os.path.join(ROOT, "results", "ns_a36", "perheight")):
    if f.startswith('h') and f.endswith('.out'):
        Hh = int(f[1:-4])
        for ln in open(os.path.join(ROOT, "results", "ns_a36", "perheight", f)):
            n, c = ln.split(); T[(int(n), Hh)] = int(c)

def stretch(a, s, KX):
    r = [0] * (KX + 1)
    for i, c in enumerate(a):
        if i * s <= KX:
            r[i * s] = c
    return r

def digit_formula(n, KX):
    r = [1] + [0] * KX; i = 0; m = n
    while m:
        d = m % 3
        if d:
            r = f3mul(r, f3pow(stretch(W, 3 ** i, KX), d, KX), KX)
        m //= 3; i += 1
    return r

checks = fails = 0
for n in range(1, 37):
    df = digit_formula(n, K)
    for k in range(0, min(K, (n - 1) // 2) + 1):
        t = T.get((n, n - k))
        if t is None:
            continue
        Pv = F(t) * F(3) ** (3 * k + 1 - n)
        if Pv.denominator != 1:
            fails += 1; continue
        checks += 1
        if int(Pv) % 3 != df[k]:
            fails += 1
chk(f"digit-product formula == banked triangle mod 3 ({checks} in-regime cells)", fails == 0)

# ---- spine identities (proved; numeric confirmation) -----------------------
chk("odd spine  [t^k] W^(3k+1) == 1, k=0..19 (proved via Lagrange inversion)",
    all(f3pow(W, 3 * k + 1, KK)[k] == 1 for k in range(20)))
chk("odd spine on data: P_k(3k+1) == 1 (mod 3), k=1..17",
    all(int(peval(P[k], 3 * k + 1)) % 3 == 1 for k in range(1, K + 1)))
chk("even spine: P_k(3k) == 3 (mod 9), k=1..17",
    all(int(peval(P[k], 3 * k)) % 9 == 3 for k in range(1, K + 1)))
chk("even spine algebra: k*(C(k,2)+1) == 1 (mod 3) for 3∤k, k<=17",
    all((k * (comb(k, 2) + 1)) % 3 == 1 for k in range(1, K + 1) if k % 3))
chk("mod-9 self-similarity: P_3m(9m) == P_m(3m) (mod 9), m=1..5",
    all(int(peval(P[3 * m], 9 * m)) % 9 == int(peval(P[m], 3 * m)) % 9 for m in range(1, 6)))

# ---- SNF count on the banked matrix ----------------------------------------
import math
def rank_mod3(N):
    M = [[T.get((i + 1, j + 1), 0) % 3 for j in range(N)] for i in range(N)]
    r = 0
    for c in range(N):
        p = next((i for i in range(r, N) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 if M[r][c] == 1 else 2
        M[r] = [(v * inv) % 3 for v in M[r]]
        for i in range(N):
            if i != r and M[i][c]:
                f_ = M[i][c]; M[i] = [(a - f_ * b) % 3 for a, b in zip(M[i], M[r])]
        r += 1
    return r
chk("SNF count: nullity(T_N mod 3) == ceil((N-1)/3), N=2..36",
    all(N - rank_mod3(N) == math.ceil((N - 1) / 3) for N in range(2, 37)))

# ---- bonus depth ------------------------------------------------------------
J = [a - b for a, b in zip(smul(smul(H, H, K), H, K), smul(H, H, K))]
J[1] -= 25
chk("H^3 - H^2 == 25t (mod 27): v3 of residual >= 3", all(v3(c) >= 3 for c in J[1:]))
L = [(c // 27) % 3 for c in J]
lvl3 = [0] * (K + 1)
for i, c in enumerate(Wt3):                   # t*(W(t^3)-1): the i=0 constant of W(t^3)
    if i and i + 1 <= K:                      # is dropped by `if i`
        lvl3[i + 1] = c
chk("(H^3-H^2-25t)/27 == t*(W(t^3)-1) (mod 3)", L == lvl3)

print()
print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAILED")
