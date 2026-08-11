# Refuter A: Proposer 1 (proof-first) — verdicts

2026-08-11, Refuter A of the triangle structure hunt
(`docs/triangle-structure-team-brief.md`). Targets: the candidates of
`results/triangle-hunt-proof-first.md`
(`experiments/tristruct/candidates/p1_inequalities.py`,
`p1_deficit_families.py`, `p1_algebraic_mod3.py`).

Checker: `experiments/tristruct/refA_prooffirst_check.py` (log
`refA_prooffirst_check.log`), exact integer arithmetic; verify.py verdicts
independently re-run and reproduced for both candidate files. All numbers
below are from those runs.

## Verdicts

| candidate | verdict |
|---|---|
| p1-two-term-lower-bound | **SURVIVES** (proof audited; bound not vacuous) |
| p1-deficit4-family-mod3 | **SURVIVES** (thin, correctly priced by the proposer) |
| p1-deficit5-family-mod3 | **SURVIVES** (same) |
| d=3 culled pattern / T(40,26) prediction | cull CORRECT; the open-cell hit is real, ~1.6 bits |
| d=6 CULLED(FIT-ERROR) | verdict wrong as stated — see the refuter-found pattern below |

## Target 1 — the proved inequality

**Proof audit (the attack the lead asked for).** Both injections check out:

- *Walk-cap* is well-defined into T(n,H): the new cell sits in a new top
  row at |dx| ≤ 1 from the old top-row leftmost cell, so the image is
  connected, has exactly n cells and height exactly H, and its top row is
  a single cell. Inverse: delete the unique top cell; the remaining
  animal's top row is the original's top row, so δ is recovered as
  col(deleted) − col(leftmost of top row). Injective from 3 disjoint
  copies; no height leak (exactly one row added).
- *Grow-right* adds a cell in the same top row (the slot right of the
  rightmost top-row cell is empty by definition of rightmost), so height
  stays exactly H; delete-top-right inverts, giving injectivity. Every
  image has ≥ 2 top-row cells.
- Disjointness is by top-row cardinality — airtight.
- H = n equality: height n with n cells forces one cell per row,
  consecutive rows at |dx| ≤ 1, giving 3^(n−1) = 3·3^(n−2); matches the
  banked anchor T(40,40) = 3^39. The candidate code demands equality
  exactly there and inequality elsewhere, matching the theorem.
- Edges: H = 2 uses T(n−1,1) = 1 (fine); H = n−1 exercises both maps
  (fine); H = n excludes grow-right via T(n−1,n) = 0 (handled).

I could not break the proof.

**Measurements.** Holds on all banked cells 2 ≤ H ≤ n ≤ 40, zero
violations; equality set is EXACTLY the H = n column (39 cells — so the
proposer's "equalities exactly H=n", verified only to n ≤ 13 on own data,
holds grid-wide). Tightness: k=1-diagonal ratio decreases monotonically to
**1.0170 at (40,39)**, confirming asymptotic tightness; and the global
worst slack over every strict banked cell is only **4.59× (at (40,5))** —
the bound is within 2.2 bits of the truth everywhere in the grid, so
"vacuous" is refuted, not just asserted. Rule-level check: the inequality
also holds on Refuter A's own independently-written TM data (H ≤ 6) out to
**n = 60, beyond the banked grid** (295 cells).

**Bits:** ~0 on a(40), exactly as the proposer concedes (one-sided bound;
the equality column is closed-form territory). No tier correction needed;
"softer, proved, zero-input" is the honest label and it carries it.

## Target 2 — deficit families d = 4, 5 (and the luck number)

Recomputed from banked data with per-cell classification against
`known.py`'s own predicates: d=4 is constant 2 on k = 4..14 and d=5 on
k = 5..14, with **exactly one law-free cell each** (k = 14: (39,25) and
(38,24)) — every other holdout cell is diagonal-law-implied, as the
proposer already conceded. The n ≥ 30-style region attack has no purchase:
the family region (k ≥ d, i.e. the in-window sleeve) is principled — it is
where deficit is defined and where the proved d = 1,2 analogues live. I
also measured what the region excludes: the below-onset tails. d=4's tail
(1, 0) breaks the constant, d=3's tail (0) breaks the period — so the
in-window boundary is content-bearing but honest. (d=5's tail (2,2)
happens to continue the constant; those two cells are column-closed-form
cells, H ≤ 4, so they add nothing.)

**The luck rate the lead asked for.** The right null is the empirical
residue distribution over ALL law-free in-grid sleeve cells — there are 42
of them (k = 14..19, all of them, none reachable by any known.py
predicate). Distribution mod 3: **{0: 16, 1: 13, 2: 13}** — statistically
uniform. So a family-shaped pattern hits one law-free cell with
probability ≈ 0.31, and the three predictions that were made (d=3 → 1 at
(40,26); d=4 → 2 at (39,25); d=5 → 2 at (38,24)) pass jointly with
a-priori probability **0.31³ = 0.0297** (uniform null 0.037). Selection
was mild — one pre-registered hypothesis class (the proved d = 1,2 class),
four lines tried, all reported including the failure — so ~3% is the
honest joint luck rate: real signal, thin, ≈ 1.7 bits per family. A
within-direction empirical control on further lines is impossible: d ≥ 7
has ≤ 3 fit cells under the class's own rules, which is why the base-rate
route above is the correct quantification.

