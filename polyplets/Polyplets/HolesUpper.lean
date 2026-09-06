/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Holes

/-!
# Holes, upper bound: the parity count, the maximization, and the moat bound

This file is the second half of the paper's Theorem 2. `Polyplets.Holes` builds
the extremal family and proves the lower bound; here we bound *every* single-hole
king animal from above.

Throughout, the diagonal coordinates are `u = x + y` and `v = x - y`; the hole of
an animal `S` is `enclosed S`, and its *window* is the smallest `ha × hm`
rectangle in `(u, v)` containing it.

## The three ingredients

* **(I′) parity count** (`card_le_of_diag_window`): a cell set whose `(u, v)`
  coordinates lie in an `ha × hm` window has at most `⌈ha·hm/2⌉` cells, because
  only one parity class of the `(u, v)` rectangle is populated. Unconditional.
* **Maximization** (`area_max`): `⌈ha·hm/2⌉ ≤ ⌊(n−2)²/8 + ½⌋` whenever
  `ha + hm + 2 ≤ n` — integer AM–GM. Unconditional.
* **(II′) the moat bound** (`MoatBound`): an `n`-cell single-hole animal whose
  hole has window `ha × hm` satisfies `n ≥ ha + hm + 2`. This is the
  discrete-Jordan step of `results/subclasses.md` (the moat-cycle argument),
  and it is **assumed here as a named hypothesis**: the paper proof runs through
  a winding number for a closed king-walk, machinery Mathlib does not have. See
  the discussion below for what *is* proved unconditionally and why the cheap
  substitutes fail.

`maxhole_upper` and `maxhole` are therefore conditional on `MoatBound`; the
lower bound `maxhole_lower` of `Polyplets.Holes` is unconditional.

## Unconditional fragments of (II′)

`mem_or_enclosed_of_rookAdj` (sealing), the four `moat_*` lemmas and
`moat_beyond_window` give the partial progress recorded in
`results/subclasses.md`: the animal reaches one diagonal step beyond the hole
on all four sides, so its `u`-extent is at least `ha + 2` and its `v`-extent at
least `hm + 2`. As the proof doc records, this yields only
`n ≥ max(ha, hm) + 2`-grade bounds: a king step changes `|u| + |v|` by at most
`2`, so *span* arguments lose a factor of two against the target sum
`ha + hm + 2`, and the loss is real (a diagonal path spans a large window with
few cells but encloses nothing). Closing the gap needs the enclosing property,
i.e. a closed curve, not a spanning one.

Two combinatorial substitutes were tried and both fail for that reason.

1. *Disjoint escape corridors* (a Menger-style route avoiding winding): charge
   one animal cell to each anti-diagonal level `u = ℓ` of the hole's range. The
   underlying claim — every such level carries an animal cell — is **false**,
   and false on the extremal family itself: the ring of the `3 × 3` box has
   `n = 8 = ha + hm + 2` yet no cell at `u = 0` or `u = 2`, because all four
   walls sit at odd `u`, leaving the even levels of the hole's range empty.
   (Measured exhaustively, `experiments/maxhole_review_checks.py`: the claim
   fails on 63,112 of the 104,727 single-hole animals with `n ≤ 9`; `≥ 2` per
   level fails on 95,252.) A king step may change `u` by `2`, so the moat can
   skip levels.
2. *Gap charging*: the repaired claim — every `u`-gap `{ℓ, ℓ+1}` for
   `u0 - 1 ≤ ℓ ≤ u1` carries `≥ 2` animal cells, and likewise for `v` — does
   hold (0 violations on the same 104,727 animals), but it cannot reach the
   target: it holds and is still too weak, so it is refuted by counting, not
   by measurement.
   Each cell lies in exactly two `u`-gaps and two `v`-gaps, so the demand
   `2(ha+1) + 2(hm+1)` only gives `4·n ≥ 2(ha + hm + 2)`, i.e. half the bound.
   The ring is tight for `MoatBound`, so the factor of two is not slack in the
   demand side: it can only be recovered by charging each cell `2` rather than
   `4`, which is exactly the statement that the relevant cells are the vertices
   of a *closed* walk (two incident steps, each paying `|Δu| + |Δv| ≤ 2`).

