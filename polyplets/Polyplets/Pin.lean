/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.LinearAlgebra.Lagrange
import Polyplets.Shape
import Polyplets.Weights3

/-!
# Pin: explicit production polynomials `P_k` for the diagonal law

`Shape.lean` proves that for every surplus `k` there is *some* `P_k ∈ ℚ[X]` of
degree `≤ k` with the production form
`T(n, n-k) = P_k(n)·3^(n-1-3k)` for `n ≥ 2k+1` (`shape_production`), but does
not identify it. This file **pins** `P_k` to the concrete production polynomial
of `orchestrator/sweep.go` (transcribed via `pin-data.md`): a degree-`≤ k`
polynomial that matches the shape witness at `k+1` distinct onset points must
*be* the shape witness, by Lagrange uniqueness (`pin`). It then carries the
whole diagonal law.

## Tiers

* **Unconditional** `k = 0, 1, 2`: the `k+1` onset points are proved outright —
  `native_decide` (`T 3 2`, `T 4 3`, `T 5 3`) and the verified peeling-recursion
  evaluator (`c_ident`/`d_rec` of `Peel.lean` reduce `T 6 4`, `T 7 5` to the
  `j ≤ 2` weights of `Weights.lean`). `P0_pinned`, `P1_pinned`/`P1_closed`,
  `P2_pinned`/`P2_closed` are the standalone diagonal laws.
* **k = 3, conditional on three heavy leaves** (`P3_pinned_of_heavy`): the same
  recursion evaluator, but its three surplus-3 leaves `V 3 3`, `Vᵗ 3 3`,
  `d 3 4` (enumerations of `C(45,6)·15`, `C(39,6)`, `C(28,7)` subsets — too
  big for one `native_decide`, hence the chunking) are taken as
  hypotheses. `Weights3Heavy.lean` discharges them by `native_decide`, giving
  the unconditional `P3_pinned`. That module is reached by the default target
  (via `Grand.PinGrand`); it costs ~37 min on a cold build and nothing after.
* **Conditional** `k = 4..11` (`Pk_pinned_of_banked`): hypothesize the `k+1`
  banked onset `T`-values (all in `results/triangle.txt`).
* `k = 12..16`: the former PARTIAL tier (`Pk_pinned_of_partial`) is DELETED
  (2026-07-31). Its beyond-banked hypotheses were the production
  polynomial's own PREDICTED values — zero cross-validation — and its
  conclusions are byte-identical to `Grand/PinGrand.lean`'s
  `P<k>_grand_prod`, which needs only two real-swept anchors per level.
  Only the `Pp<k>` definitions, degree lemmas and guards remain here (the
  Grand tier consumes them).

The `k = 4..16` tier is machine-generated from `pin-data.md` by
`scripts/gen_pin.py`; each transcription is guarded by a `norm_num` evaluation
of the polynomial at a pin point (`guard_k_n`), so a mistyped coefficient fails
to compile.
-/

namespace Polyplets

open Polynomial

/-! ## Horner polynomials from coefficient lists -/

/-- Ascending-coefficient Horner polynomial:
`horner [a₀, a₁, …, a_d] = a₀ + a₁·X + … + a_d·X^d`. -/
noncomputable def horner : List ℚ → Polynomial ℚ
  | [] => 0
  | c :: cs => C c + X * horner cs

/-- The Horner polynomial of an `(d+1)`-coefficient list has degree `≤ d`. -/
lemma horner_natDegree_le : ∀ l : List ℚ, (horner l).natDegree ≤ l.length - 1
  | [] => by simp [horner]
  | [c] => by simp [horner]
  | c :: d :: cs => by
      have ih := horner_natDegree_le (d :: cs)
      change (C c + X * horner (d :: cs)).natDegree ≤ _
      refine le_trans (natDegree_add_le _ _) ?_
      rw [natDegree_C]
      refine max_le (Nat.zero_le _) ?_
      refine le_trans natDegree_mul_le ?_
      rw [natDegree_X]
      simp only [List.length_cons] at ih ⊢
      omega

/-- Evaluation of a Horner polynomial is the Horner fold of its coefficients. -/
lemma horner_eval (l : List ℚ) (x : ℚ) :
    (horner l).eval x = l.foldr (fun c acc => c + x * acc) 0 := by
  induction l with
  | nil => simp [horner]
  | cons c cs ih => simp only [horner, eval_add, eval_mul, eval_C, eval_X, ih, List.foldr_cons]

/-- The production polynomial: a descending numerator coefficient list over the
scalar `kf` (the `k!` of `pin-data.md`). -/
noncomputable def prodPoly (num : List ℚ) (kf : ℚ) : Polynomial ℚ :=
  C (1 / kf) * horner num.reverse

/-- `prodPoly` of a `(k+1)`-coefficient numerator has degree `≤ k`. -/
lemma prodPoly_natDegree_le (num : List ℚ) (kf : ℚ) :
    (prodPoly num kf).natDegree ≤ num.length - 1 := by
  refine le_trans (natDegree_C_mul_le _ _) (le_trans (horner_natDegree_le num.reverse) ?_)
  simp [List.length_reverse]

/-- Evaluation of `prodPoly`, ready for `norm_num` at a pin point. -/
lemma prodPoly_eval (num : List ℚ) (kf x : ℚ) :
    (prodPoly num kf).eval x = (1 / kf) * num.reverse.foldr (fun c acc => c + x * acc) 0 := by
  rw [prodPoly, eval_mul, eval_C, horner_eval]

/-! ## The generic pin lemma (Lagrange uniqueness) -/

/-- **Pin lemma.** A polynomial `p` of degree `≤ k` that matches the shape
witness (`shape_production`) at the `k+1` onset points `[2k+1, 3k+1]`
*is* the shape witness, hence carries the full diagonal-law production form.

