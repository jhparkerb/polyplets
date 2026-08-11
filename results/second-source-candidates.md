# Second-source candidates — merged findings of the three-lane sweep

2026-08-11. The canonical deliverable of `docs/second-source-team-brief.md`,
synthesised from the three lane files, which remain the working record:

- `results/second-source-candidates-A.md` — enumeration & statistical
  mechanics (graph polynomials, percolation identities)
- `results/second-source-candidates-B.md` — model counting & parameterised
  algorithms (cut-and-count, pathwidth, certified compilation)
- `results/second-source-candidates-C.md` — coverage map of adjacent
  literatures + the problem under other names; cross-critique of A;
  coverage census

Status: the ranked candidate list is **pending** one contested question
between lanes A and B (§5). Everything else below is settled across lanes.

---

## 1. What "independent" means here (the brief's ruling, restated)

The project has two engines that agree perfectly: the kink NW-carry kernel
that produced the banked triangle, and the strip transfer matrix
(`results/strip-engine.md`) that re-computed all of it at H ≤ 14, n ≤ 40 with
zero mismatches. **That agreement is a consistency check, not verification**,
because both engines decide connectivity by the same rule — union-find over
frontier labels with stranded-component death, the same rule as the reference
oracle `core/transition.h`. Different code, author, and language on both
sides notwithstanding, a shared misconception about king-connectivity passes
through both untouched and shows up as agreement.

So the bar for a second source is not a different encoding, frontier shape,
or machine — it is **a different mechanism for deciding connectivity**:
inclusion–exclusion over cuts, spanning-structure algebra, a graded algebraic
carrier, a model-counting formulation where connectivity is a constraint
rather than a carried state. Every candidate below states the failure mode it
would exhibit if wrong, and why that failure mode is disjoint from
union-find-over-a-frontier's. Rank is by certainty bought over the banked
triangle, not by reach; a(40) is the final term and nothing past it has
value.

## 2. What actually needs verifying: the coverage census

Computed from the banked per-height data (`results/ns_a40/perheight/`,
row sums re-verified against a(n) for all 40 rows); details and the per-n
table in `results/second-source-candidates-C.md` §census.

- The sub-rectangle {H ≤ 14, n ≤ 40} is **469 cells and is 100%
  strip-confirmed — there are no kink-only cells at H ≤ 14**. But that is
  double coverage by two engines sharing the rule, which §1 values at zero on
  the rule axis.
