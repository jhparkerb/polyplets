# Comb Shatter — the concatenation route to a lambda upper bound is closed

2026-08-01. Follow-up on the one item `papers/MISSING.md` flagged as worth a look
after the 2026-08-01 lattice-animal paper haul: Barequet–Ben-Shachar–Osegueda,
"Concatenation arguments and their applications to polyominoes and polycubes,"
Comput. Geom. 98 (2021) 101790 (`papers/barequet_benshachar_osegueda_2021_concatenation_arguments.pdf`).

The super-multiplicative (lower-bound) half of that paper is banked and
superseded — Fekete gives `lambda >= a(40)^(1/40) = 6.2208`, the certified strip
ladder gives 6.543 (`results/strip-mu-certificates.md`). The open half is
**quasi sub-multiplicativity, which yields UPPER bounds**, and our upper end
(9.3153, `docs/proofs/polyplet-upper-bound.md`) is the loose side of the bracket.

**Verdict: the route cannot be pushed for the full king class.** The prize is
real and was worth pricing — but the missing lemma is a known-hard target whose
proof would improve the polyomino record too. Arithmetic and the shattering
witness: `experiments/concatenation_bound_check.py`.

## The prize, priced exactly

BBO Theorem 1(a): if `Z(2n) <= c1 n^c2 Z(n)^2` for all `n`, then
`mu <= (c1 (2n)^c2 Z(n))^(1/n)` for **every** `n` — one known term suffices.
With `a(40)` banked, write `F = c1 (2n)^c2` for the slack factor at `n = 40`:

| F at n=40 | consequence |
|---|---|
| `F < 7.54` | relation is **refuted** — the bound would fall below our certified `lambda >= 6.543` |
| `F < 210.5` | refuted modulo `lambda ~ 7.111` (numeric only) |
| `F < 1.03e7` | **beats** the 9.3153 certificate |

So the live window is `7.5 <= F <= 1.03e7`, i.e. **the lemma helps iff `deg P <= 3`**:

| deg P | F | bound on lambda | |
|---|---|---|---|
| 0 | 1.0 | 6.2212 | REFUTED (below the certified 6.543) |
| 1 | 80.2 | 6.9414 | refuted numerically |
| 2 | 6413 | **7.7451** | useful — this is BBO's convex shape |
| 3 | 5.13e5 | **8.6418** | useful |
| 4 | 4.10e7 | 9.6423 | no gain |

BBO's convex-polyomino P is degree 2 (`mn + 2(m+n) + 1`, their Theorem 8), so the
honest target value is **7.745** — a genuine improvement on 9.3153, still far
above `lambda ~ 7.111`, and it decays slowly with more terms (estimated 7.49 at
n=80, 7.29 at n=200 — the `(2n)^2` factor only dies like `exp(2 ln(2n)/n)`).

## Nothing in 40 terms refutes it

The ratio the lemma must dominate, measured on banked data:

| m+n | argmax | `a(m+n)/(a(m)a(n))` | `mn/(C(m+n))` predicted by `a(n) ~ C lambda^n / n` |
|---|---|---|---|
| 10 | (5,5) | 14.87 | 13.16 |
| 20 | (10,10) | 27.99 | 26.31 |
| 30 | (15,15) | 41.00 | 39.47 |
| 40 | (20,20) | 53.95 | 52.63 |

Linear in `m+n`, matching the `theta = -1` asymptotic form to ~2%. A degree-2 `P`
is consistent with every term we hold. The relation is *believed*; it is the
*proof* that is missing — and it is missing for the same reason it is missing for
ordinary polyominoes.

## Why the proof does not port (the comb)

BBO's Theorem 8 splits a convex polyomino at lexicographic rank `m` (order by `x`
then `y`). Convexity bounds the debris: each side is at most two components, the
second necessarily a vertical stick, so the reassembly code is `O(mn)` — degree 2.

For king animals the same split shatters. Take a comb: spine at `x = 0`, teeth to
the right on every third row (two rows apart is the minimum that keeps teeth
king-independent). Measured, over all split ranks:

| k | cells | worst #components |
|---|---|---|
| 2 | 10 | 3 |
| 8 | 34 | 9 |
| 16 | 66 | 17 |

`k+1 ~ n/4` pieces, each needing its own vertical offset to be restored:
`n^Theta(n)` codes, super-exponential — not a `P(x)` at all, let alone degree 3.
Nothing about king adjacency softens this; the diagonal contacts only widen the
tooth spacing from 1 row to 2.

The other split that *does* keep both sides connected — cut a canonical spanning
tree at a centroid edge — cannot prescribe the two sizes to within `O(1)`, which
is exactly what Theorem 1(a)/(b) require (1(b) allows only a **constant** index
shift `c3`). Approximate splits deliver only the convolution form
`a(n) <= K n^2 sum_m a(m) a(n-m)`, which any sequence with `a(n) ~ C lambda^n / n`
satisfies outright: it carries no information about `lambda`.

This is the connectivity wall again, in a third disguise — after the
Certificate-Squeeze P3 slack audit (`docs/proofs/polyplet-upper-bound.md`) and
the algorithmic levers (`MEMORY.md`, [[algorithmic-levers-dead-connectivity-wall]]).
The over-count that must be controlled is diffuse and non-local, so a bounded
local code cannot pay for it.

## The transfer argument (why this is hard, not merely undone)

The identical lemma for ordinary polyominoes, at degree 2, would give

```
lambda_poly <= (1.002 * 112^2 * A(56))^(1/56) = 4.3828
```

from `A(56)^(1/56) = 3.7031` (BBO sec. 2.1) — beating the best known upper bound
**4.5252** (Barequet–Shalah 2016, `C_21` twig hierarchy, the descendant of
Klarner–Rivest 1973) by 0.142, with no computation beyond already-published
terms. A one-page lemma that beats a fifty-year-old line by pure arithmetic does
not sit unclaimed. BBO themselves write that the scheme "is also suited for
obtaining upper bounds" and then apply the upper direction only to convex
polyominoes — the class where the split is bounded.

## What is left of the thread

- The upper bound stays at **9.3153** (exact-rational Bui-style convolution
  certificate). Bracket unchanged: `6.543 <= lambda <= 9.3153`.
- The only live remnant: BBO's split *does* port to **convex polyplets** (the
  parked side quest, `results/convex-polyplets.md`), which would bracket
  `lambda_convex-king`. That bounds a subclass constant, shortens no sentence in
  the paper, and is not worth the evening under the standing filter.
- `papers/MISSING.md` updated: the "[the one worth a look]" flag is spent.
