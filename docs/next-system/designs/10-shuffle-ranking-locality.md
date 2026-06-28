# 10 — can the merge shuffle be eliminated? a dense ranking exists; a LOCAL one cannot

From the architecture digs: the per-column MERGE is an all-to-all shuffle (every map
output feeds every merge band, because the transition scatters keys). Can it become
**N independent sorts**? That needs the transition to be *partition-preserving* —
successors stay in a state's key-band. This note answers it, and **retracts an
earlier overclaim** ("no compact dense ranking of king/crossing boundary states
exists" — false). Companion to designs/06 (the seek-index that made the shuffle
cheap) and #20 (the RAM wall).

## Background: why MERGE is a shuffle (recap)

A boundary state = a set partition of the occupied frontier cells (component labels)
+ touched-top/bottom flags; the KEY is the signature, the VALUE is a ranged count
vector; MERGE sums values of equal keys. The column transition canonicalizes the
labels, so a map unit's output keys scatter across the whole sorted order ⇒ every
merge band must read every map output (designs/06). In MapReduce terms it is a
`reduceByKey` whose producer rewrites keys — a *wide dependency*, so a shuffle is
mandatory **unless** the data is co-partitioned by the output key (Spark
`preservesPartitioning` is legal only if the function "doesn't modify the keys").
Afrati–Das Sarma–Ullman (VLDB 2013) bound replication-rate vs reducer-size; our
aggregation has replication rate **1** (each record to one band), so the cost is the
M×R fan-out *structure*, not data blow-up — which the seek-index already neutralized
(merge ≈ 0.2 % of a column). See `papers/`: afrati_dassarma_2013, zaharia_2012_spark,
dean_ghemawat_2004, bu_2010_haloop.

## Retraction: a compact dense ranking DOES exist

Earlier I claimed king/8-connected boundary states (which, unlike 4-connected, allow
**crossing** partitions) have no compact dense ranking, so the in-RAM indexed-vector
route is closed. Wrong:

- Set partitions — crossing or not — are exactly **restricted-growth strings** (RGS:
  `a[i+1] ≤ 1 + max(a[1..i])`). Crossing is geometric; RGS doesn't see it.
- RGS have a standard **O(W) ranking/unranking**: the number of completions of a
  prefix depends only on `(position, #blocks-so-far)` (Stirling/Bell partial sums).
  Our local adjacency rule (vertically-adjacent occupied cells share a block) keeps
  the prefix-count state bounded, so ranking stays efficient and **dense over the
  valid states**, range ≈ D_H (boundary-state count 1,5,15,39,98,246,624,1604,… ≈
  2.55^H).
- Numerically D₂₀ ≈ 1.3×10⁸ — same order as the live frontier peak (2.9×10⁷) — so a
  dense count-vector at H20 is ≈ 14 GB: **RAM-feasible**. The
  Barequet–Rote/Knuth/Jensen **in-RAM indexed-vector** scheme (no sort/merge/shuffle,
  random-access update; for non-crossing they use Motzkin-rank, but RGS handles
  crossing) is therefore *not* closed to us. Motzkin's only edge over RGS is a
  smaller range (Catalan vs a Bell-subset) and a lower-triangular matrix.

So the in-RAM, shuffle-free path is **viable**; we chose external sort-merge for
unbounded n, not because a ranking is impossible.

## What is impossible: a LOCAL (banded) ranking

Turning the one shuffle into N independent sorts needs the transition **local**:
successors within ±b ranks, so a contiguous input band → contiguous output band.
Claim: no ranking achieves this.

- **Bandwidth ⇒ small separators.** Bandwidth b ⇒ every prefix/suffix cut is crossed
  by O(b·Δ) edges (edges span ≤ b in rank; Δ = degree). Small bandwidth ⇒ small
  separators everywhere ⇒ a path-like graph.
- **The transition graph is the opposite.** Exponential growth (Perron λ≈7.1, states
  ~2.55^H) + strong mixing, and we *measure* the consequence: a contiguous input
  key-band's successors scatter across **all** output bands (the all-to-all). Even
  the literature's best ordering (Motzkin rank, Barequet–Rote) yields a matrix that
  is lower-**triangular but not banded**.
- **Therefore** no ordering bands it unless the graph has small balanced separators
  in *some* arrangement — i.e. unless it is *not* an expander. Exponential growth +
  observed scatter indicate it is one.
- **Honest limit of the argument:** this is a strong argument, not a closed theorem —
  full rigor needs a spectral-gap / separator lower bound for this specific graph,
  not proven here. But the burden is now reversed, and the triangular-not-banded
  literature corroborates. The door shut is *locality*, closed by *expansion* — not
  *ranking*.

## The corrected fork

| approach | shuffle | bound | king status |
|---|---|---|---|
| in-RAM indexed / hash aggregation | none | RAM ≈ D_H | **viable** — ~14 GB at a20; we chose not to |
| external sort-merge | all-to-all | disk, scales | our path; seek-index makes it cheap |
| out-of-core **and** shuffle-free | none | — | needs locality → blocked by expansion (only truly-closed door) |

"N independent sorts" is the third row, shut by mixing, not encoding. The realistic
lever is the **first** row: a **hash/indexed-resident frontier** for the RAM-fitting
heights (no sort, no merge, no shuffle at all), falling back to sort-merge only when
a column overflows RAM.

Corroboration: the in-RAM row holds until D_H ≈ box RAM, i.e. D_H·~104 B ≈ 78 GB,
which lands at **~a(22)** — exactly the RAM wall #20/`reach.md` derived
independently. So a hash-resident frontier is a real alternative *through ~a(21)*,
and the sort-merge shuffle engine is the right tool precisely from a(22) on, where
the frontier no longer fits and the encoding question becomes moot.

## What would actually be worth trying

1. **Hash-resident frontier for RAM-fitting heights** (kills the shuffle entirely
   below the RAM wall): a flat open-addressing map sig→count-vec, random-access
   `combine` on insert, no sorted runs. This is the Barequet/Jensen approach with our
   RGS-rankable (or just hashed) keys — and it's the same lever as the #20 "compress
   the counts row" work, since both are about fitting the frontier in RAM longer.
2. **Do NOT** chase a partition-preserving/local encoding — expansion forecloses it;
   even the 4-connected ideal is only triangular.
3. Leave the sort-merge + seek-index engine as the out-of-core path for a(22)+, where
   it is unavoidable and already cheap.
