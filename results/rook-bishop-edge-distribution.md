# Rook/diagonal edge-count distribution (sampled, not yet exact)

2026-07-07. Prompted by an evening of testing "cheap-core + sparse-correction"
decompositions of king-adjacency (all measured negative — see
`boundary-push-tensornetwork.md`'s connectivity-entanglement result and the
frontier-factorization checks in this session's transcript). Question: is the
*entirely diagonal-connected* case (0 rook edges — exactly the existing
`bishopConn == A001168` structural check in `cpp/g2_redelmeier.cpp`) a
dominant term that a small number of "1 rook edge," "2 rook edges," ...
corrections could converge toward?

## Method

2000 uniform-random n=12 polyplets from `build/tma_sample` (`/tmp/samp_12.txt`,
seed 42 — same sample used for the block-cut-tree and frontier-factorization
checks earlier this session). For each specimen, counted king-adjacent pairs
by type (rook offset vs. diagonal/bishop offset) and stratified by rook-edge
count.

**Caveat: this is a sampled distribution, not an exact enumeration.** The
engine already has the machinery to make it exact and cheap at small n (the
existing `--contacts` flag in `g2_redelmeier.cpp` tracks (size,
diagonal-contact-count) exactly; a sibling `(size, rook-edge-count)` table is
a small extension of the same code, not yet built) — flagging this as a
buildable follow-up, not claiming exactness here.

## Result

n=12, 2000 samples, stratified by rook-edge count:

| rook edges | count | fraction |
|---|---|---|
| 0 (entirely diagonal) | 4 | 0.20% |
| 1 | 36 | 1.80% |
| 2 | 89 | 4.45% |
| 3 | 195 | 9.75% |
| 4 | 305 | 15.25% |
| 5 | 366 | 18.30% |
| 6 | 397 | 19.85% (peak) |
| 7 | 285 | 14.25% |
| 8 | 177 | 8.85% |
| 9 | 93 | 4.65% |
| 10 | 40 | 2.00% |
| 11 | 11 | 0.55% |
| 12 | 2 | 0.10% |

**The distribution is unimodal, peaking near the middle** (6 of a max ~11
rook edges for a spanning tree on 12 cells), not concentrated near 0. The
entirely-diagonal case (0 rook edges, exactly A001168(12) as a fraction of
a(12)) is a vanishing 0.20%.

## Interpretation

The "spindly, mostly-diagonal" intuition for large polyplets (repeatedly
observed this session: 96.7%-99.8% of shapes are disconnected under various
single-edge-type restrictions, needing several "glue" edges of the other
type) does NOT mean typical shapes are overwhelmingly diagonal with rare rook
exceptions. It means rook and diagonal edges occur in genuinely *comparable*
amounts for a typical large polyplet — the histogram above is the honest
picture, not a rapidly-converging series. A "count pure-diagonal, then its
1-edge-different cousins" expansion would need essentially the *entire*
histogram (all ~12 terms) to reconstruct a(12), not just the first couple —
consistent with, and a further sharpening of, every other "cheap core +
sparse correction" idea killed this session.

Still a useful, real characterization of the ensemble (same family as the
existing perimeter/holes/height joint distributions), even without handing
us a computational shortcut.
