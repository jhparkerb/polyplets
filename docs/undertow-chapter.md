# Undertow — source material for the manuscript it does not yet have

2026-08-22, executing `docs/last-orders.md` A2.1. **This file proposes; it does
not edit and it is not drafted prose.** Every number is quoted with the file
that measured it.

## Why this file exists

`paper/L8-below-onset.tex` has the below-onset *mathematics*: the exact frame
in which a column's entire below-onset content is `k+1` integers, the depth-1
closed form with rate 9, exponent `−1/2` and amplitude `√6/(27√π)`, the same
closure at depths 2–4, the measurement `θ_j = j − 3/2`, and the collapse of the
depth direction onto one velocity `α = 50/81`.

Nothing anywhere has the **application**. Those defects are what let a level of
the diagonal tower be pinned from cells *below* the onset instead of from the
two tallest cells on its diagonal — which took row 40's cost off its two poles
and produced a(41). Nine L papers, and the result that most changed what this
project can compute is in none of them.

**The decision this file does not make.** Whether this is a tenth L paper, a
section of P1, or jasonp's own prose is his call under
`docs/publication-split.md`. The material is the same either way.

---

## 1. The claim, in one sentence

The classical rule pins level `k` of the diagonal tower from two **above-onset**
anchors, `T(2k+1,k+1)` and `T(2k+2,k+2)` — the two tallest cells on its
diagonal. Undertow pins it from cells *below* the onset instead, using the
exactly-known defect to correct them, and those cells are `j` rows shorter.

The grand form (`docs/proofs/grand-form.md`, Lean-complete, standard axioms)
says a level carries **exactly two new constants**, so any two independent
linear equations pin it. Severance W3 supplies them from short cells:

    T(2k+1-j, k+1-j) = P_k(2k+1-j) · 3^(2k-3k-j) + D_j(k)

with `D_j(k)` computed ab initio from bounded-excess cluster-weight families —
no triangle, no wired `P_k`.

## 2. Why it is not circular, which is the first thing a reader will ask

`D_j(k)` is computed from cluster-weight families by a DP that never reads the
triangle and never reads `P_k`. The W3 gate keeps the two sides apart and is
the check that they stay apart. The three RED controls in
`experiments/undertow_pin.py`: a perturbed `D_j` breaks the pin; the same
equation offered twice is refused as singular; a corrupted lower level breaks
the pin.

An adversarial review (`results/undertow-review-{A,B,C}.md`,
`results/undertow-review-queue.md`) traced every input to its source. Its
sharpest finding is worth carrying into any manuscript rather than being
answered defensively: **two tower routes agreeing is not two confirmations**,
because every tower statement about `T(40,19)` contains `D_3(21)` and the two
routes share the grand form and most `D_j(21)`. Only agreement against an
enumeration crosses assumption families. That is what the Motley ladder then
delivered.

## 3. What it bought, with the measurements

**Reach.** Coverage becomes `n ≤ 2·H_max + J − 1` for exact depths up to `J`.
Every two extra depths buys one height, and a height is ~2.9× compute
(`results/lastditch-cost-ladders.md`).

**Row 40.** `P_19` pins from `T(37,18)` and `T(36,17)`; `P_20` from `T(38,18)`
and `T(37,17)`. Both pairs are inside Motley's already-banked `H ≤ 18` rows, so
`T(40,21)` and `T(40,20)` became rule-independent predictions with no new
compute.

**a(41).** Computed 2026-08-20 on dalby as two halves
(`results/a41/PROVENANCE.md`): heights 1..19 by real sweep — wall 16,998.7 s
(4.72 h) on 40 cores, rss_max 557 MB, run-dir peak well under 100 GB — and
heights 20..41 by the tower, with `k ≤ 19` from the wired table and `k = 20, 21`
pinned from below-onset cells.

    a(41) = 393811462683918679824582849262105

The comparison a manuscript should make: a(40)'s H = 21 pole alone was 36.4 h
on 32 cores with a 363 GB disk peak. a(41) did not pay it.

**Audit.** Depths 1–4 plus the two onset anchors give six equations for two
unknowns per level — four independent consistency checks on the banked
triangle's tallest cells, from short cells, through mathematics sharing nothing
with the sweep. Status: 18 of 18 wired levels re-derived exactly over every
available depth pair.

## 4. The external validation, which is new and which the manuscript needs

`results/undertow-square-validation.md`, 2026-08-22. The claim was tested on the
square lattice, where the counts are published by other people.

There `b = |D| = 1`, so the law is a plain polynomial and the depth-1 defect is
`D_1(k) = (−1)^(k+1)`. At every level `k = 1..6` the below-onset fit **equals**
the classical one as a polynomial and **reproduces the tallest cell it was
denied**, exactly. The square triangle's 21 rows sum to A001168 first, and a RED
control confirms the wrong defect sign breaks the fit.

This is the only check in the whole construction that crosses out of the
project. A manuscript that omits it is weaker than the work.

Its honest limit: `J = 1` on the square lattice, because only square `D_1` is
derived, so the saving there is one height rather than the king's two or three.

## 5. What is still soft, stated before a reader finds it

- **`P_21` has one pin pair and no holdout.** `k = 20` is pinned six ways with
  five independent checks; `k = 21` pins from `T(40,19)` and `T(39,18)` and has
  nothing checking it until depth 5 exists or `T(41,20)` is swept
  (`scripts/dalby_a41_h20.sh`, ~10–11 h on 48 cores, ~185–190 GB).
  `results/confidence.md` calls this the last soft spot in the construction and
  the manuscript should say the same.
- **`§1a` does not buy what it looked like it bought.** Solving the whole
  column is a reformulation, not extra redundancy: each below-onset cell brings
  one equation *and* one unknown `D_j(k)`. The honest accounting is
  `surplus = (banked cells whose depth has a known D_j) − 2`. This correction
  is worth including — it is the kind of thing a referee finds.
- **Depth 5's cost is contested**, ~110–390 GB depending on which per-K ratio
  is trusted, and the gate that must pass before `D_5` is used at `k = 21` is
  written and currently RED by design.

## 6. Where the pieces are

| what | where |
|---|---|
| the pin, with three RED controls | `experiments/undertow_pin.py` |
| the campaign record | `results/undertow.md`, `docs/lastditch-campaign.md` |
| the candidate list and closed doors | `docs/lastditch-ideas.md` |
| a(41)'s provenance | `results/a41/PROVENANCE.md` |
| the second source at Nmax 41 | `results/cutcount_b1/rows41/` |
| the adversarial review | `results/undertow-review-{A,B,C}.md`, queue |
| the grand form | `docs/proofs/grand-form.md` |
| the defect mathematics | `paper/L8-below-onset.tex` |
| external validation | `results/undertow-square-validation.md` |
| plain-terms confidence | `results/confidence.md` |

## 7. A note on L8

L8 was drafted 2026-08-18 and its own subject moved on 08-20: `§1a`'s
correction to the equations-versus-unknowns accounting, and the `§5` P-finite
kill (fitting `D_j`'s recurrence needs ~180 values of `k` where ~15 exist). A
paper whose subject advanced after it was drafted should absorb that or say so.
Whether Undertow becomes part of L8 or stands separately is the same decision
as §0 above.
