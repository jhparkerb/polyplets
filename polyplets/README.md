# polyplets — the Lean development

Lean 4 `v4.31.0` against Mathlib `v4.31.0`, 23 modules, about 8,700 lines,
no `sorry`, no `native_decide`. `Polyplets/Report.lean` states each claim of
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
| T(n,n) = 3^(n−1) | `report_T_diag` | `T_diag_pow` (`Shape`) | — |
| diagonal law: for H > n/2, T(n,H) = P_{n−H}(n)·3^(3H−2n−1), P_k integer-valued, deg ≤ k | `report_diagonal_law` | `shape_production`, `production_int_all` (`Shape`) | — |
| leading coefficient of P_k is 25^k/k! | `report_leading_coeff` | `production_leadingCoeff` (`LeadingCoeff`) | — |
| P_k is fixed once row 3k is computed | `report_pin_row_3k` | `pin_of_leadingCoeff` (`LeadingCoeff`) | — |
| T(n,n−1) = (25n−45)·3^(n−4) | `report_T_n_nm1` | `P1_closed` (`Pin`), from the kernel-decided cells T(3,2) = 10, T(4,3) = 55 | — |
| P_k explicitly known for k ≤ 18 | `report_Pk_known` | `Pk_prod`, `grand_all` (`Grand/PinAll`), climbing level by level from `d_mu_rec` and `T_staircase` | `BankedAnchors`: 36 cells, below |
| 8·free = a + 2R90 + R180 + 2Hm + 2Dm (Burnside) | `report_free` | `free_eq` (`Symmetry`) | — |
| 4·one-sided = a + 2R90 + R180 | `report_oneSided` | `oneSided_eq` (`Symmetry`) | — |
| 2·bilateral = Hm + Dm | `report_bilateral` | `bilateral_eq` (`Symmetry`) | — |
| a(n)^(1/n) → λ | `report_growth` | `lambda_tendsto` (`Growth`, `Fekete`, `UpperBound`) | — |
| one-sided → a(n)/4, free → a(n)/8 | `SymmetryRatioClaim` | **not proved**: stated as a `Prop`, needs the symmetric counts o(a(n)) | — |

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

The peeling recursion (`Separation`, `Weights`, `Peel`). Write surplus
k = n − H. A row with one cell is a *walk row*; `d k H` counts the height-H
surplus-k animals whose top row is a walk row. A maximal run of multi-cell
rows is a *cluster*; `V ℓ j` counts the cluster shapes spanning ℓ rows with
surplus j between a walk cell below and a walk cell above, `Vt ℓ j` the same
with nothing above. A walk row separates the animal (`Separation.lean`), and
peeling the top row gives two bijections (`Peel.lean`, 1,748 lines, the long
pole):

    d k H     = 3·d k (H−1) + Σ_{j≤k} Σ_{ℓ≤j} V ℓ j · d (k−j) (H−1−ℓ)      (H ≥ k+2)
    T (H+k) H = d k H + Σ_{j≤k} Σ_{ℓ≤j} Vt ℓ j · d (k−j) (H−ℓ)              (H ≥ k+1)

Shape (`Shape.lean`). Strong induction on k through the first identity:
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

| module | lines | what |
|---|---|---|
| `Defs` | 52 | king adjacency, connectivity, canonical form, `T` |
| `Finite` | 129 | width bound; `T` as a `Finset.card` |
| `Graph` | 71 | bridge to `SimpleGraph.Reachable` |
| `Compute` | 295 | computable `Tc`, `Tc_eq_T`, the kernel-decided small cells |
| `Sequence` | 300 | `a n`, `a_eq_sum`, computable twin `ac` |
| `RowProfile` | 200 | row fibers, occupied-row interval |
| `Separation` | 238 | a walk row is a cut |
| `Weights` | 420 | `d`, `V`, `Vt`, spread bounds, the small weight values |
| `Peel` | 1748 | the two peeling bijections |
| `Shape` | 513 | the diagonal-law shape theorem, integer values |
| `LeadingCoeff` | 285 | 25^k/k!, pinning from k rows |
| `Pin` | 224 | the 19 production polynomials, Lagrange pin, `P1_closed` |
| `Grand/Series` | 259 | convolution toolkit |
| `Grand/Mu` | 287 | μ, ν, `mu_conv_nu`, the gates μ₁, μ₂ |
| `Grand/MuRec` | 238 | `d_mu_rec` |
| `Grand/Staircase` | 153 | `T_staircase` |
| `Grand/PinAll` | 370 | `GrandForm`, `level_step`, `grand_all`, `Pk_prod`, `BankedAnchors` |
| `Symmetry` | 1011 | dihedral action, Burnside identities, `r90_vanish` |
| `UpperBound` | 941 | `a n ≤ C(5n,n)` |
| `Fekete` | 164 | Fekete's lemma as a structure |
| `Growth` | 755 | λ, `lambda_tendsto`, the brackets |
| `Report` | 124 | the report's claims |
| `Audit` | 94 | the `#guard_msgs` axiom guards |

