# Offside Lane B — the case against the candidate

2026-08-14. Adversary pass on `docs/offside-design.md` (F4), read against
F1 (Li et al.), F2 (`HANDOFF.md`), F3 (the memory index), F5
(`docs/process-proposal.md`), F6 (`paper/verify_claims.py`,
`scripts/check_receipts.sh`, `tests/gate_citations.py`). Desk only; nothing
was executed, every number below is read off the tree or off a committed
measurement.

## Summary judgement

The diagnosis is right and one of the seven mechanisms (item 7, memory stops
carrying state) is worth landing on its own this week. The other six are a
fidelity system, and fidelity is not what caps this project. Five objections
are structural; six are tweaks. The ceiling answer: **great is achievable in
this family, but not by this text** — the candidate spends its machinery on
the cheaper of the two failure classes Li et al. names, and it dropped, in
the move from F5 to F4, the only mechanism it had aimed at the expensive one.

The single most damaging finding is small and concrete, so it goes first.

## The exemplar's own number is stale

`docs/offside-design.md:34` grounds mechanism 1 — the whole "status is
computed, never written" argument — on the claim that `verify_claims.py`
runs **448/448** and that this is the one state layer in the repo that has
never rotted.

448 stopped being the count on 2026-08-02. The report trim took it to 425
(`HANDOFF.md:1035`, "verify_claims 448→425 with each check pruned"), it
settled at 428, and the last recorded run says so:
`docs/paper1-reproducibility.md:182-183`, "Re-run 2026-08-06: **428 checks
passed, 0 failed, 0 skipped**. (HANDOFF records 448/448 at the a(40) close;
the count moved with the report's own trim, not …)". The verifier's own
source agrees: `paper/verify_claims.py:116` says "255 of the 428 checks live
in an optional group."

So the design document, written to stop headline values outliving their
evidential status, carries a headline value that outlived its evidential
status by twelve days, in the sentence arguing that computing status
prevents exactly that. This is not a gotcha about care. It is the residual
the design does not address and cannot: **computed status still has to be
transcribed into prose before a decision reads it, and the transcription is
where the rot lives.** Every rendered view, every session-open summary, every
brief written off a rendered view is a transcription. The candidate moves the
authoritative copy; it does not remove the copies that get read.

And the exemplar rotted a second way. `paper/verify_claims.py:58-63`: "in a
tree without `build/g2`, `build/symcount_fast` and `runs/`, 220 of 448 checks
vanished with no signal in the exit status" — the tool printed "N checks
passed, 0 failed" and exited 0. That defect lived until a hand audit
(AUDIT-2026-07-30 P6) found it, and the fix was to grow coverage accounting.
The layer the design nominates as structurally incapable of rotting has
rotted twice: once in its transcription, once in its coverage, and the second
was silent-green.

## Structural objections, ranked by how much they should move the decision

### S1. Enforcement lands at commit; the damage happens at read

Every mechanism in F4 that has teeth is a gate, and a gate fires when
something is written. Read the incident list the design is built on: a
session opens, reads a stale line, acts on it, and re-derives or re-launches.
That entire sequence completes before the first commit. `make state` surfaces
expired bets "as loudly as a red gate" only if a session runs it, and nothing
can make a session run it — F5 was honest about this and called it session
discipline (A7, "the whole of it: a session opens by reading the three
tables"), which is exhortation with a nice name.

The candidate's own list of what is enforced by gate versus by exhortation:

| Mechanism | Enforced by |
|---|---|
| 1, claim has a check or `check: none` | gate (field presence only, not check quality) |
| 2, bets carry machine stamps | gate (presence), exhortation (species choice) |
| 2, expired bet "cannot be consumed" | **exhortation** — no gate can see a consumption |
| 3, views rendered not maintained | gate can forbid a hand index; cannot make anyone read one |
| 4, progressive disclosure | **exhortation** |
| 5, papers spawn with a check | gate (the check-ownership invariant) |
| 6, standing item to read all Locks | **exhortation** |
| 7, memory carries no state | gate, per F5's shape rule — the strongest item in the doc |

Four of the seven headline mechanisms rest on the agent choosing to comply,
and the agent is by construction a fresh one every time. This is the same
gap the repo already priced once: `scripts/check_receipts.sh:9-11` records
that the rule "no log path means the instrument is unrun" worked as
discipline and was then made mechanical *because* discipline is not the
durable form. F4 re-introduces four disciplinary rules and does not say why
these ones will hold.

Not fatal — a design can be partly disciplinary — but it means the honest
claim for the candidate is "one enforced improvement (item 7) plus six
conventions", and the cost section should be priced against that, not against
seven mechanisms.

### S2. TTL-as-absence inverts the safety of every prohibition

"An expired bet is treated as absent: it cannot be consumed until a session
re-verifies it." That rule is safe for assertions that *permit* an action and
unsafe for assertions that *forbid* one. Absence of "ayr is dark" reads as
ayr being fine. Absence of "don't relaunch" reads as launchable.

This repo's load-bearing state is overwhelmingly prohibitive. Eight memory
files carry an explicit prohibition, and they are the ones with incident
histories behind them: holes n≥20 is "**NO-GO**, closed, not deferred"
(`HANDOFF.md:1122-1132`); Middle Kingdom's entry ends "Don't re-verify, and
don't relaunch any phase"; the triangle tower entry says "never re-pitch
d=15..19"; `a21-run-do-not-restart` sets a "VERY high bar: correctness or
dead box only"; `viva-do-not-raise` says omit it from every menu. Under
mechanism 2 each of these is an operational assertion or a priority — species
whose TTL is days to weeks — and each expires into absence, which is
permission. A calendar then re-opens closed doors on a schedule, and the
agent that walks through one is behaving correctly by the design's own rule.

The fix is not hard (see F5 below) but the default is wrong in the dangerous
direction, and a design whose failure mode is "re-pitch the thing he told you
never to re-pitch" is proposing the operator's most-complained-about failure
as a scheduled event.

### S3. Computed status needs a computer, and the computer is banned here and dark there

Mechanism 1 answers "is this settled?" by running the claim suite. Mechanism
3 renders the session-open views. Both execute. F4's own inherited
constraint: "anything that executes runs on ayr/dalby, never gympie."

The state of the fleet in the entry that motivated this whole design:
"Machines: **ayr unreachable** since ~23:00 UTC (no route to host — power cut
until proven otherwise)" (`HANDOFF.md:56-57`), with dalby carrying an ~82-hour
Confetti run. The very same entry records the wiring question already live:
"**Gate wiring undecided**: the check is a natural `gate-cutcount-identity`
but the gympie ban means `make` must run on ayr/dalby — jasonp's call"
(`HANDOFF.md:33-34`).

So on the day the design was written, the mechanism that computes status had
one available box and it was saturated. "Status is computed" degrades to
"status is unknown" exactly when the fleet is degraded, which is exactly when
the operator most needs to know what is true. A hand-written HANDOFF line is
readable during a power cut.

Concession, and it is a real one: the gate suite has run on gympie as
recently as 2026-08-06 at 467 s wall for 16/16 green (`Makefile:50-51`), and
a state render over plain markdown is nothing like a gate suite in cost. The
objection is not that rendering is expensive. It is that the design makes
*reading the state at all* depend on execution, and this project has a
standing hard ban on executing on the box the operator sits at. Any render
must therefore have a committed, readable output checked into the tree — at
which point the committed output is a derived index, and item 3's whole
argument was that derived indexes die. The design has to pick one.

### S4. The design optimises the cheaper of Li et al.'s two weak functionalities — this is the ceiling

Li et al. §5 names three functionalities and grades them: technical execution
strong, **research judgement limited**, **research-state representation
fragile**. F4 addresses the third and nothing else.

Price the two from their own record. The state-representation failure
(session 44) cost one withdrawn bound and a 25-day-later reproof of a
criterion the run had already proved in session 8 — real, bounded, one
branch. The judgement failure cost more: the run sat at session 18 opening
another variant of a scheme that had failed the same way repeatedly, and the
operators had to supply the pivot; the paper is blunt that "the run had
accumulated exactly the required evidence without making the connection", and
the lower bound — the run's only stated theorem — exists because a human
overrode a judgement, not because the archive was accurate. The archive
*was* accurate: "in both failures, the archive retained the original facts;
it was the compressed state governing decisions that failed."

That last sentence cuts both ways and the design only uses one edge. Yes,
compression lost the caveat. But it also says the facts were there and
findable — which is the situation this repo is already in. HANDOFF is 1,150
lines and its facts are correct; the three 2026-08-14 incidents were in
memory, and all three were caught and fixed within the same day by a session
reading the tree (`HANDOFF.md:9-12`). The measured harm from state
infidelity here is: nothing was re-run.

Meanwhile the judgement gap is visible in the same file and unaddressed. Six
"jasonp's call" points sit open in HANDOFF (lines 34, 787, 800, 809, 890,
969). The rook-parity round closed with the finding that "the goal did NOT
survive it" — a target-selection failure, not a state-fidelity failure. King
twigs and rook parity both ended on the same obstruction pattern and F5's
heuristic 1 exists because no rule fired.

**And the candidate dropped that heuristic.** F5 shipped eleven trigger→action
entries with an admission rule ("every entry names a repo incident where
following it would have changed the action taken"); F4 has none of them. What
survives into F4 is item 6's plumbing — the standing item to read all Locks
and Converts-to lines in one sitting — with the rule it was built to fire
removed. F4 §preamble calls F5 "partly superseded" and says the candidate
supersedes where they differ. On this they differ, and the candidate is
strictly weaker.

So: **the family is capped at "better than HANDOFF" on fidelity, and the cap
is that fidelity is not the binding constraint here.** What binds is that
nothing in the project computes over the corpus to produce a judgement
prompt. That is what great would look like, and it is achievable in this
family — see the ceiling section below.

### S5. State is being moved out of the only push channel into pull channels

MEMORY.md's index is injected into every session's context without anyone
asking for it. That property is why it rotted and it is also the only thing
in the system with that property. Mechanism 7 removes project state from it;
mechanisms 1–4 replace that with files a session must choose to read and a
render it must choose to run.

Look at what leaves. `middle-kingdom-plan.md` is ~120 lines carrying Bacher's
Definition 2 pinned against the actual PDF, the A007052 naming collision, the
two cells that collapse, the corrected `results/directed-king-animals.md`
predicate, and "don't relaunch any phase". Under mechanism 7 that becomes a
pointer, and the content lands in a primary doc nobody loads by default. The
retrieval story is grep — but grep needs a token, and the value of that entry
is that it arrives *before* you know which token to grep for.

Concession: F5's shape rule keeps a pointer in the push channel, so the
channel is not lost, only its bandwidth. And the argument that a
status-carrying, gate-free, auto-injected file is the worst layer is correct.
But the design should say plainly that it is trading recall-without-a-query
for accuracy, and that the trade is unmeasured. It currently reads as pure
gain.

## Fixable with a tweak

**F1. `check: none` should inherit a bet's TTL.** As written, the
claim/bet boundary is agent-chosen and unchecked, and the incentives run one
way: a claim survives forever, a bet expires, so anything an agent wants to
keep gets filed as a claim with `check: none`. That is a strictly better
hiding place than today's HANDOFF prose because it comes with a tier label.
The repo has already documented this exact drift-with-a-sign:
`check_receipts.sh:6-9`, "across round 4 of the triangle campaign every
status drift had the same sign — an instrument that was WRITTEN, UNRUN got
described as one that had run. A drift with a sign is a bias." Give
`check: none` claims a TTL and the escape hatch closes.

**F2. A restamp must cite something new on the same line.** Re-verification
is an hour; restamping is one edit; nothing distinguishes them afterwards.
That is the decay path into TTL'd prose, and it is the design's own
nightmare scenario arriving through the front door. The repo already owns the
countermeasure: `check_receipts.sh` requires an in-tree, non-empty path on
the same line as a status token. Apply it to restamps — a restamp names a
chronicle line, a log path, or a commit sha, or it is not a restamp. It does
not prove the verification happened; it makes the cheap path leave a mark.

**F3. The renderer needs coverage accounting, red-first.** Ask "who gates the
gate" concretely: a renderer whose glob stops matching after a directory
rename emits a *shorter, cleaner* view, and short-and-clean is
indistinguishable from progress. This is worse than a stale hand-written
index, which at least still shows the old rows — a broken render shows
nothing and reads as "nothing open," which is precisely the false instruction
F5 flagged at `HANDOFF.md:1134` ("No open thread needs immediate action").
Two in-tree precedents for silent-green: verify_claims dropping 220 checks
while exiting 0, and the lean2 battery's gate E reading a correct output as
zero sorries on an ASCII-vs-backtick mismatch (`check_receipts.sh:26-29`).
The render must print sources consumed and rows emitted, and fail if either
drops below the last committed value — the same fix verify_claims needed.

**F4. Rendered views lost the ancestor's only priority mechanism.** F5 A3:
"Rows sit in your priority order, which beats a priority column you would
have to maintain." F4 item 3: views are outputs of `make state`. A render
sorts by a schema field; it cannot rank by importance, and the guardrails
put "priority as a column" on the explicitly-not-copied list. So the
candidate's operations view either dumps everything at uniform weight or
invents a proxy. What a hand-written view does that a generated one cannot is
carry emphasis — `HANDOFF.md:50`, "**Read §5 (limits ledger) before citing**"
is a rendering of judgement, and no schema emits it. Fix: let the render
consume a hand-ordered list of thread names and order by it, erroring on
names it cannot resolve. Order is hand-maintained; content is not.

**F5. Prohibitions are facts with door fields, not bets.** Direct fix for S2.
A closed door does not expire; a `Reopen` condition is the only thing that
opens it, which is what F5's closed-thread fields already say. The rule
becomes: anything whose consumption is "do not", never TTLs.

**F6. Any status gate built on an exemption vocabulary inherits a leak.**
`tests/gate_citations.py:69-85` exempts at *paragraph* scope: one occurrence
of "deleted", "planned", "todo" anywhere in a run of non-blank lines exempts
every citation in it. The widening was deliberate and defensible for
citations (prose wraps). For status it is not: research prose says "deleted",
"planned" and "todo" constantly, so a paragraph-scope exemption would blind
the check across most of the corpus. F5 conceded the repo-wide status-vocabulary
check is best-effort; the receipts gate's own default scope is 23 of the 315
tracked markdown files (7%), narrowed on purpose because "prose elsewhere in
the repo says GREEN about history." Any claim that the new gate covers the
corpus should be priced against that 7%.

## The cost the operator asked about, counted

He named writes-per-session. One counted sample, the entry the design was
written the same evening as (`HANDOFF.md:3-67`, 65 lines, one file, one
write today).

Hand-enumerating its assertions gives 28. Roughly:

- **10** have an executable check that already exists (the cutcount identity
  and its 223k-subset check with 5 REDs; the king-twigs L1 bound; the
  re-entrant-frontier defect at 65% of n=8; the three N-family ranks
  453/912/1818; the ridgeline amplitudes and α = 50/81; C₁ to 2.5e−12).
- **8** are `check: none` and could not be otherwise — "the novelty check
  closed, three databases, no collision"; "the C_i ladder is dead by budget,
  ~24% needed vs BS's 6.3%"; "repaired in place with a sound BFS-frame
  derivation"; "the scaling function is a square root, not Airy"; the §5
  limits-ledger caveat.
- **10** are operational bets: ayr dark, Confetti running, dalby scratch
  disposable, eleven uncommitted paths, sign-off pending, second source owed,
  gate wiring undecided, H=13 priced at 5–6 h.

Plus the door fields king twigs now owes — Lock, Reopen, Converts-to, with
non-empty bodies — and Coin Lift's, from the entry above it.

Call it **20–25 writes where the day took one**, with about a third of the
claim rows permanently displaying `check: none` "loudly". Two things follow.
First, once `check: none` is a third of every render, loud is noise and the
display stops being read — the alarm-fatigue failure, and the design has no
answer to it. Second, this was the design's *best* case: an execution-heavy
day where agents wrote checkers as they went. A judgement day — the
2026-08-14 morning entry is two plan reviews and a launch decision — produces
almost no checkable claims and the same write count.

Two honest counters I owe the design. The chronicle write is the write the
session was making anyway, so the marginal cost is the rows, most of them one
line. And `git log -S<name>` plus 188 existing `experiments/*.py` checkers say
this repo already writes checks by habit — mechanism 1 is largely describing
established practice rather than imposing a new tax.

## What the design gets right

Not throat-clearing; these are the parts I could not break.

1. **The diagnosis and its localisation.** All three 2026-08-14 incidents
   were in the auto-injected, gate-free layer. Item 7 is correct, is the
   cheapest item in the document, needs none of items 1–6, and should land
   whatever happens to the rest.
2. **The time constraint is handled correctly and this is the sharpest
   engineering in the doc.** Machine-written stamps, expiry computed at
   render, TTL lengths as operator-set constants, agent effort estimates
   banned from becoming durations, every price a measured receipt or
   "unmeasured". I have no objection to any of it. It is the one place the
   design takes a hard property of the executor and builds around it instead
   of asking the executor to compensate.
3. **Killing hand-maintained derived indexes**, with three corpses on record
   (ROADMAP.md, the results map, the dependency map). Correct, and F5's
   distinction — these tables are authoritative, not derived — is the reason
   attempt four is not attempt four.
4. **Papers spawn red-first.** The paper+verifier pairs are the best-behaved
   artifacts in the tree even after the two rot modes I found above, and
   "every check owned by exactly one draft, every asserted number checked" is
   a real invariant a gate can hold.
5. **The name as rung zero of progressive disclosure.** Already proven here;
   `aka` closes the one hole (B1 → Motley); the decision to decline integer
   IDs is right for the same reason.
6. **Required fields on wins as well as losses.** Charging only for the
   honest label leaves "leave it OPEN forever" free. That is a genuine piece
   of incentive design and it is the second-best idea in the document.

## The ceiling question, answered

**Is great achievable in this family?** Yes, but the candidate is not it, and
the gap is not a matter of degree.

What the candidate can reach at its best: a state layer where nothing
asserted is older than its evidence, where closed doors stay closed, and
where a fresh session's first screen is accurate. Call that *fidelity
complete*. Measured against this repo's actual record, fidelity complete buys
the three 2026-08-14 incidents caught at open rather than mid-session, and
some fraction of a re-derivation that has not yet happened here. HANDOFF's
facts are, as far as this pass could tell, correct. The design is competing
against a baseline that is already good, and the ceiling of a fidelity system
is bounded by how wrong the current state actually is — which nobody has
measured. F5 knew this and specified the measurement (the migration baseline:
count stale entries found while verifying rows, count again at the end). F4
dropped it. **Adopt the candidate without that baseline and the review
question is unanswerable by construction.**

What great would require: the state layer produces *judgement prompts*, not
status. The three that the corpus can already support, with grep-level
machinery and no schema change at all:

- **Repeated obstruction across threads.** The grouped Lock listing is
  already specified (F5 A6, non-failing output every run). The rule that
  fires off it — same obstruction closes three attempts, stop searching, try
  to prove it, ask what it dualizes to — is the Li et al. pivot, is F5's
  heuristic 1, and is absent from F4. Rook parity and king twigs both ended
  this way with no rule firing.
- **The same constant in two derivations.** F5 heuristic 7, with D₀ = 5⁵/4⁴
  as its incident — and the king-twigs bound landed on 5⁵/4⁴ = 12.207
  *again* on 2026-08-14 (`HANDOFF.md:17-18`). A grep over the results corpus
  for repeated exact constants is a twenty-line script and it would have
  flagged that coincidence the day it happened.
- **A stalled row whose settling cost dropped.** Every hypothesis carries
  "what would settle it" (F5 A1). When a tool lands that changes that price,
  nothing today notices. That is a join between two files the design already
  proposes to have.

All three are computable from the sources the candidate creates, all three
are outputs rather than obligations (nobody has to maintain them), and all
three attack the functionality Li et al. priced as the expensive one. That
is the honest shape of great here: **the render's job is not to report status
but to compute coincidences the operator cannot see from inside one thread.**

**What caps the family, then?** Two things, one soft and one hard.

Soft: fidelity is not the binding constraint, and the candidate spends six of
seven mechanisms on it. Fixable — re-admit F5's heuristics file and point the
render at coincidences.

Hard, and this one does not lift: **every mechanism that surfaces something
surfaces it to one person.** Six "jasonp's call" points are open in HANDOFF
right now. The candidate adds expired bets, naked claims, the grouped Lock
listing and the standing cross-thread read, all of them arriving at the same
inbox. A design that raises the surfacing rate without raising the decision
rate converts a stale-state problem into a queue problem, and the queue has
one server who is also the person doing the mathematics. Nothing in this
family addresses that, because the whole family's theory of value is "put the
right thing in front of the human at the right time" — which assumes human
attention is the abundant resource. Here it is the scarce one.

## Recommendation

Land item 7 now, on its own, with F5's shape rule and the found-or-declared
directory check. It is the item with an incident count of three, the only one
enforced end to end, and it costs an evening.

Hold items 1–6 pending the migration baseline F4 dropped — the count of stale
rows found while verifying, taken twice. Without it the adoption decision is
being made on the assumption that the current state is bad, and the one day
we have detailed evidence for says the state was correct, the stale entries
were in memory, and nothing was re-run.

If items 1–6 do land, land F1, F2, F3 and F5 with them; they are cheap and
each closes a path by which the system decays into exactly what it replaces.

Weakest items in this file, conceded before anyone has to find them: S5 is
about bandwidth, not channel, since a pointer still rides the push channel;
S3 overstates the render's cost and its real content is the
committed-output-versus-derived-index dilemma, not the compute; and the
20–25 write count is a hand enumeration of one entry by one reader, not a
measurement — it should be redone by a second pass before it is quoted.
