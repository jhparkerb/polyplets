# Code target

Set 2026-10-27, on branch `rewrite`; master is untouched until jasonp signs
off. No calendar budget: it is done when the stop condition below holds.

## The claim

A reader who builds and runs, or reads, the programs behind the published
counts finds code they would trust: every file says what it computes and what
check catches a mistake in it, nothing in it is unused, and its names and
comments make sense without the project's history. After the rewrite they
still compute exactly what they computed before.

## In scope

The programs behind a(n), the strip and coloring recounts, and the symmetry
counts, with the checks that guard them and their Makefile rules.

| program | files | backs |
|---|---|---|
| transfer-matrix enumerator | `core/*.h`, `worker/`, `orchestrator/` (with `cmd/orchestrate`, `combine`, `predict`, `runcat`) | every enumerated T(n,H) |
| run verifier | `verify/` | checks of the enumerator's run files |
| Redelmeier enumerator | `cpp/g2_redelmeier.cpp` | whole rows n <= 22 |
| strip transfer matrix | `cpp/strip_tm.cpp` | the 469 entries with H <= 14 |
| coloring recount | `cpp/coloring_recount.cpp` | the entries with H <= 19 |
| symmetry counts | `cpp/sym/symcount_fast.cpp`, `cpp/sym/symtm.cpp`, `cpp/dmirror_spine.cpp` | a(n) mod 4, T(n,H) mod 2, the symmetry-class sequences |
| shared | `cpp/obs.h`, `cpp/argparse.h` where these use it | |
| checks | `tests/engine/`, and the `tests/gate_*.py` that run the programs above (`gate_kink_oracle`, `gate_g2`, `gate_coloring_recount`, `gate_sym`, `gate_symtm`, `gate_subgroup`, `gate_verify`), with `tests/common.py` | |

Found while scoping: `strip_tm` has no make target that runs it, and
`gate-coloring-recount` is outside the automatic chain because of `-fopenmp`. Both
get a check that `make` runs.

## Out of scope

`scripts/` (including `term.sh` and the assembly scripts, which are run to
produce the reference outputs but not rewritten), `experiments/`, the Lean in
`polyplets/`, the other programs in `cpp/` (`tma`, `strip_mu*`, perimeter,
severance, convex, middle-kingdom and the rest), the paper verifiers, and the
documents, except where a document names a file, flag or function that the
rewrite renames or removes.

## How correctness is kept

1. Before the first edit, record reference outputs from the unmodified code
   in `tests/reference/`: `scripts/term.sh 26` output, `g2 square8` through
   n = 14, the kink-oracle sums, the enumerator's T(n,H) for n <= 24,
   `strip_tm` and `coloring_recount` entries at small heights, and the symmetry
   programs' counts at their gates' sizes. Each with the command that made it.
2. One check, run by `make`, reproduces all of them and requires an exact
   match. It is seen failing on a planted change before it is trusted.
3. Every commit on `rewrite` passes that check and the full `make`.
4. A check that is edited is seen failing on a planted error again before
   the commit.
5. Behaviour changes are separate commits from renames and moves, so the
   reference check alone is the evidence for a move.
6. At the end, a fresh clone on gympie builds from the README alone and
   passes the same check. All of this work runs on gympie only; no other
   machine is used or contacted.

## Stop condition

Every in-scope file has been read through once and edited where it needs it,
and the reference check passes on gympie and on a fresh clone there.
