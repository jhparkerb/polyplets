# Triangle hunt, Proposer 3 (slice recurrences): ranked summary

2026-08-11. Hypothesis class: recurrences along rows / columns / diagonals
and cross-direction links between column rational structure and diagonal
polynomial structure. Full detail on the survivors:
`results/triangle-hunt-atoms-ab-initio.md`. Everything below is exact
integer arithmetic; nothing was fitted (all surviving candidates have
n_params = 0).

Refuter A's review (`results/triangle-hunt-refutation-columns.md`) is
folded in: verdicts below are post-refutation, and the ranking moved the
q_5 relation to the top.

## Ranked results

1. **p3-q5-strip-recurrence** (Tier B, SURVIVES refutation outright). The
   order-29 atom q_5, computed exactly ab initio (coefficients new to the
   repo), annihilates C_5(n) = Σ_{h≤5}(6−h)T(n,h) for n ≥ 30 (certified
   n ≤ 160 here, n ≤ 170 by the refuter): an in-grid, parameter-free,
   30-coefficient linear check tying five columns across 30 consecutive
   rows; 10/10 holdout rows, row 40 ok, all seven of the refuter's
   perturbations of T(40,5) fail it. Unit coefficient on the target cell.
   The banked structure work proved this atom *unreachable by fitting*
   from 40 rows. The refuter judges it the closest thing this round
   produced to the second-source ruling's "tier-3 exact-arithmetic
   certificate" prize — while correctly noting it is not that artifact:
   it consumes 29 banked rows, so it certifies internal consistency of
   the triangle, not a rule-independent count.

2. **p3-col5-tm-value, p3-col6-tm-value** (SURVIVES-WEAKENED; reclassified
   per the refuter as **independent recomputation, Tier B-equivalent
   scope, not a relation**). T(n,5) and T(n,6) for every n ≤ 40 from an
   ab-initio strip TM, derivation-blind, zero banked inputs; 17/17
   "holdout" rows each — but that is agreement of two computations, not
   prediction (no fit region exists to hold out from). Lineage, per
   jasonp's second-source ruling (branch `second-source`, 2b3115b): the
   connectivity algorithm is the same idea as `core/transition.h`, so
   this is a consistency check against transcription/overflow/sharding
   faults, not a second count; what it adds over `results/strip-engine.md`
   (which already covers H ≤ 14, 45.0% of a(40)) is authorship and code
   lineage only, with the rule itself tested independently just to n = 12
   by the four-enumerator crosscheck. Share of a(40) covered:
   T(40,5)+T(40,6) = 2.510·10⁻⁴.

3. **Atom ledger hardened** (supporting result, not a candidate): q_1..q_6
   exact with certificates, re-certified end-to-end by the refuter's
   independent TM/BM/primes (coefficient-level agreement, n ≤ 170);
   squarefree + pairwise coprime now computed fact through H = 6 (closes
   the H ≥ 5 caveat in the root-separation theorem,
   `results/triangle-structure.md` §6); column orders 42 and 106 verified;
   q_7 computation in flight (on the 322-state H = 7 TM; state count =
   M_8 − 1, confirming the proved Motzkin identification of
   `results/king-column-motzkin.md`, branch `second-source`) to extend the
   Superseeker-novel degree sequence 1,2,4,9,29,68.

## Negatives (recorded so nobody re-probes)

- **N1 — recurrence-form column structure is dead above H = 5, forever.**
  Exact minimal column recurrences first apply at n = 43 (H=5, order 42,
  refuter-measured contiguous from its first possible instance, to n=170)
  and n ≥ 107 (H=6, order 106; certified from 112); the atom recurrence on
  the strip combination C_6 first applies at n = 69. All > 40. q_5-on-C_5
  (n ≥ 30) is the only in-grid atom recurrence beyond the banked H ≤ 4
  ones. Corollary: no slice recurrence in the column direction can ever
  predict the tall columns of row 40; direct TM evaluation is the only
  column route.
- **N2 — cross-direction link, x = 3 probe.** No visible structure in
  q_H(3) or 3^deg·q_H(1/3) (values grow structurelessly). The two soft
  patterns seen (q(−1) sign-paired magnitudes; constant terms 1,1,1,1,2,4)
  are parked as held-out tests for q_7, not results.
- **N3 — directions other than columns/diagonals/half-slope:** untestable,
  full stop — Wave 0's sweep established only (0,1), (−1,1), (−1,2) have
  slices spanning fit and holdout regions (`experiments/tristruct/
  sweep_report.md`); not re-probed here per the brief.
- **N4 — rows and low-order cross-column stencils:** already provably empty
  (`results/triangle-structure.md` §3, §6 root-separation theorem — now
  with its H ≤ 6 ingredients computed, see above); not re-probed.
- **N5 — the (−1,2) half-slope direction** (onset-parallel lines) belongs
  to below-onset defect structure (proof-first's ground); the sweep's
  P-recursive pass over it (order ≤ 7, degree ≤ 2) already came back empty.
  No proposer-3 attempt beyond that.

## Attack surface offered to the refuters

Free parameters: zero, all candidates (nothing fitted, so
FITTED-NOT-TESTED cannot bite; the honest attack is lineage, above).
Edges: the value candidates cover the full columns including the n = H
onset cells; the q_5 check's region n ≥ 30 is forced by the recurrence
depth, not chosen. Same-procedure-elsewhere: the pipeline reproduces banked
q_1..q_4 exactly (coefficient-level match) and its TM agrees with four
independent enumerators on all 57 cells n ≤ 12, H ≤ 6.
