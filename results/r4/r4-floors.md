# r4-floors — adversarial audit of the three floors

Standing question: is each floor a theorem, and does it say what it is used to
say? Verdicts and the failing step, per floor. Filed incrementally.

## Floor 2 (information, L3-1) — VERDICT: THEOREM (narrow) but OVER-APPLIED

### What is stated

`results/triangle-r3-synthesis.md:201`:

> **Information floor** (L3-1). Any straight-cut method in any vocabulary must
> transmit at least Motzkin(H/2+1) quantities across the cut — the banked SVD
> ranks *are* Motzkin numbers.

and `:215-222`, "The cut is an information floor … That single fact explains why
three lanes hit the same wall and **prunes the remaining search space to no-cut
methods and cancellation**."

### Finding 2A — the floor's own number is ~2.6e4 times BELOW the incumbent's
### cost, so it excludes nothing in the affordable region

Desk arithmetic on Motzkin numbers (verified this session):

| quantity | H=21 value |
|---|---|
| L3-1 floor, M(H/2+1) = M(11)..M(12) | 5,798 .. 15,511 |
| incumbent column states, M(22)−1 | 400,763,222 |
| ratio | **25,837x** |

A cut method that transmitted 15,511 quantities per cut at H=21 would be an
enormous win, not a wall. **L3-1 therefore cannot, on its own, close any cut
method.** The gap between the floor and the incumbent's cost is exactly the room
a better cut vocabulary would live in, and the floor says nothing about it.

This is not a hypothetical gap. `results/triangle-r3-involution.md:320-330`
already exhibits an object inside it: the char-2 compressed dimension at H=21 is
~0.9–1.3e6, which the involution lane itself scores as "~10² above [the L3-1
floor], no violation" and ~10³ below B1's state space. A cut-crossing
representation 400x smaller than the incumbent, fully compliant with the
information floor, is on disk in this repo. The synthesis's pruning claim
("prunes the remaining search space to no-cut methods and cancellation") does not
follow from L3-1 and is contradicted by a sibling lane's own number.

### Finding 2B — the measured object is not the object the floor names

The banked ranks come from `results/boundary-push-tensornetwork.md`: "We MEASURED
the rank by dumping the real frontier count-vector and taking the SVD across the
balanced central cut" — i.e. the **Schmidt rank of one frontier count-vector**,
at one sweep position and one n, reshaped across a cut of the H *frontier sites*.
That is exactly the minimal bond dimension for an MPS factorization of that
vector: a genuine theorem, about MPS compression of the incumbent's own frontier.

It is not the rank of the counting problem's left-cells x right-cells matrix
across a spatial cut of the lattice. The bipartition differs (top half of a
frontier vs left half of a lattice), the object differs (a data vector at fixed
n vs the bilinear form of the whole count), and the quantifier "any method in any
vocabulary" is licensed only for the latter. As stated, L3-1 is a bound on
methods that (i) sweep in the incumbent's direction, (ii) form the incumbent's
frontier count-vector, and (iii) factorize it linearly along the frontier. It is
silent on methods that never form that vector — which is the whole no-cut class
it is being used to *define the complement of*.

### Finding 2C — the Motzkin identification is 3 confirming points and one
### unresolved miss, but it is not numerology

M(H/2+1) is a structural **upper** bound on that rank: the rank cannot exceed the
number of distinct half-frontier signatures, and a height-H/2 half-frontier has
M(H/2+1)−1 nonempty states plus empty, by the banked theorem
(`git show second-source:results/king-column-motzkin.md`, Lemmas 1–2, proved and
machine-verified three ways). So the identification has a reason, and the
load-bearing content of the *floor* direction is the measured **attainment** of
that upper bound (linear independence of the half-states) at H=8/10/12 only.
H=14 measured 298 against M(8)=323. `results/triangle-r3-l3-contour.md:250-252`
concedes: "I did not re-dump at a peak column to confirm it closes to 323."
Attainment is MEASURED-PATTERN at three points, NOT ESTABLISHED in general and
NOT ESTABLISHED at the one H where it was tested and missed.

## Floor 1 (state, L1-6) — VERDICT: OVER-APPLIED, and FALSE as literally stated

### What is stated

`results/triangle-r3-synthesis.md:198`:

