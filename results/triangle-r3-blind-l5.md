# R3 L5 blind list — pre-registration

Filed 2026-08-12 18:20 EDT, before reading anything beyond
`docs/triangle-round3-brief.md`, `docs/skeptical-reader-standard.md`,
`results/triangle-r3-harness.md`, and CLAUDE.md. Candidates named from my own
knowledge only. Appended-to later if needed; never revised.

Lane: L5 — generic exact counting tooling, written and verified by other
people, in which king-connectedness is stated in the encoding and the counter
never implements it.

## Tool / formalism families I can name

1. **Propositional model counting (#SAT), projected.** Encode "cell subset of
   an n×H box, exactly n cells, touches top and bottom row, leftmost column
   occupied, king-connected" as CNF with auxiliary witness variables
   (spanning-forest / distance-labelling encoding of connectivity); count
   models projected onto the cell variables. Exact counters written by others:
   sharpSAT, sharpSAT-TD, Cachet, ganak (has projection), GPMC (projected),
   d4, dsharp, c2d (knowledge compilation to d-DNNF, counts by evaluation),
   ExactMC, ADDMC/DPMC (dynamic-programming/ADD-based). ApproxMC is
   approximate — excluded by the exact-arithmetic rule.
2. **Constraint programming with a native graph-connectivity constraint.**
   MiniZinc's graph globals (`connected`, `reachable`) over Gecode/Chuffed;
   solution counting via exhaustive search. Connectivity is a declared global
   constraint whose propagator is third-party.
3. **Answer Set Programming.** clingo/clasp: reachability rules
   (`reach(root); reach(Y) :- reach(X), adj(X,Y), in(Y)`) + constraint that
   every chosen cell is reached; count answer sets projected onto `in/1`
   (`--project`). Connectivity = least-fixed-point semantics of the logic
   program, evaluated by a third-party grounder/solver.
4. **MSO model checking / Courcelle-style counters.** Connectivity of a
   vertex subset is MSO-expressible; tools that count satisfying assignments
   of an MSO formula on bounded-treewidth graphs: MONA (WS1S/WS2S), Sequoia,
   D-FLAT (ASP + tree decomposition). The strip graph has pathwidth ~H.
5. **Decision-diagram frontier libraries.** Graphillion / TdZdd / Knuth's
   SIMPATH-family: third-party ZDD construction for connected induced
   subgraphs. Named for completeness and flagged now: their frontier method
   IS component-labels-on-a-cut, so at best level 1 (third-party authorship),
   with the level-2 argument expected to fail.
6. **Proof-assistant formalisation + verified evaluation.** Define
   king-connected n-cell subsets of height exactly H in Lean 4 (this repo has
   a Lean environment) as a decidable predicate; count by kernel-checked
   evaluation (`decide` / kernel reduction) at tiny n. The "counter" is the
   Lean kernel — third-party, verified, and utterly generic. The strongest
   definition-level witness available; reaches only toy n.
7. **General graph libraries as the connectivity oracle in a subset sweep.**
   Sage's `connected_subgraph_iterator`, networkx/igraph connected-components
   over subsets of the king graph. Enumeration-shaped (cost ∝ count), so dead
   beyond n≈20; connectivity decision is third-party. Validation instrument,
   not a route.
8. **Integer programming / lattice-point counting** (LattE, barvinok):
   connectivity is not polyhedrally encodable without exponentially many
   subtour-style cuts; named to close it, expected no.
9. **CAS combinatorial-class tooling** (Maple combstruct, Sage species):
   connected-class constructors act on labelled GF algebra, not on lattice
   geometry; named to close it, expected no.
10. **Weighted-model-counting via tensor/tree-decomposition backends**
    (TensorOrder, DPMC with tree decompositions): same encoding as (1),
    different third-party evaluation engine; the brief's tensor-network door
    is closed for frontier MPS specifically, these count a CNF instead.

## Planned primary candidates

(1) projected #SAT as the main encoding + costing target, (3) ASP as the
second independent encoding of the same object, (6) Lean as the
definition-level gold witness, (7) as the small-n validation oracle.
