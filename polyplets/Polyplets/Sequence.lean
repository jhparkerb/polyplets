/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Compute

/-!
# The sequence `a n`: fixed polyplets of `n` cells (A006770)

`Defs.lean` counts polyplets *resolved by height* (`T n H`). The paper's
headline object is the height-blind total `a n = Σ_H T n H`, the sequence
A006770. This file introduces it.

`a n` is defined the same way `T n H` is — as the `Set.ncard` of the set of
origin-anchored canonical representatives, here with the height clauses of
`IsCanonical` dropped (`IsCanonicalAnimal`). Keeping the definition parallel
to `T`'s means downstream work (symmetry counting, the Fekete ladder) can act
on the *set* directly rather than on a sum of `T`s.

The bridge between the two is the **height function**
`heightOf S = (sup of the y-coordinates) + 1`, for which

* `isCanonical_iff` : `IsCanonical n H S ↔ IsCanonicalAnimal n S ∧ heightOf S = H`
* `heightOf_le` / `one_le_heightOf` : `1 ≤ heightOf S ≤ n` on canonical animals

so that the canonical animals of size `n` partition, by height, into the `n`
height classes counted by `T n 1, …, T n n`:

* `a_eq_sum` : `a n = ∑ H ∈ Finset.Icc 1 n, T n H`.

The upper height bound is the row analogue of `Finite.lean`'s `canonical_x_le`;
both are instances of one anchored-projection lemma (`card_bound_of_anchored`).

Finally a computable twin `ac n = ∑ H ∈ Finset.Icc 1 n, Tc n H` with
`ac_eq_a`, giving `native_decide` anchors `a 1 … a 6` against the banked row
sums of `results/triangle.txt`, and the paper's §9 strip-capture lower bound
`strip_sum_le_a`.

**Build cost.** Everything through `a 5` elaborates in ~21 s. The `a 6`
anchor alone costs ~700 s (measured 2026-07-30: whole module 724 s, ~5.9 GB
peak RSS) because `ac 6` forces `Tc 6 6`, a `C(36,6) ≈ 1.9M`-subset
enumeration that `Compute.lean`'s cost note had ruled out of that module's
budget. If that turns out to sit awkwardly on the rebuild path, `a_6` is the
one declaration to relocate — the `ComputeBridge.lean` treatment of the slow
`T 6 4` / `T 6 5` anchors.
-/

namespace Polyplets

open scoped BigOperators

/-! ## The height-blind canonical set -/

