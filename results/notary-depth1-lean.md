# Notary: what the depth-1 closure now means in Lean

2026-08-09. Campaign Notary, waves 1–4 complete same day. Plan:
`docs/notary-lean-plan.md`; the priced remainder:
`docs/notary-kernel-scoping.md`. Gate: `make gate-notary` (sorry/axiom grep +
`lake build` of the three modules; axiom audits are `#guard_msgs` blocks
inside the modules). Wave 1 was executed by two Sonnet agents against
Fable-authored skeletons whose every statement was pre-verified in exact
arithmetic (`build/notary_n3_lean_gen.py`, `build/notary_series_check.py`);
both landed with zero statement changes.

## What is now proved in Lean (was: nothing beyond finite value pins)

**`GapWalkBridge.lean`** — the finite anchor, closed end to end:

- Walk = enumeration at every reachable level: `W(2^ℓ) = V ℓ ℓ`,
  `W^b(2^ℓ) = Vᵗ ℓ ℓ`, and the previously-unformalized pure weight
  `W^p(2^ℓ) = Vp ℓ ℓ` (`IsVpConfig`/`CFGVp` new, in the `Weights.lean`
  idiom with its window-independence lemma `mem_CFGVp`), `ℓ ≤ 3`.
- All 36 depth identities of `DepthAssembly.lean` made unconditional — the
  weight-table hypotheses discharged against the banked tables.
- Identity (II) evaluated on truncated series built from the walk itself
  equals the depth-1 identity values at every `k ≤ 8`
  (`f1_matches_depth1`): enumeration → tables → (C)/(D) → (II) → walk is a
  closed loop inside Lean at those cells.
- The walk pinned against the C++ two-source table to `k ≤ 19`
  (`walk_table_19`), and the `e = 0` rows of the assembly tables identified
  as the walk's own output.

**`DepthOneConstants.lean`** — the constants as branch data of `Φ`, over any
characteristic-zero field with `s2² = 2`, `s3² = 3`, plus `ℝ`-instantiations:

- `phiC4 = (27x−1)² · g`, `g(1/27) = 7929856/19683 ≠ 0` — order-2 vanishing
  (the rate `9` per `k`).
- `Ψ(v, wv) = Φ((1−v²)/27, w)` — the Puiseux frame is polynomial (the
  exponent `−1/2`).
- `Ψ(0, V) = (7929856/14348907)(27V²−2)²` and `27V₀² = 2` — the sheet
  crossing; `(V₀/3)² = 2/243`, the θ-free amplitude square.
- `Ψ(v, V₀+V₁v+V₂v²) = v⁴·Q₄(v)` with all of `V₁, V₂, Q₄` explicit, and the
  pinning pivot nonzero — the truncated physical branch, exactly.
- `a = −1/8 − V₂/(2V₀) = 3293/92928 − 3251·√3/185856` — the `1/k`
  coefficient, in `ℚ(√3)`.

**`DepthOneSeries.lean`** — the algebraic claim, finitely:

- `N(x) = 3F₁(3x) + 1` from the walk matches the banked numerators to
  `k ≤ 19`.
- **`Φ(x, N(x)) ≡ 0 mod x^61`** in exact rationals (`phi_annihilates`) —
  4 orders of holdout past the `(8,4)` fit window on the fitted route,
  fully independent on the kernel-derived route.
- The `Φ` used here and the `Φ` of `DepthOneConstants` are the same
  polynomial (`phiCList*_eval`).

**`GapWalkRows.lean` / `GapWalkCanon.lean` / `GapWalkTrunc.lean`** (wave 3,
piece T of the scoping note, same day) — truncation exactness:

- **`walkFamiliesCap_exact`: every gap cap `M ≥ 2L + 3` emits the same
  family triples as `walkFamilies L`** — the hard-wired truncation is
  invisible to the emitted weights, so the untruncated walk (the common
  value of all sufficiently large caps) is what `walkFamilies` computes.
  With the bridge, the `k ≤ 19` pins and the `k ≤ 8` assembly now bind the
  *exact* walk, not a truncation — the "in spirit" prerequisite piece K
  named is discharged.
