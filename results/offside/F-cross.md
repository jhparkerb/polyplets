# Offside lane F — cross-examination: A against the candidate, and an adversary pass on A

2026-08-14. Wave 2. Read in order: `docs/offside-brief.md`,
`docs/offside-design.md` (F4, the candidate), `results/offside/A-ab-initio.md`
(filed blind), `results/offside/B-adversary.md`, `results/offside/C-replay.md`,
plus `docs/process-proposal.md` §§A5–A7 and the heuristics file (F5) where B and
C cite it. Desk only; nothing executed.

**Headline.** A wins four of the five conflicts, and wins them on B's and C's
own evidence rather than on argument. The candidate keeps three things A lacks
outright — tier + arity, the paper-spawning rule, and the door fields — and one
thing A dropped by accident, the chronicle. Six mechanisms were invented
independently by both lanes; the strongest of these, *memory carries no project
state*, is now agreed by three lanes with different inputs and should be treated
as settled. Neither design touches what B priced as the binding constraint, so
the composite below is the best available **fidelity** system and is not great.

---

## 1. Conflict-by-conflict verdicts

### C1. TTL (candidate) vs git-freshness, `depends:`/`at:` (A) — **A wins, decisively**

Three independent grounds, none of them A's own argument:

- **B's S2 settles it.** TTL expiry means absence, absence means permission, and
  this repo's load-bearing state is overwhelmingly prohibitive — B counts eight
  memory files carrying an explicit ban, each with an incident behind it (holes
  n≥20 NO-GO; "don't relaunch any phase"; "never re-pitch d=15..19";
  `a21-run-do-not-restart`; `viva-do-not-raise`). Under the candidate each is an
  operational assertion or a priority, each expires on a schedule, and the agent
  that walks through the reopened door is obeying the design.

  **Does A's design have this flaw? No, and not by luck.** A's stale block is
  still *present and readable*; staleness is a mark on a line of STATE.md, not a
  withdrawal. Closed blocks are never pruned from `state/closed.md`,
  contradicting one requires an appended `reopens:`, and nothing is ever
  deleted. The prohibition survives its own staleness by construction. B's fix
  F5 ("prohibitions are facts with door fields, not bets; anything whose
  consumption is *do not* never TTLs") is a patch the candidate needs and A does
  not.
- **C's day 3 shows TTL is coarser than looking.** The a(40) run's tmux server
  was OOM-killed; the operations row asserts RUNNING against a dead PID. C:
  "TTL retires that in days; the operator saw it in minutes." A calendar is the
  wrong instrument for a fact about a box.
- **Git-freshness has a true positive on the record and TTL has none.**
  `docs/proofs/polyplet-upper-bound.md` was found broken and repaired in place on
  2026-08-14; every claim resting on it goes stale on that commit, mechanically,
  whether or not anyone thought to look for dependents. C's day 1 confirms the
  collateral was found by hand and only because one session happened to hold both
  files. No TTL length fires on that event at all.

**What TTL keeps.** Exactly one class: assertions about the world outside the
tree — ayr dark, a PID alive, a disk free. Git cannot see them, because nothing
in the tree moves when a box dies, and A has no home for them either (A's block
is a claim container). The composite takes F5's rule instead of a TTL: machine
liveness is a session-open action, never a gate invariant, and a machine-condition
row is re-checked rather than consumed. That rule needs `ssh`, which is banned on
gympie, so the honest residual is that machine state is unknown to a gympie
session and must say so rather than assert.

### C2. Register tables (candidate/F5) vs per-thread append-only cards (A) — **A wins**

- **On writes, C's counts are the argument.** C's day-1 King Twigs closure costs
  six register writes (hypothesis row → REFUTED, tombstone, fact row, three door
  fields, operations row retired, chronicle). Under A the same event is *one
  appended block* on `state/king-twigs.md` plus the door fields, because the
  block already carries claim, receipt, harness and caveat in the fields the
  registers were splitting across three files. The tombstone↔fact bijection
  disappears — a CLOSED block that follows an OPEN block in the same file is the
  pairing, and it needs no gate to hold it.
- **On C's branch problem, A converts a hand reconciliation into a
  regeneration.** C's charge against the candidate is precise: gate-checked
  tables with bijective pairing "fail **closed** on a half-merged state… and the
  reconciliation is a hand edit of the very tables that were supposed to be
  authoritative." Under A, `STATE.md`, `closed.md` and `HANDOFF.md` are all
  generated, so a merge conflict in them is resolved by `make state`, not by
  hand. The only hand-resolved conflict left is append-vs-append at the end of
  one card, and the resolution rule is *keep both* — blocks are independent and
  ordered by `at:`. Two branches working different threads touch different files
  and merge clean, where today they both edit `HANDOFF.md`.

  A does not claim this and never mentions branches; it falls out of R1. Tagged
  below as A-mechanism / C-evidence, not as A's argument.
- **What the registers had that cards lose:** a single place to read all
  operations, and a single place to read all facts. A's `STATE.md` restores the
  first as a rendered view; the second is `closed.md` plus grep. Acceptable.

### C3. Summarizing renderer (candidate, unspecified) vs transcluding renderer (A) — **A wins, and this is the strongest single idea in either file**

A: the renderer selects and orders; it does not summarize; every character of
prose in the output was written once by the session that held the evidence and
is transcluded byte-for-byte. The argument is exact — *the failure mode of a
summarizing renderer is the failure mode of a summarizing session, rebuilt in
Python* — and it is the one answer to B's "who gates the gate" that removes a
failure class rather than adding a check over it.

But it does not answer all of B's F3, and B's F3 does not answer all of A. They
attack different halves and the composite needs both:

| failure | caught by |
|---|---|
| renderer invents, softens, or drops a caveat | A's transclusion (structurally impossible) |
| renderer's glob stops matching after a rename; view gets shorter and cleaner | **B's F3 only** — print sources consumed and rows emitted, fail if either drops below the last committed value |
| a session hand-edits the generated file | **A's check 4 only** — source-hash on line one, gate recomputes |

B's two in-tree silent-green precedents (verify_claims dropping 220 checks while
exiting 0; the lean2 gate E reading a correct output as zero sorries on an
ASCII-vs-backtick mismatch) are precisely the middle row, and A has nothing for
it. Take all three.

