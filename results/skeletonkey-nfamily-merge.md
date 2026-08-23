# The strip automaton is not state-minimal, and the merge is not a mod-2 fact

2026-08-20, branch `skeletonkey`. Probe
`experiments/skeletonkey/nfamily_merge.py`, run on ayr, exact integer
arithmetic throughout, gated on the banked `C_H` rows.

Two files in this tree, filed one day apart, disagree without either noticing
the other.

`results/r4/r4-floors.md` (2026-08-13) audits the project's claimed floors and
says the honest general form of the state floor is that *the M(H+1)-1
reachable column states are pairwise Nerode-distinguishable* — that the
incumbent's automaton is state-minimal. It marks that NOT ESTABLISHED,
records that a grep for `Nerode|distinguishab|minimal automaton|state-minimal`
returns no hit in a state-count context, and calls it "the cheapest missing
brick in the whole floor structure … nobody appears to have asked."

`results/exactchange-probes.md` §6 (2026-08-14) asks and answers it. Two strip
states are equivalent iff they carry the same multiset of block neighbourhoods
`N(b) = rows(b)` expanded `±1` and clipped to `[0,H)`; the class counts are
measured exact at H = 4..11. But Exact Change was a characteristic-2 campaign
throughout, so §6 states the result as **GF(2)**-Nerode equivalence and §10
prices the campaign at "one bit … roughly 55x on a computation that is already
cheap."

The argument §6 gives never mentions a field. The transition reads nothing
about a block except `N(b)` — a new cell at row `r` attaches to `b` iff
`r ∈ N(b)`, and `b` strands iff the new column's mask misses `N(b)` — so it is
a statement about the language, hence a congruence over any semiring. **This
file settles that it is: the merge is a plain state-space cut for exact
counting, and it collapses exactly the set that is the modern engine's wall.**

## The measurement

Nine heights, re-derived here from scratch — the probe imports neither Exact
Change's code nor any production code, and reads banked data only as a target.

| H | raw states | merged | ratio | raw growth | merged growth |
|---|---|---|---|---|---|
| 4 | 20 | 8 | 2.500 | — | — |
| 5 | 50 | 19 | 2.632 | 2.500 | 2.375 |
| 6 | 126 | 43 | 2.930 | 2.520 | 2.263 |
| 7 | 322 | 101 | 3.188 | 2.556 | 2.349 |
| 8 | 834 | 239 | 3.490 | 2.590 | 2.366 |
| 9 | 2,187 | 575 | 3.803 | 2.622 | 2.406 |
| 10 | 5,797 | 1,399 | 4.144 | 2.651 | 2.433 |
| 11 | 15,510 | 3,441 | 4.507 | 2.676 | 2.460 |
| 12 | 41,834 | 8,539 | 4.899 | 2.697 | 2.482 |

Raw is `Motzkin(H+1) − 1`, checked. The merged column reproduces Exact
Change's own numbers at every height it measured, including the 8,539 its
`minauto` run banked at H = 12 — two implementations sharing no code.

## Gates

All fail-closed, all green.

- **A** — reachable state count equals `Motzkin(H+1) − 1`, H = 2..8.
- **B** — the raw automaton reproduces the banked `C_H(n)` rows exactly,
  every `n ≤ 12`. These are `cutcount_b1`'s rows, produced by the cancellation
  DP, so this is a cross-rule check and not a self-comparison.
- **C** — the congruence itself: `succ_key(key(s), m) == key(succ(s, m))` for
  **every** reachable state against **every** column mask. Exhaustive, not
  sampled.
- **D** — the a-priori key automaton, built by BFS on keys with no partition
  state ever materialized, reproduces the same `C_H(n)`.
- **E** — class counts equal `exactchange-probes.md` §6's independently
  computed `N(H)`.
- **F** — the automaton built with the production engine's touched-top and
  touched-bottom flags emits `T(n,H)` directly, and it equals the
  `C_H − 2C_{H−1} + C_{H−2}` telescope over the banked rows, every `n ≤ 12`.
  Two different mechanisms for exact height, same integers.
- **G** — on the rook lattice `N(b) = rows(b)`, so the key is the state and
  the counts must be equal. They are, at every height: 3 = 3, 8 = 8, 20 = 20,
  50 = 50, 126 = 126, 322 = 322, 834 = 834.
- **H** — no row is covered by more than two neighbourhoods, so the key fits
  the signature width the engine already has.
- **RED** — dropping the `±1` expansion gives `5, 9, 24, 67, 195` where king
  gives `5, 17, 72, 332, 1582`.

