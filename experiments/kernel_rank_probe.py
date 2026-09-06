#!/usr/bin/env python3
"""Adversarial check of the finite-rank criterion in
results/subclasses.md.

The criterion says: for a 1D column-profile family counted by AREA, write
K(h, h') for the number of ways a column of height h' may follow one of height
h.  If K has finite rank as an infinite matrix, Temperley closes to a finite
linear system and the generating function is rational; if K couples the two
heights through an order relation / min / max, K has infinite rank and nothing
closes.

This script measures both halves on the kernels the repo actually cites:

  1. the rank of the N x N truncation of K, for N = 2..12 (exact, over Q);
  2. the area sequence the kernel generates, by the obvious DP
     (F_{h'}(n) = sum_h K(h,h') F_h(n-h'), one column seeded per height);
  3. whether that sequence satisfies a constant-coefficient recurrence of
     order <= 8 -- fitted on the first rows, REQUIRED to predict the rest.

No compute of any size: everything below runs in well under a second.
Read-only, writes nothing.
"""
from fractions import Fraction
import argparse

NMAX = 40


def rank(rows):
    """Exact rank of a list of lists of Fractions."""
    rows = [list(map(Fraction, r)) for r in rows]
    n = len(rows)
    m = len(rows[0]) if n else 0
    r = 0
    for c in range(m):
        piv = next((i for i in range(r, n) if rows[i][c] != 0), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pr = rows[r]
        for i in range(n):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / pr[c]
                rows[i] = [a - f * b for a, b in zip(rows[i], pr)]
        r += 1
        if r == n:
            break
    return r


def area_series(K, nmax=NMAX):
    """a(n) for the column-profile family with kernel K, counted by area."""
    # F[h][n]
    F = [[0] * (nmax + 1) for _ in range(nmax + 2)]
    for h in range(1, nmax + 1):
        F[h][h] = 1
    for n in range(1, nmax + 1):
        for hp in range(1, n + 1):
            if n - hp < 1:
                continue
            s = 0
            for h in range(1, n - hp + 1):
                k = K(h, hp)
                if k:
                    s += k * F[h][n - hp]
            F[hp][n] += s
    return [sum(F[h][n] for h in range(1, n + 1)) for n in range(1, nmax + 1)]


def cfinite(seq, maxorder=8):
    """Smallest order <= maxorder of a constant-coefficient recurrence that is
    fitted on the first rows and predicts every later term, or None."""
    for r in range(1, maxorder + 1):
        # fit on rows r..2r-1 (r equations, r unknowns), predict the rest
        rows = [[Fraction(seq[n - 1 - i]) for i in range(1, r + 1)] + [Fraction(seq[n - 1])]
                for n in range(r + 1, 2 * r + 1)]
        sol = solve(rows, r)
        if sol is None:
            continue
        ok = True
        for n in range(2 * r + 1, len(seq) + 1):
            pred = sum(sol[i - 1] * seq[n - 1 - i] for i in range(1, r + 1))
            if pred != seq[n - 1]:
                ok = False
                break
        if ok:
            return r, sol
    return None


def solve(aug, nvar):
    """Gaussian elimination on an augmented system; None if not uniquely solvable."""
    m = [list(row) for row in aug]
    n = len(m)
    piv = []
    r = 0
    for c in range(nvar):
        p = next((i for i in range(r, n) if m[i][c] != 0), None)
        if p is None:
            return None
        m[r], m[p] = m[p], m[r]
        pr = m[r]
        for i in range(n):
            if i != r and m[i][c] != 0:
                f = m[i][c] / pr[c]
                m[i] = [a - f * b for a, b in zip(m[i], pr)]
        piv.append(c)
        r += 1
        if r == n:
            break
    if r < nvar:
        return None
    return [m[i][nvar] / m[i][piv[i]] for i in range(nvar)]


def _partitions(nmax):
    p = [0] * (nmax + 2)
    p[0] = 1
    for k in range(1, nmax + 2):
        for n in range(k, nmax + 2):
            p[n] += p[n - k]
    return p


PART = _partitions(NMAX + 4)

KERNELS = [
    ("h+h'+1   column-convex polyplets (A187077)", lambda h, hp: h + hp + 1),
    ("h+h'-1   column-convex polyominoes (Klarner)", lambda h, hp: h + hp - 1),
    ("h+2      4-cone column-convex (A018902)", lambda h, hp: h + 2),
    ("h+1      bottoms nondecreasing (A007052)", lambda h, hp: h + 1),
    ("1        bargraphs (compositions)", lambda h, hp: 1),
    ("min+1    staircase (A225114)", lambda h, hp: min(h, hp) + 1),
    ("[h'<=h]  Ferrers (A000041)", lambda h, hp: 1 if hp <= h else 0),
    ("[|h-h'|<=1] banded", lambda h, hp: 1 if abs(h - hp) <= 1 else 0),
    # RANK 1 AND NOT RATIONAL: the hypothesis the criterion leaves implicit.
    # Finite rank closes Temperley to a finite system, but the system's entries
    # are sum_h x^h f_i(h) g_j(h) -- rational only if the factors are.
    ("p(h)     rank 1, non-polynomial factor", lambda h, hp: PART[h]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=NMAX)
    args = ap.parse_args()
    print(f"{'kernel':<44} {'rank of NxN truncation, N=2..12':<34} first terms / C-finite")
    for name, K in KERNELS:
        ranks = [rank([[K(h, hp) for hp in range(1, N + 1)] for h in range(1, N + 1)])
                 for N in range(2, 13)]
        seq = area_series(K, args.nmax)
        cf = cfinite(seq)
        verdict = (f"order {cf[0]}: {[str(c) for c in cf[1]]}" if cf
                   else f"no recurrence of order <= 8 on {args.nmax} terms")
        print(f"{name:<44} {str(ranks):<34} {seq[:10]}")
        print(f"{'':<44} {'':<34} {verdict}")


if __name__ == "__main__":
    raise SystemExit(main())
