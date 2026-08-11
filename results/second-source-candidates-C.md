# Second-source candidates — Teammate C: the coverage map

2026-08-11. Lane C of `docs/second-source-team-brief.md`: which methods have
been pushed to what scale on adjacent lattice objects, the ceiling each hit,
the bottleneck each author reported; plus the problem under other names
(polyplets — king-connected animals — pseudo-polyominoes, polykings, site
animals with next-nearest-neighbour adjacency, connected induced subgraphs of
P_m ⊠ P_n). Extends `results/novelty-sortie.md` N1–N6; does not re-run the
OEIS/Superseeker lookups.

Two probes were run, both under the brief's 15-minute box. **Both are banked
in full, with provenance and the misprint arithmetic, in
`results/mertens-1990-perimeter-crosscheck.md`** — the summaries below defer
to that note.

- **Probe C1** — `experiments/king_cis_probe.py` (throwaway, kept for the
  record): column-DP count of connected induced subgraphs of the n×n king
  graph using this repo's connectivity notion, vs OEIS A286139's b-file
  (computed independently by Andrew Howroyd, 16 terms; first 4 brute-forced a
  third way by Giovanni Resta via Mathematica `ConnectedGraphQ` over all 2^16
  subsets). **All nine terms computable in the box MATCH exactly** (n ≤ 9;
  n = 9 is a 24-digit count over clusters up to 81 cells; 40.9 s Python).
- **Probe C2** — Mertens 1990 Table IVB (next-nearest-neighbour square = king
  lattice perimeter polynomials, s = 11..13) extracted from the held PDF and
  compared coefficient-by-coefficient against
  `results/siteperim_square8_n14.txt`. **All ~100 nonzero coefficients agree
  exactly except one**: at (s=12, t=39) the printed table reads 26269734 where
  the repo has 26169734. The print is confirmed visually (page rendered and
  read; not an OCR artifact), and it is Mertens' misprint, not ours: his own
  column sum with the printed digit gives 257205146 ≠ a(12) = 257105146, and
  a(12) is multi-source (Redelmeier, strip TM, Tremblay–Vernay, OEIS
  A006770). His s=11 and s=13 columns sum to the banked a(11), a(13) exactly.
  The repo's g2 header (`cpp/g2_redelmeier.cpp:124,718`) names this
  cross-check as a convention check, but no coefficient-level comparison or
  the misprint was banked anywhere before this probe.

Probe C2's meaning for the brief: an entirely external 1990 enumeration
(independent author, independent Fortran implementation, perimeter-refined,
predating every line of this repo) agrees with the banked king-lattice counts
at the finest granularity we have — and the one disagreement is provably the
literature's error. That is a definition-level external anchor at n ≤ 13.

---

## The coverage map

Scale, ceiling, and reported bottleneck per method class, on the adjacent
objects. All citations are held PDFs (`papers/INDEX.txt`) or resolvable ids.

### 1. Object-materialising enumeration (cost ∝ object count)

| object | record | source | reported bottleneck |
|---|---|---|---|
| square polyominoes | n = 24 | Redelmeier 1981 (held) | CPU ∝ count |
| square, perimeter-refined | s = 22 | Mertens, J. Stat. Phys. 58 (1990) 1095 (held) | ~1 month workstation background |
| triangular, perimeter-refined | s = 21 | Mertens & Lautenbacher, J. Stat. Phys. 66 (1992) 669 (held) | 17 RISC workstations |
| **king (NNN square)** | s = 13 | Mertens 1990 Table IVB (held); earlier terms Peters, Stauffer, Hölters & Loewenich, Z. Phys. B 34 (1979) 399, DOI 10.1007/BF01325205 | ~30 h Apollo workstation |
| **king** | n = 18 | Tremblay & Vernay, RAIRO-TIA 58 (2024) (held) | CPU ∝ count |
| **king** | n = 22 | this repo, `results/redelmeier_row22/PROVENANCE.md` | 119 fleet-hours, 122 workers |
| high-dim animals | (by d) | Luther & Mertens, arXiv:1106.1078 (held) | CPU ∝ count |

