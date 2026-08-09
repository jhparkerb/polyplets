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
  sorry

/-- Bare iterates are bare stack counts inside the cone. -/
theorem iter_eq_STKB (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    (∀ g, 1 ≤ g → g ≤ 2 * l + 2 →
      iter M bareCount l (g, true) = (STKB (l + 1) g true).card) ∧
    (∀ g, 1 ≤ g → g + 2 * l ≤ M →
      iter M bareCount l (g, false) = (STKB (l + 1) g false).card) := by
  sorry

/-! ## The emissions -/

/-- The interior emission at level `l` is the interior configuration
count: `qEndF_congr` from the invariant (both sides vanish on `J`-gaps
above `2l + 2`), then `V_eq_qEndF` at `B := M`. -/
theorem qEndF_iter_eq_V (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    qEndF M (iter M startCount l) = V (l + 1) (l + 1) := by
  sorry

/-- The bare emission is the top-edge configuration count. -/
theorem qEndF_iter_eq_Vt (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    qEndF M (iter M bareCount l) = Vt (l + 1) (l + 1) := by
  sorry

/-- The bare closing emission is the pure configuration count. -/
theorem bareEndF_iter_eq_Vp (M l : ℕ) (hM : 2 * l + 4 ≤ M) :
    bareEndF M (iter M bareCount l) = Vp (l + 1) (l + 1) := by
  sorry

/-! ## The head -/

/-- **The bijection.** The gap walk emits the configuration counts: every
family triple of `walkFamilies` is `(V ℓ ℓ, Vt ℓ ℓ, Vp ℓ ℓ)`. Rewrite
through `startInterior_eq`/`startBare_eq` and `walkAux_canon` as in
`walkFamiliesCap_exact`, then apply the three emission lemmas pointwise
(`l < L` gives `2l + 4 ≤ 2L + 2 ≤ 2L + 3 = M`). -/
theorem walkFamilies_configs (L : ℕ) :
    walkFamilies L = (List.range L).map fun l =>
      (V (l + 1) (l + 1), Vt (l + 1) (l + 1), Vp (l + 1) (l + 1)) := by
  sorry

/-! ## New enumeration values, from the walk

`walk_table` + the head identity evaluate the configuration counts at
`ℓ = 4, 5, 6` — outside enumeration reach (the `ℓ ≤ 3` values took
`native_decide` over ~10⁵-pair windows; these need none). Extract entry
`ℓ − 1` of the two list forms (`List.range` reduces by `decide`/`simp
[List.range_succ]`; then `List.cons.injEq`/`Prod.mk.injEq`). -/

theorem V_4_4 : V 4 4 = 68314 := by
  sorry

theorem V_5_5 : V 5 5 = 981085 := by
  sorry

theorem V_6_6 : V 6 6 = 14115141 := by
  sorry

theorem Vt_4_4 : Vt 4 4 = 13103 := by
  sorry

theorem Vt_5_5 : Vt 5 5 = 187965 := by
  sorry

theorem Vt_6_6 : Vt 6 6 = 2703074 := by
  sorry

theorem Vp_4_4 : Vp 4 4 = 2515 := by
  sorry

theorem Vp_5_5 : Vp 5 5 = 36021 := by
  sorry

theorem Vp_6_6 : Vp 6 6 = 517701 := by
  sorry

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
