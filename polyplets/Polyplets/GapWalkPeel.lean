/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkStacks
import Polyplets.GapWalkCanon

/-!
# Notary piece B, module 2: the peel recursion

Campaign *Notary*, piece **B**. Head theorems (`STKI_card_step`,
`STKB_card_step`): the stack counts satisfy the walk's own recursion,

    |STK (i+1) (g', c')| = Σ_{(g,c) ∈ states B} |STK i (g, c)| · stepMul g c g' c',

stated with the right side as `GapWalk.funStep` so `GapWalkBij` can consume
it verbatim. Pre-verified numerically (`verify_bij_statements.py`, checks
C/D/E: recursion, master fiber lemma exhaustively over all stacks of ≤ 2
rows, truncation).

## The geometry, once

Let `T` be a stack with top row `i` = `{tL = (xL, i), tR = (xL+g, i)}` and
class `c`, and put a new pair `u = (xL+a, i+1)`, `v = (xL+a+g', i+1)` on
top; `S = insert u (insert v T)`. King steps change `y` by at most 1 and
row `i` holds only `tL, tR`, so **the entire interface between `{u, v}` and
`T` is the four Booleans**

    x0 = near a         (u ~ tL)      x1 = near (a+g')       (v ~ tL)
    y0 = near (a−g)     (u ~ tR)      y1 = near (a+g'−g)     (v ~ tR)

plus `u ~ v ↔ g' = 1`. Every component of `T` holds `tL` or `tR` (that is
`stackOK`), so the component structure of `S` is a finite quotient of at
most four atoms `{comp(tL), comp(tR), {u}, {v}}` under these five edges —
and the two head lemmas are case analyses over them:

* `stack_cond_iff` (`ok`): `S` is again a stack — every component meets
  the new top row — iff class `J`: some contact at all
  (`touch0 ∨ touchg`), class `P`: both old components touched
  (`touch0 ∧ touchg`). Dead components are those of `T` missing every
  contact; `u`, `v` themselves always meet the top row.
* `class_iff` (`nc`): given `ok`, the new pair is joined iff `g' = 1`
  (direct edge), else — `J` source: both new cells attached,
  `(x0 ∨ y0) ∧ (x1 ∨ y1)`; `P` source: some old component touched by both
  new cells, `(x0 ∧ x1) ∨ (y0 ∧ y1)` (`GapWalk.joined x0 y0 x1 y1`).

Positive directions are path-gluing (`reach_tail`, `reach_mono`,
`reach_trans`, `reach_symm`); negative directions are `reach_closed` with
the explicit trap sets listed at each lemma.

## From the master lemma to the recursion

`isStackI_insert_iff` assembles `ok`/`nc` with the row bookkeeping into:
the assembled set is a stack in state `(g', c')` iff the Boolean
`okB && (ncB == c')` holds — the *very predicate* `stepMul` filters
(`stepMul_eq_card`). The recursion is then fiberwise counting under the
truncation `τ S = S.filter (·.2 ≤ i)`:

* every `S ∈ STK (i+1) (g', c')` truncates to a stack (`trunc` lemmas;
  the trap set for "every `T`-component keeps a row-`i` cell" is
  `{q ∈ T | reach T q tL ∨ reach T q tR} ∪ {u, v}`);
* its state lands in `states B`: `J`-truncations have `g ≤ 2i`
  (`isStackI_J_le`), `P`-truncations have `g ≤ g' + 2` (both tops lie in
  the touched window of width `g' + 2`, arithmetic from `ok`);
* the fiber over a fixed `T` is in bijection with the `stepMul` filter
  window via `a ↦ insert u (insert v T)` (`Finset.card_bij`; injectivity:
  distinct `a` give distinct top rows; surjectivity: read `a` off the
  top-left cell of `S`, which its own `∃`-witness provides).
-/

namespace Polyplets

open GapWalk (St states near joined stepMul funStep)

/-! ## The transition Booleans, named -/

/-- The legality Boolean of `stepMul`, exposed: `ok` at offset `a`. -/
def okB (g : ℕ) (c : Bool) (gp : ℕ) (a : ℤ) : Bool :=
  let touch0 := near a || near (a + (gp : ℤ))
  let touchg := near (a - (g : ℤ)) || near (a + (gp : ℤ) - (g : ℤ))
  if c then touch0 || touchg else touch0 && touchg

/-- The new-class Boolean of `stepMul`, exposed: `nc` at offset `a`. -/
def ncB (g : ℕ) (c : Bool) (gp : ℕ) (a : ℤ) : Bool :=
  if gp = 1 then true
  else if c then
    (near a || near (a - (g : ℤ))) && (near (a + (gp : ℤ)) || near (a + (gp : ℤ) - (g : ℤ)))
  else joined (near a) (near (a - (g : ℤ))) (near (a + (gp : ℤ))) (near (a + (gp : ℤ) - (g : ℤ)))

/-- Bridge: the cardinality of a `Finset.range` filter equals the length of
the corresponding `List.range` filter, for any Boolean predicate. Induction
on `n` via `Finset.range_succ`/`List.range_succ`. -/
private theorem card_filter_range_eq_length_filter (n : ℕ) (p : ℕ → Bool) :
    ((Finset.range n).filter fun k => p k = true).card =
      (List.filter p (List.range n)).length := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.range_add_one, List.range_succ, List.filter_append]
      by_cases h : p n = true
      · rw [Finset.filter_insert, if_pos h, List.length_append]
        rw [Finset.card_insert_of_notMem
          (fun hmem => Finset.notMem_range_self (Finset.mem_filter.mp hmem).1)]
        simp [ih, h]
      · rw [Finset.filter_insert, if_neg h, List.length_append]
        simp [ih, h]

/-- `stepMul` counts exactly the window offsets where `okB && ncB == c'`:
its `List.filter` predicate is these Booleans at `a = n − (gp + 2)`.
(`Finset.range`/`List.range` filter-length bridge; `List.countP` route or
`rfl` after unfolding.) -/
theorem stepMul_eq_card (g : ℕ) (c : Bool) (gp : ℕ) (cp : Bool) :
    stepMul g c gp cp =
      ((Finset.range (g + gp + 5)).filter fun n : ℕ =>
        (okB g c gp ((n : ℤ) - ((gp : ℤ) + 2)) &&
         (ncB g c gp ((n : ℤ) - ((gp : ℤ) + 2)) == cp)) = true).card := by
  rw [card_filter_range_eq_length_filter]
  rfl

/-! ## The frame

Hypotheses shared by every lemma below (interior and bare alike): `T`'s
cells sit in rows `≤ i`, its row `i` is exactly the pair at gap `g`, every
cell reaches a top cell, and `c` records whether the tops are joined. The
hypotheses are spelled out per lemma (no section `variable`s: they would
not be auto-included, as none is mentioned in the statements). -/

section Frame

variable {i g : ℕ} {T : Finset (ℤ × ℤ)} {xL : ℤ} {c : Bool}

/-- New-row cells only see the two top cells of `T` (`kingAdj_y` plus the
row characterization). Stated for any cell on row `i + 1`. -/
theorem newRow_adj {b w : ℤ × ℤ}
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hb : b ∈ T) (hw : w.2 = (i : ℤ) + 1) (hadj : kingAdj b w) :
    b = (xL, (i : ℤ)) ∨ b = (xL + (g : ℤ), (i : ℤ)) := by
  have hby := hTy b hb
  have hd : |b.2 - w.2| ≤ 1 := hadj.2.2
  have hbi : b.2 = (i : ℤ) := by rw [hw] at hd; rw [abs_le] at hd; omega
  exact hrow b hb hbi

/-! ### The five adjacency Booleans, and the two new-cell facts -/

private theorem adj_u_tL (xL a : ℤ) (i : ℕ) :
    kingAdj (xL + a, (i : ℤ) + 1) (xL, (i : ℤ)) ↔ near a = true := by
  unfold kingAdj near; rw [decide_eq_true_eq]
  constructor
  · rintro ⟨-, hx, -⟩; rw [Int.abs_eq_natAbs] at hx; omega
  · intro h
    refine ⟨?_, ?_, ?_⟩
    · intro heq; injection heq with h1 h2; omega
    · rw [Int.abs_eq_natAbs]; omega
    · rw [Int.abs_eq_natAbs]; omega

private theorem adj_v_tL (xL a : ℤ) (i gp : ℕ) :
    kingAdj (xL + a + (gp : ℤ), (i : ℤ) + 1) (xL, (i : ℤ)) ↔
      near (a + (gp : ℤ)) = true := by
  unfold kingAdj near; rw [decide_eq_true_eq]
  constructor
  · rintro ⟨-, hx, -⟩; rw [Int.abs_eq_natAbs] at hx; omega
  · intro h
    refine ⟨?_, ?_, ?_⟩
    · intro heq; injection heq with h1 h2; omega
    · rw [Int.abs_eq_natAbs]; omega
    · rw [Int.abs_eq_natAbs]; omega

private theorem adj_u_tR (xL a : ℤ) (i g : ℕ) :
    kingAdj (xL + a, (i : ℤ) + 1) (xL + (g : ℤ), (i : ℤ)) ↔
      near (a - (g : ℤ)) = true := by
  unfold kingAdj near; rw [decide_eq_true_eq]
  constructor
  · rintro ⟨-, hx, -⟩; rw [Int.abs_eq_natAbs] at hx; omega
  · intro h
    refine ⟨?_, ?_, ?_⟩
    · intro heq; injection heq with h1 h2; omega
    · rw [Int.abs_eq_natAbs]; omega
    · rw [Int.abs_eq_natAbs]; omega

private theorem adj_v_tR (xL a : ℤ) (i g gp : ℕ) :
    kingAdj (xL + a + (gp : ℤ), (i : ℤ) + 1) (xL + (g : ℤ), (i : ℤ)) ↔
      near (a + (gp : ℤ) - (g : ℤ)) = true := by
  unfold kingAdj near; rw [decide_eq_true_eq]
  constructor
  · rintro ⟨-, hx, -⟩; rw [Int.abs_eq_natAbs] at hx; omega
  · intro h
    refine ⟨?_, ?_, ?_⟩
    · intro heq; injection heq with h1 h2; omega
    · rw [Int.abs_eq_natAbs]; omega
    · rw [Int.abs_eq_natAbs]; omega

private theorem adj_u_v (xL a : ℤ) (i gp : ℕ) (hgp : 1 ≤ gp) :
    kingAdj (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1) ↔ gp = 1 := by
  unfold kingAdj
  constructor
  · rintro ⟨-, hx, -⟩
    rw [Int.abs_eq_natAbs] at hx
    omega
  · intro h
    refine ⟨?_, ?_, ?_⟩
    · intro heq; injection heq with h1 h2; omega
    · rw [Int.abs_eq_natAbs]; omega
    · simp

/-- The two new cells never lie in `T` (their row `i + 1` exceeds every
`T`-row), and they are distinct from each other (`gp ≥ 1`). -/
private theorem uv_notMem_ne
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ)) (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ) :
    (xL + a, (i : ℤ) + 1) ∉ T ∧ (xL + a + (gp : ℤ), (i : ℤ) + 1) ∉ T ∧
    (xL + a, (i : ℤ) + 1) ≠ (xL + a + (gp : ℤ), (i : ℤ) + 1) := by
  refine ⟨?_, ?_, ?_⟩
  · intro hmem
    have h : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ hmem
    omega
  · intro hmem
    have h : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ hmem
    omega
  · intro heq
    have h1 : xL + a = xL + a + (gp : ℤ) := congrArg Prod.fst heq
    have hgpz : (0 : ℤ) < (gp : ℤ) := by exact_mod_cast hgp
    omega