Ceiling: universal and proved by the repo's own measurement — 6.8×/term on
the king lattice makes n = 23 ~34 fleet-days and n = 40 ~10¹³ years. The map
confirms nobody anywhere has materialised past n ≈ 22-24 on any 2D lattice
since Jensen's transfer matrix arrived; the entire field switched methods.

### 2. Transfer matrix / finite lattice method (cost ∝ states ~ c^W)

| object | record | source | ceiling hit, as the authors report it |
|---|---|---|---|
| square polyominoes | n = 46 | Jensen, J. Stat. Phys. 102 (2001) 865 (held) | memory (signature count ~3^W) |
| square polyominoes | n = 56 | Jensen, ICCS 2003, LNCS 2659 (held) | memory-bound on a ~500-processor cluster; per-run 2–4 Gb/proc, 8–10 h chunks |
| square polyominoes | **n = 70** | Barequet & Ben-Shachar, ALENEX 2024 (held) | 45°-rotated bounding boxes; ~15,000 CPU-h on 32 cores, **32 GB RAM** — the rotation shrinks the signature set |
| free polyominoes | n = 59 | Shirakawa, arXiv:2510.22446 (held) | **hit the 512 GB RAM wall at ~n = 60** even with Jensen's Motzkin encoding |
| polyhexes | n = 35 | Vöge & Guttmann, Theor. Comput. Sci. 307 (2003) 433 (held) | memory |
| polyhexes | n = 50 | Jensen, arXiv:0808.0963 (held) | 64 processors, 230 Gb aggregate memory, 22,000 CPU-h |
| self-avoiding polygons | perimeter 110 | Jensen, arXiv:cond-mat/0301468 (held) | memory maximal at W = 24; improved algorithm in Clisby & Jensen, arXiv:1111.5877 |
| self-avoiding walks | n = 79 (from 71) | Jensen, arXiv:1309.6709 | memory |
| twisted cylinders (λ bound) | W = 22 | Barequet, Moffie, Ribó & Rote, INTEGERS 6 (2006) #A22 (held) | 32 GB RAM, iterate kept on disk |
| twisted cylinders (λ > 4.00253) | W = 27 | Barequet, Rote & Shalah, CACM 59(7) (2016) 88 (held) | ~450 GB RAM supercomputer, 36 h, counts squeezed to 27 bits/entry |
| **king lattice, any TM** | **— nothing external —** | | |

Every row reports the same binding resource: **RAM for the state set**, with
CPU a distant second. Nobody reports a connectivity-correctness ceiling;
every one of these engines carries a boundary connectivity state (Jensen's
Motzkin signatures, the twisted-cylinder states) — i.e. the entire
high-scale literature sits on the same side of the brief's independence bar
as the incumbent.

**The headline gap: the king lattice row is empty.** No published transfer
matrix, finite-lattice, or twisted-cylinder computation exists for polyplets
under any of its names (searched: "pseudo-polyominoes", "polyplets",
"polykings", NNN site animals; plus novelty-sortie N2/N4 which found the king
lattice absent from the entire bounds literature). External enumeration
stops at n = 18 (Tremblay–Vernay). Above that, both counts of T(n,H) that
exist in the world live in this repository. There is no external second
source to import; the independence burden stays in-house.

### 3. Exact solutions (connectivity eliminated algebraically)

- Directed site animals, square/triangular: exact, via Baxter's hard-square
  gas — Dhar, Phys. Rev. Lett. 49 (1982) 959, DOI 10.1103/PhysRevLett.49.959;
  the combinatorial route is heaps of pieces, Bousquet-Mélou & Rechnitzer,
  Discrete Math. 258 (2002) 235 (held).
- Directed king animals: exact GF, growth 3+2√2 — Bacher, arXiv:1301.1365
  (held).
- Convex / column-convex subclasses: exactly solved (Bousquet-Mélou 1996,
  held; Gouyou-Beauchamps & Leroux 2004, held).
- Full undirected animals: the method class is closed structurally — the
  anisotropic GF is not D-finite (Rechnitzer for bond animals; this repo's
  theorem for king site animals, `results/anisotropic-not-dfinite.md`), so no
  solvable-model route produces the full count. This ceiling is a theorem,
  not a resource.

### 4. The problem under other names — external computations found

