# The king column transfer matrix has Motzkin(H+1) − 1 states

2026-08-11. Standalone structural result about this project's engine, banked
out of the scaling-exploration campaign (lanes A and C converged on it from
independent measurements; provenance below). Statement, proof, machine
verification, and the one scope fact a reader must not miss.

## Statement

**Theorem.** For the height-H king strip swept column by column under the
incumbent connectivity rule (per-column component partition with
stranded-component death), the reachable whole-column states are exactly the
pairs

    (nonempty occupancy fill F of the H rows,
     non-crossing partition π of F's maximal runs),

and their number is

    #states(H) = Σ_{k≥1} C(H+1, 2k) · Catalan(k) = Motzkin(H+1) − 1.

So the banked strip-engine state series 1, 3, 8, 20, 50, 126, 322, 834, 2187,
5797 (`results/strip-engine.md`, H = 1..10) is M₂−1, M₃−1, …, M₁₁−1 — it had
been Motzkin all along, unidentified.

**Corollary (colour-symmetrized spin TM with clash-zeroing — the
second-source campaign's rule-independent engine, B1 of
`results/second-source-candidates-B.md`).** Its whole-column states are the
same pairs with π an *arbitrary* set partition of the runs:

    #states_B1(H) = Σ_{k≥1} C(H+1, 2k) · Bell(k).

Exact values price B1's rule-independence overhead with no extrapolation:
×1.047 at H = 10 (6072 vs 5797), ×1.243 at H = 14 (386,061 vs 310,571),
×1.551 at H = 17, ×2.349 at H = 21.

## The structure theorem: non-crossing is forced, on a nonplanar graph

This is the interesting half. The king graph is not planar — every 2×2 block
of cells is a K₄ — and the engine's own design notes say crossing partitions
are needed (`docs/engine-design.md`; see the scope guard below for why both
are right). Yet at a straight column cut, crossings are impossible, and the
reason is exactly the K₄:

**Lemma 1.** Let a prefix of columns induce components on the cells of its
last column. Then no two distinct components interleave: there are no rows
a₁ < b₁ < a₂ < b₂ with a₁, a₂ in component A and b₁, b₂ in component B ≠ A.

*Proof.* Suppose they interleave. A contains a king path P_A from the cell at
row a₁ to the cell at row a₂; B contains a king path P_B from b₁ to b₂; both
paths live in the swept region (a half-plane bounded by the cut). P_A
together with the boundary column segment from a₁ to a₂ encloses b₁ away
from b₂, so P_B must cross P_A. Two 8-connected (king) paths can cross in
only two ways: they share a cell, or they cross diagonally — cells (x, y),
(x+1, y+1) on one path and (x+1, y), (x, y+1) on the other. (This is the
standard digital-topology fact that an 8-path can pass an 8-curve only
through a shared cell or a shared 2×2 window; it is the same 8-vs-4 duality
mechanism as the matching-pair Euler identities of
`results/matching-pair-convention.md`.) In the shared-cell case A = B
immediately. In the diagonal case the four cells form a 2×2 block, which in
the king graph is a K₄ — all four mutually adjacent — so A and B merge:
A = B. Contradiction. ∎

Planarity-in-effect, from a nonplanar graph: the same 2×2 mutual adjacency
that makes the king lattice nonplanar is what forbids the crossings.

## Reachability: the rails-and-spurs witness

**Lemma 2.** Every pair (nonempty fill F, non-crossing partition π of F's
runs) is reachable.

*Construction.* Write F's maximal runs bottom-to-top as R₁, …, R_k, run Rᵢ
occupying rows [loᵢ, hiᵢ]. Since runs are maximal, consecutive runs are
separated by at least one empty row, so bottom rows of distinct runs differ
by at least 2. A block of π with one member needs no scaffolding. For the
non-singleton blocks, define the span of block B as [lo of its lowest run,
hi of its highest run]; non-crossing makes any two spans nested or disjoint,
and disjoint spans are ≥ 2 rows apart (their extreme runs are distinct, so a
gap row separates them). Give each non-singleton block its nesting depth δ
(δ = 1 for blocks contained in no other; D = the maximum). Build columns
−2D, …, −1 to the left of F:

- **Rail**: block B at depth δ gets a vertical run in column −2(D − δ + 1)
  spanning B's whole span. (Deepest blocks sit closest to F, at column −2;
  outermost at −2D; rails of nested blocks are ≥ 2 columns apart.)
