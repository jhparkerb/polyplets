/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib

/-!
# Staircase king animals: the column-join is injective at fixed area

`results/hv-growth-sandwich.md` Lemma 3, and B1 of `docs/sortie-publication-plan.md`.

A *staircase king animal* is a king animal whose column intervals have both
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
exactly that — `join_valid`, `area_join`, `cut_join` — which is the combinatorial
core of `M i * M j ≤ M (i + j)`.

The counting layer on top of this — `M n`, `M i * M j ≤ M (i + j)`, and the
growth constant `µ` — is `StairGrowth.lean`, which reuses the Fekete ladder of
`Fekete.lean` rather than transcribing `Growth.lean`'s. What is here is the
combinatorial content: the join, the cut, and the injectivity.
-/

namespace Polyplets.Stair

/-- A column: its height, and the offset of its bottom above the previous
column's bottom. -/
abbrev Col := ℕ × ℕ

/-- `ValidFrom p l`: `l` is a legal continuation to the right of a column of
height `p`. -/
def ValidFrom : ℕ → List Col → Prop
  | _, [] => True
  | p, c :: t => 1 ≤ c.1 ∧ c.2 ≤ p ∧ p ≤ c.1 + c.2 ∧ ValidFrom c.1 t

/-- A staircase animal: nonempty, first offset pinned to `0` (the translation
quotient), and every later column legal against its predecessor. -/
def Valid : List Col → Prop
  | [] => False
  | c :: t => 1 ≤ c.1 ∧ c.2 = 0 ∧ ValidFrom c.1 t

/-- Area = total number of cells. -/
def area (l : List Col) : ℕ := (l.map Prod.fst).sum

/-- The height of the last column (`0` on the empty list, which `Valid` excludes). -/
def lastH : List Col → ℕ
  | [] => 0
  | [c] => c.1
  | _ :: t => lastH t

/-- Re-anchor: zero the first column's offset, undoing a join's translation. -/
def norm : List Col → List Col
  | [] => []
  | c :: t => (c.1, 0) :: t

/-- The column-join: translate `y` so that its first column sits at offset
`max(0, lastH x − h')`, then concatenate. Truncated subtraction *is* the
`max(0, ·)`. -/
def join (x y : List Col) : List Col :=
  match y with
  | [] => x
  | c :: t => x ++ (c.1, lastH x - c.1) :: t

/-- Recover the two factors: walk the columns until the cumulative area reaches
`i`. Well defined because every column has positive height, so the prefix of
area exactly `i` is unique. -/
def cut : ℕ → List Col → List Col × List Col
  | _, [] => ([], [])
  | i, c :: t =>
      if i ≤ c.1 then ([c], t)
      else ((c :: (cut (i - c.1) t).1), (cut (i - c.1) t).2)

@[simp] theorem area_nil : area [] = 0 := rfl

@[simp] theorem area_cons (c : Col) (t : List Col) : area (c :: t) = c.1 + area t := rfl

@[simp] theorem area_append (x y : List Col) : area (x ++ y) = area x + area y := by
  induction x with
  | nil => simp
  | cons c t ih => simp [area_cons, ih, Nat.add_assoc]

/-- Every column of a valid continuation has positive height, so a nonempty
continuation has positive area. -/
theorem area_pos_of_validFrom {p : ℕ} : ∀ {l : List Col}, ValidFrom p l → l ≠ [] → 0 < area l
  | [], _, h => absurd rfl h
  | c :: t, hv, _ => by
      have : 1 ≤ c.1 := hv.1
      simp only [area_cons]
      omega

/-- The unfolding lemma for `ValidFrom` at a cons, stated so proofs can name the
three constraints rather than re-deriving them from the definition. -/
theorem validFrom_cons {p : ℕ} {c : Col} {t : List Col} :
    ValidFrom p (c :: t) ↔ 1 ≤ c.1 ∧ c.2 ≤ p ∧ p ≤ c.1 + c.2 ∧ ValidFrom c.1 t := Iff.rfl

