# Ghost Ship — pre-registration (DRAFT for teardown, not scheduled)

2026-08-15. Thread name: **Ghost Ship** — an unattended Li-style session
loop, run once, instrumented, as the point of comparison jasonp asked for.
Status: DRAFT. Nothing runs until this doc survives his review and the
predictions in §7 are sealed. **The operator is on record as quite
skeptical; §7 turns that skepticism into a registered prediction so the
experiment can vindicate it rather than argue with it.**

## 1. Questions

- Q1. Does an unattended loop produce verified-progress-per-token in the
  same league as the court model (brief → role lanes → lead verification →
  operator gate)?
- Q2. Is synchronous operator steering worth its cost, against a bulletin
  read only between sessions?
- Q3. What is the token-growth shape of a report-chained loop vs the
  court's read-everything pattern?

## 2. The loop (the Li condition, in our tooling)

- **14 sessions** — the unit is the iteration, not the day — scheduled
  three per day over ~5 calendar days, unattended. The spacing exists
  only to keep the bulletin a live channel (operator edit windows fall
  between sessions); it is not a property of the loop. Each session is
  a fresh agent whose ONLY inputs are: this doc's §3 problem statement,
  `results/ghostship/BULLETIN.md`, and the prior session reports in
  `results/ghostship/reports/`. It may read its sandbox corpus freely.
- Each session: pick a direction (stated in one line at the top of its
  report), a forced one-paragraph execution plan, then work; desk +
  sandbox scripts only — **no fleet jobs, no ssh, nothing outside the
  sandbox**; write `reports/NN.md` before ending (direction, what
  happened, claims with receipts, failures, next-session suggestion).
- Sandbox: an archive-export (`git archive`, no `.git`) of the corpus
  slice for the thread, plus a filtered `git log` file. Session writes
  land only under `results/ghostship/` and the sandbox; nothing syncs
  back to the repo until grading.
- No court: no lead verification during the run, no adversary lanes, no
  wave structure. The loop's own protocol is whatever the sessions
  develop — that is part of what is being measured.

## 3. The thread

**Convex Polyplets** (`results/convex-polyplets.md`, OPEN side-quest):
judgment-shaped, no compute gate, real but not precious, and its banked
state is rich enough that re-derivation — the skeptic's predicted failure
mode — is detectable. Operator veto slot: if this thread is wrong, name
another of the same shape before launch; the choice carries the verdict
(§8, C4).

## 4. Steering rule and abstention

- The operator may edit `BULLETIN.md` at any time; sessions read it at
  open only. That is the entire steering channel.
- **Abstention:** neither the operator nor the lead reads a report and
  acts on it, corrects it, or courts it during the run. Wrongness is
  allowed to persist; whether the loop catches it is a measurement.
- **Escape hatch, all-or-nothing:** the operator may HALT the whole
  experiment at any time (logged, with reason). Partial steering outside
  the bulletin is contamination and ends the run as HALTED, not GRADED.
- Contamination log: any violation, by anyone, gets a dated line in
  `results/ghostship/CONTAMINATION.md`. An experiment with a non-empty
  contamination log reports itself as compromised.

## 5. Metrics (all fixed here, none added after launch)

| metric | how measured |
|---|---|
| tokens | per-session transcript byte count, recorded at session end |
| sessions, wall days | count |
| claims produced | claim lines in reports, with receipt paths |
| verified claims | court verification of every claim AFTER the run ends; a claim passes if the lead reproduces it from its receipt |
| false or unsupported claims | same pass |
| re-derivations | claims whose content is already banked in the full repo (checkable because the sandbox is a slice) |
| judgment failures | ≥3 same-shaped attempts without reframing; goal drift from §3; work on already-closed doors |
| operator cost | minutes editing the bulletin, self-reported |
| decay | do caveats present in report N survive to report N+3? (sampled) |

Baselines for comparison, with the mismatch stated: king twigs (court,
one day, fully receipted) and the Offside panel (court, one evening, six
lanes). Different problems — comparisons are per-token and
per-failure-class, never headline-vs-headline.

## 6. Stop rules

- Two consecutive sessions producing zero new claim lines → run ends
  early, graded as-is.
- Hard end at 14 sessions (~5 calendar days at 3/day).
- Operator halt (§4) at any time.

## 7. Sealed predictions

Before launch, two prediction files, sha256'd in this doc by edit, texts
withheld until grading:

- **jasonp (registered skeptic):** his predicted outcome — expected
  failure modes, expected verified-claim count, whether the bulletin gets
  used, what the court would have done better. His stated prior: quite
  skeptical.
- **Fable:** same categories, sealed the same way.

Grading includes scoring both prediction files against the record — the
experiment measures the predictors as well as the loop.

## 8. What would make the result uninterpretable (named now)

- C1. Contamination (§4) — partial steering or mid-run courting.
- C2. Sandbox leak — a session reaching the live repo or fleet.
- C3. Metrics added or reweighted after launch.
- C4. A problem choice that predetermines the verdict — too easy
  flatters the loop, too hard flattens both flows. This is the review
  question for §3.

## 9. Cost and the honest case for running it anyway

Fourteen desk sessions across roughly five calendar days, no compute, no
fleet risk, bounded operator cost (bulletin minutes only). Under the skeptic's prediction — the loop
produces plausible prose, re-derives banked results, and the post-run
court pass costs more than the loop saved — **the experiment still
pays**: that outcome, measured, is the point of comparison that currently
does not exist anywhere, including in Li et al., who ran only their own
condition and could not say what a court would have done with the same
weeks. Either verdict retires an argument we are currently having on
vibes.
