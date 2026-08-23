# Last ditch — the candidate list

Opened 2026-08-20, branch `lastditch`. The brief: a breakthrough that either
confirms a(40) by a second algorithm or reaches past n = 40. Everything here is
a candidate with a stated payoff and a stated way to kill it; the ones already
killed are kept with their reasons so nobody re-pitches them.

Ranked by payoff × plausibility as of the last edit. `results/` and `docs/`
citations are load-bearing — this file asserts nothing it does not point at.

---

## 1. Undertow — pin P_k from below-onset cells (LEAD CANDIDATE)

`docs/b1-closure-plan.md` §1 costs level `k` two **above-onset** anchors,
`T(2k+1,k+1)` and `T(2k+2,k+2)` — the two *tallest* cells on its diagonal. That
rule is why row 40 is expensive: P₁₉'s anchors are `T(39,20)` and `T(40,21)`,
and `T(40,21)` is the 36.4-hour H = 21 sweep that fits nothing.

The grand form (`docs/proofs/grand-form.md`, Lean-complete) says a level carries
**exactly two new constants**, so any two independent linear equations pin it.
Severance W3 (`results/onset-defect-depths234.md`) supplies them from cells that
are *shorter* than the onset anchors: for a below-onset cell at depth j,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) · 3^(2k-3k-j) + D_j(k)

with `D_j(k)` computed **ab initio** from bounded-excess cluster-weight families
— no triangle, no wired `P_k` — exact at j = 1..4 and checked against 16–19
banked cells per depth. The left side sits at height `k+1-j`, i.e. **j rows
below** the onset anchor.

Consequences if it holds:

- **row 40.** P₁₉ pins from `T(37,18)`, `T(36,17)`; P₂₀ from `T(38,18)`,
  `T(37,17)`. Both pairs are inside Motley's already-banked H ≤ 18 rows, so
  `T(40,21)` and `T(40,20)` become *rule-independent predictions* with no new
  compute. Only `T(40,19)` still wants H = 19 — or depth 5.
- **reach.** Coverage becomes roughly `n ≤ 2·H_max + J` for exact depths up to
  J. Every two extra depth levels buys one height, and a height is ~3×
  compute. a(41) stops needing the H = 21 pole: phase A of the a(40) run
  (H1–19, 80 cores) was **6.3 h**; the week and the 363 GB were phases B and C
  (`results/ns_a40/PROVENANCE.md`).
- **audit.** Depths 1–4 plus the two onset anchors give **six** equations for
  two unknowns per level — four independent consistency checks on the banked
  triangle's tallest cells, from short cells, through mathematics that shares
  nothing with the sweep.

Status: **VERIFY GREEN**, 18 of 18 wired levels re-derived exactly over every
available depth pair; `T(40,21)` predicted and matching; level 20 pinned
overdetermined (3 pairs, 2 independent checks) and predicting `T(41,21)`.
Record: `results/undertow.md`. `experiments/undertow_pin.py`, three RED controls
green (perturbed
`D_j` breaks the pin; one equation twice refused as singular; corrupted lower
level breaks the pin). `--verify` re-derives every wired level from below-onset
cells — that is the decisive run.

Ways it dies: `D_j(k)` turning out to depend on `P_k` after all (it does not,
by construction — the W3 gate keeps the two sides apart); the two depth
equations being dependent (they are not: the 2×2 is `[[1,n₁],[1,n₂]]`); the
grand form's residual failing to be linear at some level (checked in
`extract_ab`, which raises).

## 1a. The column-numerator form of the same idea (a much bigger check)

`docs/proofs/diagonal-law.md` Step 4/5 make column `k` **finite data**:
`[y^k]F = R_k(z)/(1-3z)^(k+1)` with a correction polynomial `D(z)` of degree
≤ k, so the whole column is `2` grand-form constants plus `k+1` integers —
`k+3` unknowns. Depth `j` is literally `[z^(k+1-j)] D(z)`, so depths 1..4
supply four of them ab initio, and the swept cells at `H ≤ 18` supply eighteen
equations. For `k = 19` that is 22 equations against 22 unknowns: the column is
**exactly determined by short cells plus the depth identities**, `T(40,21)`
included.

