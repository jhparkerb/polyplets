# W4 scoping: what surplus-4 weight pinning would cost in Lean

2026-08-09, gympie. Measurement only — no Lean written, no tree file edited.
Every number below is printed by `build/w4_scoping.py` (log:
`build/w4_scoping.log`, rerun as `python3 build/w4_scoping.py 748`) or read
from a build log named at the point of use.

## 1. Timing basis

`polyplets/weights3heavy.log` (the 2026-07-30 cold build of the surplus-3
chunk set) records the eight heavy chunk modules at 585, 614, 709, 755, 790,
833, 841, 856 s — mean **748 s** — plus `Polyplets.Weights3Heavy` itself at
1343 s. Each of those modules enumerates `C(24,6)·15 = 2,018,940` cluster/`q`
pairs (`WeightsChunk.lean` docstring; reproduced exactly by the script's
recipe).

Re-measured today on gympie: `build/w4_chunkA_timing.lean` — a standalone
`lake env lean` compile of the identical leaf `(CFGVchunk (-7)).card = 4`,
outside the Polyplets tree so nothing was invalidated — took **567.33 s real,
540.92 s user** (`build/w4_chunkA_timing.log`), against the 585 s that
`weights3heavy.log` records for the same leaf as `WeightsChunkA`. Agreement to
3%. Toolchain `leanprover/lean4:v4.31.0`, no download needed.

Rate used throughout: **748 s per 2.02e6 pairs = 370 s per 10^6 pairs.**

The rate is applied uniformly per chunk, which over-prices: the eight heavy
chunks are the ones whose window is the full 8 columns, while chunks `m ≥ 1`
truncate against `|x| ≤ 7` and fold into the fast `WeightsChunkTail`. Modelled
cost of the fifteen surplus-3 chunks is 15×748 = 10,800 s against 5,983 s
measured for the eight heavy ones plus a fast tail — the model runs ~1.8x
conservative. No verdict below turns on a factor of 2.

## 2. The enumeration-size formula

Read off `Weights.lean` / `WeightsChunk.lean`, with `N = |S|` and the x-spread
bound `|x| ≤ N−1` (`connected_abs_x_le`) giving `cols = 2N−1`:

| object | contents | `N` | enumeration |
|---|---|---|---|
| `V l j` (interior `W`) | `{p=(0,0)} ∪ C ∪ {q}` | `l+j+2` | `C(cols·l, l+j) · cols` |
| `Vt l j` (top edge `W^t`) | `{p} ∪ C` | `l+j+1` | `C(cols·l, l+j)` |
| bottom edge `W^b` | `C ∪ {q}`, anchored at `q` | `l+j+1` | `C(cols·l, l+j)` |
| pure `W^p` | `C` alone, one cell at the origin | `l+j` | `C(cols·l−1, l+j−1)` |
| `d k H` | walk-top animals in `box (H+k) H` | — | `C((H+k)·H, H+k)` |

Chunking by leftmost cluster column narrows the cluster window from `cols` to
`N` columns, giving `2N−1` chunks of `C(N·l, l+j)` subsets each.

Validation of the formula: at `l = 3, j = 3` it returns full `122,175,900`
(`WeightsChunk.lean`: "`C(45,6)·15 ≈ 1.2·10⁸`"), per-chunk `2,018,940` and 15
chunks (same docstring), `Vt 3 3 = C(39,6) = 3,262,623`, `d 3 4 = C(28,7) =
1,184,040` (`Weights3Heavy.lean`). Four for four.

Budgets, from what has actually compiled: **2,018,940 pairs per chunk** is the
proven-good per-`native_decide` scale; **3,262,623** (`Vt 3 3`) is the largest
proven one-shot; `1.2·10⁸` overflows the compiler's evaluation stack.

## 3. Surplus 4

Eight compositions, `(2,2,2,2) (2,2,3) (2,3,2) (2,4) (3,2,2) (3,3) (4,2)
(5,)`, i.e. `l` parts ≥ 2 summing to `l+4`; four weight families each
(`W`, `W^b`, `W^t`, `W^p` — the tuple of
`cluster_weight_dp.KNOWN_WEIGHTS`). Per-`l` figures (`build/w4_scoping.log`):

| `l` | family | full enumeration | per column-chunk | × budget | chunks |
|---|---|---|---|---|---|
| 1 | `W` | 16,731 | 273 | 0.0 | 13 |
| 2 | `W` | 8,906,625 | 120,120 | 0.06 | 15 |
| 3 | `W` | 1,968,176,700 | 15,096,510 | **7.5** | 17 |
| 3 | `W^t`, `W^b` | 45,379,620 | 346,104 | 0.17 | 15 |
| 4 | `W` | 358,261,787,925 | **1,461,189,015** | **723.4** | 19 |
| 4 | `W^t`, `W^b` | 7,392,009,768 | 30,260,340 | **15.0** | 17 |
| 4 | `W^p` | 341,149,446 | 2,629,575 | 1.3 | 15 |

