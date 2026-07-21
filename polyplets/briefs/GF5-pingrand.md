# GF-5 — `scripts/gen_grand_pin.py` + `Polyplets/Grand/PinGrand.lean`:
# pin the production P_k (k = 1..16) from 2 real cells per level

The payoff task: production formulas certified with hypotheses that are ONLY
real-swept cells (H ≤ 18). Read first: `polyplets/GRANDFORM-PLAN.md`;
`Polyplets/Grand/Staircase.lean`; `Polyplets/Pin.lean` in full (you will
reuse `horner`, `prodPoly`, `prodPoly_eval`, the `Pp<k>` definitions for
k = 4..16, the guard/`norm_num` idiom, and the hypothesis-naming style);
`polyplets/pin-data.md` (anchor values); `scripts/gen_pin.py` (generator
conventions: fail-closed, deterministic output, provenance header);
`experiments/staircase_check.py` (the numeric oracle — your generator must
reproduce its μ table exactly or abort).

## Architecture

Strong induction on the level k, all emitted by the generator:

- Level k state (for k ≥ 1), given anchors `A_k : T (2k+1) (k+1) = <lit>`
  and `B_k : T (2k+2) (k+2) = <lit>` plus all lower levels:
  1. `mu<k>_val : mu k = <lit>` — derived (NOT defined) from `T_staircase`
     at (k, H = k+1) — see "μ extraction" below.
  2. `Pstair<k> : ∀ x : ℚ, Pp<k>.eval (x+1) =
     Σ_{i=0}^{k} μᵢ·3^(2i−1)·Pp<k−i>.eval (x−i)` — with μ and 3-powers as
     rational LITERALS (μ₀·3^(−1) = 1), written out as an explicit k+1-term
     sum. Proved by `rw [<horner defs>, prodPoly_eval, …]; ring`.
     (Pre-validated for all k ≤ 16 by the oracle, section 4.)
  3. `P<k>_grand_of_banked (A_1 B_1 … A_k B_k) : ∀ H, k + 1 ≤ H →
     (3:ℚ)^(3k+1) * (T (H + k) H : ℚ) = Pp<k>.eval ((H:ℚ) + k) * 3 ^ (H + k)`
     — induction on H (`Nat.le_induction`):
     base H = k+1: LHS is `3^(3k+1)·<A_k literal>`; RHS a guard-style
     `norm_num` evaluation (emit `guard`-lemmas exactly like Pin.lean's).
     step H → H+1: `T_staircase k H` × `3^(3k+1)`, rewrite each
     `T (H + (k−i)) H` via level-(k−i) statements at height H
     (i = 0: the inner IH; i ≥ 1: lower-level theorems — validity
     `(k−i)+1 ≤ H` from `k+1 ≤ H`), collect 3-powers, finish with
     `Pstair<k>` at `x = (H:ℚ) + k` and `ring`-arithmetic.
     Exponent bookkeeping (verify symbolically before emitting):
     level-(k−i) statement gives `3^(3(k−i)+1)·T(H+(k−i)) H = Pp<k−i>(H+k−i)·3^(H+k−i)`,
     so `μᵢ·3^(3k+1)·T(H+(k−i)) H = μᵢ·3^(3i)·Pp<k−i>(H+k−i)·3^(H+k−i)
     = (μᵢ·3^(2i−1))·Pp<k−i>((H+k+1)−1−i)·3^(H+k+1)`. Summing over i and
     applying `Pstair<k>` yields `Pp<k>(H+1+k)·3^(H+1+k)` — matching the
     goal at H+1. All exponents stay in ℕ except the single literal
     `3^(2i−1)` at i = 0, which the generator emits as `1/3` merged into
     the literal coefficient — no zpow anywhere.
  4. `P<k>_grand_prod (…) : ∀ n, 2k+1 ≤ n →
     (T n (n−k) : ℚ) = Pp<k>.eval n * (3:ℚ)^((n:ℤ) − 1 − 3k)` — the
     production n-form, derived from 3 by the same conversion
     `shape_production` uses (steal that block).
- Level 0 is `T_diag_pow` (exists); levels 1..3's anchors are DISCHARGED,
  not hypothesized: emit `anchor_1_3 : T 3 2 = 10`-style lemmas proved from
  the existing closed forms (`P1_closed`, `P2_closed`, `P3_pinned` — read
  `Polyplets/Diagonal.lean` and `Pin.lean` for their exact statements) by
  `norm_num` evaluation. Consequently the final `P16_grand_of_banked`
  carries EXACTLY the 26 hypotheses for levels 4..16.

Hand-written prelude (not generated): `Pp0 := horner [1]`,
`Pp1`, `Pp2`, `Pp3` via `horner` with the production coefficient lists
(from `pin-data.md` §k=1..3; guard each with a norm_num evaluation at one
onset point against the closed-form theorems), plus any small conversion
lemmas shared by all levels.

## μ extraction (item 1) in detail

From `T_staircase k (k+1)`:
`(T (2k+2) (k+2) : ℚ) = Σ_{i≤k} mu i · T ((k+1) + (k−i)) (k+1)`.
Each RHS cell with i ≥ 1 is diagonal k−i at n = 2k+1−i, in-onset; rewrite
via level-(k−i) `_prod` theorems + guard evaluations into literals. The
i = 0 cell is anchor `A_k`... careful: i = 0 gives `T (2k+1) (k+1)` = A_k,
and the μ_k-term is i = k: `mu k · T (k+1) (k+1) = mu k · 3^k`
(`T_diag_pow`). Isolate: emit
`have h : mu k * 3^k = <lit> := by linarith [hstair, …]` (or
`linear_combination`), then `mu<k>_val` by `field_simp`/`norm_num`.
The generator computes every literal and MUST cross-check the resulting μ_k
against the staircase-solved value (oracle parity) before emitting.

## The generator (`scripts/gen_grand_pin.py`)

- Inputs: `results/triangle.txt` (cells; enforce H ≤ 18 for every
  hypothesized anchor — abort otherwise), `polyplets/pin-data.md` (production
  coefficients k ≤ 16; or parse `orchestrator/sweep.go` like
  `experiments/staircase_check.py` does — pick ONE source and assert
  equality with the other), existing `Pp<k>` names from `Pin.lean`.
- Recomputes μ level-by-level (Fraction), asserts: staircase holds at all
  real instances (the 170-instance check), P-staircase identity at k+2
  points per k, anchors match production values. ANY failure aborts with a
  message; no partial emission.
- Emits `Polyplets/Grand/PinGrand.lean` deterministically (stable ordering,
  provenance header naming generator + inputs + date), following
  `gen_pin.py`'s structure. Guards: every literal that enters a proof gets a
  `norm_num`-checked lemma, so a transcription bug fails to compile.
- Style: python per repo standards (no leading `\n` in prints, fail-closed
  everywhere, no /tmp).

## Feasibility notes & fallbacks

- `Pstair<k>` by `ring` with ~25-digit rational literals: expected to work
  (Lean ring normalizes exact rationals); k = 16 may take noticeable time.
  If `ring` times out: fallback A — emit the identity coefficient-wise
  (generator pre-expands both sides in the monomial basis; k+1 equations,
  each `norm_num`); fallback B — evaluate at k+1 points + `Polynomial`
  degree argument via `Pin.lean`'s `pin` machinery. Try A before B.
- The per-level theorem statements grow (26 hypotheses at k = 16) — Pin.lean
  already does this at 12+; acceptable.
- Build time: expect minutes for the full file; if a single level exceeds
  ~5 min compile, split the generated output into `PinGrandA/B.lean` by
  level range (generator flag) and report.

## Done criteria

Generator runs clean (prints its own ALL CHECKS PASS); generated file
builds green, no `sorry`; `#print axioms P16_grand_of_banked` = standard ∪
(whatever `P3_pinned` carries — the native_decide chunk axioms — list them
in the report); hypothesis audit: grep the emitted theorem signatures —
every `T n H = …` hypothesis has H ≤ 18. Gates G4. This is milestone 2
(orchestrator merges). Commit generator and generated file separately:
`lean-gf: gen_grand_pin — staircase pin generator` /
`lean-gf: PinGrand — P1..P16 from 2 real cells per level`.
