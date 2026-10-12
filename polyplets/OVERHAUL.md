# Lean overhaul — working list

Branch `lean-overhaul`, started 2026-10-11. Target: `Polyplets/Report.lean`
states every claim of `paper/technical-report.tex` and proves it from
standard axioms only; the L-paper modules (`Universal/`, `Upper/`,
`Stair*`) are held to the same standard. Ledger: `README.md`.

The standard (2026-10-12, from the question "what would mathlib or a
professional formalizer do"): no `native_decide`; computation by kernel
`decide` on definitions that reduce, or by reflection; no hand enumeration of
cases; validation facts out of the library proper; no duplicated
developments (generalize, do not copy); named-field structures instead of
positional conjunctions; minimal imports; no loose `#print axioms`; every
headline theorem guarded; docstrings free of campaign jargon and true.

## Queue A — the Lean behind the technical report

Easiest and most depended-on first. One commit per item.

- [x] A1. Imports (2026-10-12; `lake exe shake` still lists prunable
      imports and some dependency re-routings, left for a later pass). Replace `import Mathlib` (`Defs`, `StairAnimals`,
      `Universal/Defs`) and `import Mathlib.Tactic` (`Grand/Series`) by the
      `#min_imports` set; run `lake exe shake` and drop unused imports.
- [x] A2. Lints (2026-10-12: `#lint in Polyplets`, 934 declarations, 0
      findings after the six docstrings it asked for). Run Batteries' `#lint` over the whole tree (unused
      arguments, docBlame, simpNF, …); fix what it reports.
- [x] A3. Docstring hygiene (2026-10-12; the GD-n labels in `Universal/`
      go with A7). Undo the "shape → expShape" search-and-replace
      damage in `UpperBound`; strip campaign labels (tier 1/2, GF-3, GD-1,
      Phase B, OW-n, "anti-confabulation") and stale pointers
      (`docs/lean-record.md`, `AuditOutworks.lean`, `GRANDFORM-PLAN.md`,
      `PLAN.md`, `DESIGN.md`); delete `example : True := trivial` in
      `Grand/Series`.
- [x] A4. Loose `#print axioms` out of library modules; every headline
      theorem of the report and the L-papers gets a `#guard_msgs` guard in
      `Audit.lean` instead.
- [x] A5. Validation out of the library (2026-10-12): the kernel-decided cells, the
      numeric gates (`c_ident_check_*`, `d_mu_rec_check_*`,
      `T_staircase_check_*`, `shape_check_T_*`, the `Tc` examples) move to
      one `Polyplets/Checks.lean` that the root builds and nothing imports;
      what a proof actually needs (`T_1_1`, `T_3_2`, `T_4_3`, `V_1_1`,
      `d_0_1`) stays where it is used.
- [x] A6. Dead code (2026-10-12: 21 declarations; `#lint` has no unused-
      declaration check, a usage scan found them) and restatements: `fixCountC`/`fixPred`/
      `decidableIsCanonicalAnimal` (no consumer since the anchors went),
      `nu_zero'`, `xNorm_def'`, `rowSize_union_left`, whatever `#lint` and
      a usage grep show unused.
- [x] A7 (2026-10-12; `King.lean` is the instance, `DiscreteCalculus.lean` the
      polynomial lemmas, 2,700 lines gone). One development, not two: the king tree (`Graph`, `Finite`,
      `RowProfile`, `Separation`, `Weights`, `Peel`, `Shape`) becomes the
      `kingLattice` instance of `Universal/` (`KingAgree` already proves the
      objects agree definitionally), and `AbstractShape`'s copy of `Shape`
      is the only shape proof. Deletes ~2,400 duplicated lines and the GD-1/
      GD-2/GD-3 scaffolding (`KingShapeD` transcriptions, `kingSystemGeneric`,
      the `king_*_via_universal` re-derivations). The report cone then runs
      through `Universal/`.
- [x] A8 (2026-10-12). Structures with named fields for `IsCanonical`,
      `IsCanonicalAnimal`, `Anchored`, `IsVConfig`, `IsVtConfig` (after A7,
      so it is done once); replace the ~200 positional projections
      (`hS.2.2.2.2.2.1`) by field names.
- [x] A9 (2026-10-12: `Universal.translate` with `adj_add`, `conn_image`,
      `conn_translate` in `Universal/Defs`; the king forms in `Defs`; `shift`
      and `shiftBy` are abbreviations of it, `expShape` is `translate
      (-anchor S)`). One translation toolkit: `shift`/`shiftCell` (`Peel`), `shiftBy`
      (`Growth`), the `p + t` images of `Symmetry`, the `sub` maps of
      `UpperBound`, with cardinality, membership, adjacency and connectivity
      invariance proved once.
- [x] A10 (2026-10-12). `Grand/Series` on `PowerSeries ℚ`: `conv a b = coeff (mk a * mk b)`,
      `eps = 1`, `convPow = (·)^ℓ`; associativity, commutativity and the
      collapse lemma come from Mathlib instead of a 40-line sigma bijection.
- [x] A11 (checked 2026-10-12: Mathlib has the forward-difference calculus but no integer-valued-polynomial theorem; the local lemma stays). `int_valued_of_consecutive` from Mathlib's forward differences
      (`fwdDiff`, `shift_eq_sum_fwdDiff_iter`) instead of the 80-line
      home-grown induction; likewise `exists_poly_sum_Icc` if Mathlib's
      Faulhaber/`fwdDiff` material covers it.
- [ ] A12. A counter that reduces in the kernel: `Tc`, `d`, `V`, `Vt`,
      `fixCount` over `Fin`-indexed cells and `Bool` predicates (no
      `Finset (ℤ × ℤ)` powersets in the evaluation path), proved equal to
      the definitions; then the validation cells that `native_decide` used to
      carry (rows ≤ 6 of `T`, `a 3 … a 6`, the j ≤ 3 weights, the symmetry
      anchors n ≤ 5) return to `Checks.lean` as kernel facts, and
      `P2_closed` returns unconditional.
