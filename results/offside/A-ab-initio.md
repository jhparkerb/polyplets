# Offside lane A — the state system I would build, ab initio

2026-08-14. **Filed blind**: written without reading `docs/offside-design.md`
or `docs/process-proposal.md`, and without grepping for their contents. Inputs
were F1 (Li et al., the Grothendieck case study), F2 (`HANDOFF.md`), F3
(`MEMORY.md`), F6 (`paper/verify_claims.py`, `scripts/check_receipts.sh`,
`tests/gate_citations.py`), and the problem statement in `docs/offside-brief.md`.

---

## 0. The diagnosis I am designing against

Five of the six observed failure modes are one failure mode. Status claims
outliving their evidence, summaries decaying, caveats lost, results re-derived,
three stale-memory incidents in a day — all of them are what happens to a
**hand-maintained summary that is rewritten by a fresh session that does not
hold the evidence**. Li et al. put a number on the mechanism: their active
state was rewritten roughly two hundred times, and each rewrite pulled toward
the genre of a finished paper, in which headline values survive and evidential
status does not. Their session-44 record was set by a score whose "exploration
only" caveat had been rewritten away, and the criterion that would have
invalidated it had been proved in session 8 and lost in a later handoff. The
archive held both facts. The summary governed the decision.

This repo has the same architecture and the same result. `HANDOFF.md` is 1,151
lines; its top entry is a curated summary written by a session that then ended.
The 2026-08-14 evening incidents are the pure form: items 5 and 3 were queued
as open work, `MEMORY.md` said they were open, and both had been closed — one
on 2026-08-01, one committed. Nothing was re-run, which is luck, not design.

The sixth failure mode is different in kind and constrains everything: **the
agent has no sense of time.** So no mechanism in this design may be keyed to
elapsed duration. An agent cannot honour "recheck this monthly" or "expires in
30 days"; it can only honour a comparison between two values it can read. The
clock this project actually has is git.

Two rules follow, and the whole design is their consequence:

- **R1. The record is appended, never rewritten.** Whatever a session must
  read at open is either an append-only file or mechanically derived from one.
  Decay is a property of rewriting; remove the rewriting.
- **R2. Freshness is measured against git, never against the calendar.** A
  claim is suspect when the artifacts it rests on have moved since it was made.
  That is a comparison of two recorded commits, which an agent with no felt
  duration can perform exactly.

What is *not* broken, and which I deliberately leave alone: the result notes
under `results/`. `results/king-twigs-l1.md` and `results/motley-h17.md` lead
with the verdict, cite the harness, and carry a provenance table. They are
written once by the session that held the evidence and they are not rewritten.
They are the part of the system that already obeys R1. The design below adds a
thin index over them and deletes the curated layer above them.

---

## 1. The unit: a thread card

One file per named thread, at `state/<thread>.md`. Thread names are the ones
already in use — Motley, Confetti, Coin Lift, Ridgeline, King Twigs, Exact
Change, Notary. This leans on the one retrieval mechanism the project has
already measured as working: short evocative names, grep-findable, used in
commits and docs.

A card is a header plus an append-only sequence of **blocks**. A block is
fixed-field so one awk script can parse it, and every field is a path, a git
object, or a token from a closed vocabulary. No free prose in the fields; free
prose goes in the paragraph under them, where nothing depends on it.

```
## 2026-08-14 · level-1 twig bound · CLOSED-NEGATIVE
at:       9e1f976
claim:    level-1 king twig bound = 5^5/4^4 = 12.207, exact
receipt:  results/king-twigs-l1.md
harness:  experiments/kingtwigs/l1_schemes.py
depends:  docs/king-twigs-plan.md docs/proofs/polyplet-upper-bound.md
caveat:   the plan's crude-bound proof was broken and repaired in place;
          the constant survives, that argument did not
```

Field meanings, all load-bearing:

- `at:` — the commit the tree was at when the block was written. This is the
  block's clock reading, and the only one it will ever have.
- `claim:` — one line, the sentence that would be false if the block were
  wrong. If it cannot be written in one line the work is not finished.
- `receipt:` — an in-tree, non-empty path. Same rule as
  `scripts/check_receipts.sh` already enforces for the rook round, and I would
  reuse that script rather than write a second one.
- `harness:` — the thing that can be re-run. Separate from `receipt:` because
  the rook campaign's measured failure was written-but-unrun instruments being
  described as run.
- `depends:` — **the field a generic design omits, and the one that makes
  freshness mechanical.** Every in-tree artifact this claim rests on.
