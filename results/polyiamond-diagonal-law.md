# Polyiamonds: the diagonal law survives outside the row-local class

2026-08-06. Measured, not proved. Verifier:
`experiments/polyiamond_diagonal.py` (~7 min).

Polyiamonds are animals of equilateral triangles: cell `(x, y)` is an up- or
down-triangle by the parity of `x + y`, adjacency is `(x ± 1, y)` always and
`(x, y + 1)` **iff `x + y` is odd**. The up-neighbour set therefore depends on
position, there is no single drift set `D`, and condition (U) of
`docs/proofs/universal-diagonal-law.md` fails. **Theorem A does not apply.**
The question was whether its conclusion does anyway, and if so in what form —
the natural guess being a quasi-polynomial of period 2.

**It is not quasi-polynomial. The diagonals are plain polynomials.**

## The structure

The minimum cell count at height `H` is `n = 2H − 2`, not `H`. Reason, and it
is a proof rather than an observation: a cell that receives from below has even
`x + y` parity, so it cannot itself send upward. Every row except the first and
the last therefore needs **two** cells, the first needs one, and the cheapest
ladder costs `1 + 2(H − 2) + 1 = 2H − 2`.

Index the diagonals by cells above that minimum, `n = 2H − 2 + k`. Then
`T(2H − 2 + k, H) / 2^H` is a polynomial of degree exactly `k` in `H`:

| k | onset | T(2H−2+k, H) / 2^H | holdouts |
|---|---|---|---|
| 0 | H ≥ 2 | 1/4 | 12 |
| 1 | H ≥ 2 | H/2 | 11 |
| 2 | H ≥ 3 | H²/2 + 11H/16 − 13/16 | 9 |
| 3 | H ≥ 3 | H³/3 + 11H²/8 − 29H/24 | 8 |
| 4 | H ≥ 4 | H⁴/6 + 11H³/8 + 59H²/384 − 137H/128 − 65/32 | 6 |

The k = 0 and k = 1 rows are `2^(H−2)` and `H·2^(H−1)`, which
`experiments/universal_law_check.py` has probed since July; the rest are new.

**Onsets go as ⌊k/2⌋ + 2**, checked at every k above, against `k + 1` for the
row-local lattices. Later diagonals become valid *earlier*, relative to k, which
fits the cost structure: each row of a polyiamond ladder buys two cells rather
than one.

## The gas laws hold, with W = 2

Normalize by `q_0 = 1/4` so that `p_0 = 1`. Then:

- **leading coefficients** are `W^k / k!` with **W = 2**: `lead(p_k)·k!` comes
  out 2, 4, 8, 16 for k = 1..4, exactly `2^k`;
- **cumulants are linear in H**, `c_k = [u^k] log Σ p_k u^k`:
  `c_1 = 2H`, `c_2 = 11H/4 − 13/4`, `c_3 = 5H/3`, `c_4 = 149H/32 − 429/32`.

That is the defect gas of `docs/proofs/universal-diagonal-law.md` §The gas,
made lattice-parametric — extensive cumulants, an ideal gas of defects with the
interactions in the constants — on a lattice the theorem does not reach. So
**condition (U) is sufficient for the law, not necessary**, and the parity
dependence washes out of the counts entirely rather than surviving as a period.

## What would make it a theorem

Theorem A's proof uses a single drift set in the separation step and in the
chain identity. The polyiamond case needs a period-2 version of both — a
two-row transfer whose composite is translation-invariant. Nothing in the
evidence suggests an obstruction, and the composite of two parity steps *is*
uniform, which is presumably why the answer comes out polynomial rather than
quasi-polynomial. Not attempted.

## Method, and a bug worth recording

Counts come from a surplus-budgeted row transfer DP parametric in the parity
rule, cost depending on k and H rather than on the number of polyiamonds.
Validated against brute-force enumeration for every `(n, H)` with `H ≤ 8`, and
the window checked stable at 6 against 8.

The first version budgeted by the *current* height's allowance, `2H − 2 + k`.
That is wrong: the allowance grows by 2 per row while a row can cost 1, so a
wide early row was pruned even though later rows pay it back. It silently
undercounted the top diagonal — 376 → 262 at `(n, H) = (8, 3)` — and only the
brute-force check caught it. The right budget is surplus over the *per-row*
minimum, `s = used − (2h − 1)`, which is non-decreasing while the animal
continues. Same bug class as the window clipping recorded in
`experiments/defect_gas.py`: a bound that looks conservative but is not.