Verdict: SURVIVES, tier C, with the proposer's own thinness pricing
confirmed as accurate (measured 1.69 bits/cell vs claimed 1.585 — the
claim is marginally conservative).

## Target 3 — the d=3 pattern and T(40,26)

All verified directly from banked data: the period-3 pattern 2,0,1 holds
on k = 3..14; zeros fall exactly at k ≡ 1 (mod 3); and **T(40,26) ≡ 1
(mod 3) — the prediction is banked-true**. Ruling on content vs artifact:
the harness cull is CORRECT (its five scored holdout cells k = 9..13 are
all diagonal-law-implied — that is the interpolation tautology at work),
but the (40,26) cell at k = 14 is not law-reachable, so the hit is real
content: ~1.6 bits on a genuinely open row-40 sleeve cell. One repricing:
the sleeve-zero census (`results/ternary-spine.md`, n ≤ 40 table) already
banks WHICH sleeve cells are zero — the zeros retrodiction is therefore a
restatement of law-implied/banked facts (organizing value only), and what
the pattern adds at (40,26) beyond the census's "nonzero" is the choice of
unit, 1 bit of the 1.6. Not an artifact; a thin, real regularity.

## Refuter-found: the d=6 line is period 3 on the full grid

The proposer's CULLED(FIT-ERROR) verdict ("no pattern in class, honest
unresolved") is wrong as a statement about the line — it is an artifact of
the class's ≥ 2p fit-point prudence rule (period 3 needs 6 fit points;
n ≤ 22 gives d=6 only 4). Measured: T(3k−5, 2k−5) mod 3 for k = 6..15 is

    2, 1, 1, 2, 1, 1, 2, 1, 1, 2   — exactly (2,1,1) by (k−6) mod 3,

with TWO law-free hits: k = 14 → (37,23) ≡ 1 and k = 15 → the open row-40
sleeve cell **(40,25) ≡ 2**, both matching. Caveat, stated plainly: I
found this by reading the full grid, so unlike the d ≤ 5 candidates it is
post-hoc — its two law-free cells are observations, not predictions, and
I claim no bits for it. Its status: the pre-registered class DOES fit the
d=6 line; together the four lines d = 3..6 read (2,0,1), 2, 2, (2,1,1) —
every sleeve unit family probed so far is eventually-periodic with period
1 or 3. The correct next step is not more fitting; it is the proposer's
own named proof route (Lagrange–Bürmann to the mod-3^(d+2) master curve),
which would convert d = 3..6 from ~5 thin bits into theorems. That is the
natural round-2 narrow chase from this corner.

## Targets 4/frame — adjudication of the negative machinery

- **Frame identity verified computationally**: for k = 1..12,
  (1−3z)^(k+1) · Σ_H T(H+k,H) z^H truncates to an integer polynomial of
  degree ≤ 2k+1 (every coefficient beyond 2k+1 vanishes across the whole
  grid), and the mod-9 refinement T(H+k,H) ≡ r_{k,H} + 3(k+1)·r_{k,H−1}
  holds on every valid cell. The claimed two-line derivation from
  diagonal-law Step 4 is correct algebra once R_k is a polynomial, and it
  measurably is.
- **Freshness logic: sound as scoped.** Mod 3 the cell↔coefficient map is
  triangular with unit diagonal, so open-cell residues are in bijection
  with fresh r_{k,H} — the shape theorem alone genuinely imposes no
  relation among them. The conclusion is correctly scoped by "of this
  frame": a cross-k structure (the deficit families are exactly that) can
  still constrain sleeve cells; nothing in-frame reaches the below-onset
  H = 15..19 block of row 40. The pricing of that block as not checkable
  mod 3 by in-grid-fittable frame structure stands.
- **Empty kernel: valid as bounded.** A true algebraic equation inside
  the ansatz box would fit any truncation, so an empty kernel on the
  n ≤ 22 window is a genuine exclusion for the box — not merely "none
  found". The box-too-small escape (larger degrees/heights) is real and
  the proposer states it; the selftest (synthetic algebraic series,
  kernel found + Hensel reproduction) covers the false-negative-by-bug
  case. No correction.

## Attacks tried that found nothing

Proof audit (injectivity, disjointness, height leaks, edge cases H = 2,
H = n−1, H = n); vacuousness (refuted by measurement: max slack 4.59×);
equality-set drift (exactly H = n, grid-wide); rule-level failure beyond
the grid (own TM, n ≤ 60, holds); overfitting on the families (4 params,
proper fit/holdout, thinness conceded and re-measured); region gaming
(below-onset tails measured; boundary principled); luck (quantified at
0.0297 joint against the empirical 42-cell null); restatement
(`subgroup-mod4`/`percell-mod4` are mod-2/4 ground, no overlap; census
overlap identified and repriced above); harness reproduction (both
candidate files re-run, verdicts identical).
