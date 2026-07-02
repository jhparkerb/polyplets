# Completion-pruning audit (queue #4)

**2026-07-02.** Does our `completionLowerBound` (cpp/tma/signature.h:113) match
Barequet's completion-budget prune (their §4.1, the lever that kept A(70) in
32 GB)?

## What ours computes

`topReach + bottomReach + bandSum`:
- **topReach/bottomReach** = cells to climb to row 0 / reach row H-1 if those
  ends aren't touched. This is Barequet's **n_h** (touch both ends) — fully
  present.
- **bandSum** = sum of empty vertical bands between occupied rows that no single
  component spans. A 1-D-MST-like **vertical** connectivity term.

## Measured headroom (frontier dumps from the SVD probe)

| H | surviving states | mean components | ≥2 components |
|---|---|---|---|
| 8  | 1,604  | 1.79 | 64% |
| 10 | 11,005 | 2.12 | 79% |

Most surviving states are multi-component, so connectivity pruning has a large
candidate population — *if* our bound under-counts the cost to connect them.

## The gap, and why it's not a quick win

Barequet's **n_c** is a 2-D MST over the component graph (edge = geometric
distance between components). Ours captures only **vertical-gap** distance and
skips components with zero vertical gap (adjacent rows, different labels — which
in the diagonal encoding are separate components that must still merge to the
right at some horizontal cost our bound ignores). So ours is plausibly *looser*
than n_c on the 79% multi-component population.

**But this is a high-risk correctness surface.** These are record runs; an
over-tight completion bound *silently prunes valid states → wrong counts*, the
worst failure mode we have. A king cell can merge several components at once, so
the naive "(c−1) cells to connect c components" is **not** even a valid lower
bound — the real min-completion is geometric and subtle on the diagonal lattice.

## Recommendation

Defer as a **carefully-gated** item, not a quick win:
1. Build a brute-force oracle that computes the TRUE min cells to complete a
   signature for small H (exhaustive), red-first.
2. Only then derive a tighter admissible bound and prove it ≤ oracle on all
   small-H signatures before deploying.
3. Validate at scale (full a(20) --compare byte-match) before any record run
   trusts it.

Potential payoff (smaller spill peak → less spill-bound wall) is real given the
79% figure, but it is weeks-of-care work, not a drop-in. Behavior-preserving I/O
wins (queue #3) come first.
