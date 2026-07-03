/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Defs

/-!
# Sanity checks for the `T` definition

Small, fully-proved values that would fail if the definition of `T` (canonical
form, height convention, connectivity) were subtly wrong. These are the
guardrails validating `Polyplets/Defs.lean` before any diagonal proof.
-/

namespace Polyplets

/-- The only 1-cell polyplet of height 1 is the single origin cell, so
`T 1 1 = 1`. This pins the height convention (`max y = H - 1`) and the
origin-anchoring simultaneously. -/
theorem T_one_one : T 1 1 = 1 := by
  have hset : {S : Finset (ℤ × ℤ) | IsCanonical 1 1 S}
      = {({(0, 0)} : Finset (ℤ × ℤ))} := by
    ext S
    simp only [Set.mem_setOf_eq, Set.mem_singleton_iff]
    constructor
    · rintro ⟨hcard, -, -, hx0, -, hy0, -, -⟩
      obtain ⟨a, rfl⟩ := Finset.card_eq_one.mp hcard
      simp only [Finset.mem_singleton, exists_eq_left] at hx0 hy0
      obtain ⟨a1, a2⟩ := a
      simp_all
    · rintro rfl
      refine ⟨Finset.card_singleton _, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
      · intro p hp q hq
        rw [Finset.mem_singleton] at hp hq
        subst hp; subst hq; exact .refl
      · intro p hp; rw [Finset.mem_singleton] at hp; subst hp; norm_num
      · exact ⟨(0, 0), by simp⟩
      · intro p hp; rw [Finset.mem_singleton] at hp; subst hp; norm_num
      · exact ⟨(0, 0), by simp⟩
      · intro p hp; rw [Finset.mem_singleton] at hp; subst hp; norm_num
      · exact ⟨(0, 0), by simp⟩
  rw [T, hset, Set.ncard_singleton]

end Polyplets
