#!/usr/bin/env python3
"""p2_symtri_probe.py -- Proposer 2 structure probes on the SYMMETRY-REFINED
triangle I(n,H) = I_H(D2ax) = number of fixed king animals of height exactly H
invariant under the full height-preserving Klein group {e, h, v, r180}.

Banked source: results/subgroup_d2ax_byheight.txt (n H count, n <= 40),
computed by symcount_fast (subgroup census, results/subgroup-mod4.md).
Independent small-n source: p2_enum --sym klein column (own recursion, own
connectivity rule; data/p2_sym_n13.txt).

Probes (all exact):
  P1. cross-check banked I vs self-enumerated klein counts, all cells n<=13.
  P2. forced zeros: which (n mod 2, H mod 2) classes are empty, and is the
      zero set exactly characterized by a parity rule?
  P3. top diagonals I(n, n-k): closed form / growth structure? print k<=6.
  P4. parity pattern of I(n,H): print as bitmap, look for period/digit rule;
      also I mod 4.
  P5. column structure: I(n,H) for fixed small H -- C-finite? (print columns
      H=3..6 for eyeballing + quick linear-recurrence probe mod nothing,
      exact, order<=6 fit on n<=22 predict n>=23.)

Run from experiments/tristruct/:  python3 p2_symtri_probe.py
"""
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

def load_I():
    d = {}
    with open(os.path.join(ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
        for ln in f:
            n, H, c = (int(x) for x in ln.split())
            d[(n, H)] = c
    return d

def load_sym(path):
    d = {}
    with open(path) as f:
        for ln in f:
            p = [int(x) for x in ln.split()]
            d[(p[0], p[1])] = tuple(p[2:])
    return d

def lin_rec_fit(seq, order):
    """Exact C-finite fit: find c_1..c_order with s[i] = sum c_j s[i-j] using
    the first len(seq) terms via Gaussian elimination over Q. Returns coeffs
    or None."""
    rows = []
    rhs = []
    for i in range(order, len(seq)):
        rows.append([Fraction(seq[i - j]) for j in range(1, order + 1)])
        rhs.append(Fraction(seq[i]))
    if len(rows) < order:
        return None
    # solve least-structure: use first `order` equations, then verify on rest
    import itertools
    A = [r[:] + [rhs[k]] for k, r in enumerate(rows[:order])]
    ncol = order
    piv = []
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            return None
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                A[i] = [x - A[i][c] * y for x, y in zip(A[i], A[r])]
        r += 1
    coef = [A[i][ncol] for i in range(order)]
    for k in range(order, len(rows)):
        if sum(c * v for c, v in zip(coef, rows[k])) != rhs[k]:
            return None
    return coef

def main():
    I = load_I()
    sym = load_sym(os.path.join(HERE, 'data', 'p2_sym_n13.txt'))

    # P1 cross-check
    bad = []
    for (n, H), v in sym.items():
        klein = v[4]
        if I.get((n, H), 0) != klein:
            bad.append((n, H, klein, I.get((n, H), 0)))
    # also banked cells absent from sym data (should be zero-klein cells only)
    print("P1 banked I_H(D2ax) vs self klein counts, n<=13: %s"
          % ("ALL MATCH" if not bad else "MISMATCH %s" % bad[:8]))

    # P2 zero pattern
    from collections import Counter
    zero_classes = Counter()
    nonzero_classes = Counter()
    odd_zero_cells = []
    for n in range(1, 41):
        for H in range(1, n + 1):
            v = I.get((n, H), 0)
            cls = (n % 2, H % 2)
            (nonzero_classes if v else zero_classes)[cls] += 1
            if v == 0 and not (n % 2 == 1 and H % 2 == 0):
                odd_zero_cells.append((n, H))
    print("P2 zero cells by (n%%2,H%%2): zero=%s nonzero=%s"
          % (dict(zero_classes), dict(nonzero_classes)))
    print("P2 zeros NOT explained by {n odd,H even}: %d cells: %s%s"
          % (len(odd_zero_cells), odd_zero_cells[:15],
             " ..." if len(odd_zero_cells) > 15 else ""))

    # P3 top diagonals
    for k in range(0, 7):
        seq = [(n, I.get((n, n - k), 0)) for n in range(k + 1, 41)]
        vals = [v for _, v in seq]
        print("P3 diag k=%d: %s" % (k, vals[:18]))

    # P4 parity bitmap
    print("P4 parity of I(n,H) ('.'=even/zero, '1'=odd), rows n=1..40:")
    for n in range(1, 41):
        print("  n=%2d %s" % (n, ''.join(
            '1' if I.get((n, H), 0) % 2 else '.' for H in range(1, n + 1))))

    # P5 column recurrences
    for H in range(3, 7):
        col = [I.get((n, H), 0) for n in range(H, 41)]
        print("P5 col H=%d: %s..." % (H, col[:14]))
        for order in range(1, 7):
            fitlen = 22 - H + 1
            fit = col[:fitlen]
            coef = lin_rec_fit(fit, order)
            if coef is None:
                continue
            ok = all(
                col[i] == sum(coef[j - 1] * col[i - j] for j in range(1, order + 1))
                for i in range(fitlen, len(col)))
            print("   order-%d fit on n<=22: coeffs=%s holdout(n=23..40): %s"
                  % (order, [str(c) for c in coef], "ALL PASS" if ok else "fails"))
            break

if __name__ == '__main__':
    main()
