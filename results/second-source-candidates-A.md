# Second-source candidates — lane A (enumeration & statistical mechanics)

2026-08-11, Teammate A of the second-source team (`docs/second-source-team-brief.md`).
Lane: lattice-animal enumeration, series-expansion methods, finite lattice method,
physics transfer matrices, graph polynomials. All probes run this session on gympie,
each well inside the 15-minute box; scripts named below. Nothing here is committed.

The lane's summary up front: the graph-polynomial end (Tutte/Potts/reliability),
which the brief flagged as the most likely to clear the bar, is dead — every exact
algebraic formulation of "count connected induced subgraphs" reduces either to a
partition-carrying DP (the incumbent rule in another costume) or to an interpolation
whose state space is measured astronomically worse (kill list, K1). What survives
from this lane is the *percolation* end: the Sykes–Essam matching identity, which
ties king-connectivity counts to rook-connectivity counts computed by other people,
on another lattice, decades before this project existed. That is the one mechanism
found here in which the king connectivity rule is *tested against data that never
ran any king rule*.

---

## Ranked candidates

### A1. Sykes–Essam matching identity: king animals against published square-lattice data

**The mechanism.** The king lattice is the matching lattice of Z² for site
percolation. For the matching pair (rook foreground, king background) the mean
cluster-number densities satisfy the exact identity

    K_8(p) − K_4(1−p) = p − 4p² + 4p³ − p⁴

where `K_8(p) = Σ g⁸_{n,t} pⁿ(1−p)ᵗ` sums over fixed polyplets (king-connected
animals) with king site-perimeter t, and `K_4` likewise over fixed polyominoes with
rook site-perimeter. The right-hand polynomial is a local Euler-characteristic count
— already derived and exhaustively verified over all 65535 subsets of a 4×4 box in
`results/matching-pair-convention.md` (this candidate is the second-source upgrade
of idea 2 of `results/unexplored-avenues.md`; the convention groundwork is done).
The identity's source is Sykes & Essam 1964 [SE64].

Order p^m of the identity is one exact integer linear equation relating the king
perimeter table {g⁸_{n,t} : n ≤ m} to the rook perimeter table {g⁴_{s,t} : t ≤ m}
(rook site-perimeter t bounds size, s ≤ ((t−2)²+4)/8, so each order needs only a
finite rook set).

**Probe 1 (GREEN, `experiments/matching_series_probe.py`, 5.1 s).** Both sides
enumerated from scratch (independent Redelmeier with perimeter tracking, ~100 lines
Python, no repo code): the identity holds order by order through p⁹, with the king
totals matching Mertens 1990 Table I (1, 4, 20, 110, 638, 3832, 23592, 147941,
940982) and the rook totals matching A001168.

**Probe 2 (sensitivity, same script, KING minus one diagonal pair).** With a
deliberately wrong king adjacency the identity FAILS at p² (LHS −3 vs RHS −4), and
keeps failing at p³, p⁵, p⁶. (Instructive side effect: the wrong-rule counts come
out 1, 3, 11, 44, 186, 814 — exactly Mertens's triangular-lattice column, since
square+one-diagonal is the triangular lattice.) So the check detects a
connectivity-rule error at the first order the error touches.

**Independence argument, on the connectivity-rule axis specifically.** Three layers,
none of which runs the union-find-over-a-frontier rule:

1. The rook-side data is 4-connectivity, produced by other authors with other
   methods before this project existed: Duarte 1981 has all square g_{s,t} for
   t ≤ 16 [D81]; Mertens 1990 Table IVA extends square perimeter polynomials to
   s = 22 [M90]; Conway–Guttmann 1995 has square site high-density series by the
   finite lattice method [CG95]. A misconception about *king* connectivity cannot
   infect any of it.
2. The inhomogeneous polynomial p − 4p² + 4p³ − p⁴ is a theorem of local counting
   (densities of cells, king edges, king triangles, 2×2 blocks), verified
   exhaustively at 4×4 in-repo, no engine involved. It is short enough to be a Lean
   target if wanted.
3. The failure mode is disjoint by construction: the incumbent engines fail by
   producing wrong integers out of a shared frontier rule; this check consumes those
   integers against foreign-lattice data through an identity that the wrong-rule
   probe shows breaks at the first affected order. There is no shared code, author,
   lattice, era, or rule with the thing being tested.

