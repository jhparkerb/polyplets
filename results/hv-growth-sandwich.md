# Why (dir4, HV-convex) has the HV-convex growth constant — proved (2026-08-05)

`docs/middle-kingdom-followups-plan.md` Phase 1. The open item it closes, from
`results/middle-kingdom-phase3.md` and `results/middle-kingdom.md`:

> (dir4, HV-convex) sharing the unrestricted constant to 49 digits with a clean
> amplitude ratio looks like a theorem waiting: a bijection or a kernel argument
> that factors the 4-cone condition out of the HV-convex transfer matrix.

There is no bijection. Table B is the evidence — the two series' `d_n/d_(n−1)`
differ (0.803651401483 against 0.481008794) and their amplitude ratio, stable to
54 digits, satisfies no integer relation in any in-capacity PSLQ box — though
not for the reason the plan reads into it; see the 2026-08-06 note below. What
replaces the bijection is a squeeze, and it proves more than the 4-cone case.

**2026-08-06 — the subdominant half, re-measured and part-proved.** Everything
above stands. What changed is below "Where the subdominant singularities come
from": the reading that the two series do not share `0.4810` is wrong (a
subclass of the 4-cone series has it, at 200 trusted digits), the claim that the
extra exponential is the descending block's is now a theorem at the level of
growth rates (Lemma 4, Proposition 7) and a conjecture at the level Table B
measures (Conjecture 8), and Phase 1's two digit claims both reproduce and are
floors.

**2026-08-06, later still — Lemma 3 is stronger than it was written.** The
column-join is injective at fixed `(i, j)` on the nose, so
`M(i)M(j) ≤ M(i+j)` with no factor and no quasi-super-multiplicativity: see the
rewritten Lemma 3. Fekete then makes the limit a supremum, so every banked term
is a rigorous lower bound on `µ`, and Proposition 6's whole proof comes down to
an injection, Fekete, and a stack bound. Lemma 2's stack bound is now
elementary too (B2): the partition count is bounded by splitting at `√n`, so
Hardy–Ramanujan is gone and the squeeze uses no analytic input at all. Nothing
downstream changes; what changes is the warrant, which is the point of
`docs/sortie-publication-plan.md` B1 and B2.

**2026-08-06, later — the amplitude ratio has a formula.** See "The amplitude
ratio is a ratio of two explicit feed vectors". Table B's 54 trusted digits
become 251; the ratio is `(1/2)(w4·φ)/(w·φ)` with both feed vectors explicit
and `φ` the bounded solution of `φ(h) = (2 − x^{h−1})φ(h−1) − φ(h−2)`
(Propositions 9–11); PSLQ stays negative in every enlarged box, over `Q` and
over `Q(µ)`; and the same recurrence yields `µ` by shooting, 987 digits in
1.6 s with no series.

**Proposition 6.** Let `A(n)` count HV-convex king animals of area `n`, and let
`C` be any class with

    staircase  ⊆  C  ⊆  HV-convex.

Then `lim C(n)^(1/n)` exists and equals `lim A(n)^(1/n) = µ = 3.128943269730886…`.

`(dir4, HV-convex)` is such a class, so the 49-digit agreement is a theorem, not
a coincidence. So is `(dir5, HV-convex)`, `(ctrlB, HV-convex)` and
`(mdir, HV-convex)` — those three are equalities anyway (Corollary 4) — and so
is anything else one puts between the two rungs. The 4-cone condition is not
special. **Every** condition that leaves the staircase animals alone leaves `µ`
alone, because the staircase animals already carry all of the exponential
entropy.

