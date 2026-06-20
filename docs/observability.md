# Observability & provenance

Shared standard for every long-running program in this repository (and its sibling
repos — this file is maintained identically across them; see [Adoption](#adoption)).

How a program reports what it is, when it started, how it's progressing, and when
it will finish. The goal: a job's log alone — with no `stat`, no guessing, no
cross-referencing file mtimes — answers *"what code is this, is it alive, how far
along, and when will it land?"*

## Principles

1. **Every timestamp is absolute and unambiguous.** ISO 8601 with date *and*
   timezone: `2026-06-20T06:43:08+10:00` (or UTC `…Z`). Never a bare wall-clock
   time, never a duration without its anchor. A reader must never have to ask
   "06:43 *which day*?" or recover the date from a file's mtime.

2. **A job announces its own START and DONE.** The first line written is a `start`
   event; the last is a `done` event carrying the result. Wall time is then
   `done.t − start.t` from the log alone — no `stat`, no "assume it began when the
   previous unit ended."

3. **State the denominator up front.** At `start`, declare the total work if
   knowable (target size, range, work-unit budget). Progress is only meaningful as
   `done/total`. When the total is genuinely unknown, emit a monotonic counter and
   a rate so a watcher can still extrapolate.

4. **Heartbeat on a wall-clock cadence, not per-iteration.** One `heartbeat` line
   every ~30–60 s (or every 1% of work, whichever is *rarer*) — enough to confirm
   liveness and slope, not so much it floods. Each carries elapsed, fraction done,
   current rate, and a **self-computed ETA** derived from measured throughput, not
   guessed. The job knows its own rate better than we can reconstruct it.

5. **One line, both audiences: logfmt.** `key=value` pairs, space-separated, one
   event per line, leading `event=`. Humans skim it; `awk`/`grep`/`cut` parse it;
   no multi-line records, no JSON ceremony. Never use `\r` overwrite: every line
   is newline-terminated and survives in the log.

6. **Unbuffered / line-flushed output.** Progress that appears only when a buffer
   fills, or only at exit, is useless mid-run. Flush every event so `tail -f` is
   truthful in real time.

7. **The `done` line is the canonical ledger entry.** It restates absolute start,
   absolute end, total wall seconds, the result value(s), and the key cost metrics
   (program-specific peak metric, CPU time, peak RSS). Self-contained: paste it
   into a results ledger without re-deriving anything.

8. **Stable, predictable location.** Each unit writes its own `*.log` beside its
   `*.out`, named deterministically by its parameters. One unit, one file; no
   shared append-races.

9. **Self-identifying programs (provenance).** Every program reports the source
   that produced its numbers. See [Provenance](#provenance) — it has enough sharp
   edges to warrant its own section.

10. **Predict before frontier work.** No long run starts without a data-grounded
    runtime/memory/disk prediction from calibration. The ETA in principle 4 is the
    *running* form of the same discipline: the prediction made continuously from
    the job's own measured rate.

## Canonical formats

**Log stream** (the `*.log` file, one event per line):

```
event=start     job=<unit> t=2026-06-20T06:43:08+10:00 git=ed2ce1f dirty=0 built=2026-06-19T22:14:03+10:00 host=<host> total=<N> threads=6
event=heartbeat job=<unit> t=2026-06-20T10:00:00+10:00 elapsed_s=11812 done=0.31 rate=2280/s eta=2026-06-21T03:05:00+10:00
event=done      job=<unit> t=2026-06-21T03:07:41+10:00 start=2026-06-20T06:43:08+10:00 wall_s=73473 cpu_s=433901 peak_rss_mb=4612 result=...
```

**Output/checkpoint file header** (the `#`-comment banner at the top of each
`*.out` / data / checkpoint file). Human-first, and coexists with `#`-comment
conventions in data formats:

```
# <prog> | commit ed2ce1f | <host> | 2026-06-20T06:43:08+10:00 | job=<unit>
# source: /abs/path/to/<prog>
```

Same provenance fields in both; the log stream is the machine-parseable form, the
file header is the human/at-rest stamp.

## Provenance

**The field that matters is `git` (HEAD), reported however the language makes the
running artifact knowable. Capture it differently by language, emit the same
fields.**

- **Compiled:** bake the commit in at *build* time via a `-D` define; the binary
  outlives the source state, so a binary built days ago must report the commit it
  was *built* at, not whatever the tree is now.

  ```make
  GIT_REV   := $(shell git rev-parse --short HEAD)
  GIT_DIRTY := $(shell git diff --quiet 2>/dev/null || echo -dirty)
  CXXFLAGS  += -DGIT_REV='"$(GIT_REV)$(GIT_DIRTY)"' \
               -DBUILD_TIME='"$(shell date -u +%Y-%m-%dT%H:%M:%SZ)"'
  ```

- **Interpreted (Python/shell):** capture at *startup* — the source running *is*
  the source on disk — but **anchor the git query to the script's own directory,
  not `$CWD`** (else you report whatever repo you launched from), and include a
  **content hash** so the record survives when git can't answer. Factor this into
  one shared provenance module rather than copying it per consumer.

  Two traps specific to interpreted code:
  1. Anchor to the script: resolve `__file__` / `$0`, run git against *that* path.
  2. `dirty` matters *more* here, not less — there's no compile gate; you can edit
     a script and run it one second later. The `-dirty` flag is the only thing
     between "commit ed2ce1f" and "ed2ce1f plus an uncommitted change."

### HEAD vs. "the commit a file is at"

Make `t.py` at commit 100, then land 50 more commits that never touch `t.py`, so
HEAD is 150. What does `t.py` report?

- **It reports 150.** Git has no "commit a file is at"; `rev-parse HEAD` is a
  property of the *repo*. The file's bytes are identical across 100–150, so there
  is nothing to report but HEAD.
- **It *should* report 150** — as the primary anchor. Provenance answers *"what do
  I check out to reproduce this number?"* and the answer is **150 (clean)**:
  check out 150 and you get `t.py`-as-run **plus every sibling it imports, every
  data file it reads** as-run. Only HEAD gives that guarantee.
- **The tempting wrong answer is 100** — `git log -1 --format=%h -- t.py`, "the
  commit that last touched the file." It quietly lies in the multi-file case: if
  `t.py` imports a module that one of those 50 commits changed, **100 does not
  reproduce the run and 150 does.** Reporting 100 implies "nothing relevant
  changed since 100," which you don't know.

| field | command | answers | role |
|-------|---------|---------|------|
| `git` | `git rev-parse --short HEAD` | what tree state ran → **reproducible** | **primary, always** |
| `file_rev` | `git log -1 --format=%h -- t.py` | when this file last changed → descriptive | optional human hint |

Report HEAD always; it is never wrong (when 100 *would* reproduce, so does
150-clean). Add `file_rev` only as a labeled hint — never as a substitute.

A `dirty` build can't be reproduced from a commit alone, so any *result* from a
dirty binary is provisional until rebuilt clean.

## Adoption

This file is the single source of truth, maintained identically across the sibling
repositories. To adopt or sync: copy it verbatim, then have the repo's top-level
engineering-guidelines doc link to it rather than restating these rules. Keep the
content byte-identical across repos so a diff is the only thing that ever needs
reviewing.