Plus the base walk-top count `d 4 5 = C(45,9) = 886,163,135` — 91.2 h serial,
and **`Dc` has no leftmost-column chunking at all**: `box` is already
x-anchored, so a `d 4 5` chunking would need a freshly invented dimension
(top-row cell position, or row-0 profile) with its own partition lemma.

Two structural gaps on top of the compute:

- `W^b` and `W^p` **do not exist in Lean**. `Weights.lean` defines only
  `V` (= `W`) and `Vt` (= `W^t`). Each new family needs a definition, a
  decidability instance, and a window-independence lemma in the style of
  `mem_CFGV` / `mem_CFGVchunk` (the latter is ~85 lines of proof).
- **Per-composition values do not exist in Lean either.** `V l j` aggregates
  every composition with `l` rows; the composition is a *filter*, not a
  narrower window, so in the current style each of the three compositions at
  `l = 2` and each of the three at `l = 3` costs a full copy of that `l`'s
  enumeration. The alternative row-product enumeration (choose each row
  independently) is worse, not better: `(2,2,2,2)` costs 4,275,180,405 per
  chunk that way against 1,461,189,015 for the joint `powersetCard`.

Totals across all eight compositions and all four families, weights only:

- column-chunking alone, with a **perfect** second dimension for the
  over-budget chunks (window narrowed, no re-enumeration): 29,639,128,050
  pairs, ~14,700 modules, **3,049 h serial / 339 h 9-wide**.
- column-chunking plus filter-only subdivision (splitting an over-budget chunk
  by an extra predicate, each sub-module re-enumerating its window — the only
  subdivision that needs no new geometry): 20,121,825,446,640 pairs, **15,033
  modules, 2,069,737 h serial / 229,971 h 9-wide**.

The binding item is `W` for `(2,2,2,2)`: 1.46e9 pairs per chunk is 723x the
proven per-chunk budget, and leftmost cluster column offers only 19 chunks, so
that dimension is exhausted 723x short. Restricting to Lean's existing objects
(the aggregates `V l 4`, `Vt l 4`, eight values, no per-composition split, no
`W^b`/`W^p`) does not help: 14,214 modules, 2,068,509 h serial — the same
`l = 4` monster.

What *is* under budget at surplus 4: everything with `l ≤ 2` (all four
families, 15 chunks max each, under 0.25 h total), and `W^t`/`W^b`/`W^p` at
`l = 3` (0.5 h each). The wall is `l = 3` interior (7.5x budget) and the whole
of `l = 4`.

## 4. The two alternative W4 slices

**(a) Assembly arithmetic of the depth identities (C)/(D)**, with the weight
values taken as hypotheses (`experiments/severance_w3_depths.py`, counted by
`build/w4_scoping.py::assembly_facts` at `j = 4`, `K = 19`): **2,040
r-coefficient terms** (each a product `A·C(k−m,v)·(−3)^(k−m−v)`), **170
basis-change terms** of (D), over 17 values of `k`; the `A[m][E][k]` inputs are
40 bivariate series products (`_bimul` over 4×20 arrays) at 2,100 terms each,
**84,000 multiply-adds**. Total 86,210 exact-rational facts, **zero
enumeration**. For scale, the whole `Weights3Heavy` module — an assembly of
this kind plus two heavy `native_decide`s — is 1343 s.

**(b) The gap-walk transition table itself**
(`experiments/depth1_gap_walk.py::transitions`, counted by
`build/w4_scoping.py::transition_table` at `L = 8`, `gmax = 19`): **38 states**
`(g ∈ 1..19, class ∈ {J,P})`, **584 nonzero transitions**, total multiplicity
**4,218**, plus 38 start-state entries and 38 end weights (`q_end`/`bare_end`).
A `decide`-sized finite object. The labor is the bijection between cluster
configurations and walk paths, and the truncation argument for `g ≤ gmax`; the
table itself costs nothing to check.

## 5. Recommendations

- **Surplus 4, all four families, all eight compositions** — ~14,700 chunks,
  ~3,050 h serial / ~340 h 9-wide best case (15,033 chunks and 2,069,737 h
  with the subdivision that needs no new geometry), **infeasible** because the
  `(2,2,2,2)` interior weight enumerates 1.46e9 pairs per leftmost-column
  chunk, 723x the proven budget, exhausting the only chunking dimension that
  exists, and `d 4 5` (8.9e8) has no chunking dimension at all.
- **Assembly-only: identities (C)/(D) with weights as hypotheses** — 0 chunks,
  under 1 h build, **feasible** because 86,210 exact-rational facts (2,040 +
  170 + 84,000) carry no enumeration whatsoever, against the 1343 s that the
  comparable `Weights3Heavy` assembly costs *including* two heavy
  `native_decide`s.
- **Gap-walk transition table** — 0 chunks, under 1 h build, **feasible**
  because the object is 38 states / 584 transitions / 4,218 multiplicity, a
  `decide`-sized table whose cost is the configuration-to-path bijection, not
  compile time.

Surplus 4 becomes reachable only by formalizing the row-transfer DP
(W1's `cpp/severance_w3_families.cpp`, K=19 e=3 in 146 s) instead of the
subset enumeration — a different Lean object, not an extension of the
`WeightsChunk` pattern.
