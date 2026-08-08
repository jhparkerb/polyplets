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
  - **k = 12..16 PARTIAL: DELETED 2026-07-31** (`Pk_pinned_of_partial`).
    Their beyond-banked hypotheses were the production polynomial's own
    PREDICTED values — a fabricated hypothesis provides zero
    cross-validation — and their conclusions were byte-identical to the
    Grand tier's `P<k>_grand_prod` (two real-swept anchors per level).
    The `Pp<k>` defs, degree lemmas and guards remain (Grand consumes
    them). Nothing referenced the deleted names.
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

**Supersession.** The `Pin.lean` tier map below is now historical: the
k = 12..16 PARTIAL tier is DELETED outright (2026-07-31; "kept for
cross-validation" was wrong — hypotheses fabricated from the polynomial
cross-validate nothing), and the k = 4..11 conditional tier's hypothesis
lists are replaced by the Grand tier's real-swept-only anchors. (The one
cell there flagged formula-generated, `T 31 20` at k = 11, has since
been really swept: a38 and a39 both swept H = 20 and agree with it
digit-for-digit — noted inline in `Pin.lean`.) Banked data now fully pins every wired
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
  height-blind canonical animals; agreement is at `n ≥ 1` — Lean's
  `a 0 = 0`, OEIS's `a(0) = 1`), `a_eq_sum : a n = Σ_{H=1..n} T n H`,
  the §9 strip-capture bound `strip_sum_le_a : Σ_{H≤10} T n H ≤ a n`
  (`n ≥ 10`), computable twin `ac`, native_decide anchors `a_1..a_6` =
  1, 4, 20, 110, 638, 3832 vs banked row sums. `a_6` costs ~700 s
  (5.9 GB is the whole-module peak; forces `Tc 6 6`); `a 7` infeasible
  (C(49,7) ≈ 86M subsets).
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

  **Conditional lower bound `6.22 < λ` (added 2026-07-31, "Lean ratchet").**
  `lambda_gt_of_banked (h : a 40 = 56749893611764175164545926946127) :
  (311/50 : ℝ) < lambda`, from `a_le_lambda_pow` at `n = 40` plus the exact
  integer comparison `311⁴⁰ < a(40)·50⁴⁰` and strict monotonicity of `x⁴⁰`
  on `[0, ∞)`. Standard three axioms — the banked value is a *hypothesis*,
  not a `native_decide` computation, in the `P<k>_grand_of_banked` style; the
  guard is in `AuditOutworks.lean`. `3.95` stays the unconditional figure
  (`a 6 = 3832` is the largest row Lean enumerates for itself).

  Two honest caveats, both load-bearing:

  - **Single-source hypothesis.** `a(40)` is a kink-engine-only value at the
    top of the table — the same grade as a(23)+ and the 11 kink-only Grand
    anchors above (see the anchor-provenance discussion): cross-ISA and
    cross-revision re-runs, but no second algorithm. The strip second source
    reaches H ≤ 14 only. So the theorem is conditional on a number, and the
    number has one algorithm behind it.
  - **Still weaker than the unformalized ladder.** The certified strip
    ladder gives μ₁₇ ≥ 6.543 (`results/strip-mu-certificates.md`, addendum
    2026-07-31; bracket 6.543 ≤ λ ≤ 9.3154) — but it is not formalized. `6.22` is
    near-sharp for *this* route: `a(40)^(1/40) = 6.22084…`, so `6.23` is
    false, and no single banked term can do better than 6.221.
