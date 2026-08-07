# `paper/` — the manuscripts

This directory holds the papers this project is **writing**.

`papers/` — one letter different, and the source of every filename confusion in
this tree — holds the papers this project **reads**: the literature library, with
`papers/INDEX.txt` recording provenance and `papers/MISSING.md` recording what
could not be obtained and why. Nothing in `papers/` is ours. Nothing in `paper/`
is anyone else's.

`papers/` is gitignored in full (the top-level `.gitignore`'s first line:
"copyrighted papers stay local, never pushed"), so a fresh clone has `paper/`
and no `papers/`. Citations here that point into `papers/` are pointers into a
working copy, not into the published tree; bibliographic detail that a reader
needs is in `shared/refs.bib` instead.

Two neighbours complete the picture: `oeis/` holds OEIS submission drafts and
b-files, and `docs/` holds planning and proof notes. A proof note in
`docs/proofs/` is the *source material* for a manuscript here; it is not itself a
manuscript and is not written to be read by a stranger.

## The authorship split

`docs/publication-split.md` is the governing document. Its rule, in one
sentence: **there is never any ambiguity about whether a paper is jasonp's prose
or entirely machine-written.** No paper in this project is wholly a human's
work, and every paper says on page 1 which of the two categories it is in.

| | category | byline | disclosure block |
|---|---|---|---|
| **P** | jasonp wrote every sentence, has read every proof it states, and is responsible for its correctness | Jason Parker, alone | `\Pdisclosure` |
| **L** | written end to end by a large language model, mathematics included | per-paper decision, jasonp's | `\Ldisclosure` |

Both blocks live in `shared/disclosure.tex` and nowhere else, so that a paper
cannot quietly soften its own disclosure. The L block takes exactly one
argument: the per-result verification ledger — for each result, what warrants it
(Lean kernel, exact rational certificate, or labelled measurement) and how much
of it a human has checked. `docs/publication-split.md` §1 requires that ledger to
be **per result, not in aggregate**, and that is the whole point of the block.

## What is here

| file | paper | state |
|---|---|---|
| `technical-report.tex` | **P1** — Fixed polyplets through *a*(40) | in progress, jasonp's prose, roughly 40% built |
| `polyplets-report.tex` | — | superseded. A complete machine-written draft of P1's material, trimmed 2026-08-01. Under the split it cannot be lifted into `technical-report.tex` sentence by sentence; it is **source material and notes** |
| `L1-diagonal-law.tex` | **L1** — A diagonal law for row-local lattices | draft |
| `L3-lambda-bounds.tex` | **L3** — Bounds for the polyplet growth constant | draft |
| `L4-not-dfinite.tex` | **L4** — The by-height generating function is not D-finite | draft |

Planned and not yet drafted: **P2** (two stratifications of A006770), **P3**
(king animals by convexity and directedness), **L2** (the mod-3 arithmetic of the
height triangle), **L5** (convex king animals), **L6** (perimeter gradings).
L2 and L6 each owe a novelty sweep before they are written, and L6 is
additionally gated on compute; `docs/publication-split.md` §5 has the details.

The numbering is `docs/publication-split.md`'s and is not dense — L1, L3 and L4
were drafted first because their novelty verdicts came back clean and because P2
and P3 cite them.

## Who may edit what

**`technical-report.tex` is read-only to the machine.** It is jasonp's prose,
under the P disclosure, and a machine-written sentence in it would falsify that
disclosure. Claude does not edit it — not to fix a typo, not to reformat, not to
revert its own earlier change — without explicit per-instance direction. It also
deliberately does not `\input shared/preamble.tex`: the duplicated preamble is
the price of leaving the file alone.

Everything else here is machine-writable.

## Building

    make papers                        # every manuscript
    make paper-L3-lambda-bounds        # one, by file stem
    make papers-verify                 # the numeric verifiers
    make papers-clean

or equivalently `make -C paper`, `make -C paper L1-diagonal-law.pdf`, and so on.
`make -C paper list` prints what will be built.

The build is `pdflatex` three times with a conditional `bibtex` between the
first and second passes — conditional because the two older manuscripts still
carry inline `thebibliography` environments while the L papers use
`shared/refs.bib`. A missing TeX installation fails with an install command
rather than with `command not found`.

`make papers` is **not** part of `make gates`. The gate suite has to stay
runnable on dalby and ayr, which are compute boxes with no TeX.

## Verifying

Transcribed numbers rot. Each manuscript has, or should have, a verifier that
parses it and checks its printed numbers against banked results in `results/`:

| verifier | manuscript | needs |
|---|---|---|
| `verify_technical_report.py` | `technical-report.tex` | `results/ns_a40/`, b-files, `results/holes_n18.txt` |
| `verify_l_papers.py` | `L1`, `L3`, `L4` | `results/strip_mu_certificates.log`, `results/triangle.txt` |
| `verify_claims.py` | `polyplets-report.tex` | `build/g2` — so it is not in `make papers-verify`; run it explicitly |

Each is red-first: it fails on a manuscript whose tables have drifted, and each
carries at least one control that must fail.

## Scripts

`atom_degrees.py`, `gf_bound.py` and `lambda_fit.py` generate figures and fitted
numbers quoted by the manuscripts. `restructure-plan.md`,
`related-work-notes.md`, `technical-report-gaps.md` and
`polyplets-report-cuts.md` are working notes, not manuscripts;
`polyplets-report-cuts.md` in particular is the audit trail of the 2026-08-01
trim and is kept for that reason.
