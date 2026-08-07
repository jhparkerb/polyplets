# Both ends of the perimeter table: a triangular onset at one, a linear one at the other

2026-08-07. Extends `results/perimeter-defect-diagonals.md`, which graded
`A(n,p)` by `k = pmax(n) - p` only. The table has two boundary curves; this
pass grades from both and asks what each end's ladder looks like.

## The answer in one paragraph

The two ends are structurally different objects and the difference is sharp.
At the **maximum** end the extremal animals are sticks, the classes are
quasi-polynomials of degree exactly `k` in `n`, and their onsets follow
`onset(k) = k(k+1)/2 + 3` — **triangular**, the law
`perimeter-defect-diagonals.md` looked for and did not find. At the **minimum**
end the extremal animals are balls of the adjacency metric, the natural row
index is `p` rather than `n`, and the classes are **eventually constant** in `p`
with onset `4i + const` — **linear**. On the king lattice those constants are
exactly a convolution of the **4-coloured partition function** with the
box-skew deficits, verified at `i = 0..6` and confirmed at the mechanism level.
On square4 the ladder stabilises too but its constants are a *different*
combinatorial object — `1, 4, 18, 60, 187` where king has `1, 4, 14, 40, 105`.
So the lattices agree on leading structure at the max end and disagree at the
min end from the first nontrivial term.

## The maximum end: the onset law is triangular

`experiments/perimeter_max_structure.py` re-derives each defect class's onset
from the census (largest `n` where the fitted closed form fails, plus one)
rather than reading it off the write-up. On **both** lattices:

| k | period | degree | onset | `T_k + 3` |
|---|---|---|---|---|
| 2 | 1 | 2 | 6  | 6  |
| 3 | 2 | 3 | 9  | 9  |
| 4 | 2 | 4 | 13 | 13 |
| 5 | 6 | 5 | 18 | 18 |

    onset(k) = k(k+1)/2 + 3        for k >= 2

Four consecutive hits on each lattice. `k = 0, 1` are the degenerate exceptions
that hid the law (onsets 2 and 3, against 3 and 4), which is why a scan of
`2, 3, 6, 9, 13, 18` as a whole found nothing. **Predicts `onset(6) = 24` and
`onset(7) = 31`** — untested, see "What this run did not buy" below.

### The recentred basis is non-negative integers

The partial-fraction basis `1/Phi_1^j -> C(n+j-1, j-1)` is centred at `n = 0`,
which is why its coefficients are the ugly rationals of
`perimeter-defect-diagonals.md`. Re-expand each residue class in `C(m, j)` with
`m = (n - n0)/period` stepping along the class from its first in-regime point,
and **every coefficient is a non-negative integer**, on both lattices, for
`k = 2..5`, in every residue class. Examples (king, then square4):

    k=2        92, 48, 12                    60, 40, 12
    k=3 r=1  1528, 1868, 1164, 312          856, 1324, 1004, 312
    k=4 r=1 45753, 48873, 32438, 12484, 2176    22993, 30293, 24222, 10956, 2176

The leading coefficient is lattice-independent (`312`, `2176`, `3842640` for
`k = 3, 4, 5`) — it is `c_k * k! * period^k`, so this is the known
leading-diagonal universality in integer form, not a new one. Everything
beneath it is lattice-specific, exactly as in the partial-fraction triangle.

Defining the recentring at all needs the onset law, so this is downstream of it.

### Two doors closed

- **The onset is not the positivity threshold.** The `C(m,j)` coefficients are
  forward differences, so non-negativity says the class counts are built by
  choosing `j` things out of `m`. Tempting, but the least `n0` with all forward
  differences non-negative is strictly *below* the onset in every class on both
  lattices (`k=5`: threshold 12 against onset 18). Positivity is real and the
  onset is real; neither explains the other.
- **The numerators are not non-negative.** `G_k` carries a polynomial part
  holding the pre-onset holdouts, so testing the numerator of the full `G_k` is
  meaningless (that was the first answer, and it was noise). Done properly on
  the tail series, `Ntilde_k = (sum_{n>=onset} A(n,k) x^n) * D_k / x^onset` is a
  polynomial of degree exactly `deg D_k - 1` — a fresh confirmation of the
  predicted cyclotomic denominators — but its coefficients change sign from
  `k = 2` on. There is no positive numerator over `D_k`.

