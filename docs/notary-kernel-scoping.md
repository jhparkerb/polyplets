# Notary: scoping the research-grade remainder

2026-08-09. Companion to `docs/notary-lean-plan.md`. Wave 1 (N0, N3) and the
wave-2 finite extension (`DepthOneSeries.lean`) close every finite and
algebraic piece of the depth-1 closure in Lean. What remains between the
current state and a full Lean proof of
`results/onset-defect-depth1-closed.md` splits into four independent pieces.
This note prices them. Measurement basis is stated per claim; where there is
none, none is quoted.

## The four pieces

**T — truncation exactness.** **DONE 2026-08-09** (same-day wave 3):
`GapWalkTrunc.walkFamiliesCap_exact` — every cap `M ≥ 2L+3` emits the same
family triples, standard axioms only, gate green. The architecture that
landed is *cheaper* than the one priced below: cap stability needs only
zero-multiplicity facts (`GapWalkRows.lean`: P-locality ±2, no P→J at gap
≥ 3 or from gap ≥ 4, J→J reach ≤ +2, start supports) plus a cone induction
over an iterated-function form of the DP (`GapWalkCanon.lean`,
`GapWalkTrunc.lean`); the closed-form transition rows priced as T's cost
center below were never needed — they remain with K, which actually
consumes them. Original pricing kept for the record:
`GapWalk.walkFamilies L` (gap cap
`gmax = 2L+3`) equals the untruncated walk, for every `L`. Architecture: an
exact-walk representation `(jHead : List ℕ, pHead : List ℕ, pTail : ℕ)` — the
J-class row has finite support (spreads by ≤ 2 per step from support ≤ 2 at
either start), the P-class row is eventually constant in the gap (uniform
`12·Jm` tails from J-rows, constant boundary tails, bulk over a constant
tail is constant `9×`). Both facts are step-invariants; the exact walk is
then computable, and the theorem says truncation at `2L+3` cannot matter
because escaped P-mass needs more than the remaining rows to return to
`g ≤ 2` (bulk moves ±2) while `qEnd` reads P only at `g ≤ 2` and J-support
never reaches the cap. Cost center: proving the closed-form transition rows
(the `BOUNDARY` table and `generic_row` of
`experiments/severance_w2_kernel.py` stage 0) equal `stepMul` for symbolic
`g ≥ 3` — interval-counting case analysis, roughly one lemma per row class
(4 boundary rows, 2 generic classes, plus the two start vectors and two end
functionals). Everything else is induction bookkeeping. No new mathematics;
moderate, self-contained, the natural next Sonnet wave if any.

**B — the bijection.** **DONE 2026-08-09** (wave 4, four modules):
`GapWalkBij.walkFamilies_configs` — every emitted family triple is
`(V ℓ ℓ, Vᵗ ℓ ℓ, Vp ℓ ℓ)`, unconditionally; standard axioms only, gate
green. The architecture: partial stacks (bottom parts of all-pairs
clusters, invariant: every king-component meets the top row) with the
class flag as a *binary* state (`GapWalkStacks.lean`), the row peel
reduced to four near-Booleans + one adjacency so the fiber over a stack
is exactly `stepMul`'s own filter window (`GapWalkPeel.lean`,
`STK*_card_step`), end assemblies by fiber count and a y-flip reflection
(`GapWalkEnds.lean`), and a Trunc-style cone induction assembling the
head (`GapWalkBij.lean`). With `walk_table` the identity turns
enumeration into computation: `V`/`Vᵗ`/`Vp` at `ℓ = 4, 5, 6` are now
literal-value theorems (68314/981085/14115141, 13103/187965/2703074,
2515/36021/517701) — past `native_decide` enumeration reach, using none.
Every statement was numerically pre-verified before any proof agent ran
(`verify_bij_statements.py`, union-find); all four modules landed with
zero statement changes. Original pricing kept for the
record: walk paths ↔ `CFGV`/`CFGVt`/`CFGVp` configurations
for all `ℓ` (previously: numeric agreement at `ℓ ≤ 3`, `GapWalkBridge`).
This is transfer-matrix correctness: peel an all-pairs cluster row by row,
show the state `(gap, joined?)` is exactly what the next row's placement
count depends on, with `stepMul` counting normalized placements. Depends on
nothing else here; independently valuable (it is `GapWalk.lean`'s own stated
open item). Larger than T: the row-peeling needs a canonical decomposition
of configurations (the `mem_CFGV` machinery helps) and a
multiplicity-preserving bijection, not just an invariant.

