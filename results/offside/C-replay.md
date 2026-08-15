# Offside lane C — the candidate design replayed against three real days

2026-08-14. Materials read in order: F1 (Li et al., arXiv 2608.11195, §§1-5),
F2 `HANDOFF.md` (all 1,151 lines), F3 `MEMORY.md`, F4 `docs/offside-design.md`,
F5 `docs/process-proposal.md`, F6 `paper/verify_claims.py` /
`scripts/check_receipts.sh` / `tests/gate_citations.py`. Days reconstructed from
HANDOFF plus `git log --all` over the relevant windows. Nothing was executed.

Counting convention, stated once because it decides the headline. Every day
below writes its results notes, proof docs and scripts **in both worlds** — the
candidate does not add or remove those. What I count as a candidate write is the
*delta*: a row in `state/hypotheses.md` / `facts.md` / `operations.md`, a
Lock/Reopen/Converts-to field, a tombstone, a chronicle entry, a named check
added to a verifier. One row edit = one write, however short. Where the number
depends on a rule the design does not state, I say so rather than pick.

---

## Day 1 — 2026-08-14 evening (backlog set 5/6/2/4/3, HANDOFF:3-67)

**What the day was.** Five threads dispatched by number, one deferred on a
running job. Two of the five (5 anisotropic novelty, 3 Middle Kingdom) turned
out already done and their memory entries stale. Item 2 (king twigs) closed as a
door, and its collateral broke a proof in `docs/proofs/polyplet-upper-bound.md`,
repaired in place. Item 4 (cancellation identity) was proved by an agent lane.
Item 6 (Ridgeline) landed a derived amplitude family. Item 1 unblocked when the
dalby job landed. ayr went dark mid-session. Two agent lanes ran (Birthright,
Ridgeline). Third stale entry: `b1-lean-the-rule`'s "the cancellation identity is
unwritten", true when written and false by the end of the day.

### Reads the candidate demands at open

| # | read | rung |
|---|---|---|
| 1 | `make state` output: open threads, live doors, debts, operations | — |
| 2-8 | rung-1/2 one-liners for the seven threads in play (Anisotropic, Middle Kingdom, King Twigs, Birthright, Ridgeline, Exact Change, Motley-as-context) | 1-2 |
| 9-13 | rung-3 results notes for the five actually executed | 3 |

**13 reads, of which 8 are one-liners inside one rendered file.** In practice
that is two file opens plus five results notes — cheaper than the real session,
which read a 1,151-line HANDOFF and a memory index and still got two of the five
items wrong. The read side of this design is not the problem on any of the three
days, and I will not belabour it again.

### Writes the day demands

King Twigs closing (6): hypothesis row → REFUTED with the narrowing recorded;
tombstone; fact row (`5⁵/4⁴ = 12.207` exactly, receipt
`experiments/kingtwigs/l1_schemes.py`, tier proved-by-machine-witness); Lock /
Reopen / Converts-to in `results/king-twigs-l1.md`; operations row retired;
chronicle. Collateral (2): the broken crude-bound proof means the standing
`λ ≤ 9.3154` fact row changes receipt — a fact row whose *statement* is unchanged
and whose *evidence* was found rotten, which is the one motion the design handles
better than anything currently in the repo.

Birthright (5): fact row tier=proved, proof-doc pointer plus check
`experiments/birthright_identity_check.py`; tombstone; verification-debt row
cleared; a new pending-sign-off row (gate wiring undecided under the gympie ban);
chronicle. The four corrections to `docs/b1-closure-plan.md` §7 are prose in both
worlds. The deleted `probe_cutcount_dp.py` cited in an engine header is already
`gate_citations.py`'s job and needs nothing new.

Ridgeline (7-9): fact rows for j=5 = 35/8 and α = 50/81; a fact row withdrawn
(118/27 was a normalisation artefact); the §5 limits ledger's four named-but-
unproved singularity assumptions become hypothesis rows; assumption 4's proof
becomes an operations row. Minus one write: the memory update
(`severance-w4-depth-tower`) disappears, because memory stops carrying state.

