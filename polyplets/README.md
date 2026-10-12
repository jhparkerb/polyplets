# polyplets — the Lean development

Lean 4 `v4.31.0` against Mathlib `v4.31.0`, 43 modules, about 15,300 lines,
no `sorry`, no `native_decide`; every theorem the report or an L-paper cites
is on the standard three axioms, guarded in `Audit.lean`. The quality pass
in progress is `OVERHAUL.md`. `Polyplets/Report.lean` states each claim of
`paper/technical-report.tex` as a theorem, in the report's order, and proves
it by reference into the rest of the tree. `Polyplets/Audit.lean` wraps
`#print axioms` of every Report theorem in `#guard_msgs`, so a footprint that
drifts from `[propext, Classical.choice, Quot.sound]` is a build error. This
file is the ledger: what is proved, from what, and how to check it.

Build (gympie, from the repo root): `make lean`. By hand:

```
cd polyplets
~/.elan/bin/lake exe cache get     # once, Mathlib's oleans
~/.elan/bin/lake build             # the development: minutes once Mathlib is cached
~/.elan/bin/lake build --no-build  # verify everything is current, seconds
```

Toolchain paths and lemma-search recipes: `docs/lean-environment.md`.

## The report's claims

Every row is a theorem on the standard three axioms. "Hypothesis" is what
the theorem takes as input rather than proves.

| report claim | `Report.lean` | proved by | hypothesis |
|---|---|---|---|
| a(n) = Σ_H T(n,H) | `report_a_eq_sum` | `a_eq_sum` (`Sequence`) | — |
| T(n,n) = 3^(n−1) | `report_T_diag` | `T_diag_pow` (`King`) | — |
| diagonal law: for H > n/2, T(n,H) = P_{n−H}(n)·3^(3H−2n−1), P_k integer-valued, deg ≤ k | `report_diagonal_law` | `shape_production`, `production_int_all` (`King`) | — |
| leading coefficient of P_k is 25^k/k! | `report_leading_coeff` | `production_leadingCoeff` (`LeadingCoeff`) | — |
| P_k is fixed once row 3k is computed | `report_pin_row_3k` | `pin_of_leadingCoeff` (`LeadingCoeff`) | — |
| T(n,n−1) = (25n−45)·3^(n−4) | `report_T_n_nm1` | `P1_closed` (`Pin`), from the kernel-decided cells T(3,2) = 10, T(4,3) = 55 | — |
| T(n,n−2) = ½(625n²−2459n+1134)·3^(n−7) | — (not a report claim; `docs/proofs/T-n-nm2-and-general.md`) | `P2_closed` (`Grand/PinAll`), the climb to level 2 from the kernel-decided cells T(3,2), T(4,3), T(5,3) = 248, T(6,4) = 1480 | — |
| P_k explicitly known for k ≤ 18 | `report_Pk_known` | `Pk_prod`, `grand_all` (`Grand/PinAll`), climbing level by level from `d_mu_rec` and `T_staircase` | `BankedAnchors`: 36 cells, below |
| 8·free = a + 2R90 + R180 + 2Hm + 2Dm (Burnside) | `report_free` | `free_eq` (`Symmetry`) | — |
| 4·one-sided = a + 2R90 + R180 | `report_oneSided` | `oneSided_eq` (`Symmetry`) | — |
| 2·bilateral = Hm + Dm | `report_bilateral` | `bilateral_eq` (`Symmetry`) | — |
| a(n)^(1/n) → λ | `report_growth` | `lambda_tendsto` (`Growth`, `Fekete`, `UpperBound`) | — |
| one-sided → a(n)/4, free → a(n)/8 | `report_symmetryRatio` | `symmetryRatio` (`SymmetryRatio`): each symmetric count is o(a(n)), by encoding a symmetric animal as a connected half of about n/2 cells and comparing with `a_supermul` against the kernel-decided a(3) = 20 | — |

Out of scope by design: the computed tables (a(n), T(n,H) beyond the small
cells, the symmetry-class and hole counts) and the value λ ≈ 7.11. Those are
enumeration output. Lean certifies nothing about the engine; the engine's
numbers enter only as the hypothesis below.

### The 36 hypothesis cells

`BankedAnchors` (`Grand/PinAll.lean`) is, for each level k = 1 … 18, the two
cells A_k = T(2k+1, k+1) and B_k = T(2k+2, k+2), at and one above the onset
of level k, with the values the engine enumerated (`results/triangle.txt`).
Every one has H ≤ 20, so every one was really swept, none was generated from
a P_k. Provenance by second source:

- levels 1 … 12 and A_13, 25 cells: confirmed by the independent strip
  transfer matrix (H ≤ 14, n ≤ 36; `results/second-sources.md`), and the row
  totals through n = 22 by a second enumeration (Redelmeier);
