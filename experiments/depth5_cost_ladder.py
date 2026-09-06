#!/usr/bin/env python3
"""Settle the depth-5 (emax=4) cost from a measured K-ladder at fixed threads.

`results/undertow-review-queue.md (deleted)` row L-2 is the open question:

> Depth 5 (emax=4 at K=21) is between ~110 GB and ~390 GB depending on which
> per-K ratio you trust: K=8->10 is 4.18x per +2K, K=10->12 is 2.68x, so the
> ratio is DECELERATING and the geometric mean over the whole range
> overestimates the tail.  Two more points (K=14, K=16 at emax=4, ~15 and
> ~50 min) settle it.  Until then depth 5 is "marginal", not "16 h / 103 GB"
> as earlier plans assert.

This reads the ladder those two points complete and extrapolates it honestly:
by the *local* ratio, which is what "decelerating" means, rather than by a
geometric mean over the whole range, which is the thing L-2 says overestimates.

**The thread confound is the reason this ladder is at fixed threads.**  The
family DP's RSS scales with thread count (project memory,
`family-dp-thread-confound`), so a K-slope mixing thread counts is not a slope.
Every rung here is 8 threads.  That also means the absolute RSS is an
8-thread number and must be scaled before being compared with any figure
measured at another width.

Usage: python3 experiments/depth5_cost_ladder.py [--target 21]
"""
import argparse
import sys

# Measured on ayr, 2026-08-22, ~/var/depth5-stage/ladder.txt, 8 threads
# throughout, rev a66bc61.  wall in seconds, rss in MB.
LADDER = {
    8:  (6.52,    131956 / 1024),
    10: (48.16,   473996 / 1024),
    12: (219.20, 1177684 / 1024),
    14: (731.86, 2518568 / 1024),
    16: (1988.13, 4340916 / 1024),
}

# K=16 was PREDICTED from the first four rungs before it ran, and the
# prediction is recorded here as the extrapolator's holdout:
#   predicted 1859 s / 4607 MB   measured 1988 s / 4239 MB
#   wall 6.9% under, RSS 8.0% over.  That is the only evidence that the
#   extrapolation below is worth anything.
HOLDOUT_K16 = {"predicted": (1859.0, 4607.0), "measured": (1988.13, 4239.2)}
THREADS = 8

# What the tree asserts, for comparison.
ASSERTED = {
    "lastditch-ideas.md sec.2": (16 * 3600, 103 * 1024),
    "review-queue L-2 low":     (None, 110 * 1024),
    "review-queue L-2 high":    (None, 390 * 1024),
}


def ratios(ladder, idx):
    ks = sorted(ladder)
    out = []
    for a, b in zip(ks, ks[1:]):
        out.append((b, ladder[b][idx] / ladder[a][idx]))
    return out


def extrapolate(ladder, idx, target, damp=None):
    """Step from the top rung to `target` in +2K steps, decaying the ratio.

    The observed ratios decelerate; `damp` is the multiplicative decay applied
    to the ratio at each further step, taken from the ladder itself when not
    given.  A final odd step uses the square root of the step ratio.
    """
    ks = sorted(ladder)
    rs = ratios(ladder, idx)
    if damp is None:
        # how much the +2K ratio shrinks per +2K, from the last two ratios
        damp = (rs[-1][1] - 1) / (rs[-2][1] - 1)
    val = ladder[ks[-1]][idx]
    k = ks[-1]
    r = rs[-1][1]
    steps = []
    while k + 2 <= target:
        r = 1 + (r - 1) * damp
        val *= r
        k += 2
        steps.append((k, r, val))
    if k < target:
        r_half = (1 + (r - 1) * damp) ** 0.5
        val *= r_half
        k = target
        steps.append((k, r_half, val))
    return val, steps, damp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=21)
    args = ap.parse_args()

    print("=" * 72)
    print(f"Depth-5 (emax=4) cost ladder, measured on ayr at {THREADS} threads")
    print("=" * 72)
    print(f"{'K':>3} {'wall s':>10} {'RSS MB':>10} {'wall x/+2K':>11} "
          f"{'RSS x/+2K':>10}")
    ks = sorted(LADDER)
    rw, rr = dict(ratios(LADDER, 0)), dict(ratios(LADDER, 1))
    for k in ks:
        w, m = LADDER[k]
        print(f"{k:>3} {w:>10.2f} {m:>10.1f} "
              f"{rw.get(k, float('nan')):>11.2f} {rr.get(k, float('nan')):>10.2f}")
    print()
    print("Both ratios decelerate, which is L-2's point and is why a geometric")
    print("mean over the whole range overestimates the tail.")
    print()

    for idx, name, unit in ((0, "wall", "s"), (1, "RSS", "MB")):
        val, steps, damp = extrapolate(LADDER, idx, args.target)
        print(f"--- {name} extrapolated to K = {args.target} "
              f"(ratio decay {damp:.3f} per +2K) ---")
        for k, r, v in steps:
            if unit == "s":
                print(f"  K={k:>3}  x{r:.2f}  ->  {v:>12.0f} s  "
                      f"({v/3600:.1f} h)")
            else:
                print(f"  K={k:>3}  x{r:.2f}  ->  {v:>12.0f} MB "
                      f"({v/1024:.1f} GB)")
        print()

    wall, _, _ = extrapolate(LADDER, 0, args.target)
    rss, _, _ = extrapolate(LADDER, 1, args.target)
    print("--- The answer, with the thread caveat stated ---")
    print(f"  at {THREADS} threads:  ~{wall/3600:.1f} h,  ~{rss/1024:.1f} GB")
    print()
    print("  RSS scales with thread count, so the same run at other widths:")
    for t in (8, 16, 32, 40):
        print(f"    {t:>3} threads: ~{rss/1024 * t/THREADS:>6.1f} GB"
              f"   (wall roughly /{t/THREADS:.0f} if it scales)")
    print()
    print("--- Against what the tree asserts ---")
    for label, (w, m) in ASSERTED.items():
        wtxt = f"{w/3600:.0f} h" if w else "--"
        print(f"  {label:<28} {wtxt:>6}  {m/1024:>6.0f} GB")
    print()
    print(f"  dalby has 125 GB.  At 8 threads the projection is "
          f"{rss/1024:.0f} GB, i.e. it fits with room;")
    print(f"  the ~103 GB figure is consistent with this ladder at about "
          f"{103*1024/rss*THREADS:.0f} threads.")
    print()

    # The pessimistic bound: assume the deceleration STOPS at the top rung and
    # the ratio holds flat the rest of the way.  This is the number to quote,
    # because the deceleration is the part of the model doing the work and it
    # is fitted from two ratios.
    print("--- Pessimistic bound: no further deceleration ---")
    ks = sorted(LADDER)
    for idx, name, unit, div in ((0, "wall", "h", 3600.0),
                                 (1, "RSS", "GB", 1024.0)):
        r = ratios(LADDER, idx)[-1][1]
        val = LADDER[ks[-1]][idx]
        k = ks[-1]
        while k + 2 <= args.target:
            val *= r
            k += 2
        if k < args.target:
            val *= r ** 0.5
        best, _, _ = extrapolate(LADDER, idx, args.target)
        print(f"  {name}: ratio held flat at {r:.2f}/+2K -> "
              f"{val/div:.1f} {unit}   (decelerating model: "
              f"{best/div:.1f} {unit})")
    print()
    print("  So the honest bracket at 8 threads is the pair of those, and even")
    print("  its pessimistic end is well inside dalby.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
