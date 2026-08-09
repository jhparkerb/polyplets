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
shapes there are not plain Young diagrams. The next section closes this: the
tip counts order ideals of its tangent cone, `P(x)` is the lattice-aligned
special case, and square4 stops being an exception at all.

### A120452 is refuted at its seventh term, and the exception dissolves

**A120452 was a six-term coincidence.** jasonp's 2026-08-07 lookup matched the
per-tip series `1, 1, 3, 5, 9, 14` to A120452 (partitions of `2n` with exactly
two odd parts, the greatest among them), which continues `23, 34, 52`. That
predicts square4's `j=6` free-removal term as `1384`. The `W=13` diamond
measured `1388`, and the `W=15` probe (2026-08-07, `results/perimmin_free_15_15_0.txt`,
r=7 diamond, 113 cells) measures `1388` as well. Two hull radii agree, so `j=6`
is converged and the convergence rule `W = 2j+1` holds. The per-tip series is
`1, 1, 3, 5, 9, 14, 24`, and A120452's `23` is wrong. The discrepancy `1388 - 1384 = 4`
is exactly `4 x (24 - 23)`, i.e. the four tips are still independent; only the
tip series was misidentified.

**What the tip actually counts: order ideals of its tangent cone.** A king box
corner spans the lattice's own quadrant `{a >= 0, b >= 0}`, whose finite order
ideals are Young diagrams, hence `P(x)`. Undo the diamond's 45-degree rotation
and a square4 tip is instead the cone

    C = {(a, b) in Z^2 : a >= |b|}

Put `u = a - b`, `v = a + b`. That carries `C` to the index-2 sublattice

    Q = {(u, v) in Z_{>=0}^2 : u = v (mod 2)}

under the componentwise order. Writing a finite downset by its column sizes
`a_i = c_{2i}`, `b_i = c_{2i+1}` gives exactly

    a non-increasing, b non-increasing, a_i >= b_i, b_i >= a_{i+1} - 1

equivalently pairs of partitions `(lambda, mu)` with `mu` contained in `lambda`
and `lambda` minus its first row and column contained in `mu`, weighted by
`|lambda| + |mu|`. Setting the `-1` offset to `0` collapses `lambda = mu` and
recovers `P(x)`, which is the king control. Counting them
(`experiments/cone_order_ideals.py`) gives

    tip:      1, 1, 3, 5, 9, 14, 24, 35, 55, 81, 120, 171, 248, ...
    control:  1, 1, 2, 3, 5,  7, 11, 15, 22, 30,  42,  56,  77, ...   = P(x)

and the 4th power is

    1, 4, 18, 60, 187, 524, 1388, 3452, 8229, 18800, 41536, ...

matching every measured square4 diamond term including the `1388` that killed
A120452. The model has no free parameters; it is derived from the cone, not
fitted.

**So the min-end law is lattice-general with no exception.** Each corner of the
isoperimetric hull contributes the order-ideal generating function of its
tangent cone intersected with the lattice; `P(x)` is the special case of a
lattice-aligned (unimodular) cone, which is why king boxes and tri6 hexagons
give `P(x)^4` and `P(x)^6`. square4's diamond tips are unimodular-failing and
give `C^4`. Three lattices, one statement.

### The tip series is A053993: Andrews' generalized Frobenius partitions

Looked up from here (jasonp authorised direct `curl` against oeis.org,
2026-08-07). `1, 1, 3, 5, 9, 14, 24, 35, 55, 81, 120, 171, 248, ...` is
**A053993 = phi_2(n)**, Andrews' generalized Frobenius partitions allowing up to
two repetitions of an integer in a row (Memoirs AMS 301, 1984). All 31 computed
terms agree with the OEIS data. That gives the tip factor an explicit infinite
product, Andrews eq. (5.9):

    G_tip(x) = prod_{k>0} [ (1-x^k)(1-x^{12k-10})(1-x^{12k-9})
                            (1-x^{12k-3})(1-x^{12k-2}) ]^{-1}

