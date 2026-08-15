# Offside — the candidate research-state design (fixed text for review)

2026-08-14. This freezes the design under review by the Offside panel. It is
a candidate, not a decision. Origin: Li et al. (arXiv 2608.11195) plus this
repo's own stale-state incidents; evolved through docs/process-proposal.md
(v3, an earlier and partly superseded shape) and an operator/lead discussion.

## The problem

A long-horizon research program executed by amnesiac agent sessions steered
by one human operator. Observed failure modes, all with incidents on record:
status claims outliving their evidential status (three stale-memory incidents
on 2026-08-14 alone); curated summaries decaying under iterated rewriting
toward a genre that drops caveats; knowledge unfindable at need;
re-derivation of banked results; lost caveats governing decisions weeks
later (Li et al.'s session-44 withdrawal and 25-day reproof).

One additional hard constraint, operator-verified: **the agent has no sense
of time.** It does not experience elapsed duration, reads clocks only when a
tool shows one, and its effort estimates for cognitive work ("an afternoon",
"weeks") bear no relationship to reality. Any design that requires the agent
to judge elapsed time or estimate durations is broken on arrival.

## The candidate design

Partition state by **decay mechanism**, not by topic or epistemic kind:

1. **Claims are code; status is computed, never written.** The atomic unit
   of known things is a claim: name, one-line statement, tier (proved /
   two-source / single-source / measured-once), and an executable check —
   or an explicit `check: none`, which every rendering displays loudly.
   "Is this settled?" is answered by running the claim suite, not by
   reading a cell someone typed weeks ago. Precedent: the paper+verifier
   pairs (`verify_claims.py` 448/448, `verify_technical_report.py`) are
   the only state layer in the repo that has never rotted, and the reason
   is structural — their status is an output.
2. **Everything non-executable is a bet, and bets expire.** Hypotheses,
   priorities, plans, operational assertions (running jobs, machine
   states, ETAs) carry a machine-made timestamp at write and a TTL fixed
   per species as a schema constant (e.g. operational: days; hypothesis
   priority: weeks). An expired bet is treated as absent: it cannot be
   consumed until a session re-verifies it, which restamps it. Time never
   passes through the agent: stamps are written by the machine, expiry is
   computed at render, TTL lengths are operator-set constants, and the
   agent's own effort estimates are banned from becoming durations
   anywhere. Every "price" field is a measured receipt or "unmeasured".
3. **Views are rendered, never maintained.** The things a session reads at
   open — open threads, live doors, debts, operations — are outputs of
   `make state`, generated from claim files, bets, and the append-only
   chronicle. Nothing hand-maintains an index (three hand-maintained
   derived indexes have already died in this repo: ROADMAP.md, the results
   map, the dependency map). Rendered views cannot disagree with their
   sources; residual staleness is source-vs-world, covered by checks and
   TTLs. Expired bets and naked claims surface at session-open as loudly
   as a red gate.
4. **Progressive disclosure is the context-loading policy.** Four rungs:
   name (a unique grep token, minted at thread birth, used in every
   artifact) → one-liner → paragraph with receipts (the results note) →
   paper with verifier. Each rung answerable without loading the next.
   Sessions read rung one/two by default.
5. **Papers spawn red-first or not at all.** A notable result owes a
   paragraph and a named check in that draft's verifier, same act. The
   results note is the larval draft; a draft paper is born when results
   notes start citing each other, and it is born with its checker.
   Merging/splitting drafts moves named checks; the gate's invariant is
   every check owned by exactly one draft, every asserted number checked.
   Negative-result papers are allowed; how-it-was-solved lives in
   comments.
6. **Doors are a rendered table.** Every closed or parked thread carries
   Lock / Reopen / Converts-to (/ Price when parked) in its primary doc;
   the view collects them; a standing operations item is to read all
   Locks and Converts-to lines in one sitting, because cross-thread
   obstruction patterns are invisible from inside one thread.
7. **The chronicle is append-only narrative with no status language**, and
   MEMORY.md stops carrying project state (all three 2026-08-14 incidents
   were memory-layer).

Hard constraints inherited from the operator: super-basic (plain files, one
gate script, no YAML, no database, no framework); anything that executes
runs on ayr/dalby, never gympie; heavier machinery must be deleted if
unused (three unfilled rows → delete the field).

## What the panel is asked

The operator's stated position: neither he nor the lead knows if this is a
good idea or a bad one, and he is not at all confident it is even possible
for it to be a **great** one. The review must answer, with arguments and
not vibes: where this design degrades under real session pressure into what
it replaces; whether the check-writing cost is actually paid or the system
decays into TTL'd prose; whether "great" is achievable in this design
family at all, and what great would look like; and what a qualitatively
different design family would be.
