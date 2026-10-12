/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Order.Lattice.Nat
import Polyplets.Defs

/-!
# Bounds on polyplets: finiteness, the height range, `a` as a row sum

`Defs.lean` defines `IsPolyplet`, the two counts `a n = (polyplets n).ncard`
and `T n H = (heightClass n H).ncard`, and the bounding-box `height`. This
file proves what makes those counts genuine cardinalities and ties them
together:

* `IsPolyplet.x_le` / `IsPolyplet.y_le` : every cell of a polyplet of `n`
  cells has coordinates `≤ n - 1`, both from one anchored-projection lemma
  (`card_bound_of_anchored`: king paths skip no value, so `0, 1, …, proj p`
  are all attained);
* `polyplets_finite` / `heightClass_finite` : hence both sets are finite, and
  `T_eq_toFinset_card` reads `T` as a `Finset.card`;
* `IsPolyplet.height_le` and `height_eq_iff` : `1 ≤ height S ≤ n`, and
  `height S = H` says exactly that every `y ≤ H - 1` with some `y = H - 1`
  (`mem_heightClass_iff_rows` is the five-clause form of membership in
  `heightClass n H`);
* `a_eq_sum` : `a n = ∑ H ∈ Finset.Icc 1 n, T n H`, the polyplets of `n`
  cells partitioned by height;
* `strip_sum_le_a` : the paper's §9 strip-capture lower bound.
-/

namespace Polyplets

open scoped BigOperators

/-! ## The height of a polyplet -/

/-- **`height S = H` in two clauses.** On a polyplet, `height S = H` says
exactly that every `y ≤ H - 1` and some `y = H - 1`: the y-coordinates attain
their maximum at `H - 1`. -/
lemma height_eq_iff {n H : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) :
    height S = H ↔ (∀ p ∈ S, p.2 ≤ (H : ℤ) - 1) ∧ ∃ p ∈ S, p.2 = (H : ℤ) - 1 := by
  have hnn : ∀ p ∈ S, 0 ≤ p.2 := hS.anchored.y_nonneg
  obtain ⟨p0, hp0S, -⟩ := hS.anchored.x_zero
  obtain ⟨pm, hpmS, hpm⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0S⟩ (fun p : ℤ × ℤ => p.2.toNat)
  constructor
  · intro hh
    simp only [height] at hh
    refine ⟨fun p hp => ?_, pm, hpmS, ?_⟩
    · have hle : p.2.toNat ≤ S.sup (fun p : ℤ × ℤ => p.2.toNat) :=
        Finset.le_sup (f := fun p : ℤ × ℤ => p.2.toNat) hp
      have := hnn p hp
      omega
    · have := hnn pm hpmS
      omega
  · rintro ⟨hub, pmax, hmaxS, hmax⟩
    have hsuple : S.sup (fun p : ℤ × ℤ => p.2.toNat) ≤ H - 1 :=
      Finset.sup_le fun p hp => by
        have h1 := hnn p hp
        have h2 := hub p hp
        omega
    have hlesup : pmax.2.toNat ≤ S.sup (fun p : ℤ × ℤ => p.2.toNat) :=
      Finset.le_sup (f := fun p : ℤ × ℤ => p.2.toNat) hmaxS
    have hnnmax := hnn pmax hmaxS
    simp only [height]
    omega

/-- Membership in `heightClass n H`, spelled out: a polyplet of `n` cells with
no cell above row `H - 1` and a cell on it. -/
lemma mem_heightClass_iff_rows {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ heightClass n H ↔
      IsPolyplet n S ∧ (∀ p ∈ S, p.2 ≤ (H : ℤ) - 1) ∧ ∃ p ∈ S, p.2 = (H : ℤ) - 1 := by
  rw [mem_heightClass]
  exact ⟨fun ⟨h, hh⟩ => ⟨h, (height_eq_iff h).mp hh⟩,
    fun ⟨h, hh⟩ => ⟨h, (height_eq_iff h).mpr hh⟩⟩

/-! ## Uniform coordinate bounds -/

/-- **Anchored projections are bounded by the cell count.** If a `1`-Lipschitz
coordinate `proj` vanishes somewhere on a king-connected `S`, then it is at most
`n - 1` everywhere on `S`: the values `0, 1, …, proj p` are *all* attained (king
paths skip no value, `RowLocal.exists_proj_eq_of_cross`), so `S` has at least
`proj p + 1` distinct `proj`-fibers. Stated once for both coordinates — and, as
the proof shows, without
needing `proj` to be nonnegative on `S`. -/
lemma card_bound_of_anchored {n : ℕ} {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ}
    (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ q r : ℤ × ℤ, kingAdj q r → |proj q - proj r| ≤ 1)
    (hcard : S.card = n) (hconn : KingConnected S) (hzero : ∃ q ∈ S, proj q = 0)
    (hp : p ∈ S) : proj p ≤ (n : ℤ) - 1 := by
  obtain ⟨p0, hp0S, hp0⟩ := hzero
  have hsub : Finset.Icc (0 : ℤ) (proj p) ⊆ S.image proj := by
    intro j hj
    rw [Finset.mem_Icc] at hj
    rw [Finset.mem_image]
    rcases eq_or_lt_of_le hj.2 with hjm | hjm
    · exact ⟨p, hp, hjm.symm⟩
    · obtain ⟨c, hcS, hcj⟩ :=
        RowLocal.exists_proj_eq_of_cross (k := j) proj hlip (hconn p0 hp0S p hp) (by omega)
          (by omega)
      exact ⟨c, hcS, hcj⟩
  have hbd : (Finset.Icc (0 : ℤ) (proj p)).card ≤ n := by
    calc (Finset.Icc (0 : ℤ) (proj p)).card
        ≤ (S.image proj).card := Finset.card_le_card hsub
      _ ≤ S.card := Finset.card_image_le
      _ = n := hcard
  rw [Int.card_Icc] at hbd
  simp only [sub_zero] at hbd
  rw [Int.toNat_le] at hbd
  omega

/-- **Uniform width bound**: every cell of a polyplet of `n` cells has
`x ≤ n - 1`. -/
lemma IsPolyplet.x_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S)
    {p : ℤ × ℤ} (hp : p ∈ S) : p.1 ≤ (n : ℤ) - 1 :=
  card_bound_of_anchored Prod.fst (fun _ _ h => h.2.1) hS.card hS.conn hS.anchored.x_zero hp