- the 11 cells beyond strip reach, kink engine only, re-run across machines
  and revisions but never by a second algorithm:
  T(28,15) T(29,15) T(30,16) T(31,16) T(32,17) T(33,17) T(34,18) T(35,18)
  T(36,19) T(37,19) T(38,20).

Level 19 is deliberately not pinned: its two anchors are the top cells of
the enumeration, no holdout exists, and no banked term uses it.

## How the proof goes

Definitions (`Defs.lean`): a fixed polyplet is a finite set of cells of ℤ²,
king-connected, anchored with min x = min y = 0; `T n H` is the number with
n cells and max y = H − 1, `a n` the row sum (`Sequence.lean`). `Finite.lean` bounds the width so these are finite;
`Compute.lean` gives the computable twin `Tc` and `Tc_eq_T`, which is how the
small cells are decided by the kernel.

The peeling recursion (`Universal/Separation`, `Universal/Weights`,
`Universal/Peel`, proved for every row-local lattice; `King.lean` reads the
king instance off it, `Weights.lean` keeps the king weights as computable
enumerations for the kernel). Write surplus
k = n − H. A row with one cell is a *walk row*; `d k H` counts the height-H
surplus-k animals whose top row is a walk row. A maximal run of multi-cell
rows is a *cluster*; `V ℓ j` counts the cluster shapes spanning ℓ rows with
surplus j between a walk cell below and a walk cell above, `Vt ℓ j` the same
with nothing above. A walk row separates the animal
(`Universal/Separation.lean`), and peeling the top row gives two bijections
(`Universal/Peel.lean`, the long pole), with the drift count `b`
(3 for the king lattice) in place of the 3:

    d k H     = 3·d k (H−1) + Σ_{j≤k} Σ_{ℓ≤j} V ℓ j · d (k−j) (H−1−ℓ)      (H ≥ k+2)
    T (H+k) H = d k H + Σ_{j≤k} Σ_{ℓ≤j} Vt ℓ j · d (k−j) (H−ℓ)              (H ≥ k+1)

Shape (`Universal/AbstractShape.lean`, from the two identities alone through
the `PeelSystem` interface; `DiscreteCalculus.lean` supplies the discrete
antiderivative and integer values by finite differences). Strong induction on
k through the first identity:
`d k H = δ_k(H)·3^H` with deg δ_k ≤ k for all H ≥ k+1, the base value
absorbed into the constant term, which is why the onset is k+1 and not k+2;
the second identity carries it to the diagonal and gives `shape_production`.
Integer values on all of ℤ come from finite differences
(`production_int_all`).

Leading coefficient (`LeadingCoeff.lean`). Divide the first identity by
3^H: δ_k(H) − δ_k(H−1) is a sum over the weights, and only the V(1,1) = 25
term reaches degree k−1, so k·[X^k]δ_k = (25/9)·[X^{k−1}]δ_{k−1}; from
δ_0 = 1/3 and the 3-power bookkeeping this is 25^k/k! for any polynomial
satisfying the law, stated for an arbitrary witness. With the leading
coefficient known, k rows (2k+1 … 3k) pin P_k by Lagrange.

The staircase (`Grand/`). `Series.lean` is a convolution toolkit; `Mu.lean`
defines the multiplier sequence μ from the weights and its inverse ν;
`MuRec.lean` proves `d_mu_rec`: `d k (H+1) = Σ_i μ_i·d (k−i) H` for
H ≥ k+1, one strong induction from the first peeling identity;
`Staircase.lean` transports it to the diagonals (`T_staircase`). On this,
`Grand/PinAll.lean` climbs: `GrandForm k P` says P is the production
polynomial of level k; `level_step` passes from levels < k to level k given
the two cells A_k, B_k; `grand_all` runs it from `grand_zero` (P_0 = 1,
unconditional) to k = 18 under `BankedAnchors`, and `Pk_prod` reads off the
diagonal law with the concrete `Pp<k>` of `Pin.lean`. The 19 polynomials in
`Pin.lean` are the engine's (`orchestrator/sweep.go`, extracted to
`pin-data.md` by `scripts/extract_pin_data.py`); a wrong coefficient fails
the anchor evaluations in `PinAll`.

Symmetry (`Symmetry.lean`): the dihedral group acts by apply-then-reanchor;
`R90`, `R180`, `Hm`, `Dm` are the fixed-point counts, `Free`, `OneSided`,
`Bilateral` the orbit counts, and the three identities are Burnside.

Growth (`UpperBound`, `Fekete`, `Growth`): `a_le_choose : a n ≤ C(5n, n)`
by a decision-tree encoding, supermultiplicativity by concatenation with cut
recovery, and Fekete's lemma once (`Fekete.lean`, a structure) gives the
limit λ, `a n ≤ λ^n`, and the brackets `lambda_le : λ ≤ 3125/256` and
`lambda_gt_of_banked : 6.22 < λ` given a(40) as a hypothesis.

