# Hostile Witness — adversarial audit of the Lean formalization

2026-07-21. Brief: attack the Lean proofs as a hostile referee and shake out what a
careful OEIS editor reading the paper could reasonably object to. Seven attack lines,
each with a pre-registered kill condition. Kernel outputs (`#print axioms`) were
re-run live, all 26 PinGrand anchor values re-checked against `results/triangle.txt`,
and the definitional bridge brute-forced independently.

## Verdict

**The formalization survives the attack.** No sorry, no custom axioms, no circularity:
`T` is defined directly as a set cardinality (`Polyplets/Defs.lean:49`), the peeling
recursion is proved as bijections *against* that `T`, and the kernel confirms
`grand_form`, `T_staircase`, and the full shape chain (`shape_d`, `shape`,
`shape_production`, `production_int_*`) depend on `[propext, Classical.choice,
Quot.sound]` only — no `native_decide` anywhere in those cones. The seed really is
Sanity.lean's hand proof (`ExpForm.lean:7` imports Sanity; `base_match` uses
`T_one_one`).

What the Lean work does NOT do — and what an editor can push on — is certify the
engine data. For k ≥ 4 the explicit production polynomials are conditional theorems
(`P<k>_grand_of_banked`), and for **levels 12–16 the hypothesis cells are
single-algorithm** (kink TM only). The honest one-line grading: *the Lean proofs
convert "P_k was fitted" into "P_k is forced by a machine-checked shape theorem given
26 engine integers, 17 of which are two-algorithm-confirmed and 9 of which are
single-algorithm."* That is a real credibility upgrade, but it is bounded by the
engine at the top levels.

## Attack results

### A1 — claim language vs literal Lean statements: mostly survived, 2 wounds

The internal ledger (PROOF-STATUS.md) is honest: hypotheses are consistently
disclosed ("with hypotheses", "modulo TWO real-swept banked cells per level"), no
document claims "kernel-checked" for `native_decide`-rooted results, and every
recorded axiom expectation matched the live kernel output word for word.

Wounds:
1. **T-n-nm1.md (uncommitted) "Production P_1..P_16 are certified for all n ≥ 2k+1
   from two real-swept onset cells per level"** — for k ≥ 4 the cells are *assumed*,
   not certified-in-Lean; the summary bullet drops the "conditional" qualifier that
   PROOF-STATUS keeps. Say "certified conditional on" or "pinned from".
2. **grand-form.md contradicts itself**: the Formalization section declares the Lean
   item CLOSED and the PREDICTED tier retired, while Corollary 3 and "What remains
   open" still call the PREDICTED points "the remaining gap … planned". Stale
   paragraphs; a referee reading top-to-bottom sees the doc disagree with itself.

Nuance (label, not defect): the "UNCONDITIONAL k = 0, 1, 2" tier is unconditional in
the no-hypotheses sense but not native-free — kernel shows `P1_closed` carries
T(3,2)/T(4,3) `native_decide` leaves, `P2_closed`/`T_n_nm2` carry ~12 (weights + seed
values). Only the Grand chain (`grand_form`, shape) is truly clean.

### A2 — anchor provenance: the real finding

All 26 anchor integers in PinGrand.lean match `results/triangle.txt` exactly, and the
circularity guard is real (`scripts/gen_grand_pin.py:40,136` hard-caps anchors at
H ≤ 18; every H ≥ 20 triangle cell is P_k-generated and none is hypothesized).

Classification of the 26 cells:
- **Levels 4–12A (17 cells): MULTI-SOURCE.** The independent strip engine
  (enumeration-disjoint) confirms every cell with H ≤ 13; row totals are
  two-algorithm (g2 Redelmeier) through n = 22 and OEIS-external through n = 18.
- **Levels 12B–16 (9 cells): SINGLE-ALGORITHM.** `T(26,14), T(27,14), T(28,15),
  T(29,15), T(30,16), T(31,16), T(32,17), T(33,17), T(34,18)` are kink-TM only.
  Cross-ISA byte-identical re-runs (a34 verify covers all 26 anchors) and
  cross-revision re-runs rule out machine/build/transient corruption but cannot catch
  a logic bug shared by every run of the same kernel. This matches the grading the
  project already applies to a(23)+ ("single-algorithm, multiply cross-checked") —
  the P_k for k ≥ 12 inherit exactly that status, not two-algorithm independence.