Mathlib has neither Menger's theorem nor any digital-topology/Jordan-curve
material to build the walk on (it does have Hall's theorem, which is not enough
by itself), so (II′) stays a hypothesis here. Beyond the paper proof and the
3,927-animal machine check of `results/subclasses.md`, (II′) as stated —
with this file's exact `enclosed`/`SingleHole` definitions — was checked
exhaustively against all 104,727 single-hole king animals with `n ≤ 9`
(0 violations, tight on the box rings; `experiments/maxhole_review_checks.py`,
2026-07-31 adversarial review).
-/

namespace Polyplets

/-! ### (I′) The parity count -/

/-- **(I′) parity count.** A finite cell set whose diagonal coordinates
`u = x + y` and `v = x - y` lie in a window of extents `ha` and `hm` has at most
`⌈ha·hm/2⌉ = (ha·hm + 1) / 2` cells: the cells of `ℤ × ℤ` biject with the
`u ≡ v [MOD 2]` points of the `(u, v)` plane, and such a window contains at most
that many of them. -/
theorem card_le_of_diag_window (R : Finset (ℤ × ℤ)) (u0 v0 : ℤ) (ha hm : ℕ)
    (h : ∀ p ∈ R, u0 ≤ p.1 + p.2 ∧ p.1 + p.2 < u0 + ha ∧
      v0 ≤ p.1 - p.2 ∧ p.1 - p.2 < v0 + hm) :
    R.card ≤ (ha * hm + 1) / 2 := by
  classical
  rcases R.eq_empty_or_nonempty with rfl | hne
  · simp
  obtain ⟨p0, hp0⟩ := hne
  obtain ⟨hb1, hb2, hb3, hb4⟩ := h p0 hp0
  have hha : 1 ≤ ha := by
    by_contra hcon
    have : ha = 0 := by omega
    simp only [this, Nat.cast_zero, add_zero] at hb2
    omega
  have hhm : 1 ≤ hm := by
    by_contra hcon
    have : hm = 0 := by omega
    simp only [this, Nat.cast_zero, add_zero] at hb4
    omega
  rcases Int.even_or_odd (u0 + v0) with ⟨k, hk⟩ | ⟨k, hk⟩
  · -- Aligned corner: the window *is* a `dbox`.
    have hsub : R ⊆ dbox (k, k - v0) ha hm := by
      intro p hp
      obtain ⟨h1, h2, h3, h4⟩ := h p hp
      rw [mem_dbox]
      refine ⟨?_, ?_, ?_, ?_⟩ <;> dsimp only <;> omega
    calc R.card ≤ (dbox (k, k - v0) ha hm).card := Finset.card_le_card hsub
      _ = (ha * hm + 1) / 2 := dbox_card _ ha hm
  · -- Unaligned corner: split off the bottom `v`-level, which is a `1`-wide box.
    have hsplit :
        (R.filter (fun p => p.1 - p.2 = v0)).card
          + (R.filter (fun p => ¬ (p.1 - p.2 = v0))).card = R.card :=
      Finset.card_filter_add_card_filter_not _
    have h1 : (R.filter (fun p => p.1 - p.2 = v0)).card ≤ ((ha - 1) * 1 + 1) / 2 := by
      have hsub : R.filter (fun p => p.1 - p.2 = v0) ⊆ dbox (k + 1, k + 1 - v0) (ha - 1) 1 := by
        intro p hp
        rw [Finset.mem_filter] at hp
        obtain ⟨hpR, hpv⟩ := hp
        obtain ⟨g1, g2, g3, g4⟩ := h p hpR
        rw [mem_dbox]
        refine ⟨?_, ?_, ?_, ?_⟩ <;> dsimp only <;>
          [skip; rw [Nat.cast_sub hha]; skip; skip] <;> push_cast <;> omega
      calc (R.filter (fun p => p.1 - p.2 = v0)).card
          ≤ (dbox (k + 1, k + 1 - v0) (ha - 1) 1).card := Finset.card_le_card hsub
        _ = ((ha - 1) * 1 + 1) / 2 := dbox_card _ _ _
    have h2 : (R.filter (fun p => ¬ (p.1 - p.2 = v0))).card ≤ (ha * (hm - 1) + 1) / 2 := by
      have hsub : R.filter (fun p => ¬ (p.1 - p.2 = v0)) ⊆ dbox (k + 1, k - v0) ha (hm - 1) := by
        intro p hp
        rw [Finset.mem_filter] at hp
        obtain ⟨hpR, hpv⟩ := hp
        obtain ⟨g1, g2, g3, g4⟩ := h p hpR
        rw [mem_dbox]
        refine ⟨?_, ?_, ?_, ?_⟩ <;> dsimp only <;>
          [skip; skip; skip; rw [Nat.cast_sub hhm]] <;> push_cast <;> omega
      calc (R.filter (fun p => ¬ (p.1 - p.2 = v0))).card
          ≤ (dbox (k + 1, k - v0) ha (hm - 1)).card := Finset.card_le_card hsub
        _ = (ha * (hm - 1) + 1) / 2 := dbox_card _ _ _
    have e1 : (ha - 1) * 1 + 1 = ha := by omega
    have e2 : ha * hm = ha * (hm - 1) + ha := by
      obtain ⟨t, rfl⟩ : ∃ t, hm = t + 1 := ⟨hm - 1, by omega⟩
      simp [Nat.mul_succ]
    rw [e1] at h1
    rw [e2]
    set P := ha * (hm - 1) with hP
    omega

