# Adversarial review — the Outworks Lean campaign

2026-07-31, at master `2812cca` (the Outworks merge). Eight Opus reviewers, one
per module cluster, each briefed by the supervising session and armed with
`lake env lean` probes against the compiled library; the supervising session
cross-verified the load-bearing findings (including re-running the Northcott
refutation probe). Ground truth: the eight execution briefs
(`polyplets/briefs/OW*.md`), `polyplets/OUTWORKS-PLAN.md`, and
`polyplets/PROOF-STATUS.md` §"Outworks — second campaign". The tree was
verified green locally before review (`lake build --no-build`: all 8615 jobs
up-to-date at HEAD, so every `#guard_msgs` gate passed as built).

Since the proofs are kernel-checked, the review attacked what the kernel does
not guarantee: statement fidelity, definition drift, the trusted base
(native_decide inventory, guard coverage, option bumps), brief compliance,
PROOF-STATUS accuracy, and proof engineering. No repo file was modified by any
reviewer; all probes ran from scratch files outside the tree.

## Verdict

**The mathematics survives adversarial review intact. Zero CRITICAL findings;
zero statement-fidelity defects in any headline theorem.** Every pinned
definition and deliverable statement matches its brief (most
character-for-character), every anchor value matches the banked data, every
measured axiom footprint matches its advertised form, and the king tree is
untouched (0 deletions across the merge range; only the root import file and
PROOF-STATUS changed among pre-existing files).

The MAJOR findings are all claim-hygiene defects: guard coverage falls short
of what PROOF-STATUS and the OW-5 brief claim; one "verified out-of-file"
assertion has no artifact behind it (a recurrence of the exact pattern the
2026-07-21 hostile-witness audit fixed); and one documented "divergence"
finding in Northcott is itself mathematically false and has propagated into
PROOF-STATUS.

## MAJOR findings

### M1. Guard coverage is materially short of the blanket claim