- `caveat:` — the field whose loss Li et al. documented and this repo has
  repeated. A block with no caveat writes `caveat: none` explicitly; the gate
  rejects a missing field, so a caveat can be absent but never silently absent.
- `kill:` — required on `OPEN` blocks only (see §4).
- `reopens:` / `withdraws:` — required on the two transitions that contradict
  an earlier block (§4).

Status vocabulary, closed set, five tokens: `OPEN`, `MEASURED`, `CLOSED`,
`CLOSED-NEGATIVE`, `WITHDRAWN`.

**A block is never edited after it is written.** Every change of status is a
new block. `grep -A8 'Coin Lift' state/*.md` returns the thread's whole life in
order — question, kill condition, measurement, verdict — which is what a
session actually needs and what no rewritten summary can give it.

---

## 2. What a session reads at open

Three files, bounded, in this order. Nothing else is required reading.

1. **`state/STATE.md`** — generated, never authored. One line per thread whose
   latest block is `OPEN` or `MEASURED`, plus every thread whose latest block
   is stale (§3). Format is the latest block's own fields, transcluded
   verbatim: `thread | status | claim | receipt | fresh|STALE`. Target size is
   one screen. Today that is about eight lines.
2. **`state/closed.md`** — generated, append-only, never pruned. One line per
   `CLOSED` / `CLOSED-NEGATIVE` block ever written, with its receipt. This is
   the anti-re-derivation index and it is meant to be grepped, not read.
3. **`MEMORY.md`** — practice only, and it is auto-loaded anyway.

Then, and only then, the card for whatever the operator named. If he named
nothing, the session asks; it does not go shopping in `state/`.

`HANDOFF.md` is not on the list. Under this design it is generated (§5) and
exists for the operator, not for the session.

The size argument matters more than it looks. The session that missed the two
already-closed items on 2026-08-14 had `HANDOFF.md` and `MEMORY.md` available.
A record that must be read in full to be correct will not be read in full.
`state/closed.md` is correct under grep, which is the access pattern that
actually occurs.

---

## 3. Freshness, without a clock

For each block, the gate resolves each `depends:` path and asks git whether
that path has changed since the block's `at:` commit:

```
git log --oneline <at>..HEAD -- <path>
```

Non-empty output means the block is **stale**: something it rests on moved
after it was written. Stale is not wrong. Stale means the block's evidential
status is no longer established, and STATE.md says so on its line.

Restamping is one appended block with a new `at:` and a `checked:` field naming
what was re-read or re-run. It is cheap by construction because the block is
six lines, and it is honest by construction because `checked:` is a path.

This is the whole staleness mechanism. There is no TTL, no expiry date, no
periodic sweep, and no field anywhere in the design measured in days. Every
freshness question reduces to "did this path move between these two commits",
which is exactly answerable by an agent that cannot feel duration.

It also catches the real case rather than a hypothetical one. `docs/proofs/
polyplet-upper-bound.md` was found broken on 2026-08-14 and repaired in place.
Every banked claim with that proof in `depends:` goes stale on that commit and
appears in STATE.md the next morning, whether or not the session that repaired
it thought to go looking for dependents. Nothing in the current system does
this; the repair's collateral was found by hand, and only because the same
session happened to be reading both files.

---

## 4. The life of a hypothesis

Five states, and every transition is an append.

- **OPEN** — a question, and it may not be opened without a `kill:` line: the
  pre-registered condition under which the thread is abandoned. The gate
  refuses an `OPEN` block with no `kill:`. This is aimed squarely at rook
  parity round 1, where a whole six-agent day established that the goal was not
  well-formed; the pin sat below what the incumbent already measured and the
  bar contradicted the pin. A `kill:` line does not guarantee a well-formed
  goal, but an unwritable one is a loud signal at cost zero, and the standing
  practice [[audit-goal-before-brief]] already says to measure the beat-X
  quantity before writing the brief. This makes that practice a field.
- **Opening a thread that has a CLOSED block requires `reopens:`** naming that
  block. The gate rejects the `OPEN` otherwise. This is the mechanical form of
  "do not re-derive": a session that starts work already closed must first
  write down which closure it is contradicting, which is a step it cannot take
  without discovering the closure. It is the one anti-re-derivation control
  here that a gate can enforce rather than a habit.
- **MEASURED** — a number with a receipt. Explicitly not a claim about the
  world. The distinction is the one Li et al. lost: a fast evaluator's score,
  safe for exploration, became a record.
