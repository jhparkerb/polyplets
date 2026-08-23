# docs/ — what is in here

A map of everything else in this directory, written 2026-08-18 during the
close-out markdown sweep and held true by `make gate-docs-index`. The groups
are how the tree divides for a release decision: 1 and 2 are what a reader
needs, 3 and 4 are the project's own record, 5 and 6 are about how the work was
run rather than what it found.

`docs/viva-*.md` and `docs/drill*.md` are gitignored study notes, local to
jasonp's machine, and are not missing from a clone by accident.

## 1. Reference — read these to use or check the repo

| file | what |
|---|---|
| `docs/glossary.md` | terms used across every doc and result note |
| `docs/formats.md` | POLYRUN run files, checkpoints, cost profiles |
| `docs/engine-design.md` | the production enumerator, as built |
| `docs/dmirror-design.md` | the Hall of Mirrors symmetric transfer matrix |
| `docs/observability.md` | the provenance/heartbeat contract every long job obeys |
| `docs/engineering-standards.md` | red-first tests, fail-closed guards, hooks |
| `docs/job-checklist.md` | consult before launching any compute job |
| `docs/lean-environment.md` | toolchain paths, vendored deps, lemma search |
| `docs/lean-artifact.md` | the Lean development as a citable object |
| `docs/lean-below-onset-scope.md` | what Lean does and does not reach, and the cost of closing it |
| `docs/state-2026-08-23.md` | **the planning view** — what is true now, what is decided, what is open with its price and what it would change |
| `docs/time-at-the-bar-report.md` | what the last round did, and the five priced runs it did not launch |

## 2. `docs/proofs/` — the mathematical record

`docs/proofs/diagonal-law.md` (shape, onset and integrality — a theorem),
`docs/proofs/universal-diagonal-law.md`, `docs/proofs/dm-diagonal-law.md`,
`docs/proofs/grand-form.md`, `docs/proofs/cutcount-identity.md` (Motley's
cancellation identity), `docs/proofs/polyplet-upper-bound.md` (λ ≤ 9.3154, exact
certificate), `docs/proofs/convex-mirage.md`, `docs/proofs/T-n-nm1.md`,
`docs/proofs/T-n-nm2-and-general.md`.

## 3. Publication

| file | what |
|---|---|
| `docs/time-at-the-bar.md` | **the last round before the landing** — research still worth doing, work that could be planned, what could be removed; the round after `docs/last-orders.md`, and disjoint from `PRE-LANDING.md` by construction |
| `docs/last-orders.md` | **the round before the landing** — work that could be planned, what could be removed, research still worth doing; disjoint from `PRE-LANDING.md` by construction |
| `docs/acceptance-queue.md` | **the live worklist** — what makes a(21)–a(40) defensible |
| `docs/publication-strategy-2026-08-18.md` | current strategy: the repo is the publication |
| `docs/publication-split.md` | P papers vs L papers, the disclosure blocks, the OEIS lineup |
| `docs/sortie-publication-plan.md` | the earlier plan; its §3–§5 still stand |
| `docs/provenance-tables.md` | the per-paper warrant tables |
| `docs/reviewer-expertise-tiers.md` | what expertise each claim needs to assess |
| `docs/external-anchors.md` | what this machinery reproduces that it did not produce |
| `docs/paper1-engine-chapter.md`, `docs/paper1-reproducibility.md` | source material for P1 |
| `docs/undertow-chapter.md` | source material for the Undertow material, which became L10 on 2026-08-22 and was **merged into `paper/L8-below-onset.tex` on 08-23**; `docs/l-corpus-contraction.md` |
| `docs/l-paper-currency.md` | what each L paper would need to absorb; **superseded 2026-08-23** by `docs/l-corpus-contraction.md`, which merged four of the nine it describes |
| `docs/main-paper-audit-2026-08-18.md` | findings on `paper/technical-report.tex`, unapplied by design |
| `docs/priority-passes-2026-08-18.md` | literature-priority passes over the nine L papers |
| `docs/l-corpus-contraction.md` | **the L-paper contraction, 2026-08-23**: ten papers to six, what the assessment found, and the two campaigns it closed |
| `docs/priority-pass-L10-2026-08-23.md` | the Undertow pass: the near neighbour it found, and the limit of a web-only negative. Its verdict now lives in L8 §Novelty |
| `docs/oeis-ai-policy.md` | OEIS policy and precedent for AI-assisted submissions |
| `docs/open-problem-lambda-bracket.md` | the framed open question on λ's upper bound |

## 4. Campaign record — by thread

Each thread's *findings* live in `results/`; these are the plans, goals and
handoffs that produced them. Where a thread is closed, its header banner
carries the verdict.

