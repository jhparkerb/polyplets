# Round 3 — wind-down record

2026-08-12/13. Written at close on jasonp's instruction: stop everything, record
what each process was for and whether it finished, clean up. This is the
what-was-running record; the findings are in
`results/triangle-r3-synthesis.md` and the open work is in
`results/triangle-r3-queue.md`.

## Agents

None running. All fourteen were stopped or completed; every one filed its
deliverable to disk before stopping. Two (`r3-l4`, `r3-l5`) were terminated
mid-task for running jobs on gympie and their unfiled context was lost —
`r3-l4b` and `r3-l5b` restarted and completed that work.

## Jobs — what they were for, and whether they finished

| job | box | purpose | status |
|---|---|---|---|
| L5-JOB-1 | gympie (approved per-job) | compile the two Lean bridge theorems; regenerate the truncated eval log; run the RED mutant | **COMPLETED, FAILED gate A** — 9 errors at 6 sites in `r3_l5_normalization.lean`; gates B and C never ran. Repair deferred by jasonp. Log: `experiments/tristruct/r3_l5_job1.log`, errors in `r3_l5_normalization.log` |
| ADV3-JOB-1 | dalby | rook-stencil schema vs published square-lattice data, extend n<=9 to n<=14 | **KILLED AT WIND-DOWN**, 22 min in, through H=10 of 14 (H=10 took 397 s; the tail heights are the cost). Partial log: `dalby:~/src/polyominoes/experiments/tristruct/r3_adv3_n14.log`. The already-banked result stands: 117 external comparisons green at n<=9 plus H=2,3 to n=33 |
| KANCH-JOB-1 | ayr | king-stencil schema vs A006770's external 18-term prefix, extend n<=8 to n<=13 | **KILLED AT WIND-DOWN**, 5 min in, through H=9 of 13. Partial log: `ayr:~/src/polyominoes/experiments/tristruct/r3_kanchor_n13.log`. The already-banked result stands: 8 external row-sum comparisons green at n<=8, zero banked imports, RED verified |

Both killed jobs are stateless and rerunnable from scratch; nothing is lost but
elapsed time, and neither had reached a new external comparison beyond what is
already filed.

## Processes killed earlier in the round (gympie, against the standing rule)

Eleven, in three sweeps: two Lean runs and their `lake`/shell parents (~5.4 GB
RSS each), L1's band c-distribution (21 min) and dp_counts sweep (10 min), L4's
fixed-H exact run (8 min, 2.7 GB, under a 3500 s timeout), and a third Lean
relaunch. Cause was the brief's "laptop minutes" allowance, since replaced by
`docs/r3-job-dispatch.md`. Partial results were labelled KILLED MID-FLIGHT in
the lanes' own files; nothing was reconstructed or estimated.

## tmux

- **gympie**: the `l5job` window closed itself when the job exited. Remaining
  windows (`2.1.228`, `vim`) are jasonp's, untouched.
- **dalby**: `adv3job` window gone with its process. Remaining: `htop`,
  pre-existing, untouched.
- **ayr**: `kanchjob` window gone with its process. Remaining: `makegates`,
  `makegates2`, `makegates3`, pre-existing, untouched.

Verified after shutdown: no `r3_*`, `lean`, or `lake` processes on any of the
three boxes.

## Left on disk, deliberately

- `results/ns_a40/dalby-run-evidence/` — the a(40) production run's
  build-stamped `run.log`, three checkpoints, combine log, and the Zero Harvest
  artifact, copied from dalby with sha256 verified both sides. Banked because it
  is the only material converting the a(40) provenance record from assertion
  into evidence.
- **NOT banked, and still at risk:** the B1 cancellation run on dalby —
  `~/src/polyominoes/results/cutcount_b1/` (`calib_run.log` + `rows/C1..C16.out`)
  and the untracked working source that produced it (sha 59e90660, tree stamped
  `3b7359de-dirty`, matching no committed blob). Those rows are the round's
  largest result: their second differences reproduce banked T(40,15) and
  T(40,16) exactly, i.e. **21.64% of a(40) independently recounted** by a rule
  that never decides connectivity. Verified here to all 31 digits. The numbers
  are reproduced in `results/triangle-r3-ladder-gate.md`; the code is not in
  git anywhere.
- Two job requests filed and not run: LG-JOB-1 (bytes-per-window, blocked on a
  ~20-line residue-payload variant nobody has authored) and the two killed jobs
  above, both rerunnable as-is.

## Uncommitted

Everything from this round is uncommitted working-tree state: the brief, the
dispatch protocol, ~14 deliverables under `results/triangle-r3-*.md`, the queue,
the scripts under `experiments/tristruct/r3_*`, and the banked run evidence.
Committing is jasonp's call.

## CORRECTION, 2026-08-13 (round 4, at final shutdown)

**"None running. All fourteen were stopped or completed" was false.** Nine
round-3 teammates were still alive twelve hours later and were only found by
accident, when a `TaskStop` against an already-stopped id printed the running
list: `brief-reviewer`, `r3-harness`, `r3-l6`, `r3-l1`, `r3-l3`,
`r3-involution`, `r3-adv-independence`, `r3-adv-cost`, `r3-l4b`. All nine
stopped at 07:06 EDT 2026-08-13.

The cause is a false model of the agent lifecycle that survived two rounds:
agents were believed to exit after filing. They do not — they file, go idle,
and persist holding context. An idle notification is not an exit.

**The census method, since this cost two rounds to learn.** `ListAgents`
reports SendMessage *reachability* and returns "No reachable agents" whether
eighteen are running or none — it never lists in-process teammates. The
enumeration that works is `TaskStop` with any invalid id: the error names every
running teammate. Use that, not `ListAgents`, before claiming a team is closed.

Corollary for future rounds: an idle agent can be continued with `SendMessage`
at its full context. Spawning a fresh agent to re-read the round's accumulated
deliverables is strictly more expensive and was done nineteen times in round 4.
