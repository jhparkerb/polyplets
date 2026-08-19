/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkStacks
import Polyplets.GapWalkRows
import Polyplets.GapWalkCanon
import Polyplets.GapWalkBridge

/-!
# Notary piece B, module 3: starts and ends

Campaign *Notary*, piece **B**. This module ties the two open boundaries of
the stack recursion to the walk's boundary data and to the configuration
counts of `Weights.lean` / `GapWalkBridge.lean`:

* **starts** — one-row stacks are counted by the walk's start vectors:
  `(STKI 1 g c).card = startCount (g, c)`,
  `(STKB 1 g c).card = bareCount (g, c)`;
* **ends** — closing a stack with the free contact cell `q` (or with
  nothing) turns stack counts into configuration counts:

      V  ℓ ℓ = qEndF   B (fun s => (STKI ℓ s).card)
      Vt ℓ ℓ = qEndF   B (fun s => (STKB ℓ s).card)   (via reflection)
      Vp ℓ ℓ = bareEndF B (fun s => (STKB ℓ s).card)

  for any cap `B` large enough (`2ℓ + 2` resp. `2ℓ`).

All statements pre-verified numerically (`verify_bij_statements.py`,
checks B/G: per-stack q-fibers equal `endMul`, assembled sums hit the
banked `V`/`Vt`/`Vp` at `ℓ ≤ 3`, and the reflection is a bijection onto
the `IsVtConfig` sets).

## The q-closure geometry

A single free cell `q = (x, i+1)` above a stack `T` (top pair `tL, tR` at
gap `g`, class `c`) sees only `tL, tR` (`newRow_adj` reasoning); the full
set `insert q T` is king-connected iff `J`: `q` touches either top (each
component *is* the whole stack), `P`: `q` touches both (it must merge
them): `connected_insert_q_iff`. Counting the admissible `x` gives
`endMul g c` — `qEnd`'s weights `g+3 / 6 / 3−g / 0` (`endCount_eq`), and
summing over stacks fiberwise gives the `V`-identities exactly as the peel
recursion did (truncation `τ = filter (·.2 ≤ ℓ)`, fibers of size
`endMul`).

## The reflection

`qEnd` on the *bare* walk counts "bare stack + `q` above" — the family
`BQ ℓ` below. `Vt ℓ ℓ` counts the same clusters with the contact cell
*below* (rows `1..ℓ` above `(0,0)`). The bijection is the y-flip
`flipMap`: reflect about the top row and re-anchor at the flipped `q`;
`Finset.card_bij'` with explicit inverse (re-anchor at the row-1 minimum,
which the `BQ` anchoring pins to recover the shift).
-/

namespace Polyplets

open GapWalk (St states near startCount bareCount qEndF bareEndF canon qEnd bareEnd)
open GapWalkBridge (IsVpConfig CFGVp Vp mem_CFGVp)

/-! ## The end multiplicities -/

/-- The weight `qEnd` gives one source state: the number of placements of
the free contact cell over a top pair at gap `g`, class `c`. -/
def endMul (g : ℕ) (c : Bool) : ℕ :=
  if c then (if g ≤ 2 then g + 3 else 6) else (if g ≤ 2 then 3 - g else 0)

/-- `qEndF` is the state-sum against `endMul` (unfold `qEnd`/`canon`;
the two `if`-trees agree term by term, `P` above gap 2 giving `0 = F·0`). -/
theorem qEndF_eq_sum (B : ℕ) (F : St → ℕ) :
    qEndF B F = ((states B).map fun s => F s * endMul s.1 s.2).sum := by
  unfold qEndF qEnd canon
  rw [List.map_map]
  congr 1
  apply List.map_congr_left
  intro s _
  obtain ⟨g, c⟩ := s
  unfold endMul
  cases c <;> · by_cases hg : g ≤ 2 <;> simp [hg]

/-- `bareEndF` is the state-sum reading the `J` values. -/
theorem bareEndF_eq_sum (B : ℕ) (F : St → ℕ) :
    bareEndF B F = ((states B).map fun s => if s.2 then F s else 0).sum := by
  unfold bareEndF bareEnd canon
  rw [List.map_map]
  rfl

/-- **The q-window count**: offsets `d = x − xL` with the class-appropriate
contact Boolean, counted over the window `range (g+5)` at `d = n − 2`,
total `endMul g c`. Proof: `g ≤ 2` is two concrete gaps (substitute and
`decide`); `g ≥ 3`, class `J`: the filter is the six-element set
`{1, 2, 3, g+1, g+2, g+3}` (`Finset.ext` + omega on the `near`s, then an
insert-chain cardinality); class `P`: the filter is empty (omega). -/
theorem endCount_eq (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    ((Finset.range (g + 5)).filter fun n : ℕ =>
      (if c then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
       else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true).card =
      endMul g c := by
  rcases Nat.lt_or_ge g 3 with hlt | hge
  · interval_cases g <;> cases c <;> decide
  · have hng : ¬ g ≤ 2 := by omega
    have hMulT : endMul g true = 6 := by simp [endMul, hng]
    have hMulF : endMul g false = 0 := by simp [endMul, hng]
    cases c with
    | true =>
        rw [hMulT]
        have hset : (Finset.range (g + 5)).filter (fun n : ℕ =>
            (if true then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
             else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true) =
            ({1, 2, 3, g + 1, g + 2, g + 3} : Finset ℕ) := by
          apply Finset.ext
          intro n
          simp only [Finset.mem_filter, Finset.mem_range, Bool.or_eq_true,
            Finset.mem_insert, Finset.mem_singleton, near, decide_eq_true_eq, if_true]
          omega
        rw [hset]
        rw [Finset.card_insert_of_notMem
              (by simp only [Finset.mem_insert, Finset.mem_singleton]; omega),
            Finset.card_insert_of_notMem
              (by simp only [Finset.mem_insert, Finset.mem_singleton]; omega),
            Finset.card_insert_of_notMem
              (by simp only [Finset.mem_insert, Finset.mem_singleton]; omega),
            Finset.card_insert_of_notMem
              (by simp only [Finset.mem_insert, Finset.mem_singleton]; omega),
            Finset.card_insert_of_notMem
              (by simp only [Finset.mem_singleton]; omega),
            Finset.card_singleton]
    | false =>
        rw [hMulF]
        have hset : (Finset.range (g + 5)).filter (fun n : ℕ =>
            (if false then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
             else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true) =
            (∅ : Finset ℕ) := by
          rw [Finset.eq_empty_iff_forall_notMem]
          intro n hn
          rw [Finset.mem_filter] at hn
          obtain ⟨hlt', hb⟩ := hn
          have hif : (if false then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
              else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) =
              (near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) := rfl
          rw [hif, Bool.and_eq_true] at hb
          simp only [near, decide_eq_true_eq] at hb
          omega
        rw [hset, Finset.card_empty]

/-! ## The q-closure frame -/

section Frame

variable {i g : ℕ} {T : Finset (ℤ × ℤ)} {xL : ℤ} {c : Bool}

/-- **Closing with one free cell.** `insert (x, i+1) T` is king-connected
iff the class-appropriate contact Boolean holds at offset `x − xL`.
`←`: `J`: all of `T` reaches the touched top (`stackOK` + joined tops),
one edge more reaches `q`, and connectivity is pairwise reach through `q`'s
component; `P`: both components reach `q`, hence each other. `→`: `J`, no
contact: trap `T` (`reach_closed`; `q`'s only possible `T`-neighbors are
tops, untouched) against `reach (insert q T) tL q` from connectivity; `P`,
`tL`-side untouched: trap `{p ∈ T | reach T p tL}` — closed within `T`,
`tR` outside it (class `P`), `q` not adjacent to `tL`. -/
theorem connected_insert_q_iff
    (_hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (x : ℤ) :
    KingConnected (insert (x, (i : ℤ) + 1) T) ↔
      ((if c then near (x - xL) || near (x - xL - (g : ℤ))
        else near (x - xL) && near (x - xL - (g : ℤ))) = true) := by
  have hqnotT : (x, (i : ℤ) + 1) ∉ T := by
    intro hmem
    have h := hTy (x, (i : ℤ) + 1) hmem
    omega
  have hqmem : (x, (i : ℤ) + 1) ∈ insert (x, (i : ℤ) + 1) T := Finset.mem_insert_self _ _
  have htLmem : (xL, (i : ℤ)) ∈ insert (x, (i : ℤ) + 1) T := Finset.mem_insert_of_mem htL
  have htRmem : (xL + (g : ℤ), (i : ℤ)) ∈ insert (x, (i : ℤ) + 1) T := Finset.mem_insert_of_mem htR
  have hadjL : kingAdj (x, (i : ℤ) + 1) (xL, (i : ℤ)) ↔ near (x - xL) = true := by
    unfold kingAdj near
    simp only [decide_eq_true_eq]
    constructor
    · rintro ⟨-, hx, -⟩
      rw [abs_le] at hx
      omega
    · intro hn
      refine ⟨?_, ?_, ?_⟩
      · intro h
        have h2 : (i : ℤ) + 1 = (i : ℤ) := congrArg Prod.snd h
        omega
      · rw [abs_le]; omega
      · rw [abs_le]; omega
  have hadjR : kingAdj (x, (i : ℤ) + 1) (xL + (g : ℤ), (i : ℤ)) ↔
      near (x - xL - (g : ℤ)) = true := by
    unfold kingAdj near
    simp only [decide_eq_true_eq]
    constructor
    · rintro ⟨-, hx, -⟩
      rw [abs_le] at hx
      omega
    · intro hn
      refine ⟨?_, ?_, ?_⟩
      · intro h
        have h2 : (i : ℤ) + 1 = (i : ℤ) := congrArg Prod.snd h
        omega
      · rw [abs_le]; omega
      · rw [abs_le]; omega
  have hadjTop : ∀ p ∈ T, kingAdj (x, (i : ℤ) + 1) p →
      p = (xL, (i : ℤ)) ∨ p = (xL + (g : ℤ), (i : ℤ)) := by
    intro p hp hadj
    have hy : p.2 ≤ (i : ℤ) := hTy p hp
    have hyy : |(i : ℤ) + 1 - p.2| ≤ 1 := hadj.2.2
    rw [abs_le] at hyy
    have hp2 : p.2 = (i : ℤ) := by omega
    exact hrow p hp hp2
  have hnT : c = false → ¬ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := by
    intro hcf hr
    have := hc.mpr hr
    rw [hcf] at this
    exact absurd this (by decide)
  have connectAll : ∀ (hLR : reach (insert (x, (i : ℤ) + 1) T) (xL, (i : ℤ))
        (xL + (g : ℤ), (i : ℤ)))
      (_ : near (x - xL) = true ∨ near (x - xL - (g : ℤ)) = true),
      KingConnected (insert (x, (i : ℤ) + 1) T) := by
    intro hLR hTouch
    have hqToL : reach (insert (x, (i : ℤ) + 1) T) (x, (i : ℤ) + 1) (xL, (i : ℤ)) := by
      rcases hTouch with h1 | h2
      · exact reach_tail (reach_refl _ _) hqmem htLmem (hadjL.mpr h1)
      · exact reach_trans
          (reach_tail (reach_refl _ _) hqmem htRmem (hadjR.mpr h2)) (reach_symm hLR)
    have hallToL : ∀ p ∈ insert (x, (i : ℤ) + 1) T,
        reach (insert (x, (i : ℤ) + 1) T) p (xL, (i : ℤ)) := by
      intro p hp
      rcases Finset.mem_insert.mp hp with rfl | hpT
      · exact hqToL
      · rcases hOK p hpT with h1 | h2
        · exact reach_mono (Finset.subset_insert _ _) h1
        · exact reach_trans (reach_mono (Finset.subset_insert _ _) h2) (reach_symm hLR)
    intro p1 hp1 p2 hp2
    exact reach_trans (hallToL p1 hp1) (reach_symm (hallToL p2 hp2))
  constructor
  · intro hconn
    cases c with
    | true =>
        change (near (x - xL) || near (x - xL - (g : ℤ))) = true
        by_contra hcon
        rw [Bool.or_eq_true, not_or] at hcon
        obtain ⟨hn1, hn2⟩ := hcon
        have hCclosed : ∀ a ∈ (↑T : Set (ℤ × ℤ)), ∀ b ∈ insert (x, (i : ℤ) + 1) T,
            kingAdj a b → b ∈ (↑T : Set (ℤ × ℤ)) := by
          intro a ha b hb hadj
          rw [Finset.mem_coe] at ha
          rw [Finset.mem_coe]
          rcases Finset.mem_insert.mp hb with rfl | hbT
          · exfalso
            have hadj' : kingAdj (x, (i : ℤ) + 1) a := kingAdj_symm hadj
            rcases hadjTop a ha hadj' with rfl | rfl
            · exact hn1 (hadjL.mp hadj')
            · exact hn2 (hadjR.mp hadj')
          · exact hbT
        have hstart : (xL, (i : ℤ)) ∈ (↑T : Set (ℤ × ℤ)) := Finset.mem_coe.mpr htL
        have hqin := reach_closed hCclosed hstart
          (hconn (xL, (i : ℤ)) htLmem (x, (i : ℤ) + 1) hqmem)
        exact hqnotT (Finset.mem_coe.mp hqin)
    | false =>
        change (near (x - xL) && near (x - xL - (g : ℤ))) = true
        have hnT' := hnT rfl
        by_contra hcon
        rw [Bool.and_eq_true, not_and_or] at hcon
        rcases hcon with hn1 | hn2
        · have hCclosed : ∀ a ∈ {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL, (i : ℤ))},
              ∀ b ∈ insert (x, (i : ℤ) + 1) T,
              kingAdj a b → b ∈ {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL, (i : ℤ))} := by
            rintro a ⟨haT, haR⟩ b hb hadj
            rcases Finset.mem_insert.mp hb with rfl | hbT
            · exfalso
              have hadj' : kingAdj (x, (i : ℤ) + 1) a := kingAdj_symm hadj
              rcases hadjTop a haT hadj' with rfl | rfl
              · exact hn1 (hadjL.mp hadj')
              · exact hnT' (reach_symm haR)
            · exact ⟨hbT, reach_trans
                (reach_tail (reach_refl T b) hbT haT (kingAdj_symm hadj)) haR⟩
          have hstart : (xL, (i : ℤ)) ∈ {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL, (i : ℤ))} :=
            ⟨htL, reach_refl T _⟩
          have hqin := reach_closed hCclosed hstart
            (hconn (xL, (i : ℤ)) htLmem (x, (i : ℤ) + 1) hqmem)
          exact hqnotT hqin.1
        · have hCclosed : ∀ a ∈ {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL + (g : ℤ), (i : ℤ))},
              ∀ b ∈ insert (x, (i : ℤ) + 1) T,
              kingAdj a b → b ∈ {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL + (g : ℤ), (i : ℤ))} := by
            rintro a ⟨haT, haR⟩ b hb hadj
            rcases Finset.mem_insert.mp hb with rfl | hbT
            · exfalso
              have hadj' : kingAdj (x, (i : ℤ) + 1) a := kingAdj_symm hadj
              rcases hadjTop a haT hadj' with rfl | rfl
              · exact hnT' haR
              · exact hn2 (hadjR.mp hadj')
            · exact ⟨hbT, reach_trans
                (reach_tail (reach_refl T b) hbT haT (kingAdj_symm hadj)) haR⟩
          have hstart : (xL + (g : ℤ), (i : ℤ)) ∈
              {p : ℤ × ℤ | p ∈ T ∧ reach T p (xL + (g : ℤ), (i : ℤ))} :=
            ⟨htR, reach_refl T _⟩
          have hqin := reach_closed hCclosed hstart
            (hconn (xL + (g : ℤ), (i : ℤ)) htRmem (x, (i : ℤ) + 1) hqmem)
          exact hqnotT hqin.1
  · intro hbool
    cases c with
    | true =>
        have hLR : reach (insert (x, (i : ℤ) + 1) T) (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) :=
          reach_mono (Finset.subset_insert _ _) (hc.mp rfl)
        have hTouch : (near (x - xL) || near (x - xL - (g : ℤ))) = true := hbool
        rw [Bool.or_eq_true] at hTouch
        exact connectAll hLR hTouch
    | false =>
        have hboolAB : (near (x - xL) && near (x - xL - (g : ℤ))) = true := hbool
        rw [Bool.and_eq_true] at hboolAB
        obtain ⟨hn1, hn2⟩ := hboolAB
        have hLR : reach (insert (x, (i : ℤ) + 1) T) (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) :=
          reach_tail
            (reach_tail (reach_refl _ _) htLmem hqmem (kingAdj_symm (hadjL.mpr hn1)))
            hqmem htRmem (hadjR.mpr hn2)
        exact connectAll hLR (Or.inl hn1)

end Frame

/-! ## Starts -/

/-- Converting a `List.range` filter length into a `Finset.range` filter card
(the two idioms `startCount`/`bareCount` and `STKI`/`STKB` are stated in). -/
private theorem filter_range_length_eq_card (n : ℕ) (p : ℕ → Bool) :
    ((List.range n).filter p).length = ((Finset.range n).filter fun i => p i = true).card := by
  induction n with
  | zero => simp
  | succ k ih =>
      rw [List.range_succ, List.filter_append, List.length_append, ih, Finset.range_add_one,
        Finset.filter_insert]
      by_cases hp : p k = true
      · rw [if_pos hp, Finset.card_insert_of_notMem (by simp)]
        simp [hp]
      · rw [if_neg hp]
        simp [hp]

/-- In the fixed 3-cell set `{(0,0), (a,1), (a+g,1)}`, if the anchor `(0,0)`
touches neither top directly it is isolated (`reach_closed` on the singleton
trap `{(0,0)}`). -/
private theorem anchor_isolated {a g : ℤ} (h1 : ¬ near a = true) (h2 : ¬ near (a + g) = true) :
    ∀ y ∈ ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ)),
      reach ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ))
        ((0 : ℤ), (0 : ℤ)) y → y = ((0 : ℤ), (0 : ℤ)) := by
  intro y _ hr
  have hclosed : ∀ p ∈ ({((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)),
      ∀ q ∈ ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ)),
      kingAdj p q → q ∈ ({((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)) := by
    rintro p hp q hq hadj
    rw [Set.mem_singleton_iff] at hp
    subst hp
    exfalso
    rcases Finset.mem_insert.mp hq with rfl | hq'
    · exact hadj.1 rfl
    · rcases Finset.mem_insert.mp hq' with rfl | hq''
      · apply h1
        unfold near
        rw [decide_eq_true_eq]
        have := hadj.2.1
        rw [abs_le] at this
        omega
      · rw [Finset.mem_singleton] at hq''
        subst hq''
        apply h2
        unfold near
        rw [decide_eq_true_eq]
        have := hadj.2.1
        rw [abs_le] at this
        omega
  have h0 : ((0 : ℤ), (0 : ℤ)) ∈ ({((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)) := rfl
  have hres := reach_closed hclosed h0 hr
  simpa using hres

/-- The anchor `(0,0)` reaches a top of the 3-cell set iff it touches one of
them directly (`anchor_isolated` for the hard direction). -/
private theorem anchor_reach_iff (a g : ℤ) :
    (reach ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ))
        ((0 : ℤ), (0 : ℤ)) (a, (1 : ℤ)) ∨
      reach ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ))
        ((0 : ℤ), (0 : ℤ)) (a + g, (1 : ℤ))) ↔
    (near a || near (a + g)) = true := by
  constructor
  · rintro (h | h)
    · by_contra hcon
      rw [Bool.or_eq_true, not_or] at hcon
      have := anchor_isolated hcon.1 hcon.2 (a, (1 : ℤ))
        (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)) h
      exact absurd (congrArg Prod.snd this) (by norm_num)
    · by_contra hcon
      rw [Bool.or_eq_true, not_or] at hcon
      have := anchor_isolated hcon.1 hcon.2 (a + g, (1 : ℤ))
        (Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))) h
      exact absurd (congrArg Prod.snd this) (by norm_num)
  · intro hbool
    rw [Bool.or_eq_true] at hbool
    rcases hbool with h1 | h2
    · refine Or.inl (reach_tail (reach_refl _ _) (Finset.mem_insert_self _ _)
        (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)) ?_)
      refine ⟨by intro h; have := congrArg Prod.snd h; norm_num at this, ?_, by norm_num⟩
      rw [abs_le]
      unfold near at h1
      rw [decide_eq_true_eq] at h1
      omega
    · refine Or.inr (reach_tail (reach_refl _ _) (Finset.mem_insert_self _ _)
        (Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))) ?_)
      refine ⟨by intro h; have := congrArg Prod.snd h; norm_num at this, ?_, by norm_num⟩
      rw [abs_le]
      unfold near at h2
      rw [decide_eq_true_eq] at h2
      omega

