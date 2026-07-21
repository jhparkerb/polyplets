/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Tactic

/-!
# Series: a sequence-convolution toolkit over `ℕ → ℚ`

The self-contained algebra layer under the grand-form staircase (GRANDFORM-PLAN.md).
Everything works over plain functions `ℕ → ℚ` — no structure or type synonym, so
later files can pattern-match on the underlying lambdas.

* `conv a b` — the Cauchy convolution `m ↦ ∑_{i ≤ m} a i · b (m − i)`.
* `eps` — the convolution unit (`1` at `0`, else `0`).
* `convPow a ℓ` — the `ℓ`-fold convolution power of `a` (`convPow a 0 = eps`).
* `shiftSeq i a` — right-shift by `i` (`0` on the first `i` indices).

The core reusable lemma is **`sum_conv_collapse`**: the reindexing
`∑_i a i · (∑_t b t · f (k−i−t)) = ∑_s (conv a b) s · f (k−s)`, proved by a
bijection of sigma index sets. It is `conv_assoc` in disguise (the inner sum is
`conv b f (k − i)`), and GF-3, GF-4, GF-6 all consume it.

`conv` is a commutative, associative product with unit `eps`; convolution powers
add exponents (`convPow_add`) and a convolution inverse lifts to powers
(`conv_convPow_inv`). Truncation lemmas (`conv_congr_le`, `convPow_congr_le`,
`conv_left_vanish_lt`, `convPow_vanish_lt`) express that coefficient `m` of a
convolution reads its arguments only at indices `≤ m` — the workhorses the
well-founded `ν`/`μ` recursions of GF-2/GF-3 lean on.
-/

namespace Polyplets

/-! ## Definitions -/

/-- The Cauchy convolution of two sequences: coefficient `m` is
`∑_{i ≤ m} a i · b (m − i)`. -/
def conv (a b : ℕ → ℚ) : ℕ → ℚ :=
  fun m => ∑ i ∈ Finset.range (m + 1), a i * b (m - i)

/-- The convolution unit: `1` at index `0`, `0` elsewhere. -/
def eps : ℕ → ℚ := fun m => if m = 0 then 1 else 0

/-- The `ℓ`-fold convolution power of `a`, with `convPow a 0 = eps`. -/
def convPow (a : ℕ → ℚ) : ℕ → ℕ → ℚ
  | 0     => eps
  | ℓ + 1 => conv a (convPow a ℓ)

/-- Right-shift a sequence by `i`: `shiftSeq i a m = a (m − i)` for `i ≤ m`, else
`0`. -/
def shiftSeq (i : ℕ) (a : ℕ → ℚ) : ℕ → ℚ :=
  fun m => if i ≤ m then a (m - i) else 0

/-! ## Antidiagonal form and commutativity -/

/-- `conv` written as a sum over the antidiagonal of `m`. -/
lemma conv_eq_antidiagonal (a b : ℕ → ℚ) (m : ℕ) :
    conv a b m = ∑ p ∈ Finset.antidiagonal m, a p.1 * b p.2 := by
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk (fun p => a p.1 * b p.2) m]
  rfl

/-- Convolution is commutative. -/
lemma conv_comm (a b : ℕ → ℚ) : conv a b = conv b a := by
  funext m
  rw [conv_eq_antidiagonal, conv_eq_antidiagonal,
      ← Finset.Nat.sum_antidiagonal_swap (f := fun p => b p.1 * a p.2)]
  refine Finset.sum_congr rfl fun p _ => ?_
  simp only [Prod.fst_swap, Prod.snd_swap]
  ring

/-! ## The collapse lemma and associativity -/

