# Perimeter-defect diagonals: the perimeter grading is quasi-polynomial on both lattices

2026-08-07, executing `docs/perimeter-defect-plan.md`.

## The answer in one paragraph

Grading fixed animals by **site-perimeter defect** `k = pmax(n) - p` gives a
quasi-polynomial count on the king lattice exactly as it does on the square one:
`k = 3` carries a genuine period-2 term on both. So quasi-polynomiality is
**intrinsic to the perimeter grading, not a square-lattice artefact** — the
brief's question 1, answered. But the finding is stronger and cuts both ways.
Through `k = 5` the period, the degree, the onset and the *leading coefficient*
of the defect-k formula are **identical on square and king**; only the
sub-leading coefficients differ. The height grading is the reverse: plain
polynomials (proved, `docs/proofs/universal-diagonal-law.md`), but with
thoroughly lattice-dependent coefficients — `4n - 8` on square against
`25n - 45` on king. So the height grading is cleaner in *form* and the perimeter
grading is more universal in *content*. Neither dominates, and the honest claim
for Paper 2 is the narrow one: the diagonal law is clean because it is a proved
plain polynomial with a sharp onset, not because the perimeter grading is
somehow defective.

## What made this cheap: the defect is monotone

The plan proposed a surplus-budgeted row DP on the model of
`experiments/diagonal_machine.py`. That cannot work here — the perimeter defect
does not bound the transverse extent of a linear sweep (a U with arms far apart
has `k = 3` and unbounded spread), which is presumably why the published method
classifies patterns instead of sweeping.

What does work is simpler. Write `c` for the cycle rank `e - n + 1` of the
adjacency graph and `t` for the sum over empty adjacent cells of
(animal-neighbours − 1). Then

    k = 2c + t,

both terms non-negative, and consequently **k never decreases when a cell is
added**: placing a cell raises `pmax` by `deg/2` and changes `p` by `-1 + g`,
where `g` counts the neighbours that become fresh perimeter cells, and `g` is
capped by the neighbours the new cell shares with the animal cell it touches.
The bound is tight on both lattices (a stick extends at `dk = 0`). So a
Redelmeier DFS that abandons a partial animal the moment `k > kmax` is exact.

A second monotonicity makes it fast: a candidate cell's *cost* `dk` is itself
non-decreasing as the animal grows, so a candidate over budget is over budget
forever and can be dropped from the untried list rather than re-tested at every
node. That is worth ~20x (king n=20, k<=5: 2.4e8 nodes to 1.4e7).

`cpp/perimeter_defect.cpp`, gated by `scripts/perimeter_defect_gate.sh`:
pruned counts match `build/g2 --siteperim` cell for cell on both lattices, the
prune is confirmed to change nothing against an unpruned control run, and the
(c, H) marginals sum back. It reaches **n = 70** on both lattices on a single
gympie core — 913 s on square, 2017 s on king — where brute force stops at 14 on
king.

## The formulae

Both lattices, `k = pmax(n) - p` with `pmax = 2n+2` (square4) and `4n+4`
(square8). Fits are exact interpolations verified against at least 2 spare
points per residue class, with the onset checked to be sharp.

| k | period | degree | onset | denominator | leading coeff (BOTH lattices) |
|---|---|---|---|---|---|
| 0 | 1 | 0 | 2  | Φ₁    | 2 |
| 1 | 1 | 1 | 3  | Φ₁²   | 4 |
| 2 | 1 | 2 | 6  | Φ₁³   | 6 |
| 3 | 2 | 3 | 9  | Φ₁⁴Φ₂²  | 13/2 |
| 4 | 2 | 4 | 13 | Φ₁⁵Φ₂³  | 17/3 |
| 5 | 6 | 5 | 18 | Φ₁⁶Φ₂⁴Φ₃ | 593/144 |

Square (`k=3`, n >= 9), reproducing the published result the brief could only
reach through talk slides:

    Q_3(n) = 13/2 n^3 - 89 n^2 + 1947/4 n - 2107/2 + (-1)^n (5n/4 - 21/2)

