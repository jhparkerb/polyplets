"""r3_l1_band_cdist.py -- L1-3: component-count distribution in band geometry.

Question (queue row L1-3, dispatched by the lead 2026-08-12): the banked
"typical animal has ~n/2 pieces" (results/component-stratification.md) is a
whole-family statement at small n, summed over all heights.  Band cells are
tall and squeezed (n=40 over H=15..21 -> 1.9..2.7 cells per row).  Does
restricting to band geometry concentrate the component-count distribution at
small c, where the strata are externally computable (c=1 is A001168; c<=3 is
a small joint placement)?

Method: the validated PIECE DP of r3_l1_piece_states.py with exact c
tracking, per height-exactly-H cell.  Fail-closed guard: for every (n,H)
measured, sum_c counts must equal the banked T(n,H) (triangle.py loader,
full load-time validation) or the run aborts.

Output per cell: mean c, share with c<=3, share with c<=n/4, argmax c.
Trend displays: fixed n sweeping H (the squeeze axis), and fixed cells/row
ratio ~2.35 as n grows (the band axis).
"""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_l1_piece_states import dp_counts  # noqa: E402
from triangle import Triangle  # noqa: E402
from fractions import Fraction  # noqa: E402


def cell_stats(tri, n, H):
    t0 = time.time()
    got = dp_counts(H, n, track_c=True)
    dist = {c: v for (m, c), v in got.items() if m == n}
    tot = sum(dist.values())
    banked = tri.cell(n, H)
    if tot != banked:
        raise SystemExit("FAIL-CLOSED: sum_c=%d != banked T(%d,%d)=%d"
                         % (tot, n, H, banked))
    mean = Fraction(sum(c * v for c, v in dist.items()), tot)
    le3 = Fraction(sum(v for c, v in dist.items() if c <= 3), tot)
    leq = Fraction(sum(v for c, v in dist.items() if c <= n // 4), tot)
    mode = max(dist, key=lambda c: dist[c])
    return dict(mean=float(mean), le3=float(le3), leq4=float(leq),
                mode=mode, secs=time.time() - t0, dist=dist)


def main():
    tri = Triangle.load()
    print("(all rows fail-closed against banked T(n,H); provenance real-sweep for 3<=H<=21, lowstrip H<=2)")

    print("\n== squeeze axis: fixed n, H rising (band-like at n/H ~ 1.9..2.7) ==")
    print("n  H   n/H   mean_c  mean_c/n  mode  P(c<=3)   P(c<=n/4)  secs")
    for n, hs in ((12, range(3, 13)), (14, range(5, 8)), (16, range(6, 9))):
        for H in hs:
            s = cell_stats(tri, n, H)
            print("%-2d %-3d %-5.2f %-7.3f %-9.3f %-5d %-9.2e %-10.2e %.1f"
                  % (n, H, n / H, s['mean'], s['mean'] / n, s['mode'],
                     s['le3'], s['leq4'], s['secs']))

    print("\n== band axis: cells/row ~ 2.3, n growing ==")
    print("n  H   n/H   mean_c  mean_c/n  mode  P(c<=3)   P(c<=n/4)  secs")
    for n, H in ((7, 3), (9, 4), (12, 5), (14, 6), (16, 7), (18, 8)):
        s = cell_stats(tri, n, H)
        print("%-2d %-3d %-5.2f %-7.3f %-9.3f %-5d %-9.2e %-10.2e %.1f"
              % (n, H, n / H, s['mean'], s['mean'] / n, s['mode'],
                 s['le3'], s['leq4'], s['secs']))

    print("\n== one full distribution, the most band-like cell measured ==")
    s = cell_stats(tri, 18, 8)
    tot = sum(s['dist'].values())
    for c in sorted(s['dist']):
        print("  c=%-3d %-12d %.4f" % (c, s['dist'][c], s['dist'][c] / tot))


if __name__ == '__main__':
    main()
