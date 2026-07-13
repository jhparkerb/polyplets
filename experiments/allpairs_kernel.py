#!/usr/bin/env python3
"""K1 part 1: the all-pairs cluster family as an exact two-class gap walk.

State after each pair-row: (g, c) with g = gap between the pair's cells and
c = J (one component) / P (two pending components). Validated: the walk
reproduces count_stack's all-pairs interior weights exactly for l <= 8
(25, 339, 4778, 68314, 981085, 14115141, 203235615, 2927318947).

Measured kernel structure (for the functional-equation solve, K1 part 2):
  P-bulk (g >= 4):  g -> g + {-2,-1,0,1,2} with weights (1,2,3,2,1), stay P.
  J-class:          local moves near g' ~ g, PLUS constant-weight (8) long
                    jumps to (g', P) for arbitrarily large g' (one new cell
                    touches the block, the far cell goes pending), PLUS
                    constant-weight (8) resets to (1, J).
  Ends: start from p with 3+2 small-g injections; finish: J-state pays
  g+3 (g <= 2) or 6 (g >= 3); P-state finishable only at g <= 2 (3-g ways).
Boundary (small-g) corrections are finite and enumerated by transitions().
"""
import sys
from collections import defaultdict


def transitions(g, c, gp_max):
    out = {}
    for gp in range(1, gp_max + 1):
        for a in range(-1 - gp - 1, g + 3):
            T = (a, a + gp)
            touch0 = any(abs(t) <= 1 for t in T)
            touchg = any(abs(t - g) <= 1 for t in T)
            if c == 'P':
                if not (touch0 and touchg):
                    continue
            else:
                if not (touch0 or touchg):
                    continue
            if gp == 1:
                nc = 'J'
            elif c == 'J':
                a0 = (abs(T[0]) <= 1 or abs(T[0] - g) <= 1)
                a1 = (abs(T[1]) <= 1 or abs(T[1] - g) <= 1)
                nc = 'J' if (a0 and a1) else 'P'
            else:
                par = {k: k for k in 'ABxy'}

                def find(k):
                    while par[k] != k:
                        k = par[k]
                    return k

                def uni(u, v):
                    ru, rv = find(u), find(v)
                    if ru != rv:
                        par[ru] = rv

                if abs(T[0]) <= 1:
                    uni('x', 'A')
                if abs(T[0] - g) <= 1:
                    uni('x', 'B')
                if abs(T[1]) <= 1:
                    uni('y', 'A')
                if abs(T[1] - g) <= 1:
                    uni('y', 'B')
                nc = 'J' if find('x') == find('y') else 'P'
            out[(gp, nc)] = out.get((gp, nc), 0) + 1
    return out


def W_via_walk(l):
    gmax = 2 * l + 3
    dp = defaultdict(int)
    for g in range(1, gmax + 1):
        for a in range(-1 - g - 1, 3):
            T = (a, a + g)
            if not any(abs(t) <= 1 for t in T):
                continue
            nc = 'J' if (g == 1 or (abs(T[0]) <= 1 and abs(T[1]) <= 1)) else 'P'
            dp[(g, nc)] += 1
    for _ in range(l - 1):
        ndp = defaultdict(int)
        for (g, c), v in dp.items():
            for (gp, nc), t in transitions(g, c, gmax).items():
                ndp[(gp, nc)] += v * t
        dp = ndp
    tot = 0
    for (g, c), v in dp.items():
        if c == 'J':
            tot += v * (g + 3 if g <= 2 else 6)
        elif g <= 2:
            tot += v * (3 - g)
    return tot


RHO_25 = "14.408713986270365838148040"   # 37-digit value in results/allpairs-kernel.md


def spectral_check(gmax=60):
    """Dominant eigenvalue + kernel relation (K1 part 2)."""
    import mpmath as mp
    mp.mp.dps = 35
    states = ([(g, 'J') for g in range(1, gmax + 1)] +
              [(g, 'P') for g in range(2, gmax + 1)])
    idx = {s: i for i, s in enumerate(states)}
    cols = []
    for (g, c) in states:
        tr = transitions(g, c, gmax)
        cols.append([(idx[k], w) for k, w in tr.items() if k in idx])
    N = len(states)
    v = [mp.mpf(1)] * N
    lam = mp.mpf(0)
    for it in range(500):
        w = [mp.mpf(0)] * N
        for i in range(N):
            if v[i]:
                for j, t in cols[i]:
                    w[j] += v[i] * t
        lam_new = max(w)
        w = [x / lam_new for x in w]
        if it > 100 and abs(lam_new - lam) < mp.mpf(10) ** (-30):
            lam, v = lam_new, w
            break
        lam, v = lam_new, w
    # gmax=60 truncation is good to ~19 digits (error ~ kappa^gmax)
    assert mp.nstr(lam, 19) == mp.nstr(mp.mpf(RHO_25), 19), mp.nstr(lam, 25)
    fJ = [v[idx[(g, 'J')]] for g in range(1, gmax + 1)]
    kappa = fJ[45] / fJ[44]
    rel = kappa ** 2 + 2 * kappa + 3 + 2 / kappa + 1 / kappa ** 2
    assert abs(rel - lam) < mp.mpf(10) ** (-9), abs(rel - lam)
    print(f"spectral: rho = {mp.nstr(lam, 25)}, kernel relation OK "
          f"(kappa = {mp.nstr(kappa, 12)})")


if __name__ == "__main__":
    REF = [25, 339, 4778, 68314, 981085, 14115141, 203235615, 2927318947]
    got = [W_via_walk(l) for l in range(1, 9)]
    assert got == REF, got
    print("all-pairs gap walk == count_stack for l <= 8  OK")
    spectral_check()
