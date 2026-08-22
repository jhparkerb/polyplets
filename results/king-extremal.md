# Extremal king-animal statistics: three trivial, one open

2026-08-22, executing `docs/last-orders.md` C3.3 —
`results/unexplored-avenues.md` idea 7's remaining bullets, after the
minimum-site-perimeter one it closed. Probe:
`experiments/king_extremal.py`, four RED controls green. Exhaustive over all
fixed king animals to n = 9 (940,982 at the top row).

## The measurements

| n | animals | min diam | max diam | max artic | max holes |
|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 0 | 0 |
| 2 | 4 | 1 | 1 | 0 | 0 |
| 3 | 20 | 1 | 2 | 1 | 0 |
| 4 | 110 | 1 | 3 | 2 | 1 |
| 5 | 638 | 2 | 4 | 3 | 1 |
| 6 | 3,832 | 2 | 5 | 4 | 2 |
| 7 | 23,592 | 2 | 6 | 5 | 2 |
| 8 | 147,941 | 2 | 7 | 6 | 3 |
| 9 | 940,982 | 2 | 8 | 7 | 4 |

Diameter is the king graph's longest shortest path; articulation points are cut
vertices; holes are bounded 4-components of the complement, which is the
matching convention `results/matching-pair-convention.md` pinned.

## Three of the four are trivial, and saying so is the result

- **max diameter = n − 1** and **max articulation points = n − 2**, both
  realised by the straight line, both obvious once stated. Nothing to pursue.
- **min diameter = ⌈√n⌉ − 1**, realised by packing into the smallest enclosing
  square. Matches every measured term. Elementary; an OEIS search on
  `0,1,1,1,2,2,2,2,2` returns A000196 (integer part of √n) and unrelated
  sequences, i.e. no king-animal entry, which is what a folklore quantity with
  a one-line derivation looks like.

Idea 7 asked for these by name and the answer is that they were worth ten
minutes to close rather than to plan around. "diameter" appearing nowhere in
the repo was an absence of the word, not of a question worth asking.

## The one that is not trivial

**Max hole count: 0, 0, 0, 1, 1, 2, 2, 3, 4.**

No OEIS collision on those nine terms. It is not `⌊n/2⌋ − 1` — that predicts 3
at n = 9 and the true value is 4 — so it has no obvious closed form from this
data, and its increments (0,0,1,0,1,0,1,1) do not settle into a pattern within
reach.

Two things make it more interesting than the other three:

- **it is a king-lattice-specific quantity.** Four cells can already enclose a
  hole — a diamond at `(0,0),(1,1),(2,0),(1,−1)` is king-connected through its
  diagonals and 4-surrounds the empty centre. On the square lattice the first
  hole needs eight cells. That is exactly the point-contact subtlety
  `unexplored-avenues.md` idea 10 flags as "worth more than the tiling
  questions themselves";
- it is the counterpart of `M(n)`, max single-hole *area*, which
  `docs/proofs/`-adjacent work turned into a theorem. The count, rather than the
  area, has never been asked.

**Honest size of the prize:** nine terms, a maximum over a census that stops at
n = 9, and no conjecture. This is a candidate for the guess-and-prove treatment
that produced the maxhole theorem, not a result. `results/min-site-perimeter.md`
is the cautionary precedent — that bullet's search half finished and the
guess-and-prove half died because the closed form was already published.
**Grep OEIS and the polyomino literature before anything here is called new.**

## RED controls

- animal counts reproduce **A006770** to n = 9;
- a 6-cell line has diameter 5 and 4 articulation points;
- a 3×3 block has neither articulation points nor holes;
- the 8-cell ring has exactly one hole.

## Cost of going further

n = 10 is 6.05M animals and roughly seven times n = 9's work; the per-animal
reduction is a BFS plus an articulation scan, so this is minutes, not hours,
and it is a laptop-scale job that this repo would run on ayr anyway. Four more
terms of the hole-count sequence would be the cheapest way to decide whether it
has a closed form worth chasing. **Not run** — it shortens no sentence in any
manuscript, and idea 7's own verdict was that it "extends the paper's existing
extremal result rather than starting a new topic".

## Reproduce

    python3 experiments/king_extremal.py --nmax 9

About four minutes. `--nmax 10` is the next rung.
