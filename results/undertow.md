# Undertow — the diagonal tower pins from below, not from above

2026-08-20, branch `lastditch`. Script `experiments/undertow_pin.py`; every
number here is printed by it.

## The claim

`docs/b1-closure-plan.md` §1 costs level `k` of the diagonal tower two
**above-onset** anchors, `T(2k+1, k+1)` and `T(2k+2, k+2)` — the two *tallest*
cells on its diagonal. That is the rule that made row 40 expensive: P₁₉'s
anchors are `T(39,20)` and `T(40,21)`, and `T(40,21)` is the 36.4-hour H = 21
sweep of `results/ns_a40/PROVENANCE.md` phase C.

The anchors do not have to be the tall ones. The grand form
(`docs/proofs/grand-form.md`, Lean-complete) makes level `k` carry exactly two
new constants,

    P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j ),

so any two independent linear equations in `(a_k, b_k)` pin it. Severance W3
(`results/onset-defect-depths234.md`) supplies them from short cells: at depth
`j` below onset,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) · 3^(2k-3k-j) + D_j(k)                  (*)

and `D_j(k)` is computed **ab initio** from bounded-excess cluster-weight
families — it reads neither the triangle nor the wired `P_k`, which is what the
W3 gate exists to keep true. `P_k(n)` is linear in `(a_k, b_k)` with
coefficient 1, so (*) is one linear equation, and its cell sits at height
`k+1-j`: **j rows shorter than the onset anchor.**

### What is new here, precisely

No new theorem. The grand form is already proved and Lean-complete; `D_j(k)` is
already derived ab initio by Severance W3 and already checked against banked
cells. The content is the **choice of anchors**: `docs/b1-closure-plan.md` §1
reasoned about the cheapest *in-onset* pinning of a level and concluded
`T(2k+1,k+1)`, `T(2k+2,k+2)`, and every cost table in the campaign follows from
that. Below-onset cells are equally valid equations the moment `D_j` is exact,
and they are shorter. Two pieces of machinery that were built for different
purposes — the grand form for the tower, W3 for the certification map — turn
out to compose into a cheaper tower, and nothing else had to be true.

That is also why it was cheap to test: everything it needs was already in the
tree and already gated.

## Verify — 18 levels, every available depth pair

    grand form consistent on wired levels k = 1..19 (every residual linear in n)
    ab-initio depth series loaded for j = 1..3, k <= 19
      k= 2 ... k=19, each OK
    verify: 18 levels re-derived exactly over 100 depth pairs, 0 wrong, 1 skipped
    VERIFY GREEN

100 is the number of PAIRS, not of independent checks: pairs share cells, and
a level with `c` usable cells carries `c - 2` independent checks — about two
per level, ~36 in all at jmax 4. The conclusion is unaffected; the arithmetic
of "100" is not a count of independent evidence and was quoted as if it were.

Exactly — the same rationals, not agreement to some number of digits. The
`k = 19` line is the one that matters: **P₁₉ re-derived from `T(38,19)` and
`T(37,18)`, without `T(39,20)` or `T(40,21)`.**

RED controls (`--selftest`), all fire before the verify is believed:

- a perturbed `D_j` breaks the pin;
- one equation used twice is refused as singular;
- a corrupted lower level breaks the pin.

The grand form's own consistency is a fourth check and it is not optional:
`extract_ab` raises unless `P_k` minus the lower-level part is linear in `n` at
every wired level. It is.

## Predict — the cell that could not be swept

`--predict` pins past the wired table and prints what the tower then says:

    k=20 pinned, 3 depth pairs AGREE (2 independent checks);
         cells T(40,20), T(39,19), T(38,18)
    ...
    T(40,21) k=19: match

`T(40,21)` — the one cell `docs/b1-closure-plan.md` §3 says
"never fits", the reason its §6 table reads "out of RAM at any rung" — comes
out of the formula and matches the banked value. Every in-onset banked cell of
rows 40 and below that the tower touches matches; the run prints them.

Level 20, which the wired table never had, is pinned **overdetermined**: three
depth pairs, two independent checks, all agreeing. It predicts

    T(41,21) = 12639811314502944123098075912198
    T(42,22) = 66507597655339889181525572632880

and the whole `k ≤ 20` band of rows 41 and 42, none of which any sweep has
produced.

## What it costs, and what it buys

Coverage becomes `n ≤ 2·H_sweep + J - 1` for exact depths through `J`, against
`n ≤ 2·H_sweep` under the onset-anchor rule. Depths 1–4 are closed, so:

