/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Finite

/-!
# Row profile of a canonical polyplet

Step (b) infrastructure for the diagonal counts. For a canonical polyplet of `n`
cells and height `H`, the **row profile** records, for each row `y`, how many
cells sit in it.

The facts proved here:
* `canonical_row_occupied` — every row `0 ≤ y ≤ H-1` contains at least one cell
  (king-connectivity: the y-projection has no gaps, `exists_y_eq_of_cross`).
* `canonical_rows_image` — the set of occupied rows is *exactly* `[0, H-1]`.
* `canonical_rows_card` — there are exactly `H` occupied rows.
* `canonical_card_eq_row_sum` — the cell count is the sum of the per-row counts.
* `canonical_fiber_nonempty` — each row's fiber is nonempty.

For the `k = 1` diagonal (`H = n - 1`) these combine to the pigeonhole that
drives step (b): `n` cells across `n - 1` occupied rows force **exactly one**
row to hold two cells and every other row exactly one (proved in
`row_profile_one_doubled`).
-/

namespace Polyplets

open scoped BigOperators

/-- **Every row in range is occupied.** For `0 ≤ y ≤ H-1`, some cell of a
canonical `S` has that row: the anchored `y=0` and `y=H-1` cells bracket `y`, and
a king path between them cannot skip it (`exists_y_eq_of_cross`). -/
lemma canonical_row_occupied {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S)
    {y0 : ℤ} (h0 : 0 ≤ y0) (hH : y0 ≤ (H : ℤ) - 1) : ∃ c ∈ S, c.2 = y0 := by
  obtain ⟨pmin, hminS, hmin⟩ := hS.2.2.2.2.2.1
  obtain ⟨pmax, hmaxS, hmax⟩ := hS.2.2.2.2.2.2.2
  rcases eq_or_lt_of_le hH with hy | hy
  · exact ⟨pmax, hmaxS, by omega⟩
  · have hconn := hS.2.1 pmin hminS pmax hmaxS
    exact exists_y_eq_of_cross hconn (by omega) (by omega)

/-- **The occupied rows are exactly `[0, H-1]`.** `⊆` is the height bound from
`IsCanonical`; `⊇` is `canonical_row_occupied`. -/
lemma canonical_rows_image {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S) :
    S.image Prod.snd = Finset.Icc (0 : ℤ) ((H : ℤ) - 1) := by
  apply Finset.Subset.antisymm
  · intro y hy
    rw [Finset.mem_image] at hy
    obtain ⟨c, hcS, rfl⟩ := hy
    rw [Finset.mem_Icc]
    exact ⟨hS.2.2.2.2.1 c hcS, hS.2.2.2.2.2.2.1 c hcS⟩
  · intro y hy
    rw [Finset.mem_Icc] at hy
    rw [Finset.mem_image]
    obtain ⟨c, hcS, hc⟩ := canonical_row_occupied hS hy.1 hy.2
    exact ⟨c, hcS, hc⟩

/-- **There are exactly `H` occupied rows.** -/
lemma canonical_rows_card {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S) :
    (S.image Prod.snd).card = H := by
  rw [canonical_rows_image hS, Int.card_Icc]
  omega

/-- **Cell count = sum of per-row counts.** Fiberwise decomposition of `S` over
its rows `[0, H-1]`. -/
lemma canonical_card_eq_row_sum {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S) :
    S.card
      = ∑ y ∈ Finset.Icc (0 : ℤ) ((H : ℤ) - 1),
          (S.filter (fun c => c.2 = y)).card := by
  apply Finset.card_eq_sum_card_fiberwise
  intro x hx
  rw [Finset.mem_coe] at hx
  rw [Finset.mem_coe, Finset.mem_Icc]
  exact ⟨hS.2.2.2.2.1 x hx, hS.2.2.2.2.2.2.1 x hx⟩

/-- **Each row's fiber is nonempty.** -/
lemma canonical_fiber_nonempty {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonical n H S)
    {y : ℤ} (h0 : 0 ≤ y) (hH : y ≤ (H : ℤ) - 1) :
    (S.filter (fun c => c.2 = y)).Nonempty := by
  obtain ⟨c, hcS, hc⟩ := canonical_row_occupied hS h0 hH
  exact ⟨c, by rw [Finset.mem_filter]; exact ⟨hcS, hc⟩⟩

