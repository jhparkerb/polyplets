/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.Graph

/-!
# Finiteness of the canonical set

`{S | IsCanonical L n H S}` is a finite set of `Finset`s, so `T L n H` (defined
via `Set.ncard`) is a genuine cardinality.

This is `Finite.lean` generically, with **one lemma that does not carry over
verbatim** — flagged here because it is the only such place in the geometric
port.

* The row crossing lemmas (`exists_proj_eq_of_cross`, `exists_y_eq_of_cross`,
  `exists_adj_cross_of_reflTransGen`) are stated exactly as in the king file,
  for any `1`-Lipschitz coordinate, and are applied only at `Prod.snd`; they
  use nothing but `adj_abs_dy_le`.
* The king file's **column** specialization `exists_x_eq_of_cross` is FALSE for
  general `L`: with `D = {-2, 0, 2}` the connected animal `{(0,0), (2,1)}`
  leaves column `1` empty, so a path can skip a column and the king width bound
  `p.1 ≤ n - 1` fails outright. It is replaced by the reach bound
  `|p.1 - q.1| ≤ M · (walk length)` plus "a path has at most `card - 1` steps",
  giving `canonical_x_le : p.1 ≤ M · (n - 1)`. At `M = 1` this is the king
  statement. Nothing downstream reads the width bound quantitatively — it is
  consumed only as "some box contains every canonical set" — so the change is
  confined to this file.
-/

namespace Polyplets.Universal

/-- **Paths don't skip a coordinate value.** For any `1`-Lipschitz coordinate
`proj`, if a path inside `S` runs from a cell with `proj ≤ k` to a cell with
`proj ≥ k+1`, then some cell of `S` sits exactly at `proj = k`. Instantiated at
`Prod.snd` for rows below; the `Prod.fst` instantiation of the king file has no
generic analogue (see the module doc). -/
lemma exists_proj_eq_of_cross {L : RowLocal} {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, Adj L a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) : ∃ c ∈ S, proj c = k := by
  revert hq
  induction h with
  | refl => intro hq; exact absurd hq (by omega)
  | @tail b c _ hbc ih =>
      intro hq
      by_cases hb : k + 1 ≤ proj b
      · exact ih hb
      · exact ⟨b, hbc.1, by have h2 := hlip b c hbc.2.2; rw [abs_le] at h2; omega⟩

/-- Row specialization of `exists_proj_eq_of_cross` (`proj = Prod.snd`). -/
lemma exists_y_eq_of_cross {L : RowLocal} {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q)
    (hp : p.2 ≤ k) (hq : k + 1 ≤ q.2) : ∃ c ∈ S, c.2 = k :=
  exists_proj_eq_of_cross Prod.snd (fun _ _ hab => adj_abs_dy_le hab) h hp hq

/-- **The crossing step is an edge.** A path from `proj ≤ k` to `proj ≥ k+1`
contains an adjacent pair `a, b ∈ S` with `proj a = k` and `proj b = k+1`. -/
lemma exists_adj_cross_of_reflTransGen {L : RowLocal} {S : Finset (ℤ × ℤ)}
    {p q : ℤ × ℤ} {k : ℤ} (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, Adj L a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) :
    ∃ a b, a ∈ S ∧ b ∈ S ∧ Adj L a b ∧ proj a = k ∧ proj b = k + 1 := by
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

/-! ## The width bound -/