Exact Change (4): operations row closed on the landed job; fact row for the
H=10/11/12 ranks at tier single-source; parked row with `Price` = 5-6 h, which
the design requires be a measured receipt and here genuinely is (the H=12 wall,
1696 s). This is the cleanest fit of any item across three days.

Machines (1): ayr dark → machine-condition row.

**Day 1 delta: 25-27 writes**, against the real day's one HANDOFF edit (~65
lines, uncommitted) and two memory edits.

### Prevented, changed, or pure friction

- **Prevented, partly.** Items 5 and 3 were stale *in memory*, and A5/§7 removes
  project state from memory entirely. But the design prevents these only if the
  closing sessions (2026-08-01 anisotropic, Middle Kingdom Phase 4) wrote fact
  rows. `gate-state` checks the shape of rows that exist; it cannot check for a
  row that was never written. The design is **fail-closed on malformed state and
  fail-open on omitted state**, and omission is what produced both incidents.
  What actually changes is the *locus*: a missing fact row surfaces as a thread
  with no fact and a live operations row, which the rendered view shows at open.
  That is a real improvement and it is weaker than "prevented".
- **Prevented, cleanly.** The third incident (`b1-lean-the-rule`, "unwritten") is
  a verification-debt row, and debt rows are cleared by the session that pays the
  debt, in the same act as writing the fact. This one is structural.
- **Prevented, unmeasured.** HANDOFF:401-422's "FLEET STATE at 2026-08-07" table
  and HANDOFF:492's "IN FLIGHT: percell32 on gympie, driver PID 51511" are live
  operational assertions about a machine now under a hard ban. Under TTL both are
  expired and unconsumable. No incident on record shows anyone acting on them —
  which is precisely why this is listed as unmeasured, not as a save.
- **Friction, no payoff.** Converts-to on King Twigs. The design concedes in F5
  that a closing session cannot fill this field, and F4 keeps the field while
  dropping F5's heuristics file, so the field's only consumer is item 6's standing
  cross-thread read. On the day, this is a required field with no answer.
- **Cost the design does not carry but the day did.** The real cost of the two
  stale entries was one session noticing, correcting, and continuing. HANDOFF:12
  says it plainly: **"nothing was re-run."**

### What the day did that the candidate cannot represent

The collateral discovery — that a *proof* in the tree was broken, its frontier
missing re-entrant animals at 65% of n=8 — arrived while working an unrelated
item. Nothing in the design invites it, schedules it, or records that the
project's proofs are unaudited. A fact row at tier `proved` with a proof-doc
pointer reads identically before and after this discovery.

---

## Day 2 — 2026-08-14 morning (Motley / Coin Lift, HANDOFF:69-160)

**What the day was.** Two plan reviews run against the tree and reconciled; Coin
Lift closed dead at G2; the characteristic landscape closed by theorem plus an
exhaustive certified sweep; Motley Step 0 green; Half Measure written, gated and
measured; H=17 done green (a(n) rule-independent to n ≤ 33); Confetti H=18
launched with receipt enforcement; an uncosted `H ≤ 16` engine ceiling found and
raised; three plan-vs-tree corrections; one question left open for jasonp.
Commits `b9d725b`, `76f71c5`, `1e430fb`, `8861523`, `1d5d5f6`, `4df3fec`,
`0ce8841`, `1eb83a4`, `10144a5`, `3002104`, `443ed36`, `9f641e5`.

### Reads at open

Rendered view (1); rung-3 for Motley and Coin Lift, i.e. two plan docs and two
goal docs (4); the ladder-constant fact rows the rebudget consumes (~1 grouped
read); and — unavoidably, in both worlds — the source tree, because a plan review
against the tree is a code read. **6 reads plus the code.**

