#!/usr/bin/env python3
"""Cluster-weight counting by row-transfer DP (no per-configuration listing).

count_stack(sizes) counts king-connected configurations of a stack of rows
with the given sizes (bottom to top), up to horizontal translation (the count
is anchored by quotienting shifts via state normalization; the first row's
placements contribute multiplicity 1 each in normalized coordinates, matching
the anchored enumerations in defect_gas.py).

  interior weight  W(v)  = count_stack([1] + v + [1])     (p, cluster, q)
  boundary weight  Wb(v) = count_stack([1] + reversed(v)) (anchored at q,
                            built downward -- up/down king symmetry)
  pure weight      Wp(v) = count_stack(v)

State = (normalized cell offsets of current row, connectivity partition of
those cells). Transition adds the next row anywhere in a provably safe window
(total-cell spread bound: a connected C-cell king set spans < C columns);
pending components that fail to touch the next row can never reconnect
(rows are consecutive) and are pruned. Final states must be one component.

Purpose (2026-07-13): measure where P_k-from-the-gas dies. Direct enumeration
is Omega(W) = Omega(14^l) for stacked pairs -- hopeless past k ~ 6. The DP
evades that floor; this file measures its state growth instead.
Validated against every enumerated weight in results/defect-gas.md.
"""
import sys
import time
from itertools import combinations
from functools import lru_cache


def compositions(k):
    """All cluster row-size vectors with surplus k: s_i >= 2, sum(s_i-1) = k."""
    out = []

    def rec(vec, left):
        if left == 0:
            if vec:
                out.append(tuple(vec))
            return
        for s in range(2, left + 2):
            rec(vec + [s], left - (s - 1))

    rec([], k)
    return out


def count_stack(sizes):
    """Count connected configurations of rows with the given sizes (bottom to
    top), modulo horizontal translation."""
    total_cells = sum(sizes)
    M = total_cells + 1                      # safe window: spread < total cells

    def normalize(cells, part):
        base = cells[0]
        return tuple(c - base for c in cells), part

    def row_partition(cells):
        """Partition of a single row's cells by within-row adjacency,
        with labels compacted to 0..nblocks-1 in order of appearance."""
        lab = list(range(len(cells)))
        for i in range(len(cells) - 1):
            if cells[i + 1] - cells[i] <= 1:
                lab[i + 1] = lab[i]
        canon = {}
        out = []
        for x in lab:
            if x not in canon:
                canon[x] = len(canon)
            out.append(canon[x])
        return tuple(out)

    # initial states: first row, anchored min = 0 (spread bounded by M)
    s0 = sizes[0]
    states = {}
    for rest in combinations(range(1, M + 1), s0 - 1):
        cells = (0,) + rest
        st = (cells, row_partition(cells))
        states[st] = states.get(st, 0) + 1

    for depth, s in enumerate(sizes[1:], start=1):
        new_states = {}
        for (cells, part), cnt in states.items():
            lo, hi = cells[0] - M, cells[-1] + M
            nblocks = len(set(part))
            for T in combinations(range(lo, hi + 1), s):
                # merge bookkeeping: old blocks + new cells
                # labels: 0..nblocks-1 old, then new cells nblocks..nblocks+s-1
                lab = list(range(nblocks + s))

                def find(x):
                    while lab[x] != x:
                        lab[x] = lab[lab[x]]
                        x = lab[x]
                    return x

                def union(a, b):
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        lab[ra] = rb

                touched = [False] * nblocks
                for j, t in enumerate(T):
                    for i, c in enumerate(cells):
                        if abs(t - c) <= 1:
                            union(part[i], nblocks + j)
                            touched[part[i]] = True
                for j in range(s - 1):
                    if T[j + 1] - T[j] <= 1:
                        union(nblocks + j, nblocks + j + 1)
                # prune: any old block with no contact is stranded forever
                if not all(touched[b] for b in set(part)):
                    continue
                roots = [find(nblocks + j) for j in range(s)]
                canon = {}
                npart = []
                for r in roots:
                    if r not in canon:
                        canon[r] = len(canon)
                    npart.append(canon[r])
                st = normalize(T, tuple(npart))
                new_states[st] = new_states.get(st, 0) + cnt
        states = new_states
    return sum(c for (cells, part), c in states.items() if len(set(part)) == 1)


def interior(v):
    return count_stack([1] + list(v) + [1])