/-- **`ok` is the stack condition.** With `u = (xL+a, i+1)`,
`v = (xL+a+g', i+1)`, `S = insert u (insert v T)`:

`←`  `J`: all of `T` reaches `tL` (tops joined, `stackOK`, symmetry), `tL`
     reaches whichever top is touched and thence the touching new cell;
     `u`, `v` reach themselves. `P`: each cell reaches its top, each top
     its toucher.
`→`  `J`, no contact at all: `T` itself is a trap set (`reach_closed` —
     no `T`-cell is adjacent to `u` or `v` by `newRow_adj`), yet
     `stackOK S u v` at `tL ∈ S` demands escape; contradiction. `P`,
     `¬touch0` (tL's side untouched): trap `{q ∈ T | reach T q tL}` —
     closed within `T` by `reach_tail`, closed toward `u, v` because their
     only `T`-neighbors are tops, `tR` is not in the trap (`hc`, class
     `P`), and `tL` has no contact. Symmetrically for `¬touchg`. -/
theorem stack_cond_iff
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ) :
    stackOK
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1) ↔
    okB g c gp a = true := by
  set S := insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T)
    with hSdef
  obtain ⟨huT, hvT, huv⟩ := uv_notMem_ne (T := T) hTy gp hgp a
  have hTsub : T ⊆ S := (Finset.subset_insert _ _).trans (Finset.subset_insert _ _)
  have huS : (xL + a, (i : ℤ) + 1) ∈ S := Finset.mem_insert_self _ _
  have hvS : (xL + a + (gp : ℤ), (i : ℤ) + 1) ∈ S :=
    Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  have htLS : (xL, (i : ℤ)) ∈ S := hTsub htL
  have htRS : (xL + (g : ℤ), (i : ℤ)) ∈ S := hTsub htR
  have hAdjUL := adj_u_tL xL a i
  have hAdjVL := adj_v_tL xL a i gp
  have hAdjUR := adj_u_tR xL a i g
  have hAdjVR := adj_v_tR xL a i g gp
  have hmemS : ∀ p ∈ S, p = (xL + a, (i : ℤ) + 1) ∨
      p = (xL + a + (gp : ℤ), (i : ℤ) + 1) ∨ p ∈ T := by
    intro p hp
    rw [hSdef, Finset.mem_insert, Finset.mem_insert] at hp
    tauto
  by_cases hc' : c = true
  · -- Class J.
    have hTLR : reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := hc.mp hc'
    have hTLRS : reach S (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := reach_mono hTsub hTLR
    have hRLS : reach S (xL + (g : ℤ), (i : ℤ)) (xL, (i : ℤ)) := reach_symm hTLRS
    simp only [okB, if_pos hc', Bool.or_eq_true]
    constructor
    · intro hStack
      by_contra hcon
      push_neg at hcon
      obtain ⟨⟨hx0, hx1⟩, ⟨hy0, hy1⟩⟩ := hcon
      have hclosed : ∀ p ∈ (T : Set (ℤ × ℤ)), ∀ w ∈ S, kingAdj p w → w ∈ (T : Set (ℤ × ℤ)) := by
        intro p hp w hw hadj
        rcases hmemS w hw with rfl | rfl | hwT
        · rcases newRow_adj hTy hrow (Finset.mem_coe.mp hp) rfl hadj with rfl | rfl
          · exact absurd (hAdjUL.mp (kingAdj_symm hadj)) hx0
          · exact absurd (hAdjUR.mp (kingAdj_symm hadj)) hy0
        · rcases newRow_adj hTy hrow (Finset.mem_coe.mp hp) rfl hadj with rfl | rfl
          · exact absurd (hAdjVL.mp (kingAdj_symm hadj)) hx1
          · exact absurd (hAdjVR.mp (kingAdj_symm hadj)) hy1
        · exact hwT
      have hres := hStack (xL, (i : ℤ)) htLS
      rcases hres with hres | hres
      · exact huT (Finset.mem_coe.mp (reach_closed hclosed (Finset.mem_coe.mpr htL) hres))
      · exact hvT (Finset.mem_coe.mp (reach_closed hclosed (Finset.mem_coe.mpr htL) hres))
    · intro hok
      intro p hp
      rcases hmemS p hp with rfl | rfl | hpT
      · exact Or.inl (reach_refl S _)
      · exact Or.inr (reach_refl S _)
      · have hp0 : reach T p (xL, (i : ℤ)) ∨ reach T p (xL + (g : ℤ), (i : ℤ)) := hOK p hpT
        have hpL : reach S p (xL, (i : ℤ)) := by
          rcases hp0 with h | h
          · exact reach_mono hTsub h
          · exact reach_trans (reach_mono hTsub h) hRLS
        have hpR : reach S p (xL + (g : ℤ), (i : ℤ)) := reach_trans hpL hTLRS
        rcases hok with (hx0 | hx1) | (hy0 | hy1)
        · exact Or.inl (reach_tail hpL htLS huS (kingAdj_symm (hAdjUL.mpr hx0)))
        · exact Or.inr (reach_tail hpL htLS hvS (kingAdj_symm (hAdjVL.mpr hx1)))
        · exact Or.inl (reach_tail hpR htRS huS (kingAdj_symm (hAdjUR.mpr hy0)))
        · exact Or.inr (reach_tail hpR htRS hvS (kingAdj_symm (hAdjVR.mpr hy1)))
  · -- Class P.
    have hcFalse : ¬ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := fun hr => hc' (hc.mpr hr)
    simp only [okB, if_neg hc', Bool.and_eq_true, Bool.or_eq_true]
    constructor
    · intro hStack
      by_contra hcon
      rw [not_and_or] at hcon
      rcases hcon with hcon | hcon
      · push_neg at hcon
        obtain ⟨hx0', hx1'⟩ := hcon
        have hTLmem : (xL, (i : ℤ)) ∈ {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL, (i : ℤ))} :=
          ⟨htL, reach_refl T _⟩
        have hclosed : ∀ p ∈ {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL, (i : ℤ))}, ∀ w ∈ S,
            kingAdj p w → w ∈ {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL, (i : ℤ))} := by
          intro p hp w hw hadj
          obtain ⟨hpT, hpL⟩ := hp
          rcases hmemS w hw with rfl | rfl | hwT
          · rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
            · exact absurd (hAdjUL.mp (kingAdj_symm hadj)) hx0'
            · exact absurd (reach_symm hpL) hcFalse
          · rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
            · exact absurd (hAdjVL.mp (kingAdj_symm hadj)) hx1'
            · exact absurd (reach_symm hpL) hcFalse
          · refine ⟨hwT, ?_⟩
            have hpw : reach T p w := reach_tail (reach_refl T p) hpT hwT hadj
            exact reach_trans (reach_symm hpw) hpL
        have hres := hStack (xL, (i : ℤ)) htLS
        rcases hres with hres | hres
        · exact huT (reach_closed hclosed hTLmem hres).1
        · exact hvT (reach_closed hclosed hTLmem hres).1
      · push_neg at hcon
        obtain ⟨hy0', hy1'⟩ := hcon
        have hTRmem : (xL + (g : ℤ), (i : ℤ)) ∈
            {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ))} := ⟨htR, reach_refl T _⟩
        have hclosed : ∀ p ∈ {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ))}, ∀ w ∈ S,
            kingAdj p w → w ∈ {q : ℤ × ℤ | q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ))} := by
          intro p hp w hw hadj
          obtain ⟨hpT, hpR⟩ := hp
          rcases hmemS w hw with rfl | rfl | hwT
          · rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
            · exact absurd hpR hcFalse
            · exact absurd (hAdjUR.mp (kingAdj_symm hadj)) hy0'
          · rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
            · exact absurd hpR hcFalse
            · exact absurd (hAdjVR.mp (kingAdj_symm hadj)) hy1'
          · refine ⟨hwT, ?_⟩
            have hpw : reach T p w := reach_tail (reach_refl T p) hpT hwT hadj
            exact reach_trans (reach_symm hpw) hpR
        have hres' := hStack (xL + (g : ℤ), (i : ℤ)) htRS
        rcases hres' with hres' | hres'
        · exact huT (reach_closed hclosed hTRmem hres').1
        · exact hvT (reach_closed hclosed hTRmem hres').1
    · intro hok
      intro p hp
      rcases hmemS p hp with rfl | rfl | hpT
      · exact Or.inl (reach_refl S _)
      · exact Or.inr (reach_refl S _)
      · have hp0 : reach T p (xL, (i : ℤ)) ∨ reach T p (xL + (g : ℤ), (i : ℤ)) := hOK p hpT
        obtain ⟨hxx, hyy⟩ := hok
        rcases hp0 with hpLp | hpRp
        · have hpLS : reach S p (xL, (i : ℤ)) := reach_mono hTsub hpLp
          rcases hxx with hx0 | hx1
          · exact Or.inl (reach_tail hpLS htLS huS (kingAdj_symm (hAdjUL.mpr hx0)))
          · exact Or.inr (reach_tail hpLS htLS hvS (kingAdj_symm (hAdjVL.mpr hx1)))
        · have hpRS : reach S p (xL + (g : ℤ), (i : ℤ)) := reach_mono hTsub hpRp
          rcases hyy with hy0 | hy1
          · exact Or.inl (reach_tail hpRS htRS huS (kingAdj_symm (hAdjUR.mpr hy0)))
          · exact Or.inr (reach_tail hpRS htRS hvS (kingAdj_symm (hAdjVR.mpr hy1)))

/-- **`nc` is the new class.** Given the stack condition, the new pair is
joined iff `ncB`. Case tree (write `S`, `u`, `v` as above):

* `gp = 1`: `u ~ v` directly (`kingAdj`, same row, distance 1).
* `gp ≥ 2`, source `J`: joined iff both new cells have some contact.
  `←`: each new cell steps into the single old component and out to the
  other new cell's contact. `→`: if (say) `u` has no contact, trap `{u}`
  (its only possible `S`-neighbors are tops — excluded — and `v`, too far).
* `gp ≥ 2`, source `P`: joined iff some *single* old component is touched
  by both new cells (`joined x0 y0 x1 y1 = (x0 && x1) || (y0 && y1)`).
  `←`: `u → tL → v` (or via `tR`). `→`: contrapositive, four traps by
  `u`'s contact pattern, each excluding `v`:
  `u` touches neither top: trap `{u}`; only `tL`: trap
  `{u} ∪ {q ∈ T | reach T q tL}` (uses `¬x1`, from `¬joined` and `x0`);
  only `tR`: mirror; both: trap `{u} ∪ reachers(tL) ∪ reachers(tR)`
  (then `¬x1 ∧ ¬y1`, so `v` borders nothing in the trap). -/
theorem class_iff
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ)
    (hok : okB g c gp a = true) :
    (reach
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1)) ↔
    ncB g c gp a = true := by
  set S := insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T)
    with hSdef
  obtain ⟨huT, hvT, huv⟩ := uv_notMem_ne (T := T) hTy gp hgp a
  have hTsub : T ⊆ S := (Finset.subset_insert _ _).trans (Finset.subset_insert _ _)
  have huS : (xL + a, (i : ℤ) + 1) ∈ S := Finset.mem_insert_self _ _
  have hvS : (xL + a + (gp : ℤ), (i : ℤ) + 1) ∈ S :=
    Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  have htLS : (xL, (i : ℤ)) ∈ S := hTsub htL
  have htRS : (xL + (g : ℤ), (i : ℤ)) ∈ S := hTsub htR
  have hAdjUL := adj_u_tL xL a i
  have hAdjVL := adj_v_tL xL a i gp
  have hAdjUR := adj_u_tR xL a i g
  have hAdjVR := adj_v_tR xL a i g gp
  have hmemS : ∀ p ∈ S, p = (xL + a, (i : ℤ) + 1) ∨
      p = (xL + a + (gp : ℤ), (i : ℤ) + 1) ∨ p ∈ T := by
    intro p hp
    rw [hSdef, Finset.mem_insert, Finset.mem_insert] at hp
    tauto
  by_cases hgp1 : gp = 1
  · have hadjuv : kingAdj (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1) :=
      (adj_u_v xL a i gp hgp).mpr hgp1
    simp only [ncB, if_pos hgp1]
    constructor
    · intro _; trivial
    · intro _; exact reach_tail (reach_refl S _) huS hvS hadjuv
  · simp only [ncB, if_neg hgp1]
    -- The two singleton-trap facts, shared by both classes: reach S u v forces
    -- both `u` and `v` to touch some old top (`gp ≠ 1` excludes the direct edge).
    have htouchU : ∀ hReach : reach S (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1),
        near a = true ∨ near (a - (g : ℤ)) = true := by
      intro hReach
      by_contra hcon
      push_neg at hcon
      obtain ⟨hx0, hy0⟩ := hcon
      have hclosed : ∀ p ∈ ({(xL + a, (i : ℤ) + 1)} : Set (ℤ × ℤ)), ∀ w ∈ S,
          kingAdj p w → w ∈ ({(xL + a, (i : ℤ) + 1)} : Set (ℤ × ℤ)) := by
        intro p hp w hw hadj
        rw [Set.mem_singleton_iff] at hp
        subst hp
        rcases hmemS w hw with rfl | rfl | hwT
        · exact rfl
        · exact absurd hadj (fun h => hgp1 ((adj_u_v xL a i gp hgp).mp h))
        · exfalso
          rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
          · exact hx0 (hAdjUL.mp hadj)
          · exact hy0 (hAdjUR.mp hadj)
      have huC : (xL + a, (i : ℤ) + 1) ∈ ({(xL + a, (i : ℤ) + 1)} : Set (ℤ × ℤ)) := rfl
      exact huv (reach_closed hclosed huC hReach).symm
    have htouchV : ∀ hReach : reach S (xL + a + (gp : ℤ), (i : ℤ) + 1) (xL + a, (i : ℤ) + 1),
        near (a + (gp : ℤ)) = true ∨ near (a + (gp : ℤ) - (g : ℤ)) = true := by
      intro hReach
      by_contra hcon
      push_neg at hcon
      obtain ⟨hx1, hy1⟩ := hcon
      have hclosed : ∀ p ∈ ({(xL + a + (gp : ℤ), (i : ℤ) + 1)} : Set (ℤ × ℤ)), ∀ w ∈ S,
          kingAdj p w → w ∈ ({(xL + a + (gp : ℤ), (i : ℤ) + 1)} : Set (ℤ × ℤ)) := by
        intro p hp w hw hadj
        rw [Set.mem_singleton_iff] at hp
        subst hp
        rcases hmemS w hw with rfl | rfl | hwT
        · exact absurd (kingAdj_symm hadj) (fun h => hgp1 ((adj_u_v xL a i gp hgp).mp h))
        · exact rfl
        · exfalso
          rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
          · exact hx1 (hAdjVL.mp hadj)
          · exact hy1 (hAdjVR.mp hadj)
      have hvC : (xL + a + (gp : ℤ), (i : ℤ) + 1) ∈
          ({(xL + a + (gp : ℤ), (i : ℤ) + 1)} : Set (ℤ × ℤ)) := rfl
      exact huv (reach_closed hclosed hvC hReach)
    by_cases hc' : c = true
    · -- Class J.
      have hTLR : reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := hc.mp hc'
      have hTLRS : reach S (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := reach_mono hTsub hTLR
      have hRLS : reach S (xL + (g : ℤ), (i : ℤ)) (xL, (i : ℤ)) := reach_symm hTLRS
      simp only [if_pos hc', Bool.and_eq_true, Bool.or_eq_true]
      constructor
      · intro hReach
        exact ⟨htouchU hReach, htouchV (reach_symm hReach)⟩
      · rintro ⟨htU, htV⟩
        have hurL : reach S (xL + a, (i : ℤ) + 1) (xL, (i : ℤ)) := by
          rcases htU with hx0 | hy0
          · exact reach_tail (reach_refl S _) huS htLS (hAdjUL.mpr hx0)
          · exact reach_trans (reach_tail (reach_refl S _) huS htRS (hAdjUR.mpr hy0)) hRLS
        have hvrL : reach S (xL + a + (gp : ℤ), (i : ℤ) + 1) (xL, (i : ℤ)) := by
          rcases htV with hx1 | hy1
          · exact reach_tail (reach_refl S _) hvS htLS (hAdjVL.mpr hx1)
          · exact reach_trans (reach_tail (reach_refl S _) hvS htRS (hAdjVR.mpr hy1)) hRLS
        exact reach_trans hurL (reach_symm hvrL)
    · -- Class P.
      have hcFalse : ¬ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := fun hr => hc' (hc.mpr hr)
      simp only [if_neg hc', joined, Bool.or_eq_true, Bool.and_eq_true]
      constructor
      · intro hReach
        have htU := htouchU hReach
        have htV := htouchV (reach_symm hReach)
        by_cases hx0c : near a = true
        · by_cases hx1c : near (a + (gp : ℤ)) = true
          · exact Or.inl ⟨hx0c, hx1c⟩
          · have hy1c : near (a + (gp : ℤ) - (g : ℤ)) = true := htV.resolve_left hx1c
            by_cases hy0c : near (a - (g : ℤ)) = true
            · exact Or.inr ⟨hy0c, hy1c⟩
            · exfalso
              have hclosed : ∀ p ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                  (q ∈ T ∧ reach T q (xL, (i : ℤ)))}), ∀ w ∈ S,
                  kingAdj p w → w ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                  (q ∈ T ∧ reach T q (xL, (i : ℤ)))}) := by
                intro p hp w hw hadj
                rcases hp with rfl | ⟨hpT, hpL⟩
                · rcases hmemS w hw with rfl | rfl | hwT
                  · exact Or.inl rfl
                  · exact absurd hadj (fun h => hgp1 ((adj_u_v xL a i gp hgp).mp h))
                  · rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
                    · exact Or.inr ⟨hwT, reach_refl T _⟩
                    · exact absurd (hAdjUR.mp hadj) hy0c
                · rcases hmemS w hw with rfl | rfl | hwT
                  · exact Or.inl rfl
                  · exfalso
                    rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
                    · exact hx1c (hAdjVL.mp (kingAdj_symm hadj))
                    · exact hcFalse (reach_symm hpL)
                  · refine Or.inr ⟨hwT, ?_⟩
                    have hpw : reach T p w := reach_tail (reach_refl T p) hpT hwT hadj
                    exact reach_trans (reach_symm hpw) hpL
              have huC : (xL + a, (i : ℤ) + 1) ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                  (q ∈ T ∧ reach T q (xL, (i : ℤ)))}) := Or.inl rfl
              rcases reach_closed hclosed huC hReach with heq | ⟨hvT', -⟩
              · exact huv heq.symm
              · exact hvT hvT'
        · have hy0c : near (a - (g : ℤ)) = true := htU.resolve_left hx0c
          by_cases hy1c : near (a + (gp : ℤ) - (g : ℤ)) = true
          · exact Or.inr ⟨hy0c, hy1c⟩
          · have hx1c : near (a + (gp : ℤ)) = true := htV.resolve_right hy1c
            exfalso
            have hclosed : ∀ p ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                (q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ)))}), ∀ w ∈ S,
                kingAdj p w → w ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                (q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ)))}) := by
              intro p hp w hw hadj
              rcases hp with rfl | ⟨hpT, hpR⟩
              · rcases hmemS w hw with rfl | rfl | hwT
                · exact Or.inl rfl
                · exact absurd hadj (fun h => hgp1 ((adj_u_v xL a i gp hgp).mp h))
                · rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
                  · exact absurd (hAdjUL.mp hadj) hx0c
                  · exact Or.inr ⟨hwT, reach_refl T _⟩
              · rcases hmemS w hw with rfl | rfl | hwT
                · exact Or.inl rfl
                · exfalso
                  rcases newRow_adj hTy hrow hpT rfl hadj with rfl | rfl
                  · exact hcFalse hpR
                  · exact hy1c (hAdjVR.mp (kingAdj_symm hadj))
                · refine Or.inr ⟨hwT, ?_⟩
                  have hpw : reach T p w := reach_tail (reach_refl T p) hpT hwT hadj
                  exact reach_trans (reach_symm hpw) hpR
            have huC : (xL + a, (i : ℤ) + 1) ∈ ({q : ℤ × ℤ | q = (xL + a, (i : ℤ) + 1) ∨
                (q ∈ T ∧ reach T q (xL + (g : ℤ), (i : ℤ)))}) := Or.inl rfl
            rcases reach_closed hclosed huC hReach with heq | ⟨hvT', -⟩
            · exact huv heq.symm
            · exact hvT hvT'
      · rintro (⟨hx0c, hx1c⟩ | ⟨hy0c, hy1c⟩)
        · exact reach_trans (reach_tail (reach_refl S _) huS htLS (hAdjUL.mpr hx0c))
            (reach_symm (reach_tail (reach_refl S _) hvS htLS (hAdjVL.mpr hx1c)))
        · exact reach_trans (reach_tail (reach_refl S _) huS htRS (hAdjUR.mpr hy0c))
            (reach_symm (reach_tail (reach_refl S _) hvS htRS (hAdjVR.mpr hy1c)))