verified against the cone count to `n = 40` (`andrews_phi2()` in
`experiments/cone_order_ideals.py`, asserted at runtime). Equivalently the eta
quotient `q^{1/12} eta(q^4) eta(q^6)^2 / (eta(q) eta(q^2) eta(q^3) eta(q^12))`.
The Euler exponents measured here (`1, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1`
repeating) are exactly A053993's known period-12 Euler transform.

**Do not call this a closed form.** It is an infinite product, and calling it
closed would be the goat-grazing kind of answer. What it actually is is an eta
quotient, which is precisely the status of `P(x) = prod 1/(1-x^n)` that it
generalises: the tip factor is no more and no less explicit than the partition
function at a lattice-aligned corner. That is the honest claim, and it is
already the useful one, since a modular eta quotient carries its own asymptotic
(`phi_2(n) ~ exp(2*pi*sqrt(2n)/3) / (6*sqrt(2)*n)`, Kotesovec) and its own
transformation theory. square4's whole diamond min-end generating function is
`G_tip(x)^4`.

This makes the min-end law sharper still. Andrews' `phi_1` **is** the partition
function, so both cases we actually meet are the same family:

| corner | cone and coset | factor | OEIS |
|---|---|---|---|
| king box, tri6 hexagon | unimodular (index 1) | `phi_1 = p(n) = P(x)` | A000041 |
| square4 sharp tip | index 2, apex ON the lattice | `phi_2` | A053993 |
| square4 bevel | index 2, apex OFF it | `D` | A201077 |

The coset is not a detail: the same cone gives two different factors depending
on whether its apex is a lattice point. See the bevel section below.

**The obvious generalisation is false, and it is worth recording as closed.**
`phi_m` for an index-`m` cone fails at `m = 3`: the cone spanned by `(1,0)` and
`(1,3)` has order-ideal series `1, 1, 4, 8, 14, 24, 39, 64, 105, 161, 244, 370`,
whereas `phi_3` is **A053992** = `1, 1, 3, 6, 11, 18, 31, 49, 78, ...`. The
index-3 series is not in OEIS at all. This is not surprising in hindsight:
Andrews' `phi_k` are all *two*-rowed objects, and index-`m` cones stop being
unique up to `GL_2(Z)` at `m = 3` (Hirzebruch-Jung), so there is no single
"index-3 cone" for a formula to name. The identity is real for `m <= 2` and
that is all we need, since no lattice in this campaign produces a sharper tip.

Beware re-looking-up the tip series with six terms: A120452 matches
`1, 1, 3, 5, 9, 14` and will come back instead.

### CONFIRMED: `j = 7` and `j = 8` are `3452` and `8229`

The prediction was `3452` and `8229`, and reaching `j = 8` needed `W = 17`
(145 cells), over the old `kMaxCells = 128` u128 limit. The four-word mask
bought it, and `scripts/dalby_square4_deep.sh` ran both radii on dalby:

| box | cells | wall | nodes | free removals `j = 0..8` |
|---|---|---|---|---|
| `W=15` `r8` | 113 | 1h 24m | 5.5e11 | `1 4 18 60 187 524 1388 3452` **`8193`** |
| `W=17` `r8` | 145 | 18h 22m | 4.2e12 | `1 4 18 60 187 524 1388 3452` **`8229`** |

`j = 7 = 3452` at both radii, which is the campaign's convergence standard, and
it is the model's value. `j = 8` is `8229` at `W = 17`, also the model's value,
but the two radii **disagree** there — so on the standard as stated, `j = 8` had
one radius and not two.

**The `8193` is the box running out, not the model being wrong.** A free removal
is an order ideal in a tip cone, and a single column driven straight down the
axis of one tip needs that tip to be `j` cells deep. A radius-`r` diamond has
depth `r`, so it can hold every ideal up to size `r` and starts losing them at
`r + 1`. `W = 15` is `r = 7`: correct through `j = 7`, short at `j = 8`, by the
36 ideals that do not fit.