A by-product: **A225114 (staircase king animals = skew shapes with no empty row
or column) has growth constant `µ` too**, measured here to 204 digits. The entry
carries no asymptotic, and the repo had no growth constant for it
(`results/countable-subpopulations-criterion.md`: "the repo banks no GF for
A225114").

## The operator comparison the plan asked for

Step 1 of the plan: write both operators in the same basis. They already are.
`cpp/middle_kingdom_tm.cpp`'s PROFILE engine carries state `(h, pb, pt)` — the
last column's height and the two unimodality phases — and steps by
`d = b(j+1) − b(j)` with `s := h − h'` marking where the top turns
(`d > s` ⟺ `t` rises). Modes `hv` and `hvdir4` differ in one line: the floor on
`d` is `−h'` for `hv` and `−1` for `hvdir4`.

Step 2: is that a rank-bounded perturbation, or a change of the boundary/phase
structure only? **The latter, and exactly.** `pb` and `pt` each flip at most
once and never flip back, so the operator is block-triangular in the four
phases, and the diagonal blocks are

| phase | meaning | step constraint | kernel `K(h, h')` |
|---|---|---|---|
| `(0,0)` | `b` falls, `t` rises (heights grow) | `s ≤ d ≤ 0` | `h' − h + 1`, `h' ≥ h` |
| `(1,0)` | both rise | `d ≥ max(0, s)` | `min(h, h') + 1` |
| `(0,1)` | both fall | `d ≤ min(0, s)` | `min(h, h') + 1` |
| `(1,1)` | `b` rises, `t` falls (heights shrink) | `0 ≤ d ≤ s` | `h − h' + 1`, `h' ≤ h` |

The dir4 floor `d ≥ −1` bites only where `pb = 0`, i.e. on blocks `(0,0)` and
`(0,1)`, and there it replaces the kernel by one with entries in `{0, 1, 2}`.
Blocks `(1,0)` and `(1,1)` are **untouched, entry for entry**. Block `(1,0)` is
the staircase kernel `min(h, h') + 1`, and Proposition 6 says that block alone
fixes `µ`.

That also answers the finite-rank framing of
`results/countable-subpopulations-criterion.md` (condition 2, "the transfer
kernel must have finite rank in the unbounded state variable"): it applies, and
it localises. The infinite-rank coupling in this family is the single kernel
`min(h, h') + 1`, which appears twice, once in each middle block. The 4-cone
condition rewrites one of the two copies and leaves the other intact, which is
the whole of its effect on the leading behaviour. The criterion's own flagged
prediction —
"Staircase (A225114) has both boundaries constrained against the previous
column, which produces the same min/max coupling, so the rule **predicts** no
rational GF for it; … its 14 banked terms cannot test the prediction" — is now
testable and holds with room to spare: on 700 terms the staircase series is
**EXCLUDED** at order ≤ 24 / degree ≤ 24 (rank 625 of 625) and non-algebraic at
degree ≤ 20 / t-degree ≤ 20 (rank 441 of 441), the same boxes and the same tool
that cleared the unrestricted series.

## The proof

**Orientation, without notation.** `A(n)` counts HV-convex king animals of `n`
cells — blobs with no gap in any row or column. `M(n)` counts the staircase
ones, where scanning left to right both edges only ever move up. Staircase is a
thin slice of HV-convex, and the claim is that the two counts nevertheless grow
at the same exponential rate, as does every family between them.

Every intermediate family is trapped between `M` and `A` term by term, so the
whole job is to show those two grow alike; nothing has to be proved about the
individual families. One direction is free — staircase animals are HV-convex.
For the other, read an HV-convex animal left to right: it **fattens**, then
**shears**, then **thins**. The shearing middle is a staircase animal and the
two ends are stacks, columns nesting one inside the next (Lemma 1). Stacks are
rare enough that their number outgrows no exponential, so the ends cannot move
a growth rate (Lemma 2); the middle has a rate at all because two staircase
animals glue end to end without waste (Lemma 3). The squeeze follows.

The gluing carries a bonus: the rate is the *supremum* of the computed values,
not merely their limit, so every banked term is a rigorous floor under `µ`.

Throughout, an HV-convex king animal is a sequence of column intervals
`[b(j), t(j)]`, `j = 1..k`, with `b` valley-unimodal and `t` peak-unimodal
(Corollary 4 of `results/middle-kingdom-phase3.md`), counted up to translation.
Write `d(j) = b(j+1) − b(j)`, `h(j) = t(j) − b(j) + 1`, `s(j) = h(j) − h(j+1)`.

**Lemma 1 (three-block factorisation).** Give column `j` the phase
`(pb, pt)` with `pb = 1` iff some earlier step had `d > 0` and `pt = 1` iff some
earlier step had `t` decreasing. Valley-unimodality of `b` and peak-unimodality
of `t` make both bits monotone in `j`, so the columns split into three
consecutive (possibly empty) runs `C1 C2 C3` carrying phases `(0,0)`; one of
`(1,0)` or `(0,1)`; and `(1,1)`. Every step internal to a run obeys that run's
constraint in the table above. Taken standalone,

- `C1` and `C3` are **monotone-height blocks** (heights nondecreasing and
  nonincreasing respectively; reversing the column order carries one to the
  other), counted by `P(n)`;
- `C2` is a **staircase animal** (phase `(1,0)`) or the vertical mirror of one
  (phase `(0,1)`), counted by `M(n)`.

The animal is recovered from `(C1, C2, C3)`, the two junction offsets, and one
bit naming `C2`'s phase. Each junction offset `d` lies in `[−h', h]` with
`h + h' ≤ n`, so it takes at most `n + 1` values, and

    A(n)  ≤  2 (n+1)^2  ·  sum_{i+j+l=n}  P(i) M(j) P(l),     P(0) = M(0) = 1.   (*)

**Attribution (added 2026-08-06, `results/novelty-sortie.md` N3).** This
decomposition is not new in kind. Gouyou-Beauchamps & Leroux, *Enumeration of
symmetry classes of convex polyominoes on the honeycomb lattice*, FPSAC 2004
(arXiv:math/0403168), §2.3 "Growth phases of convex polyominoes", decompose a
convex polyomino into blocks `H_ij` by the growth phases of its upper and lower
profiles, with the column state an ordered pair, the transitions one-way, the
extreme blocks `H00`/`H22` identified as **stack polyominoes** and the middle
blocks as **staircase polyominoes** with `H02 = Pa = H20`. That is Lemma 1,
Lemma 2's identification and Proposition 9 below, for convex polyominoes on the
honeycomb lattice. Their square-lattice companion (Leroux, Rassart & Robitaille,
*Adv. Appl. Math.* 21 (1998) 343–380) uses a different route — partitions,
stacks, shifted stacks and directed convex, Temperley–Bousquet-Mélou — so 2004
is the source to cite. Both PDFs are in `papers/`. What is not
theirs: the king lattice (their middle kernel is `min(h,h')`, ours is
`min(h,h')+1`), a class with no exact solution, and everything Propositions 6,
7, 10 and 11 do with the blocks.

**Lemma 2 (the outer blocks are stacks, hence sub-exponential).**
`P(n) = A001523(n)`, the number of stacks / weakly unimodal compositions of `n`,
and `P(n) ≤ E(n) := (n+1)^{4√n+6}`, so `P(n)^{1/n} → 1`.

The lemma is two independent claims bolted together: *what* the outer blocks
are (a bijection), and *how few* of them there are (a counting bound). They are
proved separately below and only the second is used downstream.

*Proof, part 1: a stack is a weakly unimodal composition.* In a phase-`(1,1)`
block the bottoms rise and the tops fall, so the column intervals are **nested**:
`[b(j+1), t(j+1)] ⊆ [b(j), t(j)]`. Nesting means that if you ask *which columns
meet row `y`*, the answer is never a broken set — it is a prefix `1..r(y)`.
So transpose the picture: instead of the column heights, record the row widths
`r(y)`, read bottom to top. Since `{y : r(y) ≥ k} = [b(k), t(k)]` is a decreasing
nested family of intervals, `r` rises then falls — weakly unimodal — and
`Σ_y r(y) = n`. The stack is rebuilt from `r` alone, so the map is a bijection
and `P(n)` is the number of weakly unimodal compositions of `n`.

Worked instance: columns `[0,4], [1,3], [2,2]` (heights `5, 3, 1`, area 9) have
row widths `r = (1, 2, 3, 2, 1)` from row 0 up — unimodal, and also summing to 9.

*Proof, part 2: there are few of them.* Cut a weakly unimodal composition at its
peak and what falls out on either side is a partition, so
`P(n) ≤ (n+1)^2 p(n)^2` — the `(n+1)^2` pays for the peak's position and value.

For `p(n)` the classical asymptotic is not needed, and the squeeze in
Proposition 6 uses only `P(n)^{1/n} → 1`, so a deliberately crude bound will do.
Put `s = ⌈√n⌉` and split a partition of `n` at `s`. The parts `≤ s` are
determined by their `s` multiplicities, each an integer in `[0, n]`, so they
contribute at most `(n+1)^s` choices. The parts `> s` have size `≥ s+1`, so
there are at most `L = ⌊n/(s+1)⌋` of them, and listing them in nonincreasing
order gives a sequence of length `≤ L` over `n` values, at most
`(L+1)n^L ≤ (n+1)^{L+1}` choices. Hence

    p(n)  ≤  (n+1)^{s+L+1}  ≤  (n+1)^{2√n+2},

since `s ≤ √n + 1` and `L ≤ n/(√n+1) ≤ √n`. So `P(n) ≤ (n+1)^{4√n+6} = E(n)`
and `log P(n)/n ≤ (4√n+6) log(n+1)/n → 0`. ∎

Only the exponent matters: `√n · log n` is `o(n)`, so however many stacks there
are, they carry no exponential. That is the entire role of Lemma 2 in the
squeeze — the outer blocks are counted only to be discarded.

(Hardy–Ramanujan would give the sharper `P(n) = e^{O(√n)}`; nothing downstream
distinguishes the two, and the elementary bound keeps Proposition 6 free of
analytic input. `docs/sortie-publication-plan.md` B2.)

Measured: `P(n) = 1, 2, 4, 8, 15, 27, 47, 79, 130, 209, 330, 512` matches
A001523 termwise (`experiments/monotone_block_growth.py`, brute force and DP
agreeing, verified against the entry's own data by
`experiments/oeis_lookup.py`), and `P(n)^(1/n)` falls 1.706 → 1.168 over
`n = 10..400`.

**Lemma 3 (the staircase count is supermultiplicative).**
`M(i) M(j) ≤ M(i+j)` for all `i, j ≥ 0` (with `M(0) = 1`), and therefore
`lim M(n)^(1/n)` exists and equals `sup_n M(n)^(1/n)`.

*Proof.* Given staircase animals `X` (area `i`, last column height `h`) and `Y`
(area `j`, first column height `h'`), slide `Y` up by `d = max(0, h − h')` and
butt the two column sequences together.

*Why that `d`, and no other.* Staircase means both boundaries nondecreasing.
At the seam, `b` not dropping forces `d ≥ 0`; `t` not dropping forces
`d ≥ h − h'`. So `max(0, h − h')` is the smallest legal slide — `d` is a
function of `X` and `Y`, not a choice being made, which is what stops the join
from smuggling in information.

*The join is in the class.* `d ≥ 0`, so bottoms stay nondecreasing;
`d − s = max(0, h − h') − (h − h') ≥ 0`, so tops stay nondecreasing; and
`d ≤ h`, since `d = h − h' ≤ h − 1` when `h ≥ h'` and `d = 0` otherwise, so the
junction columns are king-adjacent (`b(r+1) ≤ t(r) + 1`). Area is `i + j`.

*The join is injective at fixed `(i, j)`.* The question is whether the seam can
be found again from the glued animal alone, given `i` and `j`. It can: every
column is nonempty, so the cumulative areas `h(1) + … + h(r)` are **strictly**
increasing, and a strictly increasing sequence hits `i` at most once. Cut at
that unique prefix — those are `X`'s columns, the rest are `Y`'s, each read back
up to translation, which is how both were counted in the first place. No split
index has to be supplied alongside the join, so distinct pairs have distinct
images and `M(i) M(j) ≤ M(i+j)`.

Fekete's lemma in its supermultiplicative form then gives
`lim M(n)^(1/n) = sup_n M(n)^(1/n)`. That is mathlib's
`Subadditive.tendsto_lim` applied to `−log M`, exactly as
`polyplets/Polyplets/Growth.lean`'s `a_supermul`, `negLogA_subadditive` and
`lambda_tendsto` do for `λ`. ∎

**By-product: every banked term is a rigorous lower bound on `µ`.** Because the
limit is a supremum, `µ ≥ M(n)^(1/n)` for each `n` with no extrapolation
involved. At `n = 700`,

    µ  ≥  M(700)^(1/700)  =  3.12340450886853853211…

against the extrapolated `3.128943269730886…`. The bound is exact arithmetic on
a banked term; the digits past `3.12` remain extrapolation.

*Provenance of the fix.* An earlier version of this lemma paid a factor `i + j`
for the index of `X`'s last column and derived existence by hand from
quasi-super-multiplicativity in the sense of Barequet, Ben-Shachar & Osegueda,
*Concatenation arguments and their applications to polyominoes and polycubes*,
Comput. Geom. 98 (2021) 101790, §2.2, with `P(x) = 1/x`
(`papers/barequet_benshachar_osegueda_2021_concatenation_arguments.pdf`). The
index is not free information, since strictly increasing cumulative areas
already carry it, so the exact inequality holds and neither the `(i+j)` nor the
citation is needed here. The citation remains the right tool for a
concatenation that genuinely loses information.

Measured (`experiments/staircase_supermul.py`, 0.6 s): brute force over `(h, d)`
reproduces `M(1..12)`; over all `i + j ≤ 12` every one of 1182960 joins lands in
the class, the map is injective at fixed `(i, j)`, and the area-`i` cut inverts
it; and on the banked 700 terms `M(i)M(j) ≤ M(i+j)` has **zero violations** for
every pair. Three RED controls, all required to fail: the stacks `P(n)` of
Lemma 2 are *not* supermultiplicative (`P(2)P(20) = 22480 > 22277 = P(22)`), so
the series check is not vacuous; the same join with `d = 0` leaves the class;
and cutting at cumulative area `i + 1` fails to invert.

**Proof of Proposition 6.** Write `µ = lim M(n)^(1/n) = sup_n M(n)^(1/n)`,
which exists by Lemma 3 and is `≥ 1`. Fix `ε > 0` and take `C_ε` with
`M(j) ≤ C_ε (µ+ε)^j`. In (*), bound `P(i), P(l) ≤ E(n)` by Lemma 2, which
applies to every `i, l ≤ n` since `E` is nondecreasing:

    A(n)  ≤  2 (n+1)^4 E(n)^2 C_ε (µ+ε)^n,

and `E(n)^{1/n} → 1`, so `limsup A(n)^(1/n) ≤ µ + ε` for every `ε`, i.e.
`limsup A(n)^(1/n) ≤ µ`.
In the other direction, staircase ⊆ C ⊆ HV-convex gives `M(n) ≤ C(n) ≤ A(n)`
termwise, so `liminf C(n)^(1/n) ≥ lim M(n)^(1/n) = µ` and
`limsup C(n)^(1/n) ≤ limsup A(n)^(1/n) ≤ µ`. Both limits exist and equal `µ`. ∎

**The square-lattice analogue is classical** (`results/novelty-sortie.md` N1).
Convex polyominoes by area grow at 2.30914… (Bender 1974) and the parallelogram
subclass, A006958, has the same constant: measured at 2.309138593330495, flat
from n = 100 to n = 400 (`experiments/square_staircase_area.py`, which builds
both series from the one kernel — `min(h,h')` square, `min(h,h')+1` king — and
reproduces A006958 and A225114 as positive controls). So Proposition 6's
conclusion could have been read off the solved models one lattice over. What
the proposition adds is the king case, where neither class is solved, and the
statement for *every* intermediate class rather than for two particular ones.

Staircase ⊆ (dir4, HV-convex) is Proposition 2: bottoms nondecreasing means
`d ≥ 0 ≥ −1`. The grid already records it as the collapse
`(dir4, staircase) = A225114`.

## Brute force, n ≤ 14

Against `results/mk_grid20_n14.txt` (Phase 0's independent Redelmeier
enumeration, `build/directed_cone_anchor grid 14 8`), columns *staircase*,
*(dir4, HV-convex)* and *(none, HV-convex)*:

| n | staircase `M` | (dir4, HV) | HV-convex `A` |
|---|---|---|---|
| 1 | 1 | 1 | 1 |
| 3 | 9 | 15 | 16 |
| 8 | 2659 | 5417 | 8390 |
| 14 | 2494307 | 4292477 | 8389720 |

`M(n) ≤ D(n) ≤ A(n)` at every `n ≤ 14`, and the factorisation bound (*) holds at
every `n ≤ 14` as well (`experiments/monotone_block_growth.py`; at `n = 14`,
`8389720 ≤ 3848993100`). Pinned by `make gate-middle-kingdom`, which gained the
`stair` mode against the grid's staircase column, the termwise chain
`stair ≤ hvmono ≤ hvdir4 ≤ hv`, and a RED control: dropping the tops condition
from `stair` leaves `ccmono` = A007052 = 1, 3, 10, 34, …, which must not equal
A225114 = 1, 3, 9, 28, ….

## The numerics: four rungs, one constant

Two new modes in `cpp/middle_kingdom_tm.cpp` supply the missing rungs —
`stair` (`d ≥ 0` and `d ≥ s`) and `hvmono` (`d ≥ 0`, `t` peak-unimodal), 700
terms each in 0.87 s / 50 MB and 1.28 s / 58 MB on gympie. All four series are
run through `experiments/convex_growth.py` at 500 digits of working precision:

| class | first terms | trusted digits of µ | amplitude `C` | `d_n/d_(n−1)` |
|---|---|---|---|---|
| staircase (A225114) | 1, 3, 9, 28, 87, 272 | 204 | 0.28932146397165132308 | 0.48100879371 |
| HV-convex, `b` nondecreasing | 1, 3, 10, 33, 107, 342 | 202 | 0.37545302027992473174 | 0.48100879371 |
| (dir4, HV-convex) | 1, 4, 15, 53, 177, 567 | banked | 0.45030318571234118235 | **0.803651401483** |
| HV-convex | 1, 4, 16, 61, 221, 766 | 199 | 0.97445221313500464915 | 0.48100879371 |

The staircase µ, at its 204 trusted digits, reproduces **every one** of the 199
digits the HV-convex series pins (`results/convex-polyplets.md`) and continues
past them:

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549                 <- the banked 199
                                        000485           <- staircase, beyond them
```

`hvmono` does the same at its own 202 digits. Three independent series, three
different classes, one constant.

The amplitude column reproduces Table B independently: `C_dir4 / C_HV =
0.46210904920994244003`, against the plan's directly extrapolated
0.462109049209942440035662387700305832841163439729980425.

## Where the subdominant singularities come from

Proposition 6 settles the leading term and says nothing about the corrections,
which is where the difference between the two series lives. The block table
locates them too, and the second one is measurable.

Of the four diagonal blocks, exactly two carry exponential weight standalone:

| block | unrestricted | under the 4-cone condition |
|---|---|---|
| `(0,0)` | heights nondecreasing, sub-exponential (Lemma 2) | still sub-exponential |
| `(1,0)` | staircase, growth **µ = 3.1289…** | untouched |
| `(0,1)` | mirror staircase, growth **µ** | truncated, growth **2.5146…** |
| `(1,1)` | heights nonincreasing, sub-exponential (Lemma 2) | untouched |

The truncated `(0,0)` block stays sub-exponential for a different reason from
Lemma 2's: with `h' ≥ h`, the entry count `min(2, h' − h + 1)` is 2 only at a
strict rise, the strict rises take distinct heights, so there are at most
`√(2n)` of them and the weight is `≤ 2^√(2n)`, against the `≤ E(n)` height
sequences of Lemma 2.

The truncated `(0,1)` block is the exception, and it is the only one. It is not
height-monotone — `h' ≤ h` at weight 2, `h' = h+1` at weight 1, `h' > h+1`
forbidden — so heights can climb one row at a time and Lemma 2 does not apply.
Counted by area (`experiments/dir4_descent_block.py`, DP against a brute-force
oracle at `n ≤ 12`, RED control on the climb weight) it is

    1, 3, 8, 21, 54, 138, 350, 885, 2233, 5626, …