- `IntCoeff.lean` (OW-4) — `factorial_smul_int_coeff` (deg ≤ k integer-
  valued ⇒ k!·coeffs ∈ ℤ, binomial basis via forward differences) and
  `production_factorial_int` (§6.1's "k!·P_k integral"). Standard axioms.
- `Symmetry.lean` (OW-7) — D₄/C₄ acting by apply-then-reanchor; the §7
  Burnside identities `free_eq`, `oneSided_eq`, `bilateral_eq` and
  `r90_vanish` (n ≢ 0,1 mod 4 ⇒ R90 = 0, affine quarter-turn argument),
  all standard axioms; anchors vs `results/sym_counts.txt` n ≤ 5 in-file
  (n = 6 — including the Hm/Dm 58/56 split — verified by the committed
  independent brute force `experiments/sym_brute_check.py` + log,
  2026-07-31; ~490 s/element to add in-tree); derived n = 4 spot checks
  Free/OneSided/Bilateral = 22/34/10, guarded.
- `Holes.lean` + `HolesUpper.lean` (OW-6) — hole machinery from scratch
  (rook components, `enclosed`, `SingleHole`), **`maxhole_lower`
  unconditional** (diagonal-frame family `hullBox ∖ boxHole`, card a+b+2
  for ALL a,b — no degenerate (a,b), no n = 5 special case; anchors
  n = 4..10 by kernel decide, zero native_decide), (I′) parity count +
  maximization unconditional, and Theorem 2's upper bound **conditional on
  the named `MoatBound`** hypothesis (`maxhole_upper`, `maxhole` =
  IsGreatest) — the discrete-Jordan step needs digital topology Mathlib
  lacks; substitute 1 refuted exhaustively (63,112 of the 104,727
  single-hole animals n ≤ 9, `experiments/maxhole_review_checks.py`),
  substitute 2 holds on all of them but is too weak by a counting
  argument (module doc has both). `MoatBound` itself: 0 violations on
  the same 104,727 animals. Finding: `boxHole a b` is rook-DISCONNECTED iff min(a,b) = 1
  and max ≥ 3 (multi-hole rings, invisible to the total-area checks of
  `results/maxhole-proof.md`).
- `Northcott.lean` (OW-8) — house-arrest finiteness: bounded degree +
  bounded house ⇒ finitely many algebraic integers (bridges Mathlib's
  2025 `finite_mahlerMeasure_le`; the claims audit's "Mathlib lacks it"
  is superseded). Both the finiteness form
  `finite_setOf_degree_le_of_house_le` (the closer match to the paper's
  step (iv)) and the brief's unboundedness form are proved. An earlier
  "step 5 needs the finiteness form, not bare unboundedness" divergence
  claim was a quantifier slip, refuted in the 2026-07-31 adversarial
  review (machine-checked); see the module doc's correction note.
- `Universal/` (OW-5, the Verbatim Wager) — **the diagonal law
  universalized**: `RowLocal` lattices (finite nonempty up-offset set D,
  b = |D|), abstract `PeelSystem` engine, full generic geometric port
  (Separation + the three peeling bijections), `universal_shape` /
  `universal_shape_production` / `universal_production_int_all` for EVERY
  row-local lattice, standard axioms. **Wager verdict: verbatim yes** —
  the only mathematical divergence is the width bound (`M·(n−1)`, since
  general lattices skip columns; the false-for-general-L lemma
  `exists_x_eq_of_cross` is replaced by a walk-length bound); the drift
  count `b` enters the geometry only at the three class-A peel sites, and
  the paper's p-adic integrality step is not needed (exact division,
  prime-agnostic — the king Lean proof already avoided it too). Generic
  weights are set-theoretic (no window enumeration), so the numeric
  recursion gates live at king only: `KingAgree.lean` re-derives king
  through a proved adjacency equivalence (recursions re-proved
  generically, zero new native leaves). Instances pinned: square
  `P₁ = 4X − 8` (ordinary polyominoes!), hex `P₁ = 9X − 15`, king
  `P₁ = Pin.lean's Pp1` proved outright. Cross-family gates (row sums of
  the generic computable `Tc`): A001168 6/19/63, A001207 11/44/186,
  A006770 20/110/638.

## Bui in Lean — the certificate upper bound (LANDED 2026-07-31, `Polyplets/Upper/`)

Formalization of the certificate side of the project's headline polyplet
upper bound `λ ≤ 9.3154` (`docs/proofs/polyplet-upper-bound.md`,
BREAKTHROUGH + Certificate-Squeeze; `experiments/king_bui.py`,
`experiments/king_certificate.py`). Three layers:

