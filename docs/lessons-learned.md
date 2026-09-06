# Lessons learned

The postmortem of the polyplets project (jasonp and Claude, 2026-06-11 to
2026-08-22, plus the a(41) work of 2026-09-05) and one section per closed
campaign: what it set out to do, what it found, what closed it. Nothing here
is a theorem; the mathematics the campaigns produced is graded in the files
that hold it and cited from here. The numbers are campaign records: dates,
costs, counts, the arithmetic that closed a route. Where a later record
corrected a figure, both are stated and the later one marked.

Terms. The *triangle* is T(n,H), the number of fixed polyplets with n cells
whose bounding box has height H; a(n) is its row sum, and a value of it is an
*entry*. The *diagonal formula* says that at *level* k = n − H the entry is
P_k(n)·3^(n−1−3k) for a polynomial P_k, exactly for n ≥ 2k+1; that least n is
the formula's *onset*, and smaller n are *below onset*
(`docs/proofs/diagonal-law.md`). *Undertow* fixes each level's two constants
from below-onset entries corrected by a computable defect
(`results/undertow.md`). *Motley* is the transfer-matrix program that counts
by coloring and never decides connectivity (`docs/proofs/cutcount-identity.md`).
An *agent team* is a set of Claude sessions run by one directing session,
*the lead*; a *lane* is one agent's assignment; an *adversary* is an agent
charged with refuting; a *receipt* is a log path in the tree backing a status
claim; a *wind-down* is a round's closing record. *Fable* and *Opus* are the
two Claude models used.

## 1. The arc

| when | what |
|---|---|
| 2026-06-11 | first commit: scaffolding, the Redelmeier oracle, the campaign harness |
| 2026-06 | the transfer-matrix engine, 460 commits |
| 2026-07-03 to 07-04 | a(30) through a(34) land in about thirty hours |
| 2026-07-06 | a(40); the enumeration of new terms by height stops here |
| 2026-07 to 08 | the analytic side: the diagonal formula, the λ bracket, non-D-finiteness, the mod-3 spine, below-onset defects; nine short papers drafted |
| 2026-08-17 | the literature-priority rule adopted, after a result was found to be published |
| 2026-08-20 | Undertow, and a(41) the same day |
| 2026-08-21 | the Motley runs land: a(40) confirmed in all forty entries, a(41) confirmed by an independent program |
| 2026-08-22 | the pre-landing work list closed |

At 2026-08-22: 1,482 commits, three home machines, thirty-three gates. The
published frontier of A006770 at the start was n = 18.

**Did it deliver.** Against the stated goal, extending A006770 past n = 18:
yes, by twenty-three terms, a(n) confirmed by two independent programs for
every n ≤ 41 and every entry of row 40. Against the harder goal, a new way to
count that reaches well past n = 40: no. The closed-door inventory says the
three method classes are fenced: cut methods by an information floor with no
known construction, no-cut methods by λ^n, cancellation methods by the
absence of an explicit basis (`results/closed-doors.md`, planned).

## 2. Six failure classes as day-one practices

From the first postmortem (2026-07-15); all six held afterwards.

1. **Lab and publication repository split.** Exploratory files and
   publishable artifacts in one tree cost real cleanup time.
2. **Machinery, not advice.** Every process rule that mattered became a
   script, a gate, or a checker; the ones that stayed prose were violated.
3. **Provenance and expiry.** Every recorded number carries its engine
   revision, machine, and validation; anything without provenance rotted.
4. **Result store first.** `results/*.md`, written at the moment of the
   result, was the single source of truth.
5. **Design the close at the start.** The close target existed only from
   mid-project.
6. **Collaboration contract.** The agreements of section 8 took months of
   friction to converge.

## 3. Verification culture: what caught errors

- **Withheld points everywhere.** Every fitted object (P_k, the
  diagonal-mirror quasi-polynomials, generating-function recoveries,
  recurrences) was fixed from the fewest admissible points and required to
  predict the rest. This caught a spurious order-7 recurrence for the
  all-pairs weights (refuted at l = 16 by a non-integer prediction) and two
  spurious PSLQ minimal polynomials (a degree-4 candidate's residual jumped
  fifteen orders of magnitude at higher truncation).
- **Control calibration.** A test's power must be shown on a known case. The
  convex-perimeter D-finiteness guesser first failed its own control
  (A005436, known algebraic); fixing the test until the control passed made
  the king-convex result trustworthy. The Convex Mirage's non-D-finiteness
  test is credible because the known non-D-finite control also fails it
  (`docs/proofs/convex-mirage.md`).
- **Two-algorithm agreement as the top tier**, decorrelation next, never
  silently mixed (`results/confidence.md`).
- **The master equation as a bug detector.** Cluster-weight enumeration
  windows were wrong three times; twice a downstream exact identity caught
  it by missing by a small integer (h3 off by 18 made W(2,2,2) off by 2).
- **Mod-p certificates.** Squarefreeness, coprimality and irreducibility of
  large polynomials certified modulo one or two primes, rigorous in one
  direction; a multi-prime subset-sum intersection certified a degree-462
  polynomial irreducible in seconds.
