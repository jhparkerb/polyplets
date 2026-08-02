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

## Commit 6 — phase 2, the contested cut (R11)

### R11 — the G_3(x) example (960–963) — CONTESTED, OVERRULED WITH REPAIRS
One specimen of ten recovered generating functions, printed because it fits on
a line. **Defender's contest:** (a) removing it leaves "orders" undefined —
the display was the only place a reader could see what an order is; (b) the ten
recovered GFs become unlocatable from the paper. **Overruled** as repairable,
with the bias to remove: (a) the orders list gains "(the denominator degrees)",
verified against `results/fixed_height_gfs.txt` — H=3 has order=7 and a
degree-7 Q, so the gloss is exact; (b) the Availability paragraph in §5 gains
"the recovered fixed-height generating functions".
**Verifier:** the two `G_3` transcription checks were transcriptions *of this
display*; both pruned, 427 → 425, and the `gf_block` helper they were the last
callers of goes with them. This is the phase's largest verifier cost per line
saved, and the released checker visibly shrinks. The stage is nearly
byte-neutral (−22 bytes): the two repairs cost most of what the display saved,
which is the price of the ruling and is recorded as such.

### Considered and not proposed in phase 2
tab:byheight40 (the only data form of the computed/injected split, and §4.3
instructs readers to sum its H≤21 rows); the modular-consistency bullet, the
P_19 parenthetical, and "stopped here rather than exhausted" (closed doors —
each records something that was *not* done); "Relation to existing work" and the
Klazar limitation (novelty qualification and an explicit non-reach).

### Verifier checks with no claim in the paper
Eighteen checks now test repository invariants the paper does not print: the six
residual N_k checks (phase 1), the seven hole-GF order-law checks, `H<=10
captures 74.9% of a(19)`, the a(25) bound pair, and — measured in phase 3 — the
`holefree_gas.py` and `deficit2_proof.py` checkers, neither of which corresponds
to any claim in the .tex ("deficit" appears nowhere in the paper). Not pruned —
the argument for removing them is about what the released checker promises in
its docstring, not about the document under review, and it should be settled
once after phase 5 when the final claim set is fixed.

## Commit 7 — phase 3, agreed paragraph-level batch (P1–P9, P12–P14)

Phase 3 trims whole paragraphs, list items, bullets and captions. Line spans are
positions in the post-phase-2 file (1193 lines, 64,207 bytes at 3282315). No
check parses §5, the contributions list, any lead-in, or any caption text, so
this stage is verifier-neutral by construction; the one exception was handled by
condition (P9).

### prop P1 — Contributions items 1, 2, 5, 6 (115–119, 131–136)
Item-for-item restatement of the abstract the reader has just finished; items 1,
2, 5 and 6 duplicate it clause for clause.
**Ruling:** items 3 and 4 STAY — item 3 is the only front-matter statement of
k≤18 and T(n,n−k), and item 4 is the diagonal-mirror law's only mention outside
§6.3 (phase 1 struck that sentence from the abstract). My whole-list fallback
was declined for exactly that reason.
**Cost:** the scanner loses a one-screen inventory and reads the abstract for it.

### prop P2 — the tab:terms lead-in (180–183)
Both of its facts are in the caption 30 lines below, in the same words. Where
prose and caption duplicate, the caption is the copy that must survive.
**Condition, accepted:** the tier pointer moves into the caption — "Tiers
(Table~\ref{tab:tiers}): …" — so the tags stay resolvable where they are used.

### prop P3 — the §3 one-sided paragraph (281–287)
Every clause is elsewhere: the reach explanation in tab:onesided's caption, the
remaining-companions dependency in §7's second paragraph with the actual cap.
Both of its pointers went to §7, which is the tell.
**Salvage:** one sentence keeps the table introduced.

