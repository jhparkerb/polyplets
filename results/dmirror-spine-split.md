# The two dmirror spines, counted apart — and a second source for the whole strip table

2026-08-22, executing `docs/time-at-the-bar-report.md`'s A1.3 follow-up.
Probe `experiments/dmirror_spine_split.py`, run on ayr. Exact integer
arithmetic; anchored on every banked `dmirror_strip` cell.

## The answer

**An independent enumerator reproduces all 423 banked `dmirror_strip` cells
exactly, and it splits the count into the two ground-state families.**
`d = d_main + d_anti` holds with nothing left over for `S ≥ 2k+2` — and **fails
at `S = 2k+1`**, where the two families overlap rather than partition. The
decomposition is clean exactly above the onset, which is not a coincidence:
`results/dmirror-onset-sharp.md` measured that onset at `2k+2` (even) and
`2k+3` (odd) the same day, from entirely different reasoning.

**One family passes the test the sum fails; the other does not.** At `c_2` —
where the summed family measures degree 2 — **both** families are linear. At
`c_3`, which needs level `k = 3` pinned and therefore `S = 16` even and `S = 17`
odd, they separate, and the separation widens with every level the data reaches:

|  | c_1 | c_2 | c_3 | c_4 | c_5 | |
|---|---|---|---|---|---|---|
| `d_main`, both parities | deg 0 | deg 1 | **deg 1** | **deg 1** | **deg 1** | grand-form shape |
| `d_anti`, both parities | deg 1 | deg 1 | **deg 2** | — | — | **not linear** |

So the two-spine sum is **not** the whole obstruction. The main-diagonal family
looks like a single grand-form object as far as the data reaches — **four
nontrivial cumulants, `c_2` through `c_5`, all linear on both parities** —
while the anti-diagonal family fails at `c_3`, one level past where the summed
family fails.

`c_4` came out of the data already in hand, without another rung, once the
analysis stopped assuming that level `k` has degree `k`. It does not on this
family: `d_main` runs at `⌊k/2⌋`, so pinning it needs `⌊k/2⌋+2` points rather
than `k+2`, and the levels the old criterion called unreachable were already
determined. The pin now takes the **lowest** degree that fits and requires
**every** remaining point to be reproduced, not merely the consecutive ones
nearest the fitting window — strictly more data-efficient and strictly harder to
pass. Re-run under it, the `c_2` and `c_3` verdicts above are unchanged.

Both RED controls are green in the same run: planted single-family data reports
LINEAR, planted two-family data reports NONLINEAR. They are the same pair
`dmirror_grand_form.py` uses, so the two scripts cannot disagree silently.

**This corrects a verdict banked earlier the same day.** On `S ≤ 14` the same
script reported *both* families of grand-form shape, and that reading was one
level deep — `c_2` was the last cumulant those levels reached, and this file
said so. `c_3` reverses it for `d_anti`. What was measured then is unchanged;
what it was evidence for was less than it appeared.

**What the reversal rests on, checked before it was written down.** The flip
turns entirely on `S = 16` and `S = 17`, cells no other program in this tree had
produced. Their **totals** are second-sourced: summed over corner counts, all
21 cells at `S = 15..18` and `k ≤ 6` agree exactly with the banked
`dmirror_strip` rows from `cpp/sym/symtm.cpp`. The split of those totals into
the two families is not independently checked at `S ≥ 15`; it is checked at
every `S ≤ 14` against the Python enumerator, which agrees on every value.

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

Both tables list only the regime where the split is defined, `S ≥ 2k+2`, and
both are the C++ enumerator's output (`cpp/dmirror_spine.cpp`), which agrees
with the Python at every `S ≤ 14` value and whose totals agree with the banked
strip rows at every cell shown.

`d_main(S, S+k)`, from `S = 2k+2` up to `S = 19`:

| k | values |
|---|---|
| 0 | 1 at every S |
| 1 | 4 at every S |
| 2 | 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51 |
| 3 | 120, 129, 138, 147, 156, 165, 174, 183, 192, 201, 210, 219 |
| 4 | 704, 780, 860, 944, 1032, 1124, 1220, 1320, 1424, 1532 |
| 5 | 3564, 3943, 4342, 4761, 5200, 5659, 6138, 6637 |
| 6 | 20420, 22956, 25697, 28651, 31826, 35230 |

`d_anti(S, S+k)`, same range:

| k | values |
|---|---|
| 0 | 1 at every S |
| 1 | 10, 12, 12, 14, 14, 16, 16, 18, 18, 20, 20, 22 |
| 2 | 71, 77, 99, 105, 131, 137, 167, 173, 207, 213, 251, 257 |
| 3 | 314, 447, 512, 697, 774, 1019, 1108, 1421, 1522, 1911, 2024, 2497 |
| 4 | 2656, 3190, 4516, 5228, 7156, 8070, 10752, 11892, 15496, 16886 |
| 5 | 19094, 27895, 33412, 47197, 54922, 75487, 85920, 115429 |
| 6 | 167220, 206168, 298707, 357249, 503722, 588226 |

**The two families have different degrees, and only one of them knows about
parity.** Measured by `experiments/dmirror_spine_degrees.py`, which takes the
lowest degree that pins and then requires every remaining point to survive as a
holdout, on even `S`, odd `S`, and all `S` pooled:

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| `d_main`, either parity or pooled | 0 | 0 | 1 | 1 | 2 | 2 | 3 |
| `d_anti`, per parity | 0 | 1 | 2 | 3 | — | — | — |