**Where B beats A on the render:** B's F4. A render sorts by a schema field and
cannot carry emphasis; `HANDOFF.md:50`'s "**Read §5 (limits ledger) before
citing**" is a rendering of judgement and no schema emits it. B's fix — the
render consumes a hand-ordered list of thread names and errors on names it
cannot resolve — preserves R1 (a list of names is not prose that can decay) and
belongs in A's design.

### C4. Executable check as the claim's status (candidate) vs `receipt:` + `harness:` + status token (A) — **split; A's primitive, the candidate's vocabulary**

The candidate's mechanism 1 is the one B damaged worst, twice. Its own headline
number — 448/448 — was stale by twelve days in the sentence arguing that
computed status prevents exactly that (the real count is 428, recorded at
`docs/paper1-reproducibility.md:182-183`); and the exemplar had a silent-green
coverage defect in which 220 of 448 checks vanished with exit 0. C's unmeasured
#3 finishes it: 27 `gate-*` targets against 125 `results/*.md`, and this
project's headline numbers are overwhelmingly *receipts*, not re-runnable checks
— a 10.9 h wall, a 95.0 GB peak RSS, a 23,681,423-window census.

A's split is the better primitive and answers a measured repo failure the
candidate's single field does not: `check_receipts.sh:6-9` records that across
round 4 of the triangle campaign every status drift had the same sign — an
instrument that was WRITTEN, UNRUN got described as one that had run. A separate
`harness:` (the thing that can be re-run) from `receipt:` (the thing that was
produced) makes that drift unwritable.

**What A must import:** the tier vocabulary. A's five status tokens cannot
distinguish two-source from single-source, and two-source is the discipline this
project's whole a(n) ladder is built on. Take `tier:` as a required field on
`MEASURED` and `CLOSED` blocks, with F5's arity rule — a `two-source` row names
two paths — which is gate-checkable and is one of the few candidate checks with
real teeth.

### C5. `kill:` required on OPEN (A) vs nothing (candidate) — **A wins uncontested**

The candidate has no pre-registration mechanism at all. Rook parity round 1
closed with the finding that the goal was not well-formed after a six-agent day;
B's S4 names target selection as the failure class the candidate ignores. An
unwritable `kill:` line is a loud signal at cost zero. Its limit, which A
undersells: it fires at thread birth only. C's day 3 — four OOM kills before
anyone stopped patching and redesigned — is a mid-thread repeated-obstruction
event that no `kill:` line catches.

### C6. `reopens:` / `withdraws:` (A) vs tier moves (candidate) — **A wins**

`reopens:` is one of very few controls in either design enforced by a gate at
write time rather than by discipline at read time, and it is aimed at
re-derivation, which the candidate addresses only by exhortation (B's S1 table:
four of seven headline mechanisms rest on the fresh agent choosing to comply).