One note on the rung ladder: `docs/motley-goal.md` and `docs/coin-lift-goal.md`
are *goal* docs, and the four rungs (name → one-liner → results note → paper)
have no slot for them. The rook round's own recorded lesson (HANDOFF:289-294) is
that the failure was in the goal, not the transmission. The design's disclosure
ladder has no rung for the artefact that failed.

### Writes

Coin Lift closure 6; the G2 mis-specification recorded as a fact (the well-posed
object is `mu_k`, not "the Z/4 free rank") 2; characteristic-landscape theorem
plus the tier upgrade of Coin Roll's freeness from measurement to theorem 3 —
this last is the design at its best, since tier is the transition rule and a
measurement becoming a theorem is exactly a tier move with a new receipt; Motley
Step 0 2; Half Measure's four measured factors 4; H=17's four measured quantities
plus the headline reach plus the pre-registered kill condition resolving
SUPPORTED 6; Confetti's operations row plus its projections as day-TTL bets 2;
the engine ceiling 1; three plan corrections 3.

**Day 2 delta: 29 writes.** Two-thirds are fact rows for measured numbers.

### Prevented, changed, or pure friction

- **Prevented, and this is the strongest case in the three days.** All three plan
  corrections are the design's target class: "the banked ladder closes n ≤ 31,
  not 30" is a derived number restated in a plan instead of pointed at; "`--modp`
  is already committed and carries two streams, not three" is a claim about repo
  state with no receipt; "the receipt enforcement Confetti's gate battery names
  does not exist yet" is a cited artefact that does not exist. Two Fable review
  passes were spent, and HANDOFF:73-74 records that each review found exactly one
  load-bearing statement that did not survive contact with the tree. The design
  converts that into a gate.
- **Discount on that credit.** The third correction is already inside
  `tests/gate_citations.py`'s remit — a backticked repo path that does not exist
  is `MISSING` unless the line marks it planned. Part of what the candidate
  claims as new value is delivered by a gate written on 2026-08-06 for exactly
  this failure. The marginal value is the first two corrections, not all three.
- **Cannot represent, and it mattered.** The `H ≤ 16` ceiling was three argument
  checks in the engine, uncosted, caught by neither plan nor review, and it would
  have overflowed a 12-entry stack buffer by one, silently, at H = 18. The
  design's atomic unit is a claim someone wrote down. A constant nobody claimed
  is invisible to claims, bets, TTLs, doors and the rendered view alike. This was
  the day's most expensive near-miss and the design is blind to its whole class.
- **Friction.** Coin Flip, Coin Roll and Biased Coin Flip are named, untouched
  sub-threads. Under the design each needs a row and a status; under HANDOFF one
  sentence covered all three.
- **Unstated parameter that drives everything.** The characteristic-landscape
  sweep produced ranks at H = 4..9, a cutoff series 44,633 → 849, per-prime
  percentages, and a determinantal-divisor budget. Which of these become rows?
  The design does not say, and my "4" for Half Measure and "6" for H=17 are
  guesses. See the tally.

---

## Day 3 — 2026-07-25, the a(40) launch day (HANDOFF:632-661, ten commits)

**What the day was.** a(39) banked (`c447f94`). The disk gate resolved by jasonp
cleaning ~/var and ~/tmp, 284 GB freed under explicit per-item authorization.
a(40) launched levers-on. **Four OOM kills**, in sequence: the first took the
entire tmux server about an hour in — a TOCTOU race in the per-round statfs
check for `--fast-map-dir`, with N concurrent rounds overfilling /dev/shm — fixed
by reservation-based admission against a 24 GB floor with a red-first
`TestFastMapReservationRace` (`f9d485f`); the second closed by a RAM co-budget
(`6697c04`, journal-confirmed); the third by capping the merge reader army
(`7abd27d`, attributed from a memory-log timeline that had to be built first,
`a35c1f6`); and the day ended in a four-OOM postmortem and a phased-run redesign
(`6fa8e53`, `3895652`). Collateral: dalby's user ssh-agent died with the first
kill, blocking github pulls, worked around with a git bundle.

