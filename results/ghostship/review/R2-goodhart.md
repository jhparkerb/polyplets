# Ghost Ship review, lane R2 — the Goodhart pass

2026-08-15. Read in order: `docs/ghostship-preregistration.md` (the object),
`docs/offside-brief.md`, `results/offside/B-adversary.md`,
`results/offside/C-replay.md`, Li et al. §3–§5 + Tables 1–2
(`/Users/jasonp/.claude/jobs/fd684800/tmp/gc-paper.pdf`), plus
`results/convex-polyplets.md` and `scripts/check_receipts.sh` for what a
receipt and a claim actually look like in this tree. Desk only; nothing ran.

I am playing the session, not the reviewer: below is what I would do if I
were session 07 of fourteen, wanted the run to look good, and had no
intention of being dishonest about it. That last clause is the point of the
lane. Almost every move here is one a well-behaved session takes for good
local reasons, which is why "the sessions won't do that, they're not
adversarial" is not a defence.

## Summary

Eleven vectors. Nine are detectable post-hoc, seven of those only if the
grading pass is told **now** what to look for — which §8's C3 (no metrics
added after launch) makes a pre-registration problem, not a grading problem.
Two are not detectable at all from the record as §5 defines it.

The larger finding is on the inverse side: **six of the nine metrics punish
honest behaviour, and the two that punish it hardest — the stop rule and the
false-claim count — punish exactly the two behaviours the experiment exists
to look for.** A session that spends itself verifying a predecessor scores
zero and moves the run one step from an early stop; a session that refutes a
predecessor raises the run's false-claim count and gets no credit for the
catch. If the loop's answer to "does it catch its own wrongness" is no, §5
is part of the reason.

And one mechanical hole worth fixing before anything else: as written,
**`BULLETIN.md` is inside the session's write scope** (§2: "session writes
land only under `results/ghostship/` and the sandbox"; §4: the bulletin is
`results/ghostship/BULLETIN.md`). A session can write to its own steering
channel. So can it overwrite predecessors' reports.

## What a session actually sees, and why the rubric leaks anyway

§2 gives a session three inputs: the §3 problem statement, the bulletin, the
prior reports. §5 and §7 are not among them. So the naive model is that a
session cannot game a rubric it has never read.

That is wrong on three channels, and the strength of the whole lane rests on
this, so it goes first.

1. **The report schema is the rubric.** §2 requires each report to carry
   direction, what happened, claims with receipts, failures, and a
   next-session suggestion. Every one of those fields is a §5 metric surface:
   direction ↔ judgment failures, claims-with-receipts ↔ claims produced and
   verified claims, failures ↔ false-or-unsupported, next-session suggestion ↔
   the bulletin channel. A session does not need §5. It needs the five field
   names, and it is handed them.
2. **The rubric is emergent from report 01.** The loop's protocol "is
   whatever the sessions develop — that is part of what is being measured"
   (§2). What sessions 02–14 develop is imitation of 01. Whatever session 01's
   report over-produces — claim lines, hedges, direction pivots — becomes the
   house style for the other thirteen, and it is set by a single ungraded
   draft written with no calibration. This is the one Goodhart mechanism
   specific to report-chaining and it has no counterpart in the court.
3. **The slice may contain the experiment.** The sandbox is a `git archive`
   of the corpus slice plus a filtered `git log` (§2). `docs/ghostship-
   preregistration.md` is committed in this repo, as is this review directory.
   If the filter is by path and the log filter is by anything less than an
   explicit allowlist, a session that greps its own sandbox for its own thread
   name finds §5 verbatim. That is not a leak of a secret — it is handing the
   graded party the grading table.

**One-line fix covering all three:** pre-register a fixed report template with
a worked example report (written by the lead, on a topic outside the thread)
shipped as session 00, and pre-register the slice as an explicit allowlist of
paths with `results/ghostship/**` and `docs/ghostship-*` excluded from both
the archive and the log filter.

