# OW-5 "Verbatim Wager" — universalize the diagonal law to row-local lattices

Read first: `polyplets/OUTWORKS-PLAN.md`;
`docs/proofs/universal-diagonal-law.md` (the paper-grade proof this brief
formalizes — the lattice class, Theorem A, the five steps, the instance
table); paper §6.3 (read-only) is its condensed twin. Then the Lean chain
in order: `Defs.lean`, `Finite.lean`, `Separation.lean`, `Weights.lean`,
`Peel.lean`, `Shape.lean`. Size L — the largest Outworks task, split into
three phases with a gate after each. Orchestrator reviews at each gate.

**The wager.** The paper claims the five king-proof steps carry over
VERBATIM with `b` (the up-offset count) in place of 3. If true, this is a
parameterization refactor of sorry-free code. If any step does NOT carry
over, that is a pre-publication finding: STOP, write down exactly which
step, which lemma, and why, and report — never patch the mathematics
silently. Either outcome is a success for the campaign.

## The lattice class (Lean formulation — pinned)

```lean
/-- A row-local lattice: nearest-neighbour row adjacency plus a finite
nonempty set of up-offsets. `b = D.card` is the drift count. -/
structure RowLocal where
  D : Finset ℤ
  hD : D.Nonempty
```

Adjacency: `adj L p q ↔ p ≠ q ∧ ((p.2 = q.2 ∧ |p.1 − q.1| = 1) ∨
(q.2 = p.2 + 1 ∧ q.1 − p.1 ∈ L.D) ∨ (p.2 = q.2 + 1 ∧ p.1 − q.1 ∈ L.D))`.

Scope note (record in the module doc): the paper's condition (R) allows
extra within-row adjacency; the Lean class fixes row adjacency to exactly
`|dx| = 1`. Every named instance lives in this subclass (square `D = {0}`,
hex `D = {−1, 0}`, king `D = {−1, 0, 1}`, five-neighbour `D = Icc (−2) 2`,
degenerate `D = {−2, 0, 2}`). King instance sanity: `adj (king) = kingAdj`
— prove this equivalence outright (it is the definitional anchor for
phase C; `kingAdj`'s `|Δx| ≤ 1 ∧ |Δy| ≤ 1` form vs the row/up split is an
`omega`-grade case bash).

## Architecture (decided — do not relitigate)

A parallel generic tree under `polyplets/Polyplets/Universal/`, leaving the
existing king files untouched (their guarded audit footprints must not
move). The king case is RE-DERIVED from the generic tree at phase C as a
consistency theorem, not replaced. Rationale: zero churn risk on the 8592
green jobs; the duplication is bounded because phase A abstracts the
algebra once.

### Phase A — abstract shape engine (`Universal/AbstractShape.lean`)

Shape.lean's proofs (`shape_d`, `shape`, `shape_production`,
`production_int_onset/all`) consume Peel/Weights only through a finite
interface: the numbers `d k H`, `T n H`, the weight families `V ℓ j`,
`Vt ℓ j`, the two recursions, and base facts. Extract that interface:

```lean
structure PeelSystem where
  b : ℕ
  hb : 1 ≤ b
  d : ℕ → ℕ → ℕ
  T : ℕ → ℕ → ℕ
  V Vt : ℕ → ℕ → ℕ
  -- recursion fields: the b-generic forms of Peel.lean's d_rec and c_ident,
  -- statement shapes copied verbatim with 3 ↦ b, plus whatever base/support
  -- facts Shape.lean's proofs actually use (d at small H, vanishing/support
  -- ranges of V/Vt per level, …)
```

Method for the field list: port Shape.lean's proof scripts against the
abstract `S : PeelSystem`; every place a script reaches into
Peel/Weights becomes a field. Keep the list MINIMAL (if a fact is derivable
from other fields, derive it) and record the final list prominently in your
report — it is the formal answer to "what does the shape law need from a
lattice". Deliverables: `S.shape_d`, `S.shape`, `S.shape_production`,
`S.production_int_all` — statements identical to Shape.lean's with
`3 ↦ S.b` (the `n − 1 − 3k` exponent becomes `n − 1 − 3k` still — check:
in the king form the 3 in the exponent offset is `2k + (k+1)` bookkeeping
from `b^(1+2k)`, NOT the drift 3; from the proof doc, universal is
`T(n, n−k) = P_k(n) · b^(n−1−3k)` with `P_k = b^(1+2k) q_k` — the 3 in the
exponent is structural (three = 1+2 from the two normalizations), stays).
The integrality step's p-adic argument (proof doc step 5) runs per prime
`p ∣ b` — port `production_int_*` accordingly; this is the one step whose
king proof may lean on 3 being prime. If it does and the generic version
genuinely needs new mathematics, that is a WAGER FINDING — stop and report
before inventing.

