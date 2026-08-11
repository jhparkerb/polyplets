# Refuter A: Proposer 3's column/atom candidates — verdicts

2026-08-11, Refuter A of the triangle structure hunt
(`docs/triangle-structure-team-brief.md`). Targets: the three
verifier-surviving candidates in
`experiments/tristruct/candidates/p3_columns.py`
(`results/triangle-hunt-atoms-ab-initio.md`,
`results/triangle-hunt-slices.md`).

Checker: `experiments/tristruct/refA_columns_check.py` (log
`refA_columns_check.log`) — Refuter A's own strip transfer matrix written
from the lattice definition, deliberately different construction from the
proposer's (BFS/merge-closure over vertical runs, no union-find; own
canonicalization; own limb packing), own Berlekamp–Massey, own primes, all
exact integer arithmetic. `p3_striptm.py`/`p3_atoms.py` were not imported.
Every check below is from that run unless cited otherwise.

## Verdicts

| candidate | verdict |
|---|---|
| p3-col5-tm-value | **SURVIVES-WEAKENED** (reclassify, rescope bits; values fully confirmed) |
| p3-col6-tm-value | **SURVIVES-WEAKENED** (same) |
| p3-q5-strip-recurrence | **SURVIVES** |

None of the three is broken. All are n_params = 0; the overfitting attack
has no purchase and I do not manufacture one. The weakening of the value
candidates is categorical, not numerical.

## What I could not break (attacks run, all passed)

1. **Full independent replication.** My own TM reproduces state counts
   1,3,8,20,50,126; matches the banked triangle
   (`results/ns_a40/perheight/h{1..6}.out`) on **all 240 cells** n ≤ 40,
   H ≤ 6, including structural zeros and onset cells n = H; matches the
   proposer's table `data/p3_striptm_T.txt` on all 240 cells.
