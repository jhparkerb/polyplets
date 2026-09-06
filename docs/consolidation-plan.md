# Consolidation — 459 markdown files to about 25

Decided 2026-09-05 (jasonp): closed campaigns first, raw records deleted with
their history, conclusions folded into the surviving theme file. This file is
the map and the ledger. Every deleted path is readable at the commit named
beside its wave with `git show <commit>:<path>`; `tests/gate_citations.py`
accepts such citations (class `history`).

## Theme map — where a conclusion lives now

Written before the waves ran as a plan, and rewritten 2026-09-06 to name the
files that came out of them. Every file below is in the tree; the waves that
follow say what went into each and at which commit the sources are readable.

| theme | surviving file(s) |
|---|---|
| live state, decisions, what is running | `docs/handoff.md` |
| the terms and their evidence | `results/confidence.md`, `results/provenance-table.md`, `results/residual-cells.md`, `results/ns_a*/PROVENANCE.md`, `results/a41/PROVENANCE.md`, `docs/audits/AUDIT-2026-09-02.md` |
| the engine | `docs/engine-record.md` (as it ran), `docs/engine-design.md` (the 2026-06 build design), `docs/formats.md`, `docs/observability.md` |
| second sources | `results/second-sources.md`, `docs/proofs/cutcount-identity.md` |
| the diagonal formula and its tower | `docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`, `docs/proofs/universal-diagonal-law.md`, `results/diagonal-formula.md`, `results/below-onset.md`, `results/undertow.md` |
| the mod-3 and arithmetic structure | `results/arithmetic-structure.md` |
| growth constant | `results/growth-constant.md`, `docs/proofs/polyplet-upper-bound.md` |
| symmetry classes | `results/symmetry-classes.md` |
| holes, convex, directed, poly-time subclasses | `results/subclasses.md`, `docs/proofs/convex-mirage.md` |
| perimeter | `results/perimeter.md` |
| non-D-finiteness | `results/anisotropic-not-dfinite.md` |
| routes that did not work, and the open problems | `results/closed-doors.md` |
| Lean | `polyplets/PROOF-STATUS.md`, `polyplets/DESIGN.md`, `docs/lean-environment.md`, `docs/lean-artifact.md`, `docs/lean-below-onset-scope.md` |
| the papers | `paper/README.md`, `docs/publication-split.md`, `docs/publication.md`, `docs/l-corpus-contraction.md` |
| how the work was run, and what to do differently | `docs/lessons-learned.md` |
| standards and process | `docs/engineering-standards.md`, `docs/job-checklist.md`, `docs/push-gate-tiers.md`, `docs/glossary.md`, `docs/external-anchors.md` |
| OEIS staging (no submission) | `oeis/`, `results/oeis-candidates.md` |

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
| session-state and plan documents superseded by `docs/handoff.md` | `docs/resume-here.md`, `docs/unattended-2026-09-05.md`, `docs/agent-types.md`, `docs/undertow-review-brief.md`, `docs/motley-goal.md`, `docs/coin-lift-goal.md`, `docs/certificate-squeeze-plan.md`, `docs/notary-k-handoff.md`, `docs/notary-simplify-deferred.md`, `docs/severance-w4-scoping.md`, `docs/terminal-velocity-plan.md`, `polyplets/OUTWORKS-PLAN.md`, `polyplets/PLAN.md` | `docs/handoff.md`, `polyplets/PROOF-STATUS.md` |

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
`docs/handoff.md`, `paper/`, `oeis/`, `polyplets/`, `literature/`, `tests/`.

Done 2026-09-06, 03:00 EDT, by thirteen merge lanes and the lead: seven
survivors installed first (perimeter, growth-constant, symmetry-classes,
below-onset, undertow, diagonal-formula, arithmetic-structure; 72 sources),
then six (closed-doors, subclasses, second-sources, engine-record,
publication, lessons-learned; 103 sources). Each survivor ends with a
`## Sources` list naming its folded files. Every lane filed the
contradictions it found between sources, each kept with the later record
named; the commit messages carry them. Manuscript citations were repointed;
comments in tests that named the Middle Kingdom plan tables now name
`results/subclasses.md`. Five lanes stopped at the account's usage limit
after their files were complete; the lead linted and installed those files.

## Lane brief for wave 2b (2026-09-06, the lead's text; agents execute it)

