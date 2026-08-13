# Round-3 L3 blind list — contour encoding candidates

Filed 2026-08-12 18:31 EDT, before reading anything beyond
`docs/triangle-round3-brief.md`, `docs/skeptical-reader-standard.md`,
`results/triangle-r3-harness.md`, and CLAUDE.md. Append-only from here;
nothing below this header gets revised.

Candidates, from the brief and prior knowledge only:

1. **Jensen-style contour/boundary TM** (self-avoiding-polygon technology):
   boundary states on the cut line are link patterns (arch pairings of curve
   crossings), Catalan/Motzkin-counted. Expected to be exactly the object
   `boundary-push-tensornetwork.md` measured as the cut rank — to be
   established by measurement, not asserted.
2. **Boundary-word encoding of the outer contour** (Delest–Viennot-style):
   the animal as a closed lattice walk on the dual lattice; exact for
   hole-free simply-connected animals only. Holes ⇒ one inner curve per
   hole ⇒ not a single-curve object.
3. **Hole-free by contour, plus hole strata**: count hole-free king animals
   by a contour method, then add strata with k marked holes (defect-gas
   machinery per the brief). Live only if (a) a king contour exists at all
   and (b) the strata are countable at n=40, H=15..21.
4. **Multi-curve encodings**: outer contour plus inner contours enumerated
   jointly, curve count unbounded (holes can be Θ(n)); state must carry
   which curves nest/pair — again link-pattern-shaped.
5. **King-adjacency contour existence question** (the level-1 gate): two
   cells meeting only at a corner give a boundary that visits a lattice
   point twice (pinch). Candidate repairs to check: (a) corner-resolution
   convention (split the pinch NE/SW vs NW/SE — but king-connectivity
   joins BOTH diagonals, so the two resolutions disagree); (b) contour on a
   refined (half-step) lattice; (c) contour of the closure/filled polyomino
   rather than the animal. Each must be checked for bijectivity.
6. **Perimeter/site-perimeter generating identities** as a substitute for a
   full contour TM — likely consistency-check class, not a counting route.

Prior expectation, stated for the record: the lane closes negative on the
main route (holes + link-pattern states = the measured entanglement wall),
and the only live question is whether variant 3 dies at the strata cost or
earlier at the pinch-point bijection.

---

Post-work append, 2026-08-12 ~19:0x EDT (list above unrevised). Outcome vs
the blind list: candidates 1, 2, 3/4 and the existence question 5 were the
ones that mattered; 5's resolution went through repair (c)-adjacent
territory (closed-cell-union topology, pinches always glue under king
adjacency) rather than either convention in (a). Candidate 6 was not
pursued separately — subsumed by the level-2 verdict. Deliverable:
results/triangle-r3-l3-contour.md.