with no OEIS match on ten terms (the six-term prefix collides with A127358 and
two others, all of which diverge by `n = 9`: 2230 against 2233), and its growth
constant on 700 terms is

    2.5145796438787291885104371943430998201410308559007832719354957107238409922963
    2690389299337761749953732175539964789209170137762869374741150849461805388232
                                                              (153 trusted digits)

Reproduced independently 2026-08-06 by `experiments/descent_block_oracle.py`,
which derives the same series from the geometry rather than from this kernel —
a DFS over explicit column intervals `[b, t]` with `b` and `t` nonincreasing and
`d ≥ −1`, checked against a forward DP on the *last* column's height (Phase 1's
recursion runs backward from the first), agreeing on all 700 terms. Three RED
controls, each cross-checked between its own DFS and DP and each required to
diverge: dropping the 4-cone floor (which returns the mirror staircase
`1, 3, 9, 28, 87, …` = A225114, as the block table says it must), loosening it
to `d ≥ −2`, and weighting the climb 2. The 153 is `convex_growth.py`'s figure
and reproduces; Prony on the same terms trusts 242 (below).

**That is the (dir4, HV-convex) subdominant growth rate.** 2026-08-06 settled
how far that sentence can be pushed. The three claims Phase 1 left entangled
are separated below: one is now a theorem, one is a measurement worth many more
digits than Phase 1 quoted, and the sentence Table B actually turns on is a
conjecture.