`deg Ntilde_k = 0, 1, 3, 5, 7, 11` for `k = 0..5`, consistent with the linear
growth a rational `F(x,y) = sum_k G_k(x) y^k` would need, but six terms across
two denominator regimes do not settle it.

## The minimum end: a different kind of ladder

`pmax(n)` is linear in `n`, so at the max end `n` and `p` are interchangeable.
`pmin(n)` grows like `sqrt(n)` and is a **step function**, so an `n`-indexed
ladder there has columns polynomial in `sqrt(n)` at best. The right row index is
`p`, with `nmax(p) = max{n : pmin(n) <= p}` and

    C(p, i) = A(nmax(p) - i, p).

`pmin` itself is not ours and is not refitted: square4 is A261491
(`ceil(2 + sqrt(8n-4))`), king is A235382 (`2*ceil(2*sqrt(n)) + 4`), both
already banked in `results/min-site-perimeter.md` and both re-verified against
the census here before anything else runs.

### Getting the data: complementation, not growth

The max-end prune works because `k = pmax(n) - p` is monotone under cell
addition. `p - pmin(n)` is **not** — adding a cell can lower it — so there is no
growth prune at this end at all. What replaces it is that near-minimal animals
are *fat*: they fill their own bounding box up to a few cells. `cpp/perimeter_min.cpp`
enumerates boxes and removes small subsets, at `sum_r C(M,r)` rather than
anything exponential in `n`. square4 is worked in the rotated frame `u = x+y`,
`v = x-y`, where the four rook neighbours become the four diagonals and a
diamond — which fills no `(x,y)` box — is exactly a parity-restricted box.

Completeness rests on **(H1)**: every animal's perimeter is at least its own
filled frame bounding box's. Given (H1), an animal at area deficit `i` has at
most `i` removals. (H1) is asserted at runtime and tested from outside by
`make gate-perimeter-min`, which runs with removals unbounded on small boxes —
where the program degenerates to a complete brute force — and compares cell for
cell against `build/g2 --siteperim`, a different search entirely. A violation
would surface as a missing animal. 33 and 52 `(n,p)` cells agree; a RED control
confirms the two lattice modes are not computing the same thing.

Reached `p <= 40` on king (`n` to 81) and `p <= 24` on square4 (`n` to 61),
against the `n <= 14` and `n <= 20` the brute-force censuses stop at.

### King: the ladder is the 4-coloured partition function

`C(p, i)` is eventually **constant** in `p` along each residue class mod 4, and
the constants are exactly

    p = 0 mod 4:  C(i) = q4(i) + 2 * sum_{s>=1} q4(i - s^2)
    p = 2 mod 4:  C(i) = 2 * sum_{s>=0} q4(i - s(s+1))
    p odd:        0

with `q4(j) = [x^j] prod_n (1-x^n)^-4 = 1, 4, 14, 40, 105, 252, 574` the
4-coloured partition numbers. Measured against predicted, `i = 0..6`:

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| `p = 0 mod 4` | 1 | 6 | 22 | 68 | 187 | 470 | 1106 |
| `p = 2 mod 4` | 2 | 8 | 30 | 88 | 238 | 584 | 1360 |

**All fourteen match exactly.** Two mechanisms are doing the work and both are
checked directly rather than inferred:

- *Where `q4` comes from.* Removing a corner cell of a filled king box drops one
  ring cell and adds the removed cell: net zero. So the perimeter-preserving
  removals are a Young diagram at each of the 4 corners, giving `P(x)^4`. The
  per-box free-removal counts (`--boxes`) converge to `1, 4, 14, 40, 105, 252,
  574` term by term, and converge *exactly* when the box side exceeds the
  removal count: `W=5` is right to `j=4`, `W=6` to `j=5`, `W=7` to `j=6`.
- *Where the period 4 comes from.* At semi-perimeter `S = w+h` the balanced box
  is optimal and a skew of `s` costs `s^2` cells when `S` is even and `s(s+1)`
  when odd. Different deficit sets, hence different columns, hence period 4
  in `p`.

