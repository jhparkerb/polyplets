# Perimeter gradings: both ends of the site-perimeter table

The site perimeter of a fixed lattice animal is the number of distinct empty
cells adjacent to it under the lattice's own adjacency: four neighbors on the
square lattice (`square4`, rook moves), eight on the king lattice (`square8`),
six on the triangular lattice (`tri6`). `A(n, p)` counts fixed animals of `n`
cells with site perimeter `p`; the attainable `p` fill `[pmin(n), pmax(n)]`.
Notation: `deg` is the lattice degree; `c = e − n + 1` the cycle rank of an
animal's adjacency graph; `Φ_d` the d-th cyclotomic polynomial (`Φ₁ = 1 − x`,
`Φ₂ = 1 + x`, `Φ₃ = 1 + x + x²`); `P(x) = Π_{m≥1} (1 − x^m)^{−1}`. The *onset*
of a class is the least index from which its closed form holds.

At the maximum end, `pmax(n) = (deg/2)(n + 1)`, the classes of fixed defect
`k = pmax(n) − p` are quasi-polynomials in `n` of degree `k` with cyclotomic
denominators, on both lattices through `k = 6`: the defect identity, the
monotonicity behind the enumerator and the reduction of the king column to the
square column are proved; period, degree, denominator and onset per class are
interpolated with spare points; the shared leading coefficient and onset are
derived. The square column reproduces Asinowski, Barequet and Zheng (2018); the
king column is not in the literature. At the minimum end, `pmin(n)` is
published (A261491 square, A235382 king); indexed by `p`, the classes are
eventually constant with a linear threshold. The king constants are a
convolution of the 4-colored partition function with box-skew deficits,
measured at `i = 0..6`, not proved; the per-corner factor is the order-ideal
generating function of the corner's tangent cone (`P(x)` aligned, Andrews'
`φ₂` at the square diamond's tip, A201077 at its bevel), measured through
`j = 11` with nothing fitted. A king identity
`k_min(n, H) = ⌈(n − H)/(H − 1)⌉` is sharp on 672 `(n, H)` entries. The `k = 7`
census is priced at two to six months of a 76-core pool per lattice, not run.

## Minimum site perimeter, n = 1..14

King convention: empty cells king-adjacent to the animal, the percolation
perimeter of the king lattice, as in `cpp/g2_redelmeier.cpp` (`--siteperim`),
cross-checked there against Mertens, J. Stat. Phys. 58 (1990) 1095–1108, Table
IVB; the rook variant is a control that must differ. Measured 2026-08-05 on
gympie (`git=54440c2-dirty`) by `build/directed_cone_anchor grid 14 8`
(`cpp/directed_cone_anchor.cpp`): columns 22 and 23 of
`results/mk_siteperim_n14.txt`, whose other columns equal
`results/mk_grid20_n14.txt` and `fixtures/b006770.txt` through `n = 14`.
`tests/gate_site_perim.py` (`make gate-site-perim`) cross-checks the king
minima for `n = 1..9` against `build/g2 square8 --siteperim`, a different
search, and requires the rook column to differ at every `n`.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| king minimum | 8 | 10 | 12 | 12 | 14 | 14 | 16 | 16 | 16 | 18 | 18 | 18 | 20 | 20 |
| rook minimum (control) | 4 | 6 | 7 | 8 | 8 | 9 | 10 | 10 | 11 | 11 | 12 | 12 | 12 | 13 |
| king − rook | 4 | 4 | 5 | 4 | 6 | 5 | 6 | 6 | 5 | 7 | 6 | 6 | 8 | 7 |

A `k × k` block has king site perimeter `4k + 4`, matching `n = 1, 4, 9`; the
rook minimum at `n = 9` is 11, not 12. The king row is **A235382** =
A027709(n) + 4 = `2⌈2√n⌉ + 4` on all 14 terms, checked integer-exactly
(`isqrt(4n)`, no float) by `experiments/min_site_perim_closed_form.py`; A027709
is the minimal edge perimeter of an n-omino, `2⌈2√n⌉`, and the `+4` is the four
corner cells of the king ring that rook adjacency never counts. The rook row is
**A261491** = `⌈2 + √(8n − 4)⌉`, matched by `build/g2 square4 --siteperim` for
`n = 1..14`. A027710 (balls into 3-colored boxes) is not a perimeter sequence;
the pairing "A027709/A027710" in earlier planning notes was a mistake. Both
closed forms are published and verified here only to `n = 14`; A235382's
comment credits "the students Daring, et al." by an unfetched link. Adding the
two minima to the grid pass cost, on gympie at 8 threads, wall 512.1 → 689.8 s
(+34.7%), cpu 3672.6 → 5117.6 s (+39.3%), peak RSS 1.9 MB unchanged: 12 more
neighbor-offset checks per cell over the 19 there; cpu/wall 7.17 → 7.42.

## The maximum end

### The defect identity and the prune

Let `t` be the sum over empty adjacent cells of (animal neighbors − 1).
**Proposition (proved).** On a lattice of degree `deg`,

    k = 2c + t − (deg/2 − 2)(n − 1),

`2c + t` on the square lattice, `2c + t − 2(n − 1)` on the king lattice. The
square form does not carry over: a king diagonal stick has `c = 0`,
`t = 2(n − 1)`, `k = 0`. The square form is Asinowski, Barequet and Zheng's
`k = e + 2f` (`f` circuit rank, `e` total excess;
`papers/asinowski_barequet_zheng_2018_polycubes_small_perimeter_defect.pdf`).
No count depends on the identity.

