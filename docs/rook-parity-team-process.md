# Rook-parity team process — the argued record

2026-08-13. Written before any dispatch, against the goal in
`docs/rook-parity.md` and the evidence in `docs/triangle-postmortem.md`,
`docs/agent-types.md`, `docs/r3-job-dispatch.md`,
`docs/skeptical-reader-standard.md`, and `~/.claude/skills/run-a-team/SKILL.md`.
Both sides argued for each control, then a ruling; the recommended set and a
round-1 dispatch sketch are at the end.

## The frame: what kind of failure the triangle campaign was

Two distinct failure classes, and they pull the process argument in opposite
directions:

- **Rounds 1–2 were target-selection failures.** Honest, rigorous, ~0 bits.
  Round 1's synthesis said so itself (`triangle-postmortem.md:51-53`); round 2's
  premise died to two lines of arithmetic already in hand that nobody ran at
  brief time (`triangle-postmortem.md:129-134`). No receipt gate, registrar, or
  ledger touches this class. The only controls that do: the pre-launch
  adversary (kills the false premise) and the charter rule (bans "find a
  relation" as a mission).
- **Rounds 3–4 were transmission failures.** The lanes were honest
  (`triangle-postmortem.md:237-240`); the loss was "between the deliverable and
  the summary… above the lane, not inside it" (`results/r4/r4-adv-ind.md` §8,
  quoted at `triangle-postmortem.md:96-99`). Every status drift had the same
  sign — unrun upgraded to run (`results/r4/INSTRUMENTS.md:4-8`). This class is
  what the receipt gate, ledger, and queue-close controls address.

The counterweight in the lead's proposal is therefore right as far as it goes:
process weight was not the binding constraint in rounds 1–2, and eight new
controls do nothing for a round aimed at a worthless target. But it
under-credits one fact: **for rook parity, half the target-selection work is
already banked in the goal file itself.** `rook-parity.md` is what a
brief-adversary pass produces — the 2.67 pin desk-refuted before launch
(`rook-parity.md:30`), the transport family killed by arithmetic
(`rook-parity.md:83-86`), the gates numeric (`rook-parity.md:106-123`), the
kill condition written ("g ≫ 6 kills the tower", `rook-parity.md:111-113`).
The triangle campaign never had a goal document of this quality; it had a
mission sentence and four briefs. So the honest pricing is: target selection
was the binding constraint *and it has already been paid for once*; the
process controls exist to keep rounds 3–4's failure class from spending that
down. Both matter; neither substitutes for the other.

## Mechanical vs disciplinary — the test

A control is **mechanical** if a machine fails closed without anyone
remembering anything: a `make` target that exits nonzero, an assertion that
halts a pipeline. It is **disciplinary** if a person must comply, and the
record's verdict on disciplinary controls is uniform: they were waived, every
time, usually by the lead, usually in the same file that stated them —
round 1's "the correct call is stop" hedged in the next sentence, round 2's
go/no-go converted to a go, round 3's dry-triage stop withdrawn by instruction
(`triangle-postmortem.md:109-117`). The adversary-on-brief pass was codified
in `docs/agent-types.md:67-68` during round 4 and never used
(`triangle-postmortem.md:135-138`). The no-receipt rule was violated in the
commit that created it (`triangle-postmortem.md:170-174`).

Writing a rule down is not a control. Of the lead's eight, only #3 (the make
gate) and parts of #4 are mechanical as proposed. #1, #2, #5, #7, #8 are
disciplinary in disguise — argued individually below — and the honest design
question for each is whether it can be *made* mechanical, and at what cost.

## The eight, argued

### 1. Controls as starting conditions in run-a-team / agent-types.md

**For.** Five-whys #4 is exactly this: every control the campaign ended with
was invented mid-round, after the failure it addresses, and no round started
with what the previous round had paid for (`triangle-postmortem.md:100-108`).
The skill file is the one artifact guaranteed to be read at the next launch.
Cost: one lead-hour, once.