### The series splits, and so does the spectrum

The phase automaton makes the split exact rather than asymptotic. Partition the
class by whether an animal's phase path ever visits `(0,1)`:

    D(n)  =  D_asc(n)  +  D_desc(n).

Both halves come out of the same engine: `build/middle_kingdom_tm hvdir4asc`
deletes the `(0,1)` state from the automaton, and `D_desc = hvdir4 − hvdir4asc`
is the rest. Oracle for both, and for the block series, is
`experiments/descent_block_oracle.py` — an independent DFS over explicit column
intervals `[b, t]` that carries the two phase bits itself, agreeing with the
engine on every `n ≤ 14` and with the block DP on all 700 terms.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| `D` = hvdir4 | 1 | 4 | 15 | 53 | 177 | 567 | 1767 | 5417 |
| `D_asc` | 1 | 3 | 10 | 34 | 115 | 382 | 1244 | 3993 |
| `D_desc` | 0 | 1 | 5 | 19 | 62 | 185 | 523 | 1424 |

Read the exponential spectrum of each 700-term series by Prony's method
(`experiments/prony_spectrum.py`: solve for the constant-coefficient recurrence
the tail obeys best and take the roots of its characteristic polynomial, so
every `λ_i` is measured in one solve, with no peeling and no assumed model).
Trusted digits are the agreement between three independent fits — window `N`
against `N−50`, order `k` against `k+1` — minus a guard, the same discipline
`convex_growth.py` applies to the leading constant.

| series | `λ_1` | `λ_2` | `λ_3` | `λ_4` |
|---|---|---|---|---|
| staircase | **3.12894326973088…** | **1.50504922775900…** | 1.28433727098118… | −1.25776216033063… |
| HV-convex | same | same | same | same |
| `hvmono` | same | same | same | same |
| **`D_asc`** | same | same | same | same |
| block `T` | **2.51457964387872…** | **1.43040460381247…** | 1.24846593371011… | 1.17441805313317… |
| **`D_desc`** | same | same | same | same |
| `D` = dir4 | 3.12894326973088… | 2.51457964387872… | 1.50504922775900… | 1.43040460381247… |

`D`'s spectrum is the other two interleaved, and the interleaving keeps going:
`λ_5(D)` is the staircase's `λ_3` and `λ_6(D)` its `λ_4`. Digits, from
`results/subdominant_identification.log` (`agree` = digits the two measured
numbers share; `bearable` = the smaller of their two trusted counts, which is
all a coincidence can be asserted to however many happen to agree):

| claimed coincidence | agree | bearable |
|---|---|---|
| `λ_1(D_desc)` = `λ_1(block)` | 246 | **226** |
| `λ_2(D_desc)` = `λ_2(block)` | 72 | 64 |
| `λ_1(D_asc)` = `λ_1(staircase)` | 310 | **284** |
| `λ_2(D_asc)` = `λ_2(staircase)` | 86 | **76** |
| `λ_3(D_asc)` = `λ_3(staircase)` | 37 | 32 |
| `λ_2(D)` = `λ_1(block)` | 236 | **217** |
| `λ_3(D)` = `λ_2(staircase)` | 78 | **69** |
| `λ_4(D)` = `λ_2(block)` | 62 | 55 |
| `λ_2(staircase)` = `λ_2(HV-convex)` | 85 | 77 |

Negative controls, which must fail and do: the block's `λ_1` and `λ_2` match no
root of `D_asc` (best 0 and 1 digits), and the staircase's `λ_2` matches no root
of `D_desc` (best 1 digit). The 2.5146 really is absent from one half and the
1.5050 from the other.

### What that buys, and what it does not

**Lemma 4.** `lim T(n)^(1/n)` exists. Write `ν` for it.

*Proof.* Let `T_h(n)` count runs whose first column has height `h`, and
`T_1 = T_(h=1)`. (i) `T(n) ≥ 2T(n−1)`: append a height-1 column, which the
truncated kernel admits at weight 2 from any height. (ii) `T_h(n) ≤ 2T(n−h)`:
delete the first column; the step out of it had weight ≤ 2. With (i),
`T_h(n) ≤ 2^(2−h) T(n−1)`, so `Σ_(h≥4) T_h(n) ≤ T(n−1)/2 ≤ T(n)/4` and
`T(n) ≤ 4·max_(h≤3) T_h(n)`. (iii) `T_h(n) ≤ T_1(n + h(h−1)/2)`: prepend the
climb `1, 2, …, h−1`, whose every step is the weight-1 `h' = h+1` transition;
for `h ≤ 3` that costs at most 3, and `T_1` is nondecreasing by (i)'s argument.
So `T(n) ≤ 4 T_1(n+3)`. (iv) `T_1(i) T_1(j) ≤ T_1(i+j)`: join two runs that
both start at height 1 by the step "last height → 1", weight 2; the pair is
recovered from the join and the prefix area. Fekete gives
`lim T_1(n)^(1/n) = sup_n T_1(n)^(1/n)`, and `T_1 ≤ T ≤ 4T_1(·+3)` squeezes
`T` onto the same limit. ∎

**Proposition 7.** `lim D_asc(n)^(1/n) = µ` and `lim D_desc(n)^(1/n) = ν`.