> **State floor** (L1-6). Any frontier vocabulary pays at least the cell
> frontier's state count; coarser objects do not help, because piece identity
> refines rather than abstracts.

Queue row L1-6 (`results/triangle-r3-queue.md:60`) goes further: "any strip-cut
vocabulary pays >= Motzkin; the search space for a smaller state space is exactly
the no-cut / implicit methods".

### Finding 1A — refuted by a sibling lane's measurement, same round

"Any frontier vocabulary" cannot mean *any*, because linear realizations of the
same column functional are measured, in this repo, at strictly fewer dimensions
than the cell frontier's state count. `results/triangle-r3-involution.md:284-300`,
observability closure = exact Hankel rank:

| H | cell states M(H+1)−1 | rank GF(2) | A-S1 rank mod p=2^31−1 |
|---|---|---|---|
| 7 | 322 | 58 | 88 |
| 8 | 834 | 112 | 204 |
| 9 | 2187 | 229 | 501 |

Both columns are below the cell frontier at every measured H, and the char-2
column diverges downward (0.44·2^H against Motzkin's ~3^H): ~1e6 against
4.0e8 at H=21, a factor ~400. The involution lane states the governing principle
itself (`:277-281`): "The minimal dimension of ANY field-linear realization of
the strip functional — partition basis, coincidence basis, spin basis, anything —
is the Hankel rank of the functional itself."

So the honest scope of floor 1 is **combinatorial vocabularies whose states are
objects placed on the frontier**, not "any frontier vocabulary". Linear /
weighted-automaton realizations are exactly a frontier vocabulary and they pay
less. The standing caveat that rescues the *practical* conclusion is a different
one, and it is the one that should be quoted instead: the low-rank basis is an
existence statement with no explicit basis (`triangle-r3-synthesis.md:225-228`,
"a rank is an existence statement and the explicit basis — which CKN have for
matchings — does not exist here").

### Finding 1B — even restricted to combinatorial vocabularies, it is one
### instance generalized

What L1 measured (`results/triangle-r3-l1-corner-gluing.md:73-102`) is one
coarsening: rook-piece corner-gluing assembly, cell vs piece closure at H=2..9,
piece/cell rising 1.00 -> 2.72. Validated (banked T(n,H) reproduced H<=6, RED
control), and the cell column independently reproduces M(H+1)−1. The measurement
is sound and I am not disputing it.

The *reason* given (`:103-106`) is also specific to that coarsening: "the rook
partition refines the king partition … piece identity is extra information on top
of the king labels". That argues about rook pieces. It is not an argument about
an arbitrary quotient of the frontier alphabet.

What a helping coarsening would have to be: a partition of the reachable state
set that is a **congruence** for the column transfer map and for the final
readout — i.e. merging two states that are Nerode-indistinguishable. The general
claim is therefore equivalent to: *the M(H+1)−1 reachable states are pairwise
Nerode-distinguishable*, so the incumbent's automaton is state-minimal. That
would be a theorem covering every deterministic column-sweep vocabulary at once,
and it is the right form of floor 1.

**Nobody has proved it, and nobody appears to have asked.** Grep for
`Nerode|distinguishab|minimal automaton|state-minimal` over `results/` and
`docs/` returns no hit in a state-count context. NOT ESTABLISHED. This is the
cheapest missing brick in the whole floor structure: pairwise distinguishability
at small H is a desk computation on the existing closure code, and a proof at
general H likely follows the same rails-and-spurs witness that
`king-column-motzkin.md` Lemma 2 already builds.

## Floor 3 (term-source, L4-12) — VERDICT: conclusion sound, STATEMENT wrong;
## the name points at the non-binding clause

### What is stated

`results/triangle-r3-synthesis.md:204`:

> **Term-source floor** (L4-12). Any fixed-H recurrence route needs ~2r
> rule-independent terms of order r, and terms on this lattice cost c^n from any
> rule-independent source — they exist rule-independently only to n = 18.

The derivation (`results/triangle-r3-l4-quotient.md:436-470`) names two inputs:
(i) minimal order not tiny, (ii) rule-independent terms cost c^n.

### Finding 3A — clause (ii) is false as stated, and known false in this round

`results/r4/queue.md:80` (R4-G11) reports an oracle giving **640
rule-independent values to n = 40 at H <= 16**. That falsifies "they exist
rule-independently only to n = 18" outright. r4-gen reached the right residue
already — "the term-source floor's binding clause is the ORDER, not the term
source" — and I confirm it independently. The floor should be renamed the
**order floor**; the c^n term cost is a contingent fact about today's sources and
it has already moved once in one round.

### Finding 3B — the audit of "any rule-independent source"

The justification given for (ii) is enumeration cost only ("the only
rule-independent term source is quotient DFS at ~lambda^(n/2)"). Non-enumerative
sources are not addressed:

- **another exact engine / a differently-ruled DP** — this is precisely the
  oracle of 3A, and it broke the clause.
- **a closed form or identity at fixed H** — would supply unlimited terms, but
  makes the recurrence redundant, so it cannot rescue the route. Self-defeating,
  not excluded by the floor.
- **a symmetry or transport from another lattice** — no bijection is known;
  NOT ESTABLISHED either way. The floor asserts rather than excludes here.

So the "any" is ASSERTED, and one of its cases has already been refuted.

### Finding 3C — clause (i) is well supported, but not by the number R4-G11 quotes

R4-G11 kills the reopening with "minimal order at H=15/16 is >= 2122/6045
(hmirror quotient, L4-11)". **That inverts the direction.** L4-11 is explicit
(`triangle-r3-l4-quotient.md:432-434`): "the table's numbers are exact
**ceilings** on the minimal order r, and the measured floor is r > 12". A
realization of dimension d bounds the minimal order *above*. Using 2122 as a
lower bound is a ceiling read as a floor, and if taken at face value the door is
shut with the wrong hand: 640 terms to n=40 would pin any order r <~ 20, and the
only *measured* lower bound is r > 12.

The correct support is on disk and is strong: measured exact minimal column
recurrence orders are **7 at H=3, 42 at H=5 (onset n=43), 106 at H=6 (onset
n=107)** (`results/triangle-hunt-slices.md:57-64`,
`results/triangle-hunt-synthesis.md:166-171`). Order already exceeds the
available-term budget at H=5, and the onsets alone exceed n=40. At H=15/16 the
order is not measured — NOT ESTABLISHED inside (12, 2122] — but the measured
series 7/42/106 makes r <= 20 implausible by a wide margin. Fixing the citation
costs one sentence and turns a wrong-direction argument into a right one.

## Composite — independence and coverage

### Independence: 2 of 3, not 3 of 3

Floor 3 is genuinely independent of the other two (recurrence fitting, not cuts).

Floors 1 and 2 are **not independent, and the synthesis's own lane says so**:
`results/triangle-r3-l3-contour.md:259-260` describes L3-1 as "sharpening L1-6's
state-count version" — the same statement about the same object (the straight
column cut), one in states and one in rank. They do not close different escapes;
they close the same escape ("find a better boundary vocabulary") for two
different method classes, and the rank version is 25,837x numerically weaker at
H=21. Calling them "three separate lower bounds, each closing a different escape"
(`triangle-r3-synthesis.md:195-196`) is not supported.

### Coverage: the pruning claim does not follow

"That single fact … prunes the remaining search space to no-cut methods and
cancellation" (`triangle-r3-synthesis.md:221-222`). The three floors do not
exclude the complement:

1. **Linear realizations of the cut functional below the state count.** A cut
   method, so not in "no-cut"; not cancellation in the B1 sense. Floor 1 excludes
   it only in its false-as-stated form; floor 2's bound is ~1e4 at H=21 while the
   measured char-2 rank is ~1e6 and the incumbent is 4e8. What actually keeps this
   route parked is the absence of an explicit basis — a knowledge gap, not a
   floor. The synthesis states that correctly at `:223-228` and then omits it from
   the pruning sentence.
2. **Verification protocols rather than counting methods.** None of the three
   floors constrain a bounded-soundness-error certificate: they bound the cost of
   *producing* the count, not of *checking* it. Already open as `results/r4/queue.md:85`
   (R4-G16, sumcheck/GKR, correctly scoped there) — so the class is not in fact
   being treated as closed, but it is outside the pruning sentence's dichotomy.
3. **Non-straight cuts.** Floor 2 is explicitly straight-cut only, and the banked
   theorem's scope guard (`git show second-source:results/king-column-motzkin.md`,
   "Scope guard") says the Motzkin identity fails on a jagged cell-at-a-time cut,
   where crossings genuinely occur. Direction of the failure favours the campaign
   — jagged cuts have *more* states, so a staircase is worse, not better — but the
   floor does not cover them and must not be cited as if it did.

## Summary table

| floor | verdict | the step that fails |
|---|---|---|
| 1, state (L1-6) | **OVER-APPLIED; false as literally stated** | "any frontier vocabulary" — linear realizations measured strictly below it (GF(2) rank 229 vs 2187 states at H=9). Restricted to combinatorial vocabularies it is one instance (rook pieces) generalized; the general form needs Nerode-distinguishability of the M(H+1)−1 states, NOT ESTABLISHED and never asked |
| 2, information (L3-1) | **THEOREM, narrow; OVER-APPLIED** | the measured object is the Schmidt rank of the incumbent's frontier count-vector, not the lattice cut matrix, so "any method in any vocabulary" is unlicensed; and the bound is 25,837x below the incumbent at H=21, so it excludes nothing affordable. Motzkin attainment measured at 3 points, missed at H=14, never re-measured |
| 3, term-source (L4-12) | **conclusion sound; STATEMENT wrong** | clause (ii) ("rule-independent only to n=18") falsified by the 640-value oracle; the binding clause is order, and R4-G11's supporting number reads L4-11's ceiling as a floor |

## Routes the floors do not close that have been treated as closed

- **L3-3** (fattening bijection to decorated polyominoes) and **L3-4** (dual/moat
  encoding) are both downgraded in `results/triangle-r3-queue.md:75-76` with "still
  pays L3-1's rank floor at any cut" / "pruned by L3-1 (still a cut method, same
  rank)". Paying a floor of ~1.5e4 at H=21 is not a cost objection to anything.
  Neither row is closed by floor 2; they are closed, if at all, by the separate
  argument that their *actual* state count is the incumbent's — which is argued for
  (B) in `triangle-r3-l3-contour.md:154-160` and merely asserted for L3-3/L3-4.
