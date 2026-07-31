/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.Separation

/-!
# Row profile of a canonical `L`-animal

The two row-profile facts the peeling bijections consume, ported verbatim from
`RowProfile.lean`: every row of the bounding box is occupied, because the
y-projection of a connected set has no gaps (`exists_y_eq_of_cross`, which uses
only `|Δrow| ≤ 1`).

The king file's `k = 1` pigeonhole (`row_profile_one_doubled` and downstream) is
not needed by the peeling recursion and is not ported.
-/

namespace Polyplets.Universal

/-- **Every row in range is occupied.** For `0 ≤ y ≤ H-1`, some cell of a
canonical `S` has that row: the anchored `y = 0` and `y = H-1` cells bracket
`y`, and a path between them cannot skip it. -/
lemma canonical_row_occupied {L : RowLocal} {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hS : IsCanonical L n H S) {y0 : ℤ} (h0 : 0 ≤ y0) (hH : y0 ≤ (H : ℤ) - 1) :
    ∃ c ∈ S, c.2 = y0 := by
  obtain ⟨pmin, hminS, hmin⟩ := hS.2.2.2.2.2.1
  obtain ⟨pmax, hmaxS, hmax⟩ := hS.2.2.2.2.2.2.2
  rcases eq_or_lt_of_le hH with hy | hy
  · exact ⟨pmax, hmaxS, by omega⟩
  · have hconn := hS.2.1 pmin hminS pmax hmaxS
    exact exists_y_eq_of_cross hconn (by omega) (by omega)

/-- **Each row's fiber is nonempty.** -/
lemma canonical_fiber_nonempty {L : RowLocal} {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hS : IsCanonical L n H S) {y : ℤ} (h0 : 0 ≤ y) (hH : y ≤ (H : ℤ) - 1) :
    (S.filter (fun c => c.2 = y)).Nonempty := by
  obtain ⟨c, hcS, hc⟩ := canonical_row_occupied hS h0 hH
  exact ⟨c, by rw [Finset.mem_filter]; exact ⟨hcS, hc⟩⟩

end Polyplets.Universal
