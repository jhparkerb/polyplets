> **Status: draft for discussion. Nothing here runs without jasonp's explicit
> go.**

# Round-3 brief — "Second Crown": an independent determination of the bulk band

2026-08-12. Third and final round on the T(n,H) triangle. Supersedes
`docs/triangle-structure-round2-brief.md` and shelves
`docs/triangle-structure-d9-d12-plan.md`. Scoring is
`docs/skeptical-reader-standard.md` in full — disclosure block, automatic-zero
list, correlation rule. Read `results/triangle-hunt-synthesis.md` and
`results/triangle-r2-extension-scout.md` first; this brief assumes both.

## The mission, stated once

Row 40's H = 15..21 cells carry **50.84% of a(40)** and rest on a single
production sweep. Both prior rounds tried to *predict* those cells from
elsewhere in the triangle, and the geometry says no: the fittable region and the
checkable region are disjoint, and the tower route lands below the diagonal
law's proved sharp onset at every depth, forever.

So stop trying to predict them. **Count them again, by a rule the referee will
accept.** The objection on the record is exactly one sentence long: both
production engines decide king-connectivity by union-find over a frontier
against the previous column's component labels, and a shared misconception about
what is being counted passes through both and shows up as agreement. Different
code, language, machine, ISA and modulus are not answers to it. A different
*rule* is the only answer to it.

**Deliverable of this round: a costed, proof-checked route to determining
T(40,H) for H = 15..21 — exact values or residues to a stated modulus — by a
method whose connectivity decision is independent of
union-find-over-a-frontier in the sense fixed below. Or a proved statement that
no such route exists within reach, naming the obstruction.** Both outcomes close
the question; the second is the honest epitaph and is worth writing.

Set expectations honestly in every deliverable: **residues to a small modulus
are the probable ceiling and exact values are the stretch.** A route that ends
in one more bit per band cell is a real result and must not be written up as if
it were the count.

This round scopes and proves. It does not build. Any route that survives comes
back to jasonp as a costed proposal with a red-first gate plan, and he decides
whether it runs.

## The entry ticket — two levels, and both get answered

Every lane opens with one paragraph: **where is king-connectedness decided, and
what does that decision share with union-find over a frontier against the
previous column's labels?** The answer is scored at two levels.

**Level 1 — semantic independence.** Where is connectedness *defined*, and could
the engines' hypothesised misconception reproduce there? An independent
formalisation of the object, or generic tooling that takes connectivity as a
*constraint in the encoding* rather than implementing it as an algorithm, clears
level 1 even when the machinery underneath is a partition DP.

**Level 2 — algorithmic independence.** The standard's axis 1: name the failure
mode the route would exhibit if its rule were wrong, and argue that mode is
disjoint from union-find-over-a-frontier's.

**Component labels across a cut are not disqualifying.** They are the trigger
for the level-2 argument, which must then be made explicitly rather than
assumed. This is jasonp's ruling for this round, made at brief time and not
delegated to an adversary mid-round: a route that clears level 1 admits a lane.
It does not relax `2b3115b` for any other purpose, and a level-1-only route
ranks strictly below any route that clears both. **State in the first line of
every candidate which levels it clears.**

The second ticket is cost realism. `results/boundary-push-tensornetwork.md`
measured the wall: connectivity entanglement across a cut is intrinsic
(χ ~ λ^(H/4); exact rank 21→51→127→298 over H = 8..14; MPS loses by more as H
grows). Any route that reintroduces connectivity state on a frontier pays that
rank. A route is interesting only if it pays somewhere else — coarser objects,
a different cut, or no cut at all.

## The routes

**L1 — Corner gluing.** A king animal is a set of rook-connected polyomino
pieces joined only at corners; `results/component-stratification.md` proves the
stratification and its two edge identities (`C(n,1) = A001168`,
`C(n,n) = A001168` by the 45°-sublattice bijection) and measures the typical
animal at ~n/2 pieces. Connectivity becomes a graph condition on a piece-contact
graph, and the ingredient counts are published polyomino enumerations computed
by other people with other methods — the strongest semantic independence
available anywhere in this problem.

Two things the lane must confront first, or the adversary zeroes it in a line.
(i) The piece-level-labels trap: any strip assembly of ~20 pieces needs a DP
tracking which pieces have connected so far — component labels at a coarser
granularity, which is a level-2 argument to be made, not skipped. (ii)
`component-stratification.md` already banks that no free-composition
generating function exists, because corner contacts are geometrically
constrained. So the live question is quantitative and nobody has measured it:
**does a height-H strip make coarse piece-assembly a smaller state space than
the cell frontier?** Pieces are coarser than cells, which is the one real hope.

