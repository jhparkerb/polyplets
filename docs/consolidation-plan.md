# Consolidation — 459 markdown files to about 25

Decided 2026-09-05 (jasonp): closed campaigns first, raw records deleted with
their history, conclusions folded into the surviving theme file. This file is
the map and the ledger. Every deleted path is readable at the commit named
beside its wave with `git show <commit>:<path>`; `tests/gate_citations.py`
accepts such citations (class `history`).

## Theme map — where a conclusion lives now

| theme | surviving file(s) |
|---|---|
| live state, decisions, what is running | `HANDOFF.md` |
| the terms and their evidence | `results/confidence.md`, `results/ns_a*/PROVENANCE.md`, `results/a41/PROVENANCE.md`, `results/provenance-table.md`, `results/residual-cells.md`, `AUDIT-2026-09-02.md` |
| the engine | `docs/engine-design.md`, `docs/paper1-engine-chapter.md`, `docs/formats.md`, `docs/observability.md` |
| second sources | `results/strip-engine.md`, `results/cutcount_b1/rows41/README.md`, `results/motley-par/README.md`, `docs/proofs/cutcount-identity.md`, `results/redelmeier_row22/PROVENANCE.md` |
| the diagonal formula and its tower | `docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`, `docs/proofs/universal-diagonal-law.md`, `results/defect-gas.md`, `results/undertow.md`, `results/onset-defect-*.md`, `results/ridgeline-depth-amplitudes.md` |
| the mod-3 and arithmetic structure | `results/ternary-spine.md`, `results/triangle-snf.md`, `results/v5-denominator-law.md`, `results/triangle-hunt-klein-parity.md`, `results/triangle-r2-d3-proof.md` |
| growth constant | `results/strip-mu-certificates.md`, `results/strip-growth-lambda-bounds.md`, `docs/proofs/polyplet-upper-bound.md`, `results/series-analysis-da.md`, `results/concatenation-upper-bound.md` |
| symmetry classes | `results/subgroup-mod4.md`, `results/sym_counts.txt`, `results/related-seqs-n3*.md`, `results/bilateral-parity.md` |
| holes | `results/holes_n18.txt`, `results/maxhole-*.md`, `results/hole-*.md` |
| subclasses (convex, directed, middle kingdom) | `results/middle-kingdom.md`, `results/convex-polyplets.md`, `results/hv-growth-sandwich.md`, `results/directed-*.md`, `results/multi-directed.md`, `docs/proofs/convex-mirage.md` |
| perimeter | `results/perimeter-both-ends.md`, `results/perimeter-defect-diagonals.md`, `results/min-site-perimeter.md` |
| non-D-finiteness | `results/anisotropic-not-dfinite.md`, `results/isotropic-dfinite-boxes.md` |
| Lean | `polyplets/PROOF-STATUS.md`, `polyplets/DESIGN.md`, `docs/lean-environment.md`, `docs/lean-artifact.md`, `docs/lean-below-onset-scope.md` |
| the papers | `paper/README.md`, `docs/publication-split.md`, `paper/L-readability-rules.md`, `docs/l-corpus-contraction.md`, `docs/priority-pass*.md` |
| closed campaigns, as records | `docs/triangle-postmortem.md`, `docs/rook-parity.md`, `results/ghostship/REPORT.md`, `results/skeletonkey-four-mechanisms.md`, `docs/lastditch-campaign.md`, `docs/project-postmortem.md`, `docs/lessons-learned.md` |
| standards and process | `docs/engineering-standards.md`, `docs/job-checklist.md`, `docs/push-gate-tiers.md`, `docs/glossary.md`, `docs/external-anchors.md` |
| OEIS staging (no submission) | `oeis/`, `submissions/oeis/README.md`, `results/oeis-candidates.md` |

## Wave 1 — closed campaigns, 2026-09-06

Deleted at the commit after `e5e7870`: 443 tracked files, readable with
`git show e5e7870:<path>`. What they were, and where their conclusion lives:

