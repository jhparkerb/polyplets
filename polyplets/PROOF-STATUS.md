# Lean formalization status — production diagonal formulas P_0..P_18

Goal (2026-07-20, /goal active): Lean-prove the diagonal closed forms used by
the production engine (`diagonalCell`); where full proof is out of
reach, prove as much as possible and state exactly what remains input.
The engine wires k = 0..19. Lean covers **k ≤ 18**, all grand-pinned from
two real-swept cells per level. k = 19 is deliberately not pinned: it is
fitted-no-holdout, no holdout is possible (the sequence closes at a(40)),
and no banked term uses it — see the a(40)-close extension note below.
Scope/route decisions: `PLAN.md`. Architecture (the peeling recursion,
replacing the paper's GF route): `DESIGN.md`. Pin inputs (production
coefficients + banked onset points, fail-closed generated): `pin-data.md`.

Build: `cd polyplets && lake exe cache get` (once) then `lake build`.
Green = a sorry-free tree: there are no `sorry`s anywhere in `Polyplets/`
(the historical "intended sorrys" list is gone; `Diagonal.lean` closed the
last one).

## Landed (sorry-free, green, all committed)

- `Defs.lean` — kingAdj, KingConnected, IsCanonical, T. (pre-goal)
- `Finite.lean` — crossing lemmas, width bound, finiteness, T as Finset.card.
- `RowProfile.lean` — row fibers, occupied-rows interval, step (b) one
  doubled row, (c-fwd), (d-local) for the old k=1 route. (pre-goal)
- `Compute.lean` — computable `Tc`, `Tc_eq_T`, decidable KingConnected via
  bounded closure; native_decide validation vs banked triangle (sparse cells).
- `ComputeBridge.lean` — completes the definitional bridge (hostile-witness
  audit fix, 2026-07-21): every nonzero cell of rows n ≤ 5 plus T(6,4)=1480,
  T(6,5)=945 as in-tree native_decide theorems (the n = 6 probes were
  previously "verified out-of-file" prose only). Bridge = 17 kernel-recorded
  nonzero cells, rows 1..5 complete.
- `Graph.lean` — kingGraph SimpleGraph bridge, walk-support lemma.
- `Separation.lean` — walk-row separation: generic glue, cut (boundary-dart
  excision surgery), erase-top corollary. Subsumes old k=1 (c-rev) gap.
- `Weights.lean` — walk-top counts `d k H`, aggregated cluster weights
  `V ℓ j` / `Vt ℓ j` (by rows×surplus, no type catalogue), spread bounds,
  native_decide values: V(1,1)=25, Vt(1,1)=5 (the 16+9 / 4+1 gadgets of
  docs/proofs/T-n-nm1.md), V(1,2)=49, Vt(1,2)=7, V(2,2)=339, Vt(2,2)=66;
  **identity gates PASS**: c-identity at T(5,3)=248 = 136+25+21+66 and
  d-recursion at d_2(4)=1019 = 408+125+147+339 — the DESIGN v2 recursion is
  numerically confirmed against banked data.

- `Peel.lean` — the three peeling bijections (card_nbij' with shift/xNorm
  renormalization), 1748 lines, sorry-free:
  `d_rec` : d k H = 3·d k (H−1) + ΣΣ V·d (k−j) (H−1−ℓ)   (H ≥ k+2)
  `c_ident`: T (H+k) H = d k H + ΣΣ Vt·d (k−j) (H−ℓ)      (H ≥ k+1)
  #print axioms: [propext, Classical.choice, Quot.sound] — fully deductive.
