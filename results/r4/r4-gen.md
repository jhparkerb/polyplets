# r4-gen — generator, round 4

GENERATOR, 2026-08-12. Owns no question, builds nothing, ran no compute on any
machine. Everything below is reading, `git`-free file inspection, and
arithmetic on numbers already on disk. Rows are in `results/r4/queue.md`
(`R4-G1`..`R4-G23`); this file carries the reasoning behind the ones worth more
than a line, the kills I could deliver myself, and the stale/subsumed audit.

Ranked by *different in kind*. The two rows I would defend hardest are **R4-G1**
(a proved theorem reaches T(40,21) with no frontier DP at all) and **R4-G14**
(the round is pricing the ladder for computation when the mission only needs
confirmation, at ~2.5x the necessary cost).

---

## 1. The top of the band

### 1.1 The diagonal law already reaches T(40,21), and only T(40,21) — R4-G1, R4-G3

This is the finding of my pass. It was not visible from the round-3 or round-4
files; it is visible from `docs/proofs/diagonal-law.md` crossed with the band
geometry, and the round-2 closure that everyone (including me, at first) reads
as covering it does not cover it.

The diagonal law is a **theorem**:

> T(n, n−k) = P_k(n)·3^(n−1−3k) for all n ≥ 2k+1, with deg P_k = k,
> and the onset n ≥ 2k+1 is proved and **sharp** — it fails at n = 2k.

The grand form (`docs/proofs/grand-form.md`, standard axioms in Lean) sharpens
this to **exactly two new constants per level**: P_k(n) = known_k(n) + a_k +
b_k·n, where known_k is fixed by levels < k, and

    a_j = [y^j] log( 3·K(27y) ),   b_j = [y^j] log( M(27y)/3 )

are determined by the defect-gas **cluster weights of surplus ≤ j** — objects
with no frontier, no strip, and no partition state anywhere in them.

Now put the band on that grid. At n = 40, k = n − H:

| cell | k | onset n ≥ 2k+1 | status |
|---|---|---|---|
| T(40,15) | 25 | 51 | below onset — law does not hold, **forever** |
| T(40,19) | 21 | 43 | below onset — **forever** |
| **T(40,20)** | **20** | **41** | below onset, and n = 40 = 2k is the *verified sharp-failure point* |
| **T(40,21)** | **19** | **39** | **n = 40 ≥ 39 — INSIDE the proved validity region** |
| T(40,22..40) | ≤ 18 | ≤ 37 | inside, and already wired from pinned P_k |

So the round-2 closure — "the row-40 H = 15..19 cells sit below the proved
sharp onset at every depth, forever" (`results/triangle-r2-extension-scout.md`
§6, `docs/triangle-round3-brief.md`) — is exactly right and I am not reopening
it. It names H = 15..19. **It does not name H = 20 or H = 21, and the two
behave oppositely.** H = 20 is below onset and dead by the same theorem
(R4-G3, filed with that kill so the round does not spend a week rediscovering
it). H = 21 is *in* onset.

Why is T(40,21) not already a law cell, then? Because P_19 is deliberately not
pinned. `polyplets/PROOF-STATUS.md:7` and `:179`:

> The engine wires k = 0..19. Lean covers k ≤ 18, all grand-pinned from two
> real-swept cells per level. **k = 19 is deliberately not pinned**: it is
> fitted-no-holdout, no holdout is possible (the sequence closes at a(40)), and
> no banked term uses it. ... P_19 ... is fitted from the final two top cells
> T(39,20)/T(40,21) ... pinning it in Lean would certify nothing.

That is the correct call *for the pinning-from-cells route* — the only two
in-onset cells at k = 19 with n ≤ 40 are (39,20) and (40,21), so fitting from
them and then "predicting" them is vacuous. **It is not the only route to
(a_19, b_19).** The grand form says those two constants are computable ab
initio from cluster weights of surplus ≤ 19, with no reference to any swept
cell. Compute them that way and T(40,21) and T(39,20) become *predictions of a
proved theorem*, checkable against the sweep.

What that would buy, stated precisely:

- **T(40,21) = 2.8431% of a(40)** (share quoted from
  `results/triangle-r2-extension-scout.md` §6, itself from `triangle.py
  provenance`), confirmed by a rule class with no frontier, no cut, no
  partition state, no completion predicate, and no union-find — the cleanest
  level-1-and-level-2 clearance available anywhere in this project.
- The cell the B1 ladder cannot reach: 215.8 GiB untransposed, ~68 GiB
  transposed (GEN-1) with a container gate nobody has passed yet.
- **T(39,20) as a free RED control**, predicted by the same two constants and
  independently swept.
