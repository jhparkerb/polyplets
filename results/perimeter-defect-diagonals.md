# Perimeter-defect diagonals: the perimeter grading is quasi-polynomial on both lattices

2026-08-07, executing `docs/perimeter-defect-plan.md`.

## The answer in one paragraph

Grading fixed animals by **site-perimeter defect** `k = pmax(n) - p` gives a
quasi-polynomial count on the king lattice exactly as it does on the square one:
`k = 3` carries a genuine period-2 term on both, so quasi-polynomiality is
**intrinsic to the perimeter grading, not a square-lattice artefact**. Through
`k = 6` the period, the degree, the onset and the *leading coefficient* are
identical on square and king; only the sub-leading coefficients differ.

That agreement is no longer a measured coincidence. Diagonal king steps preserve
the parity of `x+y`, so a king animal with no orthogonal edge **is** a polyomino
in rotated coordinates, and its defect is the polyomino's defect plus one unit
per independent cycle and one per hole. The king column is the square column
re-graded by cycle rank, plus the animals that do carry an orthogonal edge — a
family of degree `k-1`, which is why the leading coefficient is
lattice-independent. The height grading is the reverse: plain polynomials
(proved, `docs/proofs/universal-diagonal-law.md`), but with thoroughly
lattice-dependent coefficients — `4n - 8` on square against `25n - 45` on king.

## What made this cheap: the defect is monotone

A surplus-budgeted row DP cannot work here: the perimeter defect does not bound
the transverse extent of a linear sweep (a U with arms far apart has `k = 3` and
unbounded spread), which is presumably why the published method classifies
patterns instead of sweeping. What does work is simpler. Write `c` for the cycle rank `e - n + 1` of the
adjacency graph and `t` for the sum over empty adjacent cells of
(animal-neighbours − 1). Then, for a lattice of degree `deg`,

    k = 2c + t - (deg/2 - 2)(n - 1),

which is `2c + t` on square4 and `2c + t - 2(n-1)` on square8. **The square form
does not carry over**: a king diagonal stick has `c = 0`, `t = 2(n-1)` and
`k = 0`. Only the square form is published (Asinowski, Barequet & Zheng, as
`k = e + 2f`); the shift is what the extra 4 neighbours per cell buy.
`paper/L6-perimeter-gradings.tex` Proposition kct and the header of
`cpp/perimeter_defect.cpp` both state the square form for both lattices and are
wrong there. **No count moves**: the enumerator prunes on the monotonicity, not
on the identity.

The monotonicity is separate and does hold on both lattices. **k never decreases
when a cell is added**: placing a cell raises `pmax` by `deg/2` and changes `p`
by `-1 + g`, where `g` counts the neighbours that become fresh perimeter cells,
and `g` is
capped by the neighbours the new cell shares with the animal cell it touches.
The bound is tight on both lattices (a stick extends at `dk = 0`). So a
Redelmeier DFS that abandons a partial animal the moment `k > kmax` is exact.

A second monotonicity makes it fast: a candidate cell's *cost* `dk` is itself
non-decreasing as the animal grows, so a candidate over budget is over budget
forever and can be dropped from the untried list rather than re-tested at every
node. That is worth ~20x (king n=20, k<=5: 2.4e8 nodes to 1.4e7).

`cpp/perimeter_defect.cpp`, gated by `scripts/perimeter_defect_gate.sh`: pruned
counts match `build/g2 --siteperim` cell for cell on both lattices, the prune
changes nothing against an unpruned control, and the (c, H) marginals sum back.
It reaches **n = 70** on one gympie core — 913 s square, 2017 s king — where
brute force stops at 14 on king.

## The king column is the square column re-graded

Write `S` for the 3x3 box. Site perimeter is `p = |A + S| - n` and `pmax = 4n+4`,
so on the king lattice

    k = 5n + 4 - |A + S|.

Diagonal steps `(±1,±1)` preserve the parity of `x+y`; orthogonal steps flip it.
A king animal with **no orthogonal edge** therefore lives on one parity class,
and `(x, y) -> (u, v) = ((x+y)/2, (x-y)/2)` carries it bijectively onto a
polyomino `B` with the same cell count, king diagonal adjacency becoming
ordinary edge adjacency. Split `A + S` by parity:

- Cells of the animal's own parity in `A + S` are `B` together with its edge
  neighbours in the `(u,v)` frame — `n + p_4(B)` of them.