`PROOF-STATUS.md` ("Audit point": *"every headline theorem above has a
`#guard_msgs`-wrapped `#print axioms` … so axiom drift fails the build"*) is
false, and OW-5's Done criteria ("guards added for AbstractShape's four
deliverables and each instance P₁") are unmet on both halves.
`AuditOutworks.lean` has 28 guards; unguarded despite being advertised
headline content or brief-mandated:

- `square_P1_pinned`/`square_P1_closed`, `hex_P1_pinned`/`hex_P1_closed`,
  `king_P1_pinned_via_universal`/`_king_form`/`king_P1_closed_via_universal`
  — the bolded instance pins (only the polynomial identity `kingP1_eq_Pp1`
  is guarded, which certifies nothing about any enumerated cell);
- the nine cross-family gates `{square,hex,king}_rowSum_{3,4,5}`;
- `universal_shape_d` and the four `PeelSystem.*` deliverables (three are
  covered by the instantiated `universal_*` guards; `universal_shape_d` by
  nothing);
- `lambda_lb` (named by the OW-2 brief and gate G-C; only the derived
  `lambda_gt` is guarded — mitigating: `lambda_gt` is proved *from*
  `lambda_lb`, so drift propagates into the guarded footprint);
- the OW-7 n=4 spot checks `Free_4`/`OneSided_4`/`Bilateral_4` and all 20
  symmetry anchors ("anchors carry [the native leaf] exactly" is enforced
  nowhere);
- `maxhole_lower_banked` (the theorem that ties the Holes construction to
  banked M(n)) and `strip_sum_le_a`.

Aggravating: `AuditOutworks.lean`'s own header records footprints for
`lambda_lb`, the n=4 spot checks, and the instance pins as if guarded. Every
asserted footprint was **re-derived by probe and found correct** — the claims
are true, just unenforced; nothing fails the build if they drift.

Also: guards were mutation-tested (a falsified expectation fails the build,
exit 1) and `AuditOutworks.lean` transitively imports all 23 new modules, so
the guards that do exist genuinely fail closed.

*Disposition:* add the missing guards (the instance-P₁ and rowSum set at
minimum), or rewrite the PROOF-STATUS sentence and the audit header to name
the representative-guard policy explicitly (as OW-1 already does for `a_6`).

### M2. Symmetry's "n = 6 verified out-of-file" is prose with no artifact

`Symmetry.lean:74-79` and `PROOF-STATUS.md` claim the n=6 anchors (including
the Hm/Dm 58/56 split) were "confirmed by an independent brute force …
2026-07-30". The commit touched exactly one file; no script, no output, no
results note exists anywhere in the repo (`scripts/` contains only
engine-side tools — the *source* of `sym_counts.txt`, hence not independent).
Nothing distinguishes "confirmed" from "asserted". This is the exact pattern
the hostile-witness audit forced in-tree as `ComputeBridge.lean`.

Related inconsistency: the module doc prices the check at ~700 s/element
(misattributed — that figure is `Sequence.lean`'s whole-module `ac 6` cost),
PROOF-STATUS at ~490 s/element. A reviewer measurement (n=5 anchor: ~11 s
net for C(25,5), scaled ×36.7 to C(36,6)) puts ~490 s in the right ballpark
— i.e. three elements ≈ 25 min, which also weakens the "out of budget"
justification.

Exposure, honestly stated: the in-file anchors stop at n=5 where Hm and Dm
are numerically identical, so an h/d-mirror swap would pass every in-file
anchor — but the reviewer verified the conventions are pinned by *proof*,
not anchor (`toFun_mul` forces the multiplication table to be composition of
the eight actual linear maps; the mirror classes are decidably distinct
conjugacy classes; the point maps match the paper's wording), and every
published quantity is H/D-symmetric — no artifact anywhere (Lean, banked,
OEIS) distinguishes the 58/56 split, and nothing published changes if
swapped. The defect is claim hygiene, not mathematics.

*Disposition:* land the three n=6 anchors in-tree (~25 min build cost), or
commit the brute-force script + output under `experiments/`, or strike the
sentence and state "not verified in-tree past n = 5". Fix the cost figure.

### M3. Northcott's flagged "divergence worth a paper edit" is mathematically false

`Northcott.lean:46-57` claims step 5 of the non-D-finiteness argument needs
the finiteness form `finite_setOf_degree_le_of_house_le`, because "bare
unboundedness does not contradict [step 5] — the offending H could be one of
the r exceptions". That is a quantifier slip: step 5 makes the exceptional
set *finite*; degrees on a finite set are bounded; unboundedness at
`d = max(D, bound)` lands in the exceptional set above its own bound —
contradiction. Verified twice by compiled Lean probes (reviewer's probe
re-run independently by the supervising session: clean). Additionally, the
paper (`polyplets-report.tex` §9.1) never contained the "all but at most r
heights" phrasing being critiqued — its step (iv) already states the
finiteness form — so the "paper edit" has no target; the critiqued "step 5"
exists only in the condensed summary in `results/anisotropic-not-dfinite.md`.

The false necessity claim is propagated verbatim into `PROOF-STATUS.md`
("needs the FINITENESS form …, not bare unboundedness").

**The Lean itself is fine**: `finite_setOf_degree_le_of_house_le` is
correct, strictly stronger than the unboundedness form (which is derived
from it), and a closer literal match to the paper's (iv). Only the necessity
claim and the "divergence" framing are wrong.

*Disposition:* rewrite the module-doc note as "stronger form proved; matches
the paper's (iv) more literally" and delete the necessity clause from
PROOF-STATUS (and from the campaign follow-ups list).

## MINOR findings

Grouped by theme; file:line detail preserved where actionable.

**Trusted-base documentation.**
- The campaign-wide convention text ("axioms = standard three plus
  `Lean.ofReduceBool` exactly where allowed" — OUTWORKS-PLAN, several
  briefs, `Sequence.lean:284`, `KingAgree.lean:36`) is stale for this
  toolchain: v4.31.0 `native_decide` emits a per-declaration opaque axiom
  (`<thm>._native.native_decide.ax_1_1`); `ofReduceBool` appears nowhere.
  The guards record the real names, so enforcement is honest — but the
  trusted base grows linearly with anchors (e.g. `Free_4` carries five
  leaves), which no doc states.
- No build receipt exists for the current tree: `build-receipt-2026-07-30.log`
  covers the pre-Outworks 8592-job build at `7a62883`; the 8615-job claim
  lives only in PROOF-STATUS prose — a literal recurrence of the defect the
  receipt mechanism was created to fix (AUDIT-2026-07-30 L8). Regenerate at
  HEAD before publish.
- `lakefile.toml` never sets `autoImplicit = false` (core default true;
  `relaxedAutoImplicit = false` only). A typo'd variable in a *statement*
  can silently become a quantified implicit. Pre-existing config, not a
  campaign regression; all 34 pinned interface statements were spot-checked
  clean. Consider flipping it.
- `import Mathlib` (whole library) in `Northcott.lean:6` and
  `Universal/Defs.lean:6` versus the plan's "minimal imports" — the latter
  is the root of all 14 Universal modules, a large share of the build
  closure.

**Holes (OW-6) — documentation vs the improved construction.**
- The landed diagonal-frame family (`hullBox ∖ boxHole`, card a+b+2 for ALL
  a,b) is a genuine, *documented* improvement over the brief and the python
  family — but `results/maxhole-proof.md` and paper §8 still carry the
  now-known-false unqualified claim that the 4-neighbour ring "has exactly
  a+b+2 cells" (it has a+b+1 when min(a,b)=1 with max even — measured over
  all 144 pairs a,b ≤ 12) and is a single-hole witness (false for
  min(a,b)=1, max ≥ 3 — the rook-disconnection finding, which a reviewer
  re-proved formally in Lean). The optimizing split provably never touches
  the bad set. Paper is read-only: flagged here, not edited.
- `HolesUpper.lean:56-59`: the refuting counterexample names the wrong
  anti-diagonal level (the 3×3 ring misses u=0 and u=2, not u=1 — measured).
- The substitute-refutation statistics (8375/1375/4321) exist nowhere but
  the module doc — no script, no results file; and PROOF-STATUS's "both
  cheap substitutes measured-refuted" is wrong for substitute 2 (it *holds*
  on the sample; it is refuted by a counting argument).
- `Holes.lean:37-41` "including the (2,1) case" understates the divergence
  set (every min=1, max-even pair).
- `private abbrev rookStep` leaks into two public signatures
  (`boxHole_rook_connected`, `ringAnimal_singleHole`) as an inaccessible
  name.

**Universal (OW-5) — prose looseness around a sound core.**
- The nine cross-family rowSum gates are theorems about the computable `Tc`
  only: `Tc_eq_T_of_M_le_one` is never applied to them, and `T L n H = 0`
  for `H > n` is asserted in a doc-comment but proved nowhere — so the
  advertised reading "row sums = A001168/A001207/A006770" is two short
  lemmas away from being a theorem (a reviewer compiled the bridge for the
  square n=3 case). As build gates on the generic geometry they are fully
  effective.
- The "out-of-sample corroboration" examples in `Square.lean:162-167` /
  `Hex.lean:147-151` never reference the `T_*_5_4` anchor theorems they
  claim to confront — each would compile unchanged if the anchor said 13.
  A one-line `rw [← T_*_5_4]` makes them enforcing (compiled by probe).
- `King.lean:118-120` `gd3_Tc_agrees` docstring claims a two-enumerator
  computational cross-check; the proof is the definitional bridge. The
  genuine two-enumerator check exists (distinct native leaves,
  `T_king_3_2._native…` ≠ `T_3_2._native…`) — the docstring points at the
  wrong theorem.
- PROOF-STATUS wording: "the only parameterization is the width bound"
  understates (b enters at the three class-A sites in Peel — the file's own
  doc is accurate); "King re-derived definitionally" is an omega case-bash
  plus rewrites, not `rfl`; the noncomputable-weights deviation (generic
  V/Vt not window-enumerated, so the recursion identity gates are king-only)
  is documented in the module but invisible in PROOF-STATUS; the "p-adic
  step not needed" finding is inherited from the king proof (Shape.lean
  already avoided it), not an OW-5 discovery.
