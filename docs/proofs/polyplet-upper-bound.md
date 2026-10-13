# Upper bound on the polyplet growth constant λ

**Result.** λ ≤ 20000/2147 = 9.3153237…, so **λ ≤ 9.3154**, by an exact
rational certificate for a finite-type convolution system in the manner of
Bui (arXiv:2510.06806). The two-sided rigorous bracket is
**6.543 ≤ λ ≤ 9.3154**; the lower side is the certified strip ladder μ₁₇
(`results/growth-constant.md`). No polyplet upper bound was published before
this one.

On the decimal: 20000/2147 rounded to nearest at four places is 9.3153, which
is below the true value, so "λ ≤ 9.3153" would assert 3.2e-5 more than is
proved. An upper bound rounds away from the truth: 9.3154. Code should use the
rational `20000/2147` (`experiments/concatenation_bound_check.py` does;
`paper/verify_l_papers.py` rejects the truncated form).

## 1. The system and its certificate

### 1.1 The marked-cell type

Let `A(n)` count fixed polyplets of n cells and `G8(n)` the number of pairs
(animal, marked cell) such that the marked cell's W, SW, S and SE neighbors are
all empty (a cell that is minimal in scan order qualifies, so every animal
contributes at least once). Then `A(n) ≤ G8(n) ≤ n·A(n)`, so `G8` has growth
rate exactly λ. Measured at n = 1..7, `G8(n)/A(n)` = 1.0, 1.0, 1.1, 1.23, 1.36,
1.50, 1.63: growing, but only as the polynomial prefactor allowed by
`G8 ≤ n·A`. The anchor leaks no exponential.

### 1.2 The recurrence system

A **type** `T` is a finite neighborhood pattern around the marked cell `c`:
some cells known occupied, some known forbidden (empty), the rest free. Case
on one free cell `d` at a time:

    φ_T = φ_{T'} + φ_{T'} · φ_D

where `T' = T + {d forbidden}` and `D` is `d`'s split-off type. The branch with
`d` empty is an exact partition (`{type T, d empty} = type T'`). The branch
with `d` occupied is a valid over-count: the animal is cut into a `c`-side
and a `d`-side, each counted by its own type, and reassembly over-counts
because the two pieces may overlap or touch far from the cut. Two details
make the over-count tight enough to be useful: multi-neighbor cases stay as
convolutions (both pieces preserved) rather than being re-marked linearly, and
the split-off type `D` records that all of `c`'s other neighbors belong to the
`c`-side, so they are empty in the `d`-piece.

The free cells cased on lie within a window of radius `RD` around the marked
cell; the closure of types under the rule is finite for each `RD`. Every
recurrence was verified as a valid over-count against brute-force A006770
counts for `RD ≤ 2`; larger `RD` is valid by construction (more genuinely
empty cells in the split type make the over-count tighter and still an
over-count). Implementation: `experiments/king_bui.py`.

| RD (split window) | types | λ ≤ (numerical) |
|---|---|---|
| 1 | 21 | 10.354 |
| 2 | 185 | 9.402 |
| 3 | 5930 | 9.306 |

The window lever saturates near 9.3 (RD = 2 → 3 moved 0.096). The choice of
which free cell to case on has no effect: left-to-right, right-to-left,
diagonal-first and orthogonal-first orderings give the same 185-type closure
and the same 9.4022 at RD = 2 (`DORDER=` in `experiments/king_bui.py`). The
bound is a spectral property of the closed system.

### 1.3 The certificate

Write the system as `φ = F_x(φ)` with `x` the weight per cell. If a vector
`u > 0` of rationals satisfies `u_T ≥ F_x(u)_T` for every type `T`, then by
monotonicity of `F_x` the iteration from 0 is bounded by `u`, so the series
converge at `x` and λ ≤ 1/x.

