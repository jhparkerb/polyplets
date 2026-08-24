# The depth-5 gate is green — review row B13 closes

**2026-08-24.** `experiments/severance_w3_depth5_gate.py` passes in production.
`D_5` computed ab initio from the `emax = 4` family table reproduces all 15
banked cells `T(2k-4, k-4)`, `k = 5..19`, exactly. Review row B13 closes.

## What ran

The table is `results/severance_w3_families_K21_e4.txt` — `families 21 4` at 8
threads on dalby, 2026-08-23 09:27:27 to 14:21:47, 105 cells, produced by
`scripts/severance_e4_k21.sh` at rev `95fbb6ceb`. Pulled into the tree
2026-08-24; sha256 `4080e52d…4d3e68` verified identical to dalby's copy.

**Cost, measured against the prediction.** wall 17,660.4 s = **4 h 54 m**,
cpu 39,075.8 s, peak RSS **18,743 MB**, at the same 8 threads as the ladder
that priced it (`results/depth5-cost-settled.md`), so the thread-count RSS
confound does not apply.

| axis | predicted, decelerating | predicted, deceleration stops | measured |
|---|---|---|---|
| wall | ~3.1 h | ~6.7 h | **4.91 h** — inside the bracket |
| peak RSS | ~8.5 GB | ~16.1 GB | **18.3 GB** — *above both* |

The wall bracket held. **The RAM bracket did not contain the answer** — the
measured peak is 14% above even the pessimistic end, the one that assumed the
deceleration stopped dead. That matters beyond this run: the same
extrapolation method is what prices `families 21 5` at ~74–85 GB in
`docs/state-2026-08-23.md` §5, and that figure is the one the five-terms
decision leans on. It should be read as a floor, not a bracket.

The gate itself is cheap once the table exists: 0.20 s wall, 13.7 MB peak on
dalby, 0.11 s on gympie. Both runs print the same two lines.

```
  depth 1: 19 banked cells match exactly (k = 1..19)
  depth 5: 15 banked cells match exactly (k = 5..19)
GATE GREEN
```

`--selftest` is also green: the perturbed depth-5 series (`+3^-17` at k=12) is
still caught, so the comparator that was proved red-first in August still
fires.

## What the green covers, measured

A gate that passes is worth what its red control is worth, so the table was
mutation-tested: perturb the last digit of one entry in a shadow tree, re-run,
and see whether the gate notices. Sample was every cell with `e <= 2` and
`k <= 8`.

| column | meaning | mutants killed |
|---|---|---|
| `sig` | interior weights | 21/21 |
| `bb` | bottom-edge weights | 21/21 |
| `pp` | pure weights | **0/21** |

The `pp` result is not a hole in the gate. `pp` is structurally inert in the
depth-5 assembly: injecting a perturbed `pp` directly into `severance_w3_depths
._FAM`, table-independently, moves `D_series(j, ·)` **only at `j = 1`** —
`j = 2, 3, 4, 5` are all bit-identical. It enters `r_coeff` at line 429 and
cancels in the sum over `t`. A gate cannot catch a change that does not reach
the answer.

So B13's green is a statement about `sig` and `bb`. The e4 table's `pp` column
is not exercised by it.

## The pp column has independent coverage anyway, for e <= 3

The new table agrees cell-for-cell, all three columns, with every banked table
it overlaps — including two produced weeks earlier by other runs:

| against | shared cells | mismatches |
|---|---|---|
| `K19_e3` (2026-08-09) | 76 | 0 |
| `K22_e0` | 21 | 0 |
| `K22_e1` | 42 | 0 |
| `K22_e2` | 63 | 0 |
| `K22_e3` | 84 | 0 |
| `K60_e1` (2026-08-14) | 42 | 0 |

That leaves only the 21 `e = 4` rows new, and only their `pp` entries
unchecked by anything — a column that feeds no depth above 1.

## What this does and does not license

It closes B13, which `docs/state-2026-08-23.md` §5 names as the blocker on the
five-terms decision. The five-terms sweep remains unlaunched and unauthorised;
this removes a gate, not a decision.

It does not wire the gate into `make gates`. Successor row S-A5 asks that the
standalone experiment gates (`severance_w3_gate.py`,
`undertow_congruence_gate.py`, `severance_w3_depth5_gate.py`) be decided as a
family rather than per-file. B13 was red-by-design and therefore unwireable;
it is now green and wireable, which makes S-A5 actionable — still a decision,
still open.
