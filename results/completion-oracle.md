# Completion-prune headroom: MEASURED against the true optimum (Shaving Lambda)

**2026-07-02.** `experiments/completion_oracle/oracle.cpp`. Follow-up to
[[completion-pruning-audit]] (results/completion-pruning-audit.md), which
flagged a Barequet-n_c-style tightening of `completionLowerBound` as
"unbounded-but-real" headroom (79% of surviving states multi-component). This
probe closes the question by measuring not a tighter *bound* but the **perfect
prune**: the true minimum completion cost of every signature, computed by value
iteration over the production kernel (`stepColumnSquare8`/`forEachViableMask`)
on the full signature universe per height, then re-running the sweep with
`ms + cells + trueDist(out) > maxn` as the prune.

The oracle prune is exact-safe by definition (drops a record only if its
smallest completable animal overshoots the budget), and both variants produced
byte-identical per-n counts (built-in gate).

## Result — the current bound is already near-optimal

n/H ≈ 1.8 throughout (the production top-height ratio; a29 sweeps H16 at
maxn=29 → 1.81):

| H | maxn | universe | gap=0 states | peak-states ratio | records ratio (perfect/current) |
|---|---|---|---|---|---|
| 8  | 15 | 826    | 87% | 1.000 | **1.007** |
| 10 | 18 | 5,568  | 74% | 1.003 | **1.020** |
| 12 | 22 | 39,507 | 60% | 1.003 | **1.037** |
| 14 | 26 | (not completed — probe closed at H=12; H=14 est. ~1.05-1.06) | | | |

- `completionLowerBound` is **admissible everywhere** (0 violations,
  exhaustively per H — the first exhaustive admissibility proof of the
  deployed bound, a nice byproduct).
- The gap distribution is thin: most states sit exactly at the bound; gaps of
  1-2 cells cover nearly all the rest (one outlier per H at gap = H, the
  never-touched-anything state).
- **Peak frontier is untouched (ratio ≤1.003).** The prune only bites in the
  tail columns where budget slack is small; the mid-sweep peak that sets RAM,
  spill, and most of the map wall has slack ≫ any bound's reach.

## Why the audit's headroom was a mirage

The 79% multi-component population is real, but the vertical-band term already
prices most of their merge cost, and horizontal merges are usually *free*: a
next-column cell that merges two vertically-adjacent components also serves the
mandatory rightward extension the components need anyway (a king cell merges
up to 3 old components at once — the same k-way-merge power that makes a naive
(c−1) bound inadmissible makes the true cost of merging *low*). The truth is
within 0-2 cells of our bound almost everywhere.

## Verdict

**CLOSED — no lever here.** The ceiling for ANY completion-prune improvement
(including a full Barequet n_c 2-D MST, lazy exact lookahead, or lookup
tables) is ~2-4% of emitted records at probe heights, extrapolating to ~6% at
H16, with **zero** effect on peak states. The audit's "weeks-of-care" gated
path would buy a few percent of map records and nothing on the RAM/spill peak.
Do not build it. (This also retires queue #4 for good.)