`experiments/king_certificate.py` finds such a `u` and checks every inequality
in exact `fractions.Fraction` arithmetic. At RD = 3, `x = 2147/20000` with a
5930-component certificate (denominators ≤ 10⁶): every inequality holds, so
**λ ≤ 20000/2147**, with no floating point in the chain. The gap between
9.3154 and the numerical 9.306 is a deliberate safety margin `eps` (about
0.1%) so the super-solution has room; shrinking it tightens toward 9.306 at
the cost of larger fixpoint values. Cross-check at RD = 2: `x = 106251/10⁶`
gives λ ≤ 9.4117, PASS.

### 1.4 Where the slack is

`experiments/king_slack.py` measures `slack(T,n) = rhs(T,n) / true_count(T,n)`
for every recurrence of the RD = 2 system against brute force.

- Diffuse, not concentrated. Over 152 recurrences: max slack 1.222, median
  1.144, min 1.000; nothing above 1.5, only 4 above 1.2. The loosest are the
  far-reach split types (|T| ≈ 10, window distance 2). No small set of types
  to hand-engineer; fixing the top four barely moves the bound.
- Grows with n: `slack@8 − slack@7 ≈ +0.022` per term (median). A purely local
  over-count would be constant in n; growth means the over-count accumulates
  with animal size. In `φ_{T'}·φ_D` the d-piece and the c-side may wrap around
  and collide arbitrarily far from the cut, and no finite window forbids it.

So the over-count is intrinsic to finite-type convolution: diffuse,
compounding, non-local. Multi-cell exact casing only relocates it (that is the
leaf/cut structure of section 3, measured at ≈12.5, worse). Required-cell
types can make cuts locally exact but cannot forbid distant overlaps. The
polyomino instance of the method leaves about 14% (4.63 against 4.06); here
about 31% (9.31 against the estimate 7.11), and the king slack grows with n
where the rook slack saturates, so 8-connectivity is worse for this method.
Reaching ~8 would need the full hand-engineered required-cell apparatus for at
most one more term of λ, never λ itself.

## 2. The crude bound: λ ≤ 5⁵/4⁴ = 3125/256 ≈ 12.2

Process the animal's cells breadth-first from the scan-minimum root. A
processed cell `u` with parent `d` encodes, as one letter, which cells of its
**frame** — `N(u)` minus `{d}` minus the shared set `N(u) ∩ N(d)` — it newly
opens. Shared sets have 4 cells for orthogonal `d` and 2 for diagonal `d`, so
frames have 3 or 5 slots; coverage holds because
`N(u) = {parent} ∪ shared ∪ frame` and `shared ⊆ N(parent(u))` recurses to the
root (whose frame is all 8). Each n-cell animal maps injectively (replay
decoder) to n letters of total weight `x^(n−1) y^n`; the letter alphabet is the
5-bit mask family with `Σ x^(opens) = (1+x)⁵`, so
`a(n) ≤ [x^(n−1)] (1+x)^(5n) · O(1)` and `λ ≤ min_b (1+b)⁵/b = 5⁵/4⁴` at
`b = 1/4`. ∎ Machine-verified (round-trip, distinctness, weight identity,
alphabet census) over all animals n ≤ 8, with a control that drops a frame
slot and must fail (`experiments/kingtwigs/l1_schemes.py`).

This is the Eden level of the twig method: alphabet = all occupancy patterns
of the `K` newly exposed neighbors, `A(x) = (1+x)^K`, bound `K^K/(K−1)^(K−1)`;
rook `K = 3` gives 6.75, king `K = 5` gives 12.2.

