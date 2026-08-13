# Triangle structure hunt — synthesis and ranked verdict

2026-08-11. Lead's synthesis of the team run defined by
`docs/triangle-structure-team-brief.md`: Wave 0 (harness), four proposers
split by hypothesis class, two refuters, one round. Every claim below is
post-refutation. Per-lane detail is in the `results/triangle-hunt-*.md`
files cited inline; the harness is `experiments/tristruct/`.

## Bottom line

**Nothing reached Tier A or Tier B with real check value on a(40), and the
round's most valuable output is a negative.** The mission was: find a
relation that lets a(40) be checked by a route that does not re-run the
enumeration engines. Measured against that sentence, the honest yield is:

- one **proved theorem** about the triangle, worth **0 bits on a(40)** by
  its own construction;
- one **parameter-free in-grid relation** (the q_5 atom check) that
  certifies internal consistency of the banked triangle but is not
  rule-independent;
- one **independent recomputation** of columns 5–6, covering
  2.510·10⁻⁴ of a(40), which the project's own standing ruling classifies
  as a consistency check rather than verification;
- a set of **negatives that price the problem**, the sharpest of which says
  the largest exposed block of a(40) is not reachable by this frame at all.

No candidate produced a prediction of a(40), or of any substantial part of
row 40, from strictly smaller n. That outcome was anticipated by the brief's
own calibration section, which called Tier A a long shot and put expected
value in Tier C.

## Ranked survivors

### 1. Proved forced parity — `triangle-hunt-klein-parity.md`

T(n,H) ≡ 0 (mod 2) for n odd, H even. Proved from the definition by the
midline-reflection involution: reflection preserves n and H, non-fixed
animals pair, and for H even the row involution i ↦ H+1−i is
fixed-point-free, so every column of a fixed animal has even size and n is
even — the fixed set is empty for n odd.

Refuter B audited the proof line by line and it holds; the one subtle step
(the involution acts on translation *classes*, so invariance a priori means
reflect(A) = A + t) closes because reflection about A's own bounding-box
midline forces t = 0. That lemma is now explicit in the file.

Independently re-verified by the lead on the banked triangle: the region has
exactly **190 cells, 0 parity violations, 0 vacuous cells (no T = 0), and 0
row-40 cells**.

**Bits on a(40): 0**, and that is not a defect in the reporting — it is the
theorem's honest scope. Row 40 has n even, so the region contains no row-40
cell. What it buys is provenance: 190 cells of n ≤ 39 whose parity now rests
on a proof rather than on two engines agreeing. Increment over
`results/subgroup-mod4.md` was challenged and confirmed real but modest —
that file computes both sides of T ≡ I_H(D2ax) (mod 2) and never states or
characterizes any vanishing; the 190 zeros sit in the banked data as
silently absent rows.

### 2. The q_5 in-grid atom relation — `triangle-hunt-atoms-ab-initio.md`

The order-29 atom q_5 annihilates C_5(n) = Σ_{h≤5}(6−h)·T(n,h) for n ≥ 30
(certified to n ≤ 160 by the proposer, n ≤ 170 by the refuter). Zero free
parameters, unit coefficient on the target cell, region forced by recurrence
depth rather than chosen, 10/10 holdout rows, and all seven of the refuter's
perturbations of T(40,5) fail it.

Survived refutation outright, including an end-to-end independent
reimplementation (different TM construction, different Berlekamp–Massey,
different primes). Its supporting achievement is real and new to the repo:
**q_5 (degree 29) and q_6 (degree 68) as exact integer polynomials**, where
`results/triangle-structure.md` had only their degrees and had *proved* them
unreachable by fitting 40 rows. That also closes §6's squarefree/coprime
caveat for H ≤ 6 and verifies column orders 42 and 106.

