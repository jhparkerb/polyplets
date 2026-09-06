/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalk

/-!
# Notary piece T, module 2: the walk as an iterated state function

Campaign *Notary*, piece **T** of `docs/notary-kernel-scoping.md (deleted)` — truncation
exactness. `GapWalk.lean` runs the DP on association lists aligned with
`states gmax`; comparing two caps on that representation is painful. This
module rewrites the walk as iteration of a *function* `St → ℕ`:

* `canon cap F` — the association list of `F` over `states cap`; every list
  the walk ever touches has this shape;
* `funStep cap F` — one DP step as a function transformer;
* `iter cap F l` — `l` steps of the walk from start `F`;
* `qEndF` / `bareEndF` — the end functionals on the canonical list;
* `walkAux_canon` — the emitted family triples are exactly the end
  functionals of the iterates, `l = 0 .. n − 1`.

Then the cap-comparison toolkit: sums over `states (M + k)` split into the
`states M` part plus the `k` extra gaps (`funStep_split`), the split
collapses when every extra term dies (`*_split_zero`), and two value
functions that agree wherever the functional looks give equal outputs
(`*_congr`). Nothing here mentions the walk's geometry; every proof is list
bookkeeping (`List.map_map`, `List.range_add` / induction on `k`,
`List.sum_append`, congruence of `List.map` over a common index list).
-/

namespace Polyplets
namespace GapWalk

/-! ## The canonical representation -/

/-- The association list of the value function `F` over `states cap` —
the shape of every DP list the walk touches. -/
def canon (cap : Nat) (F : St → Nat) : List (St × Nat) :=
  (states cap).map fun s => (s, F s)

/-- One walk step as a function transformer: the value landing on target
`t`, summed over all sources below the cap. -/
def funStep (cap : Nat) (F : St → Nat) (t : St) : Nat :=
  ((states cap).map fun s => F s * stepMul s.1 s.2 t.1 t.2).sum

/-- `l` walk steps from start `F`, at cap `cap`. -/
def iter (cap : Nat) (F : St → Nat) : Nat → St → Nat
  | 0 => F
  | l + 1 => funStep cap (iter cap F l)

/-- `qEnd` on the canonical list. -/
def qEndF (cap : Nat) (F : St → Nat) : Nat := qEnd (canon cap F)

/-- `bareEnd` on the canonical list. -/
def bareEndF (cap : Nat) (F : St → Nat) : Nat := bareEnd (canon cap F)

/-! ## The walk in canonical form -/

theorem mem_states (cap g : Nat) (c : Bool) :
    (g, c) ∈ states cap ↔ 1 ≤ g ∧ g ≤ cap := by
  unfold states
  simp only [List.mem_flatMap, List.mem_range, List.mem_cons, List.not_mem_nil, or_false]
  constructor
  · rintro ⟨i, hi, h | h⟩ <;> (injection h with h1 h2; omega)
  · rintro ⟨h1, h2⟩
    refine ⟨g - 1, by omega, ?_⟩
    have hg : g - 1 + 1 = g := by omega
    cases c
    · exact Or.inr (by simp [hg])
    · exact Or.inl (by simp [hg])

theorem stepDP_canon (cap : Nat) (F : St → Nat) :
    stepDP cap (canon cap F) = canon cap (funStep cap F) := by
  unfold stepDP canon funStep
  apply List.map_congr_left
  intro t _
  congr 1
  congr 1
  rw [List.map_map]
  apply List.map_congr_left
  intro s _
  rfl

/-- Shifting the start of the iteration by one step. -/
private lemma iter_succ_shift (cap : Nat) (F : St → Nat) :
    ∀ l, iter cap (funStep cap F) l = iter cap F (l + 1)
  | 0 => rfl
  | l + 1 => by
      change funStep cap (iter cap (funStep cap F) l) = funStep cap (iter cap F (l + 1))
      rw [iter_succ_shift cap F l]

/-- The families the walk emits are the end functionals of the iterates. -/
theorem walkAux_canon (n cap : Nat) (F G : St → Nat) :
    walkAux n cap (canon cap F) (canon cap G) =
      (List.range n).map fun l =>
        (qEndF cap (iter cap F l), qEndF cap (iter cap G l),
         bareEndF cap (iter cap G l)) := by
  induction n generalizing F G with
  | zero => rfl
  | succ n ih =>
    change (qEnd (canon cap F), qEnd (canon cap G), bareEnd (canon cap G)) ::
          walkAux n cap (stepDP cap (canon cap F)) (stepDP cap (canon cap G)) = _
    rw [stepDP_canon, stepDP_canon, ih (funStep cap F) (funStep cap G)]
    have hcons : (List.range (n + 1)).map (fun l =>
        (qEndF cap (iter cap F l), qEndF cap (iter cap G l), bareEndF cap (iter cap G l))) =
        (qEndF cap F, qEndF cap G, bareEndF cap G) :: (List.range n).map (fun l =>
          (qEndF cap (iter cap F (l + 1)), qEndF cap (iter cap G (l + 1)),
           bareEndF cap (iter cap G (l + 1)))) := by
      rw [List.range_succ_eq_map, List.map_cons, List.map_map]
      simp [Function.comp, iter]
    rw [hcons]
    congr 1
    apply List.map_congr_left
    intro l _
    simp only [iter_succ_shift]

