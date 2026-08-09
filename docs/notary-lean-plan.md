# Notary: a Lean proof of the depth-1 closure

2026-08-09. Plan only — no Lean written yet. Target result:
`results/onset-defect-depth1-closed.md` — the depth-1 defect has algebraic
generating function pinned by the quartic Φ, with every campaign constant
derived from the curve.

## 0. What is and is not in Lean today

In Lean (no sorries, standard axioms + native_decide, all committed):

- `Polyplets/GapWalk.lean` — the two-class gap-walk DP as a Lean function,
  and the eighteen banked family values `W/W^b/W^p(2^ℓ)`, ℓ ≤ 6, one `rfl`
  theorem each.
- `Polyplets/DepthAssembly.lean` — the depth-j identities (C)/(D) at
  j ≤ 4, k ≤ 8, **with the weight families as hypotheses**, values as
  rational literals.
- `Polyplets/Weights*.lean` — the ab-initio cluster weights (surplus ≤ 3)
  pinned by finite enumeration (`native_decide`), independent of the walk.
- `Polyplets/Diagonal.lean` — diagonal-law instances k = 1, 2 only. Its own
  header names the general-k factorization lemma as the missing theorem.

**Not** in Lean, i.e. the answer to "do we have a Lean proof of the depth-1
closure" is **no**:

1. Identity (II): `D_1(k) = [y^k](P̂ − B²/(3+S))` — the tightness/degree
   count on diagonal-law Step 4. Verified numerically at k ≤ 19 only.
2. The kernel-method derivation (Severance W2): the walk series lies in
   `ℚ(s)[A,B]`, `A² = (1−3s)(1+s)`, `B² = (1+3s)(1−s)`, and its norm is Φ.
   Executed in sympy; no formal counterpart.
3. The branch constants: rate 9, exponent −1/2, `C₁ = √6/(27√π)`,
   `a = 3293/92928 − 3251√3/185856`.
4. The walk theorems themselves are value pins: nothing connects
   `GapWalk.walkFamilies` to the *combinatorial definition* of the weights
   in `Weights.lean` beyond eyeballing the same integers.

## 1. What is provable, tiered honestly

- **Algebra (fully mechanizable).** Items 2 and the algebraic core of 3.
  Everything happens in explicit finite extensions of ℚ; proofs are `ring` /
  `norm_num` / `decide` over stated polynomial identities. The asymptotic
  *transfer* (coefficient asymptotics with the `√π`) is real analysis with no
  Mathlib support — out of scope. The constants are instead stated as branch
  data of Φ, which is their derivation anyway:
  the leading coefficient of Φ vanishes to order exactly 2 at x = 1/27 and
  nowhere else; under `W = V/v`, `v² = 1−27x`, the order-0 part factors as
  `(27V² − 2)²`; the first Taylor step is the quadratic with roots
  `−439/1584 ∓ 23√3/792`; and `a = −1/8 − V₂/(2V₀)` evaluates in ℚ(√3) to
  the exact value above.
- **Bridges (finite, native_decide).** Item 4, and discharging
  DepthAssembly's hypotheses against the pinned weight tables so the k ≤ 8
  identities become unconditional.
- **Identity (II) (research-grade).** Item 1 needs diagonal-law Steps 4–5
  formalized, which needs the general-k factorization lemma that
  `Diagonal.lean` already lists as its missing theorem. This is the only
  open-ended part and it is priced as such (§3, N4).

If N4 stalls, the end state is still a precise disclosure: *the gap-walk
series is algebraic with minimal polynomial Φ and branch data as stated
(proved), and it equals the true defect at every banked cell k ≤ 19
(proved, finite); the identity that equates them for all k is proved on
paper (diagonal-law Step 4 tightness) and checked in Lean only finitely.*

## 2. Agent policy

Lean is the best delegation target in the repo: `lake build` is fail-closed,
so the Sonnet-agents-behind-fail-closed-checks rule is satisfied a fortiori.
Division of labour:

- **Fable (in-session):** module skeletons — definitions, theorem
  *statements*, `sorry` placeholders — plus the gate, RED-first, before any
  agent runs. Agents execute, never draft.
- **Sonnet agents:** fill proofs, one module per agent, no two agents in one
  file. An agent's brief is: this module, these sorries, `lake build` must
  pass, no new axioms, no edits outside the file.
- **Gate `gate-notary` (Makefile):** `lake build` + axiom audit
  (`#print axioms` on the head theorems routed through the existing audit
  pattern in `AuditOutworks.lean`; standard axioms + `Lean.ofReduceBool`
  only) + sorry-grep across the new modules + dead-code check greps the new
  module names. Gate lands RED (skeleton has sorries) in the first commit.
