#!/usr/bin/env python3
"""p2_symcol_rec.py -- exact C-finite recurrence hunt on the COLUMNS of the
symmetry-refined triangle I(n,H) = I_H(D2ax) (banked
results/subgroup_d2ax_byheight.txt, symcount_fast lineage).

Mechanism expectation, stated up front: a Klein-invariant animal of height H
is a palindromic sequence of tb-symmetric columns, so I(.,H) should satisfy
SOME linear recurrence (rational-GF-like structure); the finding of interest
is whether the order is small enough to fit on n <= 22 and predict n = 23..40
exactly -- because I(40,H) is the input of the banked per-cell parity check
on T(40,H) (results/subgroup-mod4.md), currently single-source at n = 40.

Method: for each H, minimal-order exact fit (order r needs the first 2r terms
of the fit window; Gaussian elimination over Q), fitted ONLY on n <= 22,
then every banked term n = 23..40 is holdout. Also fits the even-n
subsequence for even H (odd-n terms are 0 by the forced-zero theorem,
results/triangle-hunt-klein-parity.md).

Run from experiments/tristruct/:  python3 p2_symcol_rec.py
"""
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FIT_MAX_N = 22

def load_I():
    d = {}
    with open(os.path.join(ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
        for ln in f:
            n, H, c = (int(x) for x in ln.split())
            d[(n, H)] = c
    return d

def solve_rec(fit, order):
    """Exact order-`order` constant-coeff recurrence from fit terms; None if
    the linear system is inconsistent/underdetermined or any fit term fails."""
    eqs = [([Fraction(fit[i - j]) for j in range(1, order + 1)], Fraction(fit[i]))
           for i in range(order, len(fit))]
    if len(eqs) < order:
        return None
    A = [list(l) + [r] for l, r in eqs]
    m, ncol = len(A), order
    row = 0
    where = [-1] * ncol
    for c in range(ncol):
        p = next((i for i in range(row, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[row], A[p] = A[p], A[row]
        A[row] = [x / A[row][c] for x in A[row]]
        for i in range(m):
            if i != row and A[i][c] != 0:
                A[i] = [x - A[i][c] * y for x, y in zip(A[i], A[row])]
        where[c] = row
        row += 1
    # inconsistent?
    for i in range(row, m):
        if A[i][ncol] != 0:
            return None
    if any(w < 0 for w in where):
        return None   # underdetermined: demand a unique minimal fit
    coef = [A[where[c]][ncol] for c in range(ncol)]
    # verify on all fit equations (redundant ones included)
    for l, r in eqs:
        if sum(c * v for c, v in zip(coef, l)) != r:
            return None
    return coef

def try_column(name, terms_by_n, nmax=40):
    """terms_by_n: {n: value} on consecutive n (its keys define the axis)."""
    ns = sorted(terms_by_n)
    fit_ns = [n for n in ns if n <= FIT_MAX_N]
    hold_ns = [n for n in ns if n > FIT_MAX_N]
    fit = [terms_by_n[n] for n in fit_ns]
    for order in range(1, 13):
        if len(fit) < 2 * order:
            break
        coef = solve_rec(fit, order)
        if coef is None:
            continue
        # predict holdout sequentially
        seq = {n: terms_by_n[n] for n in fit_ns}
        ok = True
        for idx, n in enumerate(hold_ns):
            prev_ns = fit_ns + hold_ns[:idx]
            if len(prev_ns) < order:
                ok = False
                break
            pred = sum(coef[j - 1] * Fraction(seq[prev_ns[-j]])
                       for j in range(1, order + 1))
            if pred != terms_by_n[n]:
                ok = False
                first_fail = n
                break
            seq[n] = terms_by_n[n]
        if ok:
            print("  %s: ORDER %d fit(n<=22, %d terms) holdout %d/%d ALL PASS"
                  % (name, order, len(fit), len(hold_ns), len(hold_ns)))
            print("     coeffs: %s" % [str(c) for c in coef])
            return order
        else:
            print("  %s: order %d fits n<=22 but FAILS holdout first at n=%s"
                  % (name, order, first_fail))
    print("  %s: no order<=12 recurrence fits n<=22 (%d fit terms)"
          % (name, len(fit)))
    return None

def main():
    I = load_I()
    print("C-finite hunt on columns of I(n,H), fit n<=%d, holdout 23..40:"
          % FIT_MAX_N)
    for H in range(1, 13):
        col = {n: I.get((n, H), 0) for n in range(H, 41)}
        if H % 2 == 0:
            # odd-n entries are 0 (proved); fit the even-n subsequence
            sub = {n: col[n] for n in col if n % 2 == 0}
            axis = sorted(sub)
            relab = {i: sub[n] for i, n in enumerate(axis)}
            # keep n-labels for fit/holdout split: reindex but split on true n
            fit_terms = [sub[n] for n in axis if n <= FIT_MAX_N]
            # simplest: shift axis to consecutive ints keyed by true n order
            packed = {i: sub[axis[i]] for i in range(len(axis))}
            # emulate split: indices with axis[i] <= 22 are fit
            class _:
                pass
            # rebuild dict keyed by index but use FIT split manually:
            split = max(i for i in range(len(axis)) if axis[i] <= FIT_MAX_N)
            terms = {i: packed[i] for i in packed}
            # temporarily fake FIT_MAX_N in index space
            global_fit = split
            seq = {i: terms[i] for i in terms}
            # inline: reuse try_column on index axis with FIT boundary=split
            fit = [terms[i] for i in range(split + 1)]
            hold = [terms[i] for i in range(split + 1, len(axis))]
            done = False
            for order in range(1, 13):
                if len(fit) < 2 * order:
                    break
                coef = solve_rec(fit, order)
                if coef is None:
                    continue
                hist = list(fit)
                ok = True
                for v in hold:
                    pred = sum(coef[j - 1] * Fraction(hist[-j])
                               for j in range(1, order + 1))
                    if pred != v:
                        ok = False
                        break
                    hist.append(v)
                if ok:
                    print("  H=%d (even-n subseq): ORDER %d fit(%d terms) "
                          "holdout %d/%d ALL PASS" % (H, order, len(fit),
                                                      len(hold), len(hold)))
                    print("     coeffs: %s" % [str(c) for c in coef])
                    done = True
                    break
                else:
                    print("  H=%d (even-n subseq): order %d fits but FAILS "
                          "holdout" % (H, order))
            if not done and order:
                if not done:
                    print("  H=%d (even-n subseq): no order<=12 recurrence "
                          "fits (%d fit terms)" % (H, len(fit)))
        else:
            try_column("H=%d" % H, col)

if __name__ == '__main__':
    main()
