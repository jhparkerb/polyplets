/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.Staircase
import Polyplets.Sanity

/-!
# ExpForm: the grand form, formalized (unconditional)

The abstract exp-form of the diagonal law (`GRANDFORM-PLAN.md`, `grand-form.md`
Step 5): the diagonals of `T` are the *exp of affine cumulants* — each level `k`
adds exactly two new rational constants `(aSeq k, bSeq k)` — for every `k` and
`H ≥ k + 1`, with NO banked hypotheses:

`3^(3k+1)·T(H+k, H) = expCoeff aSeq bSeq k (H+k)·3^(H+k)`.

The construction is entirely a sequence computation over `ℕ → ℚ`:

* `mSeq i = μ_i·3^(2i−1)` — the multiplier in Lagrange-substitution units.
* `Wc` — the diagonal-Lagrange substitution `ŵ = yφ(ŵ)`, resummed to a
  prefix-guarded well-founded recursion (the `nu` pattern of `Mu.lean`);
  `W_fixed` is its fixed-point identity.
* `expSeq`/`logSeq` — series exp/log via the derivative recursion, with
  `expSeq_add` (multiplicativity) and `expSeq_logSeq` (inverse) the toolkit.
* `bSeq j = −(log Wc)_j`, `aSeq` — level-solved from `T` so the onset value
  matches by construction (`base_match`).
* the exp-staircase `expStair` — the abstract analogue of `T_staircase`.

The main theorem `grand_form` rides `base_match` (base) and `expStair` (step)
through the SAME double induction as the μ-recursion. It audits to standard
axioms only — no `native_decide` anywhere in its cone (the seed `T 1 1 = 1` is
the hand-proved `T_one_one` of `Sanity.lean`).
-/

namespace Polyplets

open scoped BigOperators

/-! ## The multiplier in substitution units -/

/-- `m_i = μ_i·3^(2i−1)` in `zpow`-free form (`m 0 = 1`). -/
noncomputable def mSeq : ℕ → ℚ := fun i => mu i * 3 ^ (2 * i) / 3

/-- `m 0 = 1`. -/
lemma mSeq_zero : mSeq 0 = 1 := by
  simp only [mSeq, mu_zero, Nat.mul_zero, pow_zero, mul_one]
  norm_num

/-! ## Series exp via the derivative recursion -/

set_option linter.unusedVariables false in
/-- Series exp of a cumulant sequence: `E_0 = 1` and, for `t ≥ 1`,
`t·E_t = Σ_{j∈Icc 1 t} j·c_j·E_{t−j}`. Prefix-guarded well-founded recursion
(the RHS reads `E` only at indices `t+1−j ≤ t`). The `0`-th coefficient of `c`
is never read. -/
noncomputable def expSeq (c : ℕ → ℚ) : ℕ → ℚ
  | 0     => 1
  | t + 1 => (1 / ((t : ℚ) + 1)) * ∑ j ∈ Finset.Icc 1 (t + 1),
      (j : ℚ) * c j * (if h : t + 1 - j ≤ t then expSeq c (t + 1 - j) else 0)
  decreasing_by exact Nat.lt_succ_of_le h

/-- `E_0 = 1`. -/
lemma expSeq_zero (c : ℕ → ℚ) : expSeq c 0 = 1 := by rw [expSeq]

/-- **De-guarded derivative recursion.** For all `t`,
`t·E_t = Σ_{j∈Icc 1 t} j·c_j·E_{t−j}` (the `t = 0` case reads `0 = 0`). -/
lemma expSeq_unfold (c : ℕ → ℚ) (t : ℕ) :
    (t : ℚ) * expSeq c t = ∑ j ∈ Finset.Icc 1 t, (j : ℚ) * c j * expSeq c (t - j) := by
  cases t with
  | zero => simp
  | succ t =>
    rw [expSeq]
    have hne : ((t : ℚ) + 1) ≠ 0 := by positivity
    have hsum : (∑ j ∈ Finset.Icc 1 (t + 1), (j : ℚ) * c j *
          (if h : t + 1 - j ≤ t then expSeq c (t + 1 - j) else 0))
        = ∑ j ∈ Finset.Icc 1 (t + 1), (j : ℚ) * c j * expSeq c (t + 1 - j) := by
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Finset.mem_Icc] at hj
      rw [dif_pos (by omega)]
    rw [hsum]
    push_cast
    field_simp

