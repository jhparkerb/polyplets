# Agent types, and the write-ahead rule

2026-08-13. Replaces the per-round team-shape sections. Three types is enough;
round 3 used fourteen agents and they were all one of these.

## The write-ahead rule — this is the point of the file

**Every agent writes what it is about to do before it does it.** Not a summary
afterwards, not a report at the end: a line on disk, in advance, so that an
agent killed, hung, or gone quiet leaves a trail whose last entry says what it
was in the middle of. Round 3 lost work three times because context died with
the agent.

Three obligations, in order:

1. **Plan first, before any other action.** Write `<workdir>/<id>.plan.md`:
   the question in one sentence, the steps in order, what each step produces,
   and what would make you stop. Then start. If the plan turns out wrong,
   append a revision with the reason — never rewrite it.
2. **Mark intent before each step.** Append to `<workdir>/<id>.progress.md`:
   `ABOUT TO: <step>` before, `DONE: <step> -> <result or file>` after. A step
   whose ABOUT TO has no DONE is exactly where a restart resumes. Mark before
   anything slow, anything that could hang, and anything whose result you would
   otherwise hold in your head.
3. **File findings as you get them.** Append to `<workdir>/<id>.md` — the
   deliverable — the moment a result exists, with its caveats attached. Your
   context is not a deliverable. Nothing you have not written down survives you.

A restart reads the plan, the progress file, and the partial deliverable, then
resumes at the first unmatched ABOUT TO. It does not redo completed steps and
it does not reconstruct or estimate anything a predecessor did not measure —
missing numbers are marked NOT ESTABLISHED.

## Where things go

| what | where |
|---|---|
| plan, progress, deliverable | `results/<round>/<id>.{plan,progress}.md`, `results/<round>/<id>.md` |
| shared idea queue | `results/<round>/queue.md` |
| scripts | `experiments/<area>/<round>_<id>_<purpose>.py` |
| logs | beside the script, same stem, `.log` |
| job requests | a row in the queue, full field block in the deliverable |

Nobody invents a path; the dispatch assigns `<id>` and `<round>`. Nothing under
`build/`, nothing in `/tmp`, no edits to another agent's files.

## The three types

**SCOUT** — takes one question and answers it. Reaches a verdict, costs it, and
files what it measured versus what it extrapolated. A scout that closes its
question **must file at least two successor rows in the queue**, different in
kind from what it killed: a closure without successors is an incomplete
deliverable, not a negative result. Scouts do not run compute; they file job
requests (with wall/RAM/disk/core estimates each labelled MEASURED,
EXTRAPOLATED or ASSERTED, plus the decision the number changes) and the lead
dispatches per `docs/r3-job-dispatch.md`. The fact-pack variant — index the
prior work, re-measure the exposure, state what the code actually does, no
hypotheses — is a scout with an empty hypothesis slot; run it first and alone
when a round needs a shared factual base.

**ADVERSARY** — audits what others filed, never generates. Two standing
questions, and one agent per question: *is the claim independent as claimed*,
and *are the numbers real*. Default verdicts are hostile ("this smuggles the
shared rule back in", "this figure is extrapolated past its anchor"), but a
hostile default is about ranking, not admission. An adversary also audits the
lead: silent caps, dispatches that narrowed the search, framings that made
something unstateable. Point one at the round's plan before launch — round 3's
brief would have killed four of six lanes without that pass.

**GENERATOR** — makes new ideas, owns no question. Reads everything, files
queue rows that are different in kind from what exists, each with an honest
prior and the cheapest thing that would kill it. Rows it can kill itself are
filed *with* the kill, because the kill is the content. It also audits the
queue for rows that are stale, subsumed, or mis-scoped. Standing instruction:
never stop making ideas.

## What the lead does

Writes the plan, assigns ids and paths, dispatches jobs to the compute boxes,
verifies load-bearing claims independently before propagating them, and stops
each agent once it has filed. Reads deliverables off disk rather than asking
for summaries — an agent that has filed has already reported.
