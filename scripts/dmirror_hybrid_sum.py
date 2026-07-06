#!/usr/bin/env python3
"""Hybrid dmirror total: direct strips S <= SMAX + pinned quasi-polynomial
closed forms for the sparse strips S > SMAX (the strips whose frontier is
RAM-infeasible but whose counts sit on pinned diagonals d(S,S+k), k small).

    D(n) = sum_{S<=SMAX} d(S, n)_direct + sum_{S>SMAX} P_{n-S}^{parity(S)}(S)

Every P_k used must be PINNED (exact differencing + holdout + forward
confirmation — results/dmirror-diagonals.md); the script hard-refuses if a
needed (k, parity) class is not in its table. This is the T3 (conjecture-
assisted) step of the n=33 companions: exact computation composed with
empirically pinned but unproven formulas.

Usage: dmirror_hybrid_sum.py MAXN SMAX SYMDIR     e.g. 33 28 runs/sym33
Writes SYMDIR/dmirror.out (n D(n) lines, n=1..MAXN) after validating:
  - all strips S=1..SMAX present, each covering n=S..MAXN;
  - closed forms reproduce every DIRECT strip's in-regime diagonal cell
    (cross-check on the overlap before trusting them off the edge).
"""
import glob
import os
import re
import sys
from fractions import Fraction as F

# Pinned classes only (results/dmirror-diagonals.md, pinned 2026-07-05/06;
# P_5 even is pinned, P_5 odd is FITTED -> deliberately absent).
PINNED = {
    (0, 0): [2], (0, 1): [2],
    (1, 0): [6, 1], (1, 1): [7, 1],
    (2, 0): [12, 7, F(1, 2)], (2, 1): [F(27, 2), 6, F(1, 2)],
    (3, 0): [50, F(40, 3), 3, F(1, 6)],
    (3, 1): [F(93, 2), F(83, 6), F(7, 2), F(1, 6)],
    (4, 0): [180, 33, F(28, 3), F(3, 2), F(1, 24)],
    (4, 1): [F(1367, 8), F(119, 3), F(97, 12), F(4, 3), F(1, 24)],
    (5, 0): [570, F(2278, 15), F(55, 3), 4, F(5, 12), F(1, 120)],
}
ONSET = lambda k, par: 2 * k + 2 + par


def peval(coeffs, S):
    v = F(0)
    for i, c in enumerate(coeffs):
        v += F(c) * S ** i
    assert v.denominator == 1, (coeffs, S)
    return int(v)


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: dmirror_hybrid_sum.py MAXN SMAX SYMDIR")
    maxn, smax, symdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

    strips = {}
    for f in glob.glob(os.path.join(symdir, "dmirror.S*.out")):
        S = int(re.search(r"S(\d+)\.out$", f).group(1))
        d = {}
        for ln in open(f):
            a, b = ln.split()
            d[int(a)] = int(b)
        strips[S] = d
    missing = [S for S in range(1, smax + 1) if S not in strips]
    if missing:
        sys.exit(f"REFUSE: missing direct strips {missing}")
    for S in range(1, smax + 1):
        want = set(range(S, maxn + 1)) if 2 * S >= S else None
        have = set(strips[S])
        need = {n for n in range(S, maxn + 1) if n <= S * S}  # bbox cap
        if not need <= have:
            sys.exit(f"REFUSE: strip S={S} missing n={sorted(need - have)}")

    # cross-check closed forms against every in-regime DIRECT cell
    ok = 0
    for S in range(1, smax + 1):
        for k in range(0, 6):
            par = S % 2
            if (k, par) not in PINNED or S < ONSET(k, par):
                continue
            n = S + k
            if n > maxn or n not in strips[S]:
                continue
            got, want = strips[S][n], peval(PINNED[(k, par)], S)
            if got != want:
                sys.exit(f"REFUSE: P_{k} {par} at S={S}: direct {got} != poly {want}")
            ok += 1
    print(f"closed forms reproduce {ok} in-regime direct cells")

    total = {n: 0 for n in range(1, maxn + 1)}
    for S in range(1, smax + 1):
        for n, v in strips[S].items():
            if n <= maxn:
                total[n] += v
    injected = 0
    for S in range(smax + 1, maxn + 1):
        for n in range(S, maxn + 1):
            k, par = n - S, S % 2
            if (k, par) not in PINNED:
                sys.exit(f"REFUSE: need unpinned P_{k} parity {par} for S={S},n={n}")
            if S < ONSET(k, par):
                sys.exit(f"REFUSE: S={S} below onset for k={k} parity {par}")
            total[n] += peval(PINNED[(k, par)], S)
            injected += 1
    print(f"injected {injected} closed-form strip cells (S={smax+1}..{maxn})")

    out = os.path.join(symdir, "dmirror.out")
    with open(out, "w") as f:
        for n in range(1, maxn + 1):
            f.write(f"{n} {total[n]}\n")
    print(f"wrote {out}; D({maxn}) = {total[maxn]}")


if __name__ == "__main__":
    main()
