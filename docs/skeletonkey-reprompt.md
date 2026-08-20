# The post-`/clear` prompt for the "beat n=40" mission

Written 2026-08-20 on branch `skeletonkey`, mid-session, because that session
went depth-first when it should have gone breadth-first. This file is the
correction: it is what to paste after a `/clear`, plus the inventory that makes
breadth cheap.

## Why this file exists

The mission — ironclad a(40), or a wholly new way to count polyplets that
reaches well past n=40 — has an unusually complete kill inventory already in
the tree. A cold session that starts generating ideas will re-derive things
this project killed months ago, one at a time, and will feel productive doing
it. In one session I independently re-derived the Sykes-Essam matching-pair
duality (held, gated), Cut&Count (killed), rank-based/representative sets
(killed), the 45-degree sweep (falsified with a king-specific mechanism), and
cluster inversion (killed) — five ideas, each costing a read, each already
banked. The inventory is the expensive thing to reconstruct, not the ideas.

**So: read the inventory first, generate breadth second, go deep last.**

## The prompt

> Goal: ironclad confidence in a(40), and/or a genuinely new way to count king
> polyplets that reaches well past n=40. Working the T(n,H) triangle harder is
> explicitly NOT the kind of result wanted.
>
> Before generating any ideas, read the kill inventory in
> `docs/skeletonkey-reprompt.md` and the files it names. Then, breadth first:
> produce **at least 15 candidate directions** in one pass, one line each, and
> for every one state which inventory entry kills it or why it survives. Do not
> open a single file to investigate a candidate until the whole list exists.
> Score the survivors by payoff x plausibility, show me the table, and only
> then go deep on one.
>
> Machines: check ayr and dalby first. Experiments run on ayr unless it is
> busy; gympie is banned for project processes.

## The inventory — read these before generating

| file | what it closes |
|---|---|
| `results/coin-flip-characteristic-landscape.md` | **T3**: any commutative-ring-linear strip method has dimension >= min_p rank_{F_p}(M); p=2 is the only prime anywhere that drops it. Closes the whole weighted-automaton class for exact values. Read the "what this does not settle" section — it names the only two open doors. |
| `results/triangle-r3-l6-wildcard.md` | 35 candidate routes filtered to 1, with the F1-F4 kill columns. Cut&Count, rank-based, ZDD, #SAT, Potts integer-q, Tutte/reliability, FLM, CTM all die here. |
| `git show second-source:results/scaling-exploration-A.md` | A-S1: the Hankel-rank floor, and "crossover: never" — the rank-compressed engine loses on compute growth. |
| `results/exactchange-probes.md` | The char-2 rank collapse (A034299), the cell-level rank, and the measured char-2 sparsity. |
| `docs/lastditch-ideas.md` sec. 6-7 | Closed doors with counterexamples: dual-connectivity TM, evaluation/interpolation in the component variable, GPU, out-of-core. |
| `results/matching-pair-convention.md` | Polyominoes/polyplets as a percolation matching pair, with the convention pinned (perimeter is SAME-lattice). |
| `results/unexplored-avenues.md` | The avenues themselves, with their honest limits stated. |
| memory `algorithmic-levers-dead-connectivity-wall` | New sweep axis, FLM, MPS/boundary compression, holonomic accelerator — four levers, measured dead. |
| memory `column-tm-already-sqrt-lambda` | The column TM is already at lambda^(n/2); the 45-degree route is falsified for king because the corner move jumps two anti-diagonals. |

## The two cost laws, so nothing gets re-priced

Both are measured, both are in `results/lastditch-cost-ladders.md`.

- **Height**: 2.9x per height, and one height buys **two** units of n. So
  **1.70x per unit of n**.
- **Depth (bounded-excess families)**: 7-9x wall per unit of excess, and one
  unit of excess buys **one** unit of n. So **7-9x per unit of n**.

Depth is therefore the wrong lever by a factor of four to five in the exponent,
and the depth ladder dies at about n=42 no matter how it is engineered. Reach
obeys `n <= 2*H_max + J - 1`.

## What is genuinely open (as of this file's date)

- **Non-linear methods.** T3 bounds weighted automata. A method that is not a
  per-column linear map is outside the fence entirely.
- **A different functional.** T3 is about f = "exactly one king-connected
  component" on the strip automaton. Something that counts a different object
  and assembles a(n) from it is unbounded here. This is the widest door.
- The a-priori-basis construction question — but see
  `results/skeletonkey-cell-sparsity.md` before spending anything on it.

## What this session closed

`results/skeletonkey-cell-sparsity.md`. A-S1's "crossover: never" rested on
assuming the compressed transfer is dense, and named sparsity as its one
unprobed rescue; Exact Change had measured that sparsity in GF(2) only. The
char-0 measurement is now taken and the rescue fails.
