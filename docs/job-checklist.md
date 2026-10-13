# Job-start checklist

Consult before launching any compute job, local or remote. It targets three
failure modes: resource conflicts, unclear purpose, lost provenance. Don't
launch until every box is checked.

1. Predict the cost, for any job that could be large, long-running, or
   important. Wall time, peak RAM, peak disk, CPU cores, from calibration or
   measured data, not a guess. If no prediction exists, benchmark a small case
   to establish one first. A trivial throwaway run is exempt; anything whose
   size, runtime, or result you'd care about is never launched blind.

2. Fit the budget, against the largest cost of what's already running. Check
   the prediction against the target machine's limits, both real (the 32-core
   server has 78 GB; the laptop 24 GB) and self-imposed (the laptop: at most 10
   performance cores). Sum it with the projected peak RAM and cores of the jobs
   already on that machine, not their current RSS (a job sitting at 1 GB now
   may be headed for 16 GB). Overcommit and swap are not "fitting". No real
   headroom: don't launch.

3. Run from a saved, self-describing in-repo script (not `/tmp`, not a stdin
   heredoc, never a long-lived `python -c` / `-e` one-liner), committed or
   not. Its header comment states: purpose, exact command, target machine,
   predicted cost (item 1), and how to resume or kill it. Inline `-c` is fine
   only for a trivial, instant probe; anything that runs nontrivially or whose
   output matters goes in a file.

4. Provenance and observability, mandatory for binaries, encouraged for
   scripts. A binary carries a baked commit/build stamp and emits the
   `start`/`heartbeat`/`done` event stream (ISO-8601, stated denominator,
   self-computed ETA) to a persistent log: a result you keep must not trace to
   a dirty or unknown tree, and a long binary must report its own progress.
   Scripts should do the same (cheap via `scripts/obs.py`), but for them it is
   not a gate. Binaries go in `build/`, never `/tmp`. See
   `docs/observability.md`.

   - Clean, current rev: an explicit gate for any run whose result you'll
     keep. Before launching, read the deployed binary's stamped `GIT_REV` and
     confirm it is (a) clean, with no `-dirty` suffix (a `-dirty` stamp means
     uncommitted changes that won't survive the run), and (b) actually contains
     the change you intend to run. (b) is the one that fails in practice: a
     correct fix sitting uncommitted on one host while a remote box runs a
     clean but stale binary with the old behaviour. After any engine edit:
     commit, then rebuild and redeploy on the target box (a stale binary
     silently ignores new flags and fixes), then re-read the rev. A clean stamp
     that doesn't match HEAD-with-your-fix is the same failure.

5. Recoverable: long or important jobs checkpoint and resume. A kill or a lost
   conflict must cost one unit, not the whole run. A job that can't checkpoint
   is a defect to fix before running it long, not a status that earns
   protection; being important does not excuse being un-interruptible. SIGSTOP
   and kill are a last resort for a conflict that items 1–2 should have
   prevented, not routine operating tools.

6. Recorded so its purpose is legible at a glance. One line, what's running
   and why, with its result tier, in the run's PROVENANCE.md, so anyone can
   answer "what is this and does it matter?" without reconstructing intent
   later.
