#!/usr/bin/env python3
"""Session 03 bonus: directed-convex KING animals = convex king animals whose
phase parse never leaves {(0,0),(1,0)}, i.e. r non-decreasing row by row
(equivalently: the animal contains its bounding box's bottom-right... in our
row order: the top boundary marches monotonically right). King analog of
directed-convex polyominoes. GF = F00(1) + F10(1), explicit in sqrt(Delta)
via the kernel formulas (proved in docs/proofs/convex-box-kernel.md).

Computes the exact box table d(w,h) from the validated transitions, prints
the semiperimeter sequence a_dir(s) = sum_{w+h=s} d(w,h) and the diagonal
d(n,n), for OEIS lookup. Control: same for polyomino mode (directed-convex
polyominoes by semiperimeter = A005817? -- check against OEIS).
"""
import sys, os
from collections import defaultdict

N = 14


def table(king=True):
    dp = [defaultdict(lambda: defaultdict(int)) for _ in range(2)]
    for k in range(1, N + 1):
        dp[0][k][k] = 1
    f = [[0] * (N + 1) for _ in range(N + 1)]

    def collect(dp, h):
        for ph in range(2):
            for k, xs in dp[ph].items():
                for w, c in xs.items():
                    f[w][h] += c

    collect(dp, 1)
    for h in range(2, N + 1):
        nd = [defaultdict(lambda: defaultdict(int)) for _ in range(2)]

        def add(ph, k, w, c):
            if k >= 1 and w <= N:
                nd[ph][k][w] += c

        for k in range(1, N + 1):
            for w, c in dp[0][k].items():
                for u in range(0, N - w + 1):
                    for v in range(0, N - w - u + 1):
                        add(0, k + u + v, w + u + v, c)
                imax = k if king else k - 1
                for i in range(1, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, N - w + 1):
                        add(1, k + e - i, w + e, c)
            for w, c in dp[1][k].items():
                imax = k if king else k - 1
                for i in range(0, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, N - w + 1):
                        add(1, k + e - i, w + e, c)
        dp = nd
        collect(dp, h)
    return f


if __name__ == "__main__":
  N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
  for king in (True, False):
    f = table(king)
    tag = "KING" if king else "POLYOMINO"
    a = []
    for s in range(2, N + 2):
        tot = sum(f[w][s - w] for w in range(max(1, s - N), min(s, N + 1)))
        a.append(tot)
    print(f"{tag} directed-convex semiperimeter a(s), s=2..{N+1}:")
    print("  " + ",".join(map(str, a)))
    print(f"{tag} diagonal d(n,n), n=1..{N}:")
    print("  " + ",".join(str(f[n][n]) for n in range(1, N + 1)))
    print(f"{tag} row d(w,2), w=1..{N}: " +
          ",".join(str(f[w][2]) for w in range(1, N + 1)))