- **Layer 1 (unconditional, `Upper/Certificate.lean`)** — the abstract
  convolution-certificate machinery, standard axioms only:
  - `BuiSystem`/`Sat`/`Super` — the abstract single-free-cell casing system
    (`φ_T ≤ φ_{T'} + φ_{T'} * φ_D`, base types isolated) over any index
    type, with a rank measure making the `T'`-chain well-founded;
  - `BuiSystem.certSum_le` / `pow_mul_le` — the monotone-iteration bound:
    a nonnegative rational super-solution `F_x(u) ≤ u` dominates
    `x^n · φ_T n` (division-free, over ℚ; strong induction on the
    truncation order, inner induction on rank);
  - `lambda_le_of_pow_bound` — `a n ≤ C·y^n ⟹ λ ≤ y` via
    `lambda_tendsto` (`C^{1/n} → 1`);
  - `lambda_le_of_buiSystem`, `RatCert.lambda_le` — the assembled theorem
    for exported certificates: all side conditions (index bounds, rank
    descent, cleared-denominator super-solution inequalities
    `nums[a]·CD + nums[a]·nums[b] ≤ nums[i]·CD`) packed into one `Bool`
    the kernel evaluates.
- **Layer 2 (RD=2 instance, conditional, `Upper/BuiData2.lean` +
  `Upper/BuiRD2.lean`)** — the 185-type system and its exact certificate
  `x = 106251/10⁶`, exported fail-closed by `scripts/gen_bui_cert.lean.py`
  (asserts the banked x, re-runs the exact Fraction check, cross-checks
  `experiments/king_certificate.py` as an independent oracle, and
  pre-verifies the very integer rows Lean re-decides). `buiRD2_valid` is a
  **kernel `decide`** (~5 s, axioms `[propext]` — no `native_decide`);
  **`lambda_le_of_bui_rd2 (h : KingBuiSystemRD2Holds) :
  lambda ≤ 10⁶/106251` (≈ 9.4117)**, standard three axioms.
- **Layer 3 (RD=3 headline instance, conditional, `Upper/BuiData3.lean` +
  `Upper/BuiRD3.lean`)** — the 5930-type system at the banked
  `x = 2147/20000`: **`lambda_le_of_bui_rd3 (h : KingBuiSystemRD3Holds) :
  lambda ≤ 20000/2147` (≈ 9.31532)** — the Lean rendering of the project's
  headline `λ ≤ 9.3154`. The 5930-row check is past the kernel evaluator
  (`decide +kernel` killed at >10 min / >6 GB; the `List.getD` walks are
  quadratic in unary steps), so `buiRD3_valid` is a **`native_decide`**
  (~7 s) and the theorem carries standard three + that one native leaf.
  Evidence-grade note (in the hypothesis doc-comment): RD=3 recurrences
  were *not* separately brute-forced — valid by construction from the
  verified RD=2 system (a larger split window only adds known-empty cells).

What is unconditional: the certificate arithmetic (that `u` really is a
super-solution at `x`) and the entire analytic chain from super-solution to
`λ ≤ 1/x`. What is hypothesis: `KingBuiSystemRD2Holds` /
`KingBuiSystemRD3Holds` — that the actual king marked-corner counting
functions satisfy the exported system inequalities and the anchor
`a n ≤ φ_root n` (MoatBound-style named `Prop`s, `∃`-form, doc-comments
state the intended witnesses). Evidence behind them: brute-force
verification of every recurrence for all `n ≤ 9` at RD ≤ 2 (`king_bui.py`)
plus the by-construction over-count argument in the doc.
**The unconditional Lean bound remains `lambda_le : λ ≤ 3125/256`.**

RED tests (2026-07-31, scratch, not committed): decrementing one
certificate entry (`nums[0]` by `1/CD`) makes `decide` refute
`buiRD2.valid = true` and `native_decide` refute `buiRD3.valid = true` —
the checks are load-bearing. Regeneration is byte-identical for both data
files (RD2 additionally cross-checked against the
`experiments/king_certificate.py` oracle at generation time; RD3 oracle run
at first generation).

Build cost: `Upper/Certificate.lean` ~5 s, `Upper/BuiData2.lean` ~5 s
(kernel decide), `Upper/BuiData3.lean` ~7 s (native_decide),
hand modules ~3 s each — incremental full build +~20 s.

