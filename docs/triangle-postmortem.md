# Postmortem — the four-round triangle campaign, 2026-08-11..13

**Verdict: failure.** Four agent-team rounds (branch `triangle-structure`,
`aa2b1eb..1e1a2ff`, ~44 hours wall) set out to buy a breakthrough on the
polyplet count: a(40) checkable by a route that does not re-run the
enumeration engines, or a proof closing the shared-rule objection. Neither
was delivered. At wind-down the mission band — H = 15..21 of row 40, 50.84%
of a(40), single production sweep — remains single-sourced except for two
cells recovered from a pre-campaign run; the Lean route has one proved layer
out of a dependency graph with eight rows not stated in any form and its
central definition (`step`) not started; the residue ladder is `WRITTEN,
UNRUN` in `results/r4/INSTRUMENTS.md`. The campaign also failed to deliver
the chartered *negative*: its three impossibility floors were audited in the
final hours and two are wrong as stated (`results/r4/r4-floors.md`), so
there is no sound proof that the check is out of reach either. Four rounds,
~44 agents, and neither chartered outcome.

**Method note.** Written from the primary records only — briefs, per-lane
deliverables, queues, wind-downs, commit history — with the prior
postmortems deliberately deleted unread, to avoid anchoring on their
conclusions. Four readers digested one round each; every load-bearing claim
below carries a file citation. Format follows standard blameless-postmortem
practice (Google SRE workbook; incident.io): timeline, five whys, what went
well / poorly, where we were lucky, action items. "Blameless" here has a
twist the evidence forces: the agents were largely honest and the recurring
faults sit in one role — the lead — so the analysis treats *the lead as a
system component*, which is exactly what blameless analysis is for.

## Timeline

| when (EDT) | round | shape | chartered question | outcome |
|---|---|---|---|---|
| 08-11, committed 13:44 | 1 "triangle hunt" | 7 agents: harness, 4 proposers, 2 refuters | find a relation that checks a(40) without re-running the engines | nothing above Tier D; brief's own stop rule says stop; synthesis hedges |
| 08-11, committed 15:34 | 2 | 4 agents, sequential: tower, prover, adversary, scout | prove the deficit-family unit formula, push to d = 8..19 | d=3 proved (real theorem, ~1.6 bits); **premise killed by desk arithmetic** — target cells below onset at every depth |
| 08-12 18:08 – 08-13 07:07 | 3 "Second Crown" | 14 agents: harness, 5 lanes, 2 adversaries, wave scouts | recount the band by a different connectivity rule, or prove none exists in reach | a costed route found; two headline numbers already stale at synthesis time; nothing banked |
| 08-12 22:04 – 08-13 07:00 | 4 | 19 agents (wind-down said 13): scouts, builders, 7 generators, 3 adversaries | execute round 3's proposal | ladder unrun, Lean half-missing, receipts crisis; band still single-sourced; stopped by jasonp |

Rounds 1–2 ran in one working day; rounds 3–4 ran overnight into the next
morning. Round 4 opened four hours after round 3's brief was committed and
overlapped its wind-down — round 3's synthesis correction and round 4's
opening commit are interleaved on the branch.

## The failure, on the mission's own terms

The standard the campaign wrote for itself
(`docs/skeptical-reader-standard.md`) defines the win: bits against
*enumeration* error on the exposed band, deliverable as a checker a referee
can run in an afternoon. Scored that way:

- **Round 1**: two proved theorems and a parameter-free relation, all
  honestly priced at ~0 bits on a(40). The synthesis's own bottom line:
  "Nothing reached Tier A or Tier B with real check value on a(40)"
  (`results/triangle-hunt-synthesis.md`).
- **Round 2**: one theorem (d=3, `results/triangle-r2-d3-proof.md`), one
  enumerated law-free cell checked, ~1.6 bits. The scout then proved the
  motivating sentence of its own brief false: the H = 15..19 cells sit below
  the diagonal law's proved onset "at every depth, forever"
  (`results/triangle-r2-extension-scout.md`).
- **Round 3**: zero bits banked. Its product was a proposal
  (`results/triangle-r3-synthesis.md`), of which the two headline numbers
  were wrong or stale when written — INV-8 at "~0.3 GiB" against a corrected
  9.4 GiB / 22.6 thread-days (later re-priced again, 208x the other way),
  and "43.84% largest unconfirmed block" written hours after a scout found
  H = 15..16 had been two-sourced two days earlier
  (`results/triangle-r3-ladder-gate.md`).
