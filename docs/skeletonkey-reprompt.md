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
  `results/skeletonkey-cell-sparsity.md` (planned) before spending anything
  on it.

## The breadth pass, and what it closed — 2026-08-20

Twenty candidates generated in one pass against the inventory above. The kills
are the point of this section: they are what a cold session would otherwise
re-derive. Full status:

| # | candidate | status |
|---|---|---|
| 1 | N-family / reach merge on the strip frontier | **ESTABLISHED, PARKED** — `results/skeletonkey-nfamily-merge.md` |
| 2 | dense compressed transfer | killed, A-S1 "crossover: never" |
| 3 | sparse compressed transfer in char 0 | see below |
| 4 | another prime / extension field / grading / auxiliary group | killed, T1–T4 |
| 5 | non-commutative realization | killed, T5 |
| 6 | Cut&Count, rank-based, ZDD, #SAT, Potts, Tutte, FLM, CTM | killed, F1–F4 |
| 7 | dual-connectivity TM | killed with counterexample |
| 8 | interpolation in the component variable | killed |
| 9 | 45°/anti-diagonal sweep | killed, king corner move |
| 10 | MPS / spatial cut | killed, measured worse |
| 11 | holonomic accelerator | killed, non-D-finite |
| 12 | GPU, out-of-core | killed on arithmetic |
| 13 | cluster/gas inversion | killed, F2 |
| 14 | published king series | killed, stops at s = 22 permanently |
| 15 | Sykes–Essam matching pair | alive, needs perimeter-graded enumeration; no sentence gets shorter |
| 16 | B1 residue/CRT ladder | **RUNNING** on dalby; protocol in `docs/resume-here.md` |
| 17 | column-numerator 22-equation audit | **KILLED 2026-08-20** — `lastditch-ideas.md` §1a correction |
| 18 | square-lattice external validation | blocker removed, headline repriced — `results/skeletonkey-parametric-master.md` |
| 19 | D2ax per-cell mod 2 | **DEAD — already shipped** on all 820 cells, `results/subgroup-mod4.md` |
| 20 | holographic / matchgates | killed, INV-5 desk survey (`triangle-r3-involution.md`) |

Three of these were closed this day and are worth naming, because each was
closed by counting rather than by computing:

- **#17 and `lastditch-ideas.md` §5.** Each below-onset cell brings one
  equation *and* one unknown `D_j(k)`, so surplus is
  `(cells at known depths) − 2` and the extra cells cancel. The P-finite
  escape needs ~180 values of `k` where ~15 exist.
- **#19.** Already shipped, on every cell of the triangle.
- **#18.** The "king-only ledger" is one substitution: `b = |D|` for the 3 in
  the renewal chain, `Ŵ_c = W_c·b^{2k−l−1}`. But the published-n=56 headline
  still needs square cells below onset at `H ≤ 28`.

### Still to re-open

`results/r4/r4-floors.md` has a section "Routes the floors do not close that
have been treated as closed" naming **L3-3** (fattening bijection to decorated
polyominoes) and **L3-4** (dual/moat encoding) — both killed in the queue by a
rank floor that sits ~1.5e4 at H = 21, which is not a cost objection to
anything. That file calls the kills "merely asserted". The queue rows live on
the unmerged `triangle-structure` branch
(`git show triangle-structure:results/triangle-r3-queue.md`).

**Of those two, only L3-3 is actually open.** L3-4 is "sweep the 4-connected
complement components (moats) instead of the foreground", which is the
dual-connectivity TM that `lastditch-ideas.md` §6 closes with a counterexample
and a measured state comparison — `b·Cat(b)` against `Bell(b)`, 11,440 vs
4,140 at `b = 8`, so the dual is *worse*. That kill is sound and independent of
any floor; r4-floors' objection lands only on the reason the queue gave, not on
the conclusion. L3-3 has no such second kill, and its own queue row prices it
"level-1 value only" — i.e. a candidate second source, not a reach lever, which
is the lane the B1 ladder already occupies more cheaply.

**L3-3 CLOSED 2026-08-20** — `results/skeletonkey-l3-3-fattening.md`. The
construction is *sound*, which is the new fact: under a lex filling convention
the image is pinch-free and the map is injective over all 176,138 king animals
to n = 8, with a proof (a block is the lex-larger candidate at its own
bottom-left corner, so it never wins that mark and is never completed by marks
— full blocks are exactly the animal). It dies on what the working construction
costs. A bijection restates a counting problem rather than reducing one, so the
image class carries exactly the king information; and the verbatim machinery the
row wants to borrow is class-agnostic, so it pays for a column of height 2H —
the incumbent's banked law `Motzkin(H+1) − 1` read at h = 42 is 1.6 × 10¹⁸
against 4.0 × 10⁸ at H = 21. The level-1 reading dies on size alone: 4n cells
per image puts a(40) at ≥ 160-cell polyominoes against a literature record of
n = 56. Note that r4-floors was *right* that the rank floor was not the
objection — the objection is that the information is identical, not that the
floor is paid.

Same file's **INV-4** asks whether B1's coincidence-partition state compresses.
That question is now known to be answerable, and to have answered "no, the
states are not minimal" once — see #1. Flagged, not pursued, because #1 is
parked.

## What this session measured

`results/skeletonkey-cell-sparsity.md` (planned). A-S1's "crossover: never"
rested on assuming the compressed transfer is dense, and named sparsity as its
one unprobed rescue; Exact Change had measured that sparsity in GF(2) only.
