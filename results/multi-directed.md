# Multi-directed king animals — Bacher's definition pinned, 200 terms (2026-08-05)

`docs/middle-kingdom-plan.md` Phase 1c. Closes the repo's self-contradiction
about what "multi-directed" means, and turns the row from "NOVEL (0 terms)" into
a 200-term series with a 12-digit growth constant.

Source: Axel Bacher, *Directed and multi-directed animals in the king's lattice*,
arXiv:1301.1365v3 (28 Oct 2015), now in
[../papers/bacher_2015_directed_multidirected_king_lattice.pdf](../papers/bacher_2015_directed_multidirected_king_lattice.pdf).

## Bacher's Definition 2, as the paper actually states it

For an animal `A` and abscissa `i`, let `b(i)` be the ordinate of the bottommost
site of `A` in column `i` (`+∞` if that column is empty; king-connectivity makes
the occupied columns an interval, so the only `+∞` values are the two sentinels
past the ends).

- A **source** is a site realising a *local minimum* of `b`.
- A **keystone** is a site realising a *local maximum* of `b`.
- On a plateau of equal `b`, the leftmost column takes the mark. With `+∞`
  sentinels the extrema alternate source, keystone, …, source: `s` sources and
  `s−1` keystones.

`A` is **multi-directed** iff both hold:

1. every site of `A` is reachable from **some** source by a forward-cone path
   (`{W, NW, N, NE, E}`) staying inside `A`;
2. every keystone `t` is reachable from a source strictly to its **left** *and*
   from one strictly to its **right**, along paths that pass through no other
   keystone at `t`'s own height.

A directed animal has one source and no keystone, so directed ⊂ multi-directed.
Proposition 3 of the paper makes this a bijection with **connected heaps of
segments** (heaps with no empty column), which is where the enumeration comes
from.

**Two things the repo had assumed were in this definition and are not.** The
sources are not confined to the global bottom row: a local minimum of `b` can
sit at any height. And a split bottom row is neither necessary nor sufficient;
condition 2 is a real extra constraint with no bottom-row phrasing at all.

## Control B is neither multi-directed nor a superset of it — it is incomparable

"Control B" (`dir5nb` / the `ctrlB` grid column) floods forward from every cell
of the **global** bottom row. Measured cross-tabulation, from-scratch Python
brute force over all fixed king animals
(`python3 experiments/multidirected_king.py 12 --crosstab 8`):

| n | both | multi-directed only | control B only | neither | m(n) | all (A006770) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 0 | 0 | 1 | 1 |
| 2 | 4 | 0 | 0 | 0 | 4 | 4 |
| 3 | 20 | 0 | 0 | 0 | 20 | 20 |
| 4 | 106 | 4 | 0 | 0 | 110 | 110 |
| 5 | 576 | 60 | 0 | 2 | 636 | 638 |
| 6 | 3179 | 611 | 0 | 42 | 3790 | 3832 |
| 7 | 17732 | 5304 | **4** | 552 | 23036 | 23592 |
| 8 | 99670 | 42276 | **78** | 5917 | 141946 | 147941 |

Both off-diagonal cells are non-empty, so **neither class contains the other**.

**Multi-directed, not control B** — smallest witness, n=4 (four of them):

```
.X.      b = (0, 2, 1);  sources (0,0) and (2,1);  keystone (1,2)
X.X
X..
```

`(2,1)` is a source in Bacher's sense — column 2's bottom is a local minimum of
`b` — but it is not on the global bottom row, and no cone path reaches it from
`(0,0)`. Control B rejects; Definition 2 accepts.

**Control B, not multi-directed** — smallest witness, n=7 (four of them):

```
...X.    b = (0, 1, 2, 0, 1);  sources (0,0) and (3,0);  keystone (2,2)
..X.X
.X..X
X..X.
```

Every cell is reachable from the bottom row `{(0,0), (3,0)}`, so control B
accepts. But the keystone `(2,2)` is reachable only from the left source
`(0,0)`; walking back from it hits nothing at `(3,2)`, `(3,1)` or `(2,1)`, so no
path connects it to the right source `(3,0)`. Condition 2 fails.