**Monotonicity (proved).** Adding a cell raises `pmax` by `deg/2` and changes
`p` by `−1 + g`, with `g` the neighbors that become fresh perimeter cells,
capped by the neighbors the new cell shares with the animal cell it touches; so
`k` never decreases, tightly (a stick extends at `Δk = 0`), and a Redelmeier
search abandoning a partial animal once `k > kmax` is exact. A candidate's
`Δk` is itself nondecreasing, so an over-budget candidate is dropped for good:
about 20x (king `n = 20`, `k ≤ 5`: 2.4e8 nodes to 1.4e7). A row transfer cannot
replace this, since the defect does not bound the transverse extent of a scan
(a U with distant arms has `k = 3`). `cpp/perimeter_defect.cpp`, gated by
`scripts/perimeter_defect_gate.sh` against `build/g2 --siteperim`
(`results/siteperim_square4_n20.txt`, `results/siteperim_square8_n14.txt`), an
unpruned control and the `(c, H)` marginals, reaches `n = 70` at `k ≤ 5` on one
gympie core (913 s square, 2017 s king, 2026-08-07); brute force stops at
`n = 14` on king.

### The king column is the square column re-graded

**Proposition (proved).** Diagonal king steps preserve the parity of `x + y`,
so a king animal `A` with no orthogonal edge lies on one parity class, and
`(x, y) → (u, v) = ((x + y)/2, (x − y)/2)` carries it bijectively onto a
polyomino `B` of the same size. With `h` the number of holes of `B`,

    k_king(A) = k_square(B) + c(B) + h(B).

*Proof.* With `S` the 3×3 box, `p = |A ⊕ S| − n` and `pmax = 4n + 4`, so
`k = 5n + 4 − |A ⊕ S|`. Cells of `A`'s parity in `A ⊕ S` are `B` and its edge
neighbors in the `(u, v)` frame, `n + p₄(B)` of them. Cells of the other parity
are in bijection with the grid vertices of the `(u, v)` lattice (an odd cell's
four orthogonal neighbors are the four cells at one vertex) and lie in `A ⊕ S`
exactly when one of those four is in `B`: `Vert(B)` of them. Euler on the cell
complex of `B` (`V − E + F = 1 − h`, `F = n`, `E = 4n − a`, `a` the adjacent
pairs) gives `Vert(B) = 3n − a + 1 − h`; substitute with `k_square = 2n + 2 − p₄`
and `c = a − n + 1`. Checked on 489,603 same-parity animals to `n = 13`, `k ≤ 6`
(`experiments/perimeter_defect_features.py`).

Feature costs (features interfere only within Chebyshev distance 2, which is
what the onsets measure):

| king feature | in `B` | defect cost |
|---|---|---|
| straight diagonal step | straight step | 0 |
| 90-degree turn | bend | 1 |
| cell with 3 diagonal neighbors | T-branch | 2 |
| cell with 4 diagonal neighbors | cross | 4 |
| independent cycle | cycle | square cost + 1 |
| enclosed cell | hole | square cost + 1 |
| orthogonal step | not in `B` | 2 |

A defect-`k` animal has at most `⌊k/2⌋` orthogonal steps.

**The counts.** `P(n, j, c)` is the square census graded by cycle rank (the `c`
column of `results/perimdefect_square4_n78_k6.txt`), `M(n, k)` the king animals
with an orthogonal edge. The cheapest holed polyomino (3×3 less center and a
corner) has `k_square = 4`, `c = 0`, `h = 1`, so a hole costs `k_king = 5`, and

    A_king(n, k) = Σ_c P(n, k − c, c) + M(n, k)        k ≤ 3, exact.

The square census carries no `h` grading, so for `k = 4, 5, 6` the identity is
checked against the king enumeration to `n = 12`. With
`R(n, k) = A_king(n, k) − Σ_c P(n, k − c, c)`, checked to `n = 78`:

    R(n,2) = 8n − 16                                          n ≥ 3
    R(n,3) = 20n² − 128n + 212                                n ≥ 4
    R(n,4) = 191/6 n³ − 811/2 n² + 5786/3 n − 3456            n ≥ 8 even
             191/6 n³ − 811/2 n² + 11581/6 n − 6937/2         n ≥ 9 odd
    R(n,5) = 109/3 n⁴ − 2368/3 n³ + 44155/6 n² − 104759/3 n + 69848      n ≥ 12 even
             109/3 n⁴ − 2368/3 n³ + 44155/6 n² − 104780/3 n + 139841/2   n ≥ 13 odd

`R(n,2) = 8(n − 2)` is derived: two straight diagonal sticks, `a + b = n`,
joined by one orthogonal edge, 16 configurations per unordered pair, halved
when `a = 1` or `a = b`; the census confirms every defect-2 mixed animal has
this shape. Since `deg R = k − 1` and `deg P(n, k − c, c) ≤ k − 2` for `c ≥ 1`,
**the king leading coefficient is the square one**; since `R`'s onsets 3, 4, 8,
12 lie below the class onsets 6, 9, 13, 18, **the king onset is the square
onset**; since a cycle in `B` forces `k_square ≥ 2c`, `k_king ≥ 3c` and
**`c ≤ ⌊k/3⌋`** (census maxima 1, 1, 1, 2 at `k = 3..6`).

### The classes

Period, degree, onset and denominator are interpolations verified against at
least two spare points per residue class.

| k | period | degree | onset | denominator | leading coefficient (both lattices) |
|---|---|---|---|---|---|
| 0 | 1 | 0 | 2  | Φ₁ | 2 |
| 1 | 1 | 1 | 3  | Φ₁² | 4 |
| 2 | 1 | 2 | 6  | Φ₁³ | 6 |
| 3 | 2 | 3 | 9  | Φ₁⁴Φ₂² | 13/2 |
| 4 | 2 | 4 | 13 | Φ₁⁵Φ₂³ | 17/3 |
| 5 | 6 | 5 | 18 | Φ₁⁶Φ₂⁴Φ₃ | 593/144 |
| 6 | 6 | 6 | 24 | Φ₁⁷Φ₂⁵Φ₃² | 13325/5184 |

