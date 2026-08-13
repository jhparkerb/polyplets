# r4-floors — plan

**Question:** Are the three floors (state L1-6, information L3-1, term-source
L4-12) theorems, and do they say what the campaign uses them to say?

## Steps

1. Read `results/triangle-r3-synthesis.md` §"Three floors" verbatim; record the
   exact wording each floor is stated in, and every place the synthesis (or
   downstream docs) *uses* a floor to close a route.
   Produces: quoted statements + a use-site list in the deliverable.
2. Information floor (hardest first). Read `results/boundary-push-tensornetwork.md`,
   the L3 lane deliverable(s), and any Motzkin evidence. Determine: (a) proof or
   measured fit for the Motzkin identification; (b) the exact method class a
   cut-rank bound covers; (c) whether non-straight / non-spatial decompositions
   escape. Produce a verdict + a named escaping method if one exists.
3. State floor. Read the L1 lane material (r3_l1_* logs, L1 deliverable).
   Determine whether "coarser objects do not help" is proved in general or
   generalized from the rook-piece instance. Look for what a helping coarsening
   would need (a quotient of the frontier alphabet that is a congruence for the
   column transfer map) and whether one is excluded.
4. Term-source floor. Read L4 lane material. Audit the "any rule-independent
   source": enumeration, identity, symmetry, other-lattice transport, proof.
5. Composite: check independence and check that the three cover the space they
   are said to prune to.
6. File verdicts per floor: THEOREM / MEASURED-PATTERN / OVER-APPLIED, with the
   failing step; excluded-classes vs cited-to-exclude-classes; and any route
   treated as closed that is not.

## Stop conditions

- Stop and file if all three verify sound and correctly applied (clean result).
- Stop if a floor's source material does not exist on disk — mark NOT
  ESTABLISHED rather than reconstructing it.
- No compute beyond sub-second desk arithmetic. No jobs. No gympie load.
