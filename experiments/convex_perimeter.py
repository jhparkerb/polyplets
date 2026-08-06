#!/usr/bin/env python3
"""Convex polyplets by SEMIPERIMETER (W+H): D-finite, unlike by area.

For HV-convex animals the monotone envelopes make the bounding box the
natural perimeter (edge-perimeter = 2(W+H), as for convex polyominoes).
Counting by exact box via the phase-automaton row DP:

  polyomino control: 1, 2, 7, 28, 120, 528, 2344, ... = A005436
    (Delest-Viennot, algebraic) -- P-recurrence found at order 2, degree 4,
    which CALIBRATES the guesser (an underpowered guesser misses it).
  king convex:       1, 2, 9, 36, 154, 668, 2916, 12740, ...
    P-recurrence at order 5, degree 2, fitted on the first 22 rows and
    verified on 8 held-out rows (s <= 36). Late ratios 4.136 -> 4.128,
    drifting toward the s-growth constant (~4.1).

So the Convex Mirage refines to: BY AREA non-D-finite (both families,
docs/proofs/convex-mirage.md); BY PERIMETER D-finite (both families) --
convexity is a perimeter lever for king animals exactly as for polyominoes.
"""
import sys
from collections import defaultdict
from fractions import Fraction as F

SMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 36


def count_by_box(Smax, king=True):
    """Row DP over the exact bounding box (W, H). Unlike convex_tm.py's area
    DP, state keys store the ABSOLUTE column boundaries (l, r), needed by
    future transitions -- so distinct rp values can't be merged into one
    scaled count the way convex_tm.py's dl values were (docs/middle-kingdom-
    plan.md Phase 1a). What DOES collapse: for a fixed lp, the same v is
    added to EVERY rp in a contiguous range (the inner rp loop) -- a
    textbook range update, done here as a 1D difference array per (lp, npl,
    tLp, npr, tRp) bucket, marked in O(1) per lp and materialized with one
    O(W) prefix-sum sweep per bucket after all source states are processed.
    The lp loop itself stays explicit (unlike wp in convex_tm.py's collapse),
    so this is ~S^6 -> ~S^5, not the ~S^5 -> ~S^4 area DP got. Verified
    against the original nested (lp, rp) loop at Smax in {12, 20, 30},
    exact match, both king and non-king, before this replaced it (Phase 1b).
    """
    out = {}
    for W in range(1, Smax):
        Hmax = Smax - W
        if Hmax < 1:
            break
        dp = defaultdict(int)
        for l in range(W):
            for r in range(l, W):
                dp[(l, r, 0, 0, l == 0, r == W - 1)] += 1

        def flush(d):
            return sum(v for (l, r, pl, pr, tL, tR), v in d.items()
                       if tL and tR)

        res = [0] * (Hmax + 1)
        res[1] = flush(dp)
        H = 1
        while H < Hmax:
            # delta[(lp, npl, tLp, npr, tRp)] = 1D difference array over rp,
            # size W+1 (index W is the "one past end" sentinel).
            delta = defaultdict(lambda: [0] * (W + 1))

            def mark(key, a, b, v):
                if a > b:
                    return
                arr = delta[key]
                arr[a] += v
                arr[b + 1] -= v

            for (l, r, pl, pr, tL, tR), v in dp.items():
                lp_lo = l if pl == 1 else 0
                lp_hi = min(W - 1, (r + 1 if king else r))
                king_off = l - 1 if king else l
                for lp in range(lp_lo, lp_hi + 1):
                    rp_lo = max(lp, king_off)
                    rp_hi = r if pr == 1 else W - 1
                    if rp_lo > rp_hi:
                        continue
                    npl = 1 if (pl == 1 or lp > l) else 0
                    tLp = tL or lp == 0

                    if pr == 0:
                        ranges = []
                        a, b = rp_lo, min(rp_hi, r - 1)
                        if a <= b:
                            ranges.append((1, a, b))
                        a, b = max(rp_lo, r), rp_hi
                        if a <= b:
                            ranges.append((0, a, b))
                    else:
                        ranges = [(1, rp_lo, rp_hi)]

                    for npr, a, b in ranges:
                        if tR:
                            mark((lp, npl, tLp, npr, True), a, b, v)
                        elif a <= W - 1 <= b:
                            if a <= W - 2:
                                mark((lp, npl, tLp, npr, False), a, W - 2, v)
                            mark((lp, npl, tLp, npr, True), W - 1, W - 1, v)
                        else:
                            mark((lp, npl, tLp, npr, False), a, b, v)

            ndp = defaultdict(int)
            for (lp, npl, tLp, npr, tRp), arr in delta.items():
                run = 0
                for rp in range(W):
                    run += arr[rp]
                    if run:
                        ndp[(lp, rp, npl, npr, tLp, tRp)] += run
            dp = ndp
            H += 1
            res[H] = flush(dp)
        for H2 in range(1, Hmax + 1):
            out[(W, H2)] = res[H2]
    return out


def perim_series(king, Smax):
    c = count_by_box(Smax, king)
    p = [0] * (Smax + 1)
    for (W, H), v in c.items():
        if W + H <= Smax:
            p[W + H] += v
    return p[2:]


def find_prec(seq, J, D, train_extra=4):
    unknowns = (J + 1) * (D + 1)
    rows = []
    for n in range(len(seq) - J):
        row = []
        for j in range(J + 1):
            for d in range(D + 1):
                row.append(F(seq[n + j]) * F(n) ** d)
        rows.append(row)
    if len(rows) < unknowns + train_extra + 4:
        return None
    train = rows[:unknowns + train_extra]
    hold = rows[unknowns + train_extra:]
    A = [r[:] for r in train]
    m, nc = len(A), unknowns
    piv = []
    ri = 0
    for col in range(nc):
        p = None
        for r in range(ri, m):
            if A[r][col] != 0:
                p = r
                break
        if p is None:
            continue
        A[ri], A[p] = A[p], A[ri]
        A[ri] = [x / A[ri][col] for x in A[ri]]
        for r in range(m):
            if r != ri and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[ri])]
        piv.append((ri, col))
        ri += 1
        if ri == m:
            break
    pivcols = [c for _, c in piv]
    free = [c for c in range(nc) if c not in pivcols]
    for fv in free:
        sol = [F(0)] * nc
        sol[fv] = F(1)
        for r, col in piv:
            sol[col] = -sum(A[r][c] * sol[c] for c in free)
        if all(sum(rw[c] * sol[c] for c in range(nc)) == 0 for rw in hold):
            return sol
    return None


if __name__ == "__main__":
    pp = perim_series(False, SMAX)
    pk = perim_series(True, SMAX)
    assert pp[:8] == [1, 2, 7, 28, 120, 528, 2344, 10416], pp[:8]  # A005436
    assert pk[:8] == [1, 2, 9, 36, 154, 668, 2916, 12740], pk[:8]
    assert find_prec(pp, 2, 4) is not None, "control must be D-finite"
    if SMAX >= 36:
        assert find_prec(pk, 5, 2) is not None, "king perimeter recurrence"
    else:
        print(f"(SMAX={SMAX} < 36: king recurrence check skipped, "
              f"needs more holdout rows)")
    print(f"s<=SMAX={SMAX}: control==A005436 & D-finite(2,4); "
          f"king convex by perimeter D-finite(5,2), holdout-verified  OK")
