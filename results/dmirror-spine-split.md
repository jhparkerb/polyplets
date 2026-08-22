# The two dmirror spines, counted apart — and a second source for the whole strip table

2026-08-22, executing `docs/time-at-the-bar-report.md`'s A1.3 follow-up.
Probe `experiments/dmirror_spine_split.py`, run on ayr. Exact integer
arithmetic; anchored on every banked `dmirror_strip` cell.

## The answer so far

**An independent enumerator reproduces all 423 banked `dmirror_strip` cells
exactly, and it splits the count into the two ground-state families.**
`d = d_main + d_anti` holds with nothing left over for `S ≥ 2k+2` — and **fails
at `S = 2k+1`**, where the two families overlap rather than partition. The
decomposition is clean exactly above the onset, which is not a coincidence:
`results/dmirror-onset-sharp.md` measured that onset at `2k+2` (even) and
`2k+3` (odd) the same day, from entirely different reasoning.

The cumulant test — whether *each* family separately has the grand form
`results/dmirror-grand-form-fails.md` showed the sum does not — needs `S = 13`
and is running. `c_2` is the discriminator and it is one level out of reach at
`S ≤ 12`; the analysis (`experiments/dmirror_spine_cumulants.py`) refuses to
decide rather than fitting what it has.

## Why the split is cheap

Sweep by **hooks**: hook `k` is the cells with `min(i,j) = k`, i.e. the corner
`(k,k)` plus the mirror pairs `{(k,k+p), (k+p,k)}`. Then **the main diagonal is
exactly the set of hook corners**, so counting by `(n, #occupied corners)`
separates the spines with no geometry beyond what the sweep already tracks:

- a main-spine animal at level `k` is within `k` defects of the full diagonal,
  so it has `≥ S−k` occupied corners;
- an anti-spine animal's cells `(i, S−1−i)` are *arm* cells at offset
  `p = S−1−2i`, never corners — except the centre when `S` is odd, which is the
  corner of hook `(S−1)/2`. So it has `≤ k+1` corners.

## The anchor, and the bug it caught

The enumerator shares no code with `cpp/sym/symtm.cpp`, which produced the
banked rows. Summing the histogram over corner counts must reproduce them cell
for cell, and it does — **423 cells, zero mismatches**. That makes this a second
source for the entire dmirror strip table, which the tree did not have.

It earned its place immediately. The first version collapsed each mirror pair
`{(k,k+p), (k+p,k)}` to a single graph node. They are one *position* — symmetry
forces them occupied together — but two *cells*, and they are not adjacent to
each other unless `p = 1`. Collapsing them counted disconnected animals as
connected, and the anchor caught it at the fourth row: `S = 4, k = 0` gave 5
where the banked value is 2. Adjacency is now computed from the coordinates by
brute force rather than from hand-derived rules.

## Exhaustiveness, which the diagnosis had assumed

`results/dmirror-grand-form-fails.md` asserts `d = d_main + d_anti` for large
`S`. That is a claim about exhaustiveness and it had never been checked. The
corner-count histogram checks it directly, and it holds — with a fencepost the
diagnosis got wrong:

| regime | result |
|---|---|
| `S ≥ 2k+2` | `d_main + d_anti = d` exactly, every cell measured |
| `S = 2k+1` | the two ranges **overlap**: 5 cells, e.g. `(S,k) = (9,4)` and `(11,5)` |
| `S ≤ 2k` | not defined; the corner-count ranges cross |

So the disjointness threshold is `S ≥ 2k+2`, not `S > 2k` as
`dmirror-grand-form-fails.md` states. That file's conclusion is unaffected —
the pinning happens above the onset, which is `2k+2` — but the sentence is one
step optimistic and is corrected here.

## The two families

`d_main(S, S+k)`:

| k | S = 2..14 |
|---|---|
| 0 | 1 at every S |
| 1 | 4 at every S |
| 2 | 25, 27, 29, 31, 33, 35 (S = 6..11) |
| 3 | 120, 129, 138, 147 (S = 8..11) |
| 4 | 704, 780 (S = 10, 11) |

`d_anti(S, S+k)`:

| k | S = 2..14 |
|---|---|
| 0 | 1 at every S |
| 1 | 6, 8, 8, 10, 10, 12, 12, 14 (S = 4..11) |
| 2 | 47, 53, 71, 77, 99, 105 (S = 6..11) |
| 3 | 314, 447, 512, 697 (S = 8..11) |
| 4 | 2656, 3190 (S = 10, 11) |

**The two families have different degrees, and that is the first real structural
finding here.** Pinning each with a holdout gives

    d_main   degree 0, 0, 1  at k = 0, 1, 2
    d_anti   degree 0, 1, 2  at k = 0, 1, 2

so `d_anti` behaves like a defect gas — degree `k`, one free position per defect
— and `d_main` is **degenerate by one**, degree `k−1`. The main diagonal is
king-connected as a path with every cell load-bearing, so a defect there is far
more constrained than a defect on the anti-diagonal, whose cells are only
diagonally adjacent and have slack. `d_main(k=1) = 4` at every `S` is the
clearest case: one corner removed and one arm pair added, and only four ways to
do it however long the spine.

That degree gap is also why the sum misbehaves. Two families of *different*
degree cannot combine into anything with a single-exponential form, which is a
sharper statement than "two families with different growth".

## What is still open

The cumulant test. `c_2` needs `k ≤ 2` pinned on both parities of both
families, which needs `S = 13` for the odd class. Running. `c_3` would need
`S = 17`, which is out of reach of this pure-Python sweep — the state space is
exponential and `S = 13` is already minutes.

If both families come back linear, the dmirror levels are finitely determined
after all, with four new constants per level rather than two, and A1.3's step 1
failed only because the two were summed. If either does not, the two-spine
reading is not the whole obstruction and `dmirror-grand-form-fails.md`'s
diagnosis is incomplete.

## Reproduce

    python3 experiments/dmirror_spine_split.py 12          # ayr, minutes
    python3 experiments/dmirror_spine_cumulants.py LOG     # instant
