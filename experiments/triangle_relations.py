#!/usr/bin/env python3
"""Hunt for independent recurrences in the polyplet triangle T(n,H).

T(n,H) = # polyplets of n cells with bounding-box height exactly H.
a(n) = sum_H T(n,H). Full triangle banked in results/ns_a36/perheight/h{H}.out
(each file lists `n  T(n,H)`; frontier a(36); ns_a35/ also present as fallback).

Goal: find relationships that let a column (or the whole triangle) be recomputed
a *second* way -- independent of the kink transfer-matrix sweep -- for validation.

This script:
  (1) loads the full 36-row triangle, checks row sums == a(n);
  (2) per column H, finds the MINIMAL constant-coefficient linear recurrence the
      data supports, i.e. smallest d with c_1..c_d s.t.
          T(n,H) = sum_j c_j T(n-j,H)   for all n,
      fit from the first 2d windows and VALIDATED on every remaining term.
      Reports order d_H and how many held-out terms confirm it.
"""
import glob, os, sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NMAX = 36

def load_triangle():
    T = {}  # (n,H) -> int
    for H in range(1, NMAX + 1):
        f = os.path.join(ROOT, f"results/ns_a36/perheight/h{H}.out")
        if not os.path.exists(f):
            continue
        with open(f) as fh:
            for line in fh:
                p = line.split()
                if len(p) >= 2:
                    T[(int(p[0]), H)] = int(p[1])
    return T

def col_seq(T, H):
    """Nonzero-onward sequence for column H: T(H,H), T(H+1,H), ... up to NMAX."""
    return [T.get((n, H), 0) for n in range(H, NMAX + 1)]

def solve_exact(A, b):
    """Solve A x = b exactly over Fractions; return x or None if singular."""
    m = len(A)
    M = [[F(A[i][j]) for j in range(m)] + [F(b[i])] for i in range(m)]
    for col in range(m):
        piv = next((r for r in range(col, m) if M[r][col] != 0), None)
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        inv = F(1) / M[col][col]
        M[col] = [x * inv for x in M[col]]
        for r in range(m):
            if r != col and M[r][col] != 0:
                fac = M[r][col]
                M[r] = [a - fac * bb for a, bb in zip(M[r], M[col])]
    return [M[i][m] for i in range(m)]

def find_min_recurrence(seq, max_order=None):
    """Smallest d with a constant-coeff linear recurrence fit from the earliest
    d equations and confirmed on ALL later terms. Returns (d, coeffs, n_holdout)
    or None if the sequence is too short to pin any recurrence with >=2 holdouts."""
    L = len(seq)
    if max_order is None:
        max_order = L // 2
    for d in range(1, max_order + 1):
        # Need d equations to fit (rows n=d..2d-1 using indices), plus holdout.
        if L < 2 * d + 2:  # require >=2 held-out confirmations
            return None
        A = [[seq[i - 1 - j] for j in range(d)] for i in range(d, 2 * d)]
        b = [seq[i] for i in range(d, 2 * d)]
        c = solve_exact(A, b)
        if c is None:
            continue
        # Validate on every remaining term.
        ok = True
        holdout = 0
        for i in range(2 * d, L):
            pred = sum(c[j] * seq[i - 1 - j] for j in range(d))
            if pred != seq[i]:
                ok = False
                break
            holdout += 1
        if ok and holdout >= 2:
            return (d, c, holdout)
    return None

def main():
    T = load_triangle()
    # (1) row-sum check
    print("== row-sum check (T sums vs a(n)) ==")
    bad = 0
    afile = os.path.join(ROOT, "results/ns_a36/triangle.txt")
    a = {}
    with open(afile) as fh:
        for line in fh:
            p = line.split()
            if len(p) >= 2:
                a[int(p[0])] = int(p[1])
    for n in range(1, NMAX + 1):
        s = sum(T.get((n, H), 0) for H in range(1, n + 1))
        if s != a.get(n):
            print(f"  MISMATCH n={n}: sum={s} a={a.get(n)}")
            bad += 1
    print(f"  {'all rows OK' if bad==0 else str(bad)+' bad'} (n=1..{NMAX})")

    # (2) per-column minimal recurrence
    print()
    print("== per-column minimal linear recurrence (fit early, confirm on rest) ==")
    print("  H  terms  order  holdout   verdict")
    for H in range(1, NMAX + 1):
        seq = col_seq(T, H)
        # strip nothing; seq starts at first nonzero (n=H)
        res = find_min_recurrence(seq)
        if res is None:
            print(f"  {H:2d}  {len(seq):5d}    --      --     too short / no low-order fit")
        else:
            d, c, ho = res
            print(f"  {H:2d}  {len(seq):5d}  {d:5d}  {ho:6d}     recurrence confirmed")

if __name__ == "__main__":
    main()
