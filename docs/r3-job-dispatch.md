# Job dispatch protocol — round 3 and after

2026-08-12. Written after seven processes had to be killed on gympie and two
agents terminated to stop them. The round brief's "laptop minutes" allowance
was the cause; this file replaces it.

## The rule

**The test is backgrounding, not size.** If a command has to run in the
background — if you would background it, wrap it in `timeout`, tee it to a log
and come back for it, or if you cannot be confident it finishes while you wait
— **it does not run on gympie.** It goes to ayr or dalby as a dispatched job.

Extremely short-lived foreground work on gympie is fine and is the agent's
judgement call: a seconds-scale probe, a small exact-arithmetic check, a quick
validation against banked data. Use judgement honestly — the question is not
"is this important" but "will this be over before jasonp notices it".

Things that are never a judgement call, because this round got them wrong:
`lean` and `lake` invocations of any kind, anything wrapped in `timeout`,
anything with a multi-GB working set, and anything you have already had to
kill once.

**Real jobs are dispatched by the lead, and only by the lead.** An agent that
wants one files a job request and continues with desk work. It does not wait
idle, and it does not run a "small version" locally while it waits.

## Job request format

File it in `results/triangle-r3-queue.md` as a row with status JOB-REQUESTED,
and state it in your reply to the lead. Every field is required; "unknown" is a
valid value but the field must be present.

    job id:            <lane>-JOB-<n>
    measures:          what number comes out
    decides:           which decision changes if it comes out differently,
                       and what the two branches are. A job that changes
                       no decision is not dispatched.
    command:           the exact command line, script path, and arguments
    script:            path under experiments/, already written and readable
    wall estimate:     with units, and the basis: MEASURED anchor at what
                       scale, or EXTRAPOLATED how far, or ASSERTED
    RAM estimate:      peak RSS, same basis rule
    disk estimate:     working set and final artifact size
    cores:             1, or how many, and whether it parallelizes per-cell
    interruptible:     does it checkpoint; can it resume; what is lost on kill
    RED control:       what corrupted input it must reject, and how you know
    closes:            which NOT ESTABLISHED item this retires

An estimate whose basis is ASSERTED is accepted, but it is dispatched with a
hard timeout at 3x the estimate and the discrepancy is recorded.

## Routing

The lead picks the machine. Standing preferences:

- **ayr** (Linux, 78 GB, 32 cores) — default for anything multi-core or
  RAM-hungry. The budget rule binds: total across ALL running jobs stays inside
  78 GB, and per-worker RAM is (total x margin) / cores, never a flat number.
  The lead checks what is already running before dispatching.
- **dalby** (Linux, Hetzner) — tall-height and RAM-heavy work, NVMe-bound
  phases, and anything that needs to outlive a local session. ssh host is
  `dalby.jhpb.org`.
- **gympie** (jasonp's laptop) — foreground seconds-scale work only, at the
  agent's judgement, per the backgrounding test above. **Nothing that runs in
  the background, ever**, and nothing on the never-a-judgement-call list. His
  standing instruction is that he will kill what he finds there.

Every dispatched job: a named script on disk, run in a tmux window on the
target (`tmux new-window -t 0 -n <name>`, never `new-session`), tee'd to a log
beside the script, PID recorded, waited on by PID rather than polled. No stdin
jobs, nothing under `/tmp`, no binaries outside `build/`.

## File before halt

An agent's context is not a deliverable. **Write results to your file as you get
them**, not at the end — anything unfiled is lost when the agent stops, and in
this round it was. On any stop instruction: write what you have to disk first,
labelled with what is partial and what was killed, then halt. Do not
reconstruct or estimate anything you did not measure.

## What the lead owes back

When a job finishes, the lead returns the numbers, the log path, and the actual
wall and RSS against the estimate. When a job is refused, the lead says why —
usually that it decides nothing, duplicates a closed-form answer, or does not
fit the box today.