**L2 — Cluster inversion.** One question only, because the rest is answered in
the file this lane would start from: `results/defect-gas.md` §"reach verdict"
measures the gas DP at ≈20× per k (k=4: 3.1 s, k=5: 65 s, k=6: >530 s), putting
realistic reach at k ≈ 7 in Python and k ≈ 9–10 with a C++ effort, against the
band's surplus of k = n−H = **19..25**. Cluster/joint-placement inversion is
therefore priced out on the record. The single live question: **is there an
inversion route that is not gas-shaped** — one whose cost is not governed by
joint placement of components? A cited paragraph answering no is a complete
deliverable. Assigned to the L1 scout; it is the same decomposition instinct
and does not need its own agent.

**L3 — Contour encoding.** Enumerate by the boundary curve rather than the
cells: connectivity enforced by the curve closing, the most refined
transfer-matrix technology in the field. Two known obstructions, both to be
established rather than assumed: king animals have holes, so a single closed
curve does not characterise them; and Jensen-style boundary states are link
patterns, i.e. component-pairing labels — the same Catalan/Motzkin object
`boundary-push-tensornetwork.md` identifies as the cut rank. The one variant
with a live semantic story, worth a sentence before the lane closes: **hole-free
by contour, plus hole strata** — `defect-gas.md` already carries hole-marked
stratification machinery, even if the strata cost likely kills it. A clean
negative here is a real result and should be cheap.

**L4 — The symmetry quotient, pushed.** The one route already proved to reach
row 40 by an unrelated algorithm: `T(n,H) ≡ I_H(D2ax) (mod 2)` on all 820 cells.
Its RHS comes from `symcount_fast`, a DFS over a quotient domain of size
~λ^(n/4) — 4.6 MB peak RSS, no frontier, level 2 cleared.

**The lane's first task is a routing audit, because the mod-4 refinement is not
so clean.** `results/percell-mod4.md` states it outright: "`symtm` holds a strip
frontier; `symcount_fast` is a DFS over a quotient domain — 3.9 GB here against
4.6 MB there." The refinement's other three inputs (`I_H(⟨h⟩)`, `I_H(⟨v⟩)`,
`I_H(C2)`) are routed through `symtm --byheight`, which shares
`core/transition.h`. As currently wired, the second bit would compute most of
its RHS by the very rule class this round exists to escape, and the proposed
vmirror mode is another strip-frontier mode. So: **state where each of the four
`I_H` inputs decides connectivity, and make a quotient-domain (Redelmeier-style)
`--byheight` route for the other three the lane's actual target.** That, not the
vmirror sweep, is the version of L4 worth buying.

The 2026-08-07 decline stands on three measured reasons: `I_H(⟨v⟩)` has no
bounded-height route, r180's cost peaks exactly on H = 15..19, and a fresh sweep
mode would itself become the thing being trusted. Reasons 1 and 2 are
engineering and are in scope to beat. Reason 3 is not a gate problem — it says
trust is *history* — so proposing to override it with red-first gating is a
decision to state plainly and argue, not to slide past.

Second question, and the one that matters more: **what is this route's
ceiling?** D2ax orbit sizes divide 4, so mod 8 needs a different group. Name the
group or prove there isn't one.

**L5 — Connectivity as a constraint, not an algorithm.** Generic exact counting
tooling, written and verified by other people, in which the animal's
connectedness is *stated in the encoding* and the counter never implements it.
That is the cleanest level-1 story available: a misconception about what is
being counted cannot survive a formalisation of "connected" that a third party's
counter then evaluates. Level 2 will be contested — general-purpose counters
tend to decompose on separators, which is a partition DP by another name — and
that argument is the lane's real work. The costing question is whether any such
tool reaches n = 40 at H = 15..21, even modulo a small prime; the honest prior
is that it does not, and the encoding is still worth having at small n as a
definition-level witness that the engines count what we say they count.

**Which tools those are is the lane's finding, not this brief's.** No candidate
list is given here deliberately (see *Blind lists*).

**L6 — The wildcard, sourced from the literature.** Any method not previously
investigated here, taken from the literature directly, indirectly, or from a
field with no connection to king animals. The question is exactly as broad as it
sounds: **what does the literature have that this project does not?** No
candidate list is given, for the same reason.

Three constraints, because this is the lane that can waste a round:

- **Prune mechanically, then read.** Build the list wide, write the structural
  filter down *before* opening a paper — exact counts or not; reaches n = 40 at
  H = 15..21 or not; decides connectivity somewhere other than a cell frontier
  or not — then read only the survivors. Report the filter and the kill counts,
  not just the survivors. Cap: at most six papers read in full.
