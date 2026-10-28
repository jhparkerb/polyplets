/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Basic

/-!
# Series: sequence convolution, as power-series coefficients

The algebra layer under the staircase (`docs/proofs/product-form.md`)
works with plain sequences `ℕ → ℚ`, so that `Mu.lean` can define the root
series `ν` by a well-founded recursion on the index and pattern-match on the
underlying functions.

* `conv a b` — the Cauchy convolution `m ↦ ∑_{i ≤ m} a i · b (m − i)`;
* `eps` — the convolution unit (`1` at `0`, else `0`);
* `convPow a ℓ` — the `ℓ`-fold convolution power of `a` (`convPow a 0 = eps`).

Every algebraic fact about them is read off Mathlib's `PowerSeries ℚ` through
the bridge `mk_conv : mk (conv a b) = mk a * mk b` (and `mk_eps`, `mk_convPow`):
commutativity, associativity (`sum_conv_collapse`, the reindexing the staircase
uses), the unit laws, and that an inverse lifts to powers (`conv_convPow_inv`).
Only the truncation lemmas (`conv_congr_le`, `convPow_congr_le`,
`conv_left_vanish_lt`), which say that coefficient `m` of a convolution reads
its arguments at indices `≤ m` only, are proved on the sum directly; the
well-founded `ν` recursion of `Mu.lean` leans on them.
-/

namespace Polyplets

open PowerSeries

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

/-! ## The bridge to `PowerSeries ℚ` -/

/-- `conv` is the coefficient of a product of power series. -/
lemma conv_eq_coeff (a b : ℕ → ℚ) (m : ℕ) : conv a b m = coeff m (mk a * mk b) := by
  rw [coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk
    (fun p => coeff p.1 (mk a) * coeff p.2 (mk b)) m]
  simp only [conv, coeff_mk]

/-- `mk` turns convolution into multiplication. -/
lemma mk_conv (a b : ℕ → ℚ) : mk (conv a b) = mk a * mk b :=
  PowerSeries.ext fun m => by rw [coeff_mk, conv_eq_coeff]

/-- `mk` turns the unit into `1`. -/
lemma mk_eps : mk eps = (1 : ℚ⟦X⟧) :=
  PowerSeries.ext fun m => by rw [coeff_mk, coeff_one, eps]

/-- `mk` turns convolution powers into powers. -/
lemma mk_convPow (a : ℕ → ℚ) (ℓ : ℕ) : mk (convPow a ℓ) = mk a ^ ℓ := by
  induction ℓ with
  | zero => simp only [convPow, mk_eps, pow_zero]
  | succ ℓ ih => simp only [convPow, mk_conv, ih, pow_succ']

/-- Two sequences with the same power series are equal. -/
lemma eq_of_mk_eq {a b : ℕ → ℚ} (h : mk a = mk b) : a = b :=
  funext fun m => by rw [← coeff_mk m a, h, coeff_mk]

/-! ## The ring laws, read off the power series -/

/-- Convolution is commutative. -/
lemma conv_comm (a b : ℕ → ℚ) : conv a b = conv b a :=
  eq_of_mk_eq (by rw [mk_conv, mk_conv, mul_comm])

/-- Convolution is associative. -/
lemma conv_assoc (a b c : ℕ → ℚ) : conv (conv a b) c = conv a (conv b c) :=
  eq_of_mk_eq (by rw [mk_conv, mk_conv, mk_conv, mk_conv, mul_assoc])

/-- **`sum_conv_collapse`** — the reindexing of the staircase: folding a nested
convolution sum along the diagonal `s = i + t` turns the inner
`∑_t b t · f (k − i − t)` into a genuine `conv a b` coefficient. It is
associativity, coefficient by coefficient: the left side is
`conv a (conv b f) k`, the right side `conv (conv a b) f k`. -/
lemma sum_conv_collapse (a b f : ℕ → ℚ) (k : ℕ) :
    ∑ i ∈ Finset.range (k + 1), a i *
        ∑ t ∈ Finset.range (k - i + 1), b t * f (k - i - t)
      = ∑ s ∈ Finset.range (k + 1), conv a b s * f (k - s) :=
  (congrFun (conv_assoc a b f) k).symm

/-- `eps` is a right unit for `conv`. -/
lemma conv_eps (a : ℕ → ℚ) : conv a eps = a :=
  eq_of_mk_eq (by rw [mk_conv, mk_eps, mul_one])

/-- `eps` is a left unit for `conv`. -/
lemma eps_conv (a : ℕ → ℚ) : conv eps a = a := by
  rw [conv_comm, conv_eps]

/-- A convolution inverse lifts to powers: if `conv a b = eps` then
`conv (convPow a ℓ) (convPow b ℓ) = eps`. -/
lemma conv_convPow_inv {a b : ℕ → ℚ} (h : conv a b = eps) (ℓ : ℕ) :
    conv (convPow a ℓ) (convPow b ℓ) = eps := by
  have hab : mk a * mk b = 1 := by rw [← mk_conv, h, mk_eps]
  exact eq_of_mk_eq (by rw [mk_conv, mk_convPow, mk_convPow, ← mul_pow, hab, one_pow, mk_eps])

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

end Polyplets