/-- `S` is the origin-anchored representative of a fixed polyplet of `n` cells,
of any height: `n` cells, king-connected, with minimum x- and y-coordinate `0`.
This is `IsCanonical` with the two height clauses dropped. -/
def IsCanonicalAnimal (n : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = n ∧ KingConnected S ∧
  (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧
  (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0)

/-- `a n`: the number of fixed polyplets of `n` cells (A006770), i.e. the number
of origin-anchored canonical representatives of any height. As with `T`,
`Set.ncard` returns the junk value `0` on infinite sets; `canonicalAnimal_finite`
shows that never happens. Note `a 0 = 0`: the empty set fails the `∃ p ∈ S`
anchoring clauses, so every statement below carries `1 ≤ n`. -/
noncomputable def a (n : ℕ) : ℕ := {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S}.ncard

/-! ## The height function -/

/-- The bounding-box height of a cell set: one more than the largest
y-coordinate. Taken through `Int.toNat` so that it is a total `ℕ`-valued
function needing no nonemptiness hypothesis; on a canonical animal every
y-coordinate is `≥ 0`, so no information is lost. -/
def heightOf (S : Finset (ℤ × ℤ)) : ℕ := S.sup (fun p => p.2.toNat) + 1

/-- Heights are positive, definitionally. -/
lemma one_le_heightOf (S : Finset (ℤ × ℤ)) : 1 ≤ heightOf S := Nat.le_add_left 1 _

/-- **`IsCanonical` is `IsCanonicalAnimal` at a pinned height.** The two extra
clauses of `IsCanonical` — every `y ≤ H - 1`, some `y = H - 1` — say exactly
that the y-coordinates attain their maximum at `H - 1`, which is
`heightOf S = H`. Both sides force `S` to be nonempty (via the `x = 0` anchor),
so no size hypothesis is needed; at `n = 0` both sides are simply false. -/
lemma isCanonical_iff (n H : ℕ) (S : Finset (ℤ × ℤ)) :
    IsCanonical n H S ↔ IsCanonicalAnimal n S ∧ heightOf S = H := by
  constructor
  · intro hS
    obtain ⟨pmax, hmaxS, hmax⟩ := hS.2.2.2.2.2.2.2
    have hnn : ∀ p ∈ S, 0 ≤ p.2 := hS.2.2.2.2.1
    have hub : ∀ p ∈ S, p.2 ≤ (H : ℤ) - 1 := hS.2.2.2.2.2.2.1
    refine ⟨⟨hS.1, hS.2.1, hS.2.2.1, hS.2.2.2.1, hnn, hS.2.2.2.2.2.1⟩, ?_⟩
    have hsuple : S.sup (fun p : ℤ × ℤ => p.2.toNat) ≤ H - 1 :=
      Finset.sup_le fun p hp => by
        have h1 := hnn p hp
        have h2 := hub p hp
        omega
    have hlesup : pmax.2.toNat ≤ S.sup (fun p : ℤ × ℤ => p.2.toNat) :=
      Finset.le_sup (f := fun p : ℤ × ℤ => p.2.toNat) hmaxS
    have hnnmax := hnn pmax hmaxS
    simp only [heightOf]
    omega
  · rintro ⟨hA, hh⟩
    obtain ⟨p0, hp0S, -⟩ := hA.2.2.2.1
    obtain ⟨pm, hpmS, hpm⟩ :=
      Finset.exists_mem_eq_sup S ⟨p0, hp0S⟩ (fun p : ℤ × ℤ => p.2.toNat)
    have hnn : ∀ p ∈ S, 0 ≤ p.2 := hA.2.2.2.2.1
    simp only [heightOf] at hh
    refine ⟨hA.1, hA.2.1, hA.2.2.1, hA.2.2.2.1, hnn, hA.2.2.2.2.2, ?_, pm, hpmS, ?_⟩
    · intro p hp
      have hle : p.2.toNat ≤ S.sup (fun p : ℤ × ℤ => p.2.toNat) :=
        Finset.le_sup (f := fun p : ℤ × ℤ => p.2.toNat) hp
      have := hnn p hp
      omega
    · have := hnn pm hpmS
      omega

/-! ## Uniform coordinate bounds -/

/-- **Anchored projections are bounded by the cell count.** If a `1`-Lipschitz
coordinate `proj` vanishes somewhere on a king-connected `S`, then it is at most
`n - 1` everywhere on `S`: the values `0, 1, …, proj p` are *all* attained (king
paths skip no value, `exists_proj_eq_of_cross`), so `S` has at least
`proj p + 1` distinct `proj`-fibres. This is `Finite.lean`'s `canonical_x_le`
argument, stated once for both coordinates — and, as the proof shows, without
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
        exists_proj_eq_of_cross (k := j) proj hlip (hconn p0 hp0S p hp) (by omega) (by omega)
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

/-- **Uniform width bound** for canonical animals (the `IsCanonical` version is
`canonical_x_le`). -/
lemma canonicalAnimal_x_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S)
    {p : ℤ × ℤ} (hp : p ∈ S) : p.1 ≤ (n : ℤ) - 1 :=
  card_bound_of_anchored Prod.fst (fun _ _ h => h.2.1) hS.1 hS.2.1 hS.2.2.2.1 hp

/-- **Uniform height bound** for canonical animals: the row analogue of
`canonicalAnimal_x_le`. Where `IsCanonical` *assumes* a height bound, a
canonical animal earns one from connectivity. -/
lemma canonicalAnimal_y_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S)
    {p : ℤ × ℤ} (hp : p ∈ S) : p.2 ≤ (n : ℤ) - 1 :=
  card_bound_of_anchored Prod.snd (fun _ _ h => h.2.2) hS.1 hS.2.1 hS.2.2.2.2.2 hp

/-- **Height range.** A canonical animal of `n` cells has height between `1`
and `n`: no row of its bounding box can be skipped, so its height is at most
its cell count. -/
lemma heightOf_le {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    heightOf S ≤ n := by
  obtain ⟨p0, hp0S, -⟩ := hS.2.2.2.1
  obtain ⟨pm, hpmS, hpm⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0S⟩ (fun p : ℤ × ℤ => p.2.toNat)
  have hy := canonicalAnimal_y_le hS hpmS
  have hnn := hS.2.2.2.2.1 pm hpmS
  simp only [heightOf]
  omega

/-- **Finiteness.** Every canonical animal of `n` cells lives in the box
`[0, n-1] × [0, n-1]`, so there are only finitely many — hence `a n` is a
genuine cardinality, not `ncard`'s junk `0`. -/
lemma canonicalAnimal_finite (n : ℕ) :
    {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc ((0 : ℤ), (0 : ℤ)) ((n : ℤ) - 1, (n : ℤ) - 1))).finite_toSet
  intro S hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  exact ⟨⟨hS.2.2.1 p hpS, hS.2.2.2.2.1 p hpS⟩,
    canonicalAnimal_x_le hS hpS, canonicalAnimal_y_le hS hpS⟩

/-! ## The sum identity -/