- Zero large-RAM compute. The work is a weight-enumeration DP over clusters,
  which the round-2 scout measured to parallelize perfectly per cell.

**The honest cost, and it is bad.** `results/triangle-r2-extension-scout.md` §3
prices the weight enumeration exponentially, ×5–15 per level with "no cliff and
no floor", and quotes *through d = 19*: **~30–100 core-years Python ≈ 0.3–1
core-years C++, fleet-months even in C++** — and that C++ DP does not exist.
Two caveats in both directions:

- **Worse than quoted.** That table is the cost of the *mod 3^m tower*, whose
  truncation only needs weights of surplus ≤ ~12 at m = 20. Exact a_19, b_19
  needs surplus ≤ 19 exactly. The true figure is above the quoted one, by an
  unmeasured factor. NOT ESTABLISHED — nobody has costed the exact-weight
  requirement, and the r2 table cannot be read as costing it.
- **Better than quoted.** The scout's own calibration says the model runs
  conservative-high by ~×3 at short range; the dominant entrants at high levels
  are the ℓ=2 interior weights ((6,7),(5,8),(4,9),…), and a **proved** W(a,b)
  closed form removes that whole family from the exponential. W(a,b) is
  currently fitted-not-proved (a=2 cubic with 3 holdouts, a=3 quartic with 1,
  both leading coefficient 24, `results/defect-gas.md` §Open) and the r2 scout
  called polynomiality-in-b "the shape of a transfer-matrix-in-b argument".
  That is R4-G9, and it is the single lever that decides whether R4-G1 is a
  quarter or a decade.

My prior that R4-G1 delivers T(40,21) exactly within this project's remaining
life: **0.15**. My prior that it is the best *level-1-and-2* route to that cell
that will ever be found: **0.6**. The cheapest thing that would kill it is not
a run — it is an afternoon's exact census of *which* weights (ℓ, surplus,
shape) enter a_19 and b_19, priced against the r2 scout's measured per-shape
anchors. That census is the same script family as `r2_scout_d8.py census`
(which already does "exact per-level weight requirements m = 3..20") pointed at
the exact rather than the truncated requirement. If the census says the top
entrant is an ℓ≥5 surplus-19 cluster with a state dictionary that will not fit,
the row dies with a number attached and R4-G9 dies with it.

### 1.2 A free arithmetic check on the two top cells — R4-G2

Independent of whether R4-G1 is ever run, P_19's *shape* is a theorem while its
two constants are a fit from T(39,20) and T(40,21). Proved facts about P_19
that the fit does not use:

- deg P_19 = 19 exactly and [n^19]P_19 = 25^19/19! (grand-form Corollary 2);
- **P_19 takes integer values at every integer** (`production_int_all` in Lean,
  Step 6 of `diagonal-law.md`);
- the minimal denominator is 19!/5^ĉ_19 with ĉ_19 given exactly by the v5
  denominator law (`results/v5-denominator-law.md`, exact to k ≤ 19).

Write P_19(n) = known_19(n) + a_19 + b_19·n. Integer-valuedness at all n forces
the fractional part of known_19(n) to be an **affine** function of n mod 1 —
a condition on known_19 alone, i.e. a zero-compute consistency test on the
already-pinned levels k ≤ 18 and hence on the real-swept cells that pinned them
— and, given that, it pins (a_19 mod 1, b_19 mod 1) exactly. The fitted
constants come from a 2×2 rational solve on two integer cell values;
integrality of the resulting polynomial at all integers is **not** automatic
from that solve. So the test has content, and every bit of it binds T(39,20)
and T(40,21).

Cost: minutes of exact rational arithmetic on polynomials the repo already
generates (`scripts/derive_pk_fast.py`, `scripts/verify_diagonal_pins.py`).
Value: unknown in advance — it is somewhere between 0 and log2(denominator)
bits. **Filed with its own kill condition:** step 1 is to check whether
`verify_diagonal_pins.py` already enforces integrality of P_19 as part of its
pass. If it does, the row is vacuous and closes immediately, and that is worth
knowing in one grep. I did not run that check — a generator files, it does not
verify — so this row's value is **NOT ESTABLISHED**.

### 1.3 The band's cost model prices the wrong state space — R4-G4, R4-G5

Everything in `results/r4/r4-a.md` §4 sizes the ladder as
`window census × bytes/window`, and the window census (ADV-I4's closed form,
2,228,466,695 at H=21) counts windows **without any reference to n**. But the
run has n ≤ 40, and at the top of the band that constraint is savage.

At H = 21 the window is 22 slots. Any state carries a partition into b live
blocks; b blocks in one window need b runs separated by gaps, and — because the
extraction is [q^1] — every one of those blocks must eventually merge into one
component, which costs cells proportional to the gaps. Adding the cells already
spent to reach the state, every window w has a **minimum total cell budget**
mincost(w) = (cells to reach w) + (cells to complete from w). A window with
mincost(w) > 40 contributes nothing to any n ≤ 40 and is dead weight in RAM.