**Stabilisation onset:** `p* = 4i + 8` for `p = 0 mod 4` and `4i + 10` for
`p = 2 mod 4`, exact for `i = 0..6`. Both say the same thing — the balanced box
side must exceed `i` — and both are **linear** in the deficit, against the max
end's triangular `T_k + 3`.

### What decides whether a column stabilises: attainability, not parity

King's odd-`p` rows do not stabilise at all — they grow. It is tempting to call
that a parity effect, and wrong: square4's odd-`p` rows stabilise perfectly well.
The actual rule, tested on both lattices by
`experiments/perimeter_min_attainability.py`, is

    C(p, .) stabilises  <=>  p is ATTAINED as pmin(n) for some n.

King's `pmin = 2*ceil(2*sqrt(n)) + 4` is always even, so **no** odd `p` is ever
an isoperimetric perimeter, and every odd column counts animals that are one
unit worse than any optimum — a different population, with a positional freedom
along the boundary that grows with it. square4's `pmin = 2 + ceil(sqrt(8n-4))`
attains every integer in range **except 5**, and correspondingly every one of
its four columns stabilises. The hypothesis is checked class by class against
the measured stabilisation and holds on both lattices with no exceptions.

The non-attained columns are not structureless — they are quadratic in `p`:

    p = 1 mod 4, i=1:  (p^2 - 10p - 39)/16
    p = 3 mod 4, i=1:  (p^2 - 10p - 43)/8
    p = 1 mod 4, i=2:  (3p^2 - 30p - 197)/8

fitted exactly with holdouts. Higher `i` needs `p` past 40 to overdetermine.

### A third lattice: tri6, and the period follows the ball