**Mission.** Write one survivor file from its sources, for a reader of the
public repository, losing no result. The sources are then deleted with their
history by the lead.

**Keep, verbatim where it is exact:** every theorem and proposition
statement; every measured number with what measured it (script path, run
date, machine) and its grade (proved, certified, measured, conjectured);
every closed door with the obstruction that closed it; every open problem;
every table of values a paper or test cites. **Drop:** process narrative,
status updates whose only content is when something happened, repeated
definitions, chat-like framing, apologies, importance-talk, transitions
that only announce a turn, anything addressed to an earlier reader of the
file rather than to a reader of the result.

**Prose standard (jasonp's, binding):** American spelling; define before
asserting; no insider words (sweep, swept, wire, wired, tower, banked, pin,
pinned, onset unless defined at first use, holdout, RED, rung, ladder except
the strip ladder μ_H, kernel except as an artifact name, incumbent, second
source); "entry" for a value of the triangle, "cell" only for a lattice
cell; no "byte for byte" or "digit for digit"; one idea per sentence; a
number goes in a table or on its own line; no aphoristic closers.

**Citations.** Cite only paths that exist in the tree after the merge: the
survivors named in the map, `docs/proofs/`, `results/ns_a*/`, `results/a41/`,
`results/cutcount_b1/`, `experiments/`, `scripts/`, `tests/`, `paper/`,
`polyplets/`, data files under `results/`. Do not cite a source file that is
being folded; instead end the survivor with a section `## Sources` listing
each folded file on its own line with the word "deleted" on that line, e.g.
`- \`results/foo.md\` (deleted 2026-09-06; its content is above)`. That
wording is what the citation gate exempts.

**Structure.** Title; a paragraph saying what the theme's results are and
their grades; sections by topic, not by source file; `## Open problems`;
`## Reproduce` (the commands and scripts that recompute the numbers, taken
from the sources); `## Sources`. Length: as short as fidelity allows, and
not more than about two fifths of the sources' total.

**Conduct.** Read-only in the repository. No jobs, no builds, no `lake`,
nothing under `timeout`; a Python one-liner to check an arithmetic identity
in a source is fine. Write the survivor to the scratch path the lead gives,
not into the tree. If a source contradicts another, keep both statements
and say which is later and which the record now holds; do not adjudicate.
Report, in the final message, only: the scratch path, the length ratio,
any contradiction between sources, and any number you could not attribute.

## Wave 4a — code nothing cites, 2026-09-06

146 files under `scripts/` and `experiments/` that no tracked text file names
(the reference corpus is every tracked file that is text, including data
headers): 101 of the triangle-structure hunt's harness `experiments/tristruct/`,
the `experiments/rook1/` probes and their logs, five of the `scripts/lastditch/`
launchers, and 35 one-off launchers, probes and figure scripts for campaigns
already deleted. Readable at the commit named in the deleting commit's
message. The rest of `experiments/tristruct/` (64 files, cited by the
triangle records that wave 2b folds) goes with them once those records are
merged.

## Wave 4b — code nothing cites after the merges, 2026-09-06

24 more files under `experiments/` and `scripts/` that no tracked text file
names once the records were merged: 20 of `experiments/tristruct/`, two
figure and probe scripts, two shell launchers. Readable with
`git show 01b62ea:<path>`. What remains of `experiments/tristruct/` is
cited by `results/arithmetic-structure.md` or `results/diagonal-formula.md`.

## Wave 3 — the superseded manuscript, and what a public reader flagged

`paper/polyplets-report.tex` (1,122 lines, superseded 2026-08) and its checker
`paper/verify_claims.py` went together on 2026-09-06, with the coverage-audit
entry, the clean-clone step and the README lines that named them. Raised by an outside
reader on 2026-09-06 and deferred to jasonp (a CI run of the gates was
proposed and declined, 2026-09-06; the pre-push hook is the gate): splitting
the closed-form injection out of `orchestrator/sweep.go`
into its own package; the module name `polyominoes` in `go.mod`; `tests/engine/`
beside `tests/`; the author's name differing between `README.md` and the
paper. The mathematics half consolidates the diagonal-formula,
arithmetic, growth, subclass and perimeter themes into one file each, and
folds the remaining dated records. `docs/paper1-engine-chapter.md` and
`docs/paper1-reproducibility.md`, absorbed by `paper/technical-report-draft.tex`,
are candidates.