`d_anti` behaves like a defect gas: degree `k`, one free position per defect.
`d_main` runs at **`⌊k/2⌋`**, now measured at **seven consecutive levels**,
`k = 0..6`, with the pooled fits carrying 2 to 11 holdouts.

**An earlier reading of this file said `d_main` has degree `k−1`.** That was
fitted on `S ≤ 11`, where `k ≤ 2` is all that pins and `k−1` and `⌊k/2⌋` agree.
`k = 3, 4, 5` separate them and it is `⌊k/2⌋`. The reading has now been used as
a prediction three times and held each time: `k = 3` and `k = 4` were predicted
before `S = 15` landed and hit 183 and 1124 exactly; `k = 5` was predicted at
degree 2 before `S = 16..18`; and `k = 6` was predicted at degree 3 before
`S = 19`. At `S = 19` itself the three pinned polynomials predicted 51, 219 and
1532 at `k = 2, 3, 4` and returned exactly those.

**And `d_main` has no parity dependence at all.** One polynomial in `S` covers
both classes at every pinned level; `d_anti`'s pooled column is unpinned from
`k = 1` on, so parity genuinely enters there. That is the mechanism
`results/dmirror-grand-form-fails.md` argued, now measured instead: reflection
in the main diagonal fixes every main-diagonal cell pointwise, while the
anti-diagonal has a centre cell only for odd `S`. **All of the dmirror family's
period-2 quasi-polynomiality comes from one of its two halves.**

## What it opens, and what it costs

A1.3's step 1 was declared dead on the summed family, and splitting the count
does not revive it. `d_anti` is not a single grand-form object either, so the
dmirror levels are **not** finitely determined by two constants per family, and
the four stranded OEIS sequences do not move by this route. What the split
bought is a sharper diagnosis than "the sum misbehaves":

- the obstruction is **not** the two-spine sum alone, which was the standing
  hypothesis until `c_3` landed;
- `d_main` — the family on the spine that is a king-connected path with every
  cell load-bearing — is grand-form-shaped as far as five levels reach, and is
  degree `⌊k/2⌋` with no parity dependence, which is a much more rigid object
  than the defect gas the anti-diagonal gives;
- so whatever breaks the grand form lives in the **anti-diagonal** family,
  whose cells are only diagonally adjacent and have slack. That is where anyone
  returning to this should look, and it is a statement about one specific
  family rather than about the symmetry class as a whole.

**The cost is no longer the obstacle, which is worth recording since it was.**
The Python enumerator took 6 h 38 min for `S = 14` alone and its own docstring
predicted minutes. `cpp/dmirror_spine.cpp` does `S = 14` in 19 s and reached
`S = 17` inside twenty minutes, by sweeping hooks with a cell budget: only
`n ≤ S + KMAX` is wanted, `n` never decreases, and the next hook's occupancies
are enumerated in increasing cell count and cut off at the remaining budget
rather than run over all `2^(S−k)` of them.

## The label field was too narrow at S >= 17, and it changed nothing

The guard added in `1a2ccac` fired 53 s into S = 20. Its reasoning — "the cell
budget keeps a hook far below" the field width — is wrong for a plain geometric
reason: hook 0 of an S x S board has 2S-1 cells, and a position `p >= 2`
contributes its two mirror cells `(k,k+p)` and `(k+p,k)` as SEPARATE components,
so an alternating occupancy reaches about S of them.

The field is six bits now (63 labels against the 48 cells a hook can hold), and
every run reports the largest hook it carried. **S = 12..19 was re-derived on
it.** The measurement:

| S | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|---|
| max components in one hook | 11 | 13 | 13 | 15 | 15 | **17** | **17** | **19** |
| four bits (16 labels) suffice | yes | yes | yes | yes | yes | **no** | **no** | **no** |
| table identical to the four-bit run | yes | yes | yes | yes | yes | **yes** | **yes** | **yes** |

So the four-bit binary really was aliasing at S = 17, 18 and 19 — the rows
`c_3`, `c_4` and `c_5` rest on — and every cell it produced is right anyway. The
reason is that aliasing can only merge two hooks carrying 17 or more components,
and no such hook completes into a connected animal inside `n <= S + 6`: it would
need more cells to join its pieces than the budget has. Aliasing merges two dead
ends into one dead end. It is also why the totals second-sourced clean against
the banked `dmirror_strip` rows at every cell.

**Nothing in this file changes.** The verdicts above stand as measured, now on a
field wide enough that the question cannot be asked again.

Note the guard was one step tighter than the field: it refuses at 16 components,
which four bits still hold, so the first value actually lost is the 17th. S = 20
was refused, not corrupted.

## What is still open

`c_4` on `d_main`, which needs `k = 4` pinned on both parities — six points
each, so `S = 18` even and `S = 19` odd. `d_main` is the only half still
consistent with a grand form, and one more level is what would either extend
that or close it the way `c_3` closed `d_anti`.

## Reproduce

    build/dmirror_spine --gate                             # 191 banked cells
    build/dmirror_spine 17 6                               # one length, minutes
    scripts/dmirror_spine_ladder.sh 15 18 6                # the ladder
    python3 experiments/dmirror_spine_cumulants.py LOG     # instant
    python3 experiments/dmirror_spine_degrees.py LOG       # instant

`experiments/dmirror_spine_split.py` is the original Python enumerator and is
kept as the second source, not as the way to run this.
