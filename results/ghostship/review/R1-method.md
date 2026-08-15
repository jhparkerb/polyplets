# Ghost Ship review, lane R1 — can the design answer its own questions?

2026-08-15. Desk pass on `docs/ghostship-preregistration.md`, read against
`docs/offside-brief.md`, `results/offside/B-adversary.md`,
`results/offside/C-replay.md`, and Li et al. §3–§5 + Tables 1–2
(`/Users/jasonp/.claude/jobs/fd684800/tmp/gc-paper.pdf`). Nothing was
executed against the project; the one measurement below reads session
transcript files under
`/Users/jasonp/.claude/projects/-Users-jasonp-src-polyominoes/`.

## Summary judgement

The protocol is honest about most of its own weaknesses and dishonest about
one: it presents itself as answering three questions, and as written it can
answer roughly half of one of them. Six items are fixable with an edit and
cost nothing; five are structural and need the questions rewritten to fit
what a single run can support.

The two findings that should move the decision most:

- **The token metric is wrong, and I can measure how wrong.** §5 defines
  tokens as transcript byte count. Over six real sessions on this project
  the bytes-to-tokens ratio ranges from 9.3 to 27.6 — a factor of three,
  larger than any effect this experiment could detect — and 94.5–97.7% of
  the tokens are cache reads, whose volume is a function of turn count and
  context size, exactly the axis on which the two flows differ for reasons
  unrelated to research output. Q1's denominator and Q3's growth curve are
  both built on this. The fix is free: the numbers are already in the
  transcripts.
- **§5 fixes metric names and leaves the verdict rule unregistered.** C3
  forbids adding or reweighting metrics after launch. There are no weights
  to reweight, and no rule anywhere saying which combination of nine
  outcomes counts as the loop doing well. A grader can therefore choose the
  weighting after seeing the record without ever touching a metric, and C3
  reports itself satisfied. Pre-registering a crude verdict rule beats
  applying a careful one afterwards; that is the whole point of sealing.

## 1. The measurement: what "tokens" costs to get wrong

Method, so it can be redone: for each session transcript, sum
`input_tokens + cache_read_input_tokens + cache_creation_input_tokens +
output_tokens` over every assistant `message.usage` record, and compare to
the file's byte size. Six most recent sessions in this project's transcript
directory:

| transcript | bytes | tokens | tokens/byte | cache-read share |
|---|---|---|---|---|
| `eb19f5d9` | 309,890 | 2,883,898 | 9.3 | 0.945 |
| `ac4e559b` | 367,709 | 4,041,434 | 11.0 | 0.949 |
| `8ec24a38` | 478,804 | 4,540,439 | 9.5 | — |
| `fd684800` | 1,436,916 | 32,872,282 | 22.9 | — |
| `4ec98b29` | 3,817,553 | 105,237,455 | 27.6 | 0.959 |
| `e81d564c` | 8,137,579 | 113,205,403 | 13.9 | 0.977 |

Three consequences.

**(a) Bytes are not a monotone proxy for tokens.** The ratio is not
constant and not even ordered by size: `e81d564c` is twice the bytes of
`4ec98b29` and costs fewer tokens, because its bytes are large tool outputs
that are written once, while the other re-sends a smaller context many more
times. A metric that can invert the ordering of the two things it compares
is not a measurement.

**(b) "Tokens" is undefined between raw and cost-weighted.** Cache reads
are 95–98% of the total and are billed at a tenth. The two flows differ
systematically here: fourteen fresh sessions each build their own cache
from scratch, while a court evening amortises one large context across
lanes and turns. Choosing raw or cost-weighted after seeing the record
moves the headline ratio by close to an order of magnitude, and §5 does not
choose. This is the same C3 hole as the verdict rule, in a different place.

**(c) The fix is one line and it is free.** Record per-session
`usage` totals from the transcript, report raw and cost-weighted
separately, and state that receipts for both are the transcript files.
Byte count can stay as a third column; it must not be the denominator.

