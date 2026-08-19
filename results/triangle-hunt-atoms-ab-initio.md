# Strip atoms q_1..q_6 computed ab initio; three surviving column candidates

> Some files cited below were filed on the unmerged branch `triangle-structure` and the unmerged branch `half-measure` and never reached this one: `git show <branch>:<path>`.

2026-08-11, Proposer 3 (slice recurrences) of the triangle structure hunt
(`docs/triangle-structure-team-brief.md`). Scripts:
`experiments/tristruct/p3_striptm.py` (strip TM from the lattice definition),
`experiments/tristruct/p3_atoms.py` (atoms pipeline; log
`experiments/tristruct/p3_atoms.log`), candidates
`experiments/tristruct/candidates/p3_columns.py`. Exact atom coefficients:
`experiments/tristruct/data/p3_atoms_q.txt`; ab-initio column values:
`experiments/tristruct/data/p3_striptm_T.txt`.

Reviewed by Refuter A (`results/triangle-hunt-refutation-columns.md`):
end-to-end independent replication (own TM construction, own BM, own
primes) confirmed every number here; the q_5 relation SURVIVES outright,
the two value candidates SURVIVE-WEAKENED — reclassified below per the
refuter, whose corrections are folded into this revision.

## What was computed, and how it differs from what was banked

`results/triangle-structure.md` measured the atoms q_1..q_4 (degrees 1,2,4,9)
by fitting banked triangle data, recorded 29 and 68 as degrees only, and
proved ("the information wall") that q_5 needs ~60 triangle rows to pin from
data — the banked 40 rows can never produce it. This work goes around the
wall exactly as that file's §5 predicted: **compute** the atoms from a strip
transfer matrix instead of fitting them. New here:

- exact integer coefficients of **q_5 (degree 29) and q_6 (degree 68)** — in
  the repo previously only as degrees, never as polynomials;
- the whole pipeline is **derivation-blind**: the TM was written from the
  lattice definition by this proposer (no repo kernel consulted), and
  cross-checked only against this proposer's own independent Redelmeier
  enumerator on all 57 cells n ≤ 12, H ≤ 6
  (`results/triangle-hunt-enumerator-crosscheck.md`, zero mismatches);
- exact certification, not floating fit: Berlekamp–Massey mod six ~10^18
  primes (degrees agree across all six), CRT-lifted coefficients, then the
  recurrence checked **exactly over Z** on every available instance
  (S_H(n), n ≤ 160): 131 instances for q_5, 92 for q_6;
- q_1..q_4 reproduce the banked polynomials' degrees and certify on 151–159
  instances each — and the banked measured degrees (1,2,4,9,29,68) are all
  confirmed ab initio.

Structural checks, all exact:

- every q_H squarefree (gcd(q,q′) = 1 mod p ⇒ over Q), pairwise coprime —
  this **closes the caveat in `results/triangle-structure.md` §6**, where
  squarefreeness/coprimality for H ≥ 5 was "the structural expectation":
  the root-separation theorem's ingredients now hold as computed fact
  through H = 6;
- column factorization p_H = q_H·q_{H−1}·q_{H−2} annihilates the column
  T(·,H) on every available instance: orders 3, 7, 15, **42** (114
  instances), **106** (49 instances) for H = 2..6 — the predicted orders for
  H = 5, 6 are now verified, not extrapolated;
- purity: the strip count C_H(n) = Σ_{h≤H}(H−h+1)·T(n,h) satisfies q_H
  **alone** from n = deg(q_H)+1 — no contamination by lower atoms, the
  mechanism behind the one-atom-per-height structure theorem. Certified on
  n ≤ 160 here, n ≤ 170 by the refuter; a proof for all n would need a
  denominator-degree bound on the TM's rational GF that nobody has written
  down.

State counts of the TM: 1, 3, 8, 20, 50, 126 for H = 1..6, which is
M_{H+1} − 1. That identification is a **proved prior result**, not a
novelty of this work: `results/king-column-motzkin.md` (branch
`second-source`, commit a6b8f6a) proves #states(H) = Motzkin(H+1)−1 as a
theorem, with the series banked to H = 10; this TM confirms it through
H = 7 (322 = M_8 − 1 states, settled by construction against Refuter A's
independent TM in `experiments/tristruct/refA_h7_states.py`).

## The three verifier-surviving candidates

`python3 verify.py candidates/p3_columns.py` — all three SURVIVE the
machine, n_params=0 (nothing fitted), every scored cell real-sweep
provenance:

| id | kind | holdout | row 40 | refuter verdict |
|---|---|---|---|---|
| p3-col5-tm-value | value: T(n,5) = ab-initio TM value | 17/17 exact (n=23..39) | T(40,5) ok | SURVIVES-WEAKENED |
| p3-col6-tm-value | value: T(n,6) = ab-initio TM value | 17/17 exact | T(40,6) ok | SURVIVES-WEAKENED |
| p3-q5-strip-recurrence | boolean: q_5 annihilates C_5(n), n ≥ 30 | 10/10 (n=30..39) | ok | SURVIVES |

