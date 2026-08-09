/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkPeel
import Polyplets.GapWalkEnds
import Polyplets.GapWalkTrunc

/-!
# Notary piece B, module 4: the bijection, assembled

Campaign *Notary*, piece **B**, head theorem. The walk's iterates *are* the
stack counts inside the truncation cone (the same cone `GapWalkTrunc.lean`
established for cap comparison), so the emitted family triples are the
configuration counts of `Weights.lean` / `GapWalkBridge.lean`:

    walkFamilies L = [(V 1 1, Vt 1 1, Vp 1 1), …, (V L L, Vt L L, Vp L L)]

(`walkFamilies_configs`). This closes `GapWalk.lean`'s stated open item:
the walk's numbers now *mean* clusters at every level, unconditionally —
previously proved only at `ℓ ≤ 3` by finite enumeration
(`GapWalkBridge.lean`). With `walk_table` the identity turns enumeration
into computation: `V`/`Vt`/`Vp` at `ℓ = 4, 5, 6` — far beyond
`native_decide` enumeration reach — become theorems with literal values.

## The cone induction (`iter_eq_STKI`/`iter_eq_STKB`)

Induct on `l` with invariant, at cap `M ≥ 2l + 4`:

* `J`-values agree at every gap `g ≤ 2l + 2`;
* `P`-values agree in the cone `g + 2l ≤ M`.

Base: `iter M start 0 = start` and the one-row stack counts
(`STKI_one_card` / `STKB_one_card`). Step: rewrite the target's stack
count by the peel recursion `STK*_card_step` at cap `B := M` (its
hypotheses `2i ≤ M`, `g' + 2 ≤ M` hold inside the ranges above — this is
where `M ≥ 2(l+1) + 4` is exactly enough), then `funStep_congr` matches
sources: `J`-sources at `gs ≤ 2l + 2` by IH, higher `J`-sources are zero
on both sides (`iter_J_support` with `startCount_J_high`/
`bareCount_J_high`; `STKI_card_J_high`/`STKB_card_J_high`); `P`-sources in
the cone by IH, outside the cone their multiplicities vanish
(`stepMul_P_far_to_J` onto `J`-targets, `stepMul_P_local` onto the
`P`-targets in question). Mirror the step of `GapWalkTrunc.iter_agree`
line by line — same case split, same vanishing lemmas.

At emission `l` the ends read `J` everywhere (`qEndF_congr` needs all
`g ≤ M`: inside `g ≤ 2l + 2` the invariant, above it both sides zero) and
`P` only at `g ≤ 2` (inside the cone since `2 + 2l ≤ M`); then
`V_eq_qEndF` / `Vt_eq_qEndF` / `Vp_eq_bareEndF` at `B := M` convert the
stack-count ends into configuration counts.

Pre-verified numerically (`verify_bij_statements.py`, checks H/J: the
invariant at the edge cap `M = 2l + 4`, heads to `L = 5`).
-/

namespace Polyplets

open GapWalk
open GapWalkBridge (Vp)

/-! ## The cone induction -/