*Proof.* `D_asc ≥ M` termwise: a staircase animal has `d ≥ 0` and `d ≥ s` at
every step, so it can never enter `(0,1)`, which needs `d ≤ 0` and `d < s`.
With `D_asc ≤ D` and Proposition 6, `lim D_asc(n)^(1/n) = µ`.
For `D_desc`, Lemma 1's factorisation with `T` in place of `M` gives
`D_desc(n) ≤ 2(n+1)^2 Σ_(i+j+l=n) P0(i) T(j) P1(l) ≤ 2(n+1)^4 E(n)^2 C_ε (ν+ε)^n`,
so `limsup D_desc(n)^(1/n) ≤ ν`. In the other direction, take a `T`-run of area
`m` whose first column is `[0, h−1]` and prepend the column `[0, h]`: the
joining step has `d = 0 ≤ 0` and `s = 1 > d`, so it enters `(0,1)`, the run's
own steps keep it there, and the result is a (dir4, HV-convex) animal of area
`m + h + 1`. Restricting to `h = 1` gives `D_desc(n) ≥ T_1(n−2)`, so
`liminf D_desc(n)^(1/n) ≥ ν` by Lemma 4. ∎

So `D(n) = D_asc(n) + D_desc(n)` with the two halves growing at exactly `µ` and
exactly `ν`: **`ν` is not an artefact of an extrapolation, it is the growth
constant of an explicitly counted half of the series.** That is proved.

What is *not* proved is the step from there to Table B's diagnostic. Table B's
`d_n/d_(n−1)` measures the second exponential of `D` itself, and reading it off
the split needs sharp asymptotics, not exponential rates:

**Conjecture 8.** `D_asc(n) = C µ^n (1 + O(ρ^n))` with
`ρ = 0.48100879370959…`, and `D_desc(n) = C' ν^n (1 + O(σ^n))` with
`σ = 0.568844421888…`, where
`C = 0.45030318571234118235361371383386342153…` and
`C' = 2.5795006951239199769623573391294166…`.

Granting it, `D(n) = C µ^n + C' ν^n + O((µρ)^n + (νσ)^n)` with
`µρ = 1.50504922775900…` and `νσ = 1.43040460381247…`, both below `ν`, so the
subdominant exponential of `D` is exactly `ν` and Table B's 0.803651401483 is
`ν/µ`. Measured support: the two correction ratios are `λ_2/λ_1` of the two
halves, trusted to 76 and 64 digits. The amplitudes are quoted to the 40 digits
`convex_growth.py` prints, on series whose growth constants that run trusts to
200 and 150 digits; `C` is stable across the last two `n` it reports.

This is not a gap peculiar to the subdominant. **The repo has no proof that any
series in this family has a sharp asymptotic at all** — Proposition 6 and
Lemma 3 give exponential rates, never `A(n) ~ Cµ^n`, and the amplitudes of the
four-rung table above are all measured, none derived. Asking for the second
exponential as a theorem is asking for strictly more than is known about the
first. A route does exist, and it is specific: A225114's OEIS entry carries a
**conjectured** continued fraction (Kurkov, Sep 2024),

    g.f. = 1/(2 − 1/(1 − x/(1 − x/(1 − x²/(1 − x²/(1 − x³/(1 − x³/(1 − …)))))))),

whose depth-24 convergent reproduces 41 terms of A225114 and whose poles, as
`1/x`, land on the measured staircase spectrum — 30, 27, 14 and 16 digits on
`λ_1 … λ_4`, improving with depth (`experiments/staircase_cf_poles.py`, with a
RED control that changes one partial numerator and diverges at n = 6). A proof
of that continued fraction would supply the meromorphic continuation and the
spectral gap that the coefficient-level argument cannot reach; the same would
then be wanted for `T`, which has no OEIS entry and no conjectured form.

### The corrected reading of Table B

Table B's two numbers are right and its reading of them is wrong. Both series
carry `0.481008794`:

| series | `d_n/d_(n−1)` | what it is |
|---|---|---|
| HV-convex, `hvmono`, staircase | 0.481008794 | `λ_2/λ_1`, the staircase block's own correction |
| `D_asc` — a subclass of (dir4, HV-convex) | **0.48100879371** | the same one |
| `D_desc` and the block `T` | 0.568844421888 | the block's own correction |
| (dir4, HV-convex) | 0.803651401483 | `ν/µ`, the *extra* exponential in front |

The 0.4810 in row two is measured on 4-cone-directed animals — no peel, no
annihilator. `convex_growth.py` on `results/mk_hvdir4asc_terms_n700.txt` prints
it stably to the twelve digits the diagnostic carries at every `n` in 695..699;
as `λ_2/λ_1` from that series' spectrum it is
`0.48100879370959321158558…`, trusted to 76 digits. (The same run trusts that
series' `µ` to 200 digits, against 51 for the unsplit 4-cone series — deleting
the descending half stops the 2.5146 from polluting the extrapolation, which is
a free by-product of the split.) So the two series do **not** have different
subdominant behaviour with the 4-cone one lacking `0.4810`; the restricted
series has an extra exponential in front of the shared one, and the
`d_n/d_(n−1)` diagnostic reports only the largest correction present. That the
extra one is `ν` is Proposition 7 at the level of rates and Conjecture 8 at the
level Table B measures.

It remains true that this rules the bijection out, and now for a reason that is
proved rather than inferred: a bijection would have to account for a half of one
side, growing at 2.5146, that has no counterpart on the other.

### Phase 1's two digit claims, checked

Both reproduce exactly, and both are floors rather than measurements of the
coincidence:

- **"153 trusted digits"** for the block's growth constant is what
  `convex_growth.py results/mk_dir4_descblock_n700.txt --prec 400` prints, and
  it prints it again. The bound is set by that tool's Aitken-vs-Richardson
  cross-check, which is the wrong comparison when the correction is geometric
  (its own `--trust` docstring says so). Prony on the same 700 terms trusts
  **242** digits.
- **"matched to 193 digits"** is what `dir4_descent_block.py --compare` prints,
  and it prints it again. It is a raw agreement between two Aitken
  extrapolations with no trusted-digit floor attached. Measured independently
  here: the two numbers agree to 236 digits and the weaker of them is trusted to
  **217**, so the claim holds with 24 digits to spare.

A 193- or 217-digit agreement is not a proof and does not become one. Two
extrapolations of the same shape could in principle share a bias — which is why
the identification is now carried by the phase split, where the 2.5146 is the
measured growth rate of a series that is counted, not extrapolated, and by
Proposition 7, where it is proved.

## The amplitude ratio is a ratio of two explicit feed vectors (2026-08-06)

Phase 1 left the ratio as "a ratio of residues of the same staircase resolvent
against two different feed vectors … but not what it equals". The feed vectors
can be written down. Once they are, the ratio is an explicit convergent
expression whose digits cost milliseconds instead of a 700-term enumeration.

### The measurement, re-taken on the split series

Table B's binding constraint was a convergence rate, not a series length.
`D(n)/A(n)` approaches its limit at `(ν/µ)^n = 0.8037^n`, which at `n = 700` is
`1e-66`. The split removes exactly that: `D_asc` and the unrestricted series
share `ρ = 0.4810` as their own subdominant ratio (the corrected reading
above), so `D_asc(n)/A(n)` approaches the **same** limit at `ρ^n`, `1e-222` at
`n = 700`. Same script, same discipline as Table B — raw and Aitken, `n = 600`
against `n = 700`, minus a 2-digit guard (`experiments/ratio_amplitude.py`):

| numerator, over `convex_area_terms_n700_king` | raw | Aitken | TRUSTED |
|---|---|---|---|
| `D` = hvdir4 — Table B's own | 56 | 239 | **54** |
| `D_asc` = hvdir4asc | 187 | 253 | **185** |