- Cells of the other parity are in bijection with the **grid vertices** of the
  `(u,v)` lattice: an odd cell's four orthogonal neighbours are exactly the four
  `(u,v)` cells meeting at one vertex. Such a cell is in `A + S` exactly when one
  of those four is in `B`, so there are `Vert(B)` of them.

Euler on the cell complex of `B` — `V - E + F = 1 - h` with `F = n`,
`E = 4n - a`, and `a` the number of adjacent cell pairs — gives
`Vert(B) = 3n - a + 1 - h`. Substituting both counts:

    k_king(A) = k_square(B) + c(B) + h(B),        c = a - n + 1.

**PROVED**, and checked cell by cell on 489,603 same-parity animals to `n = 13`,
`k <= 6` (`experiments/perimeter_defect_features.py`).

### What it costs to bend, branch and switch parity

The reduction is an isomorphism of the two pictures, so every square-lattice
feature keeps its square price. Costs are for a feature standing alone; two
features interfere only within Chebyshev distance 2, and that interference is
what the onsets measure.

| feature (king) | what it is in `B` | defect cost |
|---|---|---|
| straight diagonal step | straight step | 0 |
| 90-degree turn | bend | 1 |
| cell with 3 diagonal neighbours | T-branch | 2 |
| cell with 4 diagonal neighbours | cross | 4 |
| independent cycle | cycle | its square cost, `+1` |
| enclosed cell | hole | its square cost, `+1` |
| **orthogonal step** | not in `B` at all | 2 |

An animal of defect `k` is a tree of diagonal segments carrying features of total
cost `k` — the reduction plus the square-lattice classification, not an
independent statement. Only the last row escapes the reduction, an orthogonal
edge leaving the parity class; every animal enumerated has at most `floor(k/2)`
of them.

### The counts

Let `P(n, j, c)` be the square census graded by cycle rank (the `c` column of
`results/perimdefect_square4_n78_k6.txt`) and `M(n, k)` the king animals that do
carry an orthogonal edge. For `k <= 3` no hole is affordable — the cheapest holed
polyomino is 3x3 less its centre and one corner, `k_sq = 4`, `c = 0`, `h = 1`, so
a hole costs `k_king = 5` — and

    A_king(n, k) = sum_c P(n, k-c, c) + M(n, k)          k <= 3, exact.

Past `k = 3` the banked square census cannot supply the `h` correction, grading
by `c` and not by `h`; there the identity is checked against an independent
enumeration. Write `R(n,k)` for `A_king(n,k) - sum_c P(n, k-c, c)`, which is
`M(n,k)` for `k <= 3`:

    R(n,2) = 8n - 16                                  n >= 3
    R(n,3) = 20n^2 - 128n + 212                       n >= 4
    R(n,4) = 191/6 n^3 - 811/2 n^2 + 5786/3 n - 3456        n >= 8 even
             191/6 n^3 - 811/2 n^2 + 11581/6 n - 6937/2     n >= 9 odd
    R(n,5) = 109/3 n^4 - 2368/3 n^3 + 44155/6 n^2
                       - 104759/3 n + 69848                 n >= 12 even
                       - 104780/3 n + 139841/2              n >= 13 odd

`R(n,2) = 8(n-2)` is **derived**: at defect 2 with an orthogonal edge the animal
is two straight diagonal sticks, `a + b = n`, joined by one orthogonal edge — 16
configurations per unordered pair `{a,b}`, halved when `a=1` (a one-cell stick
has no direction) or `a=b` (the sticks swap). The enumeration confirms every
defect-2 mixed animal has that shape. The rest are interpolated and checked
against the whole census. Three consequences, derived rather than measured:

- **The leading coefficient cannot depend on the lattice.** `deg R = k-1`, and
  `P(n, k-c, c)` for `c >= 1` has degree at most `k-2`, so the `n^k` coefficient
  of `A_king(n,k)` is the `n^k` coefficient of `A_square(n,k)`.
- **The onset is the square onset.** `R`'s onsets are `3, 4, 8, 12` against class
  onsets `6, 9, 13, 18`, below at every `k`, so nothing in the king-only family
  delays the class. The triangular value `k(k+1)/2 + 3` itself remains a check on
  the square side, matched at `k = 2..6`, not a derivation.
