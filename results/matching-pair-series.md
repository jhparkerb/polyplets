# Sykes–Essam verified to order p⁹ — and the defect data is the wrong end

2026-08-22, executing `docs/last-orders.md` C1.2. Desk work, brute force at
small n, no compute job. Probe: `experiments/matching_pair_series.py`, four
RED controls green.

## Two answers

**The relation holds.** For the king/rook matching pair, in the convention
`results/matching-pair-convention.md` pinned,

    K_8(p) − K_4(1−p) = p − 4p² + 4p³ − p⁴

is verified **exactly, in rational arithmetic, at every order through p⁹** —
the four predicted coefficients 1, −4, 4, −1, and then exact zero at orders
5, 6, 7, 8, 9. This is the first time anything in the repo has tested it.

**The proposed combination is dead.** C1.2 asked whether the perimeter-defect
campaign's square-lattice series supply the perimeter-graded enumeration that
idea 2 needs. They do not, and the reason is not cost — it is that the defect
grading covers the **opposite end of the perimeter range** from the one the
relation reads.

## Why the combination fails, in one table

The defect grading is `k = pmax(n) − p`, so a banked series at `k ≤ 6` holds the
six **largest** perimeters at each size. The relation's rook side contributes at
order `p^{t_4}`, so an order-N test needs every rook animal with `t_4 ≤ N` — the
**smallest** perimeters. Measured over every fixed polyomino to n = 11:

| n | min t₄ | max t₄ | what `k ≤ 6` reaches |
|---|---|---|---|
| 5 | 8 | 12 | t ≥ 6 |
| 7 | 10 | 16 | t ≥ 10 |
| 9 | 11 | 20 | t ≥ 14 |
| 11 | 12 | 24 | t ≥ 18 |

The two windows are disjoint from n = 8 onward and diverge linearly: max t₄
grows like 2n while min t₄ grows like `3.67·√n` (measured over n = 4..11). The
defect data is a band of fixed width at the top of a window whose width grows
without bound, and the relation reads the bottom.

This is the accounting test from `docs/skeletonkey-reprompt.md` applied to a
combination rather than to a counting route, and it cost one enumeration to
n = 11.

## What a deeper test would actually cost

Inverting the measured `min t₄ ≈ 3.67·√n`:

| order | needs every rook animal with t₄ ≤ | i.e. sizes to about |
|---|---|---|
| p¹⁰ | 10 | n = 7 |
| p¹⁶ | 16 | n = 19 |
| p²⁰ | 20 | n = 29 |
| p³⁰ | 30 | n = 66 |

Quadratic in the order. The king side is linear — order N needs n ≤ N — so the
rook side is the binding constraint and gets worse the further the test is
pushed. Reaching order p²⁰ means every polyomino to n ≈ 29 with its site
perimeter, which is not an enumeration this repo has or can cheaply get; the
frontier for *counting* polyominoes is n = 70 and for enumerating them
individually it is far lower.

## The truncation signature, which is why the p⁹ result is trustworthy

The first failing order is p¹⁰, and the residual there is

    K_8 − K_4(1−p) at p^10  =  −6053180  =  −A006770(10)

exactly the missing king term. A truncation failure looks like the omitted
data and nothing else; had the convention or the inhomogeneous term been wrong,
the residual at p¹⁰ would have been some other number, and orders 5–9 would not
have been exactly zero.

## RED controls

- the enumerator reproduces **A001168 to n = 11** and **A006770 to n = 9**,
  so the animals being weighed are the right animals;
- a single cell has king perimeter 8 and rook perimeter 4;
- **the cross-lattice convention fails.** Pairing king connectivity with rook
  perimeter — the reading `matching-pair-convention.md` corrected — does not
  reproduce 1, −4, 4, −1. Without this control the test could not tell a right
  convention from a wrong one, and would have "confirmed" either.

## What this changes in the idea-2 assessment

`results/unexplored-avenues.md` idea 2 says the identity "is NOT a cheap check
on a(40) unless the perimeter refinement is pushed to n=40, which is expensive"
and that no sentence gets shorter. Both stand. What is added:

- the relation is now **checked** rather than cited, to order p⁹, in exact
  arithmetic, with a control that would catch a convention error;
- the cost of pushing it is now **measured and quadratic**, not
  back-of-envelope;
- the one route that looked like it might make the rook side cheap — the
  banked perimeter-defect series — is excluded on a structural mismatch rather
  than on cost, which is a stronger kill and one that no amount of extra
  compute would lift.

**Sentence that gets shorter: still none.** The cross-family validation channel
idea 2 hoped for would need the rook side at order ≳ 20 to constrain anything
the repo cares about, and that is n ≈ 29 of perimeter-graded polyominoes.

## Reproduce

    python3 experiments/matching_pair_series.py --nmax-rook 11 --nmax-king 9

About three minutes on a laptop; the default `--nmax-rook 12` costs more and
buys one order. The enumerator is naive growth plus canonical dedup on purpose
— it is a control, and `cpp/g2_redelmeier.cpp` is the real one.