/-! ## Splitting a larger cap -/

/-- The extra states a cap of `M + k` adds over a cap of `M`. -/
private lemma states_split (M k : Nat) :
    states (M + k) = states M ++
      (List.range k).flatMap fun i => [(M + i + 1, true), (M + i + 1, false)] := by
  unfold states
  rw [List.range_add, List.flatMap_append, List.flatMap_map]

/-- Membership in the extra-states list, independent of the class flag. -/
private lemma mem_extra (M k g : Nat) (c : Bool) :
    (g, c) ∈ (List.range k).flatMap (fun i => [(M + i + 1, true), (M + i + 1, false)]) ↔
      ∃ i, i < k ∧ g = M + i + 1 := by
  simp only [List.mem_flatMap, List.mem_range, List.mem_cons, List.not_mem_nil, or_false]
  constructor
  · rintro ⟨i, hi, h | h⟩ <;> (injection h with h1 h2; exact ⟨i, hi, h1⟩)
  · rintro ⟨i, hi, rfl⟩
    exact ⟨i, hi, by cases c <;> simp⟩

/-- The sum of a list of zeros is zero. -/
private lemma sum_eq_zero_of_forall {l : List Nat} (h : ∀ x ∈ l, x = 0) : l.sum = 0 := by
  induction l with
  | nil => simp
  | cons x xs ih =>
    have hx : x = 0 := h x List.mem_cons_self
    have hxs : xs.sum = 0 := ih (fun y hy => h y (List.mem_cons_of_mem x hy))
    simp [hx, hxs]

/-- The sum over a flatMap of two-element lists collapses to a sum over a
pairwise-summed map. -/
private lemma sum_flatMap_pair (l : List Nat) (a b : Nat → Nat) :
    (l.flatMap fun i => [a i, b i]).sum = (l.map fun i => a i + b i).sum := by
  induction l with
  | nil => simp
  | cons x xs ih => simp [List.flatMap_cons, ih, Nat.add_assoc]

/-- `canon` at cap `M + k` splits the same way as `states`. -/
private lemma canon_split (M k : Nat) (F : St → Nat) :
    canon (M + k) F = canon M F ++
      ((List.range k).flatMap fun i => [(M + i + 1, true), (M + i + 1, false)]).map
        fun s => (s, F s) := by
  unfold canon
  rw [states_split, List.map_append]

/-- Any list-map-sum over `canon` splits the same way. -/
private lemma sum_end_split (M k : Nat) (F : St → Nat) (w : St × Nat → Nat) :
    ((canon (M + k) F).map w).sum = ((canon M F).map w).sum +
      (((List.range k).flatMap fun i => [(M + i + 1, true), (M + i + 1, false)]).map
        fun s => w (s, F s)).sum := by
  rw [canon_split, List.map_append, List.sum_append, List.map_map]
  rfl

/-- A `funStep` at cap `M + k` is the cap-`M` sum plus the `k` extra gaps. -/
theorem funStep_split (M k : Nat) (F : St → Nat) (t : St) :
    funStep (M + k) F t = funStep M F t +
      ((List.range k).map fun i =>
        F (M + i + 1, true) * stepMul (M + i + 1) true t.1 t.2 +
        F (M + i + 1, false) * stepMul (M + i + 1) false t.1 t.2).sum := by
  unfold funStep
  rw [states_split, List.map_append, List.sum_append, List.map_flatMap]
  simp only [List.map_cons, List.map_nil]
  rw [sum_flatMap_pair]

/-- The split collapses when every extra term dies. -/
theorem funStep_split_zero (M k : Nat) (F : St → Nat) (t : St)
    (h : ∀ i, i < k →
      F (M + i + 1, true) * stepMul (M + i + 1) true t.1 t.2 = 0 ∧
      F (M + i + 1, false) * stepMul (M + i + 1) false t.1 t.2 = 0) :
    funStep (M + k) F t = funStep M F t := by
  rw [funStep_split]
  have hz : ((List.range k).map fun i =>
      F (M + i + 1, true) * stepMul (M + i + 1) true t.1 t.2 +
      F (M + i + 1, false) * stepMul (M + i + 1) false t.1 t.2).sum = 0 := by
    apply sum_eq_zero_of_forall
    intro x hx
    obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hx
    rw [(h i (List.mem_range.mp hi)).1, (h i (List.mem_range.mp hi)).2]
  simp [hz]

