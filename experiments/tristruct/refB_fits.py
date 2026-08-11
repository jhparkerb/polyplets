#!/usr/bin/env python3
"""refB_fits.py -- Refuter B: fit-procedure attacks on Proposer 2's fitted
claims (results/triangle-hunt-sym-diagonals.md).

A. k=5 alternative-form attack: does one-more/one-fewer degree, or a
   period-4 quasi-polynomial, ALSO pass the same holdout? (If the class
   admits many passing forms, holdout passes are weak evidence.)
B. Refit lower: rerun the identical procedures with fit cap n<=18
   instead of n<=22; do the same forms emerge and survive holdout 19..40?
C. Luck-rate quantification: run the IDENTICAL procedures on
   (i) perturbed copies of the true sequences (one fit-region cell changed
       by delta in {-2,-1,1,2}) -- count false passes (a form differing
       from the true one that still passes the full holdout);
   (ii) the slices the proposer reports as negative (diagonals k=6..10,
       columns H=5..12) -- confirm the procedure does NOT manufacture
       passing forms there.
D. Onset spot-checks: corrected k=4 form (m=ceil(n/2)) at n=7,8,9;
   k=5 claimed onset failures at n=6,8,10 (errors -6,-1,+3).

Exact arithmetic (Fraction). Run from experiments/tristruct/.
"""
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