| target | old sweep ceiling | Undertow ceiling |
|---|---|---|
| a(40) | H = 21 (36.4 h, 363 GB disk) | H = 19 |
| a(41) | H = 21 at Nmax 41 | H = 19 |
| a(42) | H = 22 | H = 20 |

A height is ~3× compute, so the a(41) run stops needing both poles that
dominated a(40) — phase B (H20, 9.6 h/48c) and phase C (H21, 36.4 h/32c) — and
keeps only phase A's range, which was 6.3 h on 80 cores at Nmax 40.

**And the disk wall goes with them.** `results/ns_a40/rundir_size.log` by
phase: H <= 19 peaked at **69 GB**, H = 20 at 172 GB, H = 21 at 363 GB. The
memory `reach-scaling-and-resourcing` calls the engine disk/spill-bound and
puts the home boxes' ceiling there; the two heights Undertow removes are
exactly the two that dominate the disk. A ladder that stops at H = 19 has a
sub-100 GB footprint, which is a different resourcing conversation from a
363 GB one.

Deeper depths extend it one term per level. `D_j` needs excess ≤ j-1 cluster
families, and `cpp/severance_w3_families.cpp` takes `emax` as an argument;
measured on dalby, emax = 4 costs 12.2 s / 138 MB at K = 8, 71.4 s / 577 MB at
K = 10 and 265.0 s / 1.54 GB at K = 12 — about 1.82× per unit K in time and
1.6× in RSS. `families 21 4` (depth 5) extrapolates to roughly 16 h and 103 GB:
inside dalby, but at the wall, and it is the run that would let level 21 pin
from `T(39,18)` and `T(38,17)`, both inside Motley's already-banked H ≤ 18
rows — i.e. **a(40) rule-independent in every cell, with no new sweep at all.**

## The row-40 regression

`experiments/undertow_a41.py` runs the assembled tower back at n = 40, with
row 40 **excluded from its own pinning set** (level 20's depth-1 cell is
literally `T(40,20)`, and pinning from a cell you then call a prediction is
circular). Level 20 then pins from `T(38,18)` and `T(39,19)` alone — tallest
cell H = 19 — and:

    level k=20 pinned from [(38, 18), (39, 19)] (tallest H=19)
    row 40 regression: 21 cells reproduced, 0 wrong
    banked row 40 re-sums to a(40) exactly

Of those 21 cells, **one is a novel check**: `T(40,20)`, predicted from a
level-20 pin whose cells are all H <= 19. `T(40,21)` is `P_19`'s own fit
anchor, and the 19 cells at H >= 22 are `diagCoeffTable` evaluations that the
a(40) run *injected* rather than enumerated (`results/ns_a40/PROVENANCE.md`:
"Real sweeps H3-H21; H22-H40 via wired P_k closed forms"), so scoring the
tower against them is formula against formula. The RED control is a perturbed
level 20, and it fails the regression.

The transitively-clean statement is `undertow_ri.py`'s, not this one.

## a(n) is rule-independent for every n <= 39

`experiments/undertow_ri.py` answers each row with a tower that excludes that
row from its own pinning set, built from nothing the incumbent produced:

- levels 1..9 assembled from Severance W1's cluster weights themselves
  (`results/severance_w1_weights_k9.txt`), not from the wired table — also the
  only way to start, since level 1's depth-2 cell would be `T(1,0)`;
- levels 10..20 pinned from **Motley's own cells**, telescoped
  `T = C_H - 2C_{H-1} + C_{H-2}` out of `results/cutcount_b1/rows/`, every
  pinning cell at `H <= 18`;
- `D_j(k)`, j <= 4, ab initio from Severance W3;
- the grand form, a Lean-complete theorem.

```
row 30: Motley H<=18 (18 cells) + tower H>=19 (12 cells), 12 agree, 0 wrong -- COMPLETE, sum MATCHES a(30)
row 31: ... (13 cells) ... COMPLETE, sum MATCHES a(31)
row 32: ... (14 cells) ... COMPLETE, sum MATCHES a(32)
row 33: ... (15 cells) ... COMPLETE, sum MATCHES a(33)
row 34: ... (16 cells) ... COMPLETE, sum MATCHES a(34)
row 35: ... (17 cells) ... COMPLETE, sum MATCHES a(35)
row 36: ... (18 cells) ... COMPLETE, sum MATCHES a(36)
row 37: ... (19 cells) ... COMPLETE, sum MATCHES a(37)
row 38: ... (20 cells) ... COMPLETE, sum MATCHES a(38)
row 39: ... (21 cells) ... COMPLETE, sum MATCHES a(39)
row 40: Motley H<=18 (18 cells) + tower H>=20 (21 cells), 21 agree, 0 wrong -- GAP [19]
```

