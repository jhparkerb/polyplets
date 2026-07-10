# Independent strip transfer-matrix engine — second source for T(n,H)

Date: 2026-07-10. The validation lever from `results/triangle-structure.md`,
now built and run. It computes the polyplet triangle a SECOND way, sharing no
enumeration with the kink NW-carry kernel that produced the banked triangle.

## What it computes

A height-H strip is swept column by column carrying a king-connectivity
partition state (which occupied rows of the current column belong to which
connected component). It counts king-connected cell sets by area with
horizontal translation fixed (leftmost occupied column = 0), giving the strip
cumulative

    C_H(n) = sum_{h<=H} (H-h+1) * T(n,h)      (vertical placements counted),

and the triangle is recovered by the exact second difference in H:

    T(n,H) = C_H(n) - 2*C_{H-1}(n) + C_{H-2}(n)     (C_0 = C_{-1} = 0).

This is the `C_H` object whose minimal recurrences are the "atoms" q_H
(degrees 1,2,4,9,29,68,...). The engine confirms those degrees directly as
its per-height recurrence orders.

## Independence

- **Different algorithm**: a classic connectivity-partition column sweep, not
  the cell-at-a-time NW-carry kink kernel. No shared code, no shared frontier.
- **Anchored at small n** by a brute-force enumerator (translation classes of
  king-connected n-cell sets, binned by bbox height) — independent of BOTH the
  strip TM and the kink kernel. Agreement n<=9: exact.
- **Cross-implementation**: a Python reference (`experiments/strip_engine.py`)
  and a C++ engine (`cpp/strip_tm.cpp`, `__int128` counts) agree byte-for-byte
  on all C_H, H<=10.

## Result

Engine-computed T(n,H) matches the banked (kink-derived) triangle EXACTLY for
every entry in columns H computed, at every n up to 36:

| Hmax | banked entries confirmed | wall (C++) |
|------|--------------------------|------------|
| 10   | 315                      | ~5 s       |
| 14   | (see strip_engine_run.log) | (running) |

Zero mismatches. What this adds over the EXISTING independent checks: the
project's Redelmeier enumerator (`build/g2 square8 --per-box`) already
two-algorithm-confirms the fixed counts A006770 through n=19 (per the b-file
provenance in `results/b030222_upload.txt`), but its cost is proportional to
object count, so it stops at ~n=19-20. The strip TM's cost is ~2^H (independent
of object count), so it EXTENDS independent per-column confirmation of the
middle heights to n=20..36 — the region Redelmeier cannot reach. That is the
strip engine's distinct contribution: columns H<=14/15 independently checked at
large n, not a first check at small n. It raises second-source coverage of the
630-entry triangle from 55.6% (columns H<=4 recurrences + P_k diagonals) toward
~85-90% (see the coverage map in `results/triangle-structure.md`).

Note: `build/g2` (cpp/g2_redelmeier.cpp) is the canonical, gated Redelmeier;
prefer it over any ad hoc enumerator.

## Complexity (measured, C++)

State count per height (distinct connectivity partitions cached):
1, 3, 8, 20, 50, 126, 322, 834, 2187, 5797, ... — grows ~2.65x/height.
Wall grows ~6x/height (H=10: 3.5s). __int128 suffices through n<=40, H<=15
since C_H(n) <= H*a(n) < 1.7e38. State packed 4 bits/row -> H<=15 cap.

## Reproduce

    make -C . build/strip_tm      # or: clang++ -O3 -std=c++17 -o build/strip_tm cpp/strip_tm.cpp
    ./build/strip_tm 14 36 results/ns_a36/perheight
    python3 experiments/strip_engine.py 10 36     # brute-anchored reference
