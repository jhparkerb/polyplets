#!/usr/bin/env python3
"""The defect-gas row model: mechanism of the diagonal cumulant law.

Read a height-H king animal row by row: the k=0 stratum is a drift walk
(3^(H-1)); a diagonal-k animal is the walk plus k surplus cells organized into
defect clusters. This script:

 1. implements the ROW-TRANSFER DP (independent third enumeration algorithm:
    states = row contents + connectivity partitions, surplus-budgeted) and
    validates it against the banked triangle: T(H+k,H), k<=2, H<=10 EXACT;
 2. classifies k=2 animals by defect geometry and extracts the interior
    cluster weights by exact polynomial fits (holdout-checked):
       single pair row        w = 25  = 16 + 9   (adjacent-pair + gap-pair;
                                                  the paper's "25 species")
       triple row             w = 441 = 21^2
       adjacent pair-pair     w = 1017 = 9*113   (true interaction)
       pairs at separation 1  w = 625 = 25^2     (EXACT factorization!)
       separated pairs        ideal gas, (25^2/2) H^2 leading term
 3. verifies the ledger sums EXACTLY to P_2(H+2) -- i.e. the cumulant law's
    k<=2 content is fully explained as a 1D defect gas with short-range
    interactions. Linear-in-n cumulants = extensivity of cluster weights;
    the exponential form = independent-cluster gas.

Run: python3 -m experiments.defect_gas   (needs results/ns_a36/perheight/)
"""
from fractions import Fraction as F
from itertools import combinations
import os

K = 2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def row_blocks(cells):
    cells = sorted(cells); out = []; cur = [cells[0]]
    for c in cells[1:]:
        if c == cur[-1] + 1: cur.append(c)
        else: out.append(tuple(cur)); cur = [c]
    out.append(tuple(cur)); return out


def canon(cells, part):
    m = min(cells)
    return (tuple(c - m for c in cells),
            tuple(sorted(tuple(sorted(x - m for x in b)) for b in part)))


def next_rows(state, budget):
    cells, part = state
    lo, hi = min(cells), max(cells)
    res = {}
    M = 3 + 2 * budget          # generous reach: pending blocks cost future surplus,
    for s in range(1, budget + 2):   # and gaps may be bridged by cells ALREADY below
        sur = s - 1
        if sur > budget: continue
        W = M
        for nxt in combinations(range(lo - W, hi + W + 1), s):
            touch = lambda c, n: abs(c - n) <= 1
            if not any(touch(c, n) for c in cells for n in nxt): continue
            if any(not any(touch(c, n) for c in b for n in nxt) for b in part): continue
            parent = {n: n for n in nxt}
            def find(x):
                while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
                return x
            def union(a, b):
                ra, rb = find(a), find(b)
                if ra != rb: parent[ra] = rb
            for i in range(len(nxt) - 1):
                if nxt[i + 1] == nxt[i] + 1: union(nxt[i], nxt[i + 1])
            for b in part:
                t = [n for n in nxt if any(touch(c, n) for c in b)]
                for i in range(len(t) - 1): union(t[i], t[i + 1])
            grp = {}
            for n in nxt: grp.setdefault(find(n), []).append(n)
            ns = canon(nxt, tuple(sorted(tuple(sorted(v)) for v in grp.values())))
            res[(ns, sur)] = res.get((ns, sur), 0) + 1
    return res


def initial_states():
    out = {}; seen = set()
    for s in range(1, K + 2):
        for cells in combinations(range(0, 4 * (K + 1)), s):
            if min(cells) != 0: continue
            st = canon(cells, tuple(row_blocks(cells)))
            if st in seen: continue
            seen.add(st)
            out[(st, s - 1)] = 1
    return out


def T_row_model(H):
    dp = initial_states()
    for _ in range(H - 1):
        ndp = {}
        for (st, used), cnt in dp.items():
            for (ns, sur), mult in next_rows(st, K - used).items():
                ndp[(ns, used + sur)] = ndp.get((ns, used + sur), 0) + cnt * mult
        dp = ndp
    out = [0] * (K + 1)
    for (st, used), cnt in dp.items():
        if len(st[1]) == 1: out[used] += cnt
    return out


