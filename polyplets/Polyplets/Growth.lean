/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Analysis.Subadditive
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Polyplets.Graph
import Polyplets.UpperBound

/-!
# The growth constant `λ`: existence and a two-sided bracket

`Sequence.lean` names the sequence `a n` and `UpperBound.lean` bounds it above.
Neither says that the *growth rate* `λ = lim a(n)^{1/n}` — the constant the
paper quotes throughout — exists at all. This file builds it, from the two
halves of Fekete's argument:

* **Klarner supermultiplicativity** (`a_supermul`): `a m * a n ≤ a (m + n)`,
  proved by an explicit injection `concat` that welds two canonical animals
  side by side across one king edge, together with the recovery maps
  (`recLeft`, `recRight`) that undo it;
* **Fekete's lemma**, from Mathlib's `Subadditive.tendsto_lim`, applied to
  `negLogA n = -log (a n)`, which is subadditive by supermultiplicativity and
  whose `negLogA n / n` is bounded below by the `UpperBound.lean` ceiling.

The payoff:

* `lambda_tendsto` : `a n ^ (1/n) → lambda`;
* `a_le_lambda_pow` : `a n ≤ lambda ^ n` (Fekete's limit-is-supremum half);
* `lambda_le` : `lambda ≤ 3125 / 256 = 5⁵/4⁴`;
* `lambda_lb` / `lambda_gt` : `3832 ≤ lambda ^ 6`, hence `3.95 < lambda`.

Together the last two are the machine-checked bracket `3.95 < λ ≤ 3125/256`.

## The concatenation injection

Given canonical `A` (`m` cells) and `B` (`n` cells), let `w = maxX A` be `A`'s
rightmost column, `aY = colTop A w` the top cell of that column, and
`bY = colTop B 0` the top cell of `B`'s column `0` (nonempty because `B` is
anchored at `x = 0`). Put `cTop A B = max aY bY` and lift each half so that its
own bridge cell sits at height `cTop`:

`concat A B = (A + (0, cTop - aY)) ∪ (B + (w + 1, cTop - bY))`.

Both lifts are nonnegative and at least one is zero, so the union is again
anchored at `y = 0`; `A`'s x-anchor is untouched and `B` is pushed strictly
right of `A`, so the union is anchored at `x = 0` and the two halves are
disjoint (hence `m + n` cells). The bridge cells `(w, cTop)` and `(w + 1, cTop)`
are king-adjacent, which glues the two connected halves
(`kingConnected_union_of_adj`).

Injectivity is by explicit recovery. The **cut** `cutAt C m` is the least `k`
with `|{p ∈ C : p.1 < k}| = m`; on `C = concat A B` it is `w + 1`, because the
left count is `< m` for every `k ≤ w` (the bridge cell `(w, cTop)` is missed)
and exactly `m` at `w + 1`. Splitting at the cut and re-anchoring — in `y` only
for the left half, in both coordinates for the right — returns `A` and `B`
(`recLeft_concat`, `recRight_concat`).
-/

namespace Polyplets

open scoped Topology

/-! ## Translating a cell set

Everything in the concatenation is a translate, so translation invariance of
the three canonicity ingredients — cardinality, king adjacency, king
connectivity — is proved once, generally. -/

/-- `S` translated by the vector `(e, d)`. -/
def shiftBy (v : ℤ × ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  S.image fun q => (q.1 + v.1, q.2 + v.2)

/-- Translating a single cell is injective. -/
lemma shift_injective (v : ℤ × ℤ) :
    Function.Injective fun q : ℤ × ℤ => (q.1 + v.1, q.2 + v.2) := by
  intro x y h
  simp only [Prod.mk.injEq] at h
  exact Prod.ext (by omega) (by omega)

/-- Membership in a translate, in component form (the form every proof below
wants: no projections of literal pairs left over). -/
lemma mem_shiftBy_iff {e d : ℤ} {q : ℤ × ℤ} {S : Finset (ℤ × ℤ)} :
    q ∈ shiftBy (e, d) S ↔ ∃ p ∈ S, q.1 = p.1 + e ∧ q.2 = p.2 + d := by
  rw [shiftBy, Finset.mem_image]
  constructor
  · rintro ⟨p, hp, rfl⟩
    exact ⟨p, hp, rfl, rfl⟩
  · rintro ⟨p, hp, h1, h2⟩
    exact ⟨p, hp, Prod.ext h1.symm h2.symm⟩

/-- Translation preserves cardinality. -/
lemma card_shiftBy (v : ℤ × ℤ) (S : Finset (ℤ × ℤ)) : (shiftBy v S).card = S.card :=
  Finset.card_image_of_injective _ (shift_injective v)

/-- Two translations compose. -/
lemma shiftBy_shiftBy (e d e' d' : ℤ) (S : Finset (ℤ × ℤ)) :
    shiftBy (e', d') (shiftBy (e, d) S) = shiftBy (e + e', d + d') S := by
  simp only [shiftBy, Finset.image_image]
  refine Finset.image_congr fun q _ => ?_
  simp only [Function.comp_apply, Prod.mk.injEq]
  constructor <;> ring

/-- Translating by zero does nothing. -/
lemma shiftBy_zero (S : Finset (ℤ × ℤ)) : shiftBy (0, 0) S = S := by
  ext q
  rw [mem_shiftBy_iff]
  constructor
  · rintro ⟨p, hp, h1, h2⟩
    have : q = p := Prod.ext (by omega) (by omega)
    rwa [this]
  · intro hq
    exact ⟨q, hq, by omega, by omega⟩

/-- **Translation is undone by the opposite translation.** Stated with the
cancellation as hypotheses so that it applies without any `-0`/`0` mismatch. -/
lemma shiftBy_cancel {e d e' d' : ℤ} (he : e + e' = 0) (hd : d + d' = 0)
    (S : Finset (ℤ × ℤ)) : shiftBy (e', d') (shiftBy (e, d) S) = S := by
  rw [shiftBy_shiftBy, he, hd, shiftBy_zero]

/-- King adjacency is translation-invariant. -/
lemma kingAdj_shift (v : ℤ × ℤ) {x y : ℤ × ℤ} (h : kingAdj x y) :
    kingAdj (x.1 + v.1, x.2 + v.2) (y.1 + v.1, y.2 + v.2) := by
  obtain ⟨hne, h1, h2⟩ := h
  rw [ne_eq, Prod.ext_iff] at hne
  refine ⟨by simp only [ne_eq, Prod.mk.injEq]; omega, ?_, ?_⟩
  · change |x.1 + v.1 - (y.1 + v.1)| ≤ 1
    rw [show x.1 + v.1 - (y.1 + v.1) = x.1 - y.1 by ring]; exact h1
  · change |x.2 + v.2 - (y.2 + v.2)| ≤ 1
    rw [show x.2 + v.2 - (y.2 + v.2) = x.2 - y.2 by ring]; exact h2

/-- King connectivity is translation-invariant. -/
lemma kingConnected_shiftBy (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} (h : KingConnected S) :
    KingConnected (shiftBy v S) := by
  intro d hd e he
  rw [shiftBy, Finset.mem_image] at hd he
  obtain ⟨x, hx, rfl⟩ := hd
  obtain ⟨y, hy, rfl⟩ := he
  refine Relation.ReflTransGen.lift (fun q : ℤ × ℤ => (q.1 + v.1, q.2 + v.2))
    (fun u w huw => ?_) (h x hx y hy)
  exact ⟨by rw [shiftBy]; exact Finset.mem_image_of_mem _ huw.1,
    by rw [shiftBy]; exact Finset.mem_image_of_mem _ huw.2.1, kingAdj_shift _ huw.2.2⟩

/-- King paths reverse: the step relation is symmetric, so its reflexive
transitive closure is. -/
lemma reflTransGen_symm {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q) :
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) q p := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | @tail b c _ hbc ih =>
      exact Relation.ReflTransGen.head ⟨hbc.2.1, hbc.1, kingAdj_symm hbc.2.2⟩ ih

