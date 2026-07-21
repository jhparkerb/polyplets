# Lean formalization status — production diagonal formulas P_0..P_16

Goal (2026-07-20, /goal active): Lean-prove the diagonal closed forms used by
the production engine (`diagonalCell`, k = 0..16); where full proof is out of
reach, prove as much as possible and state exactly what remains input.
Scope/route decisions: `PLAN.md`. Architecture (the peeling recursion,
replacing the paper's GF route): `DESIGN.md`. Pin inputs (production
coefficients + banked onset points, fail-closed generated): `pin-data.md`.

Build: `cd polyplets && lake exe cache get` (once) then `lake build`.
Green = only the intended `sorry`s listed below.

## Landed (sorry-free, green, all committed)

- `Defs.lean` — kingAdj, KingConnected, IsCanonical, T. (pre-goal)
- `Finite.lean` — crossing lemmas, width bound, finiteness, T as Finset.card.
- `RowProfile.lean` — row fibers, occupied-rows interval, step (b) one
  doubled row, (c-fwd), (d-local) for the old k=1 route. (pre-goal)
- `Compute.lean` — computable `Tc`, `Tc_eq_T`, decidable KingConnected via
  bounded closure; native_decide validation vs banked triangle (n ≤ 5 wall
  ~600k subsets; T(6,4), T(6,5) probed out-of-file, match).
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
  Same clean axiom footprint — no native_decide anywhere in the proof path.
  Leading-coeff stretch deferred; corrected target: P_k.coeff k = 25^k/k!
  (= production's "leading 25^j/j!"; the earlier δ-form in the brief was
  wrong, caught in review).

- `Weights3.lean` — j=3 light weight leaves (V(1,3)=81, Vᵗ(1,3)=9,
  V(2,3)=1860, Vᵗ(2,3)=307; 207 s one-off compile).
- `Pin.lean` — the endgame. Generic Lagrange pin lemma; recursion-evaluator
  value theorems (T(6,4), T(7,5) via d_rec/c_ident — no big enumeration);
  production polynomials transcribed by `scripts/gen_pin.py` from
  pin-data.md with per-point norm_num guards. Per-k results:
  - **k = 0, 1, 2 UNCONDITIONAL**: `P0_pinned`, `P1_pinned`/`P1_closed`,
    `P2_pinned`/`P2_closed`.
  - **k = 3**: `P3_pinned_of_heavy` (hypotheses = V 3 3 = 4778,
    Vᵗ 3 3 = 919, d 3 4 = 4687); `Weights3Heavy.lean` (OUT of default
    build) discharges them ⇒ unconditional `P3_pinned`. The V 3 3 check
    (~1.2·10⁸ candidates) stack-overflows as one native_decide, so it is
    chunked by leftmost cluster column into 15 per-file native_decides
    (`WeightsChunk*.lean`, partition lemma native_decide-free, histogram
    cross-checked by scripts/gen_v33_chunks.py). **BUILT 2026-07-21**
    (`lake build Polyplets.Weights3Heavy`, ~37 min wall: chunks ≤ 856 s
    parallel + assembly 1343 s) — `P3_pinned` is UNCONDITIONAL, axioms =
    standard + the chunk/leaf native_decide values.
  - **k = 4..11 CONDITIONAL-ON-BANKED**: `Pk_pinned_of_banked`, hypotheses
    = the k+1 banked onset T-values (results/triangle.txt, two-algorithm
    provenance).
  - **k = 12..16 PARTIAL**: `Pk_pinned_of_partial`, hypotheses = all
    banked points (12/10/8/6/4) + the 1/4/7/10/13 beyond-banked points at
    the production-PREDICTED values, explicitly flagged `-- PREDICTED` —
    these are the precisely-stated residue of what n ≤ 36 data cannot pin.
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
- `P<k>_grand_of_banked`, k = 1..16: the PRODUCTION polynomials
  (`orchestrator/sweep.go`, via `Pin.lean`'s `Pp<k>`) pinned for all
  n ≥ 2k+1 with hypotheses = **2 real-swept cells per level**
  (`T(2j+1, j+1)`, `T(2j+2, j+2)` for j = 4..16 — 26 anchors at k = 16,
  every one with H ≤ 18; levels ≤ 3 discharged from
  `P1_closed`/`P2_closed`/`P3_pinned`). Axioms: standard + `P3_pinned`'s
  heavy-k=3 native_decide set (V/Vt/d leaves + 16 CFGVchunk cards + light
  base enumerations).

**Supersession.** The `Pin.lean` tier map below is now historical (kept for
cross-validation): the k = 12..16 PARTIAL tier's flagged-PREDICTED
hypotheses are RETIRED — `P<k>_grand_of_banked` needs no beyond-banked
points — and the k = 4..11 conditional tier's hypothesis lists, which
included formula-generated cells (e.g. `T 31 20` at k = 11), are replaced
by real-swept-only anchors. n ≤ 36 data now fully pins every wired
diagonal; the "extend to n = 49" upgrade path is obsolete.

## Axiom audit

Conditional/partial tiers (k ≥ 4): pure [propext, Classical.choice,
Quot.sound]. Unconditional tiers additionally carry the native_decide axiom
exactly for the finitely many verified point/weight values they consume.
Shape/Peel/Separation themselves: no native_decide anywhere.

## What is proved vs out of reach (goal answer)

- The **shape** of every production formula (deg ≤ k polynomial × 3-power,
  onset n ≥ 2k+1, integer-valued on ℤ) is a THEOREM for all k — this is the
  part that was conjectural before this branch.
- Explicit P_k: proved outright k ≤ 3; k = 4..16 proved modulo TWO
  real-swept banked cells per level (`P<k>_grand_of_banked`, Grand tier —
  supersedes the older Lagrange tiers, whose text is kept below for
  history). The former k = 12..16 PREDICTED residue is gone, and the
  exp-structure itself (`grand_form`) is unconditional.
- Historical (pre-Grand) tier status: k = 4..11 via k+1 banked points;
  k = 12..16 additionally required flagged PREDICTED values — the
  "extend the triangle to n = 49" upgrade path this implied is obsolete.