Honest limit: it consumes 29 banked rows plus row-40 h ≤ 4, so what it
certifies is internal consistency of the banked triangle, not a
rule-independent count. It is the closest thing this round produced to the
second-source ruling's named higher prize (a tier-3 exact-arithmetic
certificate a short checker verifies) without being that artifact.

### 3. Independent recomputation of columns 5–6 — same file

T(n,5) and T(n,6) for all n ≤ 40 from an ab-initio strip transfer matrix,
matching banked on every cell. **Reclassified after refutation** from
"Tier B relation" to *independent recomputation, Tier B-equivalent scope,
not a relation*: there is no fit region, so "17/17 holdout" is agreement
between two computations, not prediction from smaller n.

The binding constraint is jasonp's standing ruling in
`docs/second-source-team-brief.md` (branch `second-source`, commit 2b3115b):
the strip transfer matrix **does not qualify as verification**, because its
union-find rule is the same rule as `core/transition.h` and the kink kernel.
Agreement is evidence against transcription, overflow and sharding faults,
and "no evidence at all" against a wrong shared connectivity rule. Refuter A
reached that verdict independently *before* the file was known to be
readable, then cited it.

Scope, measured: T(40,5) + T(40,6) = 2.510·10⁻⁴ of a(40). Residual value is
real but narrow — these are real-sweep cells checked against a no-shared-code
route, so a *systematic* all-column bug would fail here.

### 4. Symmetry-refined triangle structure — `triangle-hunt-sym-diagonals.md`

I(n,n−k) eventually quasi-polynomial of degree ⌊k/2⌋ with **no 3-power**
prefactor (contrast the diagonal law), and low-order recurrences for I(·,3)
(order 8) and I(·,4) (order 5, even-n). Refuter B did the strongest possible
thing — recomputed the entire claim surface with its own enumerator — so
these are now two-source, including I(40,3) = 187425 and I(40,4) = 8117.
That hardens the *inputs* of the banked row-40 parity check; it adds no new
bits to the check itself.

One real error was caught and fixed: the k=4 form needs m = ⌈n/2⌉, not
⌊n/2⌋ (as printed it failed at every odd n, first at n = 11).

### 5. Proved two-term cell inequality — `triangle-hunt-proof-first.md`

T(n,H) ≥ 3·T(n−1,H−1) + T(n−1,H) for 2 ≤ H ≤ n−1, with equality
T(n,n) = 3·T(n−1,n−1). Proved by two injections with disjoint images
(walk-cap with three offsets; grow-right), separated by top-row cardinality.

Refuter A audited both injections — well-definedness, injectivity,
disjointness, height leaks, and the edges H = 2, H = n−1, H = n — and could
not break it. Lead-verified independently on the banked triangle: **0
violations**, equality set is **exactly** the H = n column (39 cells), and
the tightest strict ratio is **1.0170 at (40,39)**, a number Refuter A
reproduced independently. Refuter A added the measurement that settles
vacuousness: worst global slack over every strict banked cell is only
**4.59×** (at (40,5)), i.e. the bound is within 2.2 bits of the truth
everywhere in the grid. It also holds on its own TM data out to n = 60,
beyond the banked grid.

**Bits on a(40): ~0**, as the proposer conceded — a one-sided bound, whose
equality column is closed-form territory. "Softer, proved, zero-input" is
the honest label.

## The negatives — where the real value of this round is