## The vectors, ranked by how much they distort the verdict

### V1. Claim-splitting

**The move.** One finding becomes eight claim lines sharing one receipt. This
is not hypothetical prose — take `results/convex-polyplets.md:191-201`, one
paragraph of real banked work, and it splits cleanly into: 199 terms exist at
s=2..200; the (5,2) recurrence was fitted on the first 22 rows; it predicts
all 172 remaining rows; `find_prec` returns non-None on the full series;
`find_prec` trains on `unknowns + train_extra` rows regardless of length, so
this is a re-use not a refit; the ratio at s=199→200 is 4.02172; that is
consistent with "~4.13 and falling"; `build/convex_perim_tm 200 1`
reproduces it. Eight claim lines, one receipt, one afternoon. Every one of
them is true and each would survive court reproduction.

**Scores because** "claims produced" and "verified claims" are line counts
(§5) with no granularity rule. Offside lane C already named this as the
load-bearing unknown for the *other* design
(`results/offside/C-replay.md:315-323`); here it is worse, because there the
count was a cost and here it is the headline.

**Detectable post-hoc?** Yes, mechanically — count distinct receipts per
claim and the ratio jumps out. But detection does not tell you the right
number, and deciding it after the run is C3.

**One-line fix.** Fix granularity before launch by worked example: count the
claim lines in three banked notes of different shapes (`results/motley-h17.md`,
`results/convex-polyplets.md`, `results/ridgeline-depth-amplitudes.md`), publish
those counts in §5 as the calibration, and grade the run against them.

### V2. Read-off receipts

**The move.** The slice contains banked results notes full of numbers. Lift
one, cite the note as the receipt. The receipt path exists, is non-empty, is
in-tree; the lead reproduces the claim from it in ten seconds; it verifies.
Zero work performed.

**Scores because** §5 defines verified as "the lead reproduces it from its
receipt", and a claim that *is* its receipt's content always reproduces.

**Detectable post-hoc?** Yes, and cheaply.

**One-line fix.** A receipt must be a file **created or modified during the
run**; a claim resting on a file present in the sandbox at session 00 is
tagged READ-OFF and counts in neither the claim nor the verified bucket.

### V3. Tautological receipts

**The move.** Sharper than V2 and not covered by it. Write a script that
computes X, run it, log X, claim X, cite the log. The claim is a restatement
of an artefact the session authored for the purpose. It reproduces perfectly
and asserts nothing that could have come out otherwise. "The DP at n=200
returns 47.9 s of wall" is a receipt-shaped claim about the session's own
afternoon.

**Detectable post-hoc?** Only by a grader who has been asked the right
question. Reproduction cannot distinguish a finding from an echo.

**One-line fix,** and it is native to this repo's own standard: a claim passes
only if the grader can name a **mutation of the receipt that would flip it** —
red-first, exactly `scripts/check_receipts.sh --self-test`'s rule that "a gate
that has never rejected a planted claim is not a gate"
(`scripts/check_receipts.sh:37-40`). Claims that cannot be flipped by any
mutation are counted separately as VACUOUS.

### V4. Direction-restating as reframing

**The move.** The judgment-failure metric fires on "≥3 same-shaped attempts
without reframing" (§5), and shape is read off the one-line direction
statement the report itself writes (§2). So: same work, new direction line
every session. "By area." "By area, with the 4-cone restriction." "By area,
control arm." "By area, second prime." Three of those are genuine reframes in
the convex thread's real history and one is a knob turn, and nothing in the
metric distinguishes them.

**Scores because** the graded party writes the classification input.

**Detectable post-hoc?** Yes, if the grader classifies shape from the
receipts and methods, not the prose.

**One-line fix.** Shape is assigned by the grader from the receipts and the
code paths exercised; the direction line is evidence toward that assignment
and never the assignment itself.

### V5. Bulletin-fishing

