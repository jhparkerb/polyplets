# `technical-report.tex` — running to-do

Started 2026-08-05 as a one-off review checklist; **maintained as a running
list from 2026-08-23** at jasonp's direction. Add to it, mark items off, do not
let it go stale.

> **This file proposes; it does not edit.** `technical-report.tex` is jasonp's
> prose under the P disclosure and is read-only to the machine (memory:
> `paper-is-jasonps-words`). Everything below is his to accept, reject or
> reword. Where an item says MATERIAL READY, the checked content exists in the
> repo and the remaining work is his sentences.

**Status tokens:** `OPEN` — nothing assembled. `MATERIAL READY` — the content
exists in the repo, written up and checked; only his prose is missing.
`DONE` — in the paper.

**Comparison base:** `paper/technical-report.tex` at 2026-09-04 — the
rewritten abstract through a(40), the a(n) table, the T(n,H) block with the
T(n,n) / T(n,n-1) / grand-form paragraphs, one-sided / free / bilateral /
asymmetric / A194596 tables, the hole table, a one-line growth-rate remark,
three Methods paragraphs, an empty Reproducibility section, and a bibliography
file not yet wired in.

The mechanical state is good and is gated: `paper/verify_technical_report.py`
is 2722 checks green (the tables, the closed forms, and since 2026-09-05 the
prose: each scope number read out of its sentence and the T(n,n−1) derivation
re-counted by enumeration), and `tests/gate_p_paper_verifier.py` establishes
that 287 of the paper's 288 numeric literals of two or more digits are read by
one of them. `results/figs/triangle_provenance.svg` colors the 820 cells by
what checked them, from the gated table; `docs/glossary.md` ends with the
paper's words against the repo's.