- **Spurs**: for each member run Rᵢ of B, a horizontal run of cells at row
  loᵢ (the bottom row of Rᵢ) in every column from B's rail column through
  −1.

Then append F itself.

*Why it works — the five separation facts, each pairwise:*

1. **Spurs never touch foreign runs or foreign spurs.** A spur sits at the
   bottom row of its member run; bottom rows of distinct runs differ by ≥ 2,
   and king adjacency reaches only distance 1 in each coordinate.
2. **Rails never touch foreign spurs.** A foreign spur row is the bottom row
   of a run outside the rail's block. If the two blocks' spans are disjoint,
   spans are ≥ 2 rows apart. If the spur's block is nested inside the
   rail's block: impossible to collide by columns — see fact 3. If the
   rail's block is nested inside the spur's block, the spur's row is the
   bottom row of a run *outside* the nested span (non-crossing puts no
   member of the outer block strictly inside the inner span), hence ≥ 2 rows
   from the nested rail's span.
3. **Nested rails never touch, and inner spurs never reach outer rails.**
   Nested blocks' rails are ≥ 2 columns apart, with the inner (deeper) rail
   strictly closer to F; an inner block's spurs run only from its own rail
   column rightward, so they never enter an outer rail's column, and an
   outer block's spurs pass the inner region at rows ≥ 2 away (fact 2).