- **R4-G18** (orthogonal halving, `results/r4/queue.md:87`) is killed by "pays the
  identical Motzkin floor (L3-1)". Same defect: equal floors do not imply equal
  costs. Its premise was separately corrected by R4-G5-20; the surviving argument
  should be about interface state counts, not about the floor.
- **The char-2 cut representation** is excluded from the pruning sentence by a
  floor that does not reach it. It is not formally closed anywhere; the real
  blocker is the missing explicit basis.

## What to do about it, cheapest first

1. **Nerode-distinguishability of the M(H+1)−1 column states** — desk computation
   on the existing L1 closure code at H<=8, and a likely proof by the
   rails-and-spurs witness. Turns floor 1 from one measured instance into a
   theorem about every deterministic column-sweep vocabulary. This is the single
   highest-value missing brick and it costs a session.
2. **Re-dump the H=14 frontier at a peak column** and confirm rank 298 -> 323.
   Minutes on ayr/dalby. Either the Motzkin attainment pattern holds at four
   points or the identification is wrong, and right now the one adverse point is
   explained but unresolved.
3. **Restate the three floors** with their true scopes: floor 1 for combinatorial
   vocabularies only, floor 2 as a statement about MPS factorization of the
   incumbent frontier with its numeric value quoted alongside (1.5e4 at H=21, not
   a wall), floor 3 renamed the order floor with the 7/42/106 order series as its
   support.

## NOT ESTABLISHED in this audit

- Whether the H=8/10/12 frontier dumps were themselves taken at peak columns
  (only H=14 is flagged off-peak in `boundary-push-tensornetwork.md`); if any was
  off-peak the attainment evidence is weaker still. I did not check
  `experiments/frontier_svd/`'s run parameters.
- The true minimal recurrence orders at H=15..21, anywhere in (12, ceiling].
- Whether an explicit char-2 basis exists on this lattice. Unchanged from round 3.
- I ran no compute; every number above is quoted from a cited file or is desk
  arithmetic on Motzkin numbers reproduced this session.
