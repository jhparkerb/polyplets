# Plan: Filling the Free-Polyomino Gap (Option 1)

*Drafted June 11, 2026. Companion to `research-options.md`. Sources: Shirakawa,
[Enumeration of Polyominoes up to Size N=59](https://arxiv.org/abs/2510.22446)
(local copy `papers/shirakawa_n59.pdf`); Barequet & Ben-Shachar,
[Counting Polyominoes, Revisited](https://www.researchsquare.com/article/rs-4304962/v1.pdf)
(local copy `papers/counting_polyominoes_revisited.pdf`). All OEIS extents verified
against live b-files on this date.*

## 1. Goal

Extend free polyominoes [A000105](https://oeis.org/A000105) and one-sided
polyominoes [A000988](https://oeis.org/A000988) — both currently at **n = 59** —
toward **n = 70**, the limit implied by the known fixed counts
([A001168](https://oeis.org/A001168)). Every term requires extending the
symmetry-component sequences described below; the fixed counts themselves are
already done.

## 2. Mathematical framework (Shirakawa / Mason / Burnside)

Free and one-sided counts follow from Burnside's lemma over the 8-element point
group, decomposed by *where* the symmetry element sits relative to the lattice.
Each component counts fixed polyominoes with **at least** the stated symmetry
(no exactly-this-group bookkeeping needed). With Fixed(n/2) := 0 for odd n:

```
Free(n)      = 1/8 · ( Fixed(n) + 2·Fixed(n/2) + 2·M90(n) + 2·M45(n)
                       + R180C(n) + 2·R180M(n) + R180V(n)
                       + 2·R90C(n) + 2·R90V(n) )

One-sided(n) = 1/4 · ( Fixed(n) + R180C(n) + 2·R180M(n) + R180V(n)
                       + 2·R90C(n) + 2·R90V(n) )
```

Component glossary (Mason's nomenclature):

| Component | Symmetry, position of axis/center | OEIS | Known to | Needed? |
|---|---|---|---|---|
| Fixed | none (translation only) | [A001168](https://oeis.org/A001168) | **n = 70** | done |
| M90V | mirror, axis through cell centers | = Fixed(n/2) | n = 140 equiv. | done |
| M90 | mirror, axis through cell boundaries | [A346799](https://oeis.org/A346799) | **n = 60** | → 70 |
| M45 | mirror, diagonal axis | [A346800](https://oeis.org/A346800) | **n = 66** | → 70 |
| R180C | 180° rotation about a cell center | [A390653](https://oeis.org/A390653) | **n = 59** | → 70 |
| R180M | 180° rotation about an edge midpoint | [A390654](https://oeis.org/A390654) | **n = 58** (2·29) | → 70 |
| R180V | 180° rotation about a vertex | [A390655](https://oeis.org/A390655) | **n = 58** (2·29) | → 70 |
| R90C | 90° rotation about a cell center | [A348849](https://oeis.org/A348849) | n = 97 | done |
| R90V | 90° rotation about a vertex | [A348848](https://oeis.org/A348848) | n = 92 (4·23) | done |

R180M and R180V (and M90V) are nonzero only for even n. The R90 classes and
Fixed are already past 70. **The entire project reduces to extending five
sequences: M90, M45, R180C, R180M, R180V.**

Unlock schedule (which Free(n) becomes computable when): Free(60) needs
R180{C,M,V}(60); Free(61) additionally needs M90(61) and R180C(61) (the
even-only classes contribute 0); and so on. Note that **One-sided(n) needs no
mirror classes at all** — the R180 workstream alone extends A000988.

## 3. Why the two workstreams are very different

**Mirror classes (M90, M45) — counting without generating.** Shirakawa already
uses a Jensen-style transfer-matrix algorithm (TMA) on the half-region: axis
cells weight 1, off-axis cells weight 2; a run with bounding-box short side W
is exact for n ≤ 3W. He reached n = 60 / 66 with a *simple implementation —
explicitly no pruning and no parallelization*. There is enormous headroom:
Barequet–Ben-Shachar-style signature pruning, k-way parallel signature sets,
and lattice-orientation choice are all unapplied. Reaching n ≥ 70 (W = 24)
is an engineering exercise, not research.

**Point-symmetric classes (R180C/M/V) — currently generation-bound.** Shirakawa
counts these with Redelmeier's ring method + a neighborhood-counter frontier:
every symmetric polyomino is *generated*. The counts grow ≈ λ^(1/2) ≈ 2.016×
per cell (a symmetric shape is determined by half of itself). Extrapolating
from R180C(59) ≈ 5.27·10^16:

| target n | R180C(n) ≈ | generation cost vs n=59 |
|---|---|---|
| 62 | 4×10^17 | 8× |
| 64 | 1.7×10^18 | 32× |
| 66 | 7×10^18 | 128× |
| 70 | 1.2×10^20 | 2048× |

At an optimistic aggregate 10^10 search-nodes/sec (≈100 fast cores), n = 70
means ~1.2·10^10 seconds ≈ **380 core-centuries** — generation cannot get
there. Brute-force engineering tops out around n ≈ 63–65. Going to 70 requires
a **transfer-matrix method for 180°-symmetric polyominoes**, which does not
exist in the literature as far as this survey found. That is the one research
risk in the project — and also its publishable core.

## 4. Workstreams

### Workstream A — mirror classes via TMA (engineering, low risk)

A1. Implement the half-region TMA for M90 (Jensen signature encoding, axis
    weight 1 / off-axis weight 2), validate against A346799 ≤ 60.
A2. Add Barequet–Ben-Shachar machinery: signature pruning (connection budget
    n_c via DP or MST, span budget, width budget), the odd-height mirror-merge
    symmetry, k-way signature-set splitting for parallelism + compressed
    inactive sets.
A3. M45: same engine, different orientation. Note the synergy: under the 45°
    lattice rotation, the M45 diagonal axis becomes axis-parallel (and vice
    versa) — implement one engine with a lattice-orientation switch and pick
    whichever orientation prunes better per class, mirroring the
    Barequet–Ben-Shachar gap-closing analysis.
A4. Production runs to n ≥ 70 (W = 24). Unpruned signature space 3^24 ≈ 3·10^11
    is the worst case; pruning historically cuts this by orders of magnitude.
    Budget for out-of-core or mod-p splitting if RAM pressure appears
    (see §6). Only +4 terms are needed for M45, +10 for M90.

Estimated effort: 3–6 weeks of implementation, workstation-to-single-server
compute (64 cores / 256–512 GB class; out-of-core fallback if needed).

### Workstream B — point-symmetric classes (two phases)

**B1. Engineering push of the generation method (low risk, bounded payoff).**
Reimplement the Redelmeier ring method with Shirakawa's neighborhood-counter
frontier, his synchronization-free thread partitioning (search modulo thread
ID at a fixed depth), plus: tighter inner loop (bitboards / SIMD frontier
updates), and cloud burst for the top terms. First reproduce n = 58–59 to
calibrate true node rates and costs, then push while cost-per-term (×2 each
step) stays acceptable. Realistic ceiling: **n ≈ 63–65** for ~10^4–10^5
core-hours. Each completed even/odd rung immediately yields new A000988 terms
and (with Workstream A done) new A000105 terms.

**B2. Research: a TMA for 180°-symmetric polyominoes (high risk, full payoff).**
The blocker for counting-without-generating is that 180° symmetry relates the
two halves of the sweep non-locally: connectivity can weave across the center
line, so the half-region boundary signature must also encode how its mirror
image connects through the other half. Candidate attacks, in order of
preference:

1. *Center-out two-front sweep.* Process column +c and its image −c
   simultaneously, outward from the center. By symmetry the −c side is
   determined, so only one signature is stored, but component labels must
   carry pairing information about connections made through the center
   columns. State space is plausibly the square of the ordinary signature
   space in the worst case; the open question is whether pruning (which is
   what actually tames these algorithms) keeps it manageable.
2. *Orbifold/quotient view.* Polyominoes fixed by ρ correspond to connected
   sets on the quotient cone of the plane by the rotation; a TMA on the
   quotient with a defect line at the center may linearize the problem.
3. *Literature mining before inventing.* Symmetric self-avoiding polygons and
   symmetric lattice animals have scattered prior work in the statistical
   mechanics literature (Jensen's school); 2–3 weeks of focused search may
   surface an encoding to adapt. Also: Knuth's 2014 diagonal generating-
   function approach handles bounding-box-indexed counts and may compose
   with symmetry constraints.

Decision gate after ~4 weeks: if no viable encoding emerges, the project still
delivers Free/One-sided to the B1 ceiling (~63–65) — 4–6 new terms of A000105
— and documents the obstruction. If it works, Free(70) follows and the method
itself is a paper.

### Workstream C — assembly, verification, publication

- Recompute every component independently for n ≤ 30 with a naive
  brute-force enumerator (hours of compute, total cross-check of all signs,
  weights, and class definitions).
- Verify Free(n)/One-sided(n) formulas reproduce A000105/A000988 for n ≤ 59.
- Identity checks: M90V(n) = Fixed(n/2); Mason's inclusion–exclusion to the
  "exactly"-symmetry sequences A006746/A006747/A006748/A006749 must reproduce
  their known terms.
- All large runs executed twice: counts modulo two independent 64-bit primes
  (CRT-recombined) or full-bignum on different hardware; mismatches localize
  errors cheaply.
- Deliverables: b-file extensions for A346799, A346800, A390653–A390655,
  A000105, A000988, and the derived exact-symmetry sequences; arXiv note
  describing methods and (if B2 lands) the symmetric TMA.

## 5. Milestones

| # | Milestone | Depends on | New public terms |
|---|---|---|---|
| M0 | Brute-force reference enumerator, all components n ≤ 30 | — | (validation only) |
| M1 | Generation engine reproduces R180C(59), R180M/V(58); costs calibrated | M0 | — |
| M2 | TMA engine reproduces M90(60), M45(66) | M0 | — |
| M3 | R180{C,M,V} → 60–62 | M1 | One-sided 60–62; Free 60 (61–62 after M4 partial) |
| M4 | M90 → 70, M45 → 70 | M2 | — (removes mirror bottleneck forever) |
| M5 | R180 push to B1 ceiling (~63–65) | M3 | Free + One-sided to ~63–65 |
| M6 | B2 decision gate: symmetric TMA viable? | 4 wks research | — |
| M7 | (if M6 yes) R180 classes → 70 | M6 | **Free + One-sided to 70** |

Worst case (M6 = no): A000105 extended ~59 → ~64, A000988 likewise, five
component sequences extended, full verification suite — still the largest
extension of the free count since Jensen-era data. Best case: the gap closes
completely at 70 and the symmetric-TMA technique is novel.

## 6. Compute and infrastructure

- Language: C++ (or Rust) core engines; bignum via GMP or 64-bit mod-p + CRT
  (mod-p halves memory per signature entry and doubles as verification).
- Hardware: development on workstation; production TMA runs want one
  64–128-core node with 256 GB–1 TB RAM (compressed/chunked signature sets
  reduce this, per Barequet–Ben-Shachar who fit n=70 fixed counts in 32 GB).
  B1 generation runs are embarrassingly parallel → cloud spot instances,
  budget O($10^3) for the ~10^4–10^5 core-hour ceiling push.
- Checkpointing mandatory for any run > 1 day (signature DB snapshots; the
  generation search partitions trivially by subtree).

## 7. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| B2 encoding has intractable state space | real (~50%) | decision gate at 4 wks; B1 payoff stands alone |
| TMA memory blowup at W = 24 for M90/M45 | moderate | pruning, mod-p, k-way chunking, out-of-core; precedent says fine |
| Correctness bug in a 10^4-core-hour run | moderate | dual mod-p runs, n ≤ 30 brute-force oracle, formula back-checks vs n ≤ 59 |
| Scooped: Shirakawa/Mason are active here (papers Oct 2025, OEIS edits Nov 2025) | moderate | contact both early — coordination or collaboration beats racing; their published methods cap at the generation wall anyway, so B2 is differentiated |
| Coefficient/definition error in Burnside formula transcription | low | M0 brute-force check catches instantly |

## 8. Immediate next actions

1. Set up repo scaffolding (C++ build, GMP, test harness pinned to OEIS
   b-files as golden data).
2. Write the M0 brute-force enumerator (free/fixed/each symmetry class,
   n ≤ ~16 exhaustive, n ≤ 30 for symmetric classes which are sparse).
3. Implement the Redelmeier + neighborhood-counter generation engine (B1
   foundation; also the fastest path to *any* new published term via
   R180{C,M,V}(60) → One-sided(60), Free(60)).
4. In parallel: literature sweep for symmetric-animal/symmetric-SAP transfer
   matrices (B2 step 3) and a short email to Shirakawa and John Mason
   describing intent — *draft for user review before sending; do not send
   unprompted.*
5. Then Workstream A TMA engine.
