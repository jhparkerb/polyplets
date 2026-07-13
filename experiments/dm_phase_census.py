#!/usr/bin/env python3
"""dm program step 1: the phase lemma + per-class quasi-polynomiality.

Lemma (reversal cost): a diagonal-mirror-symmetric animal with box exactly
SxS and S+k cells has at most 2k strict direction reversals in its row-min
(and row-max) sequence, hence at most 2k+1 monotone phases.
Proof: within a maximal stretch of single-cell rows, consecutive cells must
king-touch, so the position moves by steps in {-1,0,+1}; a reversal inside
the stretch immediately revisits a column (column surplus >= 1), and a
0-step likewise; reversals located at multi-cell rows are bounded by the
number of multi-cell rows (row surplus). The two pools each hold exactly k
by mirror symmetry: total reversals <= 2k. Verified TIGHT for k <= 3.

Validation: each phase class (k, runs) is SEPARATELY per-parity
quasi-polynomial of degree <= k from S >= 2k+2, and the classes partition
d(S, S+k) -- the grammar for the chain proof of the dm diagonal law.
"""
import sys
import os
from collections import defaultdict
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dm_sym_enum import enumerate_sym


def phases(seq):
    if len(seq) <= 1:
        return 1
    runs = 1
    d = 0
    for i in range(len(seq) - 1):
        nd = (seq[i + 1] > seq[i]) - (seq[i + 1] < seq[i])
        if nd == 0:
            continue
        if d == 0:
            d = nd
        elif nd != d:
            runs += 1
            d = nd
    return runs


def main():
    animals = enumerate_sym(15)
    cls = defaultdict(lambda: defaultdict(int))
    tot = defaultdict(lambda: defaultdict(int))
    maxr = defaultdict(int)
    for A in animals:
        xs = [x for x, _ in A]
        ys = [y for _, y in A]
        S = max(xs) - min(xs) + 1
        if max(ys) - min(ys) + 1 != S:
            continue
        k = len(A) - S
        if k > 3:
            continue
        rows = defaultdict(list)
        for x, y in A:
            rows[y].append(x)
        m = [min(rows[y]) for y in sorted(rows)]
        M = [max(rows[y]) for y in sorted(rows)]
        r = max(phases(m), phases(M))
        maxr[k] = max(maxr[k], r)
        if k <= 2:
            cls[(k, r)][S] += 1
            tot[k][S] += 1
    assert [maxr[k] for k in range(4)] == [1, 3, 5, 7], maxr

    def qp(d, k, onset, maxS):
        for par in (0, 1):
            pts = [(S, d.get(S, 0)) for S in range(onset, maxS + 1)
                   if S % 2 == par]
            if len(pts) < k + 2:
                if len(pts) >= 2 and len(set(v for _, v in pts)) == 1:
                    continue
                return None
            fit = pts[:k + 1]

            def lag(x):
                t = F(0)
                for i, (xi, yi) in enumerate(fit):
                    w = F(yi)
                    for j, (xj, _) in enumerate(fit):
                        if j != i:
                            w *= F(x - xj, xi - xj)
                    t += w
                return t
            if not all(lag(S) == v for S, v in pts):
                return False
        return True

    for (k, r) in sorted(cls):
        maxS = max(cls[(k, r)])
        assert qp(cls[(k, r)], k, 2 * k + 2, maxS), (k, r)
    for k in (1, 2):
        for S in sorted(tot[k]):
            assert sum(cls[(k, r)].get(S, 0)
                       for r in range(1, 2 * k + 2)) == tot[k][S]
    print("dm step 1: reversal lemma tight (max runs 1,3,5,7 at k=0..3); "
          "every phase class per-parity quasi-poly deg<=k from S>=2k+2; "
          "classes partition d(S,S+k)  OK")


if __name__ == "__main__":
    main()