- **The king cycle-rank cap is `c <= floor(k/3)`, not `floor(k/2)`.** A cycle in
  `B` forces `k_sq >= 2c` by the square identity, so `k_king >= 3c`. The census
  maxima are `1, 1, 1, 2` at `k = 3, 4, 5, 6` — exactly `floor(k/3)`.

## The formulae

Period, degree, onset and denominator are interpolations verified against at
least 2 spare points per residue class; the shared leading coefficient is derived
above, not fitted.

| k | period | degree | onset | denominator | leading coeff (BOTH lattices) |
|---|---|---|---|---|---|
| 0 | 1 | 0 | 2  | Φ₁    | 2 |
| 1 | 1 | 1 | 3  | Φ₁²   | 4 |
| 2 | 1 | 2 | 6  | Φ₁³   | 6 |
| 3 | 2 | 3 | 9  | Φ₁⁴Φ₂²  | 13/2 |
| 4 | 2 | 4 | 13 | Φ₁⁵Φ₂³  | 17/3 |
| 5 | 6 | 5 | 18 | Φ₁⁶Φ₂⁴Φ₃ | 593/144 |
| 6 | 6 | 6 | 24 | Φ₁⁷Φ₂⁵Φ₃² | 13325/5184 |

Square (`k=3`, n >= 9), reproducing the published result the brief could only
reach through talk slides — the `(-1)^n` is there, so we have not misread the
convention, and its part has degree 1, not 0:

    Q_3(n) = 13/2 n^3 - 89 n^2 + 1947/4 n - 2107/2 + (-1)^n (5n/4 - 21/2)

King `k=3` and `k=4` are the square ones plus `R(n,k)`, less the `c >= 1` term;
all refit in seconds by `experiments/perimeter_defect_fit.py`.

## The generating functions, and the triangle their coefficients form

At `k = 5` the fitted period is 6, but the Φ₆ component of the constant term is
**exactly zero**: the period-6 behaviour is Φ₂ and Φ₃ acting independently, not
a primitive 6th root. Φ₂ enters the `n^3` coefficient (Φ₂⁴), Φ₃ only the constant
(Φ₃¹), so across `k <= 6` the denominator is `Φ₁^(k+1) · Φ₂^(k-1) · Φ₃^(k-4)`
with each factor switching on at `Φ_d first appears at k = 2d - 1` (d=2 at k=3,
d=3 at k=5). **Prediction: Φ₄ first appears at k = 7**, untested — it needs a run
well past n = 70. If it holds, each successive prime-power periodicity costs a
fixed 2 units of defect to buy.

`experiments/perimeter_defect_gf.py` produces `G_k(x) = sum_n A(n, pmax(n)-k) x^n`
exactly. The denominator is *predicted* from the table above, not fitted, then
checked: dividing the series by it must leave a polynomial, with `gcd(N,D) = 1`
so no factor is spurious. It does, for every k on both lattices — 28 spare zero
coefficients at k=5 that the interpolation never saw.

King, with `Phi_1 = 1-x`, `Phi_2 = 1+x`, `Phi_3 = 1+x+x^2`, and `R_k` the
polynomial part carrying the pre-onset holdouts:

    G_0 = R_0 + 2/Phi_1
    G_1 = R_1 + 4/Phi_1^2 - 12/Phi_1
    G_2 = R_2 + 12/Phi_1^3 - 48/Phi_1^2 + 92/Phi_1
    G_3 = R_3 + 39/Phi_1^4 - 216/Phi_1^3 + (2445/4)/Phi_1^2 - (5135/4)/Phi_1
               + (5/4)/Phi_2^2 - (47/4)/Phi_2
    G_4 = R_4 + 136/Phi_1^5 - (1911/2)/Phi_1^4 + (14049/4)/Phi_1^3
               - (18863/2)/Phi_1^2 + (40769/2)/Phi_1
               + (5/4)/Phi_2^3 - (47/2)/Phi_2^2 + (349/2)/Phi_2
    G_5 = R_5 + (2965/6)/Phi_1^6 - 4234/Phi_1^5 + (685645/36)/Phi_1^4
               - (2225243/36)/Phi_1^3 + (139157959/864)/Phi_1^2
               - (150424703/432)/Phi_1
               + (15/8)/Phi_2^4 - (293/8)/Phi_2^3 + (10503/32)/Phi_2^2
               - (28141/16)/Phi_2
               + (40x/27 + 8/3)/Phi_3