**HANDOFF's banked state was `a(n) closed rule-independently for all n <= 35`.
This is n <= 39** — four terms further, from data already on disk, no new
compute — **and a(40) short by the single cell `T(40,19)`.**

The tower band also agrees with the incumbent cell by cell at every row: 12,
13, 14, ... 21 cells at rows 30..40, 173 tall-cell confirmations on top of the
342-cell audit below.

Two bugs were found getting here, both in the direction of flattering the
result: forbidding every target row at once starved level 18 of pinning cells,
and the Motley band and the tower band overlapped at H = 17-18, double-counting
those cells (the "sum WRONG" on rows 34 and 35 was the double count, not a
wrong tower). Both fixed; the numbers above are after.

**"Nothing the incumbent produced" is now literal.** Levels 1..9 were at first
read out of the wired `diagCoeffTable` — Severance W1 matched that table
coefficient for coefficient, so the numbers were a second source's, but the
*file* was the incumbent's. They are now assembled straight from
`results/severance_w1_weights_k9.txt` through
`experiments/severance_w1_assemble.py`'s own `assemble_R`/`pk_from_R`, and the
grand form's linearity check is re-run on the result. Same answers; no
incumbent file is opened anywhere in the construction. (`read_tri()` is still
imported, but only to *compare against* — the thing being confirmed.)

## Row 40 is one cell short of rule-independent, from banked data alone

`experiments/undertow_ri.py` builds the tower with **nothing the incumbent
produced**:

- levels 1..9 from Severance W1's ab-initio `P_k` (cluster weights, matched
  the wired table coefficient for coefficient);
- levels 10..20 pinned from **Motley's own cells**, telescoped
  `T = C_H - 2C_{H-1} + C_{H-2}` out of `results/cutcount_b1/rows/`, every
  pinning cell at `H <= 18`, and row 40 excluded from its own pinning set;
- `D_j(k)`, j <= 4, ab initio from Severance W3;
- the grand form, a Lean-complete theorem.

```
levels 1..9 seeded from Severance W1's ab-initio P_k
levels 10..20 pinned from MOTLEY cells only (jmax=4, every pinning cell H<=18)
row 40: tower covers H = 20..40 (21 cells); 21 match the incumbent, 0 wrong
row 40: Motley covers H = 1..18 (18 cells)
row 40: GAP = [19]
```

**39 of row 40's 40 cells are rule-independent right now, with no new
compute.** `docs/motley-plan.md`'s table has the residual band at 5 cells
after Confetti and 3 after Ticker Tape; this is 1, and it is `T(40,19)` —
which a Motley H = 19 run retires outright. That run was priced at 27–40 days
and the parallel engine now puts it at ~11 h on dalby.

The Motley triangle agrees with the incumbent on all 720 cells they share
(H <= 18), which is the already-known part; what is new is that the tower
built on it reaches H = 20 and reproduces every tall cell of row 40.

## The parallel engine, at production scale

ayr, `cpp/motley_par.cpp`, H = 18 / Nmax 40, 32 threads, reproducing the five
banked Confetti residue rows (`results/cutcount_b1/residues/`):

    p=2147483647 wall=3316.25 rss_kb=60159508
    p=2147483647 IDENTICAL to banked Confetti row

Frontier `states=72487711` — the same count HANDOFF records for Confetti.
**3316 s per prime against Confetti's ~79,940 s**, i.e. 24x, on a box with
fewer cores than the one Confetti ran on. Four more primes to go; the runner
exits nonzero on any mismatch.

## Four terms reassembled from short sweeps

`experiments/undertow_a41.py --nmax N --max-swept-h H` runs the a(41) pipeline
against terms we already have. The cap applies to the **pinning as well as the
assembly** — a run that says "heights <= H" refuses to touch a taller cell
anywhere, which is what `all_pairs`' `hmax` is for. (It was not, at first: the
first a(39) and a(38) runs claimed H <= 18 while pinning level 20 from a cell
at H = 20. They now fail closed instead.)

