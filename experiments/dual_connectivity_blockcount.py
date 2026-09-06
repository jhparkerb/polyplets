#!/usr/bin/env python3
"""Is there a small-b regime where the dual-connectivity TM wins?

`docs/lastditch-ideas.md (deleted)` sec. 6 closes the dual-connectivity transfer matrix
(track the complement's 4-connectivity, planar hence non-crossing, and recover
the component count from C = chi + holes) with a state comparison:

> (Catalan on b+1 runs) x (b component counts) exceeds Bell(b) at exactly the
> block counts that dominate -- b*Cat(b) vs Bell(b) is 11,440 vs 4,140 at
> b = 8.  The dual is *worse*.

`docs/last-orders.md (deleted)` C2.2 asks the variation that is not the same idea: the
arithmetic is only lopsided at large block counts, so does a hybrid that
carries the dual only where b is small buy anything?  That needs the block-count
DISTRIBUTION over a real frontier, which is banked data, not an opinion.

Two things fall out, and the second was not expected:

  1. the frontier's mass sits at b ~ H/3, not at small b, so a small-b hybrid
     covers almost nothing; and
  2. the incumbent does NOT pay Bell(b) per block pattern -- it pays Cat(b).
     The check is exact: sum_b C(H+1,2b)*Cat(b) = Motzkin(H+1), and
     Motzkin(22)-1 is the banked H=21 column-state count to the digit.  So the
     banked comparison understates the dual's disadvantage.

Combinatorics used, both standard:
  - binary strings of length H with exactly b maximal runs of 1s: C(H+1, 2b);
  - sum_b C(n,2b)*Cat(b) = Motzkin(n).

RED controls:
  - sum_b C(H+1,2b) must be 2^H (every subset counted once, by run count);
  - sum_b C(H+1,2b)*Cat(b) must equal Motzkin(H+1) at every H tested;
  - Motzkin(22)-1 must equal the banked incumbent state count 400763222.

Usage: python3 experiments/dual_connectivity_blockcount.py [--height 21]
"""
import argparse
import sys
from functools import lru_cache
from math import comb

# The incumbent's banked column-state count at H = 21, from
# docs/skeletonkey-reprompt.md (deleted) ("the incumbent realises Motzkin(H+1) - 1 =
# 400,763,222 column states there").
BANKED_H21_STATES = 400_763_222


def catalan(n):
    return comb(2 * n, n) // (n + 1)


def bell(n):
    B = [[0] * (n + 1) for _ in range(n + 1)]
    B[0][0] = 1
    for i in range(1, n + 1):
        B[i][0] = B[i - 1][i - 1]
        for j in range(1, i + 1):
            B[i][j] = B[i][j - 1] + B[i - 1][j - 1]
    return B[n][0]


@lru_cache(None)
def motzkin(n):
    """Motzkin numbers by their three-term recurrence.

    NOT sum_k C(n,2k)Cat(k), which is what this used to be -- and that made the
    first RED control below a tautology: it checks sum_b C(H+1,2b)*Cat(b)
    against motzkin(H+1), so with motzkin DEFINED as that sum, both sides ran
    the same code and the control could not fail. The recurrence is a second
    route (same one experiments/tristruct/r3_inv_rank_probe.py uses), so the
    identity is now actually being tested. The division is exact at every n.
    """
    if n <= 1:
        return 1
    return ((2 * n + 1) * motzkin(n - 1) + (3 * n - 3) * motzkin(n - 2)) // (n + 2)


def patterns(H, b):
    """Binary strings of length H with exactly b maximal runs of 1s."""
    return comb(H + 1, 2 * b)


def red_controls(H):
    ok = True
    bmax = (H + 1) // 2
    tot = sum(patterns(H, b) for b in range(bmax + 1))
    good = tot == 2 ** H
    print(f"RED  run-count classes partition all 2^{H} subsets "
          f"({tot} vs {2**H})  {'OK' if good else 'FAILED'}")
    ok &= good

    for h in (5, 10, 21):
        lhs = sum(patterns(h, b) * catalan(b) for b in range((h + 1) // 2 + 1))
        good = lhs == motzkin(h + 1)
        print(f"RED  sum C({h+1},2b)*Cat(b) = Motzkin({h+1}) "
              f"({lhs} vs {motzkin(h+1)})  {'OK' if good else 'FAILED'}")
        ok &= good

    good = motzkin(22) - 1 == BANKED_H21_STATES
    print(f"RED  Motzkin(22)-1 is the banked H=21 state count "
          f"({motzkin(22)-1} vs {BANKED_H21_STATES})  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", type=int, default=21)
    args = ap.parse_args()
    H = args.height
    bmax = (H + 1) // 2

    print("=" * 78)
    print(f"Dual-connectivity TM: is there a small-b regime?  H = {H}")
    print("=" * 78)
    print(f"{'b':>3} {'patterns':>10} {'Cat(b)':>8} {'Bell(b)':>9} "
          f"{'b*Cat(b)':>9} {'incumbent':>15} {'dual':>16} {'ratio':>6}")
    tot_inc = tot_dual = tot_bell = 0
    rows = []
    for b in range(bmax + 1):
        p = patterns(H, b)
        ca, be = catalan(b), bell(b)
        d = b * ca if b else 1
        inc, dua = p * ca, p * d
        tot_inc += inc
        tot_dual += dua
        tot_bell += p * be
        rows.append((b, p, ca, inc))
        print(f"{b:>3} {p:>10} {ca:>8} {be:>9} {d:>9} {inc:>15} {dua:>16} "
              f"{(d/ca):>6.0f}x")

    print()
    print(f"  incumbent total  sum p*Cat(b)   = {tot_inc:>15,}  "
          f"= Motzkin({H+1})")
    print(f"  banked incumbent (Motzkin-1)    = {tot_inc-1:>15,}")
    print(f"  dual total       sum p*b*Cat(b) = {tot_dual:>15,}  "
          f"= {tot_dual/tot_inc:.1f}x the incumbent")
    print(f"  Bell total       sum p*Bell(b)  = {tot_bell:>15,}  "
          f"= {tot_bell/tot_inc:.1f}x the incumbent")
    print()

    print("--- Where the frontier's mass actually sits ---")
    run = 0
    for b, p, ca, inc in rows:
        run += inc
        print(f"  b <= {b:>2}:  {run/tot_inc*100:6.2f}% of the frontier;  "
              f"dual costs {b if b else 1}x the incumbent at this b")
    print()

    print("--- The hybrid question, answered ---")
    # The dual's per-pattern cost is b*Cat(b) and the incumbent's is Cat(b),
    # so the ratio is exactly b.  It is <= 1 only at b <= 1.
    share = sum(inc for b, p, ca, inc in rows if b <= 1) / tot_inc
    print(f"  the dual/incumbent cost ratio is exactly b, at every block count")
    print(f"  it is not worse than the incumbent only at b <= 1, which is "
          f"{share*100:.4f}% of the frontier")
    print(f"  so a small-b hybrid has no regime to live in")
    print()

    print("--- RED controls ---")
    if not red_controls(H):
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