1. **The largest exposed block of a(40) is out of reach of this frame.**
   Row 40's H = 15..19 cells are **43.84%** of a(40) (lead-verified) and rest
   on a single production sweep. Proposer 1 gives a proof-shaped argument
   that each below-onset cell carries a fresh R_k coefficient visible at that
   cell alone, so the diagonal law's shape theorem imposes *no* relation
   among open residues — which also explains why every periodicity-class
   hypothesis over that region came back machine-BARREN. Conclusion as filed:
   no small congruence reaches the row-40 open cells.
   **Refuter A adjudicated this machinery and it stands, with one scoping
   correction.** The frame identity was verified computationally (for
   k = 1..12, (1−3z)^(k+1)·Σ_H T(H+k,H) z^H truncates to an integer
   polynomial of degree ≤ 2k+1 across the whole grid, and the mod-9
   refinement holds on every valid cell). The freshness logic is sound: mod 3
   the cell↔coefficient map is triangular with unit diagonal, so open-cell
   residues are in bijection with fresh r_{k,H} and the shape theorem alone
   imposes no relation among them. The scoping correction that matters: this
   is correctly limited to "of this frame" — a *cross-k* structure can still
   constrain sleeve cells, and the deficit families of negative 5 are exactly
   such a structure. What stands unconditionally is the pricing of the
   below-onset H = 15..19 block as unreachable by in-grid-fittable frame
   structure.

   On the companion algebraicity search: the empty kernel is a **genuine
   exclusion for the box**, not merely "none found" — a true algebraic
   equation inside the ansatz box would fit any truncation. The
   box-too-small escape is real and the proposer states it; the selftest on a
   synthetic algebraic series covers the false-negative-by-bug case.

2. **Recurrence-form column structure is dead above H = 4, permanently.**
   The exact minimal column recurrences first apply at n = 43 (H = 5,
   order 42 — corrected from 47) and n = 107 (H = 6). Both exceed 40, so no
   column-direction slice recurrence can ever predict row 40's tall columns
   inside a 40-row triangle. Only direct TM evaluation reaches them.

3. **The mechanical sweep's four survivors were all restatements.** Culled
   KNOWN-COINCIDENT once `known.py` learned the banked H ≤ 4 column
   recurrences. Confirmed from two directions: the ab-initio atoms give
   column H=3 true minimal order exactly 7, and the cross-lattice control
   found the same phenomena on the square lattice with its own orders.
   The one king-specific residue — χ ≡ (x+1)^r mod 2 at H = 3,4, which is
   what makes the periods tiny — was then killed too: q_5 mod 2 is *not*
   unipotent, so it is an H ≤ 4 accident, not king-wide structure.

4. **Only three slice directions are testable at all.** (0,1), (−1,1) and
   (−1,2) are the only directions with slices spanning both the fit and
   holdout regions; the other twelve, anti-diagonals included, have zero.
   Arbitrary-slope hunting is not merely unmotivated, it is untestable.

4b. **Fittable deficit lines and enumerated law-free cells are disjoint —
   by geometry.** This is the sharpest negative of the round and it closes
   the obvious "just aim the same method at enumerated cells" move. The 27
   enumerated law-free sleeve cells all have d ≥ 8 (H ≤ 21 with k ≥ 14
   forces d ≥ 2k−20). But fittability caps the class at d ≤ 6 (d=7 has only
   3 fit cells, d ≥ 8 at most 2). And every fittable line's k ≥ 14 cells sit
   at H = 2k+1−d ≥ 22, i.e. in the formula band, by the family's own
   geometry. So no fitted deficit-family congruence can ever touch an
   enumerated law-free cell. The only route across is the proposer's named
   proof: **a proved unit formula needs no fit region**, so levels d = 8..19
   would become checkable against exactly those 27 enumerated cells. That is
   the strongest single argument for the round-2 chase, and it is an
   argument, not a candidate.