Honest limit, which A states for the wrong case and not this one: B's S1 is
right that the damage completes before the first commit. A session that
re-derives a closed result gets stopped when it writes the `OPEN` block, by
which time the evening is spent. `reopens:` saves the record, not the evening.
The thing that saves the evening is `closed.md` being small and grep-shaped,
which is a read-side mechanism and unenforceable by anything.

### C7. Source-hash on generated files (A) vs nothing (candidate) — **A wins uncontested**

The failure it stops is attempt four: a generated file that someone starts hand
-editing is a hand-maintained derived index again, and this repo has three
corpses (ROADMAP.md, the results map, the dependency map). It also resolves B's
S3 dilemma, which A did not notice it had resolved: B argues that any render
must have a committed readable output to survive a power cut, and that a
committed derived output is the thing that dies. A hashed generated file can be
committed *and* cannot silently diverge, and A's gate is grep plus `git log`
with no compute, so it runs on gympie under the project-process ban as desk
work. That is a complete answer to S3 and the candidate has none.

---

## 2. Independent convergence

A was written without reading the candidate or its ancestor. Where the two
arrived at the same mechanism anyway, that is the strongest evidence this review
can produce, and it is worth listing separately from the argued verdicts.

1. **Memory carries no project state.** A's gate check 5 (grep one fixed
   directory for status tokens in a status position; RED, "status belongs in a
   card") and the candidate's item 7. Both localise it to the same three
   2026-08-14 incidents. B, adversarial to the candidate, independently calls
   item 7 "the strongest item in the doc… should land whatever happens to the
   rest"; C confirms one of the three is structurally prevented by it. **Three
   lanes, three different inputs, one conclusion — treat as settled.**
2. **Hand-maintained derived indexes must be generated.** A §5, candidate item 3,
   same three corpses.
3. **The thread name is the retrieval primitive.** A §1 (names already in use,
   grep-findable, in commits and docs), candidate item 4 (rung zero).
4. **Time must never pass through the agent.** A's R2, candidate item 2's stamp
   discipline. They converge on the constraint and split on the mechanism —
   which is conflict C1, and the split is the sharpest disagreement in the panel.
5. **Absence must be declared, never silent.** A's `caveat: none` as a required
   field the gate rejects when missing; the candidate's explicit `check: none`
   displayed loudly. Identical incentive design, invented twice.
6. **Receipts are in-tree resolvable paths, and `check_receipts.sh` is the
   precedent to reuse rather than reimplement.** A explicitly delegates; the
   candidate cites it as the model. Both refuse a second path checker.
7. **One gate, red-first, planted fixtures, plain files, grep, no database, no
   framework.** Both, and both name the same reason.

---

## 3. Adversary pass on A

B never saw A. These are the charges B's pass would have brought, plus A's own
three declared least-sure decisions settled where B's or C's evidence already
settles them.

**A's decision (a) — should staleness ever be RED? Settled: no, never.**
A guessed RED for `OPEN`/`MEASURED`, warning for `CLOSED`, and asked for a
two-week git replay. The evidence is already in hand and points one way. B's
alarm-fatigue finding — once `check: none` is a third of every render, loud is
noise and the display stops being read — transfers to staleness marks unchanged.
C's record supplies the rate: ten commits on one incident day, four branches in
48 hours; generous `depends:` lists against that traffic red the gate on
mornings when nobody did anything wrong. A's own sentence is the argument
against A's default: *a restamp that is reflexive is a lie with a commit hash on
it.* And F5 already names the disposal route for a gate that reds on events
outside the committer's control — "a gate that reds on a power cut gets
commented out."

So: the gate is red-first on **grammar and receipts**, which are properties of a
single block that a single session controls, and never on a property produced by
someone else's commit. Staleness is a mark on the one screen a session reads at
open. Residual, conceded: with staleness demoted, nothing forces a restamp. That
is B's S1 read-side gap and no mechanism in either design closes it.

**A's decision (b) — generated HANDOFF? Settled: take the middle option A
declined.** C's replay removes half the question: on all three days the read
side was cheaper under a rendered view, and C declines to belabour it. What
survives is A's real worry, that the generated file is worse to open cold and
the operator stops opening it — and C's day-1 supplies the concrete loss (the
"jasonp's call" account, whose sentences do not decompose into fields), with
B's F4 supplying the general form (emphasis is a rendering of judgement; no
schema emits it). A named a middle option — a generated file with one
hand-authored, gate-untouched paragraph at the top, appended per session and
never rewritten — and refused it for fear of a second place where prose drifts.
The fear is misplaced under A's own R1: an *appended* paragraph does not drift,
it becomes history. Take the middle option, plus B's F4 hand-ordered thread
list.

