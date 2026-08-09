/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkRows
import Polyplets.GapWalkCanon

/-!
# Notary piece T, module 3: truncation exactness of the gap walk

Campaign *Notary*, piece **T** of `docs/notary-kernel-scoping.md`, closing
the truncation half of `GapWalk.lean`'s stated open item. Head theorem:

    walkFamiliesCap M L = walkFamilies L    for every M ≥ 2L + 3,

i.e. the gap cap `gmax = 2L + 3` hard-wired into `walkFamilies` is exact:
*every* larger cap emits the same family triples, so the untruncated walk —
the common value of all sufficiently large caps — is what `walkFamilies`
computes. Numerically pre-verified for `L ≤ 5`, caps up to `2L + 10`.

## The argument (cone induction)

Compare caps `M ≤ M'` on the same start `F` (the starts are cap-independent
by `startInterior_eq` / `startBare_eq`). Two invariants over `l` steps:

* **J-support** (`iter_J_support`): all `J`-mass lives at gaps `≤ 2 + 2l`.
  Start support is `≤ 2` (`startCount_J_high`, `bareCount_J_high`); a `J`
  target at gap `≥ 3` needs a `J` source within two below
  (`stepMul_J_to_J_far`) or a `P` source, which cannot reach it
  (`stepMul_P_to_J`).
* **Cone agreement** (`iter_agree`), for `2l + 5 ≤ M`: the two walks agree
  on *all* `J`-values, and on `P`-values at gaps `g` with `g + 2l ≤ M`.
  The cap only ever corrupts `P`-mass near it, and that corruption moves
  down at most 2 gaps per step (`stepMul_P_local`), never reconverting to
  `J` (`stepMul_P_far_to_J`); the end functionals read `P` only at
  `g ≤ 2` and `J` only inside the support, both deep inside the cone.

With `M = 2L + 3` the cone condition at the last emission (`l = L − 1`)
is `2(L−1) + 5 = 2L + 3 ≤ M`, exactly the walk's own cap — the bound in
`walkFamilies` is the tight edge of this argument.

## Proof sketches

`iter_J_support`: induction on `l`. Step, at target `(g, true)` with
`g > 2 + 2(l+1) ≥ 4`: kill the `funStep` sum term by term
(`List.sum_eq_zero`, membership via `mem_states`): `P` sources by
`stepMul_P_to_J` (`3 ≤ g`); `J` sources at `gs` with `gs + 2 < g` by
`stepMul_J_to_J_far`, the rest by the inductive hypothesis
(`2 + 2l < gs`, value zero, term zero).

`iter_agree`: induction on `l`; base is `rfl`. Step, with
`2l + 7 ≤ M ≤ M'` and both IH parts available at `l`:

* J-part, any target `(g, true)`: first
  `funStep M' (iter M' F l) = funStep M (iter M' F l)` at this target via
  `funStep_split_zero` (`M' = M + k`): extra `J` sources die by
  `iter_J_support` (`gs ≥ M + 1 > 2 + 2l`), extra `P` sources by
  `stepMul_P_far_to_J` (`gs ≥ M + 1 ≥ 4`). Then `funStep_congr` at cap
  `M`: `J` sources agree by IH-J; a `P` source either satisfies
  `gs + 2l ≤ M` (IH-P) or has `gs > M − 2l ≥ 7 ≥ 4`, so its multiplicity
  onto a `J` target vanishes (`stepMul_P_far_to_J`).
* P-part, target `(g, false)` with `g + 2(l+1) ≤ M`: same two moves; extra
  and far `P` sources now die by `stepMul_P_local` (`g + 2 < gs`, since
  `gs > M − 2l ≥ g + 2`), extra `J` sources by `iter_J_support`, near `P`
  sources agree by IH-P (`gs ≤ g + 2 ⇒ gs + 2l ≤ M`), `J` sources by IH-J.

`walkFamiliesCap_exact`: rewrite both sides through `startInterior_eq`,
`startBare_eq`, `canon`, `walkAux_canon`; equate the `List.range L` maps
pointwise. At emission `l ≤ L − 1`: `qEndF M = qEndF (2L+3)` on the bigger
iterate by `qEndF_split_zero` (support: `2 + 2l ≤ 2L < 2L + 4`), then
`qEndF_congr` via `iter_agree` (`2l + 5 ≤ 2L + 3`, `P` read only at
`g ≤ 2`, `g + 2l ≤ 2L + 2 ≤ 2L + 3`); `bareEndF` likewise.
-/

namespace Polyplets
namespace GapWalk

/-- The walk of `walkFamilies L` run at an arbitrary gap cap `M`. -/
def walkFamiliesCap (M L : Nat) : List (Nat × Nat × Nat) :=
  walkAux L M (startInterior M) (startBare M)

theorem walkFamiliesCap_self (L : Nat) :
    walkFamiliesCap (2 * L + 3) L = walkFamilies L := rfl

/-- All `J`-mass sits at gaps `≤ 2 + 2l` after `l` steps, at any cap, from
any start whose `J`-support lies below gap 3. -/
theorem iter_J_support (cap : Nat) (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) :
    ∀ l g, 2 + 2 * l < g → iter cap F l (g, true) = 0 := by
  sorry

/-- The cone invariant: walks at caps `M ≤ M'` from a common low-`J` start
agree on every `J`-value, and on `P`-values in the cone `g + 2l ≤ M`. -/
theorem iter_agree (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (M M' : Nat) (hMM' : M ≤ M') :
    ∀ l, 2 * l + 5 ≤ M →
      (∀ g, iter M F l (g, true) = iter M' F l (g, true)) ∧
      (∀ g, g + 2 * l ≤ M → iter M F l (g, false) = iter M' F l (g, false)) := by
  sorry

/-- **Truncation exactness.** Every cap `M ≥ 2L + 3` emits the family
triples of `walkFamilies L`: the truncation of the gap walk is invisible
to the emitted weights, so the untruncated walk is what `walkFamilies`
computes. -/
theorem walkFamiliesCap_exact (L M : Nat) (h : 2 * L + 3 ≤ M) :
    walkFamiliesCap M L = walkFamilies L := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.walkFamiliesCap_exact' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
-/
#guard_msgs in
#print axioms walkFamiliesCap_exact

end GapWalk
end Polyplets
