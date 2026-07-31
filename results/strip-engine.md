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

Scoped honestly (AUDIT-2026-07-30 S1/S2/S3). What the strip engine is and
is not independent OF:

- **Disjoint from the kink kernel** — the load-bearing claim, and it holds:
  a whole-column connectivity-partition sweep, not the cell-at-a-time
  NW-carry kink kernel. No shared code, no shared frontier, no shared
  state encoding with the engine that produced the banked triangle.
- **NOT a different connectivity algorithm.** The core rule — union-find
  over the new column's cells and the old column's component labels, with
  stranded-component death — is the same rule as this repo's own reference
  column oracle, `core/transition.h`. Written independently, but not a
  different idea; a shared misconception about king-connectivity would not
  be caught by it. The genuinely disjoint axes are the surrounding ones:
  boundary granularity (whole-strip cumulative C_H vs per-column frontier),
  accounting layer (second difference in H vs direct per-height tally),
  count representation (`__int128` vs big.Int/CRT), and orchestration
  (single process vs sharded map/merge).
- **Anchored at small n** by a brute-force enumerator (translation classes of
  king-connected n-cell sets, binned by bbox height) — independent of BOTH the
  strip TM and the kink kernel. Agreement n<=9: exact. **This anchor lives
  only in the Python reference** (`brute_T`); it caps at n=9 and never runs
  at H=11..14, so those columns rest on the C++ code alone plus its
  agreement with the banked triangle.
- **Cross-implementation, but not cross-mind**: a Python reference
  (`experiments/strip_engine.py`) and a C++ *port of it*
  (`cpp/strip_tm.cpp`, `__int128` counts) agree byte-for-byte on all C_H,
  H<=10. They were written together and landed in the same commit
  (`713540c`), so this is a transcription check — it catches typos and
  overflow, not a wrong shared rule. Do not count it as a second source.

## Result

Engine-computed T(n,H) matches the banked (kink-derived) triangle EXACTLY for
every entry in columns H computed, at every n up to 40:

| Hmax | banked entries confirmed | wall (C++) |
|------|--------------------------|------------|
| 10   | 315                      | ~5 s       |
| 13   | (see strip_engine_run.log — C++ output despite the name; C_13 = 606s) | ~730 s |
| 14   | 413, 0 mismatch, n≤36 (strip_C14_run.log, dalby 2026-07-22) | ~7.5 h dalby (C_14 = 22919s; dalby ≈ 5.4x slower/thread than gympie) |
| 14   | **469, 0 mismatch, n≤40** (strip_C14_n40_run.log, dalby 2026-07-30, rev 5239e73) | ~8.6 h dalby (C_14 = 25892s) |

(`strip_engine_run.log` is `build/strip_tm` output — its first line says
`strip_tm (C++)` — not the Python reference's, despite sharing the Python
script's name. The Python reference's own output is banked separately at
`results/strip_engine_python_run.log` (Hmax=10, Nmax=14, gympie 2026-07-30):
that is where the brute-force anchor n≤9 actually runs, since `brute_T` exists
only in the Python. The original C++ run stopped after C_13, so its end-of-run
banked compare never executed and coverage stood at H≤13. The 2026-07-22 dalby
run — hostile-witness audit fix 7, `docs/lean-hostile-witness.md` — completed
C_14 and the full compare: columns H≤14 independently confirmed at every
banked n≤36. A first attempt on gympie was killed after thrashing: C_14's
measured footprint is ~38 GB, past gympie's 24 GB; RAM-size accordingly. This
flips the PinGrand anchors T(26,14) and T(27,14) to multi-source. At the
a(40) close the Grand tier reaches k≤18 and has **30** anchors, of which 19
are strip-second-sourced (H≤14, n≤36) and **11 are kink-only** — beyond
strip reach even at N=40: T(28,15), T(29,15), T(30,16), T(31,16), T(32,17),
T(33,17), T(34,18), T(35,18), T(36,19), T(37,19), T(38,20). (The "7 cells
of levels 13B..16" this paragraph used to list was the k≤16 tier's count.)
C_15 would need
~200+ GB by the same growth — off the table on current hardware.)

Zero mismatches. What this adds over the EXISTING independent checks: the
project's Redelmeier enumerator (`build/g2 square8 --per-box`) already
two-algorithm-confirms the fixed counts A006770 through n=19 (per the b-file
provenance in `results/b030222_upload.txt`), but its cost is proportional to
object count, so it stops at ~n=19-20. The strip TM's cost is ~2^H (independent
of object count), so it EXTENDS independent per-column confirmation of the
middle heights to n=20..36 — the region Redelmeier cannot reach. That is the
strip engine's distinct contribution: columns H<=14 independently checked at
large n, not a first check at small n.

