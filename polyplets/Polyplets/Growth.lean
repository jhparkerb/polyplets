/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Subadditive
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Polyplets.Fekete
import Polyplets.UpperBound

/-!
# The growth constant `λ`: existence and a two-sided bracket

`Sequence.lean` names the sequence `a n` and `UpperBound.lean` bounds it above.
Neither says that the *growth rate* `λ = lim a(n)^{1/n}` — the constant the
paper quotes throughout — exists at all. This file builds it, from the two
halves of Fekete's argument:

* **Klarner supermultiplicativity** (`a_supermul`): `a m * a n ≤ a (m + n)`,
  proved by an explicit injection `concat` that welds two polyplets
  side by side across one king edge, together with the recovery maps
  (`recLeft`, `recRight`) that undo it;
* **Fekete's lemma**, from Mathlib's `Subadditive.tendsto_lim`, applied to
  `-log (a n)`, which is subadditive by supermultiplicativity and whose
  `-log (a n) / n` is bounded below by the `UpperBound.lean` ceiling. Since
  2026-08-06 that half is `Fekete.lean`'s, run against the instance
  `polypletFekete`; `a` supplies the three hypotheses and nothing else.

The payoff:

* `lambda_tendsto` : `a n ^ (1/n) → lambda`;
* `a_le_lambda_pow` : `a n ≤ lambda ^ n` (Fekete's limit-is-supremum half);
* `lambda_le` : `lambda ≤ 3125 / 256 = 5⁵/4⁴`;
* `lambda_gt_of_banked` : `311/50 = 6.22 < lambda`, **conditional** on the
  banked hypothesis `a 40 = 56749893611764175164545926946127`.

## The concatenation injection

Given polyplets `A` (`m` cells) and `B` (`n` cells), let `w = maxX A` be `A`'s
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
and exactly `m` at `w + 1`. Splitting at the cut and anchoring — in `y` only
for the left half, in both coordinates for the right — returns `A` and `B`
(`recLeft_concat`, `recRight_concat`).
-/

namespace Polyplets

open scoped Topology

/-! ## Translating a cell set

Everything in the concatenation is a `translate` (`Universal/Defs.lean`;
invariance of the king structure in `Defs.lean`); `mem_translate_mk` is its
membership in the component form every proof below wants. -/

/-- Membership in a translate, in component form (no projections of literal
pairs left over). -/
lemma mem_translate_mk {e d : ℤ} {q : ℤ × ℤ} {S : Finset (ℤ × ℤ)} :
    q ∈ translate (e, d) S ↔ ∃ p ∈ S, q.1 = p.1 + e ∧ q.2 = p.2 + d := by
  rw [translate, Finset.mem_image]
  constructor
  · rintro ⟨p, hp, rfl⟩
    exact ⟨p, hp, rfl, rfl⟩
  · rintro ⟨p, hp, h1, h2⟩
    exact ⟨p, hp, Prod.ext h1.symm h2.symm⟩

/-- Two translations compose. -/
lemma translate_mk_translate_mk (e d e' d' : ℤ) (S : Finset (ℤ × ℤ)) :
    translate (e', d') (translate (e, d) S) = translate (e + e', d + d') S := by
  rw [translate_translate, Prod.mk_add_mk]

/-- **Translation is undone by the opposite translation.** Stated with the
cancellation as hypotheses so that it applies without any `-0`/`0` mismatch. -/
lemma translate_mk_cancel {e d e' d' : ℤ} (he : e + e' = 0) (hd : d + d' = 0)
    (S : Finset (ℤ × ℤ)) : translate (e', d') (translate (e, d) S) = S := by
  rw [translate_mk_translate_mk, he, hd]
  exact translate_zero S

/-! ## `a n ≥ 1`: the bar witness

The horizontal bar of `n` cells is a polyplet, so no `a n` with `n ≥ 1`
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

/-- The bar is a polyplet. -/
lemma bar_isPolyplet {n : ℕ} (hn : 1 ≤ n) : IsPolyplet n (bar n) := by
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
  exact (Set.ncard_pos (polyplets_finite n)).mpr ⟨bar n, bar_isPolyplet hn⟩

/-- **`a 0 = 0`.** The empty set is the only `0`-cell `Finset`, and it fails the
anchoring clauses; so supermultiplicativity has to start at `1`. -/
theorem a_zero : a 0 = 0 := by
  have hempty : polyplets 0 = ∅ := by
    ext S
    simp only [mem_polyplets, Set.mem_empty_iff_false, iff_false]
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

/-- `maxX` is attained on a polyplet. -/
lemma maxX_mem {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) :
    ∃ p ∈ S, p.1 = (maxX S : ℤ) := by
  obtain ⟨p0, hp0, -⟩ := hS.anchored.x_zero
  obtain ⟨pm, hpm, hpme⟩ :=
    Finset.exists_mem_eq_sup S ⟨p0, hp0⟩ (fun p : ℤ × ℤ => p.1.toNat)
  refine ⟨pm, hpm, ?_⟩
  have hnn := hS.anchored.x_nonneg pm hpm
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

/-- **The concatenation of two polyplets**: `B` moved one column to the
right of `A`, both lifted so their bridge cells share the height `cTop A B`. -/
def concat (A B : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  translate (0, liftA A B) A ∪ translate ((maxX A : ℤ) + 1, liftB A B) B

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
    (hq : q ∈ translate (0, liftA A B) A) : q.1 ≤ (maxX A : ℤ) := by
  obtain ⟨p, hp, h1, -⟩ := mem_translate_mk.mp hq
  have := le_maxX hp (hA p hp)
  omega

/-- The right half sits strictly right of column `maxX A`. -/
lemma concat_right_x_ge {A B : Finset (ℤ × ℤ)} (hB : ∀ p ∈ B, 0 ≤ p.1) {q : ℤ × ℤ}
    (hq : q ∈ translate ((maxX A : ℤ) + 1, liftB A B) B) : (maxX A : ℤ) + 1 ≤ q.1 := by
  obtain ⟨p, hp, h1, -⟩ := mem_translate_mk.mp hq
  have := hB p hp
  omega

/-- The two halves are disjoint. -/
lemma concat_disjoint {A B : Finset (ℤ × ℤ)} (hA : ∀ p ∈ A, 0 ≤ p.1) (hB : ∀ p ∈ B, 0 ≤ p.1) :
    Disjoint (translate (0, liftA A B) A) (translate ((maxX A : ℤ) + 1, liftB A B) B) := by
  rw [Finset.disjoint_left]
  intro q hq1 hq2
  have h1 := concat_left_x_le hA hq1
  have h2 := concat_right_x_ge (A := A) hB hq2
  omega

/-- The left bridge cell: the top of `A`'s rightmost column, lifted. -/
lemma bridgeA_mem {m : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A) :
    ((maxX A : ℤ), cTop A B) ∈ translate (0, liftA A B) A := by
  have hmem : ((maxX A : ℤ), (colTop A (maxX A : ℤ) : ℤ)) ∈ A :=
    colTop_mem hA.anchored.y_nonneg (maxX_mem hA)
  refine mem_translate_mk.mpr ⟨_, hmem, ?_, ?_⟩
  · change (maxX A : ℤ) = (maxX A : ℤ) + 0
    ring
  · change cTop A B = (colTop A (maxX A : ℤ) : ℤ) + liftA A B
    rw [liftA]; ring

/-- The right bridge cell: the top of `B`'s column `0`, shifted and lifted. -/
lemma bridgeB_mem {n : ℕ} {A B : Finset (ℤ × ℤ)} (hB : IsPolyplet n B) :
    ((maxX A : ℤ) + 1, cTop A B) ∈ translate ((maxX A : ℤ) + 1, liftB A B) B := by
  have hmem : ((0 : ℤ), (colTop B 0 : ℤ)) ∈ B :=
    colTop_mem hB.anchored.y_nonneg hB.anchored.x_zero
  refine mem_translate_mk.mpr ⟨_, hmem, ?_, ?_⟩
  · change (maxX A : ℤ) + 1 = (0 : ℤ) + ((maxX A : ℤ) + 1)
    ring
  · change cTop A B = (colTop B 0 : ℤ) + liftB A B
    rw [liftB]; ring

/-- **The concatenation is a polyplet of `m + n` cells.** Disjointness gives the
count, the bridge edge gives connectivity, and the lifts were chosen exactly so
that both anchoring clauses survive. -/
theorem concat_isPolyplet {m n : ℕ} {A B : Finset (ℤ × ℤ)}
    (hA : IsPolyplet m A) (hB : IsPolyplet n B) :
    IsPolyplet (m + n) (concat A B) := by
  have hcard : (concat A B).card = m + n := by
    rw [concat,
      Finset.card_union_of_disjoint (concat_disjoint hA.anchored.x_nonneg hB.anchored.x_nonneg),
      card_translate, card_translate, hA.card, hB.card]
  have hconn : KingConnected (concat A B) := by
    rw [concat]
    refine kingConnected_union_of_adj (kingConnected_translate _ hA.conn)
      (kingConnected_translate _ hB.conn) (bridgeA_mem hA) (bridgeB_mem hB) ?_
    refine ⟨by simp only [ne_eq, Prod.mk.injEq]; omega, ?_, ?_⟩
    · change |(maxX A : ℤ) - ((maxX A : ℤ) + 1)| ≤ 1
      rw [abs_le]; omega
    · change |cTop A B - cTop A B| ≤ 1
      simp
  refine ⟨hcard, hconn, ?_, ?_, ?_, ?_⟩
  · intro q hq
    rw [concat, Finset.mem_union] at hq
    rcases hq with hq | hq
    · obtain ⟨p, hp, h1, -⟩ := mem_translate_mk.mp hq
      have hx := hA.anchored.x_nonneg p hp
      omega
    · have hx := concat_right_x_ge (A := A) hB.anchored.x_nonneg hq
      have hw : (0 : ℤ) ≤ (maxX A : ℤ) := Int.natCast_nonneg _
      omega
  · obtain ⟨p, hp, hp1⟩ := hA.anchored.x_zero
    refine ⟨(p.1, p.2 + liftA A B), ?_, hp1⟩
    rw [concat]
    exact Finset.mem_union_left _ (mem_translate_mk.mpr ⟨p, hp, by change p.1 = p.1 + 0; ring, rfl⟩)
  · intro q hq
    rw [concat, Finset.mem_union] at hq
    rcases hq with hq | hq
    · obtain ⟨p, hp, -, h2⟩ := mem_translate_mk.mp hq
      have hy := hA.anchored.y_nonneg p hp
      have hl := liftA_nonneg A B
      omega
    · obtain ⟨p, hp, -, h2⟩ := mem_translate_mk.mp hq
      have hy := hB.anchored.y_nonneg p hp
      have hl := liftB_nonneg A B
      omega
  · rcases lift_eq_zero A B with h | h
    · obtain ⟨p, hp, hp2⟩ := hA.anchored.y_zero
      refine ⟨(p.1, p.2 + liftA A B), ?_, ?_⟩
      · rw [concat]
        exact Finset.mem_union_left _
          (mem_translate_mk.mpr ⟨p, hp, by change p.1 = p.1 + 0; ring, rfl⟩)
      · change p.2 + liftA A B = 0
        omega
    · obtain ⟨p, hp, hp2⟩ := hB.anchored.y_zero
      refine ⟨(p.1 + ((maxX A : ℤ) + 1), p.2 + liftB A B), ?_, ?_⟩
      · rw [concat]
        exact Finset.mem_union_right _ (mem_translate_mk.mpr ⟨p, hp, rfl, rfl⟩)
      · change p.2 + liftB A B = 0
        omega

/-! ## Recovery: the concatenation is injective

The cut is located by counting, then each half is anchored — the left half in
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

/-- **A translate of a polyplet remembers its vertical offset.** -/
lemma baseY_shift {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) {e d : ℤ}
    (hd : 0 ≤ d) : (baseY (translate (e, d) S) : ℤ) = d := by
  rw [baseY]
  have hmem : d.toNat ∈ {k : ℕ | ∃ p ∈ translate (e, d) S, p.2 = (k : ℤ)} := by
    obtain ⟨p₀, hp₀, hp₀2⟩ := hS.anchored.y_zero
    exact ⟨(p₀.1 + e, p₀.2 + d), mem_translate_mk.mpr ⟨p₀, hp₀, rfl, rfl⟩,
      by change p₀.2 + d = (d.toNat : ℤ); omega⟩
  have hle : sInf {k : ℕ | ∃ p ∈ translate (e, d) S, p.2 = (k : ℤ)} ≤ d.toNat :=
    Nat.sInf_le hmem
  obtain ⟨p, hp, hp2⟩ := Nat.sInf_mem (⟨_, hmem⟩ :
    {k : ℕ | ∃ p ∈ translate (e, d) S, p.2 = (k : ℤ)}.Nonempty)
  obtain ⟨q, hq, -, hq2⟩ := mem_translate_mk.mp hp
  have hy := hS.anchored.y_nonneg q hq
  omega

/-- **A translate of a polyplet remembers its horizontal offset.** -/
lemma baseX_shift {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) {e d : ℤ}
    (he : 0 ≤ e) : (baseX (translate (e, d) S) : ℤ) = e := by
  rw [baseX]
  have hmem : e.toNat ∈ {k : ℕ | ∃ p ∈ translate (e, d) S, p.1 = (k : ℤ)} := by
    obtain ⟨p₀, hp₀, hp₀1⟩ := hS.anchored.x_zero
    exact ⟨(p₀.1 + e, p₀.2 + d), mem_translate_mk.mpr ⟨p₀, hp₀, rfl, rfl⟩,
      by change p₀.1 + e = (e.toNat : ℤ); omega⟩
  have hle : sInf {k : ℕ | ∃ p ∈ translate (e, d) S, p.1 = (k : ℤ)} ≤ e.toNat :=
    Nat.sInf_le hmem
  obtain ⟨p, hp, hp1⟩ := Nat.sInf_mem (⟨_, hmem⟩ :
    {k : ℕ | ∃ p ∈ translate (e, d) S, p.1 = (k : ℤ)}.Nonempty)
  obtain ⟨q, hq, hq1, -⟩ := mem_translate_mk.mp hp
  have hx := hS.anchored.x_nonneg q hq
  omega

/-- The left part of a concatenation, cut at the right place, is the lifted `A`. -/
lemma leftOf_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A)
    (hB : IsPolyplet n B) :
    leftOf (concat A B) ((maxX A : ℤ) + 1) = translate (0, liftA A B) A := by
  ext q
  rw [leftOf, Finset.mem_filter, concat, Finset.mem_union]
  constructor
  · rintro ⟨hq | hq, hlt⟩
    · exact hq
    · have := concat_right_x_ge (A := A) hB.anchored.x_nonneg hq
      omega
  · intro hq
    exact ⟨Or.inl hq, by have := concat_left_x_le hA.anchored.x_nonneg hq; omega⟩

/-- The right part of a concatenation, cut at the right place, is the shifted `B`. -/
lemma rightOf_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A)
    (hB : IsPolyplet n B) :
    rightOf (concat A B) ((maxX A : ℤ) + 1) = translate ((maxX A : ℤ) + 1, liftB A B) B := by
  ext q
  rw [rightOf, Finset.mem_filter, concat, Finset.mem_union]
  constructor
  · rintro ⟨hq | hq, hge⟩
    · have := concat_left_x_le hA.anchored.x_nonneg hq
      omega
    · exact hq
  · intro hq
    exact ⟨Or.inr hq, concat_right_x_ge (A := A) hB.anchored.x_nonneg hq⟩