5. **Geometry of the deficit families** (lead's own measurement, new here,
   and independently corroborated by Refuter A from the other end).
   Writing family_d(k) = (3k+1−d, 2k+1−d), the diagonal index is k and the
   exponent is e = n−1−3k = **−d**: every deficit family lies below onset by
   construction, with T = P_k(n)/3^d. Their residues mod 3 along k are
   **exactly period 3 for d = 1..7 and not period-3 for d = 8..15** — a clean
   boundary. A period-3 pattern over 11–13 points has probability ~10⁻⁴–10⁻⁵
   at random, so seven consecutive families is mechanism, not coincidence.
   This generalizes Proposer 1's separate d=3,4,5 observations into one
   statement and is the most promising lead the round produced.

   Refuter A reached the same place independently by extending the proposer's
   own class: it measured the d=6 line as exactly (2,1,1) by (k−6) mod 3 on
   k = 6..15, overturning the proposer's CULLED(FIT-ERROR) verdict — which
   was an artifact of the class's ≥2p fit-point rule (period 3 needs 6 fit
   points; n ≤ 22 gives d=6 only 4), not a fact about the line. That line
   carries **two** law-free matches, including a second open row-40 sleeve
   cell, T(40,25) ≡ 2. So d = 3..6 read (2,0,1), 2, 2, (2,1,1): every sleeve
   unit family probed so far is eventually periodic with period 1 or 3.
   Refuter A flags its own d=6 find as post-hoc (found by reading the full
   grid) and claims no bits for it — correctly. Refuter B then turned up d=7
   as (2,2,1) on k = 4..15 while running controls. The measured cycles:

   | d | 1 | 2 | 3 | 4 | 5 | 6 | 7 | ≥8 |
   |---|---|---|---|---|---|---|---|----|
   | cycle | (1,1,1) | (2,2,2) | (2,0,1) | (2,2,2) | (2,2,2) | (2,1,1) | (2,2,1) | none |

   Every one starts on 2 except the proved d=1, and the break at d = 8 is
   clean. Three agents reached this object independently and from different
   directions — the proposer by extending its class, Refuter A by reading the
   grid, Refuter B through controls, and the lead by direct sweep — which is
   the main reason to treat it as structure rather than mining artifact.

## Where the deficit families actually stand

Proposer 1 filed d=4 and d=5 as SURVIVES with "one law-free real-sweep cell"
each. **The real-sweep part is wrong**, and the harness had already recorded
it: for d=4 the holdout runs k=9..14, i.e. H = 15,17,19,21,23,25, so the two
highest-k cells (H = 23, 25) are `closed-form-Pk` provenance, and the k=14
cell the proposer names as its law-free confirmation is one of them. Same
structure for d=5. The d=3 family's row-40 prediction T(40,26) ≡ 1 (mod 3)
lands on a cell the harness marks `row40 0/1 real-sweep` — also formula-derived.

Neither d=4 nor d=5 has any row-40 cell at all (`row40 no-cells`,
`bits40 0.0`). So their direct check value on a(40) is exactly zero, which
the proposer did state; the correction is to the *independence* of their
supporting evidence, not to the bits.

Two different axes are in play here and must not be conflated. Refuter A
classified these cells as **law-free** — not derivable from `known.py`'s
in-grid diagonal law, because P_14 needs 15 window points and only 12 are
available (n ≤ 40). That is why they were not culled, and it is correct. The
lead's finding is about **provenance**: law-free or not, those cells' banked
values were produced by the engine's wired P_k closed forms, not by
enumeration. Both statements hold at once.

The two axes are close to independent, and the lead's first framing overstated
the overlap. Measured over the 42 law-free in-grid sleeve cells (k = 14..19):
**27 are real-sweep (H = 15..21) and 15 are closed-form-Pk (H = 22..26)** — so
the law-free region is majority enumerated, not majority formula. But every
law-free cell the deficit families actually touch falls in the formula band,
and that is **structural rather than accidental**: family_d has H = 2k+1−d, so
once k ≥ 14 the line sits at H ≥ 29−d, i.e. H ≥ 23 for d ≤ 6. All five
law-free confirmations across d = 3,4,5,6 — (40,26), (39,25), (38,24),
(40,25), (37,23) — are therefore `closed-form-Pk` cells by the geometry of the
families themselves.