The first row reproduces Table B's 54 digits and its decimal string character
for character, so it doubles as the control on the method: the 185 is bought by
the split and by nothing else.

**The two rows must have the same limit, and that is proved rather than
observed.** `D = D_asc + D_desc` with `lim D_desc(n)^(1/n) = ν < µ`
(Proposition 7), so the descending half contributes nothing at order `µ^n` and
both quotients converge to `C(D_asc)/C_HV`. Table B measured this number
through a slower-converging window.

### Proposition 9 (the mirror halves) — the factor 1/2

Partition the HV-convex animals by which middle phase their path visits; the
two bits are monotone in `j`, so no path visits both `(1,0)` and `(0,1)` and the
three parts are a partition. Then **`A_(1,0)(n) = A_(0,1)(n)` for every `n`**,
and the remainder, the paths `(0,0) → (1,1)`, is sub-exponential. Hence if
`C_HV = lim A(n)/µ^n` exists, `C_HV = 2 C(A_(1,0))`.

(The mirror equality of the two middle blocks is Gouyou-Beauchamps & Leroux's
`H02 = Pa = H20` in the convex-polyomino setting — see the attribution note
under Lemma 1. The factor 1/2 and the sub-exponential remainder are what this
proposition adds here.)

*Proof.* The vertical mirror `[b(j), t(j)] ↦ [−t(j), −b(j)]` is an
area-preserving involution of the class that leaves every column height alone.
It carries `d(j) = b(j+1) − b(j)` to `−(t(j+1) − t(j))`, so "`b` has risen"
becomes "`t` has fallen": the phase bits swap, `(pb, pt) ↦ (pt, pb)`. Phases
`(0,0)` and `(1,1)` are fixed and `(1,0) ↔ (0,1)`, so the involution is a
bijection between the first two parts. The remainder factors as a phase-`(0,0)`
block joined to a phase-`(1,1)` block at one step, both stacks by Lemma 2, so it
is at most `(n+1)^2 E(n)^2`, which is `µ^{o(n)}` by Lemma 2. ∎

Brute-forced (`experiments/descent_block_oracle.py --mirror 14`, an independent
DFS over explicit column intervals):

| n | 1 | 2 | 3 | 4 | 5 | … | 13 | 14 |
|---|---|---|---|---|---|---|---|---|
| HV-convex | 1 | 4 | 16 | 61 | 221 | … | 2677214 | 8389720 |
| via `(1,0)` | 0 | 1 | 6 | 26 | 100 | … | 1333383 | 4184875 |
| via `(0,1)` | 0 | 1 | 6 | 26 | 100 | … | 1333383 | 4184875 |
| via neither | 1 | 2 | 4 | 9 | 21 | … | 10448 | 19970 |

### Proposition 10 (the staircase eigenvector is a three-term recurrence)

Let `T(x)` be the staircase block's operator, `T(x)_{h,h'} = x^{h'}(min(h,h')+1)`
for `h, h' ≥ 1`, and let `φ` solve

    φ(0) = 1,  φ(1) = 2,  φ(h) = (2 − x^{h−1}) φ(h−1) − φ(h−2)   (h ≥ 2).

For `0 < x < 1`: `T(x) φ = φ` **iff** `φ(h) − φ(h−1) → 0`; that happens at
exactly one `x = x_c`; and `x_c = 1/µ`.

*Proof.* Write `Q(h) = Σ_{h'>h} x^{h'} φ(h')`. Splitting `T(x)φ = φ` at
`h' = h` gives `φ(h) = Σ_{h'≤h} x^{h'}(h'+1)φ(h') + (h+1) Q(h)`; differencing
once gives `φ(h) − φ(h−1) = x^h φ(h) + Q(h)` (and `φ(0) = φ(1)/2` from `h = 1`),
differencing again gives the recurrence. Conversely, *define*
`Q(h) := φ(h) − φ(h−1) − x^h φ(h)` from the recurrence's solution; the second
difference makes `Q(h−1) − Q(h) = x^h φ(h)` an identity, so
`Q(h) = Q(∞) + Σ_{h'>h} x^{h'} φ(h')` and the eigenvector equation holds iff
`Q(∞) = 0`. Since `x < 1`, the recurrence's coefficient tends to 2 and its
solution space is spanned by one asymptotically constant and one asymptotically
linear solution; `Q(∞) = 0` is exactly "the linear one is absent", one analytic
condition on `x`.

At such an `x`, `φ` is positive: the differences `δ(h) = φ(h) − φ(h−1)` obey
`δ(h) = δ(h−1) − x^{h−1} φ(h−1)` with `δ(1) = 1`, so `δ` strictly decreases
while `φ > 0`, and `δ(h) → 0` forces `δ > 0` throughout — `φ` increases from 2
to `2.5374225302…`. `T(x)` is positive and compact on
`{f : |f(h)| ≤ C(1+h)}` (it acts there because
`Σ_{h'} x^{h'}(min(h,h')+1)(1+h') ≤ (h+1) Σ_{h'} x^{h'}(1+h')`), so by
Krein–Rutman a positive eigenvector's eigenvalue is the spectral radius.
`M(x) = v0(x) (I − T(x))^{−1} 1` with `v0(h) = x^h` is the staircase generating
function, of radius `1/µ`, and the spectral radius of `T(x)` increases
continuously in `x`, so it reaches 1 at `x = 1/µ`. ∎

**By-product.** Shooting on that recurrence computes `µ`
to arbitrary precision in `O(hmax)` operations, with no series and no
extrapolation. It reproduces all 199 banked digits and continues past them,
matching the `…922549000485` the staircase series reached above:

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549                 <- the banked 199
                                        000485072072     <- the shooting
```

**987 digits in 1.6 s** on one core (`--dps 1000 --hmax 2200`), against a
700-term enumeration plus Aitken for 200.

### Proposition 11 (the ratio) — conditional on the amplitudes existing

Write `U(h,h') = h'−h+1` and `U4(h,h') = min(2, h'−h+1)` for `h' ≥ h` (the
`(0,0)` block, unrestricted and 4-cone-truncated), `L(h,h') = min(h, h'+1)`
(the map `(0,0) → (1,0)`, and also `(0,0) → (0,1)` — the same matrix, which is
Proposition 9 at the operator level), each carrying `x^{h'}`, and

    w  = v0 (I − U )^{−1} L,      w4 = v0 (I − U4)^{−1} L,      evaluated at x_c.

If `C(D_asc) = lim D_asc(n)/µ^n` and `C_HV = lim A(n)/µ^n` exist, then

    r  =  C_dir4 / C_HV  =  (1/2) · (w4 · φ) / (w · φ).                    (*)

*Proof.* The phase automaton makes the path decomposition exact as generating
functions: `A_(1,0)(x) = w(x) (I − T(x))^{−1} q(x)` with
`q = 1 + L_{(1,0)→(1,1)} (I − T_{(1,1)})^{−1} 1`, and
`D_(1,0)(x) = w4(x) (I − T(x))^{−1} q(x)` with the **same** `T` and the **same**
`q` — the 4-cone floor `d ≥ −1` bites only inside the `(0,0)` block, since every
step out of `(1,0)` and every step within `(1,1)` already has `d ≥ 0`. The
`(0,0)` and `(1,1)` blocks are stacks (Lemma 2), so `w`, `w4` and `q` are finite
at `x_c`. By Proposition 10 and Krein–Rutman the pole of `(I − T(x))^{−1}` at
`x_c` is simple with rank-one residue `φ ψ^T / ⟨ψ, φ⟩`, so

    lim_{x→x_c⁻} (1 − µx) A_(1,0)(x) = N · (w · φ),
    lim_{x→x_c⁻} (1 − µx) D_(1,0)(x) = N · (w4 · φ),