/-- **Reach along a walk**: each step moves x by at most `M`, so a walk of
length `n` moves x by at most `M · n`. -/
lemma abs_dx_le_of_walk {L : RowLocal} {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (w : (graph L S).Walk p q) : |p.1 - q.1| ≤ L.M * (w.length : ℤ) := by
  induction w with
  | nil => simp
  | @cons a x c hadj w' ih =>
      have h1 : |a.1 - x.1| ≤ L.M := adj_abs_dx_le hadj.2.2
      have h2 : |a.1 - c.1| ≤ |a.1 - x.1| + |x.1 - c.1| := abs_sub_le _ _ _
      rw [SimpleGraph.Walk.length_cons]
      push_cast
      have : L.M * ((w'.length : ℤ) + 1) = L.M + L.M * (w'.length : ℤ) := by ring
      omega

/-- **x-spread of a connected set**: any two cells of an `L`-connected `S` differ
in x by at most `M · (card − 1)`. The path joining them has no repeated vertex,
so at most `card − 1` steps, each of reach `M`.

At `M = 1` this is the king file's `connected_sub_x_le`; the king proof (every
intermediate column is occupied) is unavailable in general. -/
lemma conn_abs_sub_x_le {L : RowLocal} {S : Finset (ℤ × ℤ)} (hconn : Conn L S)
    {a p : ℤ × ℤ} (ha : a ∈ S) (hp : p ∈ S) :
    |p.1 - a.1| ≤ L.M * ((S.card : ℤ) - 1) := by
  classical
  rw [conn_iff_reachable] at hconn
  obtain ⟨w⟩ := hconn a ha p hp
  set v := w.toPath with hv
  have hpath : v.val.IsPath := v.2
  have hsub : v.val.support.toFinset ⊆ S := by
    intro c hc
    rw [List.mem_toFinset] at hc
    exact mem_of_mem_walk_support ha v.val c hc
  have hcard : v.val.support.toFinset.card ≤ S.card := Finset.card_le_card hsub
  rw [List.toFinset_card_of_nodup hpath.support_nodup,
    SimpleGraph.Walk.length_support] at hcard
  have hb := abs_dx_le_of_walk v.val
  have hmul : L.M * (v.val.length : ℤ) ≤ L.M * ((S.card : ℤ) - 1) := by
    refine mul_le_mul_of_nonneg_left ?_ L.M_nonneg
    have : (v.val.length : ℤ) + 1 ≤ (S.card : ℤ) := by exact_mod_cast hcard
    omega
  rw [abs_sub_comm] at hb
  omega

/-- **x-spread bound at the origin.** In an `L`-connected set containing the
origin, every cell's `|x|` is at most `M · (card − 1)`. This is what makes the
enumeration windows of `Universal/Weights.lean` finite. -/
lemma conn_abs_x_le {L : RowLocal} {S : Finset (ℤ × ℤ)} (hconn : Conn L S)
    (h0 : ((0 : ℤ), (0 : ℤ)) ∈ S) {p : ℤ × ℤ} (hp : p ∈ S) :
    |p.1| ≤ L.M * ((S.card : ℤ) - 1) := by
  have h := conn_abs_sub_x_le hconn h0 hp
  simpa using h

/-- **Uniform width bound.** In a canonical `L`-animal of `n` cells, every
cell's x-coordinate is at most `M · (n − 1)`. -/
lemma canonical_x_le {L : RowLocal} {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hS : IsCanonical L n H S) {p : ℤ × ℤ} (hp : p ∈ S) : p.1 ≤ L.M * ((n : ℤ) - 1) := by
  obtain ⟨p0, hp0S, hp0⟩ := hS.2.2.2.1
  have h := conn_abs_sub_x_le hS.2.1 hp0S hp
  rw [hS.1, hp0, sub_zero] at h
  have := le_abs_self p.1
  omega

/-- **Finiteness.** `{S | IsCanonical L n H S}` is contained in the powerset of
the finite box `[0, M(n-1)] × [0, H-1]`, hence finite. -/
lemma canonical_finite (L : RowLocal) (n H : ℕ) :
    {S : Finset (ℤ × ℤ) | IsCanonical L n H S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset
      (Finset.Icc ((0 : ℤ), (0 : ℤ)) (L.M * ((n : ℤ) - 1), (H : ℤ) - 1))).finite_toSet
  intro S hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
  · exact hS.2.2.1 p hpS
  · exact hS.2.2.2.2.1 p hpS
  · exact canonical_x_le hS hpS
  · exact hS.2.2.2.2.2.2.1 p hpS

/-- **`T` is a genuine cardinality.** -/
theorem T_eq_toFinset_card (L : RowLocal) (n H : ℕ) :
    T L n H = (canonical_finite L n H).toFinset.card := by
  rw [T, Set.ncard_eq_toFinset_card _ (canonical_finite L n H)]

end Polyplets.Universal
