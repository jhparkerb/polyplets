# The cost ladders measured during the last-ditch campaign

2026-08-20, branch `lastditch`. Three ladders, each run because a plan was
resting on an extrapolation nobody had checked. Raw output in
`results/nmax-scaling.txt`, `results/emax-ladder.txt`,
`results/emax4-k-ladder.txt`; scripts in `scripts/lastditch/` and
`scripts/nmax_scaling.sh`.

**Read the methodology note before quoting any slope from this file.**

---

## 1. Fixed-height sweep cost in Nmax

`scripts/nmax_scaling.sh`, dalby, 8 cores held fixed, one height at a time.

| height | | Nmax 40 | Nmax 42 | Nmax 45 | 40->45 |
|---|---|---|---|---|---|
| 14 | wall | 300.6 s | 336.9 s | 418.4 s | 1.392x |
| 14 | cpu | 1685.9 s | 1925.5 s | 2432.0 s | **1.442x** |
| 15 | wall | 835.2 s | 1056.5 s | 1400.0 s | 1.676x |
| 15 | cpu | 4669.9 s | 5524.7 s | 6845.3 s | **1.466x** |

**Read the CPU column.** The box had a sweep, two censuses and this ladder on
it at once; wall is contaminated and the H = 15 runs caught more of it. The
1.392 vs 1.676 wall spread says nothing about the lattice. CPU agrees closely
at two heights.

Why this matters: the ladder's famous **4.4x per term** is the cost of raising
`H_sweep` *and* `Nmax` together. Undertow lowers `H_sweep`, so what governs a
higher-Nmax run at a fixed ceiling is this number, and it is ~1.45x for five
terms of Nmax, not 4.4x for one.

Exponent: `ln(1.442)/ln(1.125) = 3.10` at H = 14, `3.24` at H = 15 — climbing
about +0.14 per height, so H = 21 extrapolates to ~4.1 and `40 -> 45` to about
**1.6x**. Two points setting a slope run out six heights is a weak
extrapolation and is flagged as one in `docs/five-terms-plan.md`.

## 2. Bounded-excess family DP, per unit of excess

`scripts/lastditch/emax_ladder.sh`, ayr, 16 threads, K = 10 fixed.

| emax | wall | RSS | per-e wall | per-e RSS |
|---|---|---|---|---|
| 0 | 0.01 s | 4 MB | - | - |
| 1 | 0.09 s | 4 MB | 9.0x | 1.0x |
| 2 | 0.74 s | 17 MB | 8.2x | 4.1x |
| 3 | 4.92 s | 83 MB | 6.6x | 4.9x |
| 4 | 46.71 s | 480 MB | 9.5x | 6.0x |
| 5 | 326.79 s | 2.39 GB | 7.0x | 5.1x |

**~6x per excess in RSS, ~7-9x in wall.** Depth `j` needs `emax = j-1`, so
this is the price of each new depth.

**What it closed.** Lane C of the review proposed pinning every tower level
from strip-confirmed `H <= 14` cells, which needs depths 8-9 and therefore
`emax = 7, 8`. At the measured ratio that is 10^4-10^5 GB at K = 21 on any
per-K slope in range. Closed on arithmetic, `results/undertow-review-C.md` §6.

## 3. The same family DP, per unit of K, at emax = 4

`scripts/lastditch/emax4_kladder.sh`, ayr, **16 threads held fixed**.

| K | wall | RSS |
|---|---|---|
| 10 | 46.71 s | 480 MB |
| 14 | 705.92 s | 2.69 GB |

Same-thread slope: **1.521x per K** in RSS, 1.972x in wall. Projecting depth 5
(`emax = 4` at `K = 21`) from K = 14: **~51 GB**, ~23 h at 16 threads.

### The methodology note

Every slope quoted before this ladder mixed thread counts, and they disagreed
wildly because of it:

| reading | threads | slope | emax=4 @ K=21 |
|---|---|---|---|
| e=4, K=8->12 | 40 | 1.828x/K | 184 GB |
| e=4, K=10->12 | 40 | 1.636x/K | 84 GB |
| e=3, K=10->22 | 10 vs 40 | 1.308x/K | 18 GB |
| **e=4, K=10->14** | **16 both** | **1.521x/K** | **51 GB** |

The DP builds per-thread private maps and merges them after
(`std::vector<Map> parts(nth)` in `cpp/severance_w3_families.cpp::step`), so
thread count moves RSS directly — 480 MB at 16 threads against 577 MB at 40
for the same cell. That is also why the e=3 series appears to decelerate to
K = 19 and then accelerate to K = 22: part of that is the pool, not the DP.

**Hold the thread count fixed or the slope is not a slope.** This cost the
lead and Lane C an argument each before either of us noticed.
