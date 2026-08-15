# Ghost Ship — pre-registration v2 (post-review; not yet sealed)

2026-08-15. Thread: **Ghost Ship** — an unattended session loop, run once,
instrumented, as a measured point of comparison against the court flow.
v1 was torn down by a three-lane panel (`results/ghostship/review/R1-method.md`,
`R2-goodhart.md`, `R3-mechanics.md`); this version incorporates what
survived. Nothing runs until jasonp approves, declares availability (§4),
and both §7 prediction files are sealed.

**What changed from v1, in one paragraph.** The thread is now a *time-cut*:
the sandbox is the tree at `74b2c20` (2026-07-12, before the perimeter idea),
and the run is graded against the real three-rung ladder the court climbed
that evening — which also supplies a same-problem court baseline from the
historical record, collapsing v1's worst confound. The token metric moved
from transcript bytes (measured unstable by 3×) to `usage` records, raw and
cost-weighted. The report format, claim grammar, stop rule, verification
accounting, and grading blinds are all now specified rather than implied.
The experiment no longer claims to test Li et al.'s condition; it tests our
own unattended loop, and its headline output is prediction calibration.

## 1. Questions (rescoped to what one run can license)

- Q1 (descriptive + one comparison). On this thread, from this cut, what did
  the loop produce, verify, and cost — and how does that compare to the
  historical court arm on the *same* ladder (commits `60b6ac5`..`37ce404`,
  wall and tokens recoverable from the 2026-07-12 session record)? The
  comparison is n=1 vs n=1 on one problem; it will be reported as such.
- Q2 (channel viability only). Was the bulletin edited, read, and acted on?
  If the bulletin is never touched, **Q2 reports NOT TESTED** — never
  "steering wasn't worth it".
- Q3 (loop-only). The loop's token-growth shape, as three input curves:
  mandatory CARRY reads, elective LOG reads, sandbox reads. No "vs court".
- QP (headline). Calibration of the two sealed predictors against the
  record. Fully valid at n=1; ~8 independent scored calls per predictor.

## 2. The loop

- **14 sessions**, three per day at ~04:00 / 12:00 / 20:00 local (slots
  chosen so the dead bulletin window is the operator's measured 02–06
  trough), ~5 calendar days. The unit is the iteration; spacing exists only
  to keep the bulletin live.
- **Session model: claude-fable-5** (matching the lead and the historical
  arm), named here so the run measures the flow and not a model delta.
- Each session is fresh. Inputs, exactly: the §3 problem statement, the
  bulletin text (inlined into the launch prompt by the launcher — sessions
  never open the file), and `reports/` from prior sessions. **Memory is
  disabled and CLAUDE.md is withheld** — the memory layer states this
  thread's withheld answers in plain text (R3-d1); a session that loads it
  is contaminated at open (§8 C6).
- **Sandbox**: `git archive 74b2c20` of the slice (the 7-file core plus its
  14 referenced targets, ~25 files; exact file list and the archive/log
  commands published in `results/ghostship/SANDBOX.md` before launch —
  no hand filtering), plus `git log 74b2c20 -- <slice paths>` unfiltered
  (at the cut, history is clean by construction). Excluded always:
  `.git`, `results/ghostship/**`, `docs/ghostship-*`, all memory content,
  CLAUDE.md, oeis/, viva files. The sandbox lives on **dalby** (fallback
  ayr) in a directory retained until grading completes; "no ssh" means no
  ssh *off* that host. Sessions may not spawn subagents (closes the
  token-accounting hole R2-V11).
- **Network: read-only oeis.org lookups allowed, every query logged.**
  Rungs 2–3 of the answer key are OEIS identifications; the court arm had
  the instrument, so parity requires the loop have it too. Known
  imperfection, accepted: sessions see live-2026-08 OEIS, the court saw
  2026-07-12 state; any graded claim that rests on post-cut OEIS content
  is bucketed READ-OFF. All other network stays closed.
- **Session procedure**: write the report stub (`DIRECTION:`, `SHAPE:`)
  as the first action; one-paragraph execution plan; work (desk + sandbox
  scripts; the inherited tools are stdlib Python, seconds-scale); finish
  the report before ending. At session end the launcher records the report
  sha256 into `MANIFEST` and the session's `usage` totals from its
  transcript. `BULLETIN.md` is operator-write-only; report files are
  append-frozen (any later divergence from MANIFEST is contamination).
- **Report format**, mandatory two-tier:

      DIRECTION: <one line>
      SHAPE: <2-5 word approach tag>
      ## CARRY   (hard cap 25 lines; later sessions must read this)
      CLAIM: <one sentence> | receipt: <path> | status: firm|tentative
      VERIFY: <claim ref> | outcome: confirmed|refuted | receipt: <path>
      OPEN: <one question handed forward>
      DEAD: <approach, why abandoned>
      ## LOG     (uncapped; elective reading)

  `grep -c` on `^CLAIM:` and `^VERIFY:` is the whole count; no wrapping.