**Audit point**: `AuditOutworks.lean`, 62 guards (companion of
`Grand/Audit.lean`) — every headline theorem above, including the instance
`P₁` pins, the nine cross-family row-sum gates, `universal_shape_d`,
`lambda_lb`, `lambda_gt_of_banked`, the n = 4 Burnside spot checks,
`maxhole_lower_banked` and
`strip_sum_le_a`, has a `#guard_msgs`-wrapped `#print axioms`, so axiom
drift fails the build (the pin/rowSum/spot-check guards were added by the
2026-07-31 adversarial-review fix; before that they were asserted but
unenforced; `lambda_gt_of_banked`'s guard came with the Lean ratchet). Raw per-anchor theorems (`a_1..a_5`, the n ≤ 5 symmetry
anchors, the instance anchor cells) each carry their own native leaf and
are certified through the guarded consumers (`a_6` guarded as the
representative). Full tree green 2026-07-31 after the review fixes:
`polyplets/build-receipt-2026-07-31.log`.

**Adversarial review (2026-07-31)**: eight-reviewer sweep of the whole
campaign, `docs/reviews/outworks-adversarial.md` — zero critical findings,
zero statement-fidelity defects; the claim-hygiene fixes it mandated are
the ones recorded above.

Integration renames (root-build name clashes, resolved in the new files;
king tree untouched): UpperBound's `shape` → `expShape` (Shape.lean owns
`shape`), Growth's `logSeq` → `negLogA` (ExpForm.lean owns `logSeq`; the
`logSeq_*` lemma names were finished off as `negLogA_*` in the 2026-07-31
review fix),
Holes' `kingAdj_shift` → `kingAdj_small_shift` (Growth owns the
translation-invariance form), duplicate `kingAdj_symm`s dropped for
`Graph.lean`'s.

## v5 denominator law (LANDED 2026-07-31, `V5Denominator.lean`)

The corrected 5-adic denominator law of `results/v5-denominator-law.md`
(replacing the refuted `⌈v₅(k!)/2⌉` fit of `results/converse-sweep.md` §2),
kernel-checked against the pinned production data:

- `N1..N18` + `Pp<k>_data` — the numerator lists, certified identical to
  `Pin.lean`'s `prodPoly` arguments by `rfl` (transcription typos fail the
  build).
- `v5_law_all` — `min v₅(numerators of k!·P_k) = v₅(k!) − H(k)` at every
  level `k = 1..18`, `k = 11` included (plain kernel `decide`, NO
  native_decide).
- `ceil_fit_refuted` / `chat11` / `chat1` — the old fit's failure points
  as kernel facts.
- `eleven_no_harvest` — the k = 11 obstruction as a general multiset
  theorem: parts ≥ 2 summing to 11 ⇒ all multiplicities ≤ 4.
- `u1_seed` / `g1_seed` — `u₁ = P₁(1) − P₁(0) = 25`, `g₁ = P₁(0) = −45`
  tied to `Pp1`, with their valuations.
- `upper_half_law` — the exact upper-half profile law
  `v₅([nⁱ] k!·P_k) = 2(2i−k) + v₅(k!/((2i−k)!(k−i)!))` for `i ≥ ⌈k/2⌉`,
  every level `k = 1..18` (kernel decide; second pass).

Axioms: `v5_law_all`, `ceil_fit_refuted`, `eleven_no_harvest` carry
[propext, Quot.sound]; `u1_seed`/`g1_seed` add Classical.choice (norm_num).
No native leaves. NOT formalized (open item): the general-`k` lower bound
`ĉ_k ≥ v₅(k!) − H(k)` (Newton/multinomial over the boundary series G, Λ —
paper-level proof in `results/v5-denominator-law.md`; would need formal
finite differences + multinomial valuation bookkeeping over `ℤ[[y]]`).

## Staircase growth constant µ (LANDED 2026-08-06, `StairGrowth.lean`)

`results/hv-growth-sandwich.md` Lemma 3 and the Fekete step on top of it —
the authorized slice of Proposition 6 (`docs/lean-staircase-growth-brief.md`;
everything else about Proposition 6 stays a paper proof, deliberately).
Three files:

- `StairAnimals.lean` (sortie B1, 2026-08-06) — the combinatorial core:
  staircase king animals as a `List Col`, `join_valid`, `area_join`,
  `cut_join`, `join_injOn`. Footprint `[propext, Quot.sound]`, without
  `Classical.choice`: the join and the cut are computable.
- `Fekete.lean` — Fekete's ladder, once, for any sequence that is
  supermultiplicative, positive from `1` on, and under an exponential
  ceiling `c^k`. `negLog → subadditive → bddBelow → growth → tendsto →
  le_growth_pow → growth_le`. `Growth.lean`'s λ became the first instance
  (`polypletFekete`) in the same commit: `lambda`, `lambda_tendsto`,
  `a_le_lambda_pow`, `lambda_le` are now wrappers, with the identical
  footprints their `AuditOutworks.lean` guards already pinned, and
  `Growth.lean` is 53 lines shorter.
- `StairGrowth.lean` — the counting layer and the second instance.

**Unconditional, standard three axioms** [propext, Classical.choice,
Quot.sound], no native leaves, all guarded in `AuditOutworks.lean`:

- `Stair.M_supermul : M i * M j ≤ M (i + j)` — **Lemma 3** as a
  cardinality, for all `i` and `j`. `join_valid` puts the join in the class,
  `join_injOn` recovers the pair from the join alone once both areas are
  fixed, and `Finset.card_le_card_of_injOn` reads that as the inequality.
  This is what `make gate-middle-kingdom` cannot do: the gate checks
  supermultiplicativity on 700 computed terms, this is every `i` and `j`.
- `Stair.M_tendsto` — `µ = lim M(n)^{1/n}` exists.
- `Stair.M_le_mu_pow : (M n : ℝ) ≤ µ^n` for **every** `n` — Fekete's
  limit-is-supremum half, i.e. every banked term of the staircase sequence
  is a rigorous floor under `µ` rather than an approach to it.
- `Stair.mu_le : µ ≤ 4` — from the ceiling `M n ≤ 4^n`, which is proved by
  counting an explicit candidate `Finset` (`cand p n`, over-counting: height
  and offset ranges only) rather than by a bijection with compositions. The
  same `Finset` supplies the finiteness `M n` needs to mean anything.

**Conditional on a banked hypothesis** (the `lambda_gt_of_banked` shape —
the value enters as a hypothesis, not a computation, so still standard three
and no leaf):

- `Stair.mu_gt_of_banked (h : M 700 = 1736852…636729) :
  (15617/5000 : ℝ) < mu`, i.e. **`3.1234 < µ ≤ 4`** machine-checked.
  `M 700` is from `cpp/middle_kingdom_tm.cpp` in `stair` mode
  (`results/mk_stair_terms_n700.txt`); `M 700 ^ (1/700) = 3.1234045…`, so
  the floor is near-sharp for this `n` and still well below the measured
  `µ = 3.128943269730886…`. Same caveat as `lambda_gt_of_banked`: a
  single-source value, one transfer-matrix run, not independently
  reproduced.

NOT formalized, and not attempted: Lemma 2 (the stack bound), Lemma 1 (the
phase split), the geometric layer `IsHVCanonical`, Corollary 4, and the
squeeze `A_tendsto` — so Lean states `µ` for the **staircase** class, not
Proposition 6's "every class between staircase and HV-convex". Cost estimate
for the rest: 1700–2700 lines, most of it the geometric layer.

Those five are written down as typechecking contracts in
`Draft/Prop6Skeleton.lean`, which is outside the build (`defaultTargets =
["Polyplets"]`) and is the only file in the repo containing `sorry`. Its
header names each contract, the paper proof that establishes it
(`results/hv-growth-sandwich.md` Lemmas 1 and 2, Corollary 4 of
`results/middle-kingdom-phase3.md`), and the numeric check that backs it.
`make gate-middle-kingdom` reaches all five, but not equally: Lemma 2's bound
is verified outright to `n ≤ 120` with a RED control, the stack class and the
HV-convex predicate are brute-forced against the grid, while Lemma 1's
inequality is pinned only through the phase split it rests on and the squeeze
only through the measured `µ`. The header says which is which. `prop6` is
proved from the contracts, so its footprint carries `sorryAx` and says so.

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