/-- Truncation direction: if the assembled set is a stack over its new top
pair, then `T` was a stack over the old one. Trap set:
`{q ∈ T | reach T q tL ∨ reach T q tR} ∪ {u, v}`, entered at `u`, walked
backwards from `reach S p u ∨ reach S p v` via `reach_symm`. -/
theorem trunc_stackOK
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ)
    (hS : stackOK
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1)) :
    stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := by
  obtain ⟨huT, hvT, huv⟩ := uv_notMem_ne (T := T) hTy gp hgp a
  set S := insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T)
    with hSdef
  have hTsub : T ⊆ S := (Finset.subset_insert _ _).trans (Finset.subset_insert _ _)
  have hmemS : ∀ p ∈ S, p = (xL + a, (i : ℤ) + 1) ∨
      p = (xL + a + (gp : ℤ), (i : ℤ) + 1) ∨ p ∈ T := by
    intro p hp
    rw [hSdef, Finset.mem_insert, Finset.mem_insert] at hp
    tauto
  set C : Set (ℤ × ℤ) := {q | q = (xL + a, (i : ℤ) + 1) ∨
      q = (xL + a + (gp : ℤ), (i : ℤ) + 1) ∨
      (q ∈ T ∧ (reach T q (xL, (i : ℤ)) ∨ reach T q (xL + (g : ℤ), (i : ℤ))))}
    with hCdef
  have hclosed : ∀ p ∈ C, ∀ w ∈ S, kingAdj p w → w ∈ C := by
    intro p hp w hw hadj
    rcases hmemS w hw with rfl | rfl | hwT
    · exact Or.inl rfl
    · exact Or.inr (Or.inl rfl)
    · rcases hp with rfl | rfl | ⟨hpT, hpReach⟩
      · rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
        · exact Or.inr (Or.inr ⟨hwT, Or.inl (reach_refl T _)⟩)
        · exact Or.inr (Or.inr ⟨hwT, Or.inr (reach_refl T _)⟩)
      · rcases newRow_adj hTy hrow hwT rfl (kingAdj_symm hadj) with rfl | rfl
        · exact Or.inr (Or.inr ⟨hwT, Or.inl (reach_refl T _)⟩)
        · exact Or.inr (Or.inr ⟨hwT, Or.inr (reach_refl T _)⟩)
      · have hpw : reach T p w := reach_tail (reach_refl T p) hpT hwT hadj
        rcases hpReach with h | h
        · exact Or.inr (Or.inr ⟨hwT, Or.inl (reach_trans (reach_symm hpw) h)⟩)
        · exact Or.inr (Or.inr ⟨hwT, Or.inr (reach_trans (reach_symm hpw) h)⟩)
  have huC : (xL + a, (i : ℤ) + 1) ∈ C := Or.inl rfl
  have hvC : (xL + a + (gp : ℤ), (i : ℤ) + 1) ∈ C := Or.inr (Or.inl rfl)
  intro p hpT
  have hpS : p ∈ S := hTsub hpT
  rcases hS p hpS with hres | hres
  · rcases reach_closed hclosed huC (reach_symm hres) with heq | heq | ⟨-, hh⟩
    · exact absurd (heq ▸ hpT) huT
    · exact absurd (heq ▸ hpT) hvT
    · exact hh
  · rcases reach_closed hclosed hvC (reach_symm hres) with heq | heq | ⟨-, hh⟩
    · exact absurd (heq ▸ hpT) huT
    · exact absurd (heq ▸ hpT) hvT
    · exact hh