- **OEIS A286139** (connected induced subgraphs of the n×n king graph):
  Resta 2017 brute force n ≤ 4, Howroyd b-file to n = 16. Probe C1 above:
  exact agreement with the repo's rule at n ≤ 9.
- **OEIS A290764** (2×n king graph): closed form a(n) = (3/4)(3^{n+1}−2n−3) —
  an exact external formula aggregating the triangle's H ≤ 2 slab over all
  cluster sizes.
- **Percolation series**: the king lattice is the square lattice's matching
  lattice for site percolation (Sykes & Essam, J. Math. Phys. 5 (1964)
  1117–1127; `results/matching-pair-convention.md`). The NNN cluster series
  of Peters et al. 1979 and Mertens 1990 (probe C2) are king animal counts by
  another community's name; they stop at s = 13.
- Not found under any name: king-lattice growth-constant bounds (N4 stands),
  king-lattice TM enumeration, king-lattice height/width triangles.

---

## Candidates the map surfaces (ranked)

### C-1. Matching-pair (Sykes–Essam) identity check — rook-side data decides king-side counts

**What**: the exact order-by-order matching identity between king-cluster and
square(rook)-cluster perimeter-refined counts, with a local Euler-
characteristic inhomogeneous term (`results/matching-pair-convention.md`
verified the convention exhaustively on the 4×4 box; unexplored-avenues
idea 2). One side of the identity is the published square-lattice perimeter
polynomials (Sykes & Glen, J. Phys. A 9 (1976) 87; Mertens 1990 to s = 22) —
enumerated by other people, under the **rook** connectivity rule.

**Region and n**: perimeter-refined king counts to the depth of the repo's
`--siteperim` data (n ≤ 14 banked; affordable extension caps at n ≈ 18 ≈
24 h on 80 dalby cores) against published rook-side data to s = 22.
**Correction 2026-08-11**: this entry originally said "extendable to
~n = 19-20 at Redelmeier cost" — priced off the pure-count kernel and ~300×
optimistic, the same wrong-kernel error as lane A's n = 20 plan. The
measured `--siteperim` calibration (n = 12/13/14 → 60.9/424.6/2964.6 s,
ratios 6.97×/6.98× stable, dalby rev 3b7359de) makes n = 19 ≈ 7 days and
n = 20 ≈ 94,000 core-hours; see the canonical file's kill row.

**Independence argument**: the king side of the check is decided by rook
enumerations plus a topological identity — connectivity never passes through
a union-find-over-a-frontier on our side of the ledger. A shared
misconception about king-connectivity in both in-house engines would break
the identity at the first affected order. **Failure mode**: an order-by-order
residual in the matching identity — disjoint from the incumbent's failure
mode (two frontier engines agreeing on a wrong rule), because the reference
data was produced under a different adjacency by a different community.