/-- **Gluing two connected sets across one king edge.** Paths inside either half
lift into the union (the step predicate only weakens), and the bridge edge
`x₀ → y₀` — traversable in both directions, king adjacency being symmetric —
routes between the halves. -/
lemma kingConnected_union_of_adj {X Y : Finset (ℤ × ℤ)} {x₀ y₀ : ℤ × ℤ}
    (hX : KingConnected X) (hY : KingConnected Y) (hx₀ : x₀ ∈ X) (hy₀ : y₀ ∈ Y)
    (hadj : kingAdj x₀ y₀) : KingConnected (X ∪ Y) := by
  have liftX : ∀ p ∈ X, ∀ q ∈ X,
      Relation.ReflTransGen (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) p q :=
    fun p hp q hq => (hX p hp q hq).mono fun a b hab =>
      ⟨Finset.mem_union_left _ hab.1, Finset.mem_union_left _ hab.2.1, hab.2.2⟩
  have liftY : ∀ p ∈ Y, ∀ q ∈ Y,
      Relation.ReflTransGen (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) p q :=
    fun p hp q hq => (hY p hp q hq).mono fun a b hab =>
      ⟨Finset.mem_union_right _ hab.1, Finset.mem_union_right _ hab.2.1, hab.2.2⟩
  have bridge : (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) x₀ y₀ :=
    ⟨Finset.mem_union_left _ hx₀, Finset.mem_union_right _ hy₀, hadj⟩
  have bridge' : (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) y₀ x₀ :=
    ⟨Finset.mem_union_right _ hy₀, Finset.mem_union_left _ hx₀, kingAdj_symm hadj⟩
  intro p hp q hq
  rcases Finset.mem_union.mp hp with hp | hp <;> rcases Finset.mem_union.mp hq with hq | hq
  · exact liftX p hp q hq
  · exact ((liftX p hp x₀ hx₀).tail bridge).trans (liftY y₀ hy₀ q hq)
  · exact ((liftY p hp y₀ hy₀).tail bridge').trans (liftX x₀ hx₀ q hq)
  · exact liftY p hp q hq

/-! ## `a n ≥ 1`: the bar witness

The horizontal bar of `n` cells is canonical, so no `a n` with `n ≥ 1`
vanishes — which is what makes `log (a n)` finite below. -/

/-- The horizontal bar `{(0,0), (1,0), …, (n-1,0)}`. -/
def bar (n : ℕ) : Finset (ℤ × ℤ) := (Finset.range n).image fun i : ℕ => ((i : ℤ), (0 : ℤ))

/-- Cells of the bar. -/
lemma bar_mem {n i : ℕ} (h : i < n) : ((i : ℤ), (0 : ℤ)) ∈ bar n :=
  Finset.mem_image_of_mem _ (Finset.mem_range.mpr h)

/-- The bar has `n` cells. -/
lemma bar_card (n : ℕ) : (bar n).card = n := by
  rw [bar, Finset.card_image_of_injective _ (fun i j h => by simpa using h), Finset.card_range]

/-- The bar is threaded from its left end. -/
private lemma bar_path {n : ℕ} : ∀ i : ℕ, i < n →
    Relation.ReflTransGen (fun a b => a ∈ bar n ∧ b ∈ bar n ∧ kingAdj a b)
      ((0 : ℤ), (0 : ℤ)) ((i : ℤ), (0 : ℤ)) := by
  intro i
  induction i with
  | zero => intro _; exact Relation.ReflTransGen.refl
  | succ i ih =>
      intro hi
      have hstep : kingAdj ((i : ℤ), (0 : ℤ)) (((i : ℤ) + 1), (0 : ℤ)) := by
        refine ⟨by simp only [ne_eq, Prod.mk.injEq]; omega, ?_, ?_⟩
        · rw [abs_le]; omega
        · rw [abs_le]; omega
      have hcast : (((i + 1 : ℕ) : ℤ), (0 : ℤ)) = (((i : ℤ) + 1), (0 : ℤ)) := by push_cast; rfl
      rw [hcast]
      refine (ih (by omega)).tail ⟨bar_mem (by omega), ?_, hstep⟩
      have := bar_mem (n := n) hi
      rwa [hcast] at this

/-- The bar is king-connected. -/
lemma bar_connected (n : ℕ) : KingConnected (bar n) := by
  intro p hp q hq
  rw [bar, Finset.mem_image] at hp hq
  obtain ⟨i, hi, rfl⟩ := hp
  obtain ⟨j, hj, rfl⟩ := hq
  rw [Finset.mem_range] at hi hj
  exact (reflTransGen_symm (bar_path i hi)).trans (bar_path j hj)

/-- The bar is a canonical animal. -/
lemma bar_canonical {n : ℕ} (hn : 1 ≤ n) : IsCanonicalAnimal n (bar n) := by
  have h0 : ((0 : ℤ), (0 : ℤ)) ∈ bar n := by
    have := bar_mem (n := n) (i := 0) hn
    simpa using this
  refine ⟨bar_card n, bar_connected n, ?_, ⟨_, h0, rfl⟩, ?_, ⟨_, h0, rfl⟩⟩
  · intro p hp
    rw [bar, Finset.mem_image] at hp
    obtain ⟨i, -, rfl⟩ := hp
    exact Int.natCast_nonneg i
  · intro p hp
    rw [bar, Finset.mem_image] at hp
    obtain ⟨i, -, rfl⟩ := hp
    exact le_rfl

/-- **`a n ≥ 1` for `n ≥ 1`.** The bar witnesses it. -/
theorem one_le_a {n : ℕ} (hn : 1 ≤ n) : 1 ≤ a n := by
  rw [a]
  exact (Set.ncard_pos (canonicalAnimal_finite n)).mpr ⟨bar n, bar_canonical hn⟩

/-- **`a 0 = 0`.** The empty set is the only `0`-cell `Finset`, and it fails the
anchoring clauses; so supermultiplicativity has to start at `1`. -/
theorem a_zero : a 0 = 0 := by
  have hempty : {S : Finset (ℤ × ℤ) | IsCanonicalAnimal 0 S} = ∅ := by
    ext S
    simp only [Set.mem_setOf_eq, Set.mem_empty_iff_false, iff_false]
    rintro ⟨hcard, -, -, ⟨p, hp, -⟩, -, -⟩
    rw [Finset.card_eq_zero] at hcard
    rw [hcard] at hp
    exact absurd hp (by simp)
  rw [a, hempty, Set.ncard_empty]

/-! ## Extremal columns

The concatenation needs a *deterministic* pair of bridge cells: the top cell of
`A`'s rightmost column and the top cell of `B`'s column `0`. Both are taken
through `Int.toNat`-valued `Finset.sup`, so they are total functions needing no
nonemptiness side condition; canonicity then shows the cell they name is really
there. -/

/-- The largest x-coordinate of `S`, through `Int.toNat`. -/
def maxX (S : Finset (ℤ × ℤ)) : ℕ := S.sup fun p => p.1.toNat

/-- The largest y-coordinate among the cells of `S` in column `x`. Cells outside
the column contribute `0`, which is harmless when the column is nonempty and the
y-coordinates are nonnegative. -/
def colTop (S : Finset (ℤ × ℤ)) (x : ℤ) : ℕ :=
  S.sup fun p => if p.1 = x then p.2.toNat else 0

/-- `maxX` bounds the x-coordinates. -/
lemma le_maxX {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) (hnn : 0 ≤ p.1) :
    p.1 ≤ (maxX S : ℤ) := by
  have h := Finset.le_sup (f := fun p : ℤ × ℤ => p.1.toNat) hp
  have h' : p.1.toNat ≤ maxX S := h
  omega

/-- `maxX` is attained on a canonical animal. -/
lemma maxX_mem {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    ∃ p ∈ S, p.1 = (maxX S : ℤ) := by
  obtain ⟨p0, hp0, -⟩ := hS.2.2.2.1
  obtain ⟨pm, hpm, hpme⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0⟩ (fun p : ℤ × ℤ => p.1.toNat)
  refine ⟨pm, hpm, ?_⟩
  have hnn := hS.2.2.1 pm hpm
  have hval : maxX S = pm.1.toNat := hpme
  omega

/-- **The top of a nonempty column is a cell.** Either the `sup` is attained at a
cell of the column — and then it names that cell — or it is `0`, in which case
any cell of the column has y-coordinate `0` and is the cell named. -/
lemma colTop_mem {S : Finset (ℤ × ℤ)} {x : ℤ} (hnn : ∀ p ∈ S, 0 ≤ p.2)
    (hx : ∃ p ∈ S, p.1 = x) : (x, (colTop S x : ℤ)) ∈ S := by
  obtain ⟨p0, hp0, hp0x⟩ := hx
  obtain ⟨pm, hpm, hpme⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0⟩ (fun p : ℤ × ℤ => if p.1 = x then p.2.toNat else 0)
  by_cases hc : pm.1 = x
  · have hval : colTop S x = (if pm.1 = x then pm.2.toNat else 0) := hpme
    rw [if_pos hc] at hval
    have hy := hnn pm hpm
    have heq : (x, (colTop S x : ℤ)) = pm := Prod.ext hc.symm (by omega)
    rw [heq]; exact hpm
  · have hval : colTop S x = (if pm.1 = x then pm.2.toNat else 0) := hpme
    rw [if_neg hc] at hval
    have hle : (if p0.1 = x then p0.2.toNat else 0) ≤ colTop S x :=
      Finset.le_sup (f := fun p : ℤ × ℤ => if p.1 = x then p.2.toNat else 0) hp0
    rw [if_pos hp0x] at hle
    have hy := hnn p0 hp0
    have heq : (x, (colTop S x : ℤ)) = p0 := Prod.ext hp0x.symm (by omega)
    rw [heq]; exact hp0

/-! ## The concatenation -/

/-- The common height of the two bridge cells: the higher of `A`'s rightmost
column top and `B`'s column-`0` top. -/
def cTop (A B : Finset (ℤ × ℤ)) : ℤ :=
  max (colTop A (maxX A : ℤ) : ℤ) (colTop B 0 : ℤ)

/-- The vertical lift applied to `A` inside `concat A B`. -/
def liftA (A B : Finset (ℤ × ℤ)) : ℤ := cTop A B - (colTop A (maxX A : ℤ) : ℤ)

/-- The vertical lift applied to `B` inside `concat A B`. -/
def liftB (A B : Finset (ℤ × ℤ)) : ℤ := cTop A B - (colTop B 0 : ℤ)

/-- **The concatenation of two canonical animals**: `B` moved one column to the
right of `A`, both lifted so their bridge cells share the height `cTop A B`. -/
def concat (A B : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  shiftBy (0, liftA A B) A ∪ shiftBy ((maxX A : ℤ) + 1, liftB A B) B

lemma liftA_nonneg (A B : Finset (ℤ × ℤ)) : 0 ≤ liftA A B := by
  simp only [liftA, cTop]; omega

lemma liftB_nonneg (A B : Finset (ℤ × ℤ)) : 0 ≤ liftB A B := by
  simp only [liftB, cTop]; omega

/-- One of the two halves is not lifted at all — which is what keeps the union
anchored at `y = 0`. -/
lemma lift_eq_zero (A B : Finset (ℤ × ℤ)) : liftA A B = 0 ∨ liftB A B = 0 := by
  simp only [liftA, liftB, cTop]; omega

/-- The left half stays weakly left of column `maxX A`. -/
lemma concat_left_x_le {A B : Finset (ℤ × ℤ)} (hA : ∀ p ∈ A, 0 ≤ p.1) {q : ℤ × ℤ}
    (hq : q ∈ shiftBy (0, liftA A B) A) : q.1 ≤ (maxX A : ℤ) := by
  obtain ⟨p, hp, h1, -⟩ := mem_shiftBy_iff.mp hq
  have := le_maxX hp (hA p hp)
  omega

/-- The right half sits strictly right of column `maxX A`. -/
lemma concat_right_x_ge {A B : Finset (ℤ × ℤ)} (hB : ∀ p ∈ B, 0 ≤ p.1) {q : ℤ × ℤ}
    (hq : q ∈ shiftBy ((maxX A : ℤ) + 1, liftB A B) B) : (maxX A : ℤ) + 1 ≤ q.1 := by
  obtain ⟨p, hp, h1, -⟩ := mem_shiftBy_iff.mp hq
  have := hB p hp
  omega

/-- The two halves are disjoint. -/
lemma concat_disjoint {A B : Finset (ℤ × ℤ)} (hA : ∀ p ∈ A, 0 ≤ p.1) (hB : ∀ p ∈ B, 0 ≤ p.1) :
    Disjoint (shiftBy (0, liftA A B) A) (shiftBy ((maxX A : ℤ) + 1, liftB A B) B) := by
  rw [Finset.disjoint_left]
  intro q hq1 hq2
  have h1 := concat_left_x_le hA hq1
  have h2 := concat_right_x_ge (A := A) hB hq2
  omega

/-- The left bridge cell: the top of `A`'s rightmost column, lifted. -/
lemma bridgeA_mem {m : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A) :
    ((maxX A : ℤ), cTop A B) ∈ shiftBy (0, liftA A B) A := by
  have hmem : ((maxX A : ℤ), (colTop A (maxX A : ℤ) : ℤ)) ∈ A :=
    colTop_mem hA.2.2.2.2.1 (maxX_mem hA)
  refine mem_shiftBy_iff.mpr ⟨_, hmem, ?_, ?_⟩
  · change (maxX A : ℤ) = (maxX A : ℤ) + 0
    ring
  · change cTop A B = (colTop A (maxX A : ℤ) : ℤ) + liftA A B
    rw [liftA]; ring

/-- The right bridge cell: the top of `B`'s column `0`, shifted and lifted. -/
lemma bridgeB_mem {n : ℕ} {A B : Finset (ℤ × ℤ)} (hB : IsCanonicalAnimal n B) :
    ((maxX A : ℤ) + 1, cTop A B) ∈ shiftBy ((maxX A : ℤ) + 1, liftB A B) B := by
  have hmem : ((0 : ℤ), (colTop B 0 : ℤ)) ∈ B :=
    colTop_mem hB.2.2.2.2.1 hB.2.2.2.1
  refine mem_shiftBy_iff.mpr ⟨_, hmem, ?_, ?_⟩
  · change (maxX A : ℤ) + 1 = (0 : ℤ) + ((maxX A : ℤ) + 1)
    ring
  · change cTop A B = (colTop B 0 : ℤ) + liftB A B
    rw [liftB]; ring

/-- **The concatenation is canonical of size `m + n`.** Disjointness gives the
count, the bridge edge gives connectivity, and the lifts were chosen exactly so
that both anchoring clauses survive. -/
theorem concat_canonical {m n : ℕ} {A B : Finset (ℤ × ℤ)}
    (hA : IsCanonicalAnimal m A) (hB : IsCanonicalAnimal n B) :
    IsCanonicalAnimal (m + n) (concat A B) := by
  have hcard : (concat A B).card = m + n := by
    rw [concat, Finset.card_union_of_disjoint (concat_disjoint hA.2.2.1 hB.2.2.1),
      card_shiftBy, card_shiftBy, hA.1, hB.1]
  have hconn : KingConnected (concat A B) := by
    rw [concat]
    refine kingConnected_union_of_adj (kingConnected_shiftBy _ hA.2.1)
      (kingConnected_shiftBy _ hB.2.1) (bridgeA_mem hA) (bridgeB_mem hB) ?_
    refine ⟨by simp only [ne_eq, Prod.mk.injEq]; omega, ?_, ?_⟩
    · change |(maxX A : ℤ) - ((maxX A : ℤ) + 1)| ≤ 1
      rw [abs_le]; omega
    · change |cTop A B - cTop A B| ≤ 1
      simp
  refine ⟨hcard, hconn, ?_, ?_, ?_, ?_⟩
  · intro q hq
    rw [concat, Finset.mem_union] at hq
    rcases hq with hq | hq
    · obtain ⟨p, hp, h1, -⟩ := mem_shiftBy_iff.mp hq
      have hx := hA.2.2.1 p hp
      omega
    · have hx := concat_right_x_ge (A := A) hB.2.2.1 hq
      have hw : (0 : ℤ) ≤ (maxX A : ℤ) := Int.natCast_nonneg _
      omega
  · obtain ⟨p, hp, hp1⟩ := hA.2.2.2.1
    refine ⟨(p.1, p.2 + liftA A B), ?_, hp1⟩
    rw [concat]
    exact Finset.mem_union_left _ (mem_shiftBy_iff.mpr ⟨p, hp, by change p.1 = p.1 + 0; ring, rfl⟩)
  · intro q hq
    rw [concat, Finset.mem_union] at hq
    rcases hq with hq | hq
    · obtain ⟨p, hp, -, h2⟩ := mem_shiftBy_iff.mp hq
      have hy := hA.2.2.2.2.1 p hp
      have hl := liftA_nonneg A B
      omega
    · obtain ⟨p, hp, -, h2⟩ := mem_shiftBy_iff.mp hq
      have hy := hB.2.2.2.2.1 p hp
      have hl := liftB_nonneg A B
      omega
  · rcases lift_eq_zero A B with h | h
    · obtain ⟨p, hp, hp2⟩ := hA.2.2.2.2.2
      refine ⟨(p.1, p.2 + liftA A B), ?_, ?_⟩
      · rw [concat]
        exact Finset.mem_union_left _
          (mem_shiftBy_iff.mpr ⟨p, hp, by change p.1 = p.1 + 0; ring, rfl⟩)
      · change p.2 + liftA A B = 0
        omega
    · obtain ⟨p, hp, hp2⟩ := hB.2.2.2.2.2
      refine ⟨(p.1 + ((maxX A : ℤ) + 1), p.2 + liftB A B), ?_, ?_⟩
      · rw [concat]
        exact Finset.mem_union_right _ (mem_shiftBy_iff.mpr ⟨p, hp, rfl, rfl⟩)
      · change p.2 + liftB A B = 0
        omega

/-! ## Recovery: the concatenation is injective

The cut is located by counting, then each half is re-anchored — the left half in
`y` only (its x-anchor never moved), the right half in both coordinates. -/

/-- The part of `C` strictly left of the vertical line `x = k`. -/
def leftOf (C : Finset (ℤ × ℤ)) (k : ℤ) : Finset (ℤ × ℤ) := C.filter fun p => p.1 < k

/-- The part of `C` weakly right of the vertical line `x = k`. -/
def rightOf (C : Finset (ℤ × ℤ)) (k : ℤ) : Finset (ℤ × ℤ) := C.filter fun p => k ≤ p.1

/-- The cut: the least column boundary with exactly `m` cells to its left. -/
noncomputable def cutAt (C : Finset (ℤ × ℤ)) (m : ℕ) : ℕ :=
  sInf {k : ℕ | (leftOf C (k : ℤ)).card = m}

/-- The least y-coordinate of `S`, as a natural number (junk `0` if `S` has no
cell in a nonnegative row — never the case below). -/
noncomputable def baseY (S : Finset (ℤ × ℤ)) : ℕ := sInf {k : ℕ | ∃ p ∈ S, p.2 = (k : ℤ)}

/-- The least x-coordinate of `S`, as a natural number. -/
noncomputable def baseX (S : Finset (ℤ × ℤ)) : ℕ := sInf {k : ℕ | ∃ p ∈ S, p.1 = (k : ℤ)}

/-- **A translate of a canonical animal remembers its vertical offset.** -/
lemma baseY_shift {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) {e d : ℤ}
    (hd : 0 ≤ d) : (baseY (shiftBy (e, d) S) : ℤ) = d := by
  rw [baseY]
  have hmem : d.toNat ∈ {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.2 = (k : ℤ)} := by
    obtain ⟨p₀, hp₀, hp₀2⟩ := hS.2.2.2.2.2
    exact ⟨(p₀.1 + e, p₀.2 + d), mem_shiftBy_iff.mpr ⟨p₀, hp₀, rfl, rfl⟩,
      by change p₀.2 + d = (d.toNat : ℤ); omega⟩
  have hle : sInf {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.2 = (k : ℤ)} ≤ d.toNat :=
    Nat.sInf_le hmem
  obtain ⟨p, hp, hp2⟩ := Nat.sInf_mem (⟨_, hmem⟩ :
    {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.2 = (k : ℤ)}.Nonempty)
  obtain ⟨q, hq, -, hq2⟩ := mem_shiftBy_iff.mp hp
  have hy := hS.2.2.2.2.1 q hq
  omega

/-- **A translate of a canonical animal remembers its horizontal offset.** -/
lemma baseX_shift {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) {e d : ℤ}
    (he : 0 ≤ e) : (baseX (shiftBy (e, d) S) : ℤ) = e := by
  rw [baseX]
  have hmem : e.toNat ∈ {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.1 = (k : ℤ)} := by
    obtain ⟨p₀, hp₀, hp₀1⟩ := hS.2.2.2.1
    exact ⟨(p₀.1 + e, p₀.2 + d), mem_shiftBy_iff.mpr ⟨p₀, hp₀, rfl, rfl⟩,
      by change p₀.1 + e = (e.toNat : ℤ); omega⟩
  have hle : sInf {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.1 = (k : ℤ)} ≤ e.toNat :=
    Nat.sInf_le hmem
  obtain ⟨p, hp, hp1⟩ := Nat.sInf_mem (⟨_, hmem⟩ :
    {k : ℕ | ∃ p ∈ shiftBy (e, d) S, p.1 = (k : ℤ)}.Nonempty)
  obtain ⟨q, hq, hq1, -⟩ := mem_shiftBy_iff.mp hp
  have hx := hS.2.2.1 q hq
  omega

/-- The left part of a concatenation, cut at the right place, is the lifted `A`. -/
lemma leftOf_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A)
    (hB : IsCanonicalAnimal n B) :
    leftOf (concat A B) ((maxX A : ℤ) + 1) = shiftBy (0, liftA A B) A := by
  ext q
  rw [leftOf, Finset.mem_filter, concat, Finset.mem_union]
  constructor
  · rintro ⟨hq | hq, hlt⟩
    · exact hq
    · have := concat_right_x_ge (A := A) hB.2.2.1 hq
      omega
  · intro hq
    exact ⟨Or.inl hq, by have := concat_left_x_le hA.2.2.1 hq; omega⟩

/-- The right part of a concatenation, cut at the right place, is the shifted `B`. -/
lemma rightOf_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A)
    (hB : IsCanonicalAnimal n B) :
    rightOf (concat A B) ((maxX A : ℤ) + 1) = shiftBy ((maxX A : ℤ) + 1, liftB A B) B := by
  ext q
  rw [rightOf, Finset.mem_filter, concat, Finset.mem_union]
  constructor
  · rintro ⟨hq | hq, hge⟩
    · have := concat_left_x_le hA.2.2.1 hq
      omega
    · exact hq
  · intro hq
    exact ⟨Or.inr hq, concat_right_x_ge (A := A) hB.2.2.1 hq⟩

/-- **The cut is where the construction put it.** At `k = maxX A + 1` the left
count is exactly `m`; at any `k ≤ maxX A` the left part misses `A`'s bridge cell
`(maxX A, cTop A B)`, so it is a proper subset of the lifted `A` and its count is
`< m`. Hence the least `k` with left count `m` is `maxX A + 1`. -/
lemma cutAt_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A)
    (hB : IsCanonicalAnimal n B) : cutAt (concat A B) m = maxX A + 1 := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  have hmem : (maxX A + 1) ∈ {k : ℕ | (leftOf (concat A B) (k : ℤ)).card = m} := by
    change (leftOf (concat A B) ((maxX A + 1 : ℕ) : ℤ)).card = m
    rw [hcast, leftOf_concat hA hB, card_shiftBy, hA.1]
  have hlow : ∀ k : ℕ, (k : ℤ) ≤ (maxX A : ℤ) → (leftOf (concat A B) (k : ℤ)).card < m := by
    intro k hk
    have hsub : leftOf (concat A B) (k : ℤ) ⊆ shiftBy (0, liftA A B) A := by
      intro q hq
      rw [leftOf, Finset.mem_filter, concat, Finset.mem_union] at hq
      rcases hq.1 with h | h
      · exact h
      · have h1 := concat_right_x_ge (A := A) hB.2.2.1 h
        have h2 : q.1 < (k : ℤ) := hq.2
        omega
    have hbr : ((maxX A : ℤ), cTop A B) ∈ shiftBy (0, liftA A B) A := bridgeA_mem hA
    have hbrn : ((maxX A : ℤ), cTop A B) ∉ leftOf (concat A B) (k : ℤ) := by
      rw [leftOf, Finset.mem_filter]
      rintro ⟨-, h⟩
      have h' : (maxX A : ℤ) < (k : ℤ) := h
      omega
    calc (leftOf (concat A B) (k : ℤ)).card
        < (shiftBy (0, liftA A B) A).card :=
          Finset.card_lt_card ((Finset.ssubset_iff_of_subset hsub).mpr ⟨_, hbr, hbrn⟩)
      _ = m := by rw [card_shiftBy, hA.1]
  rw [cutAt]
  refine le_antisymm (Nat.sInf_le hmem) ?_
  by_contra hcon
  rw [Nat.not_le] at hcon
  have hin := Nat.sInf_mem (⟨_, hmem⟩ :
    {k : ℕ | (leftOf (concat A B) (k : ℤ)).card = m}.Nonempty)
  have heq : (leftOf (concat A B)
      ((sInf {k : ℕ | (leftOf (concat A B) (k : ℤ)).card = m} : ℕ) : ℤ)).card = m := hin
  have := hlow (sInf {k : ℕ | (leftOf (concat A B) (k : ℤ)).card = m}) (by omega)
  omega

