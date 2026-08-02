# polyplets-report.tex — trim log

Adversarial trim: a remover proposes cuts, a defender contests them, a referee
rules with a slight bias toward removal. Phase 1 cut whole sections; phase 2 cut
individual results. This log records what left, why, and where anything
load-bearing landed. Phase-1 line spans are positions in the pre-trim file
(1437 lines, 77,244 bytes at commit d9901d0); phase-2 spans are positions in the
post-phase-1 file.

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

## Commit 3 — S7, mod 3 and universality (partial: transport cut, spine kept)

### S7a — cut: lattice universality (738–757)
The row-local lattice definition, the five transport steps, the machine-checked
square/hexagonal instances, the $w\ne1$ and degenerate branches.
**Argument that won:** it certifies no term, feeds no engine and gates no tier,
and it is about three lattices this report does not enumerate — a précis of a
repository document it names in its own last line.
**Salvage:** one sentence at the end of the surviving subsection: the law holds
on any lattice reaching one row with $b$ up-neighbours, and mod any $p\mid b$
the diagonals are governed by $W^3=W^2+t$, with the pointer to
`docs/proofs/universal-diagonal-law.md`. The subsection is retitled "The
triangle mod 3".
**Abstract:** clause excision only — the Theorem 1 proof claim is untouched;
"govern polyominoes and polyhexes" goes, "lattice-universal, the mod-$p$ spine
cubic having its prime set by the lattice's drift count" stays, since the claim
survives in the body via the salvage.
**Verifier:** the `hex_gas.py` and `universal_law_check.py` subprocess checkers
pruned; 441 → 439 checks.

### S7b — retained: the mod-3 collapse and spine cubic (719–737)
**Defender's winning argument:** a derived corollary of the flagship theorem
about *this paper's own* triangle, machine-verified on all 420 in-band banked
cells — squarely within the report's stated claim types.

## Commit 4 — S8, diagonal-mirror triangle (partial: apparatus cut, law kept)

