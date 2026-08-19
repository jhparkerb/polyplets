# Proof-first proposer — ranked summary (Wave 1, triangle structure hunt)

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

2026-08-11, Proposer 1 (proof-first) of `docs/triangle-structure-team-brief.md`.
Enumerator crosscheck (mandatory first task) is recorded in
`results/triangle-hunt-enumerator-crosscheck.md` (zero mismatches, four
independent enumerators, n <= 12). Everything below derives from the
definition and own-enumerated cells (`build/p1_enum`, n <= 13, n <= 15 in
flight); banked data touched only through `verify.py`'s sandbox and, for
negatives, the machine sweep's recorded verdicts.

## Ranked results

### 1. PROVED two-term cell inequality (candidate SURVIVES; Tier: softer)

    T(n,H) >= 3*T(n-1,H-1) + T(n-1,H)   for 2 <= H <= n-1,
    T(n,n)  = 3*T(n-1,n-1)              (equality, pure-walk column).

*Proof.* Two injections with disjoint images. (i) Walk-cap: to an
(n-1)-cell, height-(H-1) animal add one cell in a new top row at offset
delta in {-1,0,+1} from the LEFTMOST cell of the old top row. The image has
top row = exactly one cell; deleting it recovers the animal and the offset,
so the map from 3 disjoint copies is injective. (ii) Grow-right: add a cell
immediately right of the top row's rightmost cell; delete-top-right inverts
it; every image has >= 2 cells in its top row. Top-row size separates the
two images. For H = n every cell row is a singleton and each row sits at
one of 3 offsets from the row below (T(n,n) = 3^(n-1)), giving equality. QED

Machine record: `candidates/p1_inequalities.py` — **SURVIVES, 510/510
holdout cells (323 real-sweep), row 40 ok on all 39 cells (19 real-sweep)**.
Own-data check `p1_ineq_check.py`: 0 violations, equalities exactly the
H = n column, tightest strict ratio 1.0606 at (13,12) — the bound is
asymptotically tight on the k=1 diagonal, so it is not vacuous.

