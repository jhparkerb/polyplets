# r4-tallband — plan

**Question:** What actually establishes T(40,H) for H = 22..40, and is any of it
second-sourced?

## Steps

1. Read `results/ns_a40/PROVENANCE.md`, `results/triangle.txt`, the per-height
   files `results/ns_a40/perheight/h*.out`, and `dalby-run-evidence/`.
   Produces: cell-by-cell provenance for H=22..40.
2. Read `docs/proofs/diagonal-law.md` header and state its ACTUAL proved reach
   (lead says k<=3 i.e. H>=37; verify, do not assume).
   Produces: the exact H range the closed form covers at n=40.
3. Establish whether the phase-A sweep counted these cells or merely harvested
   them. Read `combine.log`, checkpoints, r4-gen3 R4-G3-01.
   Produces: verdict on "never swept by anything".
4. Establish the strip-TM second source's actual reach (`results/strip-*`),
   and whether it extends above H=14.
   Produces: second-source coverage map for H=22..40.
5. Price the cheapest second-sourcing route for tall-narrow animals: near-
   diagonal direct enumeration, 45-degree sublattice bijection
   (`results/component-stratification.md`), row-transfer-matrix, defect-gas
   families, grand form.
   Produces: one costed route, MEASURED/EXTRAPOLATED/ASSERTED labelled.
6. Cost-per-percent comparison against H=21 spin route and H=17..19 residue
   ladder. Produces: the decision number.
7. File >=2 successor queue rows, different in kind.

## What would make me stop

- If PROVENANCE.md shows H=22..40 were produced by the same phase-A sweep as
  the bulk, gen4's "closed-form injection" claim is simply wrong and step 5-6
  reduce to pricing a second source for an ordinary swept block.
- If the diagonal law's proved reach in fact covers H>=22, the block is already
  theorem-backed and the whole premise dissolves.

## Hard constraints

No compute beyond desk arithmetic on banked integers. Read-only ssh allowed.