This is the same machinery GEN-3 proposed as a *coverage audit* ("states with
minimum > 22 have never been exercised"). Turned around it is a **feasibility
prune**, and nobody has proposed it that way. Two separable wins:

- **R4-G4, hard prune.** Drop states with mincost > 40 entirely. The census is
  Bell-driven — Σ Bell(chunks), and Bell(11) = 678,570 dominates — so the
  census mass sits exactly on the many-chunk windows, which are exactly the
  ones whose merge cost is largest. My rough count: a window with c chunks
  needs ≥ 2c−1 slots and ≥ Σgaps cells of detour, which at H = 21 starts
  colliding with the 40-cell budget somewhere around c ≈ 7–8 out of a maximum
  11. If the survivor fraction is even 1/4 the H = 20 cell drops from 68 GiB to
  17 GiB and H = 21 transposed drops inside ayr.
- **R4-G5, ragged payload.** Even for surviving states, the payload is 41 dense
  area slots. A state with mincost 30 has 11 live slots, not 41. The mean of
  (41 − mincost + 1) over surviving windows is the true payload multiplier, and
  it is bounded above by 41 with no lower bound established. This one is pure
  bookkeeping and composes with everything: it multiplies against u8 narrowing,
  against the flat container, and against transposition.

Cheapest kill for both, and it is the same experiment: at H = 12..14, where the
exact census is known and the calibration run measured real RSS, compute
mincost per window combinatorially (no DP run needed — mincost is a function of
the mask and partition) and report (i) the fraction with mincost ≤ 40 and
(ii) the mean feasible-slot count. Minutes of Python on the existing census
script. **If the survivor fraction at H = 14 is above ~0.9 and the mean slot
count above ~35, both rows die together.** I expect the prune to be weak at
H ≤ 16 (where 40 cells is generous for a 17-slot window) and strong at H = 20,
21 — so the measurement must be run at the *largest* height the census reaches,
not the cheapest, and reported as a trend in H. That is the one methodological
trap in this row and it is why I am stating it here rather than in the queue
line.

Prior that the prune is worth >2x at H = 21: **0.65**. Prior >10x: **0.3**.

### 1.4 The wall is a product of four factors and the round is varying one — R4-G8

`results/r4/r4-a.md` §4.2's table varies exactly one thing: payload word width
(u32 / u16 / u8), with one row for a flat container. The RAM at a band cell is

    RAM = census(H) × coeffs × word × buffers × (1 + container overhead)
          × (unpruned-n factor)

and the round has four independent attacks on it, three of which are unpriced
together:

1. **census(H)** — attacked by transposition (GEN-1): H = 21 → 703M windows,
   the H = 20 number, a **3.17x** cut on the hardest cell;
2. **word × coeffs** — attacked by u8 narrowing (r4-a §2.7), **2.13x**;
3. **container overhead** — attacked by the flat open-addressed table (LG-2
   calls it load-bearing), measured 270 B against a 434 B u8 payload, so
   **~2.4x**;
4. **unpruned-n factor** — attacked by R4-G4/G5, unmeasured.

Composing the three measured ones on H = 21: 2.23e9 × 434 B = 967 GiB →
transposed 305 GiB → flat container ~118 GiB. **That is already inside dalby
(121 GiB available) before any prune at all**, and inside ayr with any prune
better than 1.6x. The synthesis's "H=21 is 215.8 GiB and is off-ayr under any
bookkeeping" and r4-a's "H=20/21 are unchanged and remain out" are both
statements about a *single-factor* table. Nothing here is a new mechanism —
each factor is somebody else's row — but nobody has multiplied them, and the
product changes the verdict on the two cells the round has written off. That
is the whole content of R4-G8, and it is why I file it as a row rather than a
remark.

Caveat carried with it: these factors are not certainly independent. The flat
container is what makes u8 narrowing worth anything (a `unordered_map` node
does not shrink when its payload does), so 2 and 3 are partly the same lever
counted twice. The honest composed figure is therefore between 118 GiB and
305 GiB, and pinning it is LG-JOB-1R's job plus one design decision.

### 1.5 Out-of-core, and slicing — R4-G6, R4-G7

Two ways to stop needing the table in RAM at all, both standard elsewhere and
neither filed here.

**R4-G6, external-memory DP.** dalby has 564 GB free on `/dev/md3`. The B1
transition is local (mask shift + partition relabel), so a radix-partitioned
sort/merge DP is textbook: emit (newkey, payload), partition by key prefix,
merge-combine. The whole cost is *full-table passes*. Cell-at-a-time gives
41 columns × 22 cells = 902 passes and dies (hundreds of TB of I/O).
Chunk-at-a-time — load 1/3 of the table, run all 22 cell-steps on it, spill
successors, merge — gives ~3 passes per column, ~123 passes. At 374 GiB and
1.5 GB/s that is ~8.5 h of I/O per prime, which is not the blocker; the sort
and the successor fan-out are. Prior: **0.4**. Cheapest kill: two numbers, both
cheap — dalby's sustained sequential read+write on md3 (one `dd`-class
measurement) and the measured mean successor fan-out per cell-step from the
instrumented `--states` run that R4-A2 already requires. If fan-out × table
size exceeds disk, it dies without a design.