| what | files | conclusion now in |
|---|---|---|
| Ghost Ship: the 2026-07-12 sandbox snapshot, session logs, prompts, usage, grading lanes, review lanes, sealed predictions | `results/ghostship/` except `REPORT.md` and `DISPOSITION.md`; `scripts/ghostship/instructions.md` | `results/ghostship/REPORT.md`, `results/ghostship/DISPOSITION.md` |
| Offside and the process proposal | `results/offside/`, `docs/offside-*.md`, `docs/process-proposal.md`, `docs/state-minimal.md` | `docs/lessons-learned.md` |
| Rook parity round 1 | `results/rook1/`, `docs/rook1-brief.md` | `docs/rook-parity.md` |
| Triangle-structure hunt rounds 2--4 (working files) | `results/triangle-r2-extension-scout.md`, `results/triangle-r3-*` (five), `results/triangle-salvage.md`, `results/r4/` (most), `experiments/tristruct/sweep_report.md`, `docs/triangle-structure-d9-d12-plan.md` | `docs/triangle-postmortem.md`; the proofs stay in `results/triangle-r2-d3-proof.md` and `results/triangle-hunt-klein-parity.md` |
| L-paper review campaigns (trim, tics, coinage) | `docs/reviews/l-trim/` (all but `PROTOCOL.md`), `docs/reviews/llm-tics/` (all but `density.py`), `paper/L-coinage-candidates.md`, `paper/polyplets-report-cuts.md`, `docs/l-paper-currency.md` | `paper/L-readability-rules.md`, `docs/l-corpus-contraction.md` |
| session-state and plan documents superseded by `HANDOFF.md` | `docs/resume-here.md`, `docs/unattended-2026-09-05.md`, `docs/agent-types.md`, `docs/undertow-review-brief.md`, `docs/motley-goal.md`, `docs/coin-lift-goal.md`, `docs/certificate-squeeze-plan.md`, `docs/notary-k-handoff.md`, `docs/notary-simplify-deferred.md`, `docs/severance-w4-scoping.md`, `docs/terminal-velocity-plan.md`, `polyplets/OUTWORKS-PLAN.md`, `polyplets/PLAN.md` | `HANDOFF.md`, `polyplets/PROOF-STATUS.md` |

Held back from this wave because code, a manuscript or a gate still names
them (43 files, listed in the commit message): they go when the citing comment
is repointed, in wave 2.

By directory: results/ghostship/grading/run-record/sandbox 167; results/ghostship/grading/run-record/sandbox/experiments 74; results/ghostship/grading/run-record/logs 29; docs/reviews/l-trim 22; docs 18; results/ghostship/grading/run-record/sandbox/results 15; results/ghostship/grading/run-record/sandbox/reports 14; results/ghostship/grading/run-record/usage 14; docs/reviews/llm-tics 11; results/rook1 11; results/ghostship/grading 8; results/ghostship/grading/run-record/sandbox/docs/proofs 8.

## Wave 2a — the held-back files, 2026-09-06

Deleted at the commit after `b054dea`: 41 files, readable with
`git show b054dea:<path>`. Forty of the 43 held back from wave 1, plus
`scripts/undertow_picture.py`, the generator of a deleted picture. Kept:
`docs/middle-kingdom-plan.md` and `docs/middle-kingdom-followups-plan.md`,
whose measured tables the gates and tests cite as their source (they fold into
`results/middle-kingdom.md` in the mathematics wave), and
`docs/reviews/llm-tics/density.py`, which the coverage audit runs. The code
comments that named the deleted files stand as written; the note at the top of
`README.md` says where the files are.

The receipts gate (`scripts/check_receipts.sh`, `make gate-receipts`, four
fixtures) was the rook-parity campaign's control; with its scope deleted it
could only pass vacuously, so it is retired in the same wave.

## Wave 2b — the mathematics: the merge map

Each row is one surviving file, written fresh from its sources, which are
then deleted with their history. Manuscripts that cite a source by path are
repointed to the survivor in the same commit. Order: the smallest themes
first, so the pattern is set before the large ones.

