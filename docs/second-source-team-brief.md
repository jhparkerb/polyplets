# Team brief — a genuinely independent second count of T(n,H)

2026-08-11. Supersedes the draft brief; incorporates the repo-state
corrections in `docs/second-source-brief-critique.md` and jasonp's ruling on
the existing second source. Where the two conflict, this file wins.

---

## The ruling that frames everything below

The project has a second engine — the strip transfer matrix
(`results/strip-engine.md`, `cpp/strip_tm.cpp`), 469 cells confirmed, 0
mismatch, H ≤ 14 at every n ≤ 40. **It does not qualify as verification.** It
is a consistency check, and a useful one, but it is not a second way of
counting polyplets.

The reason is stated in the repo's own audit and jasonp holds it as
disqualifying: the strip engine's core rule — union-find over the new column's
cells against the old column's component labels, with stranded-component death
— is *the same rule* as this repo's reference column oracle, `core/transition.h`,
and the same rule as the kink kernel that produced the banked triangle. It was
written independently, but it is not a different idea. A shared misconception
about king-connectivity, or about what the count is counting, passes through
both engines untouched and shows up as agreement.

What the strip engine is disjoint on — boundary granularity, accounting layer,
count representation, orchestration — is real but is not where the risk lives.
Treat the existing agreement as evidence against transcription, overflow, and
sharding faults, and as **no evidence at all** against a wrong shared rule.

So: the target is not the uncovered cells. **The target is a count that does
not decide connectivity the way both current engines decide it, and the
standard is publication-grade certainty, not coverage percentage.** A method
that re-verifies cells already strip-confirmed, by a genuinely different route,
is worth more than one that extends the strip engine's reach.

---

## Goal

Get T(n,H) — and through it a(n) — to a standard that survives hostile review.
State the goal in this repo's warrant scale (`docs/provenance-tables.md`: tier
1 jasonp-vetted, tier 2 Lean kernel, tier 3 exact-arithmetic certificate, tier
4 reproducible measurement). Two acceptable outcomes, the second worth more:

1. **A second count that is independent on the connectivity rule**, reproducing
   banked cells at n ≤ 40. This upgrades tier-4 cells from "two engines that
   could share a blind spot" to "two engines that cannot."
2. **A tier-3 artifact** — an exact-arithmetic certificate for a cell or a row
   that a short independent checker verifies, in the shape of
   `results/strip-mu-certificates.md` or the mod-p degree certificates in
   `results/anisotropic-not-dfinite.md`. Nobody has proposed a mechanism for
   this. It is open, and it is the higher prize.

a(40) is the project's final term; the project closes there. Nothing past
n = 40 has value. Rank candidates by the certainty they buy over the banked
triangle, not by reach.

---

## The independence bar

The bar is not "a different encoding" and not "a different frontier shape."
Both current engines are frontier DPs over compressed state, and so will any
candidate be that survives n = 40 at growth ≈ 7. Requiring otherwise rules out
everything computable.

**The bar is the connectivity rule.** A candidate earns its place by deciding
connectivity by a different mechanism — inclusion–exclusion over cuts,
spanning-structure algebra, rank-based or representative-set methods,
cut-and-count, a Tutte/reliability polynomial specialisation, a
model-counting formulation where connectivity is a constraint rather than a
carried state. Being a frontier DP in every other respect is fine.

For each candidate, state:

- the failure mode it would exhibit if it were wrong, and
- the argument that this failure mode is disjoint from
  union-find-over-a-frontier's.

"Different code, different author, different language" is not an independence
argument — the strip engine already has all three and is the reason this brief
exists.

---

## Ground truth to work against

Read `results/strip-engine.md` before anything else, §Independence in
particular: it is the honest scoping of what the existing check does and does
not buy, and it is the template for the argument your candidate has to make.

- **Growth**: a(40)/a(39) = 6.935; λ estimated 7.110(1) by four agreeing
  methods; rigorous bracket 6.543 ≤ λ ≤ 9.3154
  (`docs/open-problem-lambda-bracket.md`). Anything that materialises
  individual objects is dead well before the frontier. `build/g2` (the
  canonical gated Redelmeier — check `build/` before writing any enumerator)
  confirms the fixed counts through n = 19; the banked whole-row confirmation
  reaches n = 22 and cost the **entire three-machine fleet ~119 hours of wall
  clock** (122 workers across three ISAs, 24,000 shards, 2026-07-11 to
  2026-07-16 — `results/redelmeier_row22/PROVENANCE.md`), for
  a(22) = 4.7×10¹⁶ objects.
