# Four mechanisms for counting king animals without a height sweep — all four closed

2026-08-20, branch `skeletonkey`. Written after `docs/skeletonkey-reprompt.md`'s
v2 prompt, on jasonp's instruction to set height aside and look for a mechanism
that leverages some other property of animals and of the lattice.

Four candidates were generated, evaluated in the order below, and closed. The
result worth keeping is not the four kills individually — it is that they have
only **four distinct causes** between them, and those four causes also account
for the kills already in the tree. The last section states them, because they
are a cheaper triage than reading four files.

Nothing here needed a compute job. Two small probes ran on ayr; both are named
where they are used.

---

## 1. The determinant handle on connectivity — closed by the triangle

**Mechanism.** Every method this project has used to isolate connectivity puts
a colour on frontier cells. There is one genuinely different handle. For a set
`S`, let `L_S` be the Laplacian of its induced king-subgraph; then
`det(L_S + eps.I)` vanishes to order exactly `C(S)`, the number of components.
Connectivity becomes an *order of vanishing* rather than a partition, and
orders of vanishing compose under gluing in a way partitions do not — which is
what would let it survive a change of scale. The coefficient of `eps^1` is
`n.tau(S)` when `S` is connected and identically zero otherwise, with `tau` the
spanning-tree count.

**Why it closes.** What comes out is weighted by `tau(S)`, so the question is
whether the weight can be divided out. It cannot, for any commutative edge
weighting. A single edge forces every weight to 1; a triangle — which the king
lattice has — then gives `tau = 3`, not 1. Enlarging the ring does not help:
characteristic 3 sends 3 to 0, and characteristic 2 sends it to 1 but then the
2x2 block, which is `K_4`, gives `tau = 16 = 0`.

The general form is sharper than the calculation. **A determinant counts every
spanning tree democratically, and connectivity needs exactly one representative
per set. Choosing a representative is not a linear-algebraic operation** — it
is a canonical-order choice, which is what Redelmeier's enumeration already is.

Weights in `{0,1}` do make the determinant an exact indicator, but of
connectivity through a fixed sublattice, which then closes on cause (2) below.

**Residue.** Summed over `S`, the construction counts lattice *trees* on the
king lattice — a different functional, which `docs/skeletonkey-reprompt.md`
names as the widest open door. It is not easier and it is not the target.

---

## 2. Blocking, and its inverse (inflation) — closed by the bijection test

**Mechanism, and two facts special to this lattice.** Map each cell to the 2x2
block containing it. Two facts hold and neither is available on the square
lattice:

- **Blocking preserves king-connectivity exactly.** Floor-division by 2 moves
  each coordinate by at most 1, so king-adjacent cells land on blocks that are
  equal or king-adjacent. And `Z^2` blocked by 2x2 is `Z^2` again, so the
  coarse object is a king animal on the *same* lattice — self-similar in the
  strongest sense.
- **A 2x2 block is a king-clique.** All four cells are mutually adjacent, so
  every block filling is internally connected for free, and the fine set is
  connected **iff** the *contact graph* on blocks is connected.

The contact rule is local and small: east-west contact needs the left block's
right fine column nonempty and the right block's left fine column nonempty;
diagonal contact needs the two facing corner cells. So the whole of the fine
geometry collapses into a 15-letter alphabet (the nonempty subsets of a block)
plus a per-edge rule.

