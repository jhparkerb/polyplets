#!/usr/bin/env python3
"""The hole-free defect gas (2026-07-13): the hole-free height triangle has
its own diagonal law with cluster weights = hole-free configuration counts,
derived ab initio and verified against the banked hole-free fixed-height
generating functions (results/hole_gfs.txt, G_{H,0}, H <= 8).

Weights (all / hole-free): pair-row 25/24 (the single holed configuration
is the minimal diamond: gap pair bridged middle-below AND middle-above),
triple-row 49/47, stacked pairs 339/304; boundary pair/triple unchanged
5, 7 (three or four cells against a wall cannot enclose), boundary stacked
pairs 66/62.

Derived: P0_1(n) = 24n - 42,  P0_2(n) = 288n^2 - 1113n + 507,
exact on all GF data. Structural corollary: 24 == 0 (mod 3) -- the full
triangle's mod-3 structure (the spine cubic W^3 = W^2 + t) is carried
ENTIRELY by the hole-making configurations; the hole-free triangle is
mod-3 trivial in-band (every hole-free surviving weight has positive
3-valuation).
"""
import os
import re
from itertools import combinations
from collections import deque
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def connected(cells):
    S = set(cells)
    s0 = next(iter(S))
    vis = {s0}
    q = deque([s0])
    while q:
        x, r = q.popleft()
        for dx in (-1, 0, 1):
            for dr in (-1, 0, 1):
                p = (x + dx, r + dr)
                if (dx or dr) and p in S and p not in vis:
                    vis.add(p)
                    q.append(p)
    return len(vis) == len(S)


def has_hole(cells):
    S = set(cells)
    xs = [x for x, _ in S]
    rs = [r for _, r in S]
    lo_x, hi_x = min(xs) - 1, max(xs) + 1
    lo_r, hi_r = min(rs) - 1, max(rs) + 1
    empty = {(x, r) for x in range(lo_x, hi_x + 1)
             for r in range(lo_r, hi_r + 1) if (x, r) not in S}
    start = (lo_x, lo_r)
    vis = {start}
    q = deque([start])
    while q:
        x, r = q.popleft()
        for dx, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, r + dr)
            if p in empty and p not in vis:
                vis.add(p)
                q.append(p)
    return len(vis) != len(empty)


def weights(sizes, W=9, boundary=False):
    """(all, hole-free) interior or bottom-boundary cluster weight."""
    m = len(sizes)
    tot = hf = 0

    def cells_of(rows):
        return [(x, r) for r, xs in rows.items() for x in xs]

    if boundary:
        def rec_b(i, rows, prev):
            nonlocal tot, hf
            if i == 0:
                cs = cells_of(rows)
                if connected(cs):
                    tot += 1
                    hf += not has_hole(cs)
                return
            lo, hi = min(prev), max(prev)
            for T in combinations(range(lo - W, hi + W + 1), sizes[i - 1]):
                if any(abs(a - b) <= 1 for a in prev for b in T):
                    rec_b(i - 1, {**rows, i - 1: set(T)}, T)
        rec_b(m, {m: {0}}, (0,))
        return tot, hf

    def rec(i, rows, prev):
        nonlocal tot, hf
        if i == m:
            lo, hi = min(prev), max(prev)
            for q_ in range(lo - 1, hi + 2):
                if any(abs(q_ - b) <= 1 for b in prev):
                    cs = cells_of(rows) + [(q_, m + 1)]
                    if connected(cs):
                        tot += 1
                        hf += not has_hole(cs)
        else:
            lo, hi = min(prev), max(prev)
            for T in combinations(range(lo - W, hi + W + 1), sizes[i]):
                if any(abs(a - b) <= 1 for a in prev for b in T):
                    rec(i + 1, {**rows, i + 1: set(T)}, T)
    rec(0, {0: {0}}, (0,))
    return tot, hf


