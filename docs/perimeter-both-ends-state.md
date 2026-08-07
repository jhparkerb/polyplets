# Perimeter both-ends campaign — state, written to survive a `/clear`

2026-08-07. Hand this to a fresh session and it can pick up without re-deriving.
Findings live in `results/perimeter-both-ends.md`; this file is only the state.

## What this campaign is

`A(n,p)` has two boundary curves. `results/perimeter-defect-diagonals.md` graded
only from the maximum-perimeter end. This campaign grades from both, and the two
ends turn out to be different kinds of object: **triangular onset law at the max
end, linear at the min end**.

## Jobs in flight at the time of writing (all three boxes)

Wait on any of these with `tail --pid`, never a poll loop
([[no-busywait-completion-loops]]), and never in the foreground
([[long-jobs-tmux-not-nohup]] — over five minutes and it may be killed).

**dalby** (80 cores, 125 GB; repo at `4aa9017f`, binary stamped clean
`6473890c`). tmux session 0, window `pdk6big`:

    ./scripts/dalby_perimeter_defect_pool.sh square8 78 6 456 76 14   <- RUNNING
    ./scripts/dalby_perimeter_defect_pool.sh square4 78 6 456 76 14   <- QUEUED

440/456 king shards done; the last ~16 are the heavy tail. On completion the
driver merges to `results/perimdefect_square8_n78_k6.txt` -- a PLANNED output,
not yet written, since the run has not finished -- and **refuses to merge unless
all 456 shards reported `result=ok`**, so a partial run cannot be mistaken for a
complete one.

**gympie** (10 perf cores), tmux session 0:

- window `tri30`: `perimeter_min tri6 30 6 --threads 6` -> 1031/1142 hulls.
  Firms up tri6's `i>=1` stable values, which today rest on two or three points.
- window `freeprobe`: two `--only 15 15 {0,1}` square4 free-removal probes, at
  ~1h40m. **These are the decisive ones** — see the A120452 test below.

**ayr** (32 cores, 78 GB; repo at `e22761a`, stamped clean, tmux session 0
window `pmin48`): `perimeter_min square8 48 6 --threads 30`, 71/121 hulls.
Predicted ~109000 cpu-s from the measured 6.55x per +4 in `PMAX`. Takes the
king odd-p columns from 7-8 points to 10-11, enough to determine degree 5-6.
`gate-perimeter-min` also passes on ayr — gcc/Linux against gympie's
clang/macOS, so the tri6 hexagonal-hull generalisation is confirmed
cross-compiler.

## What k=6 buys, and how to read it when it lands

Four live predictions, all testable from `results/perimdefect_square8_n78_k6.txt`
(planned -- the run that writes it is still going):

1. `onset(6) = 24` — the triangular onset law `T_k + 3`.
2. the `Phi_2` leading diagonal's `15/4` (`5(k-2)!/2^(k-1)` at k=6).
3. the `Phi_3` exponent `k-4` — **today that slope rests on a single data point**
   at k=5, so k=6 is what makes it a law or kills it.
4. `Phi_4` absent until k=7 (the `Phi_d first appears at k = 2d-1` law).

Run, in order:

    python3 experiments/perimeter_defect_denominator.py results/perimdefect_square8_n78_k6.txt --k 6
    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n78_k6.txt --lattice square8 --kmax 6

The denominator script needs far fewer points than a fit and answers 3 and 4 on
its own; it scans the onset too, so it also answers 1 independently of any
interpolation. It was validated against the known k=4 and k=5 answers.

n=78 was chosen because a period-6 degree-6 fit with two holdouts per class needs
54 points above onset 24, i.e. n to 77.

## THE live test: does A120452 predict square4's j=6?

jasonp's OEIS lookups (2026-08-07) identified the per-tip series
`1, 1, 3, 5, 9, 14` as **A120452**, which continues `23, 34, 52, 75, ...`. If the
diamond's four tips really are independent, then `g^4` with `g = A120452` gives
square4's `j=6` free-removal term as

    1384

but the `W=13` run measured **1388**. And the convergence rule observed so far —
term `j` is correct once `W = 2j+1`, verified at `j=4 -> W=9` and `j=5 -> W=11` —
says `W=13` should ALREADY be converged at `j=6`. So exactly one of these is
wrong: A120452 diverges at its seventh term, the four tips stop being independent
at `j=6`, or the convergence rule fails. **The `W=15` probes in gympie's
`freeprobe` window settle it.** Read the `j=6` entry of

    grep '^# box' results/perimmin_free_15_15_0.txt

