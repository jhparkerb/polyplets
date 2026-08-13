# Round 3 "Second Crown" — synthesis and ranked verdict

2026-08-12. Lead's synthesis of the round defined by
`docs/triangle-round3-brief.md`: one harness, five lane scouts, one
queue-dispatched scout, two adversaries, run in waves against
`results/triangle-r3-queue.md`. Per-lane detail is in the
`results/triangle-r3-*.md` files cited inline. Scoring is
`docs/skeptical-reader-standard.md`.

## Bottom line

**The round found a route, and it is affordable.** Rounds 1 and 2 asked the
triangle for a relation that predicts row 40 and got two proved negatives. This
round asked a different question — count the band again by a rule the referee
will accept — and the answer is yes, at 75 thread-hours for the block that
matters, with a second, cheaper route covering the corner the first cannot
reach, and a proof that closes the objection at the definition level for
everything at once.

Nothing here is banked. What follows is a phase-2 proposal with its go/no-go
number named, and it is jasonp's call.

Three pieces, deliberately aimed at different objections:

| piece | what it buys | share of a(40) | cost | status |
|---|---|---|---|---|
| **L3-5** Lean definition-level proof | closes the *rule* objection for every swept cell, zero enumeration | 95.85% | 3-5 sessions, no compute | scoped, `Tc_eq_T` already proved sorry-free in-tree |
| **L6-1** residue ladder, H=15..19 | exact values by a rule that never decides connectivity | **43.84%** | ~21.7 GiB, ~75 thread-hours, ayr | costed on an exact census |
| **INV-8** spin basis mod 2, H=20..21 | parity at the two cells the ladder cannot afford | 7.00% | ~0.3 GiB, single box | repriced 64x, no basis hunt |

H=20 exact is a fourth, optional piece: 68.1 GiB as a sole-tenant ayr job,
gated red-first on one measurable constant (below). H=21 exact is 215.8 GiB and
is off-ayr under any bookkeeping.

## The go/no-go number

**Bytes per window of the real binary.** The census is exact; the RAM is the
census times a per-state constant that the model puts at 104 B and nobody has
measured. H=20 fits ayr's 78 GB iff that constant is <= ~119 B, a 15% margin.
It is minutes of work at small H on ayr or dalby — RSS read against state count
— and it is the first thing a phase-2 brief pins. H=15..19 is comfortable at
any plausible constant; only H=20 turns on it.

## Why the route is independent, and how strongly

The mechanism is candidate B1 from the unmerged `second-source` branch
(`git show 5793ddf:results/second-source-candidates-B.md`): with
A_n(q) = Sum_S q^{c(S)} over n-cell subsets, the connected count is **[q^1]
A_n(q)**, computed by a frontier DP over colour-coincidence partitions in
Z[q]/(q^2). No union-find verdict, no stranded-component death, no completion
predicate — clashes zero rather than join, and connectivity is read off a
coefficient at the end.

The independence adversary settled the obvious objection by measurement rather
than argument (`results/triangle-r3-adv-independence.md`): the DP's cut states
strictly **contain** the incumbent's Motzkin object — identical through H=6,
strict superset from H=7, the surplus being exactly the crossing partitions
(323/843/2242 vs 322/834/2187 at H=7/8/9, matched by a third independent
implementation) — with the distinguishing state exhibited, a crossing ABAB
column at H=7 reachable in the colour DP and provably absent from the
incumbent's set. The dynamics differ in kind: the incumbent's defining move,
uniting two old labels, never occurs in the colour DP.

Honest limit, in the adversary's own words: the geometry is superset, not
disjoint, so independence rests on dynamics and failure modes rather than on
the state census. The route clears both entry-ticket levels; what it shares
with the engines is the adjacency definition and frontier separation, not the
propositions the referee doubts.

Three lanes reached this family independently — L6 from the literature, the
involution scout from the sign-reversing-involution tradition, and the
`second-source` branch's own lane A from the other direction. The involution
scout's derivation gives phase 2 a three-line referee-facing proof of what the
DP counts.

## The other half: prove the rule instead of varying it

`results/triangle-r3-l3-proofscope.md` is the round's best strategic finding
and it did not come from any lane's ticket paragraph — it came out of the
generativity amendment, from a lane that had just closed negative.

Three statements, not equally valuable:

- (a) the abstract frontier recurrence counts exactly the king-connected n-cell
  sets of height exactly H — a lemma, and half of it is already committed and
  sorry-free (`polyplets/Polyplets/Compute.lean:207`, `Tc_eq_T`, with
  `native_decide` cell pins; verified in-tree this session);