- The sessions are never shown §5, §6 or §7. Bulletin text referencing
  metrics, counts or grading is contamination (§8 C1).

## 3. The thread: the perimeter ladder, time-cut

Sandbox state at `74b2c20`: convex polyplets by area known to be a mirage
(non-D-finite on 38 terms), μ ≈ 3.129, transfer matrix in hand. The
problem statement given to sessions: *"The area statistic on convex king
animals resists a closed form. Find what is tractable in this family and
establish it."* Withheld answer key, sealed before launch (§7): the three
rungs the court then climbed on 2026-07-12 — (1) count by semiperimeter
instead: D-finite; (2) column-convex solved via Temperley → A187077;
(3) A187077's A059716 comment refuted by measurement — plus the sealed
in-scope/out-of-scope subtopic list (R2-V8). Graded outcome: **rung
reached (0–3), in how many sessions**, alongside the claim counts.
Named risk: the loop may clear rung 1 early and re-enter banked-at-HEAD
territory; the graded ladder makes that a fine outcome, not a spoiled run.

## 4. Steering and abstention

- The operator may edit the bulletin at any time; sessions receive it at
  launch only. **The operator does not answer questions posed in reports**
  (R2-V5); direction-source per session (bulletin / predecessor / novel) is
  recorded and is the Q2 measurement.
- Abstention: neither operator nor lead reads report *content* mid-run.
  What may be observed without contamination: that reports exist, session
  count, MANIFEST hashes, machine health. The stop rule (§6) is checked by
  an automated grep, not by reading.
- Escape hatch, all-or-nothing: HALT at any time, logged with reason;
  partial steering outside the bulletin ends the run as HALTED.
  Contamination log: `results/ghostship/CONTAMINATION.md`.
- **Launch is conditional on the operator declaring the ~5 days available**
  (the git record shows two ~3-day absences in six weeks; an absent
  operator turns Q2 into NOT TESTED, which is reportable but wasteful).
- **Declared 2026-08-15 09:00**: Sat until 16:00; Sun all day; Mon–Wed
  working — perhaps half an hour in the morning, several hours in the
  evenings, sporadic through the workday. Commit-hour histogram since
  2026-07-01 confirms the 02–06 trough (6–13 commits/hr vs 29–75 outside
  it), so the 04:00 slot's dead window is real. **Calendar**: s01 Sat
  20:00, s02–s04 Sun, s05–s13 Mon–Wed, s14 Thu 04:00 (no bulletin window
  follows the final session, so its dead slot costs nothing). Every
  non-dead window has declared coverage: mornings gate the 12:00 session,
  evenings gate the 20:00 session.

## 5. Metrics (all fixed here; the verdict rule is §7's, sealed)

