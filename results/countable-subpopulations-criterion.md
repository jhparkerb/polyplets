# When is a polyplet sub-population countable (not just enumerable)?

Date: 2026-07-10. **Criterion corrected 2026-08-05** — the original version
(convexity ⇒ 1D profile evolution ⇒ algebraic/rational GF) is false as stated,
and the repo now contains its counterexamples. Companion to
[[algorithmic-levers-dead-connectivity-wall]] and
`results/directed-king-animals.md`. The question: given an attribute
(invariant) of polyplets, does conditioning on it give a sub-population we can
*count* (closed form / rational-or-algebraic GF / polynomial cost) rather than
*enumerate* fully?

## The criterion, in two conditions

**1. Conditioning must make the connectivity constraint one-dimensional.**
Connectivity is the wall (the same wall as the finite-lattice / MPS /
holonomic negatives); an attribute buys a counting shortcut only if it
collapses that 2D constraint to a 1D layer/heap recursion. This is a severe
filter, and it is the part of the original criterion that survives.

**2. The transfer kernel must have finite rank in the unbounded state
variable.** This is the part that was missing, and it is what actually decides
the GF class. A 1D profile evolution still carries an unbounded integer in its
state — the height of the last column, the width of the last row. Write
`K(h, h')` for the number of ways a column of height `h'` may follow one of
height `h` under the predicate. If `K` is a finite sum `Σ_i f_i(h) g_i(h')`,
i.e. finite rank as an infinite matrix, Temperley's method closes to a finite
linear system and the GF is **rational**. If the predicate instead forces a
comparison between the two — an order relation, a `min`, a `max`, a running
extremum — `K` has infinite rank and nothing closes.

The plan's formulation of the same thing
(`docs/middle-kingdom-followups-plan.md` Phase 3):

> **Does the predicate need a running extremum — an unbounded integer that is
> not the area — in the transfer state?** No ⇒ rank-1 operator, rational GF.
> Yes ⇒ O(n²) states and no closed form.

That is the symptom, and it is the right thing to look for first, but it is
not the test, for two reasons this file has to be honest about:

- **The unbounded integer alone disqualifies nothing.** Every column-convex
  cell of the Middle Kingdom grid carries an unbounded column height in its
  transfer state and counts by area, and four of the five are rational
  (A187077 for both the unfiltered and the multi-directed row, A018902 for the
  4-cone row, and the novel 5-cone cell). What disqualifies is the
  *coupling*, not the integer: `K = h + h' + 1` (unfiltered column-convex) has
  rank **2** — its rows span `{1, h'}`, which is why
  `results/convex-polyplets.md`'s K2 derivation closes on a **2×2** system —
  `K = h + 2` (4-cone) has rank 1, and `min`/`max` coupling has neither.
  Rank 1 is the sharpest case, not the boundary. Every rank quoted in this
  file is measured, together with the area sequence its kernel generates, by
  `experiments/kernel_rank_probe.py`.
- **The "yes" side is not one verdict.** What is banked ranges from "not
  C-finite, at best algebraic" (the defect gas) through "not D-finite and not
  algebraic in the boxes tested" (HV-convex by area, ctrlB). No family here
  has a *proof* of no closed form; every negative is an exclusion box.

## What falsified the original version

The original text read: convexity ⇒ every row and column a contiguous run ⇒
the shape is a 1D profile evolution ⇒ algebraic/rational GFs. Two
counterexamples, both inside the repo:

- **(ctrlB, column-convex)** (`results/middle-kingdom-phase3.md`) is
  column-convex, is a 1D profile evolution, and has rational *rigorously
  excluded* at order ≤ 12 (rank 13 of 13), D-finite excluded at order ≤ 12 /
  degree ≤ 12 and order ≤ 14 / degree ≤ 8, algebraic excluded at degree ≤ 8 /
  t-degree ≤ 14 and degree ≤ 6 / t-degree ≤ 20.
- **The grounded row** of `results/king-subfamilies.md`: Ferrers polyplets are
  the partition numbers A000041, whose GF is a classical q-series — neither
  rational nor D-finite — and stacks (A001523, unimodal compositions) sit
  beside them. Both were listed under "convexity family" as passing.

Add the Convex Mirage (HV-convex by area, non-D-finite) and the original
bullet was wrong in three independent places.

## The mechanism, in the three places it is now visible

Each of these was re-read before being cited, and each is an instance of
condition 2. Only the third is a running extremum in the literal sense.