/-- **`sum_conv_collapse`** — the key reindexing used across GF-3/4/6: folding a
nested convolution sum along the diagonal `s = i + t` turns the inner
`∑_t b t · f (k − i − t)` into a genuine `conv a b` coefficient. Proved by a
bijection of the two sigma index sets `{(i,t) : i + t ≤ k}` and
`{(s,i) : i ≤ s ≤ k}`. -/
lemma sum_conv_collapse (a b f : ℕ → ℚ) (k : ℕ) :
    ∑ i ∈ Finset.range (k + 1), a i *
        ∑ t ∈ Finset.range (k - i + 1), b t * f (k - i - t)
      = ∑ s ∈ Finset.range (k + 1), conv a b s * f (k - s) := by
  have hL : ∑ i ∈ Finset.range (k + 1), a i *
        ∑ t ∈ Finset.range (k - i + 1), b t * f (k - i - t)
      = ∑ i ∈ Finset.range (k + 1), ∑ t ∈ Finset.range (k - i + 1),
          a i * (b t * f (k - i - t)) := by
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [Finset.mul_sum]
  have hR : ∑ s ∈ Finset.range (k + 1), conv a b s * f (k - s)
      = ∑ s ∈ Finset.range (k + 1), ∑ i ∈ Finset.range (s + 1),
          a i * b (s - i) * f (k - s) := by
    refine Finset.sum_congr rfl fun s _ => ?_
    simp only [conv]
    rw [Finset.sum_mul]
  rw [hL, hR, Finset.sum_sigma', Finset.sum_sigma']
  refine Finset.sum_bij'
    (fun x _ => (⟨x.1 + x.2, x.1⟩ : (_ : ℕ) × ℕ))
    (fun x _ => (⟨x.2, x.1 - x.2⟩ : (_ : ℕ) × ℕ)) ?_ ?_ ?_ ?_ ?_
  · rintro ⟨i, t⟩ hx
    simp only [Finset.mem_sigma, Finset.mem_range] at hx ⊢
    omega
  · rintro ⟨s, i⟩ hy
    simp only [Finset.mem_sigma, Finset.mem_range] at hy ⊢
    omega
  · rintro ⟨i, t⟩ _
    have h1 : i + t - i = t := by omega
    simp only [h1]
  · rintro ⟨s, i⟩ hy
    simp only [Finset.mem_sigma, Finset.mem_range] at hy
    have h1 : i + (s - i) = s := by omega
    simp only [h1]
  · rintro ⟨i, t⟩ _
    dsimp only
    have h1 : i + t - i = t := by omega
    have h2 : k - (i + t) = k - i - t := by omega
    rw [h1, h2]
    ring

/-- Convolution is associative — a definitional restatement of
`sum_conv_collapse` (the inner sum on its left is `conv b c (m − i)`). -/
lemma conv_assoc (a b c : ℕ → ℚ) : conv (conv a b) c = conv a (conv b c) := by
  funext m
  change (∑ s ∈ Finset.range (m + 1), conv a b s * c (m - s))
     = ∑ i ∈ Finset.range (m + 1), a i * conv b c (m - i)
  exact (sum_conv_collapse a b c m).symm

/-! ## The unit -/

/-- `eps` is a right unit for `conv`. -/
lemma conv_eps (a : ℕ → ℚ) : conv a eps = a := by
  funext m
  simp only [conv, eps]
  rw [Finset.sum_eq_single m]
  · simp
  · intro i hi hne
    rw [Finset.mem_range] at hi
    have : m - i ≠ 0 := by omega
    simp [this]
  · intro h
    exact absurd (Finset.self_mem_range_succ m) h

/-- `eps` is a left unit for `conv`. -/
lemma eps_conv (a : ℕ → ℚ) : conv eps a = a := by
  rw [conv_comm, conv_eps]

/-! ## Truncation: a convolution coefficient reads only low indices -/

/-- Coefficient `m ≤ M` of `conv a b` depends on `b` only at indices `≤ M`. -/
lemma conv_congr_le {a b c : ℕ → ℚ} {M : ℕ} (h : ∀ i, i ≤ M → b i = c i) :
    ∀ m, m ≤ M → conv a b m = conv a c m := by
  intro m hm
  simp only [conv]
  refine Finset.sum_congr rfl fun i hi => ?_
  rw [Finset.mem_range] at hi
  rw [h (m - i) (by omega)]

/-- Coefficient `m ≤ M` of `conv a b` depends on `a` only at indices `≤ M`. -/
lemma conv_congr_le_left {a b c : ℕ → ℚ} {M : ℕ} (h : ∀ i, i ≤ M → a i = c i) :
    ∀ m, m ≤ M → conv a b m = conv c b m := by
  intro m hm
  rw [conv_comm a b, conv_comm c b]
  exact conv_congr_le h m hm

