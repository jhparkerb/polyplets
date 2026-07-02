#!/usr/bin/env python3
"""recurrence_probe.py -- measure the intrinsic linear-algebra complexity of the
T(n,H) triangle along different slicings, on EXISTING data (no compute job).

Idea (thread #2/#4 of the 2026-07-02 boundary-push exploration): the frontier
signature count ~lambda^(H/2) is the cost of our REPRESENTATION. The intrinsic
complexity of a slicing = the minimal linear-recurrence order of that sequence.
If a slicing has low, slowly-growing order, we can extrapolate it cheaply
(compute a few terms, recur the rest) instead of sweeping.

We measure, for existing data (triangle through n=24, +a25 swept rows H3-16):
  - fixed-k diagonals  T(n, n-k)  vs n   (known: poly(n)*3^n -> low C-finite order; sanity)
  - fixed-H rows       T(n, H)    vs n   (the sweep direction; order = ?)
and for each, the minimal C-finite (constant-coeff) recurrence order that fits
ALL available points, plus the dominant characteristic roots (the "eigenvalues"
mu_i(H) / the growth spectrum). Honest about under-determination: if we have
fewer than 2*order+slack points, we report the order as a LOWER BOUND.
"""
import sys, os
from fractions import Fraction

def load_triangle(path):
    T = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        if len(p) == 3 and all(x.lstrip('-').isdigit() for x in p):
            n, H, v = int(p[0]), int(p[1]), int(p[2])
            T[(n, H)] = v
    return T

def load_swept_rows(path, T):
    """a25 swept_rows.txt: ===H<h>=== blocks of 'n value' -> merge into T (extends n to 25)."""
    if not os.path.exists(path):
        return
    h = None
    for line in open(path):
        s = line.strip()
        if s.startswith('===H'):
            h = int(s[4:].rstrip('='))
        elif s and h is not None:
            p = s.split()
            if len(p) == 2 and all(x.lstrip('-').isdigit() for x in p):
                T[(int(p[0]), h)] = int(p[1])

def min_crecurrence_order(seq, max_order=None):
    """Smallest d such that a length-d constant-coeff linear recurrence fits ALL
    of seq (exact rationals). Returns (order, determined_bool, char_roots_or_None).
    determined=False means seq too short to be sure order isn't higher.
    """
    a = [Fraction(x) for x in seq]
    N = len(a)
    if max_order is None:
        max_order = (N - 1) // 2
    for d in range(0, max_order + 1):
        if d == 0:
            if all(x == 0 for x in a):
                return 0, True, []
            continue
        if N < 2 * d:            # not enough eqs to even solve for d coeffs + 1 check
            return d, False, None
        # Solve for c_1..c_d from the first d equations a[i]=sum c_j a[i-j], i=d..2d-1
        # then verify on the rest. Build Hankel system.
        import copy
        # Gaussian elimination over Fractions on the dxd Hankel-ish system
        M = [[a[i - j] for j in range(1, d + 1)] + [a[i]] for i in range(d, 2 * d)]
        c = solve_exact(M, d)
        if c is None:
            continue  # singular at this d; the true order may still be d but this window degenerate -> try treating as not-yet
        ok = True
        for i in range(2 * d, N):
            if sum(c[j] * a[i - 1 - j] for j in range(d)) != a[i]:
                ok = False
                break
        if ok:
            determined = (N >= 2 * d + max(2, d // 2))
            return d, determined, c
    return max_order + 1, False, None

def solve_exact(aug, d):
    """Solve dxd system given as d rows of [coeffs..., rhs] over Fractions. None if singular."""
    M = [row[:] for row in aug]
    for col in range(d):
        piv = None
        for r in range(col, d):
            if M[r][col] != 0:
                piv = r; break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(d):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(d + 1)]
    return [M[r][d] for r in range(d)]

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    T = load_triangle(os.path.join(root, 'results/ns_a24/triangle.txt'))
    load_swept_rows(os.path.join(root, 'results/ns_a25/swept_rows.txt'), T)
    maxn = max(n for n, _ in T)
    print(f"loaded T(n,H), n up to {maxn}, {len(T)} cells\n")

    print("=== FIXED-k DIAGONALS  T(n,n-k) vs n  (sanity: expect low order, root 3) ===")
    for k in range(0, 9):
        seq, ns = [], []
        n = k + 1  # H=n-k>=1
        while (n, n - k) in T:
            seq.append(T[(n, n - k)]); ns.append(n); n += 1
        if len(seq) < 3:
            continue
        d, det, c = min_crecurrence_order(seq)
        print(f" k={k:2d}: {len(seq):2d} pts (n={ns[0]}..{ns[-1]})  order={d}{'' if det else '+ (lower bound)'}")

    print("\n=== FIXED-H ROWS  T(n,H) vs n  (the sweep direction; order = intrinsic cost) ===")
    for H in range(2, maxn):
        seq, ns = [], []
        n = H
        while (n, H) in T:
            seq.append(T[(n, H)]); ns.append(n); n += 1
        if len(seq) < 4:
            continue
        d, det, c = min_crecurrence_order(seq)
        note = '' if det else '  <-- UNDER-DETERMINED (order is a lower bound; need more n)'
        root = dominant_root(c) if (det and c) else None
        rstr = f"  dominant mu_H={root:.4f}" if root else ""
        print(f" H={H:2d}: {len(seq):2d} pts (n={ns[0]}..{ns[-1]})  min C-finite order >= {d}{rstr}{note}")


def dominant_root(c):
    """Largest |root| of x^d - c_1 x^(d-1) - ... - c_d, given c=[c_1..c_d]."""
    try:
        import numpy as np
    except ImportError:
        return None
    d = len(c)
    poly = [1.0] + [-float(x) for x in c]
    r = np.roots(poly)
    return max(abs(z) for z in r)

if __name__ == '__main__':
    main()
