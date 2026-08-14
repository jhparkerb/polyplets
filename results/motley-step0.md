# Motley step 0 — the provenance re-run, and what it now licenses

Run 2026-08-14 on dalby, `docs/motley-plan.md` §"Step 0". Runner
`scripts/dalby_motley_step0.sh`; rows and logs under `~/var/motley-step0`.

**GREEN.** All sixteen rows C_1..C_16 at Nmax = 40 reproduce the banked rows
**byte for byte**, and the assembled triangle matches the banked triangle
**640 of 640 cells, 0 mismatch**. The a(n) closure Motley already carried is
now citable: it rests on a committed, gated, clean-stamped binary rather than
on a dirty working copy that matched no committed revision.

## What was wrong before, and is now fixed

`results/cutcount_b1/PROVENANCE.md` recorded the caveat plainly: the banked
rows came from source sha256 `59e90660`, a dirty tree matching neither
committed version on `second-source`, with a gate battery predating the
fail-closed exit codes. The rows were evidence; their provenance was
assertion.

| | before | now |
|---|---|---|
| source | sha `59e90660`, uncommitted | `48ac108`, committed on `second-source` |
| obs stamp | `git=3b7359de-dirty` | `git=48ac1089`, no `-dirty` |
| gate | predates the fail-closed exit codes | `gate-cutcount-b1` GREEN on this build |
| binary | not retained | sha256 `e66f4466287d1417...` |

The clean stamp needed a fresh worktree (`~/src/pm-b1-step0`): the existing
`~/src/pm-b1` stamps `-dirty` off untracked results directories, and a dirty
stamp is exactly what this run exists to retire. Outputs live outside the
worktree so it stays clean.

## Cost, measured

Run as three concurrent streams rather than one core — each height is an
independent process, so this is scheduling, not a change of method.

| stream | heights | wall | peak RSS |
|---|---|---|---|
| A | 16 | 17,047 s (4.7 h) | 62.3 GB |
| B | 15 | 4,806 s (1.3 h) | 20.4 GB |
| C | 14..1 | ~2,400 s | 6.9 GB |

**4.7 h of wall against 6.7 core-hours serial**, 88 GB peak against dalby's
122 GB available. H = 16's wall came in 3.5% above the 2026-08-11 calibration
run (16,475 s) despite the co-residency, which is the first independent
confirmation that the ladder's per-height wall ratio is stable.

## The two checks, and why both are needed

1. **Rows against banked rows**, `cmp` per file: 16 of 16 byte-identical.
2. **Assembled T(n,H) against the banked triangle**: 640 of 640 cells.

The second is the one that catches a rule defect. Measured the same day
(`docs/motley-plan.md`, "What the in-engine self-checks do not check"): a
bottom-anchored stencil defect passes `q0_zero` and `q1eval_binomial` at every
height, because the q^0 check tests for a constant term and the A(1) check
evaluates at q = 1 where connectivity is never consulted. Neither self-check
is a connectivity check. Only comparison against independently computed values
catches the rule going wrong.

The first attempt at check 2 pointed `--assemble` at the C-row directory
instead of the banked triangle directory (`hN.out`, a different format). It
compared zero cells and **exited 3 with `FATAL no_banked_cells_compared`** —
the fail-open hole that `48ac108` was written to close, closing on its author.
The runner now carries both directories explicitly.

## What it licenses

- **a(n) rule-independent and citable for all n <= 31** (n = 2H - 1 at
  H = 16), by a rule that never decides connectivity — no union-find verdict,
  no stranded-component death, no completion predicate.
- The reference for every rung above: Half Measure and everything after must
  reproduce these rows byte for byte wherever both can run. Half Measure
  already does at H = 12, 13, 14, 15.
- C_15 and C_16 as the inputs to the H = 17 assembly,
  T(n,17) = C_17 - 2 C_16 + C_15 — which is why `scripts/dalby_motley_h17.sh`
  refuses to start without them.