**Onset (conjectured; five consecutive hits per lattice).**

    onset(k) = k(k+1)/2 + 3        for k ≥ 2

`k = 0, 1` are degenerate (2 and 3 against 3 and 4). `onset(6) = 24` was
predicted before the `k = 6` census and confirmed without interpolation
(`experiments/perimeter_max_structure.py` takes each onset from the census as
the largest failing `n` plus one). Predicted: `onset(7) = 31`. The onset is not
the first defect-`k` animal (a tight zigzag reaches defect `k` at `n = k + 2`)
but where the last short-range interference dies out. The degree column,
`Φ₁^{k+1}` exactly, is Asinowski, Barequet and Zheng's conjecture (their §4:
factor `(x − 1)^{k+1}`, asymptotics `γ n^k`), confirmed through `k = 6`.

`k = 3` carries a genuine period-2 term on both lattices. Square, `n ≥ 9`:

    Q₃(n) = 13/2 n³ − 89n² + 1947/4 n − 2107/2 + (−1)^n (5n/4 − 21/2)

The parity part has degree 1. King `k = 3` is the square form plus `R(n,3)`
less the `c = 1` constant 8: `13/2 n³ − 69n² + 360n − 860` (`n` even),
`13/2 n³ − 69n² + 715/2 n − 839` (`n` odd); even minus odd is `5n/2 − 21` on
both lattices. `experiments/perimeter_defect_fit.py` refits every class.

**Recentered basis.** Re-expanding each residue class in `C(m, j)`,
`m = (n − n₀)/period` from the class's first in-regime point, in place of the
`n = 0`-centered `1/Φ₁^j → C(n+j−1, j−1)`, every coefficient is a nonnegative
integer on both lattices, `k = 2..5`, every class (king, then square):

    k=2        92, 48, 12                              60, 40, 12
    k=3 r=1  1528, 1868, 1164, 312                    856, 1324, 1004, 312
    k=4 r=1  45753, 48873, 32438, 12484, 2176         22993, 30293, 24222, 10956, 2176

The leading coefficient (312, 2176, 3842640 at `k = 3, 4, 5`) is
`c_k · k! · period^k`. The recentering needs the onset formula and is downstream
of it; `k = 6` has not been run.

### Generating functions and the coefficient triangle

`experiments/perimeter_defect_gf.py` forms `G_k(x) = Σ_n A(n, pmax(n) − k) x^n`
exactly. The denominator is predicted from the table, then checked: division
must leave a polynomial with `gcd(N, D) = 1`, and does for every `k` on both
lattices; at `k = 5` (`n ≤ 70`) that is 28 consecutive exact zero coefficients
the interpolation never saw. At `k = 5` the `Φ₆` component of the constant
term is exactly zero: `Φ₂` and `Φ₃` act independently, `Φ₂` in the `n³`
coefficient, `Φ₃` only in the constant. Across `k ≤ 6`

    D_k = Φ₁^{k+1} Φ₂^{k−1} Φ₃^{k−4},      Φ_d first appears at k = 2d − 1,

predicting `Φ₄` first at `k = 7` (untested); if so, each further prime-power
periodicity costs two units of defect. Cyclotomic rationality is Asinowski,
Barequet and Zheng's theorem for the square lattice and polycubes; their proof
assumes face connectivity, so the king column is an analogue, not a corollary,
except on the no-orthogonal-edge part the reduction maps into their theorem.

King partial fractions, `G_k = R_k + Σ_j a_j/Φ₁^j + Σ_j b_j/Φ₂^j + (Φ₃ block)`,
`R_k` a polynomial carrying the pre-onset values; `a_j/Φ₁^j` contributes
`a_j C(n+j−1, j−1)`, `b_j/Φ₂^j` the same times `(−1)^n`, the `Φ₃` block a
bounded period-3 term. Rows `k`, columns by offset `d` from the top of each
block (`j = k + 1 − d` for `Φ₁`, `j = k − 1 − d` for `Φ₂`), `*` marking entries
identical on both lattices:

    Φ₁ block      d=0        d=1          d=2           d=3            d=4              d=5
      k=0         2*
      k=1         4*        −12*
      k=2        12*        −48           92
      k=3        39*       −216       2445/4       −5135/4
      k=4       136*    −1911/2      14049/4      −18863/2        40769/2
      k=5    2965/6*      −4234    685645/36   −2225243/36  139157959/864  −150424703/432

    Φ₂ block      d=0        d=1          d=2           d=3
      k=3       5/4*      −47/4*
      k=4       5/4*      −47/2        349/2
      k=5      15/8*     −293/8*    10503/32     −28141/16

    Φ₃ block, k=5:  (40x/27 + 8/3)/Φ₃, identical on both lattices in full

**The leading diagonal of each cyclotomic block is lattice-independent, and
nothing below it is.** `d = 1` differs from `k = 2` in the `Φ₁` block; the `Φ₂`
block's `d = 1` agreement at `k = 3, 5` fails at `k = 6`. The reduction
explains the `Φ₁` column: `R` has degree `k − 1` and cannot touch `d = 0`. The
`k = 6` row is in `paper/L6-perimeter-gradings.tex`. Neither leading diagonal
has a closed form:

- `Φ₁`: `a_{k+1} = c_k · k! = 2, 4, 12, 39, 136, 2965/6, 66625/36`, integral
  through `k = 4` and then not.
- `Φ₂`: `b_{k−1} = 5/4, 5/4, 15/8, 5/2` at `k = 3..6`. `5(k−2)!/2^{k−1}` fits
  three and predicts 15/4 at `k = 6`; measured 5/2 on both lattices. Withdrawn.
