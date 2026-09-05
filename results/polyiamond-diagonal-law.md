# Polyiamonds: the diagonal law with a row unit of two

2026-08-06, revised 2026-09-05. Diagonals measured by
`experiments/polyiamond_diagonal.py` (~7 min); the theorem's hypotheses checked
by `experiments/polyiamond_fibre_check.py` (~20 s).

Polyiamonds are animals of equilateral triangles: cell `(x, y)` is an up- or
down-triangle by the parity of `x + y`, adjacency is `(x ± 1, y)` always and
`(x, y + 1)` **iff `x + y` is odd**. The up-neighbour set therefore depends on
position and there is no single drift set `D`, so condition (U) of
`docs/proofs/universal-diagonal-law.md` fails. Condition (M) of that document
holds instead, with the **rhombus** — a receiver glued to a horizontally
adjacent sender — as the row unit: `m = 2`, `b = 2`, and the rhombus walk is
the polyhex walk in the coordinate `j = ⌊(x − y)/2⌋`. **Theorem A applies**, and
its conclusion is a plain polynomial rather than the quasi-polynomial of
period 2 that the parity dependence suggests.

## The structure

The minimum cell count at height `H` is `n = 2H − 2`, not `H`: a cell that
receives from below has even `x + y` parity, so it cannot itself send upward.
Every row except the first and the last therefore needs **two** cells, the
first needs one, and the cheapest ladder costs `1 + 2(H − 2) + 1 = 2H − 2`.

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

Theorem A guarantees validity from `H ≥ k + 1`. The **measured onsets are
⌊k/2⌋ + 2**, checked at every k above, so later diagonals become valid
*earlier* than the theorem promises — which fits the cost structure: each row
of a polyiamond ladder buys two cells rather than one.

## The gas laws hold, with W = 2

Normalize by `q_0 = 1/4` so that `p_0 = 1`. Then:

- **leading coefficients** are `W^k / k!` with **W = 2**: `lead(p_k)·k!` comes
  out 2, 4, 8, 16 for k = 1..4, exactly `2^k`;
- **cumulants are linear in H**, `c_k = [u^k] log Σ p_k u^k`:
  `c_1 = 2H`, `c_2 = 11H/4 − 13/4`, `c_3 = 5H/3`, `c_4 = 149H/32 − 429/32`.

That is the defect gas of `docs/proofs/universal-diagonal-law.md` §The gas,
made lattice-parametric — extensive cumulants, an ideal gas of defects with the
interactions in the constants. `W = 2` is in `H`; the pair-row weight has not
been counted as a gadget the way the row-local ones were.

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