While recording: the loop's cost is not the loop's cost. §5 measures
verified claims by a court pass that runs *after* the run and charges
nothing to the loop. The king-twigs baseline paid its verification inside
the measured day — `results/king-twigs-l1.md` verifies its own claims with
`experiments/kingtwigs/l1_schemes.py` in 12.7 s of the same session. So the
comparison as written charges one arm for verification and not the other.
Add a metric row for the verification pass's own tokens and wall time, and
report the loop as `loop tokens + verification tokens per verified claim`.
This is fixable and it is not cosmetic: on a fourteen-session run of
judgment-shaped claims, the verification pass is plausibly the larger half.

## 2. Structural: the confounds, and which question survives each

### S1. Q1 and Q2 change four variables at once

Between the Ghost Ship arm and the named baselines, these all differ:
court/no-court (Q1), synchronous/bulletin steering (Q2), sandbox slice /
full repo + git + memory injection + CLAUDE.md, the problem itself, the
session model (unspecified in §2), and session count. Six differences, two
questions, one run. No outcome can be attributed to any single one.

Two of these are fixable and should be fixed regardless: **name the model
for Ghost Ship sessions in §2 and match it to whatever arm the comparison
is against** — the project has a standing position that model choice
changes judgement work materially, so leaving it free means the headline
may be measuring models — and state the sandbox difference as a named
condition rather than an implementation detail.

The rest is structural. Scope down:

- **Q1 becomes descriptive.** "Did this sandboxed unattended loop produce
  court-verified claims on this thread, and at what token cost?" That is
  answerable and worth knowing. "In the same league as the court model" is
  not answerable at n=1 across different problems, and should be struck or
  moved behind the paired arm below.
- **Q2 is not answerable at all as designed.** There is no
  synchronous-steering arm on this thread. The design compares a bulletin
  the operator has never used against synchronous steering on two other
  problems, with abstention removing his only alternative to the bulletin.
  Either add the arm or delete Q2 and replace it with the observation it
  can actually support: *was the bulletin used, and did the sessions read
  and act on it?* That is a fact about channel viability, not about worth.
- **Q3 survives in half.** The token-growth shape of the loop is
  measurable. The court's shape is not, because both named baselines are
  single days — there is no multi-session court to draw a curve from.
  Rescope Q3 to "measure the loop's growth shape" and drop the "vs".

And a note that undercuts Q3's premise: §2 gives each session *all* prior
session reports as input. That is a read-everything pattern over a growing
corpus, not a chained-summary pattern. Unless R3's report cap is tight, by
session 14 the loop is doing what the court does, over reports instead of
over the repo. The contrast Q3 names may be null by construction — worth
checking against R3's format rules before this metric is sealed.

### S2. Fourteen sessions is below every timescale the failures live on

Li et al.'s two named weaknesses have timescales in the record. The
judgement failure manifested at session 18 and needed an operator pivot;
the state failure lost a caveat written in session 4 and a criterion proved
in session 8, and surfaced at session 44, twenty-five days later. §5's
`judgment failures` metric ("≥3 same-shaped attempts") cannot fire before
session 3 and has at most twelve chances; `decay` at N+3 has eleven
windows.

This makes the design **one-sided**: observing a failure is informative,
observing none is not. Quantify it so nobody over-reads a clean run — zero
events in fourteen sessions bounds the per-session rate only at about
3/14 ≈ 0.21 by the rule of three. A run with no re-derivations licenses
"the per-session re-derivation rate is under roughly one in five", which is
not a defence of the loop.

State this in §8 as C5: *a clean run does not acquit the loop; only a dirty
one convicts it.* The skeptic should be told this before he seals a
prediction, because it changes what his prediction is worth.

### S3. "Verified" is soft for the thread that was chosen for being soft

§3 picks Convex Polyplets because it is judgment-shaped with no compute
gate. §5's headline metric is "the lead reproduces it from its receipt". In
a sandbox with no compute and no fleet, a receipt for a judgment claim is a
file reference and an argument, and reproducing it is a second reading
agreeing with a first. The property that makes the thread suitable makes
the metric weak, and the two sections pull against each other.

Not fixable by thread choice — the alternative reintroduces the compute
gate. Fixable by splitting the metric: report `verified by execution` and
`verified by second reading` as separate counts, and require §7's
predictions to predict the mix. If the run's claims are 90% second-reading,
the reader knows what "verified" bought.