- `Φ₃`: identical in full at `k = 5`; at `k = 6` only the top coefficient is
  shared, king `(−5920x³ − 19128x² − 18528x − 12656)/243` against square
  `(−5920x³ − 18768x² − 18168x − 12296)/243`.

The triangle `B(n, k) = A(n, pmax(n) − k)`, with the `G_k` as column generating
functions, is weaker than the height triangle, which one theorem with one onset
formula covers; here each `k` has its own denominator. Neither triangle has been
checked against OEIS.

### The `k = 6` censuses and the four predictions they decided

dalby, 2026-08-07 to 08-10, `scripts/dalby_perimeter_defect_pool.sh` (456
shards, 76-way, `splitS=14`, `git=6473890c`), both merged 456/456 `result=ok`:

| lattice | wall | animals | file |
|---|---|---|---|
| king | 151,915 s | 3,948,974,545,893 | `results/perimdefect_square8_n78_k6.txt` |
| square | 83,667 s | 3,168,296,567,027 | `results/perimdefect_square4_n78_k6.txt` |

`n = 78` because a period-6 degree-6 fit with two spare points per class needs
54 points above onset 24. Analyzed with `experiments/perimeter_defect_gf.py
--kmax 6` (the default `--kmax 5` shows nothing at `k = 6`) and
`experiments/perimeter_defect_denominator.py --k 6`, which retests each passing
denominator with one factor removed.

| prediction | outcome |
|---|---|
| `onset(6) = 24` | confirmed, both lattices; `deg N − deg D = 39 − 16 = 23` |
| `Φ₃` exponent `k − 4`, so `Φ₃²` | confirmed; no longer rests on the one point `k = 5` |
| no `Φ₄` before `k = 7` | confirmed: `Φ₁⁷Φ₂⁵Φ₃²` divides exactly, `gcd(N, D) = 1`, minimal |
| `Φ₂` leading diagonal 15/4 | refuted: 5/2 on both lattices |

The census record counts 22 spare zero coefficients after the division;
`paper/L6-perimeter-gradings.tex` (2026-08-23, later) says 39, which is
`deg N`. Both stand here.

### An exact identity relating `n`, `H` and `p` on the king lattice

The minimum defect over king animals of `n` cells and bounding-box height `H`
is exactly

    k_min(n, H) = ⌈(n − H)/(H − 1)⌉        H ≥ 2,

zero violations, equality attained in all 672 `(n, H)` entries present at
`k ≤ 5`, `n ≤ 40` (`results/king_joint_nhp_n9.txt`,
`results/king_triple_classes_n9.txt`, `experiments/perimeter_vs_height_defect.py`).
Equivalently `H ≥ (n + k)/(k + 1)`, and the same for the width; `k = 0` forces
`H = W = n` (the diagonal sticks), `k = 1` forces both dimensions
`≥ (n + 1)/2`. On the square lattice `k_min(n, H) = 0` for `H ∈ {1, n}` and 1
between: the square defect-0 animals are the horizontal and vertical sticks, at
opposite ends of the height range, while both king defect-0 animals are
diagonal sticks with `H = n`.

### Closed doors, maximum end

- **The king parity term is the square parity term.** `R(n, 3)` has period 1,
  so the `(−1)^n` is inherited. It sits in the acyclic animals (the `c ≥ 1`
  parts are plain and tiny: square `k = 3`, `c = 1` is the constant 8; king one
  animal at `n = 4`), in no single height slice (every `H = n − j` is a plain
  polynomial on both lattices), and not in the height floor, whose period
  `k + 1` predicts 5 at `k = 4` where the answer is 2.
- **`c_k · k! = 2·C(2k, k)` is dead.** 2, 4, 12, 39, 136 against 2, 4, 12, 40,
  140; at `k = 5` the product is not an integer.
- **The numerators are not nonnegative.** The tail numerator
  `Ñ_k = (Σ_{n≥onset} A(n,k) x^n) · D_k / x^onset` is a polynomial of degree
  exactly `deg D_k − 1` (a further check on the denominators) with sign changes
  from `k = 2` on; the full `G_k` numerator is the wrong object, `R_k` having no
  reason to be positive.
- **The onset is not the positivity threshold.** The least `n₀` with all forward
  differences nonnegative is strictly below the onset in every class on both
  lattices (`k = 5`: 12 against 18).
- **A separate `n = 16` king enumeration on dalby** (about 17 CPU-hours) was not
  worth doing: the pruned enumerator reaches `n = 70` in 2017 s on one core.
- **The pool script's cost header** predicted about 136 core-hours and 1.8 h
  wall for king `n = 78` from `time ~ n^7.9`; the run took 42 h wall at 76-way,
  about 23x. Not calibration for anything (see the `k = 7` pricing).

### Novelty

Priority pass of 2026-08-18 (`docs/priority-passes-2026-08-18.md`): the
identity, the cyclotomic rationality theorem and the degree conjecture are
Asinowski, Barequet and Zheng's; Barequet and Magal (2023) give square formulae
to `k = 5`, held by abstract only. The king column, the parity reduction, the
onset formula, the coefficient triangle, the whole minimum end and the `n/H/p`
identity were not found anywhere.

## The minimum end

`pmin(n)` grows like `√n` and is a step function, so the row index is `p`:
`nmax(p) = max{n : pmin(n) ≤ p}` and

    C(p, i) = A(nmax(p) − i, p).

`pmin` is A261491 and A235382, re-verified against the census before anything
else runs.

### Data and completeness