/-- Interior iterates are interior stack counts inside the cone. -/
theorem iter_eq_STKI (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    (∀ g, 1 ≤ g → g ≤ 2 * l + 2 →
      iter M startCount l (g, true) = (STKI (l + 1) g true).card) ∧
    (∀ g, 1 ≤ g → g + 2 * l ≤ M →
      iter M startCount l (g, false) = (STKI (l + 1) g false).card) := by
  induction l with
  | zero =>
      refine ⟨fun g hg _ => ?_, fun g hg _ => ?_⟩
      · exact (STKI_one_card g hg true).symm
      · exact (STKI_one_card g hg false).symm
  | succ l ih =>
      have hM' : 2 * l + 4 ≤ M := by omega
      obtain ⟨ihJ, ihP⟩ := ih hM'
      have hJstart : ∀ g, 3 ≤ g → startCount (g, true) = 0 := startCount_J_high
      refine ⟨fun g hg1 hg2 => ?_, fun g hg1 hg2 => ?_⟩
      · -- J target
        have step := STKI_card_step (l + 1) (by omega) g hg1 true M (by omega) (by omega)
        rw [step]
        change funStep M (iter M startCount l) (g, true) = _
        apply funStep_congr
        intro gs cs h1 h2
        cases cs with
        | true =>
            by_cases hcone : gs ≤ 2 * l + 2
            · exact Or.inl (ihJ gs h1 hcone)
            · have hlhs : iter M startCount l (gs, true) = 0 :=
                iter_J_support M startCount hJstart l gs (by omega)
              have hrhs : (STKI (l + 1) gs true).card = 0 :=
                STKI_card_J_high (l + 1) gs (by omega) (by omega)
              exact Or.inl (by rw [hlhs, hrhs])
        | false =>
            by_cases hcone : gs + 2 * l ≤ M
            · exact Or.inl (ihP gs h1 hcone)
            · exact Or.inr (stepMul_P_far_to_J gs g (by omega))
      · -- P target
        have step := STKI_card_step (l + 1) (by omega) g hg1 false M (by omega) (by omega)
        rw [step]
        change funStep M (iter M startCount l) (g, false) = _
        apply funStep_congr
        intro gs cs h1 h2
        cases cs with
        | true =>
            by_cases hcone : gs ≤ 2 * l + 2
            · exact Or.inl (ihJ gs h1 hcone)
            · have hlhs : iter M startCount l (gs, true) = 0 :=
                iter_J_support M startCount hJstart l gs (by omega)
              have hrhs : (STKI (l + 1) gs true).card = 0 :=
                STKI_card_J_high (l + 1) gs (by omega) (by omega)
              exact Or.inl (by rw [hlhs, hrhs])
        | false =>
            by_cases hcone : gs + 2 * l ≤ M
            · exact Or.inl (ihP gs h1 hcone)
            · exact Or.inr (stepMul_P_local gs g false (by omega) (Or.inl (by omega)))

/-- Bare iterates are bare stack counts inside the cone. -/
theorem iter_eq_STKB (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    (∀ g, 1 ≤ g → g ≤ 2 * l + 2 →
      iter M bareCount l (g, true) = (STKB (l + 1) g true).card) ∧
    (∀ g, 1 ≤ g → g + 2 * l ≤ M →
      iter M bareCount l (g, false) = (STKB (l + 1) g false).card) := by
  induction l with
  | zero =>
      refine ⟨fun g hg _ => ?_, fun g hg _ => ?_⟩
      · exact (STKB_one_card g hg true).symm
      · exact (STKB_one_card g hg false).symm
  | succ l ih =>
      have hM' : 2 * l + 4 ≤ M := by omega
      obtain ⟨ihJ, ihP⟩ := ih hM'
      have hJstart : ∀ g, 3 ≤ g → bareCount (g, true) = 0 :=
        fun g hg => bareCount_J_high g (by omega)
      refine ⟨fun g hg1 hg2 => ?_, fun g hg1 hg2 => ?_⟩
      · -- J target
        have step := STKB_card_step (l + 1) (by omega) g hg1 true M (by omega) (by omega)
        rw [step]
        change funStep M (iter M bareCount l) (g, true) = _
        apply funStep_congr
        intro gs cs h1 h2
        cases cs with
        | true =>
            by_cases hcone : gs ≤ 2 * l + 2
            · exact Or.inl (ihJ gs h1 hcone)
            · have hlhs : iter M bareCount l (gs, true) = 0 :=
                iter_J_support M bareCount hJstart l gs (by omega)
              have hrhs : (STKB (l + 1) gs true).card = 0 :=
                STKB_card_J_high (l + 1) gs (by omega) (by omega)
              exact Or.inl (by rw [hlhs, hrhs])
        | false =>
            by_cases hcone : gs + 2 * l ≤ M
            · exact Or.inl (ihP gs h1 hcone)
            · exact Or.inr (stepMul_P_far_to_J gs g (by omega))
      · -- P target
        have step := STKB_card_step (l + 1) (by omega) g hg1 false M (by omega) (by omega)
        rw [step]
        change funStep M (iter M bareCount l) (g, false) = _
        apply funStep_congr
        intro gs cs h1 h2
        cases cs with
        | true =>
            by_cases hcone : gs ≤ 2 * l + 2
            · exact Or.inl (ihJ gs h1 hcone)
            · have hlhs : iter M bareCount l (gs, true) = 0 :=
                iter_J_support M bareCount hJstart l gs (by omega)
              have hrhs : (STKB (l + 1) gs true).card = 0 :=
                STKB_card_J_high (l + 1) gs (by omega) (by omega)
              exact Or.inl (by rw [hlhs, hrhs])
        | false =>
            by_cases hcone : gs + 2 * l ≤ M
            · exact Or.inl (ihP gs h1 hcone)
            · exact Or.inr (stepMul_P_local gs g false (by omega) (Or.inl (by omega)))

/-! ## The emissions -/

/-- The interior emission at level `l` is the interior configuration
count: `qEndF_congr` from the invariant (both sides vanish on `J`-gaps
above `2l + 2`), then `V_eq_qEndF` at `B := M`. -/
theorem qEndF_iter_eq_V (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    qEndF M (iter M startCount l) = V (l + 1) (l + 1) := by
  obtain ⟨ihJ, ihP⟩ := iter_eq_STKI M l hM
  rw [V_eq_qEndF (l + 1) (by omega) M hM]
  apply qEndF_congr
  · intro g hg1 hg2
    by_cases hcone : g ≤ 2 * l + 2
    · exact ihJ g hg1 hcone
    · have hlhs : iter M startCount l (g, true) = 0 :=
        iter_J_support M startCount startCount_J_high l g (by omega)
      have hrhs : (STKI (l + 1) g true).card = 0 :=
        STKI_card_J_high (l + 1) g (by omega) (by omega)
      rw [hlhs, hrhs]
  · intro g hg1 hg2
    exact ihP g hg1 (by omega)

/-- The bare emission is the top-edge configuration count. -/
theorem qEndF_iter_eq_Vt (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    qEndF M (iter M bareCount l) = Vt (l + 1) (l + 1) := by
  obtain ⟨ihJ, ihP⟩ := iter_eq_STKB M l hM
  rw [Vt_eq_qEndF (l + 1) (by omega) M hM]
  apply qEndF_congr
  · intro g hg1 hg2
    by_cases hcone : g ≤ 2 * l + 2
    · exact ihJ g hg1 hcone
    · have hlhs : iter M bareCount l (g, true) = 0 :=
        iter_J_support M bareCount (fun g hg => bareCount_J_high g (by omega)) l g (by omega)
      have hrhs : (STKB (l + 1) g true).card = 0 :=
        STKB_card_J_high (l + 1) g (by omega) (by omega)
      rw [hlhs, hrhs]
  · intro g hg1 hg2
    exact ihP g hg1 (by omega)

/-- The bare closing emission is the pure configuration count. -/
theorem bareEndF_iter_eq_Vp (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    bareEndF M (iter M bareCount l) = Vp (l + 1) (l + 1) := by
  obtain ⟨ihJ, ihP⟩ := iter_eq_STKB M l hM
  rw [Vp_eq_bareEndF (l + 1) (by omega) M (by omega)]
  apply bareEndF_congr
  intro g hg1 hg2
  by_cases hcone : g ≤ 2 * l + 2
  · exact ihJ g hg1 hcone
  · have hlhs : iter M bareCount l (g, true) = 0 :=
      iter_J_support M bareCount (fun g hg => bareCount_J_high g (by omega)) l g (by omega)
    have hrhs : (STKB (l + 1) g true).card = 0 :=
      STKB_card_J_high (l + 1) g (by omega) (by omega)
    rw [hlhs, hrhs]

/-! ## The head -/

/-- **The bijection.** The gap walk emits the configuration counts: every
family triple of `walkFamilies` is `(V ℓ ℓ, Vt ℓ ℓ, Vp ℓ ℓ)`. Rewrite
through `startInterior_eq`/`startBare_eq` and `walkAux_canon` as in
`walkFamiliesCap_exact`, then apply the three emission lemmas pointwise
(`l < L` gives `2l + 4 ≤ 2L + 2 ≤ 2L + 3 = M`). -/
theorem walkFamilies_configs (L : ℕ) :
    walkFamilies L = (List.range L).map fun l =>
      (V (l + 1) (l + 1), Vt (l + 1) (l + 1), Vp (l + 1) (l + 1)) := by
  unfold walkFamilies
  rw [startInterior_eq, startBare_eq]
  change walkAux L (2 * L + 3) (canon (2 * L + 3) startCount) (canon (2 * L + 3) bareCount) = _
  rw [walkAux_canon]
  apply List.map_congr_left
  intro l hl
  have hlL : l < L := List.mem_range.mp hl
  have hM : 2 * l + 4 ≤ 2 * L + 3 := by omega
  rw [qEndF_iter_eq_V (2 * L + 3) l hM, qEndF_iter_eq_Vt (2 * L + 3) l hM,
      bareEndF_iter_eq_Vp (2 * L + 3) l hM]

/-! ## New enumeration values, from the walk

`walk_table` + the head identity evaluate the configuration counts at
`ℓ = 4, 5, 6` — outside enumeration reach (the `ℓ ≤ 3` values took
`native_decide` over ~10⁵-pair windows; these need none). Extract entry
`ℓ − 1` of the two list forms (`List.range` reduces by `decide`/`simp
[List.range_succ]`; then `List.cons.injEq`/`Prod.mk.injEq`). -/

/-- The evaluated table, at `L = 6`, in list form (`walk_table` plus the
head identity). -/
private theorem configs6 :
    (List.range 6).map (fun l =>
        (V (l + 1) (l + 1), Vt (l + 1) (l + 1), Vp (l + 1) (l + 1))) =
      [(25, 5, 1), (339, 66, 13), (4778, 919, 177), (68314, 13103, 2515),
        (981085, 187965, 36021), (14115141, 2703074, 517701)] := by
  rw [← walkFamilies_configs 6, walk_table]

set_option maxRecDepth 100000 in
/-- The six entries of `configs6`, extracted componentwise. -/
private theorem configs6_split :
    V 4 4 = 68314 ∧ Vt 4 4 = 13103 ∧ Vp 4 4 = 2515 ∧
    V 5 5 = 981085 ∧ Vt 5 5 = 187965 ∧ Vp 5 5 = 36021 ∧
    V 6 6 = 14115141 ∧ Vt 6 6 = 2703074 ∧ Vp 6 6 = 517701 := by
  have h := configs6
  have hr : List.range 6 = [0, 1, 2, 3, 4, 5] := by decide
  rw [hr] at h
  simp only [List.map_cons, List.map_nil] at h
  norm_num at h
  exact ⟨h.2.2.2.1.1, h.2.2.2.1.2.1, h.2.2.2.1.2.2,
    h.2.2.2.2.1.1, h.2.2.2.2.1.2.1, h.2.2.2.2.1.2.2,
    h.2.2.2.2.2.1, h.2.2.2.2.2.2.1, h.2.2.2.2.2.2.2⟩

theorem V_4_4 : V 4 4 = 68314 := configs6_split.1

theorem V_5_5 : V 5 5 = 981085 := configs6_split.2.2.2.1

theorem V_6_6 : V 6 6 = 14115141 := configs6_split.2.2.2.2.2.2.1

theorem Vt_4_4 : Vt 4 4 = 13103 := configs6_split.2.1

theorem Vt_5_5 : Vt 5 5 = 187965 := configs6_split.2.2.2.2.1

theorem Vt_6_6 : Vt 6 6 = 2703074 := configs6_split.2.2.2.2.2.2.2.1

theorem Vp_4_4 : Vp 4 4 = 2515 := configs6_split.2.2.1

theorem Vp_5_5 : Vp 5 5 = 36021 := configs6_split.2.2.2.2.2.1

theorem Vp_6_6 : Vp 6 6 = 517701 := configs6_split.2.2.2.2.2.2.2.2

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only — in particular the head and the new
values must NOT pick up `Lean.ofReduceBool`; `native_decide` is out of
bounds in this module, as is declaring new axioms. If a finished proof
uses strictly fewer axioms, tighten the `info` string. -/

/--
info: 'Polyplets.walkFamilies_configs' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms walkFamilies_configs

/--
info: 'Polyplets.V_6_6' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms V_6_6

/--
info: 'Polyplets.Vp_6_6' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Vp_6_6

end Polyplets