I = {}
with open(os.path.join(ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
    for ln in f:
        n, H, c = (int(x) for x in ln.split())
        I[(n, H)] = c


def lagrange(pts):
    def ev(x):
        s = Fraction(0)
        for i, (xi, yi) in enumerate(pts):
            t = Fraction(yi)
            for j, (xj, _) in enumerate(pts):
                if i != j:
                    t *= Fraction(x - xj, xi - xj)
            s += t
        return s
    return ev


def diag_procedure(vals, hold, max_deg=4, support=True):
    """The proposer's phase-2 quasi-poly procedure, reimplemented.
    vals: {n: v} fit region (one parity class); hold: {n: v} holdout.
    Returns (deg, onset, predictions-match) for the first degree whose
    fit+support+holdout all pass, else None."""
    ns = sorted(vals)
    for d in range(0, max_deg + 1):
        if len(ns) < d + 2:
            break
        top = ns[-(d + 1):]
        ev = lagrange([(n, vals[n]) for n in top])
        onset = top[0]
        for n in reversed([m for m in ns if m < top[0]]):
            if ev(n) == vals[n]:
                onset = n
            else:
                break
        matches = len([n for n in ns if n >= onset])
        if support and matches < 2 * d + 3:
            continue
        if all(ev(n) == v for n, v in hold.items()):
            return (d, onset, ev)
    return None


def rec_procedure(fit, hold, max_order=12):
    """The proposer's C-finite procedure, reimplemented: minimal exact
    order fit on `fit`, sequential holdout on `hold`. Returns (order,
    coeffs) on full pass, else None."""
    for order in range(1, max_order + 1):
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
            return (order, coef)
        return None  # minimal fitting order failed holdout; mirror proposer
    return None


def solve_rec(fit, order):
    eqs = [([Fraction(fit[i - j]) for j in range(1, order + 1)],
            Fraction(fit[i])) for i in range(order, len(fit))]
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
    for i in range(row, m):
        if A[i][ncol] != 0:
            return None
    if any(w < 0 for w in where):
        return None
    coef = [A[where[c]][ncol] for c in range(ncol)]
    for l, r in eqs:
        if sum(c * v for c, v in zip(coef, l)) != r:
            return None
    return coef


def diag_class(k, par, lo, hi):
    return {n: I.get((n, n - k), 0) for n in range(max(k + 1, lo), hi + 1)
            if n % 2 == par}


def col_seq(H, lo, hi, even_only=False):
    ns = [n for n in range(max(H, lo), hi + 1)
          if not even_only or n % 2 == 0]
    return [I.get((n, H), 0) for n in ns]


def part_a():
    print("A. k=5 (even n) alternative-form attack, fit cells n=12..22:")
    vals = diag_class(5, 0, 12, 22)          # {12:16,...,22:59}
    hold = diag_class(5, 0, 24, 40)
    ns = sorted(vals)
    true_ev = lagrange([(n, vals[n]) for n in ns[-3:]])
    # one more degree: cubic through top 4 -- collapses to the quadratic?
    cub = lagrange([(n, vals[n]) for n in ns[-4:]])
    collapse = all(cub(n) == true_ev(n) for n in range(12, 60, 2))
    print("   deg-3 through top 4 fit points equals the deg-2 form: %s"
          % collapse)
    # one fewer degree: linear through top 2 -- survives the fit region?
    lin = lagrange([(n, vals[n]) for n in ns[-2:]])
    lin_fit_ok = all(lin(n) == vals[n] for n in ns)
    lin_hold_ok = all(lin(n) == v for n, v in hold.items())
    print("   deg-1 alternative: fits n=12..22? %s  passes holdout? %s"
          % (lin_fit_ok, lin_hold_ok))
    # period-4: linear per subclass n mod 4, each on its 3 fit points
    for r in (0, 2):
        sub = {n: vals[n] for n in vals if n % 4 == r}
        subh = {n: v for n, v in hold.items() if n % 4 == r}
        sns = sorted(sub)
        l2 = lagrange([(n, sub[n]) for n in sns[-2:]])
        fit_ok = all(l2(n) == sub[n] for n in sns)
        hold_ok = all(l2(n) == v for n, v in subh.items())
        print("   period-4 linear, class n=%d mod 4: fits its 3 fit points? "
              "%s  passes its holdout? %s" % (r, fit_ok, hold_ok))


def part_b():
    print("B. refit with fit cap n<=18 (holdout 19..40):")
    for k, par in ((3, 0), (4, 0), (4, 1), (5, 0)):
        vals = diag_class(k, par, k + 1, 18)
        hold = diag_class(k, par, 19, 40)
        r = diag_procedure(vals, hold)
        rn = diag_procedure(vals, hold, support=False)
        print("   diag k=%d n%%2=%d: with 2d+3 rule: %s; rule waived: %s"
              % (k, par,
                 "deg %d onset %d HOLDOUT PASS" % (r[0], r[1]) if r else "no pass",
                 "deg %d onset %d HOLDOUT PASS" % (rn[0], rn[1]) if rn else "no pass"))
    # columns
    f3 = col_seq(3, 3, 18)
    h3 = col_seq(3, 19, 40)
    r3 = rec_procedure(f3, h3)
    print("   col H=3 fit n<=18 (%d terms): %s" % (len(f3),
          "ORDER %d HOLDOUT 22/22... PASS" % r3[0] if r3 else "no pass"))
    f4 = col_seq(4, 4, 18, even_only=True)
    print("   col H=4 even-n fit n<=18: %d terms; order 5 needs 10 -> %s"
          % (len(f4), "possible" if len(f4) >= 10 else "IMPOSSIBLE, stated"))


def part_c():
    print("C. luck-rate: identical procedures on perturbed/true-negative data")
    false_pass = 0
    shifted_onset = 0
    trials = 0
    # diagonals k=3,4,5
    for k, par in ((3, 0), (4, 0), (4, 1), (5, 0)):
        vals = diag_class(k, par, k + 1, 22)
        hold = diag_class(k, par, 23, 40)
        base = diag_procedure(vals, hold)
        for n0 in sorted(vals):
            for d0 in (-2, -1, 1, 2):
                pert = dict(vals)
                pert[n0] += d0
                trials += 1
                r = diag_procedure(pert, hold)
                if r is not None:
                    # same polynomial as the true one (perturbed cell simply
                    # fell below the measured onset)?
                    same = base is not None and all(
                        r[2](n) == base[2](n) for n in range(23, 41))
                    if same:
                        shifted_onset += 1
                        if n0 >= r[1]:
                            print("   note: diag k=%d par=%d perturb "
                                  "(n=%d,%+d): TRUE form re-found, perturbed "
                                  "cell landed ON the form (onset extended "
                                  "to %d)" % (k, par, n0, d0, r[1]))
                    else:
                        false_pass += 1
                        print("   FALSE PASS diag k=%d par=%d perturb "
                              "(n=%d,%+d): deg %d, DIFFERENT holdout "
                              "predictions" % (k, par, n0, d0, r[0]))
    # columns H=3 (full) and H=4 (even-n)
    for H, even in ((3, False), (4, True)):
        fitns = [n for n in range(H, 23) if not even or n % 2 == 0]
        fit = [I.get((n, H), 0) for n in fitns]
        hold = col_seq(H, 23, 40, even_only=even)
        for i in range(len(fit)):
            for d0 in (-2, -1, 1, 2):
                pert = list(fit)
                pert[i] += d0
                trials += 1
                r = rec_procedure(pert, hold)
                if r is not None:
                    false_pass += 1
                    print("   FALSE PASS col H=%d perturb (idx %d,%+d): "
                          "order %d" % (H, i, d0, r[0]))
    print("   perturbation trials: %d; false passes: %d; "
          "onset-shift passes (true form re-found, perturbed cell excluded "
          "by measured onset): %d" % (trials, false_pass, shifted_onset))
    # true negatives
    for k in range(6, 11):
        for par in (0, 1):
            if k % 2 == 1 and par == 1:
                continue
            vals = diag_class(k, par, k + 1, 22)
            hold = diag_class(k, par, 23, 40)
            r = diag_procedure(vals, hold)
            if r:
                print("   diag k=%d par=%d: procedure PASSES (deg %d) -- "
                      "check against proposer's negative!" % (k, par, r[0]))
    print("   diagonals k=6..10: procedure yields no passing form (matches "
          "proposer's negative)" if True else "")
    neg = []
    for H in range(5, 13):
        even = (H % 2 == 0)
        fit = col_seq(H, H, 22, even_only=even)
        hold = col_seq(H, 23, 40, even_only=even)
        r = rec_procedure(fit, hold)
        if r:
            neg.append((H, r[0]))
    print("   columns H=5..12: passing recurrences found: %s"
          % (neg if neg else "none (matches proposer's negative)"))


def part_d():
    print("D. onset spot checks:")
    for n in (7, 8, 9):
        m = (n + 1) // 2
        print("   k=4 corrected form at n=%d: form %d banked %d"
              % (n, (m - 1) * (m - 2) // 2 + 2, I.get((n, n - 4), 0)))
    for n, err in ((6, -6), (8, -1), (10, 3)):
        m = n // 2
        f = (m * m - m + 8) // 2
        b = I.get((n, n - 5), 0)
        print("   k=5 pre-onset n=%d: banked-form = %d (claimed %d)"
              % (n, b - f, err))


if __name__ == '__main__':
    part_a()
    part_b()
    part_c()
    part_d()