- `Shape.lean` — **the diagonal law shape THEOREM**: `shape_d`, `shape`
  (T(H+k,H) = q_k(H)·3^H, deg ≤ k, ALL H ≥ k+1), `shape_production`
  (∃ P deg ≤ k: T(n,n−k) = P(n)·3^(n−1−3k) for n ≥ 2k+1, zpow +
  subtraction-free companion), `production_int_onset` (+'), and stretch
  `production_int_all` (P integer-valued on ALL of ℤ, finite differences).
  Same clean axiom footprint — no native_decide anywhere in the proof path,
  and since 2026-07-30 that is **enforced**, not asserted: `shape_d`,
  `shape`, `shape_production`, `production_int_all`, `d_rec` and `c_ident`
  each carry a `#guard_msgs`-wrapped `#print axioms` in
  `Grand/Audit.lean`, so a native_decide leaking into this cone fails the
  build (`P1_closed`/`P2_closed`/`P3_pinned` are pinned there too, with
  their real leaf sets).
  Leading-coeff stretch: CLOSED by `Grand/Lead.lean` (`lead_coeff_25`,
  `expPoly_natDegree_eq`, `shape_lead` — see Grand section). Historical
  note: corrected target was P_k.coeff k = 25^k/k! (= production's
  "leading 25^j/j!"; the earlier δ-form in the brief was wrong, caught in
  review).

- `Weights3.lean` — j=3 light weight leaves (V(1,3)=81, Vᵗ(1,3)=9,
  V(2,3)=1860, Vᵗ(2,3)=307; 207 s one-off compile).
- `Pin.lean` — the endgame. Generic Lagrange pin lemma; recursion-evaluator
  value theorems (T(6,4), T(7,5) via d_rec/c_ident — no big enumeration);
  production polynomials transcribed by `scripts/gen_pin.py` from
  pin-data.md with per-point norm_num guards. Per-k results:
  - **k = 0, 1, 2 UNCONDITIONAL**: `P0_pinned`, `P1_pinned`/`P1_closed`,
    `P2_pinned`/`P2_closed`.
  - **k = 3**: `P3_pinned_of_heavy` (hypotheses = V 3 3 = 4778,
    Vᵗ 3 3 = 919, d 3 4 = 4687); `Weights3Heavy.lean` (IN the default
    target's closure since the Grand tier landed — `Polyplets.lean` →
    `Grand.PinGrand` → `Weights3Heavy`; ~37 min on a cold build, cached
    after) discharges them ⇒ unconditional `P3_pinned`. The V 3 3 check
    (~1.2·10⁸ candidates) stack-overflows as one native_decide, so it is
    chunked by leftmost cluster column into 15 per-file native_decides
    (`WeightsChunk*.lean`, partition lemma native_decide-free, histogram
    cross-checked by scripts/gen_v33_chunks.py). **BUILT 2026-07-21**
    (`lake build Polyplets.Weights3Heavy`, ~37 min wall: chunks ≤ 856 s
    parallel + assembly 1343 s) — `P3_pinned` is UNCONDITIONAL, axioms =
    standard + the chunk/leaf native_decide values.
  - **k = 4..11 CONDITIONAL-ON-BANKED**: `Pk_pinned_of_banked`, hypotheses
    = the k+1 banked onset T-values (results/triangle.txt). These lists are
    **not** uniformly two-algorithm, and some entries are not even real
    sweeps: as the Supersession note below records, this tier's hypotheses
    include formula-generated cells (`T 31 20` at k = 11). Provenance of
    the hypothesis cells is graded by the Grand tier's anchor set, not
    here — see the split immediately below.
  - **k = 12..16 PARTIAL**: `Pk_pinned_of_partial`, hypotheses = all
    banked points (12/10/8/6/4) + the 1/4/7/10/13 beyond-banked points at
    the production-PREDICTED values, explicitly flagged `-- PREDICTED` —
    these were the precisely-stated residue of what the then-banked n ≤ 36
    data could not pin. Superseded: the triangle now runs to n ≤ 40 and the
    Grand tier pins these levels outright (see Supersession below).
- `Diagonal.lean` — `T_n_nm1`/`T_n_nm2` re-proved from `P1_closed`/
  `P2_closed`; **the tree is fully sorry-free**.

## Grand form — staircase route (LANDED 2026-07-21, `Polyplets/Grand/`)

Formalization of `docs/proofs/grand-form.md` per `GRANDFORM-PLAN.md`
(briefs `briefs/GF1..GF7`, executed by Opus agents). Seven modules:
`Series` (convolution toolkit), `Mu` (root series ν, multiplier μ,
`mu_conv_nu`), `MuRec` (**`d_mu_rec`**: `d k (H+1) = Σ_i μ_i·d (k−i) H`,
H ≥ k+1, sharp onset — the one-mode resummation as a single strong
induction from `d_rec`), `Staircase` (**`T_staircase`**, the same for
T-diagonals via `c_ident`), `PinGrand` (generated by
`scripts/gen_grand_pin.py`, fail-closed against `results/triangle.txt` and
`experiments/staircase_check.py`), `ExpForm`/`Lead` (the abstract exp-form
and leading-coefficient corollaries), `Audit` (single audit point).

Headline results and their audited axioms (verbatim from
`Polyplets/Grand/Audit.lean`, 2026-07-21):

- `d_mu_rec`, `T_staircase`, **`grand_form`**
  (`3^(3k+1)·T(H+k,H) = expCoeff aSeq bSeq k (H+k)·3^(H+k)` for ALL k,
  H ≥ k+1, no hypotheses), `grand_form_prod`:
  `[propext, Classical.choice, Quot.sound]` — **standard axioms only, no
  native_decide anywhere in the cone** (the seed `T 1 1 = 1` is
  `Sanity.lean`'s hand proof).
- `lead_coeff_25` (`[n^k]P_k = 25^k/k!` for all k — `Shape.lean`'s
  deferred stretch goal, closed), `expPoly_natDegree_eq` (deg = k exactly),
  `shape_lead`, `bSeq_one`, `mu_one`: standard + the single `V_1_1`
  native_decide leaf.
- `P<k>_grand_of_banked`, k = 1..18: the PRODUCTION polynomials
  (`orchestrator/sweep.go`, via `Pin.lean`'s `Pp<k>`) pinned for all
  n ≥ 2k+1 with hypotheses = **2 real-swept cells per level**
  (`T(2j+1, j+1)`, `T(2j+2, j+2)` for j = 4..18 — 30 anchors at k = 18,
  every one with H ≤ 20 and every one REAL-SWEPT (columns H ≤ 21 are real
  sweeps of the a(40) run); levels ≤ 3 discharged from
  `P1_closed`/`P2_closed`/`P3_pinned`). Axioms: standard + `P3_pinned`'s
  heavy-k=3 native_decide set (V/Vt/d leaves + 15 CFGVchunk cards + light
  base enumerations).

  **Anchor provenance, measured (2026-07-30, AUDIT-2026-07-30 L7).** All 30
  anchors are real-swept cells of the production kink engine. How many have
  a *second* source is a different question, and the answer is not
  "two-algorithm":

  - **19 strip-second-sourced** — the anchors with H ≤ 14 and n ≤ 36, the
    reach of the banked independent strip transfer-matrix run
    (`results/strip-engine.md`, 413 cells, 0 mismatch).
  - **11 kink-only** — beyond strip reach even at N = 40 (all have H ≥ 15):

        T(28,15) T(29,15) T(30,16) T(31,16) T(32,17) T(33,17)
        T(34,18) T(35,18) T(36,19) T(37,19) T(38,20)

    Cross-ISA and cross-revision re-runs rule out machine, build and
    transient faults for these, but cannot catch a logic bug shared by
    every run of the same kernel. Same grade the project gives a(23)+:
    single-algorithm, multiply cross-checked.

  Two-algorithm (Redelmeier) confirmation covers row totals through n = 22
  only, which reaches the k ≤ 10 anchors' rows and no further.

**Supersession.** The `Pin.lean` tier map below is now historical (kept for
cross-validation): the k = 12..16 PARTIAL tier's flagged-PREDICTED
hypotheses are RETIRED — `P<k>_grand_of_banked` needs no beyond-banked
points — and the k = 4..11 conditional tier's hypothesis lists, which
included formula-generated cells (e.g. `T 31 20` at k = 11), are replaced
by real-swept-only anchors. Banked data now fully pins every wired
diagonal; the "extend to n = 49" upgrade path is obsolete.

**a(40)-close extension (2026-07-29).** With the project closed at a(40)
(banked triangle n ≤ 40, `results/triangle.txt` reassembled from
`results/ns_a40/perheight/`), the Grand tier extends to the full wired
range: `Pp17`/`Pp18` transcribed into `Pin.lean` (defs + degree lemmas +
guards against REAL-SWEPT cells only — formula-generated cells on those
diagonals are excluded as circular), `PinGrand.lean` regenerated with
`--kmax 18` (fail-closed oracle now checks the staircase identity on 209
real-cell instances, up from 170). `P17_grand_of_banked` anchors:
T(35,18), T(36,19); `P18_grand_of_banked`: T(37,19), T(38,20) — the same
cells the production fit used. **P_19 is deliberately NOT formalized**:
it is fitted from the final two top cells T(39,20)/T(40,21), has no
possible holdout (the sequence closes at a(40)), and is never used by
any banked term; pinning it in Lean would certify nothing.

**Build receipt (AUDIT-2026-07-30 L8).** The k ≤ 18 extension had no
banked evidence that it builds — the claim lived in this file and nowhere
else. `polyplets/build-receipt-2026-07-30.log` records `lake build
--no-build` at rev `7a62883`: *All targets up-to-date (8592 jobs)*, Lean
`v4.31.0`, Mathlib `v4.31.0`, on gympie. Because `#guard_msgs` mismatches
are build errors, an up-to-date closure also certifies that every
axiom-footprint guard passed.

## Outworks — second campaign (LANDED 2026-07-30, `OUTWORKS-PLAN.md`)

Eight briefs (`briefs/OW1..OW8`), executed by Opus agents in three waves on
branch `lean-outworks`, orchestrator-reviewed per unit. Targets from the
2026-07-30 claims-vs-Lean audit. New modules, all sorry-free:

- `Sequence.lean` (OW-1) — **`a n` exists in Lean** (A006770 as ncard of
  height-blind canonical animals), `a_eq_sum : a n = Σ_{H=1..n} T n H`,
  computable twin `ac`, native_decide anchors `a_1..a_6` =
  1, 4, 20, 110, 638, 3832 vs banked row sums. `a_6` costs ~700 s / 5.9 GB
  (forces `Tc 6 6`); `a 7` infeasible (C(49,7) ≈ 86M subsets).
- `UpperBound.lean` (OW-3) — `a_le_choose : a n ≤ C(5n, n)` by the
  decision-tree exploration (14-clause invariant, accept-position code,
  re-anchored `expShape` injection — the brief's raw anchor is NOT
  word-determined, caught and fixed in execution), and
  `choose_le_pow : C(5n,n)·256^n ≤ 3125^n`. NO native_decide in the file.
- `Growth.lean` (OW-2) — **λ exists**: `a_supermul` (Klarner concatenation
  with explicit cut recovery), `lambda := exp(−lim)` via Mathlib Fekete,
  `lambda_tendsto`, `a_le_lambda_pow`, and the machine-checked bracket
  **`3.95 < λ ≤ 3125/256`** (`lambda_gt`/`lambda_le`; lower side inherits
  exactly the `a_6` leaf).
- `IntCoeff.lean` (OW-4) — `factorial_smul_int_coeff` (deg ≤ k integer-
  valued ⇒ k!·coeffs ∈ ℤ, binomial basis via forward differences) and
  `production_factorial_int` (§6.1's "k!·P_k integral"). Standard axioms.
- `Symmetry.lean` (OW-7) — D₄/C₄ acting by apply-then-reanchor; the §7
  Burnside identities `free_eq`, `oneSided_eq`, `bilateral_eq` and
  `r90_vanish` (n ≢ 0,1 mod 4 ⇒ R90 = 0, affine quarter-turn argument),
  all standard axioms; anchors vs `results/sym_counts.txt` n ≤ 5 in-file
  (n = 6 verified out-of-file; ~490 s/element to add); derived n = 4
  spot checks Free/OneSided/Bilateral = 22/34/10.
- `Holes.lean` + `HolesUpper.lean` (OW-6) — hole machinery from scratch
  (rook components, `enclosed`, `SingleHole`), **`maxhole_lower`
  unconditional** (diagonal-frame family `hullBox ∖ boxHole`, card a+b+2
  for ALL a,b — no degenerate (a,b), no n = 5 special case; anchors
  n = 4..10 by kernel decide, zero native_decide), (I′) parity count +
  maximization unconditional, and Theorem 2's upper bound **conditional on
  the named `MoatBound`** hypothesis (`maxhole_upper`, `maxhole` =
  IsGreatest) — the discrete-Jordan step needs digital topology Mathlib
  lacks; both cheap substitutes measured-refuted (module doc has the
  numbers). Finding: `boxHole a b` is rook-DISCONNECTED iff min(a,b) = 1
  and max ≥ 3 (multi-hole rings, invisible to the total-area checks of
  `results/maxhole-proof.md`).
- `Northcott.lean` (OW-8) — house-arrest finiteness: bounded degree +
  bounded house ⇒ finitely many algebraic integers (bridges Mathlib's
  2025 `finite_mahlerMeasure_le`; the claims audit's "Mathlib lacks it"
  is superseded). Finding: step 5 of the non-D-finiteness argument needs
  the FINITENESS form `finite_setOf_degree_le_of_house_le`, not bare
  unboundedness — both proved, divergence documented in the module doc.
- `Universal/` (OW-5, the Verbatim Wager) — **the diagonal law
  universalized**: `RowLocal` lattices (finite nonempty up-offset set D,
  b = |D|), abstract `PeelSystem` engine, full generic geometric port
  (Separation + the three peeling bijections), `universal_shape` /
  `universal_shape_production` / `universal_production_int_all` for EVERY
  row-local lattice, standard axioms. **Wager verdict: verbatim yes** —
  the only parameterization is the width bound (`M·(n−1)`, since general
  lattices skip columns; false-for-general-L lemma `exists_x_eq_of_cross`
  replaced by a walk-length bound), and the paper's p-adic integrality
  step is NOT needed (exact division, prime-agnostic). King re-derived
  definitionally (`KingAgree.lean`, recursions re-proved generically);
  instances pinned: square `P₁ = 4X − 8` (ordinary polyominoes!), hex
  `P₁ = 9X − 15`, king `P₁ = Pin.lean's Pp1` proved outright. Cross-family
  gates: A001168 6/19/63, A001207 11/44/186, A006770 20/110/638.

**Audit point**: `AuditOutworks.lean` — every headline theorem above has a
`#guard_msgs`-wrapped `#print axioms` (companion of `Grand/Audit.lean`),
so axiom drift fails the build. Full tree green 2026-07-30: 8615 jobs.

Integration renames (root-build name clashes, resolved in the new files;
king tree untouched): UpperBound's `shape` → `expShape` (Shape.lean owns
`shape`), Growth's `logSeq` → `negLogA` (ExpForm.lean owns `logSeq`),
Holes' `kingAdj_shift` → `kingAdj_small_shift` (Growth owns the
translation-invariance form), duplicate `kingAdj_symm`s dropped for
`Graph.lean`'s.

## Axiom audit

Conditional/partial tiers (k ≥ 4): pure [propext, Classical.choice,
Quot.sound]. Unconditional tiers additionally carry the native_decide axiom
exactly for the finitely many verified point/weight values they consume.
Shape/Peel/Separation themselves: no native_decide anywhere.

**Enforced, not advisory (2026-07-21):** every `#print axioms` in
`Grand/Audit.lean` is wrapped in `#guard_msgs` against the recorded expected
output, so any axiom-set drift FAILS the build (hostile-witness audit fix;
`docs/lean-hostile-witness.md`).

**Extended to the Shape/Peel chain (2026-07-30, AUDIT-2026-07-30 L3):** the
guards previously covered only the Grand results, so the sentence above
("Shape/Peel/Separation themselves: no native_decide anywhere") was the one
axiom claim nothing checked. `Grand/Audit.lean` now guards `shape_d`,
`shape`, `shape_production`, `production_int_all`, `d_rec`, `c_ident`
(standard axioms only) and `P1_closed`, `P2_closed`, `P3_pinned` (standard
+ their exact native leaf sets) as well. Unguarded advisory `#print axioms`
remain in `Series`/`Mu`/`MuRec`/`Staircase`/`ExpForm`/`Lead`/`PinGrand` —
those print but do not gate.

## What is proved vs out of reach (goal answer)

- The **shape** of every production formula (deg ≤ k polynomial × 3-power,
  onset n ≥ 2k+1, integer-valued on ℤ) is a THEOREM for all k — this is the
  part that was conjectural before this branch.
- The **degree and leading coefficient** are THEOREMS for all k
  (`Grand/Lead.lean`): deg P_k = k exactly and [n^k]P_k = 25^k/k!
  (`lead_coeff_25`, `expPoly_natDegree_eq`); `shape_lead` transfers both
  to any shape witness. Axioms: standard + the single `V_1_1`
  native_decide leaf.
- Explicit P_k: proved outright k ≤ 3; k = 4..18 proved modulo TWO
  real-swept banked cells per level (`P<k>_grand_of_banked`, Grand tier —
  supersedes the older Lagrange tiers, whose text is kept below for
  history). The former k = 12..16 PREDICTED residue is gone, and the
  exp-structure itself (`grand_form`) is unconditional.
- Historical (pre-Grand) tier status: k = 4..11 via k+1 banked points;
  k = 12..16 additionally required flagged PREDICTED values — the
  "extend the triangle to n = 49" upgrade path this implied is obsolete.
