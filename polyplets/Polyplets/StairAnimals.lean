/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.GroupWithZero.Nat
import Mathlib.Data.Nat.Basic
import Mathlib.Order.RelClasses

/-!
# Staircase polyplets: the column-join is injective at fixed area

`results/subclasses.md` Lemma 3, and B1 of `docs/publication.md`.

A *staircase polyplet* is a polyplet whose column intervals have both
boundaries nondecreasing (A225114 in OEIS; the middle block of the HV-convex
phase factorisation). Up to translation it is a nonempty list of columns
`(h, d)`, where `h` is the column's height and `d` the offset of its bottom
above the previous column's bottom, subject to

* `1 ≤ h` — columns are nonempty;
* `d ≤ p` — the columns are king-adjacent, `p` the previous height;
* `p ≤ h + d` — the tops do not drop.

The content of Lemma 3 is that joining two of them with the offset
`d = max(0, p − h')` lands back in the class and is **injective once the two
areas are fixed**: column areas are positive, so the prefix of total area `i` is
unique and no split index has to be carried alongside the join. This file proves
exactly that — `join_isStaircase`, `area_join`, `cut_join` — which is the combinatorial
core of `M i * M j ≤ M (i + j)`.

The counting layer on top of this — `M n`, `M i * M j ≤ M (i + j)`, and the
growth constant `µ` — is `StairGrowth.lean`, which reuses the Fekete ladder of
`Fekete.lean` rather than transcribing `Growth.lean`'s. What is here is the
combinatorial content: the join, the cut, and the injectivity.
-/

namespace Polyplets.Staircase

/-- A column: its height, and the offset of its bottom above the previous
column's bottom. -/
abbrev Column := ℕ × ℕ

/-- `ValidFrom p l`: `l` is a legal continuation to the right of a column of
height `p`. -/
def ValidFrom : ℕ → List Column → Prop
  | _, [] => True
  | p, c :: t => 1 ≤ c.1 ∧ c.2 ≤ p ∧ p ≤ c.1 + c.2 ∧ ValidFrom c.1 t

/-- A staircase animal: nonempty, first offset pinned to `0` (the translation
quotient), and every later column legal against its predecessor. -/
def IsStaircase : List Column → Prop
  | [] => False
  | c :: t => 1 ≤ c.1 ∧ c.2 = 0 ∧ ValidFrom c.1 t

/-- Area = total number of cells. -/
def area (l : List Column) : ℕ := (l.map Prod.fst).sum

/-- The height of the last column (`0` on the empty list, which `IsStaircase` excludes). -/
def lastHeight : List Column → ℕ
  | [] => 0
  | [c] => c.1
  | _ :: t => lastHeight t

/-- Re-anchor: zero the first column's offset, undoing a join's translation. -/
def norm : List Column → List Column
  | [] => []
  | c :: t => (c.1, 0) :: t

/-- The column-join: translate `y` so that its first column sits at offset
`max(0, lastHeight x − h')`, then concatenate. Truncated subtraction *is* the
`max(0, ·)`. -/
def join (x y : List Column) : List Column :=
  match y with
  | [] => x
  | c :: t => x ++ (c.1, lastHeight x - c.1) :: t

/-- Recover the two factors: walk the columns until the cumulative area reaches
`i`. Well defined because every column has positive height, so the prefix of
area exactly `i` is unique. -/
def cut : ℕ → List Column → List Column × List Column
  | _, [] => ([], [])
  | i, c :: t =>
      if i ≤ c.1 then ([c], t)
      else ((c :: (cut (i - c.1) t).1), (cut (i - c.1) t).2)

@[simp] theorem area_nil : area [] = 0 := rfl

@[simp] theorem area_cons (c : Column) (t : List Column) : area (c :: t) = c.1 + area t := rfl

@[simp] theorem area_append (x y : List Column) : area (x ++ y) = area x + area y := by
  induction x with
  | nil => simp
  | cons c t ih => simp [area_cons, ih, Nat.add_assoc]