- `Compute.lean:20-22` misstates which named lattices have reach 1 (the
  five-neighbour `Icc (−2) 2` also has M = 2).
- `Square.lean:38-39` / `Hex.lean:34-35` "everything else is
  standard-axioms" — the P₁ pins correctly inherit the two anchor leaves;
  reword to "introduces no further native_decide".
- Dead code: `Universal/Finite.lean:62` `exists_adj_cross_of_reflTransGen`,
  `Universal/Peel.lean:365` `rowSize_union_left` (zero uses); stale "king"
  wording at `Universal/Peel.lean:382,438`.
- No lattice with M > 1 has any in-Lean numeric corroboration (computable
  twin gated at M ≤ 1) — proof-only coverage for exactly the class that
  forced the width-bound divergence; scope note worth recording.

**Growth (OW-2).**
- Spec-of-record drift: two approved-in-review simplifications (self-anchoring
  double-lift concatenation instead of `reanchorY`; cut recovery by sInf
  minimality instead of the uniqueness argument) are disclosed in the module
  doc and commit but the brief was never updated.
- `lambda` prints as `Real.exp (-logSeq_subadditive.lim)` while
  `Polyplets.logSeq` is a live, unrelated Grand-tree declaration — the
  three `logSeq_*` lemmas are about `negLogA`; PROOF-STATUS's "rename"
  claim covers only the def. Rename `negLogA_*`.
