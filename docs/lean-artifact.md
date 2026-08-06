# The Lean development as a citable artifact

2026-08-06, sortie plan §2 "Not papers". Papers 2 and 3 carry tier-2 results
whose warrant *is* this development, so it has to be citable, checkable by
someone who did not write it, and honest about where computation enters.

## What it is

`polyplets/` — 65 modules, 21,659 lines, Lean 4 v4.31.0 against mathlib
v4.31.0, **zero occurrences of `sorry`**, 8624 build targets current
(`polyplets/build-receipt-2026-08-06.log`).

One file is deliberately outside that: `polyplets/Draft/Prop6Skeleton.lean`,
which carries five `sorry`s. It is not a library, `lake build` never compiles
it, and nothing in `Polyplets/` imports it. It states the architecture of the
rest of Proposition 6 — every statement typechecks, and each `sorry` is a named
contract whose paper proof and numeric gate are cited beside it in the file's
header. Its `#print axioms` prints `sorryAx`, which is the point: the file
says what it has not proved. A reader auditing the artifact should read that
header first, then `PROOF-STATUS.md`'s staircase section for what *is* proved.

## How a reader checks it

```
cd polyplets
lake build              # from cold: mathlib dominates; the development itself is minutes
lake build --no-build   # verifies everything is built and current, ~6 s
```

Part of the axiom discipline is enforced by the build rather than by a separate
audit run, and the paper should describe it precisely, because the two halves
are not equally strong:

- **88 guarded.** `Grand/Audit.lean` (18) and `AuditOutworks.lean` (70, of
  which the last eight are sortie B1's three and the five staircase-growth
  ones) wrap `#print axioms` in `#guard_msgs`, so a changed footprint is a
  **build error**. A reader who builds the project has checked these without
  being asked to trust a log.
- **148 unguarded.** The modules themselves print footprints on every build,
  but nothing enforces them. They are informational.

## The footprint, stated plainly

- Of the 88 guarded: 55 standard axioms only, 33 with named `native_decide`
  leaves.
- Of the 148 unguarded: 100 standard only, 48 with named leaves.
- A named leaf is one axiom per finite computation, e.g.
  `a_6._native.native_decide.ax_1_1` for a(6) = 3832.
- No `sorryAx`. No anonymous `Lean.ofReduceBool`.

Naming matters here: a named leaf says exactly which computation is being
trusted, so the compiled-evaluation surface is enumerable rather than diffuse.
The papers should say so in that form.

## What each paper cites it for

**Paper 2 — the universal diagonal law.** The engine
(`Universal.universal_shape_d`, `universal_shape`,
`universal_shape_production`, `universal_production_int_all`) and the
`kingSystem` / `peelSystem` instances are **standard-axioms-only**. The
per-lattice instance pins (`king_P1_*`, `square_P1_*`, `hex_P1_*`) and the
cross-family row-sum gates carry named leaves that are two triangle cells per
lattice. `grand_form` and `grand_form_prod` are standard-axioms-only; the
k ≤ 18 production pinning (`P18_grand_of_banked`, `P18_grand_prod`) carries
the chunked weight cards as leaves.

**Paper 3 — Proposition 6's Lemma 3, and `µ`.** `Stair.join_valid`,
`Stair.cut_join` and `Stair.join_injOn` (`Polyplets/StairAnimals.lean`, sortie
B1) formalise the column-join and its inverse: the join stays in the class, and
the cut at cumulative area `i` inverts it, so the map is injective once both
areas are fixed. Guarded, and their footprint is `[propext, Quot.sound]` — not
even `Classical.choice`. Since 2026-08-06 the counting layer and the Fekete
step are there too (`StairGrowth.lean`), so **Lemma 3 itself is a Lean
theorem**: `Stair.M_supermul : M i * M j ≤ M (i + j)` for all `i` and `j`,
standard three axioms, guarded. With it, `Stair.M_tendsto` (`µ` exists) and
`Stair.M_le_mu_pow` (`M n ≤ µⁿ` for every `n`, so banked terms are floors, not
approximations), and the conditional `Stair.mu_gt_of_banked` giving
`3.1234 < µ ≤ 4` from the banked `M 700`.

What Paper 3 must *not* claim from this: Proposition 6. Lemmas 1 and 2, the
geometric HV-convex layer and the squeeze are **not** formalised, so Lean
states the growth constant of the *staircase* class, not the sandwich. Cite
the paper proof for Proposition 6 and this development for Lemma 3.

**Paper 3 — the λ bracket, upper end.** `BuiSystem.certSum_le`,
`lambda_le_of_buiSystem` and `RatCert.lambda_le` are standard-axioms-only; the
concrete certificate `lambda_le_of_bui_rd3` depends on `buiRD3_valid`, a named
leaf that is the certificate's arithmetic validity check. `lambda_lb` /
`lambda_gt` depend on the evaluation of a(6). Fekete's ladder for λ —
`a_supermul`, `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le` — is
standard-axioms-only, and since 2026-08-06 it is literally shared with the
staircase constant: `Fekete.lean` carries the ladder once and `lambda` and `mu`
are two instances of it.

**Paper 1 — the hole section, if it ships.** `maxhole_lower` and
`maxhole_upper` are standard-axioms-only, and `maxhole` is **conditional on the
hypothesis `MoatBound`**. That conditionality is a formalization gap, not a
mathematical one: (II') is proved on paper by the moat-cycle winding argument
(`results/maxhole-proof.md`), and mathlib has no discrete-Jordan material to
carry it. The *multi-hole* reduction the Lean file does not attempt is no
longer open either (`results/maxhole-proof.md` §The union argument, 2026-08-06)
— but formalizing it would mean assuming the grid isoperimetric inequality for
arbitrary finite subsets, a bigger hypothesis than `MoatBound`, so the file
stays as it is.

## What it does not certify

Nothing about the engine, the banked triangle, or the anchor values. Those
enter as explicit hypotheses or as named native leaves; `PROOF-STATUS.md` is
the per-theorem ledger. A paper that cites the development for a(40) itself
would be citing the wrong artifact — a(40)'s warrant is
`docs/paper1-reproducibility.md`, not this.

## Packaging

For an archived release, the citable unit is `polyplets/` at a tagged
revision, plus the build receipt, plus `PROOF-STATUS.md`. Nothing else in the
repo is needed to build or check it. The receipt names host, date, revision,
toolchain, mathlib revision, job count, source size, sorry count and the
axiom-footprint summary, which is what a reviewer needs to reproduce the check
rather than repeat the reasoning.