## Modules

| module | what |
|---|---|
| `Defs` | king adjacency, connectivity, canonical form, `T` |
| `Finite` | width bound; `T` as a `Finset.card` |
| `Compute` | computable `Tc`, `Tc_eq_T`, the three kernel-decided cells the proofs use |
| `Sequence` | `a n`, `a_eq_sum`, computable twin `ac` |
| `Weights` | the king `d`, `V`, `Vt` as computable enumerations, window independence, `V 1 1 = 25`, `d 0 1 = 1` |
| `King` | `kingLattice`; the generic objects agree with the king ones; `d_rec`, `c_ident`, `shape_production`, `production_int_all`, `T_diag_pow` in king vocabulary |
| `DiscreteCalculus` | the discrete antiderivative, integer values by finite differences |
| `LeadingCoeff` | 25^k/k!, pinning from k rows |
| `Pin` | the 19 production polynomials, Lagrange pin, `P1_closed` |
| `Grand/Series` | convolution toolkit |
| `Grand/Mu` | μ, ν, `mu_conv_nu`, the gates μ₁, μ₂ |
| `Grand/MuRec` | `d_mu_rec` |
| `Grand/Staircase` | `T_staircase` |
| `Grand/PinAll` | `GrandForm`, `level_step`, `grand_all`, `Pk_prod`, `BankedAnchors` |
| `Symmetry` | dihedral action, Burnside identities, `r90_vanish` |
| `SymmetryRatio` | `symmetryRatio`: the symmetric counts are o(a(n)), so one-sided → a(n)/4 and free → a(n)/8 |
| `UpperBound` | `a n ≤ C(5n,n)` |
| `Fekete` | Fekete's lemma as a structure |
| `Growth` | λ, `lambda_tendsto`, the brackets |
| `Report` | the report's claims |
| `Audit` | the `#guard_msgs` axiom guards |
| `Enum` | the bit-board enumerator: `L n` lists the canonical animals of `n` cells (`L_spec`, `n ≤ 14`); `a`, `T`, `d`, `V`, `Vt` and the symmetry fixed-point counts as filtered list lengths |
| `EnumData` | the 638 and 3,832 boards of `L 5` and `L 6` as literals, checked against the enumeration in five kernel runs; `T 5 3`, `T 6 4` |
| `Checks` | validation facts nothing consumes (built, never imported) |

The generic development the report's proofs run through, and the other
L-paper modules:

| module | paper | what |
|---|---|---|
| `Universal/Defs`, `Graph`, `Finite`, `Separation`, `RowProfile`, `Weights`, `Peel` | report, L1 | the peeling recursion for every row-local lattice (a finite set `D` of up-offsets, `b = |D|`) |
| `Universal/AbstractShape`, `System` | report, L1 | the diagonal law as a theorem about any `PeelSystem`, hence for every row-local lattice |
| `Universal/Compute`, `Hex`, `Square` | L1 | the generic enumerator and pin lemma; the hex and square instances and their `P_1` |
| `Upper/Certificate` | L3 | the convolution-certificate bound `λ ≤ 1/x` from a rational super-solution, and `RatCert`, the exported-data check |
| `Upper/BuiData2`, `BuiRD2`, `BuiData3`, `BuiRD3` | L3 | the 185-type (λ ≤ 9.4117) and 5930-type (λ ≤ 9.3154) certificates as balanced lookup trees the kernel checks (`decide +kernel`, 11 s for RD = 3), conditional on the named system hypotheses |
| `StairAnimals`, `StairGrowth` | L5 | staircase king animals: the column join is injective at fixed area (Lemma 3), µ exists, 3.1234 < µ ≤ 4 given M(700) |

## No `native_decide`

Since 2026-10-12 the tree has no `native_decide` at all, so every theorem in
it is on the standard three axioms. (The RD = 3 certificate check was the last
holdout: 5930 rows with `List.getD` lookups were beyond the kernel, balanced
trees made it an 11-second `decide +kernel`.)

