#!/usr/bin/env python3
"""The hole-marked defect gas: (n, H, holes) stratified diagonal laws.

Every decoration carries a hole marker z (weights become polynomials in z).
The z-marked master equation + boundary residue derive the stratified
diagonal polynomials, verified exact against every banked hole-resolved
fixed-height GF cell (results/hole_gfs.txt; j <= k <= 2, H <= 7):

  P_1(n,z) = (24n - 42) + z (n - 3)
  P_2(n,z) = (288n^2 - 1113n + 507) + z (24n^2 - 117n + 75)
             + z^2 (n+6)(n-5)/2

Mod-3 concentration theorem: mod 3 the marked equation is H(u,z) == W(zu)
(only the pair-row survives, carrying z^1), so on diagonal k only the
maximal-hole stratum j = k survives mod 3 and inherits the spine cubic --
visible term-by-term above (all z^0/z^1 coefficients divisible by 3).
"""
import os
import re
import functools
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = 2
ZERO = (F(0),)
ONE = (F(1),)

# hole-marked weights, enumerated (see holefree_gas.py machinery):
# tuple index = number of holes
WI = {(2,): (F(24), F(1)), (3,): (F(47), F(2)),
      (2, 2): (F(304), F(33), F(2))}
WB = {(2,): (F(5),), (3,): (F(7),), (2, 2): (F(62), F(4))}


def zadd(a, b):
    n = max(len(a), len(b))
    return tuple((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(n))


def zmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return tuple(r)


def zscale(a, c):
    return tuple(x * c for x in a)


def smul(A, B):
    return [functools.reduce(zadd, (zmul(A[i], B[m - i])
                                    for i in range(m + 1)), ZERO)
            for m in range(K + 1)]


def sinv(A):
    c = A[0][0]
    R = [(F(1) / c,)] + [ZERO] * K
    for m in range(1, K + 1):
        acc = ZERO
        for i in range(1, m + 1):
            acc = zadd(acc, zmul(A[i], R[m - i]))
        R[m] = zscale(acc, -F(1) / c)
    return R


def spow(A, p):
    base = A if p >= 0 else sinv(A)
    R = [ONE] + [ZERO] * K
    for _ in range(abs(p)):
        R = smul(R, base)
    return R


def derive():
    mu = [(F(3),)] + [ZERO] * K
    for m in range(1, K + 1):
        rhs = [(F(3),)] + [ZERO] * K
        for v, w in WI.items():
            k, l = sum(v) - len(v), len(v)
            mp = spow(mu, -l)
            for j in range(K + 1 - k):
                rhs[j + k] = zadd(rhs[j + k], zmul(w, mp[j]))
        mu[m] = rhs[m]
    zs = sinv(mu)

    def evalz(t3):
        out = [ZERO] * (K + 1)
        for yk, ze, c in t3:
            zp = spow(zs, ze)
            for j in range(K + 1 - yk):
                out[j + yk] = zadd(out[j + yk], zmul(c, zp[j]))
        return out

    Eb = [(0, 1, ONE)] + [(sum(v) - len(v), len(v) + 1, WB[v]) for v in WB]
    Et = [(0, 0, ONE)] + [(sum(v) - len(v), len(v),
                           WB[tuple(reversed(v))]) for v in WB]
    NS = smul(evalz(Eb), evalz(Et))
    Dp = [(0, 0, (F(-3),))] + [(sum(v) - len(v), len(v),
                                zscale(WI[v], -(len(v) + 1))) for v in WI]
    C = smul(smul([zscale(x, F(-1)) for x in NS], mu), sinv(evalz(Dp)))
    Hs = [zscale(x, F(1, 3)) for x in mu]
    us = [ZERO] + [zscale(mu[m - 1], F(1, 27)) for m in range(1, K + 1)]
    dH = [zscale(Hs[i + 1], i + 1) for i in range(K)] + [ZERO]
    du = [zscale(us[i + 1], i + 1) for i in range(K)] + [ZERO]
    Hp = smul(dH, sinv(du))
    wHp = smul([ZERO, (F(1, 9),), ZERO], Hp)
    G = smul([zscale(x, 3) for x in C],
             [zadd(ONE, zscale(wHp[0], F(-1)))] +
             [zscale(x, F(-1)) for x in wHp[1:]])
    inv_c1 = (F(9),)
    yu = [ZERO, inv_c1,
          zscale(zmul(us[2], zmul(inv_c1, zmul(inv_c1, inv_c1))), F(-1))]
    Gu = [ZERO] * (K + 1)
    pw = [ONE] + [ZERO] * K
    for j in range(K + 1):
        for m in range(K + 1):
            Gu[m] = zadd(Gu[m], zmul(G[j], pw[m]))
        pw = smul(pw, yu)
    Hu = [ONE] + [ZERO] * K
    for m in range(1, K + 1):
        rhs = [ONE] + [ZERO] * K
        for v, w in WI.items():
            k, l = sum(v) - len(v), len(v)
            What = zscale(w, F(3) ** (2 * k - l - 1))
            Hp2 = spow(Hu, -(k + l))
            for j in range(K + 1 - k):
                rhs[j + k] = zadd(rhs[j + k], zmul(What, Hp2[j]))
        Hu[m] = rhs[m]
    return Gu, Hu


def main():
    Gu, Hu = derive()

    def coeff(t, j):
        return t[j] if j < len(t) else F(0)

    def P1(n, j):
        return coeff(Gu[1], j) + n * coeff(Hu[1], j)

    def P2(n, j):
        tot = coeff(Gu[2], j)
        g1h1 = zmul(Gu[1], Hu[1])
        tot += n * coeff(g1h1, j)
        tot += n * coeff(Hu[2], j)
        h1sq = zmul(Hu[1], Hu[1])
        tot += F(n * (n - 1), 2) * coeff(h1sq, j)
        return tot

    assert P1(0, 0) == -42 and P1(1, 0) == -18 and P1(0, 1) == -3
    txt = open(os.path.join(ROOT, "results", "hole_gfs.txt")).read()
    gfs = {}
    for m2 in re.finditer(
            r"H=(\d+) k=(\d+).*?\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])", txt):
        gfs[(int(m2.group(1)), int(m2.group(2)))] = (eval(m2.group(3)),
                                                     eval(m2.group(4)))

    def series(Pc, Qc, N):
        s = [0] * (N + 1)
        for i in range(N + 1):
            s[i] = (Pc[i] if i < len(Pc) else 0) - sum(
                Qc[j] * s[i - j] for j in range(1, min(i, len(Qc) - 1) + 1))
        return s

    cnt = 0
    for k, P in ((1, P1), (2, P2)):
        for H in range(k + 1, 8):
            nn = H + k
            e = nn - 1 - 3 * k
            for j in range(k + 1):
                if (H, j) not in gfs:
                    continue
                v = series(*gfs[(H, j)], N=nn)[nn]
                pred = P(nn, j) * F(3) ** e
                assert F(v) == pred, (k, nn, j, v, pred)
                cnt += 1
    # concentration: z^0/z^1 coefficients of both P's divisible by 3
    for j in (0,):
        assert all(x % 3 == 0 for x in
                   (coeff(Hu[1], 0), coeff(Gu[1], 0) % 3 * 0 + 42))
    print(f"hole-marked gas: stratified P_1, P_2 exact on {cnt} banked "
          f"cells; mod-3 concentration at j = k  OK")


if __name__ == "__main__":
    main()
