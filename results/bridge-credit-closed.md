# Bridge credit: the band-decomposition route to a lambda upper bound is closed

2026-08-07. Kills idea 3 of `results/unexplored-avenues.md`, which was written
down explicitly as "MOST LIKELY WRONG ... a sketch to be killed", with an
evening budgeted to do it. It took a 90-line probe
(`experiments/band_charge_probe.py`) and it died faster and at a different
place than the plan expected.

**Verdict: unsound, not merely unproved.** The encoding is not injective, so it
is not an over-count and nothing downstream of it is a bound. The quantity it
silently omits is exactly `c(H)`, the vertical-join multiplicity that
`docs/open-problem-lambda-bracket.md` names as the crux of candidate (1) — the
scheme presupposes `c(H) = 1` rather than bounding it, and `c(H) = 1` implies a
false statement.

## The sketch, as written

1. Cut an animal into horizontal bands of height `H`. Encode each band as its
   left-to-right sequence of component SHAPES plus the GAP LENGTHS between
   them. Shapes cost `mu_H^cells`.
2. A gap of length `g` in band `i` exists only because those components connect
   through band `i +/- 1`, which needs `>= g` cells bridging it there. A cell
   can be charged by at most two gaps (one above, one below), so
   `sum(gaps) <= 2n` and gap entropy is `~4^n` — constant per cell, not
   `n^Theta(n)`.
3. Credit: a bridging run of `g` cells has ONE shape, but `mu_H^g` was paid for
   it in step 1. Since `mu_13 = 6.306 > 4`, the credit beats the cost.

The plan named **step 2** as the load-bearing claim, "asserted, not proved",
and named the fastest kill as: write the charging map for a two-band example
with nested bridges and see whether a cell can be charged more than twice.

## What the probe found

Brute force over all 147941 fixed king animals at n=8, `H = 1..5`.

**Step 1 is not injective, and not marginally so.**

|  H | distinct codes | animals | collisions | worst class |
|---|---|---|---|---|
| 1 | 5597 | 147941 | 142344 | 2187 |
| 2 | 34798 | 147941 | 113143 | 45 |
| 3 | 61018 | 147941 | 86923 | 15 |
| 4 | 87663 | 147941 | 60278 | 8 |
| 5 | 117456 | 147941 | 30485 | 6 |

At `H = 1` the code identifies 96% of all animals with some other animal, and
one code class holds 2187 of them. **The first collision is at n = 2:**

```
#.        .#        #
.#        #.        #
```

All three 2-cell animals present as "two bands, each one component of shape
`single cell`, no gaps". An encoding that cannot separate the three 2-cell
animals is not an over-count of anything.

**Step 2 — the claim the plan flagged — holds everywhere measured.**

|  H | max sum(gaps) | 2n | holds? |
|---|---|---|---|
| 1 | 12 | 16 | yes |
| 2 | 6 | 16 | yes |
| 3 | 6 | 16 | yes |
| 4 | 5 | 16 | yes |
| 5 | 3 | 16 | yes |

No cell is charged more than twice anywhere in the census, and there is a
structural reason it cannot be: a cell lies in exactly one band and therefore
has exactly two adjacent bands, and within a single adjacent band two distinct
gaps must be crossed at distinct column ranges. **The plan aimed at the wrong
step.** Step 2 is fine. The sketch dies one step earlier and much more cheaply.

## Where the missing entropy is

The code records each band's shapes and internal gaps and nothing about **how
consecutive bands are aligned horizontally**. Two animals with identical band
shapes and identical (empty) gap lists differ by sliding one band sideways —
which is the n=2 counterexample, and every one of the 142344 collisions at
`H = 1`.

Repairing it means encoding the band-to-band horizontal offset. That offset is
precisely the **vertical-join multiplicity `c(H)`** of
`docs/open-problem-lambda-bracket.md` candidate (1), whose bound was the entire
point of the exercise. So the sketch does not bound `c(H)`; it assumes it away.

## Why it is unsound rather than incomplete

Run the sketch's own accounting on the animals it handles best — those with no
gaps in any band, where the gap entropy is 1 and no credit is claimed. It
reads:

```
a(n) <= mu_H^n      ==>      lambda <= mu_H
```

At `H = 17` that is `lambda <= 6.543`. But `mu_17 = 6.543` is a **certified
lower** bound (`results/strip-mu-certificates.md`), and `mu_H < lambda`
strictly for every finite `H` because height-`<= H` animals are a proper
subclass — the ladder is still climbing at `mu_13 = 6.306 -> mu_17 = 6.543`
against an estimate of 7.110(1). So the accounting yields `lambda <= mu_17 <
lambda`.

A scheme whose own arithmetic contradicts a certified bound is not waiting on a
proof of step 2. It is wrong.

## One more defect, in the regime that matters

Step 1 says "left-to-right sequence of components", which presumes the
components of a band are ordered along `x`. For `H >= 3` they need not be: put
one component in the band's top row and another in its bottom row, two rows
apart so they are not king-adjacent, with overlapping column ranges. Then "the
gap between consecutive components" is negative, and undefined as a length.

Measured at n=8: **308** such x-overlapping adjacent pairs at `H = 3`, **750**
at `H = 4`, **332** at `H = 5`, and **zero** at `H = 1, 2`. The gate the sketch
had to pass needs `c(17)`, so `H = 17` is the only regime that counts, and
step 1 is not even well-formed there.

## What this leaves

- The bracket is unchanged: `6.543 <= lambda <= 9.3154`.
- Candidate (1) of `docs/open-problem-lambda-bracket.md` is **not** refuted —
  the vertical-join question is still open and still the most promising of the
  four. What is refuted is this particular way of trying to avoid it. The
  bracket doc's own read ("the join multiplicity may itself be non-local")
  survives intact; this probe adds that any scheme which does not price the
  join is not merely weak but unsound.
- Connectivity wall, fourth disguise — after the P3 slack audit
  (`docs/proofs/polyplet-upper-bound.md`), the comb shatter
  (`results/concatenation-upper-bound.md`), and the algorithmic levers. Each
  time the over-count that must be controlled is the non-local one, and each
  time a bounded local code cannot pay for it.
- **Sentence that gets shorter: none.** Under the standing claim-pruning
  filter this was only ever worth an evening as a door to close, and it is now
  closed. It cost under an hour.

## Artifacts

- `experiments/band_charge_probe.py` — the probe; `python3 ... 8` reproduces
  every table above in ~40 s.
