#!/usr/bin/env python3
"""Convex polyplets (HV-convex king animals) by area -- row transfer matrix.

Restores the lost 38-term tool flagged as TODO in results/convex-polyplets.md
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
        for wp in range(1, N - nmin + 1):
            # enumerate dl; dr = wp - w + dl
            # king reach: dl <= w, dr >= -w; phases constrain signs
            dl_hi = w if pl == 0 else w
            dl_lo = -(N)  # will be cut by dr >= -w:  dl >= wp - w + dl >= ... dr = wp-w+dl >= -w => dl >= -wp
            for dl in range(max(-wp, wp - 2 * w) if False else -wp, dl_hi + 1):
                dr = wp - w + dl
                if dr < -w:
                    continue
                # phase transitions
                if pl == 0:
                    npl = 0 if dl <= 0 else 1
                else:
                    if dl < 0:
                        continue
                    npl = 1
                if pr == 0:
                    npr = 0 if dr >= 0 else 1
                else:
                    if dr > 0:
                        continue
                    npr = 1
                tgt = ndp[(wp, npl, npr)]
                for n0 in range(nmin, N - wp + 1):
                    v = vec[n0]
                    if v:
                        tgt[n0 + wp] += v
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