/-- Recovering the left factor: cut, then re-anchor vertically. -/
noncomputable def recLeft (C : Finset (ℤ × ℤ)) (m : ℕ) : Finset (ℤ × ℤ) :=
  shiftBy (0, -(baseY (leftOf C (cutAt C m : ℤ)) : ℤ)) (leftOf C (cutAt C m : ℤ))

/-- Recovering the right factor: cut, then re-anchor in both coordinates. -/
noncomputable def recRight (C : Finset (ℤ × ℤ)) (m : ℕ) : Finset (ℤ × ℤ) :=
  shiftBy (-(baseX (rightOf C (cutAt C m : ℤ)) : ℤ), -(baseY (rightOf C (cutAt C m : ℤ)) : ℤ))
    (rightOf C (cutAt C m : ℤ))

/-- `recLeft` inverts `concat` on the left. -/
theorem recLeft_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A)
    (hB : IsCanonicalAnimal n B) : recLeft (concat A B) m = A := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  rw [recLeft, cutAt_concat hA hB, hcast, leftOf_concat hA hB,
    baseY_shift hA (liftA_nonneg A B)]
  exact shiftBy_cancel (by ring) (by ring) A

/-- `recRight` inverts `concat` on the right. -/
theorem recRight_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsCanonicalAnimal m A)
    (hB : IsCanonicalAnimal n B) : recRight (concat A B) m = B := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  have hw : (0 : ℤ) ≤ (maxX A : ℤ) + 1 := by
    have := Int.natCast_nonneg (maxX A); omega
  rw [recRight, cutAt_concat hA hB, hcast, rightOf_concat hA hB,
    baseX_shift hB hw, baseY_shift hB (liftB_nonneg A B)]
  exact shiftBy_cancel (by ring) (by ring) B