def boundary(v):
    return count_stack([1] + list(reversed(v)))


def pure(v):
    return count_stack(list(v))


def validate():
    known_int = {(2,): 25, (3,): 49, (4,): 81, (2, 2): 339,
                 (2, 3): 930, (3, 2): 930, (2, 2, 2): 4778}
    known_bnd = {(2,): 5, (3,): 7, (4,): 9, (2, 2): 66,
                 (2, 3): 177, (3, 2): 130, (2, 2, 2): 919}
    known_pure = {(2,): 1, (3,): 1, (4,): 1, (2, 2): 13,
                  (2, 3): 25, (3, 2): 25, (2, 2, 2): 177}
    for v, w in known_int.items():
        assert interior(v) == w, (v, interior(v), w)
    for v, w in known_bnd.items():
        assert boundary(v) == w, (v, boundary(v), w)
    for v, w in known_pure.items():
        assert pure(v) == w, (v, pure(v), w)
    print("DP validated against all enumerated weights (interior/boundary/pure)")




# Two-row interior weights W(a,b) past the k <= 5 table below, banked
# 2026-08-01 (wall time in the comment; W(5,5) alone took 8.4 h). Reproduce a
# single cell with `python3 experiments/cluster_weight_dp.py pair A B`.
# Consequences in results/defect-gas.md: the a=2 cubic holds at b=7,8, the a=3
# row is the quartic 24b^4+16b^3+110b^2-19b+16 (holdout W(3,7) exact), and the
# symmetric-bicubic target is refuted -- deg_b W(a,.) = a+1.
TWO_ROW_INTERIOR = {
    (2, 7): 9454,     # 178 s
    (2, 8): 13845,    # 1502 s
    (3, 5): 19671,    # 89 s
    (3, 6): 38422,    # 1144 s
    (3, 7): 68385,    # 13388 s
    (4, 4): 28559,    # 120 s
    (4, 5): 74710,    # 1975 s
    (5, 5): 226545,   # 30137 s
}

KNOWN_WEIGHTS = {  # (interior, boundary_bottom, boundary_top, pure), DP-computed, k <= 5
    (2,): (25, 5, 5, 1),
    (2, 2): (339, 66, 66, 13),
    (3,): (49, 7, 7, 1),
    (2, 2, 2): (4778, 919, 919, 177),
    (2, 3): (930, 177, 130, 25),
    (3, 2): (930, 130, 177, 25),
    (4,): (81, 9, 9, 1),
    (2, 2, 2, 2): (68314, 13103, 13103, 2515),
    (2, 2, 3): (13459, 2569, 1857, 355),
    (2, 3, 2): (18308, 3445, 3445, 649),
    (2, 4): (1993, 372, 218, 41),
    (3, 2, 2): (13459, 1857, 2569, 355),
    (3, 3): (3325, 455, 455, 63),
    (4, 2): (1993, 218, 372, 41),
    (5,): (121, 11, 11, 1),
    (2, 2, 2, 2, 2): (981085, 187965, 187965, 36021),
    (2, 2, 2, 3): (194232, 37168, 26714, 5116),
    (2, 2, 3, 2): (268886, 51195, 50476, 9616),
    (2, 2, 4): (29515, 5603, 3192, 607),
    (2, 3, 2, 2): (268886, 50476, 51195, 9616),
    (2, 3, 3): (67371, 12567, 9095, 1699),
    (2, 4, 2): (50442, 9335, 9335, 1729),
    (2, 5): (3672, 675, 330, 61),
    (3, 2, 2, 2): (194232, 26714, 37168, 5116),
    (3, 2, 3): (38469, 5263, 5263, 721),
    (3, 3, 2): (67371, 9095, 12567, 1699),
    (3, 4): (8868, 1188, 953, 129),
    (4, 2, 2): (29515, 3192, 5603, 607),
    (4, 3): (8868, 953, 1188, 129),
    (5, 2): (3672, 330, 675, 61),
    (6,): (169, 13, 13, 1),
}