- **Redelmeier is a closed door, not a slow road.** Cost is proportional to
  object count and the count grows 6.8×/term, so from the measured a(22) run:
  a(23) is ~810 fleet-hours (34 days), a(24) ~230 days, and a(40) is ~10¹⁵
  times the a(22) run — order 10¹³ years of fleet time. No constant factor
  touches that. Do not propose extending it, sharding it further, or a faster
  object-materialising enumerator of any kind; the same arithmetic kills every
  such variant. Its only standing role is validating the *definition* and the
  low terms, and note what that means for this brief: the one existing check
  that does not share the frontier connectivity rule stops at n = 22 and cannot
  be pushed. That is the problem, not a partial solution.
- **The incumbent** is the cell-at-a-time NW-carry serpentine ("kink") kernel,
  with the `cpp/tma` column sweep as its base (`docs/engine-design.md`). It is
  disk/spill-bound, ~2.5×/term on the kink base. Compute cost tracks frontier
  size ~2^H, not object count, so a top height is never cheap however few
  animals it contributes: a(40)'s H21 phase alone cost 36.4 h on 32 cores with
  a 363 GB disk peak (`docs/paper1-engine-chapter.md` §7–8).
- **The strip engine's ceiling**, for calibration: C_14 measured ~38 GB, C_15
  projects ~200+ GB, state packed 4 bits/row caps at H = 15. A candidate whose
  state set is larger than the incumbent's is dead; a candidate that is merely
  slower is acceptable.
- **A diagonal frontier is ruled out**: on the cut i+j = c the neighbour
  (i+1, j+1) sits two layers ahead, so the cut needs extra depth. Already
  recorded — `docs/dmirror-design.md` §"Recommended geometry", and
  `results/finite-lattice-crossover.md` concludes the diagonal sweep is
  essentially optimal with the remaining speed being engineering. Do not
  re-derive either.
- **Open question, not a constraint** (Teammate B, answer with a citation):
  what is the pathwidth of the king graph P_m ⊠ P_n, and does the kink frontier
  achieve it? An earlier draft asserted that a column separator implies
  column-scan achieves minimum pathwidth; the separator claim is true, the
  implication is unsourced. The binding constraint either way is that a
  candidate must beat the kink frontier width, not match it.

---

## Split by literature, so you do not collide

**Teammate A — enumeration and statistical mechanics.** Lattice animal and
polyomino enumeration, series expansion methods, the finite lattice method
(Enting; Conway; Guttmann; Jensen), transfer matrices in the physics
literature, graph polynomials (Tutte, reliability, Potts). The graph-polynomial
end is the part most likely to clear the independence bar — that is where
connectivity is an algebraic object rather than a carried state.

**Teammate B — exact model counting and parameterised algorithms.** #SAT and
weighted model counting (sharpSAT-td, GANAK, d-DNNF compilation), treewidth and
pathwidth DP, cut-and-count, rank-based and representative-set methods for
connectivity, ZDD/BDD-based set enumeration. Note the tension you must address:
most of these reduce to a frontier DP with a connectivity state, which is the
incumbent's rule in another costume. Cut-and-count and rank-based methods are
the exceptions worth pressing on, because they replace the connectivity state
rather than re-encoding it.

**Teammate C — coverage map.** Which methods have been pushed to what scale on
adjacent lattice objects (polyominoes, polyhexes, self-avoiding walks, directed
animals), the state-space ceiling each hit, and the bottleneck each author
reported. Gaps in that map are the target. Also: find cases where this problem
is solved under a different name — polyplets, pseudo-polyominoes,
king-connected animals, connected induced subgraphs of the strong product
P_m ⊠ P_n, site animals with next-nearest-neighbour adjacency.

C starts from work already done, and extends rather than restarts:
`results/novelty-sortie.md` N1–N6 is a targeted novelty sweep with verdicts;
`papers/INDEX.txt` indexes 60+ local PDFs including Jensen, Barequet–Shalah,
Conway–Guttmann, Chan–Rechnitzer, Bousquet-Mélou–Rechnitzer; the OEIS and
Superseeker lookups for this family are done and returned novel. The literature
term here is **polyplets**, glossed at first use as king-connected animals.

All three should also re-evaluate and combine old ideas, including from the
exhausted list.

---

## Exhausted — do not propose

Combinations only, and only with a specific argument for why the combination
behaves differently.