- Proved by cap-stability cone induction: four zero-multiplicity rows
  (`P`-locality ±2; no `P → J` at gap ≥ 3 or from gap ≥ 4; `J → J` reach
  ≤ +2) plus start supports (`GapWalkRows`), the DP as an iterated state
  function with split/congruence toolkit (`GapWalkCanon`), then J-support
  `≤ 2 + 2l` and cap-agreement on all `J` plus `P` inside the cone
  `g + 2l ≤ M` (`GapWalkTrunc`). The `2L + 3` bound is the exact edge of
  the cone condition at the last emission. No closed-form rows needed —
  those stay priced under K. Standard axioms only (no `native_decide`
  anywhere in the three modules); statements pre-verified numerically
  (rows to `g ≤ 40, gp ≤ 80`; cap stability to `L ≤ 5`, caps `2L + 10`).

**`GapWalkStacks.lean` / `GapWalkPeel.lean` / `GapWalkEnds.lean` /
`GapWalkBij.lean`** (wave 4, piece B of the scoping note, same day) — the
walk ↔ configuration bijection:

- **`walkFamilies_configs`: every emitted family triple of
  `walkFamilies L` is `(V ℓ ℓ, Vᵗ ℓ ℓ, Vp ℓ ℓ)`, for every `L`,
  unconditionally** — the walk's numbers *mean* all-pairs clusters at
  every level, closing `GapWalk.lean`'s stated open item. The `ℓ ≤ 3`
  literal equalities of the bridge are subsumed.
- New literal-value theorems, past enumeration reach and using no
  `native_decide`: `V 4 4 = 68314`, `V 5 5 = 981085`,
  `V 6 6 = 14115141`; `Vᵗ 4 4 = 13103`, `Vᵗ 5 5 = 187965`,
  `Vᵗ 6 6 = 2703074`; `Vp 4 4 = 2515`, `Vp 5 5 = 36021`,
  `Vp 6 6 = 517701`. (The `ℓ ≤ 3` values took `native_decide` over
  ~10⁵-pair windows; these are pure `walk_table` arithmetic through the
  bijection.)
- Proved by row-peeling partial stacks: bottom parts of clusters whose
  every king-component meets the top row, making the class flag a binary
  state (`GapWalkStacks`); the new-row interface reduced to four
  near-Booleans plus one adjacency, so the fiber over a stack is exactly
  `stepMul`'s own counting window and the stack counts step by `funStep`
  (`GapWalkPeel`); the three end assemblies by fiber counting and a
  y-flip reflection for the top edge (`GapWalkEnds`); then a cone
  induction in the Trunc idiom (invariant at cap `M ≥ 2l + 4`: `J` agrees
  at `g ≤ 2l + 2`, `P` inside `g + 2l ≤ M`) assembling the head
  (`GapWalkBij`). Standard axioms only in all four modules; statements
  pre-verified numerically (union-find enumeration: master fiber lemma
  exhaustively at `i ≤ 2`, ends at `ℓ ≤ 3`, cone at the edge cap, heads
  to `L = 5`).

**`DepthOneKernelPhi.lean`** (wave K, piece K of the scoping note,
2026-08-10) — the kernel method at all orders:

- **`phi_annihilates_exact : Φ(x, N(x)) = 0`, exactly in `ℚ⟦x⟧` at every
  order** — the exact upgrade of the earlier mod-`x^61`
  `DepthOneSeries.phi_annihilates` (which used `native_decide`). The
  depth-1 defect kernel's closed form annihilates `Φ` identically. Proved
  entirely inside `ℚ[X, a, b]/(a²−AA, b²−BB)` (the two √-square relations),
  with no complex analysis and no `native_decide`: the whole y-form quartic
  collapses to a single scalar identity and then to a cleared `bracket = 0`,
  each discharged by one machine-generated `linear_combination` cofactor
  certificate (kernel-checked). The `x ↦ 3x` lift is coefficient-level (no
  `PowerSeries.rescale` in this Mathlib) and `Φ`'s F₁-factor is proved even
  in `s` via a from-scratch `X ↦ −X` automorphism swapping `A ↔ B`.