/-! ### The maximization -/

private lemma half_le_eighth {P T : ℕ} (h : 4 * P ≤ T) : (P + 1) / 2 ≤ (T + 4) / 8 := by
  omega

/-- **The maximization.** With `ha + hm + 2 ≤ n`, the parity count of an
`ha × hm` window never exceeds the extremal area `⌊(n−2)²/8 + ½⌋`. Integer
AM–GM: `4·ha·hm ≤ (ha + hm)² ≤ (n − 2)²`. -/
theorem area_max (n ha hm : ℕ) (h : ha + hm + 2 ≤ n) :
    (ha * hm + 1) / 2 ≤ ((n - 2) ^ 2 + 4) / 8 := by
  have hsq : 4 * (ha * hm) ≤ (ha + hm) ^ 2 := by
    have h' : (4 : ℤ) * ((ha : ℤ) * hm) ≤ ((ha : ℤ) + hm) ^ 2 := by
      nlinarith [sq_nonneg ((ha : ℤ) - hm)]
    exact_mod_cast h'
  have hmono : (ha + hm) ^ 2 ≤ (n - 2) ^ 2 := Nat.pow_le_pow_left (by omega) 2
  exact half_le_eighth (le_trans hsq hmono)

/-! ### Sealing: the unconditional fragments of (II′) -/

/-- **Sealing.** A rook neighbour of an enclosed cell is either an animal cell or
is itself enclosed: otherwise the hole would leak to infinity. -/
lemma mem_or_enclosed_of_rookAdj {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (hp : p ∈ enclosed S) (hadj : rookAdj p q) : q ∈ S ∨ q ∈ enclosed S := by
  by_cases hq : q ∈ S
  · exact Or.inl hq
  · refine Or.inr ⟨hq, Set.Finite.subset hp.2 ?_⟩
    intro r hr
    exact Relation.ReflTransGen.head ⟨hp.1, hq, hadj⟩ hr

/-- The animal reaches the level `u + 1` above a `u`-maximal hole cell, in *both*
of that cell's upward rook neighbours. -/
lemma moat_above {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ enclosed S)
    (hmax : ∀ q ∈ enclosed S, q.1 + q.2 ≤ p.1 + p.2) :
    (p.1 + 1, p.2) ∈ S ∧ (p.1, p.2 + 1) ∈ S := by
  constructor
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_horiz p (Or.inl rfl)) with h | h
    · exact h
    · have := hmax _ h; simp only at this; omega
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_vert p (Or.inl rfl)) with h | h
    · exact h
    · have := hmax _ h; simp only at this; omega

/-- The animal reaches the level `u - 1` below a `u`-minimal hole cell. -/
lemma moat_below {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ enclosed S)
    (hmin : ∀ q ∈ enclosed S, p.1 + p.2 ≤ q.1 + q.2) :
    (p.1 + -1, p.2) ∈ S ∧ (p.1, p.2 + -1) ∈ S := by
  constructor
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_horiz p (Or.inr rfl)) with h | h
    · exact h
    · have := hmin _ h; simp only at this; omega
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_vert p (Or.inr rfl)) with h | h
    · exact h
    · have := hmin _ h; simp only at this; omega