### S4. This is not the Li condition, and §9's justification leans on saying it is

§2 calls the loop "the Li condition, in our tooling". Li's condition, from
§3 of the paper: two models in distinct roles (reasoning model plus coding
agent), ~240 sessions, up to five running in parallel, a forced
plan-ahead step, up to twelve reasoning calls per session, about forty
dated human directives, and periodic operator review by reading and
summarising the reports. Ghost Ship has one model, fourteen sessions, no
parallelism, a passive bulletin, and an abstention rule that forbids the
directives Li credits with the run's only theorem.

So no outcome here is evidence about Li et al.'s setup. It is evidence
about *our* unattended loop, which is a fine thing to measure. But §9's
case — that this supplies "the point of comparison that currently does not
exist anywhere, including in Li et al., who ran only their own condition"
— does not hold: the missing comparison is a court arm on *their* problem
with *their* session count, and this experiment supplies neither. Rewrite
§2's heading and §9's paragraph to rest on our own argument. The experiment
still pays; it just does not pay that particular debt.

This matters beyond wording. If the loop fails, the reading available on
launch day will be "unattended looping does not work", and the proposition
that has an actual advocate — Li's steered, parallel, two-model,
240-session loop — will not have been tested. Naming this now is cheaper
than arguing about it at grading.

### S5. Grading bias: half of it is blindable, half is not

The lead writes the pre-registration, chooses the thread and the slice,
seals a prediction, runs the post-run court, and grades. Five roles. Taking
them in order of how much the bias can be removed:

**Blindable, and should be.**
- *Claim verification.* A claim plus its receipt path can be handed to a
  fresh agent with provenance stripped and no statement of which flow
  produced it. Verification of "does this receipt support this claim" does
  not need to know the author. Do this.
- *Prediction scoring.* §7's "grading includes scoring both prediction
  files" is the single most bias-prone act in the design: the person who
  wrote one of the predictions grades both. Fix: hand a fresh agent the
  record and both texts labelled A and B, authorship stripped. Cheap and
  complete.
- *Role separation.* Whoever grades must not hold a sealed prediction and
  must not have authored the pre-registration. Given §7 requires a Fable
  prediction, the grading instance must be a different one that never reads
  §7 until after filing.

**Not blindable — accept and mitigate.** `judgment failures` and `decay`
are read off the sequence of reports. The reports are flow-identifying by
format and content; you cannot blind a grader to which arm produced a
fourteen-report chain. Mitigation is pre-registration of the rubric, not
blinding: for each subjective metric, seal two worked positive and two
worked negative examples drawn from the existing corpus (the Offside lane
files and `results/king-twigs-l1.md` supply both kinds) *before* launch.
"≥3 same-shaped attempts without reframing" has all of its content in
"same-shaped", and that word is currently the grader's to define after
seeing the data.

## 3. Sample size 1: the strongest honest conclusion

What a single run of a single arm licenses:

- **Existence.** "On this thread, in N sessions costing T tokens, the loop
  produced C claims, of which V survived verification costing a further U
  tokens." Licensed, and worth having.
- **Failure-mode presence.** "Re-derivation occurred, here are the K
  instances." Licensed. Absence is bounded only as in S2.
- **Channel facts.** "The bulletin was edited M times and referenced in P
  reports." Licensed.
- **Prediction calibration.** This is the design's best output and it is
  already in §7. Two sealed prediction files, each covering several
  categories — failure modes, expected verified-claim count, bulletin use,
  what the court would have done better — give a handful of independent
  scored calls rather than one. At n=1 on the flow question, n≈8 on the
  predictor question. Foreground it: the experiment is better described as
  a calibration test of the skeptic and of Fable, with a flow observation
  attached, than the other way round. That reframe costs one paragraph and
  makes the design's own strongest property its headline.

Not licensed by any edit short of a second arm: rate comparisons, "same
league" claims, per-token ratios against king twigs or Offside. Those
baselines are also n=1 courts, on different problems, with different claim
genres — king twigs is one compute-backed thread closing a door against a
pre-registered kill criterion, Offside is a six-lane desk review of a
design document. Claims-per-token across those is dominated by whether a
script exists to run, not by flow.