with the same `N = ⟨ψ, q⟩ / (⟨ψ, φ⟩ · (−x_c Λ'(x_c)))`, which cancels. If the
amplitudes exist then `lim (1−µx) Σ a(n) x^n = C` by Abel's theorem, so those
two limits are `C(A_(1,0))` and `C(D_(1,0))`. Finally `C_HV = 2 C(A_(1,0))`
(Proposition 9) and `C_dir4 = C(D_asc) = C(D_(1,0))`, the `D_desc` and
"via neither" parts being `o(µ^n)` by Proposition 7 and Lemma 2. ∎

The hypothesis is **strictly weaker than Conjecture 8**, which asks for the
error terms as well. What (*) settles is the question Phase 1 left open — what
a closed form would have to look like. It is a ratio of two `q`-series in
`q = 1/µ`, both computed by `O(hmax)` prefix-sum recurrences
(`experiments/amplitude_feed_vectors.py`):

    w  · φ  =  1.29770192341040021939895011278…
    w4 · φ  =  1.19935960397018718067118376153…

### The number, and how the digit count was established

The 251 trusted digits, `experiments/amplitude_feed_vectors.py` (the identity
supplies more on demand — 987 at `--dps 1000 --hmax 2200`):

    0.4621090492099424400356623877003058328411634397299804247065092921445229505114
    444835410198048486182340620897552570414665332043843876381701390681440910143562
    899341315538121788620454046737283009596825392081974838100954958864643192857487
    4902351771539511812

Three determinations, each with its own internal cross-check; the third is
independent of the other two in method as well as in data:

| route | own cross-check | trusted |
|---|---|---|
| Table B, `D/A` extrapolated | raw vs Aitken, n=600 vs 700 | 54 |
| `D_asc/A` extrapolated | raw vs Aitken, n=600 vs 700 | 185 |
| identity (*) | `hmax` 1200 vs `hmax` 1000 | 492 |

The extrapolation and the identity **agree to 293 digits**, so by the
agree/bearable discipline used for the spectrum above, the bearable figure is
the weaker side's own count. Taking the Aitken-vs-Aitken agreement (253) as
that side's count gives **251 trusted digits** with a 2-digit guard; taking
Table B's stricter min-rule gives 185. Both are quoted below because the PSLQ
boxes scale with whichever is used. The two routes share no arithmetic: the
identity is derived from an exact operator factorisation, and the extrapolation
touches no operator at all.

Negative controls, all inside `experiments/amplitude_feed_vectors.py` and
pinned by `make gate-middle-kingdom`: dropping the factor 1/2 agrees with the
measurement to 0 digits; truncating the `(0,0)` block at `min(3, ·)` instead of
`min(2, ·)` agrees to 1; the `φ` recurrence at `x = 1/3.13` fails its own
eigen-equation at `1e-2` where `x_c` gives `1e-528`.

### PSLQ: the enlarged boxes, and the same verdict

A box is in-capacity while `(terms) × log10(height)` stays below half the
digits fed — the rule `results/convex-polyplets.md` adopted after a 137-digit
run manufactured a degree-6 "relation" of height `7e11`. Positive control on
every run: `(1 + √2)/3` must be found at degree 2, and is.

At **185 digits** (`results/amplitude_pslq_185.log`), against Table B's
`degree ≤ 12 at height ≤ 1e2, ≤ 5 at 1e4, ≤ 3 at 1e6, ≤ 2 at 1e8`:

    NO relation in any in-capacity box --
      degree <= 45 at height <= 1e2, <= 22 at 1e4, <= 14 at 1e6,
      <= 10 at 1e8, <= 6 at 1e12, <= 3 at 1e20, <= 2 at 1e30

At **251 digits** (`results/amplitude_pslq_251.log`):

    NO relation in any in-capacity box --
      degree <= 30 at height <= 1e4, <= 20 at 1e5, <= 10 at 1e11,
      <= 5 at 1e20, <= 3 at 1e30, <= 2 at 1e40

`2r`, the feed-vector ratio itself with the factor 1/2 removed, is excluded in
the same degree-12 / height-1e2 box.

### Algebraic over `Q(µ)`? Not in the searched box either

PSLQ on `{ µ^i r^j }` asks whether `r` satisfies a polynomial over `Q(µ)` — a
different question from the one Table B asked, and the natural one, since `µ` is
the constant both series share.

At 251 digits, no relation over `Q(µ)` in any in-capacity box:

    mu-degree <= 5, r-degree <= 6 at height <= 1e2
    mu-degree <= 4, r-degree <= 5 at height <= 1e4
    mu-degree <= 3, r-degree <= 4 at height <= 1e6
    mu-degree <= 2, r-degree <= 4 at height <= 1e8

`experiments/amplitude_pslq.py --digits 60 --field 2:3` shows what the capacity
rule is for: it returns a "relation" of height 48186, capacity 56 against the
60 digits fed, which the rule rejects.

`µ`'s own arithmetic status is what limits how much this can mean.
`results/convex-polyplets.md` excludes an integer polynomial for `µ` at degree
≤ 20 / height ≤ 1e8, ≤ 30 / 1e6 and ≤ 12 / 1e15, and there is no proof of
irrationality, let alone transcendence — so `Q(µ)` is a field of unknown degree
and "algebraic over `Q(µ)`" cannot be settled either way by any argument the
repo has. What the identity (*) contributes is a reason to expect the answer to
be no: `r` is a ratio of two `q`-series evaluated at `q = 1/µ`, and `µ` is
itself the reciprocal of the zero of an entire `q`-function (Proposition 10) —
the same shape as Kurkov's conjectured continued fraction for A225114.

### Cost of the routes not taken

- **Extending the series.** By Table B's rule the split series reaches
  `0.3179 n` trusted digits, so 300 would need `n ≈ 1050`. Measured on gympie:
  `middle_kingdom_tm hvdir4asc 1100` is **10.6 s**, but the partner series is
  the expensive one — `convex_area_tm 700 1` took **484 s / 272 MB** and its DP
  scales about `N⁴`, putting `n = 1100` near **50 minutes** on one core. Not
  run: (*) delivers 987 digits in 1.6 s, and the PSLQ sweeps are bounded by
  PSLQ's own cost, not by digits.
- **The top PSLQ boxes.** mpmath's PSLQ cost grows steeply in the degree, and
  it, not precision, is now what bounds the boxes: at 185 digits the
  degree-22 box takes 41 s and the degree-45 box 1669 s; at 251 digits the
  degree-30 box takes 303 s. A degree-120 box, which the identity's 492 digits
  would put in capacity, extrapolates to hours and was not run.

## What is still open

- **Conjecture 8 — sharp asymptotics for the two halves.** Proposition 7 proves
  the exponential rates `µ` and `ν`; what Table B's diagnostic reads is the
  second exponential of `D`, and getting there needs
  `D_asc(n) = Cµ^n(1 + O(ρ^n))` and `D_desc(n) = C'ν^n(1 + O(σ^n))`. Both are
  measured (76 and 64 trusted digits on `ρ` and `σ`) and neither is proved. The
  block-triangular resolvent is still the mechanism, but the missing ingredient
  is not the resolvent algebra — the phase split replaces that with an exact
  partition — it is that no series in this family has a proved sharp asymptotic,
  not even the dominant one. The one concrete route on the table is Kurkov's
  conjectured continued fraction for A225114, whose convergents' poles already
  reproduce the measured staircase spectrum.
