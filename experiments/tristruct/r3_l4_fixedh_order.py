#!/usr/bin/env python3
"""r3_l4_fixedh_order: minimal linear-recurrence order of the FIXED-H
symmetric series, measured from the banked byheight tables.

For fixed H, I_H(<h>)(n), I_H(<v>)(n), I_H(C2)(n) all have rational
generating functions (finite column transfer matrix; palindromic column
sequences for <v>/C2 reduce to matrix-power diagonals). So an IMPLICIT
route to n=40 exists at every H: pin the recurrence, then iterate. The
question LEAD-1 needs answered is the ORDER — how many rule-independent
terms would pin it — and how that order grows with H.

Method: per H, take the banked series n = 1..32 (missing rows = genuine
zeros per results/percell-mod4.md), skip the leading transient (n < H,
where width < height effects differ), fit a constant-coefficient linear
recurrence of order r on the head, accept the minimal r that then HOLDS on
the last 6 banked terms. Exact rational arithmetic. RED control: a planted
order-5 recurrence must be recovered exactly, and random digits must
report none.
"""
from fractions import Fraction
import collections, os, random

ROOT = "/Users/jasonp/src/polyominoes"
NMAX = 32
HOLD = 6

def load_tables():
    ih = collections.Counter(); iv = collections.Counter(); ic2 = {}
    with open(os.path.join(ROOT, "results/percell_raw/hmirror.byheight.n32.out")) as f:
        for line in f:
            n, H, W, c = map(int, line.split())
            ih[(n, H)] += c; iv[(n, W)] += c
    with open(os.path.join(ROOT, "results/percell_raw/r180.byheight.n32.out")) as f:
        for line in f:
            n, H, c = map(int, line.split())
            ic2[(n, H)] = c
    return ih, iv, ic2

def min_order(series, rmax=12):
    """Minimal r: recurrence fit on series[:-HOLD] annihilates the tail.
    Returns (r, ok) or (None, False). series indexed from its own start."""
    L = len(series)
    for r in range(1, rmax + 1):
        fitlen = L - HOLD
        if fitlen < 2 * r + 1:
            return None, False
        # solve for coeffs c_1..c_r: s(k) = sum c_i s(k-i), on the fit region
        rows = []
        rhs = []
        for k in range(r, fitlen):
            rows.append([Fraction(series[k - i]) for i in range(1, r + 1)])
            rhs.append(Fraction(series[k]))
        # least-structure exact solve: Gaussian elimination on [rows | rhs]
        m = [rows[i] + [rhs[i]] for i in range(len(rows))]
        ncols = r
        pivots = []
        ri = 0
        for c in range(ncols):
            piv = next((i for i in range(ri, len(m)) if m[i][c] != 0), None)
            if piv is None:
                continue
            m[ri], m[piv] = m[piv], m[ri]
            inv = m[ri][c]
            m[ri] = [x / inv for x in m[ri]]
            for i in range(len(m)):
                if i != ri and m[i][c] != 0:
                    f = m[i][c]
                    m[i] = [a - f * b for a, b in zip(m[i], m[ri])]
            pivots.append(c)
            ri += 1
        if any(all(x == 0 for x in row[:ncols]) and row[ncols] != 0 for row in m):
            continue  # inconsistent: no order-r recurrence on the fit region
        coef = [Fraction(0)] * r
        for i, pc in enumerate(pivots):
            coef[pc] = m[i][ncols]
        # verify on the whole series INCLUDING the holdout tail
        ok = all(Fraction(series[k]) ==
                 sum(coef[i - 1] * series[k - i] for i in range(1, r + 1))
                 for k in range(r, L))
        if ok:
            return r, True
    return None, False

def per_h(name, table, hs):
    print(f"-- {name} --")
    for H in hs:
        s = [table.get((n, H), 0) for n in range(1, NMAX + 1)]
        start = max(H, 1)  # skip the width<height transient head
        series = s[start - 1:]
        if sum(1 for x in series if x) < 8:
            print(f"H={H}: too few nonzero banked terms ({sum(1 for x in series if x)})")
            continue
        r, ok = min_order(series)
        if ok:
            print(f"H={H}: minimal order {r} (fit n={start}..{NMAX-HOLD}, "
                  f"holds on last {HOLD} banked terms)")
        else:
            print(f"H={H}: NO recurrence of order <= 12 pins the banked tail "
                  f"({len(series)} usable terms)")

def main():
    # RED controls
    random.seed(7)
    planted = [1, 2, 3, 4, 5]
    for _ in range(27):
        planted.append(3 * planted[-1] - 2 * planted[-2] + planted[-5])
    r, ok = min_order(planted)
    assert ok and r == 5, (r, ok)
    rnd = [random.randint(1, 9) for _ in range(32)]
    r, ok = min_order(rnd)
    assert not ok, (r, ok)
    print("RED controls: planted order-5 recovered; random rejected. OK")

    ih, iv, ic2 = load_tables()
    hs = list(range(1, 11))
    per_h("I_H(<h>)", ih, hs)
    per_h("I_H(<v>)", iv, hs)
    per_h("I_H(C2)", ic2, hs)

if __name__ == "__main__":
    main()