/-- **Klarner supermultiplicativity.** `concat` injects pairs of canonical
animals of sizes `m` and `n` into the canonical animals of size `m + n`;
`recLeft`/`recRight` are the left inverse that makes it an injection.

The `1 ≤ m`, `1 ≤ n` hypotheses are kept for the downstream interface (and
because the statement is false-flavoured without them — `a 0 = 0`) but are not
needed: a canonical animal is nonempty whatever its declared size, so at `m = 0`
there simply are none and both sides are `0`. -/
theorem a_supermul {m n : ℕ} (_hm : 1 ≤ m) (_hn : 1 ≤ n) : a m * a n ≤ a (m + n) := by
  classical
  have key : ∀ k : ℕ, a k = (canonicalAnimal_finite k).toFinset.card := fun k => by
    rw [a, Set.ncard_eq_toFinset_card _ (canonicalAnimal_finite k)]
  rw [key m, key n, key (m + n), ← Finset.card_product]
  refine Finset.card_le_card_of_injOn (fun z => concat z.1 z.2) ?_ ?_
  · intro z hz
    rw [Finset.mem_coe, Finset.mem_product] at hz
    simp only [Set.Finite.mem_toFinset, Set.mem_setOf_eq] at hz
    rw [Finset.mem_coe, Set.Finite.mem_toFinset]
    exact concat_canonical hz.1 hz.2
  · intro z hz w hw heq
    rw [Finset.mem_coe, Finset.mem_product] at hz hw
    simp only [Set.Finite.mem_toFinset, Set.mem_setOf_eq] at hz hw
    have hfun : concat z.1 z.2 = concat w.1 w.2 := heq
    have h1 : z.1 = w.1 := by
      rw [← recLeft_concat hz.1 hz.2, ← recLeft_concat hw.1 hw.2, hfun]
    have h2 : z.2 = w.2 := by
      rw [← recRight_concat hz.1 hz.2, ← recRight_concat hw.1 hw.2, hfun]
    exact Prod.ext h1 h2