**A's decision (c) — may memory carry status? Settled: no, and A's counter-case
dissolves.** A worried that stripping status leaves a table of contents nobody
consults, and asked for a strip test on twenty-odd lines. A's own sharper
version answers it from the record: the three incidents were entries that
*asserted* something false, and a pointer cannot assert. B's S5 is the same
worry stated better and concedes itself — "about bandwidth, not channel, since a
pointer still rides the push channel." One small amendment saves the routing
value A was defending: a memory line may carry a **verdict token from the closed
vocabulary plus a receipt path**, which is not prose status and is checkable by
the same shape rule. `[[king-twigs]] — CLOSED-NEGATIVE, results/king-twigs-l1.md`
routes as well as the status-bearing line did and cannot go stale in the way
"Phases 0-2 DONE, Phase 3 next" did.

**New charges against A:**

- **A8. `depends:` is hand-written, its completeness is uncheckable, and A
  argues only the safe direction.** A reasons that sessions have no incentive to
  be sparing, so lists will be over-inclusive. The under-inclusive direction has
  no argument at all and is the dangerous one: a missing `depends:` entry is a
  silently fresh block, the exact silent-green class B documented twice.
  Cheap mitigation A should have taken: `depends:` defaults to the block's own
  `receipt:` and `harness:` paths plus the thread's primary doc, so it is never
  silently empty.
- **A9. A dropped the chronicle and has nowhere to put C's day-3
  unrepresentables.** C names three events with no claim in them: the OOM killer
  taking the tmux server (a machine event with no writer), the 284 GB cleanup
  under item-by-item authorization (a human action producing no artefact,
  "expressible only as chronicle prose"), and the ssh-agent death with its
  git-bundle workaround (a capability change on a box). A's card is a claim
  container and A's file never specifies a chronicle file. The candidate's item
  7 does. Restore it.
- **A10. Fail-open on omission, same as the candidate.** C's day-1 finding
  applies verbatim: the gate checks the shape of blocks that exist and cannot
  check for a block never written. A's `closed.md` is offered as *the*
  anti-re-derivation index; a closure never written to a card is not in it. A
  concedes the different-name case in §7 and not this one.
- **A11. Multi-line prose fields contradict A's own parser rule.** A says "no
  free prose in the fields" and then writes a two-line `caveat:` in its own
  example. A multi-line field is what makes an awk parser fragile and a
  transcluding render drop rows — the ASCII-vs-backtick class again. Require one
  logical line with a continuation indent, gate-checked.
- **A12. A named the wrong measurement for adoption.** A's queue row asks for a
  git-history replay of staling rates, which measures its own mechanism. B's
  migration baseline — verify every OPEN/RUNNING/PARKED row against its primary
  doc, count the ones found wrong, repeat later — measures whether the state
  layer needs replacing at all. A's migration is eight cards, so A's version of
  that baseline is cheap, and A should have priced it.
- **A13. B's S4 lands on A undiminished, and this is the biggest charge.** A has
  no heuristics, no coincidence render, nothing cross-thread. `kill:` is its
  only judgement instrument and fires at thread birth. C's day 3 — four
  instances of one failure class before anyone redesigned — is exactly what the
  removed heuristic 1 catches and A does not have it either. A is a
  fidelity-only design under B's ceiling, same as the candidate.

**Where A survives a charge the candidate does not:** B's F6 (exemption
vocabularies leak; `gate_citations.py` exempts at paragraph scope, and research
prose says "deleted", "planned", "todo" constantly). F5's repo-wide status check
is best-effort and inherits the leak. A's check 5 is a shape rule over one fixed
directory — narrow, no exemption vocabulary, no filesystem scan. That is the
right scope and it is the check that closes the incidents actually observed.

---

## 4. The surviving composite

Mechanisms only. Tag = whose evidence supports it.

