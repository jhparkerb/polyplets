#!/usr/bin/env python3
"""Lemma 2 of results/hv-growth-sandwich.md, measured.

An HV-convex king animal factors into three consecutive runs of columns by the
two unimodality phases: a run in which the bottoms only fall and the tops only
rise (heights nondecreasing), a middle run in which both boundaries move the
same way (a staircase animal, or its vertical mirror), and a run in which the
bottoms only rise and the tops only fall (heights nonincreasing). The proof
needs the two outer runs to carry NO exponential entropy, so that the growth
constant is the middle run's alone.

The outer class, standalone, is: column intervals with heights
h_1 >= h_2 >= ... >= h_k >= 1 summing to n, weighted by the number of vertical
offsets, prod_j (h_j - h_{j+1} + 1). (The other outer run is this one read
right to left, so one computation settles both.) Lemma 2 says its count P(n)
is e^{O(sqrt n)}; this script measures P(n)^(1/n) -> 1.

Also checks the factorization inequality
    A(n) <= 2 (n+1)^2 sum_{i+j+l=n} P(i) M(j) P(l)
on the range where A (HV-convex, results/mk_grid20_n14.txt) and M (staircase,
build/middle_kingdom_tm stair) are both on disk.

RED control: the same DP with the offset count wrong (h_j - h_{j+1} + 2) must
diverge from the brute force. Both are checked against a direct enumeration
over height sequences for n <= 12 before anything is reported.

Usage: python3 experiments/monotone_block_growth.py [--nmax 400]
"""
import argparse
import sys
from functools import lru_cache


def brute(nmax, bump=1):
    """Direct enumeration over nonincreasing height sequences. O(partitions)."""
    out = [0] * (nmax + 1)

    @lru_cache(maxsize=None)
    def rec(remaining, first):
        """Weighted count of runs of total area `remaining` starting at `first`."""
        if remaining == first:
            total = 1
        else:
            total = 0
        for nxt in range(1, first + 1):
            if remaining - first >= nxt:
                total += (first - nxt + bump) * rec(remaining - first, nxt)
        return total

    for n in range(1, nmax + 1):
        out[n] = sum(rec(n, h) for h in range(1, n + 1))
    rec.cache_clear()
    return out


def dp(nmax, bump=1):
    """Same count in O(n^2) via prefix sums over the previous column height."""
    # g[m] is a list indexed by first-column height h, for total area m.
    g = [[0] * (nmax + 2) for _ in range(nmax + 1)]
    s1 = [None] * (nmax + 1)   # prefix sums of g[m]
    s2 = [None] * (nmax + 1)   # prefix sums of h * g[m]
    out = [0] * (nmax + 1)
    for n in range(1, nmax + 1):
        row = g[n]
        for h in range(1, n + 1):
            m = n - h
            if m == 0:
                row[h] = 1
                continue
            hi = min(h, m)
            # sum_{h'<=hi} (h - h' + bump) g[m][h']
            row[h] = (h + bump) * s1[m][hi] - s2[m][hi]
        out[n] = sum(row[1:n + 1])
        # prefix sums for later use as a suffix block
        a1, a2 = [0] * (nmax + 2), [0] * (nmax + 2)
        for h in range(1, nmax + 1):
            a1[h] = a1[h - 1] + row[h]
            a2[h] = a2[h - 1] + h * row[h]
        s1[n], s2[n] = a1, a2
    return out


def read_terms(path):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                vals.append(int(line.split()[-1]))
    return vals


HV14 = [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
        2677214, 8389720]
STAIR14 = [1, 3, 9, 28, 87, 272, 850, 2659, 8318, 26025, 81427, 254777,
           797175, 2494307]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=400)
    args = ap.parse_args()

    ok = brute(12)
    got = dp(12)
    assert got[1:] == ok[1:], f"DP disagrees with brute force: {got[1:]} vs {ok[1:]}"
    print(f"ok   DP == brute force, n<=12: {ok[1:9]}")
    red_b, red_d = brute(12, bump=2), dp(12, bump=2)
    assert red_d[1:] == red_b[1:], "RED control DP/brute disagree"
    assert red_b[1:] != ok[1:], "RED control MUST diverge from the real weight"
    print(f"ok   RED (offset count +1 too many) diverges: {red_b[1:9]}")

    P = dp(args.nmax)
    print(f"\n## P(n)^(1/n) for the monotone-height block "
          f"(Lemma 2 says -> 1)")
    for n in [10, 20, 50, 100, 200, 300, args.nmax]:
        if n <= args.nmax:
            print(f"  n={n:5d}  P(n)={P[n]:.6g}  P(n)^(1/n)={P[n] ** (1.0 / n):.6f}"
                  f"  log P(n)/sqrt(n)="
                  f"{__import__('math').log(P[n]) / n ** 0.5:.4f}")

    print("\n## factorization inequality "
          "A(n) <= 2 (n+1)^2 sum P(i) M(j) P(l),  n <= 14")
    M = [1] + STAIR14          # M(0) = 1, empty middle
    Q = [1] + P[1:15]          # P(0) = 1, empty outer run
    bad = []
    for n in range(1, 15):
        tot = 0
        for i in range(n + 1):
            for j in range(n - i + 1):
                tot += Q[i] * M[j] * Q[n - i - j]
        rhs = 2 * (n + 1) ** 2 * tot
        if HV14[n - 1] > rhs:
            bad.append(n)
        print(f"  n={n:2d}  A={HV14[n-1]:12d}  bound={rhs:18d}"
              f"  {'OK' if HV14[n-1] <= rhs else 'VIOLATED'}")
    if bad:
        print(f"FAIL: inequality violated at n={bad}")
        return 1
    print("ok   inequality holds on every n checked")
    return 0


if __name__ == '__main__':
    sys.exit(main())