Undertow only needs two of those equations, which is why it works at all. But
solving the whole column is the stronger *test*: it turns the 3-agreeing-pairs
check into an 18-equation consistency check per level. Worth building as the
audit form of §1.

## 1b. Cross-lattice validation against an external oracle

`docs/proofs/universal-diagonal-law.md` proves the diagonal law for every
row-local lattice — square (b=1), hex (b=2), king (b=3) — and the square
lattice's diagonal polynomials, onset `2k+1` and depth-1 defect
(`+1,-1,+1,-1,+1`) are all recorded in `results/onset-defect-law.md`. Square
polyominoes are enumerated to n = 70 in the literature
(`results/literature-record-56-corrected.md`; this file said 56, which was one
computation's reach and not the record). Only the TOTALS reach that far --
the bounding-box triangle this needs is published at no n.

So the pin can be run on a lattice where the answers are **published by other
people**. That is the one validation channel this project structurally lacks
above n = 20, and it costs a square-lattice `D_j` derivation, not machine time.
The blocker is that Severance's ledger is king-only ("what remains king-only is
the ledger — assembling c_k from the weights — and the master equation",
`results/defect-gas.md`); the weight DP itself is already lattice-parametric.

### CORRECTION 2026-08-20 — §1a's payoff does not exist, and §5 dies with it

Branch `skeletonkey`, desk arithmetic on banked files, no compute.

**§1a as written is void.** The pin's own equation (`undertow_pin.py`
docstring) is `T(2k+1-j, k+1-j) = P_k(2k+1-j)·3^(...) + D_j(k)`. A below-onset
cell at depth `j` therefore contributes one equation **and one unknown**,
`D_j(k)`, unless that depth's `D_j` is already known ab initio. Equivalently,
in the Step-5 basis the cell at height `H` touches exactly one coefficient of
the correction polynomial, `[z^H]D`. The map is one-to-one, so the eighteen
`H ≤ 18` cells cancel against fifteen new unknowns and the redundancy is
unchanged.

The honest accounting is

    surplus at level k  =  (banked cells whose depth has a known D_j)  −  2

which at `k = 19`, `j ≤ 4`, `H ≤ 18` gives depths 2, 3, 4 and surplus 1 —
exactly the "3 depth pairs, 2 independent checks" `results/undertow.md`
already reports. §1a's "turns the 3-agreeing-pairs check into an 18-equation
consistency check per level" was arrived at by counting the cells and not the
unknowns they bring. **Nothing is gained by solving the whole column**; it is
a reformulation of the same information, and what actually buys redundancy is
one more *ab initio depth*, not one more cell.

**§5 dies on the same arithmetic, from the other end.** The escape would be
that `D_j(·)` is constrained in `k`, so that cells across levels share few
unknowns. It is — `D_1` is P-finite — but at `(r,d) = (35,4)`, an ansatz with
`36 × 5 = 180` unknown coefficients. That is why
`results/onset-defect-depth1-closed.md` fitted it on 57 series orders with 144
in holdout, off `D_1` evaluated ab initio to `k = 200`. Neither supply reaches
180: there are ~15 banked cells per depth (`severance_w3_depth5_gate.py` names
its own 15, `T(2k−4, k−4)` for `k = 5..19`), and the family DP that would
supply more grows 1.52×/K in RSS (`results/lastditch-cost-ladders.md` §3).

Two caveats, stated rather than buried. `(35,4)` is the *minimal* order for
`j = 1` — the same file's mod-p scan proves nothing smaller works — so it is
a floor for the easiest depth, not a ceiling for the others; that deeper `D_j`
are no simpler is an expectation, not a measurement. And none of this touches
**§2**, the direct family-DP route to depth 5, which stands at its measured
**~3.1 h / ~8.5 GB**, or 6.7 h / 16.1 GB pessimistic (corrected 2026-08-22
from ~51 GB / ~23 h, `results/depth5-cost-settled.md`).

## 2. Depths 5–8 (the multiplier on Undertow)

