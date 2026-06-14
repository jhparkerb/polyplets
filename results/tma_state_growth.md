# Transfer-matrix state-growth calibration (square-8 / polyplets)

*Originally measured 2026-06-14; **revised same day** after building the
viable-mask + size-budget-prune engine and re-measuring. The first version of
this note contained a math error (see "Correction" below); the numbers and
verdict here supersede it.*

Question: can the column transfer-matrix method — a counting algorithm
completely different from the Redelmeier generation used in the a(19) campaigns
— reach size 19, giving an **algorithm-independent** confirmation of a(19)?
(The gympie+ayr campaigns decorrelate decomposition/compiler/ISA/hardware but
share the generation algorithm.)

## Correction to the earlier note

The earlier note claimed the standard aspect/transpose trick caps the swept
(boundary) height at ⌈n/2⌉=10, giving "megabyte scale". **That is false for
king-connected animals.** It relies on `n ≥ w+h−1` (the min cells an
*edge*-connected polyomino needs to span a w×h box). With king moves the min is
`max(w,h)` — a diagonal of 19 cells spans a 19×19 box — so the only universal
bounds are `n ≥ w` and `n ≥ h`, and the diagonal saturates both at `w=h=n`.
Transpose symmetry still halves the bookkeeping (`A = 2·#(w>h) + #(w=h)`) but
**cannot bound the swept height**. So feasibility rests on size-budget pruning
plus the (small) empirical growth base — not on a height cap.

## Measurement (optimized engine: viable-mask + admissible size-budget prune)

Peak number of distinct boundary signatures held at once (the memory
bottleneck), `build/tma square8 N`, `peak_states` on stderr. With the prune
active, every retained state is within budget. Wall times are single-core on
gympie; "v1" is the engine after the speed pass (fixed-size `Sig` keys in a flat
open-addressing state store, stack-array union-find -- no per-transition or
per-state heap allocation).

| n  | peak states | ratio | wall v0 | wall v1 | RSS v1 |
|----|-------------|-------|---------|---------|--------|
| 11 |      17,552 |  —    |    2 s  |   —     |   —    |
| 12 |      43,224 | 2.463 |    9 s  |   —     |   —    |
| 13 |     106,050 | 2.453 |   42 s  |   —     |   —    |
| 14 |     259,422 | 2.446 |  184 s  |  142 s  |   —    |
| 15 |     633,088 | 2.441 |  810 s  |  604 s  | 325 MB |
| 16 |   1,541,984 | 2.435 | 3,643 s | 2,635 s | 1.1 GB |

State-count growth base **k ≈ 2.44**, easing down slightly with n (the counts
are identical across engine versions; only speed/memory changed). Wall-time base
**≈ 4.3×/step** -- steeper than 2.44 because each larger n adds a column to every
sweep *and* enlarges the working set (cache-miss bound past ~10⁶ states). The v1
speedup grows with n (28% at n=16) as locality matters more.

Effect of the size-budget prune: **modest**, ~15–17% fewer states than no prune
(n=11: 20,597→17,552; n=12: 52,194→43,224) — it does not lower the growth base.
(The earlier note's much smaller "pruned" figures came from an *over*-aggressive,
inadmissible bound that dropped real animals; the bound here is admissible — the
gate reproduces every published A006770 term with it live.)

## Projection to n=19

- **States / memory:** 1.54M × k³ ≈ **~2.2×10⁷ peak states**. The flat store
  carries db+next double-buffered, ~**13–19 GB** at peak (incl. a grow
  transient). Fits gympie's 24 GB. Per-height checkpointing means an OOM on one
  height costs only that height (rerunnable), so memory is a bounded risk.
- **Runtime:** ~4.3×/step ⇒ 2,635 s × 4.3³ ≈ **~2.4 days** single-threaded
  (down from ~3.8 days for the v0 `unordered_map<string,…>` engine).

## Feasibility verdict: YES — runnable single-threaded

A genuine algorithm-independent n=19 check is achievable, correct (engine
validated against A006770 + the generation result through n=15, exact), and now
fast enough to run as-is: **~2.4 days, ~13–19 GB, on gympie**, crash-resumable
per height. That is the planned run.

Further speedups exist if wanted but are NOT needed for this run:
- **Per-height parallelism** — heights are independent sweeps; trivial in
  principle but the big heights are also the memory-heavy ones, so running them
  concurrently risks OOM (would need careful scheduling). One large H dominates
  the critical path, so the ceiling is only ~3–4× anyway.
- **Within-sweep parallelism** (shard the state map across cores) → near-linear,
  but more invasive. Reserve for an a(20) attempt, not a(19).

## Consequence for confidence

a(19) is already **confirmed** by the two decorrelated generation campaigns
(RESULTS.md R1). This transfer-matrix path adds *algorithm independence* — the
one residual the campaigns cannot cover (a shared generation-algorithm bug). The
engine is correct through n=15; reaching n=19 is now a speed task, not a
correctness or feasibility question.