`p − pmin(n)` is not monotone under cell addition, so there is no growth prune.
Near-minimal animals fill their bounding hull up to a few cells, so
`cpp/perimeter_min.cpp` enumerates isoperimetric hulls and removes small
subsets, at `Σ_r C(M, r)` cost. The square lattice is worked in the rotated
frame `u = x + y`, `v = x − y`, where a diamond is a parity-restricted box; a
hull is a range on each of a list of linear functionals, `u, v` (a rectangle)
or `u, v, u + v` for `tri6` (a hexagon, no parallelogram in any linear frame).
Completeness rests on hypothesis (H1), every animal's perimeter is at least its
filled hull's, so deficit `i` means at most `i` removals. (H1) is asserted at
runtime and tested by `make gate-perimeter-min` (`scripts/perimeter_min_gate.sh`)
with removals unbounded on small boxes, a complete brute force there, against
`build/g2 --siteperim`: 33 and 52 `(n, p)` entries agree on the two square-based
lattices, 35 on `tri6` (`results/siteperim_tri6_n12.txt`); a control confirms
the square and king modes differ, and an over-limit frame must fail closed.

Censuses (`n p count`, completeness domain in the header, `.log` beside; gympie
2026-08-07, `scripts/run_perimeter_min.sh`, 10 threads, except king `p ≤ 48` on
ayr by `scripts/ayr_pmin48.sh`):

| lattice | reach | files |
|---|---|---|
| king | `p ≤ 40` (`n` to 81), 44, 48 | `results/perimmin_square8_p40_r6.txt`, `results/perimmin_square8_p44_r6.txt`, `results/perimmin_square8_p48_r6.txt` |
| square | `p ≤ 24` (`n` to 61), 28 | `results/perimmin_square4_p24_r6.txt`, `results/perimmin_square4_p28_r6.txt` |
| tri6 | `p ≤ 30` | `results/perimmin_tri6_p30_r6.txt` |

Brute force stops at `n = 14` (king) and `n = 20` (square).

### King: the constants are the 4-colored partition function

`C(p, i)` is eventually constant in `p` along each residue class mod 4:

    p ≡ 0 (mod 4):  C(i) = q4(i) + 2 Σ_{s≥1} q4(i − s²)
    p ≡ 2 (mod 4):  C(i) = 2 Σ_{s≥0} q4(i − s(s+1))
    p odd:          0

with `q4(j) = [x^j] P(x)⁴ = 1, 4, 14, 40, 105, 252, 574`. Measured against
predicted at `i = 0..6`, fourteen of fourteen exact
(`experiments/perimeter_min_model.py`):

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| `p ≡ 0 (mod 4)` | 1 | 6 | 22 | 68 | 187 | 470 | 1106 |
| `p ≡ 2 (mod 4)` | 2 | 8 | 30 | 88 | 238 | 584 | 1360 |

Both mechanisms are checked directly. Removing a corner cell of a filled king
box drops one ring cell and adds the removed cell, net zero, so the
perimeter-preserving removals are a Young diagram at each of four corners:
`P(x)⁴`. The per-box free-removal counts (`--boxes`) converge to `q4` term by
term, exactly once the box side exceeds the removal count (`W = 5` right to
`j = 4`, `W = 6` to `j = 5`, `W = 7` to `j = 6`). At semiperimeter `S = w + h`
the balanced box is optimal and a skew of `s` costs `s²` cells for `S` even,
`s(s+1)` for `S` odd: different deficit sets, hence period 4. Threshold
`p* = 4i + 8` (`p ≡ 0`) and `4i + 10` (`p ≡ 2`), exact for `i = 0..6`: the
balanced box side must exceed `i`, linear in the deficit. Not proved: `q4` is
confirmed as the limit by direct count, not a bijection, and the threshold is
read off the data.

### Attainability decides stabilization

King's odd-`p` columns grow; the square lattice's stabilize, so parity is not
the rule. Tested class by class on both lattices by
`experiments/perimeter_min_attainability.py`, no exceptions:

    C(p, ·) stabilizes  ⇔  p is attained as pmin(n) for some n.

King's `pmin` is always even, so an odd column counts animals one unit worse
than any optimum, a population with a growing positional freedom. The square
`pmin` attains every integer in range except 5, and all four columns stabilize.
The non-attained king columns are quadratic in `p`, fitted exactly with spare
points (higher `i` needs `p` past 40):

    p ≡ 1 (mod 4), i=1:  (p² − 10p − 39)/16
    p ≡ 3 (mod 4), i=1:  (p² − 10p − 43)/8
    p ≡ 1 (mod 4), i=2:  (3p² − 30p − 197)/8

### The square lattice's stable columns

Values held to three equal entries at the top of the `p ≤ 28` range:

| | i=0 | i=1 | i=2 | i=3 | i=4 | stabilizes from |
|---|---|---|---|---|---|---|
| `p ≡ 0 (mod 4)` | 1 | 9 | 52 | 206 | 719 | `p* = 4i + 4` |
| `p ≡ 2 (mod 4)` | 4 | 22 | 106 | 392 | — | `p* = 4i + 6` (`i ≥ 1`) |
| `p ≡ 1 (mod 4)` | 4 | 28 | 124 | 456 | — | `p* = 4i + 9` |
| `p ≡ 3 (mod 4)` | 4 | 28 | 124 | 456 | — | `p* = 4i + 7` |

Four or five points per class, no exceptions above `i = 0`; the odd classes
agree on every converged value. `C(p, 0) = 1` for `p ≡ 0` (the perfect diamond)
and 4 otherwise (a partial layer in four rotationally equivalent positions),
`p = 6` the small-`n` exception. King and square differ here from the first
nontrivial constant.

### tri6: period 6

At `p ≤ 30`, `i = 0` and `i = 1` are stable in all six classes mod 6:

    C(p, 0) =  1,  6,  3,  2,  3,  6      p ≡ 0..5 (mod 6)
    C(p, 1) = 14, 42, 27, 24, 27, 42

