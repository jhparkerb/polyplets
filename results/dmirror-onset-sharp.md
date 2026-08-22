# T4 at k = 6 is out of reach, and the onset is why — measured, not assumed

2026-08-22, executing `docs/time-at-the-bar.md` A3.3. Probe:
`experiments/dmirror_onset_probe.py`, control green, run on ayr. Exact rational
arithmetic on the 423 tracked `dmirror_strip` rows of `results/sym_counts.txt`;
instant.

## The answer in one line

**The onset is sharp and it splits by parity: `S ≥ 2k+2` on the even class and
`S ≥ 2k+3` on the odd one, on every level that can be pinned.** There are no
spare points below it to be recovered, so T4 cannot be tested at k = 6 on banked
data, and the two points it needs are `S = 27, 29` at k = 6 — dmirror strips at
n = 33 and n = 35, which is the same `D(n)` wall as A1.3.

## Why this was worth an afternoon

T4 is `N_k(±1) = (±2)^k` for the diagonal-mirror numerators, and its 2026-07-31
reduction (`results/dmirror-diagonals.md`) is the useful part:

    N_k(1)  = 2^k      ⟺  lead(P^even_k) = lead(P^odd_k) = S^k / k!
    N_k(−1) = (−2)^k   ⟺  lead(P^even_k − P^odd_k) = (−1)^k / (k−1)!

**Testing T4 at a new level therefore needs only the two quasi-polynomials, not
the numerator `N_6`.** That is a much lower bar than reconstructing the rational
generating function, and it is why A3.3 called T4 "the most provable-looking open
statement in the tree".

The blocker was believed to be the onset. `dmirror-diagonals.md` measures it at
`S ≥ 2k+2`, which at k = 6 means `S ≥ 14`, leaving seven even points and six odd
ones — degree 6 needs seven points to pin, so the even class pins with **zero**
holdout and the odd class does not pin at all. But `S ≥ 2k+2` is a *measured*
bound, the smallest S from which the pinned polynomial happened to reproduce
every exact value. If the true onset were lower, k = 6 would gain points at both
parities and the test would become possible. That is the question this settles.

## Method

Per level and parity: take the longest gap-free run of S values in steps of 2
from the deep end; detect the degree by finite differences requiring three equal
tail values; pin a Lagrange polynomial on the deepest `k+1` points; then walk
**backward** and record the smallest S at which the polynomial still reproduces
the exact banked value. Everything is `Fraction`, so "reproduces" is bit-exact.

## The result

| k | even onset | 2k+2 | odd onset | 2k+3 | even holdouts | odd holdouts |
|---|---|---|---|---|---|---|
| 0 | 2 | 2 | 3 | 3 | 15 | 14 |
| 1 | 4 | 4 | 5 | 5 | 12 | 12 |
| 2 | 6 | 6 | 7 | 7 | 10 | 9 |
| 3 | 8 | 8 | 9 | 9 | 7 | 7 |
| 4 | 10 | 10 | 11 | 11 | 5 | 4 |
| 5 | 12 | 12 | 13 | 13 | 2 | 2 |

**Six levels, twelve cells, no exceptions.** The polynomial reproduces every
value down to the stated onset and fails at the point below it. The union
statement `S ≥ 2k+2` in `dmirror-diagonals.md` is correct and this is the
per-parity refinement of it: the odd class starts exactly one step later, which
is the half that decides k = 6.

Control: the pinned polynomials reproduce all five banked leading coefficients
exactly — `lead = 1/k!` on both parities and `lead(P^even − P^odd) =
(−1)^k/(k−1)!` giving −1, 1, −1/2, 1/6, −1/24 at k = 1..5. That is an
independent re-derivation of the numbers T4 was reduced to, from the tracked
fallback table rather than from the gitignored run directories the original used.

The control earned its place: the first version of this probe hand-expanded the
Newton form and got every degree above 0 wrong, reporting leading coefficients of
−27, 675/2 and −4025/2 where the banked values are 1, 1/2 and 1/6. The control
caught it before any verdict was drawn.

## What k = 6 needs

| parity | onset | banked points above it | needed |
|---|---|---|---|
| even | 14 | 7 | 8 (7 to pin, 1 to check) |
| odd | 15 | 6 | 8 |

The even class is short by one and the odd by two. The missing values are
`d(27, 33)` and `d(29, 35)` — dmirror strips at n = 33 and n = 35. The dmirror
count is capped at n = 32 (`results/b030234_upload.txt` header: "Reach is capped
at n=32 by the diagonal-mirror count"), and extending it is the λ^(n/2) blocker
that `results/related-seqs-n33.md` runs into and that `docs/time-at-the-bar.md`
A1.3 is entirely about.

**So A3.3 and A1.3 have the same bottleneck.** That is the finding worth
carrying forward: they are not two independent items, and anything that buys
`D(n)` past 32 buys a k = 6 test of T4 for free.

## What is closed and what is not

**Closed:** the hope that k = 6 was reachable by being less conservative about
the onset. It was not conservatism; the onset is sharp.

**Not closed:** T4 itself, which stands verified exactly at k = 1..5 and untested
at k = 6. Nothing here is evidence for or against it.

**Also not closed, and cheaper than it looks:** at k = 6 the degree cannot even
be *confirmed* from banked data — with seven points and an expected degree of 6,
the sixth difference has one value and no flatness test can run. The probe
reports "differences never flatten" rather than assuming the degree it expects,
which is the right refusal, but it means the quasi-polynomial structure itself is
unverified at k = 6 as well as its coefficients.

## Reproduce

    python3 experiments/dmirror_onset_probe.py

Instant, ayr or dalby. Input: `results/sym_counts.txt`, the tracked fallback the
gitignored `runs/sym*/` directories would otherwise be needed for.
