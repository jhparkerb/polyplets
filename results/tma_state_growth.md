# Transfer-matrix state-growth calibration (square-8 / polyplets)

*Measured June 14, 2026. Question: can the transfer-matrix method — a counting
algorithm completely different from the generation used in the a(19) campaigns
— reach size 19, and thereby give an ALGORITHM-INDEPENDENT confirmation of
a(19)? (The gympie+ayr campaigns only decorrelate decomposition/compiler/
hardware; they share the generation algorithm.)*

## Measurement

Peak number of distinct boundary signatures held at once (the memory
bottleneck), from the instrumented v0 engine (height swept up to n, no aspect
optimization, `build/tma square8 N`, `peak_states` on stderr):

| n | peak states | ratio |
|---|---|---|
| 8 | 1,604 | — |
| 9 | 4,177 | 2.60 |
| 10 | 11,005 | 2.64 |
| 11 | 29,291 | 2.66 |

Growth base **k ≈ 2.63** (ratios rising slightly with n, so the asymptotic base
is a little higher — call it ~2.6–3.0). Crucially this is SMALL — comparable to
the square lattice. The feared "non-planar king-lattice state explosion" did
**not** materialise.

## Feasibility verdict: YES

- **With the standard aspect optimisation** (count animals at least as wide as
  tall, double the strictly-wider ones; this caps boundary height at
  ⌈n/2⌉ = 10 for n = 19): peak states ~ k^10 ≈ 10^4–10^5 — **megabyte scale,
  trivially feasible**.
- **Even without it** (brute height-up-to-19): ~k^19 ≈ 0.7–4 ×10^8 states ≈
  13–80 GB unpruned — feasible on a large-memory server as-is, and pruning
  would cut it.

So a genuine algorithm-independent check on a(19) is achievable. The work
required is moderate and standard (not research): add the aspect trick and a
non-brute column-mask enumeration to the square-8 transfer-matrix engine. The
v0's only real limitation was the 2^H mask fan-out (runtime) and sweeping
height all the way to n (memory) — both removed by the aspect optimisation.

## Consequence for confidence

This upgrades a(19)'s outlook (RESULTS.md R1): beyond the dual-campaign
decorrelation and the mod-8 Burnside congruence, a true second-algorithm
equality check is now known to be feasible, so a(19) can reach genuine
"confirmed" status rather than "candidate + congruence".