That is a claim about geometry, so it was measured rather than argued.
`experiments/diamond_free_removals.py` counts free removals directly — grow the
removal set one cell at a time, keep the ones that stay perimeter-neutral and
connected — which is a different algorithm from `cpp/perimeter_min.cpp`'s
enumerate-all-subsets-and-filter, on a different implementation in a different
language. It reproduces **both** measured rows exactly, all 18 terms, and being
incremental it reaches radii the C++ cannot afford:

    r=5   W=11   1 4 18 60 187 524 1360
    r=7   W=15   1 4 18 60 187 524 1388 3452 8193
    r=8   W=17   1 4 18 60 187 524 1388 3452 8229 18760 41268
    r=9   W=19   1 4 18 60 187 524 1388 3452 8229 18800 41492  88628 184027
    r=10  W=21   1 4 18 60 187 524 1388 3452 8229 18800 41536  88876 185031
    r=11  W=23   1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185303
    r=12  W=25   1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185355
    model        1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185355

(`r=5` and `r=6` are in `scripts/perimeter_min_gate.sh` as check E, where the
C++ and this script are compared row against row on every run.)

So `W = 19` gives `j = 8 = 8229` as well, and so do `W = 21`, `W = 23` and
`W = 25`: **`j = 8` has five agreeing radii**, and the prediction is confirmed
on the campaign's own standard several times over. The ladder carries three more
predicted terms to that standard — `j = 9 = 18800` at four radii,
`j = 10 = 41536` at three, `j = 11 = 88924` at two — and offers
`j = 12 = 185355` at one.

The truncation rule the table shows is exact and worth keeping, because it says
how far to trust any future box: **radius `r` reproduces the model through
`j = r` and undercounts from `j = r + 1` on.** Every radius here breaks exactly
where that says it should — `5` at `6`, `7` at `8`, `8` at `9`, `9` at `10`,
`10` at `11`, `11` at `12` — and every term below its break is the model's;
`r = 12` runs out of `j` before it runs out of hull. Read backwards it is a cost
model: a term `j` needs `W = 2j+1`, and what the enumerator costs in that box is
what the 18-hour `W = 17` run showed.

**The model is now measured, not extrapolated, through `j = 11`.** It was fitted
to nothing in the first place — it is derived from the tangent cone — so the
four fresh terms are four predictions kept, on top of the `1388` that killed
A120452.

### RESOLVED: the corner inventory was wrong, and the missing type is the BEVEL

The `W=14 parity=0` hull (6 corners, `1, 6, 25, 88, 272, 766, 2012`) and the
`W=15 parity=1` hull (8 corners, `1, 8, 36, 128, 398, 1120, 2924`) fit no
product `P^a C^b`, and my first two explanations were both wrong. It was not
unconvergence: `W=16` measures `1, 6, 25, 88, 272, 766, 2012`, identical to
`W=14`, so the 6-corner family's `j=6` is converged at `2012`. And it was not a
failure of independence. **The corner inventory was wrong.**

Look at the parity constraint in the rotated frame. A square4 frame is the box
`{0 <= u < W, 0 <= v < H}` restricted to one class of `u+v`, and whether the
box's own corner cell survives that restriction depends on the parity:

| frame | box corners kept | corners | decomposition |
|---|---|---|---|
| odd `W`, parity 0 | all 4 (`u+v` even at each) | 4 sharp | `C^4` |
| even `W`, parity 0 | 2; the other 2 are cut | 2 sharp + 2 bevels | `C^2 D^2` |
| odd `W`, parity 1 | 0; all 4 are cut | 4 bevels | `D^4` |