/-- The animal reaches the level `v + 1` beyond a `v`-maximal hole cell. -/
lemma moat_vabove {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ enclosed S)
    (hmax : ∀ q ∈ enclosed S, q.1 - q.2 ≤ p.1 - p.2) :
    (p.1 + 1, p.2) ∈ S ∧ (p.1, p.2 + -1) ∈ S := by
  constructor
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_horiz p (Or.inl rfl)) with h | h
    · exact h
    · have := hmax _ h; simp only at this; omega
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_vert p (Or.inr rfl)) with h | h
    · exact h
    · have := hmax _ h; simp only at this; omega

/-- The animal reaches the level `v - 1` beyond a `v`-minimal hole cell. -/
lemma moat_vbelow {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ enclosed S)
    (hmin : ∀ q ∈ enclosed S, p.1 - p.2 ≤ q.1 - q.2) :
    (p.1 + -1, p.2) ∈ S ∧ (p.1, p.2 + 1) ∈ S := by
  constructor
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_horiz p (Or.inr rfl)) with h | h
    · exact h
    · have := hmin _ h; simp only at this; omega
  · rcases mem_or_enclosed_of_rookAdj hp (rookAdj_vert p (Or.inl rfl)) with h | h
    · exact h
    · have := hmin _ h; simp only at this; omega

/-- **The moat lies one diagonal step beyond the hole on all four sides** — the
unconditional fragment of (II′) recorded in `results/subclasses.md`. If the
hole fills a tight `ha × hm` window then the animal has cells at `u = u0 - 1`,
`u = u0 + ha`, `v = v0 - 1` and `v = v0 + hm`.

This is strictly weaker than `MoatBound`: it bounds the animal's *spans*
(`u`-extent `≥ ha + 2`, `v`-extent `≥ hm + 2`) but not its cardinality by the
*sum* `ha + hm + 2`, since a king step changes `|u| + |v|` by up to `2` and a
spanning animal need not close up. -/
theorem moat_beyond_window {S : Finset (ℤ × ℤ)} {u0 v0 : ℤ} {ha hm : ℕ}
    (hwin : ∀ p ∈ enclosed S, u0 ≤ p.1 + p.2 ∧ p.1 + p.2 < u0 + ha ∧
      v0 ≤ p.1 - p.2 ∧ p.1 - p.2 < v0 + hm)
    (hu0 : ∃ p ∈ enclosed S, p.1 + p.2 = u0)
    (hu1 : ∃ p ∈ enclosed S, p.1 + p.2 = u0 + ha - 1)
    (hv0 : ∃ p ∈ enclosed S, p.1 - p.2 = v0)
    (hv1 : ∃ p ∈ enclosed S, p.1 - p.2 = v0 + hm - 1) :
    (∃ s ∈ S, s.1 + s.2 = u0 - 1) ∧ (∃ s ∈ S, s.1 + s.2 = u0 + ha) ∧
      (∃ s ∈ S, s.1 - s.2 = v0 - 1) ∧ (∃ s ∈ S, s.1 - s.2 = v0 + hm) := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · obtain ⟨p, hp, hfp⟩ := hu0
    have hmin : ∀ q ∈ enclosed S, p.1 + p.2 ≤ q.1 + q.2 := fun q hq => by
      have := (hwin q hq).1; omega
    exact ⟨_, (moat_below hp hmin).1, by simp only; omega⟩
  · obtain ⟨p, hp, hfp⟩ := hu1
    have hmax : ∀ q ∈ enclosed S, q.1 + q.2 ≤ p.1 + p.2 := fun q hq => by
      have := (hwin q hq).2.1; omega
    exact ⟨_, (moat_above hp hmax).1, by simp only; omega⟩
  · obtain ⟨p, hp, hfp⟩ := hv0
    have hmin : ∀ q ∈ enclosed S, p.1 - p.2 ≤ q.1 - q.2 := fun q hq => by
      have := (hwin q hq).2.2.1; omega
    exact ⟨_, (moat_vbelow hp hmin).1, by simp only; omega⟩
  · obtain ⟨p, hp, hfp⟩ := hv1
    have hmax : ∀ q ∈ enclosed S, q.1 - q.2 ≤ p.1 - p.2 := fun q hq => by
      have := (hwin q hq).2.2.2; omega
    exact ⟨_, (moat_vabove hp hmax).1, by simp only; omega⟩