### S8a — cut: the forward hits, the GF basis, the proof sketch
Three post-pinning forward hits (772–777), the $N_k$ generating-function
paragraph with the $N_k(\pm1)=(\pm2)^k$ boundary observation (805–812), and the
segment-grammar proof paragraph (814–825).
**Argument that won:** the forward hits are asserted by tab:dmpk's own caption;
the $N_k$ basis and the shape proof are apparatus for values the paper itself
declines to publish as data (the $n=33$ companions are staged "as comments only,
never as b-file data").
**Correction forced on the remover:** the claim that tab:symcounts' ‡ footnote is
self-describing was false — $d(S,n)$, "in-regime" and $P_0$–$P_4$ are defined
only inside the proposed span, and $P_k$ there collides with the height-triangle
$P_k$. Full deletion was rejected: it would have orphaned the four published
T3 companion values, which are deliverables.
**Retained:** the subsection heading, the $d(S,n)$ definition and the
quasi-polynomial law with its onsets, tab:dmpk with its caption (which already
records pinning, holdout and post-pinning confirmation), and the
62-CPU-hour / 79 GB cost clause that justifies the T3 label. The sentence
introducing the table was shortened to keep its `\ref` alive rather than orphan
a retained float.
**Abstract / contribution 4:** the "likewise proved in shape" sentence struck
from the abstract; contribution 4 drops "whose shape is likewise proved" and
"and generating-function structure", keeping the item and its `sec:dmdiag` ref.
**Verifier:** the $N_k(\pm1)$ checks pruned, `COVERAGE["dmirror_strips"]`
40 → 30; 439 → 429 checks. The remaining $N_k$ series and degree checks now
validate repository data rather than a paper claim; left in place per the
ruling.

## Commit 5 — phase 2, agreed result-level batch (R1–R10, R12–R15)

Phase 2 trims individual results rather than sections: duplicated numbers,
superseded bounds, unverifiable second opinions, telemetry. Line spans are
positions in the post-phase-1 file (1233 lines, 66,745 bytes at 9cc8cc1).

Measured coupling, since it decided several rulings: `verify_claims.py` parses
the .tex only through five table labels (`tab:terms`, `tab:byheight40`,
`tab:symcounts`, `tab:onesided`, `tab:companions`). Every other number it
checks is hard-coded in the checker, transcribed from paper prose — so cutting
prose breaks nothing mechanically, it orphans the check that existed to test
the claim.

### R1 — the boxed a(40) equation (180–183)
The fourth printing of one 32-digit integer (abstract, box, tab:terms cell,
tab:byheight40 column sum). No label, no ref, not parsed. Cut whole.

### R2 — the n=34 symmetry counts in prose (775–776)
R_90, R_180 and H at n=34, all three in tab:symcounts' n=34 row 65 lines below,
and the R_90 vanishing rule already in that table's caption. Cut whole; zero
verifier edits (the table is parsed, the prose was not).

### R3 — the displayed OneSided(34) equation (296–300)
A display whose value is the last cell of the table 20 lines below.
**Salvage:** folded into the sentence it interrupted — "hence fifteen new
terms, listed in Table~\ref{tab:onesided}", which also absorbs the following
"Table~\ref{tab:onesided} lists them."

### R4 — the D(32) parenthetical (785)
Duplicate of tab:symcounts' n=32 D cell; the clause "D is exact through n=32"
carries the point without the digits.

### R5 — the n=18 hole counts in prose (894–895)
Hole-free, one-hole and max-holes at n=18: the k=0 and k=1 cells of tab:holes'
n=18 row plus its last populated column. **Salvage:** the OEIS-novelty sentence
that followed (Superseeker check, b-files prepared) is kept — it is a claim,
not a duplicate. Verifier untouched: `A_0(18)`, `A_1(18)` and `max holes at
n=18` test `results/holes_n18.txt` against constants the retained table still
claims.

### R6 — the differential-approximant estimate of λ (238–242)
The one numeric claim in the growth paragraph with no code path in the released
checker, and it agrees with the fit it accompanies (7.110 against
7.1108–7.1111; θ=−1.000 against −1.02..−1.03). The estimate λ≈7.111 stands on
the fits, which are recomputed.

### R7 — the denominator-structure footnote (949–958) — CONDITIONED
Ten lines of subsidiary structure, whose atom-degree list `1,2,4,9,29,68,181`
duplicates the first seven terms of the degree list at L1046 where they do real
work.
**Defender's correction, accepted:** my proposed salvage would have left
"new-root contents" at L1046 without an antecedent and unanchored the verifier's
`lifetime-3 atom degrees` check. The main-text replacement therefore (1) defines
N_H as the denominator of the height-H strip generating function, (2) states the
identity itself — exact-height counts are second differences of strip counts, so
Q_H | N_{H-2}N_{H-1}N_H by construction — and (3) keeps the observed-not-proved
caveat with its H≤7 scope. **R7 is verifier-neutral**; no check pruned.
Dropped: the OEIS-novelty note on the two degree sequences.

### R8 — the μ_H spot check (1011–1012)
A ten-case numerical confirmation of the one fact among (i)–(iv) that is proved
outright, by strict Perron–Frobenius submatrix monotonicity with a citation.

### R9 — the "Rigorous lower bounds" paragraph (1091–1102) — CONDITIONED
Lower bounds on three terms the paper now prints exactly; the paragraph itself
concedes all three were later confirmed by Method C.
**Condition, accepted:** the salvage retains the a(40) bound integer
4266005101622209395058618248135, which keeps the `GF bound captures 7.5%` check
anchored (not pruned) and keeps the computed-before-the-term-existed claim
falsifiable. Four lines at the head of §9 replace twelve. Only the a(25) bound
pair becomes paper-unanchored; not pruned.

### R10 — the bilateral identity's proof (856–866) — CONDITIONED
Eleven lines of stabilizer bookkeeping for one identity, in a report that
states the Free and OneSided Burnside formulas without proof.
**Condition, accepted:** the salvage carries both the mechanism ("a double count
of animal–reflection incidences over D_4") and the empirical check ("checked
numerically against every published term of A030234"). Verifier untouched — the
identity survives as a statement and is still exercised at every n by
`tab:companions bilat`.

### R12 — the Method B→C speedup measurements (418–419) — CONDITIONED
A benchmark against an engine that had already run out of memory; the same
class of number phase 1 removed with the appendix.
**Condition, accepted:** the H-dependence keeps one anchor — "growing with H, to
~200× at H=16"; the 29×/H=12 endpoint goes.

### R13 — the Bacher comparison (266–269) — CONDITIONED
A superseded bound: 5.828 < 6.475 < 6.543.
**Condition, accepted, and it corrects me:** my proposal targeted the sentence
*and* `\bibitem{bacher}` while my own fallback kept the citation — the two are
inconsistent and the bibitem must stay. Taken as the fallback: "It improves on
the 3+2√2 available in closed form from Bacher's directed subclass~\cite{bacher}."
The acknowledgment of prior art is not weakened further.

### R14 — the ladder's cost-growth numbers (263–265) — CONDITIONED
Resource telemetry of the kind phase 1 ruled out of the document.
**Condition, accepted:** "the rungs gain about 0.05 each" survives — it is the
convergence rate that explains the bracket's width, and it answers my own cost
sentence. Only "cost grows ~3.5× per rung, reaching 11.8 GB at H=17" goes. The
closed door ("stopped here rather than exhausted") survives, as proposed.

### R15 — the hole-refined generating functions (965–966)
A one-sentence result with no data, no consequence and no consumer.
**Verifier:** the `G_{3,1}` numerator/denominator transcriptions were anchored
only here (the paper displays no G_{3,1}); both pruned, 429 → 427. Seven further
hole-GF checks (`c_3..c_7`, the H=7 order law, `H=8 k=0 order==1499`) were
already paper-unanchored before this trim — the checker's own comment records
that claim's retirement in July — and are left alone.

## Totals

| stage | lines | bytes | verify_claims |
|---|---|---|---|
| pre-trim | 1437 | 77,244 | 448 |
| commit 1 | 1338 | 72,702 | 448 |
| commit 2 | 1279 | 69,690 | 441 |
| commit 3 | 1262 | 68,506 | 439 |
| commit 4 | 1233 | 66,745 | 429 |
| commit 5 | 1194 | 64,229 | 427 |

Phase 1 removed 204 lines and 10,499 bytes; phase 2 continues from there.
pdflatex clean at every stage (zero errors, zero undefined references, the
same seven pre-existing hyperref Unicode-bookmark warnings), and
verify_claims green at every stage.