**The one edit that buys the comparison: a paired court arm on the same
thread and the same slice.** One evening, six lanes, which the Offside
panel has already priced. Run it in parallel with the loop, with its
outputs excluded from the loop's sandbox, and grade both under the same
sealed rubric. That holds the problem, the corpus and the model fixed and
leaves court/no-court plus steering as the only difference — which
collapses S1 from six confounds to two and makes Q1 and Q2 answerable at
the level of "on this problem, this once". Without it, every per-token
sentence in the write-up will need a hedge that makes it unquotable.

## 4. Stop rules: the bias runs the opposite way from the brief's guess

§6 ends the run after two consecutive sessions with zero new claim lines.
Four problems, in order of size.

**(a) It flatters the loop's headline ratio.** Barren sessions burn tokens
and produce no claims. Truncating the barren tail *raises* claims-per-token
— the stop rule protects the metric from the failure mode it is meant to
detect. A loop that spins is precisely the skeptic's prediction, and the
design stops measuring it two sessions in. Fix: record `stopped at N` as an
outcome, and report the ratio both raw and normalised to the planned
fourteen, both declared now.

**(b) It punishes the honest behaviour it wants to see.** A session that
spends itself checking a predecessor's claim produces no new claim lines.
Two such in a row end the experiment. The design is asking whether the loop
self-corrects, and killing the run when it does. Fix: define the stop rule
on receipts created rather than claim lines, or exempt sessions whose
report resolves a prior claim. (R2's lane will reach this from the gaming
side; it is the same edit.)

**(c) No floor.** Sessions 1 and 2 are the least informed in the run — the
first reads a problem statement and nothing else. Two cold-start sessions
can end the experiment before it exists. Fix: the rule arms at session 6,
or after the first claim is produced.

**(d) Early stop voids §7's counts.** A sealed prediction of "expected
verified-claim count" is written for a fourteen-session run. If §6 fires at
session 5, the prediction is unscoreable, and the grader will improvise.
Fix: require §7's numeric predictions to be per-session rates, or
conditional on N.

Two smaller items in the same family. **Who watches the stop rule?**
Detecting two zero-claim sessions requires reading reports mid-run, which
is the exposure §4's abstention exists to prevent and which later biases
grading. Automate it — count claim lines by grep, no human reading — or
log the exposure in `CONTAMINATION.md` as known. And **the halt hatch is an
optional-stopping channel**: §4 lets the operator halt at any time, but
under abstention he is not reading reports, so §4 should say what he *may*
observe (that reports exist, machine metrics, elapsed sessions) without
reading content. As written, "halt when it looks bad" is available and
uncovered by any bias analysis in the document.

## 5. Metric-by-metric, briefly

Everything not already covered above.

- **claims produced** — "claim lines in reports" makes the unit
  agent-chosen and non-comparable to baselines written to a different
  brief. Fix: the grader extracts distinct verifiable propositions from
  each report; session line-counting is not the measurement. Removes
  claim-splitting as a side effect.
- **re-derivations** — "already banked in the full repo" is decided by the
  grader after reading the reports, which is C3's hole again. Fix:
  pre-register the banked-claim list for this thread — the extract of what
  the full repo holds and the slice does not — and sha256 it into §7
  alongside the predictions. Without it, the metric's denominator is
  written after the data.
- **decay** — measures topic change, not decay, as written. A caveat that
  is not restated because its claim was never reused is not a lost caveat.
  Fix: enrol every caveat line mechanically, and count a loss only when a
  later report *uses the qualified claim* without the caveat. Also state
  the sampling rule; "(sampled)" currently means the grader picks.
- **operator cost** — self-reported bulletin minutes against baselines
  whose operator cost was never recorded at all, so the comparison has one
  side. And it measures the wrong cost: the expensive human input in this
  design is the post-run court pass. Record that wall time too.
- **wall days** — nothing depends on it and §2 declares the spacing
  irrelevant. Keep it as a recorded fact, not a metric.