/-- **The cut is where the construction put it.** At `k = maxX A + 1` the left
count is exactly `m`; at any `k ≤ maxX A` the left part misses `A`'s bridge cell
`(maxX A, cTop A B)`, so it is a proper subset of the lifted `A` and its count is
`< m`. Hence the least `k` with left count `m` is `maxX A + 1`. -/
lemma cutAt_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A)
    (hB : IsPolyplet n B) : cutAt (concat A B) m = maxX A + 1 := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  have hmem : (maxX A + 1) ∈ {k : ℕ | (leftOf (concat A B) (k : ℤ)).card = m} := by
    change (leftOf (concat A B) ((maxX A + 1 : ℕ) : ℤ)).card = m
    rw [hcast, leftOf_concat hA hB, card_translate, hA.card]
  have hlow : ∀ k : ℕ, (k : ℤ) ≤ (maxX A : ℤ) → (leftOf (concat A B) (k : ℤ)).card < m := by
    intro k hk
    have hsub : leftOf (concat A B) (k : ℤ) ⊆ translate (0, liftA A B) A := by
      intro q hq
      rw [leftOf, Finset.mem_filter, concat, Finset.mem_union] at hq
      rcases hq.1 with h | h
      · exact h
      · have h1 := concat_right_x_ge (A := A) hB.anchored.x_nonneg h
        have h2 : q.1 < (k : ℤ) := hq.2
        omega
    have hbr : ((maxX A : ℤ), cTop A B) ∈ translate (0, liftA A B) A := bridgeA_mem hA
    have hbrn : ((maxX A : ℤ), cTop A B) ∉ leftOf (concat A B) (k : ℤ) := by
      rw [leftOf, Finset.mem_filter]
      rintro ⟨-, h⟩
      have h' : (maxX A : ℤ) < (k : ℤ) := h
      omega
    calc (leftOf (concat A B) (k : ℤ)).card
        < (translate (0, liftA A B) A).card :=
          Finset.card_lt_card ((Finset.ssubset_iff_of_subset hsub).mpr ⟨_, hbr, hbrn⟩)
      _ = m := by rw [card_translate, hA.card]
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