- `a_supermul`'s docstring justification for the unused hypotheses is wrong
  (at m=0 the RHS is not 0), though the underlying claim is right (probe:
  the hypothesis-free version is provable). The statement correctly keeps
  the brief's hypotheses.
- Very generic top-level names in namespace `Polyplets` (`bar`, `concat`,
  `cutAt`, `maxX`, …) — no clash today; landmine.
- Context note: the machine-checked bracket 3.95 < λ ≤ 3125/256 is strictly
  weaker on both sides than the paper's §3 bracket (5.828 ≤ λ ≤ 9.3153,
  deliberately out of Lean scope); paper text must not cite `lambda_gt`/
  `lambda_le` as the §3 bounds.

**Sequence/UpperBound (OW-1/OW-3).**
- Rename-corrupted docstrings in `UpperBound.lean` (":68 the successor
  expShape", ":48 a expShape", five sites) from the mechanical
  shape→expShape rename.
- Brief name `card_common_neighbours` doesn't exist (the content landed as
  two kernel decides, `countP_scanPos_origin`:204 and
  `offsetFar_count_le`:218); `height_le_card` doesn't exist (replaced by
  the strictly stronger unconditional pair `one_le_heightOf`/`heightOf_le`).
  Both undocumented deviations, both benign; the audit header and OW-3
  brief still cite the phantom name.
- PROOF-STATUS attributes "5.9 GB" to `a_6` alone; the module doc says it
  is the whole-module peak.
- `strip_sum_le_a` requires n ≥ 10 (brief-exact) while the paper §9 says
  "for any n"; the lemma is true for all n ≥ 1 — pure slack. It is also
  absent from PROOF-STATUS entirely (under-claiming).
- `a 0 = 0` vs OEIS A006770's a(0) = 1: agreement is n ≥ 1 only; worth one
  clause where "A006770" is claimed.

**IntCoeff/Northcott (OW-4/OW-8).**
- `deltaPoly_natDegree_le` duplicates the taylor argument still inline in
  `Shape.lean` (the brief's "reuse" and "don't touch Shape.lean"
  instructions conflicted; the safer was chosen); the module doc's
  "hoisted" wording implies a replacement that didn't happen.