A bug worth recording, because it fails silently in the direction of a
too-conservative answer: the N-sets were first sorted as `frozenset`s, and
`sorted` over frozensets sorts by the **subset partial order**, not a total
one — two states carrying the same multiset presented in different orders can
canonicalize differently and split one class in two. Bitmasks now. It changed
no gate (the counts already agreed with Exact Change) but it would have
inflated the class counts silently at some larger height.

## What the exact-height flags cost

The merge is flagless. The touched-top / touched-bottom flags block merges
between frontiers that differ only in whether a boundary row was ever
occupied, so an engine that gets exact height from flags keeps some of the
redundancy. Measured:

| H | flagged raw | flagged merged | flagless raw | flagless merged | today ÷ best |
|---|---|---|---|---|---|
| 4 | 39 | 21 | 20 | 8 | 4.88 |
| 5 | 98 | 48 | 50 | 19 | 5.16 |
| 6 | 246 | 108 | 126 | 43 | 5.72 |
| 7 | 624 | 248 | 322 | 101 | 6.18 |
| 8 | 1,604 | 580 | 834 | 239 | 6.71 |

"Flagged raw" is what `core/kink_column.h` produces today. The flags are a
flat ~1.92× that does not compound (flagged raw grows 2.57×/height against
flagless raw's 2.59×), and they blunt the merge — 2.77× flagged against 3.49×
flagless at H = 8.

The way out is the telescope of gate F, which `cutcount_b1 --assemble` and
`undertow_pin.read_tri_motley` already use, and which costs no extra runs
because the ladder computes every height anyway. Taking both, the end-of-column
frontier is **6.71× smaller at H = 8** than what the engine carries now.

The vertical mirror fold composes rather than overlapping: 239 keys fold to
128 orbits at H = 8, so the ~1.9× the engine already takes from `foldSig`
survives the merge.

## Why the collapse exists at all, and why it is king-only

On the rook lattice `N(b) = rows(b)`, so the key **is** the state and nothing
merges. The compression is a fact about king adjacency blurring rows: a
component occupying row 1 alone and a component occupying rows 0 and 1 both
reach `{0,1,2}`, and no later column can tell them apart. That is why it does
not appear in the polyomino literature this project reads.

## What it collapses

`results/kink-carry.md`: after the kink-carry redesign "intermediate stages
live in RAM (3.6× frontier); **only end-of-column states leave a worker**", and
"the new wall = frontier RAM at `D_H ~ 2.6^H`". The merged set is exactly that
end-of-column set, and it grows at ~2.48^H against the raw 2.70^H.

For scale, `results/ns_a40/PROVENANCE.md` records the a(40) run's H = 21
frontier peaking at 355,390,806 records and disk at 363.4 GB.

## What adoption costs

`core/kink_column.h:97`. `kinkFinalizeColumn` canonicalizes the end-of-column
key with `canonicalizeSig` and then sorts and dedups. Replacing that one call
with a reach-canonicalization makes the existing dedup do the merging. The
stage kernel in `core/kink.h` does not change, because `N(b)` is precisely
what it already reads.

The key fits the signature width the engine already has: a row `r` is in
`N(b)` only if `b` has a cell in `{r−1, r, r+1}`, and distinct blocks sit ≥2
rows apart, so **at most two blocks' neighbourhoods cover any row** — two
nibbles per row. Gated, not argued (gate H).

## NOT ESTABLISHED

- ~~**The extrapolation to H = 21.**~~ **MEASURED 2026-08-23, and the lean was
  right.** The census ladder reached H = 21 under the shared-partial-fill engine
  (`results/nkey-census.md`): **39,314,963 classes**, against the a(40) run's
  355,390,806-record frontier — a cut of **9.04×**, where the extrapolation
  carried nine heights had said "near 10×". Every height gated. The
  no-closed-form findings below the strike-through stand unchanged: there is
  still no OEIS match for `8, 19, 43, 101, 239, 575, 1399, 3441`, no
  constant-coefficient recurrence with any surplus, and
  `exactchange-probes.md` §9's three killed pattern-matches are not revived by
  having more terms. **What changed is that the 9.04× is a count and no longer
  a lean.** What did not change is that this remains king-only and that
  adoption is still unpriced — see *What adoption costs* above.
- **Whether the mid-column stage tables inherit the cut.** The congruence is
  proved and measured at column boundaries only.
- **What the telescope costs the completion prune.** `kinkFinalizeColumn`
  calls `completionLowerBound` before the fold, and part of what that prune
  knows is how many cells are still needed to reach an untouched boundary row.
  A flagless `C_H` run has no boundary requirement, so that half of the prune
  goes away. Every count above is the full reachable space with no `maxn` cap,
  i.e. the large-`maxn` limit; at production `maxn` the prune matters and the
  1.92× flag factor is an upper bound on what telescoping is worth.
- **Anything about wall clock.** No engine change has been written or timed.
  Every number here is a state count.
