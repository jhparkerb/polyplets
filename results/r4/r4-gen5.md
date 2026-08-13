# r4-gen5 — generator: what the partial routes compose to

Angle, per the dispatch: every lane has asked "what single route confirms a band
cell?" Nobody has asked what the answers *combine* to. Three directions —
arithmetic composition, epistemic composition, correlated-failure composition —
and a second pass on what my own rows share.

Everything below is desk work on files already in the repo. No compute was run
anywhere. Numbers labelled MEASURED were computed here from
`results/triangle.txt` or read out of a committed file; everything else is
labelled.

---

## §0 The substrate, measured, because every composition argument needs it

Row 40 of `results/triangle.txt`, recomputed here (`a(40)` = 106 bits =
56749893611764175164545926946127):

| heights | share of a(40) | what stands behind it today |
|---|---|---|
| 1–14 | **45.0107%** | incumbent kink sweep + strip TM (`results/strip-engine.md`: 469 cells, 0 mismatch, N=40 run 2026-07-30) + B1's `C1..C14` rows — **three** sources |
| 15–16 | **21.6439%** | incumbent + B1 exact (`results/cutcount_b1/`, `bd31a58`) |
| 17–19 | **22.1993%** | incumbent alone; the B1 residue ladder is planned (R4-L1) |
| 20–21 | **7.0013%** | incumbent alone; spin parity planned (R4-SPINPROJ-JOB-1), diagonal law reaches H=21 only (R4-G1) |
| 22–40 | **4.1449%** | **never counted** — evaluated from wired `P_k` closed forms (R4-G3-09) |

Individual band cells, bit lengths: T(40,17) 103, T(40,18) 102, T(40,19) 102,
T(40,20) 101, T(40,21) 101. Cumulatives: Σ_{H≤19} = 88.8538%, Σ_{H≤21} =
95.8551% (this is the 95.85% the Lean route quotes).

One correction to the tiering that the campaign's prose blurs, and it is
load-bearing for §2. The strip TM caches **connectivity partitions**
(`strip-engine.md`, "distinct connectivity partitions cached"), so it is a
second *connectivity* DP. Against the chartered objection — that the
connectivity decision in the production kernels may be wrong — the strip
confirmation of 45.01% buys a second implementation, not a second rule class.
By mass, the chartered objection is answered for **21.64% of row 40 and no
more**. `r4-adv-ind.md` §7 says this for the two cells; nobody has said it for
the row.

---

## §1 Direction 1 — arithmetic composition

### 1.1 R4-G5-01 — CLOSED WITH THE ARITHMETIC: the row-sum subtraction closes exactly zero cells, and the vacuity does not shrink as more cells are confirmed

This is the obvious composition and the dispatch named it first. It is worth
exactly nothing, and the proof is two lines, so it should be banked rather than
re-proposed each round.

Let the incumbent produce `t_1..t_40` at n = 40. The project's `a(40)` is
**defined** as their sum: R4-G3-01 established off disk that
`POLYCKPT.A + B + C == combine.log`'s a(n) with `A = Σ perheight/h{1..19,22..40}`,
`B = h20`, `C = h21`. There is no other a(40) anywhere in the repo.

Now suppose routes independent of the incumbent confirm `t_H` for every
`H ∈ S`, and someone proposes to obtain `t_{H'}`, `H' ∉ S`, as
`a(40) − Σ_{H ∈ S} t_H − Σ_{H ∉ S ∪ {H'}} t_H`. Substituting the definition of
a(40) gives `t_{H'} = t_{H'}`. The statement is an identity for **every** S,
including `|S| = 39`. Confirming more cells does not make the last one any less
free-by-construction; the argument is equally vacuous at S = ∅ and at S = all
but one.

**The exact condition under which it acquires content:** there must exist one
route to a(40), or to any partial sum, whose derivation does not pass through
the per-height values being subtracted. R4-G17 already noted there is no
height-blind route to a(40) (Redelmeier is Θ(a(40)) = 5.7e31 objects). I add
the two consequences it did not draw:

1. **This is permanent, not pending.** Any future row of the form "N−1 cells
   confirmed, therefore the Nth" is dead on arrival unless it names the
   height-blind total in the same sentence. File this row's id and stop.
2. **It is exactly why the 4.1449% injected tail is the campaign's most
   invisible error class** — see R4-G5-19. The tail enters a(40) additively and
   is checked by nothing, and the row sum, being an identity, cannot see it.

There is one non-vacuous survivor and it is not a route: partial sums computed
by a route that produces a **cumulative directly** rather than as a sum of
attributed heights. B1 is that route (it emits `C_H`), and the composition it
enables is R4-G5-11.

### 1.2 R4-G5-02 — CLOSED WITH THE ARITHMETIC: the campaign's cheap instruments compose to under 5 bits against a 100-bit cell

"Residue plus a tight interval" is the other composition the dispatch named. An
integer X is pinned by a residue mod M plus an interval of width w iff w ≤ M.
Ledger for T(40,21) = 101 bits (the cheapest cell to attack this way):

| instrument | bits it contributes | notes |
|---|---|---|
| Klein forced parity | **0** | the theorem is `n odd, H even` (`triangle-hunt-klein-parity.md:12`); n = 40 is even. The file says so itself: "nothing to a(40)" |
| spin parity (INV-8) | 1 | a measurement, not a theorem, at n = 40 |
| r2 tower mod 3^m at H=21 | ≤ 3.17 | mod 9, per R4-G15; deeper depth is priced but unrun |
| ternary spine | ≤ 1.58 | NOT ESTABLISHED that it applies at row 40 |
| rigorous external bracket | ≤ 2.8 | R4-G3-21 CLOSED: supermultiplicativity 0.1442×a(40), Fekete 1.03e7×a(40) — and it brackets the **total**, not a cell |
| series extrapolation of r(n) | 13.3 | R4-G3-22, ~1e-4 relative — also on the **total**, and see R4-G5-04 |

