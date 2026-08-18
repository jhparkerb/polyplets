> **Standing standard.** Every team brief that asks agents to generate ideas
> about a(40) cites this file and scores its output by it. It is not a round
> plan and it does not expire with a round.

# The skeptical-reader standard

An idea is worth the round only if it moves a skeptical reader's belief in
a(40). This file defines that reader, defines the currency their belief is
measured in, and fixes the disclosure every idea has to carry so the reader can
check the claim instead of trusting it.

The standard exists because two rounds produced work that was correct, novel,
and worth **zero** on the mission. Round 1 of the triangle hunt banked a proved
theorem that contains no row-40 cell. The strip transfer matrix confirms 469
cells with 0 mismatch and does not qualify as verification. Both are good
results. Neither moves the reader. Nothing here is about rigor — it is about
where the rigor is aimed.

## The reader

Assume a referee who wants the count to be wrong and is competent enough to
find out.

**What they grant.** That the arithmetic is exact, that the code runs, that the
authors are honest, that the machines did what the logs say. Attacks on those
are not what this project is exposed to, and defences of them buy nothing.

**What they refuse to grant.**

1. **The connectivity rule.** Both production engines decide king-connectivity
   by union-find over a frontier against the previous column's component
   labels. A shared misconception about what is being counted passes through
   both and shows up as agreement. Different code, different author, different
   language, different machine, different ISA, different modulus — none of
   these is an answer to this objection. This is the project's ruling, in
   `git show 2b3115b:docs/second-source-team-brief.md`, and it is the axis the
   reader will press.
2. **Agreement between things that share an input.** Two computations that
   consume the same banked cells corroborate the transcription, not the count.
3. **A relation fitted where it is checked.** A form with free parameters that
   reproduces the cells it was fitted on has been tested zero times.
4. **A claim about a cell whose provenance was assumed.** The reader will ask
   whether the cell was ever enumerated. If it was produced by a wired closed
   form, a check on it says nothing about the sweep.

**What they cannot do.** Re-run the enumeration. Row 40's H21 phase alone cost
36.4 h on 32 cores with a 363 GB disk peak; Redelmeier stops at n = 22 and
cannot be pushed (~10¹³ years of fleet time at n = 40). The reader has a laptop
and an afternoon. Any check they cannot execute is a claim, not a check.

## The exposure map

Cell counts, not shares. A term is wrong if any one of its cells is wrong, so
weighting a cell by its size states nothing about how far the term can be
trusted; the share column this table used to carry was removed 2026-08-18.

Measured from the banked triangle at the time of writing
(`experiments/tristruct/triangle.py`, row 40 by provenance class):

| band | cells in row 40 | provenance |
|---|---|---|
| H ≤ 14 | 14 | real sweep; also strip-TM confirmed, 0 mismatch |
| H = 15…21 | 7 | real sweep; **single production sweep, no second computation** |
| H = 15…19 | 5 | the unconfirmed block inside that band |
| H ≥ 22 | 19 | wired P_k closed forms, never enumerated |
| H ≤ 2 | 2 | engine's analytic low-strip rows, never swept |

Read the second row as the mission. An idea that touches only H ≥ 22 is
checking a formula chain the reader is not worried about. An idea that touches
only H ≤ 14 is re-confirming the confirmed. **State, in the first line of the
claim, which cells the idea reaches and by which provenance class**, and
quote `triangle.provenance(n,H)` for each cell rather than inferring it. The
rule of thumb: H ≥ 22 is wired P_k at every n, H = 3…21 is real sweep, H ≤ 2 is
the low strip.

## The currency: two bit-counts, first line, never one

Define **bits** as log₂ of the a-priori probability that a wrong count passes
the check. A congruence mod m gives log₂(m) bits against whatever produced the
number it tests. Report two, always, and label them:

    bits against enumeration error   — over cells that were actually swept
    bits against formula-chain error — conditional, and say conditional on what

If the cells in question were never enumerated, the first number is **0**. Write
the 0 in the first line, not in a caveat at the end. A claim carrying 40
conditional bits and 0 enumeration bits is a claim about a formula, and the
reader will say so before the second paragraph.

Two further rules on the arithmetic, both earned:

- **Correlated evidence does not sum.** Four claims that evaluate the same one
  or two polynomials at nearby points are one claim's worth of bits, not four.
  Before adding bits across claims, name the underlying quantity each touches
  and show they differ.
- **Match the calibration instrument to the hypothesis class.** Perturbing a
  cell to see whether a congruence still holds is vacuous — it fails by
  construction and "0 false passes" measures nothing. Congruences are
  calibrated against the empirical base rate over the region; fitted forms are
  calibrated by perturbation. Do not copy the previous report's method.

## The four independence axes

Every idea reports all four, in these words, with a one-line answer each. "Not
applicable" is an answer only with a reason.

1. **Rule independence.** Does it decide connectivity the way the engines do?
   If it is a frontier DP carrying component labels, say so plainly — that is a
   consistency check and is ranked as one. Name the failure mode the idea would
   exhibit if it were wrong, and argue that failure mode is disjoint from
   union-find-over-a-frontier's.
2. **Derivation independence.** Did the derivation read banked data, or only
   the lattice definition and cells the author enumerated themselves? Every
   banked cell a blind derivation matches afterwards is a real test; every cell
   read during derivation is not.
3. **Input footprint.** How many banked cells does it consume and what is the
   largest n among them? A relation that consumes row 39 to predict row 40
   catches faults local to row 40 and nothing else.
4. **Checker cost.** Can the reader verify it in an afternoon on a laptop, from
   the banked file and the checker alone?

## The checker requirement

The deliverable that actually moves the reader is a **short independent
checker**: exact integer or modular arithmetic, readable in one sitting, run
against the banked file in minutes, with a RED control that fails when the data
is corrupted. That is warrant tier 3 in `docs/provenance-tables.md`, and it is
the highest tier reachable without a proof. Ideas are ranked in part by whether
they end in one.

**Sensitivity is part of the checker, not a nicety.** A check that passes means
nothing until a corrupted input has been shown to break it. Ship the corruption
battery and its false-pass rate with the result.

## Mandatory disclosure block

Every candidate, in every deliverable, opens with this block filled in. A
candidate without it is not scored.

    claim:
    cells reached:                     ____  (bands: ____; provenance: ____)
    bits against enumeration error:    __
    bits against formula-chain error:  __   conditional on: ____
    rule independence:                 ____
    derivation independence:           ____
    input footprint:                   __ cells, max n = __
    checker:                           path, runtime, RED control
    sensitivity:                       corruption battery, false-pass rate
    prior-work grep:                   commands run, including cross-branch

## Automatic zero

Each of these has cost a real round. Any one of them zeroes the candidate.

- **Novelty claimed without the cross-branch grep.** A working-tree grep is not
  a novelty check; results cited by briefs have lived on other branches.
  Minimum:
  `git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'`
  then `git show <commit>:<path>` on the hits. Show the commands.
  **The `docs/*.md` term is not redundant** — measured 2026-08-12 by the round-3
  harness: `docs/**/*.md` alone matches 251 historical paths and misses 30 files
  at the top level of `docs/`, including `docs/second-source-team-brief.md`
  (2b3115b), the ruling this standard cites. With both terms: 510.
- **Fitted on every available cell.** Fit on a proper subset, hold out by n,
  report both regions.
- **A consistency check presented as verification.** Strip-TM-class
  recomputation, mod-p/CRT arithmetic, in-flight redundancy, and any
  recomputation sharing the frontier connectivity rule are consistency checks.
  They are worth reporting under that name and worth zero under this one.
- **One bit-count.** See above.
- **Provenance assumed.** Quote the loader.
- **"The pattern holds on more cells."** More agreeing cells from the same
  source is not a check; it is the same measurement, read again.

## Ranking

Rank by, in order:

1. bits against enumeration error, over the cells reached;
2. proof-backed over fitted, at equal bits;
3. checker cost to the reader, cheapest first.

Reach is not a ranking criterion. A method that re-verifies already-confirmed
cells by a route that clears the rule-independence bar outranks one that
extends a shared-rule method into new cells.

## What a brief inherits

Paste into any team brief that generates ideas about a(40):

> Scoring is `docs/skeptical-reader-standard.md`. Read it before proposing.
> Every candidate opens with its disclosure block; candidates without one are
> not scored, and the automatic-zero list applies in full.