/-! ## Fekete's ladder

`negLogA n = -log (a n)` is subadditive (that is supermultiplicativity of `a`
read through `log`) and `negLogA n / n` is bounded below (that is the
`UpperBound.lean` ceiling). Mathlib's `Subadditive.tendsto_lim` then supplies
the limit, and `Subadditive.lim_le_div` the "limit is the infimum" half that
turns into `a n ≤ lambda ^ n`. -/

/-- The exponential ceiling of `UpperBound.lean`, cast to `ℝ`. -/
theorem a_le_ratio_pow (k : ℕ) : (a k : ℝ) ≤ (3125 / 256 : ℝ) ^ k := by
  rcases Nat.eq_zero_or_pos k with rfl | hk
  · rw [a_zero]; norm_num
  have h1 : a k * 256 ^ k ≤ 3125 ^ k :=
    le_trans (Nat.mul_le_mul_right _ (a_le_choose k hk)) (choose_le_pow k)
  have h2 : ((a k : ℝ) * 256 ^ k) ≤ (3125 : ℝ) ^ k := by exact_mod_cast h1
  rw [div_pow, le_div_iff₀ (by positivity)]
  exact h2

/-- The sequence Fekete is applied to: `-log (a n)`. -/
noncomputable def negLogA (k : ℕ) : ℝ := -Real.log (a k)