### Reads at open

Rendered view (1) and the operations rows for the live dalby job (1, inside it).
This is the design's home ground: HANDOFF's own §"FLEET STATE" table exists
because sessions need exactly this, and a rendered version of it cannot disagree
with its sources. **2 reads.** Best read-side fit of the three days.

### Writes

The a(40) operations row is rewritten at every launch, kill and relaunch — five
transitions, each carrying a new PID, a new local receipt path and a new checked
stamp (5-6). The RAM and disk projections are day-TTL bets and each OOM
invalidates them: 324-412 GB against a 470 GB ceiling, then revised twice more
(3-4). Four postmortem facts, one per kill, each with its receipt (4). The three
fixes each want a claim row pointing at the red-first test that guards them —
those tests exist, so the executable-check rung is satisfied for free (3). The
mem-monitor tool and the phased-run design are new threads needing names, rows
and one-liners (3-4). a(39)'s banking is its own set: term, validate pass,
growth, the P_19 fit point (4-5). Chronicle entries for an incident day that
generated ten commits (2-3).

**Day 3 delta: 24-29 writes**, and unlike the other two days they land *during*
an incident, competing with the incident. The design's commit tie (a commit
touching the chronicle must touch `state/*.md`) makes each of the ten commits a
table edit as well.

### Prevented, changed, or pure friction

- **Prevented: nothing.** Not one of this day's four failures was a state-rot
  failure. They were a TOCTOU race, a RAM co-budget, an unbounded reader fan-out,
  and a phasing design that did not exist yet. No claim outlived its evidence, no
  caveat was lost, nothing was re-derived.
- **Slower than looking.** A job whose tmux server was killed leaves an
  operations row asserting RUNNING with a dead PID. TTL retires that in days; the
  operator saw it in minutes. On operational state the design's freshness
  mechanism is strictly coarser than the tool that was already being used.
