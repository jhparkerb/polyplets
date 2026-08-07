# Perimeter-defect diagonals — job brief

Written 2026-08-06 to survive a `/clear`. Hand this file to a fresh session and
it should be able to start without re-deriving anything.

## Why

Fixed polyominoes can be graded by **site-perimeter defect** as well as by
bounding-box height. Asinowski, Barequet, Magal & Zheng do the perimeter
grading for polyominoes (*Automatic generation of formulae for polyominoes with
a fixed perimeter defect*, Comput. Geom. 108 (2022) 101919 — **paywalled, we
hold only the talk slides**, `https://www.mat.univie.ac.at/~slc/wpapers/s79vortrag/asinowski.pdf`).
Their method and ours differ in a way that matters:

| | their grading | ours |
|---|---|---|
| defect | site perimeter, `k = 2n+2-p` | bounding-box height, `k = n-H` |
| method | classify into finitely many pattern classes, each a rational GF with **cyclotomic** denominators, then sum | transfer/cluster argument giving a proved degree bound + sharp onset, then interpolate |
| answer | **quasi-polynomial** — their k=3 carries a `(-1)^n` | **plain polynomial** |

The open question is whether that difference is intrinsic to the perimeter
grading or an artefact of the square lattice.

## What is already known (do not redo)

Commits `61f604a`, `b125950`, `ca3bbbd`, and `results/polyiamond-diagonal-law.md`.

- King animals: site perimeter obeys **p ≤ 4n + 4** (measured, n ≤ 13 — exactly
  double the polyomino 2n+2). Grading by `k = 4n+4-p`:
  - k=0: `2`, from n ≥ 2
  - k=1: `4n - 8`, from n ≥ 3
  - k=2: `6n² - 30n + 56`, from n ≥ 6 (5 holdouts)
  - k=3: **unresolved with n ≤ 13** — no cubic fits at any onset before the
    points run out. This is the whole question.
- `k=1` is `4(n-2)` under the perimeter grading on **both** square and king, and
  also under the height grading on square — but the king height grading is
  `25n - 45`. So the low-order coincidence is a square-lattice accident, not a
  structural identity (`experiments/perimeter_vs_height_defect.py`).
- Both gradings are marginals of A001168 / A006770 and sum to them; that is a
  consistency check, not a bijection.

## The questions, in priority order

1. **Does the king perimeter grading go quasi-polynomial at k=3, as the square
   one does?** If yes, quasi-polynomiality is intrinsic to the perimeter
   grading. If no, it is a square artefact and our height grading is not
   uniquely clean.
2. What are the king k=3, k=4 formulae, and what is the onset law? (Onsets so
   far: 2, 3, 6 for k = 0, 1, 2.)
3. Reproduce the published **square** k=3 quasi-polynomial from our own
   enumeration — an independent check on a paywalled result, and on our reading
   of the slides.

## Task B first: the perimeter-defect machine (local, cheap)

Near-maximal-perimeter animals are **sparse**, so a defect-budgeted DP should
reach far past any brute-force run, exactly as `experiments/diagonal_machine.py`
does for the height grading. Do this before committing to the big run — if it
works, the run becomes a cross-check rather than the source.

Model it on `experiments/diagonal_machine.py` and
`experiments/polyiamond_diagonal.py`. **Two traps, both of which have already
bitten:**

- **Budget by surplus over the per-step minimum, never by the current step's
  total allowance.** The allowance grows faster than the per-step cost, so the
  naive bound prunes states that later steps would pay back. Cost:
  376 → 262 at (n,H) = (8,3), silent, caught only by brute force
  (`results/polyiamond-diagonal-law.md` §Method).
- **Window/gap caps must be checked for stability**, not assumed. `defect_gas.py`
  records W=6 clipping a cluster weight to 4776 instead of 4778.

Validate against `build/g2 square8 N --siteperim` for every n it reaches before
believing anything.

## Task A in parallel: the enumeration run (dalby)

**Purpose.** Independent source for king k=3/k=4, and the only check on Task B.

**Command** (single shard):

    build/g2 square8 <N> --siteperim

**Measured cost, gympie, single core:** n=11 3.2 s, n=12 21.8 s, n=13 156 s.
Ratio **7.36 per n**. Extrapolated single-core: n=14 ≈ 19 min, n=15 ≈ 2.4 h,
n=16 ≈ 17.4 h, n=17 ≈ 5.3 days. **Peak RSS 1.7 MB at n=12** — RAM is a
non-issue, this is pure CPU.

**Sharding works:** `--split S K IDX` is accepted with `--siteperim` (verified).
Expect a straggler tail rather than linear speedup — see
`engine-utilization-and-scheduling`. Plan n=16 as the target and n=17 as a
stretch only if the dalby benchmark beats the gympie ratio substantially.

**SUPERSEDED 2026-08-07 — Task A was not run and should not be.** Task B
succeeded far past its brief: `build/perimeter_defect` reaches n=70 on king in 2017 s
on one core, against the n=16 this run was scoped for, and is cross-validated
against `build/g2 --siteperim` over g2's whole range. See
`results/perimeter-defect-diagonals.md`. The checklist below is kept as the
record of what a launch would have required; `scripts/dalby_siteperim.sh` was
planned here and never written.

**Checklist items that are NOT yet discharged** (`docs/job-checklist.md`):

1. Cost predicted above from measurement — but on **gympie**. Re-benchmark
   n=12 and n=13 on dalby before committing to n=16; do not assume the ratio.
2. Budget: RAM trivial, so the only constraint is cores. Check what else is
   running on dalby first.
3. Run from a named in-repo script, not a heredoc. The planned (never written,
   and now never needed) `scripts/dalby_siteperim.sh` was to follow
   `scripts/dalby_holes_perheight.sh`.
4. **The deployed local binary is stamped `fddbfae-dirty` and HEAD is now past
   that.** Rebuild and redeploy on dalby, then re-read the stamp, before any run
   whose output we keep. This is the A1 failure mode.
5. tmux window on dalby's existing session (never `new-session`), foreground
   with progress on screen, `tee` to a log; wait with `gtail --pid`.

## Task C: check the published square result (local, minutes)

`build/g2 square4 N --siteperim` works and is cheap. Grade by `k = 2n+2-p`,
confirm k=0,1,2 against the slides (`A(n,2n+2) = 1` up to symmetry — we get **2**
fixed, so mind the convention; `A(n,2n+1) = 4(n-2)`; k=2 quadratic), then fit
k=3 and confirm the `(-1)^n` term appears. If it does not, we have misread
either the slides or the convention, and that must be settled before any of this
is written up.

## Success criteria

- king k=3 settled as polynomial or quasi-polynomial, with holdouts, from two
  independent sources (Task A and Task B agreeing);
- square k=3 reproduced with its `(-1)^n`, or the discrepancy explained;
- a one-paragraph answer to question 1 written into
  `results/polyiamond-diagonal-law.md`'s neighbourhood — probably a new
  `results/perimeter-defect-diagonals.md` — stating plainly whether the
  height grading is cleaner than the perimeter grading, or merely luckier.

## What this is not

Not load-bearing for either paper. Nothing here changes a banked value. It is a
methodological question about two gradings, worth an evening because it bears on
what Paper 2 may claim about the diagonal law being "clean".
