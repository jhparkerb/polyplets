# Notary piece K — handoff (post-/clear reference)

**Status: piece K FULLY CLOSED 2026-08-10, up to the piece-D bridge.**
Commit `361143f` (and `dd256ec`, `d1be68f` before it). NOT pushed.

## What is done

- `Polyplets/DepthOneKernelPhi.lean` — `phi_annihilates_exact : Φ(x, N(x)) = 0`,
  exact in `ℚ⟦x⟧` at **all orders**, kernel-verified, **no `native_decide`**.
  The exact upgrade of the old mod-`x^61` `DepthOneSeries.phi_annihilates`.
  Proved via two machine-generated `linear_combination` certificates
  (26k `quartic_tuple` + 41k `quartic_cleared`) over the two √-square
  relations `A_sq`/`B_sq`; the `x↦3x` lift is coefficient-level; `phiF1_even`
  via a from-scratch `X↦−X` automorphism swapping `A↔B`.
- Wired: `polyplets/Polyplets.lean` import, Makefile `NOTARY_MODULES` +
  `gate-notary` lake line. `#guard_msgs` axiom audits on
  `phi_annihilates_exact` and `phi_annihilates_of_exact` — both on the
  standard three (`propext, Classical.choice, Quot.sound`) only.
- Gates: `make gate-notary` → `GATE-EXIT:0`; full `make` → `MAKE-EXIT:0`,
  every RED control fired.
- Docs: `results/notary-depth1-lean.md` (wave-K section),
  `docs/notary-kernel-scoping.md` (K DONE + verdict), `docs/notary-k-plan.md`
  (execution status). This file.

## The one boundary — piece D

`phi_annihilates_of_exact` re-derives the value pin `DepthOneSeries.phi_annihilates`
**without** `native_decide`, but conditional on an explicit hypothesis:

```
hbridge : KernelSeries.truncL 61 Nexact = DepthOneSeries.nSeries 60
```

That the kernel closed form `Nexact` **is** the walk's own `walkFamilies`
enumeration at all orders = identity (II) = **piece D**. It is NOT provable
inside K (existing walkFamilies↔value links are `native_decide`-only:
`f1_matches_depth1` k≤8, `walk_table_19` k≤19; no all-orders symbolic
version). Piece D is blocked behind `Diagonal.lean`'s general-`k`
factorization lemma and launches only on its own explicit agreement.
Closing D discharges `hbridge` and ties the exact Φ-annihilation back to
the triangle.

## Authority / entry points

- `docs/notary-k-plan.md` — THE plan and execution status for K.
- `docs/notary-kernel-scoping.md` — the K/B/D/T decomposition and pricing.
- memory `notary-campaign.md` — campaign-wide state.

## Constraints (standing)

Do NOT push (publishing is jasonp's call). Do NOT mention the OEIS viva.
Standard axioms only; no `native_decide` in K. Long builds go in tmux
(session 0 on gympie, add windows). Build from `polyplets/` with
`~/.elan/bin/lake`.
