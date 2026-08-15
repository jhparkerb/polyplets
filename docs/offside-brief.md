# Offside — panel brief

2026-08-14. Thread name: **Offside**. Three lanes, desk-only, no compute.
Mission in one sentence: **judge whether the research-state design frozen in
`docs/offside-design.md` is good, bad, or capable of being great — by
building the strongest independent alternative, the sharpest failure-mode
case, and an empirical replay against real sessions.**

## Common rules (all lanes)

- Desk work only. Reading, grepping this repo, and writing your one output
  file. **Nothing executes anywhere** — no scripts, no builds, no ssh. The
  gympie ban on project code is absolute and greps/reads are exempt.
- Your output file is your deliverable; write it as you go (file before
  halt — context is not a deliverable). Final report = the file path plus
  three sentences.
- Append at least two rows to `results/offside/queue.md` (create on first
  use; format: `| OPEN | <lane> | <one-line question or successor> |`).
  Successors different in kind, not parameter tweaks.
- Do not edit any file other than your own output and the queue. Do not
  commit. The working tree carries the operator's own uncommitted edits —
  touch nothing.
- No pompous naming, no flourish; the operator reads these raw.

## Shared fact pack (read per your lane's list, in order)

- F1: `/Users/jasonp/.claude/jobs/fd684800/tmp/gc-paper.pdf` — Li et al.,
  the prompting case study (skim §2's pure math).
- F2: `HANDOFF.md` — the current state layer and its rot, in the wild.
- F3: `/Users/jasonp/.claude/projects/-Users-jasonp-src-polyominoes/memory/MEMORY.md`
  — the memory index layer (source of the three 2026-08-14 stale-state
  incidents named in HANDOFF's top entry).
- F4: `docs/offside-design.md` — the candidate design (FIXED TEXT).
- F5: `docs/process-proposal.md` — the earlier, partly superseded proposal
  (context for how the candidate evolved; the candidate supersedes it where
  they differ).
- F6: the working verification precedents: `paper/verify_claims.py` (skim
  its structure), `scripts/check_receipts.sh`, `tests/gate_citations.py`.

## Lane A — BLIND ab initio design (output: `results/offside/A-ab-initio.md`)

You do NOT read F4 or F5. Not at all, not "briefly" — your value is that
you have never seen the candidate design or its ancestor, and the operator
specifically wants a design produced from a mind that hasn't. You read F1,
F2, F3, F6, plus the problem statement below, and then you DESIGN, ab
initio, the state system you would build. File your design complete before
anything else; mark the file "filed blind" with the date line first.

The problem: a long-horizon mathematical research program run by amnesiac
agent sessions (fresh context each session), steered by one expert human
operator, on a repo with results notes, proof docs, gates, compute jobs on
two remote boxes, and a paper with a claim-verifier. Observed failure
modes: status claims outliving their evidence; curated summaries decaying
under rewriting; re-derivation of banked results; caveats lost across
handoffs; three stale-state incidents in one recent day, all in the memory
layer. One hard constraint, operator-verified: the agent has NO sense of
time — no felt duration, clocks read only when a tool shows one, effort
estimates for cognitive work unrelated to reality. Operator constraints:
super-basic (plain files, one gate, no frameworks, no databases); grep is
the retrieval primitive; short evocative thread names are established
practice and have proven retrieval value.

Design for THIS problem, not a generic one. Commit to mechanisms, not
principles — say what a session reads at open, what a result writes, what
a gate checks, what happens to a hypothesis over its life. Then, still
blind, write one page: the three decisions in your design you are least
sure of, and what evidence would settle each.

## Lane B — adversary on the candidate (output: `results/offside/B-adversary.md`)

Read F1–F6, F4 hardest. Your job is the case AGAINST: where the candidate
degrades under real session pressure into what it replaces; whether the
check-writing cost gets paid or the system decays into TTL'd prose; every
mechanism whose enforcement is by exhortation rather than by gate; the
TTL-expiry failure modes (what legitimate long-lived truth gets wrongly
expired? what does re-stamping cost? who re-verifies, with what?); the
rendered-view failure modes (what can a generated view get wrong that a
hand-written one wouldn't? what happens when the renderer has a bug — who
gates the gate?); and the operator's ceiling question, argued honestly:
is GREAT achievable in this family, or is the family capped at "better
than HANDOFF", and what specifically caps it? Rank your objections by how
much they should change the decision; separate "fixable with a tweak" from
"structural". Concede what the design gets right — an adversary that
concedes nothing is not read.

## Lane C — replay against real sessions (output: `results/offside/C-replay.md`)

Read F1–F6, then reconstruct THREE real working days from the chronicle
and git log and replay them against the candidate design, concretely:

- 2026-08-14 evening (HANDOFF's top entry): the five-item backlog set with
  three stale-state incidents, two agent lanes, one closed-door result.
- 2026-08-14 morning (the Motley/Coin Lift entry below it): plan reviews,
  an engine ceiling bug, a production launch (Confetti) with receipt
  enforcement.
- One compute-heavy banked day of your choice from deeper in HANDOFF
  (e.g. the a(40) run or the H=17 rung).

For each: list every read the candidate demands at session open and every
write it demands as the day progresses (count them; the operator's concern
is writes-per-session); identify each moment the candidate would have
prevented a recorded mistake, changed a decision, or added friction with
no payoff; and note anything the day did that the candidate cannot
represent at all. End with the honest tally: for these three days, does
the candidate pay for itself? Where the answer depends on an unmeasured
quantity, name the measurement.

## Stop conditions

One pass each; no second wave unless the lead dispatches queue rows
explicitly. If your lane's core judgment is reached early, file and stop —
padding is a defect. If you find yourself designing a framework, stop and
reread the operator constraints.