- (b) the algorithm as the harness worded it implements (a) — handled by
  literalness: a from-scratch 40-line DP written this round reproduces all 45
  banked cells 1<=H<=n<=9, fail-closed, with a RED run (stencil narrowed to
  {r-1,r}) aborting at 15 mismatches;
- (c) the compiled kernels implement (b) — program verification of optimized
  C++ with a carry byte and packed signatures. **Not proposed.**

What (a)+(b) buys: the chartered objection — `2b3115b`'s "shared misconception
about what is being counted" — closes at the definition level for every swept
cell, 95.85% of a(40), with zero enumeration. What survives: per-binary
implementation faults, and the band remains a single kink-kernel computation
that no theorem re-runs.

Two consequences worth as much as the theorem. It **retroactively upgrades**
every existing same-rule agreement — strip-TM's 469 cells, the dual kernels,
symtm — from "consistency check against an unproved rule" to
independent-implementation cross-checks of a *proved* rule. And it is the exact
complement of L6-1: the proof closes the rule half, the recount closes the
implementation half on the band. **Each alone leaves precisely what the other
reaches.**

Risk is concentrated in one induction (partition-sufficiency, Finset
path-splitting), uncalibrated against anything in the development. The fallback
is real and was verified: a conditional theorem on a named hypothesis, the
MoatBound pattern in `HolesUpper.lean`, plus the pin battery.

## Ranked ledger

1. **L6-1 residue/CRT ladder** — both levels, 43.84% at 75 thread-hours, exact
   census, one unmeasured constant. `results/triangle-r3-l6-wildcard.md`.
2. **L3-5 definition-level proof** — 95.85%, no compute, different objection.
   `results/triangle-r3-l3-proofscope.md`.
3. **INV-8 spin basis mod 2** — H=20..21 at ~0.3 GiB, reaches the cells the
   ladder cannot. `results/triangle-r3-involution.md`.
4. **L5 Lean witness** — levels 1+2, reproduces 21 banked cells at n<=6 with
   Mathlib's own connectivity instance and no project-authored connectivity
   code. Small n, but it is the round's only artifact a referee can run.
   `results/triangle-r3-l5-constraint.md`.

   **The hardening does NOT compile, measured 2026-08-12.** The two bridge
   claims — width <= n losslessness, and
   `T n H = Nat.card (Quotient (animalSetoid n H))` — were filed as "complete
   written proofs, no step missing", and job L5-JOB-1 (authorized on gympie,
   the one job that was) failed gate A with **9 errors at 6 sites**:
   an unknown constant (`Nat.card_eq_fintypeCard`), two `introN` failures, two
   failed rewrites, and — the ones that matter — two `omega could not prove the
   goal` plus `unsolved goals` at two further sites. Identifier drift is
   mechanical; unsolved goals are holes in the argument as written. Gates B and
   C never ran, so the truncated evaluation log is still truncated and the RED
   mutant is unexercised. **Repair deliberately deferred by jasonp,
   2026-08-12.** The claims stand as source with a known error list, not as
   theorems, and the standing lesson is: compile before believing any agent's
   "this is complete" about Lean source.
5. **L5-1 ASP recount of the mod-2 bit** — a third rule class on a row-40
   quantity over the lambda^(n/4) quotient, third-party evaluated. Gated on
   `sudo port install clingo`, jasonp's call.

## Closed, with the obstruction named

Each of these is a door, not a gap. Re-deriving any of them scores zero.

- **Corner gluing (L1).** Pieces are coarser than the animal but *not* than the
  frontier: the rook partition refines the king partition, so piece identity is
  extra boundary information. Measured piece-state closure exceeds the cell
  closure at every H>=3 and diverges (~1.15-1.18x per unit H). And squeezing
  **anti-concentrates**: mean_c/n rises with height, band cells are ~21 pieces,
  small-c strata carry ~1e-7. Both axes closed on measurement.
- **Contour encoding (L3).** Pinches are extensive (99.42% of n=10 animals),
  holes are extensive and peak in the band analogue, and the honest repair —
  the glued curve system — clears level 1 then fails level 2 by state-space
  isomorphism with the incumbent.
- **Symmetry quotient (L4).** **Mod 4 is the per-cell ceiling, proved**: D2ax
  is exactly the height-preserving subgroup, glides collapse, no order-8 group
  exists. The route itself is priced out by its own answer size — order-2
  invariant counts are ~lambda^(n/2). Decline reason 1 from 2026-08-07 was a
  strip-method artifact and is dissolved; the quotient `--byheight` route does
  classify by true lifted height.
