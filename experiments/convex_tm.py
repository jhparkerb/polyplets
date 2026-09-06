#!/usr/bin/env python3
"""Convex polyplets (HV-convex king animals) by area -- row transfer matrix.

Restores the lost 38-term tool flagged as TODO in results/subclasses.md
(primary analysis: docs/proofs/convex-mirage.md). An HV-convex king animal is
a sequence of row intervals [l_i, r_i] with l unimodal (non-increasing then
non-decreasing), r unimodal (non-decreasing then non-increasing), and
consecutive intervals within king reach (l' <= r+1, r' >= l-1). Phases flip
on the first strict violation, so every animal has a unique parse.

State: (width, left-phase, right-phase); counts tracked as vectors over n.
Usage: python3 experiments/convex_tm.py [N]   (default 38)
"""
import sys
from collections import defaultdict

N = int(sys.argv[1]) if len(sys.argv) > 1 else 38

# dp[(w, pl, pr)] = list of counts by total cells n (index 0..N)
# pl: 0 = l still non-increasing, 1 = l now non-decreasing
# pr: 0 = r still non-decreasing, 1 = r now non-increasing
dp = defaultdict(lambda: [0] * (N + 1))
total = [0] * (N + 1)
for w in range(1, N + 1):
    dp[(w, 0, 0)][w] = 1
    total[w] += 1

while dp:
    ndp = defaultdict(lambda: [0] * (N + 1))
    for (w, pl, pr), vec in dp.items():
        nmin = next((i for i, v in enumerate(vec) if v), None)
        if nmin is None:
            continue
        # Prefix sums over n0 let each (npl, npr) sub-interval of dl be
        # folded into one range-sum-and-add instead of a per-dl loop:
        # every dl in a contiguous sub-interval shifts the same vec by the
        # same wp, so the O(w) dl loop collapses to O(1) box counts times
        # a single vector add scaled by the box width (a convolution with
        # a box is just a prefix-sum difference of box width, folded here
        # into a scalar multiply since the shift itself is dl-independent).
        for wp in range(1, N - nmin + 1):
            # dl range before phase forcing: [-wp, w] (dr = wp - w + dl is
            # already >= -w throughout since dl >= -wp).
            lo = -wp if pl == 0 else 0        # pl==1 forces dl >= 0
            hi = w if pr == 0 else w - wp     # pr==1 forces dl <= w - wp
            if lo > hi:
                continue
            split_l = w - wp  # dr >= 0  <=>  dl >= split_l
            for npl, lo_l, hi_l in (
                ((0, lo, min(hi, 0)), (1, max(lo, 1), hi))
                if pl == 0 else ((1, lo, hi),)
            ):
                if lo_l > hi_l:
                    continue
                for npr, lo_r, hi_r in (
                    ((0, split_l, hi), (1, lo, split_l - 1))
                    if pr == 0 else ((1, lo, hi),)
                ):
                    a, b = max(lo_l, lo_r), min(hi_l, hi_r)
                    if a > b:
                        continue
                    count = b - a + 1
                    tgt = ndp[(wp, npl, npr)]
                    for n0 in range(nmin, N - wp + 1):
                        v = vec[n0]
                        if v:
                            tgt[n0 + wp] += count * v
    dp = ndp
    for vec in dp.values():
        for n0, v in enumerate(vec):
            if v:
                total[n0] += v

REF = [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
       2677214, 8389720, 26271014, 82230035, 257333334, 805229818,
       2519563026, 7883577553]
out = total[1:N + 1]
assert out[:len(REF)] == REF[:len(out)], (out[:20], REF)
print("convex polyplets by area, n=1..%d:" % N)
print(", ".join(map(str, out)))
if N >= 22:
    print("ratios:", ", ".join(f"{out[i+1]/out[i]:.5f}" for i in range(N - 6, N - 1)))
print(f"matches convex-mirage reference (first {min(len(REF), N)} terms)  OK")
