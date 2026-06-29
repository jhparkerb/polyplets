#!/usr/bin/env python3
"""Convex polyplet (and polyomino) enumeration by AREA, via a row transfer matrix.

A convex (HV-convex) king-animal: every row is a contiguous column-interval AND
every column a contiguous row-interval. Equivalently the left border is v-shaped
(non-increasing then non-decreasing) and the right border ^-shaped. Building the
animal row by row, the only state needed is (left-phase, right-phase, width);
transitions are counted by MULTIPLICITY (how many horizontal offsets are valid)
and weighted by area (cells added). king=True lets consecutive rows corner-touch
(polyplets); king=False requires column overlap (ordinary polyominoes).

Why: testing whether the convex constraint buys a closed form. It does by
*perimeter* (classical: algebraic), but we count by *area* (cells = n). The
recurrence search below finds NO P-recurrence for convex polyplets -- nor for the
KNOWN convex-polyomino control -- strong evidence that convex enumeration by area
is q-series / non-D-finite, i.e. NOT a closed form in the D-finite sense. The
transfer matrix itself is the efficient "solution" (growth mu ~ 3.13).

Validated against brute-force enumeration (n<=8); the edge case reproduces the
known convex-polyomino area sequence. See docs/proofs/T-n-nm2-and-general.md and
the maybe-pile in ROADMAP.md.

Run:  python3 experiments/convex_polyplets.py [N]      (N>=34 runs the search)
"""
import sys
from collections import defaultdict


def count_int(lo, hi, *cons):
    """|[lo,hi] intersect cons|, each con an inclusive (a,b); None = unbounded side."""
    A, B = lo, hi
    for a, b in cons:
        if a is not None:
            A = max(A, a)
        if b is not None:
            B = min(B, b)
    return max(0, B - A + 1)


def convex_by_area(N, king=True):
    """[_, c(1), ..., c(N)] where c(n) = # fixed convex animals of n cells."""
    total = [0] * (N + 1)
    g = defaultdict(lambda: [0] * (N + 1))
    for w in range(1, N + 1):
        g[('DEC', 'INC', w)][w] += 1                  # row 1: any interval, area w
    for _, poly in list(g.items()):
        for k in range(N + 1):
            total[k] += poly[k]
    while g:
        gn = defaultdict(lambda: [0] * (N + 1))
        for (lp, rp, w), poly in g.items():
            lo = min((k for k in range(N + 1) if poly[k]), default=None)
            if lo is None:
                continue
            for w2 in range(1, N + 1):
                if lo + w2 > N:                       # adding this row overflows N
                    continue
                # next interval [l', l'+w2-1] vs current [0, w-1]; king lets it
                # corner-touch (l' in [-w2, w]); edge requires overlap.
                base = (-w2, w) if king else (1 - w2, w - 1)
                for lp2 in ('DEC', 'INC'):            # left border v-shape phase
                    if lp == 'DEC':
                        lcon = (None, 0) if lp2 == 'DEC' else (1, None)
                    else:
                        if lp2 != 'INC':
                            continue                  # INC can't revert to DEC
                        lcon = (0, None)
                    for rp2 in ('INC', 'DEC'):        # right border ^-shape phase
                        if rp == 'INC':
                            rcon = (w - w2, None) if rp2 == 'INC' else (None, w - w2 - 1)
                        else:
                            if rp2 != 'DEC':
                                continue
                            rcon = (None, w - w2)
                        mult = count_int(base[0], base[1], lcon, rcon)
                        if not mult:
                            continue
                        tgt = gn[(lp2, rp2, w2)]
                        for k in range(N + 1 - w2):
                            if poly[k]:
                                tgt[k + w2] += mult * poly[k]
        for _, poly in gn.items():
            for k in range(N + 1):
                total[k] += poly[k]
        g = gn
    return total


def brute_convex(N, king=True):
    """Ground truth: generate all fixed animals, filter HV-convex. O(exponential)."""
    def canon(cells):
        r0 = min(r for r, c in cells)
        c0 = min(c for r, c in cells)
        return frozenset((r - r0, c - c0) for r, c in cells)
    nbrs = ([(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
            if king else [(1, 0), (-1, 0), (0, 1), (0, -1)])

    def is_convex(p):
        rows, cols = {}, {}
        for r, c in p:
            rows.setdefault(r, []).append(c)
            cols.setdefault(c, []).append(r)
        for cs in rows.values():
            if max(cs) - min(cs) + 1 != len(cs):
                return False
        for rs in cols.values():
            if max(rs) - min(rs) + 1 != len(rs):
                return False
        return True

    out = [0] * (N + 1)
    polys = {canon({(0, 0)})}
    for n in range(1, N + 1):
        out[n] = sum(1 for p in polys if is_convex(p))
        if n < N:
            nxt = set()
            for p in polys:
                for (r, c) in p:
                    for dr, dc in nbrs:
                        q = (r + dr, c + dc)
                        if q not in p:
                            nxt.add(canon(p | {q}))
            polys = nxt
    return out


def find_prec(seq, r, d, fit):
    """Fit a P-recurrence sum_i p_i(n) a(n-i)=0 (deg p_i<=d) on the first `fit`
    terms, then require it to PREDICT every remaining term (holdout)."""
    import sympy as sp
    rows = []
    for k in range(r, fit):
        row = []
        for i in range(r + 1):
            for j in range(d + 1):
                row.append(sp.Integer(k + 1) ** j * seq[k - i])
        rows.append(row)
    ns = sp.Matrix(rows).nullspace()
    if not ns:
        return False
    vec = ns[0]

    def lhs(k):
        t = 0
        idx = 0
        for i in range(r + 1):
            for j in range(d + 1):
                t += vec[idx] * sp.Integer(k + 1) ** j * seq[k - i]
                idx += 1
        return t
    return all(sp.simplify(lhs(k)) == 0 for k in range(r, len(seq)))


def search_dfinite(seq, name, fit=32):
    print(f"== {name} ({len(seq)} terms), fit {fit}, holdout {len(seq) - fit} ==")
    for r in range(2, 7):
        for d in range(1, 6):
            if (r + 1) * (d + 1) >= fit - r:          # need overdetermination
                continue
            if find_prec(seq, r, d, fit):
                print(f"   D-FINITE: order {r}, deg {d} (predicts all {len(seq)} terms)")
                return (r, d)
    print("   no P-recurrence up to order 6, deg 5 (holdout-validated) -> non-D-finite")
    return None


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    plet = convex_by_area(N, king=True)
    omino = convex_by_area(N, king=False)
    bp, bo = brute_convex(8, True), brute_convex(8, False)
    assert plet[1:9] == bp[1:9], (plet[1:9], bp[1:9])
    assert omino[1:9] == bo[1:9], (omino[1:9], bo[1:9])
    print("brute-force validated (n<=8).")
    P = [plet[n] for n in range(1, N + 1)]
    O = [omino[n] for n in range(1, N + 1)]
    print("convex polyplets :", P)
    print("convex polyominoes:", O)
    if N >= 34:
        search_dfinite(O, "convex polyominoes (KNOWN control)")
        search_dfinite(P, "convex polyplets (NEW)")