- **CLOSED / CLOSED-NEGATIVE** — the question is answered or the kill fired.
  `receipt:` required. Negative closures are first-class: this project's
  cheapest asset is a closed door, and re-deriving one costs an evening.
- **WITHDRAWN** — requires `withdraws:` naming the block retracted. Nothing is
  ever deleted. The withdrawn block stays where it is, and STATE.md carries the
  withdrawal, so the history reads as a history rather than as a clean sheet
  that happens to be right.

---

## 5. HANDOFF.md becomes generated

`make state` regenerates `HANDOFF.md` and `state/STATE.md` from the cards. The
renderer **selects and orders; it does not summarize.** Every character of
prose in the output was written once, into a block, by the session that held
the evidence, and is transcluded byte-for-byte. This is deliberate and it is
the answer to "who gates the gate": a renderer that cannot write cannot decay,
and a renderer bug can drop or misorder a block but cannot invent or soften
one. The failure mode of a summarizing renderer is exactly the failure mode of
a summarizing session, and I would rather not rebuild it in Python.

The current `HANDOFF.md` is frozen to `state/archive/HANDOFF-2026-08-14.md`,
read-only, cited freely and edited never. Migration is the live threads only —
roughly eight cards — not 1,151 lines. Everything else stays in the archive and
in `results/`, where it already is.

---

## 6. The gate — one target, five checks, red-first

`make gate-state`, one script, `scripts/check_state.sh` (planned), with a `--self-test`
that runs first on every invocation, in the shape `check_receipts.sh` already
uses. Fixtures under `tests/fixtures/state/` (planned), one planted violation per check.
A check that has never rejected a planted violation is not a check.

1. **Receipts.** Every `receipt:`, `harness:`, `checked:` path exists, is
   non-empty, is inside the repo. Delegate to `scripts/check_receipts.sh` —
   its rule and its three planted mutants (absent, missing, on-another-box) are
   already right, and its narrow default scope just gains `state/*.md`.
2. **Grammar.** Every block carries every required field for its status;
   `caveat:` is required on all of them; the status token is in the closed set;
   `OPEN` carries `kill:`; a contradicting block carries `reopens:` or
   `withdraws:` and names a block that exists.
3. **Freshness.** §3's git comparison. RED when a block whose status is `OPEN`
   or `MEASURED` is stale; a stale `CLOSED` block is a warning row in STATE.md
   and not a failure. (This asymmetry is one of my three least-sure calls —
   see §8.)
4. **Generated files are not hand-edited.** `STATE.md` and `HANDOFF.md` carry a
   first-line hash of their source cards; the gate recomputes it. A session that
   hand-edits the summary gets a RED rather than a silently diverged summary,
   which is the failure this whole design exists to stop.
5. **Memory carries no status.** Grep the memory directory (a single fixed
   path, never a filesystem scan) for the status tokens in a status position.
   Any hit is RED with the message *status belongs in a card*. Memory carries
   practice, bans, and pointers; it does not carry the state of the work.

Check 5 is the one that closes the incidents actually observed. All three
2026-08-14 stale-state incidents were in the memory layer, and the memory layer
is the one layer with no gate over it — `gate-citations` and `check_receipts`
both stop at the repo boundary. Under this rule, `[[middle-kingdom-plan]]`
reads "poly-time tier campaign; plan at `docs/middle-kingdom-plan.md`" and
cannot say "Phases 0-2 DONE, Phase 3 next", which is precisely what it said and
precisely what was false.

Cost and placement: the gate is grep plus `git log`, no compute, so it is desk
work and runs anywhere, including gympie under the project-process ban. I would
give it its own target *and* list it in `make gates`, so that a full `make` on
ayr or dalby covers it without the state layer becoming hostage to a box.

---

## 7. What this costs per session, and what it stops

Writes per session, steady state: one block per landed result — one to three on
a working day — plus zero writes to `HANDOFF.md`, zero to `MEMORY.md` unless a
standing practice changed, plus the result note under `results/` that is
already being written today. Against the current cost: the 2026-08-14 evening
`HANDOFF.md` entry alone is 65 hand-authored lines, plus several memory edits,
plus the same result notes. This should be a net reduction in writing and a
large reduction in rewriting, and the honest measurement that would settle it
is named in the queue.

Reads at open: three files, one screen plus two grep targets, against the
current 1,151-line `HANDOFF.md` and a 128-line memory index.

Against the recorded failures:

| failure | mechanism | enforced by |
|---|---|---|
| status outliving evidence | `depends:` + git freshness (§3) | gate check 3 |
| summary decaying under rewriting | blocks appended, never edited; renderer cannot summarize (§1, §5) | gate check 4 |
| re-derivation of banked results | `state/closed.md` + `reopens:` required (§2, §4) | gate check 2 |
| caveats lost across handoffs | `caveat:` a required field; blocks transcluded verbatim | gate check 2 |
| stale memory (all three incidents) | memory carries no status (§6) | gate check 5 |
| no sense of time | no duration anywhere; git is the only clock (R2) | by construction |

The one I would not oversell is re-derivation. `reopens:` catches a session that
opens a closed thread by name. It does not catch a session that re-derives a
closed result under a different name, and I know of no cheap mechanism that
does.

---

## 8. The three decisions I am least sure of

**(a) Whether staleness should ever be RED, or only ever a mark.**

I have staleness RED for `OPEN`/`MEASURED` blocks and a warning for closed
ones. The split is a guess. If `depends:` lists are written generously — and
they will be, because a session writing a block has no incentive to be
sparing — then routine edits to a plan document will stale a dozen blocks at
once, the gate goes red on a morning nobody did anything wrong, and the
project learns to restamp reflexively. A restamp that is reflexive is a lie
with a commit hash on it, and I would rather have a warning nobody must clear
than a green nobody believes.

*Evidence that settles it:* replay the last two weeks of git history against
the rule. For each commit, count the blocks that would go stale and — reading
the record — how many of those stalings correspond to a claim that was in fact
affected. `docs/proofs/polyplet-upper-bound.md`'s repair is a true positive by
construction. If true positives are a small minority of stalings, drop check 3
to warning-only for every status and let STATE.md carry the marks.

**(b) Whether `HANDOFF.md` should be generated rather than authored.**

Generation is what kills the decay, and it is also the design's largest
imposition on the operator, because the thing being replaced is his own prose.
The rendered file will read as a list of blocks. Today's `HANDOFF.md` top entry
reads as an account: it says *why* item 4's gate wiring is undecided and *whose
call* it is, and those sentences do not decompose into fields. I have a real
risk that the generated file is worse to open cold, he stops opening it, and
the state layer becomes a thing that is maintained and not read — which is
strictly worse than a summary that rots, because at least a rotting summary is
read.

*Evidence that settles it:* render the eight live threads under §1's format and
set the output beside the 2026-08-14 evening entry. This is a judgment only he
can make and it is cheap to put in front of him. A middle option exists and I
did not take it: a generated file with one hand-authored, gate-untouched
paragraph at the top, appended per session and never rewritten. That preserves
the account and keeps R1, at the cost of a second place where prose can drift.

**(c) Whether memory may carry status at all.**

Check 5 is the sharpest rule here and rests on three incidents in one day.
Three is not many, and the counter-case is that memory index lines are findable
*because* they carry a verdict: `[[king-twigs-closed]] — level-1 = 5⁵/4⁴
exactly, KR deferral blocked on king` routes a cold session in one line, and
the stripped version — "king twigs; see `results/king-twigs-l1.md`" — may not.
If the rule degrades memory into a table of contents that nobody consults, it
has traded three incidents for a dead retrieval layer.

*Evidence that settles it:* take the twenty-odd status-bearing lines in
`MEMORY.md`, strip the status from each, and check whether the question each
line answers can still be routed from the stripped line to the right file.
Where it cannot, the fix is probably not "allow status" but "the pointer names
the wrong file", and that is worth knowing either way. The sharper version of
the same test: of the three incidents, ask whether a *pointer-only* entry would
also have misled. My reading of the record is that it would not have — the
entries asserted things that were false, and a pointer cannot assert — but I am
reading a two-line summary of each incident, not the incidents.

---

## 9. Deliberate non-mechanisms

Named so a reader knows they were considered and refused, not overlooked.

- **No TTLs, no expiry, no scheduled review.** R2. An agent that cannot feel
  duration can only pretend to honour them.
- **No database, no index format, no framework.** Plain markdown, one awk-shaped
  script, git. Grep remains the retrieval primitive throughout, and the block
  format exists to make grep's output readable, not to replace it.
- **No summarizing renderer** (§5).
- **No second gate.** Everything above is one target. The receipt half is
  delegated to a script that already exists and already has planted mutants;
  writing a second one would be the beginning of the framework.
- **No change to `results/`.** It works. The design indexes it and otherwise
  leaves it alone.