| term | swept heights | classical ceiling `(n+2)/2` | result | Undertow content |
|---|---|---|---|---|
| a(40) | 1..19 | 21 | EXACT | level 20 pinned |
| a(39) | 1..19 | 20 | EXACT | **none — pin loop empty** |
| a(38) | 1..18 | 20 | EXACT | **none — pin loop empty** |
| a(37) | 1..18 | 19 | EXACT | **none — pin loop empty** |

**Three of those four rows contain no Undertow at all** (Lane A, verified:
`undertow_a41.py:186 kmax_new = n - (hcap+1)` is 19, 19, 18 for a(39), a(38),
a(37) against a wired table that already reaches k = 19, so the pin loop
`range(max(P)+1, kmax_new+1)` is empty). They are the classical assembly
replayed, and they consume wired constants fitted to cells ABOVE their own
stated cap — a(39)'s H = 20 value *is* the swept `T(39,20)`, laundered through
`P_19`'s two-parameter exact fit. Only the a(40) row pins anything.

The sentence "a run that says heights <= H refuses to touch a taller cell
anywhere" was written about `all_pairs`' `hmax`, which constrains only NEWLY
pinned levels. It is **not true of the wired levels** and should not have been
written without that qualification.

## The dry run: a(40) without phases B and C

`experiments/undertow_a41.py --nmax 40 --max-swept-h 19` runs the exact
pipeline a(41) will use, on the term we already have — heights 1..19 from the
banked sweep, heights 20..40 from the tower, row 40 excluded from its own
pinning set:

    level k=20 pinned from [(38, 18), (39, 19)] (tallest H=19)
    row 40 regression: 21 cells reproduced, 0 wrong
    banked row 40 re-sums to a(40) exactly
    edges exact: T(40,40) = 3^39, T(40,39) = (25n-45)*3^36
    heights swept: [1..19]
    heights from the tower: [20..40]
    DRY RUN GREEN: a(40) reassembled EXACTLY = 56749893611764175164545926946127

**a(40) comes out of heights 1–19 alone.** The two phases that dominated the
original run — phase B (H = 20 solo, 9.6 h on 48 cores) and phase C (H = 21
solo, 36.4 h on 32 cores, 363 GB disk peak) — are both replaced by the tower.
Phase A, the range this reproduces, was 6.3 h on 80 cores.

What the dry run *is*: the end-to-end demonstration that the pipeline produces
the right total on a known answer, which is what
`validate-at-scale-before-record` asks for before it is pointed at an unknown
one. What it is *not*: independent evidence beyond the 21-cell regression it
contains — the assembly consumes the same tower values the regression checks.
The independent evidence is the audit below.

## The triangle-wide audit

`--audit` does the row-40 regression for every level at once: pin level `k`
from its two SHORTEST available cells, then predict every in-onset banked cell
on that diagonal it did not use.

    k= 2 pinned at H<= 2 (depths (1, 2)); 36 banked cells predicted, 0 wrong
    ...
    k=15 pinned at H<=14 (depths (2, 3)); 10 banked cells predicted, 0 wrong
    ...
    k=19 pinned at H<=18 (depths (2, 3));  2 banked cells predicted, 0 wrong
    audit: 342 banked cells predicted from shorter cells, 0 wrong
    AUDIT GREEN

**189 cells of the banked triangle re-derived from strictly shorter cells**
(the audit prints 342; see the correction below).
The `k = 19` line is the tower's own foundations audited: the two cells it
predicts are `T(39,20)` and `T(40,21)` — *the very anchors the wired P₁₉ was
fitted from* — and it gets both, from H <= 18.

Note also `k = 15`, pinned at `H <= 14`: that is the strip engine's
independent range (`results/strip-engine.md`), so levels up to 15 can be
pinned from cells a second source already covers, with no dependence on the
production sweep at all.

Re-run at `--jmax 4`, where the shortest pair is `(3, 4)`, the same 342 cells
come back with 0 wrong from a **completely different pin**: level 19 now pins
at `H <= 17` and still predicts `T(39,20)` and `T(40,21)`, and levels through
16 pin at `H <= 14`. So `T(40,21)` — the 36.4-hour cell — is reachable from
data no taller than H = 17.

## What the coverage bound actually says (and the measurement it waits on)

With exact depths through `J` and a real sweep of heights `H <= Hs` at
`Nmax = N`, level `k` is pinnable when two depths `j1 < j2 <= J` both satisfy
`H' = k+1-j <= Hs` — which needs `J >= k+2-Hs`, i.e.

    k_max = Hs + J - 2,        rows complete for   n <= 2*Hs + J - 1.