/-- **Uniqueness by the derivative recursion.** Any `A` with `A 0 = 1` and the
derivative recursion (for all `t`) equals `expSeq c`. -/
lemma expSeq_eq_of {c A : ℕ → ℚ} (h0 : A 0 = 1)
    (hrec : ∀ t : ℕ, (t : ℚ) * A t = ∑ j ∈ Finset.Icc 1 t, (j : ℚ) * c j * A (t - j)) :
    A = expSeq c := by
  funext t
  induction t using Nat.strong_induction_on with
  | _ t IH =>
    cases t with
    | zero => rw [h0, expSeq_zero]
    | succ t =>
      have hA := hrec (t + 1)
      have hE := expSeq_unfold c (t + 1)
      have hcong : (∑ j ∈ Finset.Icc 1 (t + 1), (j : ℚ) * c j * A (t + 1 - j))
          = ∑ j ∈ Finset.Icc 1 (t + 1), (j : ℚ) * c j * expSeq c (t + 1 - j) := by
        refine Finset.sum_congr rfl fun j hj => ?_
        rw [Finset.mem_Icc] at hj
        rw [IH (t + 1 - j) (by omega)]
      rw [hcong] at hA
      have hne : ((t : ℚ) + 1) ≠ 0 := by positivity
      have : ((t + 1 : ℕ) : ℚ) * A (t + 1) = ((t + 1 : ℕ) : ℚ) * expSeq c (t + 1) := by
        rw [hA, hE]
      have hne' : ((t + 1 : ℕ) : ℚ) ≠ 0 := by push_cast; positivity
      exact mul_left_cancel₀ hne' this

/-! ## Convolution derivative toolkit -/

/-- `range (t+1)` splits as `{0} ∪ Icc 1 t`. -/
lemma range_succ_eq_insert_Icc (t : ℕ) :
    Finset.range (t + 1) = insert 0 (Finset.Icc 1 t) := by
  ext i; simp only [Finset.mem_range, Finset.mem_insert, Finset.mem_Icc]; omega

/-- A convolution whose first argument vanishes at `0` reads only `Icc 1 t`:
`conv (fun j => j·f j) g t = Σ_{j∈Icc 1 t} j·f j·g (t−j)`. -/
lemma conv_deriv_left (f g : ℕ → ℚ) (t : ℕ) :
    conv (fun j => (j : ℚ) * f j) g t
      = ∑ j ∈ Finset.Icc 1 t, (j : ℚ) * f j * g (t - j) := by
  simp only [conv]
  rw [range_succ_eq_insert_Icc, Finset.sum_insert (by simp)]
  simp

/-- **Derivative recursion, conv form.** `t·E_t = conv (j·c_j) E`. -/
lemma expSeq_deriv (c : ℕ → ℚ) :
    (fun t : ℕ => (t : ℚ) * expSeq c t) = conv (fun j => (j : ℚ) * c j) (expSeq c) := by
  funext t
  rw [expSeq_unfold, conv_deriv_left]