1. **The defect gas — an unbounded gap** (`results/defect-gas.md`,
   2026-07-13). The all-pairs cluster weight family is **not C-finite**: an
   order-7 recurrence fitted on ℓ ≤ 14 is refuted at ℓ = 16. The stated
   structural reason is that the gap between pending blocks is an unbounded ±2
   walk, so the state space is infinite. Note the strength of the verdict: not
   rational, "at best algebraic", with the kernel method named as the open
   route to an exact constant. This instance supports the no-rational half of
   the rule and nothing beyond it.
2. **The convex-area mirage** (`docs/proofs/convex-mirage.md`, strengthened in
   `results/convex-polyplets.md`). The HV-convex row transfer matrix has state
   `(left-phase, right-phase, width)`; the phases record which side of the
   boundary's extremum the row is on, and the transitions clip by `min`/`max`
   onto those phase targets. The width is an unbounded integer that is not the
   area, and the clipping is exactly the infinite-rank coupling. **Caveat:**
   the width is not itself a running extremum, so this is an instance of
   condition 2 rather than of the plan's wording taken literally.
3. **ctrlB's running minimum** (`results/middle-kingdom-phase3.md`,
   Proposition 3). "Every local minimum of `b` is at the global minimum" is not
   a local rule on the profile steps, so the transfer matrix carries the height
   above the running minimum and the state count is O(n²) rather than O(n).
   This is the literal case: the extremum is in the state, and it is the only
   column-convex cell with no closed form.

## What passes (rational or algebraic, with the reason)

- **Directedness** — forward cone ⇒ heaps of pieces ⇒ algebraic GF (Bacher;
  `results/directed-king-animals.md`). Multi-directed is exactly solved via
  connected heaps (Bacher Theorem 8) and yet **non-D-finite** (Theorem 10;
  `results/multi-directed.md`) — the earliest sign in this file that "exactly
  solved" and "closed form" are different questions.
- **Column-convex and row-convex by area** — `K = h + h' + 1`, rank 2,
  rational: A187077, GF `x(1−x)³/(1−7x+13x²−10x³+2x⁴)`
  (`results/convex-polyplets.md`, K2). The same kernel with `h + h' − 1`
  (edge adjacency instead of king) is the classical column-convex *polyomino*
  count A001169, also rank 2 and also rational
  (`a(n) = 5a(n−1) − 7a(n−2) + 4a(n−3)`, ten terms reproduced) — the rule's one
  check outside this repo, and it passes.
- **Directedness on top of column-convexity** — each cone predicate reduces to
  a condition on the bottom profile alone (`results/middle-kingdom-phase3.md`,
  Propositions 1–5) and each surviving kernel is rank 1: 4-cone gives
  `K = h + 2` (A018902), 5-cone splits into two rank-1 runs (novel, double
  pole), bottoms-nondecreasing gives `K = h + 1` (A007052). All rational.
- **Bargraphs** — grounded columns, unconstrained kernel, `2^(n−1)`.
- **Bounded height/width** — fixed `H` ⇒ finite state ⇒ trivially finite rank
  ⇒ rational GF in `n` (our `T(n,H)` atoms, `results/fixed_height_gfs.txt`).
  Closed form, but cost exponential in `H`.
- **Convex families counted by perimeter** — classical convex polyominoes are
  algebraic by perimeter (A005436, Delest–Viennot), and HV-convex king animals
  are **algebraic** by semiperimeter too: a quadratic, minimal box `(2, 9)`,
  recovered exactly over Z and holding on 166 unseen rows
  (`results/convex-polyplets.md`). See the split below.

## What does NOT pass

- **1D but infinite-rank**: HV-convex by area (the Mirage), (ctrlB,
  column-convex), Ferrers (A000041), stacks (A001523). Staircase (A225114) has
  both boundaries constrained against the previous column, which produces the
  same `min`/`max` coupling, so the rule **predicts** no rational GF for it;
  the coupling is exactly `K = min(h, h') + 1`, and it generates A225114 from
  n = 1 (`experiments/kernel_rank_probe.py`). Predicted against the 14 banked
  terms, then **tested the same day and confirmed**
  (`results/hv-growth-sandwich.md`, followups Phase 1): on a 700-term series
  A225114 is EXCLUDED at order ≤ 24 / degree ≤ 24 (rank 625 of 625) and
  non-algebraic at degree ≤ 20 / t-degree ≤ 20 — the boxes and the tool that
  cleared the unrestricted HV-convex series. An exclusion box, like every other
  negative here, not a proof.