W3 says the frame already covers j ≥ 5 — "each depth adds finitely many
families, all computable by the same C++ DP" — and that it was not run only
because the certification map below row 34 did not need it. Depth j needs
excess ≤ j-1 families; `cpp/severance_w3_families.cpp` takes `emax` as an
argument.

Payoff, if the cost is affordable: J = 8 pins level k from height `k-7`, so the
whole tower down to k = 21 would pin from **H ≤ 14** — the strip engine's
independent range (`results/strip-engine.md`) — and the sweep for row n would
stop near `H = (n-8)/2`.

The unknown is how the family DP grows in `emax`. Measured on dalby at
emax = 4: **12.2 s / 138 MB at K = 8, 71.4 s / 577 MB at K = 10, 265.0 s /
1.54 GB at K = 12** — about 1.82x per unit K in time and 1.6x in RSS, so
`families 21 4` (depth 5) extrapolates to ~16 h and ~103 GB. Inside dalby,
at the wall. **[Superseded 2026-08-22 — see the corrected price at the end of
this section: ~3.1 h / ~8.5 GB.]**

**A per-level span cap was tried and is WRONG — do not re-pitch it.** The DP
caps the horizontal span at `2K + emax + 1` for every level, and it looks
obviously wasteful: a cluster of `ell` rows has `2*ell + e` cells and, being
connected, spans at most `2*ell + e - 1`, so level 10 should need 25 and not
47. Implemented behind `--global-span` and gated against the old behaviour: it
is **9x faster, 5x smaller, and undercounts** — 333 against 339 at
`(e, k) = (0, 2)`, K = 9.

The argument fails on prefixes. A cluster of two 2-cell rows can be
`{0,3}` over `{1,2}`: connected, four cells, span 3 = cells − 1, all correct —
but its **first row alone spans 3 with only two cells**. A prefix's span is
bounded by the *final* cluster's cell count, not its own, because a later row
can bridge a gap an earlier row opened. The honest bound at level `ell` with
excess `e2` is `span <= 2K - e2 - 1`, which is the global cap and a bit.

So depth 5 costs what the measured ladder says — and **the ladder was extended
2026-08-22 and the price falls by an order of magnitude**
(`results/depth5-cost-settled.md`). Five rungs at fixed 8 threads give
K=8 6.52 s / 129 MB through K=16 1988.13 s / 4239 MB, with both ratios
decelerating monotonically (RSS 3.59, 2.48, 2.14, 1.72 per +2K). `families 21 4`
projects to **~3.1 h and ~8.5 GB at 8 threads**, or ~6.7 h / ~16.1 GB on the
pessimistic assumption that the deceleration stops dead. The ~16 h / ~103 GB
quoted at the top of this section was a geometric mean over a decelerating
range and is superseded; K=16 was
predicted before it ran and came in within 8% on both axes. Depth 5 is not "at
the wall"; it fits with headroom. The gate did its job in about four minutes, which is the argument for
building the gate first.

## 3. Parallel Motley (insurance, and it works today)

`docs/b1-closure-plan.md` §4 names it: "The engine is still single-threaded …
RAM is the wall this document plans around; cores are the next one." Confetti
(H = 18) spent 399,700 s of wall on one core of an 80-core box.

`cpp/motley_par.cpp`: same frozen rule core (`slot`/`canon`/`gather`/`shifted`/
`successors` transcribed from the 59e90660 spec), flat open-addressed table
plus a contiguous payload slab instead of `unordered_map` + one heap vector per
state per cell-step, OpenMP cell-step, payload width chosen from the prime,
column-boundary checkpoint. Rows byte-identical to `cutcount_b1 --modp` at
H = 6, 8, 10; **1.9× faster single-threaded** before any core is added (the
per-state allocate-and-zero was that expensive).

Measured on dalby, H = 14 / Nmax = 40 / one 31-bit prime:

| threads | 1 | 8 | 32 | 80 | `cutcount_b1` |
|---|---|---|---|---|---|
| wall s | 323.3 | 41.2 | 13.1 | **11.8** | 596.0 |
| RSS MB | 718 | 718 | 693 | 733 | 1048 |