/-- `qEndF` ignores extra gaps carrying no `J`-mass: above gap 2 the `P`
branch of `qEnd` weighs 0, and the `J` branch is multiplied by zero. -/
theorem qEndF_split_zero (M k : Nat) (F : St → Nat) (h2 : 2 ≤ M)
    (h : ∀ i, i < k → F (M + i + 1, true) = 0) :
    qEndF (M + k) F = qEndF M F := by
  change qEnd (canon (M + k) F) = qEnd (canon M F)
  unfold qEnd
  rw [sum_end_split]
  have hz : (((List.range k).flatMap fun i => [(M + i + 1, true), (M + i + 1, false)]).map
      fun s => if s.2 then F s * (if s.1 ≤ 2 then s.1 + 3 else 6)
        else if s.1 ≤ 2 then F s * (3 - s.1) else 0).sum = 0 := by
    apply sum_eq_zero_of_forall
    intro x hx
    obtain ⟨s, hs, rfl⟩ := List.mem_map.mp hx
    obtain ⟨g, c⟩ := s
    obtain ⟨i, hi, rfl⟩ := (mem_extra M k g c).mp hs
    have hgt : ¬ (M + i + 1 ≤ 2) := by omega
    cases c
    · simp [hgt]
    · simp [hgt, h i hi]
  rw [hz]
  simp

/-- `bareEndF` ignores extra gaps carrying no `J`-mass. -/
theorem bareEndF_split_zero (M k : Nat) (F : St → Nat)
    (h : ∀ i, i < k → F (M + i + 1, true) = 0) :
    bareEndF (M + k) F = bareEndF M F := by
  change bareEnd (canon (M + k) F) = bareEnd (canon M F)
  unfold bareEnd
  rw [sum_end_split]
  have hz : (((List.range k).flatMap fun i => [(M + i + 1, true), (M + i + 1, false)]).map
      fun s => if s.2 then F s else 0).sum = 0 := by
    apply sum_eq_zero_of_forall
    intro x hx
    obtain ⟨s, hs, rfl⟩ := List.mem_map.mp hx
    obtain ⟨g, c⟩ := s
    obtain ⟨i, hi, rfl⟩ := (mem_extra M k g c).mp hs
    cases c
    · simp
    · simp [h i hi]
  simp [hz]

/-! ## Congruence over a common cap -/

/-- Term-by-term congruence for one step onto a fixed target: sources where
the values differ contribute nothing if their multiplicity is zero. -/
theorem funStep_congr (cap : Nat) (F G : St → Nat) (t : St)
    (h : ∀ g c, 1 ≤ g → g ≤ cap →
      F (g, c) = G (g, c) ∨ stepMul g c t.1 t.2 = 0) :
    funStep cap F t = funStep cap G t := by
  unfold funStep
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  obtain ⟨h1, h2⟩ := (mem_states cap g c).mp hs
  rcases h g c h1 h2 with heq | hzero
  · rw [heq]
  · simp [hzero]

/-- `qEndF` reads `J` everywhere and `P` only at gaps `≤ 2`. -/
theorem qEndF_congr (cap : Nat) (F G : St → Nat)
    (hJ : ∀ g, 1 ≤ g → g ≤ cap → F (g, true) = G (g, true))
    (hP : ∀ g, 1 ≤ g → g ≤ 2 → F (g, false) = G (g, false)) :
    qEndF cap F = qEndF cap G := by
  change qEnd (canon cap F) = qEnd (canon cap G)
  unfold qEnd canon
  rw [List.map_map, List.map_map]
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  obtain ⟨h1, h2⟩ := (mem_states cap g c).mp hs
  cases c
  · by_cases hle : g ≤ 2
    · simp [hP g h1 hle]
    · simp [hle]
  · simp [hJ g h1 h2]

/-- `bareEndF` reads only `J`. -/
theorem bareEndF_congr (cap : Nat) (F G : St → Nat)
    (hJ : ∀ g, 1 ≤ g → g ≤ cap → F (g, true) = G (g, true)) :
    bareEndF cap F = bareEndF cap G := by
  change bareEnd (canon cap F) = bareEnd (canon cap G)
  unfold bareEnd canon
  rw [List.map_map, List.map_map]
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  obtain ⟨h1, h2⟩ := (mem_states cap g c).mp hs
  cases c
  · simp
  · simp [hJ g h1 h2]

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.walkAux_canon' depends on axioms: [propext, Quot.sound]
-/
#guard_msgs in
#print axioms walkAux_canon

/--
info: 'Polyplets.GapWalk.funStep_split_zero' depends on axioms: [propext, Quot.sound]
-/
#guard_msgs in
#print axioms funStep_split_zero

end GapWalk
end Polyplets
