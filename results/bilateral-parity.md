# A030234's parity effect is two families, and here is the second one

2026-08-22, executing `docs/time-at-the-bar.md` A3.2. Probe:
`experiments/bilateral_parity.py`, four RED controls green, run on ayr. Exact
integer arithmetic on banked b-files; no compute budget.

## The answer in one line

**The bilateral count is `b(n) = T(n) + [n even]·B(n)`, and both parity classes
are perfectly log-convex on their own.** The failure `results/open-conjectures.md`
C2 records is not the sequence misbehaving; it is a second family switched on at
every second index, and the interleaving of two well-behaved sequences.

## The mechanism

A bilaterally symmetric animal has a mirror axis, and on the square grid an axis
is of exactly one of two kinds:

- **through-cell** — the axis runs along a column. Cells on it are fixed by the
  reflection, everything else is paired, so `n = (axis cells) + 2·(pairs)` and
  `n` may be odd or even. At least one axis cell is forced: with none, the two
  halves sit two columns apart and are not king-adjacent, so the animal would be
  disconnected.
- **between-cell** — the axis runs between two columns. No cell is fixed, every
  cell is in a 2-cycle, so **`n` is necessarily even**. The halves do connect:
  `(0, j)` and `(1, j)` are edge-adjacent across the axis.

Odd `n` is served by one family, even `n` by two. Nothing else in the companion
set has this: `A006770`, `A030222`, `A030233` and `A030235` count objects with
no such forced parity.

## The test, and what it had to be able to fail

If the effect were noise rather than an additive family, restricting to one
parity would not help. So the test is log-convexity **within each parity class**,
`a(n)² < a(n−2)·a(n+2)`, in exact integers.

| sequence | terms | interleaved | same-parity |
|---|---|---|---|
| A006770 fixed | n = 1..40 | clean | clean |
| A030222 free | n = 1..32 | 1 violation, at n = 4 | clean |
| A030233 one-sided | n = 1..34 | 1 violation, at n = 4 | clean |
| **A030234 bilateral** | n = 1..32 | **15 violations, n = 2, 4, …, 30** | **clean** |
| A030235 asymmetric | n = 1..32 | 2 violations, n = 4 and 6 | 1, at n = 5 |

Fifteen violations at n = 2, 4, …, 30 is *every even index the data can test* —
n = 32 needs n + 1 = 33 and the series stops at 32. That confirms C2's "fails at
every even n" exactly rather than correcting it.

And the same-parity column is the finding: **zero violations**, on the one
sequence that fails hardest interleaved.

Controls: a pure geometric is correctly flagged at the strict-convexity boundary;
a single log-convex family `λⁿ/n` is clean both ways; and a planted sequence of
exactly the conjectured shape — one family plus a second switched on at even n —
reproduces the signature, failing interleaved and clean on both parity classes.
The first version of that control used `λⁿ·n²`, which is log-*concave*, and it
failed; the control caught the script before the script was used on the data.

## Separating the two families, without a fit

Write `ρ = B/T`. Since `b(odd) = T` and `b(even) = T + B`, with `T(n) ~ C·μⁿ·n^θ`
the two consecutive ratios are

    g(even) = b(even)/b(odd)  ~  μ·(1 + ρ)
    g(odd)  = b(odd)/b(even)  ~  μ/(1 + ρ)

so their **product** recovers `μ` with `ρ` cancelling and their **quotient**
recovers `(1 + ρ)²` with `μ` cancelling. Neither needs a fit or an extrapolation.

| n | 8 | 12 | 16 | 20 | 24 | 28 | 30 |
|---|---|---|---|---|---|---|---|
| μ | 2.48661 | 2.53641 | 2.56358 | 2.58083 | 2.59284 | 2.60172 | 2.60535 |
| ρ = B/T | 0.05604 | 0.04928 | 0.04541 | 0.04277 | 0.04078 | 0.03923 | 0.03856 |

**Two things this buys.**

`μ` climbs monotonically to 2.60535 at n = 30, heading for
`√λ_king = √7.1102 = 2.66650` — which is what it must approach if a mirror-
symmetric animal is determined by half of itself. That is a consistency check on
the whole bilateral series against an independently measured constant, and it
passes. It is also a second route to the observation that the ratios have not
converged at n = 32: 2.605 against 2.667 is 2.3% short.

`ρ` is small and decreasing: the between-cell family is about one part in 26 of
the through-cell family at n = 30 and falling. **Whether it decreases to a
positive limit or to zero is not determined by 32 terms** — the decrements are
themselves shrinking by about 9% a step, which extrapolates to a limit near 0.03
if that ratio holds and to zero if it does not, and nothing here distinguishes
those. Stated rather than fitted.

## What this does not do

It does not prove log-convexity of either parity class — that is C2's own status
for the parent sequence, and this adds a fourth and fifth sequence with the same
evidential standing rather than proving anything. It does not separate `T` and
`B` as counts: `results/sym_counts.txt` carries `hmirror` as a single total, and
splitting it by axis kind is engine work, not arithmetic. The `ρ` above is a
ratio inferred from the interleaving, not a measured `B(n)`.

The obvious next step, if anyone wants it, is exactly that split — a symmetric
counter that reports through-cell and between-cell axes separately would turn
every estimate here into a measurement, and would say directly whether `B/T` has
a positive limit.

## One incidental finding

`A030235` (asymmetric) is the only companion with a **same-parity** violation, at
n = 5. C2 describes the companions as "log-convex past small n" and n = 5 is
small, so this is consistent with what is written; it is recorded because the
same-parity test had not been run on any of them before and this is its only
non-clean cell outside A030234.

## Reproduce

    python3 experiments/bilateral_parity.py

Instant, ayr or dalby. Inputs: the five `results/b0*_upload.txt` files, banked
and gated by `make gate-bfiles`.
