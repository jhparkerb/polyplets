#!/usr/bin/env python3
"""N1 of docs/publication.md: the square-lattice analogue of Proposition 6.

Proposition 6 (results/subclasses.md) says every class between staircase
and HV-convex KING animals has growth constant mu = 3.128943269730886...  The
novelty question is whether the same statement for ordinary polyominoes is
already implicit in the solved models. It is: Bender (1974) gives convex
polyominoes by area the growth constant 2.30914..., and the staircase
(parallelogram) subclass -- A006958, a q-Bessel quotient -- is measured here to
have the same one.

Both series come out of one column transfer with a one-character difference in
the kernel. Attaching a column of height h' to one of height h, with bottoms
nondecreasing (d >= 0) and tops nondecreasing (d >= h - h'):

    square lattice   the columns must SHARE A ROW, d <= h-1   ->  min(h, h')
    king lattice     the columns may touch at a corner, d <= h ->  min(h, h') + 1

so the king staircase kernel is the square one plus one, which is the whole of
the difference between 2.3091... and 3.1289...

Positive controls, both required: the square kernel must reproduce A006958's
banked terms, and the king kernel must reproduce A225114's.

Usage: python3 experiments/square_staircase_area.py [--nmax 400]
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KING_TERMS = os.path.join(ROOT, "results", "mk_stair_terms_n700.txt")
A006958 = [1, 2, 4, 9, 20, 46, 105, 242, 557, 1285, 2964, 6842, 15793, 36463]
BENDER = 2.30914   # convex polyominoes by area, Bender 1974


def staircase_by_area(nmax, bump=0):
    """Staircase animals by area; bump=0 square lattice, bump=1 king."""
    # f[n][h]: runs of area n whose last column has height h.
    f = [[0] * (nmax + 2) for _ in range(nmax + 1)]
    for h in range(1, nmax + 1):
        f[h][h] = 1
    out = [0] * (nmax + 1)
    for n in range(1, nmax + 1):
        row = f[n]
        for h in range(1, n + 1):
            v = row[h]
            if not v:
                continue
            for hp in range(1, nmax - n + 1):
                f[n + hp][hp] += v * (min(h, hp) + bump)
        out[n] = sum(row[1:n + 1])
    return out


def king_banked(path, upto):
    with open(path) as fh:
        return [int(line.split()[1]) for line in fh if line.strip()][:upto]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nmax", type=int, default=400)
    args = ap.parse_args()
    if args.nmax < 20:
        ap.error("--nmax must be at least 20 to say anything about the ratio")

    sq = staircase_by_area(args.nmax)
    king = staircase_by_area(min(args.nmax, 40), bump=1)
    assert sq[1:len(A006958) + 1] == A006958, \
        f"square kernel does not reproduce A006958: {sq[1:15]}"
    print(f"ok   square kernel min(h,h') reproduces A006958: {sq[1:9]} ...")
    want = king_banked(KING_TERMS, len(king) - 1)
    assert king[1:] == want, f"king kernel does not reproduce A225114: {king[1:9]}"
    print(f"ok   king kernel min(h,h')+1 reproduces A225114: {king[1:9]} ...")

    print(f"\n## staircase polyominoes by area, ratio a(n)/a(n-1)")
    for n in [50, 100, 200, 300, args.nmax]:
        if n <= args.nmax:
            print(f"  n={n:4d}  {sq[n] / sq[n - 1]:.15f}")
    ratio = sq[args.nmax] / sq[args.nmax - 1]
    print(f"\nBender's convex-by-area growth constant: {BENDER}")
    print(f"staircase-by-area ratio at n={args.nmax}:     {ratio:.15f}")
    assert abs(ratio - BENDER) < 1e-4, \
        f"staircase ratio {ratio} is not Bender's {BENDER} -- N1's premise fails"
    print("ok   the subclass carries the superclass's exponential growth, so the "
          "square-lattice\n     analogue of Proposition 6 is implicit in the solved "
          "models (docs/publication.md N1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
