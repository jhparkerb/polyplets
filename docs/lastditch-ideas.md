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

Status: `experiments/undertow_pin.py`, three RED controls green (perturbed
`D_j` breaks the pin; one equation twice refused as singular; corrupted lower
level breaks the pin). `--verify` re-derives every wired level from below-onset
cells — that is the decisive run.

Ways it dies: `D_j(k)` turning out to depend on `P_k` after all (it does not,
by construction — the W3 gate keeps the two sides apart); the two depth
equations being dependent (they are not: the 2×2 is `[[1,n₁],[1,n₂]]`); the
grand form's residual failing to be linear at some level (checked in
`extract_ab`, which raises).

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

The unknown is how the family DP grows in `emax`. An `emax = 4` ladder at
K = 8..18 is measuring it now; e = 3 at K = 19 was 146 s.

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