Columns H ≤ 4 are deliberately not claimed (KNOWN-COINCIDENT with the banked
column recurrences / engine low-strip).

Classification, per the refuter's accepted correction: the two value
candidates are **independent recomputation, Tier B-equivalent scope, not a
relation** — they recompute T(n,5), T(n,6) from scratch rather than predict
them from smaller n; "17/17 holdout" is agreement of two computations, with
no fit region to hold anything out from. The q_5 candidate is the actual
relation (Tier B as a row-40-subset check), with a checker (30 integer
coefficients) readable in one sitting.

## The four independence fields

- **Bits of independent check on a(40):** claimed 30 bits per cell
  (BITS-UNVERIFIED per the verifier's policy for value/boolean kinds; the
  values matched have 10–20 digits, so 30 bits/cell is a cap, not log2 of
  the value size) — defensible for the cells checked, not unconditional on
  a(40). Priced by the refuter: T(40,5)+T(40,6) = 2.510·10⁻⁴ of a(40). A
  wrong a(40) passes if its error avoids row-40 columns 5–6 (tall-column
  sweeps, spill/merge, P_k wiring); what genuinely fails is an error local
  to these columns or a *systematic* bug corrupting all columns — that last
  is the real residual value, since these are real-sweep cells checked
  against an enumeration-free route with no shared code. The q_5 check's
  row-40 power targets the same cell as p3-col5-tm-value (non-additive).
- **Input footprint:** derivation consumed ZERO banked cells. Predictions:
  the value candidates consume none either (pure TM output); the q_5
  recurrence check consumes banked columns h ≤ 5 of the 29 rows below the
  target (largest n = 39 when checking row 40).
- **Derivation independence:** fully blind — lattice definition → own
  enumerator (n ≤ 12 crosscheck) → own TM → BM/CRT/exact certification on
  the TM's own output. Banked data first touched by verify.py, at
  validation.
- **Rule independence:** honestly restated after review — the connectivity
  algorithm here (union-find over |dy| ≤ 1 cross-column adjacency with
  stranded-component death) is the *same idea* as `core/transition.h` and
  the kink kernel; per jasonp's settled ruling
  (`docs/second-source-team-brief.md`, branch `second-source`, commit
  2b3115b) same-rule agreement is evidence against transcription/overflow/
  sharding faults and "no evidence at all" against a wrong shared rule.
  What this work genuinely earns is **authorship and code-lineage
  independence** (no repo kernel consulted; the refuter's blind
  reimplementation converged on the same algorithm because it is the
  natural construction), anchored by the four-enumerator crosscheck — which
  does test the rule itself, but only to n = 12.

Known overlap, stated plainly: `results/strip-engine.md` already confirmed
columns H ≤ 14 for n ≤ 40 with a TM of the same design (45.0% of a(40) by
share, vs 2.5·10⁻⁴ here). The value candidates are a *third* source for
cells already confirmed twice, adding cross-mind code lineage only; the
durable novelty is the exact atoms plus the q_5 recurrence statement
(order-29 relation testable in-grid from n = 30), new to the repo.

## Negative: the atom ladder exits the triangle at H = 5

The exact minimal column recurrences predict nothing in-grid above H = 4.
The order-42 column-5 recurrence holds contiguously from **n = 43**, its
first possible instance (refuter-measured to n = 170; this file originally
said 47 from wrong "5+42" arithmetic — the certification here simply
started at 47). The order-106 column-6 recurrence's first possible instance
is n = 107 (certified here from 112; 107–111 unprobed). On the strip
combinations, q_6 first applies at n = 69 (certified from there). All > 40.
So **q_5 on C_5 (n ≥ 30) is the only atom-level recurrence with any in-grid
instances beyond H = 4, ever** — for all higher H, recurrence-form column
structure is untestable inside the 40-row triangle, and only direct TM
evaluation (the value candidates' route) can touch those columns. This
sharpens `results/triangle-structure.md` §1's "H ≥ 5 not pinnable from 35
rows": even GIVEN the exact H=5,6 recurrences, they fit zero and predict
zero triangle cells in recurrence form.

## Cross-direction probe (negative + one unexplained observation)

Looking for a link between column rational structure and diagonal 3-power
structure: q_H evaluated at the diagonal-relevant points x = 3 and x = 1/3
(reciprocal-normalized) shows no usable form — values grow without visible
structure (q_5(3) = −10855423960544, …). Recorded as a negative.

Observation, no mechanism, not claimed as a result: q_H(−1) pairs with sign
flip, q_1(−1)=−2, q_2(−1)=2; q_3(−1)=6, q_4(−1)=−6; q_5(−1)=−480,
q_6(−1)=480. Constant terms |q_H(0)| = 1,1,1,1,2,4. Both left to the q_7
computation (in flight) as held-out tests; if q_7 breaks them, they die as
coincidences.