On that basis Refuter A quantified the luck rate properly, using the right
null — the empirical residue distribution over all 42 law-free in-grid sleeve
cells (k = 14..19), which is statistically uniform at {0:16, 1:13, 2:13}. A
family-shaped pattern therefore hits one law-free cell with probability
≈ 0.31, and the three predictions made (d=3 → 1 at (40,26); d=4 → 2 at
(39,25); d=5 → 2 at (38,24)) pass jointly at **p = 0.0297**. Selection was
mild — one pre-registered class, four lines tried, the failure reported. So:
real signal, thin, ≈ 1.7 bits per family, and the proposer's own 1.585 claim
was marginally conservative.

The T(40,26) ≡ 1 (mod 3) hit is **real content, not an artifact** — the cell
is not law-reachable — but Refuter A repriced it downward: `ternary-spine.md`'s
sleeve-zero census already banks *which* sleeve cells are zero, so the zeros
retrodiction is a restatement with organizing value only, and what the pattern
adds at (40,26) beyond "nonzero" is the choice of unit — **1 bit, not 1.6**.

**Refuter B's ruling closes the referral, and it is the sharpest correction of
the round.** The proposer's "one law-free real-sweep cell per family" is not
merely mislabelled — it is **zero law-free enumerated cells, in every family**.
`known.py` is indeed silent at k = 14, but every k = 14 cell the families touch
— (39,25), (38,24), (40,26), (37,23), (40,25) — has H ≥ 22 and therefore
`closed-form-Pk` provenance. All six fit cells and five of six holdout cells
per family are k ≤ 13 and law-implied; the sixth is formula-wired. **No family
touches an enumerated cell it could check.**

So on the mission's own terms: **bits on a(40) enumeration = 0**, because the
cells in question were never enumerated — there is no count there to check.
Agreement at (40,26) checks the *wiring* of P_14, exactly as the harness README
warns.

The precise ruling is **formula-bounded but not self-circular**:

- *Not self-circular.* The wiring forces only the divisibility v₃ ≥ d (that is
  proved integrality); it never forces the **unit**, which is what the families
  claim. P_14 comes from tower structure plus two real anchors at (33,19) and
  (34,20), both real-sweep; the family patterns were fitted on k ≤ 8 sleeve
  cells, i.e. different diagonals. Neither side saw the other.
- *But formula-bounded.* The k = 14 banked values are wired-P_14 evaluations
  **extrapolated past its real-anchor range** (n = 36..40 > 35). Confirmation
  tests that extrapolation against an empirical cross-k regularity. Teeth
  against the P_14 pinning-and-wiring chain: yes, ~1.7 conditional bits each.
  **Teeth against any enumeration error, anywhere: zero** — nothing at those
  cells was ever counted.

One correlation caveat that deflates the joint figure: the law-free hits of
d = 3,4,5 (and Refuter A's post-hoc d=6 pair) all evaluate **the same one or
two polynomials**, P_14/P_15, at nearby points. That is ≈5 conditional bits on
a single object, **not four independent braces**.

Corrected independence field for the ledger: not "one law-free real-sweep cell,
~1.6 bits" but *one law-free closed-form-Pk cell; ~1.7 bits against
formula-chain error conditional on the pattern; nothing against enumeration
error.*

Luck is not the problem. Refuter B ran 131 comparable sparse control lines
through the same procedure: 13/131 passed, but 12 were constant-0 lines through
the proved zero region (cull fodder), leaving **1/131 post-cull — and that one
is the d=7 sibling line** (period (2,2,1), k = 4..15), i.e. same-class real
structure rather than a false positive. Excluding it as a non-control: 0/130.
The families are almost certainly real; what they lack is not signal but
*independence*.

## Process findings — defects in the brief itself

Recorded because they cost real time and will recur:

- **Three cited files were not on this branch.**
  `results/king-column-motzkin.md` and both second-source briefs live on
  `second-source`. The most consequential, `docs/second-source-team-brief.md`,
  is the ruling the brief invokes as governing independence — so the entire
  team worked without being able to read the standard they were judged by.
  Two agents independently rediscovered its central conclusion. The brief's
  prior-work list is now annotated with the commit hashes.
- **The prior-work list omitted `results/subgroup-mod4.md` and
  `results/percell-mod4.md`**, which between them already banked most of the
  Burnside/parity ground assigned to Proposer 2 — including the mod-2
  identity on all 820 cells *including row 40*. Now added.
- **A novelty claim survived into a refuter's own report** (the Motzkin
  identification called "new" when it is a banked theorem), which is the
  exact failure mode refuters exist to catch. Retracted in place.