The powerset counters (`Tc`, `ac`, the window enumerations of `Weights.lean`)
reach the kernel only for the smallest cells: T(1,1), T(2,1), T(2,2), T(3,1),
T(3,2), T(4,3), a(1), a(2), V(1,1), Vt(1,1), Vt(1,2), d(0,1), d(0,2), d(1,2)
at 2.7–3.5 GB each; T(3,3), a(3), d(0,3) need 6 GB and anything larger passes
8 GB (`scripts/lean-decide-trials.sh`, 2026-10-12). Everything up to six
cells comes instead from `Enum.lean`: a cell set is one natural number (bit
`16y + x`), the animals of `n + 1` cells are grown from those of `n` cells by
adjoining a frontier cell and keeping the child exactly when that cell is
its row-major-largest leaf, and `L_spec` proves the list is the canonical
animals of `n` cells, each once, for `n ≤ 14`. `EnumData.lean` stores `L 5`
and `L 6` as literals and checks them against the enumeration in five
kernel runs of 4–5 GB and 8–14 s each (`scripts/lean-enumdata-measure.sh`); a count is then a filter over the
literal. That is how `Checks.lean` has rows 4–6 of the triangle,
a(3) … a(6), the walk-top counts d(k,H) for H + k ≤ 6, the weights with at
most six cells (V(1,2), V(2,2), V(1,3), Vt(2,2), Vt(1,3), Vt(2,3)) and the
symmetry counts R90, R180, Hm, Dm for n ≤ 5, and how `P2_closed` holds
outright. Seven cells are the limit: `L 7` (23,592 boards) passes 12 GB in
one kernel run, so V(2,3), Vt(3,3), V(3,3) and d(3,4) stay out, as do the
unconditional 3.95 < λ and μ₂ that rested on them.

## What is not reached

- a(41). The pinning takes two cells at or above the onset per level; the
  a(41) route replaced one anchor by a below-onset cell corrected by the
  defect D_j(k) (`results/below-onset.md`), and neither that identity nor
  the substitution is stated in Lean.
- The engine. Nothing here certifies the enumeration, the banked triangle, or
  the 36 anchor values; a(40)'s warrant is `docs/publication.md`.

## Removed from the build, 2026-10-12

The overhaul (branch `lean-overhaul`) kept the import cone of `Report.lean`
and the modules the L-papers cite, and deleted the rest. Everything below is
at commit `697f376`
(`git show 697f376:polyplets/Polyplets/<module>.lean`), built green there with
its own `#guard_msgs` audits (`AuditOutworks.lean`, `Grand/Audit.lean`).
Lines are at that commit.

| group | lines | what it proved |
|---|---|---|
| `GapWalk*`, `DepthOne*`, `KernelRoots`, `KernelSeries`, `DepthAssembly` (20 modules) | 14,000 | the Severance and Notary campaigns: the depth-1 defect's gap walk, `Φ(x, N(x)) = 0` at every order, the depth identities for D_j(k) with the weight tables as hypotheses (`results/below-onset.md` §11) |
| `Holes`, `HolesUpper` | the maximum-hole bound, lower side unconditional, upper side under the hypothesis `MoatBound` |
| `V5Denominator` | the 5-adic denominator law of P_k for k ≤ 18, kernel `decide` |
| `Northcott` | bounded degree + bounded house ⇒ finitely many algebraic integers |
| `IntCoeff` | k!·P_k ∈ ℤ[X] |
| `Grand/ExpForm`, `Grand/Lead` | the exp-form `grand_form` and `lead_coeff_25`; superseded by `LeadingCoeff.lean` |
| `Weights3Heavy`, `WeightsChunk*` (11) | 800 | V(3,3) = 4778, Vt(3,3) = 919, d(3,4) = 4687 by chunked `native_decide`, an hour of every cold build |
| `ComputeBridge`, `Diagonal`, `Sanity`, `AuditOutworks` | more `native_decide` cells of rows ≤ 6, restatements of P1/P2, a hand proof of T(1,1) = 1, 70 axiom guards |
| `Draft/Prop6Skeleton` | — | the never-built `sorry` skeleton of Proposition 6 |

Also gone, same reasons: `Grand/PinGrand.lean` and `scripts/gen_grand_pin.py`
(2,608 generated lines, replaced by `Grand/PinAll.lean` at `7641b74`), the
old Lagrange tiers of `Pin.lean` (`P<k>_pinned_of_banked`, k = 4 … 11, with
`scripts/gen_pin.py`), `P3_pinned_of_heavy`, the `make gate-notary` target, and the planning files `PROOF-STATUS.md`, `DESIGN.md`,
`docs/lean-record.md`, whose surviving content is this file.

## History

- 2026-07-20: the diagonal-law formalization starts; the peeling recursion
  replaces the paper's generating-function route.
- 2026-07-21: shape theorem and the staircase grand form land; the
  hostile-witness audit finds no sorry, no custom axiom, no circularity, and
  that the definition of `T` matches the engine's term for term, every
  near-miss definition diverging at a cell the kernel checks.
- 2026-07-30 … 08-06: the outworks (a(n), λ, symmetry, holes, universal law,
  the Bui certificate, the 5-adic law, the staircase constant).
- 2026-10-11 … 12: the overhaul. `Report.lean` written; `LeadingCoeff.lean`
  replaces the exp-form route; `PinAll.lean` replaces the generated pinning;
  levels 1 … 3 take their anchors as hypotheses like the rest, so every Report
  theorem is on standard axioms; everything outside the Report cone deleted.
  Working list: `OVERHAUL.md`.