/-- The two tops of the 3-cell set reach each other iff `g = 1` (a direct
edge) or the anchor touches both (a two-step path through it). -/
private theorem class_reach_iff {a g : ℤ} (hg : 1 ≤ g) :
    reach ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ))
      (a, (1 : ℤ)) (a + g, (1 : ℤ)) ↔
    (g = 1 ∨ (near a = true ∧ near (a + g) = true)) := by
  constructor
  · intro hr
    by_contra hcon
    push Not at hcon
    obtain ⟨hg1, hcon2⟩ := hcon
    by_cases hna : near a = true
    · have hnag : ¬ near (a + g) = true := hcon2 hna
      have hclosed : ∀ p ∈ ({(a, (1 : ℤ)), ((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)),
          ∀ q ∈ ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ)),
          kingAdj p q → q ∈ ({(a, (1 : ℤ)), ((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)) := by
        rintro p hp q hq hadj
        rw [Set.mem_insert_iff, Set.mem_singleton_iff] at hp
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · exact Or.inr rfl
        · rcases Finset.mem_insert.mp hq' with rfl | hq''
          · exact Or.inl rfl
          · rw [Finset.mem_singleton] at hq''
            subst hq''
            exfalso
            rcases hp with rfl | rfl
            · apply hg1
              have h1 := hadj.2.1
              rw [abs_le] at h1
              omega
            · apply hnag
              unfold near
              rw [decide_eq_true_eq]
              have h1 := hadj.2.1
              rw [abs_le] at h1
              omega
      have h0 : (a, (1 : ℤ)) ∈ ({(a, (1 : ℤ)), ((0 : ℤ), (0 : ℤ))} : Set (ℤ × ℤ)) := by
        rw [Set.mem_insert_iff]; exact Or.inl rfl
      have hres := reach_closed hclosed h0 hr
      rw [Set.mem_insert_iff, Set.mem_singleton_iff] at hres
      rcases hres with heq | heq
      · exact absurd (congrArg Prod.fst heq) (by
          intro h; simp only at h; omega)
      · exact absurd (congrArg Prod.snd heq) (by norm_num)
    · have hclosed : ∀ p ∈ ({(a, (1 : ℤ))} : Set (ℤ × ℤ)),
          ∀ q ∈ ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + g, (1 : ℤ))} : Finset (ℤ × ℤ)),
          kingAdj p q → q ∈ ({(a, (1 : ℤ))} : Set (ℤ × ℤ)) := by
        rintro p hp q hq hadj
        rw [Set.mem_singleton_iff] at hp
        subst hp
        exfalso
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · apply hna
          unfold near
          rw [decide_eq_true_eq]
          have h1 := hadj.2.1
          rw [abs_le] at h1
          omega
        · rcases Finset.mem_insert.mp hq' with rfl | hq''
          · exact hadj.1 rfl
          · rw [Finset.mem_singleton] at hq''
            subst hq''
            apply hg1
            have h1 := hadj.2.1
            rw [abs_le] at h1
            omega
      have h0 : (a, (1 : ℤ)) ∈ ({(a, (1 : ℤ))} : Set (ℤ × ℤ)) := rfl
      have hres := reach_closed hclosed h0 hr
      rw [Set.mem_singleton_iff] at hres
      exact absurd (congrArg Prod.fst hres) (by
        intro h; simp only at h; omega)
  · rintro (h1 | ⟨h1, h2⟩)
    · subst h1
      refine reach_tail (reach_refl _ _) (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _))
        (Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))) ?_
      refine ⟨by intro h; have := congrArg Prod.fst h; simp at this, by rw [abs_le]; omega,
        by norm_num⟩
    · have hadj1 : kingAdj (a, (1 : ℤ)) ((0 : ℤ), (0 : ℤ)) := by
        refine ⟨by intro h; have := congrArg Prod.snd h; norm_num at this, ?_, by norm_num⟩
        rw [abs_le]
        unfold near at h1
        rw [decide_eq_true_eq] at h1
        omega
      have hadj2 : kingAdj ((0 : ℤ), (0 : ℤ)) (a + g, (1 : ℤ)) := by
        refine ⟨by intro h; have := congrArg Prod.snd h; norm_num at this, ?_, by norm_num⟩
        rw [abs_le]
        unfold near at h2
        rw [decide_eq_true_eq] at h2
        omega
      exact reach_tail
        (reach_tail (reach_refl _ _) (Finset.mem_insert_of_mem (Finset.mem_insert_self _ _))
          (Finset.mem_insert_self _ _) hadj1)
        (Finset.mem_insert_self _ _)
        (Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))) hadj2

/-- The cardinality of the fixed 3-cell set `{(0,0), (a,1), (a+g,1)}` (its
three points are pairwise distinct given `1 ≤ g`). -/
private theorem stack3_card (a : ℤ) (g : ℕ) (hg : 1 ≤ g) :
    ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)).card = 3 := by
  have hne1 : ((0 : ℤ), (0 : ℤ)) ≠ (a, (1 : ℤ)) := by
    intro h; have := congrArg Prod.snd h; norm_num at this
  have hne2 : ((0 : ℤ), (0 : ℤ)) ≠ (a + (g : ℤ), (1 : ℤ)) := by
    intro h; have := congrArg Prod.snd h; norm_num at this
  have hne3 : (a, (1 : ℤ)) ≠ (a + (g : ℤ), (1 : ℤ)) := by
    intro h
    have h2 : a = a + (g : ℤ) := congrArg Prod.fst h
    have hgz : (g : ℤ) ≠ 0 := by exact_mod_cast (show g ≠ 0 by omega)
    omega
  rw [Finset.card_insert_of_notMem (by simp [hne1, hne2]),
      Finset.card_insert_of_notMem (by simp [hne3]), Finset.card_singleton]

/-- In a two-element set, `a` reaches `b` iff they are directly adjacent
(the only possible path). -/
private theorem reach_two_iff {a b : ℤ × ℤ} (hab : a ≠ b) :
    reach ({a, b} : Finset (ℤ × ℤ)) a b ↔ kingAdj a b := by
  constructor
  · intro h
    rcases Relation.ReflTransGen.cases_head h with rfl | ⟨cc, hstep, -⟩
    · exact absurd rfl hab
    · obtain ⟨-, hcmem, hadjac⟩ := hstep
      rw [Finset.mem_insert, Finset.mem_singleton] at hcmem
      rcases hcmem with rfl | rfl
      · exact absurd rfl hadjac.1
      · exact hadjac
  · intro hadj
    exact reach_tail (reach_refl _ a) (by simp) (by simp) hadj

/-- `rowMinX` of the fixed 3-cell set at row 1 is the left row-1 cell. -/
private theorem stack3_rowMinX (a : ℤ) (g : ℕ) (hg : 1 ≤ g) :
    rowMinX ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))
      (1 : ℤ) = a := by
  have hmem : (a, (1 : ℤ)) ∈
      ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) :=
    Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  have hle : rowMinX ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))
      (1 : ℤ) ≤ a := rowMinX_le hmem rfl
  have hpos : 1 ≤ rowSize
      ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) (1 : ℤ) := by
    unfold rowSize
    exact Finset.card_pos.mpr ⟨_, Finset.mem_filter.mpr ⟨hmem, rfl⟩⟩
  have hmm := rowMinX_mem
    (S := ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))) hpos
  rw [Finset.mem_insert, Finset.mem_insert, Finset.mem_singleton] at hmm
  rcases hmm with h1 | h1 | h1
  · exact absurd (congrArg Prod.snd h1) (by norm_num)
  · exact congrArg Prod.fst h1
  · exfalso
    have h2 : rowMinX
        ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) (1 : ℤ) =
        a + (g : ℤ) := congrArg Prod.fst h1
    have hgcast : (1 : ℤ) ≤ (g : ℤ) := by exact_mod_cast hg
    omega

/-- The touch Boolean bounds the offset `a` between `-1-g` and `1`. -/
private theorem stack3_bound {a : ℤ} {g : ℕ} (h : (near a || near (a + (g : ℤ))) = true) :
    -1 - (g : ℤ) ≤ a ∧ a ≤ 1 := by
  rw [Bool.or_eq_true] at h
  rcases h with h1 | h2
  · unfold near at h1; rw [decide_eq_true_eq] at h1; omega
  · unfold near at h2; rw [decide_eq_true_eq] at h2; omega

/-- The `startCount` join Boolean, as an iff (case on `gnat = 1`). -/
private theorem nc_iff (a : ℤ) (gnat : ℕ) :
    (if gnat = 1 then true else near a && near (a + (gnat : ℤ))) = true ↔
      (gnat = 1 ∨ (near a = true ∧ near (a + (gnat : ℤ)) = true)) := by
  by_cases hg1 : gnat = 1
  · simp [hg1]
  · simp [hg1, Bool.and_eq_true]

/-- Two `Bool`s agreeing as an `= true` iff are equal. -/
private theorem bool_eq_of_iff {x y : Bool} (h : (x = true ↔ y = true)) : x = y := by
  cases x <;> cases y <;> simp_all