A scan-order version of the same argument ("when a cell is included, only
its ≤ 4 king-neighbors ahead in scan order newly enter the frontier, so
`a(n) ≤ C(5n, n)`") is wrong: *behind* does not mean *already considered*. A
re-entrant animal whose cell attaches only from below-behind, such as the hook
`{(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(3,1)}` where `(3,1)` is an
ahead-neighbor of no included cell, never enters the frontier, so the map from
animals to decision strings is undefined on it. That scheme misses 2 of 20
animals at n = 3 and 96,065 of 147,941 at n = 8. The BFS-frame derivation
above gives the same constant soundly.

The Klarner–Rivest deferral, which improves the rook Eden bound, is blocked on
king adjacency: a deferred cell always lands in the child's shared set
(`results/growth-constant.md`, which closes the twig route at exactly 5⁵/4⁴).

**Two tempting bounds that are false.** Encoding by spanning-tree
parent-direction (≤ 8 per cell, hence "λ ≤ 8") is not an injection: the same
argument gives λ ≤ 4 for polyominoes, against λ_poly ≈ 4.06. Encoding by the
Redelmeier growth tree (each cell has ≤ 4 forward king-neighbors, hence a
4-ary tree and "λ ≤ 4⁴/3³ ≈ 9.48") fails the same way: the growth tree is a
spanning tree, it drops the animal's cycles, and animal → tree is not
injective; for polyominoes it would give λ ≤ 4. Only the full decision
sequence, which records the exclude decisions on already-adjacent cells, is
injective, and that is the `C(5n,n)` count. Every candidate bound is checked
against the rook analog before it is quoted.

## 3. Routes that do not beat the certificate

**The generic twig decomposition.** The `G8` corner cell decomposes into 12
leaf cases and 3 cut cases (the cuts are exactly the NW-stranding shapes).
Every leaf reduction (`case_count(n) ≤ reduced_type(n−1)`) and every cut
convolution (`cut(n) ≤ Σ piece1(i)·piece2(j)`) is a numerically verified
over-count; the closure is 24 types at R = 1, 28 with required-cell tracking
(`experiments/king_types.py`, `king_derive.py`, `king_bound.py`,
`king_bound2.py`, `king_bound_fast.py`).

| approach | types | bound |
|---|---|---|
| generic twig, R = 1 | 28 | 12.50 |
| generic twig, R = 1, required-cell tracking | 28 | 13.00 |
| generic twig, R = 2 | 8740 | 12.5382 |

Worse than the crude 12.2 and not improved by context: the looseness is the
case-routing (multi-neighbor cases as lossy linear re-marks instead of
convolutions), which section 1.2 fixes.

**Relaxed-connectivity strip transfer matrices.** Dropping the connectivity
check from the strip engine counts column sequences that are only
king-compatible consecutively, an over-count at each height `H`. But its
growth `ν_H` is height-limited (`ν_1 = 1`), so it is not an upper bound on λ:
height limitation under-counts and relaxation over-counts, and they do not
cancel. A valid bound needs a bounded cross-section that does not cap the
animal's extent, which is what the twig method's geometric series provides.
A transfer matrix on the Redelmeier generation queue fails for the same
reason: that state is unbounded (queue length ∝ perimeter).

**Concatenation.** Barequet–Ben-Shachar–Osegueda's quasi sub-multiplicativity
gives an upper bound from a single term: with a(40), a degree-2 reassembly
polynomial would yield λ ≤ 7.745 (degree 4 already yields nothing). But their
lexicographic split shatters a king comb into about n/4 components
(measured), so the reassembly code is `n^Θ(n)`, and the connected (centroid)
split cannot prescribe halves to within `O(1)`. The missing lemma would also
beat the polyomino record 4.5252 → 4.3828 from published terms, so it is
known-hard. `results/growth-constant.md`.

## 4. Tools

- `experiments/kernel_bound.py`, `experiments/kernel_system.py`: single-kernel
  and full-system singularity extraction; reproduce Bui's polyiamond
  `λ_T ≤ 3.6108` (`z/x = 1 + z + z² + z³`, root of `2z³ + z² − 1`,
  `λ_T = 1 + 2z + 3z²`).
- `experiments/certificate_bound.py`: Bui's monotone-iteration finder and
  exact rational certificate checker; reproduces the rook 6-type `λ₂ ≤ 4.63`
  (finder 4.6287; Bui's certificate `x = 100/463` verified exactly). The rook
  system is in `rook_step`.
- `experiments/king_bui.py`, `experiments/king_certificate.py`,
  `experiments/king_slack.py`: the king system, its certificate, and the slack
  audit of section 1.