Independence fields: **bits on a(40): ~0** (one-sided bound; a same-magnitude
wrong count passes; claimed as such — the harness's VALUE-INSENSITIVE guard
is the correct judgement of its checking power, and the candidate survives
only because the proved equality column is value-sensitive). **Input
footprint:** the two row-(n-1) cells per prediction; derivation consumed no
banked cells. **Derivation independence:** definition only. **Rule
independence:** own connectivity code validated the proof's small cases.
Novelty grep: no statement of this form in `results/*.md`,
`docs/proofs/*.md` (searched inequality/monotone/3T(n-1 patterns; nearest
prior work is growth-rate sandwiches per column, `hv-growth-sandwich.md`,
which bound lambda not cells).

### 2. Deficit-family congruences mod 3 on the unswept (2,-3) lines
### (two SURVIVORS; one culled-but-predictive pattern; Tier C, thin)

The proved deficit-1 (T(3k,2k) == 1, spine T3) and deficit-2
(T(3m+2,2m+1) == 2) families are constants along n = 3k+1-d. The sweep's
geometry finding says the (2,-3) direction has zero testable slices under
its >= 10-fit-point rule, so d >= 3 was never machine-probed. Putting the
d = 1,2 hypothesis class (constant / period <= 4 in k) through the
verifier on d = 3..6 (`candidates/p1_deficit_families.py`):

| d | fitted pattern (k from d) | verdict | notes |
|---|---|---|---|
| 3 | period 3: 2,0,1 by (k-3) mod 3 | CULLED(KNOWN-COINCIDENT) | holdout k=9..13 all law-implied; **but the pattern also hits the NON-implied open sleeve cell (40,26), k=14: predicts T(40,26) == 1 (mod 3) — banked-confirmed** |
| 4 | constant 2 | **SURVIVES 6/6** | one holdout cell (k=14, n=39, real-sweep) beyond the law's k<=13 reach |
| 5 | constant 2 | **SURVIVES 6/6** | same: k=14 (n=38) is the one law-free confirmation |
| 6 | none in class (residues 2,1,1,2 at k=6..9) | CULLED(FIT-ERROR) | 4 fit points cannot support the class; honest unresolved |

Honest weight: `known.py`'s diagonal-law predicate interpolates P_k through
the window cells n = 2k+1..3k+1 — which contains every sleeve cell — so for
k <= 13 it reproduces sleeve residues tautologically, and the cull rightly
scores them as in-grid-derivable. Each survivor's law-free content is ONE
real-sweep cell at k = 14 (~1.6 bits), plus the confirmed prediction on
the open row-40 sleeve cell for d = 3. **This corrects an error in my
first framing: the genuinely open mod-3 region is below onset (n >= 2H)
plus sleeve k >= 14 — not the whole sleeve.**

Organizing find: the d = 3 pattern says sleeve zeros on that line occur
EXACTLY at k == 1 (mod 3) — it retrodicts every d = 3 zero in the
sleeve-zero census of `ternary-spine.md` ((k,n) = (4,10), (7,19), (10,28),
(13,37)) and the non-zero at (14,40). The census calls a closed law for
these "the open remainder of the Witt tower"; this is its first clean
sub-family regularity.

Conjectures + proof route (named, not executed): P_k(3k-2)/3^3 mod 3
cycles 2,0,1 with extra 3-divisibility exactly at k == 1 (mod 3);
P_k(3k-3)/3^4 == 2 and P_k(3k-4)/3^5 == 2 (mod 3) for all k. Route: the
deficit-2 proof's Lagrange-Buermann-to-master-curve method
(`experiments/deficit2_proof.py`, explicitly flagged reusable for
(n,k)-linear families) on the mod-3^(d+2) master equation — needs d more
tower levels than the mod-27 equation `defect-gas.md` derived. Desk work,
priced at one boundary-weight extension per level.

### 3. Frame identity: the mod-3 triangle IS the R_k coefficient array

From the proved Step 4 of `docs/proofs/diagonal-law.md`
([y^k]F = R_k(z)/(1-3z)^(k+1), R_k in Z[z], deg <= 2k+1), expanding
[z^H] and reducing mod 3 (only the j = H term survives the 3-powers):

    T(H+k, H) == r_{k,H} (mod 3) for ALL H,  r_{k,j} := [z^j] R_k,
    and mod 9:  T(H+k,H) == r_{k,H} + 3(k+1) r_{k,H-1}.

One-line corollary, recorded as the organizing frame (not claimed as a
result). Two consequences that ARE load-bearing:

- **Per-cell freshness (provable, explains the sweep's BARRENs):** r_{k,H}
  appears with unit coefficient in cell (H+k, H) and only with a factor
  3^(H'-H) in the higher cells of its diagonal — so mod 3, each open cell
  (sleeve/below-onset) carries a coefficient visible at that cell alone.
  The shape theorem by itself imposes NO relation among open-cell residues;
  any true relation must come from the cross-k weight grammar. This is why
  every periodicity-class hypothesis on the open region was machine-BARREN.
- **What a row-40 open residue costs:** below-onset residues T(40,H) mod 3,
  H = 15..19, are r_{k,H} for k = 21..25 — computable only from the full
  cluster-weight catalogue to surplus k (2^(k-1) types; the atom-ledger
  information wall in another basis), or from pinning data at n >= 2k+1 > 40.
  Sleeve residues H = 21..26 sit at deficit d = 3k-39 in {3,6,9,12,15,18};
  the proved deficit-family method (Lagrange-Buermann to the mod-3^(d+1)
  master curve — d=1 is spine T3, d=2 is the proved deficit-2 family) needs
  tower level d+1, i.e. level 19 for H=21. **Conclusion, stated as the
  negative it is: no small congruence can reach the row-40 open cells; the
  H15-19 single-sweep block is not checkable mod 3 by any in-grid-fittable
  structure of this frame.**

### 4. Bounded negative: the open region mod 3 is NOT algebraic in a
### spine-sized box (machine-stamped)

Hypothesis class chosen from theory (Christol: 3-automatic <=> algebraic
GF over F_3(y,z); the proved spine cubic is the in-regime instance).
`candidates/p1_algebraic_mod3.py` hunts Q(y,z,F) = 0 inside the n <= 22
sandbox over a 97-ansatz ladder (deg_F <= 4, deg_y <= 5, deg_z <= 5, always
#equations = 276 >= 2x unknowns, max 125 unknowns), for BOTH the full mod-3
series F(y,z) = sum (T mod 3) y^(n-H) z^H and its below-onset cone
restriction; an accepted equation had to Hensel-continue from scratch and
reproduce every sandbox coefficient. **Every kernel is empty** — verdict
CULLED(FIT-ERROR) with the full ladder in the flag, plus the same on own
data to n = 13 (`p1_alg_hunt.py`; machinery selftested on a synthetic
algebraic series, kernel found + Hensel reproduction). So: if the triangle
mod 3 is automatic at all, its equation lies beyond this box; the "small
law like the spine" hope for the open region is dead. (Bound honestly
stated: weight-22 window; equations of much larger height remain possible.)

### 5. Negative: onset-cell constancy

Own data showed T(2k+1, k+1) == 2 (mod 3) at k = 2..6. The machine record
already refutes the general law: slice S(-1,2)c1 (the onset line n = 2H-1)
is BARREN mod 3 on n <= 22 (`sweep_report.md` line 850), so the constancy
breaks in n = 15..21. (n=15 own-enumeration in flight to pin the first
break with own data; will be noted here.)

### 6. Negative (reasoned, no compute): in-regime residue laws are
### auto-dead, and k >= 14 diagonals are untestable

Any congruence on in-regime diagonal cells with k <= 13 is implied by the
interpolated diagonal law (`known.py` predicts exact values there) — cull
KNOWN-COINCIDENT by construction. For k >= 14 the in-grid onset window is
too short to pin the 2k+2 coefficients, and every below-onset cell adds a
fresh coefficient (freshness, #2), so there is no holdout at any modulus:
the frontier-parity wall of `ternary-spine.md` in congruence form. This
closes the "mod-2 Lucas-binomial diagonal law" idea I derived from the
frame identity ([y^k]F mod 2 = R_k/(1-z)^(k+1), a 2-automatic tail) —
provable but predictionless in-grid; recorded so nobody re-probes it.

## What I failed to prove (and why)

- **Sleeve unit formulas for d >= 3** (the open remainder of the Witt
  tower named in `ternary-spine.md`): the reusable LB-to-curve method needs
  the mod-81 master equation — one more level of boundary-cluster weight
  data than `defect-gas.md` derived (it stopped at the explicit mod-27
  equation). Desk-feasible next step but not a session deliverable; own
  data shows the d=3 family is NOT constant (T(10,6) == 0, T(13,8) == 1
  mod 3), so unlike d = 1, 2 the target is an automatic-type formula, not
  a constant.
- **Exact below-onset structure at depth j >= 4**: depths 1-3 are closed in
  the a-basis (`onset-defect-depth1-closed.md`, severance W3), but I
  verified the a-basis closures cannot yield below-onset RESIDUES: the law
  part q_k(H) 3^H needs P_k mod unbounded 3-powers for k >= 20, which no
  in-grid data pins. Not a route to row-40 checks.

## Independence summary (brief-mandated fields, per candidate)

| candidate | bits on a(40) | input footprint | derivation | rule |
|---|---|---|---|---|
| p1-two-term-lower-bound | ~0 (one-sided; stated) | 2 cells of row n-1 per check | definition only | own code |
| p1-mod3-algebraic-full/cone | 0 (negative result) | sandbox n<=22 (fit only) | class from theory; own cells n<=13 | own code for derivation data |
| p1-deficit{3,4,5,6}-family-mod3 | 0 direct (no a(40) cell); ~1.6 bits each on one law-free real-sweep holdout cell (d=4: n=39; d=5: n=38); d=3 pattern confirmed on open cell (40,26) | 4-6 family cells n<=22 (fit); predictions consume nothing | class = the proved d=1,2 analogues; own family values n<=13 examined first | no connectivity decision in the relation |

Scripts (all under `experiments/tristruct/`, run from there):
`p1_mod3_map.py`, `p1_alg_hunt.py`, `p1_ineq_check.py`,
`candidates/p1_inequalities.py`, `candidates/p1_algebraic_mod3.py`.