/-! ### The hole is finite -/

/-- A cell with a one-way *vertical* escape ray in the complement of `S` has an
infinite complement component (the vertical twin of `component_infinite_of_ray`). -/
lemma component_infinite_of_ray_vert (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) {e : ℤ}
    (he : e = 1 ∨ e = -1) (h : ∀ k : ℕ, ((p.1, p.2 + e * k) : ℤ × ℤ) ∉ S) :
    (compComponent S p).Infinite := by
  have hmem : ∀ k : ℕ, ((p.1, p.2 + e * k) : ℤ × ℤ) ∈ compComponent S p := by
    intro k
    induction k with
    | zero => simpa [compComponent] using Relation.ReflTransGen.refl
    | succ k ihk =>
        have hcast : ((p.1, p.2 + e * ((k + 1 : ℕ) : ℤ)) : ℤ × ℤ)
            = (p.1, (p.2 + e * (k : ℤ)) + e) := by push_cast; ring_nf
        rw [hcast]
        exact Relation.ReflTransGen.tail ihk ⟨h k, by rw [← hcast]; exact h (k + 1),
          rookAdj_vert (p.1, p.2 + e * (k : ℤ)) he⟩
  refine Set.infinite_of_injective_forall_mem
    (f := fun k : ℕ => ((p.1, p.2 + e * k) : ℤ × ℤ)) ?_ hmem
  intro k l hkl
  simp only [Prod.mk.injEq] at hkl
  have hne : e ≠ 0 := by rcases he with rfl | rfl <;> norm_num
  have h1 : e * (k : ℤ) = e * (l : ℤ) := by linarith [hkl.2]
  exact Nat.cast_injective (mul_left_cancel₀ hne h1)

/-- The enclosed cells of any finite animal lie inside its bounding box, so the
hole is finite. -/
lemma enclosed_finite (S : Finset (ℤ × ℤ)) : (enclosed S).Finite := by
  classical
  obtain ⟨B, hB⟩ := (S.image fun p => max |p.1| |p.2|).exists_le
  have hSB : ∀ p ∈ S, |p.1| ≤ B ∧ |p.2| ≤ B := by
    intro p hp
    have h := hB _ (Finset.mem_image_of_mem _ hp)
    exact ⟨le_trans (le_max_left _ _) h, le_trans (le_max_right _ _) h⟩
  refine Set.Finite.subset (Set.finite_Icc ((-B, -B) : ℤ × ℤ) (B, B)) ?_
  rintro p ⟨hpS, hfin⟩
  simp only [Set.mem_Icc]
  refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
  · by_contra hcon
    refine (component_infinite_of_ray S p (e := -1) (Or.inr rfl) fun k hk => ?_) hfin
    have h1 : |p.1 + -1 * (k : ℤ)| ≤ B := (hSB _ hk).1
    rw [abs_le] at h1
    omega
  · by_contra hcon
    refine (component_infinite_of_ray_vert S p (e := -1) (Or.inr rfl) fun k hk => ?_) hfin
    have h1 : |p.2 + -1 * (k : ℤ)| ≤ B := (hSB _ hk).2
    rw [abs_le] at h1
    omega
  · by_contra hcon
    refine (component_infinite_of_ray S p (e := 1) (Or.inl rfl) fun k hk => ?_) hfin
    have h1 : |p.1 + 1 * (k : ℤ)| ≤ B := (hSB _ hk).1
    rw [abs_le] at h1
    omega
  · by_contra hcon
    refine (component_infinite_of_ray_vert S p (e := 1) (Or.inl rfl) fun k hk => ?_) hfin
    have h1 : |p.2 + 1 * (k : ℤ)| ≤ B := (hSB _ hk).2
    rw [abs_le] at h1
    omega

/-! ### The window of a hole -/