So "a split bottom row makes an animal multi-directed" is wrong in both
directions. Control B's status as a separate sequence, already recorded in
[directed-cone-anchor.md](directed-cone-anchor.md), is confirmed and sharpened:
it matches neither A047781, nor A006770, nor Bacher.

## Terms: three independent routes

| route | what it is | reach |
|---|---|---|
| **generating function** | `M = D/(1−B)` from the Nordic decomposition (Theorem 8), exact integer power series | n = 400 in 30 s; n = 200 in 2.1 s |
| **brute force (C++)** | Redelmeier DFS over ALL fixed king animals, Definition 2 evaluated on each | n = 14, 162.5 s wall / 1290.5 s cpu, 8 threads |
| **brute force (Python)** | from-scratch frozenset growth, dict reachability, shares no code with either | n = 8 |

The GF side is:

```
S = t(1+S)^2 / (1 - t(1+S))            half-animals, A001003
R = S + t(1+S)
D = S + S^2/(1-R)                      directed, A047781
Q = (2-2t)S - t
B = sum_{k>=0} S(1+S)^k * QR^k/(1-QR^k)
M = D/(1-B)
```

`v(S) = v(R) = v(Q) = 1`, so the k-th summand of `B` has valuation `k+2` and the
sum is a well-defined formal power series — only `k ≤ N−2` matters mod `t^(N+1)`.

**Zero mismatches.** Series vs C++ brute force agree for every n = 1…14; the
Python brute force agrees with both for n = 1…8; the unfiltered totals in the
same C++ runs reproduce A006770 to n = 14 as a free control.

| n | m(n) multi-directed | d(n) directed A047781 | control B | all A006770 |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 |
| 2 | 4 | 4 | 4 | 4 |
| 3 | 20 | 19 | 20 | 20 |
| 4 | 110 | 96 | 106 | 110 |
| 5 | 636 | 501 | 576 | 638 |
| 6 | 3790 | 2668 | 3179 | 3832 |
| 7 | 23036 | 14407 | 17736 | 23592 |
| 8 | 141946 | 78592 | 99748 | 147941 |
| 9 | 883360 | 432073 | 564430 | 940982 |
| 10 | 5538098 | 2390004 | 3209194 | 6053180 |
| 11 | 34917224 | 13286043 | 18316729 | 39299408 |
| 12 | 221125102 | 74160672 | 104872413 | 257105146 |
| 13 | 1405276324 | 415382397 | 602013085 | 1692931066 |
| 14 | 8956020294 | 2333445468 | 3463412836 | 11208974860 |

`m(n) = A006770(n)` for n ≤ 4: every king animal of area ≤ 4 is multi-directed.
The first two that are not appear at n = 5.

Full list n = 1…200: [multidirected_terms_n200.txt](multidirected_terms_n200.txt).

## Growth constant: 6.4752, and not 6.118

The trap Phase 1c exists to avoid is `1/ρ_B ≈ 6.118`, the pole of the
*intermediate* series `B` (Lemma 11, root of `1 − 5ρ − 7ρ² + ρ³ = 0`). The
growth constant is `1/ρ_M` with `B(ρ_M) = 1` (Theorem 10, Corollary 12).

Measured on the 400-term series:

```
m(50)/m(49)   = 6.473424386397
m(100)/m(99)  = 6.475173428889
m(200)/m(199) = 6.475196273747
m(300)/m(299) = 6.475196280295
m(400)/m(399) = 6.475196280297     Aitken-extrapolated: 6.475196280297
```

`µ = 6.475196280297`. `M` has a simple pole, so `m(n) ~ Cµⁿ` (Corollary 12
writes the constant `λ`; renamed here, `λ` is the polyplet growth constant
everywhere else in this repo) with *no*
subexponential factor, and the ratios converge geometrically at rate
`ρ_M/ρ_B = 0.9448` — which is why 400 terms pin twelve digits. This
independently confirms Bacher's numerically-stated `6.475…` (Corollary 12) and
extends it; it remains numerical, with no algebraic minimal polynomial, because
`ρ_M` is defined transcendentally through the non-D-finite `B`.

Consistency with the λ bracket: `6.4752 < 6.543`, the certified strip-ladder
lower bound ([strip-mu-certificates.md](strip-mu-certificates.md)). Required,
since multi-directed ⊂ all polyplets. It also means the multi-directed bound,
best available in 2026-07, has been overtaken and stays overtaken now that its
value is known to twelve digits.

