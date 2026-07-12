# Polyplets — counting king-connected lattice animals

Exact enumeration of **fixed polyplets** (polykings): connected sets of
cells on the square lattice where corner contact counts, OEIS
[A006770](https://oeis.org/A006770). This repository extended the
sequence from a(18) to

    a(36) = 24629107617723857143962968288

(the accompanying paper reports through a(34) = 515316838423862758858377704)

together with its symmetry companions (free A030222, one-sided A030233,
bilateral A030234, asymmetric A030235, free-non-polyomino A194596), a
hole-count stratification, fixed-height generating functions, and an
empirical closed-form theory for the diagonals of two counting triangles.

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
| `tests/` | the gate suite (red-first, fail-closed; `make gates`) |
| `oeis/`, `submissions/` | staged OEIS extensions and new-sequence drafts (nothing auto-submitted) |
| `docs/` | reference docs: engineering standards, observability contract, job checklist, formats, glossary, engine + dmirror design, proofs |
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
`results/ns_a*/PROVENANCE.md`.

## Confidence tiers (the short version)

- **T1** a(1)–a(20): two algorithms sharing no counting logic agree
  (independent whole-row Redelmeier confirmed a(20), 2026-07-11; a(22) running).
- **T2** a(21)–a(34): one algorithm family, multiply decorrelated
  (full-chain regression, cross-ISA recounts, held-out closed-form
  diagonal checks, mod-p consistency). a(34)'s top-cell diagonal now has its
  held-out check (a(35) supplies it).
- **T2⁻** a(35)–a(36): T2 minus a full same-heights cross-ISA re-verify
  (a(35) had only a partial cross-ISA; a(36)'s top cell awaits a(37)).
- **T3** n=33 companions: exact computation composed with empirically
  pinned but unproven quasi-polynomial formulas — labeled, never silently.

## Authorship

An amateur project by Jason H Parker, built in collaboration with an AI
assistant (Anthropic's Claude); the author owns all decisions and the
correctness of every claim. See the report's AI note for the division of
labor.