**K — the kernel method, all orders.** `Φ(x, N(x)) = 0` exactly (currently:
mod `x^61`, `DepthOneSeries.phi_annihilates`). The right architecture — and
the reason this is feasible at all without analysis — is that the entire
derivation of `severance_w2_kernel.py` lives in `ℚ⟦s⟦` (`y = s²`):

- `A = √((1−3s)(1+s))`, `B = √((1+3s)(1−s))` are honest power series
  (constant term 1; define by coefficient recursion, prove the square).
- The small kernel roots `u₁ = ((1−s)−A)/2s`, `u₂ = (−(1+s)+B)/2s` are in
  `s·ℚ⟦s⟧` (the numerators vanish to order 2).
- "Analyticity at the small roots" becomes: the substituted series
  `Σ_m y^m Σ_g j_m(g)·uᵢ^g` is a well-defined element of `ℚ⟦s⟧` (each
  coefficient a finite sum), and the step recurrence telescopes against
  `y·K(uᵢ) = 1` to force `Q(uᵢ) = 0`. No complex analysis anywhere.
- Mathlib support, measured on this project's pinned toolchain
  (v4.31.0): `PowerSeries.subst` exists with `HasSubst` discharged by
  `constantCoeff = 0` (`RingTheory/PowerSeries/Substitution.lean`), inverses
  of units (`Inverse.lean`, 37 theorems), truncation (`Trunc.lean`). The
  square roots are hand-rolled recursions (Binomial.lean exports nothing
  usable here).

Cost centers, in order: (1) the summability bookkeeping — exchanging
`Σ_m` with `Σ_g` under s-adic convergence is coefficient-wise finite but
needs a small library of "finite per order" lemmas that Mathlib does not
provide off the shelf; (2) T is a prerequisite in spirit (the six unknown
series must be *the* walk's, not the truncated walk's); (3) verifying the
6×6 solution and the Galois-norm elimination is `ring` in `ℚ⟦s⟧` fractions
— mechanical, and measured small: the full sympy derivation reruns in 66 s
(two 32 s boundary solves), and the factored `c_i` entries of `F₁` are under
~180 characters each (`build/notary_w2_kernel_measure.log`), so the solution
transcription is not the bottleneck; the summability library is. With K done, `Φ`-annihilation plus `DepthOneConstants`'s
branch data upgrades every campaign constant from "branch data of a pinned
curve" to "derived from the walk, end to end" — but the walk itself still
hangs on B for its combinatorial meaning, and on D for the connection to
the triangle.

**D — identities (I)/(II).** `D_1(k) = lead(R_k)/(−3)^(k+1)` and
`D_1(k) = [y^k](P̂ − B²/(3+S))` for all `k`. Blocked behind the general-`k`
factorization lemma that `Diagonal.lean` names as its missing theorem
(its header: "general `k` is a *sketch*, and the factorization lemma it
needs is the real theorem"), then diagonal-law Steps 4–5 and the tightness
degree count. This is the largest piece and the only one whose paper proof
is itself a multi-step sketch at general `k`. Nothing below D changes what
is *proved about the triangle*; T/B/K live entirely on the walk side.

## Dependency picture

```
T ──┐
    ├──> K   (Φ all orders, from the walk)
B ──┘        (B also standalone: walk numbers mean clusters)
D            (independent; ties everything to T(n,H))
Full theorem = K + B + D  (T absorbed into K)
```

## Verdict

- Ordered by value per unit risk: **T first** (self-contained, finishes
  GapWalk.lean's open item, prerequisite for K), then **B**, then **K**,
  with **D** last and priced separately once `Diagonal.lean`'s general-`k`
  lemma is attempted at all. *(T landed 2026-08-09; B landed 2026-08-09;
  K is next.)*
- None of the four is a single-session Sonnet task under the wave-1 pattern
  (one file, one agent, gate-checked); each is a multi-module campaign with
  Fable-authored decompositions per module. Per the frontier rules, none
  launches without explicit agreement.
- The disclosure as of wave 2 stands on its own (`docs/notary-lean-plan.md`
  §1 fallback): algebraicity checked in Lean to order 60 with 4-order
  holdout past the fit, branch constants exact, assembly closed inside Lean
  at `k ≤ 8`, walk pinned two-source to `k ≤ 19`.
