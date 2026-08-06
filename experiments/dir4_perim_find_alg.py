#!/usr/bin/env python3
"""Phase 2b: the exact algebraic equation for (dir4, HV-convex) by semiperimeter.

build/prec_guess's `alg` mode works mod p and prints only a rank. It reports
nullity 1 in the box (K, L) = (4, 22) for
results/mk_dir4_perim_terms_s200.txt, so the annihilating relation

    sum_{j=0..4} q_j(t) F(t)^j = 0,   deg q_j <= 22,   F = sum_{s>=2} a(s) t^s

is unique up to scale and can be recovered exactly over Q. This does that,
with the same holdout discipline find_prec uses (fit on the first
unknowns + 4 rows, then require the fit to annihilate every later row), and
re-verifies the result by multiplying the series out over the integers.

  usage:  experiments/dir4_perim_find_alg.py [K] [L] [terms_file]
  target: gympie, local, single-threaded
  cost:   measured ~10 s at (4,22); see results/dir4_perim_find_alg.log
"""
import os
import sys
import time
from fractions import Fraction as F
from math import gcd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "results", "mk_dir4_perim_terms_s200.txt")


def read_terms(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(int(line.split()[-1]))
    return out


def powers(a, M, K):
    """pw[j] = coefficients of F^j mod t^(M+1), F = sum_{n=1..M} a[n] t^n."""
    pw = [[0] * (M + 1) for _ in range(K + 1)]
    pw[0][0] = 1
    for j in range(1, K + 1):
        prev = pw[j - 1]
        cur = pw[j]
        for u in range(M + 1):
            c = prev[u]
            if not c:
                continue
            for v in range(1, M + 1 - u):
                if a[v]:
                    cur[u + v] += c * a[v]
    return pw


def solve(rows, C, train):
    """Exact RREF over Q on the first `train` rows; return the nullspace
    vectors that also annihilate every remaining row."""
    A = [[F(x) for x in r] for r in rows[:train]]
    piv = []
    ri = 0
    for col in range(C):
        p = next((r for r in range(ri, len(A)) if A[r][col] != 0), None)
        if p is None:
            continue
        A[ri], A[p] = A[p], A[ri]
        inv = A[ri][col]
        A[ri] = [x / inv for x in A[ri]]
        for r in range(len(A)):
            if r != ri and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[ri])]
        piv.append((ri, col))
        ri += 1
        if ri == len(A):
            break
    pivcols = {c for _, c in piv}
    out = []
    for fv in (c for c in range(C) if c not in pivcols):
        sol = [F(0)] * C
        sol[fv] = F(1)
        for r, col in piv:
            sol[col] = -sum(A[r][c] * sol[c] for c in range(C) if c not in pivcols)
        if all(sum(rw[c] * sol[c] for c in range(C)) == 0 for rw in rows[train:]):
            out.append(sol)
    return out


def primitive(sol):
    den = 1
    for x in sol:
        den = den * x.denominator // gcd(den, x.denominator)
    ints = [int(x * den) for x in sol]
    g = 0
    for x in ints:
        g = gcd(g, abs(x))
    return [x // g for x in ints] if g else ints


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    L = int(sys.argv[2]) if len(sys.argv) > 2 else 22
    path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT
    seq = read_terms(path)
    M = len(seq)
    a = [0] + seq
    C = (K + 1) * (L + 1)
    train = C + 4
    print(f"series={os.path.basename(path)} terms={M} box=({K},{L}) "
          f"unknowns={C} rows={M+1} train={train} holdout={M+1-train}")
    t0 = time.time()
    pw = powers(a, M, K)
    rows = []
    for m in range(M + 1):
        row = [0] * C
        for j in range(K + 1):
            for l in range(min(L, m) + 1):
                row[j * (L + 1) + l] = pw[j][m - l]
        rows.append(row)
    sols = solve(rows, C, train)
    dt = time.time() - t0
    if not sols:
        print(f"NO ALGEBRAIC RELATION in box ({K},{L})  [{dt:.1f}s]")
        return 1
    print(f"FOUND {len(sols)} relation(s) surviving the holdout  [{dt:.1f}s]")
    q = primitive(sols[0])
    bad = sum(1 for r in rows
              if sum(r[c] * q[c] for c in range(C) if q[c]) != 0)
    print(f"rows failing over Z: {bad} of {M+1}")
    for j in range(K + 1):
        cs = q[j * (L + 1):(j + 1) * (L + 1)]
        terms = " + ".join(f"{c}*t^{l}" for l, c in enumerate(cs) if c)
        print(f"  q_{j}(t) = {terms if terms else 0}")
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