/-- **Uniform height bound**: the row analogue of `IsPolyplet.x_le`. -/
lemma IsPolyplet.y_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S)
    {p : ℤ × ℤ} (hp : p ∈ S) : p.2 ≤ (n : ℤ) - 1 :=
  card_bound_of_anchored Prod.snd (fun _ _ h => h.2.2) hS.card hS.conn hS.anchored.y_zero hp

/-- **Height range.** A polyplet of `n` cells has height between `1` and `n`:
no row of its bounding box can be skipped, so its height is at most its cell
count. -/
lemma IsPolyplet.height_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) :
    height S ≤ n := by
  obtain ⟨p0, hp0S, -⟩ := hS.anchored.x_zero
  obtain ⟨pm, hpmS, hpm⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0S⟩ (fun p : ℤ × ℤ => p.2.toNat)
  have hy := hS.y_le hpmS
  have hnn := hS.anchored.y_nonneg pm hpmS
  simp only [height]
  omega

/-- **Finiteness.** Every polyplet of `n` cells lives in the box
`[0, n-1] × [0, n-1]`, so there are only finitely many — hence `a n` is a
genuine cardinality, not `ncard`'s junk `0`. -/
lemma polyplets_finite (n : ℕ) : (polyplets n).Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc ((0 : ℤ), (0 : ℤ)) ((n : ℤ) - 1, (n : ℤ) - 1))).finite_toSet
  intro S hS
  have hS : IsPolyplet n S := hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  exact ⟨⟨hS.anchored.x_nonneg p hpS, hS.anchored.y_nonneg p hpS⟩, hS.x_le hpS, hS.y_le hpS⟩

/-- The height classes are finite too: each is a subset of `polyplets n`. -/
lemma heightClass_finite (n H : ℕ) : (heightClass n H).Finite :=
  (polyplets_finite n).subset fun _ hS => hS.1

/-- **`T` is a genuine cardinality.** With finiteness in hand, `T n H` is the
`Finset.card` of the materialized height class — the concrete object any
counting or bijection argument works against. -/
theorem T_eq_toFinset_card (n H : ℕ) :
    T n H = (heightClass_finite n H).toFinset.card := by
  rw [T, Set.ncard_eq_toFinset_card _ (heightClass_finite n H)]

/-! ## The sum identity -/

/-- **`a` is the row sum of the height triangle.** `height` sorts the
polyplets of `n` cells into the height classes counted by `T n H`
(`Finset.card_eq_sum_card_fiberwise`), and only heights `1 … n` occur
(`one_le_height`, `IsPolyplet.height_le`). Unconditional: at `n = 0` both
sides are `0` (no polyplet has `0` cells, and `Finset.Icc 1 0` is empty). -/
theorem a_eq_sum (n : ℕ) :
    a n = ∑ H ∈ Finset.Icc 1 n, T n H := by
  classical
  rw [a, Set.ncard_eq_toFinset_card _ (polyplets_finite n),
    Finset.card_eq_sum_card_fiberwise (f := height) (t := Finset.Icc 1 n)
      fun S hS => by
        rw [Finset.mem_coe, Set.Finite.mem_toFinset] at hS
        exact Finset.mem_coe.mpr <| Finset.mem_Icc.mpr ⟨one_le_height S, hS.height_le⟩]
  refine Finset.sum_congr rfl fun H _ => ?_
  rw [T_eq_toFinset_card]
  congr 1
  ext S
  simp [mem_heightClass, mem_polyplets]

/-! ## The §9 strip-capture lower bound -/

/-- **The paper's §9 generating-function lower bound.** The heights `1 … 10`
whose column generating functions are known exactly contribute a rigorous lower
bound for `a n`: they are a sub-collection of the height classes, and every
class is counted with a nonnegative multiplicity. -/
theorem strip_sum_le_a (n : ℕ) (hn : 10 ≤ n) :
    ∑ H ∈ Finset.Icc 1 10, T n H ≤ a n := by
  rw [a_eq_sum n]
  exact Finset.sum_le_sum_of_subset (Finset.Icc_subset_Icc_right hn)

end Polyplets
