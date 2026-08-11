"""p1_ineq_check.py -- Proposer 1: check the two proved injections on OWN
enumerated data and report margins.

Proved (proofs in results/triangle-hunt-proof-first.md):
  (i)  T(n,H) >= 3*T(n-1,H-1)            (walk-cap injection, 3 offsets)
  (ii) T(n,H) >= T(n-1,H)                (grow-right injection, top row)
  combined, images disjoint (top row exactly-1 cell vs >= 2 cells):
       T(n,H) >= 3*T(n-1,H-1) + T(n-1,H)   for 2 <= H <= n-1,
       T(n,n) = 3*T(n-1,n-1)               (equality: pure walk column).

Usage: python3 p1_ineq_check.py data/p1_king_n13.txt
"""
import sys

def main():
    T = {}
    for line in open(sys.argv[1]):
        p = line.split()
        if len(p) == 3 and p[1] != "SUM":
            T[(int(p[0]), int(p[1]))] = int(p[2])
    nmax = max(n for n, _ in T)
    bad = 0
    eq = 0
    worst = None  # smallest slack ratio T/(bound)
    for n in range(2, nmax + 1):
        for H in range(2, n + 1):
            bound = 3 * T.get((n - 1, H - 1), 0) + (T.get((n - 1, H), 0)
                                                    if H <= n - 1 else 0)
            t = T[(n, H)]
            if t < bound:
                bad += 1
                print("VIOLATION at (%d,%d): %d < %d" % (n, H, t, bound))
            elif t == bound:
                eq += 1
            else:
                r = t / bound if bound else float("inf")
                if worst is None or r < worst[0]:
                    worst = (r, n, H)
    print("checked all cells 2<=H<=n<=%d: %d violations, %d equalities "
          "(expected: the H=n column), tightest strict ratio %.4f at (%d,%d)"
          % (nmax, bad, eq, worst[0], worst[1], worst[2]))

if __name__ == "__main__":
    main()
