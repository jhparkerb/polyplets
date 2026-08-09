# Severance W3 — depths 2, 3, 4 closed

2026-08-09. Workstream W3 of docs/onset-defect-severance-plan.md, complete.
Fable-authored gate, Opus-executed derivation and port; every number below is
printed by a shipped script.

## Result

The below-onset defects `D_j(k)` are closed at depths j = 2, 3, 4 the same
way depth 1 was (results/onset-defect-depth1-closed.md): an exact identity
over independently enumerated weight families, no triangle data and no wired
`P_k` anywhere in the derivation.

- Identity (C)/(D) in `experiments/severance_w3_depths.py`: grade every
  cluster family by excess `e = Σ(s_i − 2)`; the coefficient `[z^(k+1−j)]`
  of the correction polynomial draws only on families of **total excess
  ≤ j−1**, assembled through the chain identity with binomial `(1−3z)`
  corrections. At j = 1 the identity collapses to the closed depth-1 form
  `[y^k](P̂ − B²/(3+S))`, asserted in the script.
- **Correction to the depth-1 note's §6 pricing** (now fixed there): the
  family class is excess-bounded, not "up to j−1 rows of size 3" — depth 3
  needs the one-4-row family, depth 4 needs one-5-row, 4+3, and 3+3+3.
- Family tables: Python row-transfer DP for e ≤ 2; e = 3 at K = 19 via
  `cpp/severance_w3_families.cpp` → `build/severance_w3_families`
  (exact `__int128`, checked arithmetic; 146 s, table
  `results/severance_w3_families_K19_e3.txt`).

## Evidence tier

Gate `experiments/severance_w3_gate.py` (Fable-authored; RED selftest
fires; depth-1 closed series as a known-good anchor; banked side assembled
from triangle + wired P_k, which the candidate never touches):

```
depth 1: 19 banked cells match exactly (k = 1..19)
depth 2: 18 banked cells match exactly (k = 2..19)
depth 3: 17 banked cells match exactly (k = 3..19)
depth 4: 16 banked cells match exactly (k = 4..19)
```

Run by the implementing agents and re-run independently by the manager.

Family validation: per-type KNOWN_WEIGHTS (31 types, 4 weights) exact;
aggregated (k,e) cells vs `results/severance_w1_weights_k9.txt` exact
(all four families, e ≤ 3); e = 0 series equals `depth1_gap_walk`
families l ≤ 9; C++ vs Python cross-checks at three (K, emax) corners;
span-cap independence check; fresh `count_stack` holdouts past every banked
table at k = 11 (five cells, e ≤ 2 and e = 3) and k = 10 (two e = 3 cells:
(5,2⁶) pure = 41507430, (3,3,3,2⁴) pure = 424773396).

First depth-4 values: `D_4(4..7) = 1400566/6561, 75221426/19683,
1199562484/19683, 51621741496/59049`.

## What this changes in the certification map

With depths j ≤ 4 closed, every below-onset cell of rows n ≤ 33 with
k = n−H ≤ 18 is now formula-covered (deepest depth needed at the H = 15
seam of row 33 is j = 4). Combined with the strip engine (H ≤ 14) and W1's
ab-initio P_k (k ≤ 9):

- rows n ≤ 24: two independent sources end-to-end (unchanged, W1);
- rows 25–33: fully formula-covered, with exactly one residual dependence
  on the sweep — the two anchor cells per level for k = 10..18 that pin
  P_10..P_18 inside the Lean-proved grand-form shape;
- rows 34–40: out of reach (need P_19+ pinning data at n ≥ 41).

## Open

- Depth j ≥ 5: the frame covers it (excess ≤ j−1); each depth adds finitely
  many families, all computable by the same C++ DP. Not needed for the
  certification map below row 34, so not run.
- Algebraicity of the depth-j GFs (the depth-1 note's conjecture — shared
  branch point at 1/27): untouched; the identity here is exact but the
  kernel-method elimination was only done at depth 1.
