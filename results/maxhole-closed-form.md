# The maximum hole count is `n − ⌈2√n⌉ + 1`, and the sequence is already in OEIS

2026-08-22, executing `docs/time-at-the-bar.md` A3.1. Extra term measured on
ayr with `experiments/king_extremal.py --nmax 10`, four RED controls green,
16 minutes and 8.8 GB.

## The answer in one line

**`maxholes(n) = n − ⌈2√n⌉ + 1`**, matching all ten measured terms, with a
construction that proves the `≥` direction outright. The sequence is
**A248333**, which `results/king-extremal.md` did not find because nine terms of
`0, 0, 0, 1, 1, 2, 2, 3, 4` are too short and too generic to hit.

## The measured terms

`results/king-extremal.md` had n ≤ 9. The tenth was cheap and is now banked:

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| max holes | 0 | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 4 | **4** |
| `n − ⌈2√n⌉ + 1` | 0 | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 4 | 4 |

The n = 10 run also re-derived `a(10) = 6,053,180` against A006770 and
`min diameter = 3 = ⌈√10⌉ − 1`, so the two closed forms that file already had
gained a term as well.

## The construction, which is a proof of the lower bound

Take the **even-parity sublattice**: all cells `(i, j)` with `i + j` even.

- **It is king-connected.** `(i, j)` and `(i+1, j+1)` are diagonal neighbours,
  so any two even-parity cells are joined by a diagonal walk. It is a square
  lattice in its own right, rotated 45° with spacing √2.
- **Every enclosed odd cell is a hole.** Take an odd-parity cell `v`. Its four
  *orthogonal* neighbours are all even-parity, hence occupied. A hole is a
  bounded 4-component of the complement (the convention
  `results/matching-pair-convention.md` pins), and `{v}` is a 4-component on its
  own the moment its four edge-neighbours are filled. Its diagonal neighbours are
  irrelevant — they are odd cells too, and 4-connectivity does not see them.

So an `a × b` block of the rotated sublattice uses `n = ab` cells and encloses
exactly `(a−1)(b−1)` odd cells — one at the centre of each unit square of the
rotated lattice. **This is the whole of the "four king cells enclose a hole where
the square lattice needs eight" observation, made quantitative.**

Maximising the number of complete unit squares over `n` sites of a grid — not
just rectangular blocks — is the classical quantity `n − ⌈2√n⌉ + 1`, and the
best shape is a quasi-square grown by gnomons, which is exactly how A248333 is
defined ("moving along each square gnomon starting on the y-axis and ending on
the x-axis"). Its terms, offset by one to match, are

    0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11, 12, 12, ...

and the formula reproduces them.

## What is proved and what is not

**Proved: `maxholes(n) ≥ n − ⌈2√n⌉ + 1`.** The construction above is explicit,
the connectivity is immediate, and the holes are singletons whose surrounding is
checked one cell at a time.

**Not proved: the reverse inequality.** Nothing here rules out a cleverer animal
— one mixing both parities, or using holes larger than a single cell — that beats
the sublattice construction. The evidence is that it agrees with exhaustive
enumeration for every n ≤ 10, which is all ten terms that exist.

That gap is the interesting part and it is not obviously hard. It is the same
shape as the argument in `results/maxhole-proof.md`, the theorem this project
already produced by exactly this route — measure at small n, guess the closed
form, prove it. This is the second instance of that shape and it is stalled one
step from the end.

### Reducing the upper bound to one lemma

The statement wanted is: for every king-connected `A` with `|A| = n`, the number
of bounded 4-components of the complement is at most `n − ⌈2√n⌉ + 1`.

**On a single parity class it is the classical count.** If `A` lies inside one
parity class, `A` is a subset of the rotated square lattice, and every complete
unit square of that lattice encloses exactly one odd cell whose four orthogonal
neighbours are all occupied — an isolated 4-component. So on such sets the hole
count is at least the number of complete unit squares, and the maximum of *that*
over `n` sites is exactly `n − ⌈2√n⌉ + 1`.

**What is missing is a parity-compression lemma**, and it is worth stating
sharply because it is the whole remaining gap:

> **Conjecture (compression).** For every king-connected `A` there is a
> single-parity king-connected `A'` with `|A'| ≤ |A|` and at least as many
> bounded 4-components in its complement.

Given that, the bound follows from the classical count. Two honest cautions
before anyone starts on it.

The single-parity direction proved above is a **lower** bound on holes even
within that class: an even-parity set with gaps can have unoccupied even cells
that join odd cells into one large 4-component, so "holes = complete unit
squares" needs the set to be solid in the rotated lattice, and the general
single-parity statement is itself not quite closed.

And the compression conjecture is exactly the kind of statement that is either a
short shifting argument or false, with nothing in between. The cheapest thing
that would inform it is a search for a mixed-parity animal that beats every
single-parity animal of the same size — which the exhaustive runs to n = 11
would already have found if one existed that small.

## n = 11: the prediction was tested and it held

**Run 2026-08-23 on ayr at jasonp's direction. Predicted 5, measured 5.**

`n − ⌈2√n⌉ + 1` at n = 11 is `11 − 7 + 1 = 5`, and the exhaustive sweep over
all 39,299,408 eleven-cell polyplets returns a maximum hole count of exactly 5.
This is the first term the formula did not see: the ten it was found from end at
n = 10, and n = 11 is where its increment pattern stops being forced.

The sequence is now `0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5` for n = 1..11, matching
\oeis{A248333} at every term.

**An external check came free.** The run re-derives the animal counts as it
goes, and its eleventh is `a(11) = 39,299,408`, which is A006770's value
exactly. The probe's own control table stops at n = 10, so this is a term
checked against OEIS rather than against the file's own reference — and the
control now says which it did: "reproduce A006770 to n=10 (computed to n=11; no
reference past n=10)".

**Cost, measured against the prediction.** The header predicted ~2 h and
~55 GB. Measured: **4.28 h and 62.7 GB** on ayr, single core — 2.1× the
predicted wall and 1.14× the predicted memory. The wall prediction came from a
6.4×-per-term ratio off n = 8 and n = 10; the real ratio to n = 11 is about 16×,
so **the per-term ratio is not flat** and n = 12 is worse than the ~11 h that
same model gives.

## What extending further would cost

n = 12 is not worth it by this route, and the reason is now measured rather
than modelled. It is also the wrong tool: a targeted search for high-hole
animals would settle far more terms for far less, since the extremal question
does not need the other 250 million animals.

## Corrections to `results/king-extremal.md`

That file says of the max hole count: "No OEIS collision on those nine terms…
so it has no obvious closed form from this data, and its increments
(0,0,1,0,1,0,1,1) do not settle into a pattern within reach." Both halves were
true of what was in front of it and both are now superseded — the collision is
A248333 and the closed form is `n − ⌈2√n⌉ + 1`. What was missing was not more
terms but the construction, which turns the question into a known one.

It also says `⌊n/2⌋ − 1` fails because it predicts 3 at n = 9 where the truth is
4. That stays correct and is what ruled out the obvious guess.

## Reproduce

    python3 experiments/king_extremal.py --nmax 10      # ayr, 16 min, 8.8 GB

Formula check, any machine, instant:

    n - ceil(2*sqrt(n)) + 1
