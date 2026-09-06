# docs/ — what is in here

A map of every other file in this directory, held true by `make gate-docs-index`
(it fails if a file here is not named below) and by `make gate-citations` (it
fails if a name below points at nothing). Most of what used to be in this
directory was merged into the records of group 3 in September 2026; every file
deleted then is listed, with the commit it is readable at, in
`docs/consolidation-plan.md`.

Findings live in `results/`. This directory is how the machinery works, what was
proved, and how the work was run.

`docs/viva-*.md` and `docs/drill*.md` are gitignored study notes, local to
jasonp's machine, and are not missing from a clone by accident.

## 1. Reference — read these to use or check the repo

| file | what |
|---|---|
| `docs/glossary.md` | terms used across every doc and result note |
| `docs/engine-design.md` | the 2026-06 build design of the run-file engine; superseded in part, and the as-shipped record is `docs/engine-record.md` |
| `docs/formats.md` | POLYRUN run files, checkpoints, cost profiles |
| `docs/observability.md` | the provenance/heartbeat contract every long job obeys |
| `docs/engineering-standards.md` | red-first tests, fail-closed guards, hooks |
| `docs/push-gate-tiers.md` | what the push gates cost, and what `make gates-deep` restores |
| `docs/job-checklist.md` | consult before launching any compute job |
| `docs/lean-environment.md` | toolchain paths, vendored deps, lemma search |
| `docs/lean-record.md` | the Lean development: what it proves, what it does not reach, the adversarial audit of 2026-07-21, and how a reader checks it |
| `docs/reviews/outworks-adversarial.md` | the adversarial pass over the Outworks Lean material, 2026-07-31 |

## 2. `docs/proofs/` — the mathematical record

| file | what |
|---|---|
| `docs/proofs/diagonal-law.md` | the closed form for the triangle's diagonals: shape, onset and integrality, a theorem |
| `docs/proofs/grand-form.md` | the exponential form the diagonal polynomials share, and what pins each level |
| `docs/proofs/universal-diagonal-law.md` | the same argument run without the king lattice fixed |
| `docs/proofs/dm-diagonal-law.md` | the diagonal-mirror symmetry triangle |
| `docs/proofs/cutcount-identity.md` | the cancellation identity the coloring engine evaluates |
| `docs/proofs/polyplet-upper-bound.md` | λ ≤ 9.3154 with an exact certificate |
| `docs/proofs/T-n-nm1.md`, `docs/proofs/T-n-nm2-and-general.md` | the first two diagonals by hand, and the general shape |
| `docs/proofs/convex-mirage.md` | why the convex subclass does not give what it appears to |

## 3. Publication and record

| file | what |
|---|---|
| `docs/publication-split.md` | P papers vs L papers, the disclosure blocks, the OEIS lineup |
| `docs/publication.md` | the publication record: strategy, warrant tables, standards, audits, novelty searches, removals |
| `docs/engine-record.md` | the enumerator's measured history: kernels, scheduling, memory, negatives, per-term costs, a(41) |
| `docs/consolidation-plan.md` | the 2026-09 consolidation: theme map, and the ledger of deleted records with the commit each is readable at |
| `docs/external-anchors.md` | what this machinery reproduces that it did not produce |
| `docs/handoff.md` | the project's own live state: what is running, what is decided, what is open. Internal, and the longest file here |
| `docs/pre-landing.md` | the go/no-go checklist written before the repository was made public |
| `docs/audits/` | four dated correctness audits of the engine and the claims, 2026-06-28 through 2026-09-02; the last one is cited by the current records |

## 4. Campaigns still open, and their entry points

| file | what |
|---|---|
| `docs/lastditch-campaign.md` | pinning the diagonal tower from below the onset — the route that gave a(41) |

## 5. The L papers

| file | what |
|---|---|
| `docs/l-papers-record.md` | the L papers' own record: the contraction that took ten manuscripts to six, and every literature-priority pass behind them |

no part of it is tracked any more.
