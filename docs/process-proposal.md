# Proposal: state split by kind, closed threads with fields, a heuristics file

Draft v3, 2026-08-14 (Fable, in-session), prompted by Li et al. (arXiv
2608.11195) and by this repo's own incidents, then battered through two
adversarial rounds. Design constraints: super-basic bug tracker, not an
agent framework; state split by *kind*; heuristics from the literature.

## Why

Li et al.'s diagnosis — iterated rewriting of a curated research state
regresses toward the finished-paper genre, so headline values outlive
their evidential status — reproduced here three times in one day. **All
three stale claims were in MEMORY.md, not HANDOFF** (HANDOFF:9-12, "Both
memory entries were stale and are fixed"; the third is
`b1-lean-the-rule`'s "the cancellation identity is unwritten"). An index
injected into every session's context, carrying status tokens, gated by
nothing, is the worst of the state layers and the one no previous cleanup
touched.

HANDOFF's rot is real but secondary: 1,151 lines in which §"Starting a
fresh session" says no open thread needs immediate action, three hundred
lines below an entry listing a running job and four undecided items. The
fix is that **a claim lives in one file, the file says what kind of thing
it is, and changing kind is an explicit move** — with the narrative
demoted to an append-only chronicle.

## Why attempt four survives

Three derived-index layers have already died here: ROADMAP.md (78602f8),
the results map (memory says don't recreate), and the results dependency
map (deleted at your request, HANDOFF:1023, after producing two real
findings). All three were *derived* — they restated what other docs said,
so they were maintenance cost with no authority.

These tables are **authoritative**: a row is not a summary of the primary
doc, it is the only place the answer exists. Landing this with the old
status headers left in place makes it attempt four at a derived index.

The rule is *one register per kind, named* — not "no status anywhere",
which would destroy working machinery. The registers: these three tables
for thread state; `polyplets/PROOF-STATUS.md` for Lean, `#guard_msgs`-
enforced; `paper/verify_claims.py` and `verify_technical_report.py` for
numeric claims; `oeis/SUBMISSION.md` for submission waves. Everything
else points and carries no status of its own — plan-file closed headers
(`docs/king-twigs-plan.md` has one, HANDOFF:62), results-file labels,
memory tokens, chronicle status language. The test of whether the rule
bites is `results/triangle-salvage.md`, "the index of what survived, with
verification labels and remaining work per item" (HANDOFF:302): a live
derived per-item status index of exactly the kind being replaced.

## Part A — three files, by kind

`state/hypotheses.md`, `state/facts.md`, `state/operations.md`. Plain
markdown tables, one gate. A claim appears in exactly one; promotion is a
move, and the move is the audit trail.

### A0. The thread name is the join

Every row carries the thread's short evocative name — a join column, not
a key, since one thread contributes rows to all three files. Naming is
already the practice; the rule is worth writing down because the names
do retrieval work and not just mnemonic work: they are unique tokens in
an unpolluted namespace, so `grep Confetti` returns the brief, the
results file, the runner, the tmux window and the commits with no false
hits. That is what makes a three-file split navigable rather than three
places to look.

The name is minted at thread birth, before the first artifact, and
appears in every artifact the thread creates (file name or header, commit
message, tmux window, job directory). Renames happen — B1 became Motley —
so every row carries an `aka` column, appended to and never cleared, and
the gate rejects an `aka` colliding with a live name. Without it the grep
claim is already false: `grep B1` and `grep Motley` return disjoint
halves of one thread. No opaque integer IDs; an identifier that doesn't
grep buys nothing here.

### A1. `state/hypotheses.md` — what we believe

Columns: thread; statement; status (OPEN / SUPPORTED / REFUTED); evidence
pointer; **what would settle it**, the field that prices the next
experiment; and **picture**, for an insight you can see but not yet
state, labelled so it is not mistaken for a claim. Numbers here are
conjectural by construction. Refutation narrows the statement in place
and the row records the narrowing; quiet deletion is the failure mode
this file exists to stop.

A closing hypothesis leaves a one-line tombstone naming the `facts.md`
row it became, and that row names the tombstone back. The pairing is the
enforceable form of "a claim lives in one file": promotion *rewords* the
statement — "rank = A034299 (nine points)" becomes "rank = A034299,
two-source, receipt X" — so no string comparison across files detects the
duplicate, and prose similarity has no business in a fail-closed gate.

### A2. `state/facts.md` — what we know

Columns: thread; statement; **tier** (proved / two-source / single-source
/ measured-once, the existing vocabulary); receipt pointer(s), which must
exist and be non-empty; `checked` date; **door** (yes/no), since a proved
theorem and a dead end are both facts and the gate otherwise cannot tell
which owes the closed-thread fields; and the tombstone key.

The tier is the transition rule, mechanical rather than advisory: an
agent may write `measured-once` or `single-source` unaided, `two-source`
requires the receipt field to name **two** paths and the gate counts
them, `proved` requires a proof-doc pointer. The discipline behind it is
that a shared-enumeration bug is closed only by independent
reimplementation; the gate enforces the arity, since it cannot know who
wrote what.

The `checked` date is read by the gate or it goes: a `single-source` or
`measured-once` row over 14 days stale is an error, those being the tiers
that rot. Migration rows may carry `checked: —`, but the gate errors if a
`—` row is cited from a hypothesis or the chronicle — which turns
"verified lazily on first citation" into a checked rule.

### A3. `state/operations.md` — what is running or owed

One row per: running job (box, tmux window, PID, a **local** receipt path
— last synced heartbeat snapshot — and when it was checked); queued or
parked work (QUEUED / PARKED / BLOCKED, with the measured price to start
or restart); pending sign-off; verification debt (claim, tier it lacks);
machine condition (ayr dark since …). Rows sit in your priority order,
which beats a priority column you would have to maintain. The only file a
session must read before touching a machine.

One standing row, never closed: **read every Lock and Converts-to field
across all closed threads in one sitting.**

### A4. HANDOFF.md becomes a chronicle

Append-only dated entries, narrative allowed, **no status language** —
every "X is DONE/RUNNING/DEAD" belongs to a table. Old content stays as
history, with one exception that is not optional: the tail holds live
*directives*. Line 1134's "No open thread needs immediate action" is a
false instruction; HANDOFF:492's "IN FLIGHT: percell32 on gympie, driver
PID 51511" is an operational claim about a machine now under a hard ban.
One pass strikes or banners every directive and in-flight sentence.
Per-thread history is the primary doc's own append-only log section, with
`git log -S<name>` as fallback; a per-session chronicle is no substitute.

### A5. MEMORY.md stops carrying project state

Its "Project state & results" and "Banked technical conclusions" blocks
are where all three incidents came from. A memory hook may say what a
thread is and where its row lives; it may not say whether it is open,
closed, done, running or next. Each such entry becomes a pointer or goes.
Two entries break the moment this lands and are migration items:
`roadmap-pointer` ("HANDOFF.md is the live state") and CLAUDE.md's
pointer to HANDOFF.

Three mechanisms, strongest first.

**The schema, which prevents the class at creation.** The memory schema
in your global CLAUDE.md has a `project` type — "ongoing work, goals, or
constraints" — the category whose purpose is to carry state, and the one
all three incidents came from. Redefine it so a `project` entry records
the shape of an obligation and points at its row, rather than asserting
whether anything is open, done, running or next. A schema that cannot
express status beats any check that catches it afterwards, and it makes
the two below a backstop rather than the defence. Your file, so this is a
proposal with the reason attached, not something a gate imposes.

**One permitted line shape, not a vocabulary blacklist.** The migration
is rewriting these entries anyway, so give them a single form —
`[[thread-name]] — <kind>, row in state/<file>.md`, kind from a closed
set — and let the gate parse against it, resolving the name against the
tables and failing any body line that does not match. A blacklist would
leak: the informal status vocabulary here runs to thirty-odd words
(DONE, GREEN, BANKED, LANDED, DEAD, NO-GO, WIRED, UNRUN …), and the entry
that actually caused an incident contains none of them — "the
cancellation identity is **unwritten**" is a plain present-tense
assertion that stopped being true. A blacklist passes it; a shape rule
fails it, because the danger is free text about the world in a file that
is injected into every session and checked by nothing. This binds only
the project-state and banked-conclusions blocks; `feedback`, `user` and
`reference` entries are untouched.

**Found or declared absent, never silently skipped.** The memory path
embeds the working directory as a slug
(`~/.claude/projects/-Users-jasonp-src-polyominoes/memory/`), so a repo
move, a second clone, or a rename makes the directory vanish and an
opportunistic check go green forever — on the box where sessions actually
run, guarding the class that actually bit us. So: directory present,
check it; absent and the box is declared in the machine-condition rows of
`operations.md`, skip and say so; absent and undeclared, **red**. That is
fail-closed against the one failure mode that would otherwise be silent.

The residual limit is then narrow and worth stating exactly: the gate
cannot check a memory directory on a box it is not running on, and the
third mechanism makes that condition declared rather than invisible.

### A6. `make gate-state`, fail-closed

Extends `tests/gate_citations.py`, which already checks that every cited
repo path exists — written 2026-08-06 for this exact failure. No second
path checker. New checks: vocabularies exact; the tombstone↔fact pairing
bijective, no orphan and no fact claimed twice; tier arity; each name
resolving to one primary doc; no `aka` collision; every `door: yes` doc
carrying Lock, Reopen and Converts-to, and every parked doc those plus
Price, all **with non-empty bodies** (precedent: `check_receipts.sh`
requires an in-tree non-empty path on the same line); dates parse; the
staleness errors above; memory entries against the A5 shape rule, with
the directory found or declared; and status vocabulary in any tracked
markdown file outside the four named registers — best-effort, that one,
since no line shape can be imposed on prose docs, which is exactly why
the memory check gets a shape rule instead.

Liveness of a remote process is a session-open action, never a gate
invariant — the gate runs on ayr/dalby under the gympie ban, ayr is dark
as I write this, and a gate that reds on a power cut gets commented out.

RED fixtures: missing path; orphan tombstone; fact claimed twice; a
`two-source` row naming one path; a door doc with headings and nothing
under them; an `aka` collision; a 15-day-stale `single-source` row; a
`checked: —` row cited from a hypothesis; a memory body line that is
prose rather than a pointer; an undeclared missing memory directory.

Non-failing output every run: every Lock and Converts-to line in the
tree, grouped. That listing is the mechanism behind heuristic 1.

A commit touching HANDOFF.md must touch `state/*.md`. Prose is the write
a session makes naturally; second writes get dropped, so they have to be
one act.

### A7. Session discipline

The whole of it: a session opens by reading the three tables — not the
chronicle, not memory — before proposing work.

An earlier draft also required a planning paragraph before executing,
copied from Li et al. Cut, and not merely for register: they added it to
an *unsupervised harness*, as a stand-in for an operator not in the loop.
This project has the operator, and in their own run the two decisive
interventions were both his kind. The function survives as heuristic 5,
fired by an event rather than performed every session.

## Closed threads and parked work: required fields

In the primary doc, for **every** closed thread, win or loss, and every
parked row:

- **Lock** — why it stopped: theorem / measurement / budget, with the
  receipt pointer.
- **Reopen** — the named condition under which it reopens, or "none". A
  reopened row appends and never overwrites the prior Lock; the record of
  the narrowing is the asset.
- **Converts to** — what the obstruction becomes if made universal.
- **Price** (parked only) — the measured cost to restart.

Required on wins as well as losses: charging only for the honest label
leaves "leave it OPEN forever" free, which re-creates the
flattering-genre regression this exists to stop.

**Converts to cannot be filled by the closing session, and the design
must not pretend otherwise.** In the Li et al. run the six failures were
recorded and tagged correctly, the response was to open a seventh, and
the dualization came from the operators twice — "the run had accumulated
exactly the required evidence without making the connection." The pattern
is invisible from inside one thread, hence the standing cross-thread row
in A3 and the grouped Lock listing in A6. Without a mechanism the field
is write-only, and the guardrails below say to delete such a field.

## `docs/research-heuristics.md` (planned, not yet written)

Trigger → action. Admission rule: **every entry names a repo incident
where following it would have changed the action taken.** Literature
supplies phrasing and citation, never warrant. Entries are triggers
rather than lessons because knowing a strategy and knowing to use it in
the moment are different things (Mason–Spence), and only the trigger form
survives the gap. Cap 12; eleven ship — a Pólya "solve a special case"
entry was cut rather than re-sourced when its incident turned out not to
fit its own trigger. The cap is a ceiling, not a quota.

1. **The same obstruction closes three attempts, across threads → stop
   searching; try to prove it, then ask what it dualizes to.** Fires off
   the grouped Lock listing, not from inside a thread. (Rook round and
   king twigs both ended this way — by your judgement, no rule firing,
   which is the gap the entry closes. Phrasing: Li et al. §4.)
2. **Counterexample arrives → classify before retreating:** monster (the
   definition needs care), exception (the statement needs a hypothesis),
   refutation (the broken lemma is the discovery). (Coin Lift G2 was a
   monster — "the Z/4 free rank" was identically the GF(2) rank; the
   crude-bound proof in `polyplet-upper-bound.md` was a refutation, its
   frontier missing 65% of n=8. Phrasing: Lakatos 1976.)
3. **A row's next action unchanged for three sessions → answer the
   control questions in the chronicle:** what am I doing, why, how does
   it serve the goal, what will I do with the result. No answer to any:
   PARKED with a price. (Phrasing: Schoenfeld 1985.)
4. **Choosing between directions → name what each buys before comparing
   effort:** a term, a technique, a closed door, a shorter proof. A sharp
   restricted result loses to a general one unless the sharpness is the
   point. (Li et al. record this misprioritization; ours is the
   claim-pruning filter, name the sentence that gets shorter. Tao 2007.)
5. **Before writing a multi-lane brief → measure the quantity the goal is
   stated in terms of, alone, first.** Your own lesson from the rook
   round: the controls were aimed at transmission failures while the real
   failure was target selection, and the base-anatomy audit ran in
   parallel with three lanes that depended on its answer. (HANDOFF:289.)
6. **A candidate list too long to read → cut it to ~5% with structural
   filters before reading any of it.** Judgement goes to the survivors.
7. **The same constant appears in two derivations → suspect a theorem.**
   Explain it or file it as a hypothesis before building on either.
   (D0 = 5⁵/4⁴.)
8. **A recognizer or fit fails → enlarge the field and re-scan every
   natural normalization** before writing "not recognizable".
   (a ∈ ℚ(√3); 118/27 as a normalization artefact.)
9. **Special case closes, general stalls → name the exact ingredient that
   fails to generalize.** That sentence is the next target. (Klazar D_A
   ceiling; depth-1 → depth-j.)
10. **Massive cancellation observed → the cancellation is the object.**
    Find the mechanism, stop bounding terms. (ρ-cancellation;
    b + (q−b) = q.)
11. **Before designing a reduction, encoding, or fit → do the
    impossibility arithmetic first:** the counting floor for a
    construction, degrees of freedom against data points for a fit. If
    underdetermined, declare derivation-or-nothing immediately. (R1-D β
    floor; Coin Lift's mod-p floor; the depth-tower dead end.)

## Migration, cost, and the trial

Scoped so the expensive half is the half that matters: OPEN, RUNNING and
PARKED threads get a row verified against their primary doc at creation;
closed threads get `checked: —` and are verified lazily on first
citation. Then the status strip from everything outside the four named
registers — plan-file closed headers, results-file labels,
`triangle-salvage.md`'s per-item index — the MEMORY.md pass, the
chronicle-tail directive pass, and the gate with its fixtures.

The memory pass needs one disposition rule or it stalls on the first
entry that is half practice and half state: the state half becomes a
pointer in the A5 shape, and the content half either moves into the
primary doc it describes or stays as `feedback`, which the shape rule
does not bind. Declaring ayr and dalby as boxes with no memory layer is a
three-line edit in the same commit. A day-plus: the typing is an evening, the verification is the
work, and comparable jobs here (the report trim, the salvage index) each
ran a day and double-digit commits.

**The migration produces the baseline** — a written count of stale
entries found while verifying rows, with a second count taken the same
way at the end. It costs nothing extra and it is the only honest
measurement of how bad the current state is. Between them, each session
records in the chronicle any row it found wrong and fixed. A session that
acts on stale state without noticing emits no signal, so "did anyone act
on stale state?" is unfalsifiable and is not the review question.

The recurring cost is not the file count, it is **writes per session**: a
session that runs a job and learns something touches operations.md,
facts.md and the chronicle where HANDOFF took one file. Two are one-line
edits, the third is the write it was making anyway, and the commit tie
makes them one act — but it is three writes, and rot comes from the
writer's cost, not the reader's.

## Anti-overengineering guardrails

Plain markdown; no YAML, no database, no per-session tooling; the gate is
one script extending an existing one; nothing writes the tables but a
human or an agent with the primary doc open. If a field is unfilled for
three rows running, delete the field, not the habit.

Deliberately **not** copied from a bug tracker, and not to be added later
without a new argument: assignee, milestone, component, dependency graph,
attachments, configurable workflow, per-field permissions, integer IDs,
priority as a column. What is kept is the short list that earns it: a
join column, an append-only history, a transition rule the gate can check,
and required fields on close.

## Contested points

Empty, and not by neglect. Two adversarial rounds produced twenty-odd
objections; all were adopted, adopted with a variation the reviewer
accepted, or overtaken by a revision that predated the round. The six he
drafted for this section are all doc text now, and he withdrew his own
integer-ID objection. Two decisions recorded so they are visible rather
than settled by silence:

- **Integer IDs, declined.** Renames are real, but `aka` handles them,
  and an identifier that does not grep forfeits the retrieval property
  that motivated naming threads at all.
- **The memory schema change (A5) is yours, not the gate's.** It is the
  strongest of the three mechanisms there, because it prevents bad
  entries at creation rather than catching them afterwards, and the other
  two are a backstop to it. Nothing in this proposal edits your global
  CLAUDE.md; if you decline the redefinition, the shape rule and the
  found-or-declared check still stand on their own.