- **Engine and utilization** — `docs/full-utilization-redesign.md`,
  `docs/utilization-bottleneck-log.md` (named bottlenecks, never retried),
  `docs/terminal-velocity-plan.md`, `docs/a35-two-media-plan.md` (FAILED, do not
  re-run), `docs/redelmeier-tall-plan.md`
- **RESUMING COLD** — `docs/resume-here.md` (the running job and what to do
  when it lands), after `results/confidence.md`.
- **Skeleton Key** (the hunt for a way past n = 40) —
  `docs/skeletonkey-reprompt.md` is the **entry point**: the post-`/clear`
  prompt for this mission plus the kill inventory that makes a breadth-first
  pass cheap, and the two measured cost laws (height 1.70x per unit of n,
  depth 7-9x). Results: `results/skeletonkey-hankel-closure.md` (the transfer
  floor grows at 2.43, not 3 — both extrapolations missed),
  `results/skeletonkey-cell-sparsity.md` (banked 2026-08-22: the char-0
  sparsity rescue is real at 425x but the compressed dimension is already
  1.6-2.2x the column frontier and grows faster, so "crossover: never"
  survives for a new reason).
- **Undertow / last ditch** (the diagonal tower pinned from below) —
  `docs/lastditch-campaign.md` is the **entry point**; then
  `docs/lastditch-ideas.md` (the candidate list, closed doors included),
  `docs/five-terms-plan.md` (proposed, not launched),
  `docs/undertow-review-brief.md` (the review brief). Results:
  `results/undertow.md`, `results/undertow-picture.md`, `results/a41/`,
  `results/motley-par/`, `results/lastditch-cost-ladders.md`, and the three
  review lanes `results/undertow-review-{A,B,C}.md` with
  `results/undertow-review-queue.md`.
- **Motley / Coin Lift** (the second source) — `docs/b1-closure-plan.md`,
  `docs/motley-goal.md`, `docs/motley-plan.md`, `docs/coin-lift-goal.md`,
  `docs/coin-lift-plan.md` (CLOSED at G2)
- **Onset defect / Severance / Notary** — `docs/onset-defect-handoff.md` (entry
  point), `docs/onset-defect-plans.md`, `docs/onset-defect-severance-plan.md`,
  `docs/severance-w4-scoping.md`, `docs/notary-lean-plan.md`,
  `docs/notary-k-plan.md`, `docs/notary-kernel-scoping.md`,
  `docs/notary-k-handoff.md`, `docs/notary-simplify-deferred.md`
- **Middle Kingdom** (the poly-time subclasses) — `docs/middle-kingdom-plan.md`
  (campaign complete), `docs/middle-kingdom-followups-plan.md`
- **Perimeter** — `docs/perimeter-defect-plan.md`,
  `docs/perimeter-both-ends-state.md`
- **λ bounds** — `docs/certificate-squeeze-plan.md`, `docs/king-twigs-plan.md`
  (CLOSED, closed door)
- **Triangle / rook parity** — `docs/rook-parity.md` (the banked goal),
  `docs/rook1-brief.md`, `docs/rook-parity-bar.md`,
  `docs/triangle-structure-d9-d12-plan.md`
- **Lean campaigns** — `docs/lean-staircase-growth-brief.md`,
  `docs/lean-hostile-witness.md` (adversarial audit of the formalization). The
  Lean campaign plans themselves are `polyplets/PLAN.md`,
  `polyplets/GRANDFORM-PLAN.md` and `polyplets/OUTWORKS-PLAN.md`.

## 5. Process and method

How the work was run. This group is about the project rather than about
polyplets, and `docs/publication-strategy-2026-08-18.md` §5 leaves it an open
question whether it goes public.

`docs/agent-types.md`, `docs/r3-job-dispatch.md`,
`docs/skeptical-reader-standard.md`, `docs/rook-parity-team-process.md`,
`docs/process-proposal.md`, `docs/offside-brief.md`, `docs/offside-design.md`,
`docs/state-minimal.md`, `docs/ghostship-preregistration.md`,
`docs/triangle-postmortem.md` (a four-round failure, written up),
`docs/lessons-learned.md`, `docs/project-postmortem.md` (the whole-project
view: the arc, luck both ways, and thirteen action items for the next attempt
at a mathematical contribution).

The Ghost Ship run record itself is `results/ghostship/` — hash-sealed and
frozen on purpose, because it cites a filesystem that is not this one.

## 6. `docs/reviews/` — review ledgers

`docs/reviews/l-trim/` is the five-phase argued trim of the L papers: PROTOCOL,
STATE, then cuts/defense/verdict per phase. Campaign complete, 34,758 → 31,339
words.

`docs/reviews/llm-tics/` is the running readability campaign — PLAN, catalog,
per-paper findings, round ledgers. Its rulebook is
`paper/L-readability-rules.md` and each round is gated on jasonp's say-so.

`docs/reviews/outworks-adversarial.md` is the adversarial pass over the
Outworks Lean material.
