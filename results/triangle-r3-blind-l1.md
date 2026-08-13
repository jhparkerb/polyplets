# L1 blind candidate list — corner gluing

2026-08-12, filed before any work beyond the harness pack
(`results/triangle-r3-harness.md`), the brief
(`docs/triangle-round3-brief.md`), the standard, and the lane's two named
inputs (`results/component-stratification.md`, `results/defect-gas.md`).
Append-only from here.

Candidates, as they occur to me from those files alone:

1. **Piece-refined strip DP.** Sweep the H-strip by column, state = boundary
   occupancy + rook-piece partition of boundary cells + king partition of
   pieces. This is the direct "assembly DP" the brief's trap paragraph
   predicts. Prediction to test, not assume: the rook-piece partition is a
   *refinement* of the cell frontier's king-component labels, so the state
   space should come out *larger* than the cell frontier, not smaller — the
   lane's one real hope ("pieces are coarser than cells") may be exactly
   backwards for a column sweep, because the boundary is still made of cells
   and the piece structure adds information on top of the king labels rather
   than replacing them.
2. **Whole-piece placement with external ingredient counts.** Place entire
   polyominoes (counts from published enumerations — A001168 by size; by
   size×height if published) and glue at corners, connectivity as a condition
   on the piece-contact graph. This is the version with the real independence
   story, since the ingredients are other people's numbers. Known obstruction
   from `component-stratification.md`: composition is geometrically
   constrained, no free GF. The executable form is joint placement of pieces
   — to be checked against the defect-gas reach verdict (this smells
   gas-shaped, which would also answer L2).
3. **Connectivity inversion on the contact graph** (Möbius/Mayer: connected =
   all placements − disconnected, inverted over the partition lattice or via
   the exponential formula). Ingredient = piece placements ignoring
   king-connectivity. Suspected to be the same object as candidate 2's joint
   placement, i.e. gas-shaped; if so it prices out at surplus k = 19..25 by
   `defect-gas.md`'s measured ≈20×/k.
4. **The c = n edge as a warm-up bijection.** Edge-isolated king animals ↔
   polyominoes on the 45° sublattice (`C(n,n) = A001168`, banked). Fully
   external ingredient, level-1 clean — but it covers only one stratum of
   C(n,c) and the typical animal sits at c ≈ n/2, so at best it seeds a
   stratified route, it is not one.
5. **Stratified assembly by c** (sum over component counts c, T restricted to
   c pieces, hoping small-c or near-c strata dominate in a strip). From the
   stratification table the bulk is c ≈ n/2 with ~2-cell pieces — so ~20
   pieces at n = 40, which is where the piece-level-labels trap bites
   hardest. Expect no savings; measure rather than argue.

What I commit to measuring (the lane's core deliverable): the reachable state
count of candidate 1 at small H versus the known cell-frontier sizes
(H = 8, 10, 12, 14: 1604, 11005, 68343, 161357 per
`results/boundary-push-tensornetwork.md` as quoted in my tasking), with a
growth law, and a validation that the piece DP reproduces T(n,H) exactly at
small n, H against `experiments/tristruct/triangle.py`.
