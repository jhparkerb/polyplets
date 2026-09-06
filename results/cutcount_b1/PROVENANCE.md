# B1 cancellation run — recovered from dalby, 2026-08-12

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

Round 4's first act, per `docs/triangle-round4.md`. Until now these files
existed only as untracked working-tree state on one machine; the round-3
wind-down (`results/triangle-r3-winddown.md`) flagged them as the round's
largest result and still at risk.

## What is here

| file | what |
|---|---|
| `rows/C<H>.out` | `n value` lines, H = 1..18, n <= 40 — the cut-and-count row sums. H = 17 came from Motley rung 1 (`results/second-sources.md`), H = 18 from rung 2 (`results/second-sources.md`); H <= 16 are this run's |
| `confetti_h18_run.log` | rung 2's own log, 2026-08-14..19, five prime passes and the held-out check |
| `confetti_h18_console.log` | rung 2's fuller console transcript, banked 2026-08-19 |
| `residues/C18.p<prime>.out` | rung 2's five measured residue rows --- four are the CRT inputs, the fifth (2147483563) is the held-out one. Banked 2026-08-19 so `make gate-cutcount-assembly` can re-derive the 40/40 instead of quoting the runner |
| `confetti_check_p1.py` | the early single-prime check run against pass 1, kept as a record |
| `calib_run.log` | the run's own log, 2026-08-11 09:23–16:02 EDT, per-height self-checks and banked compare |
| `calib_run.attempt1.log` | superseded false start, 09:18, kept for the record |
| `cutcount_b1.cpp.59e90660` | the exact source that produced the rows |
| `rows41/C<H>.out` | the Nmax-41 ladder, H = 1..19, n <= 41 (`rows41/README.md`); banked 2026-08-21 |
| `residues41/C<H>.p<prime>.out` | the ladder's 171 measured residue rows, nine 16-bit primes per height; the largest prime of each nine is the held-out one (`scripts/motley_crt.py`'s rule). Banked 2026-09-05 so `make gate-cutcount-assembly` re-derives every height's held-out verdict |
| `rows41/run/` | the ladder's own `timings.txt` (wall and RSS per prime pass), `console.H*.log`, `census.H*.log`, `sizes.H*.N41.txt`; banked 2026-09-05 |

Copied by `scp` from `dalby:~/src/polyominoes/`, sha256 verified on both sides.

## The method, in one paragraph

With `A_n(q) = Sum_S q^{c(S)}` over n-cell subsets weighted by component count,
the king-connected count is `[q^1] A_n(q)`, computed by a frontier DP over
colour-coincidence partitions in `Z[q]/(q^2)`. Nothing in it decides
connectivity: clashes zero rather than join, there is no union-find verdict, no
stranded-component death and no completion predicate. Connectivity is read off
a coefficient at the end. That is why the rows matter — they are the only
recount of band cells by a rule outside the class round 3 was chartered to
escape. Independence analysis: `results/triangle-r3-adv-independence.md`.

## What the rows establish

`T(n,H) = C_H(n) - 2*C_{H-1}(n) + C_{H-2}(n)`. Recomputed from these files at
recovery time, independently of the run's own compare:

    T(40,15) = 6374412577120147022430261962743
    T(40,16) = 5908452097354911220916654388822

Both match `results/triangle.txt` to all 31 digits. Together the two cells are
**21.64% of a(40), recounted exactly by a second rule.** The run's own compare
line is `mode=assemble match=640 mismatch=0` over H = 1..16, n <= 40, with
`q0_zero=OK q1eval_binomial=OK` logged per height.

## Provenance caveat, stated plainly

The source sha256 is

    59e90660b42a0d94ceae5459287db35b4d93f87a5e62753ccd549235edaa8d3d

echoed in the log header, matching neither committed version on the parked
`second-source` branch: `7b13137` (`017e639d...`) or `48ac108` (`5ab04877...`,
which adds fail-closed exit codes after this run launched). The diff against
`7b13137` is 71 lines and is almost entirely the **removal** of that version's
`--modp` mode; the exact-payload DP itself is unchanged. Banking the file here
is what converts the rows' provenance from assertion into evidence.

Two consequences worth carrying into round 4:

1. The rows were produced by a binary whose gate battery predates the
   fail-closed exit codes. The per-height match/mismatch and self-check lines
   are in the log regardless, but a phase-2 rerun should use the committed
   fail-closed engine.
2. **A mod-p payload mode already exists in committed source** (`7b13137`,
   `run_height_modp`). The round-3 job request LG-JOB-1 was blocked on "a
   ~20-line residue-payload variant nobody has authored". That premise needs
   re-checking against `7b13137` before anyone writes one.
