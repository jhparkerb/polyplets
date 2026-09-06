# Polyplets — counting king-connected lattice animals

Exact enumeration of **fixed polyplets** (polykings): connected sets of
cells on the square lattice where corner contact counts, OEIS
[A006770](https://oeis.org/A006770). This repository extended the
sequence from a(18) to

    a(40) = 56749893611764175164545926946127

and, with the closed forms of the height triangle standing in for the two
tallest heights,

    a(41) = 393811462683918679824582849262105

(`results/a41/PROVENANCE.md`; heights 1–20 enumerated, 21–41 from the closed
forms). a(1)–a(22) are confirmed exactly by two independent algorithms
sharing no counting logic (Redelmeier enumeration vs transfer matrix;
three-architecture fleet run completed 2026-07-16), together with its
symmetry companions (free A030222, one-sided A030233,
bilateral A030234, asymmetric A030235, free-non-polyomino A194596), a
hole-count stratification, fixed-height generating functions, and a
closed-form theory for the diagonals of two counting triangles (the laws'
polynomial shapes proved, the higher-level constants fitted and
holdout-validated).

**Why believe the number:** one per-cell table,
[`results/provenance-table.md`](results/provenance-table.md), says for every
cell of the triangle what confirms it and by which independent source. It is
generated, and `make gate-provenance` fails if any figure in it drifts from the
banked rows — verified fail-closed, not just asserted: planting a grown triangle
turns all six of its figures red
([`docs/engine-record.md`](docs/engine-record.md) section 8.4, which plants
into each of the 33 gates the staleness it should catch and records which
caught it; the rest of that file is the engine's measurement log and is not
required reading).

**The report** is [`paper/technical-report-draft.tex`](paper/technical-report-draft.tex),
ten pages, machine-written under the authorship rules of `docs/publication-split.md`
and approved by the author on 2026-09-06: definitions, the tables, the methods,
and what stands behind each term. Its tables are the banked values, and
`paper/verify_technical_report.py` re-reads every one of them, and every number
in its prose, from `results/` (3499 checks). The perturbation audit that
measures what a verifier actually reads has been run on `technical-report.tex`
(293 of 294 literals guarded, `results/p-paper-verifier-coverage.md`) and not
yet on the draft. Six shorter papers on the analytic and arithmetic side are
drafts. Each states a per-result verification ledger, and every one of those
ledgers currently reads "human verification: none";
`results/l-paper-verifier-coverage.md` measures how much of each is
machine-checked, which is 74 of 531 numbers, with L5 and L8 at zero.
`paper/README.md` is their index. Nothing in this repo claims more
than its tier.

**Read these five files first:** `paper/technical-report-draft.tex` (or its
PDF), `results/confidence.md` (how well each term is supported, in plain
terms), `results/provenance-table.md` (which program produced each entry of
the triangle), `docs/engine-record.md` (the enumerator as it ran, with the
measurements), and `docs/proofs/diagonal-law.md` (the closed form the tall
heights rest on). Everything else is record, and `docs/glossary.md` decodes
the names this project gave its own machinery.

## Layout

| where | what |
|---|---|
| `results/` | the evidence and the record of what it shows: the triangle, the per-term ledgers `ns_a*/` and `a41/`, and fifteen result documents — index: [`results/README.md`](results/README.md) |
| `paper/` | the manuscripts — the report (`technical-report-draft.tex`), jasonp's own partial `technical-report.tex`, and the six L papers — with the self-contained checkers `verify_technical_report.py` and `verify_l_papers.py`; index and authorship split: [`paper/README.md`](paper/README.md) |
| `papers/` | the cited literature, one letter away from `paper/` and the opposite thing: work this project reads, not work it writes. The PDFs are gitignored — copyrighted work stays local — so a clone gets `INDEX.txt` (provenance), `MISSING.md` (what could not be obtained, and why), `README.md`, `refs-transfer-matrix.md` and `polyplets-2024-2026.bib`, and none of the PDFs |
| `docs/` | reference, proofs and record: the engine, the formats, the glossary, the proofs in `docs/proofs/`, the audits in `docs/audits/`, and the project's own working state in `docs/handoff.md` — index: [`docs/README.md`](docs/README.md) |
| `core/`, `orchestrator/`, `worker/` | the production kink-carry transfer-matrix engine (Go orchestration, C++ kernels); as it ran: `docs/engine-record.md`; the 2026-06 build design of the run-file layer it grew out of: `docs/engine-design.md` |
| `cpp/` | the standalone C++ programs: Redelmeier enumerators (`g2_redelmeier.cpp`, Method A), the column transfer matrix (`tma*`), the coloring second source (`motley_par.cpp`), symmetric transfer matrices (`sym/symtm.cpp`) |
| `scripts/` | the general toolchain: production runners (`dalby_term.sh`, `symtm_run.sh`), derivers (`derive_pk_fast.py`, `derive_related.py`), assembly and combination, the naive oracles the gates check against (`g1_naive.py`, `symcount.py`), and the observability runtime `obs.py` |
| `experiments/` | one-shot derivations and probes, one file per question asked. Some are gate inputs (`grep experiments/ Makefile` says which); the rest are the working behind a paragraph in `results/`, kept for reproduction, not for reuse |
| `tests/` | the gate suite: red-first, fail-closed, `make gates`. Python and one C++ unit |
| `tests/engine/` | the C++ gate drivers and unit tests of the production engine, built by `make` into `build/ns/` |
| `verify/` | a small Go tool and package that reads run artifacts independently of the engine: CRC and architecture-fitness checks |
| `fixtures/` | external ground truth — OEIS b-files with their checksums — that most gates compare against |
| `polyplets/` | the **Lean 4 formalization** (86 sorry-free modules, plus one deliberately unproved skeleton kept outside the build): the peeling recursion, the diagonal-law shape theorem, and the grand form, with the production P_k pinned for k≤18 from two real-swept cells per level; axiom footprints are `#guard_msgs`-enforced. Status: `polyplets/PROOF-STATUS.md` |
| `oeis/` | staged OEIS extensions, b-files and new-sequence drafts, `wave2/` included. Nothing has been submitted and nothing is auto-submitted |

The repository is called polyominoes for historical reasons; the object it
counts is the polyplet, a polyomino whose cells may touch at a corner.

One-shot launch scripts, per-term plans, and the research-log corpus that
produced all this were removed when the enumeration ladder closed at a(40)
(2026-07-06), and most of the campaign records went in the consolidation of
2026-09-06 (`docs/consolidation-plan.md`); everything remains in git history.
The ladder is what closed, not the project: a(41), the analytic, arithmetic
and perimeter work all postdate it.

## Reproducing

**One command, from nothing but the clone:**

```sh
make && scripts/dalby_term.sh 26
```

(The runner is named for the machine it was tuned on; it reads its core count
and its repository root from the box it is on, and runs anywhere.)

That prints `a(26) = 102607513847014153892` and, before it does, re-derives
a(1)–a(25) and checks every one against `fixtures/b006770.txt` and the banked
per-term ledgers. **23 seconds** on 32 cores — the run that first produced
a(26), on 2026-07-02, took 4066 s on 80; the difference is the kink-carry
kernel that replaced it. `scripts/dalby_term.sh 24` is the same thing in 8 s if
you want to see it work before committing a minute.

The rest, with wall times measured on a clean clone on 2026-08-19 (ayr: 32
cores, g++ 12.2, TeX Live 2022, no clang and no Lean):

```sh
make                       # the gate suite; there is no separate build
                           # step, because each gate builds what it needs. 423 s
make ns-gates              # the production engine's own suite. 787 s
make -C paper              # the 8 PDFs, which are gitignored
python3 paper/verify_l_papers.py         # 336 checks, 23 of them RED controls
python3 paper/verify_technical_report.py # 3499 checks, the report's tables and prose
```

Two independent algorithms on the same small values:

```sh
build/g2 square8 12            # Method A: Redelmeier, counts a(1..12)
scripts/g2_campaign.sh 16 8    # same, split across 8 workers
```

against the transfer-matrix engine (see `docs/engine-design.md` and
`scripts/dalby_term.sh` for the production configuration). Per-term
provenance — which binary, which host, which validations — is in
`results/ns_a*/PROVENANCE.md`, and the one per-cell table of what is
confirmed by which independent source is
[`results/provenance-table.md`](results/provenance-table.md), generated and
gated (`make gate-provenance`) so it cannot drift from the banked rows.

## Confidence tiers (the short version)

- **T1** a(1)–a(22): two algorithms sharing no counting logic agree
  (whole-row Redelmeier fleet vs transfer matrix, completed 2026-07-16).
- **T2** a(23)–a(38): one algorithm family, multiply decorrelated. Whole-row
  double enumeration stops at 22, but the cells do not: through a(35) every
  cell is either recounted by the coloring second source or given by a formula
  pinned on that source's own cells, and through a(39) the same holds row by
  row (`results/confidence.md` items 1 and 2). The tier is about whole rows
  (full-chain regression on every run; cross-architecture recounts where
  run — full at a(34), partial at a(35), split at a(36), none for
  a(37)–a(38); and the held-out closed-form diagonal chain
  P₁₅→T(33,18), P₁₆→T(35,19), P₁₇→T(37,20), each formula predicting a
  cell of a term computed after it was pinned — with P₁₈'s first holdout,
  T(39,21), arriving as one row of the a(40) H21 sweep below rather than
  as a separate event).
- **T2⁻** a(39)–a(40): T2 minus the held-out top-cell check — their top
  real cells sit on diagonal k=19, whose closed form has no independent
  holdout and, the sequence closing at a(40), never will. Narrowed by the
  a(40) run's real H21 sweep reproducing nineteen closed-form rows in the
  same stroke that produced T(40,21), and by a standalone byte-identical
  re-sweep of the H20 column.
- **T3** n=33 companions: exact computation composed with empirically
  pinned but unproven quasi-polynomial formulas — labeled, never silently.

## Authorship

An amateur project by Jason H Parker, built in collaboration with an AI
assistant (Anthropic's Claude); the author owns all decisions and the
correctness of every claim. See the report's AI note for the division of
labor. AI assistance spans essentially the entire commit history: most
commits carry a `Co-Authored-By: Claude` trailer, but the trailer was
not backfilled onto the minority that lack one, so treat the history as
AI-assisted throughout rather than inferring per-commit provenance from
trailers alone.