The 1 is the unique perfect hexagon. The king model in the form

    C(p, i) = Σ_{hulls H : pbox(H) = p} q_c(i − deficit(H)),   deficit(H) = nmax(p) − |H|,

`c` the hull's corner count, `q_c = [x^j] P(x)^c`, fed tri6's hull inventory
from `--boxes` (`results/perimmin_tri6_p30_boxes.txt`) and `q6` with nothing
fitted, reproduces 18 of 18 settled columns (`p = 30`, `i = 0..3`: 1, 14, 87,
392; `p = 25..29`, `i = 0..2`; `experiments/perimeter_min_hex_model.py`). The
period is set by the isoperimetric shape: 4 for box and diamond, 6 for the
hexagon.

### The corner factor: order ideals of the tangent cone

Measured on single large hulls (`--only`), perimeter-preserving removal counts:

    king, square box (4 corners), W=7:   1, 4, 14, 40, 105, 252, 574   = [x^j] P(x)⁴
    tri6, hexagon (6 corners), r=4:      1, 6, 27, 98, 315             = [x^j] P(x)⁶

The hexagon's five terms also open A071734, `p(5n+4)/5`, which is `P(x)⁶` times
`Π(1 − x^{5n})⁵ = 1 − 5x⁵ + …`; they part at `j = 5`, 918 against 913, and the
`r = 5` hull (`--only 11 11 -1 5 15`) measures **918**. Each radius buys one
more correct term (`r = 3` to `j = 3`, `r = 4` to `j = 4`).

The square lattice's diamond gives

    1, 4, 18, 60, 187, 524, 1388, 3452, 8229, 18800, 41536, 88924, 185355

above `P(x)⁴` from `j = 2` (18 against 14), fourth root `1, 1, 3, 5, 9, 14, 24,
…`. A king box corner spans the lattice's own quadrant, whose finite order
ideals are Young diagrams, hence `P(x)`. Undoing the 45-degree rotation, a
diamond tip is the cone `C = {(a, b) ∈ Z² : a ≥ |b|}`, carried by `u = a − b`,
`v = a + b` to the index-2 sublattice `Q = {(u, v) ∈ Z²_{≥0} : u ≡ v (mod 2)}`
under the componentwise order, where a finite downset with column sizes
`a_i = c_{2i}`, `b_i = c_{2i+1}` is exactly

    a nonincreasing, b nonincreasing, a_i ≥ b_i, b_i ≥ a_{i+1} − 1,

pairs of partitions `(λ, μ)` with `μ ⊆ λ` and `λ` less its first row and
column contained in `μ`, weighted by `|λ| + |μ|`; setting the `−1` to 0 forces
`λ = μ` and recovers `P(x)`, the control. `experiments/cone_order_ideals.py`:

    tip:      1, 1, 3, 5, 9, 14, 24, 35, 55, 81, 120, 171, 248, …
    control:  1, 1, 2, 3, 5,  7, 11, 15, 22, 30,  42,  56,  77, …   = P(x)

The fourth power, `1, 4, 18, 60, 187, 524, 1388, 3452, 8229, 18800, 41536, …`,
matches every measured diamond term with nothing fitted.

**The tip series is A053993**, Andrews' `φ₂` (generalized Frobenius partitions
with up to two repetitions per row, Memoirs AMS 301, 1984), all 31 computed
terms agreeing, with the product of Andrews eq. (5.9)

    G_tip(x) = Π_{k>0} [(1−x^k)(1−x^{12k−10})(1−x^{12k−9})(1−x^{12k−3})(1−x^{12k−2})]^{−1},

the eta quotient `q^{1/12} η(q⁴) η(q⁶)² / (η(q) η(q²) η(q³) η(q¹²))`, verified
against the cone count to `n = 40` (`andrews_phi2()` in
`experiments/cone_order_ideals.py`, asserted at runtime); Euler exponents
`1, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1`, period 12. An infinite product, not a
closed form, of the same status as the `P(x)` it generalizes, with asymptotic
`φ₂(n) ~ exp(2π√(2n)/3)/(6√2 n)` (Kotesovec). The whole diamond generating
function is `G_tip(x)⁴`.

| corner | cone and coset | factor | OEIS |
|---|---|---|---|
| king box, tri6 hexagon | unimodular (index 1) | `φ₁ = P(x)` | A000041 |
| square diamond tip | index 2, apex on the lattice | `φ₂` | A053993 |
| square bevel | index 2, apex off the lattice | `D` | A201077 |

**A120452 refuted.** The six-term prefix `1, 1, 3, 5, 9, 14` matches A120452,
which continues 23, 34, 52 and predicts the diamond's `j = 6` term as 1384.
`W = 13` and `W = 15` (`results/perimmin_free_15_15_0.txt`, `r = 7`, 113 cells)
both measure **1388**; `4 = 4 × (24 − 23)`, so the tips are independent and only
the tip series was misidentified.

**`φ_m` for index `m` fails at `m = 3`.** The cone spanned by `(1, 0)` and
`(1, 3)` has order-ideal series `1, 1, 4, 8, 14, 24, 39, 64, 105, 161, 244, 370`;
`φ₃` is A053992 = `1, 1, 3, 6, 11, 18, 31, 49, 78, …`, and the index-3 series is
not in OEIS. Andrews' `φ_k` are two-rowed, and index-`m` cones stop being unique
up to `GL₂(Z)` at `m = 3` (Hirzebruch–Jung), so there is no single index-3 cone
to name. The identity holds for `m ≤ 2`; no lattice here has a sharper tip.

### The bevel

In the rotated frame a square-lattice hull is the box `{0 ≤ u < W, 0 ≤ v < H}`
restricted to one class of `u + v`, and whether a box corner survives depends
on parity:

| frame | box corners kept | corners | factor |
|---|---|---|---|
| odd `W`, parity 0 | all 4 | 4 sharp | `C⁴` |
| even `W`, parity 0 | 2 | 2 sharp + 2 bevels | `C² D²` |
| odd `W`, parity 1 | 0 | 4 bevels | `D⁴` |

A cut corner becomes a two-cell **bevel**, the same cone with its apex on the
other coset of the index-2 sublattice, which is why the `j = 1` counts are 4,
6, 8. Its order-ideal series, from its own cone poset with no measurement:

    D = 1, 2, 3, 6, 10, 16, 26, 40, 60, 90, 131, 188, 269, …

`D` was extracted from the even-`W` family (`W = 14` parity 0, 6 corners:
`1, 6, 25, 88, 272, 766, 2012`, identical at `W = 16`, so converged at `j = 6`;
divide by `C²`, take the square root, all coefficients integral and
nonnegative) and predicts the odd-`W` parity-1 family with nothing free:
`D⁴ = 1, 8, 36, 128, 398, 1120, 2924`, the measured `W = 15` parity-1 values,
all seven. **`D` is A201077**, the eta quotient

    D(x) = 1 / Π_{i>0} (1−q^{2i−1})² (1−q^{12i−8})(1−q^{12i−6})(1−q^{12i−4})(1−q^{12i}),

verified against the cone count to `n = 24` and asserted at runtime. A201077
and A262984 agree on twelve terms and part at the thirteenth, 269 against 268;
the brute-force count reached eleven, and the column dynamic program extended
to the bevel gave 269. Three OEIS near-misses in this campaign (A071734,
A120452, A262984) each fell one term past the comfortable match.

### Deep diamonds: `j = 7..12` and the radius rule

The model predicted `j = 7 = 3452`, `j = 8 = 8229`. `j = 8` needs `W = 17`
(145 cells), past the old 128-cell mask, widened to four words.
`scripts/dalby_square4_deep.sh`, dalby, done 2026-08-08:

| box | cells | wall | nodes | free removals `j = 0..8` | file |
|---|---|---|---|---|---|
| `W=15`, `rmax=8` | 113 | 1 h 24 m | 5.5e11 | 1 4 18 60 187 524 1388 3452 **8193** | `results/perimmin_free_15_15_0_r8.txt` |
| `W=17`, `rmax=8` | 145 | 18 h 22 m | 4.2e12 | 1 4 18 60 187 524 1388 3452 **8229** | `results/perimmin_free_17_17_0_r8.txt` |

The 8193 is the box running out: a column down one tip's axis needs that tip
`j` cells deep, and a radius-`r` diamond has depth `r`.
`experiments/diamond_free_removals.py` grows the removal set one cell at a
time, keeping what stays perimeter-neutral and connected, sharing no code with
the C++ enumerate-and-filter; it reproduces both rows above, all 18 terms, and
reaches radii the C++ cannot afford:

    r=5   W=11   1 4 18 60 187 524 1360
    r=7   W=15   1 4 18 60 187 524 1388 3452 8193
    r=8   W=17   1 4 18 60 187 524 1388 3452 8229 18760 41268
    r=9   W=19   1 4 18 60 187 524 1388 3452 8229 18800 41492  88628 184027
    r=10  W=21   1 4 18 60 187 524 1388 3452 8229 18800 41536  88876 185031
    r=11  W=23   1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185303
    r=12  W=25   1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185355
    model        1 4 18 60 187 524 1388 3452 8229 18800 41536  88924 185355

**Radius `r` reproduces the model through `j = r` and undercounts from
`j = r + 1`**, at every radius; term `j` needs `W = 2j + 1`. With two agreeing
radii as the standard, `j = 8` has five, `j = 9` four, `j = 10` three, `j = 11`
two, `j = 12` one. `r = 5, 6` are check E of `scripts/perimeter_min_gate.sh`,
the C++ and this script compared row against row on every run.

### OEIS status of the seven series

Looked up 2026-08-07 by direct query of oeis.org. A miss is OEIS's answer to
the terms submitted, not a novelty proof; query short to find and extend only
to verify a hit, since extra terms only shrink the match set.

| | series | result |
|---|---|---|
| S1 | square diamond free removals `1, 4, 18, 60, 187, 524, 1388, 3452, 8229, 18800` | no match (all ten measured as of 2026-08-09) |
| S2 | square even-`W` hull free removals `1, 6, 25, 88, 272, 766, 2012` | no match |
| S3 | per-tip `1, 1, 3, 5, 9, 14, 24, 35, 55, 81, 120, 171, 248` | A053993 (`φ₂`); A120452 refuted at the seventh term |
| S4 | hexagon free removals `1, 6, 27, 98, 315, 918` | `P(x)⁶`; A071734 refuted at the sixth term |
| S5 | tri6 `C(p, 0)` `1, 3, 2, 3, 6, 1, 6, …` | no match |
| S6 | king stable columns | no match; the model above explains them |
| S7 | square stable columns (four or five terms) | no match |

## Cost of the censuses

Maximum end, one gympie core (`cpp/perimeter_defect.cpp`):

| run | time |
|---|---|
| `k ≤ 5`, `n = 70` | 2017 s king, 913 s square |
| king `n = 26`, `k = 5` → `k = 6` | 3.0 s → 29.6 s |
| king `n = 30`, `k = 5` → `k = 6` | 8.0 s → 94.1 s |

`k = 7` calibration (`scripts/dalby_perimeter_defect_k7_calib.sh`, dalby, 12
single cores, `git=6473890c`, finished 2026-08-18T23:53Z; the `k = 6` rows are
controls reproducing the census timings 254/692/1666 s to under 0.1%):