4. **Nothing strands mid-sweep.** Each scaffolded block is horizontally
   contiguous — its rail column and every column to its right through −1
   contain a spur cell of the block — so the block keeps frontier presence
   at every intermediate cut until F arrives. Singleton blocks introduce no
   cells before F. Every intermediate column −2D … −1 is nonempty (the
   outermost block's spurs cross them all).
5. **The final hookup is exact.** A spur end at column −1, row loᵢ is
   king-adjacent in F to rows loᵢ−1 (empty: the gap below Rᵢ), loᵢ (in Rᵢ),
   and loᵢ+1 (in Rᵢ, or the gap above a length-1 run) — so it attaches to
   Rᵢ and to nothing else; conversely an F-cell can only reach column −1
   cells within row distance 1, all of which belong to its own run's spur
   or to no spur. Hence the induced partition of F's runs is exactly π. ∎

With Lemma 1 (only non-crossing states exist) this is an exact
characterization of the reachable set.

**Corollary proof for B1**: reachability is immediate — B1's fresh/coincide
colour branching realizes any set partition of the first column's runs as an
initial state, and its clash-zeroing transition preserves the (fill,
partition-of-runs) state shape — so its reachable set is all pairs, counted
by the Bell sum.

## Counting

Fills of height H with exactly k maximal runs number C(H+1, 2k) (choose the
2k run boundaries among H+1 slots; stars and bars). Non-crossing partitions
of k items number Catalan(k); arbitrary partitions Bell(k). The classical
binomial–Catalan form of the Motzkin numbers, M_n = Σ_k C(n, 2k)·Cat(k)
(Aigner, "Motzkin numbers," European J. Combin. 19 (1998) 663–675, DOI
10.1006/eujc.1998.0235; OEIS A001006), then gives

    #states(H) = M_{H+1} − 1,

the −1 removing the empty fill (k = 0 term). Consequence worth stating
loudly: the incumbent's asymptotic column-state base is Motzkin's **3**
(ratios ×2.75 at H = 14, ×2.81 at H = 21, → 3); the banked "~2.65×/height"
is the local ratio at H ≈ 10.

## Verification, three implementations plus an exhaustive witness check

- **Witness check (Lemma 2, exhaustive)**: the construction was run for
  *every* (fill, non-crossing partition) pair at every H ≤ 9 — 3,419 cases —
  through an independently written automaton; the end state equalled the
  target pair in all cases, zero failures
  (`scripts/probe_reachability_witness.py`, 0.1 s).
- **Two-sided bijection check (lane C, independent)**: complete enumeration
  both ways at H = 2..7, zero exceptions; census recounted at H = 8, 9, 10
  (`results/scaling-exploration-C.md` §S4,
  `scripts/scaling_probe_motzkin.py`).
- **Count agreement, three codebases**: lane A's BFS closure
  (`scripts/probe_hankel_rank.py` machinery), lane C's census, and the
  banked strip engine's cached-state series (`results/strip-engine.md`)
  agree at every overlapping H ≤ 10. The Bell corollary is verified exactly
  at every measured H ≤ 9 (`scripts/probe_b1_column_states.py`).

## Scope guard — read this before citing the theorem

**The theorem is about straight column cuts only.** The production kink
kernel's cell-at-a-time frontier is a *jagged* cut spanning two partial
columns, and there `docs/engine-design.md`'s note — "crossing partitions
allowed (king connectivity needs them — no Motzkin shortcut)" — is TRUE:
Lemma 1's argument needs the crossing's four cells to lie in the swept
region, which a jagged boundary does not guarantee, and crossing states
genuinely occur there. So:

- straight column cut: crossings impossible (this theorem), states =
  M(H+1) − 1;
- jagged cell-at-a-time cut: crossings occur, states are a strictly larger
  family, and `docs/glossary.md`'s "Motzkin-like ≈ 3^W" for the TMA
  signature is a heuristic gesture, not this identity.

Both statements are correct, each about its own cut. Do not "correct" either
file into the other.

## Novelty trail (grep-before-claiming-new, 2026-08-11)

- In-repo: the strip state series was banked unidentified; no repo file
  states the whole-column count (grepped motzkin / non-crossing / catalan in
  state-count contexts across results/, docs/, paper/).
- Literature: Motzkin-dimension transfer matrices are classical for
  square-lattice models — Jensen's Motzkin-path signature encoding
  (`papers/refs-transfer-matrix.md`), and the Salas–Sokal Potts/chromatic TM
  line has dim = M_{m−1} for square-lattice non-crossing partition bases
  (e.g. arXiv:cond-mat/0108144, arXiv:cond-mat/0004330). The king-lattice
  instance — the exact count via runs, with non-crossing *forced* on a
  nonplanar graph by the 2×2-K₄ mechanism — was **not found**: searched
  king graph / next-nearest-neighbour / NNN transfer matrix with
  non-crossing partitions and Motzkin, on top of the second-source coverage
  map's sweep (polyplets, polykings, pseudo-polyominoes, NNN site animals;
  the external king-TM literature row is empty,
  `results/second-source-candidates-C.md` §2). Not found is not proof of
  absence.

## What it is good for

- It puts an exact closed form under the Hankel/realization floor of
  `results/scaling-exploration-A.md` §A-S1: the floor's ambient state space
  is M(H+1) − 1, so floor-vs-states comparisons are against a known
  sequence, and every base extrapolation can be checked against Motzkin's
  drift to 3.
- It prices B1's rule-independence exactly (Bell over Catalan, table above)
  — the second-source campaign's live candidate now has a closed-form
  resource curve at column cuts.
- The 2×2-K₄ mechanism is the same one behind the matching-pair Euler
  identities (`results/matching-pair-convention.md`): one structural fact
  about the king lattice doing load-bearing work in two campaigns.

## Provenance

Lane C observed states + 1 = M(H+1) at H ≤ 7 and verified the bijection
two-sidedly; lane A found the run-partition mechanism, proved Lemmas 1–2,
and did the exhaustive witness check; the counting identity is Aigner's.
Campaign context: `results/scaling-exploration-A.md` §A-S6,
`results/scaling-exploration-C.md` §S4. Nothing here is committed; the
paper is untouched.
