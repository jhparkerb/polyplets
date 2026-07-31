/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.KingAgree
import Polyplets.Universal.Compute
import Polyplets.Pin

/-!
# Gate GD-3 at the king lattice: the re-derivation

`Universal/KingAgree.lean` settled the phase-B gate — the generic geometry
reproduces `Peel.lean`'s objects and recursions at `kingLattice`. This file
closes the loop at the top: the **universal theorems** of
`Universal/System.lean`, instantiated at `kingLattice` and rewritten through
`T_king`/`d_king`/`b_king`, are *the king theorems of `Shape.lean`* — same
statements, no bridging hypotheses, no residue of the generic vocabulary.

The statement-level diff is checked mechanically, exactly as at GD-1: the four
`Prop` transcriptions `KingShapeD`, `KingShape`, `KingShapeProduction`,
`KingProductionIntAll` of `Universal/AbstractShape.lean` are the original
`Shape.lean` types, and each is inhabited here by the universal route.
**Diff: none.**

Two further cross-checks, parallel to `Universal/{Square,Hex}.lean`:

* the *generic* enumerator `Tc` of `Universal/Compute.lean` — which knows
  nothing of `kingAdj` — reproduces the banked king cells `T(3,2) = 10`,
  `T(4,3) = 55`, `T(5,4) = 240` and the row sums `20`, `110`, `638` of
  A006770;
* the generic pin lemma at `k = 1` produces `Pin.lean`'s `P₁ = 25X − 45` on the
  nose (`kingP1_eq_Pp1`) and hence re-proves `P1_pinned` and `P1_closed`
  through the universal machinery.

The existing king tree is imported, never modified.
-/

namespace Polyplets.Universal

open Polynomial

/-! ## The four shape theorems, re-derived universally -/

/-- **`Shape.lean`'s `shape_d`, from the universal theorem.** -/
theorem king_shape_d_via_universal : KingShapeD := by
  intro k
  obtain ⟨δ, hdeg, h⟩ := universal_shape_d kingLattice k
  exact ⟨δ, hdeg, fun H hH => by simpa using h H hH⟩

/-- **`Shape.lean`'s `shape`, from the universal theorem.** -/
theorem king_shape_via_universal : KingShape := by
  intro k
  obtain ⟨q, hdeg, h⟩ := universal_shape kingLattice k
  refine ⟨q, hdeg, fun H hH => ?_⟩
  have hh := h H hH
  rw [T_king] at hh
  simpa using hh

/-- **`Shape.lean`'s `shape_production`, from the universal theorem.** -/
theorem king_shape_production_via_universal : KingShapeProduction := by
  intro k
  obtain ⟨P, hdeg, h1, h2⟩ := universal_shape_production kingLattice k
  refine ⟨P, hdeg, fun n hn => ?_, fun n hn => ?_⟩
  · have hh := h1 n hn
    rw [T_king] at hh
    simpa using hh
  · have hh := h2 n hn
    rw [T_king] at hh
    simpa using hh

/-- **`Shape.lean`'s `production_int_all`, from the universal theorem.** -/
theorem king_production_int_all_via_universal : KingProductionIntAll := by
  intro k P hdeg hP
  refine universal_production_int_all kingLattice hdeg fun n hn => ?_
  rw [T_king]
  simpa using hP n hn

-- **GD-3, statement level.** The four transcriptions are `Shape.lean`'s own
-- types (each is inhabited term-mode by the original king proof in
-- `Universal/AbstractShape.lean`); the universal route inhabits the very same
-- types. The generic-vs-king statement diff is empty.
example : KingShapeD := king_shape_d_via_universal
example : KingShape := king_shape_via_universal
example : KingShapeProduction := king_shape_production_via_universal
example : KingProductionIntAll := king_production_int_all_via_universal

/-! ## The generic enumerator at the king lattice -/

/-- The king lattice has reach `1`. -/
lemma M_king_le : kingLattice.M ≤ 1 :=
  M_le_one _ (by decide)

set_option linter.style.nativeDecide false

/-- `T(3,2) = 10`, via the **generic** enumerator (`results/triangle.txt`). -/
theorem T_king_3_2 : T kingLattice 3 2 = 10 := by
  rw [← Tc_eq_T_of_M_le_one M_king_le]; native_decide

/-- `T(4,3) = 55`, via the generic enumerator (`results/triangle.txt`). -/
theorem T_king_4_3 : T kingLattice 4 3 = 55 := by
  rw [← Tc_eq_T_of_M_le_one M_king_le]; native_decide

/-- `T(5,4) = 240`, via the generic enumerator (`results/triangle.txt`) — not a
pin point; the pinned `P₁` predicts `(125 − 45)·3^1 = 240`. -/
theorem T_king_5_4 : T kingLattice 5 4 = 240 := by
  rw [← Tc_eq_T_of_M_le_one M_king_le]; native_decide

/-- A006770 at `n = 3`: `1 + 10 + 9 = 20` fixed polyplets. -/
theorem king_rowSum_3 : rowSum kingLattice 3 3 = 20 := by native_decide

/-- A006770 at `n = 4`: `1 + 27 + 55 + 27 = 110` fixed polyplets. -/
theorem king_rowSum_4 : rowSum kingLattice 4 4 = 110 := by native_decide

/-- A006770 at `n = 5`: `1 + 68 + 248 + 240 + 81 = 638` fixed polyplets. -/
theorem king_rowSum_5 : rowSum kingLattice 5 5 = 638 := by native_decide