- **The amplitude ratio — narrowed 2026-08-06, not closed.** The section above
  turns Phase 1's "a ratio of residues against two different feed vectors" into
  the identity `r = (1/2)(w4·φ)/(w·φ)`, with both feed vectors written down and
  `φ` the bounded solution of a three-term `q`-recurrence (Propositions 9–11).
  Three things remain undone. (i) The identity is conditional on the two
  amplitudes existing — weaker than Conjecture 8, but still unproved.
  (ii) Neither `w·φ` nor `w4·φ` has a closed form of its own; they are
  convergent `q`-series and nothing more is known about either. (iii) PSLQ
  remains negative in every box the 251 digits reach, over `Q` and over `Q(µ)`,
  and cannot become conclusive: the boxes are now bounded by PSLQ's own cost
  rather than by precision, which the identity supplies without limit.
- No proof that any of these series is non-D-finite. Staircase joins the list
  of exclusion-box negatives above.

## Novelty check

**2026-08-06, the literature sweep** (`results/novelty-sortie.md`, plan items
N1–N3). One collision, recorded above: the phase-block decomposition is
Gouyou-Beauchamps & Leroux's, for convex polyominoes, and Lemma 1, Lemma 2's
identification and Proposition 9 now carry the attribution. The rest holds:
HV-convex king animals are not in OEIS and not in the literature searched under
any name; no source states the squeeze for intermediate classes; and
Propositions 6, 7, 10 and 11 have no counterpart found. The square-lattice
version of Proposition 6's conclusion is classical, and is now marked as such
in the text.

The rest of this section predates that sweep. Grepped `results/`, `docs/`,
`papers/`, `paper/`, `oeis/` before claiming any of this new. `3.1289…` appears only against the HV-convex series and the
(dir4, HV-convex) cell; no file relates it to the staircase column, and
`results/countable-subpopulations-criterion.md` records that no GF or constant
for A225114 was banked. A225114 was re-fetched 2026-08-05
(`experiments/oeis_lookup.py --full id:A225114`, read-only): the entry is
"Number of skew partitions of n whose diagrams have no empty rows and columns",
24 terms, one comment and one formula — a conjectured continued-fraction g.f.
(Kurkov, Sep 2024). The lookup prints up to six comments and four formulas and
returned one of each, so those fields are complete as fetched, and **neither
carries an asymptotic or a growth constant**. A001523 was confirmed the same way
on twelve terms.

2026-08-06, the same way. None of `1.4304046`, `1.2484659`, `1.28433727`,
`−1.25776216` occurs anywhere in `results/`, `docs/`, `papers/` or `paper/`, and
neither does the `hvdir4asc` series. Read-only OEIS lookups: the block series is
still NO MATCH at thirteen terms as well as ten (its six-term prefix collides
with A127358, A135473 and A077849 — verified by `--full id:`, and A127358, the
last to survive, diverges at n = 9 with 2230 against 2233);
`D_asc = 1, 3, 10, 34, 115, 382, 1244, 3993, 12689, 40065` NO MATCH;
`D_desc = 1, 5, 19, 62, 185, 523, 1424, 3776, 9832, 25283` NO MATCH.

2026-08-06 (the amplitude section), the same way. None of `1.29770192`,
`1.19935960` (the two feed-vector contractions) or `2.53742253` (`φ`'s limit)
occurs anywhere in `results/`, `docs/`, `papers/`, `paper/` or `oeis/`, and
neither does the recurrence `φ(h) = (2 − x^{h−1})φ(h−1) − φ(h−2)` or any
characterisation of `µ` other than as a series extrapolation. No new A-number
is cited: A225114 and A001523 were verified above, and the amplitude work
introduces no sequence to look up — the objects it adds are real constants, not
integer sequences. Kurkov's continued fraction is quoted from the A225114 entry
fetched 2026-08-05, unchanged.

Nothing here has been sent to OEIS. If µ for A225114 is ever offered, it is
jasonp's call and gated on the viva like the rest of the campaign's staged
edits.

## Reproduce

All laptop-scale. The 2026-08-05 half is seconds; of the 2026-08-06 half the
long pole is the seven-series spectrum at order 10 and 1500 digits, 8 min on one
core.

```
make build/middle_kingdom_tm build/prec_guess
make gate-middle-kingdom                       # stair vs the grid, the sandwich,
                                               # the phase split, four RED controls
python3 experiments/staircase_supermul.py      # Lemma 3, 0.6 s, three RED controls
scripts/mk_stair_growth.sh                     # 700 terms each + mu, ~15 s total
python3 experiments/monotone_block_growth.py --nmax 400
python3 experiments/dir4_descent_block.py --nmax 700 \
        --out results/mk_dir4_descblock_n700.txt \
        --compare results/mk_hvdir4_terms_n700.txt --prec 400
python3 experiments/convex_growth.py results/mk_dir4_descblock_n700.txt --prec 400
build/prec_guess prec results/mk_stair_terms_n700.txt 24 24
build/prec_guess alg  results/mk_stair_terms_n700.txt 20 20
python3 experiments/oeis_lookup.py --full id:A225114
python3 experiments/oeis_lookup.py 1,3,8,21,54,138,350,885,2233,5626

# the split and the spectrum (2026-08-06)
python3 experiments/descent_block_oracle.py --nmax 700 --brute 13 \
        --check results/mk_dir4_descblock_n700.txt      # independent oracle
python3 experiments/descent_block_oracle.py --phases 14 # the phase split's oracle
build/middle_kingdom_tm hvdir4asc 700 > results/mk_hvdir4asc_terms_n700.txt
python3 experiments/subdominant_identification.py --order 10 --dps 1500
python3 experiments/convex_growth.py results/mk_hvdir4asc_terms_n700.txt --prec 400
python3 experiments/staircase_cf_poles.py --depth 24 --terms 40

# the amplitude ratio (2026-08-06, later)
python3 experiments/descent_block_oracle.py --mirror 14        # Proposition 9
python3 experiments/ratio_amplitude.py results/mk_hvdir4asc_terms_n700.txt \
        results/convex_area_terms_n700_king.txt --prec 700 --drop 100
python3 experiments/ratio_amplitude.py results/mk_hvdir4_terms_n700.txt \
        results/convex_area_terms_n700_king.txt --prec 700 --drop 100  # = Table B
python3 experiments/amplitude_feed_vectors.py --dps 500 --hmax 1200 \
        --emit results/amplitude_ratio_constants.txt           # Propositions 10, 11
scripts/amplitude_pslq_sweep.sh 185 results/amplitude_pslq_185.log
scripts/amplitude_pslq_sweep.sh 251 results/amplitude_pslq_251.log \
        2:1e40,3:1e30,5:1e20,10:1e11,20:1e5,30:1e4 \
        5:6:1e2,4:5:1e4,3:4:1e6,2:4:1e8
```

The amplitude work is milliseconds except the two PSLQ sweeps, which are tens
of minutes each and are the only thing here worth backgrounding. Constants:
`results/amplitude_ratio_constants.txt` (`µ` then `r`, one per line, at the
precision the run reached). Logs: `results/amplitude_feed_vectors.log`,
`results/hv_mirror_split_n14.log`, `results/amplitude_pslq_185.log`,
`results/amplitude_pslq_251.log`.

Series: `results/mk_stair_terms_n700.txt`, `results/mk_hvmono_terms_n700.txt`,
`results/mk_dir4_descblock_n700.txt`, `results/mk_hvdir4asc_terms_n700.txt`,
`results/mk_hvdir4desc_terms_n700.txt` (the difference, n = 2..700). Logs:
`results/mk_stair_growth.log`, `results/mk_hvdir4asc_n700.log`,
`results/subdominant_identification.log`.

`results/mk_hvdir4desc_terms_n700.txt` is derived, not enumerated: it is
`hvdir4 − hvdir4asc` termwise, so it inherits both series' provenance and needs
no oracle of its own beyond the identity the gate checks at n ≤ 14.