**Binding resource**: the king-side perimeter-refined enumeration is
object-materialising, so it dies at n ≈ 20-22 (the a(22) fleet arithmetic);
and the published rook-side series stop at s = 22. So this buys
definition-level certainty on n ≤ ~20 — the region the brief explicitly
values ("re-verifies cells already strip-confirmed, by a genuinely different
route") — and nothing in the tall-H frontier region.

**Overlap flag**: a `probe_matching_series.py` appeared in the shared
scratchpad during this run, so a teammate is likely probing the same identity
from the stat-mech lane. Merge in the cross-critique wave; this entry's
contribution is the coverage-map framing (which external data exists and how
deep) plus probe C2's demonstration that the external tables are clean enough
to use (one misprint, detectable and detected).

### C-2. External box-aggregate anchors (A286139 family), extended to n = 16

**What**: extend probe C1 from n = 9 to Howroyd's full n = 16 with a C++
port (state count = Motzkin(17) − 1 ≈ 2.36M by the closed form in
`results/scaling-exploration-C.md` §S4; minutes, not hours), and/or have
the strip engine emit total connected-subset counts of m×n boards for direct
comparison. Every term that matches is an external, independently-computed
anchor for the connectivity rule on boxes up to 16×16 with clusters up to 256
cells — far beyond any size at which a definition error could hide in small-n
coincidence.

**Independence argument**: honest and limited. My probe carries a partition
frontier (the incumbent's rule), so the *probe* is not independent — the
independence lives in the reference values: Resta's n ≤ 4 terms come from
`ConnectedGraphQ` over explicitly-built graphs (no frontier, no union-find
over a boundary, no stranded-component logic), and Howroyd's code is an
independent implementation outside this problem's lineage. **Failure mode**:
numeric disagreement at some box size — which would specifically indict the
connectivity rule, since arithmetic/sharding faults are already covered by
the strip agreement. **What it does not do**: verify any banked T(n,H) cell —
the aggregate needs joint (height, width) bounding-box refinement at
unbounded cluster size, which the banked triangle does not carry.

**Binding resource**: nothing — minutes of CPU. It is the cheapest purchase
on the definition axis available, and probes C1+C2 have already banked the
first nine-sixteenths of it.

### C-3. The gap itself, stated as a finding

No external second count above n = 18 exists to import, under any name, in
any adjacent literature (§2, §4). Consequence for the team: candidates must
be built, not found, and the graph-polynomial / cut-and-count lanes (A and B)
are the only routes left that touch the frontier region. The coverage map
also says what a successful candidate must beat: every method that survived
past n ≈ 25 anywhere is a frontier DP whose reported wall is RAM for the
state set — so a candidate clearing the independence bar should expect the
same wall, and should be priced against the strip engine's measured ceiling
(H = 14 at 38 GB) rather than against the incumbent's kink frontier.

---

## Kill list

| candidate | killed by |
|---|---|
| Import an external king-lattice series at n > 18 | No such publication exists: this sweep (§2, §4) + novelty-sortie N2/N4. Wikipedia "Pseudo-polyomino" cites OEIS only. |
| 45°-rotated TM (the Barequet–Ben-Shachar n=70 win) ported to king | Ruled out for king geometry: on the cut i+j=c the (i+1,j+1) neighbour is two layers ahead — `docs/dmirror-design.md` §Recommended geometry, `results/finite-lattice-crossover.md` (brief, Ground truth). Discharges the "re-derive, don't trust the note" TODO in `papers/refs-transfer-matrix.md`. And even where it works it carries the same boundary connectivity state — fails the independence bar regardless. |
| Import Jensen's Motzkin encoding / SAP-SAW algorithmics for independence | Same connectivity rule in a thinner costume (§2: every high-scale engine carries a boundary connectivity signature). Engineering for the incumbent at best; the brief's exhausted list already covers engineering. |
| Percolation-series import beyond s = 13 as a second source | Peters 1979 / Mertens 1990 stop at s = 13; the community moved to Monte Carlo (no exact counts) — probe C2 + §1. Value already extracted: definition anchor at n ≤ 13. |
| Exact-solution (Dhar / heaps / hard-square gas) route to full king counts | Structural: full-animal anisotropic GF not D-finite (`results/anisotropic-not-dfinite.md`); Dhar's correspondence is directed-only; Bacher solved the directed king case and it does not lift. |
| Redelmeier-any-flavour extension of the external anchor past n ≈ 22 | The brief's own a(22) fleet arithmetic; exhausted list. Restated here only because the map shows the whole field hit the identical wall. |

## What is NOT killed and goes to the merge wave

C-1 (matching identity: measurement plan = extend `--siteperim` depth,
assemble the identity order-by-order against Sykes–Glen/Mertens rook data);
C-2 (extend the A286139 comparison to n = 16). Neither reaches the frontier
region; both are cheap and buy certainty on the axis the brief says the
project has zero external coverage of today.

---

## Cross-critique of A (`results/second-source-candidates-A.md`), 2026-08-11

Per the brief's rule that two lanes agreeing is not evidence. One critique
probe was run (C3, arithmetic on A's own enumerator, seconds; inline script,
output quoted below).

### 1. A1's negative control does not control for the brief's error class — but the conclusion survives, for a reason A did not measure

Probe 2 deletes a diagonal pair from the adjacency set. That is the crudest
possible rule error: it perturbs the tables densely from n = 2 (4→3) and
turns the lattice into the triangular one. Detecting THAT class needs no
matching identity — it is already externally anchored by Mertens Table
IVB/A286139 (probes C1/C2). The class the brief cares about is a
carried-state bug (union-find merge, stranded-component death) that first
misfires at some larger n₀ and touches few cells — and probe 2 says nothing
about sparse, high-order errors. A's own text extrapolates ("generically
breaks every order from the first touched one") beyond what probe 2 shows.

**Probe C3** closes the gap by measurement, and the news is good for A1.
Reusing A's enumerator at M = 9: a **single-cell** +1 error in g⁸ at size n
breaks the identity at **exactly p^n**, for every n tried (4, 6, 8) — the
order-p^n coefficient picks up the raw error with binomial weight C(t,0)=1,
so no cancellation is possible for a lone cell. A deliberately
moment-cancelling ±1 pair at the same n (so the p^n coefficient survives)
still fails at p^{n+1} and every order after. The general statement, read
off the coefficient formula: the total error at size n escapes a check to
order M **iff its perimeter-moments Σδᵢ, Σδᵢtᵢ, … vanish to depth M−n**.
Detection is not "generic"; it is certain outside a measure-zero error
family. Verdict: **A1's sensitivity claim is stronger than A demonstrated —
the merged document should cite C3, not probe 2, as the sensitivity
evidence**, keeping probe 2 only as the colourful adjacency-class control.

### 2. Pricing A1's reach against the real literature (my lane's job)

The structural fact that governs everything: order p^m constrains king data
at n ≤ m only, so the check's rule-axis coverage tops out at n = M, and M is
capped by the **rook** side — all g⁴_{s,t} with t ≤ M, sizes to
((M−2)²+4)/8.

- **Held data caps M = 15.** Published square perimeter polynomials reach
  s = 22 (Mertens Table IVA + Sykes–Glen 1976 for s ≤ 17). M = 15 needs
  s ≤ 21 ✓; M = 16 needs s ≤ 25 ✗. King side to n = 15 is minutes of g2
  (n ≤ 14 already banked). So the honest **no-new-compute reach is n ≤ 15**,
  not 20–22.
- **Duarte 1981 (t ≤ 16 complete-by-perimeter) buys exactly M = 16** — and
  it is unheld, known only through Mertens's Appendix A, in Portugaliae
  Physica, which A's own search could not find. Its completeness claim is
  secondhand.
- **Conway–Guttmann 1995's series order is unread** (the paper is in
  `papers/MISSING.md`, jasonp searched it 2026-08-06, library-only). A
  correctly names it as "the number that prices A1's published-data reach" —
  which means the 20–22 reach estimate currently rests on an unobtained
  paper plus two unmeasured computations (perimeter-bounded rook growth; the
  king-side `--siteperim` runs, whose cost was subsequently MEASURED and
  killed the n = 20 plan outright — 94,000 core-hours, see the canonical
  kill row; both lanes' original king-side figures shared the wrong-kernel
  error).
- **Marginal value at n ≤ 22**: the brief's own ground-truth section says
  the one existing check that does not share the frontier rule — Redelmeier
  — already reaches n = 22 (the banked row-22 fleet run). So the p = 0
  direction of A1 adds no new n on the rule axis. What it genuinely adds
  there is **provenance** (g2 is in-house, same collaboration as the
  incumbent; the rook-side data shares no author, era, lattice, or rule with
  anything in this repo) and perimeter refinement. The genuinely *additive
  regions* of A1 are the p = 1 direction and the box-summed height-resolved
  variant — those constrain compact king animals at n > 22 and the same C_H
  family the strip engine computes. Recommendation for the merge: rank those
  as A1's headline, with the p = 0 direction as its calibration stage, and
  state the no-new-compute reach as n ≤ 15.

### 3. Independence of arrival: it was a common source, and the merge must say so

Not independent. Both lanes walked out of `results/unexplored-avenues.md`
idea 2 and `results/matching-pair-convention.md` — A's file calls A1 "the
second-source upgrade of idea 2" and my C-1 cites the same two files. This
is **one in-repo discovery reached twice**, not a two-lane confirmation.
What my lane adds to it independently is external: the coverage-map fact
that the rook-side data exists at the stated depths, and probe C2's
demonstration that the published tables are clean enough to weld to (101/102
coefficients exact, and the one misprint was caught by exactly the row-sum
gate A's K4 recommends keeping as free accounting — the A1 checker should
build those gates in).

### 4. Kill list and ranking cross-checks

- **K1 (graph-polynomial three-way kill)**: sound, and the state-count
  arithmetic is decisive. One tightening worth a line in the merge: the
  reason interpolation cannot be dodged is that the connected count is
  [y¹]Q, and extracting a y-linear coefficient is the q→0 limit of the
  Potts/spin representation, which has no integer-q evaluation and no local
  realization — carrying y symbolically forces the state to know k(S), which
  is the partition state again. The kill is by identity at both ends, not
  just by cost.
- **K2, K5–K8**: agree; K5–K8 match my map §2–§3 (independent routes: A from
  the physics literature, mine from the scale/ceiling survey — these kills
  ARE two-source).
- **K4 vs my C-2**: no conflict — K4 kills rule-blind same-lattice sum
  rules; C-2 is a value-level comparison against an external computation,
  A2-class, not a sum rule.
- **A2 is partially DELIVERED, not proposed**: my
  `results/mertens-1990-perimeter-crosscheck.md` (written after A's file)
  banks the perimeter-resolved comparison at s = 11..13 coefficient-level
  with the misprint arithmetic, plus the A286139 anchors. Remaining for
  A2's full shape: s ≤ 10 perimeter-resolved needs the paywalled [PSHL79];
  totals to n = 18 via [TV24] + the OEIS A006770 history. The merge should
  mark A2 in-progress with that residue, and add A's three MISSING wants
  (D81, PSHL79 — DOI 10.1007/BF01325205 verified in my lane — and
  Sykes–Wilkinson 1986 ×2) to `papers/MISSING.md` in the merge wave's
  shared-file pass, as A proposed.

---

## Coverage census of n ≤ 40, H ≤ 14 (jasonp's question, 2026-08-11)

What fraction of the region B1 would re-verify is already covered, and by
what. Computed from `results/ns_a40/perheight/h*.out` +
`results/ns_a40/triangle.txt` (row sums re-verified against a(n) for all 40
rows before use), provenance from `results/strip-engine.md` and
`results/redelmeier_row22/PROVENANCE.md`. Not estimates.

### 1. Cell census

The sub-rectangle {1 ≤ H ≤ min(n,14), n ≤ 40} contains **469 cells** — and
469 is exactly the strip engine's confirmed-cell count (0 mismatch,
2026-07-30 run, rev 5239e73). **The sub-rectangle is 100% strip-confirmed;
there are no kink-only cells at H ≤ 14.** (The 72.2% "honest cells" figure
in `results/strip-engine.md` is over the full 820-cell n ≤ 40 triangle; do
not mix the two denominators.)

The correct split inside the 469 is therefore not strip-vs-kink but by
**rule axis**:

| bucket | cells | granularity |
|---|---|---|
| kink + strip (shared connectivity rule) | 469/469 | per-cell |
| additionally Redelmeier-confirmed (rule-independent) | rows n ≤ 22 → 217 cells | **row-sum only** (a(n) totals; `redelmeier_row22/PROVENANCE.md` confirms every row n = 1..22, two algorithms sharing no counting logic) |
| rule-independent **per-cell** | n ≤ 9 → 45 cells | the strip Python `brute_T` anchor |
| no rule-independent constraint at all | n = 23..40, H ≤ 14 → **252 cells** | — |

### 2. Share of a(n) per bucket

Rows n ≤ 22: 100% of a(n) is rule-independent-confirmed at row-sum
granularity. Rows n = 23..40 carry **zero** rule-independent coverage today;
the share of a(n) that B1's base scope (H ≤ 14) would put under a
rule-independent count:

| n | H≤14 share of a(n) | H=15–17 share | n | H≤14 share | H=15–17 share |
|---|---|---|---|---|---|
| 23 | 94.84% | 4.90% | 32 | 70.01% | 22.41% |
| 24 | 92.95% | 6.57% | 33 | 66.71% | 24.06% |
| 25 | 90.77% | 8.42% | 34 | 63.42% | 25.53% |
| 26 | 88.32% | 10.42% | 35 | 60.17% | 26.83% |
| 27 | 85.63% | 12.49% | 36 | 56.97% | 27.95% |
| 28 | 82.74% | 14.60% | 37 | 53.84% | 28.90% |
| 29 | 79.70% | 16.68% | 38 | 50.80% | 29.66% |
| 30 | 76.54% | 18.70% | 39 | 47.85% | 30.26% |
| 31 | 73.30% | 20.62% | 40 | **45.01%** | **30.70%** |

(The n = 37..40 H ≤ 14 values reproduce `results/strip-engine.md`'s
53.8/50.8/47.9/45.0 exactly — same data, independent recomputation.)

### 3. H = 15–17 and B's stretch anchors

H = 15–17 combined rises from 4.90% of a(23) to 30.70% of a(40) (per-column
at n = 40: H15 11.23%, H16 10.41%, H17 9.06%). The six kink-only Grand
anchors B flags: T(28,15) = 7.13% of a(28), T(29,15) = 7.88% of a(29),
T(30,16) = 6.13% of a(30), T(31,16) = 6.81% of a(31), T(32,17) = 5.27% of
a(32), T(33,17) = 5.87% of a(33).

### 4. The literal answer

B1's base scope is **not** redundant, but for the opposite of the naive
reason: at H ≤ 14 every cell is already double-covered — by two engines
sharing the connectivity rule, which is exactly the coverage the brief's
ruling discounts to zero on the rule axis. What B1 buys that nothing
currently provides: rule-independent coverage of the 252 cells at
n = 23..40, H ≤ 14 — carrying 94.8% of a(23), declining to 45.0% of a(40) —
plus the first rule-independent **per-cell** (not row-sum) confirmation of
anything above n = 9, including inside the n ≤ 22 rows where Redelmeier
constrains only the totals. What it cannot buy: the H ≥ 15 majority share of
the last rows — 55.0% of a(40) stays kink-only under B1's base scope; the
H = 15–17 stretch would recover a further 30.7% of a(40) (cumulative
75.7%), leaving H ≥ 18 — 24.3% of a(40), thinning at lower n — beyond any
proposed rule-independent route. **[Update 2026-08-11, final: the window census turned out to be the right
object for B1's RAM after all (cell-at-a-time engine; the equal-cut
correction changed only the cross-engine comparison). Resolved tiers:
running binary reaches H ≤ 16 (66.7% of a(40) cumulative, 4 of 11 anchors
flip); a half-day payload re-size (96 → 40 B/area) brings H = 17 at ~72 GB
(75.7%, 6 of 11); H ≥ 18 is closed permanently — 24.3% of a(40) and the 5
anchors T(34,18)..T(38,20) stay kink-only. Tier table in the canonical
file §2.] If B1 is priced and run, the useful framing
for the close-out disclosure is: every a(n) to n = 22 rule-independent in
total, and 45–95% of each a(23)..a(40) rule-independent per cell, versus
today's 0% above n = 22.