The stabilisation law is not a two-lattice coincidence. `tri6` (the 6-neighbour
triangular/hex lattice, g2's own offsets) was added to the enumerator and gated
against `build/g2 tri6 --siteperim` the same way — 35 `(n,p)` cells, exact.

It needed a genuine generalisation. The complement trick works only when the
lattice's isoperimetric shape is a **full hull**, and a hex ball is a HEXAGON,
which is not a parallelogram in any linear frame. So the hull family became a
range on each of a list of linear functionals: `u, v` for the square lattices
(a rectangle — the old behaviour exactly), and `u, v, u+v` for tri6 (a hexagon).

With that, tri6's ladder stabilises too — but with **period 6, not 4**. At
`p <= 30`, `i = 0` and `i = 1` are stable in all six classes:

    C(p, 0) =  1,  6,  3,  2,  3,  6    for p = 0..5 mod 6
    C(p, 1) = 14, 42, 27, 24, 27, 42

the `1` falling on `p = 0 mod 6`, where the hull is the perfect hexagon and is
unique.

**And the whole king model transfers, with `q6` for `q4`.** The king form was

    C(p, i) = sum over hulls H with pbox(H) = p of q_c(i - deficit(H))

with `deficit(H) = nmax(p) - |H|` and `c` the hull's corner count. Feeding tri6's
hull inventory (areas and multiplicities straight out of `--boxes`) and `q6` into
that formula, with **nothing fitted**, reproduces every settled column:

    18 of 18 settled columns agree, 0 mismatches
    (p=30: i=0..3 -> 1, 14, 87, 392; p=25..29: i=0..2 across the other classes)

So the min-end law is lattice-general rather than a fact about boxes: the hull
family supplies the deficits, the corner count supplies the exponent, and the
partition function does the rest. `experiments/perimeter_min_hex_model.py`.

So across three lattices the shape of the law is the same — eventually constant
in `p`, onset growing with `i` — and the **period is set by the isoperimetric
shape**: 4 for the square and diamond hulls, 6 for the hexagonal one.

### The free-removal factor is P(x)^(corners)

The mechanism generalises with it, and sharply. Measured directly on a single
large hull (`--only`), the perimeter-preserving removal counts are

    king, square box (4 corners), W=7:   1, 4, 14, 40, 105, 252, 574   = [x^j] P(x)^4
    tri6, hexagon    (6 corners), r=4:   1, 6, 27, 98, 315             = [x^j] P(x)^6

with `P(x) = prod 1/(1-x^n)`, each converging term by term as the hull outgrows
`j`. So the per-hull factor is `P(x)^c` with `c` the number of corners of the
isoperimetric hull: a Young diagram at each corner, independently, exactly as
the king argument said — and the hexagon confirms it was a general argument
rather than a fact about boxes.

**square4 is the exception, and its exception is informative.** Its diamond
gives `1, 4, 18, 60, 187, 524` (converged to `j=5`; `W=11` and `W=13` agree),
which is not `P(x)^4` — it is larger from `j=2` on (18 against 14). Taking a
4th root gives a per-tip series `1, 1, 3, 5, 9, 14`, not the partition numbers
`1, 1, 2, 3, 5, 7`. The reading — interpretation, not measurement — is that
`P(x)^c` needs the hull's corners to be LATTICE-ALIGNED, i.e. to span the
lattice's own quadrant. King's box corners and the hexagon's corners are;
square4's diamond tips are 90 degrees off the rook lattice, so the removable
shapes there are not plain Young diagrams.

**The per-tip series is A120452** (jasonp's lookup, 2026-08-07):
`1, 1, 3, 5, 9, 14, 23, 34, 52, 75, 109, ...`, which OEIS also characterises as
the integer partitions of `2n` with exactly two odd parts, one of which is the
greatest, and as those with reverse-alternating sum 2. So the diamond tip's
removable shapes are a known object, not a new one, and the series continues
`23, 34, 52` — which predicts square4's `j = 6, 7, 8` free-removal terms.

### A near miss that had to be measured, not argued

`P(x)^6` was claimed for the hexagon on data converged only to `j=4`
(`1, 6, 27, 98, 315`). Those five terms are also the opening of **A071734**,
`p(5n+4)/5` — Ramanujan's congruence — because
`sum p(5n+4) x^n = 5 * prod (1-x^{5n})^5 / (1-x^n)^6`, i.e. A071734 is exactly
`P(x)^6` corrected by `prod (1-x^{5n})^5 = 1 - 5x^5 + ...`. The two agree to
`j=4` and part at `j=5`: **918** against **913**.

Measured on an `r=5` hull (`--only 11 11 -1 5 15`): **918**. So it is `P(x)^6`
and the Ramanujan sequence is a coincidence of the first five terms. Each hull
radius has bought exactly one more correct term (`r=3` right to `j=3`, `r=4` to
`j=4`), so `r=5` is the first hull that can see `j=5` at all.

The lesson is the one worth keeping: five converged terms and a clean structural
argument were still not enough to exclude a different classical sequence.

### square4: stabilises, but not to the same numbers

All **four** residue classes stabilise here, not just the even ones. Values are
held to a bar of three equal entries at the top of the range; `?` marks the one
with only two. Extending the run to `p <= 28` promoted every value that the
`p <= 24` pass could only call provisional:

| | i=0 | i=1 | i=2 | i=3 | i=4 | stabilises from |
|---|---|---|---|---|---|---|
| `p = 0 mod 4` | 1 | 9  | 52  | 206 | 719 | `p* = 4i + 4` |
| `p = 2 mod 4` | 4 | 22 | 106 | 392 | -   | `p* = 4i + 6` (i>=1) |
| `p = 1 mod 4` | 4 | 28 | 124 | 456? | -  | `p* = 4i + 9` |
| `p = 3 mod 4` | 4 | 28 | 124 | 456 | -   | `p* = 4i + 7` |

So the linear stabilisation onset holds on this lattice too, exactly, with a
different constant per class — four or five points per class, no exceptions
above `i = 0`. The two odd classes agree with each other on every value that
converged. `C(p,0) = 1` when
`p = 0 mod 4` (the perfect diamond, unique) and `4` otherwise (a partial layer
in four rotationally equivalent positions), with `p=6` the small-`n` exception.

The free-removal factor is **not** `q4`. Measured on single large boxes
(`--only`), the diamond's perimeter-preserving removal counts converge to

    1, 4, 18, 60, 187        (agreeing at W=9 and W=11; j=5,6 not yet converged)

against king's `1, 4, 14, 40, 105`. They first differ at `j=2`: 18 against 14.
Taking a 4th root gives a per-tip series `1, 1, 3, 5, 9` — not the partition
numbers `1, 1, 2, 3, 5`. A diamond tip is a sharper corner than a box corner and
admits more perimeter-preserving removals; what counts them is open.

So the two lattices agree at the max end on period, degree, onset and leading
coefficient, and disagree at the min end on the very first nontrivial constant.

## What this run did not buy

- **`k = 6` at the max end was not run.** It tests four live predictions at
  once: `onset(6) = 24`, the `Phi_2` leading diagonal's `15/4`, whether the
  `Phi_3` exponent is `k-4` (that slope rests on a single data point at `k=5`),
  and whether `Phi_4` stays absent. Measured cost: `k=6` is ~12x `k=5` per `n`
  (king `n=26`: 3.0 s -> 29.6 s; `n=30`: 8.0 s -> 94.1 s), and `k=5` to `n=70`
  took 2017 s king / 913 s square4, so `k=6` to `n=70` is **3-7 hours
  single-core** and `perimeter_defect` has no sharding. A period-6 degree-6 fit
  with holdouts needs `n` near 78. Over the ask-first bar; not launched.
- **square4's free-removal counts at `j = 5, 6`** need `W = 13` (85 cells,
  `C(85,6) = 4.5e8`), and `--only` runs one box on one thread, so it did not
  finish inside the 10-minute budget given it. The `j <= 4` values are converged
  and are what is reported.
- **No OEIS lookups were run** on any sequence here — `1, 4, 18, 60, 187`, the
  per-tip `1, 1, 3, 5, 9`, and the stable square4 columns are all unchecked
  against the literature and against OEIS.

## Reproduce

    make gate-perimeter-min                       # must print GATE PASSED
    scripts/run_perimeter_min.sh                  # 571 s + 77 s wall, 10 threads
    python3 experiments/perimeter_min_model.py results/perimmin_square8_p40_r6.txt --lattice square8
    python3 experiments/perimeter_min_model.py results/perimmin_square4_p24_r6.txt --lattice square4
    python3 experiments/perimeter_min_ladder.py results/siteperim_square4_n20.txt --lattice square4
    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n70_k5.txt --lattice square8
    python3 experiments/perimeter_max_structure.py results/perimdefect_square4_n70_k5.txt --lattice square4
    ./build/perimeter_min square4 99 6 --only 11 11 0     # a single large box

Census data kept: `results/perimmin_square8_p40_r6.txt` and
`results/perimmin_square4_p24_r6.txt` (`n p count`, with the completeness domain
in the header), plus their `.log` provenance.

## OEIS status of the seven series

Looked up by jasonp, 2026-08-07 (external services are his call, so none of this
was run from here). Two hits, five apparent novelties:

| | series | result |
|---|---|---|
| S1 | square4 diamond free-removals `1, 4, 18, 60, 187, 524` | **no match** |
| S2 | square4 even-W hull free-removals `1, 6, 25, 88, 272, 766` | **no match** |
| S3 | per-tip `1, 1, 3, 5, 9, 14` | **A120452** |
| S4 | hexagon free-removals `1, 6, 27, 98, 315, 918` | `P(x)^6`; A071734 matched the first five terms and is refuted at the sixth |
| S5 | tri6 `C(p,0)` `1, 3, 2, 3, 6, 1, 6, ...` | **no match** |
| S6 | king min-perimeter stable columns | **no match** (though the model explains them) |
| S7 | square4 min-perimeter stable columns | **no match** |

"No match" is OEIS's answer to the terms I had, not a novelty proof: S1 and S2
carry six terms and S7 four or five, which is thin. S6 is the interesting one --
it has a complete model here (`q4` convolved with the box-skew deficits) and yet
is not in OEIS, so it is a derived-but-unrecorded sequence rather than a mystery.

## Status of these claims

The `pmin` closed forms are published (A261491, A235382) and only verified here.
The king min-end model is **measured and mechanism-checked, not proved**: `q4`
is confirmed as the per-box free-removal limit by direct count rather than by a
bijection, and the "box side exceeds `i`" convergence rule is read off the data.
The onset law `T_k + 3` is an exact fit at four points per lattice with the
degenerate `k < 2` excluded — a conjecture with good support, not a theorem. The
enumerator's completeness rests on (H1), which is checked exhaustively only on
the small boxes `gate-perimeter-min` reaches. Novelty is unchecked throughout.