/-- Recovering the left factor: cut, then anchor vertically. -/
noncomputable def recLeft (C : Finset (ℤ × ℤ)) (m : ℕ) : Finset (ℤ × ℤ) :=
  translate (0, -(baseY (leftOf C (cutAt C m : ℤ)) : ℤ)) (leftOf C (cutAt C m : ℤ))

/-- Recovering the right factor: cut, then anchor in both coordinates. -/
noncomputable def recRight (C : Finset (ℤ × ℤ)) (m : ℕ) : Finset (ℤ × ℤ) :=
  translate (-(baseX (rightOf C (cutAt C m : ℤ)) : ℤ), -(baseY (rightOf C (cutAt C m : ℤ)) : ℤ))
    (rightOf C (cutAt C m : ℤ))

/-- `recLeft` inverts `concat` on the left. -/
theorem recLeft_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A)
    (hB : IsPolyplet n B) : recLeft (concat A B) m = A := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  rw [recLeft, cutAt_concat hA hB, hcast, leftOf_concat hA hB,
    baseY_shift hA (liftA_nonneg A B)]
  exact translate_mk_cancel (by ring) (by ring) A

/-- `recRight` inverts `concat` on the right. -/
theorem recRight_concat {m n : ℕ} {A B : Finset (ℤ × ℤ)} (hA : IsPolyplet m A)
    (hB : IsPolyplet n B) : recRight (concat A B) m = B := by
  have hcast : ((maxX A + 1 : ℕ) : ℤ) = (maxX A : ℤ) + 1 := by push_cast; ring
  have hw : (0 : ℤ) ≤ (maxX A : ℤ) + 1 := by
    have := Int.natCast_nonneg (maxX A); omega
  rw [recRight, cutAt_concat hA hB, hcast, rightOf_concat hA hB,
    baseX_shift hB hw, baseY_shift hB (liftB_nonneg A B)]
  exact translate_mk_cancel (by ring) (by ring) B

