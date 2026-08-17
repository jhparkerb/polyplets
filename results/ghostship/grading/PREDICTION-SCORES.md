# Ghost Ship — sealed predictions scored against the graded record

Scored 2026-08-15 by a grading agent, against
`grading/CLAIM-TABLE.md` (consolidated verdict) with per-claim evidence from
`verify-A.md`, `verify-B.md`, `verify-C.md`. Authorship of both forecasts was
stripped before scoring and is not discussed here.

Grades: **HIT** — the call's stated quantity or outcome matches the record.
**PARTIAL** — one half of a compound call holds, or the direction is right and
the magnitude/grade is wrong. **MISS** — the record contradicts it.
**UNFALSIFIABLE** — the record cannot decide it, either because the call is
too vague or because the instrument to measure it does not exist.

---

## Prediction A

| # | call | quote (short) | measured outcome | grade |
|---|---|---|---|---|
| A1 | Highest rung and when | "we will reach rung 3 handily … Rung 3 first reached at **session 10**" | Rung 3 NOT REACHED; rung 2 NOT REACHED (A187077 appears nowhere in the run). Highest rung **1 of 3, at session 1**. | MISS |
| A2 | Token burn from redundant exploration | "we'll burn a lot more token and re-exploration of dead ends … explore the space more thoroughly and redundantly" | Loop raw tokens **91.13M vs court 123.18M** — fewer, not more. Cost-weighted **$225.20 vs ≈$140** — 1.6× higher. Direction right on dollars, wrong on tokens, and the mechanism (dead-end re-exploration) is not what drove the spikes: per-session totals track compute-heavy sessions s09/s12/s13, with no context-growth signature. | PARTIAL |
| A3 | Claim hygiene | "FALSE + UNFALSIFIABLE over the 20% verdict line — let's shoot for 33%" | **FALSE 0, UNFALSIFIABLE 0** of 64 claim lines (0%). One VACUOUS (s13.c6), one READ-OFF sub-clause (s04.c4). | MISS |
| A4 | Unwitting re-derivations | "**seven** unwitting restatements of banked slice content" | **0 unwitting.** Two witting/flagged: s01.v1 (labeled verification act) and s04.c4's READ-OFF sub-clause. | MISS |
| A5 | Judgment failures | "absolutely 3 or more identical failures, probably chasing OEIS phantoms" | **0 POSITIVE** under the rubric. The named mechanism was not a phantom chase: the OEIS *search endpoint* was Cloudflare-blocked (4 attempts, s06–s07), graded NEGATIVE as instrument error with a b-file workaround found and reused. The one 3-instance cluster that did occur (session-boundary job handoff, s11–s14) fails on count-of-identical and on recognition-on-record. | MISS |
| A6 | Operator uses the bulletin | "I can certainly try [to write bulletin notes]" | Bulletin read "(no operator notes yet)" in **all 14 prompts**; steering **0 min** self-reported. No edit was attempted. | MISS |
| A7 | Q2 outcome | scored as "Q2 outcome LIVE-but-weak or NOT TESTED" | **Q2 = NOT TESTED** per §1. Call holds, but it is a disjunction spanning two of the three available outcomes and only excludes a strongly-live bulletin — low information. | HIT (weak) |
| A8 | Cost multiple | "**>3×** the court's evening" | $225.20 vs ≈$140 = **1.6×**. | MISS |
| A9 | Coverage vs court | "the loop will do everything the court arm did" — all three rungs | Loop banked 1 of the court's 3 rungs and instead solved a *different* object (directed-convex, s03: A014300/A112029). It also produced 58 VE claims of out-of-scope moment/asymptotic work the court never touched — different coverage, not superset. | MISS |

**Tally A: H 1 / P 1 / M 7 / U 0** (9 calls).

---

## Prediction B

