# The certification map after the anchor cut

2026-08-14. Supersedes the map in `results/onset-defect-depths234.md`
§"What this changes in the certification map". Mechanism and proof:
`results/depth-swap-anchors.md`, `docs/proofs/depth-swap-residual.md`.
Instrument: `experiments/depth_swap_anchors.py --rebuild`.

## The rule that changed

A level's constant `mu_k` was pinned from the staircase's **onset** instance,
whose cells sit in columns `k+1` and `k+2`. With the below-onset residual
identity proved, it can be pinned from the **depth-`j`** instance instead,
whose cells sit in columns `k+1-j` and `k+2-j`, for any `j` up to the deepest
closed defect `J`. Anchors move down, not up.

    old:  level k needs columns k+1, k+2          -> sweep H_max closes n <= 2 H_max - 1
    new:  level k needs columns k+1-j, k+2-j      -> sweep H_max closes n <= 2 H_max + J - 1
          (j = max(1, k+2-H_max) <= J)

With the shipped `D_1..D_3`, `J = 3`.

## Reach, measured rather than asserted

Each row of this table is a run: pin every level from cells at or below the
guard, rebuild every cell above it, compare against the banked triangle. The
guard is enforced in the accessor, so reading a cell above it aborts the run.

| guard `H_max` | levels pinned to | rows closable | rows reproduced | cells | mismatches |
|---|---|---|---|---|---|
| 14 | k = 15 | n <= 30 | 15..30 | 136 | **0** |
| 16 | k = 17 | n <= 34 | 17..34 | 171 | **0** |
| 17 | k = 18 | n <= 36 | 18..36 | 190 | **0** |
| 18 | k = 19 | n <= 38 | 19..38 | 210 | **0** |
| 19 | k = 20 | n <= 40 | 20..40 | 231 | **0** |

`n <= 2 H_max + J - 1` holds at every guard tested. In every run the levels
that overlap the onset-anchor route agree with it exactly.

## What each source now carries

| source | reach | rows closed end-to-end | was |
|---|---|---|---|
| strip engine (independent, `results/strip-engine.md`) | H <= 14 | n <= 30 | its own cells only |
| Motley, banked and gated (`results/motley-step0.md`) | H <= 16 | **n <= 34** | n <= 31 |
| Motley H = 17 (in flight) | H <= 17 | n <= 36 | n <= 33 |
| Confetti | H <= 18 | n <= 38 | n <= 35 |
| Ticker Tape | H <= 19 | **n <= 40** | n <= 37 |

The `H <= 16` row is not a projection: `--source motley` reads Motley's own
`C_1..C_16` rows, assembles `T(n,H) = C_H - 2 C_{H-1} + C_{H-2}` as its H = 17
script does, and reproduces rows 17..34 against the banked triangle, 171 cells,
0 mismatches.

## Raising J: each depth substitutes for one swept height

`n <= 2 H_max + J - 1` is symmetric in the two levers, so a deeper defect buys
exactly what an extra height buys. What each `J` would make unnecessary:

| J | H = 16 (banked) | H = 17 (Half Measure) | H = 18 (Confetti) | H = 19 (Ticker Tape) |
|---|---|---|---|---|
| 3 (shipped) | 34 | 36 | 38 | **40** |
| 4 (validated) | 35 | 37 | 39 | 41 |
| 5 | 36 | 38 | **40** | 42 |
| 7 | 38 | **40** | 42 | 44 |
| 9 | **40** | 42 | 44 | 46 |

**J = 4 is validated**, not projected: at guard 14 with `--jmax 4`, `mu_16` pins
at depth 4 and rows 15..31 reproduce, 153 cells, 0 mismatches.

The cost is the cluster families of excess `<= j-1`. Timed on the Python path
at K = 21: j = 1, 2, 3 take 0.1 s, 3.4 s, 131 s — about **35x per depth**, so
j = 4 is ~1.3 h and j = 6 is ~80 days there. The C++ builder
(`cpp/severance_w3_families.cpp`) is the real path: it takes `emax` as an
argument, `MAXN = 8` admits excess <= 6 (hence J <= 7), and
`experiments/severance_w3_depths.py` has no depth ceiling of its own
(`emax = j - 1` throughout). So **J = 5 is a table to build, not code to
write** — but J = 7 and J = 9 are out at this scaling, needing 35^2 and 35^4
more than J = 5.

The trade is not free in evidence terms. Dropping a swept rung moves weight off
an enumerating engine and onto the depth identity, which is the single-sourced
link. Deeper J makes the independent re-derivation more load-bearing, not less.

## What this removes

- **The H = 20 rung.** `docs/b1-closure-plan.md`'s ladder builds toward H = 20
  to close a(38) and a(39) and still leaves `T(40,21)`. Ticker Tape's H = 19,
  already in the Motley plan, now closes rows to 40 outright.
- **`T(40,21)`'s special status.** §7 of that plan calls it un-finessable
  because level 19's anchors are `T(39,20)` and `T(40,21)` themselves. That is
  a property of the onset instance, not of the cell: level 19 pins from
  columns 18 and 19 at depth 2.
- **The residual band.** All six of `T(38,20)`, `T(39,20)`, `T(40,20)`,
  `T(39,21)`, `T(40,21)`, `T(40,22)` rebuild from H <= 19 data.
- **Three terms of the current claim**, at zero compute: Motley's banked H <= 16
  run closes n <= 34, not n <= 31.

## What this does NOT remove

- **The dependence on the sweep.** Levels are still pinned from swept cells;
  the cells are lower, not absent. This is an anchor *cut*, not an ab-initio
  derivation — `results/severance-w1-anchor-cut.md` remains the only ab-initio
  route, and it still stops at k = 9.
- **`D_j`'s single sourcing.** Everything above rests on defects from one
  script, `experiments/severance_w3_depths.py`. jasonp's standing condition
  (2026-08-14): these cells count as shored up only once the depth-`j` identity
  is re-derived independently of it. Until then the map is a check on the
  incumbent, not a second source.
- **The incumbent's fingerprints on the non-Motley rows.** Every guard row of
  the reach table except `--source motley` reads the incumbent's own cells
  below the guard. Rule-independence at H = 17, 18, 19 arrives with Motley's
  rows, not with this identity.
- **`J = 3` is what is shipped.** `J = 4` (`D_4`, families of excess <= 3,
  built at K = 19 and needing K = 21) would give `n <= 2 H_max + 3`, hence
  n <= 41 at H_max = 19 — but that also needs the sweep run at `Nmax = 41`,
  which is not costed anywhere and is not claimed here.