2. **Atom certification, re-done from scratch.** q_5 and q_6 as banked in
   `data/p3_atoms_q.txt` annihilate **my** S_5, S_6 exactly over Z on 141
   and 102 instances (n ≤ 170, exceeding the proposer's n ≤ 160). My own BM
   mod two fresh primes (2^61−1, 2^62−57) returns minimal degrees
   1,2,4,9,29,68 and coefficient-level agreement with the banked q_5, q_6.
   Squarefree and pairwise-coprime re-certified mod a fresh prime.
3. **The candidate check on purely banked data.** q_5 annihilates banked
   C_5(n) for all 11 instances n = 30..40. Banked C_5 equals my S_5 on
   n ≤ 40.
4. **Perturbation.** T(40,5) offset by ±1, ±3^k (k = 1,3,20,30), 10^15+7:
   all seven fail the q_5 check. Unit coefficient on the target confirmed
   (q_5 monic, h = 5 weight is 6−5 = 1). The verify.py tautology guard
   (VALUE-INSENSITIVE) had already perturbed it independently.
5. **Region forced, not chosen.** Order 29 on a sequence defined from
   n = 1 makes n = 30 the first possible instance; nothing was trimmed.
6. **Restatement grep.** q_5/q_6 coefficients appear nowhere in-tree
   outside the p3 files; `results/triangle-structure.md` carries 29 and 68
   as degrees only (its §3 "information wall" proves they were unreachable
   by fitting 40 rows — the ab-initio route is the only way in). Confirmed
   new to the repo.
7. **Procedure control.** Proposer 4's exoneration covered the *fitting*
   procedure; this pipeline doesn't fit. The control that matters is item 2
   above — an end-to-end second derivation by different code and different
   primes — which is stronger than a cross-lattice transfer.

## The two judgment calls the lead asked for

**Predict vs recompute (value candidates).** p3-col5/6-tm-value do not
predict anything from banked numbers; they *recompute* T(n,5), T(n,6) from
scratch and compare. "17/17 holdout" is agreement of two computations —
there is no fit region to hold anything out from. Under the ladder's
wording ("predicts … from strictly smaller n") the Tier B label is a
category error; under the mission sentence ("checked by a route that does
not re-run the enumeration engines") they are exactly on target. They are
second-source-class verification, the same genus as
`results/strip-engine.md`, and should be labeled that way: **independent
recomputation, Tier B-equivalent scope, not a relation.**

**Lineage (what the third source adds).** `results/strip-engine.md`
already confirmed columns H ≤ 14 at every n ≤ 40, and it concedes its rule
is `core/transition.h`'s rule. The proposer's claim of an "independent
rule" is overstated in the same way: union-find over |dy| ≤ 1 cross-column
adjacency with stranded-component death is the *same algorithm* — my own
blind implementation converged on it too (modulo replacing union-find with
merge-closure), because it is the natural construction. What is genuinely
independent is authorship and code lineage, anchored by the four-enumerator
n ≤ 12 crosscheck.

This is not just this refuter's judgment: it is the project's settled
standard, jasonp's ruling in `docs/second-source-team-brief.md` (branch
`second-source` only, commit 2b3115b — read via
`git show 2b3115b:docs/second-source-team-brief.md`; reached here
independently before that file was readable on this branch). The ruling,
on the strip engine itself: it "**does not qualify as verification**"
because its union-find rule "is *the same rule* as this repo's reference
column oracle, `core/transition.h`, and the same rule as the kink kernel
that produced the banked triangle. It was written independently, but it is
not a different idea." Agreement is "evidence against transcription,
overflow, and sharding faults, and as **no evidence at all** against a
wrong shared rule." P3's col5/col6 TM is strip-TM-class, so the ruling
applies verbatim: the value candidates are a consistency check against
transcription/overflow/sharding faults, not a second count of columns 5–6.
The one thing P3 earns beyond the ruling's scope: the n ≤ 12 agreement
with four genuinely independent enumerators
(`results/triangle-hunt-enumerator-crosscheck.md`) does test the
connectivity rule itself — but only out to n = 12.

Priced honestly: for columns 5–6 the value candidates are a third source
for cells already confirmed twice, adding cross-mind code lineage only.
The durable additions are the **exact atoms q_5, q_6** (closing
triangle-structure.md §6's squarefree/coprime caveat, verifying orders 42
and 106) and the in-grid q_5 relation. On that last: the same ruling names
the higher prize as "a tier-3 artifact — an exact-arithmetic certificate
for a cell or a row that a short independent checker verifies", for which
"nobody has proposed a mechanism". q_5-on-C_5 is the closest thing this
round produced to that shape — parameter-free, in-grid, 30 integer
coefficients checkable by a short program — but it is not that artifact:
it consumes 29 banked rows plus row-40 h ≤ 4, so it certifies internal
consistency of the banked triangle, not a rule-independent count. Closest
shape yet; the lineage gap is exactly the ruling's.

## Bits correction (all three candidates)

30 bits/cell is defensible **for the cells checked** (10–20-digit exact
match against an independent computation; a cap, and conservative at that
level). It is not an unconditional 30 bits on a(40). Measured from the
banked triangle: T(40,5)+T(40,6) = 14245607541927909032762631549 =
**2.510·10⁻⁴ of a(40)** (columns h ≤ 6 together: 2.511·10⁻⁴; strip-engine's
H ≤ 14 coverage is 45.0% by the same measure). What a wrong a(40) must look
like to pass: any error not touching row-40 columns 5–6 — e.g. one confined
to tall-column sweeps, spill/merge, or the closed-form-Pk wiring (H ≥ 22).
What fails: errors local to columns 5–6, and — worth stating, it is the
real value — any *systematic* bug corrupting all columns, since T(40,5),
T(40,6) are real-sweep cells of the same kink pipeline and are here checked
against an enumeration-free route with no shared code. The q_5 candidate's
check power on row 40 targets the same single cell as p3-col5-tm-value
(non-additive), and its inputs are 29 banked rows plus row-40 h ≤ 4, so as
an a(40) check it inherits banked lineage the value candidates do not.

## Corrections to the proposer's file

- **Onset of the order-42 column-5 recurrence: n = 43, not 47.**
  p_5 = q_5·q_4·q_3 annihilates T(·,5) contiguously from n = 43 (checked
  on my own data to n = 170; the proposer's certification simply started
  at 47 and never probed 43–46). Still > 40, so negative N1 stands
  unchanged; the "5+42" arithmetic in
  `results/triangle-hunt-atoms-ab-initio.md` is wrong.
- **Cross-branch citation, and the Motzkin identification is NOT new.**
  `results/king-column-motzkin.md` is absent from this branch but real: it
  lives on branch `second-source` (commit a6b8f6a, 2026-08-11), and it
  proves #states(H) = Motzkin(H+1)−1 as a theorem (fill × non-crossing
  run-partition), with the state series banked to H = 10. P3's citation is
  correct; P3's observation is a confirmation of a proved result, not a
  novelty. (An earlier version of this file called the citation dangling
  and the identification new — both wrong.)
- **H = 7 state count: P3's "323" was a transcription slip, not a spurious
  state.** P3's report to the lead gave 323 states at H = 7; the proved
  count is M_8 − 1 = 322. Settled by construction
  (`experiments/tristruct/refA_h7_states.py`, log `refA_h7_states.log`):
  Refuter A's own TM and P3's `build_states(7)` both construct exactly
  **322** states, identical sets, with H = 1..6 controls 1,3,8,20,50,126
  agreeing on both sides. The in-flight q_7 job (`p3_atoms7.py`) calls the
  same `strip_series`/`build_states` and therefore runs on the correct
  322-state space; only the sentence in P3's report needs fixing.
- **Wording precision:** "q_5 annihilates C_5(n) for all n ≥ 30" is
  certified through n = 170, and on every in-grid instance; a proof for
  all n needs a denominator-degree bound on the TM's rational GF that
  nobody has written down. Immaterial to the in-grid candidates; the
  statement should say "certified n ≤ 170" if it stays.

## Attacks that found nothing (named per the brief)

Overfitting (no free parameters — no purchase); fit-region gaming (no fit
exists; q_5 region forced); edge cells (onset n = H, structural zeros,
small-n: all match); tautology (perturbations fail, target coefficient
unit); restatement (grep clean for the atoms; state counts previously
banked, flagged above); certification fraud (independent replication
passes, degrees/squarefree/coprime confirmed); procedure transfer
(replaced by end-to-end reimplementation).
