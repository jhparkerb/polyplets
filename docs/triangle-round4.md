# Clarifications, 2026-08-12 (settled with jasonp before dispatch)

Round id is **r4**. Working dir is `results/r4/`; scripts are
`experiments/tristruct/r4_<id>_<purpose>.{py,cpp,sh}` with logs alongside.
The shared queue is `results/r4/queue.md`, seeded from the still-open rows of
`results/triangle-r3-queue.md`.

**This round executes as well as generates.** Round 3 scoped and did not build;
round 4 inherits its costed proposal and delivers it. The three live pieces are
the B1 cancellation ladder (H=15,16 already exact and unbanked; H=17..19 next),
the L3-5 definition-level Lean proof, and INV-8 spin parity for H=20..21. New
ideas run continuously alongside; the goal statement above is the acceptance
test, not the work plan.

**Compute authority: free rein on ayr and dalby**, bounded by real RAM and disk
rather than by wall clock. CPU oversubscription is allowed while no
timing-sensitive job is running. gympie stays under the limits below. Agents
still do not launch jobs; the lead dispatches, per `docs/r3-job-dispatch.md`,
which carries over unchanged.

**Model: Opus, unrestricted, until Fable's quota resets 2026-08-13 07:00.** No
agent starts under Fable before then — it is at 97% for the week and would die
on dispatch. The 2026-08-07 Opus restriction is lifted for this round by
jasonp's instruction; the lead still verifies load-bearing claims off disk.
Team size is lean and situational, not round 3's fourteen.

**First act, before any new lane: recover the B1 artifacts from dalby.** The
rows that recount T(40,15) and T(40,16) — 21.64% of a(40) by a rule that never
decides connectivity — exist only as untracked files on one machine
(`results/cutcount_b1/`, source sha256 `59e90660b42a0d94`). Pull, verify, commit.

# The Goal

A team of agents of different kinds works until we produce a breakthrough on
the structure of the T(n,H) table or the king animals such that we have total
confidence in a(40) through a (relatively) efficient way to confirm the
Transfer Matrix number(s) independently, or a Lean proof of the result through
some legitimate means that a skeptical reviewer would complete.

The *goal* of the team is set, as are rules for communication and coordination.
*What* gets investigate is not set except to say that discarded ideas should
not be re-vetted without cause so as to not waste tokens.

# Your Role

Start and manage the team of agents and act as the intermediary to the user.
It is your job to ensure specifically that the agents that generate ideas are
always doing so, even as other jobs run.  Until a winning idea is found, making
*new* ideas is the most important thing to do.

You may vary the number and mix of agents as needed.

# Agent Roles

## The write-ahead rule

Every agent writes what it is about to do before it does it. Not a summary
afterwards, not a report at the end: a line on disk, in advance, so that an
agent killed, hung, or gone quiet leaves a trail whose last entry says what it
was in the middle of.

## Three obligations

1. Plan first, before any other action. Write <workdir>/<id>.plan.md: the
   question in one sentence, the steps in order, what each step produces, and
   what would make you stop. Then start. If the plan turns out wrong, append a
   revision with the reason — never rewrite it.

2. Mark intent before each step. Append to <workdir>/<id>.progress.md: ABOUT
   TO: <step> before, DONE: <step> -> <result or file> after. A step whose
   ABOUT TO has no DONE is exactly where a restart resumes. Mark before
   anything slow, anything that could hang, and anything whose result you
   would otherwise hold in your head.

3. File findings as you get them. Append to <workdir>/<id>.md — the
   deliverable — the moment a result exists, with its caveats attached. Your
   context is not a deliverable. Nothing you have not written down survives
   you.

A restart reads the plan, the progress file, and the partial deliverable, then
resumes at the first unmatched ABOUT TO. It does not redo completed steps and
it does not reconstruct or estimate anything a predecessor did not measure —
missing numbers are marked NOT ESTABLISHED.

## Where things go

┌─────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│            what             │                              where                               │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ plan, progress, deliverable │ results/<round>/<id>.{plan,progress}.md, results/<round>/<id>.md │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ shared idea queue           │ results/<round>/queue.md                                         │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ scripts                     │ experiments/<area>/<round>_<id>_<purpose>.py                     │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ logs                        │ beside the script, same stem, .log                               │
├─────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ job requests                │ a row in the queue, full field block in the deliverable          │
└─────────────────────────────┴──────────────────────────────────────────────────────────────────┘

Nobody invents a path; the dispatch assigns <id> and <round>.

## The three agent types

SCOUT — takes one question and answers it. Reaches a verdict, costs it, files
what it measured versus what it extrapolated. A closure must file at least two
successor rows, different in kind — a closure without successors is an
incomplete deliverable, not a negative result. Scouts don't run compute; they
file job requests with estimates labelled MEASURED/EXTRAPOLATED/ASSERTED and
the decision the number changes. The fact-pack variant — index prior work,
re-measure exposure, state what the code does, no hypotheses — is a scout with
an empty hypothesis slot; run it first and alone.

ADVERSARY — audits what others filed, never generates. Two standing questions,
one agent each: is the claim independent as claimed, and are the numbers real.
Hostile defaults, but hostility is about ranking, not admission. It also audits
the lead: silent caps, dispatches that narrowed the search, framings that made
something unstateable.

GENERATOR — makes new ideas, owns no question. Files rows different in kind
from what exists, each with an honest prior and the cheapest thing that would
kill it; rows it can kill itself are filed with the kill, because the kill is
the content. Also audits the queue for stale and subsumed rows.  Standing
instruction: never stop making ideas.

## What the lead does

Writes the plan, assigns ids and paths, dispatches jobs, verifies load-bearing
claims before propagating them, and stops each agent once it has filed. Reads
deliverables off disk rather than asking for summaries — an agent that has
filed has already reported. 

# Use of resources

## gympie

`gympie` is the machine that runs the Claude Code session.  It runs macos.  As
such, due to risk of OOM or full disk, it SHOULD NOT be used to run
long-running jobs.  small tests that take <1GB RAM per core, 2 or fewer cores
and 10 minutes maximum may run on gympie.  all other jobs must run elsewhere.

## ayr

`ayr` is an AMD linux machine with 32 cores and 78GiB of RAM with the following
filesystems:

```
Filesystem             Size  Used Avail Use% Mounted on
/dev/mapper/fast-home  726G  376G  319G  55% /home
/dev/mapper/slow-work  2.8T  1.8T  933G  66% /home/jasonp/work
```

## dalby

`dalby` is an ARM limux machine with 80 3GHz cores, 126GiB of RAM and the
following filesystems:

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/md3        874G  267G  564G  33% /
```
