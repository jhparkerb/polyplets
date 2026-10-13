# docs/

Results are in `results/`. This directory holds the proofs, a description of
how the computation works, and the notes used to maintain the repository.
`make gate-docs-index` fails if a file here is not listed below.

## Proofs

| file | what |
|---|---|
| `docs/proofs/diagonal-law.md` | the closed form for the diagonals of the height triangle: shape, onset and integrality |
| `docs/proofs/grand-form.md` | the exponential form the diagonal polynomials share, and what determines each one |
| `docs/proofs/universal-diagonal-law.md` | the same argument for any lattice whose neighbors lie in adjacent rows |
| `docs/proofs/dm-diagonal-law.md` | the triangle of diagonally symmetric polyplets |
| `docs/proofs/T-n-nm1.md`, `docs/proofs/T-n-nm2-and-general.md` | the first two diagonals by hand, and the general shape |
| `docs/proofs/cutcount-identity.md` | the identity behind the second enumerator, which counts by coloring |
| `docs/proofs/polyplet-upper-bound.md` | λ ≤ 9.3154 with an exact certificate |
| `docs/proofs/convex-mirage.md` | why the convex subclass does not give what it appears to |

## How the computation works

| file | what |
|---|---|
| `docs/engine-record.md` | the transfer-matrix enumerator: design, kernels, memory, measured costs per term |
| `docs/formats.md` | the run, checkpoint and cost-profile file formats |
| `docs/external-anchors.md` | published values this machinery reproduces that it did not produce |
| `docs/glossary.md` | the terms used in the code and the notes |

## Maintaining the repository

| file | what |
|---|---|
| `docs/engineering-standards.md` | how the tests are written: a check must be seen to fail before it is trusted |
| `docs/push-gate-tiers.md` | which checks run on every push, what they cost, and what `make gates-deep` adds |
| `docs/job-checklist.md` | before launching a long computation |
| `docs/observability.md` | the start/heartbeat/done log format long jobs write |
| `docs/lean-environment.md` | the Lean toolchain and how to build `polyplets/` |

## The machine-written papers

| file | what |
|---|---|
| `docs/publication-split.md` | how the papers in `paper/` are labelled: the author's prose, or machine-written and unread |
| `docs/l-papers-record.md` | the numbering, and the literature searches the machine-written papers' novelty sections rely on |