- **Unrepresentable, four ways.** (a) The OOM killer taking the whole tmux
  server: a machine event with no writer. (b) The 284 GB cleanup and its
  item-by-item authorization: a human action producing no artefact, expressible
  only as chronicle prose. (c) The ssh-agent death and the git-bundle workaround:
  a capability change on a box, not a claim, not a bet, not a door. (d) The arc
  itself — four instances of the same failure class before anyone stopped
  patching and redesigned. F5 had a trigger for this ("the same obstruction
  closes three attempts → stop searching; try to prove it"). **F4 dropped the
  heuristics file.** The single mechanism that would have shortened this day by
  two OOMs is the part the candidate design does not carry.
- **Friction with a real edge.** Restamping bets four times in one day is cheap
  per write and expensive in attention at the exact moment attention is scarce.

---

## Cross-cutting: the branch problem, which all three days exhibit

Between 2026-08-13 and 2026-08-14 this repo had commits on **master,
`half-measure`, `worktree-depth-swap2`, `gc-predictions`, `triangle-salvage` and
`triangle-structure`** — four of them on 08-14 alone. `worktree-depth-swap2`
carries two HANDOFF entries (`74bf988`, 18 lines, "anchor cut state, depth ladder
to J=5, and the gympie ban"; `cf3470b`, 53 lines, "Clean Room in flight") that
**do not exist on master**: `grep -i "anchor cut\|clean room"` over the working
HANDOFF returns nothing. Seventy-one lines of live state, including a thread in
flight, are invisible to a session that opens on master.

The candidate inherits this whole-cloth, and worsens it in one specific way.
`state/*.md` are tracked files, so a worktree agent's rows are branch-local
exactly as HANDOFF's paragraphs are. But HANDOFF's failure under divergence is a
prose merge conflict that a human resolves by reading. A gate-checked table with
bijective tombstone↔fact pairing and no-fact-claimed-twice fails **closed** on a
half-merged state: `make state` reds on master until someone reconciles, and the
reconciliation is a hand edit of the very tables that were supposed to be
authoritative. Multiple concurrent sessions appending to the same table region is
also the worst case for textual merge.

Nothing in F4 or F5 addresses parallel branches or worktrees, and this project
runs them as normal practice.

---

## The honest tally

**Writes.** 25-27, 29, 24-29 across the three days, against a baseline of one
HANDOFF edit plus zero-to-two memory edits per day. Call it **25-30 extra small
writes per working day**, most of them one-line table rows, in a project whose
sessions already produce ten commits on a busy day. The operator's stated concern
is writes-per-session, and on this evidence the concern is correct in magnitude:
the design roughly doubles the number of distinct places a productive session
must touch.

**Does it pay for itself over these three days?** Split by day, and the split is
the finding:

- **Day 2 (plan reviews): yes, clearly.** Three plan-vs-tree corrections, found
  by two paid agent review passes, all three in the design's target class. Even
  discounting the one `gate_citations.py` already covers, a mechanism that
  catches plan-asserts-repo-state on commit is worth more than 29 row edits.
- **Day 1 (backlog): marginal.** It reaches two of three recorded stale
  incidents, and reaches them by relocation and rendering rather than by
  enforcement, since the gate cannot detect an omitted row. The measured cost of
  those incidents on the day was zero re-runs.
- **Day 3 (compute): no.** Zero prevented failures, 24-29 writes, a freshness
  mechanism coarser than looking at the box, four unrepresentable events, and the
  one design element that would have helped (the repeated-obstruction trigger)
  removed between F5 and F4.

Net over three days: **roughly break-even, and the break-even is carried entirely
by the cheapest mechanisms in the design** — receipt pointers that must resolve,
reach numbers rendered from one source, and status out of memory. The expensive
mechanisms — executable checks per claim, TTL'd bets, tombstone bijection,
required door fields — did not prevent anything on any of the three days. That is
a survivable verdict for the design and a poor one for its most distinctive
parts.

### The unmeasured quantities the verdict depends on

1. **Claim granularity — the load-bearing unknown.** Every write count above
   depends on how many of a results note's numbers become rows, and the design
   does not say. My counts assume roughly one row per headline number and none
   per supporting number; the characteristic-landscape sweep alone could justify
   twenty. **Measurement:** take three banked notes of different shapes —
   `results/motley-h17.md`, `results/coin-flip-characteristic-landscape.md`,
   `results/ridgeline-depth-amplitudes.md` — write their rows for real, and count.
   Until that exists, writes-per-session is unknown to within an order of
   magnitude and no verdict on this design is quantitative.
2. **The cost of a stale-state incident, not its count.** The design is justified
   by three incidents in one day; the record says nothing was re-run and the
   session caught them all. **Measurement:** for each stale-state incident
   recoverable from HANDOFF and git, the compute or wall time spent before it was
   caught. If that number is near zero throughout, the entire design family is
   solving a cheap problem expensively.
3. **Check coverage of the actual claim population.** Mechanism 1 — status is
   computed by running the claim suite — assumes claims have runnable checks. The
   tree has **27 `gate-*` targets against 125 `results/*.md`**, and this project's
   headline numbers are overwhelmingly *measurements*: a 10.9 h H=17 wall, a 95.0
   GB peak RSS, a 23,681,423-window census. None of those is re-runnable as a
   check; each is a receipt. **Measurement:** classify the facts in a sample of
   results notes into re-runnable-under-a-minute, re-runnable-expensively, and
   receipt-only. If receipt-only dominates, then "status is computed, never
   written" describes a minority of the state and the majority falls back to
   exactly the `check: none` case the design displays loudly and does nothing
   about.
4. **Whether the day-2 saving is real.** The design catches the three plan
   corrections, but jasonp may run plan reviews regardless, for judgement rather
   than for fact-checking — in which case the saving is zero and only the
   reviewers' time-on-task shifts. No clean measurement; it is his call to state.
