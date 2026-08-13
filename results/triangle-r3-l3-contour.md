# Round-3 L3 — contour encoding: established negative

2026-08-12, L3 lane scout. Brief: `docs/triangle-round3-brief.md`; scored
under `docs/skeptical-reader-standard.md`; engine facts from
`results/triangle-r3-harness.md` Part 3. Blind list filed first at
`results/triangle-r3-blind-l3.md` (18:31 EDT, unrevised).
Measurement script: `experiments/tristruct/r3_l3_pinch.py`
(log `experiments/tristruct/r3_l3_pinch.log`, 196 s, laptop).

**Verdict, first line: no contour route reaches T(40,H) for H = 15..21.
The negative is established, not assumed, on three measurements and one
proved identity. Candidate (B) below clears entry level 1 and fails level 2
by state-space isomorphism; candidates (A) and (C) die earlier, at the
steps named.**

## Entry ticket

Where is king-connectedness decided in a contour encoding, and what does
that share with union-find over a frontier? A contour method *defines*
connectedness topologically — the animal's closed cell squares form a
connected compact set iff the boundary-curve system, glued at pinch
vertices, is one component — which is a genuinely independent
formalisation, so the definition clears **level 1** (Lemma 1 below makes it
well-defined for king adjacency). But any transfer-matrix *implementation*
of curve closure must carry, per column cut, which boundary crossings
belong to the same partial curve system. That cut object is a non-crossing
partition of the cut — and the off-branch theorem
(`git show second-source:results/king-column-motzkin.md`) proves the
production engines' reachable column states are exactly the pairs (fill,
non-crossing partition of runs), count Motzkin(H+1)−1. The contour TM's
states are the same object under a bijection (§3), confirmed numerically:
the banked exact cut ranks 21, 51, 127 (H = 8, 10, 12,
`results/boundary-push-tensornetwork.md`) are exactly M(5), M(6), M(7). So
the failure mode of a wrong contour rule is a wrong partition-of-the-cut —
proposition 2 of the harness's shared-misconception statement — NOT
disjoint from union-find-over-a-frontier's. **Level 2 fails, established by
isomorphism rather than assumed.**

## Disclosure block (phase-1 mapping per the brief)

    claim:                             no contour-encoding route to T(40,H), H=15..21; obstructions measured/proved below
    share of a(40) reached:            0%  (no surviving route; the band named is H=15..21, 50.8445%, provenance 'real-sweep' — quoted from results/triangle-r3-harness.md Part 2, tri.provenance(40,H)='real-sweep' for each H in 15..21, loader classification experiments/tristruct/triangle.py:53-58)
    bits against enumeration error:    0   (negative result; nothing counted)
    bits against formula-chain error:  0   conditional on: n/a
    rule independence:                 level 1 clears (topological definition); level 2 fails (cut states isomorphic to the incumbent partition object — proved + measured)
    derivation independence:           measurements from a from-scratch rooted-growth enumerator sharing no code with any repo engine; validated against banked hole table (see input footprint)
    input footprint:                   27 banked (n,holes) cells n<=10 (validation), A0/a ratio n<=19 (extrapolation; n=19 tier-degraded, flagged), 4 banked cut ranks, the banked strip state series; max n consumed = 19; zero row-40 cells consumed
    checker:                           none proposed (negative result). Measurement script: experiments/tristruct/r3_l3_pinch.py, 196 s, RED control exercised (corrupted table cell -> abort, exit 1)
    sensitivity:                       deferred per phase-1 mapping; the one gate this file rests on (hole-distribution validation) had its corruption test run: +1 on a single banked count fails closed
    prior-work grep:                   see §Novelty greps (both docs pathspec terms, commands shown)

## 1. Does a contour encoding of king animals exist? (the level-1 question)

**Lemma 1 (king contour semantics).** Two cells are king-adjacent iff their
closed unit squares intersect. Hence an animal is king-connected iff the
union of its closed squares is a connected compact set. *Proof:* king
adjacency = Chebyshev distance 1 = squares sharing an edge or a corner
point; conversely disjoint closed unit squares of non-adjacent cells are at
positive distance. ∎