/-- The generic and king `T` agree at `(3,2)` — by the definitional bridge
`T_king`, not by computation. The genuine two-enumerator cross-check is
`T_king_3_2` (generic `Tc`, its own native leaf) against the king tree's
`Polyplets.T_3_2` (king `Tc`, a distinct native leaf): both are forced to
the same `results/triangle.txt` constant `10` or the build fails. -/
theorem gd3_Tc_agrees : T kingLattice 3 2 = Polyplets.T 3 2 := T_king 3 2

/-! ## `P₁` through the generic pin -/

/-- The king lattice's level-1 production polynomial, written as
`Universal/{Square,Hex}.lean` write theirs. -/
noncomputable def kingP1 : Polynomial ℚ := C 25 * X - C 45

/-- `P₁` has degree `≤ 1`. -/
lemma kingP1_deg : kingP1.natDegree ≤ 1 := by
  refine le_trans (natDegree_sub_le _ _) (max_le ?_ ?_)
  · exact le_trans (natDegree_C_mul_le _ _) (by simp)
  · simp

/-- `P₁` evaluated. -/
lemma kingP1_eval (x : ℚ) : kingP1.eval x = 25 * x - 45 := by simp [kingP1]

/-- **The generic pin reproduces `Pin.lean`'s polynomial.** -/
theorem kingP1_eq_Pp1 : kingP1 = Polyplets.Pp1 := by
  refine Polynomial.funext fun x => ?_
  rw [kingP1_eval, Polyplets.Pp1, Polyplets.prodPoly_eval]
  norm_num
  ring

/-- Guard at the first pin point: `P₁(3) = T(3,2) · b^1 = 30`. -/
lemma king_guard_3 : kingP1.eval (3 : ℚ) = ((T kingLattice 3 2 * kingLattice.b ^ 1 : ℕ) : ℚ) := by
  rw [kingP1_eval, T_king_3_2, b_king]; norm_num

/-- Guard at the second pin point: `P₁(4) = T(4,3) · b^0 = 55`. -/
lemma king_guard_4 : kingP1.eval (4 : ℚ) = ((T kingLattice 4 3 * kingLattice.b ^ 0 : ℕ) : ℚ) := by
  rw [kingP1_eval, T_king_4_3, b_king]; norm_num

/-- **The king `P₁`, pinned through the universal machinery.** -/
theorem king_P1_pinned_via_universal : ∀ n : ℕ, 2 * 1 + 1 ≤ n →
    (T kingLattice n (n - 1) : ℚ)
      = kingP1.eval (n : ℚ) * (kingLattice.b : ℚ) ^ ((n : ℤ) - 1 - 3 * 1) := by
  refine pin kingLattice 1 kingP1 kingP1_deg ({3, 4} : Finset ℕ) (by decide) ?_ ?_
  · intro n hn; fin_cases hn <;> norm_num
  · intro n hn
    fin_cases hn
    · simp only [show (3 - 1 : ℕ) = 2 from rfl, show (3 * 1 + 1 - 3 : ℕ) = 1 from rfl]
      exact king_guard_3
    · simp only [show (4 - 1 : ℕ) = 3 from rfl, show (3 * 1 + 1 - 4 : ℕ) = 0 from rfl]
      exact king_guard_4

/-- `Pin.lean`'s `P1_pinned` statement, transcribed. Inhabited twice below. -/
def KingP1Pinned : Prop := ∀ n : ℕ, 2 * 1 + 1 ≤ n →
  (Polyplets.T n (n - 1) : ℚ) = Polyplets.Pp1.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 1)

-- The original: `Pin.lean`'s proof inhabits it term-mode.
example : KingP1Pinned := Polyplets.P1_pinned

/-- **GD-3 for `P₁`**: the universal route inhabits the same statement. -/
theorem king_P1_pinned_king_form : KingP1Pinned := by
  intro n hn
  have h := king_P1_pinned_via_universal n hn
  rw [T_king, kingP1_eq_Pp1] at h
  simpa using h

/-- The human form, re-derived: `T(n, n−1) = (25n − 45)·3^(n−4)` for `n ≥ 3`
(`Pin.lean`'s `P1_closed`). -/
theorem king_P1_closed_via_universal (n : ℕ) (hn : 3 ≤ n) :
    (Polyplets.T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := king_P1_pinned_via_universal n (by omega)
  rw [T_king] at h
  simp only [b_king, kingP1_eval, Nat.cast_ofNat] at h
  rw [h]
  ring_nf

/-- The out-of-sample corroboration, enforcing: the numeral from the anchor
`T_king_5_4` meets the pinned law in one statement, so the `example` fails if
either side drifts. -/
example : ((240 : ℕ) : ℚ) = (25 * (5 : ℚ) - 45) * (3 : ℚ) ^ ((5 : ℤ) - 4) := by
  rw [← T_king_5_4, T_king]
  exact_mod_cast king_P1_closed_via_universal 5 (by norm_num)

/-! ## Axiom audit -/

#print axioms king_shape_d_via_universal
#print axioms king_shape_via_universal
#print axioms king_shape_production_via_universal
#print axioms king_production_int_all_via_universal
#print axioms T_king_3_2
#print axioms T_king_4_3
#print axioms T_king_5_4
#print axioms king_rowSum_3
#print axioms king_rowSum_4
#print axioms king_rowSum_5
#print axioms kingP1_eq_Pp1
#print axioms king_P1_pinned_via_universal
#print axioms king_P1_pinned_king_form
#print axioms king_P1_closed_via_universal

end Polyplets.Universal