| survivor | sources folded into it |
|---|---|
| `results/perimeter.md` (planned) | `perimeter-both-ends.md`, `perimeter-defect-diagonals.md`, `perimeter-defect-k7-pricing.md`, `min-site-perimeter.md` |
| `results/growth-constant.md` (planned) | `strip-growth-lambda-bounds.md`, `strip-mu-certificates.md`, `strip-mu-fast.md`, `strip-mu-engine-resumption.md`, `strip-fss-lambda-sensitivity.md`, `series-analysis-da.md`, `theta-universality.md`, `confluent-universality.md`, `stretched-exponential-test.md`, `concatenation-upper-bound.md`, `bridge-credit-closed.md`, `king-twigs-l1.md`, `lambda-atlas-probe.md`, `nu-exponent.md`, `height-distribution-collapse.md`, `docs/open-problem-lambda-bracket.md` |
| `results/symmetry-classes.md` (planned) | `subgroup-mod4.md`, `percell-mod4.md`, `bilateral-parity.md`, `related-seqs-n24.md`, `related-seqs-n32.md`, `related-seqs-n33.md`, the six `dmirror-*.md`, `dm-diagonal-recon.md`, `joint-box-probe.md`, `docs/dmirror-design.md` |
| `results/below-onset.md` (planned) | `onset-defect-law.md`, `onset-defect-depth1-closed.md`, `onset-defect-depths234.md`, `onset-defect-crossover.md`, `ridgeline-depth-amplitudes.md`, `depth-tower-bivariate-dead-end.md`, `diagonal-law-below-onset.md`, `allpairs-kernel.md`, `severance-w1-anchor-cut.md`, `notary-depth1-lean.md`, `docs/onset-defect-handoff.md` |
| `results/undertow.md` (rewritten) (planned) | `undertow-review-A.md`, `undertow-review-B.md`, `undertow-review-C.md`, `undertow-square-validation.md`, `undertow-square-depth2.md`, `depth5-cost-settled.md`, `depth5-gate-green.md`, `depth6-cost-settled.md`, `lastditch-cost-ladders.md` |
| `results/diagonal-formula.md` (planned) | `defect-gas.md`, `diagonal-closed-forms.md`, `k8-pinning.md`, `hex-diagonal-law.md`, `polyiamond-diagonal-law.md`, `slope-slicings.md`, `slope-growth-saddle.md`, `production-matrix-probe.md`, `triangle-combinations.md`, `triangle-structure.md`, `gf-head-check.md` (the proofs in `docs/proofs/` stay) |
| `results/arithmetic-structure.md` (planned) | `ternary-spine.md`, `triangle-snf.md`, `v5-denominator-law.md`, `triangle-hunt-klein-parity.md`, `triangle-r2-d3-proof.md`, `coin-flip-characteristic-landscape.md`, `char2-basis-status.md`, `exactchange-probes.md` |
| `results/closed-doors.md` (planned) | the six `skeletonkey-*.md`, `nkey-census.md`, `dual-connectivity-blockcount.md`, `span-cap-variation.md`, `band-structure-probes.md`, the two `boundary-push-*.md`, the two `matching-pair-*.md`, `discarded-term.md`, `strip-spectrum-defect-rate.md`, `finite-lattice-crossover.md`, `converse-sweep.md`, `isotropic-dfinite-boxes.md`, `unexplored-avenues.md`, `open-conjectures.md`, `resource-asks.md` |
| `results/subclasses.md` (planned) | `middle-kingdom.md`, `middle-kingdom-grid.md`, `middle-kingdom-phase3.md`, `docs/middle-kingdom-plan.md`, `docs/middle-kingdom-followups-plan.md`, `mk-dir4-perimeter.md`, `hv-growth-sandwich.md`, `king-subfamilies.md`, `countable-subpopulations-criterion.md`, `convex-polyplets.md`, `convex-anisotropic.md`, `directed-king-animals.md`, `directed-cone-anchor.md`, `multi-directed.md`, `beyond-polyplets.md`, `polyplet-zoo.md`, `component-stratification.md`, `move-graph-connectivity.md`, `rook-bishop-edge-distribution.md`, `king-extremal.md`, the four `hole-*.md` and `maxhole-*.md` |
| `results/second-sources.md` (planned) | `strip-engine.md`, `motley-h17.md`, `motley-h18.md`, `motley-step0.md`, `coin-lift-g2.md`, `ticker-tape-assessment.md`, `congruence-crt-combination.md`, `redelmeier_row20/RESULT.md`, `docs/b1-closure-plan.md` (the directories `cutcount_b1/`, `motley-par/`, `redelmeier_row22/` keep their own records) |
| `docs/engine-record.md` (planned) | `docs/paper1-engine-chapter.md` as the base; `a34-utilization-postmortem.md`, `utilization-fix-and-ceiling.md`, `docs/utilization-bottleneck-log.md`, `docs/full-utilization-redesign.md`, `fanin-tax.md`, `overcommit-hydra.md`, `overlap-kink-design-sketch.md`, `steal-tail-h18.md`, `sub-record-interrupt-design.md`, `scheduling.md`, `perf-outcomes.md`, `map-profile.md`, `map-body-profile.md`, `merge-ledger.md`, `dalby-perf-audit.md`, the four `kink-carry*.md`, `kink-resume-sigterm-bug.md`, `completion-oracle.md`, `completion-pruning-audit.md`, `nmax-disk-scaling.md`, `terminal-velocity.md`, `second-wind.md`, `crt-counter-shaping.md`, `gate-class-sweep.md` |
| `docs/publication.md` (planned) | `docs/publication-strategy-2026-08-18.md`, `docs/sortie-publication-plan.md`, `docs/provenance-tables.md`, `docs/reviewer-expertise-tiers.md`, `docs/skeptical-reader-standard.md`, `docs/main-paper-audit-2026-08-18.md`, `docs/prove2me-note.md`, `docs/oeis-ai-policy.md`, `docs/acceptance-queue.md`, `docs/paper1-reproducibility.md`, `results/removals-2026-08-22.md`, `results/novelty-sortie.md`, `results/l-paper-proof-audit.md`, `results/literature-record-56-corrected.md`, `results/mathematics.md` |
| `docs/lessons-learned.md` (rewritten) (planned) | `docs/project-postmortem.md`, `docs/triangle-postmortem.md`, `docs/rook-parity.md`, `results/ghostship/REPORT.md`, `results/ghostship/DISPOSITION.md`, `results/skeletonkey-four-mechanisms.md` (as the closed-campaign summaries) |