- **Rule-independent** coverage today: rows n ≤ 22 at **row-sum granularity
  only** (the Redelmeier fleet campaign, `results/redelmeier_row22/
  PROVENANCE.md`); per-cell only to n = 9 (the strip's brute anchor). The
  **252 cells at n = 23..40, H ≤ 14 carry no rule-independent constraint at
  all**, and they hold 94.8% of a(23), declining monotonically to 45.0% of
  a(40).
- H = 15–17 holds a further 4.9% of a(23) rising to 30.7% of a(40); the six
  kink-only Grand anchors T(28,15)..T(33,17) carry 5.3–7.9% of their rows.
- Ceiling of the entire program — **RESOLVED 2026-08-11 (B's re-size)**. The
  revision closed both ways: B1's RAM is genuinely priced by the mid-column
  WINDOW census (the engine is cell-at-a-time and its hash table holds the
  window at every step — A's column-cut correction changed the cross-engine
  comparison, not the memory), so the running binary's ceiling stands at
  H = 16; but the re-size found real slack — the I256 coefficients are
  over-provisioned (C_H(n) ≤ H·a(n) < 2^127, and the wrapping-ring argument
  for mod-2^256 justifies mod-2^128 identically; the binomial self-check
  coefficient moves to a 63-bit prime), dropping the payload 96 → 40 B per
  area-slot and bringing H = 17 back at ~72 GB. Three tiers:

  | tier | needs | share of a(40) rule-independent, cumulative | kink-only Grand anchors flipped |
  |---|---|---|---|
  | H ≤ 14 (base) | production run | 45.0% | 0 of 11 |
  | H ≤ 16 | running binary | 66.6% | 4: T(28,15) 7.1%, T(29,15) 7.9%, T(30,16) 6.1%, T(31,16) 6.8% of their rows |
  | H ≤ 17 | half-day payload change (u128 + prime check) + ~a day of dalby — the wall figure is an extrapolation from the measured 34.2 s/column at H = 14, held UNFIRMED until tonight's measured H = 15/16 walls | 75.7% | 6, adding T(32,17) 5.3%, T(33,17) 5.9% |
  | H ≥ 18 | ~210 GB — **closed permanently** | 24.3% of a(40) stays kink-only | T(34,18)..T(38,20), 5 anchors, never |

  Whether H = 17 is worth the code change is jasonp's call once the H = 16
  verdict and measured walls are in. The honest close-out floor, independent
  of tier: every a(n) to n = 22 rule-independent in total, 45–95% of each
  a(23)..a(40) rule-independent per cell at H ≤ 14, versus 0% above n = 22
  today.

## 3. The geometry axis is closed; only the rule axis is open

Lane B settled the brief's assigned open question: **pw(P_m ⊠ P_n) = m + 1
at every probed size** (exact vertex-separation DP, m = 2..5), with
m ≤ pw ≤ m + 1 proved in general (grid-minor lower bound via [Bod98] +
[Kin92]; two-line column-major layout upper bound). The kink frontier's
width is exactly m + 1 — **the kink already sits at the graph's pathwidth**,
so no frontier geometry can beat its state ceiling on the same rule; the
whole-column strip scan does not achieve pathwidth and wins by state
compression instead. No literature source states the exact value (searched;
recorded in `papers/MISSING.md`). Consequence: every remaining candidate
differs on the rule, not the frontier.

## 4. External definition anchors (delivered during the sweep)

Banked in `results/mertens-1990-perimeter-crosscheck.md`:

- **Mertens 1990 Table IVB** (NNN-square = king perimeter polynomials,
  s = 11..13, computed 1990, independent author/implementation/community):
  101 of 102 nonzero coefficients match the banked
  `results/siteperim_square8_n14.txt` exactly; the single disagreement at
  (s = 12, t = 39) is provably Mertens' misprint — his own column sum breaks
  against multi-source a(12) by exactly the cell delta, and the printed digit
  was confirmed visually.
- **OEIS A286139** (connected induced subgraphs of the n×n king graph;
  Resta brute force n ≤ 4 via `ConnectedGraphQ` — no frontier, no union-find
  — plus Howroyd's independent b-file to n = 16): a repo-rule DP matches all
  nine terms computable in the probe box (n ≤ 9, clusters to 81 cells).

These anchor the *definition* of king-connectivity externally. They do not
verify any T(n,H) cell (different gradings). Residue worth an afternoon:
extend the A286139 comparison to n = 16 in C++; obtain Peters et al. 1979
for the s ≤ 10 perimeter-resolved rows (`papers/MISSING.md`).

## 5. Ranked candidate list

The A/B collision is resolved: A attacked B1 and conceded (lane A file,
"Cross-critique of B" — read it for the full reasoning). A reimplemented the
DP from B's stated rules with independent canonicalization and bookkeeping,
matched B's state counts at every H = 4..10, matched [q¹] against its own
floodfill brute force at 3×4, 2×6, and 4×4 (beyond B's validation set), and
verified the no-join claim against the code: a cell adjacent to ≥2 blocks is
weight-zeroed and the branch dropped, aged-out classes vanish with no
verdict, and disconnected subsets cancel out of [q¹] by signed
falling-factorial algebra. A's K1 is SUPERSEDED with respect to this
formulation, and A retracted its "no local realization" claim.

**Naming, precisely** (A's correction, adopted throughout): mechanically this
engine is the **colour-symmetrized spin-representation transfer matrix with
clash-zeroing**, computed exactly in ℤ[q]/(q²). It is NOT the
Fortuin–Kasteleyn / random-cluster TM — the FK TM joins partitions, which is
precisely the misreading that produced the original kill. [SS01] and [BCKN15]
stand as lineage only.

### 1. B1 — colour-symmetrized spin TM, connectivity as the [q¹] coefficient

- **Region and n**: all columns H ≤ 14 at every n ≤ 40 — the 252
  rule-axis-uncovered cells of §2 plus per-cell coverage inside n ≤ 22.
  Stretch: H = 15/16 are inside the running job — if clean, T(28,15),
  T(29,15), T(30,16), T(31,16) become two-source, adding 21.6% of a(40).
  H = 17 is reachable with a half-day payload change (§2 tier table);
  H ≥ 18 closed permanently.
- **Independence**: connectivity is never decided — no union verdict, no
  stranded-component death; every subset flows through and the connected
  count is read once, at the end, as a coefficient of a graded algebra.
  **Failure mode**: an error in the fresh-colour weight (q − b), the
  truncation, or block canonicalization — corrupting the whole graded family
  jointly, which is over-determined ([q⁰] = 0 identically; A_n(1) = C(HW, n),
  a binomial identity no connectivity code touches; N_{n,2}, N_{n,3}
  brute-checkable at small n). Disjoint from union-find-with-death by
  construction. Two independent implementations of the stated rules agree
  with brute force.
- **Cost — the equal-cut comparison (headline, corrected 2026-08-11)**: on
  the SAME column cut, B1's states are 20, 50, 126, 323, 843, 2242
  (H = 4..9) against the incumbent's 20, 50, 126, 322, 834, 2187 — and the
  structure is exact, not fitted (lane A): B1's column states are ALL set
  partitions of the occupied runs, Σ_k C(H+1,2k)·Bell(k); the incumbent's
  are the non-crossing ones, Σ_k C(H+1,2k)·Catalan(k) = Motzkin(H+1) − 1.
  **The price of rule-independence is Bell-over-Catalan**: ×1.047 at
  H = 10, ×1.243 at H = 14, ×2.349 at H = 21 — percent-level at the working
  heights, growing at the frontier, and not a growth-base change (both
  engines' asymptotic column base is Motzkin's 3; the banked "2.65" is the
  local ratio near H ≈ 10). **Cut-confusion warning, so nobody re-derives
  the wrong number**: the earlier "2.72 → 2.90, ~2.9×/height" ratio
  sequence and the census 107,241 / 306,858 / 891,074 (H = 12/13/14)
  measure B1's mid-column WINDOW states — a different, larger cut — and
  must not be compared against the strip's column-cut census; they remain
  correct as window-cut figures (A's blind window-cut prediction of
  ~9×10⁵ ± 30% landed on the measured 891,074 — two lanes agreeing on a
  number neither could look up). **Memory sizing RESOLVED (B)**: the window
  census is the right object for RAM after all — the engine's hash table
  holds the H+1-cell window at every step — so the equal-cut correction
  changes only the cross-engine comparison. Running-binary ceiling H = 16
  (H = 17 ~170 GB at the current 96 B/area payload); the payload re-size to
  wrapping u128 + a 63-bit-prime check coefficient (40 B/area, justified by
  C_H(n) < 2^127 and the same wrapping-ring argument) brings H = 17 back at
  ~72 GB; H = 18 ~210 GB, dead regardless. Tier table in §2. Run status at
  filing: 13/13 heights `q0_zero=OK q1eval_binomial=OK (n=1..40)`,
  mid-H = 14, heartbeat states = 891,074 matching the census exactly.
  Binding resource: RAM for the coefficient payload, then bigint
  throughput; strip C₁₄ for scale: 38 GB, 8.6 h dalby.
- **Validation basis** (the strongest evidence in this document, two
  independent halves): (i) A's from-the-rules reimplementation — separate
  canonicalization and bookkeeping — matches the state counts at every
  H = 4..10 and matches [q¹] against A's own floodfill brute force beyond
  B's validation set; (ii) B's C++ engine reproduces the banked triangle
  exactly at H ≤ 6, n ≤ 14 (84/84) and H ≤ 10, n ≤ 40 (**400/400**, 4.0 s
  single-threaded, 91 MB peak). The run also carries a third payload
  coefficient (the polynomial at q = 1) and logs per height
  `q0_zero=OK q1eval_binomial=OK (n=1..40)` — checking the q = 1 value
  against C(HW, n) − C(H(W−1), n) computed by Pascal in the same wrapping
  ring, an exact identity containing no connectivity anywhere, with fatal
  exit on violation. That is a self-check the engine cannot pass by sharing
  the incumbent's blind spot, and it is logged by the run rather than
  asserted in the design.
- **Shared surface, honestly**: the king-adjacency definition and the
  accounting layer — exactly the axes §4's external anchors and the matching
  identity cover. B1 and the matching identity are complementary, each
  covering the other's conceded axis, not competitors.

### 2. B2 — certified knowledge compilation: DECLINED by jasonp, 2026-08-11

Recorded as a closed door so it is not re-proposed. The mechanism (d-DNNF +
CPOG with the Lean 4 verified checker [BNAH23]; trusted base = definitional
CNF generator + verified checker, no connectivity rule trusted) was the
first concrete proposal for the brief's outcome 2. Declined by decision:
its ceiling is DP-trace-sized certificates [BCMS16], reaching n ≲ 20,
H ≲ 10 — cells already three-way confirmed — so it buys a different *kind*
of warrant on the best-covered region and can never touch the kink-only
anchors. jasonp's words: not confident we SAT our way to a(40). **What dies
with it: outcome 2 (a tier-3 exact-arithmetic certificate) is again open
with no live mechanism.**

### 3. Sykes–Essam matching identity — a measurement plan, ranked below B1

Not a sized candidate (A's own demotion, accepted): the live parts — the
p → 1 direction and the box-summed height-resolved variant, both taking
their king side from a perimeter-graded strip TM — are contingent on
unprobed numbers. The p → 0 direction is reduced to an external-definition
adjunct at n ≤ ~16, zero new compute, off Duarte's print (at affordable n
it is redundant with the row-22 run on the rule axis and nearly so with
probe C2 on the definition axis; n = 20 is dead — §7 kill row). External
anchor range, corrected: **n ≤ 13–16** (13 coefficient-level via Mertens,
~16 via Duarte), not 13–21. Covers what B1 concedes: the adjacency
definition, against data no in-house rule touches. Partially delivered
already via §4.

### 4. External-anchor residue (A2/C)

Extend the A286139 comparison to Howroyd's n = 16 (minutes of C++); the
s ≤ 10 perimeter-resolved layer via [PSHL79] when obtained; totals to n = 18
via [TV24] + OEIS history. Cheapest certainty on the definition axis;
`results/mertens-1990-perimeter-crosscheck.md` is the pattern to extend.

## 6. The Sykes–Essam matching identity, presented once

Both lanes A and C proposed this. **The arrival was a common source, not
independent convergence** — both walked out of the repo's own
`results/unexplored-avenues.md` idea 2 and `results/matching-pair-convention.md`
— so the double proposal carries no evidential weight (the brief's own rule).
Merged statement:

**Mechanism** (lane A). The king lattice is the matching lattice of ℤ² for
site percolation [SE64]. The mean cluster-number densities satisfy the exact
identity K_8(p) − K_4(1−p) = p − 4p² + 4p³ − p⁴, where K_8 sums fixed king
animals by (size, king site-perimeter) and K_4 sums fixed polyominoes by
(size, rook site-perimeter); the right side is a local Euler-characteristic
count verified exhaustively at 4×4 in-repo. Order p^m is one exact integer
sum rule tying the king table at n ≤ m to the rook table at t ≤ m.

**Validation** (lane A, probe GREEN): both sides enumerated from scratch,
identity holds through p⁹, totals match Mertens Table I and A001168.

**Sensitivity** (lane C, critique probe C3 — supersedes A's wrong-adjacency
control as the evidence): a single-cell error in the king table at size n
breaks the identity at exactly p^n; a moment-cancelling ±1 pair at the same n
still breaks at p^{n+1}. In general an error at size n escapes a check to
order M iff its perimeter-moments vanish to depth M − n — detection is
certain outside a measure-zero error family, stronger than "generic".

**Independence**: the rook side is 4-connectivity data produced by other
authors, methods, and decades ([D81] t ≤ 16; [M90] square D_s to s = 22;
[CG95] FLM series); no king rule of any kind touches it. Failure mode: an
order-by-order integer residual at the first affected order — disjoint from
two frontier engines agreeing on a shared wrong rule.

**Reach, corrected twice** (lane C's pricing + lane A's perimeter-
completeness refinement, both accepted): the rook side of order M needs all
g⁴_{s,t} with **t ≤ M** — perimeter-graded, not size-graded. A size-s table
is t-complete only up to the minimum perimeter of size s+1, so Mertens's
s = 22 buys complete rook data to t = 15, and the two pricings agree:
**no-new-compute reach is M = 15**; M = 16 is unlocked only by the unheld
[D81] (all g_{s,t} for t ≤ 16, completeness known secondhand via Mertens's
Appendix A); anything beyond rests on the unread [CG95] plus unmeasured
enumerations on both sides. **The p → 0 direction is now demoted outright**:
its king side at n = 20 is killed by measurement (§7 kill row — 94,000
core-hours, not 2.6 fleet-hours; both A's and C's earlier n ≈ 19–22
king-side reach figures used the wrong kernel's throughput), and at the
affordable n ≤ 18 it is redundant on the rule axis (row-22 Redelmeier) and
nearly so on the definition axis (probe C2, Duarte). The candidate's live
content is the **p → 1 direction** (king compact side, small t at unbounded
n — reaches n > 22) and the **box-summed height-resolved variant**
(constrains the same C_H family the strip engine computes; meets C-2's
A290764 anchor at H = 2) — neither probed yet; they are the first steps of
the measurement plan in lane A's file.

## 7. Merged kill list

Deduplicated across lanes. "Two-source" = reached independently by two lanes
via different routes (the only agreements this brief counts); entries without
the mark rest on one lane's probe or citation. Brief-exhausted items
(mod-p/CRT, Burnside, Redelmeier variants, engineering negatives, …) are not
re-listed.

| candidate | verdict | killed by | lanes |
|---|---|---|---|
| Potts / graph-polynomial route, three named formulations: integer-q interpolation, partition-basis ("colour-symmetrized" in the Bell-number sense), treewidth-DP forms | killed as named; **kill of the family SUPERSEDED by B1** | A's K1 arithmetic stands against those three (22¹⁴ ≈ 6×10¹⁸ states at H=14 n=20; Bell(15) ≈ 1.4×10⁹; partition-join = union-find). B1's ℤ[q]/(q²) truncation is a fourth member that evades all three — resolved 2026-08-11, A conceded after independent reimplementation (lane A "Cross-critique of B"); B1 is §5 rank 1. | A, B |
| A1's p → 0 direction via `g2 --siteperim` at n = 20 | killed | Measured, three calibration points on dalby 2026-08-11 (`./build/g2 square8 N --siteperim`, rev 3b7359de — tracked tree clean, the `-dirty` stamp is untracked result files — single-threaded, peak RSS 2.6 MB): n=12 → 60.9 s, n=13 → 424.6 s, n=14 → 2964.6 s; ratios 6.97× then 6.98×, stable ⇒ n=20 ≈ 3.4×10⁸ core-s ≈ 94,000 core-h ≈ 49 days on all 80 dalby cores (n=19 ≈ 7 days, n=18 ≈ 24 h). The original 2.6-fleet-hour figure was priced off the pure-count kernel (~10⁸ objects/s); `--siteperim` runs at ~3×10⁶/s — lane C's "n ≈ 19–20 at Redelmeier cost" carried the same wrong-kernel error, corrected in its file. At the affordable n ≤ 18 the direction is redundant on the rule axis (row-22 Redelmeier) and nearly so on the definition axis (probe C2 to n = 13, Duarte's print to ~16). Lane A's K9 matches. | measured (lead) + A + C |
| Tutte / reliability polynomial specialisations | killed | [TAM11]: connected *induced vertex* subsets are not a Tutte/Rel specialisation — that is why Q(x,y) exists and is provably not Tutte-determined. | A |
| Matrix-tree / Grassmann spanning-structure algebra | killed as stated; algebraic residue lives in B1 | A's K3: no linear functional of spanning-tree counts isolates [κ ≥ 1]; the mod-2 isolation repair *is* cut-and-count. | A → B |
| Cut-and-count proper [CNP+11] | killed (as a counter) | B's K3: Monte-Carlo mod-2 decision, not exact counting; its exact descendant is B1. | B |
| Rank-based / representative-set counting [BCKN15] | folded into B1 | B's K2: row reduction is unsound for exact counting; BCKN's counting variant is determinants over the cut space = B1. | B |
| ZDD / frontier-based search (simpath, [KIIM17]) | killed | B's K1: the "mate" array is the frontier partition with death bookkeeping — the incumbent's rule compressed. | B |
| Generic pathwidth/treewidth partition DP | killed | B's probe P0 + [KN25]: kink already at exact pathwidth; pure DP provably cannot escape partition-type state. | B |
| #SAT model counters as a *reach* instrument | killed; survives only as B2's substrate | B's probe P1 (no counter on the fleet) + [BCMS16] (component cache ≥ frontier-behavior count). | B |
| First-component peel / inclusion–exclusion recursion | killed | B's K6: shape-indexed recursion is object-materialising or becomes a frontier DP. | B |
| Exact-solution routes (Temperley strata, kernel method, heaps, Dhar hard-square gas, Bacher directed-king) | killed | Structural theorems in-repo: anisotropic GF not D-finite, T(n,H) not 2D-holonomic; Dhar/Bacher are directed-only. | **two-source: A (K7, physics lit) + C (map §3)** |
| FLM as accounting-layer independence | killed on the rule axis (per the brief's required distinction) | A's K5 + brief: each rectangle still runs a column TM with the shared rule; reach already closed in `results/finite-lattice-crossover.md`. Only live use: wrapper for a rule-independent in-rectangle counter. | **two-source: A + C (map §2)** |
| Corner transfer matrices (Chan–Rechnitzer) | killed | Read-negative in-repo: fails locality/symmetry; approximates free energies, no exact integers. | A (repo citations) |
| Series analysis (differential approximants, ratio methods) | killed | A's K8: confidence intervals are out of scope by the brief's standard. | A |
| Same-lattice sum rules / partition-of-unity moments | killed as evidence; kept as free accounting gates | A's K4: rule-blind — they hold for any consistent partition of sites. (No conflict with §4's anchors, which are value-level external comparisons.) | A |
| Import an external king-lattice series above n = 18 | killed | C's map: no such publication exists under any name (polyplets, pseudo-polyominoes, polykings, NNN site animals, king-graph subgraphs); external enumeration stops at Tremblay–Vernay's n = 18. | C |
| Percolation-series import beyond s = 13 | killed | C's map + closure of A's objection: Sykes–Wilkinson 1986 (19:3407, 19:3415; DOIs 10.1088/0305-4470/19/16/035, /036) are simple-cubic/BCC only — abstracts read. Peters 1979 / Mertens 1990 end the nnSquare series record at s = 13. | C |
| 45°-rotated TM (Barequet–Ben-Shachar n = 70 win) ported to king | killed | `docs/dmirror-design.md` + `results/finite-lattice-crossover.md` (diagonal cut needs extra depth on king); shares the rule regardless. Discharges the "re-derive" TODO in `papers/refs-transfer-matrix.md`. | C (repo citations) |
| Motzkin-encoding / SAP-SAW algorithmic imports for independence | killed | C's map §2: every high-scale engine in the field carries a boundary connectivity state — engineering for the incumbent at best. | C (concurring: B's K4 theorem cover) |

## 8. Consolidated citations (load-bearing in this file)

Lane files carry the full lists; everything here is held or resolves.

- [SE64] Sykes & Essam, "Exact critical percolation probabilities for site
  and bond problems in two dimensions," J. Math. Phys. 5 (1964) 1117–1127.
  DOI 10.1063/1.1704215.
- [M90] Mertens, J. Stat. Phys. 58 (1990) 1095–1108. DOI 10.1007/BF01026565.
  Held: `papers/mertens_1990_lattice_animals.pdf`.
- [D81] Duarte, Portgal. Phys. 12 (1981) 99 — unheld, known via [M90] ref 14;
  `papers/MISSING.md`.
- [CG95] Conway & Guttmann, J. Phys. A 28 (1995) 891–904. DOI
  10.1088/0305-4470/28/4/015 — unheld; `papers/MISSING.md` (annotated: its
  series order prices §6's reach).
- [PSHL79] Peters, Stauffer, Hölters & Loewenich, Z. Phys. B 34 (1979) 399.
  DOI 10.1007/BF01325205 — unheld; `papers/MISSING.md`.
- [TAM11] Tittmann, Averbouch & Makowsky, European J. Combin. 32 (2011)
  954–974. DOI 10.1016/j.ejc.2011.03.017; arXiv:0812.4147.
- [CNP+11] Cygan et al., FOCS 2011. arXiv:1103.0534.
- [BCKN15] Bodlaender, Cygan, Kratsch & Nederlof, Inform. and Comput. 243
  (2015). arXiv:1211.1505.
- [KN25] Kluk & Nederlof, arXiv:2512.23121.
- [BNAH23] Bryant, Nawrocki, Avigad & Heule, SAT 2023.
  DOI 10.4230/LIPIcs.SAT.2023.6; arXiv:2501.12906.
- [BCMS16] Bova, Capelli, Mengel & Slivovsky, IJCAI 2016.
- [KIIM17] Kawahara, Inoue, Iwashita & Minato, IEICE Trans. Fundamentals
  E100-A(9) (2017). DOI 10.1587/transfun.E100.A.1773.
- [Kin92] Kinnersley, Inf. Process. Lett. 42 (1992) 345–350.
  DOI 10.1016/0020-0190(92)90234-M.
- [Bod98] Bodlaender, Theoret. Comput. Sci. 209 (1998) 1–45.
  DOI 10.1016/S0304-3975(97)00228-4.
- OEIS A286139, A290764, A006770, A001168; Sykes–Wilkinson 1986 DOIs in §7.

## 9. Needs jasonp's decision (carried from the lanes)

1. ~~B1 go/no-go~~ — approved, calibrated, and running (`cpp/cutcount_b1.cpp`;
   validation, census, and tier table in §5/§2). Remaining decision:
   **whether H = 17 is worth the half-day payload change** (buys 2 more
   anchors and 9.1% of a(40)) — his call once the H = 16 verdict and the
   measured H = 15/16 walls land. H ≥ 18 needs no decision; it is closed.
2. ~~B2 toolchain~~ — **DECLINED by jasonp 2026-08-11** (§5.2). With it,
   outcome 2 (tier-3 certificate) has no live mechanism.
3. (folded into 1.)
4. Matching-identity plan: the two 15-minute probes (p → 1 direction,
   box-summed variant) are free-rein. The g2 `--siteperim` n = 20 run is
   DEAD — killed by measurement (§7), do not re-propose.