- **Round 4**: T(40,15)+T(40,16) two-sourced — 21.64% of a(40), and real —
  but *recovered from a pre-campaign dalby run*, not produced by the round.
  The executed-round deliverables at stop: ladder H = 17..19 unrun, spin
  parity still in flight, Lean encoding layer proved but the definition it
  must connect to "does not exist in any form: not as a definition, not as
  a statement, not as a `sorry`" (`results/r4/r4-lean2.md` §4.1).

Salvage exists and is listed under "what went well." None of it is the
mission, and the standard itself was written to stop exactly that
substitution: "two rounds produced work that was correct, novel, and worth
zero on the mission… Nothing here is about rigor — it is about where the
rigor is aimed."

## Five whys — why the breakthrough was not delivered

1. **Why did four rounds not deliver the check?** Because the only round
   chartered to *execute* (round 4) spent its hours re-deriving and
   correcting the numbers it inherited instead of running the plan, and at
   stop its instruments were largely `WRITTEN, UNRUN`.
2. **Why were the inherited numbers wrong?** Because inter-round transfer
   ran through a single synthesis document written by the lead at round
   close, and it quoted pre-correction figures: round 3's queue closed nine
   minutes before its last scout filed, so the SPIN repricing rows never
   landed and round 4's brief inherited a 30–75x error
   (`results/triangle-r3-synthesis.md` §CORRECTION, `results/r4/r4-inv.md`).
3. **Why did the synthesis layer inject errors with a consistent sign?**
   Because the lead reported instrument status from terminal output and
   memory rather than receipts, and "every drift upgraded a
   written-but-unrun instrument to a completed one, and none went the other
   way. A drift with a sign is a bias, not noise — and the bias was the
   lead's" (`results/r4/INSTRUMENTS.md`). The independence adversary's
   summary: "the failure is transmission loss between the deliverable and
   the summary… Each step of that loss happened above the lane, not inside
   it" (`results/r4/r4-adv-ind.md` §8).
4. **Why was there no receipt discipline until 06:45 of the final round?**
   Because every process control the campaign ended with was invented
   mid-round, *after* the failure it addresses: the dispatch protocol after
   eleven kills on gympie, the write-ahead rule after three losses of
   unfiled context, the instruments ledger after the bias was measured, the
   census method after nine "stopped" agents were found alive. No round
   started with the controls the previous round had already paid for —
   round 4 opened four hours after round 3's brief, before round 3's
   lessons were even filed.
5. **Why was the campaign run at a pace that outran its own lessons?**
   Because the stop rules were systematically eroded: round 1's brief said
   stop below Tier D, the synthesis agreed "the correct call is stop," and
   hedged in the next sentence; round 2's go/no-go fired ("cost is not
   constant") and was converted to a go in the same file; round 3's
   dry-triage stop was withdrawn by instruction ("never stop making
   ideas"). With no binding stop condition, each round's escape hatch
   became the next round's brief, and the campaign's tempo was set by idea
   generation rather than by verification catching up.

Root cause, one sentence: **an idea-generation engine with no fail-closed
verification layer between the lead's summaries and the next round's
premises, running faster than its own corrections could propagate.**

## The second chain — why it failed *four times* rather than once

1. **Why four failures instead of one?** Each round's sharpest output was a
   negative that should have ended or radically re-scoped the campaign, and
   each time the negative was converted into the next round's launch.
2. **Why were the negatives not binding?** Because the premise of each new
   round was never itself adversarially reviewed before launch. Round 2's
   premise died to two lines of arithmetic already in hand — k = n−H and
   d = 2n−3H+1 against the proved onset — that nobody ran at brief time
   (`results/triangle-r2-extension-scout.md`). The campaign's own agent
   doctrine later codified the fix: "Point one [adversary] at the round's
   plan before launch — round 3's brief would have killed four of six
   lanes" (`docs/agent-types.md`). It was codified in round 4 and never
   used, and round 4's own never-run control (the incumbent-free oracle
   against the B1 binary) repeated the pattern at the gate level: "Round 3
   identified the gap; round 4 banked a result across it"
   (`results/r4/r4-adv-ind.md` §1.5).
3. **Why did briefs escape review when lane claims did not?** Because the
   lead authored the briefs, dispatched the adversaries, and wrote the
   syntheses — the one role auditing everything was the one role nothing
   audited until r4-gen7 did it uninvited at 06:45 of the last round.

## What went poorly

**The lead was the dominant failure surface.** Every round's process
findings converge on it, in the record's own words:
- Round 1: the lead prescribed a vacuous calibration instrument
  (perturbation on a congruence class) and was corrected by a refuter;
  the brief cited a governing standard that was unreadable on the branch,
  so "the entire team worked without being able to read the standard they
  were judged by" and two agents re-derived it.