27× on cores, 1.84× before any core, **50× end to end**, and byte-identical at
every thread count. The first cut scaled 4× while burning 76 cores: one global
row counter and spinlock bytes packed 64 to a cache line. Per-thread index
blocks and the lock moved into its own payload row fixed both. (An 8-bit
payload then found a second one: `rb + 8 = 90` is not 4-aligned, and a
misaligned `atomic<u32>` is a SIGBUS on aarch64, not a slow path.)

Even with Undertow this is worth having: Motley H = 19 retires `T(40,19)`
outright, and the H ≤ 18 rows Undertow pins from are Motley rows.

## 4. Rungs that are named and unpriced in the closure plan

- **Top-bottom mirror fold** — §5 calls it "the one factor that would move
  H = 21", ~2× on states, and leaves it unpriced because the flip commutes with
  a column-at-a-time transfer and not with the row-at-a-time scan. A
  chunk-through-the-column restructure would recover it.
- **Width truncation** `W = 42-H` — sound for the telescope provided all three
  `C_H` run at the same W, ~2× time at H = 21, needs the H ≤ 16 replay as its
  gate. Time only: peak states saturate at column 2.
- **Severance W1's k = 10 wall** — declined on memory (53 GB at k = 9), and the
  note says what it needs: "a state-space reduction (symmetry quotient or
  frontier compression in the stack DP), not more cores". Pushing it makes more
  of the tower ab initio rather than anchor-fitted.

## 5. P-finite recurrences for `D_j`, j ≥ 2

`D_1` is P-finite at (r,d) = (35,4), exhibited, which is how it reached k = 200
in 42 s (`results/onset-defect-depth1-closed.md`). If each `D_j` is likewise
P-finite, fitting the recurrence once from moderate k makes every later
evaluation free — and Undertow only ever needs `D_j` at two values of k per
level. Cheap to try, and it feeds §2 directly.

## 6. Closed doors — do not re-pitch

- **Dual-connectivity TM.** Track the *complement's* 4-connectivity (planar,
  hence non-crossing/Catalan partitions rather than crossing/Bell) and recover
  the component count from `C = χ + holes`, with χ already local and already
  implemented in `core/euler.h`. Dies on the prune: a configuration is doomed
  once its closed-image component count exceeds the number of filled runs in
  the frontier, so the count has to be carried, and (Catalan on b+1 runs) × (b
  component counts) exceeds Bell(b) at exactly the block counts that dominate —
  `b·Cat(b)` vs `Bell(b)` is 11,440 vs 4,140 at b = 8. The dual is *worse*,
  and the reason is the reason connectivity is the wall.
  **Baseline corrected 2026-08-22** (`results/dual-connectivity-blockcount.md`):
  the incumbent does not pay `Bell(b)` per block pattern, it pays `Cat(b)` —
  checkable, since `sum_b C(H+1,2b)Cat(b) = Motzkin(H+1)` and `Motzkin(22)-1`
  is the banked 400,763,222 to the digit. So the ratio is **exactly b at every
  block count**, 8x rather than 2.8x at b = 8, and the kill is uniform in b
  rather than holding only where the block counts dominate. The hybrid that
  would carry the dual only at small b has no regime: the ratio is <= 1 only at
  `b <= 1`, which is 0.0001% of the H = 21 frontier, whose mass sits at
  b = 6-8.
- **Evaluation/interpolation in the component-count variable.** Truncating the
  `v`-polynomial is only valid as the doomed-configuration prune, which cannot
  be expressed at a single evaluation point; carrying the polynomial explicitly
  costs more than it saves.
- Everything in `results/`'s four measured-dead levers (new sweep axis, finite
  lattice method, MPS/boundary compression, holonomic accelerator) and the
  45°/anti-diagonal TM — see the memory index, all falsified with receipts.

## 7. Not levers for counting, kept for completeness

GPU on ayr (GTX 1660, 6 GB — caps out around H = 15 and the inner loop is
hash-bound); mod-2 Exact Change compression (6× at cell level, mod 2 only,
`results/exactchange-probes.md`); out-of-core Motley at cell-step granularity
(~430 TB of I/O at H = 21, dead on arithmetic alone).