- **Cite or log it.** No claim about a paper from memory. Anything unobtainable
  goes in `papers/MISSING.md` per standing practice rather than being
  paraphrased. Penn State access is free to PA residents if it comes to that.
- **The entry ticket applies unchanged.** A method is interesting here because
  of where it decides connectivity, not because it is unfamiliar. And if the
  best thing you find does not fit that vocabulary at all — an identity, a
  bijection, a bound from another direction — file it anyway and say the ticket
  did not fit. That is a finding about the ticket.

## Blind lists

Every scout's **first deliverable is its own candidate list, filed before it
reads anything beyond the harness pack and the files its lane names.** Write it,
timestamp it, then work. Do not revise it afterwards; append instead.

The reason is recorded so nobody mistakes it for ceremony. The lead holds a seed
list for L5 and L6 — the obvious candidates from one context, this one — and
withheld it on purpose, because a brief that names the methods makes the round a
test of the lead's list rather than a search. That list goes to the completeness
adversary **after** the scouts file, as a scoring instrument: what a scout found
that the seed missed is what the seeding would have cost; what the seed holds
that no scout found is a fact about this round that gets written down plainly,
not quietly adopted.

The same discipline is why the lanes differ in how much they say. L1, L3 and L4
point hard at banked artifacts — those are this project's own results and
withholding them buys a rediscovery, not independence. L5 and L6 point at
nothing.

## What is closed — re-deriving any of it scores zero

- The deficit families and the mod-3^m tower at every depth. Row-40 H = 15..19
  is below onset and unreachable by that frame forever. Do not propose
  d = 9..19.
- Slice and stencil mining in every direction (920 hypotheses, BARREN; only
  three directions span fit and holdout at all).
- Strip-TM recomputation: consistency check by ruling, and the engine cannot
  reach the band anyway (~52 h at H = 15, ~7.6 years at H = 19, 4-bit packing
  caps at H ≤ 15).
- Column recurrences above H = 4 (onsets n = 43, n = 107).
- Non-D-finiteness of the bivariate GF; no global P-recurrence in (n,H).
- Site-MPS compression of the frontier (measured, decisive) — L6 may look at
  other contraction structures, not at this one again.
- The H22 holdout and cross-ISA recount are declined by standing decision and
  are not this round's business — but the closing statement must acknowledge
  they exist, so it cannot be read as pretending the direct route was never
  there.

## Rules of engagement

Standing project rules unchanged: exact integer arithmetic, named scripts under
`experiments/`, no stdin jobs, no `/tmp`, no binaries outside `build/`,
`paper/technical-report.tex` read-only, `docs/viva-*.md` never committed, no
jobs on gympie, anything over five minutes in a tmux window.

**The measurement boundary. REPLACED 2026-08-12, mid-round, by
`docs/r3-job-dispatch.md` — read it, it governs.** The original wording said
"throwaway scripts, laptop minutes, small n". That was wrong: it put every probe
in this round on gympie, jasonp's working laptop, against the project's standing
rule. The lead wrote it; the lanes followed it correctly.

In short, and the dispatch file has the detail: **no agent runs compute on any
machine.** An agent that needs a number files a job request — with wall, RAM,
disk and core estimates, each labelled MEASURED, EXTRAPOLATED or ASSERTED, plus
what decision the number changes and what RED control it carries — and the lead
dispatches it to ayr or dalby, or asks jasonp for gympie per job. Agents write
results to disk as they get them, never holding them in context; measurements
already taken stand and nothing is re-run.

**The disclosure block, mapped to phase 1.** These are route proposals, not
checks, so: *bits* are projected-at-phase-2 with the modulus stated; *checker*
is the phase-2 artifact the route would end in, described; *sensitivity* is
deferred and marked so; *share of a(40) reached*, *provenance*, *input
footprint* and the entry-ticket levels are answered for real. Do not invent a
private mapping.

Plus: **a proof, or a named obstruction with the step it dies at.** "The pattern
holds on more cells" is round 1's output, banked at zero.

## Team shape

1. **Harness (1), first, alone.** Mechanical prior-work index from
   `results/*.md` titles; the row-40 exposure table re-measured from the current
   banked file with provenance quoted; and a one-page statement of what the two
   engines actually share, sourced to `core/transition.h` and the kink kernel,
   so every lane argues independence against the real thing rather than a
   paraphrase. No hypotheses.