Untouched by design: the per-term records (`results/ns_a*/`, `results/a41/`,
`results/redelmeier_row22/`, `results/cutcount_b1/`, `results/motley-par/`),
`results/confidence.md`, `results/provenance-table.md`, `results/residual-cells.md`,
`docs/proofs/`, the four audits, the reference docs of `docs/README.md` group 1,
`HANDOFF.md`, `paper/`, `oeis/`, `polyplets/`, `papers/`, `tests/`.

Not started.

## Wave 3 — the superseded manuscript, and what a public reader flagged

`paper/polyplets-report.tex` (1,122 lines, superseded 2026-08) and its checker
`paper/verify_claims.py` go together, with the coverage-audit entry, the
clean-clone step and the README lines that name them; that is a code change
across `tests/` and `scripts/` and is its own commit. Raised by an outside
reader on 2026-09-06 and deferred to jasonp (a CI run of the gates was
proposed and declined, 2026-09-06; the pre-push hook is the gate): splitting
the closed-form injection out of `orchestrator/sweep.go`
into its own package; the module name `polyominoes` in `go.mod`; `test/`
beside `tests/`; the author's name differing between `README.md` and the
paper. The mathematics half consolidates the diagonal-formula,
arithmetic, growth, subclass and perimeter themes into one file each, and
folds the remaining dated records. `docs/paper1-engine-chapter.md` and
`docs/paper1-reproducibility.md`, absorbed by `paper/technical-report-draft.tex`,
are candidates.