- **A gate comparing two derived artifacts cannot see a stale input.** The
  provenance gate regenerates the front-door table and fails if the note
  disagrees. On 2026-08-22 the generator still carried Motley's height as 18
  while the recorded rows had held 19 for a day; both were stale and the
  gate was green. The fix derives the constant from the recorded rows.

## 4. Bestiary of computational bugs

- **Window and truncation bugs, three times.** Tell: a downstream identity
  off by a small integer. Rule: a window needs a proof (spread less than the
  count) or a widening-stability check.
- **Float rot, twice.** Big-integer coefficients overflowed a float
  evaluation; the wrong root briefly faked a monotonicity violation in the
  strip growth constants μ_H. Rule: exact or multiprecision arithmetic for
  anything feeding a conclusion.
- **PSLQ and lattice-fit noise.** A relation consuming as many digits as the
  input provides is a coin flip. Rule: coefficient digits times degree well
  below reliable digits, then re-verification at higher precision.
- **Premature commit, twice in one day.** Rule: the assertion runs before
  the commit, mechanically.
- **Stale artifacts that look like data.** An unvalidated generating function
  (H = 11) sat in a results file and was nearly consumed by an analysis pass;
  a structural invariant flagged it (it shared no roots with its neighbors).
  Rule: a quarantine namespace.
- **External data is data too.** A published OEIS comment (A187077,
  "equivalent to row-convex polyhexes") was measurably wrong. Rule: cite it,
  then check it.
- **Asserted prices propagate.** The height-20 enumeration for a(41) was
  quoted at "20 to 30 hours, 450 GB" before anything was measured and copied
  into three places, one the launch script's own header; the measured run
  was 9.63 hours on 76 cores (`results/a41/PROVENANCE.md`). Rule: a number
  is not quotable until measured, and an estimate is marked as one.
- **Measurements that live on a compute box.** A cell-sparsity result sat in
  a home directory on ayr for two days while three tracked documents promised
  the file. Rule: a number on one machine only is not a result.
- **Review queues stale in the reader's favor.** The Undertow review queue
  still read OPEN on rows the Motley runs had answered.

## 5. Research-process lessons

**The largest lesson: two months optimizing an implementation before
questioning the rule it served.** The classical rule fixes a level of the
diagonal formula from its two tallest entries. Under it, row 40's top two
heights were three quarters of the processor time and took disk from 69 GB
to 363 GB; reaching them took the cell-at-a-time transfer step, work
stealing, spill formats, a 4.6× tmpfs win, fleet scheduling and a failed
two-media plan. Undertow says those entries were never needed: below-onset
entries, corrected by a derivable defect, are equally valid equations, and a
level needs only two. It arrived on 2026-08-20, week ten of ten, and gave
a(41) that day from an enumeration stopping at height 19. The defect
mathematics and the proof that each level carries exactly two constants
(`docs/proofs/grand-form.md`) were already in the results directory. What was
missing was a pass asking what the project assumed it had to compute.

- **Measure, don't reason.** A shortcut to P_17 through the defect gas was
  killed by a three-point timing extrapolation instead of a week of theory;
  "is there insight in the box table?" was answered by an afternoon probe
  with a pre-registered verdict.
- **Grep, and look up the OEIS, before claiming new.** Convex polyplets were
  re-derived once in ignorance of a deeper recorded investigation; the
  Temperley generating function once before checking the OEIS.
- **Priority passes belong before derivation.** The rule came on 2026-08-17,
  after a result was derived at length and found published. The retroactive
  passes over nine papers found one central identity was
  Fortuin–Kasteleyn/Potts, one square-lattice column reproduced
  Asinowski–Barequet–Zheng, and one negative was weak. Ghost Ship's third
  layer was in Richard, arXiv:0704.0716; the minimum-site-perimeter closed
  form was A235382.
- **Negative results are results.** The measured dead ends (matrix-product
  rank, banded encodings, bounded-depth recurrences, P_17 from the gas, root
  recycling in the convex family) each prevented a re-investigation, and two
  (root separation and its convex counterpart) became ingredients of
  theorems. The closed-door inventories, written at the moment of each kill,
  are the most useful documents for anyone continuing
  (`docs/lastditch-campaign.md`; `results/closed-doors.md`, planned).
- **Correction in place, next to the claim.** Struck paragraphs and
  superseded readings stay with their reasons; that is why the numbers can be
  trusted although the descriptions around them moved.
- **Name things.** Undertow, Motley, Confetti, Ternary Spine, Kink Carry,
  Ghost Ship, Skeleton Key, Coin Lift, Convex Mirage: named results get
  remembered and not re-derived.
- **The best tool transfers.** One proof template (walk, clusters, partial
  fractions) pushed through every object in sight gave the height,
  hole-graded, hex, square, polyiamond and diagonal-mirror formulas.
- **The gate suite was the best single decision.** Thirty-three gates,
  written to fail first and fail closed, run before every push; on the last
  day they caught a dangling citation, a residual-entry claim stated in prose
  instead of generated, and a quoted table that had changed under its note.

## 6. Luck