/-- **Supermultiplicativity, read through `log`.** The degenerate cases `m = 0`
and `n = 0` are equalities: `a 0 = 0` and `Real.log 0 = 0`, so `negLogA 0 = 0`. -/
theorem logSeq_subadditive : Subadditive negLogA := by
  intro p q
  rcases Nat.eq_zero_or_pos p with rfl | hp
  · simp [negLogA, a_zero]
  rcases Nat.eq_zero_or_pos q with rfl | hq
  · simp [negLogA, a_zero]
  have h1 : (0 : ℝ) < a p := by exact_mod_cast one_le_a hp
  have h2 : (0 : ℝ) < a q := by exact_mod_cast one_le_a hq
  have hsm : ((a p : ℝ) * (a q : ℝ)) ≤ (a (p + q) : ℝ) := by
    exact_mod_cast a_supermul hp hq
  have hlog : Real.log ((a p : ℝ) * (a q : ℝ)) ≤ Real.log (a (p + q) : ℝ) :=
    Real.log_le_log (by positivity) hsm
  rw [Real.log_mul (ne_of_gt h1) (ne_of_gt h2)] at hlog
  simp only [negLogA]
  linarith

/-- The lower bound on `negLogA n / n` supplied by the exponential ceiling. -/
theorem logSeq_div_ge {k : ℕ} (hk : 1 ≤ k) :
    -Real.log (3125 / 256 : ℝ) ≤ negLogA k / k := by
  have hkR : (0 : ℝ) < k := by exact_mod_cast hk
  have hpos : (0 : ℝ) < a k := by exact_mod_cast one_le_a hk
  have hlog : Real.log (a k) ≤ k * Real.log (3125 / 256 : ℝ) := by
    calc Real.log (a k) ≤ Real.log ((3125 / 256 : ℝ) ^ k) :=
          Real.log_le_log hpos (a_le_ratio_pow k)
      _ = k * Real.log (3125 / 256 : ℝ) := by rw [Real.log_pow]
  rw [le_div_iff₀ hkR]
  simp only [negLogA]
  linarith