### Coverage, stated three ways (AUDIT-2026-07-30 S4)

"~85-90% coverage" was a *cell* count that credited the P_k closed forms as a
second source — including for the cells those very formulas produced. Over
the closed n<=40 triangle (820 cells), recomputed:

| figure | value (n≤36 strip) | value (N=40 strip, 2026-07-30) | what it counts |
|---|---|---|---|
| doc-style cell union | 90.5% (742) | **95.4%** (782) | H<=4 recurrences ∪ P_k diagonals ∪ strip (H<=14), P_k credited everywhere in its onset |
| honest cells | 67.3% (552) | **72.2%** (592) | same, but a closed form is NOT a second source for a cell it generated — P_k credited only on really-swept cells (H<=21) |
| strip alone | 50.4% (413) | **57.2%** (469) | the strip engine's own verified region |

Exact rule for reproducing these, so they are not folklore: cells are all
(n,H) with 1<=H<=n<=40 (820 of them); `R` = H<=4; `S` = H<=14 and n<=36
(now n<=40 for the right-hand column); `P` = diagonals k = n-H with
**k <= 18** and n >= 2k+1. Diagonal k=19 is
excluded from `P` deliberately — P_19 is fitted-no-holdout, so it certifies
nothing; including it adds exactly its own two fit points, T(39,20) and
T(40,21), and would read 90.7% / 67.6%. Then doc-style = |R ∪ P ∪ S|,
honest = |R ∪ S ∪ (P ∩ {H<=21})|.

Cells are the flattering denominator, because the triangle's cells are wildly
unequal in size. **By mass** the picture is starker. The banked strip run is
H<=14 **and n<=36**, so it touches no cell of rows 37-40 at all:

| term | strip mass, pre-extension (n<=36) | with the N=40 extension (DELIVERED 2026-07-30) |
|---|---|---|
| a(37) | 0% | 53.8% |
| a(38) | 0% | 50.8% |
| a(39) | 0% | 47.9% |
| a(40) | 0% | 45.0% |

(right-hand column = share of that row's mass in heights H<=14, recomputed
from `results/ns_a40/perheight/h*.out`.) Do not confuse this with the
**holdout-confirmed** mass (9.1% / 5.5% / 2.5% / 0.0% for a(37)-a(40)),
which is a different and unrelated quantity — closed-form cells later
reached by a real sweep, tabulated in `results/ns_a40/PROVENANCE.md`. The
original strip run stopped four terms short of the close, and the mass
lives in the tall middle heights. The N=40 strip run closing that gap
COMPLETED 2026-07-30 (dalby, ~8.6 h, rev 5239e73;
`results/strip_C14_n40_run.log`): 469 cells, 0 mismatch — every banked
row now carries independent strip confirmation of its H<=14 mass
(45.0% of a(40)). The per-height mass breakdown of a(40) itself is in
`results/ns_a40/PROVENANCE.md`.

Note: `build/g2` (cpp/g2_redelmeier.cpp) is the canonical, gated Redelmeier;
prefer it over any ad hoc enumerator.

## Complexity (measured, C++)

State count per height (distinct connectivity partitions cached):
1, 3, 8, 20, 50, 126, 322, 834, 2187, 5797, ... — grows ~2.65x/height.
Wall grows ~6x/height (H=10: 3.5s). __int128 suffices through n<=40, H<=15
since C_H(n) <= H*a(n) < 1.7e38. State packed 4 bits/row -> H<=15 cap.

## Reproduce

    make -C . build/strip_tm      # or: clang++ -O3 -std=c++17 -o build/strip_tm cpp/strip_tm.cpp
    ./build/strip_tm 14 40 results/ns_a40/perheight   # the 2026-07-30 full-reach run (~38 GB RAM, ~8.6 h dalby)
    python3 experiments/strip_engine.py 10 36     # brute-anchored reference