A method that worked because the problem was kind should not be sold as a
method that works.

**Lucky.** The triangle had exact, provable structure on its diagonals;
nothing guaranteed a polynomial times a power of 3 with a sharp onset. The
below-onset error was structured, not noisy: algebraic at depth 1 (an
irreducible quartic), closable at depths 2, 3 and 4. The machinery is
lattice-generic (the diagonal formula holds on every row-local lattice, the
master equation is parametric in the drift b), discovered late, and it is
what made an external validation channel possible (`results/undertow.md`).
A genuinely independent second algorithm existed, the cut-count identity.
The sequence was under-explored at n = 18. Three home machines were just
enough: dalby's 125 GB and 76 cores fit the H = 18 and H = 19 Motley passes,
the H = 19 prime pass peaking at 63 GB. Two power cuts on ayr, which is
mains-exposed, missed the long runs: one on 2026-08-07 killed a perimeter
run; the 22-hour a(30)..a(34) run and the week-long a(40) run were untouched.

**Unlucky.** λ's upper bound is blocked by a barrier the project then
proved: the certificate method's over-count is diffuse and grows with n, the
signature of a non-local constraint no finite window sees, so the whole
finite-type class floors strictly above λ and the bracket [6.543, 9.3154]
stays wide around a value estimated at 7.11 (`results/growth-constant.md`,
planned). The sequence is not D-finite, proved unconditionally
(`results/anisotropic-not-dfinite.md`). Seven algorithmic ideas (a new
enumeration axis, the finite-lattice method, boundary compression, a
holonomic accelerator, the 45° axis, the dual-connectivity transfer matrix,
rank compression) were all measured dead against the cost of tracking
connectivity; the two genuine openings, the characteristic-2 rank collapse
and the characteristic-0 Hankel room, are real and non-constructive. Several
results collided with the literature after long derivations. H = 21 was out
of reach by a factor of about two: the keys alone are 135 GB
(`results/second-sources.md`, planned).

**Both.** Undertow arrived at all: lucky. In week ten: unlucky, and section 5
says why it was not only luck.

## 7. Action items for the next attempt at a mathematical contribution

Ordered by expected value.

1. **Budget a "what are we assuming we must compute?" pass**, on the
   calendar, in week two and whenever a cost estimate crosses a threshold.
2. **Run the literature-priority pass before deriving.** Minutes.
3. **Design the external validation channel on day one**: which published
   number will the machinery reproduce that it did not produce? Every
   internal cross-check shares your conceptual errors.
4. **Every gate must touch ground truth somewhere.** Derive constants from
   the evidence; never hand-edit one a gate then checks against a note.
5. **A result is not a result until it is in the repository**, with its
   provenance, the day it lands.
6. **Never let an unmeasured number become quotable.** Mark estimates as
   asserted and re-mark them when measured.
7. **Keep a kill inventory as a first-class artifact**, each dead end with
   what killed it, as the entry point for anyone resuming.
8. **Apply an accounting test before opening a file**: equations against
   unknowns, ansatz coefficients against data, image size against the
   literature record.
9. **Distinguish a bijection from a reduction.** A map onto another class
   restates a counting problem; it killed a correct construction here that
   survived two rounds of triage.
10. **Name the sentence that gets shorter** before starting any work.
11. **Write the collaboration contract on day one** (section 8).
12. **Separate the lab from the publication from the start** (practice 1).
13. **Record luck as luck**, next to the result it touches.

## 8. Operations and the collaboration contract

Operations (`docs/job-checklist.md`, `docs/observability.md`,
`docs/engineering-standards.md`): fleet sizing from all-core benchmarks,
rebalancing by contiguous ID ranges, per-worker RAM as total times margin
over cores; one tmux session per machine, jobs in foreground windows with
logs and heartbeat lines carrying progress and eta, no jobs from standard
input, no pattern-kill; the observability standard as shared code (`obs.py`,
`cpp/obs.h`); the job-start checklist before any compute launch.

The contract, as converged: direct answers in the asked format first, no
adjacent offers; match verbosity, never restate the human's point; small
samples before full runs, no job over an hour without explicit agreement,
and once a frontier job is healthy only correctness restarts it; autonomy
within a turn, options at decision points; externally visible actions (OEIS,
email, publication) are the human's exclusively; all authorship
representations are the human's own words, meaning-checked only.

## 9. Closed campaigns

### 9.1 The triangle-structure hunt, 2026-08-11 to 08-13

**Set out to do.** Four agent-team rounds on the branch `triangle-structure`
(`aa2b1eb..1e1a2ff`, about 44 hours wall, about 44 agents) to buy a(40)
checkable by a route that does not re-run the enumeration engines, or a
proof closing the objection that every program producing row 40 tracked
connectivity by the same rule. Round 1 (seven agents): find a relation that
checks a(40). Round 2 (four agents): prove the deficit-family unit formula
and push it to depths 8..19. Round 3 (fourteen agents): recount the exposed
band H = 15..21 of row 40 by a different connectivity rule, or prove none in
reach. Round 4 (nineteen agents): execute round 3's proposal. Rounds 1 and 2
ran in one day; round 4 opened four hours after round 3's brief and
overlapped its wind-down.