/-- `negLogA n / n` is bounded below, the hypothesis Fekete's lemma needs. -/
theorem logSeq_bddBelow : BddBelow (Set.range fun k : ℕ => negLogA k / k) := by
  refine ⟨-Real.log (3125 / 256 : ℝ), ?_⟩
  rintro x ⟨k, rfl⟩
  rcases Nat.eq_zero_or_pos k with rfl | hk
  · simp only [negLogA, a_zero, Nat.cast_zero, Real.log_zero, neg_zero, zero_div]
    have := Real.log_nonneg (by norm_num : (1 : ℝ) ≤ 3125 / 256)
    linarith
  · exact logSeq_div_ge hk

/-- **The growth constant of the polyplet sequence**, `λ = lim a(n)^{1/n}`,
built as `exp` of the negated Fekete limit of `negLogA`. -/
noncomputable def lambda : ℝ := Real.exp (-logSeq_subadditive.lim)

/-- `λ` is positive. -/
lemma lambda_pos : 0 < lambda := Real.exp_pos _

/-- **`λ` is the limit of `a(n)^{1/n}`.** -/
theorem lambda_tendsto :
    Filter.Tendsto (fun n => (a n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (𝓝 lambda) := by
  have h0 : Filter.Tendsto (fun k : ℕ => negLogA k / k) Filter.atTop
      (𝓝 logSeq_subadditive.lim) :=
    logSeq_subadditive.tendsto_lim logSeq_bddBelow
  have h2 : Filter.Tendsto (fun k : ℕ => Real.exp (-(negLogA k / k))) Filter.atTop (𝓝 lambda) :=
    (Real.continuous_exp.tendsto _).comp h0.neg
  refine h2.congr' ?_
  filter_upwards [Filter.eventually_ge_atTop 1] with k hk
  have hpos : (0 : ℝ) < a k := by exact_mod_cast one_le_a hk
  rw [Real.rpow_def_of_pos hpos]
  congr 1
  simp only [negLogA]
  ring

/-- **Fekete's supremum half:** `a n ≤ λⁿ` for every `n ≥ 1`. The Fekete limit
of a subadditive sequence is the infimum of `u n / n`, so `-lim` dominates
`log (a n) / n` at every `n`. -/
theorem a_le_lambda_pow {n : ℕ} (hn : 1 ≤ n) : (a n : ℝ) ≤ lambda ^ n := by
  have hpos : (0 : ℝ) < a n := by exact_mod_cast one_le_a hn
  have hn0 : n ≠ 0 := by omega
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  have hle : logSeq_subadditive.lim ≤ negLogA n / n :=
    logSeq_subadditive.lim_le_div logSeq_bddBelow hn0
  rw [le_div_iff₀ hnR] at hle
  simp only [negLogA] at hle
  calc (a n : ℝ) = Real.exp (Real.log (a n)) := (Real.exp_log hpos).symm
    _ ≤ Real.exp ((n : ℝ) * (-logSeq_subadditive.lim)) := Real.exp_le_exp.mpr (by linarith)
    _ = lambda ^ n := by rw [lambda]; exact Real.exp_nat_mul _ n

/-- **The upper bound `λ ≤ 5⁵/4⁴ = 3125/256`**, from the decision-tree ceiling
of `UpperBound.lean`. -/
theorem lambda_le : lambda ≤ 3125 / 256 := by
  have hbd : -Real.log (3125 / 256 : ℝ) ≤ logSeq_subadditive.lim := by
    refine ge_of_tendsto (logSeq_subadditive.tendsto_lim logSeq_bddBelow) ?_
    filter_upwards [Filter.eventually_ge_atTop 1] with k hk using logSeq_div_ge hk
  rw [lambda]
  calc Real.exp (-logSeq_subadditive.lim) ≤ Real.exp (Real.log (3125 / 256 : ℝ)) :=
        Real.exp_le_exp.mpr (by linarith)
    _ = 3125 / 256 := Real.exp_log (by norm_num)

/-- **The lower bound `3832 ≤ λ⁶`**, from the banked anchor `a 6 = 3832`. -/
theorem lambda_lb : (3832 : ℝ) ≤ lambda ^ 6 := by
  have h := a_le_lambda_pow (n := 6) (by norm_num)
  rw [a_6] at h
  exact_mod_cast h

/-- **The numeric lower bound `3.95 < λ`**: `3.95⁶ = 3798.24… < 3832 ≤ λ⁶`.
Together with `lambda_le` this is the bracket `3.95 < λ ≤ 3125/256`, i.e.
`3.95 < λ ≤ 12.207…`. -/
theorem lambda_gt : (3.95 : ℝ) < lambda := by
  by_contra hcon
  rw [not_lt] at hcon
  have h1 : lambda ^ 6 ≤ (3.95 : ℝ) ^ 6 := pow_le_pow_left₀ (le_of_lt lambda_pos) hcon 6
  have h2 := lambda_lb
  norm_num at h1
  linarith

/-! ## Axiom audit

Plain `#print axioms`; the `#guard_msgs`-wrapped versions are integrated into
the campaign audit point by the orchestrator. `a_supermul`, `lambda_tendsto`,
`a_le_lambda_pow` and `lambda_le` must carry the standard three; `lambda_lb` and
`lambda_gt` additionally carry the `native_decide` constant of the `a 6` anchor
they inherit from `Sequence.lean`. -/

#print axioms a_supermul
#print axioms lambda_tendsto
#print axioms a_le_lambda_pow
#print axioms lambda_le
#print axioms lambda_lb
#print axioms lambda_gt

end Polyplets
