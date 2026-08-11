# Notary Lean — deferred simplify items (build-in-the-loop follow-up)

2026-08-10. From the pass-1 (Lean) simplify checkpoint over `simplified..HEAD`.
The **contained, low-risk** cleanups were applied in that pass (5-lemma
Finset-helper dedup `GapWalkColumns`→`GapWalkClosing`; dead `have`/unused
binders in `GapWalkPeel`/`GapWalkStacks`/`GapWalkExact`; `<;>` branch merges in
`KernelRoots`/`GapWalkRowVals`). The items below are real but were **deferred**:
each either introduces/moves a lemma (higher risk on freshly-gated proofs, and
each forces a ~multi-min re-verify build) or needs the exact Mathlib lemma list
confirmed against a build. Do them with the build in the loop, one at a time,
re-running `make gate-notary` per change — not as a blind batch.

## Cross-module de-private / hoist (removes true duplication)

- **`Kernel.sqrtCoef_succ`** (`KernelRoots.lean:132`) is reproved verbatim as
  `sqrtCoef_succ'` in **`DepthOneKernelPhi.lean:195`** and
  **`DepthOneKernelUnique.lean:353`** (~25 lines each; the Phi copy's own comment
  admits it). Fix: drop `private` on the `KernelRoots` original, delete both
  primed copies, point call sites at `Kernel.sqrtCoef_succ`. Highest line-count
  payoff — but touches the two heavy certificate modules.
- **`mem_states`** (`GapWalkCanon.lean:61`, public) is reproved as `mem_states'`
  in **`GapWalkStacks.lean:308`**. Both import `GapWalk.lean`, where `states` is
  defined (`:85`). Fix: state `mem_states` once in `GapWalk.lean` beside
  `states`; both modules reuse it. Touches 3 files.
- **`sum_eq_zero_of_forall`** duplicated in **`GapWalkExact.lean:83`** and
  **`GapWalkCanon.lean:139`** is Lean core's
  `List.sum_eq_zero_iff_forall_eq_nat.mpr` — confirm the core lemma name/sig
  against the build, then delete both and call it. (`sum_flatMap_pair` vs
  `sum_flatMap_pair'` are **not** mergeable — different RHS, `map (a+b)` vs
  `map a + map b`.)

## Local helper extractions (repeated inline blocks)

- **`GapWalkPeel.lean:148,159,171,183`** — `adj_u_tL`/`adj_v_tL`/`adj_u_tR`/
  `adj_v_tR` have byte-identical bodies → one private `adj_row_succ`.
- **`DepthOneKernelUnique.lean:227,264,300,320,885,922,958,978`** — inline
  `(8 : PowerSeries ℚ) ≠ 0` / `(512 : …) ≠ 0` proved 8×; extract
  `eight_ps_ne_zero`/`c512_ps_ne_zero` mirroring the file's existing
  `two_ps_ne_zero` (`:709`).
- **`KernelRoots.lean:280,301`** — `(4:PowerSeries ℚ)*X ≠ 0` derivation
  copy-pasted between `u1_lin`/`u2_lin` → one `four_X_ne_zero`.
- **`GapWalkEnds.lean:638,717`** — `((g:ℤ)=1 ∨ P) ↔ (g=1 ∨ P)` block twice →
  `cast_g1_or_iff`. Also **`:1260,1297,1703,1740`** — `have hrz : rowSize T
  ((ℓ:ℤ)+1) = 0` repeated per `hfiber`; hoist once after `hty`.
- **`GapWalkExact.lean:263,300`** — `jE_step`/`pE_step` share the `hJ`
  support-trim block (target flag never inspected) → one private lemma
  parameterized over the target state.
- **`GapWalkClosing.lean:338,432`** — `rw [show {3,4} = insert 3 {4} …,
  sum_insert, sum_singleton]` → `Finset.sum_pair (by decide)`.
- **`DepthOneKernelPhi.lean:185`** — `bbC_eq_sgn_aaC`: `rcases n with _|_|_|n`
  then identical `simp` in all four branches → `<;> simp [...]` (same merge
  already applied to `mk_aaC`/`mk_bbC` in `KernelRoots`).

## Structural (real refactors — only if the payoff is judged worth it)

