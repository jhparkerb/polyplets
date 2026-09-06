# Polyplets — counting king-connected lattice animals

A **polyplet** is a connected set of cells on the square lattice where corner
contact counts, and `a(n)` counts those with `n` cells up to translation: OEIS
[A006770](https://oeis.org/A006770). This project took the sequence from
`a(18)` to

    a(40) = 56749893611764175164545926946127
    a(41) = 393811462683918679824582849262105

`a(40)` is enumerated. `a(41)` is enumerated for heights 1 to 20 and comes from
proved closed forms above that.

**Start here.** The ten-page report,
[`paper/technical-report.tex`](paper/technical-report.tex), states the results
and what stands behind each one. Then
[`results/confidence.md`](results/confidence.md), which says in plain terms how
far each term can be trusted.

**Why believe the numbers.** `a(1)` to `a(22)` are computed twice, by two
programs sharing no counting logic. Above that, the check is per cell rather
than per term: [`results/provenance-table.md`](results/provenance-table.md)
says for every entry of the height triangle what confirms it and by which
independent source. Three entries in the whole table rest on a single
enumeration, and that table names them.

The verification is itself checked. Every number the report prints is read back
out of the stored results by `paper/verify_technical_report.py`, 3406 checks.
The provenance table is generated, and `make gate-provenance` fails if any
figure in it drifts. Both are fail-closed by measurement, not by assertion:
planting a grown triangle turns all six figures red, and section 8.4 of
[`docs/engine-record.md`](docs/engine-record.md) plants a failure into each of
the 33 gates and records which caught it.

More, in decreasing order of how much you probably want it:
[`results/README.md`](results/README.md) indexes the mathematics, from the
closed form the tall heights rest on to the routes that were tried and closed.
Six shorter papers cover the analytic and arithmetic side; `paper/README.md` is
their index, and each is a draft whose verification ledger reads "human
verification: none". `docs/README.md` maps the engine, the proofs and the
project's own record. `docs/glossary.md` decodes the names this project gave
its own machinery.

## Layout

| where | what |
|---|---|
| `results/` | the evidence and the record of what it shows: the triangle, the per-term ledgers `ns_a*/` and `a41/`, and fifteen result documents — index: [`results/README.md`](results/README.md) |
| `paper/` | the manuscripts — the report (`technical-report.tex`) and the six L papers — with the self-contained checkers `verify_technical_report.py` and `verify_l_papers.py`; index and authorship split: [`paper/README.md`](paper/README.md) |
| `literature/` | the cited literature: work this project reads, not work it writes (it was `papers/` until 2026-09-06). The PDFs are gitignored — copyrighted work stays local — so a clone gets `INDEX.txt` (provenance), `MISSING.md` (what could not be obtained, and why), `README.md`, `refs-transfer-matrix.md` and `polyplets-2024-2026.bib`, and none of the PDFs |
| `docs/` | reference, proofs and record: the engine, the formats, the glossary, the proofs in `docs/proofs/`, the audits in `docs/audits/`, and the project's own working state in `docs/handoff.md` — index: [`docs/README.md`](docs/README.md) |
| `core/`, `orchestrator/`, `worker/` | the production kink-carry transfer-matrix engine (Go orchestration, C++ kernels); as it ran: `docs/engine-record.md`; the 2026-06 build design of the run-file layer it grew out of: `docs/engine-design.md` |
| `cpp/` | the standalone C++ programs: Redelmeier enumerators (`g2_redelmeier.cpp`, Method A), the column transfer matrix (`tma*`), the coloring second source (`motley_par.cpp`), symmetric transfer matrices (`sym/symtm.cpp`) |
| `scripts/` | the general toolchain: production runners (`term.sh`, `symtm_run.sh`), derivers (`derive_pk_fast.py`, `derive_related.py`), assembly and combination, the naive oracles the gates check against (`g1_naive.py`, `symcount.py`), and the observability runtime `obs.py` |
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
make && scripts/term.sh 26
```

That prints `a(26) = 102607513847014153892` and, before it does, re-derives
`a(1)` through `a(25)` and checks every one against `fixtures/b006770.txt` and
the banked per-term ledgers. It takes 23 seconds on 32 cores. Use
`scripts/term.sh 24` to see it work in 8 seconds instead.

The rest, with wall times measured on a clean clone on 2026-08-19 (ayr: 32
cores, g++ 12.2, TeX Live 2022, no clang and no Lean):

```sh
make                       # the gate suite; there is no separate build
                           # step, because each gate builds what it needs. 423 s
make ns-gates              # the production engine's own suite. 787 s
make -C paper              # the 8 PDFs, which are gitignored
python3 paper/verify_l_papers.py         # 336 checks, 23 of them RED controls
python3 paper/verify_technical_report.py # 3406 checks, the report's tables and prose
```

Two independent algorithms on the same small values:

```sh
build/g2 square8 12            # Method A: Redelmeier, counts a(1..12)
scripts/g2_campaign.sh 16 8    # same, split across 8 workers
```

against the transfer-matrix engine (see `docs/engine-design.md` and
`scripts/term.sh` for the production configuration). Per-term
provenance — which binary, which host, which validations — is in
`results/ns_a*/PROVENANCE.md`, and the one per-cell table of what is
confirmed by which independent source is
[`results/provenance-table.md`](results/provenance-table.md), generated and
gated (`make gate-provenance`) so it cannot drift from the banked rows.

## Confidence tiers (the short version)

Four tiers, and `results/confidence.md` is the long version.

- **T1** `a(1)`–`a(22)`: two algorithms sharing no counting logic agree, whole
  row by whole row.
- **T2** `a(23)`–`a(38)`: one algorithm family, decorrelated many ways. Whole-row
  double enumeration stops at 22, but the cells do not. Through `a(35)` every
  cell is either recounted by the coloring second source or given by a formula
  pinned on that source's own cells, and through `a(39)` the same holds row by
  row.
- **T2⁻** `a(39)`–`a(40)`: T2 without the held-out top-cell check. Their top
  real cells sit on the diagonal `k = 19`, whose closed form has no independent
  holdout and, the sequence closing at `a(40)`, never will.
- **T3** the `n = 33` companions: exact computation composed with pinned but
  unproven quasi-polynomial formulas. Labeled, never silently.

The five companion sequences are extended too: free A030222, one-sided A030233,
bilateral A030234, asymmetric A030235, and the free polyplets that are not
polyominoes A194596. So is the hole-count stratification, and the triangle
`T(n,H)` itself is proposed as a new entry. Nothing has been submitted.

## License

Apache License 2.0, `LICENSE` at the root: code, proofs, records and
manuscripts alike. The Lean modules carry the header form of the same grant.
The one exception is `literature/`, which is other people's copyrighted work,
is gitignored, and is not distributed with this repository at all.

## Authorship

An amateur project by Jason H Parker, built in collaboration with an AI
assistant (Anthropic's Claude); the author owns all decisions and the
correctness of every claim. See the report's AI note for the division of
labor. AI assistance spans essentially the entire commit history: most
commits carry a `Co-Authored-By: Claude` trailer, but the trailer was
not backfilled onto the minority that lack one, so treat the history as
AI-assisted throughout rather than inferring per-commit provenance from
trailers alone.