## No `native_decide`

Since 2026-10-12 the tree has no `native_decide` at all, so every theorem in
it is on the standard three axioms. The validation cells that remain are
kernel-decided (`decide +kernel`): T(1,1), T(2,1), T(2,2), T(3,1), T(3,2),
T(4,3), a(1), a(2), V(1,1), Vt(1,1), Vt(1,2), d(0,1), d(0,2), d(1,2), each
under 3.5 GB. The brute-force definitions blow up fast in the kernel
(`scripts/lean-decide-trials.sh`, 2026-10-12): T(3,3), a(3), d(0,3) need
6 GB; T(5,4), a(4), V(1,2), d(1,3) and the symmetry counts at every n pass
8 GB and were killed. The larger validation facts those modules used to
carry by `native_decide` (rows ≤ 6 of T, a(3) … a(6), the j ≤ 3 weights, the
symmetry anchors n ≤ 5, the k = 2 closed form, μ₂, the unconditional
3.95 < λ) are gone with it; the kernel-decided cells above already separate
the definition of `T` from every near-miss the 2026-07-21 audit tried, and
nothing on the report's path consumed the rest.

## What is not reached

- The symmetry-ratio claim, above.
- a(41). The pinning takes two cells at or above the onset per level; the
  a(41) route replaced one anchor by a below-onset cell corrected by the
  defect D_j(k) (`results/below-onset.md`), and neither that identity nor
  the substitution is stated in Lean.
- The engine. Nothing here certifies the enumeration, the banked triangle, or
  the 36 anchor values; a(40)'s warrant is `docs/publication.md`.

## Removed from the build, 2026-10-12

The overhaul (branch `lean-overhaul`) kept the import cone of `Report.lean`
and deleted the rest. Everything below is at commit `697f376`
(`git show 697f376:polyplets/Polyplets/<module>.lean`), built green there with
its own `#guard_msgs` audits (`AuditOutworks.lean`, `Grand/Audit.lean`).
Lines are at that commit.

| group | lines | what it proved |
|---|---|---|
| `GapWalk*`, `DepthOne*`, `KernelRoots`, `KernelSeries`, `DepthAssembly` (20 modules) | 14,000 | the Severance and Notary campaigns: the depth-1 defect's gap walk, `Φ(x, N(x)) = 0` at every order, the depth identities for D_j(k) with the weight tables as hypotheses (`results/below-onset.md` §11) |
| `Universal/` (14) | 4,200 | the diagonal law for every row-local lattice, with square, hex and king instances and their P_1 |
| `Upper/` (5) | 1,000 | the certificate side of λ ≤ 9.3154 (`lambda_le_of_bui_rd3`, one `native_decide` leaf) |
| `Holes`, `HolesUpper` | 1,100 | the maximum-hole bound, lower side unconditional, upper side under the hypothesis `MoatBound` |
| `StairAnimals`, `StairGrowth` | 500 | staircase king animals: Lemma 3 (`M_supermul`), µ exists, 3.1234 < µ ≤ 4 given M(700) |
| `V5Denominator` | 300 | the 5-adic denominator law of P_k for k ≤ 18, kernel `decide` |
| `Northcott` | 180 | bounded degree + bounded house ⇒ finitely many algebraic integers |
| `IntCoeff` | 255 | k!·P_k ∈ ℤ[X] |
| `Grand/ExpForm`, `Grand/Lead` | 790 | the exp-form `grand_form` and `lead_coeff_25`; superseded by `LeadingCoeff.lean` |
| `Weights3Heavy`, `WeightsChunk*` (11) | 800 | V(3,3) = 4778, Vt(3,3) = 919, d(3,4) = 4687 by chunked `native_decide`, an hour of every cold build |
| `ComputeBridge`, `Diagonal`, `Sanity`, `AuditOutworks` | 750 | more `native_decide` cells of rows ≤ 6, restatements of P1/P2, a hand proof of T(1,1) = 1, 70 axiom guards |
| `Draft/Prop6Skeleton` | — | the never-built `sorry` skeleton of Proposition 6 |

Also gone, same reasons: `Grand/PinGrand.lean` and `scripts/gen_grand_pin.py`
(2,608 generated lines, replaced by `Grand/PinAll.lean` at `7641b74`), the
old Lagrange tiers of `Pin.lean` (`P<k>_pinned_of_banked`, k = 4 … 11, with
`scripts/gen_pin.py`), `P2_closed` and `P3_pinned_of_heavy`, the `make
gate-notary` target, and the planning files `PROOF-STATUS.md`, `DESIGN.md`,
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
