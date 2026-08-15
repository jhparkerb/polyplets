# R3 — mechanics and the C4 check

Lane R3 of the Ghost Ship panel, 2026-08-15. Desk only; nothing was executed
beyond reads, greps and `git log`. Object under review:
`docs/ghostship-preregistration.md`.

Headline: **§3's thread choice fails C4**, but not in either of the two ways
§8 anticipates — it fails *both at once*, and the failure is repairable
without changing threads by cutting the corpus at a git date instead of at a
file boundary. The sandbox as specified is not self-contained (45 files, 77
dangling references), and the largest contamination channel in the protocol
is one nobody named: the agent memory directory, which is loaded into every
session by default and states the thread's banked answer in plain text.

---

## (a) C4: is Convex Polyplets the right thread?

### Verdict: no, as scoped. Both horns at once.

The pre-registration wants a thread that is simultaneously (i) rich enough in
banked state that re-derivation is *detectable*, and (ii) open enough that
real progress is *available*. In this repo those two properties are
anti-correlated — a thread is thoroughly banked precisely because it was
tractable, so its residue is the intractable part. Convex Polyplets is the
extreme case of that anti-correlation, not an exception to it.

**What is banked.** `results/convex-polyplets.md` is 620 lines. Read with
`docs/proofs/convex-mirage.md` and `results/middle-kingdom.md`, the thread
already contains: the area series to n=700 (king and the A067675 control);
non-D-finite and non-algebraic exclusions at order ≤24 / degree ≤24, by a
mod-p rank argument that is rigorous over Q, with four RED-first controls;
the semiperimeter series to s=200 and its order-5 degree-2 P-recurrence on a
172-row holdout; the unrestricted semiperimeter GF proved algebraic of degree
2 in box (2,9); the (dir4, HV-convex) GF proved algebraic of degree 4 in box
(4,22), exact over Q, with the nullity law measured cell-for-cell against
prediction; µ to 199 trusted digits, θ=0, the amplitude to 40 digits; PSLQ
negative in every box the precision supports; the column-convex GF solved by
Temperley and identified as A187077, with a measured refutation of that
entry's A059716 comment and a drafted correction. Two gates pin it
(`gate-convex-dfinite`, `gate-dir4-perim-alg`).

**What is left.** I walked the open lists in `results/middle-kingdom.md` §Open
and `docs/proofs/convex-mirage.md`. The entire residue is:

1. *Proofs* of the non-D-finiteness that is currently a box exclusion. Open
   in the literature for the polyomino control too. Not a 14-desk-session
   target by any reading.
2. `build/convex_perim_tm 206 1 dir4` — the out-of-sample enumerator run the
   note itself prices at ~21 minutes and marks "Not run here."
3. ctrlB × column-convex at n=400 — 11 minutes, 4 GB, priced in
   `results/middle-kingdom.md:144`, with the note "Not run — no current claim
   needs it."

Items 2 and 3 are not research; they are *running a command that is already
written down in the note*, and both are compute the sandbox's spirit excludes.
Item 1 is a wall. **There is no rung at the difficulty band the experiment
needs.** A session that wants a claim line has exactly one cheap move
available — restate banked material with a receipt path that genuinely
resolves — and exactly one honest move that scores zero. That gradient is
built into the thread, which is what C4 forbids: the choice predetermines the
verdict, in the skeptic's favour.

