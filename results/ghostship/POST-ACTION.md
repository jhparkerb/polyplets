# Ghost Ship — post-action review

2026-08-17. Two items closed: an audit of the run's DEAD lines (the field
grading never looked at), and a score of the pre-launch review panel (the
last unscored forecasting artifact). Companion to `REPORT.md` (hygiene),
`VALUE-TRIAGE.md` (worth) and `DISPOSITION.md` (decisions).

---

# Part 1 — DEAD-line audit

`VALUE-TRIAGE.md` §F found one false DEAD line by accident. This is the
sweep it implied.

## Why the field matters

R3 invented the DEAD grammar (`R3-mechanics.md` edit #5) and the sessions
used it as designed. Nobody put it in the rubric. So a DEAD line is
ungraded, unverified, and *inherited*: it is the one report field whose
whole purpose is to stop successors doing something. A false CARRY claim
misinforms; a false DEAD line removes a capability from every session after
it, silently, and reaches the capstone as settled fact.

## The population

Thirteen DEAD-field entries across fourteen sessions (s11 and s14 have
none; s05/s08/s10/s13 write "none" plus a successor NOTE). Ten assert a
substantive negative. Verdicts:

| session | DEAD content | verdict |
|---|---|---|
| s01 | area-statistic P-recurrence dead; convex-mirage negative stands | SOUND — matches the repo's banked position |
| s01 | only sqrt(1−4t) occurs; disc = 4t⁶(1−4t)⁵(1+2t)⁴ | **SOUND, tested** — see below |
| s02 | Ehrhart reciprocity probe "inconclusive, low priority" | **MISLABELLED** — an open lead filed in the do-not-retry field |
| s03 | bivariate exact run at box (160,242) is "~4h+ in pure Python" | **UNMEASURED** — a cost estimate closing a route; never run to completion |
| s04 | q-kernel-root substitution at q ≠ 1 | SOUND — mechanism given (no power-series root) |
| s06 | "OEIS SEARCH is Cloudflare-blocked for curl — use b-file URLs" | **FALSE** |
| s07 | "/search AND entry pages Cloudflare-blocked (b-files still work)" | **FALSE** — propagation of s06 |
| s07 | naive integer-pole-only extraction of Var(w\|s) gives 7/12, 1/4 — wrong | SOUND — self-caught, mechanism given |
| s09 | P+Q√Δ ansatz for M00-phase values; they are rational | SOUND — stated as a closed-subsystem fact |
| s12 | pattern-matching B_r factors by fixed atom shapes | SOUND — refuted by probe, and REPORT credits the refutation |

**Four of ten defective.** Against 64 graded CARRY claims with 0 FALSE.
The errors are concentrated in the field nobody graded.

## The one worth testing, tested

s01's second DEAD line is the load-bearing negative under the run's best
result: it asserts the algebraic GF carries no radical but √(1−4t). Tested
by independently re-implementing the CARRY closed form here — exact
`Fraction` power series, series for √(1−4t) built from Catalan numbers, no
sympy, no reuse of the loop's code:

    F(t) = [t²(2−10t+14t²−5t³−4t⁴) − t³(1+2t)²√(1−4t)] / ((2+t)(1−4t)²)

reproduces **all 200 terms** of `king_semiperim_200.txt` exactly, first
coefficients 1, 2, 9, 36, 154, 668, 2916, 12740. No second radicand is
needed and none appears. DEAD line sound; and the run's single most
valuable claim now has a third independent confirmation.

## The two false ones, and the actual mechanism

`VALUE-TRIAGE.md` §F has the sequence: s01 hit the Cloudflare challenge on
a bare `curl`, fixed it in the same session with a browser User-Agent, and
the loop searched normally through s05. s06 ran bare `curl`, re-derived
"blocked", banked it; s07 repeated it and widened it to entry pages;
`FINAL-SYNTHESIS.md` carries it under "Dead ends (do not retry)".

Mechanism, measured today: from gympie a bare `curl` to both
`https://oeis.org/A005436` and `/search?q=...&fmt=json` returns 200 with no
challenge page. The loop ran on dalby, a Hetzner datacenter address, which
Cloudflare challenges by default. So the claim was never a property of
OEIS, was locally reproducible on the run's host, and had a working
in-record workaround five sessions old. (Not re-tested on dalby itself —
no agent forwarded here.)

s07's widening is the part to notice: it extended a false claim to entry
pages, which s03 and s05 had themselves queried successfully via
`search?q=id:Axxxxxx`. The loop refuted s07 twice before s07 wrote it.

## The two soft ones

s02 files "inconclusive, low priority" under DEAD. That is not a negative
result; it is an open lead in the field that means do-not-retry. The
grammar has no slot for "unresolved", so unresolved things land in the
nearest bin.

s03 closes a route on an unmeasured cost estimate ("~4h+ in pure Python").
No capability was lost — the session reached the same box another way in
~4 min — but a resource guess that closes a route is the same failure shape
as s06, with arithmetic instead of a network in the middle.

## What this changes

- The §F finding is not an anecdote. Two false DEAD lines from one root,
  plus two soft ones, in a field with no grading and no verification.
- **The rubric measured the wrong direction.** It counted claims a session
  asserts and never the capabilities a session retires. Both of the run's
  known information losses — this one and the s11–s14 job-handoff
  relaunches — are losses of *capability at a session boundary*, and the
  rubric has no instrument for either.
- Minimum fixes for any run 2: DEAD lines enter the graded grammar and get
  verified like claims; a successor must re-test an inherited infrastructure
  negative before honouring it; and the grammar needs an `UNRESOLVED:` slot
  so open leads stop being filed as closed doors.

---

# Part 2 — the pre-launch panel, scored

Both predictions were scored blind at grading. The three review lanes were
not, and they were the artifacts specifically about *method* failure —
which is where the run actually broke. Scored here against the
preregistration as launched and against the run's record.

## Adoption

Nearly total, and verifiable in the shipped documents.

**R1 (can the design answer its own questions?)** — 11 of 12 numbered items
landed. Tokens from `usage` records rather than byte count (§5; the
`usage/session-NN.json` files exist and carry the report's 91.13M);
verification charged to the loop (REPORT's grading-cost section);
verdict rule pre-registered (`sealed/VERDICT-RULE.md`); banked-claim list
sealed (`sealed/BANKED-CLAIMS.md`); worked examples sealed
(`sealed/WORKED-EXAMPLES.md`); blinding of claim verification and
prediction scoring, with the grading instance holding no prediction and not
authoring the prereg (REPORT's opening paragraph is a point-by-point
recital of this item); session model named `claude-fable-5` (§2:42);
decay conditioned on claim reuse with both numerator and denominator and a
NOT TESTED floor (§5:140); stop rule armed at session 6 (§6:149); C5's
rule-of-three bound (REPORT quotes R1's own ~0.21 figure).

Declined: **item 12, the paired court arm.** R3's time cut supplied a
*historical* same-problem court instead of a parallel one, which is why Q1
has a table at all — and R1's stated consequence of declining still landed
exactly: "Q2 is dead and Q1 is descriptive only." REPORT: Q2 NOT TESTED;
the per-rung ratio "entirely a numerator-of-one effect."

R1's S3 split — report verified-by-execution separately from
verified-by-second-reading — is the reason REPORT can say "58 by execution,
5 by reading" instead of one soft number. That split is doing most of the
work in the run's headline finding.

**R2 (Goodhart)** — every bucket it asked for exists in the graded record:
UNFALSIFIABLE (V10), VACUOUS (V3's flip test), witting/unwitting
re-derivation split (V9), direction-source logging per session (V5 — this
*is* REPORT's Q2 line, "predecessor-OPEN in 11/14, novel in 2, PENDING in
1"), VERIFY lines counting for the stop rule (inverse-incentive 1),
self-caught errors credited positively (inverse-incentive 2), grading
minutes reported alongside steering minutes (inverse-incentive 7), and the
claim table filed and hashed before either prediction was opened ("the
grader has a stake").

**V8 is the panel's sharpest single call.** "Fleeing the core to stay clean
on re-derivation": work where nothing could be banked, score zero
re-derivations, and let a one-line scope statement absorb it. That is the
run's verdict shape exactly — 0 re-derivations, 1/3 rungs, eleven sessions
on ground the court never touched. R2 named the signature four months of
design ahead of the record; it attributed it to incentive-following rather
than to the loop simply taking the first tractable lever, but the
observable it predicted is the observable that occurred.

**R3 (mechanics)** — 10 of 11 edits landed, and edit #1 *became the
design*: cut at `74b2c20`, grade against the three-rung ladder to
`37ce404`. Its report grammar (DIRECTION / SHAPE / CARRY / CLAIM / OPEN /
DEAD / LOG / VERIFY) is verbatim what all fourteen sessions wrote. Its
§(b) 7-file measured core is cited by name in `SANDBOX.md`. Its #8 —
"record bulletin edit count; untouched ⇒ Q2 reports NOT TESTED, never
'steering not worth its cost'" — is REPORT's Q2 section word for word.

Its #3 is the catch of the whole panel: the agent memory directory loads
`convex-polyplets-lead.md`, which states the rung-1 answer in plain text,
into every session by default. §8's contamination list did not name it.
Had that not been caught, the run would have been contaminated at open and
the entire exercise void.

Not delivered: **#7, three token curves.** Preregistered (§2:31) and then
not built by the launcher. Q3's "instrumentation gap" is therefore not a
review miss — it is an implementation failure against an adopted
recommendation.

R3's named risk for its own design was half right: it predicted rung 1 might
fall by session 2 and the loop would then be "back in banked-answer
territory by session 5." Rung 1 fell at session 1; the loop did not return
to banked territory at all.

## What all three lanes missed

Two things, and the triage found both.

**1. Literature priority.** Every lane analysed re-derivation against *the
repo*. R1 item 4 sealed a repo-scoped banked-claim list; R2's V8/V9 argue
about repo-banked material; R3's C4 analysis is entirely about what
`results/convex-polyplets.md` already holds. No lane asked whether the loop
could re-derive *published* work and whether anyone would notice. R3 came
within one sentence of it — noting the non-D-finiteness proof is "open in
the literature for the polyomino control too" — and did not generalise.
The run then re-derived a published area limit law at roughly a third of
its budget (`VALUE-TRIAGE.md` §C), invisibly to loop and grader alike.

**2. False negatives.** R2's entire frame is inflation of positives: eleven
vectors, all about making the record look better than the work. A DEAD line
makes the record look *smaller*, so it is outside the frame. R3 designed the
DEAD field and proposed no rule for grading it. Part 1 above is the cost.

Both misses share a shape: the panel audited what the loop would *assert*
and never what it would *foreclose*. That is the same blind spot the rubric
inherited, and it is the one thing a run 2 must fix before anything else on
the DISPOSITION §5 list.

## Verdict on the panel process

It worked, and it is the cheapest thing in the whole experiment. Three desk
lanes, one day, no compute; ~30 of 34 numbered recommendations adopted; one
of them (R3 #3) prevented a void run and another (R3 #1) supplied the entire
graded design. Almost every property that makes `REPORT.md` readable —
the sealed verdict rule, the blinding, the execution/reading split, the
four claim buckets, the direction-source count, NOT TESTED as a distinct
outcome from a null result — traces to a specific numbered panel item.

Against that: the panel shared one blind spot across all three lanes, and
it was the blind spot that cost the run a third of its budget. Diverse
lanes are not diverse perspectives when they all read the same
preregistration and the same repo. A fourth lane briefed to read *outward*
— what does the literature already know, and what would we do if the loop
re-derived it — would have been the highest-value seat at the table and cost
the same as the other three.
