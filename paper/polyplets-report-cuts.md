# polyplets-report.tex — trim log, phase 1 (sections)

Adversarial trim: a remover proposed section-level cuts, a defender contested
them, a referee ruled with a slight bias toward removal. This log records what
left, why, and where anything load-bearing landed. Line spans are positions in
the pre-trim file (1437 lines, 77,244 bytes at commit d9901d0).

Gate on every commit: `pdflatex -output-directory=paper paper/polyplets-report.tex`
run twice, zero errors and zero undefined references/citations; `python3
paper/verify_claims.py` passing; `wc -c` strictly decreasing.

## Commit 1 — uncontested batch (S1, S2, S3, S4, S5, S9)

### S1 — Appendix A, "Computational profile" (1265–1300, incl. `\appendix`)
Wall/core-hour/RSS/disk figures for a(37)–a(40) (tab:costsladder) plus the
diagonal-mirror farm costs.
**Argument that won:** it reports no claim of the paper, and its own last
sentence concedes the authoritative version is elsewhere ("Full per-run
profiles ... are in the repository's provenance ledgers"). Its one load-bearing
assertion, disk-not-RAM as the binding resource, is already in Method C
("the binding resource is disk bandwidth rather than memory").
**Salvage:** none. The optional hardware roster was skipped by ruling.
**Refs resolved:** the sole inbound `\ref{sec:profile}` (in Reach and limits)
died with S3; `tab:costsladder` was never referenced.

### S2 — §4.5, "Method E: diagonal closed forms" (560–574)
A fifth "method" that was a pointer to the diagonal law.
**Argument that won:** all three of its claims are stated more fully elsewhere —
the injection mechanics in §4.3 ("Which cells are computed and which are
injected", with the exact percentages), the two-point fit and holdout in §6.1,
and the epistemic point (a holdout checks the engine, not the law) verbatim in
§6.1's "their held-out hits stay load-bearing as checks of the *engine* rather
than of the law".
**Salvage:** none needed. Per the ruling's condition the §4 preamble keeps the
*why* of injection: "Four counting methods (A–D) computed these numbers, with
closed forms (Section~\ref{sec:heightdiag}) replacing the top diagonals, a
sweep's most expensive and least populated cells".
**Refs resolved:** §6.1's `\ref{sec:methodE}` retargeted to `sec:methodC`, where
the injection boundary is actually specified.

### S3 — §10, "Reach and limits" (1225–1236)
A closing section on sweep-height cost and the verification limit.
**Argument that won:** two of its three sentences recapitulate — disk-binding is
§4.3, and "the frontier is always one term ahead of its own closed-form
certification / the sequence closes at a(40)" is tab:tiers' T2⁻ row and §5's
held-out bullet, which name the diagonal and the two cells.
**Salvage:** the per-term sweep-height ladder was the one non-duplicated fact
(§4.3 gave only two of its four rungs). Moved verbatim, all four rungs, into
§4.3's injection paragraph, minus the appendix reference: "Method C's cost is
set by its tallest surviving sweep height, which advanced only as each new
diagonal was certified: H=18 through a(34), H=19 for a(35)–a(37), H=20 for
a(38)–a(39), H=21 for a(40)."

### S4 — §11, "Data and code availability" (1237–1248)
Repository inventory.
**Argument that won:** every artifact it lists is already named at its point of
use (eight inline `\texttt{}` paths), the abstract already closes with "all
code, data, and a claim-verifier are released", and its last two sentences
restate §5's Hygiene bullet.
**Salvage (mandatory per ruling):** a two-line `\paragraph{Availability.}` at the
end of §5, naming the per-height triangle rows for every term through n=40 with
their provenance ledgers (this is what makes §4.3's "sum Table 4's rows H≤21
against the banked per-height data" actionable), the b-files, the source and
gates, and the claim-verifier. Placed at the end of §5 rather than at the end of
the document: with the closing sections gone the last body section is the
not-D-finite proof, and a dangling availability note would read as belonging to
it.

### S5 — §12, "Author's note: use of AI" (1249–1264)
Disclosure of AI assistance, plus a paragraph restating the tier system.
**Argument that won:** the disclosure is already made in the Introduction, and
the second paragraph is §5's opening premise and tab:tiers' T2 row again. One
sentence discharges the obligation; a section elevates a process note to the
weight of a results section.
**Salvage:** the Introduction clause now reads "It is an amateur contribution
carried out in collaboration with an AI assistant (Anthropic's Claude Code); the
author set the goals, made the design and verification decisions, ran the
machines, and is responsible for correctness."
**Refs resolved:** the sole inbound `\ref{sec:ai}` was in the sentence rewritten.

### S9 — §2, "Definitions" (175–199)
Polyomino/polyplet, fixed/one-sided/free, the two refining triangles.
**Argument that won:** written for a reader this report does not have. Its first
paragraph re-derives the abstract and the Introduction's opening; its
checkerboard aside is disowned in its own parentheses ("The remark is
illustrative only"); T(n,H) is defined again in §4.2 where it is used, and the
symmetry-invariant counts again in §7 with the Burnside formulas.
**Salvage (three conditions, all met):** (1) into §1, not §7 — the fixed /
one-sided / free convention with A006770 named as the fixed count; (2) the same
sentence now coins "height triangle" and defines T(n,H) with the summation
identity, since the phrase appears in a section heading and the abstract but was
coined only here; (3) the colour-class fact survives, relocated to §5's
structural cross-check bullet where it explains why bishop-connected sub-counts
should reproduce A001168. The disowned parenthetical did not survive.
**Refs resolved:** `sec:object` was never referenced; its two outbound refs to
`sec:companions` died with it.

## Commit 2 — S6, hole stratification (partial: max-hole area cut, triangle kept)

### S6a — cut: "Maximum hole area" (1011–1059)
Theorem 2 (single-hole maximum enclosed area
$\lfloor(n-2)^2/8+\frac12\rfloor$), its two-sided proof, Conjecture 1
(multi-hole total), Open Problem 1 (the peeling inequality), and
`\bibitem{strang}`.
**Argument that won:** a self-contained isoperimetric result about king animals,
consuming none of the report's machinery and consumed by none of it — no term,
no bound, no check depends on it, and it brings its own conjecture and open
problem into a document whose thesis is twenty-two computed terms.
**Salvage:** none; nothing surviving referred to it. `thm:diamond` and `op:mn`
were never referenced, `conj:diamond` only from inside the cut span.
**Also removed:** the abstract's max-hole clause, the max-hole half of
contribution 6, and A001971 from the (uncited) OEIS bibitem list, which the
deleted span was the only text to use.
**Verifier:** the M(n) block (values, diamond identities, `maxhole.txt`
reproduction) and the `round((n-2)^2/8)` check pruned, `COVERAGE["maxhole"]`
dropped; 448 → 441 checks.

### S6b — retained: hole convention, stratification, tab:holes (939–1009)
**Defender's winning argument:** it is the same engine's output (hole count
carried as a second additive index on the column transfer matrix), inside the
report's stated scope ("the results that grew out of computing them"), and the
row-sums-equal-A006770 / flood-fill oracle / cross-ISA recount sentences are
validation evidence whose deletion would be silent.
