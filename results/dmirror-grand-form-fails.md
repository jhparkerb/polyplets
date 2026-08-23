# A1.3 step 1 does not go: the dmirror family is a two-spine sum, and the parity split does not separate it

2026-08-22, executing `docs/time-at-the-bar.md` A1.3 step 1 — the step the item
itself names as deciding whether the rest is worth attempting. Probe
`experiments/dmirror_grand_form.py`, three RED controls green, run on ayr.
Exact rational arithmetic; instant.

**Verdict: abandoned at step 1, as A1.3 instructed.** Steps 2 and 3 (below-onset
defect terms for the family, then the pinning) are not attempted and should not
be until the obstruction below is dealt with.

> **Superseded in one direction, later the same day.** "What would actually go"
> below nominates splitting the count by spine. That was done
> (`results/dmirror-spine-split.md`), and **each family separately is linear at
> `c_2`, on both parities** — the exact place the summed family measures degree
> 2. So what this file establishes is that the grand form does not transfer to
> the family **as summed**; it does not establish that the route is closed. The
> obstruction is the sum and nothing else has been found behind it. That rests
> on one nontrivial cumulant with one holdout per pin, and going deeper needs
> the split at larger `S` than pure Python reaches. Everything measured below
> stands as measured.

## The answer in one line

**Every cumulant past the first is nonlinear in S, on both parity classes.** The
grand form is the statement that they are all linear; it fails at `c_2` and gets
worse. So level k does not carry two new constants over the levels below, and
the four stranded OEIS sequences do not move by this route.

## The obstruction is not what A1.3 expected

A1.3 anticipated that if step 1 failed it would "die in a paragraph about why a
symmetry-restricted family is not row-local". Row-locality is not the problem,
and the real one is sharper and more tractable.

**The dmirror diagonal has two ground states.** `d(S, S) = 2` for every S ≥ 2 —
measured, in `results/sym_counts.txt` — because both the main diagonal and the
anti-diagonal are king-connected and both are fixed *as sets* by reflection in
the main diagonal. For fixed k and large S an animal cannot be within k defects
of both spines, since the two disagree in about 2S cells, so

    d(S, S+k) = d_main(S, S+k) + d_anti(S, S+k)      (disjoint, S large)

and the grand form is a statement about a **single** exponential:
`T(H+k,H) = [y^k](C(y)·μ(y)^H)`, equivalently every cumulant exactly linear in
the size parameter. The log of a sum of two exponentials is not linear unless
the two are proportional.

This is not new to the tree — `results/dmirror-diagonals.md` already recorded
"the cumulants are messy — expected, since they are the log of a SUM of
families". What is new is that the natural repair has now been tested and does
not work.

**Two corrections from `results/dmirror-spine-split.md`, which counted the two
families apart later the same day.** The threshold above is one step optimistic:
the families partition `d` exactly for `S ≥ 2k+2`, and at `S = 2k+1` they
*overlap* rather than partition. Nothing here depends on it — the pinning happens
above the onset, which is `2k+2`. And the two families turn out to have
*different degrees*, `k−1` for `d_main` against `k` for `d_anti`, which is a
sharper reason the sum has no single-exponential form than "two families with
different growth".

## Where the parity comes from, and why the repair was worth trying

Reflection in the main diagonal fixes every main-diagonal cell pointwise, but
*reverses* the anti-diagonal: `(i, S−1−i) → (S−1−i, i)`, which is fixed only
when `S` is odd. So the anti-spine has a centre cell exactly for odd S and none
for even S. That is the period-2 quasi-polynomiality, and it is the same
mechanism `results/bilateral-parity.md` found in A030234 the same day: one
family present at every size, a second whose structure switches on with parity.

If the parity split already separated the two families' contributions, then each
parity class on its own would be a single-family object and would have the grand
form. **It does not.**

## The measurement

For each parity class, form `A^p_S(y) = Σ_k P^p_k(S) y^k` from the pinned
quasi-polynomials and take `log` in ℚ[[y]] with coefficients polynomial in S.

| | c_1 | c_2 | c_3 | c_4 | c_5 |
|---|---|---|---|---|---|
| even S, degree in S | **1** | 2 | 2 | 4 | 4 |
| odd S, degree in S | **1** | 2 | 2 | 4 | 4 |

Linear at `j = 1` and nowhere after. The two classes agree exactly, which is
itself informative — whatever is breaking linearity is not a parity artefact.

**The degree pattern is a signature, not noise.** `deg(c_j) = 2⌊j/2⌋` for j ≥ 2
is what a sum of exactly two exponential families produces: the first
nonlinearity enters at second order and the degrees step in pairs. A sum of
three would step differently. So the measurement is consistent with the
two-spine reading and inconsistent with the family being irreducibly messy.

Controls, all green and all necessary:

- **(a)** planted single-family data, read off an exact `C(y)·μ(y)^S`, is
  reported linear — so "linear" is being measured and not merely printed;
- **(b)** planted two-family data with `μ_A ≠ μ_B` is reported nonlinear — so
  the test can fail, which is the half that makes the real answer mean anything;
- **(c)** the pinned `P^p_k` reproduce the banked leading coefficients `1/k!`,
  the same anchor `results/dmirror-onset-sharp.md` uses.

## What this costs A3.3

`results/dmirror-onset-sharp.md` showed T4 cannot be tested at k = 6 because
pinning a degree-6 polynomial needs 7 points and the odd class has 6. A grand
form would have reduced level 6 to **two** new constants, needing 2 points
against the 7 and 6 available, and T4 would have got its first new test since
2026-07-31 with 5 and 4 holdouts. That route is closed too.

**With the split, the arithmetic changes and the input does not exist.** Four
constants per level — two per family — still fits inside 7 even and 6 odd
points with holdouts to spare, so the counting is not what blocks it. What
blocks it is that those points would have to be `d_main` and `d_anti` at
`S ≈ 14..17`, and the banked table carries only their sum. See
`results/dmirror-spine-split.md`.

## What would actually go

Split the count. If `d_main` and `d_anti` were enumerated separately rather than
summed, each is a single-spine defect gas and the grand-form question becomes
askable of each in isolation — and the degree pattern above says there are
exactly two pieces to find. That is a change to the dmirror enumerator (label
each animal by which spine it is within k defects of, which is well defined for
S > 2k), not a derivation, and it is the only step here that is cheap in
thought and merely fiddly in code.

Two things to note before anyone starts. The split is only clean for `S > 2k`,
which is above the onset and therefore exactly where the pinning happens, so
that is not a real restriction. And `d_main + d_anti = d` is a free
fail-closed check on the split at every banked cell — 423 of them.

## What stays true

Nothing in `results/dmirror-diagonals.md` is contradicted. Its quasi-polynomial
structure, its degree-k-per-parity finding, its onset, and the T4 reduction all
stand; `results/dmirror-onset-sharp.md` sharpened the onset the same day. What
is settled here is only that the king lattice's grand form does not transfer,
and why.

## Reproduce

    python3 experiments/dmirror_grand_form.py

Instant, ayr or dalby. Input: `results/sym_counts.txt` via
`experiments/dmirror_onset_probe.py`'s pinning.