So a contour formalisation is well-defined: take the boundary edge set of
the closed union. The map animal ↔ boundary edge set is bijective (the cell
set is recovered as the odd-winding region), and connectivity = the curve
system, with curves *glued at pinch vertices*, being a single component
(under king adjacency, the two diagonal cells at a pinch are always
adjacent, so a pinch always glues). Holes contribute additional closed
curves that must be assigned to their enclosing component.

What does NOT exist is the classical single-simple-closed-curve picture.
A **pinch vertex** — a lattice vertex whose four incident cells show
exactly one filled diagonal pair — makes the boundary visit that vertex
twice. Measured (§2): 99.42% of n = 10 king animals have at least one, the
mean count grows linearly (~0.53 per cell → ~20 expected at n = 40), and
the single-simple-curve class (hole-free AND pinch-free) is 0.58% at
n = 10, shrinking ×0.566 per cell — ~2·10⁻¹⁰ of the population at n = 40
under geometric extrapolation. A Jensen-style simple-polygon encoding
covers a measure-zero subclass; the obstruction is extensive, not an edge
case. (Consistent with the L1 stratification: mean rook pieces measured
5.51 at n = 10, slope ~0.50/cell — the brief's "~n/2 pieces joined only at
corners"; every corner joint is a pinch.)

## 2. The measurements

From-scratch Redelmeier-style enumeration of fixed king animals, n ≤ 10
(6,053,180 animals at n = 10), no shared code with any repo engine.
**Fail-closed validation:** the full per-(n, holes) distribution matches
`results/holes_n18.txt` exactly for all n ≤ 10 (row sums = A006770); RED
control run: a +1 corruption of one banked cell aborts with exit 1. Hole
convention as banked: 4-connected complement components not touching the
frame (`results/holes_n19.txt` header).

| n | animals | ≥1 hole | ≥1 pinch | multi-piece | simple-curve class | mean pinches |
|---|---|---|---|---|---|---|
| 6 | 3,832 | 4.38% | 94.36% | 94.36% | 5.64% | 2.55 |
| 8 | 147,941 | 8.34% | 98.19% | 98.16% | 1.81% | 3.59 |
| 10 | 6,053,180 | 12.27% | 99.42% | 99.40% | 0.58% | 4.65 |

Per-height at n = 10, the band analogue (H/n ∈ [0.375, 0.525] mirrors
n = 40, H = 15..21): hole share **peaks in the band** — 15.00% at H = 4,
14.60% at H = 5, against 12.27% overall; pinch share ≥ 98.8% there;
simple-curve class ≤ 1.22%.

**Hole share at n = 40.** From the banked table: hole share 26.56% at
n = 18, 28.17% at n = 19 (tier-degraded row, flagged in its header). The
hole-free fraction decays geometrically at the measured ρ = 0.97800/cell
(`results/hole-free-growth-constant.md`, banked, n ≤ 18 first-class):
extrapolating, hole-free(40) ≈ 0.7183·0.978²¹ ≈ 0.450 — **≈55% of n = 40
animals have at least one hole**, and the per-height profile above says the
band-conditional share is higher still. Any hole-free-only route forfeits
the majority of every band cell, and forfeiting it is fatal: T(40,H) is
the full count, and no hole-free count constrains it without the strata.

## 3. The link-pattern verdict: the same object, measured

**Same object, said plainly.** A contour TM's cut state must record, for
the boundary edges crossing the cut, which crossings belong to the same
partial glued-curve system (else closure cannot be detected) and how they
nest (else holes and dead enclosures are confused). Crossings delimit the
filled runs of the cut column; "same curve system" is precisely "same
connected component of the swept region"; planarity of the arc diagram
forces non-crossing. That is a (fill, non-crossing partition of runs) pair
— exactly the reachable state set of the incumbent union-find engines,
proved to number **Motzkin(H+1) − 1** by the second-source-branch theorem
(`git show second-source:results/king-column-motzkin.md`, Lemmas 1–2:
non-crossing forced by the 2×2-K₄ mechanism; every pair reachable).

Numerical confirmation from two banked artifacts that had not been put
side by side: the exact SVD ranks of the frontier count-vector at the
central cut (`results/boundary-push-tensornetwork.md`) are

| H | banked exact rank | M(H/2 + 1) |
|---|---|---|
| 8 | 21 | 21 — exact |
| 10 | 51 | 51 — exact |
| 12 | 127 | 127 — exact |
| 14 | 298 | 323 (≤; that dump was taken at maxn = 16, off the peak column — not all half-cut states attained) |

The cut rank IS the Motzkin count of the half-boundary's state space
(M(H/2+1) = states of a height-(H/2) column including the empty fill).
The "Catalan/Motzkin at the cut" gesture in that file is an exact identity.
So the entanglement wall the brief's second ticket names and the contour
TM's state space are the same object, measured — a contour route pays the
rank at the same cut, not somewhere else.

## 4. The candidates, each with the step it dies at

**(A) Single closed curve, Jensen-style (simple polygons).** Clears
neither level: the object does not represent king animals. Dies at the
**definition step** — the encodable class (hole-free ∧ pinch-free) is
0.58% at n = 10 and ~10⁻¹⁰ at n = 40 (§2).

**(B) Glued-curve-system contour TM (the honest repair).** Clears level 1
(Lemma 1), fails level 2: its cut states are isomorphic to the incumbent's
(fill, non-crossing partition) states (§3), so a partition-insufficiency
misconception reproduces identically. And it buys no reach: state count
M(H+1) − 1 = **400,763,222 at H = 21** — the very state space whose sweep
cost 36.4 h on 32 cores with a 363 GB disk peak for the H21 phase alone.
Dies at the **level-2 / cost step**: same states, same wall, ranked by the
brief's own rule strictly below nothing — it is the incumbent in different
clothes.

**(C) Hole-free by contour, plus hole strata** (the brief's one live
variant). Two sub-routes, and the step each dies at:

- *(C1) strata from the hole-marked defect gas.* The machinery exists and
  is exact (`results/defect-gas.md` §hole-marked gas, verified on all 26
  banked hole-resolved cells, j ≤ k ≤ 2) — but it is diagonal-law
  machinery whose cost is the cluster-weight DP, measured there at ≈20×
  per unit of surplus (k=4: 3.1 s, k=5: 65 s, k=6: >530 s; "realistic
  reach k ≈ 7 in Python, k ≈ 9–10 with a C++ effort"). The band needs
  k = n−H = **19..25**. Dies at the **cluster-weight computation**, the
  same wall that closed L2 — ~20¹⁰⁺ past reach, no modulus helps (the DP
  itself, not the arithmetic, is the cost).
- *(C2) stratified contour TM: track j inner curves.* Holes are extensive
  (mean ~0.018·n and rising at n ≤ 19; max hole count ~n/2, Kahle–Roldán
  via `results/maxhole-proof.md`), so j runs to ~20 at n = 40 — but the
  killer is structural, not the strata count: each stratum's TM must carry
  the outer-curve pairing state PLUS inner-curve nesting/assignment, so
  every stratum's state space contains the unstratified Motzkin object of
  §3. Stratification adds state; it never removes the wall. Dies at the
  **state-space step**: stratum states ⊇ route (B) states, and (B) is
  already the incumbent.

## 5. The three standard questions

1. **Does it reach H = 15..21 at n = 40?** No, by any variant. (A) cannot
   represent the objects; (B) reaches only at the production sweep's own
   cost with the production sweep's own state object; (C) dies at the gas
   wall (C1) or contains (B) (C2).
2. **At what cost, anchored on own measurement?** My anchor: the n ≤ 10
   enumeration (196 s for 6.05M animals with per-animal boundary
   analysis) plus exact arithmetic on the banked ranks. Route (B)'s state
   count is exact, not extrapolated: M(H+1)−1 states per column cut,
   4.0·10⁸ at H = 21, base drifting to Motzkin's 3 per row against the
   incumbent's measured 2.75–2.81 — the contour parametrization is never
   below the incumbent at any H. Route (C1)'s cost is the gas DP's
   measured ≈20×/k from k ≈ 7 to k = 19..25.
3. **Entry-ticket levels?** (A): neither. (B): level 1 yes, level 2 no —
   established. (C): level moot; dies before the ticket matters (C1
   inherits the gas's level-1-only status, C2 inherits B's failure).

A clean negative was the expected outcome; this one is established: one
lemma (king contour semantics), three measurements (pinch extensivity,
hole share, rank = Motzkin exactly), one proved identity (state-space
isomorphism via the off-branch theorem).

## Novelty greps

Claims needing novelty checks: the rank = M(H/2+1) identification and the
pinch-share measurements. Commands (both docs pathspec terms per the
standard; the harness's finding that `docs/**/*.md` alone misses top-level
docs is why both appear):

    git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'   # 1538 lines
    grep -iE 'contour|pinch|boundary-word|jensen|curve' <paths>   # 3 hits, none a counting route
    git grep -l -iE 'motzkin' -- 'results/*.md' 'docs/*.md'
    git show second-source:results/king-column-motzkin.md          # read in full
    git show second-source:results/scaling-exploration-A.md        # §A-S1/A-S6 rank discussion

Findings: no prior contour-encoding route anywhere in history. "Pinched
contours" appears once, in `results/maxhole-proof.md:242` (the moat-cycle
argument exercises pinch corners — a proof device, not an encoding).
The Motzkin state-count theorem is banked off-branch and cited above; its
own novelty trail says the strip series "had been Motzkin all along,
unidentified". The *cut-rank* equality — banked SVD ranks 21/51/127 equal
M(5)/M(6)/M(7) exactly — is stated nowhere: `scaling-exploration-A.md`
compares growth bases (2.4 vs 3) without the exact identity, and
`boundary-push-tensornetwork.md` says only "~ Catalan/Motzkin". That
identification is this file's one new fact. Not found is not proof of
absence.

## NOT ESTABLISHED

- The n = 40 hole share (≈55%) is an extrapolation from measured
  geometric decay at n ≤ 19 (n = 19 tier-degraded); establishing it
  exactly would need the declined holes-n≥20 campaign (~11 days at
  n = 20). The qualitative statement (majority holed, band-peaked) does
  not depend on the third digit.
- The simple-curve-class share at n = 40 (~10⁻¹⁰) is geometric
  extrapolation from four points (n = 7..10, ratio stable at 0.566±0.001).
  Only "vanishing" is load-bearing.
- The (B)↔incumbent state bijection is argued at the object level (§3,
  with the proved Motzkin theorem carrying the incumbent side and the
  exact rank equalities as corroboration); I did not build a contour TM
  and verify state-count equality mechanically at small H. Doing so is
  the one experiment that could upset the level-2 verdict, and I judge it
  phase-2-shaped and pointless: even if the contour states were a strict
  subset, the measured cut rank already equals the Motzkin count, so the
  information crossing the cut cannot shrink below it.
- H = 14's rank 298 < M(8) = 323 is explained here by the off-peak dump
  (maxn = 16); I did not re-dump at a peak column to confirm it closes to
  323.

## Appended 2026-08-12 (amendment: successor rows)

Per the lead's mid-round amendment and `results/triangle-r3-queue.md`'s
protocol, this lane's closures filed four successor rows, different in kind:

- **L3-1** — the rank = M(H/2+1) identity read as a family lemma: an exact
  *information* floor at any straight cut, sharpening L1-6's state-count
  version; rules in only no-cut and cancellation methods.
- **L3-2** — prove the rule rather than vary it: Lean/certified equivalence
  of the harness's three shared propositions with the topological
  curve-closure definition (Lemma 1). The level-2 failure of candidate (B)
  says the frontier rule and curve closure are the same mathematics; a
  proof of that equivalence answers the referee's objection at the
  definition level for every cell at once, with zero enumeration.
- **L3-3** — object change: fattening bijection to decorated polyominoes on
  a refined lattice, where the boundary is pinch-free (half-formed;
  level-1 value only, still pays L3-1's floor at a cut).
- **L3-4** — dual-side (moat) encoding: hole boundaries are simple cycles
  on the 4-connected complement, so hole strata are native there
  (half-formed; pruned as a full route by L3-1, filed for its
  stratification shape as a partner to L6-3).

## Appended 2026-08-12 (L3-2 dispatched: proof scope)

The lead dispatched queue row L3-2 to this lane. Full scope — the
(a)/(b)/(c) crux, existing Lean inventory, exact module plan, 3–5 session
cost, and the certified-checker verdict — is in
`results/triangle-r3-l3-proofscope.md`, with the executable spec at
`experiments/tristruct/r3_l3_schema_dp.py` (45/45 banked cells reproduced
by a literal transcription of the harness's three propositions; RED
stencil-break caught). Queue rows L3-5/L3-6/L3-7 filed.