This is the same trap as the Ramanujan near-miss below, one level deeper, so do
not skip the check because A120452 "obviously" continues.

## Resolved since the first draft

- **The hexagon is `P(x)^6`, and it was not safe to assume.** `1, 6, 27, 98, 315`
  — my five converged terms — is also the opening of **A071734**, `p(5n+4)/5`,
  because `sum p(5n+4)x^n = 5*prod(1-x^{5n})^5/(1-x^n)^6` makes A071734 exactly
  `P(x)^6` corrected by `1 - 5x^5 + ...`. They part at `j=5`: 918 against 913.
  Measured **918** at BOTH `r=5` and `r=6`. `P(x)^6` stands.
- **OEIS status of all seven series** is now recorded in
  `results/perimeter-both-ends.md`: two hits (A120452, and A071734 refuted),
  five with no match — which is an answer to the terms I had, not a novelty
  proof, since S1/S2 carry six terms and S7 four or five.
- **king min `p<=44`** landed. The three fitted odd-p columns each gain a point
  and still hold. Higher `i` remains UNDERdetermined (7-8 points cannot fix a
  degree-6 polynomial with holdouts) — which is why `p=48` is running on ayr.

## Still open, NOT gated on dalby

- **square4 free-removals at `j=7`+**: needs `W=17`, 145 cells — **over the
  `kMaxCells = 128` u128 limit**, so it needs a wider connectivity mask first.
  Only worth doing if the `W=15` test above leaves the picture unsettled.
- **A full `make gates`** has not been run since the tri6 generalisation of
  `cpp/perimeter_min.cpp`. `gate-perimeter-min` (on gympie AND ayr) and
  `gate-perimeter-defect` pass; the rest is unverified against these changes.
  Low value for discovery, but it is owed. Wants a box idle.
- **What counts the square4 tip shapes structurally.** A120452 names the
  sequence; it does not explain why a diamond tip's removable shapes are the
  partitions of `2n` with exactly two odd parts, one of which is the greatest.
  `experiments/perimeter_min_tip_shapes.py` prints the shapes directly (with
  king's corner as the control that must return plain partitions) but is too
  slow as written — it recomputes the whole perimeter per subset instead of a
  local delta.

## Gated on dalby

- `k=7`, the direct `Phi_4` test. ~12x k=6 per the measured ratio, so plan it
  only after k=6 lands and the pool driver's tail is understood.
- The bivariate `F(x,y) = sum_k G_k(x) y^k` rationality question, which needs
  `Ntilde_6` before six terms across two denominator regimes become seven.

## Tooling added this campaign (all gated)

| what | where |
|---|---|
| min-end enumerator, 3 lattices, hull = ranges on linear functionals | `cpp/perimeter_min.cpp` |
| its gate (RMAX unbounded vs g2 `--siteperim`, + RED control) | `scripts/perimeter_min_gate.sh`, `make gate-perimeter-min` |
| `--split S K IDX` for the max-end enumerator | `cpp/perimeter_defect.cpp` |
| its gate, check D = shards sum to the unsplit run | `scripts/perimeter_defect_gate.sh`, `make gate-perimeter-defect` |
| sharded production driver with a worker pool | `scripts/dalby_perimeter_defect_pool.sh` |
| onset law / recentred basis / numerator probes | `experiments/perimeter_max_structure.py` |
| denominator finder (few points, scans onset, tests minimality) | `experiments/perimeter_defect_denominator.py` |
| min ladder, both indexings | `experiments/perimeter_min_ladder.py` |
| min-end model vs the partition function | `experiments/perimeter_min_model.py` |
| attainability law + odd-p fits | `experiments/perimeter_min_attainability.py` |

## Two traps already paid for

- **The max-end numerator test is meaningless on the full `G_k`**, which carries
  a polynomial part holding the pre-onset holdouts. It must be run on the tail
  series from the onset. The first answer was noise.
- **(H1)** — every animal's perimeter is at least its own filled hull's — is what
  makes the min-end enumeration complete, and it is a hypothesis. It is checked
  at runtime and, more usefully, from outside by the gate. Do not weaken the
  gate; a violation surfaces only as a *missing* animal.