- Waves respect the 3h usage window: N0/N3 first (independent, cheap),
  N1→N2 second, N4 only after scoping.

## 3. Workstreams

### N0 — the bridge (Sonnet, native_decide)

New `Polyplets/GapWalkBridge.lean`:

- `walkFamilies` values = the `Weights.lean` enumerated definitions, per ℓ,
  for every level both sides can reach (interior ℓ ≤ 6 exists on the walk
  side; enumeration sizes priced by the §2 formula of
  `docs/severance-w4-scoping.md` at 370 s per 10⁶ pairs — the ℓ = 6
  boundary/pure enumerations must be sized *before* launch, and any level
  over the proven 2.0·10⁶-pair per-chunk budget gets chunked exactly as
  `WeightsChunk*.lean` does).
- Discharge DepthAssembly's hypotheses with the pinned tables: corollary
  theorems `depth{1..4}_k{0..8}_unconditional`.
- Emit the banked exact defects `D_1(k)`, k ≤ 19, as Lean literals (generator
  script in the `build/w4_depth_lean_gen.py` mould, committed) and prove the
  walk assembly (II)-RHS matches them — the finite two-source anchor.

### N1 — the kernel equations (Sonnet, after Fable skeleton)

New `Polyplets/GapWalkKernel.lean`: `S`, `B`, `P̂` as `PowerSeries ℚ` defined
from the DP recurrence, and the functional (kernel) equations they satisfy,
by coefficient induction. This is where the walk stops being a table and
becomes an equation. Statements come from `experiments/severance_w2_kernel.py`
verbatim; Fable transcribes them into the skeleton, Sonnet proves.

### N2 — algebraicity (Sonnet, depends on N1)

New `Polyplets/DepthOneAlgebraic.lean`: the ring `ℚ(s)[A,B]` as an explicit
quotient, the closed form `F₁ = c₀ + c₁A + c₂B + c₃AB`, a uniqueness lemma
(the kernel system plus finitely many initial coefficients determines the
series — this replaces the paper's analyticity argument and is the one lemma
Fable should draft in full), and the head theorem: **Φ(x, N(x)) = 0** for the
walk series N, by `ring` in the quotient.

### N3 — branch data (Sonnet, independent of N1/N2)

New `Polyplets/DepthOneConstants.lean`: the four algebraic facts of §1
about Φ, plus `a`'s minimal polynomial over ℚ and its ℚ(√3) value. Pure
polynomial arithmetic; no walk, no series.

### N4 — identity (II) and (I) (Fable scopes first; Sonnet leaf lemmas only)

Prerequisites: general-k factorization lemma in `Diagonal.lean`
(its listed TODO), then Step-5 split (`R_k`, correction polynomial `D(z)`),
then the tightness count (top z-degree ⟺ all rows size 2 ⟺ all-pairs
families). Fable produces a lemma-level decomposition and a cost verdict
*before* any agent launch; this workstream may be declined on price, and
§1's fallback disclosure is the planned landing zone for that case.

## 4. Order of battle

1. Fable: skeletons + RED `gate-notary` + agent briefs. Commit.
2. Wave 1: N0, N3 (parallel, two agents).
3. Wave 2: N1, then N2.
4. N4 scoping (Fable, measurement-only doc in the w4-scoping mould), then
   go/no-go.

Every wave ends: `make gate-notary`, then full `make` once per code-touching
session. No ETAs are quoted anywhere in this plan because none have a
measured basis; N0's enumeration sizes are computed before launch from the
scoping formula, which is the only measured rate we have.

## Execution status (2026-08-09, same day)

- **Wave 1 COMPLETE, gate green.** N0 (`GapWalkBridge.lean`) and N3
  (`DepthOneConstants.lean`) both landed by Sonnet agents with zero
  statement changes against the pre-verified skeletons.
- **Wave 2 re-scoped and COMPLETE.** The original N1/N2 (kernel equations →
  algebraicity, all orders) turned out research-grade on design — the
  summability bookkeeping in `ℚ⟦s⟧` is a small library, not a wave —
  so wave 2 delivered the strongest finite statement instead:
  `DepthOneSeries.lean`, `Φ(x, N(x)) ≡ 0 mod x^61` plus the `k ≤ 19` pin.
  The full-kernel architecture and pricing moved to
  `docs/notary-kernel-scoping.md` (piece K), alongside truncation (T),
  bijection (B), and identities (D).
- **N4 scoping folded into the same note.** Verdict: T → B → K → D by
  value per risk; none launches without explicit agreement.
- Outcome summary: `results/notary-depth1-lean.md`.