end Frame

/-! ## The master fiber lemmas -/

/-- **Master fiber lemma, interior.** Adding the pair at offset `a`, span
`g'` to an interior `i`-row stack in state `(g, c)` yields an interior
`(i+1)`-row stack in state `(g', c')` exactly when `stepMul`'s Boolean
holds. Assemble: `stack_cond_iff` + `class_iff` (frame from
`isStackI_top`, `hTy` from the bounds clause, `hrow` from the top
extraction) for the `∃`-clause; cardinality (`u, v` new, distinct), row
bounds, `rowSize` updates (`rowSize_insert_*`), and the top-witness
uniqueness for the `→` direction (the witness of the assembled stack's
`∃`-clause must be `u`: its row is `i+1`, and `row_eq_pair` pins the row to
`{u, v}` with `u` left). -/
theorem isStackI_insert_iff {i g : ℕ} {c : Bool} {T : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (hT : IsStackI i g c T)
    (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) (a : ℤ) :
    IsStackI (i + 1) g' c'
      (insert (rowMinX T (i : ℤ) + a, (i : ℤ) + 1)
        (insert (rowMinX T (i : ℤ) + a + (g' : ℤ), (i : ℤ) + 1) T)) ↔
    (okB g c g' a && (ncB g c g' a == c')) = true := by
  set xL := rowMinX T (i : ℤ) with hxLdef
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (hT.2.2.2.1 p hp).2
  obtain ⟨htL, htR, hmaxeq, hOK, hc, hrow⟩ := isStackI_top hi hT
  obtain ⟨huT, hvT, huv⟩ := uv_notMem_ne (T := T) (xL := xL) hTy g' hg' a
  set S := insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T)
    with hSdef
  have hTsub : T ⊆ S := (Finset.subset_insert _ _).trans (Finset.subset_insert _ _)
  have huS : (xL + a, (i : ℤ) + 1) ∈ S := Finset.mem_insert_self _ _
  have hvS : (xL + a + (g' : ℤ), (i : ℤ) + 1) ∈ S :=
    Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  have hmemS : ∀ p ∈ S, p = (xL + a, (i : ℤ) + 1) ∨
      p = (xL + a + (g' : ℤ), (i : ℤ) + 1) ∨ p ∈ T := by
    intro p hp
    rw [hSdef, Finset.mem_insert, Finset.mem_insert] at hp
    tauto
  have hunotinsvT : (xL + a, (i : ℤ) + 1) ∉ insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T := by
    rw [Finset.mem_insert]
    rintro (h | h)
    · exact huv h
    · exact huT h
  have hcardS : S.card = 2 * (i + 1) + 1 := by
    rw [hSdef, Finset.card_insert_of_notMem hunotinsvT,
      Finset.card_insert_of_notMem hvT, hT.2.1]
    ring
  have hanchorS : ((0 : ℤ), (0 : ℤ)) ∈ S := hTsub hT.2.2.1
  have hrowS0 : rowSize S 0 = 1 := by
    rw [hSdef, rowSize_insert_other (by omega), rowSize_insert_other (by omega),
      hT.2.2.2.2.1]
  have hboundsS : ∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ ((i : ℕ) + 1 : ℤ) := by
    intro p hp
    rcases hmemS p hp with rfl | rfl | hpT
    · omega
    · omega
    · obtain ⟨h1, h2⟩ := hT.2.2.2.1 p hpT
      omega
  have hTrow0 : rowSize T ((i : ℤ) + 1) = 0 := by
    unfold rowSize
    rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro p hp
    have := hTy p hp
    omega
  have hrowIccS : ∀ r ∈ Finset.Icc 1 (i + 1), rowSize S (r : ℤ) = 2 := by
    intro r hr
    rw [Finset.mem_Icc] at hr
    by_cases hcase : r = i + 1
    · subst hcase
      change rowSize S ((i : ℤ) + 1) = 2
      rw [hSdef, rowSize_insert_same hunotinsvT rfl, rowSize_insert_same hvT rfl, hTrow0]
    · have hri : (1 : ℕ) ≤ r ∧ r ≤ i := ⟨hr.1, by omega⟩
      have hTeq : rowSize T (r : ℤ) = 2 := hT.2.2.2.2.2.1 r (Finset.mem_Icc.mpr hri)
      rw [hSdef, rowSize_insert_other (by omega), rowSize_insert_other (by omega), hTeq]
  constructor
  · intro hS
    obtain ⟨p, hpS, hpi, hpvS, hSOK, hSc⟩ := hS.2.2.2.2.2.2
    push_cast at hpi hpvS hSOK hSc
    have hrowSi1 : rowSize S ((i : ℤ) + 1) = 2 :=
      hrowIccS (i + 1) (Finset.mem_Icc.mpr ⟨by omega, le_refl _⟩)
    have hune : (xL + a, (i : ℤ) + 1) ≠ (xL + a + (g' : ℤ), (i : ℤ) + 1) := huv
    have hpairS := row_eq_pair hrowSi1 huS hvS rfl rfl hune
    rcases hpairS p hpS hpi with hpeq | hpeq
    · -- p = u
      subst hpeq
      have hokB : okB g c g' a = true := by
        rw [← stack_cond_iff hT.1 hTy htL htR hrow hOK hc g' hg' a]
        exact hSOK
      have hncEq : ncB g c g' a = c' := by
        have hclass := class_iff hT.1 hTy htL htR hrow hOK hc g' hg' a hokB
        have hiff : (c' = true) ↔ (ncB g c g' a = true) := hSc.trans hclass
        revert hiff
        cases c' <;> cases (ncB g c g' a) <;> simp
      rw [Bool.and_eq_true]
      exact ⟨hokB, by simp [hncEq]⟩
    · -- p = v: contradiction, since (p.1 + g', i+1) would be a third row cell
      exfalso
      have hne3 : (p.1 + (g' : ℤ), (i : ℤ) + 1) ≠ (xL + a, (i : ℤ) + 1) := by
        rw [hpeq]
        intro heq
        have h1 : xL + a + (g' : ℤ) + (g' : ℤ) = xL + a := congrArg Prod.fst heq
        have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
        omega
      have hne4 : (p.1 + (g' : ℤ), (i : ℤ) + 1) ≠ (xL + a + (g' : ℤ), (i : ℤ) + 1) := by
        rw [hpeq]
        intro heq
        have h1 : xL + a + (g' : ℤ) + (g' : ℤ) = xL + a + (g' : ℤ) := congrArg Prod.fst heq
        have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
        omega
      rcases hpairS (p.1 + (g' : ℤ), (i : ℤ) + 1) hpvS rfl with h | h
      · exact hne3 h
      · exact hne4 h
  · intro hok
    rw [Bool.and_eq_true] at hok
    obtain ⟨hokB, hncEqB⟩ := hok
    have hncEq : ncB g c g' a = c' := beq_iff_eq.mp hncEqB
    have hSOK : stackOK S (xL + a, (i : ℤ) + 1) (xL + a + (g' : ℤ), (i : ℤ) + 1) :=
      (stack_cond_iff hT.1 hTy htL htR hrow hOK hc g' hg' a).mpr hokB
    have hSc : c' = true ↔ reach S (xL + a, (i : ℤ) + 1) (xL + a + (g' : ℤ), (i : ℤ) + 1) := by
      rw [← hncEq]
      exact (class_iff hT.1 hTy htL htR hrow hOK hc g' hg' a hokB).symm
    refine ⟨hg', hcardS, hanchorS, hboundsS, hrowS0, hrowIccS,
      (xL + a, (i : ℤ) + 1), huS, rfl, hvS, hSOK, hSc⟩

/-- **Master fiber lemma, bare.** Identical assembly over `IsStackB`
(the two extra clauses — anchor cell and row-1 left bound — hold in the
assembled set iff they held in `T`, as the new cells sit on row
`i + 1 ≥ 2`). -/
theorem isStackB_insert_iff {i g : ℕ} {c : Bool} {T : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (hT : IsStackB i g c T)
    (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) (a : ℤ) :
    IsStackB (i + 1) g' c'
      (insert (rowMinX T (i : ℤ) + a, (i : ℤ) + 1)
        (insert (rowMinX T (i : ℤ) + a + (g' : ℤ), (i : ℤ) + 1) T)) ↔
    (okB g c g' a && (ncB g c g' a == c')) = true := by
  set xL := rowMinX T (i : ℤ) with hxLdef
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (hT.2.2.2.1 p hp).2
  obtain ⟨htL, htR, hmaxeq, hOK, hc, hrow⟩ := isStackB_top hi hT
  obtain ⟨huT, hvT, huv⟩ := uv_notMem_ne (T := T) (xL := xL) hTy g' hg' a
  set S := insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T)
    with hSdef
  have hTsub : T ⊆ S := (Finset.subset_insert _ _).trans (Finset.subset_insert _ _)
  have huS : (xL + a, (i : ℤ) + 1) ∈ S := Finset.mem_insert_self _ _
  have hvS : (xL + a + (g' : ℤ), (i : ℤ) + 1) ∈ S :=
    Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  have hmemS : ∀ p ∈ S, p = (xL + a, (i : ℤ) + 1) ∨
      p = (xL + a + (g' : ℤ), (i : ℤ) + 1) ∨ p ∈ T := by
    intro p hp
    rw [hSdef, Finset.mem_insert, Finset.mem_insert] at hp
    tauto
  have hunotinsvT : (xL + a, (i : ℤ) + 1) ∉ insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T := by
    rw [Finset.mem_insert]
    rintro (h | h)
    · exact huv h
    · exact huT h
  have hcardS : S.card = 2 * (i + 1) := by
    rw [hSdef, Finset.card_insert_of_notMem hunotinsvT,
      Finset.card_insert_of_notMem hvT, hT.2.1]
    ring
  have hanchorS : ((0 : ℤ), (1 : ℤ)) ∈ S := hTsub hT.2.2.1
  have hboundsS : ∀ p ∈ S, 1 ≤ p.2 ∧ p.2 ≤ ((i : ℕ) + 1 : ℤ) := by
    intro p hp
    rcases hmemS p hp with rfl | rfl | hpT
    · omega
    · omega
    · obtain ⟨h1, h2⟩ := hT.2.2.2.1 p hpT
      omega
  have hrow1S : ∀ p ∈ S, p.2 = 1 → 0 ≤ p.1 := by
    intro p hp hp1
    rcases hmemS p hp with rfl | rfl | hpT
    · exfalso
      have h1 : (i : ℤ) + 1 = 1 := hp1
      omega
    · exfalso
      have h1 : (i : ℤ) + 1 = 1 := hp1
      omega
    · exact hT.2.2.2.2.1 p hpT hp1
  have hTrow0 : rowSize T ((i : ℤ) + 1) = 0 := by
    unfold rowSize
    rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro p hp
    have := hTy p hp
    omega
  have hrowIccS : ∀ r ∈ Finset.Icc 1 (i + 1), rowSize S (r : ℤ) = 2 := by
    intro r hr
    rw [Finset.mem_Icc] at hr
    by_cases hcase : r = i + 1
    · subst hcase
      change rowSize S ((i : ℤ) + 1) = 2
      rw [hSdef, rowSize_insert_same hunotinsvT rfl, rowSize_insert_same hvT rfl, hTrow0]
    · have hri : (1 : ℕ) ≤ r ∧ r ≤ i := ⟨hr.1, by omega⟩
      have hTeq : rowSize T (r : ℤ) = 2 := hT.2.2.2.2.2.1 r (Finset.mem_Icc.mpr hri)
      rw [hSdef, rowSize_insert_other (by omega), rowSize_insert_other (by omega), hTeq]
  constructor
  · intro hS
    obtain ⟨p, hpS, hpi, hpvS, hSOK, hSc⟩ := hS.2.2.2.2.2.2
    push_cast at hpi hpvS hSOK hSc
    have hrowSi1 : rowSize S ((i : ℤ) + 1) = 2 :=
      hrowIccS (i + 1) (Finset.mem_Icc.mpr ⟨by omega, le_refl _⟩)
    have hune : (xL + a, (i : ℤ) + 1) ≠ (xL + a + (g' : ℤ), (i : ℤ) + 1) := huv
    have hpairS := row_eq_pair hrowSi1 huS hvS rfl rfl hune
    rcases hpairS p hpS hpi with hpeq | hpeq
    · -- p = u
      subst hpeq
      have hokB : okB g c g' a = true := by
        rw [← stack_cond_iff hT.1 hTy htL htR hrow hOK hc g' hg' a]
        exact hSOK
      have hncEq : ncB g c g' a = c' := by
        have hclass := class_iff hT.1 hTy htL htR hrow hOK hc g' hg' a hokB
        have hiff : (c' = true) ↔ (ncB g c g' a = true) := hSc.trans hclass
        revert hiff
        cases c' <;> cases (ncB g c g' a) <;> simp
      rw [Bool.and_eq_true]
      exact ⟨hokB, by simp [hncEq]⟩
    · -- p = v: contradiction, since (p.1 + g', i+1) would be a third row cell
      exfalso
      have hne3 : (p.1 + (g' : ℤ), (i : ℤ) + 1) ≠ (xL + a, (i : ℤ) + 1) := by
        rw [hpeq]
        intro heq
        have h1 : xL + a + (g' : ℤ) + (g' : ℤ) = xL + a := congrArg Prod.fst heq
        have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
        omega
      have hne4 : (p.1 + (g' : ℤ), (i : ℤ) + 1) ≠ (xL + a + (g' : ℤ), (i : ℤ) + 1) := by
        rw [hpeq]
        intro heq
        have h1 : xL + a + (g' : ℤ) + (g' : ℤ) = xL + a + (g' : ℤ) := congrArg Prod.fst heq
        have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
        omega
      rcases hpairS (p.1 + (g' : ℤ), (i : ℤ) + 1) hpvS rfl with h | h
      · exact hne3 h
      · exact hne4 h
  · intro hok
    rw [Bool.and_eq_true] at hok
    obtain ⟨hokB, hncEqB⟩ := hok
    have hncEq : ncB g c g' a = c' := beq_iff_eq.mp hncEqB
    have hSOK : stackOK S (xL + a, (i : ℤ) + 1) (xL + a + (g' : ℤ), (i : ℤ) + 1) :=
      (stack_cond_iff hT.1 hTy htL htR hrow hOK hc g' hg' a).mpr hokB
    have hSc : c' = true ↔ reach S (xL + a, (i : ℤ) + 1) (xL + a + (g' : ℤ), (i : ℤ) + 1) := by
      rw [← hncEq]
      exact (class_iff hT.1 hTy htL htR hrow hOK hc g' hg' a hokB).symm
    refine ⟨hg', hcardS, hanchorS, hboundsS, hrow1S, hrowIccS,
      (xL + a, (i : ℤ) + 1), huS, rfl, hvS, hSOK, hSc⟩

/-! ## Truncation lands in the source states -/

/-- `near` unfolded to the arithmetic `natAbs` fact `decide` computes. -/
private theorem near_true_iff (t : ℤ) : near t = true ↔ t.natAbs ≤ 1 := by
  unfold near; rw [decide_eq_true_eq]

/-- The class Boolean built from `decide` on `reach` reports exactly `reach`. -/
private theorem decide_reach_iff {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} :
    (decide (reach S p q) = true) ↔ reach S p q := by
  rw [decide_eq_true_eq]

/-- Filtering by `·.2 ≤ i` doesn't disturb `rowSize` at a row `y ≤ i`. -/
private theorem rowSize_filter_le {S : Finset (ℤ × ℤ)} {i y : ℤ} (hy : y ≤ i) :
    rowSize (S.filter fun p => p.2 ≤ i) y = rowSize S y := by
  unfold rowSize
  rw [Finset.filter_filter]
  congr 1
  apply Finset.filter_congr
  intro p _
  constructor
  · rintro ⟨_, h⟩; exact h
  · intro h; exact ⟨h ▸ hy, h⟩

/-- Truncating an `(i+1)`-row interior stack gives an `i`-row interior
stack. Row bookkeeping: `τ S` keeps rows `≤ i` verbatim, drops exactly the
two top cells; connectivity: `trunc_stackOK`; class/gap: read off row `i`
(`row_two_cells`); the `∃`-witness is the left row-`i` cell. -/
theorem isStackI_trunc {i g' : ℕ} {c' : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI (i + 1) g' c' S) :
    ∃ g c, IsStackI i g c (S.filter fun p => p.2 ≤ (i : ℤ)) ∧
      1 ≤ g ∧ (c = true → g ≤ 2 * i) ∧ (c = false → g ≤ g' + 2) := by
  set T := S.filter fun p => p.2 ≤ (i : ℤ) with hTdef
  obtain ⟨huS, hvS, hmaxeq, hSOK, hSc, hSrow⟩ := isStackI_top (by omega : 1 ≤ i + 1) h
  set u := (rowMinX S ((i : ℤ) + 1), (i : ℤ) + 1) with hudef
  set v := (rowMinX S ((i : ℤ) + 1) + (g' : ℤ), (i : ℤ) + 1) with hvdef
  have hmemT : ∀ p ∈ S, p.2 ≤ (i : ℤ) → p ∈ T := fun p hp hp2 =>
    Finset.mem_filter.mpr ⟨hp, hp2⟩
  have hTmemS : ∀ p ∈ T, p ∈ S := fun p hp => (Finset.mem_filter.mp hp).1
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (Finset.mem_filter.mp hp).2
  have hSeq : S = insert u (insert v T) := by
    apply Finset.ext
    intro p
    constructor
    · intro hp
      obtain ⟨h1, h2⟩ := h.2.2.2.1 p hp
      rcases eq_or_lt_of_le h2 with heq | hlt
      · rcases hSrow p hp heq with rfl | rfl
        · exact Finset.mem_insert_self _ _
        · exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
      · exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (hmemT p hp (by omega)))
    · intro hp
      rw [Finset.mem_insert, Finset.mem_insert] at hp
      rcases hp with rfl | rfl | hp
      · exact huS
      · exact hvS
      · exact hTmemS p hp
  have huT : u ∉ T := fun hmem => by
    have := hTy u hmem
    simp only [hudef] at this
    omega
  have hvT : v ∉ T := fun hmem => by
    have := hTy v hmem
    simp only [hvdef] at this
    omega
  have huv : u ≠ v := by
    intro heq
    have h1 : rowMinX S ((i : ℤ) + 1) = rowMinX S ((i : ℤ) + 1) + (g' : ℤ) :=
      congrArg Prod.fst heq
    have : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast h.1
    omega
  have hTcard : T.card = 2 * i + 1 := by
    have : S.card = T.card + 2 := by
      rw [hSeq, Finset.card_insert_of_notMem, Finset.card_insert_of_notMem hvT]
      rw [Finset.mem_insert]
      rintro (heq | heq)
      · exact huv heq
      · exact huT heq
    have hScard : S.card = 2 * (i + 1) + 1 := h.2.1
    omega
  have hTanchor : ((0 : ℤ), (0 : ℤ)) ∈ T := hmemT _ h.2.2.1 (by omega)
  have hTbounds : ∀ p ∈ T, 0 ≤ p.2 ∧ p.2 ≤ (i : ℤ) := fun p hp =>
    ⟨(h.2.2.2.1 p (hTmemS p hp)).1, hTy p hp⟩
  have hTrow0 : rowSize T 0 = 1 := by
    rw [hTdef, rowSize_filter_le (by omega)]
    exact h.2.2.2.2.1
  have hTrowIcc : ∀ r ∈ Finset.Icc 1 i, rowSize T (r : ℤ) = 2 := by
    intro r hr
    rw [Finset.mem_Icc] at hr
    rw [hTdef, rowSize_filter_le (by exact_mod_cast hr.2)]
    exact h.2.2.2.2.2.1 r (Finset.mem_Icc.mpr ⟨hr.1, by omega⟩)
  have hTrowi2 : rowSize T (i : ℤ) = 2 := hTrowIcc i (Finset.mem_Icc.mpr ⟨hi, le_refl i⟩)
  obtain ⟨tL, tR, htLT, htRT, htLy, htRy, htlt, htrow⟩ := row_two_cells hTrowi2
  set g := (tR.1 - tL.1).toNat with hgdef
  have hgpos : (0 : ℤ) < tR.1 - tL.1 := by omega
  have hgcast : (g : ℤ) = tR.1 - tL.1 := by
    rw [hgdef]; omega
  have htRfix : tR = (tL.1 + (g : ℤ), (i : ℤ)) := by
    apply Prod.ext
    · simp only; omega
    · simp only [htRy]
  have htLfix : tL = (tL.1, (i : ℤ)) := Prod.ext rfl htLy
  have hrowT : ∀ q ∈ T, q.2 = (i : ℤ) → q = (tL.1, (i : ℤ)) ∨ q = (tL.1 + (g : ℤ), (i : ℤ)) := by
    intro q hq hqy
    rcases htrow q hq hqy with rfl | rfl
    · exact Or.inl htLfix
    · exact Or.inr htRfix
  have ha : u.1 - tL.1 = u.1 - tL.1 := rfl
  set a := u.1 - tL.1 with hadef
  have huv_eq : u = (tL.1 + a, (i : ℤ) + 1) := by
    apply Prod.ext
    · simp only; omega
    · rfl
  have hv_eq : v = (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) := by
    apply Prod.ext
    · simp only [hvdef, hudef, hadef]; omega
    · rfl
  have hSeq' : S =
      insert (tL.1 + a, (i : ℤ) + 1) (insert (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) T) := by
    rw [hSeq, huv_eq, hv_eq]
  have hSOK' : stackOK
      (insert (tL.1 + a, (i : ℤ) + 1) (insert (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) T))
      (tL.1 + a, (i : ℤ) + 1) (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) := by
    rw [← hSeq', ← huv_eq, ← hv_eq]
    exact hSOK
  have htLTfix : (tL.1, (i : ℤ)) ∈ T := htLfix ▸ htLT
  have htRTfix : (tL.1 + (g : ℤ), (i : ℤ)) ∈ T := htRfix ▸ htRT
  have hTOK : stackOK T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) :=
    trunc_stackOK (by omega : 1 ≤ g) hTy htLTfix htRTfix hrowT g' h.1 a hSOK'
  refine ⟨g, decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ))), ⟨by omega, hTcard,
    hTanchor, hTbounds, hTrow0, hTrowIcc, (tL.1, (i : ℤ)), htLTfix, rfl, htRTfix, hTOK,
    decide_reach_iff⟩, by omega, ?_, ?_⟩
  · intro hcJ
    have hreach : reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) := decide_reach_iff.mp hcJ
    have hbound := reach_abs_x_le hreach htLTfix htRTfix
    rw [abs_le] at hbound
    have hcardZ : (T.card : ℤ) = 2 * (i : ℤ) + 1 := by exact_mod_cast hTcard
    omega
  · intro hcP
    have hnreach : ¬ reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) := by
      rw [decide_eq_false_iff_not] at hcP
      exact hcP
    -- The stack condition on `S'` at the frame (T, tL, tR, g) with class `false`
    -- pins both tops into the window of width g' + 2 around the new row.
    have hokB : okB g (decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)))) g' a = true :=
      (stack_cond_iff (by omega : 1 ≤ g) hTy htLTfix htRTfix hrowT
        (fun p hp => hTOK p hp) decide_reach_iff g' h.1 a).mp hSOK'
    have hcPeq : decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ))) = false := by
      rw [decide_eq_false_iff_not]; exact hnreach
    rw [hcPeq] at hokB
    simp only [okB, if_neg (by decide : ¬ ((false : Bool) = true)), Bool.and_eq_true,
      Bool.or_eq_true, near_true_iff] at hokB
    obtain ⟨htouch0, htouchg⟩ := hokB
    have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast h.1
    omega

theorem isStackB_trunc {i g' : ℕ} {c' : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB (i + 1) g' c' S) :
    ∃ g c, IsStackB i g c (S.filter fun p => p.2 ≤ (i : ℤ)) ∧
      1 ≤ g ∧ (c = true → g ≤ 2 * i) ∧ (c = false → g ≤ g' + 2) := by
  set T := S.filter fun p => p.2 ≤ (i : ℤ) with hTdef
  obtain ⟨huS, hvS, hmaxeq, hSOK, hSc, hSrow⟩ := isStackB_top (by omega : 1 ≤ i + 1) h
  set u := (rowMinX S ((i : ℤ) + 1), (i : ℤ) + 1) with hudef
  set v := (rowMinX S ((i : ℤ) + 1) + (g' : ℤ), (i : ℤ) + 1) with hvdef
  have hmemT : ∀ p ∈ S, p.2 ≤ (i : ℤ) → p ∈ T := fun p hp hp2 =>
    Finset.mem_filter.mpr ⟨hp, hp2⟩
  have hTmemS : ∀ p ∈ T, p ∈ S := fun p hp => (Finset.mem_filter.mp hp).1
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (Finset.mem_filter.mp hp).2
  have hSeq : S = insert u (insert v T) := by
    apply Finset.ext
    intro p
    constructor
    · intro hp
      obtain ⟨h1, h2⟩ := h.2.2.2.1 p hp
      rcases eq_or_lt_of_le h2 with heq | hlt
      · rcases hSrow p hp heq with rfl | rfl
        · exact Finset.mem_insert_self _ _
        · exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
      · exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (hmemT p hp (by omega)))
    · intro hp
      rw [Finset.mem_insert, Finset.mem_insert] at hp
      rcases hp with rfl | rfl | hp
      · exact huS
      · exact hvS
      · exact hTmemS p hp
  have huT : u ∉ T := fun hmem => by
    have := hTy u hmem
    simp only [hudef] at this
    omega
  have hvT : v ∉ T := fun hmem => by
    have := hTy v hmem
    simp only [hvdef] at this
    omega
  have huv : u ≠ v := by
    intro heq
    have h1 : rowMinX S ((i : ℤ) + 1) = rowMinX S ((i : ℤ) + 1) + (g' : ℤ) :=
      congrArg Prod.fst heq
    have : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast h.1
    omega
  have hTcard : T.card = 2 * i := by
    have : S.card = T.card + 2 := by
      rw [hSeq, Finset.card_insert_of_notMem, Finset.card_insert_of_notMem hvT]
      rw [Finset.mem_insert]
      rintro (heq | heq)
      · exact huv heq
      · exact huT heq
    have hScard : S.card = 2 * (i + 1) := h.2.1
    omega
  have hTanchor : ((0 : ℤ), (1 : ℤ)) ∈ T := hmemT _ h.2.2.1 (by omega)
  have hTbounds : ∀ p ∈ T, 1 ≤ p.2 ∧ p.2 ≤ (i : ℤ) := fun p hp =>
    ⟨(h.2.2.2.1 p (hTmemS p hp)).1, hTy p hp⟩
  have hTrow1 : ∀ p ∈ T, p.2 = 1 → 0 ≤ p.1 := fun p hp hp1 =>
    h.2.2.2.2.1 p (hTmemS p hp) hp1
  have hTrowIcc : ∀ r ∈ Finset.Icc 1 i, rowSize T (r : ℤ) = 2 := by
    intro r hr
    rw [Finset.mem_Icc] at hr
    rw [hTdef, rowSize_filter_le (by exact_mod_cast hr.2)]
    exact h.2.2.2.2.2.1 r (Finset.mem_Icc.mpr ⟨hr.1, by omega⟩)
  have hTrowi2 : rowSize T (i : ℤ) = 2 := hTrowIcc i (Finset.mem_Icc.mpr ⟨hi, le_refl i⟩)
  obtain ⟨tL, tR, htLT, htRT, htLy, htRy, htlt, htrow⟩ := row_two_cells hTrowi2
  set g := (tR.1 - tL.1).toNat with hgdef
  have hgpos : (0 : ℤ) < tR.1 - tL.1 := by omega
  have hgcast : (g : ℤ) = tR.1 - tL.1 := by
    rw [hgdef]; omega
  have htRfix : tR = (tL.1 + (g : ℤ), (i : ℤ)) := by
    apply Prod.ext
    · simp only; omega
    · simp only [htRy]
  have htLfix : tL = (tL.1, (i : ℤ)) := Prod.ext rfl htLy
  have hrowT : ∀ q ∈ T, q.2 = (i : ℤ) → q = (tL.1, (i : ℤ)) ∨ q = (tL.1 + (g : ℤ), (i : ℤ)) := by
    intro q hq hqy
    rcases htrow q hq hqy with rfl | rfl
    · exact Or.inl htLfix
    · exact Or.inr htRfix
  set a := u.1 - tL.1 with hadef
  have huv_eq : u = (tL.1 + a, (i : ℤ) + 1) := by
    apply Prod.ext
    · simp only; omega
    · rfl
  have hv_eq : v = (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) := by
    apply Prod.ext
    · simp only [hvdef, hudef, hadef]; omega
    · rfl
  have hSeq' : S =
      insert (tL.1 + a, (i : ℤ) + 1) (insert (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) T) := by
    rw [hSeq, huv_eq, hv_eq]
  have hSOK' : stackOK
      (insert (tL.1 + a, (i : ℤ) + 1) (insert (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) T))
      (tL.1 + a, (i : ℤ) + 1) (tL.1 + a + (g' : ℤ), (i : ℤ) + 1) := by
    rw [← hSeq', ← huv_eq, ← hv_eq]
    exact hSOK
  have htLTfix : (tL.1, (i : ℤ)) ∈ T := htLfix ▸ htLT
  have htRTfix : (tL.1 + (g : ℤ), (i : ℤ)) ∈ T := htRfix ▸ htRT
  have hTOK : stackOK T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) :=
    trunc_stackOK (by omega : 1 ≤ g) hTy htLTfix htRTfix hrowT g' h.1 a hSOK'
  refine ⟨g, decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ))), ⟨by omega, hTcard,
    hTanchor, hTbounds, hTrow1, hTrowIcc, (tL.1, (i : ℤ)), htLTfix, rfl, htRTfix, hTOK,
    decide_reach_iff⟩, by omega, ?_, ?_⟩
  · intro hcJ
    have hreach : reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) := decide_reach_iff.mp hcJ
    have hbound := reach_abs_x_le hreach htLTfix htRTfix
    rw [abs_le] at hbound
    have hcardZ : (T.card : ℤ) = 2 * (i : ℤ) := by exact_mod_cast hTcard
    omega
  · intro hcP
    have hnreach : ¬ reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)) := by
      rw [decide_eq_false_iff_not] at hcP
      exact hcP
    have hokB : okB g (decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ)))) g' a = true :=
      (stack_cond_iff (by omega : 1 ≤ g) hTy htLTfix htRTfix hrowT
        (fun p hp => hTOK p hp) decide_reach_iff g' h.1 a).mp hSOK'
    have hcPeq : decide (reach T (tL.1, (i : ℤ)) (tL.1 + (g : ℤ), (i : ℤ))) = false := by
      rw [decide_eq_false_iff_not]; exact hnreach
    rw [hcPeq] at hokB
    simp only [okB, if_neg (by decide : ¬ ((false : Bool) = true)), Bool.and_eq_true,
      Bool.or_eq_true, near_true_iff] at hokB
    obtain ⟨htouch0, htouchg⟩ := hokB
    have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast h.1
    omega

/-! ## The recursion -/

/-- `List.sum` over a `Nodup` list's own `toFinset` matches the `Finset.sum`. -/
private theorem sum_toFinset_eq_sum_list {α : Type*} [DecidableEq α] {l : List α}
    (hl : l.Nodup) (f : α → ℕ) : ∑ x ∈ l.toFinset, f x = (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
      rw [List.nodup_cons] at hl
      rw [List.toFinset_cons, Finset.sum_insert (by rw [List.mem_toFinset]; exact hl.1),
        ih hl.2, List.map_cons, List.sum_cons]

/-- `okB` pins the offset into a window around `[-g'-1, g+1]` (union of the
four `near`-windows the four contact Booleans can certify). -/
private theorem okB_window {g g' : ℕ} {c : Bool} {a : ℤ} (hok : okB g c g' a = true) :
    -(g' : ℤ) - 1 ≤ a ∧ a ≤ (g : ℤ) + 1 := by
  cases c with
  | false =>
      simp only [okB, if_neg (by decide : ¬ ((false : Bool) = true)), Bool.and_eq_true,
        Bool.or_eq_true, near_true_iff] at hok
      omega
  | true =>
      simp only [okB, if_true, Bool.or_eq_true, near_true_iff] at hok
      omega

/-- The fiber of the truncation map over a fixed `T ∈ STKI i g c` has exactly
`stepMul g c g' c'` elements: the assembled-set bijection with the
`stepMul_eq_card` window. -/
private theorem STKI_fiber_card {i g : ℕ} {c : Bool} (hi : 1 ≤ i) {T : Finset (ℤ × ℤ)}
    (hT : IsStackI i g c T) (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) :
    ((STKI (i + 1) g' c').filter (fun S => S.filter (fun p => p.2 ≤ (i : ℤ)) = T)).card =
      GapWalk.stepMul g c g' c' := by
  classical
  set xL := rowMinX T (i : ℤ) with hxLdef
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (hT.2.2.2.1 p hp).2
  rw [stepMul_eq_card]
  symm
  refine Finset.card_nbij
    (fun n => insert (xL + ((n : ℤ) - ((g' : ℤ) + 2)), (i : ℤ) + 1)
      (insert (xL + ((n : ℤ) - ((g' : ℤ) + 2)) + (g' : ℤ), (i : ℤ) + 1) T))
    ?_ ?_ ?_
  · -- MapsTo
    intro n hn
    simp only [Finset.mem_coe, Finset.mem_filter] at hn ⊢
    obtain ⟨-, hnpred⟩ := hn
    rw [Bool.and_eq_true, beq_iff_eq] at hnpred
    refine ⟨?_, ?_⟩
    · rw [mem_STKI (by omega)]
      exact (isStackI_insert_iff hi hT g' hg' c' _).mpr
        (by rw [Bool.and_eq_true, beq_iff_eq]; exact hnpred)
    · apply Finset.ext
      intro p
      simp only [Finset.mem_filter, Finset.mem_insert]
      constructor
      · rintro ⟨(rfl | rfl | hp), hple⟩
        · omega
        · omega
        · exact hp
      · intro hp
        exact ⟨Or.inr (Or.inr hp), hTy p hp⟩
  · -- injective
    intro n1 hn1 n2 hn2 heq
    simp only [Finset.coe_filter, Set.mem_setOf_eq, Finset.mem_range] at hn1 hn2
    have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
    set a1 := (n1 : ℤ) - ((g' : ℤ) + 2) with ha1def
    set a2 := (n2 : ℤ) - ((g' : ℤ) + 2) with ha2def
    have hrowsize : ∀ b : ℤ, rowSize
        (insert (xL + b, (i : ℤ) + 1) (insert (xL + b + (g' : ℤ), (i : ℤ) + 1) T))
        ((i : ℤ) + 1) = 2 := by
      intro b
      have huT : (xL + b, (i : ℤ) + 1) ∉ insert (xL + b + (g' : ℤ), (i : ℤ) + 1) T := by
        rw [Finset.mem_insert]
        rintro (h | h)
        · have := congrArg Prod.fst h; omega
        · have h2 : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ h
          omega
      have hvT : (xL + b + (g' : ℤ), (i : ℤ) + 1) ∉ T := fun h => by
        have h2 : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ h
        omega
      rw [rowSize_insert_same (y := (i : ℤ) + 1) huT rfl,
        rowSize_insert_same (y := (i : ℤ) + 1) hvT rfl]
      have hT0 : rowSize T ((i : ℤ) + 1) = 0 := by
        unfold rowSize
        rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
        intro p hp
        have := hTy p hp
        omega
      omega
    have hne : ∀ b : ℤ, (xL + b, (i : ℤ) + 1) ≠ (xL + b + (g' : ℤ), (i : ℤ) + 1) := by
      intro b h
      have := congrArg Prod.fst h
      omega
    have hpair1 := row_eq_pair (hrowsize a1) (Finset.mem_insert_self _ _)
      (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)) rfl rfl (hne a1)
    have heq' : insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) =
        insert (xL + a2, (i : ℤ) + 1) (insert (xL + a2 + (g' : ℤ), (i : ℤ) + 1) T) := heq
    have hu2in1 : (xL + a2, (i : ℤ) + 1) ∈
        insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [heq']; exact Finset.mem_insert_self _ _
    have hv2in1 : (xL + a2 + (g' : ℤ), (i : ℤ) + 1) ∈
        insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [heq']; exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
    rcases hpair1 _ hu2in1 rfl with hu2eq | hu2eq
    · have e1 := congrArg Prod.fst hu2eq
      omega
    · rcases hpair1 _ hv2in1 rfl with hv2eq | hv2eq
      · exfalso
        have e1 := congrArg Prod.fst hu2eq
        have e2 := congrArg Prod.fst hv2eq
        omega
      · exfalso
        have e1 := congrArg Prod.fst hu2eq
        have e2 := congrArg Prod.fst hv2eq
        omega
  · -- surjective
    intro S hS
    simp only [Finset.coe_filter, Set.mem_setOf_eq] at hS
    obtain ⟨hSmem, hSfilter⟩ := hS
    rw [mem_STKI (by omega : 1 ≤ i + 1)] at hSmem
    obtain ⟨huS', hvS', hmaxeq', hSOK', hSc', hSrow'⟩ := isStackI_top (by omega : 1 ≤ i + 1) hSmem
    push_cast at huS' hvS' hmaxeq' hSOK' hSc' hSrow' hSmem
    set a := rowMinX S ((i : ℤ) + 1) - xL with hadef
    have hrmXeq : rowMinX S ((i : ℤ) + 1) = xL + a := by omega
    rw [hrmXeq] at huS' hvS' hSrow' hSOK' hSc'
    have hSeq : S = insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [← hSfilter]
      apply Finset.ext
      intro p
      constructor
      · intro hp
        obtain ⟨h1, h2⟩ := hSmem.2.2.2.1 p hp
        rcases eq_or_lt_of_le h2 with heq2 | hlt2
        · rcases hSrow' p hp heq2 with rfl | rfl
          · exact Finset.mem_insert_self _ _
          · exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
        · exact Finset.mem_insert_of_mem
            (Finset.mem_insert_of_mem (Finset.mem_filter.mpr ⟨hp, by omega⟩))
      · intro hp
        rw [Finset.mem_insert, Finset.mem_insert] at hp
        rcases hp with rfl | rfl | hp
        · exact huS'
        · exact hvS'
        · exact (Finset.mem_filter.mp hp).1
    have hSmem' : IsStackI (i + 1) g' c'
        (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T)) := by
      rw [← hSeq]; exact hSmem
    have hokBc' : (okB g c g' a && (ncB g c g' a == c')) = true :=
      (isStackI_insert_iff hi hT g' hg' c' a).mp hSmem'
    rw [Bool.and_eq_true] at hokBc'
    have hwin := okB_window hokBc'.1
    refine ⟨(a + (g' : ℤ) + 2).toNat, ?_, ?_⟩
    · simp only [Finset.coe_filter, Set.mem_setOf_eq, Finset.mem_range]
      have hna : ((a + (g' : ℤ) + 2).toNat : ℤ) = a + (g' : ℤ) + 2 := by omega
      refine ⟨by omega, ?_⟩
      rw [Bool.and_eq_true, beq_iff_eq]
      have heqa : ((a + (g' : ℤ) + 2).toNat : ℤ) - ((g' : ℤ) + 2) = a := by omega
      rw [heqa]
      exact ⟨hokBc'.1, beq_iff_eq.mp hokBc'.2⟩
    · have heqa : ((a + (g' : ℤ) + 2).toNat : ℤ) - ((g' : ℤ) + 2) = a := by omega
      dsimp only
      rw [heqa]
      exact hSeq.symm

/-- **The interior stack counts satisfy the walk recursion.** Fiberwise
count over the truncation map into
`U = (states B).toFinset.biUnion (fun s => STKI i s.1 s.2)`
(`Finset.card_eq_sum_card_fiberwise`, target membership by
`isStackI_trunc` + the gap bounds + `mem_STKI`); split the sum over the
`biUnion` (`Finset.sum_biUnion`; disjointness from
`isStackI_state_unique`); per `T`, the fiber
`(STKI (i+1) g' c').filter (fun S => τ S = T)` is in `Finset.card_bij`
with the `stepMul_eq_card` window via `n ↦` the assembled set at
`a = n − (g' + 2)`:

* membership: `isStackI_insert_iff` (←) plus `τ (assembled) = T`;
* injectivity: two offsets giving the same set give the same row-`(i+1)`
  left cell, and the assembled left cell is `rowMinX T i + a` (its row is
  exactly the two new cells, `a`-monotone);
* surjectivity: for `S` in the fiber, `S = insert u (insert v (τ S))` with
  `u` the top-left witness (rows `≤ i` are `τ S`, row `i+1` is `{u, v}` by
  `row_eq_pair`); its offset lies in the window because `okB` holds
  (`isStackI_insert_iff` (→) after rebuilding `S` in assembled form), and
  `okB` pins `−g'−1 ≤ a ≤ g+1` (omega on the `near`s);

finally `List.sum_toFinset` (with `states_nodup`) turns the `Finset` sum
into `funStep`'s list sum. -/
theorem STKI_card_step (i : ℕ) (hi : 1 ≤ i) (g' : ℕ) (hg' : 1 ≤ g')
    (c' : Bool) (B : ℕ) (hB1 : 2 * i ≤ B) (hB2 : g' + 2 ≤ B) :
    (STKI (i + 1) g' c').card =
      funStep B (fun s => (STKI i s.1 s.2).card) (g', c') := by
  classical
  set U := (GapWalk.states B).toFinset.biUnion (fun s => STKI i s.1 s.2) with hUdef
  have hMaps : Set.MapsTo (fun S : Finset (ℤ × ℤ) => S.filter (fun p => p.2 ≤ (i : ℤ)))
      (↑(STKI (i + 1) g' c') : Set (Finset (ℤ × ℤ))) (↑U : Set (Finset (ℤ × ℤ))) := by
    intro S hS
    rw [Finset.mem_coe] at hS
    rw [mem_STKI (by omega)] at hS
    obtain ⟨g, c, hTin, hg1, hgJ, hgP⟩ := isStackI_trunc hi hS
    have hgle : g ≤ B := by
      cases c with
      | true => have h2 := hgJ rfl; omega
      | false => have h2 := hgP rfl; omega
    rw [Finset.mem_coe, hUdef, Finset.mem_biUnion]
    refine ⟨(g, c), ?_, ?_⟩
    · rw [List.mem_toFinset, GapWalk.mem_states]
      exact ⟨hg1, hgle⟩
    · rw [mem_STKI hi]; exact hTin
  have hdisj : ((GapWalk.states B).toFinset : Set (ℕ × Bool)).PairwiseDisjoint
      (fun s : ℕ × Bool => STKI i s.1 s.2) := by
    intro x _ y _ hxy
    change Disjoint (STKI i x.1 x.2) (STKI i y.1 y.2)
    rw [Finset.disjoint_left]
    intro T hTx hTy
    rw [mem_STKI hi] at hTx hTy
    exact hxy (Prod.ext (isStackI_state_unique hi hTx hTy).1 (isStackI_state_unique hi hTx hTy).2)
  rw [Finset.card_eq_sum_card_fiberwise hMaps, hUdef, Finset.sum_biUnion hdisj]
  rw [funStep]
  rw [← sum_toFinset_eq_sum_list (states_nodup B)]
  apply Finset.sum_congr rfl
  intro s _
  rw [Finset.sum_congr rfl
      (fun T hT => STKI_fiber_card hi (T := T) ((mem_STKI hi).mp hT) g' hg' c'),
    Finset.sum_const, smul_eq_mul]

/-- **The bare stack counts satisfy the walk recursion.** Same proof over
`IsStackB`. -/
private theorem STKB_fiber_card {i g : ℕ} {c : Bool} (hi : 1 ≤ i) {T : Finset (ℤ × ℤ)}
    (hT : IsStackB i g c T) (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) :
    ((STKB (i + 1) g' c').filter (fun S => S.filter (fun p => p.2 ≤ (i : ℤ)) = T)).card =
      GapWalk.stepMul g c g' c' := by
  classical
  set xL := rowMinX T (i : ℤ) with hxLdef
  have hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ) := fun p hp => (hT.2.2.2.1 p hp).2
  rw [stepMul_eq_card]
  symm
  refine Finset.card_nbij
    (fun n => insert (xL + ((n : ℤ) - ((g' : ℤ) + 2)), (i : ℤ) + 1)
      (insert (xL + ((n : ℤ) - ((g' : ℤ) + 2)) + (g' : ℤ), (i : ℤ) + 1) T))
    ?_ ?_ ?_
  · -- MapsTo
    intro n hn
    simp only [Finset.mem_coe, Finset.mem_filter] at hn ⊢
    obtain ⟨-, hnpred⟩ := hn
    rw [Bool.and_eq_true, beq_iff_eq] at hnpred
    refine ⟨?_, ?_⟩
    · rw [mem_STKB (by omega)]
      exact (isStackB_insert_iff hi hT g' hg' c' _).mpr
        (by rw [Bool.and_eq_true, beq_iff_eq]; exact hnpred)
    · apply Finset.ext
      intro p
      simp only [Finset.mem_filter, Finset.mem_insert]
      constructor
      · rintro ⟨(rfl | rfl | hp), hple⟩
        · omega
        · omega
        · exact hp
      · intro hp
        exact ⟨Or.inr (Or.inr hp), hTy p hp⟩
  · -- injective
    intro n1 hn1 n2 hn2 heq
    simp only [Finset.coe_filter, Set.mem_setOf_eq, Finset.mem_range] at hn1 hn2
    have hgz : (0 : ℤ) < (g' : ℤ) := by exact_mod_cast hg'
    set a1 := (n1 : ℤ) - ((g' : ℤ) + 2) with ha1def
    set a2 := (n2 : ℤ) - ((g' : ℤ) + 2) with ha2def
    have hrowsize : ∀ b : ℤ, rowSize
        (insert (xL + b, (i : ℤ) + 1) (insert (xL + b + (g' : ℤ), (i : ℤ) + 1) T))
        ((i : ℤ) + 1) = 2 := by
      intro b
      have huT : (xL + b, (i : ℤ) + 1) ∉ insert (xL + b + (g' : ℤ), (i : ℤ) + 1) T := by
        rw [Finset.mem_insert]
        rintro (h | h)
        · have := congrArg Prod.fst h; omega
        · have h2 : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ h
          omega
      have hvT : (xL + b + (g' : ℤ), (i : ℤ) + 1) ∉ T := fun h => by
        have h2 : (i : ℤ) + 1 ≤ (i : ℤ) := hTy _ h
        omega
      rw [rowSize_insert_same (y := (i : ℤ) + 1) huT rfl,
        rowSize_insert_same (y := (i : ℤ) + 1) hvT rfl]
      have hT0 : rowSize T ((i : ℤ) + 1) = 0 := by
        unfold rowSize
        rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
        intro p hp
        have := hTy p hp
        omega
      omega
    have hne : ∀ b : ℤ, (xL + b, (i : ℤ) + 1) ≠ (xL + b + (g' : ℤ), (i : ℤ) + 1) := by
      intro b h
      have := congrArg Prod.fst h
      omega
    have hpair1 := row_eq_pair (hrowsize a1) (Finset.mem_insert_self _ _)
      (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)) rfl rfl (hne a1)
    have heq' : insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) =
        insert (xL + a2, (i : ℤ) + 1) (insert (xL + a2 + (g' : ℤ), (i : ℤ) + 1) T) := heq
    have hu2in1 : (xL + a2, (i : ℤ) + 1) ∈
        insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [heq']; exact Finset.mem_insert_self _ _
    have hv2in1 : (xL + a2 + (g' : ℤ), (i : ℤ) + 1) ∈
        insert (xL + a1, (i : ℤ) + 1) (insert (xL + a1 + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [heq']; exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
    rcases hpair1 _ hu2in1 rfl with hu2eq | hu2eq
    · have e1 := congrArg Prod.fst hu2eq
      omega
    · rcases hpair1 _ hv2in1 rfl with hv2eq | hv2eq
      · exfalso
        have e1 := congrArg Prod.fst hu2eq
        have e2 := congrArg Prod.fst hv2eq
        omega
      · exfalso
        have e1 := congrArg Prod.fst hu2eq
        have e2 := congrArg Prod.fst hv2eq
        omega
  · -- surjective
    intro S hS
    simp only [Finset.coe_filter, Set.mem_setOf_eq] at hS
    obtain ⟨hSmem, hSfilter⟩ := hS
    rw [mem_STKB (by omega : 1 ≤ i + 1)] at hSmem
    obtain ⟨huS', hvS', hmaxeq', hSOK', hSc', hSrow'⟩ := isStackB_top (by omega : 1 ≤ i + 1) hSmem
    push_cast at huS' hvS' hmaxeq' hSOK' hSc' hSrow' hSmem
    set a := rowMinX S ((i : ℤ) + 1) - xL with hadef
    have hrmXeq : rowMinX S ((i : ℤ) + 1) = xL + a := by omega
    rw [hrmXeq] at huS' hvS' hSrow' hSOK' hSc'
    have hSeq : S = insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T) := by
      rw [← hSfilter]
      apply Finset.ext
      intro p
      constructor
      · intro hp
        obtain ⟨h1, h2⟩ := hSmem.2.2.2.1 p hp
        rcases eq_or_lt_of_le h2 with heq2 | hlt2
        · rcases hSrow' p hp heq2 with rfl | rfl
          · exact Finset.mem_insert_self _ _
          · exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
        · exact Finset.mem_insert_of_mem
            (Finset.mem_insert_of_mem (Finset.mem_filter.mpr ⟨hp, by omega⟩))
      · intro hp
        rw [Finset.mem_insert, Finset.mem_insert] at hp
        rcases hp with rfl | rfl | hp
        · exact huS'
        · exact hvS'
        · exact (Finset.mem_filter.mp hp).1
    have hSmem' : IsStackB (i + 1) g' c'
        (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (g' : ℤ), (i : ℤ) + 1) T)) := by
      rw [← hSeq]; exact hSmem
    have hokBc' : (okB g c g' a && (ncB g c g' a == c')) = true :=
      (isStackB_insert_iff hi hT g' hg' c' a).mp hSmem'
    rw [Bool.and_eq_true] at hokBc'
    have hwin := okB_window hokBc'.1
    refine ⟨(a + (g' : ℤ) + 2).toNat, ?_, ?_⟩
    · simp only [Finset.coe_filter, Set.mem_setOf_eq, Finset.mem_range]
      have hna : ((a + (g' : ℤ) + 2).toNat : ℤ) = a + (g' : ℤ) + 2 := by omega
      refine ⟨by omega, ?_⟩
      rw [Bool.and_eq_true, beq_iff_eq]
      have heqa : ((a + (g' : ℤ) + 2).toNat : ℤ) - ((g' : ℤ) + 2) = a := by omega
      rw [heqa]
      exact ⟨hokBc'.1, beq_iff_eq.mp hokBc'.2⟩
    · have heqa : ((a + (g' : ℤ) + 2).toNat : ℤ) - ((g' : ℤ) + 2) = a := by omega
      dsimp only
      rw [heqa]
      exact hSeq.symm

theorem STKB_card_step (i : ℕ) (hi : 1 ≤ i) (g' : ℕ) (hg' : 1 ≤ g')
    (c' : Bool) (B : ℕ) (hB1 : 2 * i ≤ B) (hB2 : g' + 2 ≤ B) :
    (STKB (i + 1) g' c').card =
      funStep B (fun s => (STKB i s.1 s.2).card) (g', c') := by
  classical
  set U := (GapWalk.states B).toFinset.biUnion (fun s => STKB i s.1 s.2) with hUdef
  have hMaps : Set.MapsTo (fun S : Finset (ℤ × ℤ) => S.filter (fun p => p.2 ≤ (i : ℤ)))
      (↑(STKB (i + 1) g' c') : Set (Finset (ℤ × ℤ))) (↑U : Set (Finset (ℤ × ℤ))) := by
    intro S hS
    rw [Finset.mem_coe] at hS
    rw [mem_STKB (by omega)] at hS
    obtain ⟨g, c, hTin, hg1, hgJ, hgP⟩ := isStackB_trunc hi hS
    have hgle : g ≤ B := by
      cases c with
      | true => have h2 := hgJ rfl; omega
      | false => have h2 := hgP rfl; omega
    rw [Finset.mem_coe, hUdef, Finset.mem_biUnion]
    refine ⟨(g, c), ?_, ?_⟩
    · rw [List.mem_toFinset, GapWalk.mem_states]
      exact ⟨hg1, hgle⟩
    · rw [mem_STKB hi]; exact hTin
  have hdisj : ((GapWalk.states B).toFinset : Set (ℕ × Bool)).PairwiseDisjoint
      (fun s : ℕ × Bool => STKB i s.1 s.2) := by
    intro x _ y _ hxy
    change Disjoint (STKB i x.1 x.2) (STKB i y.1 y.2)
    rw [Finset.disjoint_left]
    intro T hTx hTy
    rw [mem_STKB hi] at hTx hTy
    exact hxy (Prod.ext (isStackB_state_unique hi hTx hTy).1 (isStackB_state_unique hi hTx hTy).2)
  rw [Finset.card_eq_sum_card_fiberwise hMaps, hUdef, Finset.sum_biUnion hdisj]
  rw [funStep]
  rw [← sum_toFinset_eq_sum_list (states_nodup B)]
  apply Finset.sum_congr rfl
  intro s _
  rw [Finset.sum_congr rfl
      (fun T hT => STKB_fiber_card hi (T := T) ((mem_STKB hi).mp hT) g' hg' c'),
    Finset.sum_const, smul_eq_mul]

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.STKI_card_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms STKI_card_step

/--
info: 'Polyplets.STKB_card_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms STKB_card_step

end Polyplets
