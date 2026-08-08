# OUTWORKS-PLAN — extending Lean coverage beyond the height triangle

2026-07-30. Master plan for the second Lean formalization campaign, executed by
**Opus agents** (one per task brief, `polyplets/briefs/OW*.md`), orchestrated
from a supervising session — same machinery as `GRANDFORM-PLAN.md`.

## Why "Outworks"

The Grand campaign fortified the keep: the height-triangle diagonal law and
grand form are Lean theorems. But the paper's headline object `a(n)` does not
exist in the Lean tree at all, and every claim outside §6.1 is paper-proved or
computational. This campaign builds the outworks: the sequence itself, the λ
apparatus, and the highest-value theorems ranked by the 2026-07-30
claims-vs-Lean audit (81 claims mapped; audit output preserved in the
supervising session).

## Target roster

| Task | Name | Deliverable | Size | Depends on |
|---|---|---|---|---|
| OW-1 | Name the Sequence | `a n` defined; `a n = Σ_H T n H`; computable twin + banked anchors; §9 GF lower bound | S | — |
| OW-2 | Fekete's Ladder | λ = lim a(n)^{1/n} exists (Klarner supermultiplicativity + Mathlib Fekete); first in-Lean numeric λ lower bound | M | OW-1, OW-3 |
| OW-3 | Corset | rigorous exponential upper bound on a(n) (paper's crude scan bound, target λ ≤ 5⁵/4⁴) | M | OW-1 |
| OW-4 | Factorial Residue | k!·P_k ∈ ℤ[X] from `production_int_all` | S | — |
| OW-5 | Verbatim Wager | diagonal law universalized to row-local lattices (paper §6.3); square/hex instances | L | — |
| OW-6 | Moat and Diamond | Theorem 2 (single-hole max area = ⌊(n−2)²/8 + ½⌋); hole machinery from scratch | L | — |
| OW-7 | Eightfold Count | Burnside identities, Bilateral = ½(H+D), R₉₀ vanishing, integrality (§7) | M | OW-1 |
| OW-8 | House Arrest | Northcott finiteness at bounded degree + house (the reusable piece of Theorem 3's step 4) | S | — |

## Survey corrections vs the 2026-07-30 claims audit

Found while drafting the briefs (the briefs already incorporate these):

- **OW-8 shrank**: the pinned Mathlib HAS Northcott for the Mahler measure
  (`Polynomial.finite_mahlerMeasure_le`, `NumberTheory/MahlerMeasure.lean`,
  2025) plus Kronecker (`pow_eq_one_of_mahlerMeasure_eq_one`). The audit's
  "Mathlib only has fixed-field `finite_of_norm_le`" is superseded; OW-8 is
  a bridge lemma, size S.
- **OW-6 lower bound is uniform**: the audit's "n ≢ 0 mod 4 construction
  open" is stale — `results/maxhole-proof.md` closed it 2026-07-12 with the
  parity-aligned box family (`experiments/maxhole_box_construction.py`).
  Real subtlety preserved in the brief: (a,b) = (2,1) is degenerate, so
  n = 5 needs the pad-cell special case.
- **OW-3 arithmetic verified**: `C(5n,n)·256^n ≤ 3125^n` reduces to a ratio
  inequality whose difference polynomial is
  `400000n⁴ + 1030000n³ + 935000n² + 349280n + 44280` (n⁵ cancels; all
  coefficients nonnegative — `positivity`-grade).
- **OW-4 has no Mathlib shortcut**: no integer-valued-polynomial API exists
  (`RingTheory/Binomial.lean` is binomial rings; the connection is a TODO
  there); the brief specs the finite-difference/binomial-basis proof from
  scratch, reusing Shape.lean's Δ machinery where it exists.

Explicitly OUT of scope (audit verdict: blocked on machinery Mathlib lacks,
not worth building here): the mod-3 spine (char-3 Lagrange inversion), the
dm-mirror quasi-polynomial law (Ehrhart), Theorem 3 non-D-finiteness in full
(Perron–Frobenius + Pringsheim + D-finiteness, all absent from Mathlib), the
λ ≤ 9.3154 certificate (type-system soundness exists only in Python), the
hole-graded diagonal laws (need OW-6's machinery plus mod-3), and every
computed value including a(40).

## Task DAG

```
OW-1 Sequence ──► OW-3 Corset ──► OW-2 Fekete's Ladder
        └───────► OW-7 Eightfold Count
OW-4 Factorial Residue     (independent)
OW-5 Verbatim Wager        (independent, largest)
OW-6 Moat and Diamond      (independent)
OW-8 House Arrest          (independent)
```

Parallelism: OW-1, OW-4, OW-5, OW-6, OW-8 can all start immediately;
OW-3 and OW-7 when OW-1 lands; OW-2 last of its chain.

## Shared conventions (every agent MUST follow — GRANDFORM rules carried over)

- **Repo/branch**: work in `~/src/polyominoes` on branch `lean-outworks`
  (create from master if absent). Commit per completed unit with prefix
  `lean-ow:`; NEVER push; never touch files outside `polyplets/`; never edit
  a file that has a `.swp` sibling; the paper
  (`paper/polyplets-report.tex`, `paper/technical-report.tex`) is READ-ONLY.
- **Build**: `cd polyplets && lake build` (mathlib cache fetched; on fresh
  state `lake exe cache get` first). Toolchain pinned
  (`leanprover/lean4:v4.31.0`, mathlib `v4.31.0`) — NEVER bump it.
- **Module layout**: new files under `polyplets/Polyplets/`, namespace
  `Polyplets`. Standard copyright header (copy from `Pin.lean`), `/-! # -/`
  module doc, minimal imports.
- **Done = green**: `lake build` succeeds with ZERO `sorry`, axioms =
  `[propext, Classical.choice, Quot.sound]` plus `Lean.ofReduceBool` exactly
  where the brief allows native_decide. Every headline theorem gets a
  `#guard_msgs`-wrapped `#print axioms` in the audit point (extend
  `Grand/Audit.lean` or a new `Audit` section per brief).
  *(Toolchain correction, 2026-07-31 review: on lean4 v4.31.0
  `native_decide` emits a per-declaration axiom
  `<thm>._native.native_decide.ax_1_1`, not `Lean.ofReduceBool` — read
  every "ofReduceBool" in this plan and the briefs as that per-declaration
  leaf; the guards in `AuditOutworks.lean` record the real names, so the
  trusted base grows by one named leaf per anchor.)*
- **Style**: mirror `Shape.lean`/`Pin.lean` (docstrings everywhere, `omega`
  for index arithmetic, `exact_mod_cast` at casts, `norm_num` literal guards).
  Linters on, keep green.
- **Do not re-prove what exists**: read `PROOF-STATUS.md` first; `d_rec`,
  `c_ident`, `shape*`, `production_int_all`, `grand_form`, `lead_coeff_25`,
  the V/Vt weights, `Tc`/`Tc_eq_T` all exist.
- **STOP-and-report**: if the mathematics diverges from the brief (an
  argument the paper calls verbatim does not carry over; a claimed detail is
  genuinely open), STOP and report the exact divergence — never patch the
  math silently. A divergence here is a pre-publication finding, not a
  formalization inconvenience.
- **Reporting**: final message = files written, build status, axiom audit of
  main results, deviations from brief and why.

## Escalation & review protocol (orchestrator side)

- Orchestrator reviews OW-2's concatenation injection and OW-6's committed
  scope BEFORE those agents start proving; reviews each merge into
  `lean-outworks`.
- Agent stuck after two focused attempts on a lemma → STOP, report exact
  goal state; orchestrator unsticks.
- Merge `lean-outworks` → master at milestones: after the OW-1/3/2 chain
  (λ exists with two-sided bounds), and per independent task as each lands.

## Verification gates (cumulative; details in each brief's Done criteria)

- G-A (OW-1): `a 1..6` anchors match banked A006770 row sums by
  native_decide; `a_eq_sum` standard-axioms, guarded.
- G-B (OW-3): `a_le_choose` with NO native_decide (the injection is a
  proof); ratio inequality closes by positivity.
- G-C (OW-2): `lambda_tendsto`/`lambda_le` standard axioms; `lambda_lb`
  gives the first machine-checked numeric bracket 3.95 < λ ≤ 3125/256.
- G-D (OW-4): `production_factorial_int` standard axioms, guarded.
- G-E (OW-5): three phase gates GD-1/2/3 (see brief) — abstract engine,
  the wager verdict on the geometric port, king/square/hex instances with
  P₁ pinned; existing king audit guards untouched throughout.
- G-F (OW-6): `maxhole_lower` unconditional with anchors matching banked
  M(n); upper bound lands unconditional or conditional on the named
  `MoatBound` lemma (reported either way).
- G-G (OW-7): the three Burnside equations + `r90_vanish` standard axioms;
  anchors match `results/sym_counts.txt`; derived Free/OneSided/Bilateral
  spot checks at n = 4 (22 / 34 / 10).
- G-H (OW-8): all three finiteness deliverables standard axioms, no
  native_decide.

## Post-campaign

All eight briefs landed and merged 2026-07-30. Adversarially reviewed
2026-07-31 — `docs/reviews/outworks-adversarial.md` (zero critical, zero
statement-fidelity defects; the review's claim-hygiene fixes are recorded
in `PROOF-STATUS.md`). Where a brief and the landed code differ (OW-2's
concatenation design, OW-3's `card_common_neighbours` naming, OW-6's
uniform family), the briefs are left as the historical contract and the
deviations are documented in the module docs and the review.

## Briefs (all ready for execution)

`briefs/OW1-sequence.md` · `briefs/OW2-fekete.md` · `briefs/OW3-corset.md` ·
`briefs/OW4-factorial.md` · `briefs/OW5-universal.md` (3 phases) ·
`briefs/OW6-diamond.md` (2 phases) · `briefs/OW7-burnside.md` ·
`briefs/OW8-northcott.md`

Suggested execution waves (respecting the DAG, ≤ 4 agents at once):
wave 1 = OW-1, OW-4, OW-8, OW-5(A); wave 2 = OW-3, OW-7, OW-5(B),
OW-6(a); wave 3 = OW-2, OW-5(C), OW-6(b).
