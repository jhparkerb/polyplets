#!/usr/bin/env python3
"""The hex diagonal law + dyadic spine -- see results/diagonal-formula.md.

Checks: (1) brute hex enumerator reproduces A001207 (n<=9 here for speed);
(2) hex row-transfer DP (asymmetric touch x' in {x-1,x}) matches brute on
the diagonal band; (3) T(n,n-k) = P_k(n) 2^(n-1-3k) with P_1 = 9n-15 and
quadratic P_2, holdout-exact to H=14; (4) the dyadic spine: P_k mod 2 =
[u^k](1 + uH^-3) H^n with H^3 = H^2 + u over F_2.
"""
from itertools import combinations
from collections import defaultdict, deque
from functools import lru_cache
from fractions import Fraction as F

BUD = 2
M = 3 + 2 * BUD
A001207 = [1, 3, 11, 44, 186, 814, 3652, 16689, 77359]


def hex_neighbors(c):
    x, y = c
    return [(x - 1, y), (x + 1, y), (x, y + 1), (x - 1, y + 1),
            (x, y - 1), (x + 1, y - 1)]


def brute(nmax):
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        return frozenset((x - mx, y - my) for x, y in cells)
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    T = defaultdict(int)
    T[(1, 1)] = 1
    tot = {1: 1}
    while frontier:
        new = []
        for A in frontier:
            if len(A) >= nmax:
                continue
            cand = set()
            for c in A:
                for nb in hex_neighbors(c):
                    if nb not in A:
                        cand.add(nb)
            for c in cand:
                B = canon(set(A) | {c})
                if B not in seen:
                    seen.add(B)
                    new.append(B)
        frontier = new
        if new:
            n = len(new[0])
            tot[n] = len(new)
            for A in new:
                H = max(y for _, y in A) - min(y for _, y in A) + 1
                T[(n, H)] += 1
    return tot, T


def rowpart(cells):
    lab = list(range(len(cells)))
    for i in range(len(cells) - 1):
        if cells[i + 1] - cells[i] == 1:
            lab[i + 1] = lab[i]
    cmap = {}
    out = []
    for x in lab:
        if x not in cmap:
            cmap[x] = len(cmap)
        out.append(cmap[x])
    return tuple(out)


@lru_cache(maxsize=None)
def shape_transitions(cells, part):
    spread = cells[-1]
    nb = len(set(part))
    out = []
    for s in range(1, BUD + 2):
        for T in combinations(range(-M, spread + M + 1), s):
            lab = list(range(nb + s))

            def find(x):
                while lab[x] != x:
                    lab[x] = lab[lab[x]]
                    x = lab[x]
                return x

            def uni(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    lab[ra] = rb

            touched = [False] * nb
            for j, t in enumerate(T):
                for i, c in enumerate(cells):
                    if t == c or t == c - 1:      # hex touch-up
                        uni(part[i], nb + j)
                        touched[part[i]] = True
            for j in range(s - 1):
                if T[j + 1] - T[j] == 1:
                    uni(nb + j, nb + j + 1)
            if not all(touched[b] for b in set(part)):
                continue
            roots = [find(nb + j) for j in range(s)]
            cmap = {}
            npart = []
            for r in roots:
                if r not in cmap:
                    cmap[r] = len(cmap)
                npart.append(cmap[r])
            shift = T[0]
            out.append((tuple(t - shift for t in T), tuple(npart), s - 1))
    return out


def hex_T(H):
    dp = defaultdict(int)
    for s in range(1, BUD + 2):
        for rest in combinations(range(1, M + 1), s - 1):
            cells = (0,) + rest
            dp[(cells, rowpart(cells), s - 1)] += 1
    for _ in range(H - 1):
        ndp = defaultdict(int)
        for (cells, part, sur), v in dp.items():
            for (nc, np_, ds) in shape_transitions(cells, part):
                if sur + ds <= BUD:
                    ndp[(nc, np_, sur + ds)] += v
        dp = ndp
    out = defaultdict(int)
    for (cells, part, sur), v in dp.items():
        if len(set(part)) == 1:
            out[H + sur] += v
    return out


def nf(v, e):
    return F(v, 2 ** e) if e >= 0 else F(v * 2 ** (-e))


def main():
    tot, TB = brute(9)
    assert [tot[n] for n in sorted(tot)] == A001207, tot
    vals = {}
    for H in range(1, 15):
        vals[H] = hex_T(H)
        for k in range(BUD + 1):
            n = H + k
            if (n, H) in TB:
                assert vals[H][n] == TB[(n, H)], (n, H)
    print("hex brute == A001207; row DP == brute on the band  OK")
    for k in (1, 2):
        pts = [(H + k, nf(vals[H][H + k], H + k - 1 - 3 * k))
               for H in range(k + 1, 15)]
        fit = pts[:k + 1]

        def lag(x):
            t = F(0)
            for i, (xi, yi) in enumerate(fit):
                w = yi
                for j, (xj, _) in enumerate(fit):
                    if j != i:
                        w *= F(x - xj, xi - xj)
                t += w
            return t
        assert all(lag(x) == y for x, y in pts), k
        if k == 1:
            assert all(lag(n) == 9 * n - 15 for n in range(3, 20))
    print("hex diagonal law: P_1 = 9n-15, P_2 quadratic, "
          "exponent 2^(n-1-3k), holdout-exact H<=14  OK")
    KX = 40
    W = [1] + [0] * KX
    for _ in range(KX + 2):
        inv = [1] + [0] * KX
        for m in range(1, KX + 1):
            inv[m] = (-sum(W[i] * inv[m - i] for i in range(1, m + 1))) % 2
        i2 = [sum(inv[i] * inv[m - i] for i in range(m + 1)) % 2
              for m in range(KX + 1)]
        Wn = [1] + [i2[m - 1] for m in range(1, KX + 1)]
        if Wn == W:
            break
        W = Wn

    def xmul2(a, b):
        return [sum(a[i] * b[m - i] for i in range(m + 1)) % 2
                for m in range(KX + 1)]

    def xpow2(a, p):
        r = [1] + [0] * KX
        base = a[:]
        while p:
            if p & 1:
                r = xmul2(r, base)
            base = xmul2(base, base)
            p >>= 1
        return r

    W2 = xmul2(W, W)
    W3 = xmul2(W2, W)
    assert all((W3[m] - W2[m] - (1 if m == 1 else 0)) % 2 == 0
               for m in range(KX + 1)), "cubic"
    for k in (1, 2):
        for H in range(k + 1, 15):
            n = H + k
            pred = (xpow2(W, n)[k] + xpow2(W, n - 3)[k - 1]) % 2
            Pk = nf(vals[H][n], n - 1 - 3 * k)
            if Pk.denominator == 1:
                assert Pk.numerator % 2 == pred, (k, n)
    print("dyadic spine: H^3 = H^2 + u over F_2, G = 1 + uH^-3, "
          "all in-band cells  OK")


if __name__ == "__main__":
    main()
