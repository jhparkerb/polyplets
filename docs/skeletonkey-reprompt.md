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

## The prompt, v2 — 2026-08-20, after the breadth pass

**Use this one.** v1 below is kept because its rationale is why the inventory
exists, but its instruction — go breadth-first — has been carried out. Twenty
candidates were generated in one pass and the yield was kills, not leads. A
session that runs breadth again will produce the same twenty.

The failure mode has moved. It is no longer "re-derives a killed idea". It is
"generates a twenty-first candidate that is the incumbent in new clothes, and
does not notice". L3-3 is the worked example: a construction that is genuinely
correct, genuinely pretty, survived two rounds of triage, and buys nothing.

> Goal: ironclad confidence in a(40), and/or a genuinely new way to count king
> polyplets that reaches well past n = 40. Working the T(n,H) triangle harder is
> explicitly NOT the kind of result wanted.
>
> **Do not run another breadth pass.** The twenty-row table in
> `docs/skeletonkey-reprompt.md` is the breadth pass; read it and the three
> triage tests below before anything else.
>
> Every counting method for this problem lands in one of three boxes. Place
> your candidate in one, out loud, before opening a file:
>
> 1. **Cut methods** — anything whose sweep crosses a straight cut. Floor:
>    `M(H/2+1)` independent quantities (L3-1), which is 15,511 at H = 21. The
>    incumbent realises `Motzkin(H+1) − 1 = 400,763,222` column states there.
>    The whole prize in this box is the gap between those two numbers, no
>    construction for it is known, and A-S1 already called that headroom
>    non-constructive (`docs/coin-lift-plan.md` §4).
> 2. **No-cut methods** — Redelmeier/quotient DFS, involutions, Pfaffian-style.
>    All λ^n. Involutions closed by INV-1, Pfaffian/matchgate by INV-5.
> 3. **Cancellation** — count something whose exact value is *not* the animal
>    count (mod 2^m, signed, graded), so that less information crosses the cut
>    than an exact count requires. The only box with a measured escape: the
>    char-2 rank collapse is real, ~1e6 at H = 21 against 9.4e8 (INV-6). Its
>    blocker is constructive — no explicit basis — and that is the single
>    largest open technical question in the mission.
>
> Then apply all three tests, and state the answers:
>
> - **The bijection test.** If your candidate maps king animals one-to-one onto
>   some other class, it is dead, and no property of the target class rescues
>   it. A bijection restates a counting problem; it does not reduce one. The
>   image carries exactly the same information and pays exactly the same floor,
>   however much published technology exists for the target. This is what
>   killed L3-3 — see `results/skeletonkey-l3-3-fattening.md`, and note that
>   L3-3 survived earlier triage only because its kill had been *misstated* as
>   "pays L3-1's rank floor", which `results/r4/r4-floors.md` correctly
>   rejected as a non-objection. Paying a floor is not the objection. Carrying
>   identical information is.
> - **The cancellation test** (L6-8, already in the queue). "Where is your
>   cancellation identity?" A box-3 candidate without one is a box-1 candidate
>   in a costume.
> - **The accounting test.** Every kill made on 2026-08-20 came from counting
>   rather than computing: equations against unknowns (#17), ansatz
>   coefficients against available data (§5), image size against a literature
>   record (L3-3). If a candidate's payoff can be priced in a paragraph of
>   arithmetic, price it there before reading anything.
>
> A result that clears all three is worth going deep on. Show me the placement
> and the three answers before you do.
>
> Machines: ayr and dalby; gympie is banned for project processes. Check what
> is already running first (`docs/resume-here.md`). Nothing over an hour gets
> launched without asking.

### What "even harder" is actually being spent against

Stated plainly so the next session does not mis-allocate. The mission has two
halves and they are not equally likely.

- **Ironclad a(40)** is in reach and mostly in flight — the Motley ladder
  gives a(40) a second program in all forty cells and a(41) its first, and
  Undertow pins the tower from below-onset cells. This half is engineering and
  patience, not invention.
- **Past n = 40 by a new method** is where the three boxes above say the
  honest odds are poor. Box 1 is fenced by an information floor with no known
  construction, box 2 is λ^n, and box 3 needs an explicit char-2 basis that
  nobody in the literature has for this functional. That is not a reason to
  stop; it is a reason to spend the effort on box 3's basis question rather
  than on a twenty-first re-encoding.

If a session has one expensive idea in it, the char-2 basis (INV-6, and
`exactchange-basis-hunt` in MEMORY.md) is where it should go.

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
  `results/skeletonkey-cell-sparsity.md` before spending anything on it --
  and note what it says: a sparse basis demonstrably EXISTS in char 0 (2.15
  nonzeros/row against a dense 913 at H=8) and buys nothing there, because
  dimension not density is what beats the char-0 engine. The basis hunt is
  motivated by the char-2 COLLAPSE and never by char-0 sparsity.

## The breadth pass, and what it closed — 2026-08-20

Twenty candidates generated in one pass against the inventory above. The kills
are the point of this section: they are what a cold session would otherwise
re-derive. Full status:

| # | candidate | status |
|---|---|---|
| 1 | N-family / reach merge on the strip frontier | **ESTABLISHED, PARKED** — `results/skeletonkey-nfamily-merge.md` |
| 2 | dense compressed transfer | killed, A-S1 "crossover: never" |
| 3 | sparse compressed transfer in char 0 | floor base measured **2.43, not 3** at H=11 — the room is real but still non-constructive; `results/skeletonkey-hankel-closure.md` |
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
  the renewal chain, `Ŵ_c = W_c·b^{2k−l−1}`. But the published-n headline
  still needs square cells below onset at `H ≤ 28`. (The published reach is
  n = 70, not the 56 this file said — `results/literature-record-56-corrected.md`
  — and it is totals only, so the blocker is unchanged.)

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

**This section is now empty.** Both rows it named are closed, L3-4 on the dual
state comparison and L3-3 on the bijection test. Nothing in `r4-floors.md`'s
"treated as closed" list is still open except the two rows it raises that are
not counting routes at all (R4-G18's premise, and the char-2 cut
representation, which is INV-6's basis question wearing a different name).

Same file's **INV-4** asks whether B1's coincidence-partition state compresses.
That question is now known to be answerable, and to have answered "no, the
states are not minimal" once — see #1. Flagged, not pursued, because #1 is
parked.

## What this session measured

`results/skeletonkey-cell-sparsity.md` — BANKED 2026-08-22. A-S1's "crossover:
never" rested on assuming the compressed transfer is dense, and named sparsity
as its one unprobed rescue; Exact Change had measured that sparsity in GF(2)
only. The char-0 answer: sparsity is real and 425x at H=8, and the engine loses
anyway on dimension (2.748x/height against the column frontier's 2.541x, and
already 1.6x behind at H=4). H=8 did not break the trend.


---

## The prompt, v1 — superseded, kept for its rationale

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