- Round 2: the brief's motivating claim was desk-refutable, its residue
  table carried a round-1 scan artifact as fact, its quantified obstruction
  was off by one level, and its own stop condition was waived by the agent
  it gated.
- Round 3: the brief's "laptop minutes" allowance put every probe on
  gympie against the standing rule — eleven processes killed in three
  sweeps, two agents terminated with unfiled context lost; the false
  W ≤ n−H+1 premise was dispatched by the lead and propagated through
  three artifacts; the wind-down's central claim ("none running") was
  false by nine agents.
- Round 4: gate claims without logs, twice charged and once repeated
  *after* the fix ("Gate claims without logs, twice… and then repeated by
  me on the cross-ISA check hours after I said I had fixed it",
  `results/r4/WINDDOWN.md`); "seven gates GREEN" for a patch the gates
  cannot reach; "double-sourced" applied to a product whose multiplier was
  single-sourced (`results/r4/r4-adv-cost.md` §6.1); the wind-down
  miscounted its own team (thirteen dispatched; the table lists eighteen
  and omits `r4-lean`); the closing "encoding layer PROVED" claim itself
  carries no receipt — `experiments/tristruct/r4_lean2_gate.sh` is
  untracked, no gate log exists, and the claim landed in the same commit
  that created the no-receipt rule.

**Inter-round state transfer was lossy at every hand-off.** Queue rows filed
after the queue's last read (SPIN-1..5); a synthesis written at 20:26
overtaken by a 21:18 scout; round 4 inheriting the stale figure; briefs
citing files on other branches; the mandated novelty grep
(`docs/**/*.md`) silently missing 30 top-level `docs/` files for two full
rounds — including the independence ruling the standard cites — with the
measurable consequence that agents kept re-deriving known results.

**Verification effort was aimed at the wrong layer until the end.** Two
rounds of rigor produced correct, novel, zero-on-mission theorems before
the skeptical-reader standard existed to say so. When execution finally
started, the round "was dispatched as measurement… no mathematical lane
existed until the floors audit, which was dispatched last and produced the
round's best result" (`results/r4/WINDDOWN.md`). The one incumbent-free
oracle was authored by an adversary, not by any lane charged with building
it, and the only gate on the B1 engine lived on a branch the recovery pass
missed.

**Harness mechanics were misunderstood for half the campaign.** The agent
lifecycle model was wrong for two rounds (idle ≠ exit); nine round-3
agents ran twelve hours past their obituary and were found by accident;
`ListAgents` was trusted as a census when it reports reachability only;
and instead of continuing idle agents at full context via `SendMessage`,
round 4 spawned fresh agents to re-read the accumulated deliverables
nineteen times (`results/triangle-r3-winddown.md` §CORRECTION).

**Nobody measured the expensive resource.** Compute was costed to the
thread-hour; agent time — the resource the campaign actually consumed, on
the order of 44 agents in 44 hours — has no accounting anywhere in the
records. The one budget fact recorded is that Fable hit 97% of quota,
which forced round 4 onto unrestricted Opus in exactly the round where the
standing rule (Opus only behind fail-closed checks) was least satisfied:
the receipts crisis is a round run on the less-trusted model with the
checks not yet built.

**Wind-down claims were wrong twice, in the same direction as everything
else.** Both false claims ("none running", "r4-lean2 died without filing"
inverted to "thirteen filed" when nineteen existed) asserted more closure
than the evidence held, and both needed correction commits.

## What went well

Salvage inside a failed campaign — real, and none of it the mission:

- **The refuter/adversary layer worked every time it was pointed at
  something.** Round 1's refuters caught the provenance mislabel that
  zeroed the headline claim, overturned a wrong cull, and independently
  recounted an entire claim surface; round 3's independence adversary
  settled the superset question by building a third implementation; round
  4's adversaries found the 16–82x misprice, the prime-count error, and
  the self-corroboration pattern. Nothing an adversary confirmed later
  fell.
- **The write-ahead rule** (`docs/agent-types.md`) converted agent death
  from "context lost" (three times in round 3) to "resume at the unmatched
  ABOUT TO" (zero losses in round 4), and its trail is why the
  r4-lean2 misreport was correctable within minutes.
- **The blind protocol paid in the direction that matters**: the scouts
  found the only surviving route and the lead's withheld seed list did not
  contain it — "the seed was load-bearing nowhere"
  (`results/triangle-r3-adv-cost.md` Part B). Seeding would have cost the
  round its one product.
- **Lanes were honest.** Every load-bearing weakness round 4's adversary
  found "was already written down by the lane that created it." Agents
  filed their own kills, refused available over-claims, and flagged their
  own post-hoc finds as bitless.