The hypothesis `hpts` states, at each of the `k+1` onset points
`n ∈ [2k+1, 3k+1]`, that `p(n)` equals the integer `T(n,n-k)·3^(3k+1-n)`
that `production_int_onset` also forces on the witness; Lagrange
(`eq_of_degrees_lt_of_eval_finset_eq`) over `ℚ`, on the interval cast into
`ℚ`, then identifies the two polynomials. (2026-07-31: specialized to
`s = Finset.Icc (2k+1) (3k+1)` — every caller passed exactly that set, so
the former `s`/`hcard`/`hin` parameters were noise.) -/
theorem pin (k : ℕ) (p : Polynomial ℚ) (hp : p.natDegree ≤ k)
    (hpts : ∀ n ∈ Finset.Icc (2 * k + 1) (3 * k + 1),
      p.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ)) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = p.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) := by
  set s : Finset ℕ := Finset.Icc (2 * k + 1) (3 * k + 1) with hs
  have hcard : k + 1 ≤ s.card := by rw [hs, Nat.card_Icc]; omega
  have hin : ∀ n ∈ s, 2 * k + 1 ≤ n ∧ n ≤ 3 * k + 1 := fun n hn =>
    Finset.mem_Icc.mp (hs ▸ hn)
  obtain ⟨P, hPdeg, hPzpow, hPcomp⟩ := shape_production k
  have hpP : p = P := by
    have hinj : Set.InjOn (Nat.cast : ℕ → ℚ) s := fun a _ b _ h => by exact_mod_cast h
    have hcard' : (s.image (Nat.cast : ℕ → ℚ)).card = s.card :=
      Finset.card_image_of_injOn hinj
    apply Polynomial.eq_of_degrees_lt_of_eval_finset_eq (s.image (Nat.cast : ℕ → ℚ))
    · calc p.degree ≤ (p.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hp
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · calc P.degree ≤ (P.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hPdeg
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · intro x hx
      rw [Finset.mem_image] at hx
      obtain ⟨n, hn, rfl⟩ := hx
      rw [hpts n hn]
      obtain ⟨hn1, hn2⟩ := hin n hn
      rw [production_int_onset hPcomp hn1 hn2]
  rw [hpP]
  exact hPzpow

/-! ## The peeling-recursion evaluator

Specialisations of `Peel.lean`'s `d_rec` and `c_ident` to fixed small surplus,
with the double sum over `(j, ℓ)` unfolded. Used to reduce the `k ≤ 3` onset
`T`-values to the aggregated weights of `Weights.lean` / `Weights3.lean`. -/

lemma d_rec_k0 (H : ℕ) (hH : 2 ≤ H) : d 0 H = 3 * d 0 (H - 1) := by
  have h := d_rec 0 H hH
  rw [show (Finset.Icc 1 0 : Finset ℕ) = ∅ from by decide, Finset.sum_empty, add_zero] at h
  exact h

lemma d_rec_k1 (H : ℕ) (hH : 3 ≤ H) :
    d 1 H = 3 * d 1 (H - 1) + V 1 1 * d 0 (H - 2) := by
  have h := d_rec 1 H hH
  simp only [show (Finset.Icc 1 1 : Finset ℕ) = {1} from by decide, Finset.sum_singleton] at h
  rw [show H - 1 - 1 = H - 2 from by omega] at h
  simp only [Nat.reduceSub] at h
  omega

lemma d_rec_k2 (H : ℕ) (hH : 4 ≤ H) :
    d 2 H = 3 * d 2 (H - 1) + V 1 1 * d 1 (H - 2)
      + V 1 2 * d 0 (H - 2) + V 2 2 * d 0 (H - 3) := by
  have h := d_rec 2 H hH
  rw [show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide,
      Finset.sum_pair (by decide : (1 : ℕ) ≠ 2)] at h
  rw [show (Finset.Icc 1 1 : Finset ℕ) = {1} from by decide,
      show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide] at h
  rw [Finset.sum_singleton, Finset.sum_pair (by decide : (1 : ℕ) ≠ 2)] at h
  rw [show H - 1 - 1 = H - 2 from by omega, show H - 1 - 2 = H - 3 from by omega] at h
  simp only [Nat.reduceSub] at h
  omega

lemma d_rec_k3 (H : ℕ) (hH : 5 ≤ H) :
    d 3 H = 3 * d 3 (H - 1) + V 1 1 * d 2 (H - 2)
      + V 1 2 * d 1 (H - 2) + V 2 2 * d 1 (H - 3)
      + V 1 3 * d 0 (H - 2) + V 2 3 * d 0 (H - 3) + V 3 3 * d 0 (H - 4) := by
  have h := d_rec 3 H hH
  rw [show (Finset.Icc 1 3 : Finset ℕ) = {1, 2, 3} from by decide,
      Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton] at h
  rw [show (Finset.Icc 1 1 : Finset ℕ) = {1} from by decide, Finset.sum_singleton,
      show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide,
      Finset.sum_insert (by decide), Finset.sum_singleton,
      show (Finset.Icc 1 3 : Finset ℕ) = {1, 2, 3} from by decide,
      Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton] at h
  rw [show H - 1 - 1 = H - 2 from by omega, show H - 1 - 2 = H - 3 from by omega,
      show H - 1 - 3 = H - 4 from by omega] at h
  simp only [Nat.reduceSub] at h
  omega

lemma c_ident_k2 (H : ℕ) (hH : 3 ≤ H) :
    T (H + 2) H = d 2 H + Vt 1 1 * d 1 (H - 1)
      + Vt 1 2 * d 0 (H - 1) + Vt 2 2 * d 0 (H - 2) := by
  have h := c_ident 2 H hH
  rw [show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide,
      Finset.sum_pair (by decide : (1 : ℕ) ≠ 2)] at h
  rw [show (Finset.Icc 1 1 : Finset ℕ) = {1} from by decide,
      show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide] at h
  rw [Finset.sum_singleton, Finset.sum_pair (by decide : (1 : ℕ) ≠ 2)] at h
  simp only [Nat.reduceSub] at h
  omega

lemma c_ident_k3 (H : ℕ) (hH : 4 ≤ H) :
    T (H + 3) H = d 3 H + Vt 1 1 * d 2 (H - 1)
      + Vt 1 2 * d 1 (H - 1) + Vt 2 2 * d 1 (H - 2)
      + Vt 1 3 * d 0 (H - 1) + Vt 2 3 * d 0 (H - 2) + Vt 3 3 * d 0 (H - 3) := by
  have h := c_ident 3 H hH
  rw [show (Finset.Icc 1 3 : Finset ℕ) = {1, 2, 3} from by decide,
      Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton] at h
  rw [show (Finset.Icc 1 1 : Finset ℕ) = {1} from by decide, Finset.sum_singleton,
      show (Finset.Icc 1 2 : Finset ℕ) = {1, 2} from by decide,
      Finset.sum_insert (by decide), Finset.sum_singleton,
      show (Finset.Icc 1 3 : Finset ℕ) = {1, 2, 3} from by decide,
      Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton] at h
  simp only [Nat.reduceSub] at h
  omega

/-! ### Onset `d`- and `T`-values from the evaluator (unconditional) -/

theorem d_0_5 : d 0 5 = 81 := by
  have h := d_rec_k0 5 (by norm_num); norm_num [d_0_4] at h; omega
theorem d_0_6 : d 0 6 = 243 := by
  have h := d_rec_k0 6 (by norm_num); norm_num [d_0_5] at h; omega
theorem d_1_4 : d 1 4 = 195 := by
  have h := d_rec_k1 4 (by norm_num); norm_num [d_1_3, V_1_1, d_0_2] at h; omega
theorem d_1_5 : d 1 5 = 810 := by
  have h := d_rec_k1 5 (by norm_num); norm_num [d_1_4, V_1_1, d_0_3] at h; omega
theorem d_1_6 : d 1 6 = 3105 := by
  have h := d_rec_k1 6 (by norm_num); norm_num [d_1_5, V_1_1, d_0_4] at h; omega
theorem d_2_5 : d 2 5 = 5515 := by
  have h := d_rec_k2 5 (by norm_num)
  norm_num [d_2_4, V_1_1, d_1_3, V_1_2, d_0_3, V_2_2, d_0_2] at h; omega
theorem d_2_6 : d 2 6 = 25794 := by
  have h := d_rec_k2 6 (by norm_num)
  norm_num [d_2_5, V_1_1, d_1_4, V_1_2, d_0_4, V_2_2, d_0_3] at h; omega

/-- `T(6,4) = 1480` from the surplus-2 c-identity. -/
theorem T_6_4 : T 6 4 = 1480 := by
  have h := c_ident_k2 4 (by norm_num)
  norm_num [d_2_4, Vt_1_1, d_1_3, Vt_1_2, d_0_3, Vt_2_2, d_0_2] at h; omega

/-- `T(7,5) = 7273` from the surplus-2 c-identity. -/
theorem T_7_5 : T 7 5 = 7273 := by
  have h := c_ident_k2 5 (by norm_num)
  norm_num [d_2_5, Vt_1_1, d_1_4, Vt_1_2, d_0_4, Vt_2_2, d_0_3] at h; omega

/-! ## Unconditional tier: `k = 0, 1, 2` -/

/-- k=0 production polynomial `P_0 = 1`. -/
noncomputable def Pp0 : Polynomial ℚ := prodPoly [1] 1
lemma Pp0_deg : Pp0.natDegree ≤ 0 := by
  rw [Pp0]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_0_1 : Pp0.eval (1 : ℚ) = ((T 1 1 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp0, prodPoly_eval]; norm_num [T_1_1]

/-- **k=0 diagonal, unconditional**: `T(n,n) = 3^(n-1)` for `n ≥ 1`. -/
theorem P0_pinned : ∀ n : ℕ, 2 * 0 + 1 ≤ n →
    (T n (n - 0) : ℚ) = Pp0.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 0) := by
  refine pin 0 Pp0 Pp0_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (1 - 0 : ℕ) = 1 from rfl, show (3 * 0 + 1 - 1 : ℕ) = 0 from rfl]
    exact guard_0_1

/-- k=1 production polynomial `P_1 = 25X - 45`. -/
noncomputable def Pp1 : Polynomial ℚ := prodPoly [25, -45] 1
lemma Pp1_deg : Pp1.natDegree ≤ 1 := by
  rw [Pp1]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_1_3 : Pp1.eval (3 : ℚ) = ((T 3 2 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp1, prodPoly_eval]; norm_num [T_3_2]
lemma guard_1_4 : Pp1.eval (4 : ℚ) = ((T 4 3 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp1, prodPoly_eval]; norm_num [T_4_3]

/-- **k=1 diagonal, unconditional** (production form). -/
theorem P1_pinned : ∀ n : ℕ, 2 * 1 + 1 ≤ n →
    (T n (n - 1) : ℚ) = Pp1.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 1) := by
  refine pin 1 Pp1 Pp1_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (3 - 1 : ℕ) = 2 from rfl, show (3 * 1 + 1 - 3 : ℕ) = 1 from rfl]
    exact guard_1_3
  · simp only [show (4 - 1 : ℕ) = 3 from rfl, show (3 * 1 + 1 - 4 : ℕ) = 0 from rfl]
    exact guard_1_4

/-- **k=1 diagonal, human form**: `T(n, n-1) = (25n - 45)·3^(n-4)` for `n ≥ 3`
(retires `Diagonal.T_n_nm1`). -/
theorem P1_closed (n : ℕ) (hn : 3 ≤ n) :
    (T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := P1_pinned n hn
  rw [Pp1, prodPoly_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

/-- k=2 production polynomial `P_2 = ½(625X² - 2459X + 1134)`. -/
noncomputable def Pp2 : Polynomial ℚ := prodPoly [625, -2459, 1134] 2
lemma Pp2_deg : Pp2.natDegree ≤ 2 := by
  rw [Pp2]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_2_5 : Pp2.eval (5 : ℚ) = ((T 5 3 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp2, prodPoly_eval]; norm_num [T_5_3]
lemma guard_2_6 : Pp2.eval (6 : ℚ) = ((T 6 4 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp2, prodPoly_eval]; norm_num [T_6_4]
lemma guard_2_7 : Pp2.eval (7 : ℚ) = ((T 7 5 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp2, prodPoly_eval]; norm_num [T_7_5]

/-- **k=2 diagonal, unconditional** (production form). -/
theorem P2_pinned : ∀ n : ℕ, 2 * 2 + 1 ≤ n →
    (T n (n - 2) : ℚ) = Pp2.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 2) := by
  refine pin 2 Pp2 Pp2_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (5 - 2 : ℕ) = 3 from rfl, show (3 * 2 + 1 - 5 : ℕ) = 2 from rfl]
    exact guard_2_5
  · simp only [show (6 - 2 : ℕ) = 4 from rfl, show (3 * 2 + 1 - 6 : ℕ) = 1 from rfl]
    exact guard_2_6
  · simp only [show (7 - 2 : ℕ) = 5 from rfl, show (3 * 2 + 1 - 7 : ℕ) = 0 from rfl]
    exact guard_2_7

/-- **k=2 diagonal, human form**: `T(n, n-2) = ½(625n² - 2459n + 1134)·3^(n-7)`
for `n ≥ 5` (retires `Diagonal.T_n_nm2`). -/
theorem P2_closed (n : ℕ) (hn : 5 ≤ n) :
    (T n (n - 2) : ℚ)
      = (1 / 2) * (625 * (n : ℚ) ^ 2 - 2459 * (n : ℚ) + 1134) * (3 : ℚ) ^ ((n : ℤ) - 7) := by
  have h := P2_pinned n hn
  rw [Pp2, prodPoly_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

/-! ## k = 3: conditional on the three heavy surplus-3 leaves -/

/-- k=3 production polynomial `P_3 = (15625X³ - 100050X² + 122213X - 32940)/6`. -/
noncomputable def Pp3 : Polynomial ℚ := prodPoly [15625, -100050, 122213, -32940] 6
lemma Pp3_deg : Pp3.natDegree ≤ 3 := by
  rw [Pp3]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_3_7 : Pp3.eval (7 : ℚ) = ((7898 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp3, prodPoly_eval]; norm_num
lemma guard_3_8 : Pp3.eval (8 : ℚ) = ((47066 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp3, prodPoly_eval]; norm_num
lemma guard_3_9 : Pp3.eval (9 : ℚ) = ((241864 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp3, prodPoly_eval]; norm_num
lemma guard_3_10 : Pp3.eval (10 : ℚ) = ((1134865 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp3, prodPoly_eval]; norm_num

/-- **k=3 diagonal, conditional on the three heavy leaves.** Given the surplus-3
cluster weights `V 3 3 = 4778`, `Vᵗ 3 3 = 919` and the base walk-top count
`d 3 4 = 4687` (each an out-of-budget `native_decide`, discharged in
`Weights3Heavy.lean`), the peeling-recursion evaluator reduces the four onset
values `T(7,4), T(8,5), T(9,6), T(10,7)` to banked/light weights, and Lagrange
pins `P_3`. -/
theorem P3_pinned_of_heavy (hV33 : V 3 3 = 4778) (hVt33 : Vt 3 3 = 919)
    (hd34 : d 3 4 = 4687) :
    ∀ n : ℕ, 2 * 3 + 1 ≤ n →
      (T n (n - 3) : ℚ) = Pp3.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 3) := by
  have hd35 : d 3 5 = 32203 := by
    have h := d_rec_k3 5 (by norm_num)
    norm_num [hd34, V_1_1, d_2_3, V_1_2, d_1_3, V_2_2, d_1_2, V_1_3, d_0_3, V_2_3, d_0_2,
      hV33, d_0_1] at h
    omega
  have hd36 : d 3 6 = 178460 := by
    have h := d_rec_k3 6 (by norm_num)
    norm_num [hd35, V_1_1, d_2_4, V_1_2, d_1_4, V_2_2, d_1_3, V_1_3, d_0_4, V_2_3, d_0_3,
      hV33, d_0_2] at h
    omega
  have hd37 : d 3 7 = 878833 := by
    have h := d_rec_k3 7 (by norm_num)
    norm_num [hd36, V_1_1, d_2_5, V_1_2, d_1_5, V_2_2, d_1_4, V_1_3, d_0_5, V_2_3, d_0_4,
      hV33, d_0_3] at h
    omega
  have hT74 : T 7 4 = 7898 := by
    have h := c_ident_k3 4 (by norm_num)
    norm_num [hd34, Vt_1_1, d_2_3, Vt_1_2, d_1_3, Vt_2_2, d_1_2, Vt_1_3, d_0_3, Vt_2_3, d_0_2,
      hVt33, d_0_1] at h
    omega
  have hT85 : T 8 5 = 47066 := by
    have h := c_ident_k3 5 (by norm_num)
    norm_num [hd35, Vt_1_1, d_2_4, Vt_1_2, d_1_4, Vt_2_2, d_1_3, Vt_1_3, d_0_4, Vt_2_3, d_0_3,
      hVt33, d_0_2] at h
    omega
  have hT96 : T 9 6 = 241864 := by
    have h := c_ident_k3 6 (by norm_num)
    norm_num [hd36, Vt_1_1, d_2_5, Vt_1_2, d_1_5, Vt_2_2, d_1_4, Vt_1_3, d_0_5, Vt_2_3, d_0_4,
      hVt33, d_0_3] at h
    omega
  have hT10_7 : T 10 7 = 1134865 := by
    have h := c_ident_k3 7 (by norm_num)
    norm_num [hd37, Vt_1_1, d_2_6, Vt_1_2, d_1_6, Vt_2_2, d_1_5, Vt_1_3, d_0_6, Vt_2_3, d_0_5,
      hVt33, d_0_4] at h
    omega
  refine pin 3 Pp3 Pp3_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (7 - 3 : ℕ) = 4 from rfl, show (3 * 3 + 1 - 7 : ℕ) = 3 from rfl, hT74]
    exact guard_3_7
  · simp only [show (8 - 3 : ℕ) = 5 from rfl, show (3 * 3 + 1 - 8 : ℕ) = 2 from rfl, hT85]
    exact guard_3_8
  · simp only [show (9 - 3 : ℕ) = 6 from rfl, show (3 * 3 + 1 - 9 : ℕ) = 1 from rfl, hT96]
    exact guard_3_9
  · simp only [show (10 - 3 : ℕ) = 7 from rfl, show (3 * 3 + 1 - 10 : ℕ) = 0 from rfl, hT10_7]
    exact guard_3_10

/-! ## Conditional (`k = 4..11`) and partial (`k = 12..16`) tiers

Machine-generated from `pin-data.md` by `scripts/gen_pin.py`. The coefficient
lists are wide; the `longLine` style linter is disabled for this data section
(as `nativeDecide` is in the validation modules). -/

section GeneratedTiers
set_option linter.style.longLine false

/-- k=4 production polynomial (numerator / 24), transcribed from `pin-data.md`. -/
noncomputable def Pp4 : Polynomial ℚ := prodPoly
  [390625, -3596250, 8099843, -6462882, 1752840] 24
lemma Pp4_deg : Pp4.natDegree ≤ 4 := by
  rw [Pp4]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_4_9 : Pp4.eval (9 : ℚ) = ((278240 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp4, prodPoly_eval]; norm_num
lemma guard_4_10 : Pp4.eval (10 : ℚ) = ((1631340 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp4, prodPoly_eval]; norm_num
lemma guard_4_11 : Pp4.eval (11 : ℚ) = ((8533676 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp4, prodPoly_eval]; norm_num
lemma guard_4_12 : Pp4.eval (12 : ℚ) = ((41336884 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp4, prodPoly_eval]; norm_num
lemma guard_4_13 : Pp4.eval (13 : ℚ) = ((189262009 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp4, prodPoly_eval]; norm_num
/-- **k=4, conditional tier.** Given the 5 banked onset values
    `T(n,n-4)` at `n = 9..13` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P4_pinned_of_banked
    (h9 : T 9 5 = 278240)
    (h10 : T 10 6 = 1631340)
    (h11 : T 11 7 = 8533676)
    (h12 : T 12 8 = 41336884)
    (h13 : T 13 9 = 189262009)
    : ∀ n : ℕ, 2 * 4 + 1 ≤ n →
      (T n (n - 4) : ℚ) = Pp4.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 4) := by
  refine pin 4 Pp4 Pp4_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (9 - 4 : ℕ) = 5 from rfl,
      show (3 * 4 + 1 - 9 : ℕ) = 4 from rfl, h9]
    exact guard_4_9
  · simp only [show (10 - 4 : ℕ) = 6 from rfl,
      show (3 * 4 + 1 - 10 : ℕ) = 3 from rfl, h10]
    exact guard_4_10
  · simp only [show (11 - 4 : ℕ) = 7 from rfl,
      show (3 * 4 + 1 - 11 : ℕ) = 2 from rfl, h11]
    exact guard_4_11
  · simp only [show (12 - 4 : ℕ) = 8 from rfl,
      show (3 * 4 + 1 - 12 : ℕ) = 1 from rfl, h12]
    exact guard_4_12
  · simp only [show (13 - 4 : ℕ) = 9 from rfl,
      show (3 * 4 + 1 - 13 : ℕ) = 0 from rfl, h13]
    exact guard_4_13

/-- k=5 production polynomial (numerator / 120), transcribed from `pin-data.md`. -/
noncomputable def Pp5 : Polynomial ℚ := prodPoly
  [9765625, -120546875, 425836625, -650171245, 422003550, 76975920] 120
lemma Pp5_deg : Pp5.natDegree ≤ 5 := by
  rw [Pp5]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_5_11 : Pp5.eval (11 : ℚ) = ((10311170 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
lemma guard_5_12 : Pp5.eval (12 : ℚ) = ((59434367 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
lemma guard_5_13 : Pp5.eval (13 : ℚ) = ((313029646 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
lemma guard_5_14 : Pp5.eval (14 : ℚ) = ((1544727695 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
lemma guard_5_15 : Pp5.eval (15 : ℚ) = ((7251119572 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
lemma guard_5_16 : Pp5.eval (16 : ℚ) = ((32703766750 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp5, prodPoly_eval]; norm_num
/-- **k=5, conditional tier.** Given the 6 banked onset values
    `T(n,n-5)` at `n = 11..16` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P5_pinned_of_banked
    (h11 : T 11 6 = 10311170)
    (h12 : T 12 7 = 59434367)
    (h13 : T 13 8 = 313029646)
    (h14 : T 14 9 = 1544727695)
    (h15 : T 15 10 = 7251119572)
    (h16 : T 16 11 = 32703766750)
    : ∀ n : ℕ, 2 * 5 + 1 ≤ n →
      (T n (n - 5) : ℚ) = Pp5.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 5) := by
  refine pin 5 Pp5 Pp5_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (11 - 5 : ℕ) = 6 from rfl,
      show (3 * 5 + 1 - 11 : ℕ) = 5 from rfl, h11]
    exact guard_5_11
  · simp only [show (12 - 5 : ℕ) = 7 from rfl,
      show (3 * 5 + 1 - 12 : ℕ) = 4 from rfl, h12]
    exact guard_5_12
  · simp only [show (13 - 5 : ℕ) = 8 from rfl,
      show (3 * 5 + 1 - 13 : ℕ) = 3 from rfl, h13]
    exact guard_5_13
  · simp only [show (14 - 5 : ℕ) = 9 from rfl,
      show (3 * 5 + 1 - 14 : ℕ) = 2 from rfl, h14]
    exact guard_5_14
  · simp only [show (15 - 5 : ℕ) = 10 from rfl,
      show (3 * 5 + 1 - 15 : ℕ) = 1 from rfl, h15]
    exact guard_5_15
  · simp only [show (16 - 5 : ℕ) = 11 from rfl,
      show (3 * 5 + 1 - 16 : ℕ) = 0 from rfl, h16]
    exact guard_5_16

/-- k=6 production polynomial (numerator / 720), transcribed from `pin-data.md`. -/
noncomputable def Pp6 : Polynomial ℚ := prodPoly
  [244140625, -3861328125, 19486496875, -47366857935, 55373728180, 946828380, -32099353920] 720
lemma Pp6_deg : Pp6.natDegree ≤ 6 := by
  rw [Pp6]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_6_13 : Pp6.eval (13 : ℚ) = ((393543824 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_14 : Pp6.eval (14 : ℚ) = ((2234817674 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_15 : Pp6.eval (15 : ℚ) = ((11793556454 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_16 : Pp6.eval (16 : ℚ) = ((58863947192 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_17 : Pp6.eval (17 : ℚ) = ((281054436836 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_18 : Pp6.eval (18 : ℚ) = ((1293898414102 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
lemma guard_6_19 : Pp6.eval (19 : ℚ) = ((5776897734667 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp6, prodPoly_eval]; norm_num
/-- **k=6, conditional tier.** Given the 7 banked onset values
    `T(n,n-6)` at `n = 13..19` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P6_pinned_of_banked
    (h13 : T 13 7 = 393543824)
    (h14 : T 14 8 = 2234817674)
    (h15 : T 15 9 = 11793556454)
    (h16 : T 16 10 = 58863947192)
    (h17 : T 17 11 = 281054436836)
    (h18 : T 18 12 = 1293898414102)
    (h19 : T 19 13 = 5776897734667)
    : ∀ n : ℕ, 2 * 6 + 1 ≤ n →
      (T n (n - 6) : ℚ) = Pp6.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 6) := by
  refine pin 6 Pp6 Pp6_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (13 - 6 : ℕ) = 7 from rfl,
      show (3 * 6 + 1 - 13 : ℕ) = 6 from rfl, h13]
    exact guard_6_13
  · simp only [show (14 - 6 : ℕ) = 8 from rfl,
      show (3 * 6 + 1 - 14 : ℕ) = 5 from rfl, h14]
    exact guard_6_14
  · simp only [show (15 - 6 : ℕ) = 9 from rfl,
      show (3 * 6 + 1 - 15 : ℕ) = 4 from rfl, h15]
    exact guard_6_15
  · simp only [show (16 - 6 : ℕ) = 10 from rfl,
      show (3 * 6 + 1 - 16 : ℕ) = 3 from rfl, h16]
    exact guard_6_16
  · simp only [show (17 - 6 : ℕ) = 11 from rfl,
      show (3 * 6 + 1 - 17 : ℕ) = 2 from rfl, h17]
    exact guard_6_17
  · simp only [show (18 - 6 : ℕ) = 12 from rfl,
      show (3 * 6 + 1 - 18 : ℕ) = 1 from rfl, h18]
    exact guard_6_18
  · simp only [show (19 - 6 : ℕ) = 13 from rfl,
      show (3 * 6 + 1 - 19 : ℕ) = 0 from rfl, h19]
    exact guard_6_19

/-- k=7 production polynomial (numerator / 5040), transcribed from `pin-data.md`. -/
noncomputable def Pp7 : Polynomial ℚ := prodPoly
  [6103515625, -119765625000, 812310625000, -2839739579250, 5194366339015, -1878923357430, -6841564107480, 7756630081200] 5040
lemma Pp7_deg : Pp7.natDegree ≤ 7 := by
  rw [Pp7]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_7_15 : Pp7.eval (15 : ℚ) = ((15308484950 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_16 : Pp7.eval (16 : ℚ) = ((85849256593 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_17 : Pp7.eval (17 : ℚ) = ((452930356022 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_18 : Pp7.eval (18 : ℚ) = ((2277043672928 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_19 : Pp7.eval (19 : ℚ) = ((11003764277892 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_20 : Pp7.eval (20 : ℚ) = ((51437609215985 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_21 : Pp7.eval (21 : ℚ) = ((233701237739494 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
lemma guard_7_22 : Pp7.eval (22 : ℚ) = ((1035856891052731 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp7, prodPoly_eval]; norm_num
/-- **k=7, conditional tier.** Given the 8 banked onset values
    `T(n,n-7)` at `n = 15..22` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P7_pinned_of_banked
    (h15 : T 15 8 = 15308484950)
    (h16 : T 16 9 = 85849256593)
    (h17 : T 17 10 = 452930356022)
    (h18 : T 18 11 = 2277043672928)
    (h19 : T 19 12 = 11003764277892)
    (h20 : T 20 13 = 51437609215985)
    (h21 : T 21 14 = 233701237739494)
    (h22 : T 22 15 = 1035856891052731)
    : ∀ n : ℕ, 2 * 7 + 1 ≤ n →
      (T n (n - 7) : ℚ) = Pp7.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 7) := by
  refine pin 7 Pp7 Pp7_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (15 - 7 : ℕ) = 8 from rfl,
      show (3 * 7 + 1 - 15 : ℕ) = 7 from rfl, h15]
    exact guard_7_15
  · simp only [show (16 - 7 : ℕ) = 9 from rfl,
      show (3 * 7 + 1 - 16 : ℕ) = 6 from rfl, h16]
    exact guard_7_16
  · simp only [show (17 - 7 : ℕ) = 10 from rfl,
      show (3 * 7 + 1 - 17 : ℕ) = 5 from rfl, h17]
    exact guard_7_17
  · simp only [show (18 - 7 : ℕ) = 11 from rfl,
      show (3 * 7 + 1 - 18 : ℕ) = 4 from rfl, h18]
    exact guard_7_18
  · simp only [show (19 - 7 : ℕ) = 12 from rfl,
      show (3 * 7 + 1 - 19 : ℕ) = 3 from rfl, h19]
    exact guard_7_19
  · simp only [show (20 - 7 : ℕ) = 13 from rfl,
      show (3 * 7 + 1 - 20 : ℕ) = 2 from rfl, h20]
    exact guard_7_20
  · simp only [show (21 - 7 : ℕ) = 14 from rfl,
      show (3 * 7 + 1 - 21 : ℕ) = 1 from rfl, h21]
    exact guard_7_21
  · simp only [show (22 - 7 : ℕ) = 15 from rfl,
      show (3 * 7 + 1 - 22 : ℕ) = 0 from rfl, h22]
    exact guard_7_22

/-- k=8 production polynomial (numerator / 40320), transcribed from `pin-data.md`. -/
noncomputable def Pp8 : Polynomial ℚ := prodPoly
  [152587890625, -3625976562500, 31658675781250, -149222374175000, 391357255277905, -350057694296660, -718224955399380, 2136536485853040, -923712586957440] 40320
lemma Pp8_deg : Pp8.natDegree ≤ 8 := by
  rw [Pp8]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_8_17 : Pp8.eval (17 : ℚ) = ((603392972436 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_18 : Pp8.eval (18 : ℚ) = ((3348606811298 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_19 : Pp8.eval (19 : ℚ) = ((17644523530186 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_20 : Pp8.eval (20 : ℚ) = ((89123929241486 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_21 : Pp8.eval (21 : ℚ) = ((434488576945172 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_22 : Pp8.eval (22 : ℚ) = ((2054838878732818 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_23 : Pp8.eval (23 : ℚ) = ((9464813564473094 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_24 : Pp8.eval (24 : ℚ) = ((42594477635772598 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
lemma guard_8_25 : Pp8.eval (25 : ℚ) = ((187767529262410933 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp8, prodPoly_eval]; norm_num
/-- **k=8, conditional tier.** Given the 9 banked onset values
    `T(n,n-8)` at `n = 17..25` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P8_pinned_of_banked
    (h17 : T 17 9 = 603392972436)
    (h18 : T 18 10 = 3348606811298)
    (h19 : T 19 11 = 17644523530186)
    (h20 : T 20 12 = 89123929241486)
    (h21 : T 21 13 = 434488576945172)
    (h22 : T 22 14 = 2054838878732818)
    (h23 : T 23 15 = 9464813564473094)
    (h24 : T 24 16 = 42594477635772598)
    (h25 : T 25 17 = 187767529262410933)
    : ∀ n : ℕ, 2 * 8 + 1 ≤ n →
      (T n (n - 8) : ℚ) = Pp8.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 8) := by
  refine pin 8 Pp8 Pp8_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (17 - 8 : ℕ) = 9 from rfl,
      show (3 * 8 + 1 - 17 : ℕ) = 8 from rfl, h17]
    exact guard_8_17
  · simp only [show (18 - 8 : ℕ) = 10 from rfl,
      show (3 * 8 + 1 - 18 : ℕ) = 7 from rfl, h18]
    exact guard_8_18
  · simp only [show (19 - 8 : ℕ) = 11 from rfl,
      show (3 * 8 + 1 - 19 : ℕ) = 6 from rfl, h19]
    exact guard_8_19
  · simp only [show (20 - 8 : ℕ) = 12 from rfl,
      show (3 * 8 + 1 - 20 : ℕ) = 5 from rfl, h20]
    exact guard_8_20
  · simp only [show (21 - 8 : ℕ) = 13 from rfl,
      show (3 * 8 + 1 - 21 : ℕ) = 4 from rfl, h21]
    exact guard_8_21
  · simp only [show (22 - 8 : ℕ) = 14 from rfl,
      show (3 * 8 + 1 - 22 : ℕ) = 3 from rfl, h22]
    exact guard_8_22
  · simp only [show (23 - 8 : ℕ) = 15 from rfl,
      show (3 * 8 + 1 - 23 : ℕ) = 2 from rfl, h23]
    exact guard_8_23
  · simp only [show (24 - 8 : ℕ) = 16 from rfl,
      show (3 * 8 + 1 - 24 : ℕ) = 1 from rfl, h24]
    exact guard_8_24
  · simp only [show (25 - 8 : ℕ) = 17 from rfl,
      show (3 * 8 + 1 - 25 : ℕ) = 0 from rfl, h25]
    exact guard_8_25

/-- k=9 production polynomial (numerator / 362880), transcribed from `pin-data.md`. -/
noncomputable def Pp9 : Polynomial ℚ := prodPoly
  [3814697265625, -107720947265625, 1172546074218750, -7126125723281250, 25246485663128625, -39217219391133945, -44784313962337720, 312218815384892340, -359168984859479760, 17928204588927360] 362880
lemma Pp9_deg : Pp9.natDegree ≤ 9 := by
  rw [Pp9]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_9_19 : Pp9.eval (19 : ℚ) = ((24014057424024 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_20 : Pp9.eval (20 : ℚ) = ((132107598093637 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_21 : Pp9.eval (21 : ℚ) = ((694918765309300 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_22 : Pp9.eval (22 : ℚ) = ((3521085234178586 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_23 : Pp9.eval (23 : ℚ) = ((17278818571437182 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_24 : Pp9.eval (24 : ℚ) = ((82463515269090962 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_25 : Pp9.eval (25 : ℚ) = ((384025992867882686 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_26 : Pp9.eval (26 : ℚ) = ((1749771804351434045 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_27 : Pp9.eval (27 : ℚ) = ((7817976479588367238 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
lemma guard_9_28 : Pp9.eval (28 : ℚ) = ((34317502124615571106 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp9, prodPoly_eval]; norm_num
/-- **k=9, conditional tier.** Given the 10 banked onset values
    `T(n,n-9)` at `n = 19..28` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P9_pinned_of_banked
    (h19 : T 19 10 = 24014057424024)
    (h20 : T 20 11 = 132107598093637)
    (h21 : T 21 12 = 694918765309300)
    (h22 : T 22 13 = 3521085234178586)
    (h23 : T 23 14 = 17278818571437182)
    (h24 : T 24 15 = 82463515269090962)
    (h25 : T 25 16 = 384025992867882686)
    (h26 : T 26 17 = 1749771804351434045)
    (h27 : T 27 18 = 7817976479588367238)
    (h28 : T 28 19 = 34317502124615571106)
    : ∀ n : ℕ, 2 * 9 + 1 ≤ n →
      (T n (n - 9) : ℚ) = Pp9.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 9) := by
  refine pin 9 Pp9 Pp9_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (19 - 9 : ℕ) = 10 from rfl,
      show (3 * 9 + 1 - 19 : ℕ) = 9 from rfl, h19]
    exact guard_9_19
  · simp only [show (20 - 9 : ℕ) = 11 from rfl,
      show (3 * 9 + 1 - 20 : ℕ) = 8 from rfl, h20]
    exact guard_9_20
  · simp only [show (21 - 9 : ℕ) = 12 from rfl,
      show (3 * 9 + 1 - 21 : ℕ) = 7 from rfl, h21]
    exact guard_9_21
  · simp only [show (22 - 9 : ℕ) = 13 from rfl,
      show (3 * 9 + 1 - 22 : ℕ) = 6 from rfl, h22]
    exact guard_9_22
  · simp only [show (23 - 9 : ℕ) = 14 from rfl,
      show (3 * 9 + 1 - 23 : ℕ) = 5 from rfl, h23]
    exact guard_9_23
  · simp only [show (24 - 9 : ℕ) = 15 from rfl,
      show (3 * 9 + 1 - 24 : ℕ) = 4 from rfl, h24]
    exact guard_9_24
  · simp only [show (25 - 9 : ℕ) = 16 from rfl,
      show (3 * 9 + 1 - 25 : ℕ) = 3 from rfl, h25]
    exact guard_9_25
  · simp only [show (26 - 9 : ℕ) = 17 from rfl,
      show (3 * 9 + 1 - 26 : ℕ) = 2 from rfl, h26]
    exact guard_9_26
  · simp only [show (27 - 9 : ℕ) = 18 from rfl,
      show (3 * 9 + 1 - 27 : ℕ) = 1 from rfl, h27]
    exact guard_9_27
  · simp only [show (28 - 9 : ℕ) = 19 from rfl,
      show (3 * 9 + 1 - 28 : ℕ) = 0 from rfl, h28]
    exact guard_9_28

/-- k=10 production polynomial (numerator / 3628800), transcribed from `pin-data.md`. -/
noncomputable def Pp10 : Polynomial ℚ := prodPoly
  [95367431640625, -3151702880859375, 41724067382812500, -316409147402343750, 1450416433150453125, -3370526923710995055, -1108292379978242050, 31805482385795516100, -69735093253554241800, 32190356082435763680, 25618243319042572800] 3628800
lemma Pp10_deg : Pp10.natDegree ≤ 10 := by
  rw [Pp10]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_10_21 : Pp10.eval (21 : ℚ) = ((962797249464752 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_22 : Pp10.eval (22 : ℚ) = ((5257610926802452 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_23 : Pp10.eval (23 : ℚ) = ((27605091155079103 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_24 : Pp10.eval (24 : ℚ) = ((140166422140948001 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_25 : Pp10.eval (25 : ℚ) = ((691293861738937174 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_26 : Pp10.eval (26 : ℚ) = ((3323155898057126432 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_27 : Pp10.eval (27 : ℚ) = ((15614430359151357239 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_28 : Pp10.eval (28 : ℚ) = ((71877874772392940643 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_29 : Pp10.eval (29 : ℚ) = ((324790356631486274300 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_30 : Pp10.eval (30 : ℚ) = ((1443010407311300007988 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
lemma guard_10_31 : Pp10.eval (31 : ℚ) = ((6312683044683280162504 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp10, prodPoly_eval]; norm_num
/-- **k=10, conditional tier.** Given the 11 banked onset values
    `T(n,n-10)` at `n = 21..31` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P10_pinned_of_banked
    (h21 : T 21 11 = 962797249464752)
    (h22 : T 22 12 = 5257610926802452)
    (h23 : T 23 13 = 27605091155079103)
    (h24 : T 24 14 = 140166422140948001)
    (h25 : T 25 15 = 691293861738937174)
    (h26 : T 26 16 = 3323155898057126432)
    (h27 : T 27 17 = 15614430359151357239)
    (h28 : T 28 18 = 71877874772392940643)
    (h29 : T 29 19 = 324790356631486274300)
    (h30 : T 30 20 = 1443010407311300007988)
    (h31 : T 31 21 = 6312683044683280162504)
    : ∀ n : ℕ, 2 * 10 + 1 ≤ n →
      (T n (n - 10) : ℚ) = Pp10.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 10) := by
  refine pin 10 Pp10 Pp10_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (21 - 10 : ℕ) = 11 from rfl,
      show (3 * 10 + 1 - 21 : ℕ) = 10 from rfl, h21]
    exact guard_10_21
  · simp only [show (22 - 10 : ℕ) = 12 from rfl,
      show (3 * 10 + 1 - 22 : ℕ) = 9 from rfl, h22]
    exact guard_10_22
  · simp only [show (23 - 10 : ℕ) = 13 from rfl,
      show (3 * 10 + 1 - 23 : ℕ) = 8 from rfl, h23]
    exact guard_10_23
  · simp only [show (24 - 10 : ℕ) = 14 from rfl,
      show (3 * 10 + 1 - 24 : ℕ) = 7 from rfl, h24]
    exact guard_10_24
  · simp only [show (25 - 10 : ℕ) = 15 from rfl,
      show (3 * 10 + 1 - 25 : ℕ) = 6 from rfl, h25]
    exact guard_10_25
  · simp only [show (26 - 10 : ℕ) = 16 from rfl,
      show (3 * 10 + 1 - 26 : ℕ) = 5 from rfl, h26]
    exact guard_10_26
  · simp only [show (27 - 10 : ℕ) = 17 from rfl,
      show (3 * 10 + 1 - 27 : ℕ) = 4 from rfl, h27]
    exact guard_10_27
  · simp only [show (28 - 10 : ℕ) = 18 from rfl,
      show (3 * 10 + 1 - 28 : ℕ) = 3 from rfl, h28]
    exact guard_10_28
  · simp only [show (29 - 10 : ℕ) = 19 from rfl,
      show (3 * 10 + 1 - 29 : ℕ) = 2 from rfl, h29]
    exact guard_10_29
  · simp only [show (30 - 10 : ℕ) = 20 from rfl,
      show (3 * 10 + 1 - 30 : ℕ) = 1 from rfl, h30]
    exact guard_10_30
  · simp only [show (31 - 10 : ℕ) = 21 from rfl,
      show (3 * 10 + 1 - 31 : ℕ) = 0 from rfl, h31]
    exact guard_10_31

/-- k=11 production polynomial (numerator / 39916800), transcribed from `pin-data.md`. -/
noncomputable def Pp11 : Polynomial ℚ := prodPoly
  [2384185791015625, -91056823730468750, 1437517181396484375, -13264842209179687500, 76160367268876171875, -243501035699144280750, 120586120186765409825, 2497738719648063722600, -9207797682124933481700, 10269478266342644052000, 3325021854753536899200, 5868473845727607206400] 39916800
lemma Pp11_deg : Pp11.natDegree ≤ 11 := by
  rw [Pp11]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_11_23 : Pp11.eval (23 : ℚ) = ((38826609174639928 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_24 : Pp11.eval (24 : ℚ) = ((210692983396251014 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_25 : Pp11.eval (25 : ℚ) = ((1104184694723970106 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_26 : Pp11.eval (26 : ℚ) = ((5614506356004078534 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_27 : Pp11.eval (27 : ℚ) = ((27798973373501478242 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_28 : Pp11.eval (28 : ℚ) = ((134417487965477643619 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_29 : Pp11.eval (29 : ℚ) = ((636255557111930718092 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_30 : Pp11.eval (30 : ℚ) = ((2954110296739891764128 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_31 : Pp11.eval (31 : ℚ) = ((13476628255738123866262 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_32 : Pp11.eval (32 : ℚ) = ((60496763632561182774506 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_33 : Pp11.eval (33 : ℚ) = ((267567344516616416852062 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
lemma guard_11_34 : Pp11.eval (34 : ℚ) = ((1167265695441145358152351 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp11, prodPoly_eval]; norm_num
/-- **k=11, conditional tier.** Given the 12 banked onset values
    `T(n,n-11)` at `n = 23..34` (all in `results/triangle.txt`),
    the production polynomial is pinned by Lagrange uniqueness. -/
theorem P11_pinned_of_banked
    (h23 : T 23 12 = 38826609174639928)
    (h24 : T 24 13 = 210692983396251014)
    (h25 : T 25 14 = 1104184694723970106)
    (h26 : T 26 15 = 5614506356004078534)
    (h27 : T 27 16 = 27798973373501478242)
    (h28 : T 28 17 = 134417487965477643619)
    (h29 : T 29 18 = 636255557111930718092)
    (h30 : T 30 19 = 2954110296739891764128)
    (h31 : T 31 20 = 13476628255738123866262) -- since real-swept: a38/a39 h20.out agree
    (h32 : T 32 21 = 60496763632561182774506)
    (h33 : T 33 22 = 267567344516616416852062)
    (h34 : T 34 23 = 1167265695441145358152351)
    : ∀ n : ℕ, 2 * 11 + 1 ≤ n →
      (T n (n - 11) : ℚ) = Pp11.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 11) := by
  refine pin 11 Pp11 Pp11_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (23 - 11 : ℕ) = 12 from rfl,
      show (3 * 11 + 1 - 23 : ℕ) = 11 from rfl, h23]
    exact guard_11_23
  · simp only [show (24 - 11 : ℕ) = 13 from rfl,
      show (3 * 11 + 1 - 24 : ℕ) = 10 from rfl, h24]
    exact guard_11_24
  · simp only [show (25 - 11 : ℕ) = 14 from rfl,
      show (3 * 11 + 1 - 25 : ℕ) = 9 from rfl, h25]
    exact guard_11_25
  · simp only [show (26 - 11 : ℕ) = 15 from rfl,
      show (3 * 11 + 1 - 26 : ℕ) = 8 from rfl, h26]
    exact guard_11_26
  · simp only [show (27 - 11 : ℕ) = 16 from rfl,
      show (3 * 11 + 1 - 27 : ℕ) = 7 from rfl, h27]
    exact guard_11_27
  · simp only [show (28 - 11 : ℕ) = 17 from rfl,
      show (3 * 11 + 1 - 28 : ℕ) = 6 from rfl, h28]
    exact guard_11_28
  · simp only [show (29 - 11 : ℕ) = 18 from rfl,
      show (3 * 11 + 1 - 29 : ℕ) = 5 from rfl, h29]
    exact guard_11_29
  · simp only [show (30 - 11 : ℕ) = 19 from rfl,
      show (3 * 11 + 1 - 30 : ℕ) = 4 from rfl, h30]
    exact guard_11_30
  · simp only [show (31 - 11 : ℕ) = 20 from rfl,
      show (3 * 11 + 1 - 31 : ℕ) = 3 from rfl, h31]
    exact guard_11_31
  · simp only [show (32 - 11 : ℕ) = 21 from rfl,
      show (3 * 11 + 1 - 32 : ℕ) = 2 from rfl, h32]
    exact guard_11_32
  · simp only [show (33 - 11 : ℕ) = 22 from rfl,
      show (3 * 11 + 1 - 33 : ℕ) = 1 from rfl, h33]
    exact guard_11_33
  · simp only [show (34 - 11 : ℕ) = 23 from rfl,
      show (3 * 11 + 1 - 34 : ℕ) = 0 from rfl, h34]
    exact guard_11_34

/-- k=12 production polynomial (numerator / 479001600), transcribed from `pin-data.md`. -/
noncomputable def Pp12 : Polynomial ℚ := prodPoly
  [59604644775390625, -2602958679199218750, 48223920440673828125, -530815263596191406250, 3721840065507802734375, -15512118396389744456250, 21149152791035920752695, 157168222110058996109130, -936571784113889621399900, 1860945781255305037306200, -561954556767083249661120, 2518353204096205882465920, -12192370946767873838592000] 479001600
lemma Pp12_deg : Pp12.natDegree ≤ 12 := by
  rw [Pp12]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_12_25 : Pp12.eval (25 : ℚ) = ((1573134737210737385 * 3 ^ 12 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_26 : Pp12.eval (26 : ℚ) = ((8490578913536448064 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_27 : Pp12.eval (27 : ℚ) = ((44416775012217775973 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_28 : Pp12.eval (28 : ℚ) = ((226062958310935838176 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_29 : Pp12.eval (29 : ℚ) = ((1122769428042637253575 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_30 : Pp12.eval (30 : ℚ) = ((5455070058849476986528 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_31 : Pp12.eval (31 : ℚ) = ((25980777373832690315657 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_32 : Pp12.eval (32 : ℚ) = ((121507773432815574458792 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_33 : Pp12.eval (33 : ℚ) = ((558865928667766384033421 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_34 : Pp12.eval (34 : ℚ) = ((2531214280334205695134436 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_35 : Pp12.eval (35 : ℚ) = ((11302231433302167372053753 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_36 : Pp12.eval (36 : ℚ) = ((49802601845517580926757996 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
lemma guard_12_37 : Pp12.eval (37 : ℚ) = ((216761708659294196806446100 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp12, prodPoly_eval]; norm_num
/-- k=13 production polynomial (numerator / 6227020800), transcribed from `pin-data.md`. -/
noncomputable def Pp13 : Polynomial ℚ := prodPoly
  [1490116119384765625, -73735713958740234375, 1581930904388427734375, -20438647987884521484375, 171498867051782080078125, -897242973195286876640625, 2053473678621559440657125, 7845602899216787491993635, -78302966517647904123999050, 242568775590879458927220300, -252892500470648129748781800, 630295671430278785315535840, -4709212944929227143077529600, 8516420444581467205615027200] 6227020800
lemma Pp13_deg : Pp13.natDegree ≤ 13 := by
  rw [Pp13]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_13_27 : Pp13.eval (27 : ℚ) = ((63986427407097237332 * 3 ^ 13 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_28 : Pp13.eval (28 : ℚ) = ((343733831675681363476 * 3 ^ 12 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_29 : Pp13.eval (29 : ℚ) = ((1795111626265027715356 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_30 : Pp13.eval (30 : ℚ) = ((9142099138689979555656 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_31 : Pp13.eval (31 : ℚ) = ((45518261981941858305944 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_32 : Pp13.eval (32 : ℚ) = ((222037213145303005489339 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_33 : Pp13.eval (33 : ℚ) = ((1063017698873182965322124 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_34 : Pp13.eval (34 : ℚ) = ((5002581174202331698460002 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_35 : Pp13.eval (35 : ℚ) = ((23171984177741390734335158 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_36 : Pp13.eval (36 : ℚ) = ((105767663082981556782445241 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_37 : Pp13.eval (37 : ℚ) = ((476222071911467914867327506 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_38 : Pp13.eval (38 : ℚ) = ((2117045402320488291101904275 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_39 : Pp13.eval (39 : ℚ) = ((9299730798107170785360030808 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
lemma guard_13_40 : Pp13.eval (40 : ℚ) = ((40397094232064445666534976009 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp13, prodPoly_eval]; norm_num
/-- k=14 production polynomial (numerator / 87178291200), transcribed from `pin-data.md`. -/
noncomputable def Pp14 : Polynomial ℚ := prodPoly
  [37252902984619140625, -2072393894195556640625, 50912246036529541015625, -761843525055694580078125, 7524678110464896240234375, -48052027303805350998046875, 157448856577961057749371875, 276655470142052990154351185, -5583936647603503419750059540, 25191124931485376140721243800, -47958023503387714879301084400, 118184880567640594471489711440, -979514007904340174674683668160, 3638916058760447487430557542400, -4028797193164605150126008371200] 87178291200
lemma Pp14_deg : Pp14.natDegree ≤ 14 := by
  rw [Pp14]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_14_29 : Pp14.eval (29 : ℚ) = ((2611110015255604740530 * 3 ^ 14 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_30 : Pp14.eval (30 : ℚ) = ((13969442417594351366268 * 3 ^ 13 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_31 : Pp14.eval (31 : ℚ) = ((72837427176953272756444 * 3 ^ 12 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_32 : Pp14.eval (32 : ℚ) = ((371092643133615870167145 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_33 : Pp14.eval (33 : ℚ) = ((1851392394172366952982798 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_34 : Pp14.eval (34 : ℚ) = ((9061341124316405172057950 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_35 : Pp14.eval (35 : ℚ) = ((43575275424260085198846849 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_36 : Pp14.eval (36 : ℚ) = ((206170745618188078237908398 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_37 : Pp14.eval (37 : ℚ) = ((960872649499611634617388174 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_38 : Pp14.eval (38 : ℚ) = ((4415798153086364928090741638 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_39 : Pp14.eval (39 : ℚ) = ((20029030415976318128336407820 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_40 : Pp14.eval (40 : ℚ) = ((89738450015816790329906273587 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_41 : Pp14.eval (41 : ℚ) = ((397456680396732807972242026742 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_42 : Pp14.eval (42 : ℚ) = ((1741355390468722299734072854984 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
lemma guard_14_43 : Pp14.eval (43 : ℚ) = ((7551589891593991743211503128986 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp14, prodPoly_eval]; norm_num
/-- k=15 production polynomial (numerator / 1307674368000), transcribed from `pin-data.md`. -/
noncomputable def Pp15 : Polynomial ℚ := prodPoly
  [931322574615478515625, -57846307754516601562500, 1611761021614074707031250, -27620633003425598144531250, 316736418664104003906250000, -2416046782053819856347656250, 10461322884210958342060156250, 1967893236430787060707991250, -346618516939812097631010184825, 2203970151840239765899986819750, -6398534829863605593928976949100, 17955993014682160383586429971000, -146852693386847802168160405132800, 824216279306486381670291956424000, -1935618838774923672066722617670400, 1370506748049564268873803929856000] 1307674368000
lemma Pp15_deg : Pp15.natDegree ≤ 15 := by
  rw [Pp15]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_15_31 : Pp15.eval (31 : ℚ) = ((106848447386284024770292 * 3 ^ 15 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_32 : Pp15.eval (32 : ℚ) = ((569579285523233406028051 * 3 ^ 14 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_33 : Pp15.eval (33 : ℚ) = ((2965403643769893816836542 * 3 ^ 13 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_34 : Pp15.eval (34 : ℚ) = ((15111742807653801090985593 * 3 ^ 12 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_35 : Pp15.eval (35 : ℚ) = ((75518035463847720292413552 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_36 : Pp15.eval (36 : ℚ) = ((370662558309766127292835233 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_37 : Pp15.eval (37 : ℚ) = ((1789337957103928389914572136 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_38 : Pp15.eval (38 : ℚ) = ((8505713267602095540716166565 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_39 : Pp15.eval (39 : ℚ) = ((39855827398943917208656353418 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_40 : Pp15.eval (40 : ℚ) = ((184265041867569186198215286920 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_41 : Pp15.eval (41 : ℚ) = ((841257097247076130709957596760 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_42 : Pp15.eval (42 : ℚ) = ((3795574848533585489216721942077 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_43 : Pp15.eval (43 : ℚ) = ((16935054908991996005303442375392 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_44 : Pp15.eval (44 : ℚ) = ((74769781466143100221951023237056 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_45 : Pp15.eval (45 : ℚ) = ((326845683400612576938034232258422 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
lemma guard_15_46 : Pp15.eval (46 : ℚ) = ((1415345781292850930051962247664808 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp15, prodPoly_eval]; norm_num
/-- k=16 production polynomial (numerator / 20922789888000), transcribed from `pin-data.md`. -/
noncomputable def Pp16 : Polynomial ℚ := prodPoly
  [23283064365386962890625, -1604855060577392578125000, 50296202898025512695312500, -977645294998168945312500000, 12866158692583824157714843750, -115227786191848182480468750000, 627956075188775884851523437500, -744604346962912741214695500000, -18856370906133182542352742484975, 168083439133981919034904849231800, -683834540674642382762519712038200, 2295047561654327718980302632052800, -17913005887676406640071685928060400, 131791153675357698130550590831267200, -488805850691225808484910594988268800, 759766595538270156033339090440755200, -219118392304691271841806767714304000] 20922789888000
lemma Pp16_deg : Pp16.natDegree ≤ 16 := by
  rw [Pp16]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_16_33 : Pp16.eval (33 : ℚ) = ((4382793740312244017806517 * 3 ^ 16 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_34 : Pp16.eval (34 : ℚ) = ((23288787870043631158670332 * 3 ^ 15 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_35 : Pp16.eval (35 : ℚ) = ((121081244529132538941157409 * 3 ^ 14 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_36 : Pp16.eval (36 : ℚ) = ((617106574276148286251699568 * 3 ^ 13 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_37 : Pp16.eval (37 : ℚ) = ((3088116532240663753100466552 * 3 ^ 12 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_38 : Pp16.eval (38 : ℚ) = ((15194228798887114342965900210 * 3 ^ 11 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_39 : Pp16.eval (39 : ℚ) = ((73593578944746874408267467610 * 3 ^ 10 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_40 : Pp16.eval (40 : ℚ) = ((351269152616432930163117009906 * 3 ^ 9 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_41 : Pp16.eval (41 : ℚ) = ((1653826612613977820761919292031 * 3 ^ 8 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_42 : Pp16.eval (42 : ℚ) = ((7687014105490732269809813183582 * 3 ^ 7 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_43 : Pp16.eval (43 : ℚ) = ((35299971363376894531180373585317 * 3 ^ 6 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_44 : Pp16.eval (44 : ℚ) = ((160265426904862806342404790324662 * 3 ^ 5 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_45 : Pp16.eval (45 : ℚ) = ((719824883297688221996444422232570 * 3 ^ 4 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_46 : Pp16.eval (46 : ℚ) = ((3200253917372236958256602419568304 * 3 ^ 3 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_47 : Pp16.eval (47 : ℚ) = ((14090970086504811644168254469037734 * 3 ^ 2 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_48 : Pp16.eval (48 : ℚ) = ((61476084902654001318172334339180692 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
lemma guard_16_49 : Pp16.eval (49 : ℚ) = ((265872905714472345246195735620197402 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp16, prodPoly_eval]; norm_num
/-! ### k = 17, 18: definitions + real-swept guards only (a(40)-close extension).
    The Lagrange tier is NOT extended here (it would need onset points to
    n = 52, far beyond banked data); these definitions feed the Grand
    tier (`Grand/PinGrand.lean`), which pins P_17 from TWO real cells.
    Guards check only REAL-SWEPT cells (columns H <= 21 of the a(40) run);
    the formula-generated cells on this diagonal are excluded as circular. -/
noncomputable def Pp17 : Polynomial ℚ := prodPoly
  [582076609134674072265625, -44283457100391387939453125, 1549785345792770385742187500, -33886054842615127563476562500, 506738958957323265075683593750, -5253930386581950765319824218750, 34866787110157325826676367187500, -86528320883080938837347917187500, -889937241002481289280616442864375, 11422356391454342173853403279879275, -62157637321860866791915723663376800, 253251875227507029291999691317061400, -1898632937628268836106376147065825200, 16730852931327365644218857489259687600, -86335313597104845199405280481932515200, 218410029105004429734891444381037497600, -171351859928354717515789878977767372800, -114129552065978933164859052982947840000] 355687428096000
lemma Pp17_deg : Pp17.natDegree ≤ 17 := by
  rw [Pp17]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_17_35 : Pp17.eval (35 : ℚ) = ((180152359823857046862682314 * 3 ^ 17 : ℕ) : ℚ) := by
  rw [Pp17, prodPoly_eval]; norm_num
lemma guard_17_36 : Pp17.eval (36 : ℚ) = ((954543410624801880699125196 * 3 ^ 16 : ℕ) : ℚ) := by
  rw [Pp17, prodPoly_eval]; norm_num
lemma guard_17_37 : Pp17.eval (37 : ℚ) = ((4956437442714322066925263218 * 3 ^ 15 : ℕ) : ℚ) := by
  rw [Pp17, prodPoly_eval]; norm_num
lemma guard_17_38 : Pp17.eval (38 : ℚ) = ((25262080143961999373255793104 * 3 ^ 14 : ℕ) : ℚ) := by
  rw [Pp17, prodPoly_eval]; norm_num
noncomputable def Pp18 : Polynomial ℚ := prodPoly
  [14551915228366851806640625, -1216004602611064910888671875, 47220123186707496643066406250, -1152996117314100265502929687500, 19425111820647906303405761718750, -230445407070280340071105957031250, 1818181407908782536004023437500000, -6826614118228039757132018320312500, -34818861040188463329071106306984375, 701508624630574629016108663795874925, -4974015500069905129885380187424318850, 24632585272713265594357624257091138200, -181772288700805914476560807450032440000, 1799250000012213308990934660048459646800, -11981768558659998471685945614032297834400, 43413108716808863459147673721575806860800, -62928082571267723622620177718733540032000, -37079629775551619904419498589278737305600, 127787800900726736892183047952793411584000] 6402373705728000
lemma Pp18_deg : Pp18.natDegree ≤ 18 := by
  rw [Pp18]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_18_37 : Pp18.eval (37 : ℚ) = ((7418664369542642927200487045 * 3 ^ 18 : ℕ) : ℚ) := by
  rw [Pp18, prodPoly_eval]; norm_num
lemma guard_18_38 : Pp18.eval (38 : ℚ) = ((39207474138446972682720171554 * 3 ^ 17 : ℕ) : ℚ) := by
  rw [Pp18, prodPoly_eval]; norm_num
lemma guard_18_39 : Pp18.eval (39 : ℚ) = ((203342057467470725522863434005 * 3 ^ 16 : ℕ) : ℚ) := by
  rw [Pp18, prodPoly_eval]; norm_num


end GeneratedTiers

end Polyplets