- **`isStackI_*`/`isStackB_*` and `STKI_*`/`STKB_*` twins**
  (`GapWalkStacks`/`GapWalkPeel`) and the **`u1`/`u2` closing-equation pairs**
  (`GapWalkClosing`) are genuine duplication, but unifying needs abstraction
  over the stack-class predicate / kernel root — a structural change, kept in
  lockstep intentionally (`GapWalkClosing:760` docstring says do not edit the
  `colJ3_case`/`master_J` pair).
- **`DepthOneKernelPhi`** `sgnHom`/`scale3` → one `coeffScaleHom c`; and
  **`GapWalkColumns:684-714`** `coeff_2mul…coeff_12mul` → one `coeff_ofNat_mul`
  (touches ~9 downstream `simp only` sets).

## Build-cost (needs a build to confirm safe)

- **`StairAnimals.lean:6`** whole-library `import Mathlib` on an elementary
  list/`Nat` file with ~12 bare `simp` calls → narrow the import + `simp only`.
  (`Northcott.lean:6`'s full import is defensible — real algebraic-integer
  machinery.)
- Bare `simp` → `simp only [...]` across `GapWalkEnds`/`GapWalkExact`/
  `GapWalkCanon`/`KernelRoots`/`KernelSeries` (dozens): speeds elaboration but
  each needs its exact lemma list pinned against a build.

## Pass 2 (non-Lean) — observations deferred

From the pass-2 review over the durable non-Lean code (tests, `scripts/*.sh`,
`cpp/`, tooling). The contained fixes were applied (dead `import copy`,
`guess_algebraic` over-determined guard + `with open` in
`experiments/braw_from_data.py`; `tracked_markdown()` called once in
`tests/gate_citations.py`; dead `Func`/`kFuncsRect`/`kFuncsHex` deleted from
`cpp/perimeter_min.cpp`). Deferred:

- **`tests/gate_subgroup.py:44,150,173,193,199`** — five
  `subprocess.run(..., check=True)` reimplement `common.run`, but swapping
  changes the failure-path exception (`CalledProcessError`→`RuntimeError`), so
  not behavior-preserving; leave unless the gate's fail contract is revisited.
- **`cpp/severance_w1.cpp` + `cpp/severance_w3_families.cpp`** share ~80 lines
  (`die`/`add_checked`/`to_dec`/FNV-1a `KeyHash`/union-find/combination
  iterator) → a planned `cpp/severance_common.h`. Real refactor: scale-validated
  engines that differ load-bearingly (`int16_t c[20]` vs `int8_t c[8]`; w3 also
  has `mul_checked`).
- **FNV-1a byte hash written 4×** (`severance_w1`/`w3` `KeyHash`, `symtm`
  `SigHash` + `DmShard::rawHash`, the last two in one file) → one
  `fnv1a(const u8*, n)`. Hot-path hashers of validated engines — don't
  auto-apply.
- **`scripts/dalby_perimeter_defect_{k6,pool}.sh`** — byte-identical `MERGEPY`
  shard-merge heredoc → a planned `experiments/merge_defect.py`. Deliberately separate
  job records (one-shard-per-core vs worker-pool).
- **Probe scripts** (`gympie_j7_probe`, `gympie_square4_hullprobe`,
  `dalby_square4_deep`) open-code what `scripts/perimeter_min_only.sh` already
  parametrizes — **leave as-is** (each is a self-documenting job record with its
  own cost/rationale header); noted so no one adds a fourth copy.
- **`cpp/perimeter_min.cpp:572,602`** — the `# box … free:` line built twice →
  `emitBoxLine`; output contract the gate greps, so not mechanical.
- **`cpp/sym/symcount_fast.cpp:311`** — per-thread full `Counter` copy is
  intentional (independent read-only graph per worker); **do not touch**.

## Not touched (justified, do not "fix")

- Every `maxHeartbeats`/`maxRecDepth` bump in `DepthOneKernel{Sol,Phi,Unique}`
  and the `decide`/`native_decide` on `walkFamilies` sit on generated
  degree-25..40 certificates — proportionate, out of scope.
- `DepthAssembly`/`DepthOneConstants`/`DepthOneKernelSol` certificate blobs are
  generator output — as tight as the generator makes them.