| lattice | k | n=30 | n=34 | n=38 | fitted exponent |
|---|---|---|---|---|---|
| square | 6 | 76 | 225 | 578 | 8.58 |
| square | 7 | 601 | 2150 | 6510 | 10.08 |
| king | 6 | 254 | 691 | 1665 | 7.95 |
| king | 7 | 2528 | 8077 | 22386 | 9.23 |

Local slopes `d log t / d log n` are flat over 30–38. The pool script's
`n^7.9` fits king `k = 6` only and carries no `k` dependence, the source of the
23x miss; each step in `k` costs about `n^1.3` (king) to `n^1.5` (square). The
`k = 7 : k = 6` ratio grows as `n^(e7 − e6)`: square 7.9, 9.6, 11.3 and king
10.0, 11.7, 13.4 at `n = 30, 34, 38`; at `n = 78`, 25x and 29x. Price of a
`k = 7` census on the 76-way pool, from the `k = 6` runs (42 h king, 23 h
square) with the fitted exponents:

| `n_max` | square | king |
|---|---|---|
| 78 | 32 d | 59 d |
| 82 | 53 d | 93 d |
| 85 | 76 d | 130 d |
| 88 | 107 d | 179 d |

A `k = 7` fit wants about 44 coefficients on onset 31, against `k = 6`'s 32 on
24, so the range is `n = 85..88`: two to six months per lattice. Planning input
only; neither approved nor launched.

Minimum end: `scripts/run_perimeter_min.sh` took 571 s and 77 s wall at 10
threads for the king `p ≤ 40` and square `p ≤ 24` censuses. A `W = 13` diamond
(85 cells, `C(85, 6) = 4.5e8` subsets) did not finish in 10 minutes on one
thread.

## Open problems

- Prove the degree and the onset at the maximum end. The height grading has a
  proof (`docs/proofs/universal-diagonal-law.md`) because a single-cell row is a
  cut; the perimeter defect supports no such cut.
- Is `F(x, y) = Σ_k G_k(x) y^k` rational? The denominator exponents are linear
  in `k` and `deg Ñ_k` grows linearly. The census record lists
  `deg Ñ_k = 0, 1, 3, 5, 7, 11` for `k = 0..5`; `paper/L6-perimeter-gradings.tex`
  (later) lists `2, 5, 7, 11, 15` for `k = 2..6` as `deg D_k − 1`, and
  `deg D₂ − 1 = 2`. Terms across two denominator regimes do not settle it.
- Prove the king min-end model and its threshold, both read off data.
- The hull factorization assumes independent corners, confirmed for the box,
  the hexagon, the diamond and the `C²D²`, `D⁴` square hulls; no general
  statement.
- Untested: `Φ₄` first at `k = 7` and `onset(7) = 31` (priced above); the
  `k = 6` recentering; the reduction identity at `k = 4..6` past `n = 12`; (H1)
  beyond the gate's boxes; novelty of S1, S2, S5, S6, S7 beyond an OEIS miss.

## Reproduce

    make build/perimeter_defect
    scripts/perimeter_defect_gate.sh                        # must print GATE PASSED
    ./build/perimeter_defect square8 40 5 > k.txt
    python3 experiments/perimeter_defect_fit.py k.txt --lattice square8
    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n70_k5.txt
    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n70_k5.txt results/perimdefect_square4_n70_k5.txt --compare
    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n78_k6.txt --kmax 6
    python3 experiments/perimeter_defect_denominator.py results/perimdefect_square8_n78_k6.txt --k 6
    python3 experiments/perimeter_defect_tail_degree.py
    python3 experiments/perimeter_defect_features.py       # the reduction and the closed forms, fail-closed
    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n70_k5.txt --lattice square8
    python3 experiments/perimeter_max_structure.py results/perimdefect_square4_n70_k5.txt --lattice square4

    make gate-perimeter-min                                 # must print GATE PASSED
    scripts/run_perimeter_min.sh
    python3 experiments/perimeter_min_model.py results/perimmin_square8_p40_r6.txt --lattice square8
    python3 experiments/perimeter_min_model.py results/perimmin_square4_p24_r6.txt --lattice square4
    python3 experiments/perimeter_min_ladder.py results/siteperim_square4_n20.txt --lattice square4
    python3 experiments/perimeter_min_attainability.py
    python3 experiments/perimeter_min_hex_model.py
    python3 experiments/cone_order_ideals.py
    python3 experiments/diamond_free_removals.py
    ./build/perimeter_min square4 99 6 --only 11 11 0        # a single large box

    make build/directed_cone_anchor build/g2
    make gate-site-perim
    scripts/run_site_perim_n14.sh                           # 689.8 s wall, 8 threads, gympie
    python3 experiments/min_site_perim_closed_form.py
    build/g2 square4 14 --siteperim
    build/g2 square8 9  --siteperim

Data: `results/perimdefect_square8_n70_k5.txt`, `results/perimdefect_square4_n70_k5.txt`,
`results/perimdefect_square8_n78_k6.txt`, `results/perimdefect_square4_n78_k6.txt`
(`n k c H count`); `results/siteperim_square4_n20.txt`,
`results/siteperim_square8_n14.txt`, `results/siteperim_tri6_n12.txt`,
`results/bbox_square4_n21.txt`; the `results/perimmin_*.txt` censuses and hull
probes with their `.log` files; `results/mk_siteperim_n14.txt`. The `k = 7`
calibration directory was removed 2026-08-22; its numbers are above.

## Sources

- `results/perimeter-both-ends.md` (deleted 2026-09-06; its content is above)
- `results/perimeter-defect-diagonals.md` (deleted 2026-09-06; its content is above)
- `results/perimeter-defect-k7-pricing.md` (deleted 2026-09-06; its content is above)
- `results/min-site-perimeter.md` (deleted 2026-09-06; its content is above)