One property of §2 worth protecting because it is a genuine anti-Goodhart
win: sessions are given §3, the bulletin, and prior reports — **not §5 and
not §6**. The sessions cannot optimise for metrics they have not seen. Two
leaks threaten it: a session that speculates in its report about how it is
being judged teaches every later session, and the bulletin is an
uncontrolled operator channel into the run. Add one line to §4: any
bulletin text referencing metrics, counts or grading is contamination.

## 6. The list, separated

**Fixable with an edit, cheap:**

1. Token metric from `usage` records, not bytes; report raw and
   cost-weighted separately. (§1 above; measured.)
2. Charge the post-run verification pass's tokens and wall time to the
   loop, and say so in the ratio's definition.
3. Pre-register the verdict rule — which combination of outcomes counts as
   the loop doing well — with numbers chosen now. Closes C3's real hole.
4. Pre-register and seal the banked-claim list used to grade
   re-derivations.
5. Pre-register worked examples for `judgment failures`, `decay` and claim
   extraction; two positive and two negative each, from the existing
   corpus.
6. Blind what can be blinded: claim verification with provenance stripped,
   prediction scoring with authorship stripped; the grading instance holds
   no sealed prediction and did not author the pre-registration.
7. Name the session model in §2 and match it across arms.
8. Fix `decay` to condition on claim reuse; state the sampling rule.
9. Stop rule: arm at session 6, define on receipts not claim lines, report
   raw and 14-normalised, make §7's numbers rates.
10. §4: bulletin text about metrics or grading is contamination; automate
    the stop-rule check so nobody reads reports mid-run; state what the
    operator may observe before halting.
11. Add C5 to §8: a clean run does not acquit the loop (rule of three,
    ~0.21 per session at 0/14).

**Fixable but not cheap, and the highest-value item:**

12. A paired court arm on the same thread and slice, run in parallel, its
    outputs excluded from the sandbox, graded under the same sealed
    rubric. One evening at Offside's price. Without it, Q2 is dead and Q1
    is descriptive only.

**Structural — accept and scope down:**

- Q1 becomes descriptive unless item 12 lands; Q2 is deleted or waits for
  item 12; Q3 loses its "vs" and may be null by construction if the loop
  reads all prior reports.
- Fourteen sessions cannot observe Li's failures at their timescales;
  evidence is one-sided.
- "Verified" is soft on a judgment-shaped thread; split the metric rather
  than pretend otherwise.
- This is not the Li condition; §2's heading and §9's justification need
  rewriting to stop borrowing its authority.
- `judgment failures` and `decay` cannot be blinded; pre-registered
  examples are the only mitigation.
- n=1 licenses existence, failure presence, channel facts and prediction
  calibration. Nothing else.

## What the design gets right

Conceded plainly, because three of these are better than the corresponding
parts of anything in `docs/offside-design.md`.

1. **§7 is the strongest thing in the document.** Sealing the skeptic's
   prediction converts an argument into a measurement, it is the one part
   of the design that is fully valid at n=1, and it measures the
   predictors as well as the loop. It should be the headline.
2. **Withholding §5 and §6 from the sessions.** Most protocols of this
   shape hand the graded population its own rubric. This one does not, by
   construction of §2's input list.
3. **§8 exists at all, and C4 is delegated to a reviewer rather than
   answered by the author.** Naming what would make your own result
   uninterpretable, before launch, is the part everyone skips.
4. **The abstention rule is stated as all-or-nothing with a contamination
   log.** Partial steering is the failure that would silently make this
   experiment meaningless, and §4 makes it a HALTED outcome instead of a
   footnote.
5. **§9 prices the null result honestly** — it argues the experiment pays
   under the skeptic's own prediction, which is the correct standard for
   deciding to run it. The argument's dependence on Li is what needs
   cutting, not the argument.

Weakest items in this file, conceded before anyone finds them: the token
ratios in §1 are six sessions of mixed provenance, not a controlled
measurement of the two flows, and they establish that the byte proxy is
unstable rather than the size of the error it would introduce here; the
rule-of-three bound assumes independence across sessions, which a
report-chained loop violates in the direction that makes the bound
optimistic; and item 12 is a recommendation to roughly double the cost of
an experiment whose cheapness is part of its case, which is the operator's
call and not mine.