- [x] A13 (2026-10-12). `Separation.reachable_seg_aux`: one proof for both cut lines
      instead of two 30-line mirror-image branches.
- [x] A14 (2026-10-12: `IsConfig L cap ℓ j` in `Universal/Weights` with
      `IsVConfig = IsConfig 1`, `IsVtConfig = IsConfig 0`; `peel cap H`,
      `cluster_facts`, `peel_mem_and_glue`, `glue_mem_and_peel`, `card_class`
      in `Peel`, with `card_classB`/`card_classC` as the two instances; 405
      lines gone). `Peel`: classes B and C share one peel/glue pair
      parametrized by whether a walk cell caps the cluster, instead of two
      ~350-line copies.
- [x] A15 (2026-10-12: `D4 = DihedralGroup 4`, `C4 = Multiplicative (ZMod 4)`
      through `rotHom`; the action is built from one quarter turn and one
      mirror). `Symmetry`: `DihedralGroup 4` from Mathlib in place of the
      hand-rolled `D4` and `C4` tables.
- [ ] A16. `SymmetryRatioClaim` as a theorem, conditional on the banked
      a(40): encode a symmetric animal by its axis cells and the components
      of one half, bound the count by `a_le_lambda_pow` and the components,
      and beat it with `lambda_gt_of_banked`; needs the encoding tight enough
      that `λ ≤ 12.2` suffices, or `lambda_le_of_bui_rd3` (9.3154) from
      Queue B. Last: it is the only item that is new mathematics.

## Queue B — the Lean behind the L-papers

- [x] B1. `native_decide` in the restored modules (2026-10-12: `RatCert`
      tables are balanced `NatMap` trees, `buiRD3_valid` is `decide +kernel`
      in 11 s; the hex and square `P₁` pins take `T(4,3)` as a hypothesis) (18 sites in
      `Universal/{King,Hex,Square}`, `buiRD3_valid`): kernel-decide what
      closes under the guard, delete the rest with their consumers, and make
      `RatCert.valid` kernel-checkable (iterate the three lists together
      instead of `List.getD` index lookups, so the 5930-row check is linear
      in the kernel). Must precede the next commit: `make lean` greps for
      `native_decide`.
- [x] B2. Pointers: `README.md` lists `Universal/`, `Upper/`, `Stair*` as
      live again with the L-paper each supports; `docs/lean-environment.md`
      counts; `StairGrowth`'s `docs/lean-record.md` reference.
- [x] B3. Imports, lints, docstrings, loose `#print axioms`, guards for
      these modules (A1–A4 applied to `Universal/`, `Upper/`, `Stair*`).
- [x] B4 (2026-10-12, with A7). `Universal/Compute.pin` duplicates `Pin.pin`;
      `Universal/Peel` duplicates `Peel`.
- [x] B5 (2026-10-12: regenerated RD=3 against the oracle, 0 diff lines; RD=2
      likewise). `Upper`: the `RatCert` data files were converted in place
      (`scripts/bui_lists_to_trees.py`); `scripts/gen_bui_cert.lean.py` emits
      the same format but has not been rerun against the oracle; regenerate
      and diff.
- [x] B6 (2026-10-12: `join_valid` and `cut_join` share `Valid.exists_cons`,
      `validFrom_of_valid` and `validFrom_join_step` instead of two copies of
      a `match` on `Valid`; the structural recursions stay). `StairAnimals`:
      `cut`/`join` on `List (ℕ × ℕ)` is fine; replace the `match … with`
      proofs by structural induction where `#lint` or readability asks.

## Done

- `Report.lean` drafted and in the root build (2026-10-11).
- `LeadingCoeff.lean`: leading coefficient 25^k/k!, and P_k fixed from rows
  2k+1 … 3k (2026-10-11).
- `Grand/PinAll.lean` replaces `Grand/PinGrand.lean` (2608 generated lines →
  ~330): one `mu_step`, one `grand_step`, a 15-level climb from
  `BankedAnchors` (2026-10-11).
- Option A (2026-10-12): levels 1–3 take their two onset cells as hypotheses
  like levels 4–18, so `BankedAnchors` is 36 cells and `Weights3Heavy` leaves
  the Report cone. Every `Report.lean` theorem is on
  `[propext, Classical.choice, Quot.sound]` alone.
- Delete outside the Report cone (2026-10-12, third checkpoint): 60 modules,
  24k lines; `Pin.lean` cut to the polynomials, the pin lemma and
  `P1_closed`. Reversed the same day for the L-paper modules `Universal/`,
  `Upper/`, `StairAnimals`, `StairGrowth` (restored from 697f376); the rest
  (GapWalk/DepthOne/Kernel, Holes, V5Denominator, Northcott, IntCoeff,
  ExpForm/Lead, Weights3Heavy and chunks, ComputeBridge, Diagonal, Sanity,
  AuditOutworks, Draft/) stays deleted; `README.md`'s "Removed" table says
  what each proved.
- `native_decide` burned down to zero in the Report cone (2026-10-12):
  14 cells close in the kernel under 3.5 GB and are `decide +kernel`; the
  rest needed 6–9+ GB and were deleted with their consumers.
- Ledger fold (2026-10-12): `PROOF-STATUS.md`, `DESIGN.md`, the old
  `README.md` and `docs/lean-record.md` are one file, `README.md`.
- `make lean` (2026-10-12): `sorry` and `native_decide` greps, then the root
  build; axiom footprints are the `#guard_msgs` in `Polyplets/Audit.lean`.