A cut corner does not vanish, it becomes a two-cell **bevel** — which is why the
`j=1` counts are 4, 6 and 8 rather than 4, 4 and 4. The bevel is the same cone
`{a >= |b|}` with its apex landing on the OTHER coset of the index-2
sublattice, so the apex cell is absent and the corner presents two minimal cells
instead of one. Its order-ideal series is

    D = 1, 2, 3, 6, 10, 16, 26, 40, 60, 90, 131, 188, 269, ...

**This is a real prediction, not a fit.** `D` was extracted from the even-`W`
family (`m6 / C^2`, square root, all coefficients integral and non-negative) and
then predicts the odd-`W` parity-1 family with nothing left free:

    D^4       = 1, 8, 36, 128, 398, 1120, 2924
    measured  = 1, 8, 36, 128, 398, 1120, 2924

all seven terms. And `D` falls out of its own cone poset directly — the odd
coset of `{(u,v) >= 0}` — with no reference to any measurement.

**`D` is A201077**, and it is an eta quotient like `phi_2`:

    D(x) = 1 / prod_{i>0} (1-q^{2i-1})^2 (1-q^{12i-8})(1-q^{12i-6})
                          (1-q^{12i-4})(1-q^{12i})

verified against the cone count to `n = 24` and asserted at runtime.

**The six-term trap fired a third time and was caught.** A201077 and **A262984**
agree on `1, 2, 3, 6, 10, 16, 26, 40, 60, 90, 131, 188` — twelve terms — and
part at the thirteenth, `269` against `268`. The brute-force enumerator only
reached eleven. Extending the fast column DP to the bevel gave `269`, so it is
A201077. Three near-misses now in one campaign (A071734, A120452, A262984), each
killed only by computing one term past where the lookup was comfortable.

So the earlier "same factor `1, 1, -1, -1, 0, 1, 1` in both" was an artifact of
forcing `C^4` onto hulls that do not have four sharp tips. Nothing was wrong
with the product law; the geometry was misread.

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

First looked up by jasonp 2026-08-07; S3 **re-run from here the same day with
the extra terms** the cone model supplied, after jasonp authorised direct `curl`
against oeis.org. That re-run is the whole point of the table: it turned a wrong
hit into the right one. Two hits, five apparent novelties:

| | series | result |
|---|---|---|
| S1 | square4 diamond free-removals `1, 4, 18, 60, 187, 524, 1388, 3452, 8229, 18800` | **no match** (looked up when the last two were model values; all ten are measured as of 2026-08-09) |
| S2 | square4 even-W hull free-removals `1, 6, 25, 88, 272, 766, 2012` | **no match** |
| S3 | per-tip `1, 1, 3, 5, 9, 14, 24, 35, 55, 81, 120, 171, 248` | **A053993**, Andrews' `phi_2`; an eta quotient, same status as `P(x)`. A120452 matched only the first six terms and is refuted at the seventh |
| S4 | hexagon free-removals `1, 6, 27, 98, 315, 918` | `P(x)^6`; A071734 matched the first five terms and is refuted at the sixth |
| S5 | tri6 `C(p,0)` `1, 3, 2, 3, 6, 1, 6, ...` | **no match** |
| S6 | king min-perimeter stable columns | **no match** (though the model explains them) |
| S7 | square4 min-perimeter stable columns | **no match** |

**Query short to find, extend to verify, and don't confuse the two.** More terms
can only shrink the match set, so re-running a *miss* with extra terms buys
nothing (I did it for S1 and S2 anyway, and it bought nothing); for discovery it
is actively worse, since a candidate whose OEIS entry lists eight terms can
never match a ten-term query. Extra terms earn their keep only against a *hit*,
which is exactly how S3 and S4 were caught.

"No match" is OEIS's answer to the terms submitted, not a novelty proof, and no
term count changes that — the transform battery is what would, and that is
jasonp's to send. S7 carries only four or five terms, which is thin on both
counts. S6 is the interesting one --
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
