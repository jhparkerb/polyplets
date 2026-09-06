#!/usr/bin/env python3
"""Settle the depth-6 (emax=5) cost from a measured K-ladder at fixed threads.

`docs/time-at-the-bar-report.md (deleted)` B2 found that disk is no longer what caps the
five terms: done at the target Nmax, the `Hs = 20` poles are 252 GB (n <= 44)
and 277 GB (n <= 45) against `Hs = 21`'s 580 GB, and dalby has 563 GB free.
What binds instead is that **`J = 6` is asserted** -- ~20-60 h and ~50-100 GB,
obtained by applying the per-excess ladder's ~6x RSS and ~7-9x wall once to
`J = 5`'s projection.

Depth 5 was asserted the same way at 16 h / 103 GB until five rungs measured it
at 3.1 h / 8.5 GB, an order of magnitude out (`results/undertow.md`).
These are those rungs for depth 6.

METHOD: the extrapolator is imported from `depth5_cost_ladder.py` rather than
reimplemented, so the two depths are priced by the same code and any difference
between them is in the data and not in the arithmetic. It steps from the top
rung in +2K increments, decaying the ratio by the decay the ladder itself
shows, because the ratios decelerate and a geometric mean over the whole range
overestimates the tail.

THE THREAD CONFOUND, again: the family DP's RSS scales with thread count
(project memory `family-dp-thread-confound`), so every rung here is 8 threads,
matching the depth-5 ladder rung for rung.

HOLDOUT: K = 14 is predicted from the first three rungs and compared with what
it measured, which is the only evidence the K = 21 projection carries.

Usage: python3 experiments/depth6_cost_ladder.py [--target 21]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from depth5_cost_ladder import (  # noqa: E402
    LADDER as LADDER_E4, extrapolate, ratios)

# Measured on dalby, 2026-08-22/23, ~/var/emax5-k/kladder.txt, 8 threads
# throughout, rev 1bec4fbf6.  wall in seconds, RSS in MB.
LADDER = {
    8:  (40.04,    423732 / 1024),
    10: (369.50,  2283476 / 1024),
    12: (1951.05, 7233364 / 1024),
    14: (7633.96, 17282040 / 1024),
}
THREADS = 8

# What the tree asserts for J = 6, and what it is measured against.
ASSERTED = {"docs/time-at-the-bar-report.md (deleted) B2 low": (20 * 3600, 50 * 1024),
            "docs/time-at-the-bar-report.md (deleted) B2 high": (60 * 3600, 100 * 1024)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=21)
    args = ap.parse_args()

    print("=" * 74)
    print(f"Depth-6 (emax=5) cost ladder, measured on dalby at {THREADS} threads")
    print("=" * 74)
    rw, rr = dict(ratios(LADDER, 0)), dict(ratios(LADDER, 1))
    print(f"{'K':>3} {'wall s':>10} {'RSS MB':>10} {'wall x/+2K':>11} "
          f"{'RSS x/+2K':>10}")
    for k in sorted(LADDER):
        w, m = LADDER[k]
        print(f"{k:>3} {w:>10.2f} {m:>10.1f} "
              f"{rw.get(k, float('nan')):>11.2f} {rr.get(k, float('nan')):>10.2f}")
    print()

    # The per-excess factor, at each K where both ladders have a rung.  The
    # assertion this run exists to replace treats it as a constant.
    print("Per-excess factor (emax=5 / emax=4) at each shared rung:")
    print(f"{'K':>3} {'wall x':>9} {'RSS x':>9}")
    for k in sorted(set(LADDER) & set(LADDER_E4)):
        print(f"{k:>3} {LADDER[k][0]/LADDER_E4[k][0]:>9.2f} "
              f"{LADDER[k][1]/LADDER_E4[k][1]:>9.2f}")
    print()

    # HOLDOUT: predict the top rung from the ones below it.
    lower = {k: v for k, v in LADDER.items() if k <= 12}
    top = max(LADDER)
    ok = True
    print(f"HOLDOUT: K = {top} predicted from K <= 12, before its measurement "
          "is used")
    for idx, name, unit in ((0, "wall", "s"), (1, "RSS", "MB")):
        pred, _, _ = extrapolate(lower, idx, top)
        meas = LADDER[top][idx]
        err = (pred - meas) / meas * 100
        ok &= abs(err) < 50
        print(f"  {name:<5} predicted {pred:>10.0f} {unit}   measured "
              f"{meas:>10.0f} {unit}   {err:+.1f}%")
    if not ok:
        print("  HOLDOUT FAILED by more than 50% -- the projection below is "
              "not worth reading")
        return 1
    print()

    for idx, name, unit in ((0, "wall", "s"), (1, "RSS", "MB")):
        val, steps, damp = extrapolate(LADDER, idx, args.target)
        print(f"--- {name} extrapolated to K = {args.target} "
              f"(ratio decay {damp:.3f} per +2K) ---")
        for k, r, v in steps:
            if unit == "s":
                print(f"  K={k:>3}  x{r:.2f}  ->  {v:>12.0f} s  ({v/3600:.1f} h)")
            else:
                print(f"  K={k:>3}  x{r:.2f}  ->  {v:>12.0f} MB ({v/1024:.1f} GB)")
        print()

    wall, _, _ = extrapolate(LADDER, 0, args.target)
    rss, _, _ = extrapolate(LADDER, 1, args.target)
    # The pessimistic bound the depth-5 file used: hold the top ratio flat,
    # i.e. assume the deceleration stops dead.
    rw_top = ratios(LADDER, 0)[-1][1]
    rr_top = ratios(LADDER, 1)[-1][1]
    steps = (args.target - max(LADDER)) / 2.0
    wall_flat = LADDER[max(LADDER)][0] * rw_top ** steps
    rss_flat = LADDER[max(LADDER)][1] * rr_top ** steps

    print("--- The answer, with the thread caveat stated ---")
    print(f"  decelerating, {THREADS} threads:  ~{wall/3600:.1f} h,  "
          f"~{rss/1024:.1f} GB")
    print(f"  deceleration stops dead:          ~{wall_flat/3600:.1f} h,  "
          f"~{rss_flat/1024:.1f} GB")
    print()
    print("  RSS scales with thread count, so the same run at other widths:")
    for t in (8, 16, 32, 40):
        print(f"    {t:>3} threads: ~{rss/1024 * t/THREADS:>6.1f} GB "
              f"(decelerating) / ~{rss_flat/1024 * t/THREADS:>6.1f} GB (flat)")
    print()
    print("--- Against what the tree asserts ---")
    for label, (w, m) in ASSERTED.items():
        print(f"  {label:<40} {w/3600:>4.0f} h  {m/1024:>5.0f} GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