**R4-G7, boundary-conditioned slicing.** The classic RAM-for-time trade: pin a
boundary condition somewhere in the sweep, run both sides restricted to it, sum
over conditions. Perfectly parallel, tiny RAM per slice. The version that could
work here is *not* pinning a full mid-column state (there are 2.2e9 of them);
it is pinning a **coarse invariant** — the occupancy mask alone (2^22 classes),
or the chunk count, or the area used at the cut — and letting the rest vary.
Prior: **0.35**, because the restriction only shrinks states *near* the cut and
the DP's state count is roughly flat across columns. Cheapest kill, and it is
sharp: at H = 12–14, measure the reachable state count of each half when the
mid-column mask is pinned. If it exceeds ~1/10 of unrestricted, the trade never
pays and the row closes with a curve.

I flag one thing about R4-G7 that makes it worth more than its prior: it is the
only row in the entire queue, mine included, that changes the *shape of the
computation* rather than the rule, the payload, or the reach. Every memory wall
in every other field falls to exactly this move. Its low prior here is a fact
about this DP's state geometry, not about the technique, and it should be
measured rather than argued.

---

## 2. What the recovered oracle makes newly possible

### 2.1 Truncated-Nmax runs at the unconfirmed heights — R4-G10

The round wants H = 17..19 at n = 40 and prices it at 14.7 h / 47.7 h / 156 h
per run. Nobody has priced **H = 17..19 at Nmax = 20, 25, 30**. Two reasons
that is not a rounding detail:

- the payload is 41 area slots *because* Nmax = 40; at Nmax = 25 it is 26 slots,
  a flat 1.6x;
- more importantly, the reachable state count at Nmax = 25 is far below the
  unbounded census, by exactly the R4-G4 mechanism, and at H = 19 with 25 cells
  the constraint bites hard.