def T_classified(H):
    dp = {}
    for (st, sur), _ in initial_states().items():
        cls = () if sur == 0 else (('2',) if sur == 1 else (('3',) if sur == 2 else None))
        dp[(st, sur, cls, 0 if sur else 2)] = dp.get((st, sur, cls, 0 if sur else 2), 0) + 1
    for _ in range(H - 1):
        ndp = {}
        for (st, used, cls, dist), cnt in dp.items():
            for (ns, sur), mult in next_rows(st, K - used).items():
                if sur == 0: ncls, ndist = cls, min(dist + 1, 2)
                elif sur == 1:
                    if cls == (): ncls, ndist = ('2',), 0
                    elif cls == ('2',): ncls, ndist = ('2', '2', min(dist, 2)), 0
                    else: continue
                else:
                    if cls == (): ncls, ndist = ('3',), 0
                    else: continue
                key = (ns, used + sur, ncls, ndist)
                ndp[key] = ndp.get(key, 0) + cnt * mult
        dp = ndp
    out = {}
    for (st, used, cls, dist), cnt in dp.items():
        if len(st[1]) == 1 and used == K:
            out[cls] = out.get(cls, 0) + cnt
    return out


def fitpoly(vals, Hs, deg):
    n = deg + 1
    M = [[F(Hs[i]) ** j for j in range(n)] + [vals[i]] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f2 = M[r][c]; M[r] = [a - f2 * b for a, b in zip(M[r], M[c])]
    coef = [M[i][n] for i in range(n)]
    ok = all(sum(coef[j] * F(h) ** j for j in range(n)) == vals[i]
             for i, h in enumerate(Hs) if i >= n)
    return coef, ok


def main():
    Tb = {}
    for f in os.listdir(os.path.join(ROOT, "results", "ns_a36", "perheight")):
        if f.startswith('h') and f.endswith('.out'):
            Hc = int(f[1:-4])
            for ln in open(os.path.join(ROOT, "results", "ns_a36", "perheight", f)):
                n, c = ln.split(); Tb[(int(n), Hc)] = int(c)
    ok = all(T_row_model(H) == [Tb.get((H + k, H), 0) for k in range(K + 1)]
             for H in range(1, 11))
    print("row model == banked triangle (H<=10, k<=2):", ok)

    Hs = list(range(4, 11))
    data = {H: T_classified(H) for H in Hs}
    classes = sorted({c for d in data.values() for c in d})
    total = [F(0)] * 3
    for c in classes:
        vals = [F(data[H].get(c, 0)) * F(3) ** (5 - H) for H in Hs]
        deg = 2 if (len(c) == 3 and c[2] == 2) else 1
        coef, hold = fitpoly(vals, Hs, deg)
        for j, x in enumerate(coef): total[j] += x
        print(f"  {str(c):18s}: {[str(x) for x in coef]}  holdout={hold}")
    # P2(H+2) reconstruction: P2(n) = (a2+b2 n) + (a1+b1 n)^2/2
    a1, b1, a2, b2 = F(-45), F(25), F(-891, 2), F(-209, 2)
    def P2(n): return (a2 + b2 * n) + (a1 + b1 * n) ** 2 / 2
    lhs = [sum(total[j] * F(H) ** j for j in range(3)) for H in Hs]
    rhs = [P2(H + 2) for H in Hs]
    print("ledger sum == P_2(H+2) exactly:", lhs == rhs)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# THEOREM (single-row cluster weights): the interior weight of an s-cell
# single-row cluster is (2s+1)^2, for all s >= 2.  PROOF: gaps of width 2 must
# be bridged by the below-contact p or the above-contact q at the gap middle
# (wider gaps need surplus cells, excluded at this weight); one cell bridges at
# most one gap, so a row with j wide gaps contributes
#   j=0: (s+2)^2      j=1: 2(s+3)-1      j=2: 2      j>=3: 0
# and  (s+2)^2 + (s-1)(2s+5) + C(s-1,2)*2 = 4s^2+4s+1 = (2s+1)^2.  QED
# (25 = 16+9 is the s=2 case; 49 = 25+11+11+2 the s=3 case.)
# ---------------------------------------------------------------------------
def single_row_weight(s):
    import itertools as it
    def blocks(cells):
        cells = sorted(cells); out = []; cur = [cells[0]]
        for c in cells[1:]:
            if c == cur[-1] + 1: cur.append(c)
            else: out.append(tuple(cur)); cur = [c]
        out.append(tuple(cur)); return out
    touch = lambda c, n: abs(c - n) <= 1
    total = 0
    for gaps in it.product((1, 2), repeat=s - 1):
        T = [0]
        for g in gaps: T.append(T[-1] + g)
        B = blocks(T)
        for p in range(-2, T[-1] + 3):
            if not any(touch(t, p) for t in T): continue
            for q in range(-2, T[-1] + 3):
                if not any(touch(t, q) for t in T): continue
                par = list(range(len(B)))
                def find(x):
                    while par[x] != x: par[x] = par[par[x]]; x = par[x]
                    return x
                def uni(a, b):
                    ra, rb = find(a), find(b)
                    if ra != rb: par[ra] = rb
                for ext in (p, q):
                    tb = [i for i, b in enumerate(B) if any(touch(c, ext) for c in b)]
                    for i in range(len(tb) - 1): uni(tb[i], tb[i + 1])
                if len({find(i) for i in range(len(B))}) == 1: total += 1
    return total


# ---------------------------------------------------------------------------
# THE MASTER EQUATION (2026-07-12).  General cluster weight: an l-row cluster
# of row sizes (s_1..s_l), all s_i >= 2, surplus k = sum(s_i) - l, counted with
# a fixed single-cell contact row p below and a free single-cell contact row q
# above.  The renewal chain (drift step weight 3z, cluster macro-step weight
# W_c y^k z^{l+1}) gives per-row growth mu(y): 1 = 3z + sum W_c y^k z^{l+1} at
# z = 1/mu, i.e. mu = 3 + sum_c W_c y^{k_c} mu^{-l_c}.  Substituting the
# diagonal Lagrange parametrization mu = 3*H(u), u = y*mu/27 yields
#
#     H(u) = 1 + sum_c  What_c u^{k_c} H^{-(k_c + l_c)},
#     What_c = W_c * 3^{2 k_c - l_c - 1}.
#
# Verified EXACT through order u^3 against h = (25, 208, 1483) using the
# enumerated weights below (h2 = -2*25^2 + 441 + 1017 = 208 on the nose).
#
# VALUATION LEMMA: every cluster row carries >= 1 surplus, so k >= l and
# v3(What) = 2k - l - 1 + v3(W) >= k - 1, which is >= 1 for every cluster
# except the bare pair-row (k = l = 1, What = 25).  Hence mod 3 the master
# equation collapses to H = 1 + u/H^2, i.e.  H^3 = H^2 + u  -- THE SPINE
# CUBIC, DERIVED.  Mod 9: 441 + 1017 = 1458 == 0, so H^3 = H^2 + 25u == H^2 +
# 7u.  Mod 27 the equation is FINITE (all k >= 4 clusters die: v3 >= k-1 >= 3):
#     H = 1 + 25 u H^-2 + 441 u^2 H^-3 + 1017 u^2 H^-4 + 43002 u^3 H^-6
# with 43002 = 9 * W(2,2,2) = 9 * 4778 -- verified against ALL 18 known
# coefficients of H (checked in check_master()).
#
# WINDOW WARNING (third instance of the same bug class): cluster enumeration
# windows must be generous; W = 6 clipped W(2,2,2) to 4776 (off by 2), caught
# because the master equation then gave h3 = 1465 != 1483.
# ---------------------------------------------------------------------------
def cluster_weight(sizes, W=9):
    """Interior weight of a cluster with given row sizes: rows p/T1..Tm/q,
    p = {0} fixed, q free; count connected configurations."""
    from itertools import combinations
    from collections import deque

    def connected(rows):
        allc = [(x, r) for r, xs in rows.items() for x in xs]
        S = set(allc); seen = {allc[0]}; dq = deque([allc[0]])
        while dq:
            x, r = dq.popleft()
            for dx in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    pt = (x + dx, r + dr)
                    if (dx or dr) and pt in S and pt not in seen:
                        seen.add(pt); dq.append(pt)
        return len(seen) == len(S)

    m = len(sizes); total = 0

    def rec(i, rows, prev):
        nonlocal total
        if i == m:
            lo, hi = min(prev), max(prev)
            for q in range(lo - 1, hi + 2):
                if any(abs(q - b) <= 1 for b in prev):
                    if connected({**rows, m + 1: {q}}):
                        total += 1
            return
        lo, hi = min(prev), max(prev)
        for T in combinations(range(lo - W, hi + W + 1), sizes[i]):
            if not any(abs(a - b) <= 1 for a in prev for b in T):
                continue
            rec(i + 1, {**rows, i + 1: set(T)}, T)

    rec(0, {0: {0}}, (0,))
    return total


def check_master():
    """Verify the master equation: exactly to u^3, and mod 27 to u^17."""
    from fractions import Fraction as F

    weights = {(2,): 25, (3,): 49, (4,): 81,
               (2, 2): cluster_weight((2, 2)),      # 339
               (2, 3): cluster_weight((2, 3)),      # 930
               (3, 2): cluster_weight((3, 2)),      # 930
               (2, 2, 2): cluster_weight((2, 2, 2))}  # 4778
    assert weights[(2, 2)] == 339 and weights[(2, 3)] == 930
    assert weights[(3, 2)] == 930 and weights[(2, 2, 2)] == 4778
    hat = []
    for sizes, w in weights.items():
        l = len(sizes); k = sum(sizes) - l
        hat.append((F(w) * F(3) ** (2 * k - l - 1), k, l))

    K = 3

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

    H = [F(1)] + [F(0)] * K
    for _ in range(8):
        rhs = [F(1)] + [F(0)] * K
        for What, k, l in hat:
            Hp = spow(H, -(k + l))
            for m in range(K + 1 - k):
                rhs[m + k] += What * Hp[m]
        H = rhs
    assert H == [F(1), F(25), F(208), F(1483)], H
    print(f"master equation exact to u^3: h = {[int(x) for x in H[1:]]}  OK")

    # mod-27 all-orders check against the banked H series
    import types, os, io, contextlib
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(root, "scripts", "derive_pk_fast.py")).read()
    mod = types.ModuleType("dpk")
    mod.__dict__['__file__'] = os.path.join(root, "scripts", "derive_pk_fast.py")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "dpk", "exec"), mod.__dict__)
        P, _ = mod.derive(17)

    def peval(poly, n):
        r = F(0)
        for c in reversed(poly):
            r = r * n + c
        return r

    KX = 17
    Gs = [int(peval(P[k], 0)) if k else 1 for k in range(KX + 1)]
    GH = [int(peval(P[k], 1)) if k else 1 for k in range(KX + 1)]

    def xmul(a, b, MOD=None):
        out = [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(KX + 1)]
        return [v % MOD for v in out] if MOD else out

    inv = [1] + [0] * KX
    for m in range(1, KX + 1):
        inv[m] = -sum(Gs[j] * inv[m - j] for j in range(1, m + 1))
    Hfull = xmul(GH, inv)

    for MOD, terms, name in (
        (27, [(25, 1, 2), (441, 2, 3), (1017, 2, 4), (43002 % 27, 3, 6)],
         "H = 1 + 25uH^-2 + 441u^2H^-3 + 1017u^2H^-4 + 43002u^3H^-6"),
        (9, [(25, 1, 2)], "H = 1 + 25uH^-2"),
        (3, [(1, 1, 2)], "H = 1 + uH^-2  (spine cubic H^3 = H^2 + u)"),
    ):
        Hm = [h % MOD for h in Hfull]

        def minv(a):
            r = [pow(a[0], -1, MOD)] + [0] * KX
            for m in range(1, KX + 1):
                r[m] = (-r[0] * sum(a[i] * r[m - i] for i in range(1, m + 1))) % MOD
            return r

        def mpow(a, p):
            base = a if p >= 0 else minv(a)
            r = [1] + [0] * KX
            for _ in range(abs(p)):
                r = xmul(r, base, MOD)
            return r

        rhs = [1] + [0] * KX
        for w, k, p in terms:
            Hp = mpow(Hm, -p)
            for m in range(KX + 1 - k):
                rhs[m + k] = (rhs[m + k] + w * Hp[m]) % MOD
        assert Hm == rhs, (MOD, name)
        print(f"mod {MOD:>2}: {name}  -- matches all {KX + 1} coefficients  OK")