/-- Truncation lifts to convolution powers: agreement of the bases up to `M`
gives agreement of every power up to `M`. -/
lemma convPow_congr_le {b c : ℕ → ℚ} {M : ℕ} (h : ∀ i, i ≤ M → b i = c i) :
    ∀ (ℓ m : ℕ), m ≤ M → convPow b ℓ m = convPow c ℓ m := by
  intro ℓ
  induction ℓ with
  | zero => intro m _; rfl
  | succ ℓ ih =>
    intro m hm
    change conv b (convPow b ℓ) m = conv c (convPow c ℓ) m
    rw [conv_congr_le_left h m hm]
    exact conv_congr_le ih m hm

/-! ## Vanishing below a threshold -/

/-- If `a` vanishes below `ℓ`, the convolution coefficient drops its low terms:
`conv a b m = ∑_{j ∈ Icc ℓ m} a j · b (m − j)`. -/
lemma conv_left_vanish_lt {a b : ℕ → ℚ} {ℓ : ℕ} (h : ∀ j, j < ℓ → a j = 0)
    (m : ℕ) :
    conv a b m = ∑ j ∈ Finset.Icc ℓ m, a j * b (m - j) := by
  simp only [conv]
  refine (Finset.sum_subset ?_ ?_).symm
  · intro x hx
    rw [Finset.mem_Icc] at hx
    rw [Finset.mem_range]
    omega
  · intro x hx hxni
    rw [Finset.mem_range] at hx
    have hlt : x < ℓ := by
      by_contra hc
      exact hxni (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
    rw [h x hlt, zero_mul]

/-- If `a` vanishes below `ℓ` then so does `conv a b`. -/
lemma conv_eq_zero_of_lt {a b : ℕ → ℚ} {ℓ : ℕ} (h : ∀ j, j < ℓ → a j = 0)
    {m : ℕ} (hm : m < ℓ) : conv a b m = 0 := by
  rw [conv_left_vanish_lt h m, Finset.Icc_eq_empty (by omega), Finset.sum_empty]

/-- If `a` vanishes below `1` (i.e. `a 0 = 0`), the `ℓ`-th convolution power
vanishes below `ℓ`. -/
lemma convPow_vanish_lt {a : ℕ → ℚ} (h : a 0 = 0) :
    ∀ (ℓ m : ℕ), m < ℓ → convPow a ℓ m = 0 := by
  intro ℓ
  induction ℓ with
  | zero => intro m hm; exact absurd hm (Nat.not_lt_zero m)
  | succ ℓ ih =>
    intro m hm
    simp only [convPow, conv]
    refine Finset.sum_eq_zero fun i hi => ?_
    rw [Finset.mem_range] at hi
    rcases Nat.eq_zero_or_pos i with hi0 | hipos
    · rw [hi0, h, zero_mul]
    · have : m - i < ℓ := by omega
      rw [ih (m - i) this, mul_zero]

/-! ## Convolution powers -/

/-- Exponents add: `convPow a (ℓ₁ + ℓ₂) = conv (convPow a ℓ₁) (convPow a ℓ₂)`. -/
lemma convPow_add (a : ℕ → ℚ) (ℓ₁ ℓ₂ : ℕ) :
    convPow a (ℓ₁ + ℓ₂) = conv (convPow a ℓ₁) (convPow a ℓ₂) := by
  induction ℓ₂ with
  | zero => simp only [Nat.add_zero, convPow, conv_eps]
  | succ ℓ ih =>
    have he : ℓ₁ + (ℓ + 1) = (ℓ₁ + ℓ) + 1 := by omega
    rw [he]
    simp only [convPow]
    rw [ih, ← conv_assoc, conv_comm a (convPow a ℓ₁), conv_assoc]

/-- A convolution inverse lifts to powers: if `conv a b = eps` then
`conv (convPow a ℓ) (convPow b ℓ) = eps`. -/
lemma conv_convPow_inv {a b : ℕ → ℚ} (h : conv a b = eps) :
    ∀ ℓ : ℕ, conv (convPow a ℓ) (convPow b ℓ) = eps := by
  intro ℓ
  induction ℓ with
  | zero => simp only [convPow]; exact conv_eps eps
  | succ ℓ ih =>
    simp only [convPow]
    rw [conv_assoc, ← conv_assoc (convPow a ℓ) b, conv_comm (convPow a ℓ) b,
        conv_assoc b, ih, conv_eps, h]

/-! ## Axiom sanity check -/

section Sanity

/-- Axiom audit for the collapse lemma: standard axioms only, no `native_decide`. -/
example : True := trivial

#print axioms sum_conv_collapse
#print axioms conv_assoc
#print axioms conv_convPow_inv

end Sanity

end Polyplets
