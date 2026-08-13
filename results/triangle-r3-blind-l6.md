# L6 blind list — wildcard lane, filed before reading

**Timestamped 2026-08-12 18:22:30 EDT.** Written from memory only, before
opening any paper, before listing `papers/`, before any web query. Inputs so
far: `docs/triangle-round3-brief.md`, `docs/skeptical-reader-standard.md`,
`results/triangle-r3-harness.md`, CLAUDE.md. Per the brief this file is
append-only; anything added later is under a dated "Appended" heading.

## (a) Candidate list, as wide as I can make it

Tags are my prior guess at fate, recorded so the filter can be scored against
them; the filter below is what actually decides.

**Algorithmic / parameterized-complexity literature**

1. Redelmeier rooted-growth DFS and its parallel/GPU descendants
   (Mertens–Lautenbacher line).
2. Jensen-style contour transfer matrix with link-pattern boundary states.
   (L3's lane; listed for completeness.)
3. Conway–Enting finite lattice method. (Project measured it: crossover
   NEGATIVE.)
4. Twisted-cylinder methods (Barequet–Shalah line) — growth-constant bounds.
5. ZDD / frontier-based search (Knuth Simpath; Kawahara–Minato "frontier
   method"; Graphillion as packaged tooling) — mate/label arrays on a
   frontier inside a third-party decision-diagram library.
6. **Cut&Count** (Cygan–Nederlof–Pilipczuk–Pilipczuk–van Rooij–Wojtaszczyk,
   FOCS 2011): connectivity enforced by cancellation — count (subset,
   consistent 2-sided cut) pairs; disconnected subsets contribute 2^(c−1) ≡ 0
   mod 2. No component labels anywhere; frontier state is a per-cell side
   bit. Gives residues mod 2 (and possibly lifts).
7. Rank-based / representative-sets approach to connectivity DPs
   (Bodlaender–Cygan–Kratsch–Nederlof): deterministic, but built for
   optimization — does a counting version exist?
8. Björklund-style algebraic cancellation (determinant sums for
   Hamiltonicity; parity counting lines, mod-2^k extensions if they exist).
9. Vertex-exponential Tutte / fast subset convolution
   (Björklund–Husfeldt–Kaski–Koivisto 2008) — 2^(#cells) over 840 cells.
10. **Potts spin-basis transfer matrix / Fortuin–Kasteleyn identity**, site
    version: Σ_S q^(c(S)) = #{(S, f: S→[q]) : f constant on king-adjacent
    pairs within S}. The RHS is a purely local constraint — frontier state is
    per-row "empty or color i", (q+1)^H states, **no partition labels, no
    union-find, no stranding rule**. Z(q) is a polynomial of degree ≤ n in q;
    Z(2^j)/2^j ≡ C₁ (mod 2^j) gives the connected count to modulus 2^j from a
    single integer-q run. Same cancellation family as 6; 6 is its q=2 case.
11. Tutte/Whitney polynomial evaluations of grid graphs — bond/spanning
    objects, not induced site animals, unless routed through 10.
12. #SAT / projected model counters with connectivity in the encoding —
    L5's lane; listed to mark the boundary, not to claim it.
13. Holographic algorithms / matchgates.
14. Treewidth/pathwidth DP on the strip — pathwidth = H, i.e. the frontier
    again by another name.
15. Color-coding (Alon–Yuster–Zwick) and motif-counting frameworks.
16. Inclusion–exclusion over component structure (exponential formula /
    Möbius inversion on the partition lattice) — the gas shape; L2 closed it.
17. **Euler-characteristic DP:** χ(S) = c(S) − holes(S), and χ is a sum of
    local terms (V − E + F over the cell complex), so Σ_S x^(χ(S)) has a
    label-free frontier DP. c = χ + h; needs the hole distribution from
    elsewhere (the project has hole-marked machinery). Half a route; listed
    as a long shot.
18. Independently published site-percolation cluster series from physics on
    the square lattice with NN+NNN adjacency (the king / "square matching"
    lattice): Sykes-school perimeter polynomials, Mertens-line modern series.
    External anchors at small n by other people's methods.
19. Perimeter-polynomial / mean-cluster-size identities as consistency
    relations on the same series.
20. Baxter corner transfer matrix and CTMRG-style contraction (a non-MPS
    contraction structure — the closed door is site-ordered MPS
    specifically).
21. Monte Carlo (Rosenbluth, PERM/flatPERM) — not exact.
22. Series analysis / differential approximants — not exact.
23. Formally verified counter (Lean/Coq-verified enumeration) as a
    definition-level witness at small n.
24. Quantum / annealing anything.
25. Species theory / dissymmetry-theorem counting.
26. Bijective identities: heaps of pieces (Viennot) — known to solve
    *directed* animals; any undirected king version would be an identity
    finding, not a counting route.
27. Temperley methodology / Bousquet-Mélou-school solvable subclasses
    (column-convex etc.) — exact GFs for subclasses only.
28. Symmetry block-diagonalization of the color transfer operator of 10
    (Fourier/Hadamard in color space) — engineering on 10, not a separate
    method.
29. Mod-p and mod-p^k lifts of cancellation counts (literature check
    stacked on 6/8: does anyone count connected structures mod higher prime
    powers by cancellation?).
30. Random-cluster / medial-lattice reformulations — bond-side restatement
    of 10.
31. Persistent homology / TDA component counting — no exact enumeration at
    this scale.
32. Knuth dancing-links exact cover enumeration.
33. Transfer matrix run in the diagonal direction (the project's own
    diagonal-sweep exists for λ; a *counting* diagonal TM with color states
    would be a variant of 10, with labels a variant of the closed class).
34. Independence-polynomial / hard-core-model relations — no connectivity
    content.
35. Cellular-automaton preimage counting / de Bruijn-graph methods — no
    connectivity content.

**Prior expectation, recorded for scoring:** the live find is the
cancellation family {6, 10, 28, 29}; the external-series item {18, 19} is a
semantic-independence prize that cannot reach row 40 and will be filed as a
ticket-misfit if it survives reading; {17} is the dark horse; {20} needs a
one-paragraph reason it differs from the measured MPS wall before it may
survive; everything else I expect the filter to kill.

## (b) The structural filter, fixed before reading

Applied in this order; a candidate dies at the first failing question. Kill
counts will be reported per question.

- **F1 — exact.** Does it produce exact integer counts, or residues to a
  stated modulus? (Bounds, estimates, approximants, stochastic estimates
  die here.)
- **F2 — reach.** Is there a stated-cost route to n = 40 at H = 15..21 —
  state space × work within ~10^12-ish laptop-or-fleet-scale operations for
  at least one nontrivial modulus? (Anything Redelmeier-shaped at n = 40,
  anything 2^(#cells), and per-cell enumeration die here. External
  small-n series die here *as counting routes* but are eligible for the
  ticket-misfit filing the brief asks for.)
- **F3 — rule.** Does it decide king-connectivity somewhere other than a
  cell frontier carrying component labels? Encoding-level (brief's level 1)
  passes with the level stated; anything whose state is a partition of
  boundary cells dies here, per the brief's closed list (site-MPS closed;
  strip-TM recomputation closed by ruling).
- **F4 — not already banked.** Not on the brief's closed list and not in the
  harness prior-work index as measured-dead. (Finite-lattice method, cluster
  inversion, slice mining, site-MPS die here if they got this far.)

Reading cap after pruning: at most six papers in full, per the brief.