/-- Appending a legal continuation to a valid animal keeps `ValidFrom`. -/
theorem validFrom_append {p : ℕ} : ∀ {x : List Col} {y : List Col},
    ValidFrom p x → x ≠ [] → ValidFrom (lastH x) y → ValidFrom p (x ++ y)
  | [], _, _, h, _ => absurd rfl h
  | [c], y, hx, _, hy => by
      refine ⟨hx.1, hx.2.1, hx.2.2.1, ?_⟩
      simpa [lastH] using hy
  | c :: c' :: t, y, hx, _, hy => by
      refine ⟨hx.1, hx.2.1, hx.2.2.1, ?_⟩
      have : ValidFrom (lastH (c' :: t)) y := by simpa [lastH] using hy
      exact validFrom_append hx.2.2.2 (by simp) this

/-- **The join lands in the class.** `d = lastH x - h'` is `max(0, lastH x − h')`
in `ℕ`, and both constraints it has to meet — `d ≤ lastH x` and
`lastH x ≤ h' + d` — hold in each of the two cases. -/
theorem join_valid {x y : List Col} (hx : Valid x) (hy : Valid y) : Valid (join x y) := by
  match y, hy with
  | c :: t, hy =>
    match x, hx with
    | e :: s, hx =>
      have he2 : e.2 = 0 := hx.2.1
      have hvx : ValidFrom e.1 (e :: s) := ⟨hx.1, by omega, by omega, hx.2.2⟩
      have hstep : ValidFrom (lastH (e :: s)) ((c.1, lastH (e :: s) - c.1) :: t) :=
        ⟨hy.1, Nat.sub_le _ _, by omega, hy.2.2⟩
      exact ⟨hx.1, hx.2.1, (validFrom_append hvx (by simp) hstep).2.2.2⟩

@[simp] theorem area_join (x y : List Col) : area (join x y) = area x + area y := by
  cases y with
  | nil => simp [join, area]
  | cons c t => simp [join, area_cons]

/-- **The cut inverts the join at fixed area.** Walking `x ++ z` until the
cumulative area reaches `area x` returns exactly `x` and `z`, because every
column of `x` is nonempty and `z`'s columns are too. -/
theorem cut_append : ∀ {x : List Col} {z : List Col} {p : ℕ},
    ValidFrom p x → x ≠ [] → ValidFrom (lastH x) z → z ≠ [] →
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
        cut_append hx.2.2.2 (by simp) (by simpa [lastH] using hz) hznil
      rw [List.cons_append, cut, if_neg hgt]
      simp only [area_cons, Nat.add_sub_cancel_left] at hrec ⊢
      rw [hrec]

/-- The join's second factor, re-anchored, is `y` again. -/
theorem cut_join {x y : List Col} (hx : Valid x) (hy : Valid y) :
    (cut (area x) (join x y)).1 = x ∧ norm (cut (area x) (join x y)).2 = y := by
  match y, hy with
  | c :: t, hy =>
    match x, hx with
    | e :: s, hx =>
      have he2 : e.2 = 0 := hx.2.1
      have hvx : ValidFrom e.1 (e :: s) := ⟨hx.1, by omega, by omega, hx.2.2⟩
      have hstep : ValidFrom (lastH (e :: s)) ((c.1, lastH (e :: s) - c.1) :: t) :=
        ⟨hy.1, Nat.sub_le _ _, by omega, hy.2.2⟩
      have hcut := cut_append hvx (by simp) hstep (by simp)
      have hjoin : join (e :: s) (c :: t)
          = (e :: s) ++ (c.1, lastH (e :: s) - c.1) :: t := rfl
      rw [hjoin, hcut]
      refine ⟨rfl, ?_⟩
      have hcd : c.2 = 0 := hy.2.1
      simp only [norm, List.cons.injEq, and_true]
      exact Prod.ext rfl hcd.symm

/-- **Injectivity at fixed areas**: the pair is recovered from the join alone,
so distinct pairs of equal areas have distinct joins. This is the step
`results/hv-growth-sandwich.md` Lemma 3 turns into `M i * M j ≤ M (i + j)`. -/
theorem join_injOn {x y x' y' : List Col} (hx : Valid x) (hy : Valid y)
    (hx' : Valid x') (hy' : Valid y') (harea : area x = area x')
    (h : join x y = join x' y') : x = x' ∧ y = y' := by
  have h1 := cut_join hx hy
  have h2 := cut_join hx' hy'
  rw [h, harea] at h1
  exact ⟨h1.1.symm.trans h2.1, h1.2.symm.trans h2.2⟩

end Polyplets.Stair