Each block is one piece of the quasi-polynomial: `a_j/Phi_1^j` gives
`a_j*C(n+j-1, j-1)`; `b_j/Phi_2^j` the same times `(-1)^n`; `Phi_3` a bounded
period-3 wobble.

**These coefficients form their own triangle, and lattice-independence in it is
exactly one diagonal deep.** Writing rows k and columns by offset d from the top
of each block, `*` marking entries identical on square and king:

    Phi_1 block            d=0        d=1         d=2          d=3
      k=0               2*
      k=1               4*       -12*
      k=2              12*        -48          92
      k=3              39*       -216      2445/4      -5135/4
      k=4             136*    -1911/2     14049/4     -18863/2   (40769/2)
      k=5          2965/6*      -4234   685645/36  -2225243/36   (...)

    Phi_2 block            d=0        d=1         d=2          d=3
      k=3             5/4*     -47/4*
      k=4             5/4*      -47/2       349/2
      k=5            15/8*    -293/8*    10503/32    -28141/16

Every `d = 0` entry agrees across the lattices; `d = 1` already fails from k=2 in
the `Phi_1` block. The leading diagonal of each cyclotomic block is universal and
everything beneath it is lattice-specific — a diagonal statement about a triangle
of *coefficients* rather than about counts, and the closest structural analogue
to the diagonal law this grading offers. The reduction accounts for the `Phi_1`
column: `R` has degree `k-1`, so it perturbs `d >= 1` and cannot touch `d = 0`.

Neither leading diagonal has a closed form:

- `Phi_2`: `b_(k-1)` runs 5/4, 5/4, 15/8, 5/2. `5(k-2)!/2^(k-1)` fits the first
  three and predicts 15/4 at k=6, where the answer is 5/2 on both lattices — a
  coincidence of three terms. The value stays lattice-independent.
- `Phi_1`: `a_(k+1) = c_k * k!` = 2, 4, 12, 39, 136, 2965/6 — integral through
  k=4 and then not, which is what killed the `2*C(2k,k)` guess.
- `Phi_3` at k=5 is identical on both lattices **in full**, not merely in its
  leading term: `(40x/27 + 8/3)/Phi_3`. That too is a k=5 accident: at k=6 king
  carries `(-5920x^3 - 19128x^2 - 18528x - 12656)/243` against square's
  `(-5920x^3 - 18768x^2 - 18168x - 12296)/243`, agreeing only in the top
  coefficient.

The obvious triangle — `B(n,k) = A(n, pmax(n)-k)`, rows n, columns k, row sums
a(n), with the `G_k` as its column GFs — is a much weaker object than the height
triangle: the diagonal law covers every `k <= (n-1)/2` from one theorem with one
onset formula, while here each k has its own denominator. Neither triangle has
been checked against OEIS or the literature.

## An exact identity relating n, H and p on the king lattice

The minimum defect over king animals of `n` cells and bounding-box height `H` is
**exactly** `k_min(n,H) = ceil((n-H)/(H-1))` for `H >= 2` — zero violations and
equality *attained* in all 672 (n,H) cells present at `k <= 5`, `n <= 40`, so no
better bound exists. Equivalently `H >= (n+k)/(k+1)`, and by transposition the
same with the width. Hence `k = 0` forces `H = W = n` (the diagonal sticks) and
`k = 1` forces both dimensions `>= (n+1)/2`.

**On the square lattice there is essentially nothing**: `k_min(n,H) = 0` for
`H in {1, n}` and `1` for every `H` between, because the two square defect-0
animals are the horizontal *and* vertical sticks, at opposite ends of the height
range. Both king defect-0 animals are diagonal sticks with `H = n`, which is why
the king bound bites — the asymmetry
`experiments/perimeter_vs_height_defect.py` saw from the marginal side.

## Closed doors

- **The king parity term is the square parity term.** `R(n,3)` has period 1, so
  by the reduction the king `k=3` quasi-polynomial differs from the square one by
  a plain polynomial: even minus odd is `5n/2 - 21` on both. The hunt for a
  king-side source of the `(-1)^n` is therefore over — it is inherited. It is
  carried by the acyclic animals (the `c >= 1` parts are plain and tiny: square
  k=3, c=1 is the constant 8), by no single height slice (every `H = n - j` is a
  plain polynomial on both lattices), and not by the height floor, whose period
  `k+1` predicts 5 at `k=4` where the answer is 2.
