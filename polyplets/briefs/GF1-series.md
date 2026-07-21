# GF-1 — `Polyplets/Grand/Series.lean`: the sequence-convolution toolkit

Read first: `polyplets/GRANDFORM-PLAN.md` (conventions, gates), then skim
`polyplets/Polyplets/Shape.lean` for house style. No mathematical risk here;
this is a small, self-contained algebra file every later task imports.

## Deliverables

Working over `ℕ → ℚ` (plain functions; do NOT introduce a structure/type
synonym — later files pattern-match on plain lambdas):

```lean
def conv (a b : ℕ → ℚ) : ℕ → ℚ :=
  fun m => ∑ i ∈ Finset.range (m + 1), a i * b (m - i)

def eps : ℕ → ℚ := fun m => if m = 0 then 1 else 0

def convPow (a : ℕ → ℚ) : ℕ → ℕ → ℚ
  | 0     => eps
  | ℓ + 1 => conv a (convPow a ℓ)

def shiftSeq (i : ℕ) (a : ℕ → ℚ) : ℕ → ℚ :=
  fun m => if i ≤ m then a (m - i) else 0
```

Lemmas (names indicative; keep them or improve, but export exactly this
functionality):

1. `conv_comm : conv a b = conv b a` (reindex `i ↦ m − i`;
   `Finset.sum_nbij'` or `Finset.sum_bij` on `range (m+1)`).
2. `conv_assoc : conv (conv a b) c = conv a (conv b c)` (both sides equal the
   triple sum over `{(i,j,k) : i+j+k = m}`; easiest via
   `Finset.Nat.sum_antidiagonal` after rewriting `conv` in antidiagonal form —
   consider proving `conv_eq_antidiagonal : conv a b m = ∑ p ∈
   Finset.Nat.antidiagonal m, a p.1 * b p.2` first and working from that).
3. `conv_eps : conv a eps = a` and `eps_conv : conv eps a = a`.
4. `conv_congr_le : (∀ i ≤ M, b i = c i) → ∀ m ≤ M, conv a b m = conv a c m`
   — the truncation workhorse (coefficient m of a convolution reads its
   arguments only at indices ≤ m). Also the symmetric version, and
   `convPow_congr_le` (induction on ℓ).
5. `conv_left_vanish_lt : (∀ j < ℓ, a j = 0) → conv a b m =
   ∑ j ∈ Finset.Icc ℓ m, a j * b (m - j)` (and `= 0` when `m < ℓ`);
   likewise `convPow_vanish_lt : (∀ j < ℓ, a j = 0) → ∀ m < ℓ·1…` — you only
   need: if `a` vanishes below 1 then `convPow a ℓ` vanishes below ℓ.
6. **`sum_conv_collapse`** (the key reusable reindexing; used by GF-3 twice,
   GF-4, GF-6): for `a b : ℕ → ℚ`, `f : ℕ → ℚ`, `k : ℕ`:
   ```lean
   ∑ i ∈ Finset.range (k + 1), a i *
       ∑ t ∈ Finset.range (k - i + 1), b t * f (k - i - t)
     = ∑ s ∈ Finset.range (k + 1), conv a b s * f (k - s)
   ```
   Proof route: turn the LHS double sum into a sum over the sigma set
   `{(i,t) : i ≤ k, t ≤ k−i}`, reindex by `s = i + t` (bijection with
   `{(s,i) : s ≤ k, i ≤ s}`), and fold the inner sum into `conv a b s`.
   Mind ℕ-subtraction: on the index set, `k − i − t = k − s` — discharge
   side conditions with `omega`.
7. `convPow_add : convPow a (ℓ₁ + ℓ₂) = conv (convPow a ℓ₁) (convPow a ℓ₂)`
   (induction, using assoc), and
   `conv_convPow_inv : conv a b = eps → conv (convPow a ℓ) (convPow b ℓ) = eps`
   (induction on ℓ with comm/assoc juggling).

## Notes

- All sums are `Finset.range`/`Finset.Icc` over ℕ with values in ℚ; no
  casts appear in this file at all.
- Function-extensionality direction: state lemmas 1–3, 7 as equalities of
  functions (`funext m` inside), since later files rewrite pointwise anyway;
  or pointwise — your choice, be consistent.
- Keep it under ~300 lines. If a lemma resists, check
  `Mathlib.Data.Finset.NatAntidiagonal` and
  `Finset.sum_sigma`/`Finset.sum_biUnion` for the right primitive.

## Done criteria

`lake build Polyplets.Grand.Series` green, no `sorry`, no new axioms,
linters clean. Commit `lean-gf: Series — convolution toolkit`.
