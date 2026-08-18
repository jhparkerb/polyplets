# Polyplets — counting king-connected lattice animals

Exact enumeration of **fixed polyplets** (polykings): connected sets of
cells on the square lattice where corner contact counts, OEIS
[A006770](https://oeis.org/A006770). This repository extended the
sequence from a(18) to

    a(40) = 56749893611764175164545926946127

with a(1)–a(22) confirmed digit-for-digit by two independent algorithms
sharing no counting logic (Redelmeier enumeration vs transfer matrix;
three-architecture fleet run completed 2026-07-16), together with its
symmetry companions (free A030222, one-sided A030233,
bilateral A030234, asymmetric A030235, free-non-polyomino A194596), a
hole-count stratification, fixed-height generating functions, and a
closed-form theory for the diagonals of two counting triangles (the laws'
polynomial shapes proved, the higher-level constants fitted and
holdout-validated).

**The full account is the report: [`paper/polyplets-report.tex`](paper/polyplets-report.tex)**
— results, methods ladder, and (critically) the confidence-tier system
that says exactly how well-verified each number is. Nothing in this repo
claims more than its tier.

## Layout

| where | what |
|---|---|
| `results/` | banked evidence: per-term ledgers `ns_a*/` (triangle, PROVENANCE, per-height rows, cost), analysis notes, b-file staging (`b*_upload.txt`) |
| `paper/` | the report + its self-contained claims checker `verify_claims.py` and fit/bound scripts |
| `cpp/` | Redelmeier enumerators (`g2_redelmeier.cpp`, Method A), column transfer matrix (`tma*`), symmetric transfer matrices (`sym/symtm.cpp`) |
| `core/`, `orchestrator/`, `worker/` | the production kink-carry transfer-matrix engine (Go orchestration, C++ kernels); design: `docs/engine-design.md` |
| `scripts/` | the general toolchain: production runners (`dalby_term.sh`, `symtm_run.sh`, `dmirror_strips.sh`), derivers (`derive_pk_fast.py`, `dmirror_diagonals.py`, `derive_related.py`), assembly (`dmirror_sum.py`, `dmirror_hybrid_sum.py`), independent confirmation (`g2_campaign.sh`) |
| `polyplets/` | the **Lean 4 formalization** (34 files, sorry-free): the peeling recursion, the diagonal-law shape theorem, and the grand form, with the production P_k pinned for k≤18 from two real-swept cells per level; axiom footprints are `#guard_msgs`-enforced. Status: `polyplets/PROOF-STATUS.md` |
| `tests/` | the gate suite (red-first, fail-closed; `make gates`) |
| `oeis/`, `submissions/` | staged OEIS extensions and new-sequence drafts (nothing auto-submitted) |
| `docs/` | reference docs (engineering standards, observability contract, job checklist, formats, glossary, engine + dmirror design), the proofs in `docs/proofs/`, and the campaign record — map: [`docs/README.md`](docs/README.md) |
| `papers/` | the cited literature (PDFs) |

One-shot launch scripts, per-term plans, and the research-log corpus that
produced all this were removed at project close (2026-07-06); they remain
in git history.

## Reproducing

```sh
make                 # builds engines into build/
make gates           # the full validation gate suite
python3 paper/verify_claims.py   # re-verifies the report's numeric claims
```

Small-scale end-to-end check, two independent algorithms:

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
- **T2** a(23)–a(38): one algorithm family, multiply decorrelated
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