Both pinning cells are then automatically inside the sweep: `n' = 2k+1-j <=
k + Hs <= 2Hs + J - 2 <= N`. Against the onset-anchor rule's `n <= 2*Hs`,
that is `J - 1` extra rows **from the same sweep height**.

At `Hs = 21` — the height a(40) already swept — and `J = 4` that reads
`n <= 45`. Whether that is real turns on one number nobody has measured: how a
**fixed-height** sweep's cost grows in `Nmax`. The ladder's famous 4.4x per
term is the cost of raising `Hs` AND `Nmax` together; at fixed `Hs` the
frontier is bounded by the height's own state space and only the column count
and payload width follow `Nmax`, which argues for polynomial. Arguing is not
measuring: `scripts/nmax_scaling.sh` runs heights 14 and 15 at
`Nmax = 40, 42, 45` on a fixed core count for exactly this ratio, and
`runs/a41_low` (H <= 19 at Nmax 41, against a(40) phase A's H <= 19 at Nmax 40,
6.3 h on 80 cores) is the same measurement at scale.

Until those land, the claim this file will stand behind is the narrow one:
**two heights off the sweep ceiling.** The several-rows-per-sweep version is
a consequence of the bound above and an unmeasured cost model, in that order.

Levels 20 through 23 would each carry only the `j = 3, 4` pair, so none of them
gets a cross-check without depth 5 — the same weakness level 21 has today, and
the same fix.

## Limits

- Levels 20 and 21 have no above-onset cell to cross-check against, by
  construction — that is the point of the method. Level 20's guard is the
  three agreeing depth pairs; level 21 has one pair until depth 5 exists, and
  should not be wired into `diagCoeffTable` before it has two.
- The depth identities are exact and derived, but they were *checked* against
  banked cells only at `k ≤ 19` (W3's 16–19 cells per depth). Using them at
  `k = 20, 21` is extrapolation of a derivation, not of a fit — but it is
  extrapolation, and the agreeing-pairs test is what stands in for a holdout.
- Everything below level 10 rests on Severance W1's ab-initio `P_k`; above it,
  on the wired table. Undertow does not change that dependency, it moves which
  *cells* the wired table needs.


---

# Corrections, from the Lane A audit

`results/undertow-review-A.md`, 2026-08-20. An adversarial audit of the four
headline claims. Every correction below was verified by the lead before being
written in.

| claim | grade | what changed |
|---|---|---|
| `a(n)` rule-independent for `n <= 39`, gap `T(40,19)` | **CLEAN** | strengthened: rows 19..39 all COMPLETE, not just 30..39 |
| a(41) | **CLEAN on circularity** | one addition, below |
| 342 cells from shorter cells | **weaker than stated** | 189 enumerated + 153 formula-vs-formula identities |
| four terms from short sweeps | **weaker; three rows circular as independence claims** | see the table above |

**The one fact that reprices most of the checks.** The banked triangle's
H >= 22 cells are not enumerations — the a(40) run wrote `diagCoeffTable`
evaluations into `h22.out..h40.out`. Lane A verified all 171 in-onset banked
cells at H >= 22 equal the wired-law evaluation exactly. Since `extract_ab`
and `grand_form` are an exact inverse pair, any tower built on wired levels
evaluates to identically the polynomial the run injected, and every
"tower reproduces the banked cell" comparison up there is guaranteed. Worth
one line — "Python and Go evaluate the same polynomial the same way" — not
153.

**What is genuinely strongest**, per Lane A and I agree: the audit's 189 real
cells include `T(39,20)` and `T(40,21)` predicted from H <= 18 pins (H <= 17
at jmax 4). Every level up to 17 already had a holdout; **18 and 19 never
did**. That is the first independent cross-check wired `P_19` has ever had.

**Two further defects found**, both now open:

- `undertow_ri.py` crashes on rows <= 18 (`min()` on an empty tower band), so
  the pure-Motley rows are claimed but not attestable by the script. They
  reduce to the 720-cell Motley agreement, which holds — the attestation is
  the gap, not the claim.
- The `k = 20..22` rows of `results/severance_w3_families_K22_e*.txt` rest on
  the C++ enumerator alone; the Python cross-check stops at K = 19. The
  extrapolation past W3's validated range has a **software** leg as well as a
  mathematical one.

**Also vacuous, and harmless**: in the a(40) dry run,
`sweep_agrees_with_banked` compares `results/ns_a40/perheight` against
`read_tri()`, which reads that same directory — file against itself. The same
check inside the real a(41) run is real (760 cells, cross-Nmax, 0 disagree).