**On the other side, the detectability premise is sound and I can evidence it.**
The re-derivation failure mode is not hypothetical for this thread — it has
already happened once, to a fresh session working from a partial view, and it
is recorded: `results/convex-polyplets.md:8` ("**Integration correction:**
convex polyplets were already investigated, more thoroughly, in
`docs/proofs/convex-mirage.md`… This note re-derived a subset of that"). So
§3's claim that re-derivation is detectable here is correct and has a
precedent. The problem is difficulty, not detectability.

### The slice does not rescue it — it forks the failure

§2 says the sandbox is a *slice*, so one might argue the sessions never see
the banked state and therefore face a real problem. That splits into two
designs and both are broken:

- **Slice = current state.** Nothing to do but paraphrase (item 1 is a wall,
  items 2–3 are banned compute). Fails as above.
- **Slice = state with the results cut out.** Every achievable result is then
  banked-but-withheld, so *every* claim the loop can produce is a
  re-derivation by construction. The re-derivation metric — the skeptic's
  headline predicted failure — goes to 100% mechanically and stops carrying
  any information. And what gets measured is reproduction speed, which is not
  what Q1 asks and is not what the king-twigs/Offside baselines measured.

### The fix, and it keeps the thread: cut the corpus at a git date

Make the slice a **time cut**, not a file selection. Export the tree at
`74b2c20` (2026-07-12 17:59, "tool(convex): restore lost 38-term transfer
matrix"). At that commit the thread's state is: area is a known mirage,
non-D-finite on 38 terms, µ≈3.129, transfer matrix in hand — and the
perimeter idea has not been had.

What actually happened next is a dated ladder of desk-sized rungs, each with a
recorded court wall-time:

| commit | when | what | court cost from previous |
|---|---|---|---|
| `74b2c20` | 07-12 17:59 | (cut point) | — |
| `60b6ac5` | 07-12 18:23 | by perimeter, king convex polyplets are D-finite | 24 min |
| `3afca73` | 07-12 19:24 | column-convex solved via Temperley → A187077 | 61 min |
| `37ce404` | 07-12 20:51 | the A187077/A059716 comment refuted by measurement | 87 min |

This design fixes every objection above at once:

- **Real rungs exist at the right difficulty**, demonstrably — the court
  cleared three of them in under three hours of one evening.
- **Re-derivation becomes the measurement rather than a tautology.** A loop
  that reaches rung 1 has produced a checkable hit against a withheld answer;
  a loop that produces area-flavoured prose for 14 sessions is a clean
  negative. Either way it grades itself.
- **The comparison stops being apples-to-oranges.** Q1's per-token comparison
  currently pits the loop against king twigs and Offside on *different
  problems*. Here the court's own token spend on *this* ladder is recoverable
  from the session record, and the loop runs the identical problem. That is
  the strongest baseline available anywhere in this repo and it costs nothing
  to adopt.
- **Rung 1 is a judgment call, not a grind** — "stop counting by area, count
  by semiperimeter" is exactly the direction-choosing capability the
  experiment claims to be testing.
- **The git-log filtering problem solves itself** (see (b)).

Sealed predictions in §7 get sharper too: predict the rung reached, not a raw
claim count.

Risk to name honestly: the loop may reach rung 1 in session 2 and then be back
in banked-answer territory by session 5. Mitigation is already in the design —
the ladder has three rungs, and the run has a natural graded outcome
("reached rung k of 3 in N sessions") that a flat claim count does not.

---

## (b) The sandbox: file list, exclusions, self-containment

### Self-containment of the as-written slice: fails, measured

Following file references transitively out of `results/convex-polyplets.md`
reaches **438 paths, 126 of them markdown, at depth up to 9**. There is no
natural boundary; the note is a hub into the whole repo.

Cut at depth 1 and you get a 45-file slice with **77 distinct out-of-slice
references**, emitted by 9 of the 45 files:

| file in slice | outbound refs |
|---|---|
| `docs/middle-kingdom-followups-plan.md` | 19 |
| `results/middle-kingdom-phase3.md` | 16 |
| `results/middle-kingdom.md` | 16 |
| `docs/middle-kingdom-plan.md` | 14 |
| `docs/proofs/polyplet-upper-bound.md` | 14 |
| `results/strip-mu-certificates.md` | 10 |
| `results/defect-gas.md` | 9 |
| `results/mk-dir4-perimeter.md` | 6 |
| `results/directed-king-animals.md` | 2 |

Two of those targets are absent from the live repo entirely (`docs/layout.md`,
`results/lifetime3-proof.md` — deleted, still cited), so even a *full-repo*
export leaves dangling pointers. This is the flail-on-missing-files mode the
brief asked me to check, and it is not marginal: 77 dead ends across a 45-file
slice is roughly two per file.

### Self-containment at the proposed cut: passes, measured

Same computation at `74b2c20` over the four-file core plus its markdown
references gives a **7-file slice**:

```
docs/proofs/convex-mirage.md
docs/proofs/polyplet-upper-bound.md
results/convex-polyplets.md
results/defect-gas.md
results/directed-king-animals.md
experiments/convex_polyplets.py
experiments/convex_tm.py
```

**14 out-of-slice references, zero absent from that tree.** An order of
magnitude better on both counts. Ship those 14 targets too if you want zero
dangling refs; the slice is still under 25 files.

### Tool availability

At the cut, both scripts are pure Python 3 standard library — `sys`,
`collections.defaultdict`, and nothing else. No Makefile, no GMP, no `mpmath`,
no `build/`, no `tests/common.py`, no `experiments/seriestools.py`, no data
files. Measured cost of the tool the sessions inherit (from the note's own
table): n=100 in 3.07 s / 17.2 MB, n=200 in 47.9 s / 23.3 MB.

Contrast the HEAD slice, which needs `cpp/obs.h`, `cpp/argparse.h`, the
Makefile (45 gate targets, nearly all referring to files outside any convex
slice), `fixtures/`, GMP with `gmpxx`, `mpmath`, five shell scripts under
`scripts/dir4_perim_*.sh`, and seven `.txt` term files totalling ~310 KB.
`tests/common.py` shells out to `make` by design, so the gates cannot come
without the build system. Shipping a hand-written sandbox Makefile is a
protocol change §2 does not currently authorise.

### Explicit exclusion list

Whatever cut is chosen, these must be kept out or the re-derivation metric is
void:

1. `.git` — already excluded by §2's `git archive`. Also excludes reflog and
   any branch containing later work.
2. **`docs/proofs/convex-mirage.md`'s "Strengthened 2026-08-05" paragraph** if
   shipping HEAD; at the `74b2c20` cut it does not yet exist.
3. `results/middle-kingdom*.md`, `docs/middle-kingdom*.md` — the whole
   campaign index. Absent at the cut.
4. `oeis/`, `results/oeis-candidates.md` — states the sequence is novel and
   worth submitting, which is a conclusion.
5. `docs/viva-*.md` — local-only and never committed, so `git archive` cannot
   export them, but `results/convex-polyplets.md`'s reference closure *does*
   point at `docs/viva-reserve.md` (permission-denied on this machine). If any
   slice is built by copying rather than by `git archive`, that file must be
   named in an exclude list.
6. `CLAUDE.md`, `docs/lean-environment.md`, `docs/job-checklist.md` — operator
   process docs, not corpus.
7. **The agent memory directory.** See (d)-1; this is the important one.

### The filtered git log

At HEAD, "a filtered `git log` file" is a judgment call with no safe setting:
the commit subjects *are* the answers. `221b813` reads "convex: area wild,
perimeter tame -- and it survives directedness"; `53b7afd` reads "criterion:
convexity does not imply a closed form -- rank does, nearly". Filter by path
and you leak; filter by hand and the lead has shaped the sandbox in a way that
is unreviewable after the fact — a C3-adjacent hazard, since it is the grader
doing the shaping.

At `74b2c20`, `git log 74b2c20` is *already* the right log. No filter, no
judgment call, no leak surface. Add `--` path restriction only to keep it
short, and publish the exact command in the protocol so it is reproducible.

---

## (c) Session mechanics

### Report format

Fourteen unstructured reports will not stay readable, and the precedent is
right here: the six Offside lanes ran 343–478 lines each, 2 447 lines for a
single wave. Fourteen at that size is ~5 600 lines, and because each session
reads all predecessors, total reading across the run is quadratic — session 14
alone opens ~5 200 lines before it does anything. That is a mechanical
failure, not an aesthetic one.

Mandate a two-tier report:

```
DIRECTION: <one line>
SHAPE: <2-5 word tag for the approach taken>

## CARRY            (hard cap 25 lines; every later session MUST read this)
CLAIM: <one sentence> | receipt: <path or command> | status: firm|tentative
CLAIM: ...
OPEN: <the one question this session would hand forward>
DEAD: <approach tried, why abandoned>

## LOG              (uncapped; later sessions read it at their discretion)
<narrative, working, failures, everything else>
```

Why each piece:

- **`CLAIM:` as a one-line grammar with a fixed separator.** §5 counts "claim
  lines in reports" — without a grammar, the count is contested and the person
  contesting it is the grader. `grep -c '^CLAIM:'` must be the whole
  measurement. One line, no wrapping.
- **`SHAPE:` tag.** §5's judgment-failure metric is "≥3 same-shaped attempts
  without reframing". "Same-shaped" is unadjudicable post-hoc unless sessions
  declare the shape themselves, in advance of knowing the outcome. Without
  this the metric is the grader's opinion.
- **`status: firm|tentative`.** Feeds the decay metric directly — §5 asks
  whether caveats in report N survive to N+3, and a free-text caveat is
  sampled by hand; a status token is counted.
- **CARRY cap, LOG uncapped.** This is the only shape that does not
  contaminate Q3. A flat length cap would *make* the token-growth answer, and
  Q3 asks what that growth is. With this split, the mandatory reading is
  linear and bounded by construction, and the elective reading is a free
  variable — so instrument input tokens as **three curves** (mandatory carry /
  elective log reads / sandbox reads) rather than one. Q3's real content is
  the elective curve: what a chained loop *chooses* to re-read.

### Write-order rule (fixes a stop-rule failure)

§2 says "write `reports/NN.md` before ending". Make it: **write the stub with
`DIRECTION:` and `SHAPE:` as the session's first action**, then update at the
end. A session that exhausts its budget mid-work otherwise contributes a
missing file, and §6's stop rule ("two consecutive sessions producing zero new
claim lines") then fires on a harness truncation rather than on an exhaustion
of ideas — an early stop that would be scored as a finding about the loop.

Related, and I expect R2 reaches it independently: under a strict
`grep -c '^CLAIM:'` count, a session that spends itself *verifying* a
predecessor's claim produces zero new claim lines, and two such sessions in a
row end the run. Cheapest fix consistent with the grammar: allow
`VERIFY: <claim ref> | outcome: confirmed|refuted | receipt: <path>` to count
as non-zero output for the stop rule while staying out of the claim count.

### 3/day against the operator's real hours

Measured from `git log` (author-local timestamps), 2026-06-15 → 2026-08-14,
1 276 commits:

- Hour histogram is close to uniform. Every hour of the day carries between 42
  and 102 commits **except a single trough at 02:00–06:00** (13, 15, 6, 9
  commits at 02, 03, 04, 05).
- So an 8-hour session spacing leaves a bulletin window overlapping active
  hours almost wherever the slots land. Window *size* is not the binding
  constraint. Place the slots at roughly **04:00 / 12:00 / 20:00** so the one
  unavoidable dead window is the one that was dead anyway.

The real risk is different and the git record shows it plainly. Over
2026-07-01 → 2026-08-14 there are 60 inter-commit gaps of ≥3 h and 38 of ≥6 h
— but also **two gaps of 86.3 h and 69.7 h** (starting 2026-08-02 16:37 and
2026-08-10 16:20). Multi-day absences happen roughly twice in six weeks and
run about three days. A 5-calendar-day run has a material chance of overlapping
one, and if it does, the bulletin goes untouched and Q2 ("is synchronous
steering worth its cost?") gets answered by absence rather than by measurement.

Two one-line protocol additions close it:

- Launch is conditional on the operator declaring the ~5 days available.
- Record bulletin edit count. If the bulletin is never touched, **Q2 reports
  NOT TESTED**, never "steering not worth its cost". This is the difference
  between a null result and a null measurement, and §5 currently cannot tell
  them apart.

---

## (d) Not buildable with existing tooling

**1. The memory directory defeats the sandbox, and it is on by default.**
This is the largest hole in the protocol and §8's C2 does not name it. Every
Claude session in this project loads
`~/.claude/projects/-Users-jasonp-src-polyominoes/memory/MEMORY.md` into
context, and recall surfaces the individual memory files. One of them is
`convex-polyplets-lead.md`, whose body states, in plain text: *"convex
polyplets by **area** are **empirically non-D-finite** (convexity is a
*perimeter* tractability lever, not an area one)"* and *"Don't re-derive"*.
That is the withheld answer to the proposed rung 1, handed to session 1 before
it reads anything. Neighbouring memories leak `grand-form-proved`,
`diagonal-law-proved`, the middle-kingdom state and more. A Ghost Ship session
must run with memory disabled and with `CLAUDE.md` withheld, and the
pre-registration must say so; otherwise the run is contaminated at open and
C2 has been violated before any session acts.

**2. Sandbox isolation (C2) has no enforcement mechanism.** A subagent with
Bash can reach the live repo; the permission system gates *tools*, not
*paths*. The best available construction is: run the sessions on a host where
no checkout of this repo exists (a fresh directory on dalby), plus explicit
`ssh`/`scp`/`git clone` deny rules in `settings.json`. That is buildable but
it is work someone must do, and as pre-registered C2 is an honour system —
a weak link in an experiment whose whole subject is what happens unattended.

**3. There is nowhere for the sandbox to execute, as written.** §2 permits
"desk + sandbox scripts" and bans ssh. gympie is under a hard ban on running
any project-authored code (2026-08-14, after an OOM kill; read-only git and
greps are fine). Those two rules together leave no host: gympie is banned,
and reaching ayr or dalby needs the ssh that §2 forbids. Resolve by naming the
host in the protocol — the session agent's working directory *is* on
ayr/dalby, and "no ssh" means no ssh *out of* the sandbox host. At the
proposed cut this is a small ask: the inherited tools are stdlib Python at
seconds and tens of megabytes.

**4. `tokens = per-session transcript byte count` is not measurable by the
thing being measured.** A session cannot read its own transcript, and bytes
are not tokens. This needs a harness-side mechanism named in the protocol —
which transcript file, read by whom, after the run. Without that, the metric
that carries Q1 and Q3 has no procedure.

**5. "Bulletin read at open only" is a prompt instruction, not a mechanism.**
Buildable properly and cheaply: keep `BULLETIN.md` *outside* the sandbox and
have the launcher inline its contents into the session prompt. Then the
read-once property is structural rather than promised. Worth specifying,
because §4 calls this "the entire steering channel" and everything about Q2
rests on it.

**6. Things that ARE buildable, for the record.** Unattended 3/day scheduling
(the routines/cron tooling exists); sha256-sealing the two prediction files;
post-run court verification, *provided* the protocol names where the sandbox
archive is retained — §2 says nothing syncs back until grading, so a session's
own scripts live only in the sandbox and the receipts are unreproducible if
that directory is not preserved.

---

## Summary of proposed edits

| # | edit | why |
|---|---|---|
| 1 | §3: cut the corpus at `74b2c20`, grade against the 3-rung ladder to `37ce404` | C4 fails as scoped; this fixes difficulty, re-derivation grading and the baseline together |
| 2 | §2: name the sandbox host (ayr/dalby); "no ssh" = no ssh off it | gympie ban vs. ssh ban leaves nowhere to run |
| 3 | §2/§8: disable memory and withhold `CLAUDE.md` for sessions | memory states the withheld answer; contamination at open |
| 4 | §2: publish the exact `git archive` and `git log` commands | filtering at HEAD is unreviewable grader-shaping |
| 5 | §2: two-tier report format with `CLAIM:`/`SHAPE:`/`VERIFY:` grammars | §5's claim, judgment-failure and decay metrics are otherwise uncountable |
| 6 | §2: write the report stub first, update at end | stop rule otherwise fires on truncation |
| 7 | §5: instrument input tokens as three curves, not one | keeps Q3 from being an artifact of the length cap |
| 8 | §4/§5: record bulletin edit count; untouched ⇒ Q2 NOT TESTED | 70–86 h absences are in the record twice in six weeks |
| 9 | §5: name the transcript mechanism for the token metric | not measurable by the session |
| 10 | §4: inline the bulletin into the session prompt | makes read-at-open-only structural |
| 11 | §2: name where the sandbox archive is retained for grading | receipts otherwise unreproducible post-run |