/-- Every nonempty finite cell set has a tight window in any coordinate: an
interval `[c, c + m)` of length `m` containing all its values and attaining both
ends. -/
lemma exists_window (R : Finset (ℤ × ℤ)) (hR : R.Nonempty) (f : ℤ × ℤ → ℤ) :
    ∃ (c : ℤ) (m : ℕ), (∀ p ∈ R, c ≤ f p ∧ f p < c + m) ∧
      (∃ p ∈ R, f p = c) ∧ (∃ p ∈ R, f p = c + m - 1) := by
  classical
  have hne : (R.image f).Nonempty := hR.image f
  set lo := (R.image f).min' hne with hlo
  set hi := (R.image f).max' hne with hhi
  have hle : lo ≤ hi := Finset.min'_le _ _ ((R.image f).max'_mem hne)
  have hcast : (((hi - lo + 1).toNat : ℕ) : ℤ) = hi - lo + 1 := Int.toNat_of_nonneg (by omega)
  refine ⟨lo, (hi - lo + 1).toNat, ?_, ?_, ?_⟩
  · intro p hp
    have h1 : lo ≤ f p := Finset.min'_le _ _ (Finset.mem_image_of_mem f hp)
    have h2 : f p ≤ hi := Finset.le_max' _ _ (Finset.mem_image_of_mem f hp)
    rw [hcast]
    omega
  · obtain ⟨p, hp, hfp⟩ := Finset.mem_image.1 ((R.image f).min'_mem hne)
    exact ⟨p, hp, hfp⟩
  · obtain ⟨p, hp, hfp⟩ := Finset.mem_image.1 ((R.image f).max'_mem hne)
    refine ⟨p, hp, ?_⟩
    rw [hcast, hfp]
    omega

/-! ### (II′) as a named hypothesis, and the two-sided theorem -/

/-- **(II′), the moat bound** — the discrete-Jordan step of the paper's proof of
Theorem 2, stated as a named hypothesis.

If the hole of an `n`-cell single-hole king animal fits in a tight `ha × hm`
window in the diagonal coordinates `u = x + y`, `v = x - y` (tight: all four
sides are touched), then `n ≥ ha + hm + 2`.

`results/subclasses.md` proves this by tracing the outer contour of the hole
into a closed king-walk in the animal, erasing it to a simple cycle with nonzero
winding number about every hole cell, and counting `Σ|Δu| ≥ 2(ha+1)`,
`Σ|Δv| ≥ 2(hm+1)` against `|Δu| + |Δv| ≤ 2` per king step. It was
machine-checked on 3,927 single-hole king animals with no failures, and it is
tight on every box ring of `Polyplets.Holes` (`(ringAnimal a b).card = a + b + 2`
with window `a × b`). Formalizing it needs digital topology (contours, winding
numbers for king walks) that Mathlib does not provide. -/
def MoatBound : Prop :=
  ∀ (S : Finset (ℤ × ℤ)) (u0 v0 : ℤ) (ha hm : ℕ),
    KingConnected S → SingleHole S →
    (∀ p ∈ enclosed S, u0 ≤ p.1 + p.2 ∧ p.1 + p.2 < u0 + ha ∧
      v0 ≤ p.1 - p.2 ∧ p.1 - p.2 < v0 + hm) →
    (∃ p ∈ enclosed S, p.1 + p.2 = u0) →
    (∃ p ∈ enclosed S, p.1 + p.2 = u0 + ha - 1) →
    (∃ p ∈ enclosed S, p.1 - p.2 = v0) →
    (∃ p ∈ enclosed S, p.1 - p.2 = v0 + hm - 1) →
    ha + hm + 2 ≤ S.card

/-- **Theorem 2, upper bound** (conditional on `MoatBound`). Every `n`-cell
king-connected single-hole animal encloses at most `⌊(n−2)²/8 + ½⌋` cells. -/
theorem maxhole_upper (hmoat : MoatBound) {S : Finset (ℤ × ℤ)} {n : ℕ} (hn : S.card = n)
    (hconn : KingConnected S) (hhole : SingleHole S) :
    (enclosed S).ncard ≤ ((n - 2) ^ 2 + 4) / 8 := by
  classical
  have hfin := enclosed_finite S
  have hmemR : ∀ p : ℤ × ℤ, p ∈ hfin.toFinset ↔ p ∈ enclosed S := fun _ => hfin.mem_toFinset
  have hRne : hfin.toFinset.Nonempty := by
    obtain ⟨p, hp⟩ := hhole.1
    exact ⟨p, (hmemR p).mpr hp⟩
  obtain ⟨u0, ha, hub, hu0, hu1⟩ := exists_window _ hRne (fun p => p.1 + p.2)
  obtain ⟨v0, hm, hvb, hv0, hv1⟩ := exists_window _ hRne (fun p => p.1 - p.2)
  have hwin : ∀ p ∈ enclosed S, u0 ≤ p.1 + p.2 ∧ p.1 + p.2 < u0 + ha ∧
      v0 ≤ p.1 - p.2 ∧ p.1 - p.2 < v0 + hm := by
    intro p hp
    have h1 := hub p ((hmemR p).mpr hp)
    have h2 := hvb p ((hmemR p).mpr hp)
    exact ⟨h1.1, h1.2, h2.1, h2.2⟩
  have hmoat' : ha + hm + 2 ≤ n := by
    rw [← hn]
    refine hmoat S u0 v0 ha hm hconn hhole hwin ?_ ?_ ?_ ?_
    · obtain ⟨p, hp, hfp⟩ := hu0; exact ⟨p, (hmemR p).mp hp, hfp⟩
    · obtain ⟨p, hp, hfp⟩ := hu1; exact ⟨p, (hmemR p).mp hp, hfp⟩
    · obtain ⟨p, hp, hfp⟩ := hv0; exact ⟨p, (hmemR p).mp hp, hfp⟩
    · obtain ⟨p, hp, hfp⟩ := hv1; exact ⟨p, (hmemR p).mp hp, hfp⟩
  have hcardR : hfin.toFinset.card ≤ (ha * hm + 1) / 2 := by
    refine card_le_of_diag_window _ u0 v0 ha hm fun p hp => hwin p ((hmemR p).mp hp)
  rw [Set.ncard_eq_toFinset_card _ hfin]
  exact le_trans hcardR (area_max n ha hm hmoat')

/-- **Theorem 2** (conditional on `MoatBound`). For `n ≥ 4` the maximum area
enclosed by an `n`-cell king animal with a single hole is exactly
`⌊(n−2)²/8 + ½⌋ = ((n−2)² + 4) / 8`; the lower half is the unconditional
`maxhole_lower`. -/
theorem maxhole (hmoat : MoatBound) (n : ℕ) (hn : 4 ≤ n) :
    IsGreatest {A | ∃ S : Finset (ℤ × ℤ), S.card = n ∧ KingConnected S ∧ SingleHole S ∧
      (enclosed S).ncard = A} (((n - 2) ^ 2 + 4) / 8) := by
  constructor
  · obtain ⟨S, h1, h2, h3, h4⟩ := maxhole_lower n hn
    exact ⟨S, h1, h2, h3, h4⟩
  · rintro A ⟨S, h1, h2, h3, rfl⟩
    exact maxhole_upper hmoat h1 h2 h3

/-! ### Sanity gates

The parity count is tight on the extremal family: the `4 × 4` box hole has
window `4 × 4` and `(4 * 4 + 1) / 2 = 8` cells, and its ring has
`4 + 4 + 2 = 10` cells — exactly the moat bound, so `MoatBound` has no slack. -/

example : (boxHole 4 4).card = 8 := by decide
example : (ringAnimal 4 4).card = 10 := by decide

/-- The `4 × 4` box hole touches all four sides of its `4 × 4` window, so the
window of `enclosed (ringAnimal 4 4)` is exactly `4 × 4`. -/
theorem boxHole_window_four :
    (∀ p ∈ boxHole 4 4, (0 : ℤ) ≤ p.1 + p.2 ∧ p.1 + p.2 < 4 ∧
        (0 : ℤ) ≤ p.1 - p.2 ∧ p.1 - p.2 < 4) ∧
      ((0, 0) : ℤ × ℤ) ∈ boxHole 4 4 ∧ ((3, 0) : ℤ × ℤ) ∈ boxHole 4 4 := by
  refine ⟨fun p hp => ?_, ?_, ?_⟩
  · rw [mem_boxHole] at hp; exact_mod_cast hp
  · rw [mem_boxHole]; norm_num
  · rw [mem_boxHole]; norm_num

/-! ### Axiom audit -/

#print axioms card_le_of_diag_window
#print axioms area_max
#print axioms mem_or_enclosed_of_rookAdj
#print axioms moat_above
#print axioms moat_beyond_window
#print axioms enclosed_finite
#print axioms exists_window
#print axioms maxhole_upper
#print axioms maxhole
#print axioms boxHole_window_four

end Polyplets