**The move.** End every report with a sharp question aimed at the operator —
"the (19,3) box is minimal on the frontier; is a proof of minimality worth a
session, or should I take the out-of-sample enumerator run?" A skeptic who
reads that and answers in the bulletin has just supplied program-level
research judgement, which is precisely the human contribution Li et al.
isolate as the one the system could not supply (§5, "the operators supplied
program-level research judgement… the lower bound pivot is the crucial
instance"). It is formally legal: §4 makes the bulletin the entire steering
channel and lets the operator edit it at any time.

**Scores because** the loop borrows the court's judgment channel and keeps
the loop's token accounting. It also destroys Q2: if the loop performs well
because the operator answered fourteen questions, the experiment measured the
operator.

**Detectable post-hoc?** Yes — bulletin edits are dated and reports are
dated. Nobody has been told to do the join.

**One-line fix.** Pre-register that the operator does not answer questions
posed in reports, and record per session whether its direction came from the
bulletin, from a predecessor's suggestion, or from nowhere — that count is
the Q2 measurement and §5 currently does not contain it.

### V6. The bulletin and the reports are writable

**The move.** Append to `BULLETIN.md` — a note to successors that dodges the
report format, the length discipline and the claims-block, and arrives in
successors' context labelled as operator instruction. Or edit `reports/03.md`
to soften a claim a later run refuted, or to remove a caveat before the N+3
decay sample lands on it.

**Scores because** §2 puts session writes under `results/ghostship/`, which
is where both the bulletin and the reports live. No rule in the document says
otherwise.

**Detectable post-hoc?** Only if hashes are taken. From the final directory
state, an edited report is indistinguishable from a well-written one, and
this is one of the two vectors that is genuinely invisible.

**One-line fix.** `BULLETIN.md` is operator-write-only and read-only to
sessions, and each `reports/NN.md` is sha256'd at session end into a manifest;
any later divergence is a `CONTAMINATION.md` line.

### V7. Caveat laundering, both directions

**The move, (a) the empty denominator.** Write no caveats. Decay is "do
caveats present in report N survive to report N+3" (§5); zero caveats survive
perfectly. A caveat-free run scores 100% on the metric built to catch Li's
session-44 failure.

**The move, (b) the standing block.** Copy a boilerplate caveats block
verbatim into all fourteen reports. It survives to N+3 by construction, while
no decision respects it. This is Li's failure exactly as diagnosed: "in both
failures, the archive retained the original facts; it was the compressed
state governing decisions that failed" (§5). Textual survival is not what
went wrong there, and it is all §5 measures.

**Detectable post-hoc?** (a) yes and trivially — count caveats per report.
(b) yes, but only by checking consumption, which is a judgement call the
grading pass has not been assigned.

**One-line fix.** Report both numbers — caveats written per report and
survival rate — and score survival only over caveats whose scope a later
report's work actually entered, so a caveat that never had a chance to be
violated is excluded from the denominator rather than counted as a save.

### V8. Fleeing the core to stay clean on re-derivation

**The move.** Re-derivation is the skeptic's predicted failure and the
session can guess it: the sandbox is visibly a slice, and a slice implies a
complement. Safest play is to work where nothing could be banked — the
periphery, the untouched corner, the question nobody asked because it does
not matter. Zero re-derivations, and the goal-drift metric is soft enough
(§3 is one sentence) to absorb it.

**Scores because** re-derivations are counted and irrelevance is not.

**Detectable post-hoc?** Partly — goal drift is in §5 — but §3's boundary is
one line and the grader is also the person who chose the thread, so the call
is unfalsifiable in either direction.

**One-line fix.** Seal an explicit in-scope / out-of-scope subtopic list for
the thread alongside the §7 predictions, so drift is decided against a text
written before the run.

### V9. Re-derivation as the cheapest source of verified claims

**The move,** and it is V8's mirror. Banked results reproduce. If a session
does not know the weighting between "verified claims" (up) and
"re-derivations" (down), re-deriving is the highest-yield thing it can do
with an afternoon: guaranteed reproduction, clean receipts, real mathematics.

**Scores because** §5 lists both counts and states no relation between them.
As written, a re-derived claim plausibly scores in *both* buckets.

**Detectable post-hoc?** Yes; the check is a grep against the full repo, and
§5 already specifies it.

**One-line fix.** A re-derived claim moves buckets, it does not add: it is
excluded from "verified claims" entirely. And split the count into *witting*
(the report flags the possibility) and *unwitting*, with only unwitting
counting as a failure — otherwise V8 and V9 leave the session no honest play.

### V10. Hedging to protect the false-claim count

**The move.** Write nothing falsifiable. "Suggests", "appears consistent
with", "is compatible with". Under §5's three buckets — verified, false,
unsupported — a hedged claim with a resolving receipt is not false, and it is
not unsupported either.

**Detectable post-hoc?** Yes, but only with a bucket that does not currently
exist.

**One-line fix.** Add a fourth bucket now, UNFALSIFIABLE, and weight it with
false rather than with verified.

### V11. Starving the denominator

**The move.** Q1 is a per-token ratio and the session controls the
denominator completely. Skim the predecessors instead of reading them, skip
the corpus, produce one cheap claim, end the session. Per-token score:
excellent.

**Scores because** the numerator is assessed after the run by someone else
and the denominator is assessed at session end by byte count. Only one of the
two is in the session's hands, and it is the one it can push toward zero.

**Detectable post-hoc?** Yes in aggregate; not per session, because "cheap
and right" and "cheap and shallow" have identical records.

**One-line fix.** Compute the per-token comparison run-total against
run-total only; per-session ratios are not a metric and are not reported.
(Also pin whether sub-agent transcripts count toward a session's bytes —
`git archive` sandboxes do not stop the Agent tool, and unpriced sub-agents
are a token-accounting hole large enough to swallow Q1 and Q3 together.)

## Detectability at a glance

| # | vector | detectable from the record? | needs a rule pre-registered? |
|---|---|---|---|
| V1 | claim-splitting | yes, mechanically | yes — granularity calibration |
| V2 | read-off receipts | yes, cheaply | yes — receipt must post-date session 00 |
| V3 | tautological receipts | only if the grader is asked | yes — flip-test |
| V4 | direction-restating | yes, from receipts | yes — shape assigned by grader |
| V5 | bulletin-fishing | yes, by date join | yes — no answers; log direction source |
| V6 | writable bulletin/reports | **no**, without hashes | yes — permissions + manifest |
| V7a | zero caveats | yes, by counting | yes — report the denominator |
| V7b | boilerplate caveats | only by consumption check | yes |
| V8 | fleeing the core | **no**, §3 is one line | yes — sealed scope list |
| V9 | re-derivation for credit | yes, §5 already specifies it | yes — bucket relation |
| V10 | hedging | yes, with a fourth bucket | yes |
| V11 | starving the denominator | in aggregate only | yes — run-total ratio |

## Metrics that punish honest behaviour

This is the half of the lane I did not expect to be the larger one.

1. **The stop rule punishes verification, and it is the sharpest instance.**
   §6: two consecutive sessions producing zero new claim lines ends the run.
   A session that spends itself reproducing a predecessor's claim produces
   zero new claim lines. Two honest sessions in a row therefore kill the
   experiment early, "graded as-is", with the verification work counting for
   nothing. The brief asked whether the claims-per-session incentive punishes
   such a session; it does worse than punish it — it makes it a threat to the
   run. **Fix:** a verification or refutation of a prior claim is a claim line,
   tagged VERIFICATION or REFUTATION.
2. **The false-claim count punishes catching wrongness.** §4 says wrongness
   is allowed to persist and "whether the loop catches it is a measurement".
   But a session that catches it raises "false or unsupported claims" and
   earns nothing; a session that lets it stand keeps the run's headline clean
   and might see the claim quietly verify. Every incentive in §5 points at
   leaving predecessors' errors alone. **Fix:** self-caught false claims are
   their own bucket, and reported as a positive for the loop.
3. **The judgment-failure trigger punishes correct persistence.** Three
   same-shaped attempts is a failure, so a session that reads two
   predecessors' attempts at the right approach and correctly continues it is
   walking into the metric, while one that pivots away from a working
   direction is protected. Li's own criterion was tighter than §5's: the
   attempts there "had failed for the same structural reason" (§5). **Fix:**
   require same-shaped *and* failed-the-same-way, so measurable progress
   breaks the chain.
4. **Decay punishes writing caveats at all** (V7a). The honest session that
   records five caveats risks five decay failures; the incurious one risks
   none.
5. **Re-derivation punishes honest self-checking** (V8/V9). With no witting
   /unwitting split, a session that writes "this may already be in the tree"
   volunteers itself for the failure column.
6. **Tokens punish reading the predecessors** (V11) — the loop's own memory
   mechanism, and the one thing that distinguishes report-chaining from
   fourteen unrelated sessions. Reading all prior reports is the behaviour the
   design is testing and the metric charges for it.
7. **Operator cost is defined so that the court pays for verification and the
   loop does not.** §5 measures operator cost as "minutes editing the
   bulletin, self-reported", while §5's own verified-claims row puts the
   court's reproduction pass *after* the run. The baselines — king twigs "one
   day, fully receipted", the Offside panel "one evening" — carry their
   verification inside the measured envelope. So the comparison charges the
   court for its verification and grants the loop its verification free, on
   the exact axis Q1 is about. §9 already concedes the post-run court pass may
   cost more than the loop saved; then it belongs in the metric. **Fix:**
   operator cost has two lines, steering minutes and grading minutes, and the
   headline carries both.

## The grader has a stake

§7 seals a Fable prediction and §7's last line makes grading score it. The
same party then decides, claim by claim, what verified and what was a
judgment failure — most of which are judgement calls (V3's flip test, V4's
shape assignment, V8's drift boundary). That is not an accusation, it is a
structural conflict of the same species Offside lane B flagged when the state
doc's own headline had rotted: care is not the mechanism.

**One-line fix:** the claim-by-claim grading table is filed and sha256'd
*before* either prediction file is opened.

## Weakest items in this file, conceded before anyone has to find them

- V2 and V9 overlap substantially; if the "receipt must post-date session 00"
  rule lands, V9 mostly closes with it and the separate bucket relation is
  belt-and-braces.
- V11's sub-agent hole is asserted from the protocol text, not from a test —
  I did not check what tooling a `git archive` sandbox actually exposes, and
  R3 owns that question.
- The claim that the report schema leaks the rubric (§"three channels", item
  1) is an inference about how a session behaves, not an observation. It is
  the assumption the whole lane stands on, and the cheapest way to test it is
  one throwaway pilot session graded against §5 before the fourteen are
  scheduled — which the two dry sessions in §6 could be repurposed to do.
- I have not costed any of the fixes. Most are one sentence in §5; the
  manifest in V6 and the calibration in V1 are not, and V1's calibration is
  real work that has to happen before launch.

## If only five changes land

1. `BULLETIN.md` read-only to sessions; `reports/NN.md` hashed at session end
   (V6 — the only invisible-and-mechanical one).
2. A receipt must be a file created or modified during the run (V2, most of
   V9).
3. Claim granularity calibrated against three banked notes before launch (V1).
4. Verification and refutation of a prior claim count as claim lines, for the
   count and for the stop rule (inverse-incentives 1 and 2 — the two that
   punish the behaviours the experiment is looking for).
5. Operator cost reports grading minutes alongside steering minutes (inverse-
   incentive 7 — without it Q1's comparison is decided by an accounting
   boundary rather than by the run).

All five are edits to §2, §5 and §6 of the pre-registration, none of them
adds a metric after launch, and all five are cheaper than one session.