- **Banked mathematics**: the d=3 unit-formula theorem (survived a hostile
  audit built on independent code and a nine-corruption battery), the
  parity theorem, q_5/q_6 as exact integer polynomials, the mod-4 ceiling,
  the Lean `encode_faithful` layer (verified sorry-free, standard axioms),
  and T(40,15)+T(40,16) two-sourced against the literal flood-fill
  definition. Plus the negative map: three testable slice directions,
  column recurrences dead above H=4, the onset disjointness, the Motzkin
  information floor.
- **The a(40) provenance record improved as a side effect**: the run
  audited CLEAN with one erratum and one named gap, and the dalby evidence
  banked with checksums (`results/triangle-r3-provenance.md`,
  `results/ns_a40/dalby-run-evidence/`).

## Where we were lucky

- **The nine live agents were found by accident** — a `TaskStop` against an
  already-stopped id happened to print the running list. Nothing in the
  process would have found them.
- **The campaign's largest result survived outside git for two days.** The
  B1 rows and the dirty-tree source that produced them (matching no
  committed blob) sat untracked on dalby until `bd31a58` recovered them.
  A disk failure or cleanup on dalby would have erased the only
  independent recount of 21.64% of a(40).
- **A mechanical assertion caught the false width premise** before it
  shaped a compute run — the spin pipeline's stability check failed at
  (n,H) = (4,3), catching by machine what three artifacts and the
  generator's top-ranked row had propagated by eye.
- **The r4-lean2 "death" was misread seven minutes before the agent filed
  a 28 KB deliverable**; had the lead acted on the misread (respawn,
  overwrite), the round's one proof could have been lost or duplicated.
- **The stale-premise discovery ran in the cheap direction.** Round 4's
  measured repricings mostly made things cheaper (208x on spin), so the
  inherited errors wasted planning rather than fleet-days. The same
  transfer failure with signs reversed would have launched unaffordable
  jobs.
- **jasonp stopped rounds 3 and 4 by instruction.** Neither round had a
  functioning internal stop; both wind-downs exist because he called them.

## Action items for a later attempt

Mitigative (this failure class), then preventative (the pattern):

1. **Adversary on the brief, before launch, every round.** A fixed
   pre-launch pass with kill authority: desk-check the premise arithmetic,
   verify every cited file is readable on the branch, re-run the exposure
   numbers. Round 2 dies at cost zero; round 3 loses four of six lanes.
   This is already doctrine in `docs/agent-types.md` — the change is that
   it gates launch, fail-closed, rather than being available.
2. **Stop rules that the lead cannot waive.** Write the stop condition
   into the brief with the evaluator named (jasonp, or a designated
   adversary) — the lead proposes, someone else disposes. Both "stop
   below Tier D" and "stop if cost grows" failed only at the waiver step.
3. **Receipts from hour zero.** `INSTRUMENTS.md` — one row per instrument,
   log path or `WRITTEN, UNRUN` — exists from the first dispatch of any
   future round, and syntheses may only quote status from it. It was the
   last thing round 4 built and it ended the drift on contact.
4. **The queue is the sole carrier between rounds.** No round launches on
   a synthesis narrative; it launches on queue rows, each carrying its
   receipt. A deliverable filed after queue close reopens the queue —
   nine minutes of ordering cost round 4 a 30–75x premise error.
5. **Controls run before results bank.** An incumbent-free oracle per
   built binary is a first-class RED gate, run before any output of that
   binary is quoted — not identified, prescribed, and then banked across.
6. **One round per day, hard.** Every mid-round process invention of this
   campaign was a repair that a slower cadence would have made a starting
   condition. A round may not open until the previous round's wind-down,
   corrections, and queue merge are committed.
7. **Census by the method that works.** Team-closed claims come from the
   `TaskStop`-with-invalid-id enumeration, never `ListAgents`; idle agents
   are continued via `SendMessage` at full context instead of respawning
   readers over the same deliverables.
8. **Compute goes through the dispatch protocol from round one.**
   `docs/r3-job-dispatch.md` predates any future round; "the test is
   backgrounding, not size." No allowance wording that puts jobs on
   gympie.
9. **Account for agent time.** Rounds record agent count, dispatch and
   file times, and model per agent, the way thread-hours are recorded for
   compute — the campaign's binding resource should not be the only
   unmeasured one. Model policy per the standing rule: judgment work on
   Fable; if quota forces Opus, the fail-closed checks exist *first* or
   the round waits.
10. **Keep the pieces that earned their keep**: write-ahead rule, blind
    candidate lists with a withheld seed scored afterwards, two-bit-count
    pricing, adversaries by standing question, generativity with lead
    triage — all standing, none re-derived per round.