/-- **Klarner supermultiplicativity.** `concat` injects pairs of polyplets
of sizes `m` and `n` into the polyplets of size `m + n`;
`recLeft`/`recRight` are the left inverse that makes it an injection.

Unconditional: at `m = 0` the left side is `a 0 * a n = 0` and the
inequality degenerates to `0 ≤ a n`. (The outworks brief pinned a `1 ≤ m`,
`1 ≤ n` signature; the hypotheses were dead and dropped 2026-07-31.) -/
theorem a_supermul {m n : ℕ} : a m * a n ≤ a (m + n) := by
  classical
  have key : ∀ k : ℕ, a k = (polyplets_finite k).toFinset.card := fun k => by
    rw [a, Set.ncard_eq_toFinset_card _ (polyplets_finite k)]
  rw [key m, key n, key (m + n), ← Finset.card_product]
  refine Finset.card_le_card_of_injOn (fun z => concat z.1 z.2) ?_ ?_
  · intro z hz
    rw [Finset.mem_coe, Finset.mem_product] at hz
    simp only [Set.Finite.mem_toFinset, mem_polyplets] at hz
    rw [Finset.mem_coe, Set.Finite.mem_toFinset]
    exact concat_isPolyplet hz.1 hz.2
  · intro z hz w hw heq
    rw [Finset.mem_coe, Finset.mem_product] at hz hw
    simp only [Set.Finite.mem_toFinset, mem_polyplets] at hz hw
    have hfun : concat z.1 z.2 = concat w.1 w.2 := heq
    have h1 : z.1 = w.1 := by
      rw [← recLeft_concat hz.1 hz.2, ← recLeft_concat hw.1 hw.2, hfun]
    have h2 : z.2 = w.2 := by
      rw [← recRight_concat hz.1 hz.2, ← recRight_concat hw.1 hw.2, hfun]
    exact Prod.ext h1 h2