- **Implicit routes to the invariant counts (LEAD-1).** No P-recurrence for
  Fix(h) or Fix(r180) over the 34 banked terms; no algebraic GF in a fitted box
  with holdout, RED-controlled both directions. Fixed-H rational GFs exist but
  their minimal orders blow up geometrically, and pinning order r needs ~2r
  rule-independent terms — more enumeration than the check would justify.
- **Non-group involutions (L4-3/LEAD-2).** The **two-horn obstruction**:
  move-validity is connectivity of the result, a global predicate, so a
  validity-aware site key drifts under its own move; make it validity-blind and
  images leave the (n,H) class. Franklin escapes only because partition parts
  do not interact; king cells have no move-invariant monotone statistic.
  Measured over four families, 176,411 animals. And the **forced-parity
  lemma**: any correct involution's fixed-set parity equals T mod 2 by
  necessity, so independence lives in the rule class computing |Fix|, never in
  the residue.
- **Pfaffian/matchgate parity (L4-4).** Edge-local machinery, global
  constraint, non-planar king graph; the genuine "parity is easier" content is
  the cancellation identity already held.
- **Enumeration-based third-party counters (L5).** Bounded below by the model
  count: the band sum is 2.885e31, i.e. 9e14 years at 1e9/s. Component-caching
  #SAT dies on the banked result that the cache must hold at least the frontier
  behaviours.
- **Everything the literature has (L6).** 35 candidates, pre-registered filter,
  kill counts 12/10/5/7, one survivor — and the survivor was already
  project-held. A tropical-circuit bound plus a compilation floor plus the
  measured cut ranks together say there is **no third route class** in the
  literature; the only escape from partition-DP blowup is algebraic
  cancellation.

## Three floors, and they are independent

The round found three separate lower bounds, each closing a different escape.
Together they are why every lane converged on the same short list.

1. **State floor** (L1-6). Any frontier vocabulary pays at least the cell
   frontier's state count; coarser objects do not help, because piece identity
   refines rather than abstracts.
2. **Information floor** (L3-1). Any straight-cut method in any vocabulary must
   transmit at least Motzkin(H/2+1) quantities across the cut — the banked SVD
   ranks *are* Motzkin numbers.
3. **Term-source floor** (L4-12, new). Any fixed-H recurrence route needs ~2r
   rule-independent terms of order r, and terms on this lattice cost c^n from
   any rule-independent source — they exist rule-independently only to n = 18.
   Exact band ceilings are now known (hmirror quotient states 2122..49720 at
   H=15..21, from Sum C(ceil(H/2),k) C(k,floor(k/2)) = A005773(ceil(H/2)+1)-1,
   with the v-mirror and C2 realizations paying full Motzkin), and even the most
   favourable untested order costs ~1e32 laptop-years against 75 thread-hours
   for the whole ladder. **General, not symmetric-specific.**

## One new structural fact, measured three ways

**The cut is an information floor.** Banked central-cut SVD ranks equal Motzkin
numbers exactly — 21/51/127 at H=8/10/12 are M(5)/M(6)/M(7) — so any
straight-cut method in any vocabulary must transmit at least that many
quantities across the cut. L1 reproduced the same object as Motzkin(H+1)-1 from
a piece-assembly construction, and the banked column-Motzkin theorem is the
third route in. That single fact explains why three lanes hit the same wall and
prunes the remaining search space to no-cut methods and cancellation.

A char-2 collapse is real but not yet buyable: GF(2) rank runs 0.44*2^H
(6/15/27/58/112/229 at H=4..9 against 20/50/126/322/834/2187 states), ~1000x
below B1 at H=21 and two orders above the spatial floor, but a rank is an
existence statement and the explicit basis — which CKN have for matchings —
does not exist here.

## Process findings

- **The novelty grep in the standing standard was broken.** `docs/**/*.md` never
  matched top-level `docs/*.md`: 251 historical paths vs 510 with both terms,
  missing 30 files including `docs/second-source-team-brief.md`, the ruling the
  standard itself cites. Two agents rediscovering that ruling unaided in round 1
  now has a mechanical explanation. Fixed in the standard with the measurement.