/-- One-row interior stacks are the walk's interior start vector. The set
`S = {(0,0), (a,1), (a+g,1)}`: membership analysis is a three-cell special
case (reach in a 3-set: `(0,0)` reaches a top iff adjacent to one —
trap `{(0,0)}` otherwise; the tops are joined iff `g = 1` or `(0,0)`
touches both — traps `{u}` resp. `{u, (0,0)}` otherwise), matching
`startCount`'s filter Boolean at `a = n − (g+2)`; then the same
window bijection as the peel recursion (`n ↦` the 3-set, left cell
`a`-monotone; surjectivity reads `a` off the top-left witness). -/
theorem STKI_one_card (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    (STKI 1 g c).card = startCount (g, c) := by
  have hchar : ∀ S : Finset (ℤ × ℤ), S ∈ STKI 1 g c ↔
      ∃ a : ℤ, S = ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) ∧
        (near a || near (a + (g : ℤ))) = true ∧
        (c = true ↔ (g = 1 ∨ (near a = true ∧ near (a + (g : ℤ)) = true))) := by
    intro S
    rw [mem_STKI (le_refl 1)]
    constructor
    · intro hS
      obtain ⟨hL, hR, hmaxeq, hOK', hcls', hforce⟩ := isStackI_top (le_refl 1) hS
      simp only [Nat.cast_one] at hL hR hmaxeq hOK' hcls' hforce
      obtain ⟨-, hcard, h0, hty, hrow0, hrow1, p, hpS, hpi, hpgS, hOK, hcls⟩ := hS
      set a := rowMinX S (1 : ℤ) with hadef
      have hrow0' : ∀ q ∈ S, q.2 = 0 → q = ((0 : ℤ), (0 : ℤ)) := by
        intro q hq hq0
        have hmem1 : q ∈ S.filter (fun c => c.2 = 0) := Finset.mem_filter.mpr ⟨hq, hq0⟩
        have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S.filter (fun c => c.2 = 0) :=
          Finset.mem_filter.mpr ⟨h0, rfl⟩
        exact Finset.card_le_one.mp (le_of_eq hrow0) q hmem1 _ hmem2
      have hsub :
          S ⊆ ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) := by
        intro q hq
        have hqy := hty q hq
        rcases (show q.2 = 0 ∨ q.2 = 1 by omega) with hq0 | hq1
        · rw [hrow0' q hq hq0]; exact Finset.mem_insert_self _ _
        · rcases hforce q hq hq1 with heq | heq
          · rw [heq]; exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
          · rw [heq]
            exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))
      have hUcard := stack3_card a g hg
      have hSeq :
          S = ({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) :=
        Finset.eq_of_subset_of_card_le hsub (by rw [hUcard, hcard])
      rw [hSeq] at hOK' hcls' h0
      refine ⟨a, hSeq, ?_, ?_⟩
      · rw [← anchor_reach_iff]
        exact hOK' ((0 : ℤ), (0 : ℤ)) h0
      · rw [class_reach_iff (a := a) (g := (g : ℤ)) (by exact_mod_cast hg)] at hcls'
        constructor
        · intro hcT
          rcases hcls'.mp hcT with hgeq | hb
          · left; exact_mod_cast hgeq
          · right; exact hb
        · intro hdisj
          apply hcls'.mpr
          rcases hdisj with hgeq | hb
          · left; exact_mod_cast hgeq
          · right; exact hb
    · rintro ⟨a, rfl, hbool, hcbool⟩
      have hcard3 := stack3_card a g hg
      refine ⟨hg, hcard3, Finset.mem_insert_self _ _, ?_, ?_, ?_,
        (a, (1 : ℤ)), Finset.mem_insert_of_mem (Finset.mem_insert_self _ _), rfl,
        Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _)),
        ?_, ?_⟩
      · intro q hq
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · exact ⟨le_refl 0, by norm_num⟩
        · rcases Finset.mem_insert.mp hq' with rfl | hq''
          · exact ⟨by norm_num, le_refl 1⟩
          · rw [Finset.mem_singleton] at hq''
            subst hq''
            exact ⟨by norm_num, le_refl 1⟩
      · unfold rowSize
        have hfe :
            (({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))).filter
              (fun c => c.2 = 0) = {((0 : ℤ), (0 : ℤ))} := by
          apply Finset.ext
          intro q
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          constructor
          · rintro ⟨(rfl | rfl | rfl), hq0⟩
            · rfl
            · norm_num at hq0
            · norm_num at hq0
          · rintro rfl
            exact ⟨Or.inl rfl, rfl⟩
        rw [hfe, Finset.card_singleton]
      · intro r hr
        rw [Finset.mem_Icc] at hr
        have hr1 : r = 1 := by omega
        subst hr1
        simp only [Nat.cast_one]
        unfold rowSize
        have hfe :
            (({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))).filter
              (fun c => c.2 = (1 : ℤ)) = {(a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} := by
          apply Finset.ext
          intro q
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          constructor
          · rintro ⟨(rfl | rfl | rfl), hq1⟩
            · norm_num at hq1
            · exact Or.inl rfl
            · exact Or.inr rfl
          · rintro (rfl | rfl)
            · exact ⟨Or.inr (Or.inl rfl), rfl⟩
            · exact ⟨Or.inr (Or.inr rfl), rfl⟩
        rw [hfe]
        have hne3 : (a, (1 : ℤ)) ≠ (a + (g : ℤ), (1 : ℤ)) := by
          intro h
          have h2 : a = a + (g : ℤ) := congrArg Prod.fst h
          have hgz : (g : ℤ) ≠ 0 := by exact_mod_cast (show g ≠ 0 by omega)
          omega
        exact Finset.card_pair hne3
      · rw [stackOK]
        simp only [Nat.cast_one]
        intro q hq
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · rw [anchor_reach_iff]
          exact hbool
        · rcases Finset.mem_insert.mp hq' with rfl | hq''
          · exact Or.inl (reach_refl _ _)
          · rw [Finset.mem_singleton] at hq''
            subst hq''
            exact Or.inr (reach_refl _ _)
      · simp only [Nat.cast_one]
        rw [class_reach_iff (a := a) (g := (g : ℤ)) (by exact_mod_cast hg)]
        constructor
        · intro hcT
          rcases hcbool.mp hcT with hgeq | hb
          · left; exact_mod_cast hgeq
          · right; exact hb
        · intro hdisj
          apply hcbool.mpr
          rcases hdisj with hgeq | hb
          · left; exact_mod_cast hgeq
          · right; exact hb
  unfold startCount
  rw [filter_range_length_eq_card]
  apply Finset.card_bij (fun S _ => ((rowMinX S (1 : ℤ) + (g : ℤ) + 2)).toNat)
  · intro S hS
    obtain ⟨a, hSeq, hboolA, hcbool⟩ := (hchar S).mp hS
    have hrmin : rowMinX S (1 : ℤ) = a := by rw [hSeq]; exact stack3_rowMinX a g hg
    rw [hrmin]
    obtain ⟨hb1, hb2⟩ := stack3_bound hboolA
    rw [Finset.mem_filter, Finset.mem_range]
    have htoNat : ((a + (g : ℤ) + 2).toNat : ℤ) = a + (g : ℤ) + 2 := by omega
    refine ⟨by omega, ?_⟩
    have haeq : (((a + (g : ℤ) + 2).toNat : ℤ) - ((g : ℤ) + 2)) = a := by omega
    simp only [haeq]
    rw [Bool.and_eq_true, beq_iff_eq]
    exact ⟨hboolA, bool_eq_of_iff ((nc_iff a g).trans hcbool.symm)⟩
  · intro S1 hS1 S2 hS2 heq
    obtain ⟨a1, hSeq1, hb1, -⟩ := (hchar S1).mp hS1
    obtain ⟨a2, hSeq2, hb2, -⟩ := (hchar S2).mp hS2
    have hr1 : rowMinX S1 (1 : ℤ) = a1 := by rw [hSeq1]; exact stack3_rowMinX a1 g hg
    have hr2 : rowMinX S2 (1 : ℤ) = a2 := by rw [hSeq2]; exact stack3_rowMinX a2 g hg
    rw [hr1, hr2] at heq
    obtain ⟨hb11, hb12⟩ := stack3_bound hb1
    obtain ⟨hb21, hb22⟩ := stack3_bound hb2
    have haeq : a1 = a2 := by
      have e1 : ((a1 + (g : ℤ) + 2).toNat : ℤ) = a1 + (g : ℤ) + 2 := by omega
      have e2 : ((a2 + (g : ℤ) + 2).toNat : ℤ) = a2 + (g : ℤ) + 2 := by omega
      have hcast : ((a1 + (g : ℤ) + 2).toNat : ℤ) = ((a2 + (g : ℤ) + 2).toNat : ℤ) := by
        exact_mod_cast congrArg (fun k : ℕ => (k : ℤ)) heq
      omega
    rw [hSeq1, hSeq2, haeq]
  · intro n hn
    rw [Finset.mem_filter, Finset.mem_range] at hn
    obtain ⟨hnlt, hnpred⟩ := hn
    set a : ℤ := (n : ℤ) - ((g : ℤ) + 2) with hadef
    rw [Bool.and_eq_true, beq_iff_eq] at hnpred
    refine ⟨({((0 : ℤ), (0 : ℤ)), (a, (1 : ℤ)), (a + (g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)), ?_, ?_⟩
    · rw [hchar]
      refine ⟨a, rfl, hnpred.1, ?_⟩
      rw [← nc_iff a g, hnpred.2]
    · rw [stack3_rowMinX a g hg]
      have : a + (g : ℤ) + 2 = (n : ℤ) := by rw [hadef]; ring
      omega

/-- One-row bare stacks are the bare start vector: the anchoring pins
`S = {(0,1), (g,1)}` (witness pair = the two row-1 cells, leftmost at 0),
`stackOK` is trivial (both cells are tops), and the tops are joined iff
they are adjacent, i.e. `g = 1` (trap `{(0,1)}` for `g ≥ 2`) — so the
count is `1` when `c` matches `g == 1`, else `0`, which is
`bareCount (g, c)`. -/
theorem STKB_one_card (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    (STKB 1 g c).card = bareCount (g, c) := by
  have hne : ((0 : ℤ), (1 : ℤ)) ≠ ((g : ℤ), (1 : ℤ)) := by
    intro h
    have h2 := congrArg Prod.fst h
    have hgz : (g : ℤ) ≠ 0 := by exact_mod_cast (show g ≠ 0 by omega)
    omega
  have hchar : ∀ S : Finset (ℤ × ℤ), S ∈ STKB 1 g c ↔
      S = ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) ∧ (c = true ↔ g = 1) := by
    intro S
    rw [mem_STKB (le_refl 1)]
    constructor
    · intro hS
      obtain ⟨hL, hR, hmaxeq, hOK', hcls', hforce⟩ := isStackB_top (le_refl 1) hS
      simp only [Nat.cast_one] at hL hR hmaxeq hOK' hcls' hforce
      obtain ⟨-, hcard, hanchor, hty, hx0, -⟩ := hS
      set a := rowMinX S (1 : ℤ) with hadef
      have hmin0 : a = 0 := by
        have h1 : a ≤ 0 := rowMinX_le hanchor rfl
        have h2 : (0 : ℤ) ≤ a := hx0 _ hL rfl
        omega
      have hsub : S ⊆ ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) := by
        intro q hq
        have hq1 : q.2 = 1 := by have := hty q hq; omega
        rcases hforce q hq hq1 with heq | heq
        · rw [heq, hmin0]; exact Finset.mem_insert_self _ _
        · rw [heq, hmin0]
          simp
      have hUcard : ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)).card = 2 := by
        rw [Finset.card_insert_of_notMem (by simp [hne]), Finset.card_singleton]
      have hSeq : S = ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) :=
        Finset.eq_of_subset_of_card_le hsub (by rw [hUcard, hcard])
      refine ⟨hSeq, ?_⟩
      rw [hSeq, hmin0] at hcls'
      simp only [zero_add] at hcls'
      rw [hcls', reach_two_iff hne]
      unfold kingAdj
      constructor
      · rintro ⟨-, hx, -⟩
        rw [abs_le] at hx
        omega
      · intro hgeq
        refine ⟨hne, ?_, by norm_num⟩
        rw [abs_le]; omega
    · rintro ⟨rfl, hgc⟩
      have hcard2 : ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)).card = 2 := by
        rw [Finset.card_insert_of_notMem (by simp [hne]), Finset.card_singleton]
      refine ⟨hg, hcard2, Finset.mem_insert_self _ _, ?_, ?_, ?_,
        ((0 : ℤ), (1 : ℤ)), Finset.mem_insert_self _ _, rfl,
        (show (((0 : ℤ), (1 : ℤ)).1 + (g : ℤ), (1 : ℤ)) ∈
          ({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ)) by simp), ?_, ?_⟩
      · intro q hq
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · exact ⟨le_refl 1, le_refl 1⟩
        · rw [Finset.mem_singleton] at hq'
          subst hq'
          exact ⟨le_refl 1, le_refl 1⟩
      · intro q hq _
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · norm_num
        · rw [Finset.mem_singleton] at hq'
          subst hq'
          positivity
      · intro r hr
        rw [Finset.mem_Icc] at hr
        have hr1 : r = 1 := by omega
        subst hr1
        simp only [Nat.cast_one]
        unfold rowSize
        have hfe : (({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))).filter
            (fun c => c.2 = (1 : ℤ)) = {((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} := by
          apply Finset.ext
          intro q
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          constructor
          · rintro ⟨hqm, -⟩; exact hqm
          · rintro (rfl | rfl)
            · exact ⟨Or.inl rfl, rfl⟩
            · exact ⟨Or.inr rfl, rfl⟩
        rw [hfe]
        exact Finset.card_pair hne
      · simp only [Nat.cast_one, zero_add]
        rw [stackOK]
        intro q hq
        rcases Finset.mem_insert.mp hq with rfl | hq'
        · exact Or.inl (reach_refl _ _)
        · rw [Finset.mem_singleton] at hq'
          subst hq'
          exact Or.inr (reach_refl _ _)
      · simp only [Nat.cast_one, zero_add]
        rw [reach_two_iff hne, hgc]
        unfold kingAdj
        constructor
        · intro hgeq
          refine ⟨hne, ?_, by norm_num⟩
          rw [abs_le]; omega
        · rintro ⟨-, hx, -⟩
          rw [abs_le] at hx
          omega
  by_cases hiff : c = true ↔ g = 1
  · have hSTKB : STKB 1 g c = {({((0 : ℤ), (1 : ℤ)), ((g : ℤ), (1 : ℤ))} : Finset (ℤ × ℤ))} := by
      apply Finset.ext
      intro S
      rw [hchar, Finset.mem_singleton]
      constructor
      · rintro ⟨rfl, -⟩; rfl
      · rintro rfl; exact ⟨rfl, hiff⟩
    have heqc : c = (g == 1) := bool_eq_of_iff (hiff.trans (beq_iff_eq (a := g) (b := 1)).symm)
    rw [hSTKB, Finset.card_singleton]
    unfold bareCount
    rw [if_pos (beq_iff_eq.mpr heqc)]
  · have hSTKB : STKB 1 g c = ∅ := by
      apply Finset.eq_empty_iff_forall_notMem.mpr
      intro S
      rw [hchar]
      rintro ⟨-, hc⟩
      exact hiff hc
    rw [hSTKB, Finset.card_empty]
    unfold bareCount
    have hcondf : ¬ ((c == (g == 1)) = true) := by
      intro hcon
      rw [beq_iff_eq] at hcon
      apply hiff
      rw [hcon, beq_iff_eq]
    rw [if_neg hcondf]

/-- A `Nodup` list's mapped sum equals the `Finset.sum` over its `toFinset`
(bridges `Finset.card_eq_sum_card_fiberwise`'s target, indexed by
`(states B).toFinset`, back to the walk's list-sum functionals). -/
private theorem list_sum_eq_finset_sum_toFinset {α : Type} [DecidableEq α]
    (l : List α) (hl : l.Nodup) (f : α → ℕ) :
    (l.map f).sum = ∑ x ∈ l.toFinset, f x := by
  induction l with
  | nil => simp
  | cons a t ih =>
      rw [List.nodup_cons] at hl
      rw [List.map_cons, List.sum_cons, List.toFinset_cons,
        Finset.sum_insert (by simpa using hl.1), ih hl.2]

/-- **Pigeonhole**: if every term of a length-`n` sum is `≥ c` and the sum is
exactly `n * c`, every term is exactly `c` (else the excess term alone forces
the sum past the bound). -/
private theorem forall_eq_of_sum_eq_of_forall_le {n c : ℕ} {f : ℕ → ℕ}
    (hge : ∀ r ∈ Finset.range n, c ≤ f r) (hsum : (Finset.range n).sum f = n * c) :
    ∀ r ∈ Finset.range n, f r = c := by
  intro r0 hr0
  by_contra hne
  have hgt : c < f r0 := lt_of_le_of_ne (hge r0 hr0) (Ne.symm hne)
  have hlt : (Finset.range n).sum (fun _ => c) < (Finset.range n).sum f :=
    Finset.sum_lt_sum hge ⟨r0, hr0, hgt⟩
  rw [Finset.sum_const, Finset.card_range, smul_eq_mul] at hlt
  omega

/-- Sharpening a `Config`-style `2 ≤ rowSize` bound on rows `1..ℓ` to exact
equality, given the total row-1..ℓ cell count is `2ℓ` (the pigeonhole
argument via `card_eq_sum_rowSize` + `forall_eq_of_sum_eq_of_forall_le`). -/
private theorem rowSize_eq_two {S : Finset (ℤ × ℤ)} {ℓ : ℕ}
    (hy : ∀ p ∈ S, (1 : ℤ) ≤ p.2 ∧ p.2 < 1 + (ℓ : ℤ))
    (hge : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ))
    (hcard : S.card = 2 * ℓ) :
    ∀ i ∈ Finset.Icc 1 ℓ, rowSize S (i : ℤ) = 2 := by
  have hsum := card_eq_sum_rowSize (S := S) (y0 := 1) (h := ℓ) hy
  rw [hcard] at hsum
  have hge' : ∀ r ∈ Finset.range ℓ, 2 ≤ rowSize S ((1 : ℤ) + r) := by
    intro r hr
    rw [Finset.mem_range] at hr
    have hmem := hge (1 + r) (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
    have heq : ((1 + r : ℕ) : ℤ) = (1 : ℤ) + (r : ℤ) := by push_cast; ring
    rwa [heq] at hmem
  have hsum' : (Finset.range ℓ).sum (fun r => rowSize S ((1 : ℤ) + r)) = ℓ * 2 := by
    rw [← hsum]; ring
  have hall := forall_eq_of_sum_eq_of_forall_le hge' hsum'
  intro i hi
  rw [Finset.mem_Icc] at hi
  have hr : i - 1 ∈ Finset.range ℓ := by rw [Finset.mem_range]; omega
  have hres := hall (i - 1) hr
  have heq : (1 : ℤ) + ((i - 1 : ℕ) : ℤ) = (i : ℤ) := by omega
  rwa [heq] at hres

/-- **The q-truncation trap.** If `insert (x, i+1) T` is fully king-connected
and `T`'s top row `i` is exactly the pair `tL, tR` (so `q := (x, i+1)`'s only
possible `T`-neighbors are `tL, tR`), then `T` alone already satisfies
`stackOK`: chase `reach (insert q T) q p` (from full connectivity) through
the closed set `{q} ∪ {r ∈ T | reach T r tL ∨ reach T r tR}` (closed since
`q`'s only exits land on `tL`/`tR`, already in the set, and `T`-internal
steps preserve reach-to-a-top). -/
private theorem stackOK_of_connected_insert {i g : ℕ} {T : Finset (ℤ × ℤ)} {xL x : ℤ}
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (_htL : (xL, (i : ℤ)) ∈ T) (_htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) → q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hconn : KingConnected (insert (x, (i : ℤ) + 1) T)) :
    stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := by
  have hqnotT : (x, (i : ℤ) + 1) ∉ T := by
    intro hmem
    have := hTy _ hmem
    omega
  set D : Set (ℤ × ℤ) := {(x, (i : ℤ) + 1)} ∪
      {r | r ∈ T ∧ (reach T r (xL, (i : ℤ)) ∨ reach T r (xL + (g : ℤ), (i : ℤ)))} with hDdef
  have hD : ∀ a ∈ D, ∀ b ∈ insert (x, (i : ℤ) + 1) T, kingAdj a b → b ∈ D := by
    rintro a ha b hb hadj
    rw [hDdef, Set.mem_union, Set.mem_singleton_iff, Set.mem_setOf_eq] at ha
    rw [hDdef, Set.mem_union, Set.mem_singleton_iff, Set.mem_setOf_eq]
    rcases ha with rfl | ⟨haT, ha⟩
    · rcases Finset.mem_insert.mp hb with rfl | hbT
      · exact absurd rfl hadj.1
      · have hb2 : b.2 = (i : ℤ) := by
          have hyy := hadj.2.2
          have hby := hTy b hbT
          rw [abs_le] at hyy
          omega
        rcases hrow b hbT hb2 with rfl | rfl
        · exact Or.inr ⟨hbT, Or.inl (reach_refl _ _)⟩
        · exact Or.inr ⟨hbT, Or.inr (reach_refl _ _)⟩
    · rcases Finset.mem_insert.mp hb with rfl | hbT
      · exact Or.inl rfl
      · refine Or.inr ⟨hbT, ?_⟩
        have hba : reach T b a := reach_tail (reach_refl T b) hbT haT (kingAdj_symm hadj)
        rcases ha with h1 | h1
        · exact Or.inl (reach_trans hba h1)
        · exact Or.inr (reach_trans hba h1)
  intro p hp
  have hstart : (x, (i : ℤ) + 1) ∈ D := Set.mem_union_left _ rfl
  have hres := reach_closed hD hstart
    (hconn (x, (i : ℤ) + 1) (Finset.mem_insert_self _ _) p (Finset.mem_insert_of_mem hp))
  rw [hDdef, Set.mem_union, Set.mem_singleton_iff, Set.mem_setOf_eq] at hres
  rcases hres with heq | ⟨-, hh⟩
  · exfalso
    have h2 := congrArg Prod.snd heq
    have := hTy p hp
    omega
  · exact hh

/-! ## The interior end: `V ℓ ℓ` -/

/-- **Interior assembly.** Partition `CFGV ℓ ℓ` (membership = `IsVConfig`,
`mem_CFGV`) fiberwise along `S' ↦ topState (τ S') ℓ`-style truncation into
the stack sets, exactly as in `STKI_card_step`:

* `IsVConfig ℓ ℓ S'` forces exactly two cells in rows `1..ℓ`
  (`card_eq_sum_rowSize`: `2ℓ + 2 = 1 + 2ℓ + 1` with every interior row
  `≥ 2`), a unique `q` on row `ℓ+1`;
* `τ S' = S'.filter (·.2 ≤ ℓ)` is an interior stack (q-truncation trap),
  whose state lies in `states B`: `J`-gaps `≤ 2ℓ ≤ B`, `P`-gaps `≤ 2`
  (both `near`s at the `q`-contact);
* the fiber over a stack `T` in state `(g, c)` counts admissible `q`
  columns: `connected_insert_q_iff` matches the `endCount_eq` window
  (bijection `n ↦ insert (xL + n − 2, ℓ+1) T`), giving `endMul g c`;
* sum against `qEndF_eq_sum` (`Finset.sum_biUnion` +
  `isStackI_state_unique` disjointness + `List.sum_toFinset`/
  `states_nodup`). -/
theorem V_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    V ℓ ℓ = qEndF B (fun s => (STKI ℓ s.1 s.2).card) := by
  have hdecomp : ∀ S' ∈ CFGV ℓ ℓ, ∃ g c,
      (S'.filter (fun p => p.2 ≤ (ℓ : ℤ))) ∈ STKI ℓ g c ∧ (g, c) ∈ states B := by
    intro S' hS'mem
    rw [mem_CFGV] at hS'mem
    obtain ⟨hcard, h0, hy, hrow0, hrowtop, hrowmid, hconn⟩ := hS'mem
    have hqS' : (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) ∈ S' := rowMaxX_mem (by omega)
    set q : ℤ × ℤ := (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) with hqdef
    set T' : Finset (ℤ × ℤ) := S'.filter (fun p => 1 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ)) with hT'def
    have hq0notT' : ((0 : ℤ), (0 : ℤ)) ∉ T' := by rw [hT'def]; simp
    have hqnotT' : q ∉ T' := by
      rw [hT'def, Finset.mem_filter]
      rintro ⟨-, -, hle⟩
      rw [hqdef] at hle
      omega
    have hins : insert ((0 : ℤ), (0 : ℤ)) (insert q T') = S' := by
      apply Finset.ext
      intro p
      simp only [Finset.mem_insert, hT'def, Finset.mem_filter]
      constructor
      · rintro (rfl | rfl | ⟨hpS', -⟩)
        · exact h0
        · exact hqS'
        · exact hpS'
      · intro hpS'
        obtain ⟨hy1, hy2⟩ := hy p hpS'
        by_cases hp0 : p.2 = 0
        · left
          have hmem1 : p ∈ S'.filter (fun c => c.2 = 0) := Finset.mem_filter.mpr ⟨hpS', hp0⟩
          have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
            Finset.mem_filter.mpr ⟨h0, rfl⟩
          exact Finset.card_le_one.mp (le_of_eq hrow0) p hmem1 _ hmem2
        · by_cases hptop : p.2 = (ℓ : ℤ) + 1
          · right; left
            have hmem1 : p ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
              Finset.mem_filter.mpr ⟨hpS', hptop⟩
            have hmem2 : q ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
              Finset.mem_filter.mpr ⟨hqS', by rw [hqdef]⟩
            exact Finset.card_le_one.mp (le_of_eq hrowtop) p hmem1 _ hmem2
          · right; right
            exact ⟨hpS', by omega, by omega⟩
    have hq0notinsert : ((0 : ℤ), (0 : ℤ)) ∉ insert q T' := by
      rw [Finset.mem_insert]
      rintro (heq | hmem)
      · have h2 := congrArg Prod.snd heq
        rw [hqdef] at h2
        omega
      · exact hq0notT' hmem
    have hT'card : T'.card = 2 * ℓ := by
      have hc1 := Finset.card_insert_of_notMem hq0notinsert
      have hc2 := Finset.card_insert_of_notMem hqnotT'
      rw [hins, hc2] at hc1
      omega
    have hfeq : ∀ i ∈ Finset.Icc 1 ℓ, rowSize T' (i : ℤ) = rowSize S' (i : ℤ) := by
      intro i hi
      rw [Finset.mem_Icc] at hi
      unfold rowSize
      rw [hT'def, Finset.filter_filter]
      congr 1
      apply Finset.filter_congr
      intro p _
      constructor
      · rintro ⟨-, hpeq⟩; exact hpeq
      · intro hpeq; exact ⟨by omega, hpeq⟩
    have hrowmid' : ∀ i ∈ Finset.Icc 1 ℓ, rowSize T' (i : ℤ) = 2 := by
      have hy' : ∀ p ∈ T', (1 : ℤ) ≤ p.2 ∧ p.2 < 1 + (ℓ : ℤ) := by
        intro p hp
        rw [hT'def, Finset.mem_filter] at hp
        omega
      have hge' : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize T' (i : ℤ) := by
        intro i hi
        rw [hfeq i hi]
        exact hrowmid i hi
      exact rowSize_eq_two hy' hge' hT'card
    have hτeq : S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) = insert ((0 : ℤ), (0 : ℤ)) T' := by
      apply Finset.ext
      intro p
      rw [Finset.mem_filter, Finset.mem_insert, hT'def, Finset.mem_filter]
      constructor
      · rintro ⟨hpS', hple⟩
        by_cases hp0 : p.2 = 0
        · left
          have hmem1 : p ∈ S'.filter (fun c => c.2 = 0) := Finset.mem_filter.mpr ⟨hpS', hp0⟩
          have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
            Finset.mem_filter.mpr ⟨h0, rfl⟩
          exact Finset.card_le_one.mp (le_of_eq hrow0) p hmem1 _ hmem2
        · right
          obtain ⟨hy1, -⟩ := hy p hpS'
          exact ⟨hpS', by omega, hple⟩
      · rintro (rfl | ⟨hpS', -, hple⟩)
        · exact ⟨h0, by norm_num⟩
        · exact ⟨hpS', hple⟩
    have hrsizeT' : rowSize T' (ℓ : ℤ) = 2 := hrowmid' ℓ (Finset.mem_Icc.mpr ⟨hℓ, le_refl ℓ⟩)
    obtain ⟨aL, aR, haLT', haRT', haLy, haRy, hlt, hforceT'⟩ := row_two_cells hrsizeT'
    set g : ℕ := (aR.1 - aL.1).toNat with hgdef
    have hcastg : (g : ℤ) = aR.1 - aL.1 := by rw [hgdef]; omega
    have hAeq : (aL.1, (ℓ : ℤ)) = aL := Prod.ext rfl haLy.symm
    have hpteq : (aL.1 + (g : ℤ), (ℓ : ℤ)) = aR := by
      rw [hcastg]
      have heq2 : aL.1 + (aR.1 - aL.1) = aR.1 := by ring
      rw [heq2]
      exact Prod.ext rfl haRy.symm
    have haLτ : aL ∈ insert ((0 : ℤ), (0 : ℤ)) T' := Finset.mem_insert_of_mem haLT'
    have haRτ : aR ∈ insert ((0 : ℤ), (0 : ℤ)) T' := Finset.mem_insert_of_mem haRT'
    have hTy0 : ∀ p ∈ insert ((0 : ℤ), (0 : ℤ)) T', p.2 ≤ (ℓ : ℤ) := by
      intro p hp
      rcases Finset.mem_insert.mp hp with rfl | hpT'
      · norm_num
      · rw [hT'def, Finset.mem_filter] at hpT'; omega
    have hrow0' : ∀ q' ∈ insert ((0 : ℤ), (0 : ℤ)) T', q'.2 = (ℓ : ℤ) →
        q' = (aL.1, (ℓ : ℤ)) ∨ q' = (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      intro q' hq' hq'ℓ
      rcases Finset.mem_insert.mp hq' with rfl | hq'T'
      · exfalso; simp only at hq'ℓ; omega
      · rcases hforceT' q' hq'T' hq'ℓ with rfl | rfl
        · exact Or.inl hAeq.symm
        · exact Or.inr hpteq.symm
    have hSOK0 : stackOK (insert ((0 : ℤ), (0 : ℤ)) T') (aL.1, (ℓ : ℤ))
        (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      apply stackOK_of_connected_insert (i := ℓ) (xL := aL.1) (x := rowMaxX S' ((ℓ : ℤ) + 1))
        hTy0
      · rw [hAeq]; exact haLτ
      · rw [hpteq]; exact haRτ
      · exact hrow0'
      · rw [Finset.insert_comm]; rw [hins]; exact hconn
    set c : Bool :=
      decide (reach (insert ((0 : ℤ), (0 : ℤ)) T') (aL.1, (ℓ : ℤ)) (aL.1 + (g : ℤ), (ℓ : ℤ)))
      with hcdef
    have hc : c = true ↔ reach (insert ((0 : ℤ), (0 : ℤ)) T') (aL.1, (ℓ : ℤ))
        (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      rw [hcdef]
      constructor
      · intro h; exact of_decide_eq_true h
      · intro h; exact decide_eq_true h
    have hgpos : 1 ≤ g := by rw [hgdef]; omega
    have hstkI : (insert ((0 : ℤ), (0 : ℤ)) T') ∈ STKI ℓ g c := by
      rw [mem_STKI hℓ]
      refine ⟨hgpos, ?_, Finset.mem_insert_self _ _, ?_, ?_, ?_,
        (aL.1, (ℓ : ℤ)), ?_, rfl, ?_, hSOK0, hc⟩
      · rw [Finset.card_insert_of_notMem hq0notT', hT'card]
      · intro p hp
        rcases Finset.mem_insert.mp hp with rfl | hpT'
        · exact ⟨le_refl 0, by omega⟩
        · rw [hT'def, Finset.mem_filter] at hpT'; exact ⟨by omega, hpT'.2.2⟩
      · unfold rowSize
        have hfe : (insert ((0 : ℤ), (0 : ℤ)) T').filter (fun c => c.2 = 0) =
            {((0 : ℤ), (0 : ℤ))} := by
          apply Finset.ext
          intro p
          simp only [Finset.mem_filter, Finset.mem_insert, hT'def, Finset.mem_singleton]
          constructor
          · rintro ⟨(rfl | hpT'), hp0⟩
            · rfl
            · omega
          · rintro rfl; exact ⟨Or.inl rfl, rfl⟩
        rw [hfe, Finset.card_singleton]
      · intro i hi
        rw [rowSize_insert_other (by rw [Finset.mem_Icc] at hi; omega)]
        exact hrowmid' i hi
      · rw [hAeq]; exact haLτ
      · rw [hpteq]; exact haRτ
    have htL0 : (aL.1, (ℓ : ℤ)) ∈ insert ((0 : ℤ), (0 : ℤ)) T' := by rw [hAeq]; exact haLτ
    have htR0 : (aL.1 + (g : ℤ), (ℓ : ℤ)) ∈ insert ((0 : ℤ), (0 : ℤ)) T' := by
      rw [hpteq]; exact haRτ
    have hconn' : KingConnected (insert (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1)
        (insert ((0 : ℤ), (0 : ℤ)) T')) := by
      rw [Finset.insert_comm, hins]; exact hconn
    have hbool := (connected_insert_q_iff hgpos hTy0 htL0 htR0 hrow0' hSOK0 hc
      (rowMaxX S' ((ℓ : ℤ) + 1))).mp hconn'
    refine ⟨g, c, ?_, ?_⟩
    · rw [hτeq]; exact hstkI
    · rw [GapWalk.mem_states]
      refine ⟨hgpos, ?_⟩
      have hIsStackI : IsStackI ℓ g c (insert ((0 : ℤ), (0 : ℤ)) T') := (mem_STKI hℓ).mp hstkI
      by_cases hcT : c = true
      · rw [hcT] at hIsStackI
        have hJ := isStackI_J_le hℓ hIsStackI
        omega
      · have hcF : c = false := by
          revert hcT
          generalize c = c'
          cases c' <;> simp
        have hif : (if c then near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) ||
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))
            else near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) &&
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))) =
            (near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) &&
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))) := by rw [hcF]; rfl
        rw [hif, Bool.and_eq_true] at hbool
        obtain ⟨hn1, hn2⟩ := hbool
        unfold near at hn1 hn2
        rw [decide_eq_true_eq] at hn1 hn2
        omega
  have hmapsTo : (CFGV ℓ ℓ : Set (Finset (ℤ × ℤ))).MapsTo
      (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)))
      ((states B).toFinset.biUnion (fun s => STKI ℓ s.1 s.2)) := by
    intro S' hS'
    rw [Finset.mem_coe] at hS'
    obtain ⟨g, c, hTmem, hsmem⟩ := hdecomp S' hS'
    rw [Finset.mem_coe, Finset.mem_biUnion]
    exact ⟨(g, c), List.mem_toFinset.mpr hsmem, hTmem⟩
  have hfiber : ∀ g c, ∀ T ∈ STKI ℓ g c,
      ((CFGV ℓ ℓ).filter (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) = T)).card =
      endMul g c := by
    intro g c T hT
    have hstkOrig : IsStackI ℓ g c T := (mem_STKI hℓ).mp hT
    obtain ⟨hL, hR, hmaxeq, hOK, hc, hforce⟩ := isStackI_top hℓ hstkOrig
    obtain ⟨hgpos, hTcard, hT0, hTty, hTrow0, hTrowmid, hex⟩ := hstkOrig
    have hty : ∀ p ∈ T, p.2 ≤ (ℓ : ℤ) := fun p hp => (hTty p hp).2
    set xL := rowMinX T (ℓ : ℤ) with hxLdef
    have hmemIff : ∀ x : ℤ, insert (x, (ℓ : ℤ) + 1) T ∈ CFGV ℓ ℓ ↔
        (if c then near (x - xL) || near (x - xL - (g : ℤ))
         else near (x - xL) && near (x - xL - (g : ℤ))) = true := by
      intro x
      have hqnotT : (x, (ℓ : ℤ) + 1) ∉ T := by intro hmem; have := hty _ hmem; omega
      rw [mem_CFGV]
      constructor
      · intro hVc
        exact (connected_insert_q_iff hgpos hty hL hR hforce hOK hc x).mp hVc.2.2.2.2.2.2
      · intro hbool
        have hKC := (connected_insert_q_iff hgpos hty hL hR hforce hOK hc x).mpr hbool
        refine ⟨by rw [Finset.card_insert_of_notMem hqnotT, hTcard]; omega,
          Finset.mem_insert_of_mem hT0, ?_, ?_, ?_, ?_, hKC⟩
        · intro p hp
          rcases Finset.mem_insert.mp hp with rfl | hpT
          · exact ⟨by omega, by omega⟩
          · have hb := hTty p hpT
            exact ⟨hb.1, by omega⟩
        · rw [rowSize_insert_other (by omega), hTrow0]
        · have heq2 : rowSize (insert (x, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              rowSize T ((ℓ : ℤ) + 1) + 1 := rowSize_insert_same hqnotT rfl
          rw [heq2]
          have hrz : rowSize T ((ℓ : ℤ) + 1) = 0 := by
            unfold rowSize
            rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
            intro p hp
            have := hty p hp
            omega
          omega
        · intro i hi
          rw [rowSize_insert_other (by rw [Finset.mem_Icc] at hi; omega), hTrowmid i hi]
    have hbij : ((Finset.range (g + 5)).filter fun n : ℕ =>
        (if c then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
         else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true).card =
        ((CFGV ℓ ℓ).filter (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) = T)).card := by
      refine Finset.card_bij (fun n _ => insert (xL + (n : ℤ) - 2, (ℓ : ℤ) + 1) T) ?_ ?_ ?_
      · intro n hn
        rw [Finset.mem_filter] at hn
        rw [Finset.mem_filter]
        have heq1 : (xL + (n : ℤ) - 2) - xL = (n : ℤ) - 2 := by ring
        refine ⟨(hmemIff (xL + (n : ℤ) - 2)).mpr (by rw [heq1]; exact hn.2), ?_⟩
        apply Finset.ext
        intro p
        rw [Finset.mem_filter, Finset.mem_insert]
        have hqnotT : (xL + (n : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
          intro hmem; have := hty _ hmem; omega
        constructor
        · rintro ⟨rfl | hpT, hple⟩
          · exact absurd hple (by omega)
          · exact hpT
        · intro hpT
          exact ⟨Or.inr hpT, hty p hpT⟩
      · intro n1 hn1 n2 hn2 heq
        have e1 : xL + (n1 : ℤ) - 2 = xL + (n2 : ℤ) - 2 := by
          have := congrArg (fun S => rowMaxX S ((ℓ : ℤ) + 1)) heq
          have hqnotT1 : (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
            intro hmem; have := hty _ hmem; omega
          have hqnotT2 : (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
            intro hmem; have := hty _ hmem; omega
          have hrz : rowSize T ((ℓ : ℤ) + 1) = 0 := by
            unfold rowSize
            rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
            intro p hp
            have := hty p hp
            omega
          have hr1 : rowMaxX (insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              xL + (n1 : ℤ) - 2 := by
            have hm := rowMaxX_mem (S := insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T) (y := (ℓ:ℤ)+1)
              (by rw [rowSize_insert_same hqnotT1 rfl]; omega)
            rw [Finset.mem_insert] at hm
            rcases hm with heqm | hmT
            · exact congrArg Prod.fst heqm
            · exfalso
              have := hty _ hmT
              have h2 := le_rowMaxX (S := insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T)
                (y := (ℓ:ℤ)+1) (Finset.mem_insert_self _ _) rfl
              omega
          have hr2 : rowMaxX (insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              xL + (n2 : ℤ) - 2 := by
            have hm := rowMaxX_mem (S := insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T) (y := (ℓ:ℤ)+1)
              (by rw [rowSize_insert_same hqnotT2 rfl]; omega)
            rw [Finset.mem_insert] at hm
            rcases hm with heqm | hmT
            · exact congrArg Prod.fst heqm
            · exfalso
              have := hty _ hmT
              have h2 := le_rowMaxX (S := insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T)
                (y := (ℓ:ℤ)+1) (Finset.mem_insert_self _ _) rfl
              omega
          rw [hr1, hr2] at this
          exact this
        omega
      · intro S' hS'
        rw [Finset.mem_filter] at hS'
        obtain ⟨hS'mem, hS'eq⟩ := hS'
        obtain ⟨hV'card, hV'0, hV'y, hV'row0, hV'rowtop, hV'rowmid, hV'conn⟩ := mem_CFGV.mp hS'mem
        have hqS' : (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) ∈ S' := rowMaxX_mem (by omega)
        set q' := (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) with hq'def
        have hS'eqT : S' = insert q' T := by
          apply Finset.ext
          intro p
          rw [Finset.mem_insert]
          constructor
          · intro hpS'
            obtain ⟨hpy1, hpy2⟩ := hV'y p hpS'
            by_cases hple : p.2 ≤ (ℓ : ℤ)
            · right
              rw [← hS'eq, Finset.mem_filter]
              exact ⟨hpS', hple⟩
            · left
              have hpeq : p.2 = (ℓ : ℤ) + 1 := by omega
              have hmem1 : p ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
                Finset.mem_filter.mpr ⟨hpS', hpeq⟩
              have hmem2 : q' ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
                Finset.mem_filter.mpr ⟨hqS', by rw [hq'def]⟩
              exact Finset.card_le_one.mp (le_of_eq hV'rowtop) p hmem1 _ hmem2
          · rintro (rfl | hpT)
            · exact hqS'
            · rw [← hS'eq] at hpT
              exact (Finset.mem_filter.mp hpT).1
        have hbool : (if c then near (q'.1 - xL) || near (q'.1 - xL - (g : ℤ))
            else near (q'.1 - xL) && near (q'.1 - xL - (g : ℤ))) = true := by
          apply (hmemIff q'.1).mp
          have hqeq : (q'.1, (ℓ : ℤ) + 1) = q' := Prod.ext rfl rfl
          rw [hqeq, ← hS'eqT, mem_CFGV]
          exact ⟨hV'card, hV'0, hV'y, hV'row0, hV'rowtop, hV'rowmid, hV'conn⟩
        have hbound : -1 ≤ q'.1 - xL ∧ q'.1 - xL ≤ (g : ℤ) + 1 := by
          cases c with
          | true =>
              simp only [if_true] at hbool
              rw [Bool.or_eq_true] at hbool
              rcases hbool with h1 | h2
              · unfold near at h1; rw [decide_eq_true_eq] at h1; omega
              · unfold near at h2; rw [decide_eq_true_eq] at h2; omega
          | false =>
              simp only [Bool.false_eq_true, if_false, Bool.and_eq_true] at hbool
              obtain ⟨hn1, hn2⟩ := hbool
              unfold near at hn1 hn2
              rw [decide_eq_true_eq] at hn1 hn2
              omega
        refine ⟨(q'.1 - xL + 2).toNat, ?_, ?_⟩
        · rw [Finset.mem_filter, Finset.mem_range]
          refine ⟨by omega, ?_⟩
          have heq1 : ((q'.1 - xL + 2).toNat : ℤ) - 2 = q'.1 - xL := by omega
          rw [heq1]
          exact hbool
        · have hxeq : xL + ((q'.1 - xL + 2).toNat : ℤ) - 2 = q'.1 := by omega
          have hqeq2 : (q'.1, (ℓ : ℤ) + 1) = q' := Prod.ext rfl rfl
          rw [hxeq, hqeq2, ← hS'eqT]
    rw [← hbij, endCount_eq g hgpos c]
  have hdisj : ((states B).toFinset : Set GapWalk.St).PairwiseDisjoint (fun s : GapWalk.St =>
      STKI ℓ s.1 s.2) := by
    intro s1 _ s2 _ hne
    apply Finset.disjoint_left.mpr
    intro T hT1 hT2
    apply hne
    obtain ⟨g1, c1⟩ := s1
    obtain ⟨g2, c2⟩ := s2
    obtain ⟨hg1, hc1⟩ := isStackI_state_unique hℓ ((mem_STKI hℓ).mp hT1) ((mem_STKI hℓ).mp hT2)
    exact Prod.ext hg1 hc1
  unfold V
  rw [Finset.card_eq_sum_card_fiberwise hmapsTo, Finset.sum_biUnion hdisj]
  rw [qEndF_eq_sum, ← list_sum_eq_finset_sum_toFinset (states B) (states_nodup B)]
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  rw [Finset.sum_congr rfl (fun T hT => hfiber g c T hT), Finset.sum_const, smul_eq_mul,
    Nat.mul_comm]

/-! ## The bare ends: `Vp ℓ ℓ` and (via reflection) `Vt ℓ ℓ` -/

/-- **Pure assembly.** A pure configuration *is* a connected bare stack:
`IsVpConfig ℓ ℓ S ↔ ∃ g, IsStackB ℓ g true S` (`stackOK` comes for free
from connectivity; conversely `stackOK_reach_iff_connected`). Partition
`CFGVp ℓ ℓ` fiberwise along `topState · ℓ` into `(states B).toFinset`
(gaps `≤ card − 1 = 2ℓ − 1 ≤ B`), fibers = `STKB ℓ g true` for `J` states
and empty for `P` states, and compare with `bareEndF_eq_sum`. -/
theorem Vp_eq_bareEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ ≤ B) :
    Vp ℓ ℓ = bareEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  have hiff : ∀ S : Finset (ℤ × ℤ), IsVpConfig ℓ ℓ S ↔ ∃ g, IsStackB ℓ g true S := by
    intro S
    constructor
    · intro hS
      obtain ⟨hcard, h01, hy, hx0, hrow, hconn⟩ := hS
      have hcard2 : S.card = 2 * ℓ := by omega
      have hy' : ∀ p ∈ S, (1 : ℤ) ≤ p.2 ∧ p.2 < 1 + (ℓ : ℤ) := by
        intro p hp
        obtain ⟨h1, h2⟩ := hy p hp
        exact ⟨h1, by omega⟩
      have hrowEq := rowSize_eq_two hy' hrow hcard2
      have hrsize : rowSize S (ℓ : ℤ) = 2 := hrowEq ℓ (Finset.mem_Icc.mpr ⟨hℓ, le_refl ℓ⟩)
      obtain ⟨aL, aR, haLS, haRS, haLy, haRy, hlt, -⟩ := row_two_cells hrsize
      have hpteq : (aL.1 + ((aR.1 - aL.1).toNat : ℤ), (ℓ : ℤ)) = aR := by
        have h1 : aL.1 + ((aR.1 - aL.1).toNat : ℤ) = aR.1 := by omega
        rw [h1]
        exact Prod.ext rfl haRy.symm
      refine ⟨(aR.1 - aL.1).toNat, by omega, hcard2, h01, hy, hx0, hrowEq, aL, haLS, haLy,
        by rw [hpteq]; exact haRS, fun p hp => Or.inl (hconn p hp aL haLS), ?_⟩
      rw [hpteq]
      exact ⟨fun _ => hconn aL haLS aR haRS, fun _ => rfl⟩
    · rintro ⟨g, hstk⟩
      obtain ⟨-, hcard, h01, hy, hx0, hrow, p, hpS, hpi, hpgS, hOK, hcls⟩ := hstk
      refine ⟨by omega, h01, hy, hx0, fun i hi => by rw [hrow i hi], ?_⟩
      exact (stackOK_reach_iff_connected hpS hpgS hOK).mp (hcls.mp rfl)
  have hmaps : ∀ S ∈ CFGVp ℓ ℓ, topState S (ℓ : ℤ) ∈ (states B).toFinset := by
    intro S hS
    rw [mem_CFGVp (by omega)] at hS
    obtain ⟨g, hstk⟩ := (hiff S).mp hS
    rw [List.mem_toFinset, isStackB_topState hℓ hstk]
    have hgle : g ≤ 2 * ℓ := isStackB_J_le hℓ hstk
    rw [GapWalk.mem_states]
    exact ⟨hstk.1, by omega⟩
  rw [Vp, Finset.card_eq_sum_card_fiberwise hmaps, bareEndF_eq_sum,
    ← list_sum_eq_finset_sum_toFinset (states B) (states_nodup B)]
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  cases c with
  | true =>
      simp only
      have hset : (CFGVp ℓ ℓ).filter (fun S => topState S (ℓ : ℤ) = (g, true)) = STKB ℓ g true := by
        apply Finset.ext
        intro S
        rw [Finset.mem_filter, mem_STKB hℓ]
        constructor
        · rintro ⟨hSmem, hSs⟩
          rw [mem_CFGVp (by omega)] at hSmem
          obtain ⟨g', hstk⟩ := (hiff S).mp hSmem
          rw [isStackB_topState hℓ hstk] at hSs
          have hgeq : g' = g := (Prod.ext_iff.mp hSs).1
          rwa [hgeq] at hstk
        · intro hstk
          refine ⟨?_, isStackB_topState hℓ hstk⟩
          rw [mem_CFGVp (by omega)]
          exact (hiff S).mpr ⟨g, hstk⟩
      rw [hset, if_pos trivial]
  | false =>
      simp only
      have hset : (CFGVp ℓ ℓ).filter (fun S => topState S (ℓ : ℤ) = (g, false)) = ∅ := by
        apply Finset.eq_empty_iff_forall_notMem.mpr
        intro S
        rw [Finset.mem_filter]
        rintro ⟨hSmem, hSs⟩
        rw [mem_CFGVp (by omega)] at hSmem
        obtain ⟨g', hstk⟩ := (hiff S).mp hSmem
        have := isStackB_topState hℓ hstk
        rw [this] at hSs
        exact absurd hSs (by simp)
      rw [hset, Finset.card_empty, if_neg (by simp)]

/-- The **bare-stack-plus-contact family** `BQ ℓ`: what `qEnd` on the bare
walk counts directly — rows `1..ℓ` two cells each anchored bare-style, one
extra cell on row `ℓ+1`, all king-connected. -/
def IsBQ (ℓ : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = 2 * ℓ + 1 ∧
  ((0 : ℤ), (1 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 1 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + 1) ∧
  (∀ p ∈ S, p.2 = 1 → 0 ≤ p.1) ∧
  rowSize S ((ℓ : ℤ) + 1) = 1 ∧
  (∀ r ∈ Finset.Icc 1 ℓ, rowSize S (r : ℤ) = 2) ∧
  KingConnected S

instance (ℓ : ℕ) (S : Finset (ℤ × ℤ)) : Decidable (IsBQ ℓ S) := by
  unfold IsBQ; infer_instance

/-- `BQ ℓ`, enumerated in the window idiom (connected with an anchor on
row 1, `card = 2ℓ + 1`, so `|x| ≤ 2ℓ` by `connected_sub_x_le`; width
`2ℓ + 1` for slack). -/
def BQ (ℓ : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  ((window (2 * ℓ + 1) 1 (ℓ + 1)).powersetCard (2 * ℓ + 1)).filter (IsBQ ℓ)

/-- Window independence for `BQ` (mirror `mem_CFGVp`). -/
theorem mem_BQ {ℓ : ℕ} (hℓ : 1 ≤ ℓ) {S : Finset (ℤ × ℤ)} :
    S ∈ BQ ℓ ↔ IsBQ ℓ S := by
  rw [BQ, Finset.mem_filter]
  constructor
  · exact fun hmem => hmem.2
  · intro hS
    refine ⟨?_, hS⟩
    obtain ⟨hcard, h01, hy, -, -, -, hconn⟩ := hS
    rw [Finset.mem_powersetCard]
    refine ⟨?_, hcard⟩
    intro p hp
    have hx1 : p.1 - (0 : ℤ) ≤ (S.card : ℤ) - 1 := connected_sub_x_le hconn h01 hp
    have hx2 : (0 : ℤ) - p.1 ≤ (S.card : ℤ) - 1 := connected_sub_x_le hconn hp h01
    obtain ⟨hy1, hy2⟩ := hy p hp
    have hcardZ : (S.card : ℤ) = 2 * (ℓ : ℤ) + 1 := by exact_mod_cast hcard
    rw [hcardZ] at hx1 hx2
    rw [mem_window]
    refine ⟨?_, ?_, ?_, ?_⟩ <;> omega

/-- **Bare assembly.** `(BQ ℓ).card` counted fiberwise over bare-stack
truncations — the identical argument to `V_eq_qEndF` with `IsStackB`
replacing `IsStackI` (anchor clauses pass to the truncation verbatim: the
dropped cell sits on row `ℓ + 1 ≥ 2`). -/
theorem BQ_card_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    (BQ ℓ).card = qEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  have hdecomp : ∀ S' ∈ BQ ℓ, ∃ g c,
      (S'.filter (fun p => p.2 ≤ (ℓ : ℤ))) ∈ STKB ℓ g c ∧ (g, c) ∈ states B := by
    intro S' hS'mem
    rw [mem_BQ hℓ] at hS'mem
    obtain ⟨hcard, h01, hy, hx0, hrowtop, hrowmid, hconn⟩ := hS'mem
    have hqS' : (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) ∈ S' := rowMaxX_mem (by omega)
    set q : ℤ × ℤ := (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) with hqdef
    set T : Finset (ℤ × ℤ) := S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) with hTdef
    have hqnotT : q ∉ T := by
      rw [hTdef, Finset.mem_filter]
      rintro ⟨-, hle⟩
      rw [hqdef] at hle
      omega
    have hins : insert q T = S' := by
      apply Finset.ext
      intro p
      simp only [Finset.mem_insert, hTdef, Finset.mem_filter]
      constructor
      · rintro (rfl | ⟨hpS', -⟩)
        · exact hqS'
        · exact hpS'
      · intro hpS'
        obtain ⟨hy1, hy2⟩ := hy p hpS'
        by_cases hptop : p.2 = (ℓ : ℤ) + 1
        · left
          have hmem1 : p ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
            Finset.mem_filter.mpr ⟨hpS', hptop⟩
          have hmem2 : q ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
            Finset.mem_filter.mpr ⟨hqS', by rw [hqdef]⟩
          exact Finset.card_le_one.mp (le_of_eq hrowtop) p hmem1 _ hmem2
        · right
          exact ⟨hpS', by omega⟩
    have hTcard : T.card = 2 * ℓ := by
      have hc1 := Finset.card_insert_of_notMem hqnotT
      rw [hins] at hc1
      omega
    have hT01 : ((0 : ℤ), (1 : ℤ)) ∈ T := by
      rw [hTdef, Finset.mem_filter]
      exact ⟨h01, by omega⟩
    have hty : ∀ p ∈ T, (1 : ℤ) ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) := by
      intro p hp
      rw [hTdef, Finset.mem_filter] at hp
      exact ⟨(hy p hp.1).1, hp.2⟩
    have hty' : ∀ p ∈ T, p.2 ≤ (ℓ : ℤ) := fun p hp => (hty p hp).2
    have hx0' : ∀ p ∈ T, p.2 = 1 → 0 ≤ p.1 := by
      intro p hp hp1
      rw [hTdef, Finset.mem_filter] at hp
      exact hx0 p hp.1 hp1
    have hrowmid' : ∀ i ∈ Finset.Icc 1 ℓ, rowSize T (i : ℤ) = 2 := by
      intro i hi
      have hfeq : rowSize T (i : ℤ) = rowSize S' (i : ℤ) := by
        rw [Finset.mem_Icc] at hi
        unfold rowSize
        rw [hTdef, Finset.filter_filter]
        congr 1
        apply Finset.filter_congr
        intro p _
        constructor
        · rintro ⟨-, hpeq⟩; exact hpeq
        · intro hpeq; exact ⟨by omega, hpeq⟩
      rw [hfeq]
      exact hrowmid i hi
    have hrsizeT : rowSize T (ℓ : ℤ) = 2 := hrowmid' ℓ (Finset.mem_Icc.mpr ⟨hℓ, le_refl ℓ⟩)
    obtain ⟨aL, aR, haLT, haRT, haLy, haRy, hlt, hforceT⟩ := row_two_cells hrsizeT
    set g : ℕ := (aR.1 - aL.1).toNat with hgdef
    have hcastg : (g : ℤ) = aR.1 - aL.1 := by rw [hgdef]; omega
    have hAeq : (aL.1, (ℓ : ℤ)) = aL := Prod.ext rfl haLy.symm
    have hpteq : (aL.1 + (g : ℤ), (ℓ : ℤ)) = aR := by
      rw [hcastg]
      have heq2 : aL.1 + (aR.1 - aL.1) = aR.1 := by ring
      rw [heq2]
      exact Prod.ext rfl haRy.symm
    have htL0 : (aL.1, (ℓ : ℤ)) ∈ T := by rw [hAeq]; exact haLT
    have htR0 : (aL.1 + (g : ℤ), (ℓ : ℤ)) ∈ T := by rw [hpteq]; exact haRT
    have hrow0' : ∀ q' ∈ T, q'.2 = (ℓ : ℤ) →
        q' = (aL.1, (ℓ : ℤ)) ∨ q' = (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      intro q' hq' hq'ℓ
      rcases hforceT q' hq' hq'ℓ with rfl | rfl
      · exact Or.inl hAeq.symm
      · exact Or.inr hpteq.symm
    have hSOK0 : stackOK T (aL.1, (ℓ : ℤ)) (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      apply stackOK_of_connected_insert (i := ℓ) (xL := aL.1) (x := rowMaxX S' ((ℓ : ℤ) + 1))
        hty' htL0 htR0 hrow0'
      rw [hins]; exact hconn
    set c : Bool :=
      decide (reach T (aL.1, (ℓ : ℤ)) (aL.1 + (g : ℤ), (ℓ : ℤ))) with hcdef
    have hc : c = true ↔ reach T (aL.1, (ℓ : ℤ)) (aL.1 + (g : ℤ), (ℓ : ℤ)) := by
      rw [hcdef]
      constructor
      · intro h; exact of_decide_eq_true h
      · intro h; exact decide_eq_true h
    have hgpos : 1 ≤ g := by rw [hgdef]; omega
    have hstkB : T ∈ STKB ℓ g c := by
      rw [mem_STKB hℓ]
      exact ⟨hgpos, hTcard, hT01, hty, hx0', hrowmid', (aL.1, (ℓ : ℤ)), htL0, rfl, htR0,
        hSOK0, hc⟩
    have hconn' : KingConnected (insert (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) T) := by
      rw [hins]; exact hconn
    have hbool := (connected_insert_q_iff hgpos hty' htL0 htR0 hrow0' hSOK0 hc
      (rowMaxX S' ((ℓ : ℤ) + 1))).mp hconn'
    refine ⟨g, c, ?_, ?_⟩
    · exact hstkB
    · rw [GapWalk.mem_states]
      refine ⟨hgpos, ?_⟩
      have hIsStackB : IsStackB ℓ g c T := (mem_STKB hℓ).mp hstkB
      by_cases hcT : c = true
      · rw [hcT] at hIsStackB
        have hJ := isStackB_J_le hℓ hIsStackB
        omega
      · have hcF : c = false := by
          revert hcT
          generalize c = c'
          cases c' <;> simp
        have hif : (if c then near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) ||
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))
            else near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) &&
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))) =
            (near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1) &&
              near (rowMaxX S' ((ℓ : ℤ) + 1) - aL.1 - (g : ℤ))) := by rw [hcF]; rfl
        rw [hif, Bool.and_eq_true] at hbool
        obtain ⟨hn1, hn2⟩ := hbool
        unfold near at hn1 hn2
        rw [decide_eq_true_eq] at hn1 hn2
        omega
  have hmapsTo : (BQ ℓ : Set (Finset (ℤ × ℤ))).MapsTo
      (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)))
      ((states B).toFinset.biUnion (fun s => STKB ℓ s.1 s.2)) := by
    intro S' hS'
    rw [Finset.mem_coe] at hS'
    obtain ⟨g, c, hTmem, hsmem⟩ := hdecomp S' hS'
    rw [Finset.mem_coe, Finset.mem_biUnion]
    exact ⟨(g, c), List.mem_toFinset.mpr hsmem, hTmem⟩
  have hfiber : ∀ g c, ∀ T ∈ STKB ℓ g c,
      ((BQ ℓ).filter (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) = T)).card =
      endMul g c := by
    intro g c T hT
    have hstkOrig : IsStackB ℓ g c T := (mem_STKB hℓ).mp hT
    obtain ⟨hL, hR, hmaxeq, hOK, hc, hforce⟩ := isStackB_top hℓ hstkOrig
    obtain ⟨hgpos, hTcard, hT01, hTty, hTx0, hTrowmid, hex⟩ := hstkOrig
    have hty : ∀ p ∈ T, p.2 ≤ (ℓ : ℤ) := fun p hp => (hTty p hp).2
    set xL := rowMinX T (ℓ : ℤ) with hxLdef
    have hmemIff : ∀ x : ℤ, insert (x, (ℓ : ℤ) + 1) T ∈ BQ ℓ ↔
        (if c then near (x - xL) || near (x - xL - (g : ℤ))
         else near (x - xL) && near (x - xL - (g : ℤ))) = true := by
      intro x
      have hqnotT : (x, (ℓ : ℤ) + 1) ∉ T := by intro hmem; have := hty _ hmem; omega
      rw [mem_BQ hℓ]
      constructor
      · intro hVc
        exact (connected_insert_q_iff hgpos hty hL hR hforce hOK hc x).mp hVc.2.2.2.2.2.2
      · intro hbool
        have hKC := (connected_insert_q_iff hgpos hty hL hR hforce hOK hc x).mpr hbool
        refine ⟨by rw [Finset.card_insert_of_notMem hqnotT, hTcard],
          Finset.mem_insert_of_mem hT01, ?_, ?_, ?_, ?_, hKC⟩
        · intro p hp
          rcases Finset.mem_insert.mp hp with rfl | hpT
          · exact ⟨by omega, le_refl _⟩
          · have hb := hTty p hpT
            exact ⟨hb.1, by omega⟩
        · intro p hp hp1
          rcases Finset.mem_insert.mp hp with rfl | hpT
          · exfalso; omega
          · exact hTx0 p hpT hp1
        · have heq2 : rowSize (insert (x, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              rowSize T ((ℓ : ℤ) + 1) + 1 := rowSize_insert_same hqnotT rfl
          rw [heq2]
          have hrz : rowSize T ((ℓ : ℤ) + 1) = 0 := by
            unfold rowSize
            rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
            intro p hp
            have := hty p hp
            omega
          omega
        · intro i hi
          rw [rowSize_insert_other (by rw [Finset.mem_Icc] at hi; omega), hTrowmid i hi]
    have hbij : ((Finset.range (g + 5)).filter fun n : ℕ =>
        (if c then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
         else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true).card =
        ((BQ ℓ).filter (fun S' => S'.filter (fun p => p.2 ≤ (ℓ : ℤ)) = T)).card := by
      refine Finset.card_bij (fun n _ => insert (xL + (n : ℤ) - 2, (ℓ : ℤ) + 1) T) ?_ ?_ ?_
      · intro n hn
        rw [Finset.mem_filter] at hn
        rw [Finset.mem_filter]
        have heq1 : (xL + (n : ℤ) - 2) - xL = (n : ℤ) - 2 := by ring
        refine ⟨(hmemIff (xL + (n : ℤ) - 2)).mpr (by rw [heq1]; exact hn.2), ?_⟩
        apply Finset.ext
        intro p
        rw [Finset.mem_filter, Finset.mem_insert]
        have hqnotT : (xL + (n : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
          intro hmem; have := hty _ hmem; omega
        constructor
        · rintro ⟨rfl | hpT, hple⟩
          · exact absurd hple (by omega)
          · exact hpT
        · intro hpT
          exact ⟨Or.inr hpT, hty p hpT⟩
      · intro n1 hn1 n2 hn2 heq
        have e1 : xL + (n1 : ℤ) - 2 = xL + (n2 : ℤ) - 2 := by
          have := congrArg (fun S => rowMaxX S ((ℓ : ℤ) + 1)) heq
          have hqnotT1 : (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
            intro hmem; have := hty _ hmem; omega
          have hqnotT2 : (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) ∉ T := by
            intro hmem; have := hty _ hmem; omega
          have hrz : rowSize T ((ℓ : ℤ) + 1) = 0 := by
            unfold rowSize
            rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
            intro p hp
            have := hty p hp
            omega
          have hr1 : rowMaxX (insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              xL + (n1 : ℤ) - 2 := by
            have hm := rowMaxX_mem (S := insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T) (y := (ℓ:ℤ)+1)
              (by rw [rowSize_insert_same hqnotT1 rfl]; omega)
            rw [Finset.mem_insert] at hm
            rcases hm with heqm | hmT
            · exact congrArg Prod.fst heqm
            · exfalso
              have := hty _ hmT
              have h2 := le_rowMaxX (S := insert (xL + (n1 : ℤ) - 2, (ℓ : ℤ) + 1) T)
                (y := (ℓ:ℤ)+1) (Finset.mem_insert_self _ _) rfl
              omega
          have hr2 : rowMaxX (insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T) ((ℓ : ℤ) + 1) =
              xL + (n2 : ℤ) - 2 := by
            have hm := rowMaxX_mem (S := insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T) (y := (ℓ:ℤ)+1)
              (by rw [rowSize_insert_same hqnotT2 rfl]; omega)
            rw [Finset.mem_insert] at hm
            rcases hm with heqm | hmT
            · exact congrArg Prod.fst heqm
            · exfalso
              have := hty _ hmT
              have h2 := le_rowMaxX (S := insert (xL + (n2 : ℤ) - 2, (ℓ : ℤ) + 1) T)
                (y := (ℓ:ℤ)+1) (Finset.mem_insert_self _ _) rfl
              omega
          rw [hr1, hr2] at this
          exact this
        omega
      · intro S' hS'
        rw [Finset.mem_filter] at hS'
        obtain ⟨hS'mem, hS'eq⟩ := hS'
        obtain ⟨hV'card, hV'01, hV'y, hV'x0, hV'rowtop, hV'rowmid, hV'conn⟩ :=
          (mem_BQ hℓ).mp hS'mem
        have hqS' : (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) ∈ S' := rowMaxX_mem (by omega)
        set q' := (rowMaxX S' ((ℓ : ℤ) + 1), (ℓ : ℤ) + 1) with hq'def
        have hS'eqT : S' = insert q' T := by
          apply Finset.ext
          intro p
          rw [Finset.mem_insert]
          constructor
          · intro hpS'
            obtain ⟨hpy1, hpy2⟩ := hV'y p hpS'
            by_cases hple : p.2 ≤ (ℓ : ℤ)
            · right
              rw [← hS'eq, Finset.mem_filter]
              exact ⟨hpS', hple⟩
            · left
              have hpeq : p.2 = (ℓ : ℤ) + 1 := by omega
              have hmem1 : p ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
                Finset.mem_filter.mpr ⟨hpS', hpeq⟩
              have hmem2 : q' ∈ S'.filter (fun c => c.2 = (ℓ : ℤ) + 1) :=
                Finset.mem_filter.mpr ⟨hqS', by rw [hq'def]⟩
              exact Finset.card_le_one.mp (le_of_eq hV'rowtop) p hmem1 _ hmem2
          · rintro (rfl | hpT)
            · exact hqS'
            · rw [← hS'eq] at hpT
              exact (Finset.mem_filter.mp hpT).1
        have hbool : (if c then near (q'.1 - xL) || near (q'.1 - xL - (g : ℤ))
            else near (q'.1 - xL) && near (q'.1 - xL - (g : ℤ))) = true := by
          apply (hmemIff q'.1).mp
          have hqeq : (q'.1, (ℓ : ℤ) + 1) = q' := Prod.ext rfl rfl
          rw [hqeq, ← hS'eqT, mem_BQ hℓ]
          exact ⟨hV'card, hV'01, hV'y, hV'x0, hV'rowtop, hV'rowmid, hV'conn⟩
        have hbound : -1 ≤ q'.1 - xL ∧ q'.1 - xL ≤ (g : ℤ) + 1 := by
          cases c with
          | true =>
              simp only [if_true] at hbool
              rw [Bool.or_eq_true] at hbool
              rcases hbool with h1 | h2
              · unfold near at h1; rw [decide_eq_true_eq] at h1; omega
              · unfold near at h2; rw [decide_eq_true_eq] at h2; omega
          | false =>
              simp only [Bool.false_eq_true, if_false, Bool.and_eq_true] at hbool
              obtain ⟨hn1, hn2⟩ := hbool
              unfold near at hn1 hn2
              rw [decide_eq_true_eq] at hn1 hn2
              omega
        refine ⟨(q'.1 - xL + 2).toNat, ?_, ?_⟩
        · rw [Finset.mem_filter, Finset.mem_range]
          refine ⟨by omega, ?_⟩
          have heq1 : ((q'.1 - xL + 2).toNat : ℤ) - 2 = q'.1 - xL := by omega
          rw [heq1]
          exact hbool
        · have hxeq : xL + ((q'.1 - xL + 2).toNat : ℤ) - 2 = q'.1 := by omega
          have hqeq2 : (q'.1, (ℓ : ℤ) + 1) = q' := Prod.ext rfl rfl
          rw [hxeq, hqeq2, ← hS'eqT]
    rw [← hbij, endCount_eq g hgpos c]
  have hdisj : ((states B).toFinset : Set GapWalk.St).PairwiseDisjoint (fun s : GapWalk.St =>
      STKB ℓ s.1 s.2) := by
    intro s1 _ s2 _ hne
    apply Finset.disjoint_left.mpr
    intro T hT1 hT2
    apply hne
    obtain ⟨g1, c1⟩ := s1
    obtain ⟨g2, c2⟩ := s2
    obtain ⟨hg1, hc1⟩ := isStackB_state_unique hℓ ((mem_STKB hℓ).mp hT1) ((mem_STKB hℓ).mp hT2)
    exact Prod.ext hg1 hc1
  rw [Finset.card_eq_sum_card_fiberwise hmapsTo, Finset.sum_biUnion hdisj]
  rw [qEndF_eq_sum, ← list_sum_eq_finset_sum_toFinset (states B) (states_nodup B)]
  congr 1
  apply List.map_congr_left
  intro s hs
  obtain ⟨g, c⟩ := s
  rw [Finset.sum_congr rfl (fun T hT => hfiber g c T hT), Finset.sum_const, smul_eq_mul,
    Nat.mul_comm]

/-- The row profile transports exactly under a `flipMap` image: row `y` of
the image is the image of row `cy − y`. -/
private theorem rowSize_flipMap_image (S : Finset (ℤ × ℤ)) (cx cy y : ℤ) :
    rowSize (S.image (flipMap cx cy)) y = rowSize S (cy - y) := by
  unfold rowSize
  have heq : (S.image (flipMap cx cy)).filter (fun p => p.2 = y) =
      (S.filter (fun p => p.2 = cy - y)).image (flipMap cx cy) := by
    apply Finset.ext
    intro p
    simp only [Finset.mem_filter, Finset.mem_image]
    constructor
    · rintro ⟨⟨q, hqS, rfl⟩, hy⟩
      refine ⟨q, ⟨hqS, ?_⟩, rfl⟩
      unfold flipMap at hy
      simp only at hy
      omega
    · rintro ⟨q, ⟨hqS, hq2⟩, rfl⟩
      refine ⟨⟨q, hqS, rfl⟩, ?_⟩
      unfold flipMap
      simp only
      omega
  rw [heq, Finset.card_image_of_injective _ (flipMap_injective cx cy)]

/-- `rowMinX` transports under a `flipMap` image, given the source row is
nonempty: the leftmost cell of row `y` in the image is the shift of the
leftmost cell of row `cy − y` in the source. -/
private theorem rowMinX_flipMap_image {S : Finset (ℤ × ℤ)} (cx cy y : ℤ)
    (h : 1 ≤ rowSize S (cy - y)) :
    rowMinX (S.image (flipMap cx cy)) y = rowMinX S (cy - y) - cx := by
  have hSize : 1 ≤ rowSize (S.image (flipMap cx cy)) y := by
    rw [rowSize_flipMap_image]; exact h
  have hmem1 : (rowMinX S (cy - y) - cx, y) ∈ S.image (flipMap cx cy) := by
    apply Finset.mem_image.mpr
    refine ⟨(rowMinX S (cy - y), cy - y), rowMinX_mem h, ?_⟩
    unfold flipMap
    simp
  have hle : rowMinX (S.image (flipMap cx cy)) y ≤ rowMinX S (cy - y) - cx :=
    rowMinX_le hmem1 rfl
  have hmem2 := rowMinX_mem (S := S.image (flipMap cx cy)) (y := y) hSize
  obtain ⟨p, hpS, hpeq⟩ := Finset.mem_image.mp hmem2
  have hp2 : p.2 = cy - y := by
    have hh : (flipMap cx cy p).2 = ((rowMinX (S.image (flipMap cx cy)) y, y) : ℤ × ℤ).2 :=
      congrArg Prod.snd hpeq
    change p.2 = cy - y
    have : cy - p.2 = y := hh
    omega
  have hp1eq : p.1 - cx = rowMinX (S.image (flipMap cx cy)) y := by
    have hh : (flipMap cx cy p).1 = ((rowMinX (S.image (flipMap cx cy)) y, y) : ℤ × ℤ).1 :=
      congrArg Prod.fst hpeq
    exact hh
  have hge2 : rowMinX S (cy - y) ≤ p.1 := rowMinX_le hpS hp2
  omega

/-- **The reflection.** `Vt ℓ ℓ = (BQ ℓ).card` by the y-flip about row
`ℓ + 1` (`Finset.card_bij'`):

* forward `CFGVt ℓ ℓ → BQ ℓ`:
  `S' ↦ S'.image (flipMap (rowMinX S' ℓ) (ℓ + 1))` — the contact cell
  `(0,0)` becomes the row-`(ℓ+1)` cell, old row `r` becomes new row
  `ℓ+1−r`, and the shift re-anchors the new row 1 (old row `ℓ`) at
  minimum `x = 0`;
* inverse `BQ ℓ → CFGVt ℓ ℓ`:
  `D ↦ D.image (flipMap (rowMinX D (ℓ+1)) (ℓ + 1))` — re-anchor at the
  unique top cell, which lands on `(0,0)`;
* round trips by `flipMap_flipMap` (each composite is a translation whose
  shift the anchors force to zero: `rowMinX` of the image row computes to
  minus the original shift);
* membership transport: `Finset.card_image_of_injective`
  (`flipMap_injective`) for the cardinality, `rowSize` under images of
  injective maps for the row profile, `kingConnected_image_of_adj_iff` +
  `kingAdj_flipMap` for connectivity, `mem_CFGVt` on the config side.
  For row extraction under the flip: `rowMinX (S.image (flipMap cx cy)) y
  = rowMinX S (cy − y) − cx` (min of a shifted image; prove as a private
  helper via `rowMinX_mem`/`rowMinX_le` antisymmetry rather than `min`
  algebra). -/
theorem Vt_eq_BQ_card (ℓ : ℕ) (hℓ : 1 ≤ ℓ) : Vt ℓ ℓ = (BQ ℓ).card := by
  unfold Vt
  refine Finset.card_bij'
    (fun S' _ => S'.image (flipMap (rowMinX S' (ℓ : ℤ)) ((ℓ : ℤ) + 1)))
    (fun D _ => D.image (flipMap (rowMinX D ((ℓ : ℤ) + 1)) ((ℓ : ℤ) + 1)))
    ?_ ?_ ?_ ?_
  · -- forward: CFGVt ℓ ℓ → BQ ℓ
    intro S' hS'
    rw [mem_CFGVt] at hS'
    obtain ⟨hcard, h0, hy, hrow0, hrowmid, hconn⟩ := hS'
    set cx := rowMinX S' (ℓ : ℤ) with hcxdef
    set S'' := S'.filter (fun p => 1 ≤ p.2) with hS''def
    have h0notS'' : ((0 : ℤ), (0 : ℤ)) ∉ S'' := by rw [hS''def]; simp
    have hins : insert ((0 : ℤ), (0 : ℤ)) S'' = S' := by
      apply Finset.ext
      intro p
      simp only [Finset.mem_insert, hS''def, Finset.mem_filter]
      constructor
      · rintro (rfl | ⟨hpS', -⟩)
        · exact h0
        · exact hpS'
      · intro hpS'
        obtain ⟨hy1, hy2⟩ := hy p hpS'
        by_cases hp0 : p.2 = 0
        · left
          have hmem1 : p ∈ S'.filter (fun c => c.2 = 0) := Finset.mem_filter.mpr ⟨hpS', hp0⟩
          have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
            Finset.mem_filter.mpr ⟨h0, rfl⟩
          exact Finset.card_le_one.mp (le_of_eq hrow0) p hmem1 _ hmem2
        · right
          exact ⟨hpS', by omega⟩
    have hS''card : S''.card = 2 * ℓ := by
      have hc1 := Finset.card_insert_of_notMem h0notS''
      rw [hins] at hc1
      omega
    have hfeq : ∀ i ∈ Finset.Icc 1 ℓ, rowSize S'' (i : ℤ) = rowSize S' (i : ℤ) := by
      intro i hi
      rw [Finset.mem_Icc] at hi
      unfold rowSize
      rw [hS''def, Finset.filter_filter]
      congr 1
      apply Finset.filter_congr
      intro p _
      constructor
      · rintro ⟨-, hpeq⟩; exact hpeq
      · intro hpeq; exact ⟨by omega, hpeq⟩
    have hrowmid2 : ∀ i ∈ Finset.Icc 1 ℓ, rowSize S' (i : ℤ) = 2 := by
      have hy'' : ∀ p ∈ S'', (1 : ℤ) ≤ p.2 ∧ p.2 < 1 + (ℓ : ℤ) := by
        intro p hp
        rw [hS''def, Finset.mem_filter] at hp
        have := hy p hp.1
        omega
      have hge'' : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S'' (i : ℤ) := by
        intro i hi
        rw [hfeq i hi]
        exact hrowmid i hi
      have hall := rowSize_eq_two hy'' hge'' hS''card
      intro i hi
      rw [← hfeq i hi]
      exact hall i hi
    have hminS'0 : rowMinX S' (0 : ℤ) = 0 := by
      have h1 : rowMinX S' (0 : ℤ) ≤ 0 := rowMinX_le h0 rfl
      have h3 := rowMinX_mem (S := S') (y := (0 : ℤ)) (by omega)
      have hmem1 : (rowMinX S' (0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
        Finset.mem_filter.mpr ⟨h3, rfl⟩
      have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
        Finset.mem_filter.mpr ⟨h0, rfl⟩
      have heq := Finset.card_le_one.mp (le_of_eq hrow0) _ hmem1 _ hmem2
      have := congrArg Prod.fst heq
      simpa using this
    have hrowℓ1 : 1 ≤ rowSize S' (ℓ : ℤ) := by
      have := hrowmid2 ℓ (Finset.mem_Icc.mpr ⟨hℓ, le_refl ℓ⟩); omega
    rw [mem_BQ hℓ]
    have hcardI : (S'.image (flipMap cx ((ℓ : ℤ) + 1))).card = 2 * ℓ + 1 := by
      rw [Finset.card_image_of_injective _ (flipMap_injective _ _), hcard]; omega
    refine ⟨hcardI, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · have heq : (ℓ : ℤ) + 1 - 1 = (ℓ : ℤ) := by ring
      have hmineq := rowMinX_flipMap_image cx ((ℓ : ℤ) + 1) 1 (heq ▸ hrowℓ1)
      rw [heq, hcxdef, sub_self] at hmineq
      have hmem := rowMinX_mem (S := S'.image (flipMap cx ((ℓ : ℤ) + 1))) (y := (1 : ℤ))
        (by rw [rowSize_flipMap_image, heq]; exact hrowℓ1)
      rwa [hmineq] at hmem
    · intro p hp
      rw [Finset.mem_image] at hp
      obtain ⟨q, hqS', rfl⟩ := hp
      obtain ⟨hqy1, hqy2⟩ := hy q hqS'
      have h1 : (flipMap cx ((ℓ : ℤ) + 1) q).2 = (ℓ : ℤ) + 1 - q.2 := rfl
      rw [h1]
      omega
    · intro p hp hp1
      rw [Finset.mem_image] at hp
      obtain ⟨q, hqS', rfl⟩ := hp
      have h1 : (flipMap cx ((ℓ : ℤ) + 1) q).1 = q.1 - cx := rfl
      have h2 : (flipMap cx ((ℓ : ℤ) + 1) q).2 = (ℓ : ℤ) + 1 - q.2 := rfl
      rw [h2] at hp1
      have hq2 : q.2 = (ℓ : ℤ) := by omega
      have hle : cx ≤ q.1 := rowMinX_le hqS' hq2
      rw [h1]; omega
    · rw [rowSize_flipMap_image]
      have heq : (ℓ : ℤ) + 1 - ((ℓ : ℤ) + 1) = 0 := by ring
      rw [heq]; exact hrow0
    · intro i hi
      rw [rowSize_flipMap_image]
      rw [Finset.mem_Icc] at hi
      have heq : (ℓ : ℤ) + 1 - (i : ℤ) = ((ℓ + 1 - i : ℕ) : ℤ) := by omega
      rw [heq]
      exact hrowmid2 (ℓ + 1 - i) (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
    · exact kingConnected_image_of_adj_iff (flipMap_injective _ _) (kingAdj_flipMap _ _) hconn
  · -- backward: BQ ℓ → CFGVt ℓ ℓ
    intro D hD
    rw [mem_BQ hℓ] at hD
    obtain ⟨hDcard, hD01, hDy, hDx0, hDrowtop, hDrowmid, hDconn⟩ := hD
    set cx' := rowMinX D ((ℓ : ℤ) + 1) with hcx'def
    have hDrow1_2 : rowSize D (1 : ℤ) = 2 := hDrowmid 1 (Finset.mem_Icc.mpr ⟨le_refl 1, hℓ⟩)
    have hminD1 : rowMinX D (1 : ℤ) = 0 := by
      have h1 : rowMinX D (1 : ℤ) ≤ 0 := rowMinX_le hD01 rfl
      have h3 := rowMinX_mem (S := D) (y := (1 : ℤ)) (by omega)
      have h2 : 0 ≤ rowMinX D (1 : ℤ) := hDx0 _ h3 rfl
      omega
    have hDrowtop1 : 1 ≤ rowSize D ((ℓ : ℤ) + 1) := by omega
    rw [mem_CFGVt]
    have hcardI : (D.image (flipMap cx' ((ℓ : ℤ) + 1))).card = ℓ + ℓ + 1 := by
      rw [Finset.card_image_of_injective _ (flipMap_injective _ _), hDcard]; omega
    refine ⟨hcardI, ?_, ?_, ?_, ?_, ?_⟩
    · have heq : (ℓ : ℤ) + 1 - 0 = (ℓ : ℤ) + 1 := by ring
      have hmineq := rowMinX_flipMap_image cx' ((ℓ : ℤ) + 1) 0 (heq ▸ hDrowtop1)
      rw [heq, hcx'def, sub_self] at hmineq
      have hmem := rowMinX_mem (S := D.image (flipMap cx' ((ℓ : ℤ) + 1))) (y := (0 : ℤ))
        (by rw [rowSize_flipMap_image, heq]; exact hDrowtop1)
      rwa [hmineq] at hmem
    · intro p hp
      rw [Finset.mem_image] at hp
      obtain ⟨q, hqD, rfl⟩ := hp
      obtain ⟨hqy1, hqy2⟩ := hDy q hqD
      have h1 : (flipMap cx' ((ℓ : ℤ) + 1) q).2 = (ℓ : ℤ) + 1 - q.2 := rfl
      rw [h1]
      omega
    · rw [rowSize_flipMap_image]
      have heq : (ℓ : ℤ) + 1 - 0 = (ℓ : ℤ) + 1 := by ring
      rw [heq]; exact hDrowtop
    · intro i hi
      rw [rowSize_flipMap_image]
      rw [Finset.mem_Icc] at hi
      have heq : (ℓ : ℤ) + 1 - (i : ℤ) = ((ℓ + 1 - i : ℕ) : ℤ) := by omega
      rw [heq]
      have := hDrowmid (ℓ + 1 - i) (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
      omega
    · exact kingConnected_image_of_adj_iff (flipMap_injective _ _) (kingAdj_flipMap _ _) hDconn
  · -- left_inv: j (i S') = S'
    intro S' hS'
    rw [mem_CFGVt] at hS'
    obtain ⟨hcard, h0, hy, hrow0, hrowmid, hconn⟩ := hS'
    set cx := rowMinX S' (ℓ : ℤ) with hcxdef
    have hminS'0 : rowMinX S' (0 : ℤ) = 0 := by
      have h1 : rowMinX S' (0 : ℤ) ≤ 0 := rowMinX_le h0 rfl
      have h3 := rowMinX_mem (S := S') (y := (0 : ℤ)) (by omega)
      have hmem1 : (rowMinX S' (0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
        Finset.mem_filter.mpr ⟨h3, rfl⟩
      have hmem2 : ((0 : ℤ), (0 : ℤ)) ∈ S'.filter (fun c => c.2 = 0) :=
        Finset.mem_filter.mpr ⟨h0, rfl⟩
      have heq := Finset.card_le_one.mp (le_of_eq hrow0) _ hmem1 _ hmem2
      have := congrArg Prod.fst heq
      simpa using this
    set cx2 := rowMinX (S'.image (flipMap cx ((ℓ : ℤ) + 1))) ((ℓ : ℤ) + 1) with hcx2def
    have hcx2eq : cx2 = -cx := by
      have heq : (ℓ : ℤ) + 1 - ((ℓ : ℤ) + 1) = 0 := by ring
      have hrsize : 1 ≤ rowSize S' (0 : ℤ) := by omega
      have hmineq := rowMinX_flipMap_image cx ((ℓ : ℤ) + 1) ((ℓ : ℤ) + 1) (heq ▸ hrsize)
      rw [heq, hminS'0] at hmineq
      rw [hcx2def, hmineq]; ring
    have hcomp : ∀ r : ℤ × ℤ, flipMap cx2 ((ℓ : ℤ) + 1) (flipMap cx ((ℓ : ℤ) + 1) r) = r := by
      intro r
      rw [flipMap_flipMap, hcx2eq]
      have heq : r.1 - cx - -cx = r.1 := by ring
      rw [heq]
    change (S'.image (flipMap cx ((ℓ : ℤ) + 1))).image (flipMap cx2 ((ℓ : ℤ) + 1)) = S'
    rw [Finset.image_image]
    apply Finset.ext
    intro p
    rw [Finset.mem_image]
    constructor
    · rintro ⟨r, hr, heq⟩
      have : flipMap cx2 ((ℓ : ℤ) + 1) (flipMap cx ((ℓ : ℤ) + 1) r) = p := heq
      rw [hcomp r] at this
      rwa [← this]
    · intro hp
      exact ⟨p, hp, hcomp p⟩
  · -- right_inv: i (j D) = D
    intro D hD
    rw [mem_BQ hℓ] at hD
    obtain ⟨hDcard, hD01, hDy, hDx0, hDrowtop, hDrowmid, hDconn⟩ := hD
    set cx' := rowMinX D ((ℓ : ℤ) + 1) with hcx'def
    have hDrow1_2 : rowSize D (1 : ℤ) = 2 := hDrowmid 1 (Finset.mem_Icc.mpr ⟨le_refl 1, hℓ⟩)
    have hminD1 : rowMinX D (1 : ℤ) = 0 := by
      have h1 : rowMinX D (1 : ℤ) ≤ 0 := rowMinX_le hD01 rfl
      have h3 := rowMinX_mem (S := D) (y := (1 : ℤ)) (by omega)
      have h2 : 0 ≤ rowMinX D (1 : ℤ) := hDx0 _ h3 rfl
      omega
    set cx'' := rowMinX (D.image (flipMap cx' ((ℓ : ℤ) + 1))) (ℓ : ℤ) with hcx''def
    have hcx''eq : cx'' = -cx' := by
      have heq : (ℓ : ℤ) + 1 - (ℓ : ℤ) = 1 := by ring
      have hrsize : 1 ≤ rowSize D (1 : ℤ) := by omega
      have hmineq := rowMinX_flipMap_image cx' ((ℓ : ℤ) + 1) (ℓ : ℤ) (heq ▸ hrsize)
      rw [heq, hminD1] at hmineq
      rw [hcx''def, hmineq]; ring
    have hcomp : ∀ r : ℤ × ℤ, flipMap cx'' ((ℓ : ℤ) + 1) (flipMap cx' ((ℓ : ℤ) + 1) r) = r := by
      intro r
      rw [flipMap_flipMap, hcx''eq]
      have heq : r.1 - cx' - -cx' = r.1 := by ring
      rw [heq]
    change (D.image (flipMap cx' ((ℓ : ℤ) + 1))).image (flipMap cx'' ((ℓ : ℤ) + 1)) = D
    rw [Finset.image_image]
    apply Finset.ext
    intro p
    rw [Finset.mem_image]
    constructor
    · rintro ⟨r, hr, heq⟩
      have : flipMap cx'' ((ℓ : ℤ) + 1) (flipMap cx' ((ℓ : ℤ) + 1) r) = p := heq
      rw [hcomp r] at this
      rwa [← this]
    · intro hp
      exact ⟨p, hp, hcomp p⟩

/-- **Bottom-edge assembly**, the composite the walk emits. -/
theorem Vt_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    Vt ℓ ℓ = qEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  rw [Vt_eq_BQ_card ℓ hℓ, BQ_card_eq_qEndF ℓ hℓ B hB]

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms
(kernel `decide` on the concrete small gaps is fine). -/

/--
info: 'Polyplets.V_eq_qEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms V_eq_qEndF

/--
info: 'Polyplets.Vt_eq_qEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Vt_eq_qEndF

/--
info: 'Polyplets.Vp_eq_bareEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Vp_eq_bareEndF

end Polyplets