/-! ## Fekete's ladder

`-log (a n)` is subadditive (that is supermultiplicativity of `a` read through
`log`) and `-log (a n) / n` is bounded below (that is the `UpperBound.lean`
ceiling). Mathlib's `Subadditive.tendsto_lim` then supplies the limit, and
`Subadditive.lim_le_div` the "limit is the infimum" half that turns into
`a n ≤ lambda ^ n`.

The ladder itself lives in `Fekete.lean`. It asks a sequence for exactly the
three facts used here: supermultiplicative, positive from `1` on, under an
exponential ceiling. From those it runs `negLog → subadditive → bddBelow →
growth → tendsto → le_growth_pow` once. `λ` is one instance of it; the
staircase constant `µ` of `StairGrowth.lean` is the other. Everything below
this point is the instance and five wrappers. -/

/-- The exponential ceiling of `UpperBound.lean`, cast to `ℝ`. -/
theorem a_le_ratio_pow (k : ℕ) : (a k : ℝ) ≤ (3125 / 256 : ℝ) ^ k := by
  rcases Nat.eq_zero_or_pos k with rfl | hk
  · rw [a_zero]; norm_num
  have h1 : a k * 256 ^ k ≤ 3125 ^ k :=
    le_trans (Nat.mul_le_mul_right _ (a_le_choose k hk)) (choose_le_pow k)
  have h2 : ((a k : ℝ) * 256 ^ k) ≤ (3125 : ℝ) ^ k := by exact_mod_cast h1
  rw [div_pow, le_div_iff₀ (by positivity)]
  exact h2

