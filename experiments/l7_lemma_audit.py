#!/usr/bin/env python3
"""Audit L7's Lemma T against the block series it is a statement about.

Lemma T proves lim T(n)^(1/n) exists by four steps, and Proposition split uses
the fourth.  Each step is an inequality about the truncated (0,1) descent block
and each is checkable on real data:

    (i)   T(n) >= 2 T(n-1)
    (ii)  T_h(n) <= 2 T(n-h)
    (iii) T_h(n) <= T_1(n + h(h-1)/2)
    (iv)  T_1(i) T_1(j) <= T_1(i+j)          -- supermultiplicativity
    (v)   T(n) <= 4 max_{h<=3} T_h(n)        -- derived in the paper from (i),(ii)
    (vi)  T(n) <= 4 T_1(n+3)                 -- derived from (ii),(iii)

T_h counts runs whose FIRST column has height h.  The enumeration reuses
experiments/descent_block_oracle.py's geometry (interval sequences, b and t
nonincreasing, king adjacency, dir4 floor) rather than re-deriving it, but the
per-h split is done here.

RED controls: each inequality is re-run in a deliberately wrong direction and
must fail, so a check that cannot fire is visible as such.

    python3 experiments/l7_lemma_audit.py [--nmax 18]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import descent_block_oracle as oracle  # noqa: E402


def by_first_height(nmax):
    """T_h(n) for every first-column height h, by the oracle's own DFS."""
    table = {}
    sys.setrecursionlimit(10000)

    def walk(b, t, area, out):
        out[area] += 1
        room = nmax - area
        for bp in range(max(b - 1, b - room), b + 1):
            for tp in range(max(bp, b - 1), t + 1):
                hp = tp - bp + 1
                if area + hp > nmax:
                    break
                walk(bp, tp, area + hp, out)

    for h in range(1, nmax + 1):
        out = [0] * (nmax + 1)
        walk(0, h - 1, h, out)
        table[h] = out
    return table


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=18)
    args = ap.parse_args()
    N = args.nmax

    T = oracle.brute(N)
    Tdp = oracle.dp(N)
    ok = T[:N + 1] == Tdp[:N + 1]
    print("oracle DFS == oracle DP through n=%d: %s" % (N, "yes" if ok else "NO"))
    if not ok:
        return 1
    print("T =", ", ".join(str(T[n]) for n in range(1, min(N, 12) + 1)), "...")

    Th = by_first_height(N)
    # the split must be exact: sum_h T_h(n) = T(n)
    bad = [n for n in range(1, N + 1)
           if sum(Th[h][n] for h in Th) != T[n]]
    print("sum_h T_h(n) == T(n) for all n <= %d: %s" % (N, "yes" if not bad else "NO %s" % bad))
    if bad:
        return 1

    T1 = Th[1]
    fails = []

    def check(name, cond, detail):
        if not cond:
            fails.append("%s: %s" % (name, detail))

    for n in range(2, N + 1):
        check("(i)", T[n] >= 2 * T[n - 1], "n=%d: %d < 2*%d" % (n, T[n], T[n - 1]))
    for h in Th:
        for n in range(h, N + 1):
            if n - h >= 1:
                check("(ii)", Th[h][n] <= 2 * T[n - h],
                      "h=%d n=%d: %d > 2*%d" % (h, n, Th[h][n], T[n - h]))
            shift = n + h * (h - 1) // 2
            if shift <= N:
                check("(iii)", Th[h][n] <= T1[shift],
                      "h=%d n=%d: %d > %d" % (h, n, Th[h][n], T1[shift]))
    for i in range(1, N + 1):
        for j in range(1, N + 1 - i):
            check("(iv)", T1[i] * T1[j] <= T1[i + j],
                  "i=%d j=%d: %d*%d > %d" % (i, j, T1[i], T1[j], T1[i + j]))
    for n in range(1, N + 1):
        check("(v)", T[n] <= 4 * max(Th[h][n] for h in (1, 2, 3)),
              "n=%d: %d > 4*%d" % (n, T[n], max(Th[h][n] for h in (1, 2, 3))))
        if n + 3 <= N:
            check("(vi)", T[n] <= 4 * T1[n + 3],
                  "n=%d: %d > 4*%d" % (n, T[n], T1[n + 3]))

    print()
    for name in ("(i)", "(ii)", "(iii)", "(iv)", "(v)", "(vi)"):
        hits = [f for f in fails if f.startswith(name)]
        print("  %-6s %s" % (name, "OK" if not hits else "FAIL (%d) e.g. %s"
                             % (len(hits), hits[0])))

    # RED controls.  A control that cannot fire proves nothing, so each one
    # here is a corruption of the DATA or a genuinely tighter constant, and is
    # required to break the corresponding step.
    print("\nRED controls (each must fire):")

    T1bad = list(T1)
    for i in range(2, len(T1bad)):
        if T1bad[i]:
            T1bad[i] -= 1          # one entry short: supermultiplicativity dies
            break
    red = [
        ("(i) with factor 3",
         any(T[n] < 3 * T[n - 1] for n in range(2, N + 1))),
        ("(iv) on T1 with one entry decremented",
         any(T1bad[i] * T1bad[j] > T1bad[i + j]
             for i in range(1, N + 1) for j in range(1, N + 1 - i))),
        ("(iv) on T rather than T1",
         any(T[i] * T[j] > T[i + j]
             for i in range(1, N + 1) for j in range(1, N + 1 - i))),
        ("(iii) with the climb cost dropped (shift 0)",
         any(Th[h][n] > T1[n] for h in Th for n in range(h, N + 1))),
        ("(vi) with shift 3 -> 0 and no factor",
         any(T[n] > T1[n] for n in range(1, N + 1))),
    ]
    for name, fired in red:
        print("  %-42s %s" % (name, "FIRED" if fired else "DID NOT FIRE"))
    if not all(f for _, f in red):
        print("  NOTE: a control that did not fire marks a check with no bite.")

    # How much bite do the checks have?  An inequality with three orders of
    # magnitude of slack is not evidence about its constant.
    print("\nslack (how close each step runs to failing):")
    r_i = min(T[n] / T[n - 1] for n in range(2, N + 1))
    print("  (i)   min T(n)/T(n-1) = %.3f  against the required 2" % r_i)
    ratios = [T1[i + j] / (T1[i] * T1[j])
              for i in range(1, N + 1) for j in range(1, N + 1 - i)
              if T1[i] and T1[j]]
    print("  (iv)  min T1(i+j)/(T1(i)T1(j)) = %.3f  against the required 1"
          % min(ratios))
    r_vi = max(T[n] / T1[n + 3] for n in range(1, N - 2) if T1[n + 3])
    print("  (vi)  max T(n)/T1(n+3) = %.3f  against the allowed 4" % r_vi)
    print("  Steps with large slack are confirmed only against gross "
          "mis-statement, not in their constants.")

    if fails:
        print("\nRESULT: %d FAILURES" % len(fails))
        return 1
    print("\nRESULT: every step of Lemma T holds on the enumerated block "
          "through n=%d" % N)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