What it buys is not a step toward n = 40. It buys **the first second-source
values at the exact heights nobody has ever recounted**, checkable against the
banked triangle at rows ~20–30 of H = 17, 18, 19 — heights whose kink-kernel
sweep output currently has *no* independent confirmation at any n. Today's
deepest residue validation is planned at H = 16 (R4-A3's RED-modp). This adds
H = 17, 18, 19 at reduced n, which is a different axis of coverage, and it is
the natural staircase: run Nmax = 25, then 30, then 35, and stop where the box
stops. Prior it is cheap enough to matter: **0.7**. Kill: one `--states 17 40 26`
census against `--states 17 40 41`; if the state count barely moves, the
truncation buys only the flat 1.6x and the row degrades to a footnote.

### 2.2 The calibration log is 16 measured cost points and the round is
extrapolating from five — R4-G13

`results/cutcount_b1/calib_run.log` carries per-height wall and RSS for
H = 1..16 of the exact-payload binary. `results/r4/r4-a.md` §4 builds its whole
routing table on the H = 15→16 marginal slope (two points) plus a `windows × H`
scaling law fitted to the observed 3.21 per-height ratio. Sixteen real points
are on disk. Fitting bytes/window and µs/slot-col across all sixteen, with
residuals, would either confirm the two-point slope or expose curvature — and
curvature is exactly what a rehash discontinuity looks like. Zero compute, one
afternoon of `awk` and least squares on a file the repo now owns. Prior it
changes a decision: **0.3**. Prior it is worth its cost: **0.95**.

### 2.3 Two things the oracle does *not* unlock — R4-G11, R4-G12, filed with
their kills

I looked for these first because a generator's cheapest contribution is
stopping a plausible-looking successor.

**R4-G11 — it does not reopen cell-to-cell relation fitting.** The L4-12 term
source floor says fixed-H recurrence fitting fails because rule-independent
terms cost c^n and existed only to n = 18. The oracle supplies **640
rule-independent values, to n = 40, at H ≤ 16** — a direct assault on the
floor's premise, and the first thing I checked. It fails anyway, twice over:
the minimal order at H = 15, 16 is bounded below by the hmirror-quotient census
(2122 and 6045, L4-11) and by full Motzkin M(H+1)−1 ≈ 8.5e5 for the
unsymmetrized object, so 40 terms cannot pin anything; and even a fitted
recurrence at H = 16 says nothing about H = 17. The bivariate direction is
closed independently by rounds 1 and 2. **Closed at filing.** What it does tell
us is worth keeping: the floor's binding clause is the *order*, not the term
source, and any future row that proposes to relieve the term source has already
lost.

**R4-G12 — it does not upgrade GEN-4's analytics.** GEN-4 screens band values
against certified μ_H brackets. Running the same screen against the oracle's
C_H rows adds exactly nothing, because the oracle already matches banked to all
31 digits at 640 cells — the screen would be testing a number against itself.
**Closed at filing**, so nobody files "now do GEN-4 on the second source".

---

## 3. Confirmation that is not recounting

### 3.1 The ladder is priced for computation; the mission only needs
confirmation — R4-G14

This is an audit finding on our own round and I think it is the largest
unclaimed cost saving on the table.

`results/r4/r4-a.md` §2.5 sets the run count from a **bit budget**:
C_H(40) < 2^112, four 31-bit primes give 124 bits, plus one held out for RED-D,
so **k = 5**. §4.3 then prices every routing decision at five runs: H = 18 is
"three waves × 47.7 h ≈ 143 h", H = 19 is "5 × 156 h ≈ 780 h, not a phase-2
job".

A bit budget of 112 bits is what you need to **reconstruct C_H(40) from
nothing**. That is not the mission. The banked value already exists; the
question is whether it is right. One 31-bit prime run answers that with a
false-pass probability of ~2^−31 against any error not divisible by p. Two
runs give ~2^−62 *and* keep a second prime as the cross-check that RED-D was
introduced to provide. There is no third thing five primes buy.

The independence adversary already said this in round 3 — ADV-I3 (r3 queue line
97): "testing banked values needs no CRT at all — each prime run is a
standalone log2(p)-bit congruence check". The round-4 cost table did not apply
it. Re-pricing §4.3 at **2 runs**:

| height | r4-a at 5 runs | at 2 runs | share of a(40) |
|---|---|---|---|
| H = 17 | 5 concurrent on dalby, ≤ 14.7 h | 2 concurrent, ≤ 14.7 h | 9.06% |
| H = 18 | 3 waves, ~143 h (~6 days) | 1 wave (ayr + dalby), **≤ 47.7 h** | 7.42% |
| H = 19 | 780 h serial, "not a phase-2 job" | **2 × 156 h ≈ 13 days serial**, or one wave if two boxes hold 90.8 GiB u8 | 5.72% |

H = 18 goes from a week to two days. **H = 19 goes from written-off to a
fortnight**, which is the single biggest verdict change available to this round
and it costs nothing to obtain — it is an accounting correction, not a new
idea. It also composes with everything in §1.4 and §1.3: R4-G4's prune and
R4-G8's product act on the RAM, R4-G14 acts on the run count, and they
multiply.

Two honest counterweights, both of which I would put in the phase-2 brief
rather than let the row carry silently:

- A residue check confirms *the banked value*; it does not produce an
  independently computed value that could be published as such. If jasonp wants
  the paper to say "recomputed by a second method" rather than "confirmed to
  1 part in 2^62 by a second method", the CRT budget comes back. That is a
  wording decision, not a technical one, and it is his.
- Systematic (non-random) errors are not uniformly distributed mod p. A
  shard-loss error that drops a clean power of two is not more likely to be
  divisible by a 31-bit prime than any other, but the argument is heuristic and
  the RED battery, not the residue count, is what covers it.

Prior the re-pricing is correct as arithmetic: **0.9**. Prior it survives
jasonp's publication standard: **0.6**.

### 3.2 Count every free bit — R4-G15

Generalizing R4-G14: confirmation is an information budget, and the project
already owns bits it never spends. The Klein forced-parity theorem is banked
and holdout-verified to n = 40 (GEN-10) — that is T(40,H) mod 2 for free, from
a proved theorem, on every band cell. The ternary spine gives proved mod-3
structure. INV-8 offers mod 2 at H = 20, 21 for ~0.3 GiB. The round-2 tower
offers T(40,21) mod 9 at full depth. None of these is large — one to three bits
each — and stacked they do not replace a prime. The row's value is not the
arithmetic; it is that **the project has never once totalled the bits it holds
against the bits it needs**, and the r2 extension scout's bit-accounting table
is the only place in the repo where a route was scored in that currency at all.
See also R4-G21.

### 3.3 GEN-9's certificate closure is over-broad — R4-G16

GEN-9 closed reader-checkable certificates at filing: "any per-run transcript
smaller than the frontier cannot force column-transition correctness (the
BCMS16 compilation floor applies to verification artifacts exactly as to
counters)".

The BCMS16 floor is a lower bound on **knowledge compilation** — the size of a
deterministic, one-pass-checkable representation. It says nothing about
protocols with bounded soundness error. Sumcheck / GKR verify a layered
arithmetic circuit in polylogarithmic verifier time with soundness error
O(d/|F|), and a Merkle-committed transcript with random spot-checks verifies in
O(√) time. Neither is a compilation, and neither is bounded by the compilation
floor. GEN-9's exception clause names only certified compilation (CPOG); the
probabilistic class is not mentioned and is not covered by its argument.

Two separate claims, and I want them scored separately:

- **The closure is over-broad as written: prior 0.85.** That is the content,
  and it is a desk fix — one paragraph in whoever inherits GEN-9.
- **A sumcheck-style certificate is practical for this DP: prior 0.2.**
  Arithmetizing an `unordered_map` partition DP over Z[q]/(q²) into a layered
  circuit is a research project, and the prover pays the full run cost anyway,
  so it does nothing for H = 20/21. Where it *would* pay is exactly where the
  round is weakest: it turns the H = 17/18/19 runs from "trust our binary" into
  "verify in minutes with soundness 2^−100", which is a referee-facing property
  no other row offers.

Cheapest kill for the second half: name the field and the circuit depth. If the
DP's transition cannot be written as a low-degree arithmetic circuit over a
prime field without blowing the degree past the state count, it dies on the
spot and the row keeps only its audit half.

### 3.4 Cumulative accounting, and what the endgame actually is — R4-G17

From C_H(n) = Σ_h (H−h+1)·T(n,h):

    C_H(n) − C_{H−1}(n) = Σ_{h ≤ H} T(n,h)

A **first** difference of two heights gives a cumulative; the **second**
difference of three heights gives a cell. Consequences the round has not
stated:

1. The H = 17, 18, 19 ladder confirms not only three cells but the cumulative
   Σ_{h≤19} T(40,h) = **93.00% of a(40)** as a single arithmetic statement, and
   that statement is stronger than the three cells taken separately in one
   respect: it is insensitive to how the sweep attributes cells *between*
   heights, which is precisely proposition 3 (height accounting) of the shared
   rule.
2. Therefore, after H = 19 lands, **the entire residual of the mission is one
   number**: T(40,20) + T(40,21) = a(40) − [C_19 − C_18](40) = 7.00% of a(40).
   Not two cells — one sum. Any route that produces a(40)-as-a-total by any
   means closes the top of the band without ever touching H = 20 or H = 21.
3. And the flip side, which is the kill I owe with it: I know of no
   height-blind route to a(40). Redelmeier is Θ(a(n)); a strip DP for the total
   needs H = 40. So (2) is a *reframing*, not a route — but it is the right
   frame for the round's last mile, and it is the frame in which GEN-11's
   unbiased SIS estimator, or any future total-count idea, becomes worth its
   variance instead of being dismissed as non-exact.

### 3.5 Two more, filed with their kills — R4-G18, R4-G19

**R4-G18, orthogonal halving.** The natural response to "the vertical cut costs
Motzkin(H/2+1)" is to cut horizontally instead: split the H = 21 strip into two
~11-row halves, grade each by the partition induced on the interface row, and
glue. **Killed by the band's own geometry.** A connected animal needs
n ≥ H + W − 1, so at H = 21, n = 40 the width is W ≤ 20 — the horizontal cut is
*the same length as the vertical one*, and pays the same Motzkin floor
(L3-1). The interface partition multiplies the H = 11 state count back up to
~1e9, i.e. within a small factor of the H = 21 census. Filed so that the next
person who thinks of it reads the kill instead of measuring it. The residue
worth keeping: the halving does become favourable if W ≪ H, which never happens
in this band but is the condition to check on any future lattice.

**R4-G19, forward/adjoint consistency.** Run the DP backwards from the
completion condition and check the inner product against the forward run. It is
a genuinely different code path with disjoint indexing bugs. It does **not**
halve RAM — both directions need the full table at the meeting column — and it
costs a second full run, so it is a poor buy against a second prime, which
costs the same and gives 2^−31. Filed with that kill. The residue worth
keeping is real and feeds R4-G4: **forward-reachable and backward-reachable
state sets are different**, and the DP as written explores forward-reachable
states, many of which can never complete within budget. That asymmetry *is* the
feasibility prune, arrived at from the opposite direction — two independent
routes to the same measurement is a reason to raise R4-G4's priority, not
lower it.

### 3.6 A second payoff of §1.1's machinery — R4-G20

If ab initio (a_k, b_k) are computable at all, the levels **below** 19 matter
more than level 19. Today, `docs/proofs/grand-form.md` §Conditionality: the
wired diagonals k = 10..19 — which carry cells across a(30)..a(40) — rest on
"real sweeps + the shape theorem (Lean) + this theorem + **the banked 2-point
solve inputs**", and `polyplets/PROOF-STATUS.md` is explicit that the pin cells
"are hypotheses of the Lean theorems, engine values assumed, not proved in
Lean". Ab initio constants at level k discharge that hypothesis at level k and
convert every wired cell on that diagonal from engine-conditional to
theorem-derived. That is a bigger prize than T(40,21) and it is not on the
mission statement, which is exactly why I am filing it: a referee who accepts
a(40) will ask about a(30)..a(39) next.

---

## 4. Job requests

**None.** Every measurement I name is either desk work or rides inside a job
someone else has already requested (R4-A2's instrumented `--states` run carries
the successor fan-out that R4-G6 needs; LG-JOB-1R's H = 12..16 ladder carries
the anchors that R4-G13 refits). The one experiment I would most like run —
the mincost census behind R4-G4/G5 — is Python over an existing closed-form
census script at H ≤ 21, seconds to minutes, and belongs to whichever scout
picks the row up rather than to a generator.

---

## 5. Stale and subsumed OPEN rows in `results/triangle-r3-queue.md`

Judged against the round-4 state. I am naming the reason, not just the verdict.
Nothing here is an edit to that file — the protocol is append-only and these
belong to the lead's triage.

**Stale — the row's premise no longer holds:**

| row | why |
|---|---|
| `ADV-C1` (line 90) | Both legs gone. Leg (ii) census closed exactly by ADV-I4; leg (i) closed by LG-1 (the dalby run completed) plus R4-A3. GEN-C2 rescoped it, GEN-C5 superseded that. Nothing live remains; it should be CLOSED, not OPEN. |
| `ADV-C2` (line 91, binary provenance) | CLOSED by PROV-1, which found the run.log and the phase-B erratum. Left OPEN by oversight. |
| `ADV-C5` (line 94, transpose accounting) | CLOSED by PROV-3 (measured NOT EXERCISED, with a successor). Left OPEN. |
| `LG-JOB-1` (line 138) | Superseded outright by R4-A3/LG-JOB-1R, whose premise correction (`--modp` already exists) invalidates this row's prerequisite line. |
| `LG-4` (61-bit primes, 2 runs/height) | Stale twice: r4-a §2.7 shows 61-bit primes overflow the committed u64 accumulator (needs `__int128` mulmod, not a 6-line change), and R4-G14 makes "2 runs" the default at *any* prime width, which removes the row's entire motivation. |
| `LG-3` (7×16-bit vs 14×8-bit) | Stale on the same §2.7 finding: the committed payload is u32, so prime width changes neither code nor RAM. The row survives only as a rider on the narrowing change, not as a choice. |
| `L5-6` | Already recorded as effectively CLOSED-RED by GEN-C3 (job ran, 9 errors, repair deferred). Still shows JOB-REQUESTED. |

**Subsumed — a later row does strictly more:**

| row | subsumed by | why |
|---|---|---|
| `L4-5` (symcount two-rule-class agreement, n ≤ 26) | the recovered oracle + R4-A5 | L4-5 was "the cheapest exact-value stress test of the frontier rule class against a no-cut counter, hundreds of cells", at n ≤ 26, costing ~10 laptop-hours. `results/cutcount_b1/rows/` is **640 exact cells at n ≤ 40, H ≤ 16, by a rule with no connectivity decision in it at all**, already banked at zero further cost. Strictly more reach and strictly more rule-distance. Retire it. |
| `L6-1` | LG-*/R4-A* | The row as written covers H = 15..20 with 8-bit primes. H = 15, 16 are done; the pricing is superseded three times over. It should be rescoped to H = 17..19 or closed in favour of R4-A3. |
| `L6-2` | INV-8 | The 3^20 pricing the row rests on is 64x wrong (INV-8's exact reachable-colouring count). Every number in L6-2 is stale even though its idea is live. |
| `L6-5` (third-party enumerator past s = 14) | KANCH-1 | KANCH-1 pinned the external king ladder to n = 18 from primary sources without running anyone's code. L6-5's remaining content is only "run their binary", which is a jasonp call, not a route. |
| `ADV-I1` (stencil-blind gate fact) | R4-A3's RED battery | Absorbed as a first-class control in LG-JOB-1R. Keep the fact, retire the row. |
| `L4-10` (derive fixed-H recurrences from an independent formalization) | L4-11 + L4-12 | The row is level-1-only by its own admission, and L4-12's term-source floor kills the family generically. |
| `L1-11` (finish the band c-distribution grid) | its own note | Self-declared "confirmation depth, not a live route" on a closure that already stands on 11 cells plus an exact endpoint. In a round with contested compute it should not be competing. |

**Not stale, and I want to say so explicitly:** `ADV-I3` (line 97) is the
opposite of stale — it is *correct and unapplied*, and R4-G14 exists only
because round 4 re-derived the five-prime budget without it. `ADV-C4`
(archived-state replay) still costs one `ls` on dalby and still nobody has run
it, three rounds in. `GEN-1` (transposition) is load-bearing for §1.4 and
should be raised, not left mid-queue.

---

## 6. Second pass — what my own rows have in common

Reading §1–§3 back as a set, three shared assumptions, and one of them is
costing the round something.

**(a) Every row treats the unit of confirmation as one exact integer at one
(n = 40, H).** That is what "share of a(40) two-sourced" measures, and it is
the only currency this round has used. It silently ranks a route that gives one
cell exactly above a route that gives twenty cells partially — even when the
second buys more total protection against the error modes we actually fear. The
one place in the repo that ever scored routes differently is
`results/triangle-r2-extension-scout.md` §6, which tabulated **bits against
enumeration error** and, separately, **bits against formula-chain error**, and
noted that the two adversaries are not the same and are not covered by the same
work. Round 4 has collapsed them into one number and lost that distinction.
This is R4-G21, and it is the row I would most like someone senior to argue
with: adopt bits-against-error as a second ranking column, re-score the three
live pieces in it, and see whether the order changes. My guess is that it does
— L3-5's 95.85% is enormous in share and *zero* in bits against enumeration
error, while a 27-cell mod-3^m tower is negligible in share and tens of bits
against exactly that adversary.

**(b) Every row, mine and everyone's, audits a computation that has already
happened.** The only exception in the whole queue is PROV-4, which asks future
sweeps to emit width alongside height. The generalization is R4-G22: **decide
now what the next production sweep must emit to be checkable at all** — per-column
frontier census, per-height width marginals, worker build identity (PROV-1's
successor), and a state-space checkpoint at one in-band column (which would
have made ADV-C4 free instead of speculative). Every one of these is near-zero
marginal cost in-pass and impossible retroactively, and the project has now
been bitten by exactly this three times (no width data, no archived state, no
worker rev). It is not a route to a(40) and it should not compete with one; it
is the row that stops round 6 from filing these same three findings again.

**(c) Every row assumes the answer must be produced before anything is said.**
R4-G23, half-formed and jasonp's call alone: the mission is "total confidence",
and the round is treating that as a precondition for publication. A staged
claim — a(40) with an itemized provenance table, X% two-sourced by a rule that
never decides connectivity, 95.85% rule-proved in Lean, and a named,
reproducible residual — is a *different deliverable*, not a weaker one, and it
is the one that most published enumeration records actually are. I file it
because "an unfiled idea costs more than a bad row", and because the
alternative to filing it is that it gets decided by default when the compute
budget runs out rather than on its merits. It is not an agent's decision and I
am not arguing for it.

---

## NOT ESTABLISHED

- **The exact-weight cost of ab initio (a_19, b_19)** (§1.1). The r2 scout's
  ~30–100 core-years figure is for the *truncated* mod-3^m tower, which needs
  weights of surplus ≤ ~12 at m = 20; the exact constants need surplus ≤ 19.
  The true cost is higher by an unmeasured factor and no one has censused it.
- **Whether R4-G2's integrality check is vacuous.** One grep of
  `scripts/verify_diagonal_pins.py` settles it; I did not run it.
- **The survivor fraction and mean feasible-slot count under the mincost prune**
  (§1.3). Every number in that section is a structural argument, not a
  measurement. The 118 GiB composed figure in §1.4 likewise rests on three
  factors that may not be independent.
- **dalby's sustained sequential I/O** and the DP's successor fan-out (§1.5,
  R4-G6). Both quoted as placeholders.
- **Whether the B1 DP's transition admits a low-degree arithmetization**
  (§3.3). Asserted as the kill condition, not tested.
- I ran **no compute anywhere**, and I did not verify any claim in
  `results/r4/r4-a.md` or `results/cutcount_b1/PROVENANCE.md` beyond reading
  them. Where I re-price r4-a's table (§3.1) I am changing its run count, not
  its measured anchors, and its anchors remain as labelled there.

---

**Filing verified.** Rows R4-G1..R4-G23 were re-read out of
`results/r4/queue.md` after appending (23/23 present, no id collision with the
R4-A, R4-INV or R4-LEAN lanes that filed concurrently). Doing that check is
R4-INV-4's recommendation and this deliverable follows it.