/-- **The polyplet sequence as a Fekete instance.** Klarner's injection is
`supermul`, `Sequence.lean`'s `one_le_a` is `one_le`, and the decision-tree
ceiling is `ceiling`. Nothing else about `a` is used downstream of this point. -/
noncomputable def polypletFekete : Fekete where
  f := a
  c := 3125 / 256
  one_le_c := by norm_num
  supermul := fun _ _ => a_supermul
  one_le := one_le_a
  ceiling := a_le_ratio_pow

/-- **The growth constant of the polyplet sequence**, `λ = lim a(n)^{1/n}`. -/
noncomputable def lambda : ℝ := polypletFekete.growth

/-- `λ` is positive. -/
lemma lambda_pos : 0 < lambda := polypletFekete.growth_pos

/-- **`λ` is the limit of `a(n)^{1/n}`.** -/
theorem lambda_tendsto :
    Filter.Tendsto (fun n => (a n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (𝓝 lambda) :=
  polypletFekete.tendsto

/-- **Fekete's supremum half:** `a n ≤ λⁿ` for every `n ≥ 1`. The Fekete limit
of a subadditive sequence is the infimum of `u n / n`, so `-lim` dominates
`log (a n) / n` at every `n`. -/
theorem a_le_lambda_pow {n : ℕ} (hn : 1 ≤ n) : (a n : ℝ) ≤ lambda ^ n :=
  polypletFekete.le_growth_pow hn

/-- **The upper bound `λ ≤ 5⁵/4⁴ = 3125/256`**, from the decision-tree ceiling
of `UpperBound.lean`. -/
theorem lambda_le : lambda ≤ 3125 / 256 := polypletFekete.growth_le

/-! ## The conditional lower bound from the banked final term

The project's banked table reaches `a 40`, and Fekete's `a n ≤ λⁿ` turns
*any* banked term into a lower bound for `λ`. Taking the banked value as an
explicit hypothesis, as `Grand/PinAll.lean` takes its enumerated cells, keeps the
computation outside the kernel and visible in the statement. (An
unconditional `3.95 < λ` from the `native_decide` fact `a 6 = 3832` was
removed 2026-10-12 with that fact.) -/

/-- **The conditional lower bound `6.22 < λ`, given the banked final term.**
`a 40 = 56749893611764175164545926946127` is the last term of the banked
triangle (`results/triangle.txt`, provenance `results/ns_a40/PROVENANCE.md`);
it enters here as a hypothesis, not as a computation. From it,
`(311/50)⁴⁰ = 6.22⁴⁰ < a 40 ≤ λ⁴⁰` — an exact integer comparison,
`311⁴⁰ < 56749893611764175164545926946127 · 50⁴⁰` — and `x ↦ x⁴⁰` is strictly
monotone on `[0, ∞)`, so `6.22 < λ`.

The constant is close to sharp for this `n`: `a 40 ^ (1/40) = 6.22084…`, so
`6.23` is already false. Note the conditionality is real — the hypothesis is a
single-source value (the top of the table is kink-engine-only; see
`polyplets/README.md`'s anchor-provenance discussion), and the bound is still
weaker than the unformalized strip ladder. -/
theorem lambda_gt_of_banked (h : a 40 = 56749893611764175164545926946127) :
    (311 / 50 : ℝ) < lambda := by
  have hle : ((56749893611764175164545926946127 : ℕ) : ℝ) ≤ lambda ^ 40 := by
    have := a_le_lambda_pow (n := 40) (by norm_num)
    rwa [h] at this
  have hpow : ((311 / 50 : ℝ)) ^ 40 < lambda ^ 40 := by
    refine lt_of_lt_of_le ?_ hle
    norm_num
  exact lt_of_pow_lt_pow_left₀ 40 (le_of_lt lambda_pos) hpow

end Polyplets