**Superseded 2026-07-30 (AUDIT-2026-07-30 L7/S5).** The classification above
is the 2026-07-21 state (26 anchors, k ≤ 16). Two things moved: the completed
C_14 strip run (dalby 2026-07-22, `results/strip_C14_run.log`) confirmed
columns H ≤ 14 to n = 36, and the Grand tier extended to k ≤ 18 at the a(40)
close (`c54ce70`), taking the anchor set to **30**. The current split is
**19 strip-second-sourced / 11 kink-only**. The 11 are beyond strip reach
even at N = 40 (H ≥ 15):

    T(28,15) T(29,15) T(30,16) T(31,16) T(32,17) T(33,17)
    T(34,18) T(35,18) T(36,19) T(37,19) T(38,20)

`T(26,14)` and `T(27,14)`, single-algorithm above, are now strip-confirmed.
The reasoning about what cross-ISA and cross-revision re-runs can and cannot
catch is unchanged and still applies to the 11.

Two documentation errors found:
1. **Strip-engine coverage is H ≤ 13, not H ≤ 14** (`results/strip-engine.md:44-47`:
   C_14 was never completed; the H=14 log only computed the growth constant, no
   per-cell diff). The "0 mismatch H ≤ 14" note in project memory overstated by one
   column. Corrected.
2. **`oeis/SUBMISSION.md:97-100` cites T(36,20) as a P16 holdout — it is circular**
   (T(36,20) was itself P16-generated per `ns_a36/PROVENANCE.md:9-11`). Only
   T(35,19) is a genuine holdout, and it is same-algorithm.

Cheapest provenance upgrade: complete strip C_14 — flips T(26,14) and T(27,14) to
multi-source in one run.

### A3 — build integrity and audit enforcement: survived, 2 process dings

The heavy certificate set (15 `CFGVchunk` `native_decide`s + `Vt_3_3` + `d_3_4`) was
green in one coherent 8579-job build finishing 02:46 on 2026-07-21
(`polyplets/weights3heavy.log`), and the import chain (root → Grand.Audit → PinGrand
→ Weights3Heavy → chunks) puts every certificate in the build graph. Live re-run of
`Grand/Audit.lean` reproduced the recorded axiom sets exactly, including the full
~40-leaf list for `P16_grand_of_banked`.

Dings:
1. `#print axioms` is advisory — nothing fails the build if an axiom set drifts.
   A `#guard_msgs` wrapper (or a CI grep on the audit output) would make the
   "standard axioms only" claim self-enforcing.
2. The heavy build's only record is an untracked log file plus local `.olean`
   timestamps. Commit the log (or a dated one-line receipt in PROOF-STATUS).

### A4 — definitional bridge: attack failed

Lean `IsCanonical` ≡ engine definition term-for-term (fixed animals, translation
anchored, 8-connected, bounding-box height exactly H; `g2_redelmeier.cpp` per-box
h = maxy+1, miny = 0). Every plausible near-miss formalization (height ≤ H,
4-connectivity, free counting, |Δ| off-by-one, maxy = H, missing anchor) diverges at
a cell that IS machine-checked — most by n ≤ 3 — and an independent brute force
reproduced the banked triangle exactly through (6,5). The only "survivor" (allowing
p = q in `kingAdj`) is semantically identical, not an error.

Correction to the ledger's implication: the machine-checked bridge is **9 nonzero
cells** — (1,1),(2,1),(2,2),(3,1),(3,2),(3,3),(4,3),(5,3),(5,4) — not "n ≤ 5 all H";
the n = 6 values at `Compute.lean:285-286` are a prose comment, not checks. The 9
cells happen to be well-chosen (they kill every natural near-miss), but adding the
missing n ≤ 5 columns and the two n = 6 probes as real `native_decide` theorems is
cheap insurance.

### A5 — native_decide trust base: survived

All 56 `native_decide` uses bottom out in `Lean.ofReduceBool` (compiler trust, not
kernel). The classic escalation vectors are absent — zero `implemented_by`,
`@[extern]`, `unsafe`, `partial def` in project files — and every
`native_decide`-rooted result is labeled as such in the ledger with its axiom
footprint. Toolchain pinned (lean4 v4.31.0, mathlib v4.31.0). Residual risk is
generic compiler trust, honestly disclosed.