**2026-09-05, the support pass** (jasonp: "make technical-report.tex easier to
back up and understand", then "we have to pay down technical debt"): the
sentence-by-sentence table in §A, the prose checks and the T(n,n−1) census in
the verifier, the RED gate widened to two-digit literals, the provenance
figure (replacing two unused triangle figures), provenance headers on the hole
files, and the concordance in the glossary. Dropped as more files than value:
an engine block diagram and generated `\input` tables for the engine chapter,
a tripleplet figure for the definition, a generated recipe list. Net files:
−6.

---

# Decisions, 2026-09-04 (jasonp's replies to the finish list)

- **Validation section (C1/B4):** he does not understand Motley and will not
  defend it. The section states what he can defend (Redelmeier to 22, the
  strip engine to H ≤ 14, every run re-deriving all rows below it, the
  external anchors) and reports the Motley agreement as machine work with a
  pointer, or not at all. Explanation on request, Q&A form.
  The defensible three-sentence version of what Motley computes — the
  Fortuin–Kasteleyn/Potts statement, in the engine's own terms — is the opening
  paragraph of `docs/proofs/cutcount-identity.md` and can be lifted verbatim.
- **Growth rate (C2/C3):** he cannot defend most of it. The Fekete floor is
  his (one argument, in the tex comment); Madras, the differential-approximant
  estimate and the L3 bracket are cite-or-drop.
- **Diagonal wording (C13):** he will fix it by asking questions, not by
  taking wording. Pending.
- **Holes (C6, C7, C11, C17):** deferred. The existing table stays because it
  is the data behind three staged OEIS sequences — the hole triangle and its
  k = 0 and k = 1 columns (`oeis/SUBMISSION.md:48-58`). Nothing more unless it
  earns its place.
- **a(41):** in, with an asterisk. See B5.
- **T(n,n−2) (C5), 2026-09-05: in.** He writes it in the T(n,n−1) style from
  `docs/proofs/T-n-nm2-and-general.md` §1 (one triple: 49 interior, 7 at an
  end; two doubles separated: two independent 25/5 gadgets, the quadratic;
  two doubles adjacent: 339/66, linear). If he cannot keep the explanation
  straight, he cuts it. When the paragraph lands the verifier gets what the
  T(n,n−1) paragraph has: the display checked on every banked cell and a
  census of the three cases at n = 5..8 against his coefficients.
  **2026-09-05 late: the verifier already carries it**, independent of the
  sentence: the closed form on all 36 banked cells, and the enumeration census
  for n = 5..8 split seven ways (interior triple 49, end triple 7, separated
  doubles 25·25 / 25·5 / 5·5, adjacent doubles 339 / 66), each equal to its
  formula; two adjacent doubled rows bridge each other, so their gaps are
  unconstrained, which the first cut of the census got wrong and the count
  caught. When his paragraph lands, only the sentence-reading needs adding.
- **Spelling and punctuation:** last, and not before he says.
- **Abstract: DONE** (end of session 2026-09-04). Next by the finish list:
  Reproducibility (B1), then the engine chapter (B2) from
  `docs/engine-record.md`, then item 6 (C13 wording) by Q&A.

---

# A. What the paper says now, sentence by sentence

2026-09-05. Every non-numeric claim in the paper, the record it rests on, and
the check that reads it. `paper/verify_technical_report.py` (2722 checks)
reads each scope number out of its sentence and compares it with the record;
`tests/gate_p_paper_verifier.py` perturbs every literal of two or more digits
in a copy and requires the verifier to go red (287 of 288; the exception is
the year on the title page). BACKED = the record says what the sentence says.
SCOPE = the sentence reaches further than the record. What a sentence leaves
out is not a row.

| line | the sentence says | record | check | status |
|---|---|---|---|---|
| 37–41 | A006770 expanded through a(40) | `results/ns_a40/PROVENANCE.md`; `results/triangle.txt` | abstract a(40); tab:an ×40; row sums ×40 | BACKED |
| 43–45 | T(n,H) proposed; for H > n/2 a polynomial factor fixed from earlier rows times an exponential | `docs/proofs/diagonal-law.md` (Lean); `orchestrator/sweep.go` `diagCoeffTable` | 171 real-swept in-onset cells against a refit from the two earliest per level; `ns-gate-diag-pins` | BACKED |
| 47 | a(19) computed directly with Redelmeier | commit `6598dcd` (2026-06-14: two decorrelated Redelmeier campaigns, gympie and ayr); the transfer-matrix check came after, `55f3053` | Redelmeier rows 1–22 == banked | BACKED |
| 47–48 | a(20)–a(23) by transfer matrix | `results/ns_a20/PROVENANCE.md` (`cpp/tma`); `ns_a21`, `ns_a23` (column kernel) | the run records | BACKED |
| 48–49 | a(24)–a(40): earlier rows fix the polynomial factors for the most expensive cells | `results/ns_a24/PROVENANCE.md` (first injection, k ≤ 7) through `ns_a40` (k ≤ 18, H ≥ 22) | `ns-gate-diag-pins`; 171 injected cells self-consistent with the refit | BACKED |
| 51–52 | for n ≤ 22 transfer matrix and Redelmeier agree | `results/redelmeier_row22/PROVENANCE.md` (fleet, 2026-07-16) | rows 1–22 == banked; the sentence's 22 == the top row of the record | BACKED |
| 52–53 | for n ≤ 40 the coloring method confirms the T(n,H ≤ 19) cells | `results/cutcount_b1/rows41/`; `docs/proofs/cutcount-identity.md` | 589 cells re-derived from C_H by second difference == triangle; the sentence's 19 and 40 == the record's reach; `gate-cutcount-assembly` | BACKED |
| 53–54 | all a(n) pass Burnside-congruence checks and the closed forms | `results/symmetry-classes.md`; `results/subgroup_counts.txt` | a(n) mod 4 recomputed from I(C4)+I(D2ax)+I(D2diag)−2I(D4) for n ≤ 40; the diagonal checks | BACKED. The in-make `gate-subgroup` reaches n ≤ 11; n ≤ 40 is the banked 2026-08-07 census |
| 70–79, 166 | each symmetry class names its OEIS entry | `oeis/A0*.txt`; `results/b0*_upload.txt` | the A-number in each item == the b-file its column is checked against | BACKED |
| 82–83 | a 1-cell hole needs 4 cells; a domino or two 1-cell holes need 6 | `results/holes_n18.txt`; `results/maxhole.txt` | smallest n with k ≥ 1 is 4, with k ≥ 2 is 6, with hole area ≥ 2 is 6 | BACKED |
| 85–86 | row sums of T(n,H) give a(n) | `results/triangle.txt` | row sums ×40 | BACKED |
| 127 | terms 1–18 match A006770 | `fixtures/b006770.txt` (lines ≤ 18 are OEIS's; 19–20 ours, `docs/external-anchors.md`) | banked vs OEIS ×18; `gate-bfiles` | BACKED |
| 131–133 | T(n,n) = 3^{n−1}, one cell per row | `docs/proofs/T-n-nm1.md` | ×40 | BACKED |
| 133–135 | H > n/2: T = P_{n−H}(n)·3^{3H−2n−1}, P_k integer-valued of degree k with leading coefficient 25^k/k! | `docs/proofs/diagonal-law.md` | integrality at every banked in-onset cell, k ≤ 19; leading coefficient of each refit P_k, k ≤ 18, the 25 read from the sentence | BACKED |
| 135 | P_k explicitly known for k ≤ 19 | `orchestrator/sweep.go` `maxDiagKMax` | the sentence's 19 == the constant | BACKED |
| 136 | fitted against computed values and verified against values from later rows | the 171 real-swept cells beyond the two fit cells, k ≤ 18; `docs/publication.md` §6, §8 | as above | **SCOPE.** True for k ≤ 18. P_19's diagonal has two in-onset real cells, T(39,20) and T(40,21), and both fit it; no later row exists. The Undertow re-derivation from short cells is a consistency check on those two values, not a holdout. |
| 136–137 | P_k can be fixed after computing the 3k-th row | `docs/publication.md` §2.2 | with 25^k/k! fixed, rows 2k+1..3k pin P_k and predict every later banked in-onset cell, k ≤ 13 | BACKED, given the previous sentence: see A4 |
| 160 | shaded cells can be computed using formulas | — | shaded ⇔ H > n/2, all 78 cells | BACKED |
| 164–168 | new one-sided, free, bilateral, asymmetric and non-polyomino counts; few polyplets are polyominoes; one-sided → a(n)/4, free → a(n)/8 | `results/b0*_upload.txt`; `fixtures/b000105.txt` | tables ×92; non-polyomino = free − A000105 (n = 18..32); polyominoes under 1 in 1000 of free; 4·one-sided/a(n) − 1 and 8·free/a(n) − 1 positive, decreasing two steps apart (they alternate by parity), under 10⁻⁶ at the last row | BACKED |
| 220–222 | bilateral + asymmetric = free | — | ×15 | BACKED |
| 226–229 | holes counted in the transfer matrix by the Euler characteristic through n = 18; Redelmeier flood-fill checked n ≤ 14 | `results/holes_n18.txt` (`tma_holes`, `cpp/tma/euler.h`; dalby copy identical); `results/holes_n14.txt` (`g2 --holes`); headers in the files | the sentences' 18 and 14 == the files' reach; the files agree on every (n,k) with n ≤ 14; hole rows sum to a(n); `gate-tma` check H | BACKED |
| 289 | a(n)^{1/n} → λ ≈ 7.11, checkable from Table 1 | `results/growth-constant.md`; `results/growth-constant.md` | a(m+n) ≥ a(m)a(n) on the table | **SCOPE.** The table gives a(40)^{1/40} = 6.2208 and a(40)/a(39) = 6.9352; 7.11 is an extrapolation of the ratios. The comment block above the sentence has the numbers and anchors. Cite-or-drop, your item 5. |
| 294–296 | Redelmeier used to extend a(n) and to confirm; only through n = 22 | as 47 and 51–52 | as 51–52 | BACKED |
| 298–302 | the transfer matrix: frozen left side, previous-column constraints, top and bottom flags, connectivity, cells remaining | `core/signature.h`, `core/transition.h`, the prune at `core/signature.h:123-174`; `docs/engine-record.md` §0 | the engine gates | BACKED |
| 304–345 | the T(n,n−1) derivation: three options per single cell; one doubled row; domino or split, a gap of three cannot be spanned; n−3 interior rows; 16 and 4·1+1·5 per interior joiner; 2·5 at the ends; (25n−45)·3^{n−4} | `docs/proofs/T-n-nm1.md`; `docs/publication.md` §2.1 | every fixed polyplet of size ≤ 8 enumerated (Redelmeier); for n = 4..8 the interior-domino, interior-split, end-domino and end-split counts and the zero for gap ≥ 3 each equal the paper's coefficient, read from its formula, times (n−3)·3^{n−4} or 3^{n−4}; the total ×37 | BACKED |

## A4. `OPEN` Keep the two P_k sentences adjacent

"Fixed after computing the 3k-th row" is correct *because* the previous
sentence supplies the leading coefficient `25^k/k!`. Separated, it reads off by
one. Audit §2.2.

The comment block above the abstract's old provenance sentence (item A2 of the
2026-08-18 audit, DONE 2026-09-04) is stale and stays until you say to pull it.

---

# B. Sections that do not exist

`docs/publication-split.md` on P1: "Most of the 30-50 hours is the engine
chapter and section Reproducibility, both still unwritten."

## B1. `MATERIAL READY` Reproducibility

`docs/publication.md` is the assembled source material — every
claim, the number it rests on, the command that regenerates it, the gate that
pins it, and the limit past which it must not be pushed, all regenerated from
banked artifacts rather than copied from notes. Also `docs/publication.md`
items 2-4. This is the section a stranger reads first under a repo release.

## B2. `MATERIAL READY` The engine chapter

Methods currently has three paragraphs. `docs/engine-record.md`
(2026-08-06, **updated 2026-09-04** at jasonp's direction) is the source:
every component with a code anchor, which kernel produced which term, the
per-term cost ledger a(26)–a(41), the a(41) route, and the 2026-09-02 audit's
list of engine sentences not to write.

## B3. `OPEN` The paper has no bibliography

Zero `\cite`, no `thebibliography`. Under the P disclosure the machine does the
novelty search and the citations, so this is assembled work, not his:
Redelmeier, Klarner-Rivest, Jensen, Barequet-Ben-Shachar, Bacher, Madras, and
the OEIS entries. Anything un-findable goes to `literature/MISSING.md`.

## B4. `OPEN` External anchors, as a subsection of the validation chapter

Audit §4.4: what the machinery reproduces that it did not produce — a(1)-a(18)
against OEIS, Bender's and Klarner-Rivest's constants at certified precision,
Richard's limit law, and the Fortuin-Kasteleyn/Potts identity behind the second
source. Four items, all checkable by the reader, none of them ours.
`docs/external-anchors.md`. A stronger opening to a validation chapter than any
internal consistency check, because the reader does not have to trust us.

## B5. `OPEN` The frontier moved past the paper: a(41)

The paper stops at a(40). `a(41) = 393811462683918679824582849262105` is banked
with an independent recount that never reads the wired table, and **a(n) is
rule-independent for every n <= 39**. That is a different confidence story from
the one the abstract tells, and the route that produced it — heights 1-19 real,
20-41 from the Undertow-pinned tower — is not in Methods at all.
`results/confidence.md` is the plain-terms version; `results/a41/PROVENANCE.md`
and `results/undertow.md` are the record. Interacts with A2.

**2026-09-04, jasonp: a(41) goes in, with an asterisk.** What the asterisk can
honestly carry: heights 1–19 swept by two engines that agree on all 19 cells;
heights 20–41 composed from the diagonal tower, levels `k <= 19` wired and
`k = 20, 21` pinned from below-onset cells; level 21 rests on one depth pair
whose stated guard tests integrality only (`docs/audits/AUDIT-2026-09-02.md:44-80`, M1).
The one-second depth-5 re-pin test that closes M1 has not been run (ayr
unreachable 2026-09-04; dalby refused the key from the session shell). Run it
before the asterisk is worded. "Conjecture" undersells the 19 swept heights;
the audit's own phrasing at `:128-138` is the accurate one.

**2026-09-05, Claude: M1's test run, and gated.** `undertow_a41.py --jmax 5
--perheight results/a41`: level 21 pinned from `T(38,17)`, `T(39,18)`,
`T(40,19)`, three pairs, two independent checks, a(41) reproduced digit for
digit; `--verify --jmax=5` 18 levels over 160 pairs, `--audit --jmax=5` 342
cells, 0 wrong. The blind spot measured: `sig[3][21] + 9` in a shadow table
leaves the congruence gate green and moves the depth-4 a(41) by exactly 9;
depth 5 refuses it. `make gate-undertow-pairs` now carries that as a RED
control. What the asterisk can carry is therefore: heights 1–19 swept by two
engines agreeing on all 19 cells (gated, `gate-cutcount-assembly`); heights
20–41 from the tower, every level overdetermined, sharing `D_j(20..21)` between
its two fits; no enumeration of `T(41,20)` exists (the H = 20 sweep, ~11 h on
dalby, unrun). `results/a41/PROVENANCE.md` and `results/confidence.md` say the
same. Wording is yours.

**2026-09-05 21:19 EDT, Claude: the H = 20 sweep landed.** 9.63 h on dalby's
76 cores, rc = 0. `T(41,20) = 18004779862205054677763902712770`, equal to the
tower's prediction digit for digit; banked as `results/a41/h20.out`; the
assembler now sweeps H <= 20 and takes 21..41 from the tower (800 regression
cells agree); `gate-undertow-pairs` carries the holdout comparison with a RED
control. What the asterisk can now carry: heights 1-19 by two engines, height
20 enumerated once and equal to the formula that predicted it, heights 21-41
from the tower with a(41) no longer touching `P_21`. Still not a(40)'s grade:
the coloring engine stops at H = 19, so `T(41,20)` has one enumeration.

---

# C. Results in the repo but not in the paper

2026-08-05, ordered by how much machinery is needed to follow the
**statement** — not by importance. Numbering is stable; do not renumber.

## C1. `MATERIAL READY` Validation architecture — see B1

the project handoff file (removed from the repository), `results/second-sources.md`, `paper/polyplets-report.tex:485`.
Every production run re-derives all smaller terms; Redelmeier confirms to
n=22; an independent strip transfer-matrix engine sharing no enumeration code
confirms T(n,H) for H≤14 across all n≤40 (469 cells, 0 mismatches). Also the
tier system (computed twice / computed once / composed with pinned formulas).
Prose only, no math. Biggest hole in the report right now.

## C2. `OPEN` Fekete's lower bound: λ ≥ a(40)^(1/40) = 6.2208

`results/growth-constant.md`. Supermultiplicativity, one sentence,
and it puts a floor under the "λ≈7.11" remark.

## C3. `OPEN` The growth-rate paragraph is a stub

`paper/polyplets-report.tex:200`, `results/growth-constant.md`. Ratio fit
with a confluent term Δ₁=½ gives λ≈7.111, θ≈−1.02, matching the universal 2-D
lattice-animal θ=−1; differential approximants independently give λ=7.110(1),
θ=−1.000(1). The report currently says "λ≈7.11, checkable from Table 1."

**Added 2026-08-06:** the ratio limit is not just an assumption — `a(n+1)/a(n)
→ λ` is a **theorem** for site animals on the king lattice (Madras 1999,
Thm 2.2 / Cor 3.6; his §3.1(f) spread-out lattice at M=1 with the sup norm
*is* the king lattice). One sentence, and it licenses the whole ratio-fit
paragraph instead of leaving it as a numerical hope.

## C4. `OPEN` Where the 25 in the T(n,n−1) derivation comes from: 25 = 16 + 9

`results/diagonal-formula.md`. The derivation in the report already computes 16
(domino joiner) + 9 (split joiner). The defect-gas note shows that "split" is
exactly the two-cell cluster weight and that the same bookkeeping generates
every P_k. One paragraph, and it makes the hand derivation the k=1 case of a
machine.

## C5. `IN (2026-09-05, his call; cut if the explanation will not hold)` T(n,n−2) in closed form

`docs/proofs/T-n-nm2-and-general.md`. T(n,n−2) = ½(625n²−2459n+1134)·3^{n−7}
for n≥5, proved in the same style as the n−1 case (one row of 3, or two rows
of 2), brute-verified n=4..8 and against the triangle to n=20. Natural next
paragraph after the one already written.

## C6. `DEFERRED 2026-09-04` The hole-fill bijection

`results/subclasses.md`. An n-cell polyplet with one
area-1 hole ↔ (hole-free (n+1)-cell polyplet, choice of interior cell). Exact,
provable, three sentences, and it sits directly under the existing hole table.

## C7. `DEFERRED 2026-09-04` Maximum enclosed hole area: M(n) = ⌊((n−2)²+4)/8⌋

`results/subclasses.md`, `results/maxhole.txt`. Exact by enumeration to
n=17 (M(17)=28 predicted and confirmed). The hole section counts holes but
never asks how big they get. **Revised again 2026-08-06, both sources read:**
it is the grid isoperimetric inequality, entire, and nothing here is a new
theorem. Sieben 2008 Thm 4.1 is the single-hole half verbatim (σ(e) =
⌊e²/8 − e/2 + 1⌋, no inversion); the same minimum for an *arbitrary finite
subset* of ℤ² — **Wang & Wang 1977**, ℤ² count explicit in Altshuler et al.
2006 — applied to the union of all the holes gives the all-holes half in three
lines. **Nothing is conditional any more** — but the statement must be printed
as a corollary, citing Wang–Wang first.
What is ours: the question (the hole literature counts holes, it doesn't
measure them) and the n ≤ 17 enumeration.

## C8. `OPEN` Component stratification C(n,c)

`results/subclasses.md`. Polyplets split by number of
rook-connected components. C(n,1)=A001168 (fixed polyominoes) and C(n,n)=A001168
*also*, via a clean bijection — edge-isolated king animals are polyominoes on
the 45°-rotated sublattice. The distribution peaks near c≈n/2: the typical
polyplet is ~n/2 tiny pieces joined at corners, which is the mechanism behind
λ≈7.11 ≫ 4.06. Triangle not in OEIS.

## C9. `OPEN` Directed king animals as a closed-form anchor

`results/subclasses.md`, `results/subclasses.md`.
Bacher's directed king animals have GF ¼((1+t)/√(1−6t+t²)−1) and growth
exactly 3+2√2 ≈ 5.8284. Filtering the enumeration down to them reproduces
A047781 exactly — validation against a *formula* rather than a second
enumeration, available at any n.

## C10. `OPEN` How the height of a typical polyplet grows

`results/growth-constant.md`, `results/growth-constant.md`. mean_H/n
falls monotonically 0.745 (n=4) → 0.379 (n=40): growing but sublinear height,
neither fixed-small-H nor n/2. Plus a universal limit shape under rescaling.
State qualitatively — both notes were explicitly narrowed to drop the ν
exponent claim.

## C11. `DEFERRED 2026-09-04` Hole-free polyplets grow strictly slower, exponentially so

`results/subclasses.md`. The hole-free fraction decays
exponentially, not polynomially: a hole is an entropic gain, not a rare
accident. Qualitative only — the note forbids quoting λ₀≈6.94.
**Revised 2026-08-06: this is a corollary of Madras 1999's pattern theorem**
(take the pattern "eight neighbors present, center absent"; hole-free animals
contain zero translates, hence are exponentially rare), so print it as a cited
consequence, not a measurement. The measured ratio λ₀/λ ≈ 0.978 is the part
that is ours, and it is n ≤ 18 data.

## C12. `OPEN` A rigorous two-sided bracket: 6.543 ≤ λ ≤ 9.3154

`results/growth-constant.md`, `docs/proofs/polyplet-upper-bound.md`,
`paper/polyplets-report.tex:218`. Lower: certified strip ladder to H=17
(6,536,381 states), each rung a Collatz–Wielandt witness checkable in exact
integer arithmetic, anchored at μ₂=1+√2. Upper: a Bui-style finite-type
convolution certificate, x=2147/20000. No upper bound on λ appears in the
literature.

## C13. `OPEN` The diagonal law is a theorem, not a fit

`docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`. §Results currently
says P_k was "fitted against computed values of T(n,H) and verified against
values from later rows." The shape is proved: degree ≤ k, the 3-power,
integrality of P_k, and the sharp onset n ≥ 2k+1 (failure at n=2k verified on
all banked data). Also worth checking: the report says P_k known for k≤19; the
pinned range on record is k≤18. **Stale 2026-09-04:** `k <= 19` is wired
(`orchestrator/sweep.go:2306`); see A3.

## C14. `OPEN` The diagonal-mirror triangle

`results/symmetry-classes.md`, `paper/polyplets-report.tex:648`. d(S,S+k) is
quasi-polynomial in S with period 2 and degree k per parity class. Still
conjectural — the last unproved law — which is itself worth saying in print.

## C15. `OPEN` The same law holds on every row-local lattice

`docs/proofs/universal-diagonal-law.md`, `results/diagonal-formula.md`.
T(H+k,H) = q_k(H)·b^H where b is the number of up-neighbors: b=1 square, b=2
hex, b=3 king. The report's 3^{n−1} is the b=3 instance of a theorem. Proved,
all three instances machine-checked.

## C16. `OPEN` The triangle mod 3

`results/arithmetic-structure.md`. The whole diagonal family's mod-3 behavior is
governed by one algebraic series: the unique W ∈ 𝔽₃[[t]] with W(0)=1 solving
W³ = W² + t. 15/15 checks including a 342-cell check against the banked
triangle. Compact statement; the derivation is where it starts costing.

## C17. `DEFERRED 2026-09-04` The maximum number of holes: `n - ceil(2*sqrt(n)) + 1`

`results/subclasses.md`. This is **A248333**, with a construction
proving the lower bound; n = 10 measured at 4 and n = 11 at 5, both predicted
first. Distinct from C7, which is the maximum hole *area*. The hole section
counts holes and never asks how many there can be.

---

## Above the line

Deliberately cut as beyond the "follow the statement unaided" bar, in rough
order of remove:

- **Non-D-finiteness of the by-height GF** (`results/anisotropic-not-dfinite.md`,
  `paper/polyplets-report.tex:878`). Unconditional, and the strongest pure-math
  result in the repo. Worth putting in the paper as a *statement* if desired;
  the Rechnitzer haruspicy machinery behind it is not.
- **Smith normal form of the triangle is an all-3-powers group**
  (`results/arithmetic-structure.md`, `results/closed-doors.md` C1).
- **The v₅ denominator law** (`results/arithmetic-structure.md`) — already demoted
  to a closed door on its own merits.
- **Convex polyplets by area** (`docs/proofs/convex-mirage.md`,
  `results/subclasses.md`) — q-series, empirically non-D-finite.
- **The differential-approximant methodology** behind item 3 (the numbers it
  produces are in scope; the method is not).

---

# D. Every result the paper must state and prove, in dependency order

2026-09-05, at jasonp's request ("list all the results that the current
technical report requires me to state and prove, even if already done, order
them topologically"). Line numbers are into `technical-report.tex` at the
comparison base above. "Needs" names the earlier items each one rests on.
Onset sharpness (failure at n = 2k) is not asserted by the current text and
is not required.

## Lattice facts

1. **Polyominoes are polyplets.** Rook adjacency implies king adjacency.
   Implicit; used by the A194596 column and by "few polyplets are
   polyominoes" (line 165). Needs nothing.
2. **Row occupancy and the walk-row cut.** A connected animal occupies every
   row of its bounding box; king adjacency changes the row by at most one, so
   a one-cell row separates the animal. Not in the paper. The engine of every
   closed form below. Proved: `docs/proofs/diagonal-law.md` step 1. Needs
   nothing.
3. **Height partition.** Σ_H T(n,H) = a(n). Stated as a definition, line 85.
   Needs nothing.

## Closed forms

4. **T(n,n) = 3^(n−1).** Consecutive one-cell rows connect iff the column
   offset is in {−1,0,1}. In the paper with proof, lines 131 and 293.
   Needs 2.
5. **Doubled-row gap lemma.** Two cells in one row join only as a domino or
   with a gap of exactly one empty cell, bridged by a single cell in the
   middle column of a neighboring row. One clause, line 314. Proved:
   `docs/proofs/T-n-nm1.md` §3. Needs 2.
6. **T(n,n−1) = (25n−45)·3^(n−4)**, n ≥ 3. In the paper with derivation,
   lines 304–345; census n = 4..8 in the verifier. Needs 2, 4, 5.
7. **The diagonal law.** For n ≥ 2k+1, T(n,n−k) = P_k(n)·3^(n−3k−1), P_k of
   degree ≤ k, integer-valued. Stated lines 133–135 as a fitted fact.
   Proved: `docs/proofs/diagonal-law.md` and Lean; not in the paper.
   Needs 2, 3.
8. **Leading coefficient 25^k/k!**, so deg P_k = k exactly. Stated line 135.
   Proved: `docs/proofs/grand-form.md`, taking 25 from item 6. Not in the
   paper. Needs 6, 7.
9. **P_k pinned by rows 2k+1..3k.** With the leading coefficient fixed, k
   unknowns, k in-onset cells, nonsingular Vandermonde. Stated line 136.
   Needs 7, 8. Item A4: wrong if separated from the sentence before it.
10. **Composition of a(24)–a(40).** Cells with H > n/2 are in onset, so swept
    cells plus closed-form evaluations sum to a(n), and the closed forms
    check the swept cells. Abstract. Needs 3, 9.
11. **T(n,n−2) = ½(625n²−2459n+1134)·3^(n−7)**, n ≥ 5. Decided in
    2026-09-05, not yet in the tex. Proof: `docs/proofs/T-n-nm2-and-general.md`
    §1, in the style of item 6. Needs 2, 4, 5. Leading coefficient 625/2 is
    the k = 2 instance of item 8.

## Growth

12. **Exponential upper bound a(n) ≤ C^n.** Spanning-tree count for connected
    n-sets through a fixed cell in a degree-8 graph, C ≤ 7e or so. Not in the
    paper. Makes λ finite; used by 17. Cite or prove in two lines. Needs
    nothing.
13. **Supermultiplicativity and Fekete.** Diagonal-corner concatenation is
    injective, so a(m+n) ≥ a(m)a(n); hence a(n)^(1/n) → λ = sup a(n)^(1/n),
    λ ≥ a(40)^(1/40) = 6.2208, a(n) ≤ λ^n. Convergence asserted line 289
    without proof; his argument is in the tex comment above it. Needs 12.
14. **λ ≈ 7.11.** Not a theorem. 2026-09-04 decision: cite or drop (Madras
    ratio theorem, differential approximants, L3 bracket 6.543 ≤ λ ≤ 9.3154).
    Needs 13 to be well defined.

## Symmetry

15. **Burnside on D4.** Free = ⅛ Σ_{D4} Fix(g); one-sided = ¼ Σ_{C4} Fix(g);
    bilateral = free classes with a reflection; bilateral + asymmetric =
    free. Only the last is in the paper, line 220. Cite Burnside. Needs
    definitions only.
16. **The Burnside congruence** a(n) ≡ I(C4) + I(D2ax) + I(D2diag) − 2·I(D4)
    (mod 4), from the orbit-size count with F(H) for stabiliser exactly H.
    Invoked abstract line 53, never stated. Three lines in
    `results/symmetry-classes.md`. Needs 15.
17. **Symmetric polyplets are negligible.** Each nontrivial Fix(g)(n) ≤
    poly(n)·a(⌈n/2⌉ + O(1)) (a symmetric animal is a half plus an axis);
    a(n) ≥ 6.2208^(n−39) from 13; the ratio vanishes exponentially provided
    C^(1/2) < 6.2208. This is "one-sided → a(n)/4, free → a(n)/8", line 166.
    Not in the paper, not in the repo as a proof. Needs 12, 13, 15.
18. **Polyominoes are a vanishing share.** Fixed polyominoes ≤ 4.65^n
    (Klarner–Rivest) against a(n) ≥ 6.2208^(n−39). "Few polyplets are
    polyominoes thanks to the higher growth rate", line 165; A194596 = free
    polyplets − A000105 rests on item 1. Needs 1, 13, 15 for the free
    version, one citation.

## Holes

19. **Hole definition and the Euler count.** A hole is a bounded
    rook-connected component of the complement. With 8-connected foreground
    and 4-connected background, Gray's 2×2-window formula with the −2·Q_D
    branch gives E = components − holes, so holes = 1 − E for a connected
    animal, and E accumulates over column pairs. What "tracking the Euler
    characteristic" (line 226) rests on. Not stated. Cite Gray 1971 or
    Rosenfeld. Needs the definition at line 81.
20. **Minimal enclosures.** A 1-cell hole needs its four rook neighbors,
    pairwise king-adjacent, so 4 is minimal and unique; a domino hole needs
    its six; two 1-cell holes need ≥ 6 (two 4-sets share ≤ 2 cells), achieved
    diagonally. Stated lines 82–83 without proof. Needs 19.

## Methods

21. **Transfer-matrix signature sufficiency.** Equal frozen column,
    connectivity partition, top/bottom flags and remaining budget give equal
    completions, so the count over signatures is T(n,H) exactly. Described
    lines 298–302, correctness never stated. Cite Jensen or Conway; state the
    invariant. Needs 2, 3.
22. **The coloring second source.** C_H(n) = Σ_{h≤H} (H−h+1)·T(n,h), T its
    second difference in H; the connected count is the q¹ coefficient of the
    Fortuin–Kasteleyn polynomial. Abstract line 52. 2026-09-04 decision:
    machine work with a pointer, or drop. If kept, state only the
    second-difference identity and cite `docs/proofs/cutcount-identity.md`.
    Needs 3.
23. **Redelmeier.** Citation only.

**Status summary.** Stated and proved in the paper: 4, 6. Stated or invoked
without proof: 3, 7, 8, 9, 13, 15, 16, 20. Needed by the text, never stated:
1, 2, 5, 12, 17, 18, 19, 21. Decided in, unwritten: 11. Cite-or-drop: 14, 22.