if __name__ == "__main__" and __import__("sys").argv[-1] == "master":
    check_master()


# ---------------------------------------------------------------------------
# BOUNDARY WEIGHTS AND THE LADDER (2026-07-12).  Bottom-boundary cluster (no p
# row; counted relative to the renewal q above): single-row s-cluster has
# boundary weight 2s+1 -- the interior (2s+1)^2 literally factors entry x exit.
# The chain identity with boundaries is EXACT (verified 40/40 vs the banked
# triangle, k <= 3, H <= 10, including all boundary corrections):
#   F(y,z) = Eb/(1 - 3z - sum Wint y^k z^(l+1)) * Et + pure-cluster poly,
#   Eb = z(1 + sum Wb y^k z^l),  Et likewise with reversed clusters.
# Residue extraction at z* = 1/mu gives the amplitude, hence
#   G = eps_b eps_t (1 - wH') / (1 + sum (l+1) What u^k H^-(k+l)),
#   eps = 1 + sum Bhat u^k H^-(k+l),  Bhat = Wb 3^(2k-l)
# (verified exactly against known G through u^3).
#
# (*a) G == 1 (mod 9), DERIVED: boundary valuation v3(Bhat) >= 2k-l >= k kills
# every boundary cluster mod 9 except the pair-row (Bhat = 15); the denominator
# similarly reduces to 1 + 50u/H^2 (v3((l+1)What) >= 2 structurally, the l=k=2
# case saved by the factor l+1 = 3).  The surviving identity
#   (1 + 15u/H^2)^2 (1 - uH'/H) == 1 + 50u/H^2  (mod 9)
# collapses to H^2 H' + 3uH' + 2H == 0 (mod 9), which follows from the mod-9
# cubic H^3 = H^2 + 25u and its derivative: substituting u = 4(H^3 - H^2)
# gives H'(3H^3 - 2H^2) + 2H = 25H + 2H = 27H == 0.  QED (mod law + chain).
#
# (*c) upgraded: the mod-27 master equation has a UNIQUE fixed point in
# (Z/27)[[u]] (u-adic contraction), computable by pure algebra with no
# enumeration; S = (H^3 - H(u^3))/3 == u^2 + uW (mod 3) verified on it to
# u^300 (checked in check_ladder()).  All three ladder items of
# results/ternary-spine.md now stand on the gas.
# ---------------------------------------------------------------------------
def boundary_weight(sizes, W=9):
    """Bottom-boundary cluster weight: rows 1..m the cluster, row m+1 = q fixed."""
    from itertools import combinations
    from collections import deque

    def connected(rows):
        allc = [(x, r) for r, xs in rows.items() for x in xs]
        S = set(allc); seen = {allc[0]}; dq = deque([allc[0]])
        while dq:
            x, r = dq.popleft()
            for dx in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    pt = (x + dx, r + dr)
                    if (dx or dr) and pt in S and pt not in seen:
                        seen.add(pt); dq.append(pt)
        return len(seen) == len(S)

    m = len(sizes); total = 0

    def rec(i, rows, prev):
        nonlocal total
        if i == 0:
            if connected(rows):
                total += 1
            return
        lo, hi = min(prev), max(prev)
        for T in combinations(range(lo - W, hi + W + 1), sizes[i - 1]):
            if any(abs(a - b) <= 1 for a in prev for b in T):
                rec(i - 1, {**rows, i - 1: set(T)}, T)

    rec(m, {m: {0}}, (0,))
    return total