### Loose end closed: Sykes & Wilkinson 1986 (A's objection to kill C-4)

Both pinned and read at abstract level this session; **neither touches the
nnSquare/king lattice**, confirming the "no percolation import beyond
s = 13" kill:

- Sykes & Wilkinson, "Generating functions for connected embeddings in a
  lattice: V. Application to the simple cubic and body-centred cubic
  lattices," J. Phys. A 19 (1986) 3407–3414, DOI 10.1088/0305-4470/19/16/035
  — title settles it; consistent with Mertens citing it only for a cubic
  g₁₃ value (his footnote at Table area, p. 1097).
- Sykes & Wilkinson, "Derivation of series expansions for a study of
  percolation processes," J. Phys. A 19 (1986) 3415–3424, DOI
  10.1088/0305-4470/19/16/036 — abstract read (IOP): site and bond mixtures
  on the simple cubic and BCC lattices only.

They need not be obtained and should NOT be added to `papers/MISSING.md`;
Mertens's own Appendix text stands: the only pre-1990 nnSquare source is
Peters et al. 1979 [PSHL79].

## References not held and not resolvable from the desk

None added to `papers/MISSING.md` by this lane — every citation above is
either a held PDF, an OEIS entry, or carries a DOI/arXiv id verified this
session (Peters et al. 1979: DOI 10.1007/BF01325205, confirmed; Dhar 1982:
DOI 10.1103/PhysRevLett.49.959, confirmed; Sykes & Essam 1964: J. Math.
Phys. 5, 1117–1127, ADS 1964JMP.....5.1117S, confirmed).
