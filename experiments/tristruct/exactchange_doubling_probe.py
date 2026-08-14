#!/usr/bin/env python3
"""Exact Change probe 5: the top-row doubling behind the A034299 recurrence.

r(H) = 2 r(H-1) + (-1)^(H-1) ceil(H/2) (A034299's own recurrence) predicts a
decomposition of the observability space V_H by top-row usage of the SUFFIX:

  V_H^low := span{ g_w : w avoids row H-1 }.

For such suffixes a prefix block interacts only through N(b) truncated to
[0, H-2], so V_H^low is a pullback of the height-(H-1) functional -- EXCEPT
that truncation can produce families no (H-1)-state has (a top-row singleton
block truncates to the 1-row neighborhood {H-2}).  So:

  dim V_H^low == r(H-1)        -> clean doubling, quotient carries r(H-1)
                                  +- ceil(H/2) and the A000975 correction
  dim V_H^low  > r(H-1)        -> the exotic truncated families are visible
                                  and the bookkeeping shifts

Also measured: the bottom-row variant (must equal by up-down symmetry) and
the both-rows variant (against r(H-2)).

Fail-closed: full-alphabet rank must equal A034299 at every H.
"""
import sys
import time

from exactchange_minauto import build_min_automaton, obs_rank, a034299


def main():
    maxh = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print("H  r(H)  low  r(H-1)  bot  both  r(H-2)   quotient r(H)-low")
    for H in range(4, maxh + 1):
        t0 = time.time()
        order, delta, accept, masks, _ = build_min_automaton(H)
        full = obs_rank(order, delta, accept, masks)
        assert full == a034299(H), f"H={H}: {full} != A034299"
        top = 1 << (H - 1)
        low = obs_rank(order, delta, accept, [m for m in masks if not m & top])
        bot = obs_rank(order, delta, accept, [m for m in masks if not m & 1])
        both = obs_rank(order, delta, accept,
                        [m for m in masks if not m & (top | 1)])
        print(f"{H}  {full}  {low}  {a034299(H-1)}  {bot}  {both}  "
              f"{a034299(H-2)}   {full - low}"
              f"   ({time.time()-t0:.1f}s)", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