### A6/A7 — the paper vs the proofs: the paper is the weak document, not Lean

`paper/technical-report.tex` mentions Lean **zero** times and:
- states the diagonal law as hand-waving ("cell placement choices are sufficiently
  constrained to require…") when it is a machine-checked theorem;
- says P_k were "**fitted** against computed values … and verified against values
  from later rows" in the same breath as the exact `25^k/k!` claim — the single
  sentence an OEIS editor will push on. "Fitted" is also wrong in kind: given the
  proved degree-k bound, P_k is a determined exact solve, over-determined by later
  rows, not a regression;
- gives no provenance statement for which a(n) rest on pinned closed forms vs
  independent enumeration.

The admitted gaps (onset sharpness ab initio only k ≤ 5; monomial *coefficient*
integrality observed, only integer *values* proved) are stated consistently in
diagonal-law.md and grand-form.md and are not contradicted elsewhere.

## What an OEIS editor could reasonably object to, ranked

1. "Fitted" polynomials next to exact leading-coefficient claims, with the proof
   apparatus uncited (paper).
2. No provenance grading in the paper: which a(n) and which P_k are two-algorithm
   vs single-algorithm (levels 12–16 anchors and a(23)+ are single-algorithm).
3. T(36,20) presented as a holdout in SUBMISSION.md when it is P16-generated.
4. grand-form.md's stale self-contradiction about what remains open.
5. "Certified" without "conditional" in the T-n-nm1.md supersession bullet.

None of these is a defect in the Lean proofs. The attack brief — "show the proofs do
not lend credibility" — is not sustained by the evidence; what is sustained is that
the *documents around them* currently undersell (paper) or slightly oversell
(one bullet, one stale section) what was proved, and that the top five levels of the
pinned tier are exactly as strong as the kink engine and no stronger.

## Fix list (cheap → costly)

1. Reword T-n-nm1.md bullet: "certified conditional on two real-swept cells/level".
2. Delete/rewrite the two stale grand-form.md paragraphs (Corollary 3 note, "What
   remains open" Lean item).
3. Fix SUBMISSION.md holdout claim: T(35,19) only; drop or re-label T(36,20).
4. Commit weights3heavy.log (or a receipt); wrap Audit.lean in `#guard_msgs`.
5. Add the missing n ≤ 5 cells + the two n = 6 probes as real `native_decide`
   theorems in Compute.lean.
6. Paper: replace "fitted" with the determined-solve statement, cite the Lean
   theorems for shape/degree/integrality/25^k/k!, add a provenance table.
7. Complete strip C_14 (flips two anchors to multi-source; upgrades level 12–13
   provenance).

## Applied (2026-07-21, same day)

1. **Done** — T-n-nm1.md bullet now states the k = 4..16 conditionality
   explicitly.
2. **Done** — both stale grand-form.md paragraphs rewritten to match the
   Formalization section.
3. **Done** — SUBMISSION.md: T(35,19) is the holdout; T(36,20) re-labeled a
   consistency check (P_16-generated).
4. **Done** — `Grand/Audit.lean` wrapped in `#guard_msgs` (axiom drift now
   FAILS the build; verified against live output, all 8 guards pass);
   `weights3heavy.log` committed.
5. **Done** — `Polyplets/ComputeBridge.lean`: rows n ≤ 5 complete + T(6,4),
   T(6,5) as in-tree `native_decide` theorems; built green (258 s), bridge is
   now 17 kernel-recorded nonzero cells.
6. **Done** (paragraph rewrite incl. provenance grading; a fuller provenance
   table remains a paper-polish item).
7. **Done (2026-07-22)** — full Hmax=14 strip sweep vs banked triangle:
   **413 cells, 0 mismatches, columns H ≤ 14 independently confirmed to
   n = 36** (`results/strip_C14_run.log`; ran on dalby after the gympie
   attempt thrashed at a measured ~38 GB footprint). Anchors T(26,14) and
   T(27,14) flip to MULTI-SOURCE; the single-algorithm set shrinks from 9
   cells to the 7 of levels 13B–16. Recorded in `results/strip-engine.md`.