**Inflation, the inverse direction** (jasonp's question, 2026-08-20): can a
smaller animal be inflated into a larger one by replacing each cell with one of
sixteen options? Yes, with **15** options — the empty subset has to be excluded
or the coarse animal is not recovered — and **no, not every choice stays
connected.** Counterexample: two horizontally adjacent coarse cells, the left
filled with only its left column and the right with only its right column,
leaves two fine cells three columns apart.

**Why it closes.** The correspondence

    a(n) = sum over coarse animals A of
           #{fillings of A totalling n cells whose contact graph is connected}

is exact, and it is a **bijection**. It restates the problem rather than
reducing it, which is the failure mode `results/skeletonkey-l3-3-fattening.md`
established and which the v2 prompt puts first. Concretely, the coarse animal
has between `n/4` and `n` cells, so `a(n)` appears on its own right-hand side
(the `m = n` term is one cell per block, four choices each) and nothing is
smaller. The fibre is a percolation-style partition function on `A` restricted
to connected configurations — the same problem, one scale down.

Dropping the contact constraint to get an inequality is **vacuous**: it gives
`A(x) <= A((1+x)^4 - 1)` coefficientwise, and pushing that to a bound on
`lambda` yields `u <= 4u + 6u^2 + 4u^3 + u^4`, true for every positive `u`. The
one-cell-per-block fillings swamp it.

The clique gift is also a level-1 accident. At the next level the blocks are
4x4 regions, which are not cliques, so their internal linkage has to be
encoded and the alphabet regenerates the partition state. One free level, then
the wall.

**Residue.** Restricting to fillings where contact is automatic gives
injections, hence rigorous lower bounds on `lambda` by concatenation — the
Klarner style the banked `6.543` already comes from.

---

## 3. The 2-adic filtration — closed on this tree's own numbers

**Mechanism.** The stuck form of INV-6 is "find an explicit basis for the
char-2 collapse", which has no known technique. The quantity that actually
governs cost is not a basis but the elementary-divisor spectrum over the
2-adics: rank over `Z/2^m` is the number of elementary divisors of 2-valuation
below `m`, so the char-2 rank is only the first layer of a filtration. Since an
exact `a(60)` needs about 168 bits, the useful question is how the rank grows
with `m`, not what the rank is at `m = 1`.

**Why it closes.** `results/exactchange-probes.md` already answers the part
that matters, and the framing in `docs/skeletonkey-reprompt.md` (~1e6 against
9.4e8) reads more dramatic than the situation is:

- the collapse to `A034299`, `r(21) = 932,071`, is at **column** granularity,
  and the column-level automaton needs one `r x r` matrix per column mask,
  `2^H - 1` of them — the file itself calls this useless;
- at **cell** granularity, where an algorithm can live, the char-2 rank is
  `Theta(H . 2^H)`, about `2e7` at `H = 21`, against the engine's reachable
  `1.3e8`.

So the ceiling on the whole idea is **6x in state count**, and exact values
need words about 2.6x wider than the engine carries now. Best case, roughly
2x — under one height, against a 2.9x per-height cost ladder. The file's own
disposition (residual value is dynamics diversity; the bit it would produce is
already banked) was right.

---

## 4. The relaxation hierarchy — closed twice, and the second closure generalises

**Mechanism, first form.** Connectivity is "no separating cut", so restrict the
family of cuts: forbid only vertical cuts, then staircases with at most `k`
turns, and so on, each level a rigorous upper bound computable with less state.

**First closure.** It does not interpolate. "Every adjacent column pair is
linked" is satisfied by two parallel horizontal bars ten rows apart, so level 1
admits far more than it excludes; and every repair that fixes it has to
remember which run connects to which, which is the partition state. The
hierarchy jumps straight from useless to the full wall.

**Mechanism, second form — the rescue that looked real.** Bound the number of
maximal **runs per column** by `r`. This is a genuine hierarchy: `r = 1` is
column-convex, already derived here (`results/convex-polyplets.md`,
`results/king-subfamilies.md`, A187077); the frontier's component count is
bounded by construction; every level is a rigorous lower bound on `a(n)`; and
the state is `(run positions, a bounded partition)`, which is polynomial in the
height rather than exponential — so **the height wall disappears entirely**.

**Second closure — capture.** Column-convex king animals run 1, 4, 18, 83, 385,
whose successive ratios settle near 4.6, against the full class's
`lambda = 7.12`. Every fixed `r` has the same disease with a slightly larger
constant, because bounding runs per column is a large-deviation restriction on
a typical animal: the subclass grows at a strictly smaller rate, so the ratio
of what it captures to what it should decays geometrically. At `n = 60` the
`r = 1` level is off by about eleven orders of magnitude. The hierarchy
converges pointwise and uselessly.

This is the same failure as the height decomposition tried earlier the same day
(section 6), with a different knob.

---

## 5. The four causes

Every closure above, and as far as this file can tell every closure already in
the tree, is one of these:

1. **Locality.** No local grading separates connected from disconnected. The
   additive invariants a bounded-state sweep can carry are area, perimeter and
   Euler characteristic, and `chi = C - h` never separates its two terms —
   an animal and a two-component set with one hole both have `chi = 1`.
   Isolating connectivity requires cancellation, whose floor is a colour per
   frontier cell.
2. **Capture.** Any subclass defined by bounding a local complexity measure —
   runs per column, frontier components, box dimensions, convexity defects —
   has a strictly smaller growth constant, so what it captures against the full
   class decays geometrically in `n`. No such family gives a useful one-sided
   bound or an "exact bulk plus small correction" split.
3. **Bijection.** A re-encoding carries identical information and pays the same
   floor, however much machinery exists for the target class. Closed L3-3;
   closed blocking here.
4. **Exponent against constant.** Everything in this problem is `c^n`. The
   incumbent is about `1.66^n` (2.25e8 reachable states at `H = 19` is 2.75 per
   height, and two heights buy one unit of `n`). Every asymptotically cleverer
   geometry generated today — bulk-only sweeps, corner-transfer style
   coarse-graining at `exp(boundary)` cost — has a better exponent and a worse
   constant, and loses in every range that can be run.

**The shape a breakthrough has to have** follows: non-local, capturing a
constant share of the class, not a re-encoding, and improving the constant
rather than the exponent. Cause (2) is the one that rules out deterministic
decompositions essentially by definition, since a decomposition one can name is
a bounded-complexity class. It does not apply to a sampler, whose coverage is
not such a class — that is a principled reason to look there, distinct from
treating it as a fallback.

---

## 6. The height decomposition tried first, and what its measurements settled

Before the four above, the day tried "sweep the bulk exactly, estimate the
tail". `experiments/skeletonkey/height_tail_extrapolation.py`, on the banked
`results/ns_a40/perheight/` triangle, closed it and produced two facts worth
keeping.

**Where the sweep ceiling sits.** Fitting the banked rows, `<H> = 1.228 n^0.682`
(against `nu -> 0.6407` in `results/height-distribution-collapse.md`). Exact
quantiles of the height of an `n`-cell animal:

| n | `<H>` | q0.5 | q0.9 | q0.99 | q0.999 |
|---|---|---|---|---|---|
| 20 | 9.46 | 9 | 12 | 15 | 17 |
| 30 | 12.48 | 12 | 16 | 20 | 22 |
| 40 | 15.17 | 15 | 20 | 24 | 27 |

At `n = 40` the sweep ceiling `H = 19` sits just under the 0.9 quantile and the
tower picks up immediately above it — which is why row 40 closes. Carrying the
same collapse forward gives `<H>(60) = 20.0` with predicted q0.5 = 19.8,
q0.9 = 26.4, q0.99 = 31.7, and a tower floor at `H = 29`. **At n = 60 the sweep
ceiling sits at the median and the tower floor sits above the 0.9 quantile**,
so the untouched heights run from the middle of the distribution to past its
ninetieth percentile. There is no "small remainder" to estimate.

**The collapse extrapolates quantiles, not tail shares.** Predicting row 40
from row 30's collapsed shape gives 14.6, 19.4, 24.3, 26.7, 29.2 against exact
15, 20, 24, 27, 29 — good to within a cell. Read instead as tail shares the
same prediction is off by a factor of 2 to 4 at the far end, because a small
shape error is amplified that way. An earlier draft of this file asserted the
collapse was simply not a tail predictor; that was wrong, and the quantile
reading is the one to use.

**No free bulk either.** `results/fixed_height_gfs.txt` would have given
`T(n,H)` at any `n` for nothing, but it stops at `H = 11` and the recurrence
orders run 1, 3, 7, 15, 42, 106, 278, 711, 1897, 5005, 13381 — 2.65 per height,
the frontier's own rate. `H = 19` would need on the order of `2e7` terms.

**The general form of the closure**, which subsumes any variant organised by
height, width or perimeter: covering all but a vanishing part of the class
needs `H_max` about `2 n^0.68` at cost about `3^H_max`, against about `3^(n/2)`
for the *entire* exact computation. Those cross near `n = 76`, where the
bulk-only method needs `H = 40`. **"Compute the bulk exactly, estimate the
tail" is never cheaper than computing everything, at any `n` that could be
run.**

---

## 7. The combinations, and the one number left standing

Tried, all closed: 1+3 (the determinant as the bookkeeping blocking needs
between scales — dies with 1); 1+3 in characteristic 2 (spanning trees mod 2
gives animals weighted by tree-parity, which is not `a(n) mod 2`); 2 with the
cell-level rank (section 3); 4 with the capture cause (section 5); and the
Sykes-Essam matching pair, which stays closed on the accounting already made —
reaching king `n = 40` through it needs square-lattice data to order about 200
in the percolation variable, against a literature record of 56 by area.

What is left holding a real number is the cut-compression gap, and this day
sharpens *why* it is unrealised rather than merely restating that it is. The
Hankel floor is `Motzkin(H/2+1) = 15,511` independent quantities at `H = 21`
where the incumbent carries about `4e8` states. Closing it would move the base
from about `1.66` to about `1.32` per unit of `n`, which is worth roughly
twenty-five terms — much the largest prize anywhere in this problem. And the
char-2 **column** rank, `0.44 . 2^H`, sits far closer to that floor than the
engine does. The obstruction is now locatable:

> the compression exists at column granularity; an algorithm must read one
> cell at a time; and the cell-level rank is `Theta(H . 2^H)` rather than
> `2^H`. That factor of `H` is the whole difference between a 6x win and a
> 20x one, and between either of those and the floor.

## 8. What ran, and what it cost

- `experiments/skeletonkey/height_tail_extrapolation.py` — seconds on ayr,
  on the banked triangle. RED gate: perturbing a row must move the quantile.
- `cell_sparsity_modp 8` landed the same afternoon (`~/var/skeletonkey/`), and
  its `H = 8` row is used in section 3's reading only through the published
  `results/exactchange-probes.md` figures, not on its own.

No candidate in this file was expensive enough to justify a compute job, which
is itself the point: all four were settled by counting.