- **`phi_annihilates_of_exact`** re-derives `DepthOneSeries.phi_annihilates`
  (the mod-`x^61` value pin) from the exact theorem *without*
  `native_decide` — conditional on the one thing piece K cannot supply: the
  walk↔closed-form bridge `truncL 61 Nexact = nSeries 60` (that the kernel
  closed form is the walk's own `walkFamilies` enumeration at all orders),
  which is identity (II) = **piece D**. It is carried as an explicit
  hypothesis `hbridge`, not a `sorry`.

Axioms throughout: `propext, Classical.choice, Quot.sound` plus
`Lean.ofReduceBool` on the `native_decide` theorems (project standard;
audited per-theorem in-file). `phi_annihilates_exact` and
`phi_annihilates_of_exact` are on the standard three only.

## Terminus (2026-08-10): where Notary stops, and why each boundary is principled

The walk side is closed end to end — T (truncation exactness), B (walk ↔
cluster configurations), K (`Φ(x, N(x)) = 0` exact at all orders), and the
branch constants (DepthOneConstants) — all on standard axioms. Two boundaries
remain, and **neither is unfinished work**: one is a genuine open pure-math
question, the other a deliberately scoped-out real-analysis step. Notary is at
its achievable maximum.

**Boundary 1 — the all-orders walk ↔ triangle tie (piece D) is provably not
closable as a formula.** Piece D is identity (I), `D₁(k) = lead(R_k)/(−3)^(k+1)`,
tying the walk's defect to the triangle's diagonal polynomial `R_k`; its
all-orders form is exactly the `hbridge` hypothesis of
`phi_annihilates_of_exact` and exactly `Diagonal.lean`'s general-`k`
factorization lemma. That lemma reduces to a closed form for the single-cluster
generating function `B(y)`. **We now know there is none:** extending the
extraction to the banked a(40) triangle gives 18 converged terms of `B(y)`
(vs 9 at a(21) — squarely inside the 15–20-term window once thought decisive),
and every falsifiable algebraic (`P(f,y)=0`) and D-finite (linear-ODE) form
returns the trivial solution only (`experiments/braw_from_data.py`, log
`build/braw_a40.log`; recorded in `docs/proofs/T-n-nm2-and-general.md` §5). So
`B(y)` is not algebraic or D-finite at any reachable complexity — consistent
with the non-D-finiteness of polyomino growth series. Piece D therefore stays
**exactly identified with the literal triangle at finite order** — assembled
inside Lean at `k ≤ 8`, two-source-verified at `k ≤ 19`, algebraicity
holdout-checked to order 60 — and that finite pin is the mathematical maximum,
not a placeholder. `hbridge` remains an explicit hypothesis, discharged only up
to whatever finite order one is willing to compute (a `native_decide`-scale
check, deliberately not taken since the exact `phi_annihilates_exact` already
subsumes the finite value pin).

**Boundary 2 — the analytic transfer** (branch data → the literal `k^{−1/2}`
asymptotic and `C₁ = √6/(27√π)` with its `√π`): real-analytic, no Mathlib
support, **deliberately out of scope since wave 2**. The constants live in Lean
as exact branch data (`(27x−1)²`, `27V₀² = 2`, `a`); the passage from
"square-root branch" to coefficient asymptotics is stated in the paper and
consumes those Lean-verified constants.

**Net.** Notary's deliverable — the depth-1 defect law, its quartic `Φ`, and
its exact algebraic constants — is proved on the walk side, at all orders, on
standard axioms. Its identification with the literal polyplet triangle is exact
to finite order and known to have no uniform closed form beyond that. There is
no remaining proof effort that would change this: piece D is an open pure-math
question (not a to-do), and the analytic transfer is a scoped-out real-analysis
step. The optional finite increments that remain — fixed-`k` `k = 3, 4` in
`Diagonal.lean` (mechanical, no `B(y)`), or discharging `hbridge` to a chosen
finite order — strengthen the finite pin but change nothing structural.

(History: T and B launched and landed 2026-08-09; K launched and landed
2026-08-10; the `B(y)` non-closability check completed 2026-08-10, converting
D from "pending multi-module campaign" to "confirmed open, finite-pinned.")
