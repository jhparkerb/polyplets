# Candidate: windowed (variable-width) counts-row — ANALYSIS (survives)

The counts-row (N+1 u32s per state) is ~84% of per-state footprint and the working set
*is* the bandwidth bottleneck (MT plateaus ~3.5x regardless of cores). Trimming it should
ease bandwidth → faster, esp. under MT. This branch holds the analysis; implementation TBD.

## Probe (fraction of current full alloc actually needed; lower = more savings)
```
              perColTrim   leadTrim   fullTrim
H=11 N=18       0.685       0.350      0.328
H=11 N=20       0.667       0.363      0.341
H=11 N=22       0.652       0.376      0.352
H=13 N=16       0.763       0.307      0.256   (heaviest sampled — best savings)
```
- **leadTrim ~0.31-0.38**: ~65% of the row is leading zeros (store [minSize..maxn]). Working
  set → ~45-55% of current → bandwidth relief → plausibly ~1.5-2x (more than a constant trim).
- **Heavy heights benefit most** (the a(22)-dominant sweeps).
- **leadTrim ≈ fullTrim**: trailing zeros negligible — leading-trim alone captures ~95%.
- **perColTrim ~0.67**: per-COLUMN uniform stride fails (minSize varies within a column).
  **Per-STATE variable width is REQUIRED.**

## Implementation crux: a next-state's base (minSize) isn't known at first insert
Later contributions in the same column can land at a smaller index → leftward growth.
Approaches: (a) packed arena + handle leftward growth (repack); (b) cheap STRUCTURAL lower
bound on minSize(out) from the signature → fix base at creation, no growth (the research bit);
(c) per-row alloc (rejected — reintroduces per-state heap alloc the hot path avoids).

Verdict: validated top single-machine lever (attacks bandwidth directly), research-grade
implementation (the base-handling). Priority informed by the a(22) ETA — if the job is long,
the ~2x is very worth implementing pre-launch; the squad + a cmp oracle de-risks correctness.
