# Ghost Ship — disposition

2026-08-17. The decision layer. `REPORT.md` is the graded record (hygiene);
`VALUE-TRIAGE.md` is the novelty pass (worth). This file says what the two
together license, what to salvage, and whether the experiment continues.
It adds no new evidence — every claim below points at one of those two.

## 1. What the run actually bought

One question got answered, cleanly and against both predictions:

> **"The loop's output will be mostly junk needing expensive triage."**
> Retired. 64 claims, 0 FALSE, 0 unfalsifiable, 0 receipt-missing, 58
> verified by execution, at 1.6× court cost and *below* the court's raw
> token count.

Nothing else was settled.

- **Q2 (bulletin steering): not tested.** 0 steering minutes; the file was
  never written. The operator's own ruling (DIVERGENCES D1) is that blind
  steering had no legitimate content given foreknowledge of the ladder —
  so the arm as designed could not have produced data.
- **Q3 (token shape): instrumentation gap.** Per-session totals only; the
  preregistered CARRY / LOG / sandbox-read split is unrecoverable.
- **Q1 (cost per rung):** $225 vs ≈$47, but at n=1 rung the ratio is a
  numerator-of-one artefact and carries almost no information.

So of four preregistered questions, one answered, one untestable as
designed, one lost to instrumentation, one degenerate.

## 2. What the run produced, after triage

Per `VALUE-TRIAGE.md`:

- **Keep, novel:** the king-adjacency box/semiperimeter algebraic GF
  (Layer 1, kernel-derived, no fitting in the final chain); the Temperley
  q-series closed form with 44-digit certified constants (Layer 2); four
  new sequences; three OEIS-comment-grade identifications
  (A014300 / A112029 / A153337).
- **Keep, narrow:** area-moment GF algebraicity for every r; the
  king ≡ polyomino universality statement.
- **Lead, not result:** non-D-finiteness via K(q)'s zeros accumulating at
  q=1 under a Gieseking-constant oscillation law. Firm empirical, rigor
  gap correctly scoped by the loop itself.
- **Superseded:** the Layer 3 limit law and the `c_r = (r!)²/2^{r+7}` law.
  Richard, arXiv:0704.0716 — convex polygons carry the rectangles area
  law β₁,₁/₂; the loop's moment sequence is exactly that of U(1−U)/2.

Roughly two genuinely new results and a handful of catalogue-grade items,
against a most-expensive-third spent re-deriving published work.

## 3. The defect that matters

The rubric's "0 unwitting re-derivations" is **scoped to our repo**. Against
the literature the loop re-derived a published limit law at something like
a third of its budget — invisible to the loop (sandbox: 21 files, no
library) and invisible to grading (rubric: never asks).

This is structural, not a mistake by either arm. A sealed sandbox cannot
check priority, and a hygiene rubric cannot detect what it does not query.
Consequence: **cost-per-new-result for an unattended loop is currently
unmeasurable**, and the rung ladder measures conformance to a withheld path
rather than research value.

It is a larger defect than the untested bulletin, and it was not on either
predictor's list.

## 4. Salvage — recommended, not yet done

1. **Import Layer 1 into `results/convex-polyplets.md`** (an OPEN
   side-quest) with explicit Ghost Ship provenance, carrying the kernel
   proof `docs/proofs/convex-box-kernel.md` and the functional equation.
   This is the single highest-value action available and is ordinary
   research work, not experiment work.
2. **Import Layer 2** (q-series form, certified μ and A, 60 exact terms)
   alongside it.
3. **Stage the four sequences and three OEIS comments.** Submission remains
   gated behind the viva; staging is not submitting.
4. **Record the Layer 3 collision** wherever the moment machinery would
   otherwise look novel, so it is not re-derived a third time.
5. **Leave the non-D-finiteness item as a lead** with its two named gaps
   (rigorous oscillation law near q=1; residue nonvanishing at infinitely
   many zeros).

The sandbox tree is committed under `grading/run-record/sandbox/`, so
nothing is at risk while these wait — but a "run record" directory is where
results go to not be read.

## 5. Should the experiment continue?

**Not as a repeat.** A second run on the current design re-buys the one
argument already retired and leaves the same three questions open.

A second run is worth its cost only with all four of:

1. **Literature-priority pass folded into grading.** Cheap — the triage
   behind this file ran in under an hour. Without it there is no value
   metric, and without a value metric there is nothing to grade against
   that the first run did not already settle.
2. **Responsive steering arm** (DIVERGENCES D1), since the blind arm is
   ruled out on the operator's own reasoning. Otherwise drop Q2 from the
   design rather than carry an untestable question a second time.
3. **Per-curve token instrumentation** at the launcher, or drop Q3.
4. **Session-boundary handoff fix.** Three instances (s11–s14): a successor
   reads a missing receipt as a dead run and relaunches work already in
   flight. Structural cost of the fresh-session design, unpredicted by
   both predictors.

**And the rung ladder should not survive.** The loop "failed" by not
pursuing a target it was never told about, while building eleven verified
sessions on untouched ground. Grading run 2 on value-per-dollar requires
(1) as a prerequisite, which is why (1) is listed first and why the salvage
in §4 comes before any relaunch decision.

**Standing recommendation:** do §4, then decide. If the four conditions
above are not all going to be met, the honest close is that Ghost Ship
answered its junk-rate question, produced two real results as a byproduct,
exposed a structural blind spot in its own design, and is finished.