/-- Appending a legal continuation to a valid animal keeps `ValidFrom`. -/
theorem validFrom_append {p : ℕ} : ∀ {x : List Column} {y : List Column},
    ValidFrom p x → x ≠ [] → ValidFrom (lastHeight x) y → ValidFrom p (x ++ y)
  | [], _, _, h, _ => absurd rfl h
  | [c], y, hx, _, hy => by
      refine ⟨hx.1, hx.2.1, hx.2.2.1, ?_⟩
      simpa [lastHeight] using hy
  | c :: c' :: t, y, hx, _, hy => by
      refine ⟨hx.1, hx.2.1, hx.2.2.1, ?_⟩
      have : ValidFrom (lastHeight (c' :: t)) y := by simpa [lastHeight] using hy
      exact validFrom_append hx.2.2.2 (by simp) this

/-- A valid animal is nonempty. -/
theorem IsStaircase.exists_cons {x : List Column} (hx : IsStaircase x) : ∃ e s, x = e :: s := by
  cases x with
  | nil => exact hx.elim
  | cons e s => exact ⟨e, s, rfl⟩

/-- A valid animal is a legal continuation of its own first column's height
(its first offset is `0`). -/
theorem validFrom_of_isStaircase {e : Column} {s : List Column} (hx : IsStaircase (e :: s)) :
    ValidFrom e.1 (e :: s) :=
  ⟨hx.1, by have := hx.2.1; omega, by omega, hx.2.2⟩

/-- **The join's step is legal.** `d = lastHeight x - h'` is `max(0, lastHeight x − h')`
in `ℕ`, and both constraints it has to meet — `d ≤ lastHeight x` and
`lastHeight x ≤ h' + d` — hold in each of the two cases. -/
theorem validFrom_join_step (x : List Column) {c : Column} {t : List Column}
    (hy : IsStaircase (c :: t)) :
    ValidFrom (lastHeight x) ((c.1, lastHeight x - c.1) :: t) :=
  ⟨hy.1, Nat.sub_le _ _, by omega, hy.2.2⟩

/-- **The join lands in the class.** -/
theorem join_isStaircase {x y : List Column} (hx : IsStaircase x) (hy : IsStaircase y) :
    IsStaircase (join x y) := by
  obtain ⟨c, t, rfl⟩ := hy.exists_cons
  obtain ⟨e, s, rfl⟩ := hx.exists_cons
  exact ⟨hx.1, hx.2.1,
    (validFrom_append (validFrom_of_isStaircase hx) (by simp) (validFrom_join_step _ hy)).2.2.2⟩

@[simp] theorem area_join (x y : List Column) : area (join x y) = area x + area y := by
  cases y with
  | nil => simp [join, area]
  | cons c t => simp [join, area_cons]

/-- **The cut inverts the join at fixed area.** Walking `x ++ z` until the
cumulative area reaches `area x` returns exactly `x` and `z`, because every
column of `x` is nonempty and `z`'s columns are too. -/
theorem cut_append : ∀ {x : List Column} {z : List Column} {p : ℕ},
    ValidFrom p x → x ≠ [] → ValidFrom (lastHeight x) z → z ≠ [] →
    cut (area x) (x ++ z) = (x, z)
  | [], _, _, _, h, _, _ => absurd rfl h
  | [c], z, p, hx, _, hz, hznil => by
      have h1 : 1 ≤ c.1 := hx.1
      simp [cut, area_cons, area_nil]
  | c :: c' :: t, z, p, hx, _, hz, hznil => by
      have h1 : 1 ≤ c'.1 := hx.2.2.2.1
      have hgt : ¬ (area (c :: c' :: t) ≤ c.1) := by
        simp only [area_cons]; omega
      have hrec : cut (area (c' :: t)) ((c' :: t) ++ z) = (c' :: t, z) :=
        cut_append hx.2.2.2 (by simp) (by simpa [lastHeight] using hz) hznil
      rw [List.cons_append, cut, if_neg hgt]
      simp only [area_cons, Nat.add_sub_cancel_left] at hrec ⊢
      rw [hrec]

/-- The join's second factor, anchored, is `y` again. -/
theorem cut_join {x y : List Column} (hx : IsStaircase x) (hy : IsStaircase y) :
    (cut (area x) (join x y)).1 = x ∧ norm (cut (area x) (join x y)).2 = y := by
  obtain ⟨c, t, rfl⟩ := hy.exists_cons
  obtain ⟨e, s, rfl⟩ := hx.exists_cons
  rw [show join (e :: s) (c :: t) = (e :: s) ++ (c.1, lastHeight (e :: s) - c.1) :: t from rfl,
    cut_append (validFrom_of_isStaircase hx) (by simp) (validFrom_join_step _ hy) (by simp)]
  refine ⟨rfl, ?_⟩
  simp only [norm, List.cons.injEq, and_true]
  exact Prod.ext rfl hy.2.1.symm

/-- **Injectivity at fixed areas**: the pair is recovered from the join alone,
so distinct pairs of equal areas have distinct joins. This is the step
`results/subclasses.md` Lemma 3 turns into `M i * M j ≤ M (i + j)`. -/
theorem join_injOn {x y x' y' : List Column} (hx : IsStaircase x) (hy : IsStaircase y)
    (hx' : IsStaircase x') (hy' : IsStaircase y') (harea : area x = area x')
    (h : join x y = join x' y') : x = x' ∧ y = y' := by
  have h1 := cut_join hx hy
  have h2 := cut_join hx' hy'
  rw [h, harea] at h1
  exact ⟨h1.1.symm.trans h2.1, h1.2.symm.trans h2.2⟩

end Polyplets.Staircase
