# Job-start checklist

Consult before launching any compute job, local or remote. It targets the three
failure modes that have actually bitten us: **resource conflicts, unclear
purpose, lost provenance.** Don't launch until every box is checked.

1. **Predict the cost — for any job that could be large, long-running, or
   important.** Wall time, peak RAM, peak disk, CPU cores — from calibration/
   measured data, not a guess. If no prediction exists, benchmark a small case to
   establish one first. A trivial throwaway run is exempt; anything whose size,
   runtime, or result you'd care about is **never launched blind.**

2. **Fit the budget — against the MAX cost of what's already running.** Check the
   prediction against the target machine's limits, both real (ayr 78 GB / 32
   cores; gympie 24 GB) and self-imposed (gympie ≤10 perf cores). **Sum it with
   the projected PEAK RAM/cores of the jobs already on that machine — not their
   current RSS** (a job sitting at 1 GB now may be headed for 16 GB). Overcommit/
   swap is not "fitting." No real headroom → don't launch.

3. **Run from a saved, self-describing in-repo script** (not `/tmp`, not a stdin
   heredoc, **never a long-lived `python -c` / `-e` one-liner**) — committed or
   not. Header comment states: purpose, exact command, target machine, predicted
   cost (item 1), and how to resume/kill it. Inline `-c` is fine *only* for a
   trivial, instant probe; anything that runs nontrivially or whose output matters
   goes in a file.

4. **Provenance + observability — mandatory for binaries, encouraged for
   scripts.** A binary MUST carry a baked commit/build stamp and MUST emit the
   `start`/`heartbeat`/`done` event stream (ISO-8601, stated denominator,
   self-computed ETA) to a persistent log — a result you keep must not trace to a
   dirty/unknown tree, and a long binary must report its own progress. Scripts
   should do the same (cheap via `obs.py`) but it's nice-to-have, not a gate.
   Binaries go in `build/`, never `/tmp`. See `docs/observability.md`.

   - **Clean, current rev — explicit gate for any run whose result you'll keep.**
     Before launching, read the *deployed* binary's stamped `GIT_REV` and confirm
     it is **(a) clean** — no `-dirty` suffix (a `-dirty` stamp means uncommitted
     changes that won't survive the run) — **and (b) actually contains the change
     you intend to run.** (b) is the one that bit us: the **A1 incident**
     (AUDIT-2026-06-28) was a correct fix sitting *uncommitted* on one host while
     a remote box ran a clean-but-*stale* binary with the old behavior. After any
     engine edit: commit, then rebuild+redeploy on the target box (a stale binary
     silently ignores new flags/fixes), then re-read the rev. A clean stamp that
     doesn't match HEAD-with-your-fix is the same failure wearing a clean suit.

5. **Recoverable — long/important jobs MUST checkpoint and resume.** Not optional:
   a kill or a lost conflict must cost one unit, not the whole run. A job that
   can't checkpoint is **badly behaved — a defect to fix before running it long,
   not a status that earns protection**; being important does not excuse being
   un-interruptible. SIGSTOP and kill are last-resort break-glass for a conflict
   that items 1–2 should have prevented — not routine operating tools.

6. **Recorded so its purpose is legible at a glance.** One line — what's running
   and *why*, with its result tier — in the ledger/HANDOFF, so anyone (me,
   especially) can answer "what is this and does it matter?" without
   reconstructing intent later.
