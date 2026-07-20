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

## In progress

- `Peel.lean` (agent grinding): the three peeling bijections ⇒
  `d_rec` : d k H = 3·d k (H−1) + ΣΣ V·d (k−j) (H−1−ℓ)   (H ≥ k+2)
  `c_ident`: T (H+k) H = d k H + ΣΣ Vt·d (k−j) (H−ℓ)      (H ≥ k+1)
  The project's hardest step (x-renormalization round-trips).

## Remaining

- `Shape.lean` — strong induction on k over the recurrence ⇒
  T(H+k,H) = q_k(H)·3^H, deg ≤ k, onset H ≥ k+1 exactly; production form
  P_k(n)·3^(n−1−3k) for n ≥ 2k+1; integrality free at integer n ≥ 2k+1
  (stretch: all-ℤ via finite differences; stretch: leading coeff
  (V(1,1)/27)^k/k! — closes the k=12 shortfall). Brief staged.
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