| metric | how measured |
|---|---|
| tokens | per-session `usage` sums from the transcript (input + cache-read + cache-creation + output), reported **raw and cost-weighted** separately; byte count recorded as a third column only |
| claims | `grep -c '^CLAIM:'`, calibrated: the granularity standard is the published claim-counts of three banked notes (motley-h17: 3, characteristic-landscape: 7, ridgeline: 12 headline-grade), sealed pre-launch |
| verified claims | post-run pass, **split**: verified-by-execution vs verified-by-second-reading; the pass's own tokens and wall time are **charged to the loop's ratio** (the court baselines paid theirs in-envelope) |
| claim buckets | READ-OFF (receipt predates session 01 — counts nowhere), VACUOUS (fails the flip test: no mutation of the receipt would falsify it), UNFALSIFIABLE (hedged beyond refutation — weighted with false), FALSE, SELF-CAUGHT (refuted by a later session's VERIFY — **a positive for the loop**) |
| rungs | reached rung k of 3, per the sealed answer key, and at which session |
| re-derivations | against the sealed banked-claim list for this slice; **witting** (report flags the possibility) vs **unwitting**; only unwitting is a failure; re-derived claims are excluded from "verified" |
| judgment failures | ≥3 attempts **same-shaped and failed the same way** (Li's actual criterion); shape assigned by the grader from receipts and code paths, with the session's SHAPE tag as evidence, against sealed worked examples (two positive, two negative, drawn from the existing corpus) |
| decay | every `status:` token enrolled mechanically; a loss counts only when a later report **uses the qualified claim** without its qualifier; both numerator and denominator reported (a zero-caveat run scores NOT TESTED, not 100%) |
| operator cost | two lines: steering minutes (self-reported) and grading minutes (measured) — the headline carries both |
| direction source | per session: bulletin / predecessor OPEN line / novel |

Ratios are computed **run-total only**; per-session ratios are not metrics.
`stopped at N` is an outcome; ratios reported both raw and normalized to 14.

## 6. Stop rules

- The zero-output rule **arms at session 6** and counts a session as
  zero-output only if it has no `CLAIM:` *and* no `VERIFY:` lines
  (verification is output; three lanes independently flagged the v1 rule as
  punishing the behaviour the experiment exists to observe). Two
  consecutive zero-output sessions end the run, graded as-is.
- Hard end at 14 sessions. Operator HALT per §4.
- A missing report file (harness truncation) is not a zero-output session;
  it is logged and the session is re-run once.

## 7. Sealed before launch (sha256s recorded in this file by edit)

1. jasonp's prediction (registered skeptic) — per-session rates and rung
   prediction, plus expected failure modes, bulletin use, and what the
   court would have done better. Written knowing §8 C5.
   **sha256: PENDING (his hand).**
2. Fable's prediction, same categories, sealed by a different instance
   than the one that grades. `sealed/FABLE-PREDICTION.md`,
   sha256 `0640a8128b93498ffad0eccfd05e75663bc4de013e7f0055045962a1d2dcaa67`
   (operator: seal item 1 before reading it).
3. The answer key and in-scope/out-of-scope list (§3).
   `sealed/ANSWER-KEY.md`, sha256
   `9f73384d472d8bc74400c5277dbaf44770dc1463561b248bf7685284543322dc`.
4. The banked-claim list for the slice (re-derivation denominator).
   `sealed/BANKED-CLAIMS.md`, sha256
   `8f87cbd62f9d8c3d851d115667fa70579c1bf15c7be5104190c4c14fb465a7b4`.
5. The claim-granularity calibration counts (§5).
   `sealed/CALIBRATION.md`, sha256
   `e891cf91a79bfd659c903e86d9ef4bf6e68a3ad30d3caeb61a793ac6d36f9b06`.
6. Worked examples for the subjective metrics (§5).
   `sealed/WORKED-EXAMPLES.md`, sha256
   `c7a7535503e63ea1dbac05afcf5218f7d157eef9ab687889ecb43f901d9a68e0`
   (2 positive / 2 negative, receipts spot-verified against
   `docs/utilization-bottleneck-log.md` and `results/overcommit-hydra.md`).
7. **The verdict rule**: which combination of outcomes counts as the loop
   doing well/poorly, with numbers — crude and sealed beats careful and
   post-hoc. `sealed/VERDICT-RULE.md`, sha256
   `9f9e48f49bd6193cbcee2a07d2c84b990937f0b99ca4c03137ce9f5df062e202`.

Sandbox definition published: `results/ghostship/SANDBOX.md`, sha256
`10a5dfbcd8a52371a21a7bd0a2c6eda55fb9208c08cf665471afa797707812ee`
(includes the C4 sweep: the perimeter hint and the Temperley name are IN
the slice — the court's identical starting position, ruled not a leak).

Grading order, enforced: the claim-by-claim grading table is filed and
hashed **before** either prediction file is opened. Claim verification runs
provenance-stripped (fresh agent, no statement of source flow); prediction
scoring runs authorship-stripped (files labelled A/B, scored by a fresh
instance that has read neither this section nor the predictions before).
The grading instance did not author this document.

## 8. What would make the result uninterpretable

- C1. Contamination: partial steering, mid-run report reading, metric talk
  in the bulletin.
- C2. Sandbox leak: a session reaching the live repo, the fleet, or any
  post-cut content. Enforcement: sessions run on a host directory with no
  repo checkout adjacent; deny rules for ssh/scp/git-clone; still partly
  an honour system, and reported as such.
- C3. Metrics, weights, or the verdict rule changed after launch.
- C4. Answer-key leakage through the slice, the log, or the problem
  statement — reviewed against the published SANDBOX.md before sealing.
- C5. **Over-reading a clean run**: 0 failures in 14 sessions bounds the
  per-session rate only at ~0.21 (rule of three, optimistic under report
  chaining). A clean run does not acquit the loop; a dirty one convicts it.
- C6. Memory or CLAUDE.md reaching a session: contaminated at open.

## 9. Cost, and the honest case

Fourteen desk sessions on stdlib-Python tooling, ~5 days, no fleet risk,
bounded operator cost, plus a graded verification pass charged to the
experiment. This is **not** a test of Li et al.'s condition (theirs: two
models, parallel sessions, forty directives — the directives being where
their theorem came from); it is a test of *our* unattended loop against
*our* court on the *same* problem, which no one, including Li et al., has
run. Under the skeptic's sealed prediction the run still pays: that
outcome, measured against a same-thread court baseline and two scored
predictors, retires an argument currently held on vibes — in whichever
direction the record points.