2. **Lane scouts (5), in parallel:** L1 (carrying L2's single question), L3, L4,
   L5, L6. Each answers three questions and nothing else: does the route reach
   H = 15..21 at n = 40; at what cost, with a model anchored on its own
   measurement; and which entry-ticket levels does it clear.
3. **Adversaries (2), fixed.** One on independence — default verdict "this
   smuggles the frontier rule back in at level 2", which is a verdict about
   ranking, not admission. One on cost and completeness — the entanglement wall,
   whether any cost model rests on an unmeasured extrapolation, and the blind
   lists against the lead's withheld seed list.
4. **Synthesis (lead).** One ranked ledger; one phase-2 proposal if a lane earns
   it; and the closing statement on the triangle either way.

Model: Fable throughout.

## Generativity — the round runs in waves, not one pass

Added mid-round, 2026-08-12, on jasonp's instruction, after L4 closed: a fan-out
in which every agent gives exactly one idea a thorough look and then reports
that there is nothing is not a search. **Ruling something out is half a lane's
job. The other half is what the obstruction tells you to try next.**

`results/triangle-r3-queue.md` is the shared append-only idea queue, with its
protocol at the top. Every agent that closes a candidate files at least two
successor rows, different in kind rather than parameter tweaks: what would have
to be different about the problem for it to work, whether an adjacent object has
that property, and what the obstruction proves about the family rather than the
instance. "None — the obstruction is terminal for this whole family" is an
answer only when it is argued. Rows are cheap and half-formed rows are wanted;
cross-lane rows are wanted; an unfiled idea costs the round more than a bad row
does. L6's pruned near-misses go in the queue rather than into a silent cap.

Between waves the lead runs a **triage pass**: rank the OPEN rows by the queue's
standing order, dispatch the top ones as the next wave, and record what was
dropped and why. **The round ends when two consecutive triage passes produce no
row worth dispatching** — not when the first wave of lanes reports back. That
dry condition, met twice, is what licenses the closing statement; a single quiet
wave does not.

## Stop conditions

**REVISED 2026-08-12, and the revision is the point.** The original text ended
the round on two consecutive dry triage passes. **That rule is withdrawn on
jasonp's instruction: never stop making ideas.** The queue outlives the round
that opened it, and no brief here again carries a condition whose satisfaction
is a reason to stop generating.

The evidence is this round's own record. Every closure threw off something
better than what it killed: the involution lane died on a two-horn dilemma
whose escape *was* the cancellation family; the contour lane died by
state-space isomorphism, and that isomorphism produced the definition-level
proof — the round's best idea, from its worst-performing lane; the quotient
lane's cost floor is what made anyone ask what an implicit count would look
like. None of it was in any brief, and the lead's withheld seed list did not
contain the one route that survived.

What remains:

- A lane that clears neither ticket level files the reason **and its
  successors**. A closure without successors is an incomplete deliverable, not
  a negative result.
- No lane builds anything, and no lane runs compute — see
  `docs/r3-job-dispatch.md`. A scout that starts writing a sweep mode, or
  launches a background job, has left its brief.
- If every lane fails both levels, the proved statement that the rule cannot be
  varied within reach is a **deliverable, not a terminus**. File it, then file
  what it makes newly askable.

## Deliverable — exact paths, assigned here

Nobody invents a filename. Write to your assigned path and no other; if you need
a second file, name it with your lane's prefix and say so in the main file.

| agent | blind list, filed first | main deliverable |
|---|---|---|
| harness | — | `results/triangle-r3-harness.md` |
| L1 (+L2's question) | `results/triangle-r3-blind-l1.md` | `results/triangle-r3-l1-corner-gluing.md` |
| L3 | `results/triangle-r3-blind-l3.md` | `results/triangle-r3-l3-contour.md` |
| L4 | `results/triangle-r3-blind-l4.md` | `results/triangle-r3-l4-quotient.md` |
| L5 | `results/triangle-r3-blind-l5.md` | `results/triangle-r3-l5-constraint.md` |
| L6 | `results/triangle-r3-blind-l6.md` | `results/triangle-r3-l6-wildcard.md` |
| adversary, independence | — | `results/triangle-r3-adv-independence.md` |
| adversary, cost + completeness | — | `results/triangle-r3-adv-cost.md` |
| lead | — | `results/triangle-r3-synthesis.md` |

Scripts go under `experiments/tristruct/` named `r3_<lane>_<purpose>.py` (or
`.cpp`); logs alongside as `r3_<lane>_<purpose>.log`. Nothing under `build/`,
nothing in `/tmp`, no edits to any existing script or engine.

Each main file carries its mapped disclosure block and its entry-ticket
paragraph. The lead's synthesis carries the ranked ledger and the phase-2
proposal if one is earned; one line lands in `HANDOFF.md` recording what the
final round bought.