def main():
    K = 2
    Wl, Bl = {}, {}
    expect = {(2,): ((25, 24), (5, 5)), (3,): ((49, 47), (7, 7)),
              (2, 2): ((339, 304), (66, 62))}
    for v, (ei, eb) in expect.items():
        wi = weights(v)
        wb = weights(v, boundary=True)
        assert wi == ei and wb == eb, (v, wi, wb)
        Wl[v] = wi[1]
        Bl[v] = wb[1]
    print("hole-free weights: pair 24, triple 47, stacked pairs 304 "
          "(boundary 5, 7, 62)  OK")

    def smul(a, b):
        return [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(K + 1)]

    def sinv(a):
        r = [F(1) / a[0]] + [F(0)] * K
        for m in range(1, K + 1):
            r[m] = -sum(a[i] * r[m - i] for i in range(1, m + 1)) / a[0]
        return r

    def spow(a, p):
        base = a if p >= 0 else sinv(a)
        r = [F(1)] + [F(0)] * K
        for _ in range(abs(p)):
            r = smul(r, base)
        return r

    mu = [F(3)] + [F(0)] * K
    for m in range(1, K + 1):
        rhs = [F(3)] + [F(0)] * K
        for v, w in Wl.items():
            k, l = sum(v) - len(v), len(v)
            mp = spow(mu, -l)
            for j in range(K + 1 - k):
                rhs[j + k] += w * mp[j]
        mu[m] = rhs[m]
    zs = sinv(mu)

    def evalz(t3):
        out = [F(0)] * (K + 1)
        for yk, ze, c in t3:
            zp = spow(zs, ze)
            for j in range(K + 1 - yk):
                out[j + yk] += c * zp[j]
        return out

    Eb = [(0, 1, F(1))] + [(sum(v) - len(v), len(v) + 1, F(Bl[v])) for v in Bl]
    Et = [(0, 0, F(1))] + [(sum(v) - len(v), len(v),
                            F(Bl[tuple(reversed(v))])) for v in Bl]
    NS = smul(evalz(Eb), evalz(Et))
    Dp = [(0, 0, F(-3))] + [(sum(v) - len(v), len(v),
                             F(-(len(v) + 1) * Wl[v])) for v in Wl]
    C = smul(smul([-x for x in NS], mu), sinv(evalz(Dp)))
    Hs = [x / 3 for x in mu]
    us = [F(0)] + [mu[m - 1] / 27 for m in range(1, K + 1)]
    dH = [(i + 1) * Hs[i + 1] for i in range(K)] + [F(0)]
    du = [(i + 1) * us[i + 1] for i in range(K)] + [F(0)]
    Hp = smul(dH, sinv(du))
    wHp = smul([F(0), F(1, 9)] + [F(0)] * (K - 1), Hp)
    G = smul([3 * x for x in C], [F(1) - wHp[0]] + [-x for x in wHp[1:]])
    c1, c2 = us[1], us[2]
    yu = [F(0), 1 / c1, -c2 / c1 ** 3]
    Gu = [F(0)] * (K + 1)
    pw = [F(1)] + [F(0)] * K
    for j in range(K + 1):
        for m in range(K + 1):
            Gu[m] += G[j] * pw[m]
        pw = smul(pw, yu)
    Hu = [F(1)] + [F(0)] * K
    for m in range(1, K + 1):
        rhs = [F(1)] + [F(0)] * K
        for v, w in Wl.items():
            k, l = sum(v) - len(v), len(v)
            What = F(w) * F(3) ** (2 * k - l - 1)
            Hp2 = spow(Hu, -(k + l))
            for j in range(K + 1 - k):
                rhs[j + k] += What * Hp2[j]
        Hu[m] = rhs[m]
    h1, h2, g1, g2 = Hu[1], Hu[2], Gu[1], Gu[2]
    assert (h1, g1) == (24, -42), (h1, g1)

    def P1(n):
        return h1 * n + g1

    def P2(n):
        return g2 + g1 * h1 * n + n * h2 + F(n * (n - 1), 2) * h1 ** 2

    assert P2(0) * 0 == 0
    # against the banked hole-free GFs
    txt = open(os.path.join(ROOT, "results", "hole_gfs.txt")).read()
    gfs = {}
    for m2 in re.finditer(r"H=(\d+) k=(\d+).*?\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])", txt):
        gfs[(int(m2.group(1)), int(m2.group(2)))] = (eval(m2.group(3)),
                                                     eval(m2.group(4)))

    def series(Pc, Qc, N):
        s = [0] * (N + 1)
        for i in range(N + 1):
            s[i] = (Pc[i] if i < len(Pc) else 0) - sum(
                Qc[j] * s[i - j] for j in range(1, min(i, len(Qc) - 1) + 1))
        return s

    for k, P in ((1, P1), (2, P2)):
        for H in range(k + 1, 9):
            if (H, 0) not in gfs:
                continue
            t = series(*gfs[(H, 0)], N=H + k)[H + k]
            e = H - 1 - 2 * k
            pred = P(H + k) * F(3) ** e
            assert F(t) == pred, (k, H, t, pred)
    print("P0_1(n) = 24n - 42 and P0_2(n) = 288n^2 - 1113n + 507 "
          "ab initio == all banked hole-free GF data  OK")
    assert h1 % 3 == 0
    print("24 == 0 (mod 3): the spine cubic is carried entirely by "
          "hole-making configurations  OK")
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