| # | call | quote (short) | measured outcome | grade |
|---|---|---|---|---|
| B1 | Rung 1 timing | "Rung 1 by session 3 … a fresh reader acts on [the on-disk hint] early" | **Rung 1 REACHED at session 01** (s01.c1, ~19 min claude time), explicitly acting on the on-disk hint as the key scopes it. Inside the stated bound. | HIT |
| B2 | Rung 2 timing | "Rung 2 first reached at session 8–10 … **Final: rung 2, first reached around session 9**" | **Rung 2 NOT REACHED.** No session addressed the column-convex subfamily. | MISS |
| B3 | Rung 3 | "Rung 3 NOT reached" | **NOT REACHED.** (The stated reason — distrusting an OEIS comment, building a cross-lattice control — went untested, since rung 2 never landed.) | HIT |
| B4 | CLAIM rate | "mean ≈ 2.5/session after re-graining (range 0–5)" | 64 CLAIM lines / 14 sessions = **4.57 mean** (5.33 over the 12 claim-bearing sessions); range **0–7** (s02 and s05 each carry 7). Re-graining was checked by the grader and moved no count by more than ±1. | MISS |
| B5 | Bucket shares | "READ-OFF ≈ 15%, VACUOUS ≈ 10%, FALSE + UNFALSIFIABLE ≈ 15%" | READ-OFF: 1 sub-clause, no whole claim. VACUOUS **1/64 = 1.6%**. FALSE+UNF **0%**. Every share overshot by roughly an order of magnitude, and the DID-WELL threshold was cleared, not grazed. | MISS |
| B6 | Self-caught | "≥ 1 SELF-CAUGHT instance across the run" | **Two**: s06.c5 (zero census corrected, 12 missed zeros vs s05) and s12.c3 (s10/s11 factorization shape REFUTED for r≥2). | HIT |
| B7 | Verification shape | "VERIFY lines present in ≥ 5 sessions, but execution-backed in only 3–4; second-reading verification will dominate late sessions" | 31 VERIFY lines, **30 SOUND, 1 UNSOUND** (s13.v3, the run's only receipt-discipline failure); claims verified **by execution 58, by reading 5**. Presence half holds and then some; the execution-scarcity and late-reading-dominance half is contradicted — the two heaviest execution sessions are s12 and s13. | PARTIAL |
| B8 | Re-derivations | "exactly 2 … one early session restates the Convex Mirage … one restates the μ ≈ 3.129 landscape" | **0 unwitting.** Both named topics did surface, but neither as a re-derivation: the mirage appears as s04.c4's READ-OFF sub-clause (corpus states it), and μ was *sharpened* to an exact characterization plus 44 certified digits — recorded as beyond the banked claim, not a restatement of it. Right topics, wrong count and wrong kind. | PARTIAL |
| B9 | Failure mode 1 (area chase) | "≥ 3 same-shaped attempts at the *area* statistic … spread across sessions 3–9, despite the slice saying area is a mirage" | The run's center of mass *did* move to area from s04 on — the drift was called correctly, and at nearly the right session. But it was productive, not a failure: 58 VE claims came out of that territory, and it graded as ordinary out-of-scope work, not a judgment failure (0 POSITIVE overall). | PARTIAL |
| B10 | Failure mode 2 (decay) | "at least one tentative→firm laundering survives to the final report (1-of-3 to 1-of-5 enrolled caveats lost)" | **0/4 losses** in later reports, the metric's own denominator. The footnote records s07.c6's fill-ratio claim propagating unqualified into two *same-session* results docs — against the metric's spirit, inside its letter, and not into a final report. | PARTIAL |
| B11 | Failure mode 3 (genre drift) | "by session 10+, LOG sections turn retrospective … DIRECTION lines converge to near-copies of the predecessor's OPEN line" | DIRECTION half corroborated: predecessor-OPEN is the direction source in **11 of 14** sessions, and verify-C shows s11 quoting predecessor OPEN lines near-verbatim. Retrospection half contradicted: s12 refuted a standing conjecture, s13 derived the c_r local transfer, s14 adjudicated r=7 at 96/96 and registered r=8. | PARTIAL |
| B12 | Bulletin / Q2 | "Operator edits ~3 times; bulletin-sourced direction in ≥ 2 sessions → **Q2 = LIVE**" | Bulletin untouched in all 14 prompts, steering 0 min, bulletin-sourced direction **0** sessions, **Q2 = NOT TESTED**. | MISS |
| B13 | Cost multiple | "cost-weighted tokens ≥ 15× the court's … tokens-per-rung ≥ 20× court" | **1.6×** cost-weighted ($225.20 vs ≈$140); raw tokens *below* court (91.13M vs 123.18M). Per rung: 1 rung vs court's 3 gives ≈4.8× cost-per-rung, still far short of 20×. | MISS |
| B14 | Reading-curve shape | "Mandatory CARRY reads grow linearly and stay minor; elective LOG reading decays to near-zero by session 8" | The three-curve split is **NOT RECOVERABLE** from the banked usage records (launcher stored per-session totals only) — Q3 reports the instrumentation gap. The only decidable fragment is that there is no monotone context-growth signature, which is consistent with but does not confirm either curve. | UNFALSIFIABLE |
| B15 | What the court does better | "Rung 3, and the 9.3153→9.3154 catch" | Both items were indeed left unclaimed by the loop: rung 3 NOT REACHED, and "Nobody touched the λ ≤ 9.3153 rounding (grader-note opportunity unclaimed)". The comparative half — that the court *would* have caught them — is a counterfactual the record cannot test. | PARTIAL |
| B16 | Loop's advantage | "session 1–2 freshness acts on the on-disk perimeter hint without the court's sunk attachment to the area statistic" | Rung 1 landed at **session 1** precisely by acting on the on-disk hint, with the statistic switched to semiperimeter in that session. | HIT |

**Tally B: H 4 / P 6 / M 5 / U 1** (16 calls).

---

## Comparison

B tracked the record better, and the gap is widest on the calls that carried
the most weight.

**Rungs.** B got the two ends right — rung 1 early off the on-disk hint (B1,
B16, both HIT at an even earlier session than predicted) and rung 3 never
(B3) — and missed only the middle (B2). A staked its headline on rung 3 at
session 10 and on the loop reproducing the court's full ladder (A1, A9), both
MISS; the loop reached one rung of three.

**Magnitudes.** Both forecasts overshot pathology and cost, A by more. On
claim hygiene A predicted 20–33% FALSE+UNFALSIFIABLE against a measured 0%
(A3), and 7 unwitting re-derivations against 0 (A4); B's 15%/10%/15% bucket
shares (B5) and its count of 2 re-derivations (B8) were wrong in the same
direction but by less, and B at least named the two banked topics that
actually surfaced. On cost, A's >3× (A8) and B's ≥15× (B13) bracket a measured
1.6×; A is the closer number, and it is the only dimension where A wins.

**Failure modes.** Neither predicted the failure shape that the record
actually flags. A's named mechanism (chasing OEIS phantoms) inverts what
happened — the OEIS *instrument* broke and the loop routed around it via
b-files (A5). B's area-drift call (B9) identified the right movement at
roughly the right session and mis-graded its consequence. The structural cost
the record does name — session-boundary job handoff, 3 instances across
s11–s14 — appears in neither file.

**Bulletin.** Both were wrong about operator behaviour, in opposite ways: B
predicted ~3 edits and Q2 LIVE (B12, MISS), A predicted an attempt that would
carry little (A6, MISS). A's scored disjunction happens to contain the
measured NOT TESTED (A7), but it excludes only one of three outcomes and
should not be read as a strong call.

**Falsifiability.** B is the more testable document: 16 extractable calls,
only one undecidable, and that one undecidable because the instrument was
never built (B14) rather than because the language was loose. A's nine calls
are mostly crisp numbers, but two of them (A2's "a lot more token", A7's
two-way disjunction) resolve only by charity or by fiat.