/-- **Product rule.** `t·(A ∗ B)_t = (t·A ∗ B)_t + (A ∗ t·B)_t`. -/
lemma conv_deriv (A B : ℕ → ℚ) (t : ℕ) :
    (t : ℚ) * conv A B t
      = conv (fun s => (s : ℚ) * A s) B t + conv A (fun s => (s : ℚ) * B s) t := by
  simp only [conv, Finset.mul_sum, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun i hi => ?_
  rw [Finset.mem_range] at hi
  have hcast : (t : ℚ) = (i : ℚ) + ((t - i : ℕ) : ℚ) := by
    rw [← Nat.cast_add]; congr 1; omega
  rw [hcast]; ring

/-- `conv` distributes over a pointwise sum in its first argument. -/
lemma conv_add_left (A B C : ℕ → ℚ) (t : ℕ) :
    conv (fun s => A s + B s) C t = conv A C t + conv B C t := by
  simp only [conv, add_mul, Finset.sum_add_distrib]

/-! ## Multiplicativity of `expSeq` -/

/-- **`expSeq_add`.** The exp is multiplicative: `exp(c + c') = exp c ∗ exp c'`.
No `c 0 = 0` hypothesis is needed — `expSeq` never reads the `0`-th cumulant. -/
theorem expSeq_add (c c' : ℕ → ℚ) :
    expSeq (fun j => c j + c' j) = conv (expSeq c) (expSeq c') := by
  refine (expSeq_eq_of ?_ ?_).symm
  · simp [conv, expSeq_zero]
  · intro t
    -- t·F = conv D_c F + conv D_{c'} F  (F = E ∗ E'), then fold to Icc sum.
    have hD := conv_deriv (expSeq c) (expSeq c') t
    rw [expSeq_deriv c, expSeq_deriv c'] at hD
    -- reassociate the two convolution triples onto F = conv E E'
    have hL : conv (conv (fun j => (j : ℚ) * c j) (expSeq c)) (expSeq c') t
        = conv (fun j => (j : ℚ) * c j) (conv (expSeq c) (expSeq c')) t := by
      rw [conv_assoc]
    have hR : conv (expSeq c) (conv (fun j => (j : ℚ) * c' j) (expSeq c')) t
        = conv (fun j => (j : ℚ) * c' j) (conv (expSeq c) (expSeq c')) t := by
      rw [conv_comm (fun j => (j : ℚ) * c' j) (expSeq c'), ← conv_assoc,
        conv_comm (conv (expSeq c) (expSeq c')) (fun j => (j : ℚ) * c' j)]
    rw [hL, hR] at hD
    rw [hD, conv_deriv_left c (conv (expSeq c) (expSeq c')) t,
      conv_deriv_left c' (conv (expSeq c) (expSeq c')) t, ← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun j _ => ?_
    ring

/-! ## Series log via the derivative recursion -/

set_option linter.unusedVariables false in
/-- Series log: `L_0 = 0` and, for `t ≥ 1`,
`t·L_t = t·a_t − Σ_{s<t} s·L_s·a_{t−s}`. Prefix-guarded well-founded recursion. -/
noncomputable def logSeq (a : ℕ → ℚ) : ℕ → ℚ
  | 0     => 0
  | t + 1 => a (t + 1) - ∑ s ∈ Finset.Icc 1 t,
      ((s : ℚ) / ((t : ℚ) + 1)) * (if h : s ≤ t then logSeq a s else 0) * a (t + 1 - s)
  decreasing_by exact Nat.lt_succ_of_le h

/-- **The defining identity of `logSeq`** (in the form the exp-inverse consumes):
for `a 0 = 1`, `t·a_t = Σ_{j∈Icc 1 t} j·L_j·a_{t−j}` (the `j = t` term is `t·L_t`
by `a 0 = 1`, matching the derivative recursion). -/
lemma logSeq_key (a : ℕ → ℚ) (h0 : a 0 = 1) (t : ℕ) :
    (t : ℚ) * a t = ∑ j ∈ Finset.Icc 1 t, (j : ℚ) * logSeq a j * a (t - j) := by
  cases t with
  | zero => simp
  | succ t =>
    have hrec : ((t : ℚ) + 1) * logSeq a (t + 1)
        = ((t : ℚ) + 1) * a (t + 1)
          - ∑ s ∈ Finset.Icc 1 t, (s : ℚ) * logSeq a s * a (t + 1 - s) := by
      rw [logSeq]
      have hg : (∑ s ∈ Finset.Icc 1 t, ((s : ℚ) / ((t : ℚ) + 1)) *
              (if h : s ≤ t then logSeq a s else 0) * a (t + 1 - s))
          = ∑ s ∈ Finset.Icc 1 t, ((s : ℚ) / ((t : ℚ) + 1)) * logSeq a s * a (t + 1 - s) := by
        refine Finset.sum_congr rfl fun s hs => ?_
        rw [Finset.mem_Icc] at hs; rw [dif_pos (by omega)]
      rw [hg, mul_sub, Finset.mul_sum]
      congr 1
      refine Finset.sum_congr rfl fun s _ => ?_
      have hne : ((t : ℚ) + 1) ≠ 0 := by positivity
      field_simp
    rw [Finset.sum_Icc_succ_top (by omega : 1 ≤ t + 1)]
    rw [Nat.sub_self, h0, mul_one]
    have hlow : (∑ j ∈ Finset.Icc 1 t, (j : ℚ) * logSeq a j * a (t + 1 - j))
        = ((t : ℚ) + 1) * a (t + 1) - ((t : ℚ) + 1) * logSeq a (t + 1) := by
      rw [hrec]; ring
    push_cast
    rw [hlow]; ring

/-- **`expSeq_logSeq`.** The exp of `logSeq a` (zeroed at `0`) recovers `a`. -/
theorem expSeq_logSeq (a : ℕ → ℚ) (h : a 0 = 1) :
    expSeq (fun j => if j = 0 then 0 else logSeq a j) = a := by
  refine (expSeq_eq_of h fun t => ?_).symm
  rw [logSeq_key a h t]
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [Finset.mem_Icc] at hj
  rw [if_neg (by omega)]

/-! ## Scalar powers of `expSeq` -/

/-- The exp of the zero cumulant is the convolution unit. -/
lemma expSeq_const_zero : expSeq (fun _ : ℕ => (0 : ℚ)) = eps := by
  refine (expSeq_eq_of (by simp [eps]) fun t => ?_).symm
  rw [Finset.sum_eq_zero (by intro j _; ring)]
  rcases Nat.eq_zero_or_pos t with rfl | ht
  · simp [eps]
  · rw [show eps t = 0 by simp only [eps]; rw [if_neg (by omega)]]; ring

/-- **`expSeq_nsmul`.** `exp(p·c) = (exp c)^{∗p}` — the natural-power law. -/
lemma expSeq_nsmul (c : ℕ → ℚ) (p : ℕ) :
    expSeq (fun j => (p : ℚ) * c j) = convPow (expSeq c) p := by
  induction p with
  | zero =>
    simp only [Nat.cast_zero, zero_mul, convPow]
    exact expSeq_const_zero
  | succ p ih =>
    have hfun : (fun j => ((p + 1 : ℕ) : ℚ) * c j)
        = fun j => ((p : ℚ) * c j) + c j := by
      funext j; push_cast; ring
    rw [hfun, expSeq_add (fun i => (p : ℚ) * c i) c, ih, convPow]
    rw [conv_comm]

/-! ## The Lagrange substitution series `Wc` -/

set_option linter.unusedVariables false in
/-- `W`: the unique series with `W₀ = 1` and `1 = Σ_i m_i·(shift i)(W^{∗(i+1)})`
— the diagonal-Lagrange substitution `ŵ = yφ(ŵ)` of `grand-form.md`, resummed.
Prefix-guarded well-founded recursion (the `(t+1−i)`-th coefficient of the
`(i+1)`-power reads `W` only at `≤ t+1−i ≤ t`). -/
noncomputable def Wc : ℕ → ℚ
  | 0     => 1
  | t + 1 => - ∑ i ∈ Finset.Icc 1 (t + 1), mSeq i *
      convPow (fun s => if h : s ≤ t then Wc s else 0) (i + 1) (t + 1 - i)
  decreasing_by exact Nat.lt_succ_of_le h

/-- `W₀ = 1`. -/
lemma Wc_zero : Wc 0 = 1 := by rw [Wc]

/-- The prefix guard agrees with `Wc` on its support. -/
lemma Wc_guard_eq (k : ℕ) :
    ∀ i, i ≤ k → (fun s => if _h : s ≤ k then Wc s else 0) i = Wc i := by
  intro i hi
  simp only [dif_pos hi]

/-- **De-guarding.** For `t ≥ 1`, the guarded prefix in `Wc`'s recursion may be
replaced by `Wc` itself. -/
lemma Wc_unfold (t : ℕ) (ht : 1 ≤ t) :
    Wc t = - ∑ i ∈ Finset.Icc 1 t, mSeq i * convPow Wc (i + 1) (t - i) := by
  obtain ⟨k, rfl⟩ : ∃ k, t = k + 1 := ⟨t - 1, by omega⟩
  rw [Wc]
  congr 1
  refine Finset.sum_congr rfl fun i hi => ?_
  rw [Finset.mem_Icc] at hi
  congr 1
  exact convPow_congr_le (Wc_guard_eq k) (i + 1) (k + 1 - i) (by omega)

/-- `convPow Wc 1 = Wc`. -/
lemma convPow_Wc_one : convPow Wc 1 = Wc := by simp only [convPow, conv_eps]

/-- **The `W` fixed point.** `eps = Σ_i m_i·W^{∗(i+1)}` coefficient-by-coefficient
(with the `y^i` shift built into the range). The `t = 0` case reads `1 = m₀·W₀`. -/
lemma W_fixed (t : ℕ) :
    eps t = ∑ i ∈ Finset.range (t + 1), mSeq i * convPow Wc (i + 1) (t - i) := by
  rcases Nat.eq_zero_or_pos t with rfl | ht
  · rw [Finset.range_one, Finset.sum_singleton, Nat.sub_zero, mSeq_zero, one_mul,
      convPow_Wc_one, Wc_zero]
    simp [eps]
  · rw [range_succ_eq_insert_Icc, Finset.sum_insert (by simp), Nat.sub_zero, mSeq_zero,
      one_mul, convPow_Wc_one, Wc_unfold t ht,
      show eps t = 0 by simp only [eps]; rw [if_neg (by omega)]]
    ring

/-! ## The cumulant sequence `bSeq` and the `W`-power bridge -/

/-- Cumulant coefficients `b_j := −(log W)_j` (with `b 0 = 0`). -/
noncomputable def bSeq : ℕ → ℚ := fun j => if j = 0 then 0 else - logSeq Wc j

/-- `exp(−b) = W`. -/
lemma expSeq_neg_b : expSeq (fun j => -bSeq j) = Wc := by
  have h : (fun j => -bSeq j) = fun j => if j = 0 then 0 else logSeq Wc j := by
    funext j
    simp only [bSeq]
    split <;> simp
  rw [h]
  exact expSeq_logSeq Wc Wc_zero

/-- **The `W`-power bridge.** `exp(p·(−b)) = W^{∗p}`. -/
lemma expSeq_neg_b_pow (p : ℕ) :
    expSeq (fun j => (p : ℚ) * (-bSeq j)) = convPow Wc p := by
  rw [expSeq_nsmul (fun j => -bSeq j) p, expSeq_neg_b]

/-! ## The level-solved cumulant `aSeq` and `expCoeff` -/

set_option linter.unusedVariables false in
/-- `a`: level-solved from `T` so that level `k` matches `T` at its onset point
`n = 2k+1` by construction. Prefix-guarded well-founded recursion (`aSeq` is read
only at `j < k`; the `j = k` term is forced to `0` inside `expSeq`, so it
contributes `bSeq k·(2k+1)` there). -/
noncomputable def aSeq : ℕ → ℚ
  | k => 3 ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) / 3 ^ (2 * k + 1)
      - expSeq (fun j => (if h : j < k then aSeq j else 0) + bSeq j * ((2 * k + 1 : ℕ) : ℚ)) k
  decreasing_by exact h

/-- `exp` of the affine cumulants `a_j + b_j·n` at level `k`. -/
noncomputable def expCoeff (a b : ℕ → ℚ) (k : ℕ) (n : ℚ) : ℚ :=
  expSeq (fun j => a j + b j * n) k

/-- **Coefficient-wise congruence.** If two cumulant sequences agree on
`[1, M]`, their `expSeq` agree up to index `M`. -/
lemma expSeq_congr_le {c c' : ℕ → ℚ} {M : ℕ}
    (h : ∀ j, 1 ≤ j → j ≤ M → c j = c' j) :
    ∀ m, m ≤ M → expSeq c m = expSeq c' m := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m IH =>
    intro hm
    cases m with
    | zero => rw [expSeq_zero, expSeq_zero]
    | succ m =>
      have hs : (∑ j ∈ Finset.Icc 1 (m + 1), (j : ℚ) * c j * expSeq c (m + 1 - j))
          = ∑ j ∈ Finset.Icc 1 (m + 1), (j : ℚ) * c' j * expSeq c' (m + 1 - j) := by
        refine Finset.sum_congr rfl fun j hj => ?_
        rw [Finset.mem_Icc] at hj
        rw [h j hj.1 (by omega), IH (m + 1 - j) (by omega) (by omega)]
      have hmul : ((m + 1 : ℕ) : ℚ) * expSeq c (m + 1)
          = ((m + 1 : ℕ) : ℚ) * expSeq c' (m + 1) := by
        rw [expSeq_unfold, expSeq_unfold, hs]
      have hne : ((m + 1 : ℕ) : ℚ) ≠ 0 := by push_cast; positivity
      exact mul_left_cancel₀ hne hmul

/-- Peel the top (`j = k`) term of `expSeq`: for `k ≥ 1`,
`(k+1)·E_{k+1} = (k+1)·c_{k+1} + Σ_{j∈Icc 1 k} j·c_j·E_{k+1−j}`. -/
lemma expSeq_succ_split (c : ℕ → ℚ) (k : ℕ) :
    ((k + 1 : ℕ) : ℚ) * expSeq c (k + 1)
      = ((k + 1 : ℕ) : ℚ) * c (k + 1)
        + ∑ j ∈ Finset.Icc 1 k, (j : ℚ) * c j * expSeq c (k + 1 - j) := by
  rw [expSeq_unfold, Finset.sum_Icc_succ_top (by omega : 1 ≤ k + 1), Nat.sub_self,
    expSeq_zero, mul_one]
  ring

/-- **Onset value.** `expCoeff aSeq bSeq k (2k+1) = 3^(3k+1)·T(2k+1,k+1)/3^(2k+1)`
by construction — for `k = 0` this is `T 1 1 = 1` (`T_one_one`), for `k ≥ 1` a
top-term cancellation using `aSeq`'s definition. -/
lemma base_val (k : ℕ) :
    expCoeff aSeq bSeq k ((2 * k + 1 : ℕ) : ℚ)
      = 3 ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) / 3 ^ (2 * k + 1) := by
  cases k with
  | zero =>
    simp only [expCoeff, expSeq_zero, Nat.mul_zero, Nat.zero_add, pow_one,
      T_one_one, Nat.cast_one, mul_one]
    norm_num
  | succ k =>
    -- unfold aSeq at level k+1 (exact expression it reduces to)
    have haSeq0 : aSeq (k + 1)
        = 3 ^ (3 * (k + 1) + 1) * (T (2 * (k + 1) + 1) (k + 1 + 1) : ℚ) / 3 ^ (2 * (k + 1) + 1)
          - expSeq (fun j => (if h : j < k + 1 then aSeq j else 0)
              + bSeq j * ((2 * (k + 1) + 1 : ℕ) : ℚ)) (k + 1) := by
      conv_lhs => rw [aSeq]
    rw [expCoeff]
    set n0 : ℚ := ((2 * (k + 1) + 1 : ℕ) : ℚ) with hn0
    set cum : ℕ → ℚ := fun j => aSeq j + bSeq j * n0 with hcum
    set cum' : ℕ → ℚ :=
      fun j => (if h : j < k + 1 then aSeq j else 0) + bSeq j * n0 with hcum'
    -- goal: expSeq cum (k+1) = 3^.../3^... ;  haSeq0 : aSeq (k+1) = … − expSeq cum' (k+1)
    have hagree : ∀ j, 1 ≤ j → j ≤ k → cum j = cum' j := by
      intro j _ hjk
      simp only [hcum, hcum', dif_pos (by omega : j < k + 1)]
    have hlow : (∑ j ∈ Finset.Icc 1 k, (j : ℚ) * cum j * expSeq cum (k + 1 - j))
        = ∑ j ∈ Finset.Icc 1 k, (j : ℚ) * cum' j * expSeq cum' (k + 1 - j) := by
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Finset.mem_Icc] at hj
      rw [hagree j hj.1 hj.2,
        expSeq_congr_le (M := k) (fun i hi1 hik => hagree i hi1 hik) (k + 1 - j) (by omega)]
    have hsplit := expSeq_succ_split cum k
    have hsplit' := expSeq_succ_split cum' k
    rw [hlow] at hsplit
    have hcumk : cum (k + 1) = aSeq (k + 1) + bSeq (k + 1) * n0 := by simp only [hcum]
    have hcumk' : cum' (k + 1) = bSeq (k + 1) * n0 := by
      simp only [hcum', dif_neg (by omega : ¬ k + 1 < k + 1), zero_add]
    have hne : ((k + 1 : ℕ) : ℚ) ≠ 0 := by push_cast; positivity
    have hdiff : expSeq cum (k + 1) - expSeq cum' (k + 1) = aSeq (k + 1) := by
      have hmul : ((k + 1 : ℕ) : ℚ) * (expSeq cum (k + 1) - expSeq cum' (k + 1))
          = ((k + 1 : ℕ) : ℚ) * aSeq (k + 1) := by
        rw [mul_sub, hsplit, hsplit', hcumk, hcumk']; ring
      exact mul_left_cancel₀ hne hmul
    have hassemble : expSeq cum (k + 1) = aSeq (k + 1) + expSeq cum' (k + 1) := by
      rw [← hdiff]; ring
    rw [hassemble, haSeq0]; ring

/-- **The induction base.** `3^(3k+1)·T(2k+1,k+1) = expCoeff aSeq bSeq k (2k+1)·3^(2k+1)`
— the `H = k+1` instance of `grand_form`, by construction of `aSeq`. -/
lemma base_match (k : ℕ) :
    (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ)
      = expCoeff aSeq bSeq k ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1) := by
  rw [base_val k]
  have h3 : (3 : ℚ) ^ (2 * k + 1) ≠ 0 := by positivity
  field_simp

/-! ## The affine shift and the exp-staircase -/

/-- **Affine shift.** Shifting the evaluation point down by `i+1` convolves in the
`(i+1)`-th power of `W` (the cumulant difference is `−(i+1)·b`). -/
lemma affine_shift (k i : ℕ) (n : ℚ) :
    expCoeff aSeq bSeq k (n - ((i : ℚ) + 1))
      = conv (expSeq (fun j => aSeq j + bSeq j * n)) (convPow Wc (i + 1)) k := by
  rw [expCoeff]
  have hfun : (fun j => aSeq j + bSeq j * (n - ((i : ℚ) + 1)))
      = fun j => (aSeq j + bSeq j * n) + (((i + 1 : ℕ) : ℚ) * (-bSeq j)) := by
    funext j; push_cast; ring
  rw [hfun, expSeq_add (fun j => aSeq j + bSeq j * n) (fun j => ((i + 1 : ℕ) : ℚ) * (-bSeq j)),
    expSeq_neg_b_pow (i + 1)]

/-- **The exp-staircase** (abstract analogue of `T_staircase`): one step in `n`
folds the `expCoeff` diagonal family against `mSeq`, exactly. Proved from the
affine shift and the `W` fixed point. -/
lemma expStair (k : ℕ) (n : ℚ) :
    expCoeff aSeq bSeq k (n + 1)
      = ∑ i ∈ Finset.range (k + 1), mSeq i * expCoeff aSeq bSeq (k - i) (n - (i : ℚ)) := by
  -- expand each RHS term via the affine shift into an explicit double sum
  have hterm : (∑ i ∈ Finset.range (k + 1), mSeq i * expCoeff aSeq bSeq (k - i) (n - (i : ℚ)))
      = ∑ i ∈ Finset.range (k + 1), ∑ s ∈ Finset.range (k - i + 1),
          mSeq i * (expSeq (fun j => aSeq j + bSeq j * (n + 1)) s
            * convPow Wc (i + 1) (k - i - s)) := by
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [show n - (i : ℚ) = (n + 1) - ((i : ℚ) + 1) by ring, affine_shift (k - i) i (n + 1)]
    simp only [conv]
    rw [Finset.mul_sum]
  -- swap the order of summation over the triangle {(i,s) : i+s ≤ k}
  have hswap : (∑ i ∈ Finset.range (k + 1), ∑ s ∈ Finset.range (k - i + 1),
          mSeq i * (expSeq (fun j => aSeq j + bSeq j * (n + 1)) s
            * convPow Wc (i + 1) (k - i - s)))
      = ∑ s ∈ Finset.range (k + 1), ∑ i ∈ Finset.range (k - s + 1),
          mSeq i * (expSeq (fun j => aSeq j + bSeq j * (n + 1)) s
            * convPow Wc (i + 1) (k - i - s)) := by
    apply Finset.sum_comm'
    intro i s
    simp only [Finset.mem_range]
    omega
  -- the inner `i`-sum is `eps (k−s)` by the W fixed point
  have hinner : ∀ s ∈ Finset.range (k + 1),
      (∑ i ∈ Finset.range (k - s + 1), mSeq i *
          (expSeq (fun j => aSeq j + bSeq j * (n + 1)) s * convPow Wc (i + 1) (k - i - s)))
        = expSeq (fun j => aSeq j + bSeq j * (n + 1)) s * eps (k - s) := by
    intro s hs
    rw [Finset.mem_range] at hs
    rw [W_fixed (k - s), Finset.mul_sum]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    rw [show k - i - s = (k - s) - i by omega]
    ring
  have hcollapse : (∑ s ∈ Finset.range (k + 1),
        expSeq (fun j => aSeq j + bSeq j * (n + 1)) s * eps (k - s))
      = conv (expSeq (fun j => aSeq j + bSeq j * (n + 1))) eps k := rfl
  rw [hterm, hswap, Finset.sum_congr rfl hinner, hcollapse, conv_eps, expCoeff]

/-! ## The grand form -/

/-- **The grand form, formalized** (unconditional): the diagonals of `T` are the
exp of affine cumulants — exactly two new rational constants `(aSeq k, bSeq k)`
per level — for every `k` and `H ≥ k+1`, with NO banked hypotheses. Proved by
strong induction on `k` with an inner `Nat.le_induction` on `H`: base
`base_match`, step `T_staircase` + `expStair`. Standard axioms only. -/
theorem grand_form : ∀ k H : ℕ, k + 1 ≤ H →
    (3 : ℚ) ^ (3 * k + 1) * (T (H + k) H : ℚ)
      = expCoeff aSeq bSeq k ((H : ℚ) + k) * 3 ^ (H + k) := by
  intro k
  induction k using Nat.strong_induction_on with
  | _ k IHk =>
    intro H hH
    induction H, hH using Nat.le_induction with
    | base =>
      rw [show (k + 1) + k = 2 * k + 1 by omega,
        show ((k + 1 : ℕ) : ℚ) + (k : ℚ) = ((2 * k + 1 : ℕ) : ℚ) by push_cast; ring]
      exact base_match k
    | succ H hkH IHH =>
      -- unified level statement for every `i ∈ range (k+1)`
      have hG : ∀ i, i ≤ k →
          (3 : ℚ) ^ (3 * (k - i) + 1) * (T (H + (k - i)) H : ℚ)
            = expCoeff aSeq bSeq (k - i) ((H : ℚ) + ((k - i : ℕ) : ℚ)) * 3 ^ (H + (k - i)) := by
        intro i hik
        rcases Nat.eq_zero_or_pos i with rfl | hpos
        · simpa using IHH
        · exact IHk (k - i) (by omega) H (by omega)
      -- pull the goal's RHS into exp-staircase form
      have hrhs : expCoeff aSeq bSeq k (((H + 1 : ℕ) : ℚ) + k) * 3 ^ ((H + 1) + k)
          = (∑ i ∈ Finset.range (k + 1),
              mSeq i * expCoeff aSeq bSeq (k - i) ((H : ℚ) + ((k - i : ℕ) : ℚ)))
            * 3 ^ (H + k + 1) := by
        rw [show (((H + 1 : ℕ) : ℚ) + k) = ((H : ℚ) + k) + 1 by push_cast; ring,
          expStair k ((H : ℚ) + (k : ℚ)), show ((H + 1) + k) = H + k + 1 by omega]
        congr 1
        refine Finset.sum_congr rfl fun i hi => ?_
        rw [Finset.mem_range] at hi
        rw [show ((H : ℚ) + (k : ℚ)) - (i : ℚ) = (H : ℚ) + ((k - i : ℕ) : ℚ) by
          rw [Nat.cast_sub (by omega : i ≤ k)]; ring]
      rw [hrhs, T_staircase k H hkH, Finset.mul_sum, Finset.sum_mul]
      refine Finset.sum_congr rfl fun i hi => ?_
      rw [Finset.mem_range] at hi
      have hg := hG i (by omega)
      set EC : ℚ := expCoeff aSeq bSeq (k - i) ((H : ℚ) + ((k - i : ℕ) : ℚ)) with hEC
      set TT : ℚ := (T (H + (k - i)) H : ℚ) with hTT
      have hpid : (3 : ℚ) ^ (3 * k + 1) * 3
          = 3 ^ (2 * i) * 3 ^ (i + 1) * 3 ^ (3 * (k - i) + 1) := by
        rw [← pow_succ, ← pow_add, ← pow_add,
          show 3 * k + 1 + 1 = 2 * i + (i + 1) + (3 * (k - i) + 1) by omega]
      rw [show (3 : ℚ) ^ (H + k + 1) = 3 ^ (H + (k - i)) * 3 ^ (i + 1) by
          rw [← pow_add, show H + (k - i) + (i + 1) = H + k + 1 by omega],
        show mSeq i * EC * (3 ^ (H + (k - i)) * 3 ^ (i + 1))
            = mSeq i * 3 ^ (i + 1) * (EC * 3 ^ (H + (k - i))) by ring,
        ← hg, mSeq,
        show (mu i * 3 ^ (2 * i) / 3) * 3 ^ (i + 1) * (3 ^ (3 * (k - i) + 1) * TT)
            = mu i * TT * ((3 ^ (2 * i) * 3 ^ (i + 1) * 3 ^ (3 * (k - i) + 1)) / 3) by ring,
        ← hpid]
      ring

/-- **Production coordinates** of the grand form: for `n ≥ 2k+1`,
`T(n, n−k) = expCoeff aSeq bSeq k n · 3^(n−1−3k)` (`zpow`, negative on the onset
window). The `n`-indexed form the counting engine reads. -/
theorem grand_form_prod (k n : ℕ) (hn : 2 * k + 1 ≤ n) :
    (T n (n - k) : ℚ) = expCoeff aSeq bSeq k (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) := by
  have hkn : k ≤ n := by omega
  have hg := grand_form k (n - k) (by omega)
  rw [show (n - k) + k = n by omega,
    show ((n - k : ℕ) : ℚ) + (k : ℚ) = (n : ℚ) by rw [Nat.cast_sub hkn]; ring] at hg
  have hz : (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) = 3 ^ n / 3 ^ (3 * k + 1) := by
    have hexp : (n : ℤ) - 1 - 3 * k = ((n : ℕ) : ℤ) - ((3 * k + 1 : ℕ) : ℤ) := by push_cast; ring
    rw [hexp, zpow_sub₀ (by norm_num : (3 : ℚ) ≠ 0), zpow_natCast, zpow_natCast]
  rw [hz]
  have h3 : (3 : ℚ) ^ (3 * k + 1) ≠ 0 := by positivity
  field_simp
  linear_combination hg

/-! ## Axiom sanity check -/

section Sanity

#print axioms expSeq_add
#print axioms expSeq_logSeq
#print axioms W_fixed
#print axioms T_one_one
#print axioms base_val
#print axioms base_match
#print axioms affine_shift
#print axioms expStair
#print axioms grand_form
#print axioms grand_form_prod

end Sanity

end Polyplets
