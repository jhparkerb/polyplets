# `paper/` — the manuscripts

This directory holds the papers this project is **writing**.

`papers/` — one letter different, and the source of every filename confusion in
this tree — holds the papers this project **reads**: the literature library, with
`papers/INDEX.txt` recording provenance and `papers/MISSING.md` recording what
could not be obtained and why. Nothing in `papers/` is ours. Nothing in `paper/`
is anyone else's.

The top-level `.gitignore` starts by ignoring `papers/` — "copyrighted papers stay
local, never pushed" — so the PDFs themselves never leave this machine. Five
text files there are tracked anyway: `INDEX.txt`, `MISSING.md`, `README.md`,
`refs-transfer-matrix.md` and `polyplets-2024-2026.bib`. So a fresh clone gets
the *record* of the library and none of its contents. Citations in `paper/` that
point at a PDF under `papers/` are pointers into a working copy, not into the
published tree;
bibliographic detail a reader actually needs is in `shared/refs.bib`.

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
| `L1-diagonal-law.tex` | **L1** — A diagonal law for row-local lattices | draft, 14pp |
| `L2-ternary-spine.tex` | **L2** — The mod-3 arithmetic of the height triangle | draft, 10pp — swept 2026-08-18, no collision |
| `L3-lambda-bounds.tex` | **L3** — A certified two-sided bound for λ | draft, 13pp |
| `L4-not-dfinite.tex` | **L4** — An arithmetic obstruction to D-finiteness | draft, 10pp |
| `L5-convex-polyplets.tex` | **L5** — Convex polyplets | draft, 14pp |
| `L6-perimeter-gradings.tex` | **L6** — Perimeter gradings of lattice animals | draft, 12pp — compute gate **cleared** 2026-08-18 |
| `L7-subdominant-amplitude.tex` | **L7** — The subdominant exponential and the amplitude ratio | draft, 10pp |
| `L8-below-onset.tex` | **L8** — Below the onset: the diagonal law's error term | draft, 9pp — swept 2026-08-18, **weak negative**; absorbed the external check 2026-08-22 |
| `L9-cutcount-identity.tex` | **L9** — A cancellation identity for scan-order colourings | draft, 6pp — **the identity is not new** |
| `L10-undertow.tex` | **L10** — Undertow: pinning a diagonal tower from cells below its onset | draft, 7pp — swept 2026-08-23, **near neighbour found** |

Every L paper carries a loud draft banner, because every one of their
verification ledgers currently reads "human verification: none". All ten have
had a literature-priority pass, dated after their own drafting: nine in
`docs/priority-passes-2026-08-18.md` and L10's in
`docs/priority-pass-L10-2026-08-23.md`. **Four** carry a second banner because
of what that pass found:

- **L9's identity is not new.** It is the Fortuin–Kasteleyn/Potts
  correspondence — evaluating $q^c$ by colouring components instead of tracking
  them — specialised to site clusters in scan order, with Hoshen–Kopelman (1976)
  as the unsigned ancestor of the labelling. The paper claims no theorem. What
  survives is the specific rule and the proof that its window suffices.
- **L6's square-lattice column reproduces published work.** Asinowski, Barequet
  and Zheng have the defect identity $k = e + 2f$ and the theorem that each
  fixed-defect generating function is rational with cyclotomic denominator; both
  are attributed in place, to the ANALCO 2018 paper obtained 2026-08-18 rather
  than to the slides. The king column, the onset formula, the two-lattice
  universality, the coefficient triangle and the whole minimum end survive.
- **L8's negative is weak**, and page 1 says so: the object it studies is defined
  relative to this project's own diagonal law, so a pass over it tests little.
- **L10's manoeuvre is standard practice next door.** Correcting a finite-size
  calculation by a term describing how far it is wrong, so as to use it beyond
  where it is exact, is what Baxter–Guttmann (1988) and Jensen–Guttmann do for
  directed-percolation series. L10 cites them and claims only the combination:
  there the corrections are conjectured (a Catalan ansatz), here they are
  computed ab initio, and the count of unknowns per level is proved rather than
  assumed.
  Its new §​square-lattice section postdates the pass and has not been swept,
  which its own novelty section states.

- **L6's compute gate is cleared** (2026-08-18). Both *k* = 6 censuses landed;
  three of its four predictions held and the fourth, the Φ₂ leading diagonal's
  closed form, was refuted and is withdrawn. The paper no longer carries a
  do-not-submit banner.

Planned and not yet drafted: **P2** (two stratifications of A006770) and **P3**
(king animals by convexity and directedness). Both are jasonp's prose and are
not the machine's to write.

The numbering is `docs/publication-split.md`'s through L6; L7 was carved out of
L5, and L8 and L9 were added 2026-08-18 for material that postdates that
document (the below-onset campaign, and the cut-count identity behind the
second-source engine). **L10 was added 2026-08-22** on jasonp's decision that
the Undertow material — the application of the below-onset defects, which is
what produced a(41) — should stand as its own paper rather than join L8 or wait
for P1. L8 keeps the defect mathematics; L10 uses it.

L1, L3 and L4 were drafted first because their novelty
verdicts came back clean and because P2 and P3 cite them.

**The standing literature-priority rule applies to all ten.** Adopted
2026-08-17 after a result was derived at length and found afterwards to be
published: a priority pass runs before anything is called new. Three papers here
have had no pass at all and say so; the rest carry the verdicts of the N1–N6
sweeps, which predate their own later sections.

**L5 has a standing attribution requirement.** Gouyou-Beauchamps and Leroux
(FPSAC 2004, §2.3) have its block decomposition and its mirror equality, for
convex polyominoes on the honeycomb lattice. `docs/publication-split.md` requires
that citation in three places — at Lemma 1, at Proposition 9, and in the
related-work section. A revision that drops one of them is a regression.

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
| `verify_l_papers.py` | `L1`, `L3`, `L4`, `L6` | `results/strip_mu_certificates.log`, `results/triangle.txt`, `results/perimmin_square8_p48_r6.txt`, `results/perimdefect_square{4,8}_n78_k6.txt` |
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