- Kronecker is credited (module doc + PROOF-STATUS "Northcott/Kronecker
  finiteness") but never used; and paper §9.1 attributes the
  degree+house-finiteness step to Kronecker when it is Northcott's theorem
  — citation check before publication (paper read-only; flagged only).
- `binomQ` docstring asserts degree/leading-coefficient facts the file
  never proves (both true; probe-verified).
- `factorial_smul_int_coeff`'s Q has no stated degree bound;
  `production_factorial_int` is an ∃ with no uniqueness lemma tying its P
  to `Pin.lean`'s concrete `Pp1` — both one extra line for a downstream
  citation, neither demanded by the brief.

## Notable positive verifications (what "clean" means here)

- **OW-3's exploration injection** verified end-to-end: the re-anchoring
  fix (`expShape` + `expShape_injOn`) is sound and honestly documented; the
  5n budget invariant is correct and *sharp* (exhaustive replay over every
  canonical animal n = 3,4,5 — 20/110/638 distinct codes, zero collisions,
  max considered = exactly 5n); the ratio polynomial matches an independent
  sympy expansion.
- **MoatBound is exactly the paper's (II′)**, weaker-never-stronger than
  the paper-proved lemma (extra KingConnected/SingleHole hypotheses), and
  was exhaustively tested: 0 violations over all 104,727 single-hole king
  animals with n ≤ 9, tight on the box rings — non-vacuous and plausibly
  true. The rook-disconnection finding was independently re-proved in Lean.
- **The verbatim wager verdict stands**: `PeelSystem` has no hidden
  king-only hypotheses (probed: exotic lattices `D = {7}`, `{−2,0,2}`,
  `Icc (−2) 2` all instantiate every universal theorem with no side goals);
  normalized diffs show Separation ported with *zero* proof-body divergence
  and Peel with exactly the three class-A hunks plus the width bound; the
  generic integrality proof is genuinely prime-agnostic; d_rec/c_ident
  onsets did not drift; the GD-1/GD-3 statement identity with Shape.lean
  and Pin.lean is definitional (`rfl`-provable Prop equality).
- **Symmetry's group theory is real**: D₄/C₄ group axioms proved, action
  laws proved (`one_smul`/`mul_smul` via the reanchor composition chain),
  `Bilateral` is genuinely "orbits with a mirror-fixed representative" (not
  a tautological half-sum), `bilateral_eq` is a genuine double count, and
  the computable path independently reproduces a_1..a_4 through a different
  enumeration. Free/OneSided/Bilateral(4) = 22/34/10 match the OEIS files.
- **λ is pinned**: `lambda_tendsto` is the genuine rpow-form limit, so
  uniqueness of limits characterizes `lambda` independently of the Fekete
  plumbing (probe compiled); 3.95 = 79/20 exactly, 3.95⁶ < 3832 by
  norm_num; concatenation geometry validated on concrete instances.
- **Trusted base globally**: zero sorry/axiom/partial/unsafe/
  implemented_by/extern/opaque/macro tricks/maxHeartbeats/maxRecDepth/
  nolint across all 23 new files (the only set_option in the campaign is
  the nativeDecide *style linter*, five sites); native_decide inventory
  exactly matches the brief allowances file-by-file (44 total: 6 Sequence,
  20 Symmetry, 18 instance anchors; zero in UpperBound, IntCoeff, Holes,
  HolesUpper, Northcott, KingAgree, and all of Universal phases A/B);
  Holes anchors are kernel decide (`maxhole_lower_anchors` = [propext]
  only); guards mutation-tested fail-closed; root import closure complete;
  king tree byte-identical; toolchain/manifest pins untouched; all 34
  pinned interface names exist with the intended elaborated statements.
- **Anchors vs banked data**: all Sequence anchors = triangle.txt row sums;
  all symmetry anchors = sym_counts.txt columns; Holes anchors = maxhole.txt
  M(4..10) (and the single-hole/multi-hole distinction was closed by brute
  force for n ≤ 9); instance anchors and row sums re-derived by two
  independent reviewer enumerators and checked against A001168/A001207/
  A006770 and triangle.txt, including out-of-sample law checks to n = 8.

## Fixes applied (2026-07-31, same day, this session)

Everything below was applied immediately after the review and the tree
rebuilt green (8615 jobs, all guards passing); the paper items remain flags
only (paper is read-only).

- **M1**: 23 guards added to `AuditOutworks.lean` (51 total) — the instance
  `P₁` pins, the nine row-sum gates, `universal_shape_d`, `lambda_lb`, the
  n = 4 Burnside spot checks, `maxhole_lower_banked`, `strip_sum_le_a`;
  header rewritten to match; PROOF-STATUS audit paragraph now describes the
  enforced state; fresh build receipt `build-receipt-2026-07-31.log`.
- **M2**: independent brute force committed as
  `experiments/sym_brute_check.py` + log — all four columns n = 1..6
  reproduce `results/sym_counts.txt` exactly, including the 58/56 split,
  and the derived free/one-sided/bilateral match A030222/A030233/A030234;
  Symmetry module doc now cites it, with the corrected ~490 s/element
  figure.
- **M3**: Northcott module-doc note rewritten as a correction (necessity
  claim deleted, refutation recorded); PROOF-STATUS bullet corrected;
  unused Kronecker credit trimmed.
- Holes set: `experiments/maxhole_review_checks.py` + log (exhaustive
  n ≤ 9: MoatBound and (I′) 0 violations over 104,727 single-hole animals;
  substitute 1 refuted 63,112/104,727, ≥2-variant 95,252; substitute 2
  holds at 0; family checks confirm the ring shortfall and disconnection
  sets exactly); HolesUpper doc numbers replaced with the deterministic
  ones and the u-level fixed; MoatBound corroboration recorded in the
  module doc; `rookStep` made public; disconnection warning added to
  `ringAnimal_singleHole`; caveat added to `results/maxhole-proof.md`.
- Universal set: the three out-of-sample examples made enforcing
  (`rw [← T_*_5_4]` so the anchor numeral meets the law in one statement);
  `gd3_Tc_agrees` docstring corrected; `Compute.lean` reach-1 list fixed;
  Square/Hex axiom-wording fixed.
- Growth: `logSeq_*` → `negLogA_*` completed (14 sites); `a_supermul`
  docstring justification corrected.
- Plan/status: OUTWORKS-PLAN toolchain correction (per-declaration
  `._native.native_decide.ax_1_1` leaves, not `Lean.ofReduceBool`) and a
  post-campaign section; briefs left as the historical contract.

Deferred (batch with the next /simplify): the `UpperBound.lean`
rename-corrupted docstrings and `Sequence.lean` cosmetic notes (editing
either file forces the ~700 s `a_6` recompile cascade for zero substance),
dead-code removal in `Universal/{Finite,Peel}.lean` (Peel recompile is the
heavy one), the generic top-level names in Growth, and the optional
`rowSum`→`∑ T` bridge lemmas. Paper flags (§8 ring sentence, §9.1
Kronecker→Northcott attribution, §9 strip-bound range, §3-vs-Lean bracket
context) are recorded here and in the corrected memory only.

## Suggested disposition order

1. M3 — delete the false necessity claim (Northcott module doc,
   PROOF-STATUS, follow-ups list); smallest fix, stops a wrong claim
   propagating toward the paper.
2. M1 — close the guard gap (instance P₁s + rowSums + `universal_shape_d` +
   `lambda_lb` + n=4 spot checks at minimum) or rewrite the two blanket
   sentences; regenerate the build receipt at HEAD at the same time.
3. M2 — land the n=6 symmetry anchors in-tree (~25 min) or commit the
   checker + output; fix the 700s/490s figure.
4. The Holes documentation set (maxhole-proof.md caveat, module-doc level
   fix, substitute-refutation numbers) and the paper flags (§8 ring
   sentence, §9.1 Kronecker/Northcott attribution) — paper edits are
   jasonp's.
5. The prose/naming minors (ofReduceBool convention text, logSeq_*,
   expShape docstrings, PROOF-STATUS wording items) — batch with the next
   /simplify pass.