**Verdict: failure**, on the standard the campaign wrote for itself: bits
against enumeration error on the exposed band, as a checker a referee can
run in an afternoon. Round 1: two theorems and a parameter-free relation,
about 0 bits on a(40). Round 2: the depth-3 formula proved, about 1.6 bits,
and its own premise refuted, since the H = 15..19 entries of row 40 sit
below the formula's onset at every depth. Round 3: nothing recorded, and
both headline prices wrong when written (an instrument at "0.3 GiB" against
a corrected 9.4 GiB, later re-priced 208× the other way; a "43.84% largest
unconfirmed block" written hours after H = 15..16 had been confirmed).
Round 4: T(40,15) and T(40,16) confirmed by an independent program, but
recovered from a pre-campaign run of the cut-count program on dalby, not
produced by the round; its instruments largely written and unrun at the
stop. Of three impossibility floors audited in the final hours, two are
wrong as stated, so no sound proof that the check is out of reach was
delivered either.

**What it found, kept.** The depth-3 unit-formula theorem, which survived a
hostile audit on independent code and a nine-corruption battery; the parity
theorem; q_5 and q_6 as exact integer polynomials; the mod-4 ceiling
(`results/arithmetic-structure.md`, planned). T(40,20) ≡ T(40,21) ≡ 1 mod 2
by the involution route, twin runs identical on ayr and dalby, not
independent of the cut-count program. The Lean encoding layer for the strip
automaton (`polyplets/`), sorry-free on standard axioms; its six-gate
battery first ran during salvage on 2026-08-13 (gympie, Lean toolchain
v4.31.0), failed on its own bug (a sorry-count pattern written for ASCII
quotes where the toolchain emits backticks), and passed after a one-line
fix: the wind-down's "encoding layer proved" was true and had been claimed
over a gate that had never run. The a(40) provenance record audited clean
with one erratum and one named gap, and the dalby run evidence was recorded
with checksums (`results/ns_a40/PROVENANCE.md`,
`results/ns_a40/dalby-run-evidence/`). The negative map: three testable
slice directions, column recurrences dead above H = 4, the onset
disjointness, the Motzkin information floor (`results/closed-doors.md`,
planned).

**What closed it.** jasonp stopped rounds 3 and 4 by instruction; neither
had a functioning internal stop. The salvage merged on 2026-08-13
(`bb897b1`). The band the campaign failed to confirm was confirmed on
2026-08-21 by the Motley runs.

**Root cause:** an idea-generation engine with no fail-closed verification
layer between the lead's summaries and the next round's premises, running
faster than its own corrections could propagate. Transfer between rounds ran
through one synthesis the lead wrote at round close from pre-correction
figures: round 3's queue closed nine minutes before its last scout filed, so
round 4 inherited a 30–75× error and spent its hours re-deriving it. The
lead reported instrument status from memory rather than receipts, and every
drift upgraded an unrun instrument to a completed one, none the other way.
Every control the campaign ended with was invented mid-round, after the
failure it addresses. The stop rules eroded each round: round 1's synthesis
agreed "the correct call is stop" and hedged in the next sentence; round
2's go/no-go fired and was converted to a go in the same file; round 3's
stop was withdrawn by instruction. It failed four times rather than once
because each round's sharpest output was a negative that should have ended
it, and no new round's premise was adversarially reviewed before launch;
round 2's died to two lines of arithmetic already in hand, k = n − H and
d = 2n − 3H + 1 against the proved onset. The lead authored the briefs,
dispatched the adversaries and wrote the syntheses, and nothing audited the
lead until one agent did so uninvited in the last round. Also on the record:
a governing standard unreadable on the branch; probes on the laptop against
the standing rule, eleven processes killed, two agents' unfiled context
lost; a false width premise propagated through three artifacts before a
stability check caught it at (n,H) = (4,3); gate claims without logs, twice,
once repeated after the fix; a wind-down that miscounted its own team; the
novelty search silently missing thirty top-level files for two rounds; the
agent lifecycle misread (idle is not exit), nine agents found alive twelve
hours past their obituary and fresh agents spawned nineteen times to re-read
what idle agents held; no accounting of agent time, the one resource
consumed; Fable at 97% of quota, forcing round 4 onto Opus where the
fail-closed checks were least built.

**What went well.** The adversary layer worked every time it was pointed at
something, and nothing an adversary confirmed later fell. The write-ahead
rule turned agent death from lost context (three times in round 3) to
resumable (none in round 4). The blind protocol paid: the scouts found the
only surviving route and the lead's withheld seed list did not contain it.
Lanes were honest: every weakness the round-4 adversary found had been
written down by the lane that created it. The largest result survived by
luck: the cut-count rows and the uncommitted source that produced them sat
untracked on dalby for two days before `bd31a58` recovered them.

**Action items:** an adversary on the brief before launch, with kill
authority; stop rules the lead cannot waive, evaluator named; receipts from
hour zero, one row per instrument, syntheses quoting status only from them;
the queue as the sole carrier between rounds; controls before results are
recorded, one oracle free of the production engine per built binary, as a
gate that must fail on a broken input; one round per day; a census by the
method that works, idle agents continued rather than respawned; compute
through the dispatch protocol from round one; agent time accounted like
thread-hours, Opus only behind checks that already exist; keep write-ahead,
blind lists scored against a withheld seed, two-bit-count pricing, and
adversaries by standing question.

The working records (`results/r4/`, `results/triangle-r3-*`,
`results/triangle-salvage.md`, `docs/agent-types.md`) were deleted
2026-09-06; `git show e5e7870:<path>`. Some per-agent records were filed
only on the unmerged branch `triangle-structure`.

### 9.2 Rook parity, 2026-08-13

**Set out to do.** The goal, recorded 2026-08-13 after the triangle campaign
failed:

> Reduce the base of the exponential running time of polyplet counting to
> rook parity: c ≤ √3 ≈ 1.73 in O*(c^n), the proven base of the polyomino
> state of the art. Constant-factor and polynomial-factor improvements,
> however large, are out of scope. Test: a(40) recomputed end to end by the
> new method, using no anchor entries or intermediate values from the
> recorded run.

"Reducing the base of the exponential" is the Fomin–Kratsch O*(c^n) sense;
"exponential speedup", "asymptotic improvement", "better upper bound" and
"subexponential algorithm" mean other things and were excluded.

| bar | meaning | verdict |
|---|---|---|
| 2.67 = √λ_king | the first draft | refuted at the desk: the production engine is already below it under every λ in [6.543, 9.3154] |
| 2.01 = √λ_rook | "as cheap as polyominoes", mis-derived | nobody's cost; polyomino counting is proven O(n^(5/2)·√3^n) (Barequet–Moffie 2007), about 1.41^n with pruning, record n = 70 |
| √3 ≈ 1.73 | the rook method's proven base | chosen |

The route was the closed forms of the diagonal formula, not transport to the
rook lattice. Heights 20 and 21 were 84% of the a(40) processor time
(1,116,858 + 3,329,644 of 5,318,465 s), so an enumeration to H ≤ 19, plus
P_k computed from first principles to k = 19, plus the closed depth-1
correction at k = 20, recomputes a(40) with no anchor entries at composite
base max(√3, √g), g the per-level growth of the first-principles cost:
g ≲ 3 is parity, g < 5.9 still beats the production engine. Transport was
out of scope: the transport literature is directed only
(Gouyou-Beauchamps–Viennot 1988, Bousquet-Mélou–Rechnitzer 2002, Bacher
2015), every localization probe in the tree was measured dead, and a
reduction with linear size blowup β wins only for β < ln 2.42/ln 1.73 = 1.61,
while the block map is β = 4 and the diagonal splice β ≥ 2. Gates: measure g;
a(30) end to end with the fitted per-term cost ratio over n = 24..30 below
the production engine's, plus a control dropping the northwest stencil that
must fail; a(34) against its telemetry; a(40). Two corrections the goal
rested on: the transpose cap min(H,W) ≤ n/2 claimed in the finite-lattice
record does not hold for king animals (a diagonal staircase has
min(H,W) = n), and its "essentially optimal" claim rests on floors the
triangle audit found two-thirds over-applied (`results/closed-doors.md`,
planned); the polyomino record in project documents was stale at n = 56
against n = 70.

**What round 1 found.** One desk-only round, six Fable agents, no compute
(`e72e5ac..4a90412`; the consolidation note of 2026-09-06 dates the round
2026-08-16..17, the commits are dated 2026-08-13, and the commits are the
record). From `HANDOFF.md`, the 2026-08-14 entry:

- The production engine's base is b = 1.7266 = √2.9813, from the a(40)
  run's per-height processor-time ratio, phase C over phase B
  (3,329,644 / 1,116,858), on the treadmill of one height per two terms:
  0.3% below the √3 bar. The goal's own "about 2.42–2.5" for the same
  engine was a pre-kink state-growth number from another engine on another
  trajectory, and its 1.61 is the state-count base, a lower bound on cost;
  1.7266 is the figure the record holds.
- The figure is conditional: on a frozen fence the ratio is 2.98, and it was
  still rising (2.60, 2.73, 2.98 across H = 18..21); if it crosses 3, b
  crosses the bar from below.
- Gate 0 killed the first-principles P_k route: g ≈ 20 per level (21.0 at
  k = 4→5, lower bound 8.15 at k = 5→6); even at g = 3, k = 9 to 19 is 7.4
  years of 16-thread dalby. But gate 0 measured the wrong object: the a(40)
  assembly consumes two rational constants per level, not the weight
  dynamic program, and depth ≤ 4 below-onset entries are closed from first
  principles, so every level is fixable from the route's own H ≤ 19
  enumeration. Not a rescue: both routes enumerate to half height, the
  re-anchored route's base is b, and deleting phases B and C is a constant
  factor, out of scope by the goal's own terms.
- Transport is dead unconditionally: the floor on all injective reductions
  is β ≥ ln λ_king/ln λ_rook = 1.244 rigorous, 1.400 at best estimates,
  against a budget of β < 0.994 at b = 1.7266; β ≥ 2 for the diagonal splice
  is derived and tight.
- Rook shows no characteristic-2 crack: GF(2) Hankel ranks 20, 49, 119, 288,
  696, 1681 at H = 4..9 on a state space identical to king's, about 2.42×
  per height, mod-p exactly full. King's 0.44·2^H collapse is specific to
  the king stencil.
- For any future gate: a bottom-anchored transition defect cancels exactly
  in the exact-height second-difference telescope, so the corrupted engine
  still reproduces A001168 for n ≤ 8. A planted anchored defect is needed,
  not only the dropped stencil.

**What closed it.** jasonp's verdict, with the evidence agreeing: the goal
is not well-formed. The bar sits 0.3% above what the engine measures, the
test is passable by the production engine, and the bar contradicts the figure
it was set against. His process lesson: the round's controls were aimed at
transmission failures while the failure was target selection again; the
base-anatomy audit was the goal's own first question and ran in parallel
with three lanes that depended on its answer. Not restarted. The receipts
gate the round introduced was retired 2026-09-06 with its records
(`results/rook1/`, `docs/rook1-brief.md`, `docs/rook-parity-bar.md`;
`git show e5e7870:<path>`). The two base changes on record, kink carry (4.4
to about 2.5 in state growth) and Barequet–Ben-Shachar's rotated boxes
(n = 56 to 70 on the square lattice), both came from pricing an unpriced
design choice; the proven Motzkin exponent of the straight-cut vocabulary has
never moved on any lattice.

### 9.3 Ghost Ship, 2026-08-15 to 08-17

**Set out to do.** An unattended loop: fourteen fresh Claude sessions
launched by cron on dalby (`scripts/ghostship/run_session.sh`), each reading
a sealed 21-file snapshot of one research slice (convex and perimeter king
animals, at `74b2c20`) and its predecessors' reports, with no memory, no
project instructions and no operator. Preregistered with sealed hashes for
both predictors' forecasts, an answer key and a mechanical verdict rule.
Baseline: the interactive session of 2026-07-12 that took the same slice
through a three-step target path. Four questions: cost per step against the
baseline; whether a broadcast-only operator bulletin steers; the token shape
across sessions; each predictor's calibration. Sealed predictions: jasonp,
step 3 by session 10, seven re-derivations, 33% bad claims, over 3× cost;
Fable, step 2 by about session 9, step 3 never, two re-derivations, at
least 15× cost. The run was compressed to one day at jasonp's direction
(10:20 to 20:38 EDT, 2026-08-15) and graded that evening in the
preregistered order: claim table filed and hashed before either prediction
was opened, verification by three fresh agents with provenance stripped,
prediction scoring with authorship stripped. Claim-table sha256:

    c7cebc99c5ef9ff07806b482e39585edb44c8ffce8adb134adf8877de8c63561

**Verdict, by the sealed rule.** Did poorly, on the step criterion alone:
step 1 in session 1 in about 19 minutes of model time (the baseline took
24), steps 2 and 3 never visited. Every other failure trigger was clear, and
claim hygiene was clean beyond either forecast.

| claims | 64 |
|---|---|
| verified by execution (mostly re-implemented by the graders) | 58 |
| verified by reading | 5 |
| vacuous | 1 |
| false, unfalsifiable, missing receipt | 0, 0, 0 |
| VERIFY lines, sound | 31, 30 |

Registered-prediction discipline appeared unprompted in sessions 7, 11, 13
and 14, every prediction later confirmed. Zero failures in fourteen sessions
bounds the per-session pathology rate at about 0.21, no better.

| | loop | baseline 2026-07-12 |
|---|---|---|
| steps reached | 1 of 3 | 3 of 3 |
| model-active wall | about 356 min | 172 min |
| raw tokens | 91.13M | 123.18M |
| cost-weighted | $225.20 | about $140 |
| cost per step | $225 | about $47 |

Fewer raw tokens than the baseline, 1.6× the dollars; the per-step ratio of
about 4.8× is a numerator-of-one effect. The bulletin question was not
tested: the file was never written, and the operator ruled that blind
steering had no legitimate content given foreknowledge of the target path.
The token-shape question was lost to instrumentation (per-session totals
only; spikes track compute-heavy sessions, 17.5M, 21.1M and 12.0M tokens in
sessions 9, 12 and 13). Calibration: jasonp 1 hit, 1 partial, 7 misses of 9
calls; Fable 4 hits, 6 partials, 5 misses, 1 unfalsifiable of 16, every
error overestimating pathology and cost by about an order of magnitude.
Neither predicted the actual failure shape, the session-boundary handoff: a
successor reads a missing receipt as a dead run and relaunches work in
flight (sessions 11 to 14), and session 6 lost session 1's workaround for
the OEIS search block, re-derived "search is blocked" from a bare request,
and recorded a DEAD line that reached the final synthesis. The report
counted three instances, the disposition two days later four; four is the
record.

**What it produced, after the novelty triage of 2026-08-17.** Novel: an
algebraic bivariate generating function for king animals by box and
semiperimeter, derived from its functional equation with no fitting in the
final chain; the Temperley q-series closed form, with μ the root of an
explicit q-series to 44 certified digits and interval-certified amplitudes;
four new sequences; three OEIS-comment-grade identifications (A014300,
A112029, A153337). Narrow: area-moment generating-function algebraicity for
every order r; the king-equals-polyomino universality statement. A lead:
non-D-finiteness through the zeros of K(q) accumulating at q = 1 under a
Gieseking-constant oscillation, two gaps named. Superseded: the third
layer's limit law and c_r = (r!)²/2^(r+7), the moment sequence of U(1−U)/2,
in Richard, arXiv:0704.0716, for convex polygons; sessions 9 to 14, the
three most expensive among them, largely re-derived it. The salvage of
2026-08-17 (`a4c8085`) imported the two novel layers into the
convex-polyplets record (`results/subclasses.md`, planned) and found half of
the first already in the repository (the s ≤ 200 series and degree-2
algebraicity, 2026-08-05). The sequences and comments are staged, not
submitted.

**The defect that matters.** "0 unwitting re-derivations" was scoped to the
21 sealed files. Against the literature the loop re-derived a published
limit law at about a third of its budget, and against the repository it
re-derived recorded work; both were invisible to the loop (no library) and to
grading (the rubric never asks). A sealed sandbox cannot check priority and a
hygiene rubric cannot detect what it does not query, so cost per new result
is unmeasurable and the step path measures conformance to a withheld route,
not research value. A post-action review (`b468ee2`) found 4 of 10
substantive DEAD lines defective (two false, one a mislabeled lead, one an
unmeasured cost) against 0 false among 64 graded claims; a false DEAD line
removes a capability from every later session, and the rubric cannot see one.

**What closed it.** One question answered against both predictions: the
loop's output is not mostly junk needing triage. Nothing else settled. The
disposition set four conditions for a second run (a literature-priority pass
in grading, a responsive steering arm, per-curve token instrumentation, a
handoff fix with DEAD lines in the graded grammar) and said the step path
should not survive. Decided 2026-08-17: no second run and no further
unattended-loop machinery; adversarial desk panels and the interactive
baseline earned their cost, the loop did not; the literature-priority pass
became standing practice on any result called new. Grading cost about 95
minutes wall, of which three verification agents ran about 26 minutes in
parallel on dalby copies; steering 0 minutes. The run record, grading tree,
divergences, contamination log and value triage were deleted 2026-09-06
(`git show e5e7870:results/ghostship/<path>` and
`git show e5e7870:docs/ghostship-preregistration.md`).

### 9.4 Skeleton Key: four mechanisms without a height enumeration, 2026-08-20

**Set out to do.** On the branch `skeletonkey`, at jasonp's instruction:
set height aside and find a counting mechanism that uses some other property
of animals and of the lattice. Four candidates were generated, priced and
closed the same day; two small probes ran on ayr and no compute job was
needed. The derivations and tables are in `results/closed-doors.md`
(planned).

**What it found.** Each candidate, and what closed it:

- **The determinant handle.** det(L_S + εI) for the induced king-subgraph
  Laplacian vanishes to order exactly the component count, so connectivity
  becomes an order of vanishing, which composes under gluing. Closed: the ε¹
  coefficient is weighted by the spanning-tree count, which no commutative
  edge weighting divides out (a single edge forces weight 1, a triangle then
  gives 3; characteristic 3 kills it, characteristic 2 kills the 2×2 block).
  A determinant counts every spanning tree, and connectivity needs one
  representative per set, a canonical-order choice, not a linear operation.
- **Blocking and inflation.** The 2×2 block map preserves
  king-connectivity exactly and a block is a king-clique, so the fine set is
  connected exactly when the contact graph on blocks is; inflation works
  with 15 fillings and not every choice stays connected. Closed: the
  correspondence is a bijection with a(n) on its own right-hand side, the
  relaxed inequality is satisfied by every positive value, and the clique
  gift holds at one level only.
- **The 2-adic filtration.** The characteristic-2 rank is the first layer of
  the elementary-divisor spectrum, and a(60) needs about 168 bits. Closed on
  the tree's own numbers: the collapse is at column granularity, the
  cell-level rank is Θ(H·2^H), and the ceiling is 6× in state count, about
  2× best case, under one height against a 2.9× per-height cost.
- **The relaxation hierarchy.** Restricted cut families do not
  interpolate; bounding runs per column is a genuine polynomial-state
  hierarchy, closed by capture: column-convex king animals (1, 4, 18, 83,
  385, ratios near 4.6 against λ = 7.12) grow at a strictly smaller rate, so
  each level's share of the class decays geometrically, about eleven orders
  of magnitude at n = 60 for one run per column.

The height decomposition tried first that day, enumerate the bulk exactly
and estimate the tail, was closed by measurement
(`experiments/skeletonkey/height_tail_extrapolation.py` on the recorded
`results/ns_a40/perheight/` rows, seconds on ayr, with a control requiring
that a perturbed row move the quantile): mean height grows as 1.228·n^0.682,
so at n = 60 the enumeration ceiling sits at the median height and the
closed-form floor above the 0.9 quantile, with no small remainder to
estimate; the collapse predicts quantiles to within one height and tail
shares only to a factor of 2 to 4; and covering all but a vanishing part of
the class costs about 3^(2n^0.68) against about 3^(n/2) for everything,
crossing near n = 76. Bulk plus tail is never cheaper than everything at any
n that could be run. `results/fixed_height_gfs.txt` gives no free bulk: it
stops at H = 11 with recurrence orders growing 2.65 per height.

**The four causes**, which also account for every closure already in the
tree: locality (no local grading separates connected from disconnected; the
Euler characteristic C − h never separates its terms); capture (a subclass
bounded by a local complexity measure has a strictly smaller growth
constant); bijection (a re-encoding pays the same floor); exponent against
constant (every cleverer geometry has a better exponent and a worse constant
and loses in every runnable range). A breakthrough must be non-local, capture
a constant share of the class, not be a re-encoding, and improve the
constant. Cause 2 excludes any nameable deterministic decomposition; it does
not apply to a sampler. The combinations were tried and closed, and the
Sykes–Essam matching pair stays closed on its accounting (king n = 40 needs
square-lattice data graded to about order 200 in the percolation variable;
the published totals reach 70 and are not graded). The one number left
standing is the cut-compression gap: the Hankel floor is
Motzkin(H/2+1) = 15,511 independent quantities at H = 21 where the engine
carries about 4×10⁸ states, and closing it would move the base from about
1.66 to about 1.32 per unit of n; the obstruction is that the compression
exists at column granularity while an algorithm reads one cell at a time,
where the rank is Θ(H·2^H) rather than 2^H. The same day found the strip
automaton is not state-minimal, since frontiers with the same multiset of
block reaches can be added (6.71× at H = 8; 9.04× measured at H = 21 on
2026-08-23), and jasonp parked it: established, nothing built.

**What closed it.** All four were settled by counting; none was expensive
enough to justify a compute job, which is the point of the day.

### 9.5 Offside and the process proposal, 2026-08, closed 2026-09-06

Two rounds designed a replacement for the ad-hoc session state: Offside (six
lanes and a queue) and the process proposal. The candidate was recorded
2026-08-14 and never adopted; `HANDOFF.md` remained the live state and
worked. Records deleted 2026-09-06: `results/offside/`, `docs/offside-*.md`,
`docs/process-proposal.md`, `docs/state-minimal.md`
(`git show e5e7870:<path>`).

### 9.6 Last ditch, 2026-08-20

The one campaign here that delivered: a(41), and a(n) independent of the
connectivity rule for every n ≤ 39. Its record stays in
`docs/lastditch-campaign.md`, with its closed doors and their
counterexamples.

## Open problems

- jasonp's sections are unwritten: what the project was for and whether it
  delivered that; what he would do differently on the human side; whether
  the self-certification bar worked; the cost and benefit of the
  hardware-months and of the collaboration; anything the account above gets
  wrong or misses.
- Rook parity left recorded and unpursued: whether the per-height
  processor-time ratio crosses 3 (the only question that can still move the
  base); the corrected gate-0 measurement, the e ≤ 3 family dynamic program's
  growth over K = 19..25, minutes-scale, unrun; the production engine's own
  n = 24..30 cost curve, about 2 hours on dalby, to run only beside a
  challenger.
- Ghost Ship's bulletin and token-shape questions are untested and lost
  respectively; no second run is planned.
- Skeleton Key's cut-compression gap is real and non-constructive; the
  frontier merge by block reach is measured and parked; a sampler is the one
  direction cause 2 does not exclude.

## Reproduce

- Skeleton Key's height quantiles and crossover:
  `python3 experiments/skeletonkey/height_tail_extrapolation.py` on
  `results/ns_a40/perheight/` (seconds; the control perturbs a row and must
  move the quantile).
- The Ghost Ship launcher is `scripts/ghostship/run_session.sh` (cron
  `0 4,12,20 * * *` on dalby); sandbox, protocol and grading tree are history
  only.
- The triangle campaign's Lean encoding layer builds with `polyplets/`
  (`docs/lean-environment.md`); its original gate battery and harness under
  `experiments/tristruct/` go with the triangle records.
- The rook-parity figures are quotients of the a(40) phase timings in
  `results/ns_a40/PROVENANCE.md`; the round's receipts gate is retired.

## Sources

- `docs/lessons-learned.md` (the previous version of this file, 2026-07-15
  with additions to 2026-09-06; rewritten in place)
- `docs/project-postmortem.md` (deleted 2026-09-06; its content is above)
- `docs/triangle-postmortem.md` (deleted 2026-09-06; its content is above)
- `docs/rook-parity.md` (deleted 2026-09-06; its content is above)
- `results/ghostship/REPORT.md` (deleted 2026-09-06; its content is above)
- `results/ghostship/DISPOSITION.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-four-mechanisms.md` (deleted 2026-09-06; its campaign
  summary is above, its mathematics in `results/closed-doors.md`, planned)