/-- **`a` is the row sum of the height triangle.** `heightOf` sorts the
canonical animals of `n` cells into height classes; each class is exactly the
canonical set counted by `T n H` (`isCanonical_iff`), the classes are disjoint
because `heightOf` is a function, and only heights `1 … n` occur
(`one_le_heightOf`, `heightOf_le`). The `1 ≤ n` hypothesis is kept for the
downstream interface but is not needed: at `n = 0` both sides are `0`
(no canonical animal has `0` cells, and `Finset.Icc 1 0` is empty). -/
theorem a_eq_sum (n : ℕ) (_hn : 1 ≤ n) :
    a n = ∑ H ∈ Finset.Icc 1 n, T n H := by
  have hbi : (canonicalAnimal_finite n).toFinset
      = (Finset.Icc 1 n).biUnion fun H => (canonical_finite n H).toFinset := by
    ext S
    simp only [Set.Finite.mem_toFinset, Set.mem_setOf_eq, Finset.mem_biUnion,
      Finset.mem_Icc]
    constructor
    · intro hS
      exact ⟨heightOf S, ⟨one_le_heightOf S, heightOf_le hS⟩,
        (isCanonical_iff n (heightOf S) S).mpr ⟨hS, rfl⟩⟩
    · rintro ⟨H, -, hSH⟩
      exact ((isCanonical_iff n H S).mp hSH).1
  have hdisj : ∀ x ∈ Finset.Icc 1 n, ∀ y ∈ Finset.Icc 1 n, x ≠ y →
      Disjoint ((canonical_finite n x).toFinset) ((canonical_finite n y).toFinset) := by
    intro x _ y _ hxy
    rw [Finset.disjoint_left]
    intro S hSx hSy
    rw [Set.Finite.mem_toFinset] at hSx hSy
    exact hxy ((((isCanonical_iff n x S).mp hSx).2).symm.trans
      (((isCanonical_iff n y S).mp hSy).2))
  rw [a, Set.ncard_eq_toFinset_card _ (canonicalAnimal_finite n), hbi,
    Finset.card_biUnion hdisj]
  exact Finset.sum_congr rfl fun H _ => (T_eq_toFinset_card n H).symm

/-! ## Computable twin and banked anchors -/

/-- Computable counterpart of `a`: the row sum of the computable triangle `Tc`.
Brute force (`Tc` enumerates subsets of the box), so useful only for small `n`. -/
def ac (n : ℕ) : ℕ := ∑ H ∈ Finset.Icc 1 n, Tc n H

/-- The computable twin agrees with `a`, termwise by `Tc_eq_T` and in total by
`a_eq_sum`. -/
theorem ac_eq_a (n : ℕ) (hn : 1 ≤ n) : ac n = a n := by
  rw [ac, a_eq_sum n hn]
  exact Finset.sum_congr rfl fun H _ => Tc_eq_T n H

/-! The right-hand sides are the row sums of `results/triangle.txt`
(provenance `results/ns_a40/PROVENANCE.md`): `a n = 1, 4, 20, 110, 638, 3832`
for `n = 1 … 6`. `native_decide` is the approved route for this validation
section (PLAN.md, scope interview 2026-07-20). -/

set_option linter.style.nativeDecide false

/-- `a 1 = 1`: the single cell. -/
theorem a_1 : a 1 = 1 := by rw [← ac_eq_a 1 (by norm_num)]; native_decide

/-- `a 2 = 4`: the horizontal, vertical and two diagonal king dominoes. -/
theorem a_2 : a 2 = 4 := by rw [← ac_eq_a 2 (by norm_num)]; native_decide

/-- `a 3 = 20` (banked row sum, `results/triangle.txt`). -/
theorem a_3 : a 3 = 20 := by rw [← ac_eq_a 3 (by norm_num)]; native_decide

/-- `a 4 = 110` (banked row sum, `results/triangle.txt`). -/
theorem a_4 : a 4 = 110 := by rw [← ac_eq_a 4 (by norm_num)]; native_decide

/-- `a 5 = 638` (banked row sum, `results/triangle.txt`). -/
theorem a_5 : a 5 = 638 := by rw [← ac_eq_a 5 (by norm_num)]; native_decide

/-- `a 6 = 3832` (banked row sum, `results/triangle.txt`). This anchor is the
expensive one: it needs the whole `n = 6` row of `Tc`, including `Tc 6 6` — a
`C(36,6) ≈ 1.9M`-subset enumeration that `Compute.lean`'s cost note explicitly
ruled out of that module's budget. Measured ~700 s on its own (see the module
header). `a 7` would need `Tc 7 7`, `C(49,7) ≈ 86M` subsets — roughly 44 times
this one, so the anchors stop at `n = 6`. -/
theorem a_6 : a 6 = 3832 := by rw [← ac_eq_a 6 (by norm_num)]; native_decide

/-! ## The §9 strip-capture lower bound -/

/-- **The paper's §9 generating-function lower bound.** The heights `1 … 10`
whose column generating functions are known exactly contribute a rigorous lower
bound for `a n`: they are a sub-collection of the height classes, and every
class is counted with a nonnegative multiplicity. -/
theorem strip_sum_le_a (n : ℕ) (hn : 10 ≤ n) :
    ∑ H ∈ Finset.Icc 1 10, T n H ≤ a n := by
  rw [a_eq_sum n (by omega)]
  exact Finset.sum_le_sum_of_subset (Finset.Icc_subset_Icc_right hn)

/-! ## Axiom audit

Plain `#print axioms` here; the `#guard_msgs`-wrapped versions are integrated
into the campaign audit point by the orchestrator. `a_eq_sum` must carry the
standard three; the anchors add exactly `Lean.ofReduceBool`. -/

#print axioms a_eq_sum
#print axioms a_6

end Polyplets
