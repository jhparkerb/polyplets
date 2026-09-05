# Where `paper/technical-report.tex` would take a citation

2026-09-05, `paper/technical-report-gaps.md` B3. The keys are in
`paper/technical-report.bib`, every entry checked against the copy in `papers/`
(or, for OEIS, the live entry). The `.tex` is jasonp's and is not edited here:
this file says which sentence, which key, and why, and he places the `\cite`.
Line numbers are those of the 2026-09-04 working tree.

Nothing on the list is unfindable, so `papers/MISSING.md` gains no entry from
this pass.

| tex line | sentence (abridged) | key(s) | why |
|---|---|---|---|
| 37 | "The king-lattice polyplet sequence A006770 has been expanded through a(40)" | `oeisA006770`, `oeis` | the sequence; the encyclopedia once, at first mention |
| 47 | "a(19) was computed directly with Redelmeier enumeration" | `redelmeier1981` | the algorithm |
| 47-48 | "a(20)–a(23) were computed via transfer matrix" | `jensen2001` | the finite-lattice transfer-matrix method for animals; `jensen2003` if the parallel implementation is mentioned |
| 51-52 | "for n ≤ 22, transfer matrix and Redelmeier enumeration agree" | `redelmeier1981` (already cited at 47; no second cite needed) | — |
| 54 | "pass checks based on Burnsides congruences" | `stanley2012` (optional) | Burnside's lemma, if a reference is wanted; Redelmeier §5 counts the symmetry classes the same way |
| 70 | "Fixed polyplets are distinct up to translation (A006770)" | `oeisA006770` | the `\href` already points there; a `\cite` makes it a bibliography entry |
| 72 | "One-sided ... (A030233)" | `oeisA030233` | |
| 74 | "Free ... (A030222)" | `oeisA030222` | |
| 78 | "bilateral ... (A030234)" | `oeisA030234` | |
| 79 | "asymmetric ... (A030235)" | `oeisA030235` | |
| 166 | "free polyplets that are not polyominoes (A194596)" | `oeisA194596` | |
| 150 (Table 1 caption) | "Terms 1–18 match A006770" | `mertens1990`, `tremblayVernay2024` | where those 18 came from: Redelmeier's unpublished figures, Mertens's Table 1, and Tremblay–Vernay for a(18) — the OEIS entry's own %C/%H lines name all three |
| 289 | "Growth rate: a(n)^{1/n} → λ" | `klarner1967`, `madras1999` | Klarner: the limit exists (supermultiplicativity); Madras: the ratio a(n+1)/a(n) converges to the same λ, which is what "checkable from Table 1" needs if the ratios are what a reader checks. The CLAUDE comment at 276-288 already names Madras |
| 289 (if an upper-bound clause is added) | — | `klarnerRivest1973` | the transfer-matrix upper-bound procedure; `paper/L3-lambda-bounds.tex` is where the bounds live |
| 294-296 | "only terms through n = 22 could be confirmed with this software" | `barequetBenShachar2026` | places the polyplet frontier beside the polyomino one (n = 70 there); also the reference point for "Redelmeier is O(a(n))" |
| 298-302 | "Transfer matrix method ... freezing the left-hand side ..." | `jensen2001` | same as line 47; cite once, here or there |
| (none yet) | the king lattice as a setting for enumeration | `bacher2015` | the one prior enumeration paper on the king lattice (directed animals); a Related-work sentence if one is written |

## What to add to the preamble

    \bibliographystyle{plain}
    ...
    \bibliography{technical-report}      % before \end{document}

`paper/Makefile` runs bibtex when the `.aux` carries both a `\bibdata` line and
a `\citation`, so the first `\cite` turns the bibliography on.

## Not cited, and why

- Redelmeier's polyplet counts themselves were never published (OEIS A006770
  credits them as personal communication); `redelmeier1981` is cited for the
  algorithm, not for the terms.
- Klarner–Rivest is offered, not required: the report states no upper bound.
- The L papers' shared bibliography, `paper/shared/refs.bib`, holds the same
  entries under the same keys where they overlap (`redelmeier1981`,
  `klarner1967`, `klarnerRivest1973`, `jensen2001`, `madras1999`, `oeis`);
  `bacher2015` is `@misc` here where `refs.bib` has it as `@article` with the
  arXiv id in the journal field. Reconciling that is a `refs.bib` change, not
  made here.
