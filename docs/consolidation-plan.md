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

## Wave 2b — the mathematics

Not started. The mathematics half consolidates the diagonal-formula,
arithmetic, growth, subclass and perimeter themes into one file each, and
folds the remaining dated records. `docs/paper1-engine-chapter.md` and
`docs/paper1-reproducibility.md`, absorbed by `paper/technical-report-draft.tex`,
are candidates.