**What it verifies, honestly scoped.** One linear equation per order, so it is a
sum-rule check on the perimeter-refined tables, not a per-cell verification: an
adversarial error tuned to the checked functionals would pass, but the target class
— a *systematic* shared rule error, the class the brief says the strip engine cannot
catch — perturbs whole tables and generically breaks every order from the first
touched one (probe 2). Row sums Σ_t g⁸_{n,t} = a(n) tie the checked tables to the
banked triangle.

**Region and n.** Two expansion directions:

- About p = 0: verifies king data at n ≤ M, all heights aggregated. **Pricing
  CORRECTED 2026-08-11 (measured, was ~300× off).** The original figures here
  (n = 20 ≈ 2.6 fleet-hours) were scaled off the banked a(22) fleet run — the
  wrong kernel: that run used the Terminal Velocity pure-count kernel
  (~10⁸ objects/s), while `--siteperim` does per-object perimeter bookkeeping
  (~3×10⁶/s). Team-lead calibration on dalby (`./build/g2 square8 N --siteperim`,
  single-threaded, rev 3b7359de, tracked tree clean, 2026-08-11): n = 12 →
  60.9 s, n = 13 → 424.6 s, ratio 6.97×. At the measured curve: n = 18 ≈ 24 h on
  all 80 dalby cores, n = 19 ≈ 7 days, n = 20 ≈ 49 days (~94,000 core-hours).
  **So this direction stops at n ≈ 18 on current hardware — inside the range the
  banked row-22 Redelmeier run already covers on the rule axis** — and its
  residual value is only the external-definition axis, which C's probe C2 has
  already banked at n ≤ 13 and Duarte's t ≤ 16 print extends to at most n ≈ 16.
  A modest A2-grade adjunct, no longer A1's payload. Rook side to t ≤ 22 needs
  sizes to s ≤ 50 in a perimeter-bounded (compact-animal) enumeration — Duarte
  reached t ≤ 16 on 1981 hardware, so t ≤ 22 is plausible but unmeasured (plan
  below).
- About p = 1 (roles swap): verifies the king *compact* side — g⁸_{n,t} for t ≤ M
  at unbounded n — against square-by-size data published to s = 22 perimeter-refined
  [M90] (sizes to 70 unrefined, Barequet–Ben-Shachar, `papers/
  counting_polyominoes_revisited.pdf`). Every king animal with t ≤ ~30 has both box
  dimensions ≤ ~15, so this side is inside strip-engine geometry if the strip TM is
  given a perimeter grade.