**Gate GD-1**: `AbstractShape` green; the king `PeelSystem` instance
(fields discharged from the existing `Peel.lean`/`Weights.lean` theorems)
yields `shape_production` for king, and the derived statement is
definitionally identical to `Shape.lean`'s (`example : … := king_system.shape_production …` typechecks against the original statement).

### Phase B — generic geometry (`Universal/{Defs,Finite,Separation,Peel}.lean`)

Parameterize the geometric front over `L : RowLocal`: connectedness,
canonical anchoring, `T L n H` (ncard), crossing lemmas, width bound,
finiteness; then the separation surgery and the two peeling bijections,
producing a `PeelSystem` for every `L`. This is where the verbatim wager
is settled — the king files are the template:

- `Defs`/`Finite`: mechanical (the crossing lemmas use only |Δrow| ≤ 1 —
  verify; the width bound uses max |dx| which is now `max |D| ∪ {1}`).
- `Separation.lean` (walk-row separation, boundary-dart excision): the
  paper says step 1 uses only "adjacency changes the row index by at most
  1". Check every lemma; the dart excision touches actual offsets — the
  place a hidden king-dependence would most plausibly hide.
- `Peel.lean` (1748 lines, three `card_nbij'` bijections with shift/xNorm
  renormalization): the heavy port. The drift step "3 choices" becomes
  "`b = D.card` choices"; the shift normalization must use a canonical
  enumeration of `D` (order it; `Finset.orderIsoOfFin`). Generic weights
  `V L ℓ j` defined as the king ones are, with the same spread bounds
  (now in terms of `max(1, max|D|)`).

Do NOT port `Grand/` (the μ/staircase/exp tier): the universal claim in
the paper and proof doc is Theorem A (shape law) — the grand form per
lattice is out of scope (Theorem B mod-p spine is also out of scope:
blocked machinery, see OUTWORKS-PLAN roster).

**Gate GD-2**: generic `PeelSystem L` construction green for every `L`;
instantiating at king and discharging against the EXISTING `Peel.lean`
values (`d`, `V 1 1 = 25`, …) agrees — spot-check by `native_decide` on
2–3 small cells per the Compute pattern. The wager is settled at this
gate; the report states "verbatim: yes" or the precise divergence.

### Phase C — instances (`Universal/{King,Square,Hex}.lean`)

- **King**: `adj = kingAdj` equivalence ⇒ `T (king) = Polyplets.T` (ncard
  of the same set) ⇒ the generic law re-derives `shape_production`;
  cross-check statement-level with Shape.lean (GD-1's example, now via
  phase B's system).
- **Square** (`D = {0}`, b = 1): the law reads `T(H+k, H) = q_k(H)` — the
  by-height diagonals of ORDINARY POLYOMINOES are eventually polynomial.
  Pin `P₁` (paper: density 4 = 2², `P₁(n) = 4(n−2) = 4n − 8`): build the
  computable twin `Tc L` (port `Compute.lean`'s bounded closure
  generically — it is already adjacency-agnostic modulo the neighbour
  enumeration), native_decide two square anchor cells, Lagrange-pin at
  level 1 (the `Pin.lean` pattern: base + one solve cell).
- **Hex** (`D = {−1, 0}`, b = 2): pin `P₁(n) = 9n − 15` the same way
  (paper instance table; density 9 = 3²).
- Anchor values: compute in-Lean via the generic `Tc` — the repo has no
  banked square/hex triangles; do not import external data. Sanity: the
  square `Tc` row sums at small n must reproduce A001168 fixed polyominoes
  (1, 2, 6, 19, 63 for n = 1..5) — assert two of these by native_decide as
  a cross-family gate.

**Gate GD-3**: three instance files green; `P₁` pinned for square and hex;
report includes the generic-vs-king statement diff (should be none).

## What NOT to do

- Do not touch the existing king tree or its audit guards.
- Do not attempt V/Vt enumerations beyond level-1 weights for the new
  instances (`V 1 1`-analogues); higher pins are follow-up work, not this
  brief.
- Do not widen the class beyond the pinned `RowLocal` (no extra row
  adjacency, no period-2 polyiamond extension — the proof doc marks that
  out of the literal class).
- Do not chase onset sharpness (per-lattice empirical, per the proof doc).

## Done criteria

All three gates passed; `lake build` green, no `sorry`; axiom audit:
phase A/B standard-three, instance anchors carry `Lean.ofReduceBool`
exactly; guards added for `AbstractShape`'s four deliverables and each
instance `P₁`. Commits per phase:
`lean-ow: Universal A — abstract shape engine`,
`lean-ow: Universal B — row-local peel systems (wager: <verdict>)`,
`lean-ow: Universal C — king/square/hex instances`.