### prop P4 — "Relation to existing work", compression (1026–1052)
Cut: the three-lattice transport repetition ("That lightness is why the proof
transports…"), which is already stated at the end of §9.1 and in the abstract;
and the anatomy of what Bell–Nguyen–Zannier and Bell–Hu–Satriano bound.
**Conditions, accepted, both from the defender:** (1) the haruspicy route's
requirement survives in compressed form ("needs an explicit combinatorial
description of the denominators (cyclotomic products, in the polygon setting)")
— it is the only support for the abstract's "lighter than the existing
haruspicy route"; (2) "explicit excluded (r,D) boxes rather than a bare
dichotomy" survives — it is the only thing defining "effectively" in the
retained divergence sentence. Retained as proposed: the priority concession with
both citations, the reason BNZ/BHS do not apply, and the novelty hedge verbatim.
**Honest note:** the conditions ate most of the saving — 27 lines to 19, not the
~13 I projected.

### prop P5 — Method C's chain-regression paragraph (421–423)
The third statement of one discipline; §4's preamble states it as an engine-wide
invariant and §5's bullets lean on it by name. Explicitly NOT treated as a
duplicate of §5's "External truth" bullet, which claims agreement with published
A006770 (external) rather than chain-reproduction (internal).

### prop P6 — the P_19 parenthetical in §6.1 (639–642)
The third of three statements of one fact, and the least precise; §5's held-out
bullet names the two cells and the diagonal.
**Salvage (mandatory — this is a closed door relocated, not deleted):** the
unique content, that P_19 passes the leading-coefficient and integrality checks
and is recorded unused, appends to §5's held-out bullet.

### prop P7 — the I/O integrity paragraph, compression (411–419)
Cut: the scene-setting ("A multi-hour external shuffle can fail in mid-flight"),
the truncation gloss, and the rhetorical "These refusal paths are not assumed to
work". The no-silent-loss claim the T2 grade leans on, the record counts, the
refusing readers/merge/combiner, and the fault-injection gate all survive.

### prop P8 — the §6 section lead-in (615–618)
A roadmap for three subsections whose titles announce their contents.

### prop P9 — the hole-graded diagonal law paragraph (908–914) — CONDITIONED
Argued on a NEW ground, since phase 1 retained it inside a span defended as a
whole and never on its own merits: phase 2's accepted R15 ruling cut a
structurally identical item (a one-sentence result with no data, no consequence
and no consumer, pointing at a repository script).
**Condition, accepted:** the clause I offered is mandatory, extended with the
datum — §6.2 now carries "The same decomposition refines by hole count (the
pair-row's weight splits 25=24+1), and mod 3 only the maximal-hole stratum
survives (\texttt{experiments/hole\_strata\_gas.py})". This keeps the
`hole-marked strata` checker anchored, so it was NOT pruned and the verifier
stays at 425.

### prop P12 — the §5 lead-in (528–529)
Signposting for a self-describing itemization.

### prop P13 — the tab:tiers caption's second sentence (171–173)
A gloss restating the first clause of three rows in the same words, which also
silently omits T2-minus — the tier the paper's own frontier terms carry.

### prop P14 — the §5 Hygiene bullet, compression (598–603) — CONDITIONED
Cut: the trailing gates clause (duplicating the Availability paragraph four
lines below) and the sanitizer parenthetical.
**Condition, accepted:** "every kept result traces to a clean-tree commit stamp
in a provenance ledger" survives explicitly, alongside the sanitizer and
multithreaded-equals-serial keeps.

### prop P10 — CONTESTED, RETAINED (no edit)
The §5 bullet "Direct enumeration = transfer matrix through a(22)".
**Defender's winning argument:** tab:tiers delegates its coverage itemization to
§5 by name, so cutting this bullet would leave that itemization without an entry
for the tier the table calls strongest; and it is the only statement of which
algorithm pairs cover which part of the T1 range, so cutting it would
misattribute the a(20)–a(22) anchor to the Method A/B pairing that only reaches
a(19).

## Commit 8 — phase 3, the contested cut (P11)

### prop P11 — Method B's state-encoding paragraph (376–382) — CONTESTED, CUT IN FALLBACK FORM
Implementation detail for the engine that ran out of memory.
**Defender's contest:** (a) Method C's "The state encoding is as in Method B"
would dangle, pointing at a description that no longer exists; (b) my own
proposal admitted the canonical-renumbering rationale is the single most useful
implementation sentence in the paper. **Ruling:** cut in fallback form, bias to
remove — Method C's parenthetical absorbs both the renumbering rationale and the
\texttt{core/signature.h} pointer, and its sentence is made self-contained
rather than cross-referential. "Canonical" remains true and explained.
Theorem 3's irreducibility argument leans on the boundary-signature definition
in §4.2's first paragraph, which is untouched.
**Net:** small (~2 lines), by design.

## Commit 9 — phase 4, sentence-level tightening (T1–T13, T15–T18)

Phase 4 removes and tightens individual sentences and clauses inside surviving
paragraphs. Line spans are positions in the post-phase-3 file (1140 lines,
60,978 bytes at d2db7cb). Verifier-neutral throughout: no check parses the
abstract, §1, §5, any lead-in, or the λ-bound prose (measured, not assumed —
`2147`, `20000`, `9.31`, `6.543`, `Collatz`, `certificate`, `Superseeker` all
return nothing in verify_claims.py).

Sixteen items applied. Six touch protected sentences and were filed with
before/after text so the defender could check each scope survived; all six were
verified and applied verbatim as filed.

| id | target | what went |
|---|---|---|
| T1 | §9 transition, 891–893 | "as we now show", three lines above the heading that says it |
| T2 | tab:byheight40 lead-in, 417–418 | caption carries it; the table keeps its other in-prose reference (the sum-rows-H≤21 instruction) |
| T3 | §3, 225 | "Each rung is certified rather than measured." — topic sentence for the three that prove it |
| T4 | §6.1, 600 | "The law's shape is a theorem:" bridge into a theorem environment |
| T5 | §4.3, 394 | "The headline totals contain both, so the split must be stated exactly." — promise immediately before the disclosure |
| T6 | §4 preamble, 300–301 | "each subsection states what ran out and what replaced it" — roadmap for four self-titled subsections |
| T7 | §1, 109–111 | the data-appears-in-both sentence and its rationale clause |
| T8 | abstract, 60–61 | "The tiers record that." |
| T9 | §3 growth, 217–218 | PROTECTED: "This is an estimate, not a rigorous bound; the two-sided bracket follows." → "; this is not a rigorous bound." |
| T10 | §3 upper bound, 257 | PROTECTED: "verified with no floating point in the deductive chain." — third exactness assertion in eight lines; the other two stand |
| T11 | §4.1, 320–322 | PROTECTED: the shared-algorithm admission stays; its answer goes, because the paragraph's last sentence gives it more precisely |
| T12 | tab:tiers T2⁻ row, 153–154 | PROTECTED: the tag's rationale sentence; the definition and coverage stand |
| T13 | §5 held-out bullet, 539–541 | PROTECTED: two adjacent sentences merged, both halves of the distinction kept |
| T15 | §9.1, 902–903 and 919–920 | "each stated here in the form used"; "In the standard terminology" (the term *house* survives, (iv) needs it) |
| T16 | §8, 824–827 | PROTECTED: "exact" asserted twice in consecutive sentences; row-sums-equal-A006770 survives in tab:holes' caption, so the `hole rows sum to a(n)` check stays anchored |
| T17 | §6.3, 702 | "Their practical role:" — a label before a colon-led explanation |
| T18 | §7, 729–731 | "records … themselves" tightened; both table references survive |

### STANDING CONSTRAINT from T4 — binding on phases 5 and 6
With the "The law's shape is a theorem:" bridge gone, §6.1's sentence at what is
now L616 —
"What remains fitted rather than derived is $P_k$ for $6\le k\le18$; with the
theorem in hand those fits are interpolation of a known-shape form" —
is the subsection's SOLE in-place statement of the shape-proved / constants-fitted
split. It is **not available for later cutting on the ground that it is stated
elsewhere.** Recorded at the defender's insistence and upheld.

### prop T14 — CONTESTED, RETAINED (no edit)
§9.1's in-proof "This extraction is the opening move of Lemma~9 of~\cite{bmr2002};
what follows is where we depart from it."
**Defender's winning argument:** the sentence's load is not the attribution
(which is indeed duplicated in "Relation to existing work") but the **departure
marker** — it locates where the borrowed step ends and the paper's own argument
begins. That boundary is the substance of the paper's hedged novelty claim, and
nothing else in the proof marks it.

### Compounding note — T8 + T12, binding
Both statements that the weaker \tiertwominus{} standard is *deliberately* marked
are now gone (the abstract's "The tiers record that." and the tier row's "The tag
exists so the weaker standard is never silently absorbed into \tiertwo{}"). The
fact itself survives four ways: the abstract's clause that a(39)/a(40) lack the
held-out check and never will get it, the \tiertwominus{} row's definition and
coverage, §5's held-out bullet, and the tier tags on the results tables. The
defender will not concede a third cut in this family and the referee upholds
that: **no further trimming of the T2⁻ marking.**

### Declined addition — tab:terms reintroduction
The remover raised the missing in-prose reference as a phase-3 deviation flag and
then declined its own invitation to add one back: the section heading, the pinned
[H] float and the self-describing caption leave no ambiguity, the verifier finds
the table by label, and re-adding a sentence phase 3 removed would undo an
accepted cut. Defender confirmed. P2's caption condition was verified landed —
tab:terms' caption reads "Tiers (Table~\ref{tab:tiers}): …".

## Commit 10 — phase 5, word-level cuts (batch + BL2/BL5/BL6)

The finest grain: individual words and short phrases inside surviving
sentences. Adjudicated as one batch rather than per item. Line spans are
positions in the post-phase-4 file (1123 lines, 59,891 bytes at feb1c81).
Verifier-neutral; both proposals sitting inside sentences that carry a checked
quantity were audited and neither touches the number or the qualifier the check
tests (A1 near the injection shares, which are computed from tab:byheight40's
body; A5 in the sentence carrying the a(40) GF-bound integer, where "while that
term was out of reach" survives intact).

**Applied — intensifiers:** A1 "at all" (injection paragraph), A2 "any"
(formula-assistance sentence), A3 "very" (the sweep that produced T(40,21)),
A4 "active" (the frontier is active by definition), A5 "still".

**Applied — doubled qualifiers:** B1 "a single … at a time" → "one … at a
time"; B2 "may only ever lose" → "may only lose" (claim-touching: the pruning
admissibility claim is carried by "only").

**Applied — wordy constructions:** C1 "are conjecture-assisted and are staged"
→ "are conjecture-assisted, staged" (both halves of the T3 scope survive);
C2 "what follows is where we depart from it" → "what follows departs from it".

**Applied — filler:** D1 "in this paper"; D2 "thus".

**Applied — repeated word:** E1 "the provenance and verification of those
numbers" → "their provenance and verification".

**Applied — borderlines the defender cleared:** BL2 "precisely" (the definite
article carries the set-equality claim); BL5 "the data show, and" (one of two
attributions of the same evidence; the stronger remains); BL6 "themselves" at
the constants sentence.

### prop D3 — PULLED, with refutation
"completed" in "the completed $n=32$ farm prefix-matches both the $n\le24$
oracle range and the earlier $n\le28$ run exactly."
**Defender's refutation of my dependency reasoning, accepted:** I argued a farm
that prefix-matches ran to completion. It does not follow. A strip of exact
bounding box $S$ contributes only to $n\ge S$, so prefix-matching at $n\le24$
and $n\le28$ cannot detect a missing high-$S$ strip; and the checker loads
`runs/sym32/dmirror.out` as given. "completed" is therefore the document's only
assertion that every strip of the farm was summed, and it stays.

### Borderlines retained (one line each)
- **BL1** "entirely" (L328): phase 4's T11 already traded away this sentence's
  twin; "entirely different principle" is now the definitional strength claim
  the \tierone{} tier rests on at the point Method B is introduced.
- **BL3** "and uniform" (L399): "uniform" asserts identical application at every
  $k$, which is what makes $P_{19}$'s exclusion rule-driven rather than ad hoc.
- **BL4** "at all" (L505): an intensifier on self-criticism; removing it shifts
  register on the paper's frankest admission of weak coverage.
- **BL7** "at the meeting point of" (L86): an intersection claim, and it carries
  the paired-citation structure that follows.

### Erosion floors recorded
- **C2:** "what follows departs from it" is the T14 departure marker in full.
  No further compression; "what follows" is untouchable.
- **D2** was approved on corrected grounds: the inference is carried by the
  adjacent sentence, not by the phase-4 T11 claim I cited.

### Coverage gap found (verify_claims.py)
The D3 exchange surfaced an unverified gap: **nothing in the checker validates
farm completeness for the $n=32$ diagonal-mirror strip farm.** `dmirror.out` is
consumed as given, and the prefix-match checks that do run cannot see a missing
high-$S$ strip. Not a trim item and not fixed here — logged with the
paper-unanchored checks below as something the author may want a real check for
(a per-strip manifest against the expected $S$ range would do it).

## Commit 11 — phase 6, claude-isms and LLM-speak sweep

The final pass, on the author's direction to apply a very low bar to register
noise — with the explicit condition that this is for readability, not for
laundering: no de-watermarking intent, and the AI-assistance disclosure in §1
is untouchable and untouched. Line spans are positions in the post-phase-5 file
(1123 lines, 59,760 bytes at 58e7cb0).

**Finding first: two families were already clean.** The pre-session commits
(em-dash density 76→6, rhetorical closers stripped) did more than the top
layer. Measured on the current file: zero discourse scaffolds ("Note that",
"Observe that", "It is worth noting", "Importantly", "Crucially", "Indeed",
"In other words", "That is,", "Specifically,", "In particular", "Moreover",
"Furthermore", "Notably"); zero "serves as"/"acts as"/"plays the role of";
zero sentence-initial And/But/Yet/So/Now as beat markers; zero of "careful",
"comprehensive", "robust", "elegant", "powerful", "subtle", "crucial",
"remarkable", "striking"; one body em-dash, a genuine apposition in a technical
definition.

**The "rather than" family was audited in full and none was cut as decorative.**
All twelve instances are load-bearing scope statements or protected caveats:
decorrelation/independence, fitted/derived, stopped/exhausted, disk/memory,
fails-closed/silent-loss, detected/absorbed, split/recomputed-whole, L616,
derived/observed, computed/derived, observed/proved, analytic/polynomial. One
item (X4) touched the family only to break a doubled construction inside a
single sentence, keeping both contrasts.

**Applied:**
- X1 the fault-injection epigram ("the checks fail on wrong programs and pass on
  right ones") — a restatement of the sentence it hung on; all three planted
  errors and the negative control survive verbatim.
- X2 "From that shared start the arguments diverge." — a beat before the two
  clauses that state the divergence.
- X3 the abstract's "rigorously" — the machine-checkable exact certificates are
  the rigour, and claim it more specifically.
- X4 "detected on read rather than absorbed" → "detected on read, not absorbed"
  — second of two "rather than" constructions in one sentence.
- X5 "described next" — a pointer to the next bullet in a list.
- X6 "The abstract degree growth is visible concretely:" — the degree list is
  its own demonstration. ANCHOR CHECKED: the list `1,2,4,9,29,68,181,462,1254,
  3289`, which the phase-2 R7 ruling deliberately made the anchor for
  `lifetime-3 atom degrees`, is untouched.
- BX1 "The strongest single check came with the final term:" — self-assessment.
- BX2 "explicit" in "carries an explicit confidence tier".
- BX4 "The tiers record an asymmetry:" — scaffold before the asymmetry itself.
- BX5 "One limitation." — beat marker; the Klazar limitation is untouched.
- BX6 reworded, not deleted: "…that $P_0$ and $P_1$ now supply directly, at the
  price of the \tierthree{} label." The T3 attribution and the cost datum both
  survive; the epigram's first clause, which restated the preceding sentence,
  goes.

### BX4 — family ruling recorded
The T2⁻ standing constraint covers statements that the weaker standard is
*deliberately marked*. "The tiers record an asymmetry" is a tier-asymmetry
statement, not a deliberate-marking statement: out of family, cut on merits.

### Borderlines retained (phase 6)
- **BX3** "rigorous" at the fact-(ii) reference: it asserts the imported bound's
  theorem status at the proof step that depends on it, and is the only
  point-of-use statement of that status.
- **BX7** "decisively": a causal attribution of the 200× to reshuffle-volume
  reduction, distinct from the binding-resource claim, and the design rationale
  a reimplementer needs.

---

# CLOSE-OUT

## Per-phase totals

| phase | what | lines | bytes | checks |
|---|---|---|---|---|
| — | pre-trim (d9901d0) | 1437 | 77,244 | 448 |
| 1 | sections (commits 1–4) | 1233 | 66,745 | 429 |
| 2 | results (commits 5–6) | 1193 | 64,207 | 425 |
| 3 | paragraphs (commits 7–8) | 1140 | 60,978 | 425 |
| 4 | sentences (commit 9) | 1123 | 59,891 | 425 |
| 5 | words (commit 10) | 1123 | 59,760 | 425 |
| 6 | register (commit 11) | 1122 | 59,400 | 425 |

**315 lines (21.9%) and 17,844 bytes (23.1%) removed.** The verifier lost 23
checks, every one pruned in the same commit as the claim it tested; it has been
green at 425 for four consecutive phases.

## Contested-retained across all six phases

Items the remover proposed and the defender saved, with the argument that won:

1. **Hole convention, stratification, tab:holes** (phase 1, S6b) — same engine's
   output via a second additive index; the row-sums/flood-fill/cross-ISA
   sentences are validation evidence whose deletion would be silent.
2. **The mod-3 collapse and spine cubic** (phase 1, S7b) — a derived corollary of
   Theorem 1 about this paper's own triangle, machine-verified on 420 cells.
3. **The diagonal-mirror core** (phase 1, S8) — full deletion rejected: it would
   orphan the four published T3 companion values, which are deliverables. The
   remover's claim that tab:symcounts' ‡ footnote is self-describing was false.
4. **§5's T1-anchor bullet** (phase 3, P10) — tab:tiers delegates coverage
   itemization to §5 by name, and this is the only statement of which algorithm
   pairs cover which part of the T1 range.
5. **The in-proof Lemma 9 sentence** (phase 4, T14) — its load is the departure
   marker, not the attribution: it locates where the borrowed step ends.
6. **"completed"** in the n=32 farm sentence (phase 5, D3) — the only assertion
   that every strip was summed; prefix-matching cannot detect a missing high-S
   strip.
7. **"entirely"** (phase 5, BL1) — after T11's trade, the definitional strength
   claim the T1 tier rests on where Method B is introduced.
8. **"and uniform"** (phase 5, BL3) — asserts identical application at every k,
   what makes P_19's exclusion rule-driven.
9. **"at all"** at the single-machine admission (phase 5, BL4) — intensifier on
   self-criticism; removing it shifts register on the frankest admission.
10. **"at the meeting point of"** (phase 5, BL7) — an intersection claim carrying
    the paired-citation structure.
11. **"rigorous"** at the fact-(ii) reference (phase 6, BX3).
12. **"decisively"** (phase 6, BX7).

Two contested items were cut in fallback form rather than retained: the G_3
display (phase 2, R11, cut with two repairs) and Method B's state-encoding
paragraph (phase 3, P11, folded into Method C).

## Standing constraints and erosion floors

Binding on any future trimming of this file:

- **L616** — "What remains fitted rather than derived is $P_k$ for $6\le k\le18$;
  with the theorem in hand those fits are interpolation of a known-shape form"
  is §6.1's sole in-place statement of the shape-proved/constants-fitted split.
  Not available for cutting on the ground that it is stated elsewhere.
- **The T2⁻ marking family** — both statements that the weaker standard is
  deliberately marked are gone; the fact survives four ways (abstract, T2⁻ row,
  §5 held-out bullet, table tags). No third cut. Tier-*asymmetry* statements are
  out of family (phase 6 BX4).
- **"what follows departs from it"** — the T14 departure marker in full. No
  further compression; "what follows" is untouchable.
- **tab:terms' caption** must keep "Tiers (Table~\ref{tab:tiers}): …" — with the
  lead-in gone, it is the only place the tier tags are made resolvable.
- Closed doors, evidence, and scoping caveats keep their substance throughout:
  the modular-consistency bullet, the H≤7 no-cancellation caveat, "stopped here
  rather than exhausted", the single-machine admission, the Klazar limitation,
  the novelty hedge, the T3 labels.

## Release-integrity flags (deferred past phase 5 — BOTH CLOSED 2026-08-02, commit 2cad8f2)

Both are about `paper/verify_claims.py`, not the document, and both should be
settled before release rather than by a trimming pass:

1. **Eighteen checks with no claim in the paper.** The six residual N_k checks,
   the seven hole-GF order-law checks (`c_3..c_7`, the H=7 order law,
   `H=8 k=0 order==1499`), `H<=10 captures 74.9% of a(19)`, and the a(25) bound
   pair. The checker's docstring promises to verify "every arithmetic/algebraic
   claim in polyplets-report.tex"; it now also guards repository invariants the
   paper never prints. Either prune them or amend the docstring to say so.
2. **No farm-completeness check for the n=32 diagonal-mirror strip farm.**
   `runs/sym32/dmirror.out` is consumed as given. A strip of exact bounding box
   S contributes only to n≥S, so the prefix-matches at n≤24 and n≤28 cannot
   detect a missing high-S strip, and the paper's "completed" rests on nothing
   machine-checked. A per-strip manifest against the expected S range would
   close it.

## Totals

| stage | lines | bytes | verify_claims |
|---|---|---|---|
| pre-trim | 1437 | 77,244 | 448 |
| commit 1 | 1338 | 72,702 | 448 |
| commit 2 | 1279 | 69,690 | 441 |
| commit 3 | 1262 | 68,506 | 439 |
| commit 4 | 1233 | 66,745 | 429 |
| commit 5 | 1194 | 64,229 | 427 |
| commit 6 | 1193 | 64,207 | 425 |
| commit 7 | 1145 | 61,233 | 425 |
| commit 8 | 1140 | 60,978 | 425 |
| commit 9 | 1123 | 59,891 | 425 |
| commit 10 | 1123 | 59,760 | 425 |
| commit 11 | 1122 | 59,400 | 425 |

Final: 315 lines and 17,844 bytes off the pre-trim document (21.9% of the
lines, 23.1% of the bytes), with the verifier down 23 checks, every one of them
pruned in the same commit as the claim it tested, and green at 425 for the last
four phases. pdflatex clean at all eleven stages: zero errors, zero undefined
references or citations, and the same seven pre-existing hyperref
Unicode-bookmark warnings the document started with.
pdflatex clean at every stage (zero errors, zero undefined references, the
same seven pre-existing hyperref Unicode-bookmark warnings), and
verify_claims green at every stage.