The three cell-level instruments compose to modulus 2 × 9 = 18, i.e. **4.17
bits, against 101 needed. The shortfall is a factor of 2^96.8.** Adding a
31-bit prime leaves 65.9 bits.

The interval half is worse than it looks. An interval of relative precision ε
saves `log2(1/ε)` bits, and a 31-bit prime is 31 bits, so an interval must reach
**ε ≈ 4.7e-10 relative** to save a single prime run. The best instrument the
campaign has is 1e-4 (R4-G3-22, and that is on a(40), not on a cell), which
saves 0.43 of a prime — nothing.

**Kill, stated so the family closes together:** there is no assembly of this
campaign's non-computational instruments that pins any band cell, and the gap
is not close enough for any plausible new cheap instrument to change it. Cheap
bits are worth what they are worth **as detectors** — 4.17 bits is a 1-in-18
chance of missing a random error — and their value is only nonzero on cells
where no exact route exists, i.e. H = 20 and 21. On H = 17..19 they compose
with the ladder to nothing, because 2^-62 already dominates them.

### 1.3 R4-G5-03 — CLOSED WITH THE ARGUMENT: CRT across rule classes is strictly worse than mod-wise cross-checking, for a confirmation mission

The dispatch's "CRT across rule classes rather than across primes" is a real
idea and it inverts. To *reconstruct* X from residues supplied by routes
A, B, C you must trust all three; a single wrong contributor produces a
confident wrong X with no signal. To *cross-check*, you take each route's
residue against the banked value separately; a wrong contributor produces a
mismatch, and you trust nobody.

Reconstruction is only preferable when the banked value does not exist. It
does. So for every cell in the band, the same residues bought mod-wise are
worth strictly more than the same residues bought as CRT inputs, at identical
cost. R4-G14 and R4-L1 reached this for the *prime* ladder as a budget
argument ("confirm, don't reconstruct"). The generalisation is the content:
**it holds for every future route, and it means no route ever needs to bring
a full 106-bit modulus to the table.** A route contributing 1 bit at H = 20 is
not "1/101 of a cell"; it is a detector with power 1/2, and it should be
ranked that way.

### 1.4 R4-G5-04 — re-scope R4-G3-22: series extrapolation composes with nothing, and that raises rather than lowers its value

R4-G3-22's ratio fit predicts r(40) = a(40)/a(39) to ~1e-4. Per R4-G5-01 it
cannot be composed into a cell, and per R4-G5-02 its 13.3 bits cannot be spent
against one. So it is not an ingredient of anything.

What it is: **the only instrument in the campaign that sees the 4.1449%
injected tail.** The tail enters a(40) additively; a wrong tail moves a(40)
and therefore moves r(40); a 1e-4-sensitive fit against a tail that is 4.14% of
the row would catch a tail error down to ~0.25% of the tail. Nothing else in
the campaign looks at that region at all (§0). R4-G3-22 justified itself as a
fractional-percent detector on the total; the sharper justification is that it
is the **only** detector pointed at the one block that was never counted.
Prior it fires: 0.03. Prior worth its minutes: 1.0.

### 1.5 R4-G5-05 — FLAGSHIP: the bounding-box table is symmetric in (height, width) and this campaign has never used it

Let `N(n,H,W)` be the number of fixed polyplets of size n whose bounding box is
exactly H × W. King adjacency is invariant under the dihedral group of the
square lattice, so transposition is a bijection on polyplets and

> **N(n,H,W) = N(n,W,H) for all n, H, W.**

A theorem, one line, level 1 by construction. It is not an accounting
rearrangement in the sense R4-G3-23 killed for Burnside, because the two sides
are computed by **different runs of the sweep**: the production engine fixes H
as the frontier height parameter and enforces it with touch-top/touch-bottom
flags in the state key (`orchestrator/runref.go:42`), while W is the column
index the sweep is counting off. Height and width are decided by mechanisms
with nothing in common. Transpose symmetry therefore tests one against the
other.

The convenient form, because it needs no per-width payload:

> **M(h,w) := #{polyplets, n = 40, H ≤ h, W ≤ w} satisfies M(h,w) = M(w,h).**

`M(h,w)` is what every engine in the campaign already computes, with one
change: cap the column count at `w` instead of 41. B1 already parameterises the
column count (`cutcount_b1.cpp:17-20`, "sweep W = Nmax+1 columns"), so on that
engine this is a loop bound, not a redesign.

Prior the symmetry holds: 1.0 (it is a theorem). Prior the campaign can
actually evaluate `M(h,w)` off-diagonal at useful (h,w): 0.6. **Cheapest kill:
build the full joint table `N(n,H,W)` by brute force at n ≤ 12 and confirm the
symmetry and the identity `T(n,H) = Σ_W N(n,H,W)` — minutes, laptop-scale, and
it is the same grower `probe_cutcount_dp.py` already has.** If the engines turn
out not to admit a column cap the row degrades to R4-G5-06's check only.

### 1.6 R4-G5-06 — the transpose identity is the missing instrument for R4-G3-06, which is ranked the highest residual risk in the campaign

R4-G3-06, rank 1 of r4-gen3's list: *"nothing anywhere tests which height a
swept animal was attributed to"*, and it explicitly establishes that the B1
ladder cannot test it either, because a swap between H = 17 and H = 18 cancels
inside a cumulative. Its stated conclusion is that only a future sweep emitting
per-height data can touch it.

`M(h,w) = M(w,h)` touches it with runs at heights we can already afford. Take
`h = 14`, `w = 19`:

> `M(14,19)` = size-40 polyplets in a 14-row, 19-column box — a **strip-range**
> computation (H ≤ 14 is the strip TM's verified region), 19 columns.
> `M(19,14)` = size-40 polyplets in a 19-row, 14-column box — a computation at
> heights **15..19**, the unconfirmed block, over only 14 columns.

The two must be equal. A misattribution between H = 17 and H = 18 does not
cancel here, because the right-hand side is one number over the whole
height range while the left-hand side is computed at heights that never touch
15..19 at all. More usefully, sliding `h` over 14..19 with `w` fixed gives a
telescoping family whose differences isolate individual heights against
column-capped strip-range runs.

Honest limits, up front. (i) This is a check, not a route — it produces no new
cell value. (ii) It is blind to any error that commutes with transposition; the
king stencil is D4-symmetric, so a stencil misconception passes it perfectly
(R4-G5-21 — my own flagship inherits the campaign's top common mode). (iii)
The cost of the right-hand side is unmeasured: a 19-row, 14-column sweep at
n = 40 is not a banked configuration. **Cheapest kill: `--states 19 40 41` with
a 14-column cap against the uncapped run, on the existing instrumented probe
R4-A2/R4-L3 already require — if the reachable state count barely falls, the
capped runs cost what the uncapped ones cost and the check is unaffordable at
h = 19.** Prior the check is affordable at h ≤ 17: 0.6; at h = 19: 0.35.

### 1.7 R4-G5-07 — column-capped runs put most of T(40,20) and T(40,21) inside the affordable height range, and this is the only route filed against H=20 since R4-G3 closed the diagonal law there

Decompose by transposition rather than by height:

> `T(40,21) = Σ_W N(40,21,W) = Σ_W N(40,W,21)`

Every term of the right-hand sum is a **height-W** quantity over a **21-column**
box. Terms with W ≤ 14 are strip-range; W = 15,16 are B1-exact range;
W = 17,18,19 are exactly the ladder's heights. Same for T(40,20) with a
22-column box. So:

> `T(40,21) = [ Σ_{W ≤ 19} N(40,W,21), all from height-≤19 runs capped at 21
> columns ] + [ Σ_{W ≥ 20} N(40,21,W) ]`

and the second bracket is contained in the **corner** `min(H,W) ≥ 20` (R4-G5-08).
`N(40,W,21)` is a difference of two capped runs (`≤21 columns` minus `≤20
columns`) at height exactly W, which the engines already produce as a second
difference in H; the width difference is the same manoeuvre in the other index.

Why this matters more than its prior: **H = 20 currently has no route at all.**
R4-G3 closed the diagonal law at H = 20 permanently (onset n ≥ 41; n = 40 is
the point where sharpness is verified to fail). R4-G1 reaches H = 21 only. The
ladder is priced out. Spin gives one bit. This row is the first proposal since
that closure that reaches the H = 20 cell by anything other than running the
H = 20 census.

Honest caveats, because this is the row I most want attacked. (i) The corner
term is not bounded by this argument and may be the whole difficulty —
R4-G5-08 is the measurement that decides it. (ii) A 21-column cap does **not**
obviously shrink peak RAM: R4-G2-6 MEASURED that at Nmax = 40 the reachable
state space saturates to the full window census at H ≤ 16, so the naive hope
that "40 cells cannot fill 19×21" reduces the table is contradicted by the one
measurement we have — see R4-G5-09 for the part of that measurement that does
not transfer. (iii) It needs the sum over *all* W ≤ 19 at a 21-column cap, so
it is ~19 capped runs, not one; the ladder's heights dominate the bill and the
capped versions are the only ones that could be cheaper than the uncapped ones.
Prior the decomposition is correct: 0.97 (it is arithmetic on a theorem).
Prior it delivers a usable value for either cell: **0.2**. Prior it is the
cheapest instrument that touches H = 20 at all: 0.7.

### 1.8 R4-G5-08 — the true residual of the mission is the corner `min(H,W) ≥ 20`, and its size is a cheap measurement nobody has made

Reorganise row 40 by the joint table instead of by height. Every cell with
`min(H,W) ≤ 19` is reachable from a height-≤19 run with a column cap
(R4-G5-07, using symmetry for the H ≥ 20, W ≤ 19 half). What is left is the
corner `H ≥ 20 and W ≥ 20`: polyplets of 40 cells spanning at least 20 rows and
at least 20 columns.

That set is an upper-bounded 11.15% of a(40) (= the 7.0013% at H = 20,21 plus
the 4.1449% tail, intersected with W ≥ 20), and its real size is unknown. It is
a strongly constrained family — under king adjacency the minimum cell count to
span an H × W box is `max(H,W)`, not `H+W−1` (R4-G5-20), so at n = 40 with both
extents ≥ 20 the surplus is at most 20 and these are long thin objects.

**Cheapest kill, and it is genuinely cheap: build `N(n,H,W)` by brute force for
n ≤ 12 and by the existing engines wherever a joint table can be extracted, and
plot the corner's share of `T(n,Hmax)` as a function of n.** If the corner
holds most of T(40,21)'s mass, R4-G5-07 is decorative and this row closes it.
If it holds a few percent, the two written-off cells are 95%-reachable from
heights ≤ 19 and the round's cost table is wrong about which cells are hard.
Prior the corner is under 20% of T(40,21): **0.5, and I would not bet either
way** — a height-21, 40-cell animal averages 1.9 cells per row, which argues
for small widths, but nothing stops it wandering. This is exactly the kind of
number that should be measured rather than argued.

### 1.9 R4-G5-09 — R4-G2-6's saturation measurement does not transfer to capped sweeps, and the capped regime is where R4-G4's prune was always going to bite

R4-G2-6 CLOSED "the window census is a model" by MEASURING `maxstates` equal to
ADV-I4's closed form exactly at H = 12..16 — the state space saturates. Its own
rider (i) says the identity holds at Nmax = 40 only. The rider that was not
written is the one that matters here: **saturation was measured with 41 columns
available, which is the configuration in which the "cells to complete" half of
R4-G4's mincost is weakest.** Under a `w`-column cap, a state at column `c` must
complete within `w − c` columns, and the completion budget is explicit and
small.

So the capped sweep is the regime where R4-G4's prune stops being speculative,
and R4-G4's stated methodological trap (measure the trend in H, not one cheap
height) acquires a second axis: measure the trend in the *cap*. Concretely, the
prune's survivor fraction should be reported as a surface over (H, w), and the
one number the whole of R4-G5-07 turns on is the survivor fraction at
(H = 19, w = 21). Prior the capped survivor fraction at (19,21) is under 1/4:
0.45. **Cheapest kill: the same closed-form mincost census R4-G4 already
specifies, with a remaining-columns term added — an afternoon, no run.**

### 1.10 R4-G5-10 — the one exact challenger-vs-challenger meet available today, and it is free

B1's `results/cutcount_b1/rows/C14.out` and the strip TM's per-height rows at
H ≤ 14 both cover n ≤ 40. Every committed compare in the campaign is
challenger-vs-incumbent (`tests/gate_cutcount_b1.py` compares B1 to
`results/ns_a40/perheight`). Nobody has compared the two challengers to each
other.

What it buys, honestly, is small: both are connectivity-agnostic *of each
other* but the strip TM does decide connectivity (§0), so this is not a new rule
class; and B1 and the strip share the second-difference extent layer outright
(`r4-adv-ind.md` §2.1). What it does break is a **plumbing** common mode: both
banked comparisons run through the same incumbent artifact and the same compare
script family. Cost: a join of two files already on disk. Prior it disagrees:
0.01. Prior worth the ten minutes: 0.8.

### 1.11 R4-G5-11 — the composite over H=15..19 is a block statement, and the block is immune to exactly the error the per-height claims are exposed to

The ladder produces `C_17, C_18, C_19` mod p; the strip TM produces per-height
rows to H = 14 exactly; B1 produces `C_14, C_15, C_16` exactly. Compose:

- `C_19 − C_14` two-sources the **block** `Σ_{h=15}^{19} T(40,h)` = **33.8432%
  of a(40)** as one number, at whatever soundness the ladder's primes buy.
- The *split* of that block into five heights is two-sourced only for h = 15,16
  (via B1's own `C_14, C_15, C_16`), and is not tested at all for h = 17,18,19
  — R4-G3-06's finding, arriving from the composition side.

So the joint statement over the block and the joint statement over its cells are
different claims with different strengths, and the campaign's ledger has one
column for both. The block statement is **insensitive to inter-height
misattribution**, which is the highest-ranked residual risk on file; the cell
statements are not. Report both. This is R4-G17(i) generalised from the ladder's
three heights to the full 15..19 block by bringing the strip's `C_14` in, and
the generalisation is where the 33.84% comes from.

### 1.12 R4-G5-12 — the 4.1449% that was never counted is where the diagonal-law rows pay best, and it is the cheapest way to change the row's worst clause

R4-G1/R4-G9/R4-G20 are scored in the queue against T(40,21) (2.8431%) and
against discharging the standing hypothesis on lower rows. The composition
nobody made: ab initio `(a_k, b_k)` also cover **H = 22..40 at n = 40**, which
is the 4.1449% that no sweep ever touched and that is currently
formula-conditional on constants pinned from the same table (R4-G3-09). Those
heights are `k = n − H ≤ 18`, i.e. **exactly the levels R4-G20 says are cheaper
per level than k = 19**.

Against the joint sentence in §2, this is the highest-leverage clause change
available from the diagonal-law family: it converts "4.1449% was never counted
and rests on constants fitted to this table" into "4.1449% is derived from a
proved shape with ab initio constants". Prior it lands at all: inherits
R4-G1's 0.15 for k = 19 but is **higher for k ≤ 18** because the surplus is
smaller — call it 0.4 that the bottom-up program reaches k = 14 or so, and the
census kill (R4-G1's) is the same one run bottom-up.

### 1.13 R4-G5-25 — the engine already computes the width-capped object, and an exact, connectivity-free piece of T(40,21) is available on the existing H≤16 binary

I wrote §1.5–§1.9 expecting the column cap to be a design change. It is not.
Read off `results/cutcount_b1/cutcount_b1.cpp.59e90660`:

- line 18: "sweep **W = Nmax+1 columns**; `C_H(n) = f_W(n) − f_{W−1}(n)` fixes
  horizontal translation (leftmost column = 0) and counts vertical placements,
  then `T(n,H) = C_H − 2C_{H−1} + C_{H−2}`";
- line 27: `--states <Hmin> <Hmax> <Ncols>` — the column count is **already a
  command-line parameter** in the census mode;
- line 213: `int W = Nmax + 1;` — in the production mode it is one constant;
- line 281: `bW = binom_rows(H*W), bW1 = binom_rows(H*(W−1))` — W is threaded
  through the accounting, so changing it is a parameter change and not a hack.

Write `f^h_w(n)` for what the engine sums: size-`n` animals in an `h × w`
window, counted with both placements. Then
`f^h_w = Σ_{η,ω} (h−η+1)(w−ω+1) N(n,η,ω)`, the engine's first difference in `w`
fixes horizontal translation and its second difference in `h` picks the exact
height, leaving

> `D(h,w) := Σ_{ω ≤ w} N(40,h,ω)` — height exactly `h`, width at most `w`.

`D(h, 41)` is the banked `T(40,h)`. Nothing else about the engine changes. Set
`M(h,w) = Σ_{η ≤ h} D(η,w)`; transpose symmetry (R4-G5-05) gives `M(h,w) =
M(w,h)`, and differencing in the first index:

> **`D(21,w) = M(w,21) − M(w,20) = Σ_{η ≤ w} [ D(η,21) − D(η,20) ]`.**

Take `w = 16`. The right-hand side is sixteen differences of quantities the
**existing, gated, exact** B1 binary produces at heights 1..16 — inside the
`H > 16` refusal at lines 377/381, inside the range validated by the 640-cell
compare — run twice, at column caps 21 and 20 instead of 41.

> **#{n = 40 polyplets of height exactly 21 and width at most 16} is exactly
> computable today, by a rule that never decides connectivity, at H ≤ 16 cost.**

It is a *piece* of T(40,21), the cell the campaign has no route to. The two
capped runs are strictly cheaper than the 41-column H = 16 run already banked
(21/41 of the sweep, and the feasibility prune of R4-G5-09 on top), so this is
hours on dalby, not days, and it needs no new rule, no new engine, no RAM
lever and no H > 16 anything.

What it does not do: bound how much of T(40,21) it covers. That is R4-G5-08's
measurement and it is now cheap to take *from the same runs* — `D(21,16)` as a
fraction of the banked `T(40,21)` is the corner question answered directly at
the real n and the real height, not extrapolated from small n. **This is the
cheapest kill and the deliverable at once, which is why it is the row I would
run first.** Prior the identity is right: 0.9 (it is algebra on the engine's
own stated accounting, and I have not run it). Prior the runs are affordable:
0.85. Prior `D(21,16)` is above 10% of T(40,21): 0.5.

RED that must ride with it, because the whole thing turns on the cap being
honest: run heights 1..16 at cap 41 and confirm the output reproduces the
banked `C15/C16` rows bit-for-bit, and run at a cap of 41 vs 44 and confirm
`D(h,w)` is unchanged past the point where no animal can be wider (width ≤ n).

### 1.14 R4-G5-26 — the ladder heights, run with a column cap, deliver pieces of the two cells the ladder does not reach

Continue R4-G5-25 upward. `D(21,w)` for `w = 17,18,19` needs `D(η,21)` and
`D(η,20)` at heights `η = 17,18,19` — the ladder's own heights, with a
21-column cap rather than 41. Likewise `D(20,w)` for the other cell, with a
22-column cap. So:

> Every capped run at a ladder height contributes an exact (or, at a prime, a
> congruence-confirmed) slice of **T(40,20) and T(40,21)** — the two cells the
> ladder was never able to reach — as a by-product of a run at a height it can
> afford.

The width slices accumulate: after heights ≤ 19 are done at caps 20/21/22, what
remains of the two cells is exactly the corner `min(H,W) ≥ 20` (R4-G5-08). The
ladder's brief currently prices H = 17..19 as three cells' worth of coverage
(22.20%); on this reading the same runs, re-parameterised, also chip at the
7.00% that nothing else touches.

Honest caveats. (i) The capped runs are additional runs, not free riders — cap
21 and cap 20 are two more sweeps per height, so the ladder's bill roughly
doubles for the heights where this is wanted, offset by each capped sweep being
about half the columns. (ii) Everything here inherits R4-G5-09's unmeasured
survivor fraction. (iii) Nothing here reaches heights 20 and 21 themselves, so
the corner survives and the mission's residual is genuinely the corner and not
the two cells. Prior the by-product is worth the extra runs: **0.4**, and it
should be decided by `D(21,16)`'s measured share from R4-G5-25 before anyone
budgets a capped ladder.

---

## §2 Direction 2 — epistemic composition, stated precisely

### 2.1 R4-G5-13 — the joint statement over row 40, written out

The campaign keeps flattening exact-two-source, modular-confirmation-only, and
single-source-with-proved-rule into one sentence. Here is the joint statement,
with the states kept apart, as of tonight plus everything currently planned
landing green. It is written to be handed to a referee verbatim.

> For n = 40, the height decomposition of a(40) stands as follows. 45.01%
> (heights 1–14) is exact and reproduced by a second engine of different design
> and a third that never decides connectivity — but the second engine is itself
> a connectivity DP, so against the connectivity objection this tier is
> two-sourced, not three. 21.64% (heights 15–16) is exact and reproduced by a
> rule that never decides connectivity and that obtains bounding-box height by a
> mechanism sharing nothing with the production engine's; this is the only part
> of the row where the chartered objection is answered. 22.20% (heights 17–19)
> rests on one engine; the planned ladder does not recompute it but bounds the
> probability that a congruence check would have missed an error at 2^−62.
> 7.00% (heights 20–21) rests on one engine, with a planned one-bit-per-cell
> parity cross-check by a route that shares the production engine's adjacency
> stencil and shares its extent accounting with the other challenger. 4.14%
> (heights 22–40) was never counted: it is evaluated from closed forms whose
> constants are pinned from lower rows of the same table. Every route named here
> shares one hand-written king-adjacency stencil, and no committed check on any
> built binary compares that stencil to an incumbent-free definition. Finally,
> these percentages are computed from the values under examination, so the
> unconfirmed share bounds the number of doubted cells and not the magnitude of
> a possible error.

Three things become visible only when it is written as one paragraph, and each
is a row below: the connectivity tiering (R4-G5-14), the stencil clause
attaching to 100% rather than to a tier (R4-G5-15), and the last sentence
(R4-G5-16).

### 2.2 R4-G5-14 — the ledger needs two columns, because "recomputed exactly" and "confirmed to 2^−62" are different predicates and the round is about to merge them

R4-G14 and R4-L1 correctly re-priced the ladder from reconstruction to
confirmation. The consequence for the ledger has not been drawn: after the
ladder lands green, 22.20% of row 40 will be reported in the same column as the
21.64% that was recomputed, and the two are not the same claim. A referee can
accept "reproduced by a second rule" without further argument; "confirmed to
2^−62" additionally requires them to accept that our errors are not divisible
by our primes, which is a model of the adversary (R4-G2-7's point, and it is
still open).

Proposal, and it costs a table header: **`share exact-two-source` and `share
congruence-confirmed (soundness, #primes)` as separate columns, never summed.**
This is the concrete form of R4-G21's "adopt a second ranking column" and of
R4-G3-25's third column, at the reporting layer rather than the triage layer.
Prior jasonp wants it: 0.7. Prior it changes a dispatch decision: 0.15 — the
value is that the round cannot accidentally publish a sum.

### 2.3 R4-G5-15 — the single cheap addition that most improves the joint statement is the stencil closure, and it is not a band cell

Score each clause of §2.1 by the share of row 40 it qualifies, and against the
cost of removing it:

| clause | share it qualifies | cheapest thing that removes it |
|---|---|---|
| "every route shares one hand-written king-adjacency stencil, unchecked against an incumbent-free definition" | **100.00%** | R4-G2-19's programmatic `gather()` check (seconds) + R4-G2-18's stencil enumeration + JOB-IND-1 as re-scoped by R4-G2-20 — hours, laptop-scale |
| "4.14% was never counted" | 4.14% | one grep (R4-G3-09) to establish whether the diag tests pin at n=40, plus a free integrality check via the v5 law |
| "22.20% rests on one engine" | 22.20% | the ladder: ≥30 h of dalby, and it downgrades the clause rather than removing it |
| "7.00% rests on one engine" | 7.00% | spin: hours, and it downgrades to "plus one bit" |
| "these percentages bound cells, not magnitude" | 100.00% | nothing cheap; see R4-G5-16 |

The dispatch guessed the answer is not the most expensive cell, and the
arithmetic agrees more strongly than I expected: **the stencil clause qualifies
5× more of row 40 than the entire H = 17..19 ladder, and the three instruments
that would close it cost hours against the ladder's days.** Every one of them is
already filed by somebody else (R4-G2-18, R4-G2-19, R4-G2-20, R4-AI1). What is
new here is the ranking argument — the campaign has been ranking by share of
a(40) *reached*, and by share of a(40) whose caveats get *removed* the order
inverts completely.

Second on that ranking is the 4.14% grep, which costs one command.

### 2.4 R4-G5-16 — the unconfirmed share is not an error bound, and the campaign's headline number invites the reader to think it is

"66.65% of a(40) is two-sourced" is true and says nothing about how wrong a(40)
could be. The confirmed cells are confirmed; the unconfirmed cells' *magnitudes*
are known only from the source under examination. If heights 17–19 were
undercounts — a whole class of animal missed by the frontier's completion
predicate, say — the true a(40) is larger by an amount the ledger cannot bound,
because the ledger's denominator is itself the suspect number. The error is
bounded below by nothing and above by nothing; only overcounts are bounded, and
then only by the share.

This asymmetry is worth one sentence in any writeup and it is the sentence that
distinguishes a coverage ledger from a confidence interval. It also re-ranks the
instruments: R4-G3-22's ratio extrapolation is the **only** thing in the
campaign that constrains a(40) from outside its own decomposition at
fractional-percent resolution, which is R4-G5-04's point arriving from the
epistemic side. Prior a referee raises this: 0.4. Cost of the fix: one sentence.

---

## §3 Direction 3 — correlated-failure composition, ranked

The question the dispatch asked, and it is the right one: independent routes are
worth their independence only if their errors are uncorrelated. `r4-adv-ind.md`
established three shared layers (one identity behind spin and B1; the second
difference among the challengers; the hand-written stencil in both). **So what
passes the composite?**

Rank is `P(error exists) × P(it survives everything currently on the board)`.
Impact is tracked separately because the two do not co-vary — the stencil is the
lowest-probability and highest-impact item on the list.

| rank | class | P | undetect | product | impact if real |
|---|---|---|---|---|---|
| 1 | R4-G5-17 compare-plumbing self-assertion | 0.15 | 0.9 | **0.135** | a "confirmed" tier is not confirmed |
| 2 | R4-G5-18 shared unstated combinatorial premises | 0.5 (≥1 more is wrong) | 0.9 | 0.45 → **0.05** baked into a counting engine | varies; one instance would be total |
| 3 | R4-G5-19 the injected 4.14% tail | 0.05 | 0.95 | **0.048** | a(40) wrong by up to 4.14%, undetectably |
| 4 | king-adjacency stencil (`r4-adv-ind` §7, not my row) | 0.03 | 1.0 | 0.030 | every number in the project |
| 5 | R4-G5-21 D4-symmetric errors vs the transpose check | 1.0 conditional | 1.0 | — | it is a blind spot, not an error |
| 6 | height misattribution (R4-G3-06) | 0.05 | 1.0 today, **0.2** with R4-G5-06 | 0.050 → 0.010 | 22.20% mis-split |
| 7 | R4-G5-22 anchoring/normalisation under column caps | 0.2 cond. | 0.5 | 0.10 cond. | new-work-only |
| 8 | R4-G5-23 cap-indexed guard errors | 0.15 cond. | 0.7 | 0.105 cond. | new-work-only |
| — | single-ISA codegen (R4-G3-12), H-indexed guards (R4-G2-19) | filed elsewhere; cited, not re-filed | | | |

### 3.1 R4-G5-17 — RANK 1: every "match=640 mismatch=0" in this campaign is asserted by the same script that does the matching, and no RED tests the cell count

The composite's weakest joint is not in any engine. Every independence claim in
the round reduces to a compare that reports how many cells it compared, and in
every case the reporter is the comparer. A compare that silently skips cells — a
parse that drops a header line, a missing file treated as empty, a key that
never matches because of a format change, a loop bound off by one — reports
`mismatch=0` and is indistinguishable from success in the log. This passes
**every** route simultaneously by construction, because it is downstream of all
of them, and it is the one failure mode that gets *more* likely as the campaign
adds routes.

The evidence that it is live rather than theoretical is already on file and was
read as being about something else: `r4-adv-cost` R4-AC5 found that two of three
"compiled and gated" claims have no receipt on disk and that **the quoted values
equal exactly what the design document predicted**; `r4-adv-ind` §6 item 8 found
that 21 of GATE 0's 49 cells are structural zeros the lane derived itself. Both
are instances of the same thing: the count of what was compared is testimony.

**Cheapest kill, and it is minutes: a RED for every compare in the campaign —
perturb one banked row in a scratch copy, assert the compared count is unchanged
and the mismatch count rises to 1 and the exit is nonzero.** A compare that
cannot distinguish 640 from 639 is not a control. The project's own standard
already requires this (`docs/engineering-standards.md`, RED-first); it has been
applied to the engines and not to the comparators, which are the things every
claim actually rests on. Prior at least one compare in the campaign has a silent
coverage bug: 0.15. Prior none of them has a coverage RED today: 0.8.

### 3.2 R4-G5-18 — RANK 2: the campaign has audited shared code and has never audited shared *premises*, and I found two wrong or trap-shaped in an hour

`r4-adv-ind` enumerates shared implementation layers exhaustively. Nothing
enumerates the shared **unstated combinatorial facts about king animals** that
lanes reuse without derivation — and those are shared far more widely than any
code, because every lane inherits them by reading each other's deliverables.
Two found tonight, without looking hard:

- **`n ≥ H + W − 1` is false for polyplets** (R4-G5-20). Used in `r4-gen.md`
  §1.5 / R4-G18 to bound `W ≤ 20` at H = 21.
- **Frontier partitions of a king animal can cross** (R4-G5-20). Any state-space
  reduction assuming non-crossing (Motzkin) rather than arbitrary (Bell) would
  silently undercount.

Neither is currently baked into a counting engine — the census is Bell-driven
and R4-G18's conclusion survives its broken reason — so the *realised* damage
tonight is zero and the product above reflects that. The class is rank 2 anyway
because it is invisible to every control the campaign owns: gates test binaries,
adversaries test claims, and nothing tests the arithmetic in the margin of a
brief that a later lane will build on.

**Cheapest kill: one pass over the campaign's deliverables extracting every
asserted combinatorial fact about king animals into a list, each with a
derivation or a brute-force check at n ≤ 10.** An afternoon, no compute, and the
output is a page a referee can check. Prior it finds a third: 0.5. Prior one of
them is load-bearing for a number rather than a cost model: 0.1.

### 3.3 R4-G5-19 — RANK 3: the injected 4.14% is the one error class the row-sum's vacuity makes permanently invisible

Compose R4-G5-01 with R4-G3-09. Heights 22–40 at n = 40 are evaluated from
wired `P_k`, not counted. They enter a(40) additively. The row sum cannot see
them, because a(40) is *defined* as the sum that includes them — the identity is
vacuous in precisely the direction that would catch it. No sweep touches them.
No second engine reaches them. The strip stops at 14, B1 at 16, spin at 21, the
ladder at 19. The Lean route's 95.85% is `Σ_{H≤21}` and stops exactly below
them.

So this 4.14% is the only block of row 40 with **zero** instruments pointed at
it, and the composition is what makes that visible: each route's coverage
statement mentions where it stops, and nobody has taken the union and looked at
the complement.

Two cheap things, both already half-filed elsewhere, and their value should be
re-scored against this framing rather than against their own lanes:
R4-G3-09's grep (does any `diag_p*_test.go` pin an evaluated value at n = 40?),
and the free integrality check on every injected cell via the v5 denominator law
(exact denominator known, so the check is total and costs rational arithmetic).
Third, R4-G5-04: the ratio fit is the only external detector that would see a
tail error at all. Prior the injected values are wrong at n = 40: 0.05 — low,
because the shape is a theorem and the wiring is tested at holdouts, but not
lower, because nothing pins the n = 40 evaluation itself.

### 3.4 R4-G5-20 — two shared premises, corrected, with the arithmetic

**(a) The minimum cell count to span an H × W box under king adjacency is
`max(H,W)`, not `H + W − 1`.** The main diagonal of a k × k box is
king-connected and has k cells. Confirmed against the banked table: `T(40,40) =
4052555153018976267 > 0`, so animals with n = 40 and H = 40 exist and their
widths run up to 40, which `H + W − 1 ≤ n` forbids.

Where it is used: `results/r4/r4-gen.md:477` and queue row R4-G18, to conclude
`W ≤ 20` at H = 21 and therefore that a horizontal cut is the same length as a
vertical one. The conclusion survives — if W can exceed 20, the horizontal
interface is *longer*, so orthogonal halving is worse than R4-G18 said, not
better — but the reason as written is wrong and its residue clause ("halving
becomes favourable iff W ≪ H, which never happens in this band") is unfounded
as stated: nothing in the band forbids W ≫ H. Anyone reusing that bound to size
a state space would be wrong in the unsafe direction.

**(b) Frontier partitions of king animals can cross.** In a column sweep the
occupied cells of the frontier column group into runs; the state records which
runs are already connected through the prefix. For rook-connected polyominoes
planarity forces this partition to be non-crossing (Motzkin). For king animals
it does not: the two diagonals of a 2 × 2 square are both adjacencies, so two
disjoint components can pass through each other — `(r,c)–(r+1,c+1)` and
`(r+1,c)–(r,c+1)` are simultaneously realisable in disjoint components. The
census is Bell-driven (`Bell(11) = 678,570` at H = 21, per R4-G4), which is
correct; `designs/10`'s Motzkin rank is used as an *ordering*, which is also
fine; L3-1's Motzkin bound is a *lower* bound and remains valid. The trap is
live for anything future: **a non-crossing state reduction is unsound on this
lattice and would undercount silently.** Filed as a row precisely so it is a
disclosure rather than a discovery.

Prior (a) and (b) are both right as stated: 0.95 each — each is a one-line
construction and I checked (a) against the banked table. **Cheapest kill for
both: brute-force at n ≤ 10, the grower that already exists.**

### 3.5 R4-G5-21 — my own flagship inherits the campaign's top common mode exactly, and I would rather say so than have an adversary find it

`M(h,w) = M(w,h)` holds for **any** adjacency relation invariant under
transposition. King adjacency is D4-symmetric. So is rook adjacency. So is every
plausible wrong stencil anyone would hand-write — the round-3 finding that
"rook and king closures are census-identical at H ≤ 8" is the same phenomenon.
The transpose check therefore has **zero power** against the one common mode
`r4-adv-ind` §7 identifies as the whole residual, and it would report clean
while the campaign's most consequential shared object was wrong.

Worse, in the way that matters for a composite: adopting the check *adds* a
clean-looking green light to a ledger whose weakest clause it cannot see. This
is the composite failure mode in its purest form — a new route that increases
apparent coverage while adding no bits against the dominant adversary. The
correct disclosure is that R4-G5-05/06 buy protection against **attribution and
accounting** errors and nothing against **rule** errors, and they must be
reported in a different column from anything that does (R4-G5-14, R4-G21).

### 3.6 R4-G5-22 and R4-G5-23 — two error classes my own proposals create, filed with the proposals

**R4-G5-22 — anchoring under a column cap.** Every engine counts *fixed*
animals, normalised by anchoring the leftmost occupied column. Under a `w`-column
cap, "leftmost column occupied" and "sweep terminates at column w" become the
same kind of statement and an off-by-one in either becomes an off-by-one in the
other. The uncapped runs never exercised the interaction. It is caught by
`M(h,w) = M(w,h)` at small h,w against brute force, which is why R4-G5-05's kill
must run before any capped production run, not after. P 0.2 conditional on
capped runs happening; undetect 0.5.

**R4-G5-23 — cap-indexed guards.** R4-G2-19's finding is that `gather()` is
H-indexed and every incumbent-free oracle runs at small H, so H-indexed guard
errors are invisible. A column cap introduces a **second** index with exactly
the same property: guards at `c = 0` and now at `c = w−1`, exercised only in
capped runs, validated only wherever brute force reaches. The fix is the same
shape as R4-G2-19's and should be written at the same time: for every (H, w)
in range, assert programmatically that the cells the sweep reads at the
boundary columns are exactly the king-neighbours preceding them in processing
order. Costs nothing to add to a check that should be written anyway.

---

## §4 Second pass — what my own rows share

### 4.1 R4-G5-24 — three properties, and the third is a criticism of the whole file

**(a) Every row above is an argument about an object nobody has built, and the
three that are not are the two kills and one source read.** R4-G5-01 and
R4-G5-02 are arithmetic on banked numbers and they close things; §1.5–§1.9 are
proposals whose decisive numbers (the corner's share, the capped survivor
fraction) are unmeasured; R4-G5-25 is the one row that became concrete, and it
did so because I opened the source instead of reasoning about the engine from
other people's deliverables — which is R4-G3-25's finding about plumbing,
recurring in the same round that filed it.

**(b) Composition turned out to be mostly a *subtractive* instrument, and I did
not expect that.** Four of my strongest results are that things do not compose:
the row sum composes to an identity (01), the cheap instruments compose to 4.17
bits against 101 (02), CRT across rule classes composes worse than not doing it
(03), and the campaign's coverage statements compose to a complement nobody was
looking at (19). One direction composed additively and it is the file's
best row: the transpose identity plus the engine's existing column parameter
plus the banked H ≤ 16 exact range compose into an exact piece of a cell none
of the three reaches alone (25/26). The pattern in that one success is worth
more than the four failures — **it composed a theorem with a parameter, not two
partial results with each other**, and every failure above was an attempt at the
latter. The generalisation worth carrying: **in a confirmation mission,
independent partial routes almost never combine into a stronger positive claim,
because the missing ingredient is always the same one (an independent total),
and they combine readily into a stronger negative one, because their coverage
complements intersect.** That is a fact about the shape of this problem and it
should be tested against round 5's rows rather than assumed.

**(c) The criticism: I ranked by clause-coverage and I have no more warrant for
that currency than the queue has for share-of-a(40).** R4-G21 proposes
bits-against-error, R4-G3-25 proposes what-must-still-be-trusted, and §2.3 of
this file proposes share-of-the-row-whose-caveat-is-removed. Three generators
have now each invented a private ranking currency, all three disagree with the
queue's, and **none of us has proposed how to choose between them.** That is the
next second-pass row and it is not mine to answer: it is a decision about what
the deliverable is, and by R4-G23's logic it will otherwise get made by default
when the compute budget runs out.

### 4.2 What I did not do

- I did not price anything. Every capped-run cost in §1 is labelled unmeasured
  and the two probes that would settle them (R4-G5-06's kill, R4-G5-09's census)
  are desk-scale and specified.
- I did not re-file the stencil, the single-ISA exposure, the H-indexed guards,
  the receipt gaps, or R4-G3-06's risk. All five are cited by id and left with
  their owners; §2.3 and §3 re-rank them, which is a different act from filing
  them again.
- I did not touch the closed-doors or three-floors sections of
  `results/triangle-r3-synthesis.md`.

## NOT ESTABLISHED

- The corner `min(H,W) ≥ 20` share of T(40,20) and T(40,21) at n = 40. Every
  cost claim in §1.7 is conditional on it.
- ~~Whether any engine accepts a column cap as a parameter today.~~ RESOLVED
  while writing §1.13: `--states` takes `Ncols` (line 27), the production mode
  sets it from one constant (line 213), and the accounting threads it (line
  281). What remains NOT ESTABLISHED is whether the exact `--height` mode
  honours a changed `W` end-to-end — I read the accounting, not the row writer.
- The reachable state count of a height-19, 14- or 21-column sweep at n = 40.
  R4-G2-6's saturation measurement is at 41 columns and I argue in R4-G5-09 that
  it does not transfer; I have not shown that it does not.
- Whether the ternary spine yields a residue at row 40 (used as an upper bound
  of 1.58 bits in R4-G5-02's ledger, which is conservative for the kill).
- Whether `tests/gate_cutcount_b1.py` or any spin gate has a coverage RED today.
  R4-G5-17's prior of 0.8 that none does is my estimate from reading the round's
  own audits, not a grep of the test files.