**Unit.** One append-only card per named thread, `state/<thread>.md`; blocks are
fixed single-line fields; a block is never edited, every status change is a new
block. [A; merge behaviour supported by C's branch section]

**Fields.** `at:` (commit at write) · `claim:` · `tier:` (proved / two-source /
single-source / measured-once, arity-checked) · `receipt:` · `harness:` ·
`depends:` (defaults to receipt+harness+primary doc) · `caveat:` (required,
`none` allowed) · `kill:` (required on OPEN) · `reopens:` / `withdraws:` (required
on contradiction) · `reopen:` and `price:` on CLOSED/PARKED, price a measured
receipt or `unmeasured`. [A, except `tier` and `price`-discipline from the
candidate, arity from F5]

**Status set.** OPEN, MEASURED, CLOSED, CLOSED-NEGATIVE, WITHDRAWN. [A]

**Freshness.** `git log <at>..HEAD -- <path>` per `depends:` entry. A stale block
is marked, never absent, never RED. No TTL anywhere. [A mechanism; B's S2 and
C's day 3 supply the reason it beats TTL; the never-RED setting is this lane's
call off B's alarm-fatigue finding]

**Machine state.** A machine-condition register, re-checked at session open,
never consumed as truth, never a gate invariant; a gympie session says machine
state is unknown rather than asserting it. [F5 A6; B's S3]

**Views.** `make state` regenerates `STATE.md`, `closed.md` and `HANDOFF.md`.
The renderer transcludes and never summarizes [A]; it prints sources consumed
and rows emitted and fails if either drops below the last committed value [B's
F3]; generated files carry a source hash and hand edits go red [A]; ordering
comes from a hand-maintained list of thread names, erroring on unresolvable ones
[B's F4]; one hand-authored, appended, never-rewritten operator paragraph sits
at the top of HANDOFF [A's declined middle option, restored on C's day-1
evidence].

**Chronicle.** Append-only narrative, no status language — the home for events
with no claim in them. [candidate item 7; C's day-3 unrepresentables]

**Memory.** Pointer plus an optional closed-vocabulary verdict token plus a
receipt path. Gate: shape rule over one fixed directory, found-or-declared.
[A check 5 + candidate item 7 + F5's shape rule; A's decision (c) settled here]

**Gate.** One target, grep and `git log` only, `--self-test` first, one planted
fixture per check. Red-first on grammar and receipts; marks, not reds, on
freshness. Delegates path checking to `check_receipts.sh`. [A; fixture
discipline from `check_receipts.sh`'s three mutants]

**Papers.** A notable result owes a paragraph and a named check in that draft's
verifier in the same act; every check owned by exactly one draft; every asserted
number checked; negative-result papers first-class. [candidate item 5, whole —
A has nothing here and B rates it among the four things the candidate gets
right]

**Doors.** Lock, Reopen, Price on closed and parked blocks; the grouped Lock
listing as non-failing render output. **Converts-to is optional and its
retention is conditional**: C found it unfillable on the day (King Twigs, "a
required field with no answer"), F5 concedes the closing session cannot fill it,
and the candidate's own guardrail says three unfilled rows means delete the
field. Its only consumer is the repeated-obstruction rule, which the candidate
dropped. Restore the rule or drop the field. [C's day 1; F5; B's S4]

**Disclosure ladder.** name → one-liner → results note → paper. Add the slot C
found missing: goal docs have no rung, and the rook round's own lesson is that
the failure was in the goal, not the transmission. A card carries `goal:`
pointing at its goal doc. [candidate item 4; C's day-2 gap]

**Not in the composite, and named so nobody re-adds them silently:** TTLs,
expiry, scheduled review; a summarizing renderer; register tables with bijective
tombstone pairing; a second path checker; any field measured in days.

---

## 5. What remains genuinely undecidable without lane D

- **Block granularity.** C's load-bearing unknown, unchanged by the move from
  registers to cards: how many blocks does a landed result cost? C's counts
  assume one row per headline number; the characteristic-landscape sweep alone
  could justify twenty. Every write-count comparison in §1's C2 verdict is
  qualitative until this is measured.
- **Whether a freshness mark is informative at all.** I settled the *policy*
  (never RED) on alarm-fatigue grounds, which is robust. I did not settle
  whether the marks carry signal: the true-positive rate of `depends:`-driven
  staling against the last two weeks of git history is unmeasured, and if it is
  near zero the mechanism is decoration.
- **`depends:` completeness in practice.** Untestable by any gate; only
  measurable by comparing hand-written lists against dependency sets recovered
  from history. See queue.
- **The cost, not the count, of a stale-state incident.** C's #2. The record for
  the one detailed day says nothing was re-run. If that holds throughout, both
  designs are solving a cheap problem expensively.
- **Receipt-only share of the claim population.** C's #3. Decides how much of
  "status is computed" is reachable at all; my C4 verdict (A's primitive) is
  robust to the answer, but the candidate's mechanism 1 is not.
- **The migration baseline.** B's, dropped by the candidate. Without it the
  adoption question is unanswerable by construction, and A's eight-card
  migration makes the baseline cheap.

**Verdicts robust to all six measurements**, and adoptable now: memory carries
no project state; prohibitions never expire; the renderer transcludes; generated
files carry a source hash; `kill:` on OPEN; `reopens:` on contradiction.