- **Not even 1D**: holes, edge-connected-component count, perimeter, symmetry
  class, coloring/parity, edge/corner-contact counts. None change the
  dimensionality of connectivity; conditioning on them leaves the full 2D-hard
  problem restricted to a subset. (We still *stratify* by these via
  enumeration — `T(n,H)`, A0/A1 holes, companions — but that is enumeration,
  not a counting shortcut.)

## The area/perimeter split: what the rule does and does not explain

`results/convex-polyplets.md` banks HV-convex king animals as **algebraic by
semiperimeter** (a quadratic in the minimal box `(2, 9)`, nullity 1, fitted on
34 rows and holding on all 166 later ones; the order-5 degree-2 P-recurrence,
fitted on ~22 rows and predicting all 172 remaining out to s = 200, is its
D-finite shadow) and **not D-finite by area** (order ≤ 24 / degree ≤ 24,
700 terms).

**Explained.** By semiperimeter the counting variable is the bounding box
`W + H`, so the unbounded state parameter *is* bounded by the counting
variable: at each `s` the state space is finite and the infinite-rank coupling
the rule names cannot arise. By area it can, because the width is free of the
area. This is the content of the plan's "an unbounded integer that is **not**
the area" — the obstruction is a property of the pair (predicate, statistic),
not of the predicate alone.

**Not explained.** The rule sorts rational from not-rational. It does not say
where a family that fails it lands, and by semiperimeter every family here
lands algebraic without the rule predicting it: A005436 for polyominoes
(Delest–Viennot), degree 2 for HV-convex king animals, degree 4 for
(dir4, HV-convex) — one step apart in the same hierarchy, and the rule sees
none of that structure. Nor does it explain why the area side of the polyomino
control (A067675) fails in the same boxes as the king series. A finite state
space per `s` is consistent with the measured algebraicity; it is not a
derivation of it.

## Why none of them help count a(n)

Even the solvable subclasses are strict subsets that do **not** compose back to
the total: directed ↛ undirected, convex ↛ all. Same non-reduction as the
directed/undirected inequality. So every countable sub-population is a
side-quest — a standalone result, a rigorous bound, or a validation anchor —
never a lever on `a(n)`.

## Parked lead (2026-07-10) — separating invariants

Distinct from *covering* (partitioning) attributes: is there a small set of
attributes whose joint value **pins a polyplet uniquely** (no two distinct shapes
collide)? A "separating"/complete-invariant set, not just a partition. None of the
standard attributes come close alone. Flagged interesting by jasonp, deferred.

## The open nugget, CLOSED 2026-08-05

The nugget guessed that HV-convex polyplets, being the king version of a
classically algebraic family, were "plausibly still algebraic". The guess was
wrong, and the family is not algebraic and not D-finite:

- **Not D-finite** at order ≤ 24 / degree ≤ 24 and **not algebraic** at
  degree ≤ 24 / t-degree ≤ 24 in `F`, on 700 terms
  (`results/convex-polyplets.md`). Both verdicts also hold at (20,20), at
  (20,20) with the first 50 rows dropped, and at (20,20) under a second prime.
  The test is a full-column-rank check mod `p = 2^61−1`, which is a rigorous
  exclusion over Q rather than a numerical one, and the boxes nest, so the
  maximal box settles every box inside it. (25,25) is the first box 700 terms
  cannot decide. The guesser is kept powered by the four arms of
  `make gate-convex-dfinite`, and the HV-convex **polyomino** control
  (A067675) is excluded in exactly the same boxes.
- The two other clauses of the nugget stand. The family really is new — no
  OEIS match on nine terms or on the six-term prefix, re-checked 2026-08-05
  (`results/middle-kingdom-phase3.md`), and no king convex enumeration in the
  literature, all classical convex work being edge-connected.
- What is left of the "classical tractability" intuition is the perimeter
  lever, not the area one: D-finite by semiperimeter, per the split above.

The nugget's own suggestion — "a small GF derivation" — is closed with it.
There is no closed form to derive at the searched sizes.

## Recorded, not pursued: the k-local interpolation

Between (dir5, column-convex) — rational — and (ctrlB, column-convex) — no
closed form — sits the family "every local minimum of `b` lies within `k` rows
of the global minimum". It interpolates, and it is not worth running for any
`k`. The predicate still needs an unbounded counter for every finite `k`,
because a later descent retroactively invalidates an earlier local minimum:
the transfer state must carry the height above the running minimum to know
whether a local minimum already passed is still within `k` of it, exactly as
ctrlB does. So every member sits on the wrong side of the rule and the family
would farm a supply of sequences all as synthetic as ctrlB, which is itself a
RED control that turned out to be its own sequence
(`results/directed-cone-anchor.md`). The design rule above is the deliverable;
the sequence family is not.
