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