- **The blind-list experiment paid, in the direction that matters.** The scouts
  found the cancellation family — the round's only surviving route — and the
  lead's withheld seed list **does not contain it**. What the seed held that no
  scout found (Grobner counting, lace expansions, Martin/matrix-tree, automatic
  sequences) dies at the scouts' own filters or was covered without the name:
  **the seed was load-bearing nowhere**, convergence ~11/14. Seeding would have
  cost the round its product.
- **Generativity changed the outcome.** The queue (45+ rows) was opened
  mid-round after the first lane closed with one idea and a shrug. The two best
  findings in this file — the definition-level proof and the 64x repricing of
  the spin backstop — are both queue successors, not lane deliverables.
- **Measurement-provenance defect, the lead's.** The brief's "laptop minutes"
  allowance put every probe on gympie against the project's standing rule.
  Machine-relative figures (all "laptop-year" units, accept rates, the Python
  scale point) are calibrated to a machine that should not have been used;
  exact counts, censuses and validations are machine-independent and
  unaffected; and L6-1's decisive anchors are pre-round dalby measurements from
  the branch, so the flagship model's core survives. Seven processes were
  killed mid-flight; two lanes' partial results are labelled as such.
- **The entry ticket's vocabulary has a residue.** Two items the round could not
  state in "where is connectivity decided" terms, and which nobody picked up:
  **binary provenance of the a(40) run** (the harness filed it NOT ESTABLISHED,
  it is an afternoon of log headers, and it is the cheapest attack on the
  record), and archived-state replay of one in-band column.

## Recommendation

1. **Pin the go/no-go constant** — bytes per window of the real binary, minutes
   on ayr or dalby. Everything else waits on it only for H=20.
2. **Run L6-1 at H=15..19** if the constant is sane: ~75 thread-hours on ayr,
   43.84% of a(40) recounted by a different rule. **Gate it red-first on the
   small-n brute-force battery, and make the RED asymmetric.** Two independent
   findings say the elegant checks are blind: the DP's own structural
   invariants ([q^0]=0, A_n(1)=binomial) both pass while [q^1] is wrong if the
   NW stencil is dropped, and state censuses cannot see symmetric stencil
   errors at all — rook and king closures reach identical state sets at every
   measured H<=8. A symmetric RED control would pass a broken engine.
3. **Start L3-5** in parallel; it needs no compute and closes a different
   objection.
4. **INV-8** for H=20..21 mod 2, cheap, single box.
5. **Do the log-header audit** of the a(40) run's binary provenance. It is the
   one thing this round proved it could not see.

## CORRECTION, 2026-08-13 (round 4, lead)

**The INV-8 figures in this file are wrong. "~0.3 GiB, single box" in the table
above, in ranked-ledger item 3, and in recommendation item 4 must not be quoted
again.** This file was written at 20:26; `results/triangle-r3-spin.md` — the
wave-5 scout that actually repriced the route — was filed at 21:18, after the
last write to the round-3 queue at 21:09, and its five SPIN rows never landed
(`grep '^| SPIN-' results/triangle-r3-queue.md` returns nothing). The synthesis
therefore quotes a pre-correction number, and round 4's brief inherited it.

The mistake underneath is geometric: the dispatched premise took H=21 to force
W <= n-H+1 = 20, which is the *polyomino* bound. King animals violate it —
{(0,0),(1,1),(2,0)} has n=3, H=2, W=3 — and the spin file's own pipeline caught
it mechanically before anyone caught it by eye.

Corrected design, re-derived independently in `results/r4/r4-inv.md` (§1.2, by
hand against the banked W(18) = 20,346,159 and 3.032e13 at m=21, so the
arithmetic is now double-sourced): four runs at strip heights m = 18..21,
**22.6 thread-days and 9.4 GiB peak, 6.5 GiB dense-ranked**. The route is still
live and still the only thing that reaches H=20..21 — it is 75x the RAM and a
different job shape than this file said.

Two further findings from that re-derivation, both of which belong in any
write-up: the height second-difference accounting is **common-mode** with B1 and
the strip engine, one formula and one semantics; and forced parity clears the
independence bar against the kink engines but **not** against B1, since B1's
[q^1] of Sum q^{c(S)} in Z[q]/(q^2) and spin's evaluation at q=2 in Z/4 are two
extractions from one identity. That matters only for gating, because B1 cannot
afford H=20/21 anyway.

The round's chartered question is answered: the connectivity rule *can* be
varied within reach, on the block that carries the exposure, and the variation
is affordable. The triangle closes as a source of relations between cells —
rounds 1 and 2 settled that, and nothing here reopens it — but the count itself
is now reachable a second way.
