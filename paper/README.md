# `paper/` — the manuscripts

The papers this project writes. The papers it reads are in `literature/`.
`docs/publication-split.md` says how each manuscript is labelled: the
technical report is the author's prose, and the six L papers were written
end to end by a language model and have not been read for correctness by
anyone. Both disclosure blocks are in `shared/disclosure.tex` and nowhere
else, so a paper cannot soften its own.

| file | what | state |
|---|---|---|
| `technical-report.tex` | Fixed polyplets through a(40) | the author's prose; not edited by the machine |
| `L1-diagonal-law.tex` | A diagonal law for row-local lattices, and the mod-3 arithmetic of the king instance | draft, 23 pp |
| `L3-lambda-bounds.tex` | A certified two-sided bound for λ | draft, 13 pp |
| `L4-not-dfinite.tex` | An arithmetic obstruction to D-finiteness | draft, 10 pp |
| `L5-convex-polyplets.tex` | Convex polyplets: by area, by semiperimeter, and the growth constant | draft, 21 pp |
| `L6-perimeter-gradings.tex` | Perimeter gradings of lattice animals | draft, 14 pp |
| `L8-below-onset.tex` | Below the onset: the error term of the diagonal formula | draft, 15 pp |

The numbering has gaps; `docs/l-papers-record.md` says why, and records the
literature searches each paper's novelty section relies on. Three things a
reader of the L papers should know from those searches: L6's square-lattice
column reproduces published work (Asinowski, Barequet and Zheng), attributed
in place, and only its king column and minimum end are new; L8's first half
tests little, since its defect is defined relative to this project's own
diagonal law; and L5 depends on a block decomposition and mirror equality
that Gouyou-Beauchamps and Leroux have for the honeycomb lattice, cited at
both places and in its related work. Of L6's four predictions for `k = 6`,
three held and the fourth, a closed form for the Φ₂ leading diagonal, was
refuted and withdrawn.

`related-work-notes.md`, `technical-report-cites.md` and
`technical-report-gaps.md` are working notes for the technical report, not
manuscripts. `technical-report.bib` is its bibliography; the `.tex` carries
no `\cite` until the author places them. `atom_degrees.py`, `gf_bound.py`
and `lambda_fit.py` generate figures and fitted numbers the manuscripts
quote.

## Building

    make papers                        # every manuscript
    make paper-L3-lambda-bounds        # one, by file stem
    make papers-verify                 # the numeric verifiers
    make papers-clean

`pdflatex` three times with `bibtex` between the first and second passes
when the `.aux` asks for it. A missing TeX installation fails with an
install command. `make papers` is not part of `make`, which has to run on
machines without TeX.

## Verifying

Each manuscript has a verifier that parses it and checks its printed numbers
against the data in `results/`:

| verifier | manuscript | reads |
|---|---|---|
| `verify_technical_report.py` | `technical-report.tex`: its tables and the numbers in its prose | `results/ns_a40/`, b-files, `results/holes_n18.txt`, `results/a41/`, `results/coloring-recount/rows41/` |
| `verify_l_papers.py` | L1, L3, L4, L6; not L5 or L8 | `results/strip_mu_certificates.log`, `results/triangle.txt`, `results/perimmin_square8_p48_r6.txt`, `results/perimdefect_square{4,8}_n78_k6.txt` |

Each fails on a manuscript whose tables have drifted and carries a control
that must fail. How much each reads is measured, not assumed:
`tests/l_paper_coverage_audit.py` perturbs every numeric literal in a copy
and re-runs the verifier. For the technical report, `tests/gate_p_paper_verifier.py`
runs that on every push. For the L papers the answer
(`results/l-paper-verifier-coverage.md`) is 74 of 531 literals; L5 and L8
are 0 of 144 and 0 of 69, so not one number either prints is read by
anything.
