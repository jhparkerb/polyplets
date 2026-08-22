# Cell sparsity in characteristic 0: extreme, structured, and it still loses

2026-08-22. The measurement `docs/skeletonkey-reprompt.md`,
`docs/resume-here.md` and `docs/README.md` have all been promising since
2026-08-20, banked at last. Executes `docs/last-orders.md` A1.5, and answers
C2.4 in the same pass.

Data: `results/skeletonkey/cellsparse.txt`, produced by
`experiments/skeletonkey/cell_sparsity_modp.py` on ayr, H = 4..8, primes
131071 and 65521. The H = 8 row took 2 h 47 min and ~7 GB against its own
header's prediction of "5-15 min and ~2 GB" — the prediction was wrong and is
recorded here as wrong.

## Why it was run

`git show second-source:results/scaling-exploration-A.md` (A-S1) rejected the
rank-compressed engine on compute growth — "crossover: never" — **assuming the
compressed transfer is dense**, and named sparsity as the one unprobed rescue.
`results/exactchange-probes.md` had measured that sparsity in GF(2) only. This
is the characteristic-0 measurement.

## The numbers

| H | cell states | column states | d_p | d_p/col | d_p ratio | col ratio | A₀ row wt | dense d/2 | sparser by |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 300 | 20 | 32 | 1.60 | — | — | 1.06 | 16.0 | 15× |
| 5 | 1,550 | 50 | 99 | 1.98 | 3.094 | 2.500 | 1.24 | 49.5 | 40× |
| 6 | 7,938 | 126 | 249 | 1.98 | 2.515 | 2.520 | 1.39 | 124.5 | 90× |
| 7 | 40,894 | 322 | 692 | 2.15 | 2.779 | 2.556 | 1.77 | 346.0 | 195× |
| 8 | 212,670 | 834 | 1,826 | 2.19 | 2.639 | 2.590 | 2.15 | 913.0 | 425× |

`d_p` is the compressed dimension in characteristic 0; `col` is the incumbent's
column frontier, which is `Motzkin(H+1) − 1` exactly at every row here. A₀ is
the mean nonzeros per row of the compressed transfer.

**Gates in the file itself:** the char-2 cell rank reproduces the banked value
at H = 4, 5, 6, 7 (32, 93, 210, 516), and a RED control confirms that perturbed
successor maps give ranks [373, 362, 374], none of them 93.

## Two readings, and they point opposite ways

**The sparsity rescue is real, and it is not small.** A₀ is 2.15 nonzeros per
row at H = 8 against a dense `d_p/2 = 913` — **425× sparser**, and the factor
is growing 15 → 40 → 90 → 195 → 425. A-S1's density assumption was wrong by
more than two orders of magnitude, exactly as it suspected it might be.

**The engine still loses, for a different reason than A-S1 gave.** The
compressed dimension is *already larger* than the object it would replace, at
every height measured — 1.60× at H = 4 rising to 2.19× at H = 8 — and it grows
faster: **2.748×/height against the column frontier's 2.541×**. There is no
crossover to wait for. Extrapolating the ratio's own 1.082×/height gives
**~6× worse at H = 21**, which is worse than the ~2× the provisional H ≤ 7
reading projected.

So **"crossover: never" survives, and the H = 8 point does not break the
trend** — the geometric growth over the full range, 2.748×, sits inside the
2.78× the H ≤ 7 rows predicted. What changes is the reason: the compressed
engine is not beaten by density, it is beaten by dimension, and it was behind
from H = 4 rather than catching up.

## C2.4: what this says about the basis question

`docs/skeletonkey-reprompt.md` calls an explicit char-2 basis "the single
largest open technical question in the mission", and C2.4 asked whether the
char-0 sparsity pattern shows structure a basis could be read off.

**It does, and that is the least useful place it could have shown up.** The
file records row weights in two bases at once. At H = 8:

    generator basis      A0 = 65.01,  A1 = 113.03
    compressed basis     A0 =  2.15,  A1 =   2.68

A factor of 30. A sparse basis therefore **exists** in characteristic 0 and the
compression procedure finds it; at 2.15 nonzeros per row on a dimension-1826
operator the compressed transfer is essentially a permutation with a small
correction, which is as structured as an operator gets. The A₀ weights grow
about +0.27 per height (1.06, 1.24, 1.39, 1.77, 2.15) while the dimension grows
2.75× per height — the structure is not an artifact of small H.

But an explicit description of that basis **would not rescue anything**,
because density is not what is killing the char-0 engine — dimension is, and
writing the basis down does not change `d_p`. The two questions separate
cleanly:

- **characteristic 0**: sparse basis demonstrably exists, would buy nothing,
  because `d_p` exceeds the incumbent and grows faster;
- **characteristic 2**: `d_2` is the quantity that actually *collapses*
  (1,155 against 1,826 at H = 8, and ~1e6 against 9.4e8 at H = 21 per INV-6),
  and there the basis is unknown and would buy the collapse.

**So the basis hunt should be motivated by the char-2 collapse and never by
char-0 sparsity.** A session that sees "2.15 nonzeros per row, therefore
structure, therefore look for the basis" is looking in the field where finding
it changes nothing. That redirection is what C2.4 bought.

## Reading the file

Its `cellstates` column is a **presentation** size, not a live-state count: it
is exactly `colstates × (2^H − 1)` at every height (300/20 = 15, 1550/50 = 31,
7938/126 = 63, 40894/322 = 127, 212670/834 = 255). Do not divide by it to get a
speedup ratio. That error was made once during the session that produced the
data and corrected there.

## Honest limits

- Five heights, and the extrapolation to H = 21 runs thirteen rungs out from
  the last one. The ratio `d_p/col` is decelerating (1.24, 1.00, 1.09, 1.02 per
  rung), so 6× is an upper-ish reading and 3× is defensible from the last three
  rungs alone. Both are above 1, which is the only part the conclusion needs.
- Two primes, both around 2¹⁷ and 2¹⁶. `d_p` is a rank over `F_p` used as a
  proxy for the characteristic-0 rank; the two primes agree, which is evidence
  and not proof that neither is unlucky.
- "Essentially a permutation with a small correction" is a description of the
  row weights, not an examination of the matrix. Nobody has looked at the
  compressed basis vectors themselves.

## Artifacts

- `results/skeletonkey/cellsparse.txt` — the run's own output, gates included.
- `experiments/skeletonkey/cell_sparsity_modp.py` — the probe.
- `results/skeletonkey-four-mechanisms.md` §3 reads the H = 8 row through the
  published `results/exactchange-probes.md` figures rather than on its own; with
  this file banked it can be read directly.