/-- **Step (c), forward.** In a canonical polyplet, any two consecutive occupied
rows `t`, `t+1` are directly king-linked: some `a, b ∈ S` with `a.2 = t`,
`b.2 = t+1`, `kingAdj a b`. (King-connectivity forces an edge across the
`t`/`t+1` cut; a king edge across it lands exactly on the two rows.) The reverse
direction — reconstructing connectivity from per-row links — is deferred to the
step (e) bijection. -/
lemma canonical_consecutive_rows_linked {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hS : IsCanonical n H S) {t : ℤ} (h0 : 0 ≤ t) (hH : t + 1 ≤ (H : ℤ) - 1) :
    ∃ a b, a ∈ S ∧ b ∈ S ∧ kingAdj a b ∧ a.2 = t ∧ b.2 = t + 1 := by
  obtain ⟨pmin, hminS, hmin⟩ := hS.2.2.2.2.2.1
  obtain ⟨pmax, hmaxS, hmax⟩ := hS.2.2.2.2.2.2.2
  have hconn := hS.2.1 pmin hminS pmax hmaxS
  exact exists_adj_cross_of_reflTransGen Prod.snd (fun _ _ hab => hab.2.2)
    hconn (by omega) (by omega)

/-- A `ℕ`-valued sum over a finset equals `1` iff exactly one summand is `1` and
the rest are `0`. -/
private theorem exists_unique_of_sum_eq_one {β : Type*}
    {s : Finset β} {f : β → ℕ} (hsum : ∑ b ∈ s, f b = 1) :
    ∃ a ∈ s, f a = 1 ∧ ∀ b ∈ s, b ≠ a → f b = 0 := by
  classical
  obtain ⟨a, ha, hfa⟩ :=
    Finset.exists_ne_zero_of_sum_ne_zero (s := s) (f := f) (by omega)
  have hle : f a ≤ ∑ b ∈ s, f b := Finset.single_le_sum (fun i _ => Nat.zero_le _) ha
  refine ⟨a, ha, by omega, ?_⟩
  have hrest : ∑ b ∈ s.erase a, f b = 0 := by
    have hcomb := Finset.add_sum_erase s f ha
    omega
  intro b hb hba
  exact (Finset.sum_eq_zero_iff.mp hrest) b (Finset.mem_erase.mpr ⟨hba, hb⟩)

/-- **Step (b): exactly one doubled row.** For the `k = 1` diagonal (`H = n-1`),
a canonical polyplet of `n` cells has all `n-1` rows occupied, so `n` cells over
`n-1` rows forces exactly one row to hold two cells and every other row exactly
one. -/
theorem row_profile_one_doubled {n : ℕ} {S : Finset (ℤ × ℤ)} (hn : 2 ≤ n)
    (hS : IsCanonical n (n - 1) S) :
    ∃ y0 ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
      (S.filter (fun c => c.2 = y0)).card = 2 ∧
      ∀ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1), y ≠ y0 →
        (S.filter (fun c => c.2 = y)).card = 1 := by
  have hg1 : ∀ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
      1 ≤ (S.filter (fun c => c.2 = y)).card := by
    intro y hy
    rw [Finset.mem_Icc] at hy
    exact (canonical_fiber_nonempty hS hy.1 hy.2).card_pos
  have hcardR : (Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1)).card = n - 1 := by
    rw [← canonical_rows_image hS, canonical_rows_card hS]
  have hsum : ∑ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
      (S.filter (fun c => c.2 = y)).card = n := by
    rw [← canonical_card_eq_row_sum hS, hS.1]
  have hexc : ∑ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
      ((S.filter (fun c => c.2 = y)).card - 1) = 1 := by
    have hcongr : ∑ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
        (((S.filter (fun c => c.2 = y)).card - 1) + 1)
          = ∑ y ∈ Finset.Icc (0 : ℤ) ((↑(n - 1) : ℤ) - 1),
              (S.filter (fun c => c.2 = y)).card :=
      Finset.sum_congr rfl (fun y hy => by have := hg1 y hy; omega)
    rw [Finset.sum_add_distrib, Finset.sum_const, hcardR, smul_eq_mul, mul_one,
      hsum] at hcongr
    omega
  obtain ⟨y0, hy0R, hy0e, hrest⟩ := exists_unique_of_sum_eq_one hexc
  refine ⟨y0, hy0R, ?_, ?_⟩
  · have := hg1 y0 hy0R; omega
  · intro y hyR hy
    have hb := hrest y hyR hy
    have := hg1 y hyR
    omega

end Polyplets