- Burnside / symmetry decomposition.
- Alternative decompositions of the count.
- Recombination across a second machine.
- **mod-p / CRT computation** — and the reason matters, because this one comes
  back in new hats: residue arithmetic catches arithmetic, overflow and
  transcription faults but shares the enumeration, so it is not independence
  (`results/crt-counter-shaping.md`; the a(23) readiness analysis behind
  `results/ns_a23`).
- In-flight redundancy checking.
- **Any enumeration that materialises individual objects** — Redelmeier and
  every variant of it, however sharded or optimised. Killed by measurement, not
  by judgement: see the a(22) fleet numbers above. A candidate whose cost is
  proportional to the object count is dead on arrival at every n this project
  cares about, including a(23).
- The serpentine cell-by-cell frontier ("kink") — this is the **incumbent**,
  not a candidate.
- Formal verification of the existing implementation in Lean.
- **The four algorithmic levers**, all measured dead at the connectivity wall
  (`docs/paper1-engine-chapter.md` §8, `results/second-wind.md`,
  `results/strip-growth-lambda-bounds.md`,
  `docs/full-utilization-redesign.md` Part 4). What is left there is
  engineering, not algorithms.
- **Engineering negatives**: PGO, LPT scheduling, work-stealing at scale, tmpfs
  past a(34), cloud burst, rook/bishop edge distribution.
- **Finite-type convolution certificates** (Klarner–Rivest, Barequet–Shalah,
  Bui) — a different target, but the whole method class is characterised and
  its barrier proved in `docs/open-problem-lambda-bracket.md`.
- **The bivariate depth tower** (`results/depth-tower-bivariate-dead-end.md`).

---

## On the table as a floor to beat, not as answers

- **The finite lattice method** (Enting, Conway–Guttmann) — read
  `results/finite-lattice-crossover.md` first. Its *reach* payoff is closed
  negative here: the bounding-box halving is the same ½ this engine already
  gets from transpose symmetry plus the diagonal-polynomial derivation, so it
  does not stack. Its *accounting* independence is a separate and still-open
  question — inclusion–exclusion over W×L rectangles is a different layer, but
  a column transfer matrix sits inside each rectangle, so the connectivity rule
  stays shared. Propose it only with that distinction made explicitly.
- Tree-decomposition exact model counting (sharpSAT-td, GANAK lineage).
- Inclusion–exclusion over component structure.
- Sequential importance sampling for confidence intervals rather than exact
  values.

---

## Deliverables

Appended to `results/second-source-candidates.md`, following the repo
convention that negative results are their own banked note in the shape of
`results/depth-tower-bivariate-dead-end.md`:

- **A ranked candidate list.** Each entry: the region of the triangle it could
  verify and at what n; **the independence argument against the
  connectivity-rule axis specifically**, with the failure mode it would exhibit
  named; and the resource that binds it first.
- **A kill list**, with the probe number or citation that killed each entry.
  Negative results are deliverables and must be recorded so no later teammate
  re-treads them. A candidate that cannot be killed cheaply gets a stated
  measurement plan instead of a verdict.
- **Citations**: title, authors, year, and a resolvable identifier (DOI, arXiv
  ID, or URL). Do not cite from memory. If you cannot verify a reference
  exists, say so rather than producing a plausible one; un-findable references
  go to `papers/MISSING.md` with what was searched. Tasks are gated on
  citations resolving — an unresolvable reference bounces the task back to you.

Critique each other's candidates directly. Two of you agreeing is not evidence
— that is the whole point of this brief. No candidate leaves the list without
either a probe number or a resolvable citation.

Cross-critique needs a mechanism: three agents running at once cannot read each
other's findings. Either write to the shared file under a stated append-only
protocol, or run the critique as a second wave over the first wave's output.

---

## Code and probes

You may write and run code, with limits. Code exists only to produce
measurements for the findings document — state-space sizes, where an existing
tool falls over, growth of an intermediate representation. Probes are
throwaway, run on small instances, and are time-boxed to 15 minutes. Do not
implement a candidate. Do not tune a probe that runs slowly: a probe exceeding
its budget is a measurement, and the candidate goes on the kill list with that
number attached. Every quantitative claim in your deliverable must come from a
probe or a cited paper, never from estimation.

Follow `docs/job-checklist.md`. In particular: anything that could exceed five
minutes runs in a tmux window on the machine's existing session, never in the
foreground and never under `nohup`; named scripts on disk, no stdin jobs;
binaries build into `build/`, nothing in `/tmp`; no filesystem-wide scans
(`find /`, `grep -r /`); per-worker RAM is (total × margin)/cores, never a flat
number; gympie caps at 10 performance cores.