One methodological result worth keeping, because the lead asked for the wrong
instrument and was corrected: **a perturbation study is vacuous for a
congruence class.** Refuter B's 268-trial perturbation calibration was the
right tool for the fitted quasi-polynomial class, so the lead asked Refuter A
to match that standard on the mod-3 families. It cannot be matched, and the
reason is structural — perturbing a cell changes its residue, which fails a
congruence by definition, so "0 false passes" is guaranteed and measures
nothing. The correct instrument there is the empirical base rate over the
law-free cells, which is what Refuter A used. Match the calibration
instrument to the hypothesis class, not to the previous round's report.

## Recommendation for round 2

The brief allows a narrow conditional second round of 1–3 agents chasing one
specific thing, and says to stop if round 1 produced nothing above Tier D.
Read strictly, the a(40)-check mission produced nothing above Tier D, and the
correct call is **stop**.

If one thread is pursued anyway, it should be the period-3 deficit-family
structure (negative 5), and both refuters converged on that recommendation
independently. Reasons: it is a single sharp statement with a visible break
at d = 8; it sits exactly on the sleeve/below-onset region that negative 1
identifies as the open ground, and is precisely the *cross-k* structure that
negative 1's scoping leaves alive; the proposer has named a concrete proof
route (Lagrange–Bürmann to the mod-3^(d+2) master curve, needing one more
tower level than `defect-gas.md` derived); and unlike everything else in this
round it is a *proof* target rather than a fit. As Refuter A puts it, the
correct next step is not more fitting — it is the proof route, which would
convert d = 3..6 from ~5 thin bits into theorems.

It would not check a(40) — negative 1 says nothing in this frame will, and
Refuter B's ruling confirms these lines touch no enumerated cell — but it
would close a piece of the ternary spine's stated open remainder.

The sharpest single target for that chase, handed over by Refuter B, is stated
on **real-swept** data rather than formula cells:

> v₃(P_k(3k−2)) > 3 **iff** k ≡ 1 (mod 3), verified through k = 11.

Lead-verified independently: v₃(P_k(3k−2)) = 3 for every k in range except
k ≡ 1 (mod 3), where it is 7, 4, 4 at k = 4, 7, 10 — all three real-sweep
cells — and 5 at k = 13. Exceptionless on enumerated data.

That is the organizing regularity behind the d=3 family's zeros, it lives on
enumerated cells, and it is a clean target for the Lagrange–Bürmann route.
Refuter B's d=7 sibling line (period (2,2,1)) is the companion case for the
proof-first lane. Together with the lead's d = 1..7 boundary (negative 5),
these are one coherent object, not four coincidences.

The decisive argument for doing it as a *proof* rather than more fitting is
negative 4b: fitted lines can never reach an enumerated law-free cell, but a
proved unit formula carries no fit region and would land directly on the 27
enumerated ones. That is the only identified path from this corner to a check
that touches counted cells.

Final tier ruling, adopting Refuter B's wording: **as checks on a(40), all
four deficit families sit below the acceptance ladder**; as braces on the
formula ecosystem and as proof targets, keep d = 3 and note d = 7.

The two things NOT worth another round: more slice/stencil mining (the
machine already swept it and the geometry limits it to three directions), and
further strip-TM recomputation (the ruling prices it, and coverage is not the
bottleneck).
