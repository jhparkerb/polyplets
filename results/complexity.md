# Complexity: Redelmeier generation vs. column transfer matrix

The two methods used for the fixed-polyplet counts, with the constants measured
this session (λ from the series, the transfer-matrix state growth from the
per-height D_H run).

| | Time | Memory | Parallelism |
|---|---|---|---|
| **Redelmeier generation** | Θ(a(n)) ≈ λⁿ/n, **λ ≈ 7.10** (measured) — visits every animal once | **polynomial** — O(n) (recursion stack + frontier), essentially none | **embarrassingly parallel** (ran 64–96-way) |
| **Transfer matrix** | Θ(peak boundary-state count) — **exponential in n, base ≪ λ** (per-height ≈ **2.6^H** measured) | **exponential** — the state table *is* the memory (≈12.5 GB at a(19)) | **memory-bandwidth bound**, ~2× within a height; heights independent |

## The qualitative split (the whole story)
- **Generation:** time-expensive, memory-free, trivially parallel. Pays the full
  λ≈7.1 per term but needs ~no RAM and scales to as many cores as available.
- **Transfer matrix:** smaller time base (it *merges* all animals sharing a
  boundary instead of listing them), paid for with an exponential state table and
  poor parallelism (bandwidth wall ~2×).

TANSTAAFL: the transfer matrix trades generation's polynomial memory for a smaller
time base, and trades away the easy parallelism in doing so.

## What we actually lived (wall-clock ≠ asymptotics)
For a(19), **generation was faster in wall-clock** (hours, 64–96-way) than the
transfer matrix (*days*, bandwidth-bound at ~2× parallelism) — despite the TM's
smaller asymptotic base. The TM's smaller base only wins past a crossover at large
n on a big-RAM machine; below it, generation's parallelism dominates. So in
practice: **generation = workhorse, transfer matrix = independent check** — its
value here was never speed but that its failure modes are disjoint from
generation's.

## Measured refinements (this session)
- λ ≈ 7.10 (ratio-extrapolation of a(n), n≤19; θ ≈ −1), was previously an eyeball.
- TM per-height state growth ≈ 2.6^H (D_H = 1, 5, 15, 39, 98, 246, 624, 1604,
  4177, 11005 for H=1..10) — far below the Bell(H+1) I had first guessed (~60×
  smaller at H=10), which is why the fixed-height-GF wall sits at ~H=18–20, not ~13.
