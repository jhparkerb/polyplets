# Refuter B: Proposer 1's mod-3 deficit families — the circularity ruling

2026-08-11, Refuter B of the triangle-structure hunt, final scope per the
lead: rule on whether the deficit families' law-free confirmations are
circular, and whether a better test exists at no compute cost. Attack
script: `experiments/tristruct/refB_deficit.py`; verification of the lead's
and Refuter A's measured inputs re-run independently (numbers below).

**Deferred to Refuter A** (`results/triangle-hunt-refutation-proof-first.md`),
not restated here: the luck-rate quantification (joint p = 0.0297 against
the 42-cell empirical null, ~1.7 bits/family), the cull-boundary
verification (exactly one law-free cell per family, P_14 not in-grid
interpolable at 12 of 15 needed points), and the T(40,26) repricing
(census overlap; 1 of the 1.6 bits is the unit choice). All of Refuter A's
inputs I relied on were re-verified: 42 law-free sleeve cells (k = 14..19),
residue distribution {0:16, 1:13, 2:13}, provenance split 27 real-sweep /
15 closed-form-Pk — the lead's corrected framing (law-free is majority
enumerated) is confirmed.

## The ruling: partially circular — formula-bounded, not self-circular

Two questions, answered separately.

**Does the wiring force the observed residues? No — except the zeros.**
On a deficit-d line, T = P_k(3k+1−d)/3^d. The proved integrality of the
diagonal law forces the DIVISIBILITY v₃ ≥ d (that much is wired in by
theorem), but nothing in the wiring or the shape theorem determines the
UNIT — the residue after dividing by 3^d. P_14 as wired is tower structure
(grand-form/severance derivation) plus two real anchor cells; per
`results/ns_a40/PROVENANCE.md` the documented instances are P_18 fit on
real T(37,19), T(38,20) and P_19 on real T(39,20), T(40,21), i.e. anchors
at (k+19, 19), (k+20, 20) — for P_14 that is (33,19), (34,20), both
real-sweep (verified). The family pattern was fitted on sleeve cells
k ≤ 8, entirely different diagonals. Neither side was fitted to the other:
**not self-circular.**

**Is the confirmation independent, then? No — it is formula-bounded.**
The banked values at (39,25), (38,24), (40,26) are evaluations of wired
P_14 at n beyond its real-anchor range (n = 36..40 > 35). Confirming the
pattern there tests one thing: that the tower-derived, anchor-pinned P_14,
EXTRAPOLATED past all enumerated k=14 data, has the low-3-adic units an
empirical cross-k regularity demands. A failure would have meant either
the pattern is false or the P_14 pinning/wiring chain (tower algebra,
anchor transcription, engine wiring) is wrong. So the check has real
teeth — against the formula chain only. It touches no count: nothing at
those cells was ever enumerated, so no enumeration error, anywhere, at any
n, can ever be caught by it.

**Price on the d=4 / d=5 supporting evidence** (the lead's ask):

- 9 (d=4) / 8 (d=5) enumerated real-sweep cells at k ≤ 12 showing the
  constant — genuine evidence the regularity is real, zero independent
  check value (each is diagonal-law-redundant given other enumerated
  in-grid cells).
- 1 law-free cell each: **~1.7 conditional bits on the P_14
  pinning-and-wiring chain** (conditional on the unproved pattern; rate
  per Refuter A's null), **0 bits on any enumeration**, and 0 direct bits
  on a(40) (no row-40 cells — the proposer stated that honestly).
- Correlation caveat for the synthesis: the law-free hits of d = 3, 4, 5
  (and Refuter A's post-hoc d=6 pair) all evaluate the SAME one or two
  polynomials, P_14 and P_15, at nearby points. Jointly they are ~5
  conditional bits on one object's 3-adic behavior, not four independent
  braces.

Verdict wording for the ledger: d=4, d=5 **SURVIVE as regularities**
(Refuter A's statistical case stands), with independence field corrected
from "one law-free real-sweep cell, ~1.6 bits" to "one law-free
closed-form-Pk cell; ~1.7 bits against formula-chain error conditional on
the pattern; nothing against enumeration error." The proposer's report
mislabels both cells' provenance ("real-sweep"); `triangle.py` says
closed-form-Pk, and the harness's own README states the consequence
("checking the wiring of a formula, not the count").

## Question 2: can the class be aimed at enumerated law-free cells? No — by geometry

Measured (script, verified): the 27 real-sweep law-free sleeve cells all
have deficit **d ≥ 8** (d = 3k+1−n with H = n−k ≤ 21 and k ≥ 14 forces
d ≥ 2k−20 ≥ 8). But the fit-low/predict-high protocol needs ≥ 4 fit cells
at n ≤ 22, which caps the class at **d ≤ 6** (d=7: 3 fit cells; d=8,9: 2;
d=10: 1). And every fittable line's law-free cells sit at H = 2k+1−d ≥ 22
for k ≥ 14 — the formula band, by the family's own geometry. So within
this hypothesis class the fittable lines and the enumerated law-free cells
are **disjoint**: any line that reaches an enumerated law-free cell cannot
be fitted, and any line that can be fitted confirms only against formula
output. This is the class-level instance of Proposer 1's own frame
negative (which Refuter A adjudicated sound as scoped), and it is why the
honest answer to "is there a better test at no compute cost" is **no**.

The one upgrade path is the one the proposer already named: prove the
deficit-d unit formulas (Lagrange-Bürmann to the mod-3^(d+2) master
curve). A PROVED formula needs no fit region, so tower levels d = 8..19
would then be checkable directly against the 27 enumerated law-free cells
— converting exactly the cells this class cannot reach into theorem-grade
checks. That is a round-2 argument, not a candidate.

## Complements from my earlier pass (kept, one line each)

- Per-cell provenance audit of all four families is in
  `refB_deficit.py` part A/B output (every fit and holdout cell, flag and
  known.py-implication).
- Procedure-level calibration, complementary to Refuter A's value-level
  null: 131 comparable sparse control lines through the identical fit
  procedure — 13 strict passes, 12 of them cull-fodder constant-0 lines,
  post-cull 1/131; 30 perturbation trials, fail-closed except 6
  head-cell perturbations outside the constant rule's last-3 window (the
  certificate covers the last 3 fit cells plus holdout, not the head).
- The post-cull control pass is the **d=7 line**: period (2,2,1) in k
  holding from k = 4 (including its below-onset head) through k = 15,
  law-free cells (36,22), (39,24) — both formula-band, consistent with
  the geometry above. Found by grid mining, post-hoc, no bits claimed;
  sits alongside Refuter A's d=6 find (2,1,1) as the next instances for
  the proof route (d = 3, 6, 7 periods: (2,0,1), (2,1,1), (2,2,1)).
- Below-onset probes: d=3, 4, 6 patterns break one step below onset;
  d=5's continuation at k=4 is a coincidence on column-closed-form cells
  (Refuter A measured the same).