The `(-1)^n` is there, so we have not misread the slides or the convention.
Note the parity part has degree 1, not 0. King (`k=3`, n >= 9), the same shape
with different sub-leading coefficients:

    n even:  13/2 n^3 - 69 n^2 + 360 n   - 860
    n odd:   13/2 n^3 - 69 n^2 + 715/2 n - 839

King `k=4` (n >= 13) and both lattices' `k=5` (n >= 18, period 6) are in
`results/perimdefect_square*_n*_k5.txt` and refit in seconds by
`experiments/perimeter_defect_fit.py`.

## The cyclotomic content is finer than the period

At `k = 5` the fitted period is 6, but the Φ₆ component of the constant term is
**exactly zero**: the period-6 behaviour is Φ₂ and Φ₃ acting independently, not
a primitive 6th root. Reading the exponents off where each factor first
perturbs a coefficient: Φ₂ enters the `n^3` coefficient (so Φ₂⁴) and Φ₃ only the
constant (Φ₃¹).

So across `k <= 5` the denominator is `Φ₁^(k+1) · Φ₂^(k-1) · Φ₃^(k-4)`, with
each factor switching on at

    Φ_d first appears at k = 2d - 1        (d=2 at k=3, d=3 at k=5)

**Prediction: Φ₄ first appears at k = 7**, and no `k <= 6` formula carries a
period-4 term. Untested — `k = 7` needs a run well past n = 70. If it holds, the
"quasi-polynomial" label is coarse and what is really happening is that each
successive prime-power periodicity costs a fixed 2 units of defect to buy.

## The generating functions, and the triangle their coefficients form

`experiments/perimeter_defect_gf.py` produces `G_k(x) = sum_n A(n, pmax(n)-k) x^n`
exactly. The denominator is not fitted: it is *predicted* from the table above as
`Phi_1^(k+1) . Phi_2^(k-1) . Phi_3^(k-4)` and then checked — dividing the n<=70
series by it must leave a polynomial. It does, for every k on both lattices, with
`gcd(N, D) = 1` so no factor is spurious. For k=5 that is 28 consecutive exact
zero coefficients the interpolation never saw, a far harder test than the
2-spare-per-class bar the formulae were fitted at.

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
`a_j*C(n+j-1, j-1)`, the plain part; `b_j/Phi_2^j` the same times `(-1)^n`; the
`Phi_3` block a bounded period-3 wobble.

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
the `Phi_1` block. So the leading diagonal of each cyclotomic block is universal
and everything beneath it is lattice-specific. That is a diagonal statement about
a triangle of *coefficients* rather than about counts, and it is the closest
structural analogue to the diagonal law that this grading offers.

Of the two leading diagonals, one closes and one does not:

- **`Phi_2`: b_(k-1) = 5(k-2)!/2^(k-1)`, exactly, both lattices** (5/4, 5/4,
  15/8). Predicts 15/4 at k=6.
- `Phi_1`: `a_(k+1) = c_k * k!` = 2, 4, 12, 39, 136, 2965/6 — integral through
  k=4 and then not, which is what killed the `2*C(2k,k)` guess. No closed form.
- `Phi_3` at k=5 is identical on both lattices **in full**, not merely in its
  leading term: `(40x/27 + 8/3)/Phi_3`. The entire period-3 content of the
  perimeter grading is lattice-independent.

The obvious triangle — `B(n,k) = A(n, pmax(n)-k)`, rows n, columns k, row sums
a(n), with the `G_k` as its column GFs — exists but is a much weaker object than
the height triangle. The diagonal law covers every `k <= (n-1)/2` from ONE
theorem with ONE onset formula; here each k is its own problem with its own
onset (2, 3, 6, 9, 13, 18 — no law found) and its own denominator. Neither
triangle has been checked against OEIS or the literature.

## An exact identity relating n, H and p on the king lattice

The minimum defect over king animals of `n` cells and bounding-box height `H` is
**exactly**

    k_min(n, H) = ceil((n - H) / (H - 1))        for H >= 2

— zero violations and equality *attained* in all 672 (n,H) cells present at
`k <= 5`, `n <= 40`, so it is sharp and no better bound exists. Equivalently

    H >= (n + k) / (k + 1)     i.e.    p <= 4n + 4 - ceil((n-H)/(H-1))

and by transposition the same with the width `W`. Hence `k = 0` forces
`H = W = n` (the diagonal sticks) and `k = 1` forces both dimensions `>= (n+1)/2`.

**On the square lattice there is essentially nothing**: `k_min(n,H) = 0` for
`H in {1, n}` and `1` for every `H` between. The reason is structural — the two
square defect-0 animals are the horizontal *and* vertical sticks, at opposite
ends of the height range, so no height is ever more than one defect unit from
optimal. Both king defect-0 animals are diagonal sticks with `H = n`, which is
why the king law bites. This is the same asymmetry that
`experiments/perimeter_vs_height_defect.py` saw from the marginal side.

## Closed doors

- **The parity is not carried by the cyclic animals.** Splitting each class by
  cycle rank: the `c >= 1` parts are plain polynomials and tiny (square k=3,
  c=1 is the constant 8; king k=3, c=1 is one animal at n=4 and nothing after).
  All of the `(-1)^n` sits in the acyclic animals, so the appealing "a ring has
  an even cell count" story is dead.
- **It is not carried by any single height slice.** Every slice `H = n - j` at
  fixed `j` is a plain polynomial on both lattices.
- **It is not the height floor either.** The floor law above has period `k+1`,
  and the near-floor king slices do oscillate with period 4 at `k=3`
  (`[4, 2, 20, 12, 4, 2]`) — but it predicts period 5 at `k=4` where the answer
  is 2, and the square lattice has no meaningful floor at all yet shows the
  identical period. The floor contributes; it is not the source.
- **`c_k · k! = 2·C(2k,k)` is dead.** The leading coefficients times `k!` run
  2, 4, 12, 39, 136 against `2·C(2k,k)` = 2, 4, 12, 40, 140, tempting through
  `k=4`; `k=5` gives 593/144, whose product with `5!` is not even an integer.
- **Task A (the dalby enumeration run) is not worth doing.** It was scoped to
  reach n=16 on king in ~17 CPU-hours as an independent source for k=3/k=4. The
  pruned enumerator reaches n=70 on king in 2017 s on one gympie core and is
  already cross-validated against g2 over the whole range g2 can reach, which is
  a stronger check than a second brute-force run at n=16 would have been.

## Status of these claims

Everything above is **measured and interpolated, not proved**. The degree bound
and onset are read off the data, not derived, so each row of the table is a
conjecture supported by exact values with holdouts and spare-point checks — the
opposite of the height diagonal law, which is a theorem with a proved degree
bound and a proved sharp onset (`docs/proofs/universal-diagonal-law.md`,
[[diagonal-law-proved]]). The `k = 2c + t` identity and the monotonicity that
licenses the prune ARE proved, in the header of `cpp/perimeter_defect.cpp`, and
they are what makes the values trustworthy.

Novelty unchecked against the literature: Asinowski, Barequet, Magal & Zheng
(Comput. Geom. 108 (2022) 101919) is paywalled and we hold only the talk slides,
so the square column here reproduces rather than extends them. The king column
and the `n`/`H`/`p` identity have not been searched for in the literature.

## Reproduce

    make build/perimeter_defect
    scripts/perimeter_defect_gate.sh                       # must print GATE PASSED
    ./build/perimeter_defect square8 40 5 > k.txt
    python3 experiments/perimeter_defect_fit.py k.txt --lattice square8
    python3 experiments/perimeter_defect_gf.py results/perimdefect_square8_n70_k5.txt
    python3 experiments/perimeter_defect_gf.py \
        results/perimdefect_square{8,4}_n70_k5.txt --compare

Census data kept: `results/perimdefect_square{4,8}_n{40,60,70}_k5.txt` (n, k, c,
H, count), `results/siteperim_square4_n20.txt` and
`results/siteperim_square8_n14.txt` (the g2 brute-force cross-checks),
`results/king_joint_nhp_n9.txt` and `results/king_triple_classes_n9.txt` (the
(n,H,p) joint census behind the identity above), `results/bbox_square4_n21.txt`.