**Against.** A doc is the weakest control form. The dispatch protocol existed
before round 4 and round 4 still banked a result across the gap round 3 had
named (`triangle-postmortem.md:137-139`). Growing the skill file also has a
reading cost: every agent brief inherits more boilerplate, and the
no-filesystem-scans memory already shows boilerplate creep is real.

**Ruling: ADOPT, minimally.** The skill gets the starting-condition list
(gate built, ledger open, INSTRUMENTS.md open, brief-kill pass done) as a
pre-launch checklist — a dozen lines, not the controls' full text. It is
disciplinary; its function is to make the mechanical controls exist before
hour zero, not to substitute for them.

### 2. Split the lead; standing registrar owns queue + INSTRUMENTS.md, sole writer of status lines

**For.** The strongest single finding in the postmortem is that the lead was
the failure surface: author, dispatcher, and synthesizer, "the one role
auditing everything was the one role nothing audited"
(`triangle-postmortem.md:141-143`), and the status bias was specifically the
lead's (`results/r4/INSTRUMENTS.md:4-8`). Separating custody of the status
ledger from the role that benefits from optimistic status is standard
segregation of duties.

**Against.** Three points, and together they win.

- *At 8 agents the registrar is 12.5% of the roster doing clerical work.* The
  campaign's binding resource was lead attention and agent time
  (`triangle-postmortem.md:200-209`); a standing agent that generates no bits
  is expensive precisely in that currency.