## Tools

| file | role |
|---|---|
| `experiments/multidirected_king.py` | the GF scheme, the from-scratch Python brute force, `--crosstab` |
| `cpp/directed_cone_anchor.cpp` modes `mdir` / `mdirbad` | Definition 2 on the Redelmeier enumeration; `mdirbad` drops condition 2 |
| `tests/gate_multidirected.py` (`make gate-multidirected`) | GREEN 2026-08-05 |
| `results/multidirected_terms_n200.txt` | n = 1…200 |

Reproduce:

```
make build/directed_cone_anchor && make gate-multidirected          # ~15 s
build/directed_cone_anchor mdir 14 8                                # 162 s
python3 experiments/multidirected_king.py 200 --out results/multidirected_terms_n200.txt
python3 experiments/multidirected_king.py 12 --crosstab 8           # ~4 s
```

## RED controls (the filter discriminates)

| control | what changed | n = 1…8 | verdict |
|---|---|---|---|
| **mdirbad** | Definition 2's condition 2 (keystone two-sided) dropped | 1, 4, 20, 110, 636, **3792**, 23082, 142596 | diverges at n=6, 3792 vs 3790 |
| **dir5nb** (control B) | sources = global bottom row instead of local minima of `b` | 1, 4, 20, **106**, 576, 3179, 17736, 99748 | diverges at n=4, 106 vs 110 |
| **dir5** | Bacher directed (one source, no keystone) | 1, 4, **19**, 96, 501, 2668, 14407, 78592 | strict subset, diverges at n=3 |

`mdirbad` is the sharp one: it isolates condition 2 alone, and it is a strict
superset (≥ termwise), so a wrong reading of the keystone rule could not have
passed unnoticed. The gate also checks `B(1/µ) = 0.999979 ≈ 1` — Theorem 10's
defining relation, evaluated on the computed `B` series — and that the ratio is
*not* drifting to `1/ρ_B`.

One latent bug fixed while wiring this in: the generation stamps in
`directed_cone_anchor.cpp` are `uint32_t` and were incremented without a wrap
guard. `mdir` burns one generation per keystone per animal on top of the flood,
so wrap is reachable in the low teens; `bump()` now zeroes the marker array on
wrap. The pre-existing `reach()` uses it too — same behaviour unless a run
wraps, which the n≤14 runs on record did not.

## What this changes in the record

- [directed-king-animals.md](directed-king-animals.md) said disjoint bottom runs
  joined higher up are "multi-directed". That is control B's predicate, not
  Bacher's; corrected there, with a pointer here.
- [directed-cone-anchor.md](directed-cone-anchor.md) was right that control B is
  a genuine third sequence, but justified its n=3 example by the same
  split-bottom-row reasoning; the reasoning is corrected, the conclusion stands.
- [middle-kingdom-grid.md](middle-kingdom-grid.md)'s `ctrlB` column is now
  permanent, not a placeholder: it is a distinct class, incomparable with
  multi-directed, and the multi-directed row is a fifth directedness value the
  16-cell grid does not have a slot for.

## Open

Both items below were closed by Phase 3 the same day
(`results/middle-kingdom-phase3.md`):

- ~~The `multi-directed × {column-convex, HV-convex, staircase}` cells of the
  Phase 3 grid are untouched~~ — the grid mode grew a fifth `mdir` row, and all
  three cells collapse onto the unfiltered row: **every column-convex king
  animal is multi-directed** (proved, and brute-forced to n=14). So they are
  A187077, the novel HV-convex-by-area series, and A225114.
- ~~Novelty against OEIS is **unchecked here**~~ — oeis.org's 403 was a
  User-Agent problem; `experiments/oeis_lookup.py` gets through. The answer
  corrects the record: multi-directed king animals are **A222205** ("Number of
  multi-directed animals with n vertices", Sloane 2013, citing this same Bacher
  paper), **not novel**. Our 200 terms match all 23 of the entry's exactly and
  extend it; the entry has no b-file, no growth constant and no formula beyond
  a pointer to Bacher's Theorem 9. `docs/middle-kingdom-plan.md`'s "NOVEL"
  label for this row is corrected there.