def check_ladder(KX=300):
    """Iterate the mod-27 master equation as a pure-algebra fixed point and
    verify the Ternary Spine ladder on it: (*b) H==W mod 3, the mod-9 lift,
    and (*c) S == u^2 + uW mod 3 -- to u^KX, no enumeration involved."""
    MOD = 27

    def xmul(a, b):
        out = [0] * (KX + 1)
        for i, ai in enumerate(a):
            if ai:
                for j in range(KX + 1 - i):
                    if b[j]:
                        out[i + j] = (out[i + j] + ai * b[j]) % MOD
        return out

    def xinv(a, M=MOD):
        r = [pow(a[0], -1, M)] + [0] * KX
        for m in range(1, KX + 1):
            r[m] = (-r[0] * sum(a[i] * r[m - i] for i in range(1, m + 1))) % M
        return r

    def xpow(a, p):
        base = a if p >= 0 else xinv(a)
        r = [1] + [0] * KX
        q = abs(p)
        while q:
            if q & 1:
                r = xmul(r, base)
            base = xmul(base, base); q >>= 1
        return r

    H = [1] + [0] * KX
    for _ in range(KX + 2):
        rhs = [1] + [0] * KX
        for w, k, p in ((25, 1, 2), (441, 2, 3), (1017, 2, 4), (43002 % 27, 3, 6)):
            Hp = xpow(H, -p)
            for m in range(KX + 1 - k):
                rhs[m + k] = (rhs[m + k] + w * Hp[m]) % MOD
        if rhs == H:
            break
        H = rhs

    W = [1] + [0] * KX
    for _ in range(KX + 2):
        Wi = xinv([w % 3 for w in W], 3)
        Wi2 = [0] * (KX + 1)
        for i, a in enumerate(Wi):
            if a:
                for j in range(KX + 1 - i):
                    if Wi[j]:
                        Wi2[i + j] = (Wi2[i + j] + a * Wi[j]) % 3
        Wn = [1] + [Wi2[m - 1] % 3 for m in range(1, KX + 1)]
        if Wn == W:
            break
        W = Wn

    assert all((H[m] - W[m]) % 3 == 0 for m in range(KX + 1)), "(*b)"
    H2 = xmul(H, H); H3 = xmul(H2, H)
    assert all((H3[m] - H2[m] - (25 if m == 1 else 0)) % 9 == 0
               for m in range(KX + 1)), "mod-9 lift"
    Hu3 = [0] * (KX + 1)
    for m in range(KX // 3 + 1):
        Hu3[3 * m] = H[m]
    num = [(H3[m] - Hu3[m]) % 27 for m in range(KX + 1)]
    assert all(x % 3 == 0 for x in num), "(*c) divisibility"
    S = [(x // 3) % 3 for x in num]
    tgt = [0] * (KX + 1); tgt[2] = 1
    for m in range(KX):
        tgt[m + 1] = (tgt[m + 1] + W[m]) % 3
    assert S == tgt, "(*c)"
    print(f"ladder on the mod-27 fixed point to u^{KX}: "
          f"(*b), mod-9 lift, (*c) all OK")


if __name__ == "__main__" and __import__("sys").argv[-1] == "ladder":
    for s in ((2,), (3,), (4,), (2, 2)):
        pass
    assert [boundary_weight((s,)) for s in (2, 3, 4)] == [5, 7, 9]
    assert boundary_weight((2, 2)) == 66
    check_ladder()
