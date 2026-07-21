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

## In progress

- `Pin.lean` + `Weights3.lean` (agent): j=3 leaves, recursion-evaluator
  value theorems, Lagrange pin lemma, per-k production theorems
  (unconditional k ≤ 3 / conditional-on-banked k ≤ 11 / partial k = 12..16
  with explicit predicted-value residual hypotheses).

## Remaining
- `Pin.lean` — explicit P_k per k (Lagrange uniqueness
  `eq_of_degrees_lt_of_eval_finset_eq` + points):
  - k ≤ 2 unconditional (points native_decide-verified; T(7,5) via the
    proved recursion as evaluator, not brute force); k=3 attempt.
  - k ≤ 11: conditional on banked triangle values (all points in
    pin-data.md).
  - k = 12..16: banked points fall short by 1/4/7/10/13 (triangle ends at
    n=36) — partial pinning + explicit residual hypotheses; leading-coeff
    stretch would close k=12.
- `Diagonal.lean` — `T_n_nm1` (hcount sorry) and `T_n_nm2` (full sorry):
  to be re-proved from Shape+Pin; the old direct gadget route (steps c-rev,
  d-global, e) then optional/retired.

## Intended sorrys currently in tree

- `Diagonal.lean:50` hcount (old k=1 route), `Diagonal.lean:87` T_n_nm2.
