# Severance W1 — the anchor-cut: P_k ab initio for k ≤ 9

2026-08-09. Workstream W1 of docs/onset-defect-severance-plan.md, complete.
Fable-authored gates, Opus-executed implementation, every number below printed
by a shipped script.

## Result

The diagonal polynomials `P_1..P_9` are now derived **ab initio from cluster
weights alone** — no swept cell enters the derivation. For these levels the
wired `diagCoeffTable` (orchestrator/sweep.go) is confirmed by an independent
second source, and the two-anchor-cells-per-level dependence on the production
sweep is severed.

- Weights: `cpp/severance_w1.cpp` → `build/severance_w1`, exact `__int128`
  with loud overflow check; all 511 compositions to surplus level 9 in
  `results/severance_w1_weights_k9.txt` (k ≤ 8 file alongside).
- Assembly: `experiments/severance_w1_assemble.py`, exact Fractions, chain
  identity per docs/proofs/{diagonal-law,grand-form}.md; derived P_k equals
  the wired table coefficient-for-coefficient for k = 1..9, reproduces 3
  banked in-onset cells per level, deg R_k = 2k+1 throughout.
- New ab-initio depth-1 leads beyond the banked k ≤ 5 sequence:
  lead(R_6..R_9) = −24323825, 607833256, −15348306104, 390644841751
  (consistent with the gap-walk D_1 via lead(R_k) = (−3)^(k+1)·D_1(k)).

## Evidence tier

- Gate `experiments/severance_w1_gate.py` (Fable-authored, RED selftest
  fires): banked k ≤ 5 per-composition exact; fresh level-6 DP holdouts
  ((7,) full; (4,4), (3,5) boundary/pure fresh + interior against the banked
  8.4 h/3.7 h Python cells); structural invariants (completeness, reference
  order, reversal symmetry, single-row closed forms) at every level to 9.
  Run twice: by the implementing agent and independently by the manager.
- Assembly gate is internal to `severance_w1_assemble.py`; RED control
  (`--red`) fires 23 assertions; corrupted-input run exits nonzero
  (verified independently).
- One real bug caught by the ladder during the port: interval-based contact
  test overcounted ((2,2) gave 340 vs 339); fixed to cell-by-cell union as
  in the reference. The k ≤ 5 gate is what caught it — the fail-closed
  structure did its job.
- Cross-machine: dalby-built binary's k ≤ 5 output md5-identical before the
  long run; k = 9 computed on dalby (66 min wall, 16 threads, 53 GB peak).

## Ceiling

k = 10 was declined on memory, not time: peak RSS scales past dalby's
125 GB and the tail is one huge stack whose state map alone would be tens of
GB. Extending needs a state-space reduction (symmetry quotient or frontier
compression in the stack DP), not more cores. k = 9 is therefore the honest
W1 ceiling as built.

## What this changes in the certification map

Middle-band rows are fully code-independent when every cell has H ≤ 14
(strip engine) or k = n−H ≤ 9 (this result): rows n ≤ 24 once the
below-onset depths j ≤ n−29 are closed — for n ≤ 24 no depth formulas are
needed (all such cells are in-onset), so **rows n ≤ 24 of T(n,·) are now
covered by two independent sources end-to-end.** Rows 25–33 additionally
need W3 (depths) and keep the 2-cells-per-level anchor for k = 10..18.