- **`c_k · k! = 2·C(2k,k)` is dead.** Leading coefficients times `k!` run
  2, 4, 12, 39, 136 against 2, 4, 12, 40, 140; at `k=5` the product is not even
  an integer.
- **Task A (the dalby enumeration run) is not worth doing.** Scoped to reach
  n=16 on king in ~17 CPU-hours as an independent source; the pruned enumerator
  reaches n=70 in 2017 s on one gympie core, cross-validated against g2 over the
  whole range g2 can reach.
- **`scripts/dalby_perimeter_defect_pool.sh`'s cost header is refuted.** It
  predicted ~136 core-hours and ~1.8 h wall for king n=78 from `time ~ n^7.9`;
  the run took 42 h wall at 76-way, ~23x. Not calibration for anything else.

## Status of these claims

| claim | status |
|---|---|
| `k = 2c + t - (deg/2 - 2)(n-1)`, and the monotonicity | proved |
| `k_king = k_square + c + h` for animals with no orthogonal edge | proved |
| `A_king(n,k) = sum_c P(n,k-c,c) + M(n,k)`, `k <= 3` | proved |
| the same for `k = 4, 5, 6` | checked, `n <= 12` |
| leading coefficient lattice-independent; onset = square onset | derived from the above |
| `A_king(n,k)` for `k <= 4`, `R(n,k)` for `k <= 5` | checked to n=78 |
| `M(n,2) = 8(n-2)` | derived |
| period, degree, denominator, onset per class | interpolated, not derived |
| the triangular onset `k(k+1)/2 + 3` | checked at k=2..6 |

The interpolated rows are conjectures supported by exact values with holdouts —
the opposite of the height diagonal law, a theorem with a proved degree bound and
a proved sharp onset (`docs/proofs/universal-diagonal-law.md`,
[[diagonal-law-proved]]). Note that the onset is *not* the first appearance of a
defect-k animal: a tight zigzag reaches defect k at n = k+2, far below
`k(k+1)/2 + 3`. The onset is where the last short-range interference between
features dies out.

Novelty: the 2026-08-18 priority pass obtained the Asinowski--Barequet--Zheng
full text (`papers/asinowski_barequet_zheng_2018_polycubes_small_perimeter_defect.pdf`),
so the square column reproduces rather than extends them, and the identity, the
rationality theorem and the degree conjecture are theirs. The king column, the
parity reduction and the `n`/`H`/`p` identity were not found anywhere.

## Reproduce

    make build/perimeter_defect
    scripts/perimeter_defect_gate.sh                       # must print GATE PASSED
    ./build/perimeter_defect square8 40 5 > k.txt
    python3 experiments/perimeter_defect_fit.py k.txt --lattice square8
    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n70_k5.txt
    python3 experiments/perimeter_defect_gf.py \
        results/perimdefect_square{8,4}_n70_k5.txt --compare
    python3 experiments/perimeter_defect_features.py   # the reduction and the
                                                       # closed forms, fail-closed

Census data kept: `results/perimdefect_square{4,8}_n{40,60,70,78}_k{5,6}.txt`
(n, k, c, H, count); `results/siteperim_square4_n20.txt` and
`results/siteperim_square8_n14.txt` (g2 brute-force cross-checks);
`results/king_joint_nhp_n9.txt`, `results/king_triple_classes_n9.txt` and
`results/bbox_square4_n21.txt`.

## The n = 78, k <= 6 censuses

Run on dalby 2026-08-07/08-10 under `scripts/dalby_perimeter_defect_pool.sh`
(456 shards, 76-way, splitS=14, `git=6473890c`), both merged 456/456
`result=ok`: king 151,915 s wall and 3,948,974,545,893 animals, square 83,667 s
and 3,168,296,567,027. Analysed with `perimeter_defect_gf.py --kmax 6` (the
default `--kmax` is 5, which is why a first pass shows nothing at k = 6). The
predicted `Phi_1^7 Phi_2^5 Phi_3^2` divides exactly — `deg(N) = 39`,
`gcd(N,D) = 1`, 22 spare zero coefficients — so the `Phi_3` exponent `k-4` no
longer rests on the single point at k = 5, no `Phi_4` factor is needed, and
`deg(N) - deg(D) = 23` puts the onset at 24, as the triangular formula predicts.