def check_grand_form(K=5):
    """Ab-initio grand form through order K=5: H (master equation) and G
    (boundary residue) from KNOWN_WEIGHTS alone, vs the banked series.
    All series algebra; runs in milliseconds. (2026-07-13)"""
    from fractions import Fraction as F

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

    # mu order-by-order (fixed-point garbage blows up big-int sizes otherwise)
    mu = [F(3)] + [F(0)] * K
    for m in range(1, K + 1):
        rhs = [F(3)] + [F(0)] * K
        for v, (wi, _, _, _) in KNOWN_WEIGHTS.items():
            k, l = sum(v) - len(v), len(v)
            mp = spow(mu, -l)
            for j in range(K + 1 - k):
                rhs[j + k] += wi * mp[j]
        mu[m] = rhs[m]
    H = [x / 3 for x in mu]

    # H in u-units via the master equation, order-by-order
    Hu = [F(1)] + [F(0)] * K
    for m in range(1, K + 1):
        rhs = [F(1)] + [F(0)] * K
        for v, (wi, _, _, _) in KNOWN_WEIGHTS.items():
            k, l = sum(v) - len(v), len(v)
            What = F(wi) * F(3) ** (2 * k - l - 1)
            Hp = spow(Hu, -(k + l))
            for j in range(K + 1 - k):
                rhs[j + k] += What * Hp[j]
        Hu[m] = rhs[m]
    assert [int(x) for x in Hu] == [1, 25, 208, 1483, 20688, 130208], Hu

    # G from the boundary residue formula
    zs = sinv(mu)

    def evalz(terms3):
        out = [F(0)] * (K + 1)
        for yk, ze, c in terms3:
            zp = spow(zs, ze)
            for j in range(K + 1 - yk):
                out[j + yk] += c * zp[j]
        return out

    Eb = [(0, 1, F(1))] + [(sum(v) - len(v), len(v) + 1, F(wb))
                           for v, (_, wb, _, _) in KNOWN_WEIGHTS.items()]
    Et = [(0, 0, F(1))] + [(sum(v) - len(v), len(v), F(wt))
                           for v, (_, _, wt, _) in KNOWN_WEIGHTS.items()]
    NS = smul(evalz(Eb), evalz(Et))
    Dp = [(0, 0, F(-3))] + [(sum(v) - len(v), len(v), F(-(len(v) + 1) * wi))
                            for v, (wi, _, _, _) in KNOWN_WEIGHTS.items()]
    C = smul(smul([-x for x in NS], mu), sinv(evalz(Dp)))
    us = [F(0)] + [mu[m - 1] / 27 for m in range(1, K + 1)]
    dHdy = [(i + 1) * H[i + 1] for i in range(K)] + [F(0)]
    dudy = [(i + 1) * us[i + 1] for i in range(K)] + [F(0)]
    Hp = smul(dHdy, sinv(dudy))
    wHp = smul([F(0), F(1, 9)] + [F(0)] * (K - 1), Hp)
    G = smul([3 * x for x in C], [F(1) - wHp[0]] + [-x for x in wHp[1:]])
    assert G == [F(1), F(-5), F(-62, 9), F(-1625, 81),
                 F(-56842, 729), F(-2170913, 6561)], G
    print("grand form ab initio through u^5: H = [1,25,208,1483,20688,130208]"
          " and G (g1..g5) both match banked  OK")


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[1] == "pair":
        a, b = int(sys.argv[2]), int(sys.argv[3])
        t0 = time.time()
        w = interior((a, b))
        banked = TWO_ROW_INTERIOR.get((a, b)) or TWO_ROW_INTERIOR.get((b, a))
        tag = ""
        if banked is not None:
            tag = "  (matches banked)" if banked == w else f"  MISMATCH vs {banked}"
        print(f"W({a},{b}) = {w}   [{time.time() - t0:.0f}s]{tag}")
        sys.exit(0)

    validate()
    for v, (wi, wb, wt, wp) in KNOWN_WEIGHTS.items():
        if sum(v) - len(v) <= 3:
            assert (interior(v), boundary(v),
                    boundary(tuple(reversed(v))), pure(v)) == (wi, wb, wt, wp)
    check_grand_form()
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for k in range(1, kmax + 1):
        t0 = time.time()
        rows = []
        for v in compositions(k):
            rows.append((v, interior(v), boundary(v),
                         boundary(tuple(reversed(v))), pure(v)))
        dt = time.time() - t0
        print(f"k={k}: {len(rows)} types, {dt:.2f}s")
        for v, wi, wb, wt, wp in rows:
            print(f"   {str(v):16} int={wi:<10} bot={wb:<9} top={wt:<9} pure={wp}")
