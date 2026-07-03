/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Defs

/-!
# Finiteness of the canonical set

Step (a) of the diagonal-count infrastructure: `{S | IsCanonical n H S}` is a
finite set of `Finset`s, so `T n H` (defined via `Set.ncard`) is a genuine
cardinality rather than the junk `0` that `ncard` returns on infinite sets.

The one nontrivial ingredient is a **uniform width bound**: every canonical `S`
lies in the box `[0, n-1] × [0, H-1]`. The height bounds are handed to us by
`IsCanonical`; the width bound `p.1 ≤ n-1` is the king-connectivity fact
`exists_x_eq_of_cross` — a king step moves x by at most one, so a path from the
`x = 0` cell to any cell plants a cell at every intermediate x-value, forcing
`n ≥ p.1 + 1` distinct columns.
-/

namespace Polyplets

/-- **King paths don't skip a coordinate value.** For any `1`-Lipschitz
coordinate `proj` (king steps move it by at most one), if a king path inside `S`
runs from a cell with `proj ≤ k` to a cell with `proj ≥ k+1`, then some cell of
`S` sits exactly at `proj = k`: the step crossing the `k`/`k+1` boundary lands
on it. Instantiated at `Prod.fst`/`Prod.snd` for columns and rows below. -/
lemma exists_proj_eq_of_cross {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, kingAdj a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) : ∃ c ∈ S, proj c = k := by
  revert hq
  induction h with
  | refl => intro hq; exact absurd hq (by omega)
  | @tail b c _ hbc ih =>
      intro hq
      by_cases hb : k + 1 ≤ proj b
      · exact ih hb
      · exact ⟨b, hbc.1, by have h2 := hlip b c hbc.2.2; rw [abs_le] at h2; omega⟩

/-- Column specialization of `exists_proj_eq_of_cross` (`proj = Prod.fst`). -/
lemma exists_x_eq_of_cross {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : p.1 ≤ k) (hq : k + 1 ≤ q.1) : ∃ c ∈ S, c.1 = k :=
  exists_proj_eq_of_cross Prod.fst (fun _ _ hab => hab.2.1) h hp hq

/-- Row specialization of `exists_proj_eq_of_cross` (`proj = Prod.snd`). -/
lemma exists_y_eq_of_cross {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : p.2 ≤ k) (hq : k + 1 ≤ q.2) : ∃ c ∈ S, c.2 = k :=
  exists_proj_eq_of_cross Prod.snd (fun _ _ hab => hab.2.2) h hp hq

/-- **The crossing step is a king edge.** Strengthening `exists_proj_eq_of_cross`
to return the whole boundary-crossing *edge*: a king path from `proj ≤ k` to
`proj ≥ k+1` contains a king-adjacent pair `a, b ∈ S` with `proj a = k` and
`proj b = k+1` (the step can only move `proj` by one, so it lands squarely on
the boundary). This is the forward half of the row-connectivity picture. -/
lemma exists_adj_cross_of_reflTransGen {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, kingAdj a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) :
    ∃ a b, a ∈ S ∧ b ∈ S ∧ kingAdj a b ∧ proj a = k ∧ proj b = k + 1 := by
  revert hq
  induction h with
  | refl => intro hq; exact absurd hq (by omega)
  | @tail b c _ hbc ih =>
      intro hq
      by_cases hb : k + 1 ≤ proj b
      · exact ih hb
      · have h2 := hlip b c hbc.2.2
        rw [abs_le] at h2
        exact ⟨b, c, hbc.1, hbc.2.1, hbc.2.2, by omega, by omega⟩

/-- **Uniform width bound.** In a canonical polyplet of `n` cells, every cell's
x-coordinate is at most `n - 1`: the columns `0, 1, …, p.1` are all occupied
(no skipped columns, by `exists_x_eq_of_cross` from the anchored `x = 0` cell),
so there are at least `p.1 + 1` distinct columns, hence `p.1 + 1 ≤ n`. -/
lemma canonical_x_le {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S)
    {p : ℤ × ℤ} (hp : p ∈ S) : p.1 ≤ (n : ℤ) - 1 := by
  obtain ⟨p0, hp0S, hp0⟩ := hS.2.2.2.1
  have hsub : Finset.Icc (0 : ℤ) p.1 ⊆ S.image Prod.fst := by
    intro j hj
    rw [Finset.mem_Icc] at hj
    rw [Finset.mem_image]
    rcases eq_or_lt_of_le hj.2 with hjm | hjm
    · exact ⟨p, hp, hjm.symm⟩
    · have hconn := hS.2.1 p0 hp0S p hp
      have hcross : ∃ c ∈ S, c.1 = j :=
        exists_x_eq_of_cross hconn (by omega) (by omega)
      obtain ⟨c, hcS, hcj⟩ := hcross
      exact ⟨c, hcS, hcj⟩
  have hcard : (Finset.Icc (0 : ℤ) p.1).card ≤ n := by
    calc (Finset.Icc (0 : ℤ) p.1).card
        ≤ (S.image Prod.fst).card := Finset.card_le_card hsub
      _ ≤ S.card := Finset.card_image_le
      _ = n := hS.1
  rw [Int.card_Icc] at hcard
  simp only [sub_zero] at hcard
  rw [Int.toNat_le] at hcard
  omega

/-- **Step (a): finiteness.** `{S | IsCanonical n H S}` is contained in the
powerset of the finite box `[0, n-1] × [0, H-1]`, hence finite. -/
lemma canonical_finite (n H : ℕ) :
    {S : Finset (ℤ × ℤ) | IsCanonical n H S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc ((0 : ℤ), (0 : ℤ)) ((n : ℤ) - 1, (H : ℤ) - 1))).finite_toSet
  intro S hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
  · exact hS.2.2.1 p hpS
  · exact hS.2.2.2.2.1 p hpS
  · exact canonical_x_le hS hpS
  · exact hS.2.2.2.2.2.2.1 p hpS

/-- **`T` is a genuine cardinality.** With finiteness in hand, `T n H` is the
`Finset.card` of the materialized canonical set — the concrete object any
counting/bijection argument works against. -/
theorem T_eq_toFinset_card (n H : ℕ) :
    T n H = (canonical_finite n H).toFinset.card := by
  rw [T, Set.ncard_eq_toFinset_card _ (canonical_finite n H)]

end Polyplets
