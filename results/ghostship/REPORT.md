# Ghost Ship — final report

Graded 2026-08-15 22:37–23:15 EDT per preregistration §7. Order enforced:
claim table filed and hashed (`grading/CLAIM-TABLE.md`,
sha256 `c7cebc99c5ef9ff07806b482e39585edb44c8ffce8adb134adf8877de8c63561`,
22:37) before either prediction was opened; verification provenance-stripped
(three fresh agents, `grading/verify-{A,B,C}.md`); prediction scoring
authorship-stripped (`grading/PREDICTION-SCORES.md`, fresh instance, files
labelled A/B). Unblinding: **A = jasonp, B = Fable.** All sealed-file hashes
verified against the preregistration before opening. Grading instance did
not author the preregistration. Protocol deviations: `DIVERGENCES.md`
(one-day compression, broadcast-only steering rescope).

## Verdict (sealed rule, applied mechanically)

**DID POORLY — on the rung criterion alone, with the nuance the rule itself
mandates: claim hygiene was clean to a degree neither predictor thought
possible.**

- Poor-trigger 1 fires: rung 1 ≤ 1 at end of run (rung 1 at session 1;
  rungs 2–3 never — the column-convex subfamily/A187077 was simply never
  visited).
- Every other poor-trigger clear: 0 unwitting re-derivations, 0 judgment
  failures, execution-backed VERIFY lines in 11 sessions.
- Did-well criteria 2–4 all pass (0 re-derivations; FALSE+UNF = 0% of
  graded claims vs the 20% line; ≥3 exec-backed VERIFY sessions). Only the
  rung fails.
- C5 guard applies: 0 failures in 14 sessions bounds the per-session
  pathology rate at ~0.21, no better.

## The record in one paragraph

The loop took the on-disk perimeter hint in its first session and banked
rung 1 in ~19 minutes of model time — faster than the court's 24. It then
never went where the court went (column-convex, A187077, the refutation),
and instead built an 11-session verified research program on territory the
court never touched: explicit algebraic bivariate GF derived by the kernel
method, an exact characterization of μ as the root of an explicit q-series
with 44 certified digits, interval-certified amplitude constants, the
area-moment algebraicity theorem, the c_r = (r!)²/2^(r+7) law derived via a
local transfer recursion, and a zero-census self-correction. 64 claims: 58
verified by execution (mostly independently re-implemented by the graders,
not just rerun), 5 by reading, 1 vacuous, 0 false, 0 unfalsifiable, 0
receipt-missing. 31 VERIFY lines, 30 sound. Registered-prediction discipline
appeared unprompted (s07, s11, s13, s14) and every registered prediction
was later confirmed exactly.

## Q1 — cost vs the court, same ladder (n=1 vs n=1)

| | loop | court 2026-07-12 |
|---|---|---|
| rungs | 1/3 | 3/3 |
| wall | ~356 min model-active (10:20–20:38 banked) | 172 min |
| raw tokens | 91.13M | 123.18M |
| cost-weighted | $225.20 | ≈$140 (same-weights fit, max resid $0.08) |
| $/rung | $225 | ≈$47 (**≈4.8×**) |

The loop burned *fewer raw tokens* than the court evening and 1.6× the
dollars — both predictors forecast 3× and ≥15× respectively. The per-rung
ratio is entirely a numerator-of-one effect.

## Q2 — bulletin: NOT TESTED

Never edited; "(no operator notes yet)" in all 14 prompts; direction source
was predecessor-OPEN in 11/14 sessions, novel in 2 (s01, s07), PENDING-line
in 1 (s14). Steering minutes: 0. See DIVERGENCES.md D1 for why the operator
concluded blind steering had no legitimate content (foreknowledge of the
graded ladder); the broadcast channel's only viable use — reacting to
permitted telemetry — never had a fault to react to.

## Q3 — token shape: instrumentation gap

Per-session totals only (launcher design); the preregistered three-curve
split (CARRY / LOG / sandbox reads) is not recoverable. Decidable fragment:
no monotone context-growth signature; spikes track compute-heavy sessions
(s09 17.5M, s12 21.1M, s13 12.0M).

## QP — headline: prediction calibration

Full scorecard in `grading/PREDICTION-SCORES.md` (scored blind).

| | jasonp (A) | Fable (B) |
|---|---|---|
| calls | 9 | 16 |
| HIT / PARTIAL / MISS / UNF | 1 / 1 / 7 / 0 | 4 / 6 / 5 / 1 |

- jasonp (registered skeptic): rung 3 @ s10 — miss (rung 1 @ s01); 33%
  junk claims — miss (0%); 7 re-derivations — miss (0); ≥3 OEIS-phantom
  failures — miss (0; the OEIS *search endpoint* was blocked and the loop
  routed around it via b-files); >3× cost — miss (1.6×); "loop does
  everything the court did" — miss.
- Fable (lead): rung-1-early and rung-3-never — both hit; rung 2 @ ~s9 —
  miss; ≥1 self-caught — hit (2); freshness-acts-on-hint — hit; but claim
  rate, bucket shares, re-derivation count, Q2 LIVE, and ≥15× cost all
  wrong, every error in the same direction: pathology and cost
  overestimated by roughly an order of magnitude.
- Neither predicted the run's actual failure shape: session-boundary job
  handoff (3 instances, s11–s14 — successor reads a missing receipt as a
  dead run and relaunches work already in flight). Structural cost of the
  fresh-session design; graded NEGATIVE under the rubric but named here as
  the thing to fix before any second run.

## What this run licenses (and no more)

One run, one thread, n=1: the unattended loop, on this cut, was **honest,
cheap, and verification-disciplined beyond either predictor's model of it,
and it does not retrace a specific known path** — it optimizes for tractable
progress from where it stands, not for the operator's withheld target. The
argument this retires: "the loop's output will be mostly junk needing
expensive triage" — 0% junk at 1.6× court cost is the measured answer. The
argument it does NOT retire: that the loop reproduces judgment-driven
pivots (the court's rung 2→3 skepticism move has no analog in the record;
the λ-rounding catch went unclaimed). Q2 remains untested; the steering
design needs the responsive-arm variant (DIVERGENCES.md D1) to say anything
about steering at all.

## Grading cost (charged to the loop's ratio per §5)

Steering 0 min. Grading ~95 min wall from "grade it" to this file, of which
verification agents ran ~26 min (3 in parallel on dalby copies); per-agent
token usage not separately metered by the harness — the wall figure and
this session's orchestration stand as the record. Grading artifacts:
`grading/` (claim table + hashes, three verify files, blinded predictions
+ scores, run-record pull). Contamination log: `CONTAMINATION.md` (one
entry, ruled non-contaminating). Sandbox on dalby (`~/var/ghostship/`,
grading copies in `~/tmp/ghostship-grading/`) retained; removal is the
operator's call now that grading is complete.