- **Height-resolved refinement.** The Euler identities hold pointwise on any finite
  box (that is what the repo's 4×4 census established), so summing them with
  p-weights over an H×L box gives an exact identity per box: E_p[C_8] − E_p[H_4] =
  |box|·p − (#king edges)p² + (#king triangles)p³ − (#2×2 blocks)p⁴. The king term
  is the height-≤H strip object graded by size and box-clipped perimeter — i.e. this
  version constrains per-height data, the same C_H family the strip engine computes,
  at every order n ≤ M. Not probed this session; first step of the plan.

**Binding resource.** Corrected with the calibration above: king D_n(q) has no
affordable producer past n ≈ 18 (`--siteperim` measured at ~3×10⁶ objects/s;
n = 19 ≈ 7 dalby-days), so the p = 0 direction is capped there, redundantly with
the row-22 run. For the surviving directions the binder is the perimeter-bounded
enumeration growth (both lattices, unmeasured) and the cost of a perimeter grade
on the strip TM (unmeasured).

**Re-ranking after the calibration (2026-08-11).** What A1 has left:

- *Live*: the p → 1 direction and the height-resolved box variant. Both take
  their king side from a perimeter-graded strip TM (compact king animals, t ≤ M,
  fit in H ≤ ~15 for M ≤ ~30 — strip geometry), not from g2, so the measured g2
  kill does not touch them; the box variant is the only version that constrains
  per-height data. Both were flagged unprobed at filing and stay that way: live
  *contingent on* measurement-plan items (i)/(ii) plus a perimeter-grade cost
  probe on the strip TM. Until those numbers exist this is a measurement plan,
  not a sized candidate.
- *Speculative / demoted*: the p = 0 direction past what print affords — reduced
  to an A2-grade external-definition adjunct at n ≤ ~16 (Duarte's t ≤ 16), sized
  at zero new compute.

**Measurement plan (cannot be killed cheaply; per brief, stated instead of a
verdict).** (i) 15-min probe: count square animals with t ≤ T for T = 12…16 by
perimeter-bounded Redelmeier, confirm against Duarte via Mertens's citation, fit the
growth rate, price T = 22 — and the king twin of the same probe for the p → 1 side.
(ii) 15-min probe: the box-summed identity at H = 3, L ≤ 6 against brute force.
(iii) ~~One g2 `--siteperim` run at n = 20~~ **CLOSED BY MEASUREMENT 2026-08-11 —
killed; see K9.** (iv) new: measure the state/wall multiplier of a perimeter grade
(q-polynomial payload) on the strip TM at small H.

### A2. Direct third-party king-lattice tables (bank the comparison as a deliverable)

The literature computed polyplet perimeter polynomials before this project: Peters,
Stauffer, Hölters & Loewenich 1979 (nnSquare g_{s,t}, s ≤ 10, per Mertens's ref 11)
[PSHL79]; Mertens 1990 (perimeter-resolved to s = 13, totals to s = 14, Tables I
and IVB, held locally) [M90]; Tremblay & Vernay 2024 (a(18), held) [TV24].
`results/matching-pair-convention.md` records that `--siteperim` was cross-checked
against Table IVB informally; nothing banks the comparison as a provenance artifact.
Deliverable shape: a short note + checker listing repo values against literature
values cell by cell, n ≤ 14 perimeter-resolved, n ≤ 18–19 totals (OEIS A006770
history included).

Independence: same axis as A1 layers 1 and 3 — 1979/1990 Fortran enumerations and a
2024 generation algorithm share no rule, code, or author with either repo engine.
Failure mode: a definition-level misconception (what counts as king-adjacent, what
counts as one animal) shows as a value mismatch at small n. Region: n ≤ 14
perimeter-resolved, ≤ 19 totals — low, but this is the cheapest genuine
rule-axis check on the list (zero new compute; an afternoon of transcription), and
low n is where a definition error lives. Binding resource: none worth naming.

### A3. Tier-3 shape: the matching identity as an exact-arithmetic certificate

The brief says no mechanism has been proposed for a tier-3 artifact. A modest one,
at sum-rule granularity: ship (king table, rook table, order M) plus a checker in
the shape of `experiments/matching_series_probe.py`'s last loop — ~30 lines of
integer arithmetic verifying M polynomial identities — plus the 4×4-census
derivation of the inhomogeneous term (Lean-able: a statement about finite local
counts). The checker is independent of every engine, and the certificate transfers
trust from published rook data rather than from a re-run. Scope is honest: it
certifies the sum rules, not each cell; it is an upgrade of A1's deliverable format,
not a separate compute.

---

## Kill list

**K1. Potts / Fortuin–Kasteleyn / subgraph-component-polynomial route (the lane's
flagged favourite).** **[SUPERSEDED 2026-08-11 — see "Cross-critique of B" below.
The three kills stand against the three formulations they name, but B1's
ℤ[q]/(q²) truncation is a fourth member of this family that evades all three;
this entry must not enter the merged document as a kill of the family.]** The exact object is Q(G; x, y) = Σ_S x^|S| y^k(S)
(Tittmann–Averbouch–Makowsky [TAM11]); T(n,H) sits in its y-linear part. Three
formulations, all dead:
  - *Spin representation, integer q, interpolation.* Locally weighted TM with
    (q+1)^H column states and no connectivity decisions anywhere — genuinely
    rule-independent — but [xⁿ]Q has y-degree n, so n+1 evaluation points:
    largest q = n+1. Measured state counts (probe 3, arithmetic): H=14, n=20 →
    22¹⁴ = 6.2×10¹⁸ states; H=10, n=40 → 42¹⁰ = 1.7×10¹⁶; even H=10, n=20 →
    2.7×10¹³ against the incumbent's ~10⁶-state frontier. Dead at every useful
    (n, H).
  - *Color-symmetrized basis.* Collapsing the q-fold color symmetry turns column
    states into set partitions of occupied cells: Bell(H+1) = 1.4×10⁹ at H=14
    (probe 3) — ~10³ times the strip engine's measured 4-bit-packed partition
    count — and, decisive for this brief, the symmetrized transition is the
    partition-join, i.e. union-find again. Fails the independence bar by identity,
    not merely by cost.
  - *FPT/treewidth algorithms for Q* [TAM11] are partition-carrying DPs — the
    incumbent rule in the brief's own words.

**K2. Tutte / reliability polynomial specializations.** Their connected objects are
spanning *edge* subgraphs; no specialization of T(G;x,y) or Rel(G;p) counts
connected *induced vertex* subsets — that is why [TAM11] introduces Q as a new
polynomial and proves it is not determined by the Tutte polynomial (their §1, §8).
The site version is K1. Killed by citation.

**K3. Matrix-tree / Grassmann (spanning-structure algebra).** Σ_S x^|S| κ(G[S])
(κ = spanning-tree count, a local-determinant object with a genuinely different
mechanism) counts vertex-weighted lattice *trees*, not animals; no linear functional
of κ isolates [κ ≥ 1]. The known repair — work mod 2 with random weights and an
isolation lemma — is exactly cut-and-count, Teammate B's lane; recorded here as a
handoff, killed as an A-lane candidate.

**K4. Partition-of-unity / moment sum rules** (Σ_n n D_n-type identities, the
classical percolation series checks). Rule-blind: they hold for *any* deterministic
partition of occupied sites into parts with consistently counted boundary, because
they only encode "each site is in exactly one cluster." Zero power on the
connectivity-rule axis; keep them only as free accounting gates on any new perimeter
table. Killed by the argument above (contrast with A1, whose cross-lattice pairing
is what buys rule sensitivity — probe 2).

**K5. Finite lattice method as accounting-layer independence.** The brief requires
the distinction made explicit: FLM's inclusion–exclusion over W×L rectangles is a
different accounting layer, but each rectangle is counted by a column TM carrying
the same connectivity rule, so the axis this brief cares about stays shared. The
reach question was separately closed negative in `results/finite-lattice-crossover.md`
(same n/2 cap the engine already gets). Only live use: if Teammate B produces a
rule-independent in-rectangle counter, FLM is the accounting to wrap it in.

**K6. Corner transfer matrices (Baxter; Chan–Rechnitzer).** Read-negative in-repo:
fails their locality/symmetry conditions and their κ is per-site for a
local-constraint gas, not per-cell for connected clusters
(`papers/chan_rechnitzer_2018_*.pdf`, notes in INDEX.txt;
`results/strip-growth-lambda-bounds.md`). Approximates free energies; produces no
exact integers. Killed by citation.

**K7. Exact-solution routes** (Temperley strata, kernel method, heaps of dimers,
Bacher's king-lattice directed animals). Solvable subclasses only; for the full
class the repo has theorems in the way: T(n,H) is not 2D-holonomic
(`results/boundary-push-recurrence.md`) and the anisotropic GF is not D-finite
(`results/anisotropic-not-dfinite.md`). Bacher 2015 solves *directed* king animals
— a different family. Killed by repo citation.

**K8. Series analysis (differential approximants, ratio methods).** Estimates with
confidence intervals; the goal is publication-grade exact verification. Out of
scope by the brief's own standard.

**K9. A1's p = 0 direction via `g2 --siteperim` at n = 20 (was measurement-plan
item iii).** Killed by team-lead calibration, dalby 2026-08-11
(`./build/g2 square8 N --siteperim`, single-threaded, rev 3b7359de, tracked tree
clean): n = 12 → 60.9 s, n = 13 → 424.6 s, ratio 6.97×/term ⇒ n = 20 ≈ 3.4×10⁸
core-seconds ≈ 94,000 core-hours ≈ 49 days on all 80 dalby cores; n = 19 ≈ 7 days;
n = 18 ≈ 24 h. The perimeter-bookkeeping kernel runs ~3×10⁶ objects/s against the
pure-count Terminal Velocity kernel's ~10⁸/s — my original ~2.6-fleet-hour figure
was scaled off the banked a(22) run's wrong kernel, ~300× optimistic. And at the
affordable n ≤ 18 the direction is redundant on the rule axis (row-22 Redelmeier
covers it) and nearly so on the definition axis (C's probe C2 to n = 13, Duarte's
print to ~16).

---

## Citations

- [SE64] M. F. Sykes & J. W. Essam, "Exact critical percolation probabilities for
  site and bond problems in two dimensions," J. Math. Phys. 5 (1964) 1117–1127.
  DOI 10.1063/1.1704215. (Matching theorem for mean cluster numbers; verified via
  ADS/AIP record this session.)
- [M90] S. Mertens, "Lattice animals: a fast enumeration algorithm and new
  perimeter polynomials," J. Stat. Phys. 58 (1990) 1095–1108. DOI
  10.1007/BF01026565. Held: `papers/mertens_1990_lattice_animals.pdf`. Read this
  session: Table I (nnSquare totals to s=14), Table IVA (square D_s to s=22),
  Table IVB (nnSquare D_s, s=11–13), refs 5–11 for the earlier series lineage.
- [CG95] A. R. Conway & A. J. Guttmann, "On two-dimensional percolation," J. Phys.
  A 28 (1995) 891–904. DOI 10.1088/0305-4470/28/4/015. Abstract verified this
  session (IOP): high- and low-density site series on the square lattice by FLM.
  Already in `papers/MISSING.md` (jasonp searched 2026-08-06, library-only); its
  high-density series order is the number that prices A1's published-data reach.
- [D81] J. A. M. S. Duarte, Portgal. Phys. 12 (1981) 99. Cited from [M90] ref 14
  and its Appendix A statement "Duarte calculated all g_st for t ≤ 16 on the square
  lattice; his values are confirmed." Not found free this session (one web pass);
  → MISSING block below.
- [PSHL79] H. P. Peters, D. Stauffer, H. P. Hölters & K. Loewenich, "Radius,
  perimeter, and density profile for percolation clusters and lattice animals,"
  Z. Phys. B 34 (1979) 399. DOI 10.1007/BF01325205 (Springer record verified this
  session; paywalled). Per [M90], source of nnSquare g_{s,t} for s ≤ 10.
- [TAM11] P. Tittmann, I. Averbouch & J. A. Makowsky, "The enumeration of vertex
  induced subgraphs with respect to the number of components," European J. Combin.
  32 (2011) 954–974. DOI 10.1016/j.ejc.2011.03.017; arXiv:0812.4147 (free).
  Verified this session.
- [TV24] H. Tremblay & J. Vernay — held, `papers/tremblay_vernay.pdf` (see
  INDEX.txt).
- Sieben 2008 (min site perimeter, used for the rook size bound) — held,
  `papers/sieben_2008_minimum_site_perimeter.pdf`.
- M. F. Sykes & M. K. Wilkinson, J. Phys. A 19 (1986) 3407 and 3415 — from [M90]
  refs 8–9; existence confirmed by citation trail only, content (whether they carry
  nnSquare series past s=10) unverified → MISSING block.

**For `papers/MISSING.md`** (not appended directly — three agents are running and
the merge wave should do the shared-file writes): [D81] (searched: title-less
journal citation via Mertens; one web pass, no digitized Portugaliae Physica copy
found); [PSHL79] (Springer record found, paywalled; wanted for the s ≤ 10 nnSquare
tables); Sykes–Wilkinson 1986 ×2 (not individually searched beyond the citation
trail; wanted to pin the best pre-1990 nnSquare series order). [CG95] is already
listed there; add to its entry: *the high-density site series order is what prices
candidate A1's no-new-compute reach.*

## Probe artifacts

- `experiments/matching_series_probe.py` (uncommitted) — probes 1 and 2; run as
  `python3 experiments/matching_series_probe.py 9` (5.1 s; the wrong-rule variant is
  the same file with one KING line edited, output quoted above).
- Probe 3 is four lines of arithmetic ((q+1)^H, Bell numbers); numbers quoted in K1.
- Probe 4 (critique wave, below): `build/probe_king_perim12` from the session
  scratchpad's `probe_king_perim12.cpp` — C++ port of probe 1's enumerator,
  n ≤ 12 king perimeter polynomials in 24 s.

---

## Cross-critique of C (`results/second-source-candidates-C.md`), 2026-08-11

Written after reading C's file and `results/mertens-1990-perimeter-crosscheck.md`.
B had not reported when this was written.

### 1. C-1 versus A1 — same identity, materially different framings

**Where C's framing overstates.** C-1 says "rook-side data decides king-side
counts" and "the king side of the check is decided by rook enumerations plus a
topological identity." Not supported. The identity yields ONE integer linear
equation per order in p; it constrains one functional of the king perimeter table
per order, it does not determine the table. The defensible claim (A1) is: a
*systematic* rule error generically breaks the identity at the first order it
touches — demonstrated by A1's probe 2, where a wrong adjacency fails at p² —
while an adversarial error tuned to the checked functionals would pass. The
merged document should carry A1's scoping sentence, not C-1's "decides."

**Where C's reach number is wrong in an important way.** C-1 prices the rook side
as "published series stop at s = 22." Size-graded tables are the wrong axis: the
p→0 expansion at order p^m needs rook animals of *perimeter* t ≤ m at all sizes
(sizes reach ((m−2)²+4)/8). A size-s table is t-complete only up to the minimum
perimeter of size s+1, so Mertens's s = 22 buys complete rook data only to
t = 15 (min perimeter of s = 23 is 16, Sieben's bound). The published number that
actually sets the no-new-compute check order is Duarte 1981's all-g_st-for-t ≤ 16
[D81 in my citations; Mertens ref 14 and his Appendix A confirm it] — so order
~p¹⁵–p¹⁶ from print, not p²². Beyond that: perimeter-bounded rook enumeration
(cheap-looking, unmeasured — A1 measurement plan (i)) or the Conway–Guttmann 1995
high-density FLM series, whose order is unread (MISSING.md). [Correction
2026-08-11: C-1's "extendable to ~n = 19-20 at Redelmeier cost" and my own
n ≤ 21–22 king-side reach both used the wrong kernel's throughput; the measured
`--siteperim` calibration caps the king size-graded side at n ≈ 18 — see K9. The
p = 0 direction is demoted for both files; A1's re-ranking section has what
survives.]

**Where C-1 is stronger, conceded.** (a) Probe C2 is executed work my A2 only
proposed — the coefficient-level Mertens comparison now exists with provenance,
and my A2 collapses to "extend C's crosscheck note to the s ≤ 10 layer via
Peters et al. 1979 when obtained, plus OEIS/Tremblay–Vernay totals to n = 18."
(b) C's coverage map ("the king TM row is empty; nothing external exists above
n = 18 to import") is the fact that makes the matching identity the *only*
external channel at any n — my A1 asserted its value, C's map proves there is no
competitor. (c) C cites Sykes & Glen 1976 directly where I only walked Mertens's
reference list.

**What A1 adds that C-1 lacks** (for the merge): the executed order-by-order
probe (GREEN to p⁹) and the wrong-rule sensitivity demonstration; the p→1
expansion direction (tests king *compact* perimeter-graded data against
square-by-size tables — a second, distinct slice); the height-resolved per-box
Euler variant (the only version that constrains per-height strip-family data);
the tier-3 certificate framing (A3); and the corrected reach pricing above.

### 2. The convergence, honestly

It is a common source, not independent invention. `results/unexplored-avenues.md`
idea 2 and `results/matching-pair-convention.md` sit in the repo both of us swept;
C reached them through percolation-series coverage, I through the statistical-
mechanics end of my lane, but neither of us invented the identity — the repo
already had it, conventions pinned, at 4×4. What the double arrival buys is
*ranking* corroboration only: two different literature sweeps ended at the same
survivor, which says something about the search space, and nothing about
correctness. The evidential content of the candidate lives entirely in the
probes and in the externality of the rook-side data, exactly per the brief's
"two of you agreeing is not evidence." The merged document should present the
identity once, sourced to the repo's own idea 2, with the two lanes' additive
contributions folded in — not as a convergence argument.

### 3. C's Mertens misprint claim — CONFIRMED, and strengthened

Checked independently three ways this session (probe 4):

- **Mechanical re-extraction** (`pdftotext -layout`, own pass, not C's artifact):
  printed Table IVB columns sum to 39299408 / 257205146 / 1692931066 for
  s = 11/12/13; s = 12 overshoots by exactly 100000 = 26269734 − 26169734.
  Matches C's table.
- **Strengthening C's row-sum argument**: the overshoot is refuted by *Mertens's
  own paper* — Table I of the same paper prints g₁₂ = 257105146. The
  inconsistency is internal (Table I vs Table IVB of one publication), pinned to
  a single cell by the other 33 coefficients; no repo data, OEIS, or 2024 source
  is needed to conclude the print is wrong. C's version leans on the banked
  a(12)'s multi-source provenance — correct but weaker than necessary, since a
  hostile reader could discount all post-Mertens sources as one lineage.
- **Third-lineage recount of the cell itself**: C++ port of my probe-1 enumerator
  (this session's code, not g2, not Mertens), `build/probe_king_perim12`, full
  D₁₂ in 24 s: (s=12, t=39) = **26169734**, all other 33 printed s = 12
  coefficients reproduced exactly, all totals n ≤ 12 match Table I. So the
  banked value now has three independent computations (Mertens's own row-sum
  identity, g2, this probe) against one printed digit.

Verdict: C's arithmetic is right, the misprint is real and is the literature's.
Suggest the merged note add the Table-I-internal argument and the third-lineage
recount, and consider sending Mertens a two-line erratum note (jasonp's call —
publishing-is-jasonp's-call).

### 4. Kill lists, both directions

- **C's "percolation-series import beyond s = 13" kill is one citation short of
  closed.** Sykes & Wilkinson 1986 (J. Phys. A 19, 3407 and 3415 — Mertens refs
  8–9) are cluster-series papers whose content neither of us has read; if either
  carries matching-lattice (nnSquare) series past s = 13, the kill's premise
  ("the community moved to Monte Carlo") fails at the margin. Cheap to settle:
  the two abstracts. Flagged in my MISSING block; C's kill row should carry the
  caveat until then.
- **C's C-2 scoping is honest and survives critique** — the probe carries the
  incumbent's rule and C says so; the independence lives in Resta's
  `ConnectedGraphQ` brute force and Howroyd's outside lineage. One addition: the
  A290764 closed form (2×n king slab) is exactly A1's box-identity family at
  H = 2 in aggregate, so C-2 and A1's height-resolved variant meet there — a
  natural first cross-check for both.
- **Nothing in C's map undermines my kills.** C's §2 observation that every
  high-scale engine in the field carries a boundary connectivity state is
  independent support for K1/K5 (the partition basis is the same rule
  everywhere); C's §3 matches K7. Conversely C's kill of the 45°-rotated TM
  (with the two-layers-ahead diagonal argument) discharges the "re-derive, don't
  trust the note" TODO in `papers/refs-transfer-matrix.md` — worth keeping in
  the merged document so that TODO dies on the record.

---

## Cross-critique of B (`results/second-source-candidates-B.md`), 2026-08-11

Written after reading B's file and `experiments/probe_cutcount_dp.py` in full,
and after an independent reimplementation probe (probe 5, below). Verdict up
front, since jasonp is waiting on it: **B1 survives the attack. K1 is superseded
with respect to B1's formulation, and the calibration run should go.**

### 1. Does ℤ[q]/(q²) evade the three K1 kills? Yes — all three, specifically:

- **(a) integer-q interpolation** attacked recovering the full polynomial
  A_n(q) from n+1 integer evaluations, which needs q ≈ n and (q+1)^H spin
  states. B1 recovers nothing of the sort: it wants one coefficient, [q¹], and
  the quotient map ℤ[q] → ℤ[q]/(q²) is a ring homomorphism that commutes with
  every DP operation, so tracking two integers per (state, area) is exact. My
  error was conflating "determine A_n(q)" with "extract its linear
  coefficient." The kill stands against interpolation; interpolation is not
  what B1 does.
- **(b) Bell-number state blowup** used the wrong combinatorial universe:
  partitions of the H+1 window *cells* (Bell(15) = 1.4×10⁹ at H = 14). The
  reachable states are partitions of the occupied *runs* — vertically adjacent
  occupied cells are same-color by force, and the ≥2-block clash rule prunes
  further — and the measured count is 13,733 at H = 10. Killed by B's
  measurement, and I have independently confirmed the measurement (below).
- **(c) "the partition-join is union-find again"** — the one that matters, see
  §2. It does not apply: B1's transition contains no join.

**Consequence for my critique of C, retracted:** my §1 tightening claimed
y-linear extraction is the q→0 limit "with no integer-q or local realization."
Wrong. ℤ[q]/(q²) is the realization, and its weights are local (per-cell,
window-state-dependent only). The merged document must not carry that sentence.

### 2. Is it union-find wearing coefficient arithmetic? No — checked against the code, not the prose

The state is a partition, which is what invited K1(c); but the incumbent's rule
is not "has partition states," it is two per-event *decisions*: the union
verdict (new cell adjacent to ≥2 blocks → unite them) and stranded-component
death (block ages out unconnected → kill the state). In
`experiments/probe_cutcount_dp.py` the transition has **no analogue of
either**: a cell adjacent to ≥2 distinct blocks is weight-zeroed (the branch
is dropped, blocks are never united — the merge that union-find would perform
is exactly the event that gets weight 0, because distinct blocks carry
distinct colors); and a block whose window cells age out vanishes silently
with no verdict — disconnected subsets flow through to the end and cancel out
of [q¹] by signed falling-factorial algebra ((q)_k has [q¹] = (−1)^{k−1}(k−1)!,
so the coincidence-pattern sum performs an inclusion–exclusion the DP never
sees). The subtle point I attacked hardest: the fresh-color weight (q − b)
uses b = *window-visible* blocks only, though aged-out classes exist. It is
right — coinciding with a visible block is enumerated separately (b branches
of weight 1), so each unconstrained class choice totals b·1 + (q−b) = q, and
never-covisible components correctly contribute q each — and it is validated
where it would break, at (2,6), where classes age out (B's run and mine).

**Probe 5** (`probe_b1_states.py`, session scratchpad, 2.2 s): I reimplemented
the DP *from B's stated rules*, not from B's code — separate canonicalization,
separate neighbor-offset derivation, separate payload bookkeeping — and (i)
reachable state counts match B's at every H = 4..10 (45, 111, 279, 718, 1884,
5041, 13733), (ii) [q¹] matches my own floodfill brute force at 3×4, 2×6, and
4×4 — the last beyond B's validation set — with [q⁰] = 0 throughout. Two
independent implementations of the stated mechanism agreeing with brute force
is evidence the *mechanism* is well-defined, which is what a rules-level
critique can establish.

What stays shared with the incumbent, and the complementarity that resolves
it: B1 concedes the king-adjacency definition and the window geometry. That
is exactly the axis A1/C-1 cover — the matching identity and the external
tables (Mertens, Resta, Howroyd) anchor the *definition* at n ≤ 13–16 (n ≤ 13
coefficient-level, ~16 via Duarte's print; the 21-ish reach originally claimed
here fell with the K9 calibration) with no in-house rule anywhere. B1 covers the region (H ≤ 14, all n ≤ 40) that no
external channel reaches. The merged document should present B1 and A1 as a
pair covering each other's conceded axis, not as competing candidates.

One naming correction for the merge: mechanically B1 is the color-symmetrized
*spin*-representation transfer matrix with clash-zeroing, not the
Fortuin–Kasteleyn / random-cluster TM — the FK TM (Salas–Sokal) carries
connectivity partitions and *does* join blocks. The [SS01] citation is fine as
lineage, but the merged text should describe the mechanism precisely, because
"FK transfer matrix" invites exactly the misreading my K1(c) made.

### 3. The checkable point: B right, A wrong

Settled above — retraction recorded in §1. The local realization exists and
both implementations of it agree with brute force.

### 4. Growth extrapolation, checked independently

State counts reproduced exactly (probe 5). The arithmetic caveats that the
calibration run should absorb:

- The growth ratio is **still climbing** at B's last measured point: 2.47,
  2.51, 2.57, 2.62, 2.68, 2.72, 2.77, 2.82 for H = 5..12, a steady ~+0.05 per
  level with no plateau. "Nearly identical growth rate" to the strip's ~2.65 is
  optimistic phrasing; the incumbent's ratio also drifts, and the *relative*
  factor widens with H — 13,733/5,797 = 2.37× at H = 10, ~2.6× at H = 12,
  plausibly ~3× at H = 14. Extrapolating with the drift: ~9×10⁵ states at
  H = 14 (±30%; the drift is unmodelled).
- B's "~0.5 GB at H = 14" understates the payload arithmetic: 9×10⁵ states ×
  41 areas × 2 coefficients × 32 B ≈ 2.3 GB, and double-buffering the
  transition doubles it. **The verdict is unchanged** — ~5 GB is comfortable
  against the strip's measured 38 GB at C₁₄, and B's identification of bigint
  throughput as the real binder stands — but the number in the merged document
  should be the corrected one.
- Recommendation for the calibration run: measure the H = 13 state count on
  the way up (cheap) to pin the ratio drift with one more point before pricing
  the H = 15–17 stretch; and log A_n(1) = C(HW, n) at a small full-polynomial
  H alongside [q⁰] = 0, since those are the over-determination checks B's
  independence argument leans on.

### Verdict

B1 clears the brief's bar: connectivity is never decided, it is extracted from
a graded algebra whose failure modes (weight line, truncation, canonicalization)
are jointly self-checking and disjoint from union-find-with-death. My K1 kill
of the family was wrong at the member B found; marked SUPERSEDED above.
Remaining shared surface (adjacency definition, accounting layer) is covered by
A1/C-1's external anchors. The C++ calibration run is worth its cost, and
nothing in my lane blocks it.