- *The registrar is another transmission hop of exactly the class that
  failed.* The r4 loss was between deliverable and summary; a registrar
  transcribing lane reports into status lines reproduces that hop with a
  different author. The fix that actually ended the drift was not a person —
  it was the receipt column: "no log path ⇒ WRITTEN, UNRUN, and no brief may
  describe it otherwise" (`results/r4/INSTRUMENTS.md:10-11`). That rule is
  mechanizable (#3); once it is a make gate, the registrar's status function
  is redundant — anyone can write the line, because the gate rejects the line
  the receipt doesn't support.
- *The queue-custody function is likewise covered*: the queue is append-only
  with a close protocol (#8), and the roster ledger (#4) is appended by the
  dispatcher at spawn — one actor, one line, no custodian needed.

Note also this proposal is disciplinary in disguise: "the lead may cite
status, never author it" is a rule about what the lead writes, enforced by
nobody. The mechanical version is a scanner that runs over the lead's
synthesis too — which is #3 with wider scope.

**Ruling: REJECT the standing registrar at this scale.** Adopt the narrow
core: status is quotable *only* as a copy of an INSTRUMENTS.md row, the
scanner (#3) runs over briefs and syntheses as well as deliverables, and any
PROVED/RUN/GREEN token in a lead-authored file needs the same adjacent
receipt. Revisit a registrar only if a future round legitimately needs >12
agents, which #6 currently forbids.

### 3. Receipts as a make gate, fail-closed, red-first

**For.** This is the only proposal that is mechanical as stated, and it
targets the measured bias directly. The evidence that discipline alone fails
is total: gate claims without logs "twice charged and once repeated *after*
the fix" (`triangle-postmortem.md:164-167`); the "encoding layer PROVED"
claim carried no receipt and landed in the same commit that created the
no-receipt rule (`triangle-postmortem.md:170-174`). INSTRUMENTS.md "ended
the drift on contact" (`triangle-postmortem.md:293-296`) but only for files
that quoted it. A scanner that fails `make` when a status token has no
adjacent non-empty in-tree log closes the loop without anyone's memory. The
planted-claim mutant is the red-first standard the project already holds
gates to (quality-gates memory; `docs/engineering-standards.md`).

**Against.** Two real limits, neither fatal.

- *"Log exists and is non-empty" is a weak predicate.* The salvage addendum
  is the proof: the lean2 gate battery's first-ever run failed on its own
  bug — gate E read a correct output as zero sorries because of an
  ASCII-vs-backtick pattern (`triangle-postmortem.md:329-338`). A green log
  from a gate that never ran red is not evidence; a non-empty log from a
  broken gate is worse. The scanner verifies *that a receipt exists*, not
  *that the receipt says what the claim says*. The cross-ISA row shows the
  same gap from the other side: a real result with a "WEAK RECEIPT"
  (`results/r4/INSTRUMENTS.md:26`).
- *Token scanning has a false-positive surface* — "RUN" and "GREEN" occur in
  prose about history, in this very file. Scoping (results/<round>/ and
  briefs only; token in a status position, e.g. table cell or `status:`
  line) and an allowlist annotation (`status-quote:` for historical mention)
  handle it, at the cost of a convention.

**Ruling: ADOPT — highest-value item on the list.** Build it before round 1,
red-first: the planted-claim mutant (a deliverable asserting RUN with no
log) must fail the gate before the gate is trusted. Scope: all files under
`results/<round>/` plus the round brief. And keep the division of labor
honest in the brief text: the gate proves a receipt exists; the numbers
adversary still reads the receipt. The gate exists so the adversary reads
logs instead of hunting for their absence.

### 4. Roster by construction — dispatch ledger at spawn

**For.** Nine agents ran twelve hours past their obituary and were found by
accident (`triangle-postmortem.md:255-258`); the wind-down miscounted its own
team three ways (13 dispatched / 18 listed / 19 real,
`triangle-postmortem.md:167-169`); agent time — the binding resource — has no
accounting anywhere in the records (`triangle-postmortem.md:200-203`). One
appended line at spawn (id, type, model, time) makes census and accounting
free, and postmortem item 9 asks for exactly this. Cost ≈ zero.

**Against.** It is disciplinary at the append: the dispatcher can forget the
line. But dispatch is a single actor performing a deliberate act, the line
is written at the same keystroke as the spawn, and — the closing move — it
can be made mechanical at the *other* end: the wind-down's "team closed"
claim is valid only when the ledger matches the TaskStop-enumeration census
(postmortem item 7, `triangle-postmortem.md:308-311`), and that match is a
check a script runs. A missing ledger row then surfaces as a census
mismatch, fail-closed.

**Ruling: ADOPT**, with the census-match rule attached; file/stop times and
model per agent appended at wind-down, which retires postmortem item 9's
accounting half in the same stroke.

### 5. Pre-launch adversary on the brief, kill authority, evaluator = jasonp

**For.** The best-evidenced control in the record. Round 2's premise was
desk-refutable at cost zero; round 3's brief "would have killed four of six
lanes" (`docs/agent-types.md:67-68`, `triangle-postmortem.md:283-288`). The
second why-chain is explicit: negatives weren't binding because no round's
premise was adversarially reviewed before launch
(`triangle-postmortem.md:127-134`).

**Against.** Three objections, two of which reshape it.

- *It would not have saved rounds 1–2's real problem.* An adversary chartered
  to check premise arithmetic passes round 1's brief — the arithmetic was
  fine; the target was worthless. If this control is adopted only in its
  postmortem form, the counterweight scenario (impeccably audited, wrongly
  aimed) is exactly what it produces. The fix is in the charter: the pass
  asks *two* questions — is the premise true (desk arithmetic, citations
  readable on the branch, exposure numbers re-run), and **does the chartered
  deliverable move a gate in `rook-parity.md`** (which gate, by how much,
  and would a total success still leave the bar untouched). The second
  question is this campaign's analogue of the skeptical-reader standard's
  "where the rigor is aimed" (`docs/skeptical-reader-standard.md:16-17`).
- *Kill authority vs evaluator: who actually disposes?* Giving an agent kill
  authority with jasonp as evaluator is ambiguous in the case that matters —
  a kill the lead disputes. Resolution: the adversary's KILL verdict blocks
  launch mechanically (the launch checklist requires a PASS file); the lead
  may appeal to jasonp; jasonp is not a routine gate on every launch, only
  the appeal path. This respects the postmortem's "the lead proposes,
  someone else disposes" (`triangle-postmortem.md:289-292`) without making
  him read every brief.
- *Latency.* One agent-session and some hours per round. Against the record
  — round 2's entire cost, four of round 3's six lanes — this is the
  cheapest insurance on the list. Under one-round-per-day cadence the
  latency is absorbed anyway.

**Ruling: ADOPT, with the two-question charter and the appeal structure.**
This is disciplinary at exactly one point — the lead must not launch without
the PASS file — so put the PASS-file check in the same pre-launch script
that #3 and #4 hang off, making the waiver visible even if not impossible.

### 6. Hard cap of 8 agents per round

**For.** The honest rounds were 7 and 4 agents; the drift, census, and
receipt failures arrived with 14 and 19 (`triangle-postmortem.md:33-36`).
The lead's verification capacity is the real constraint — round 3's
synthesis was overtaken by a scout 52 minutes later because the lead
couldn't keep up with 14 lanes' output (`triangle-postmortem.md:86-90`).
And the counterweight argues *for* this control: fewer agents force target
selection over coverage. A cap is also self-pricing — it costs negative
agent-hours.

**Against.** The number is arbitrary, and the naive reading damages the one
mechanism that demonstrably paid: round 3's two best findings were queue
successors filed after lanes closed (`run-a-team` SKILL.md:57-59), and the
skill's re-dispatch rule ("an agent that has finished still holds its lane's
context and is the cheapest thing on the board", SKILL.md:66-68) is how a
small roster covers a queue. A cap on *spawns* that also counted
re-dispatches would push the lead back toward the round-4 pathology of
spawning nineteen fresh readers (`triangle-postmortem.md:194-200`).

**Ruling: ADOPT as 8 spawned agents per round, hard;** SendMessage
re-dispatch of an already-spawned, filed agent is free and preferred. The
number is defensible, not sacred: rounds 1–2 fit in it, and the desk day
below needs five.

### 7. Charter = machine-checkable deliverable, never "find a route"

**For.** "Find a relation that checks a(40)" bought four rounds of nothing;
the two rounds chartered on open search produced the substitution the
skeptical-reader standard was written to stop
(`docs/skeptical-reader-standard.md:12-17`). Rook parity is unusually
chartable: gates 0–3 are numeric (`rook-parity.md:106-123`), so "file X
exists, gate log Y green" is genuinely available for the compute rounds.

**Against.** Read strictly, this bans legitimate work the goal file itself
charters. The transport-obstruction lane — "state precisely what a
size-preserving king→rook reduction must do to the Motzkin cut information,
or exhibit the obstruction" (`rook-parity.md:88-90`) — is not machine-
checkable, and it is wanted. The desk day's base-anatomy audit produces a
number, not a green log. And round 3's one product came from a lane the
brief gave no candidate list at all (`run-a-team` SKILL.md:25-27) —
open-endedness inside a lane is where the generativity lives.

**Ruling: ADOPT, amended.** Every *round* charters a falsifiable deliverable:
a named file whose absence is failure, machine-checkable where a gate exists
(all compute rounds here), a specific claim-or-obstruction file where not.
"Find a route" is permitted as one bounded lane inside a round, never as the
round's charter. The distinction that matters is round-level: a round must
be able to fail.

### 8. Queue as sole inter-round carrier; late deliverable reopens the queue

**For.** The 9-minute ordering failure cost round 4 a 30–75x premise error
(`triangle-postmortem.md:86-90`), and postmortem item 4 is this control
verbatim (`triangle-postmortem.md:297-300`). Synthesis narratives were the
proven contamination channel — stale INV-8, stale 43.84%
(`triangle-postmortem.md:60-65`).

**Against.** "Reopens the queue" is a liveness hazard: an agent that keeps
filing keeps the round open, and the round-4 spin jobs were still in flight
at *salvage* (`triangle-postmortem.md:339-342`) — a literal reading would
have held the round open for days. Also, queue rows are terse; the lead's
synthesis has legitimate judgment content. The fix is not to ban synthesis
but to demote it: it may argue, it may not be *cited* as a premise.

**Ruling: ADOPT with a close protocol instead of reopening.** Queue close is
an event that happens only after the census check (#4) confirms every agent
stopped or explicitly handed off (in-flight jobs get an IN FLIGHT queue row
with a waiter attached, as `results/r4/INSTRUMENTS.md:27` correctly did).
Anything filed after close lands as the *next* round's first queue rows —
same guarantee, no zombie rounds. Next round's brief may cite queue rows and
receipts; a synthesis sentence with no queue row behind it is not a
launchable premise, and the brief-kill pass (#5) checks exactly that.

## The postmortem's ten, where they differ

Items 1, 3, 4, 7, 8, 9, 10 are absorbed above (#5, #3, #8, #4, dispatch
protocol standing, #4-accounting, and the keep-list respectively). Three are
not, and all three are adopted:

- **Item 2, stop rules the lead cannot waive.** Not in the lead's eight, and
  it is the deepest cut in the record — all three stop failures were waiver
  failures, not detection failures (`triangle-postmortem.md:109-117`).
  Mechanical form for this campaign: kill thresholds are *numeric and
  pre-registered in the brief before the measurement runs* (the postmortem's
  go/no-gos died because the threshold and the verdict were written by the
  same hand in the same file, after the number existed). "g > 6 measured on
  the k ≤ 9 fit kills the tower" is written on desk day, before g is fit.
  Converting a fired kill into a go requires jasonp, in so many words.
- **Item 5, controls run before results bank.** Sharper than #3: it demands
  the RED control *run red* before the instrument's output is quotable, not
  merely that a log exist. For rook parity this is already chartered — the
  NW-stencil RED at gate 1 is mandatory (`rook-parity.md:117-120`) — and it
  composes with #3: the gate script for a(30) requires both the match log
  and the stencil-drop failure log. Adopted as written.
- **Item 6, one round per day.** Not in the lead's eight. Round 4 opened
  four hours after round 3's brief, before round 3's lessons were filed
  (`triangle-postmortem.md:106-108`), and every mid-round invention was a
  repair a slower cadence would have made a starting condition
  (`triangle-postmortem.md:304-307`). Disciplinary, but the waiver is
  jasonp-visible (a round opening is a commit), which is the enforcement
  that actually worked in this campaign — both stops that held were his
  (`triangle-postmortem.md:276-278`). Adopted.

## Missing from both lists

**Repatriation of remote results.** The campaign's largest result sat
untracked on dalby for two days, matching no committed blob; a disk failure
would have erased the only independent recount of 21.64% of a(40)
(`triangle-postmortem.md:259-264`). Neither list touches it, and
`docs/r3-job-dispatch.md` §"What the lead owes back" returns numbers and a
log path but not the artifact. Rule: job completion includes rsync of
results + logs into the repo working tree in the same sitting; a job row is
not DONE until its artifact has a local path. Cheap, mechanical at the
INSTRUMENTS.md level (receipt must be an *in-tree* path — #3 already
enforces in-tree, so this closes by making the job protocol say so too).

**A campaign-level stop, distinct from round-level kills.** Round kills
(g > 6, gate 1 slope fails) are covered. Nothing says when the *campaign*
ends short of the goal. The triangle record shows the failure shape: each
round's escape hatch became the next round's brief
(`triangle-postmortem.md:115-117`). Rule: a round that advances no gate
(0–3) and banks no negative-map entry is a strike; two consecutive strikes
trigger a mission review with jasonp instead of a round 3. The gates make
this checkable — "advances a gate" means a gate log, not a narrative.

**The desk day is not a round, and should not be run as one.** The
"First questions" day (`rook-parity.md:125-137`) has no generators, no blind
seed (there is no candidate list to withhold yet), no waves, and a
dependency structure a wave design would break: question 1 (base anatomy)
*sets the measured clause of the bar itself* (`rook-parity.md:51-56`), and
the kill threshold for question 2 must be registered before question 2's fit
is run. Structure: sequential-ish scouts plus one adversary, all Fable,
charter = a single file (`docs/rook-parity-bar.md` or similar) containing
the numeric bar, the g fit with basis labels, the Hankel verdict, and the
registered kill thresholds for round 2. INSTRUMENTS.md, the roster ledger,
and the receipt gate exist from this day — `rook-parity.md:138-141` already
says controls apply from hour zero, and the desk day is hour zero.

**Model policy × quota, sequenced.** The postmortem names the trap: Fable at
97% forced round 4 onto Opus in exactly the round where the fail-closed
checks didn't exist (`triangle-postmortem.md:204-209`), and item 9's fix —
"the checks exist *first* or the round waits" — is a scheduling constraint,
not a preference. Consequences: (a) the receipt gate (#3) is built before
round 1, when quota pressure is zero, so the Opus-with-checks option exists
before it is needed; (b) role policy is fixed now: brief-kill adversary,
numbers adversary, and synthesis inputs are Fable, always — these are the
judgment roles the standing rule (delegate-to-opus memory) protects;
generators and mechanical scouts may run Opus once the gate is green;
(c) wave staggering respects the 3h window per the standing memory — desk
day is one wave and immune; round 2+ briefs state the wave plan against the
window explicitly.

**The registrar question, answered directly.** Not worth its cost at 8
agents. Its two functions decompose: status custody is subsumed by the
mechanical gate (#3, with lead-authored files in scope), and queue/census
custody by the ledger + close protocol (#4, #8). What remains — a human hop
between deliverable and status line — is the failure class of rounds 3–4
with a new author. If a future campaign genuinely needs >12 agents, revisit;
under the cap, it cannot.

## RECOMMENDED SET

| # | control | ruling | reason |
|---|---|---|---|
| 1 | controls as starting conditions in skill/docs | **ADOPT** (as a short pre-launch checklist) | makes the mechanical controls exist at hour zero; a doc alone proved insufficient in r4 |
| 2 | registrar as standing status/queue custodian | **REJECT** | 12.5% of roster for a transmission hop of the class that failed; #3+#4 mechanize both functions |
| 2' | status quotable only from INSTRUMENTS.md rows; scanner covers lead-authored files | **ADOPT** | the part of #2 that survives; mechanical via #3 scope |
| 3 | receipts as fail-closed make gate, red-first, planted-claim mutant | **ADOPT** | the one mechanical control; targets the measured bias; built before round 1 |
| 4 | dispatch ledger at spawn + census-match at wind-down | **ADOPT** | census and agent-time accounting at ~zero cost; fail-closed via the census match |
| 5 | pre-launch brief adversary with kill authority | **ADOPT** (two-question charter; PASS-file blocks launch; jasonp = appeal, not routine gate) | best-evidenced control; the target-value question is what saves it from the counterweight |
| 6 | hard cap 8 per round | **ADOPT** (8 spawns; SendMessage re-dispatch free) | honest rounds fit; drift arrived with 14/19; protects the re-dispatch mechanism that paid |
| 7 | machine-checkable round charter | **ADOPT amended** | rounds must be falsifiable; "find a route" allowed as a bounded lane, never a charter |
| 8 | queue sole carrier | **ADOPT with close protocol** | close after census; late filings open next round's queue; no reopen/zombie hazard |
| PM2 | stop rules lead cannot waive | **ADOPT** | numeric thresholds pre-registered before measurement; fired kill → go needs jasonp |
| PM5 | RED controls run before results bank | **ADOPT** | composes with #3: gate requires the red log too; already chartered at gate 1 |
| PM6 | one round per day | **ADOPT** | cadence outran corrections four times; round-open commits make waiver visible |
| — | remote-result repatriation in job protocol | **ADOPT** (new) | B1 rows near-miss; receipt must be in-tree, so #3 enforces it |
| — | campaign stop: two gateless rounds → mission review | **ADOPT** (new) | prevents escape-hatch chaining; checkable against gate logs |
| — | model sequencing: gate before round 1; judgment roles Fable always | **ADOPT** (new) | the 97%-quota trap is predictable; remove the forced choice before it recurs |

Deferred: nothing. The registrar is rejected, not deferred — the revisit
condition (>12 agents) is unreachable under the cap.

## Round 1 of rook parity, agent by agent

**Pre-round (lead, in-session, before any spawn):**
build `scripts/check_receipts.sh` + make target, red-first — planted-claim
mutant deliverable must fail it; open `results/rook1/INSTRUMENTS.md` and
`results/rook1/LEDGER.md`; write the desk-day brief including the
pre-registered kill thresholds (g > 6 kills the tower; the measured-clause
threshold left explicitly TBD-by-R1-A per `rook-parity.md:56`); brief-kill
pass on that brief (R1-K below) before the scouts spawn.

Five spawns, all Fable, desk-only, `docs/r3-job-dispatch.md` binding (the
Hankel probe is the only lane likely to file a job request):

- **R1-K — adversary on the brief** (spawned first, alone). Two questions:
  premise arithmetic (the `rook-parity.md` numbers re-derived: the 84% cpu
  split, β = 1.61 bound, the three contradictory in-repo base claims at
  `kink-carry.md:46,69` and `ns_a40/PROVENANCE.md:19,25`), and target value
  (does each chartered deliverable move gate 0 or set the bar). PASS file
  required before wave 2 spawns.
- **R1-A — scout, base anatomy audit** (`rook-parity.md:126-128`). From
  existing run logs only: the incumbent's fitted per-term ratio over
  n = 24..30 with residuals, reconciling the 2.42 / 1.61 / 1.73
  contradiction; deliverable includes the proposed numeric measured-clause
  threshold for the bar. No compute beyond seconds-scale.
- **R1-B — scout, P_k tower feasibility** (`rook-parity.md:129-131`). Fit g
  from the severance records (k ≤ 9 measured, `severance-w1-anchor-cut.md`
  §Ceiling); survey state-space-reduction options past k = 10; overlap check
  against `docs/middle-kingdom-plan.md` before calling anything new. Reports
  g with MEASURED/EXTRAPOLATED labels against the registered thresholds
  (g ≲ 3 parity; 3 < g < 5.9 beats incumbent only; g > 6 kill).
- **R1-C — scout, rook Hankel ranks at small H** (`rook-parity.md:132-136`).
  Ground truth via `build/g2 --rook-bishop` (check `build/` first, per the
  g2 memory); seconds-scale on gympie or a job request to ayr, nothing in
  between. Verdict: does rook show the char-2 crack
  (`triangle-r3-involution.md` §2) or not, and does the answer change any
  king decision.
- **R1-D — adversary, transport obstruction** (`rook-parity.md:88-90`). The
  one chartered "find a route" survivor, run as its negative: state what a
  size-preserving king→rook reduction must do to the Motzkin cut
  information, or exhibit the obstruction. Either outcome files as a
  negative-map entry; two successor queue rows mandatory per
  `docs/agent-types.md:51-54`.

**Round deliverable (falsifiable per #7):** a bar file containing the
numeric measured clause, the g verdict against the pre-registered
thresholds, the Hankel verdict, and the go/kill for the tower route —
plus `results/rook1/queue.md` closed per protocol. `make` green including
the receipts gate. Round 2 (first compute: gate 0 completion, then the
a(30) pipeline with its NW-stencil RED) launches only from those queue
rows, only after its own brief-kill pass, not before 08-14.

Roster arithmetic: 5 spawns of 8; three slots held for queue-successor
re-dispatch or an unforeseen lane, and the census at close is 5 rows
against the TaskStop enumeration.
