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
one of them. `results/figs/triangle_provenance.svg` colours the 820 cells by
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
- **Spelling and punctuation:** last.
- **Abstract: DONE** (end of session 2026-09-04). Next by the finish list:
  Reproducibility (B1), then the engine chapter (B2) from
  `docs/paper1-engine-chapter.md`, then item 6 (C13 wording) by Q&A.

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
| 52–53 | for n ≤ 40 the colouring method confirms the T(n,H ≤ 19) cells | `results/cutcount_b1/rows41/`; `docs/proofs/cutcount-identity.md` | 589 cells re-derived from C_H by second difference == triangle; the sentence's 19 and 40 == the record's reach; `gate-cutcount-assembly` | BACKED |
| 53–54 | all a(n) pass Burnside-congruence checks and the closed forms | `results/subgroup-mod4.md`; `results/subgroup_counts.txt` | a(n) mod 4 recomputed from I(C4)+I(D2ax)+I(D2diag)−2I(D4) for n ≤ 40; the diagonal checks | BACKED. The in-make `gate-subgroup` reaches n ≤ 11; n ≤ 40 is the banked 2026-08-07 census |
| 70–79, 166 | each symmetry class names its OEIS entry | `oeis/A0*.txt`; `results/b0*_upload.txt` | the A-number in each item == the b-file its column is checked against | BACKED |
| 82–83 | a 1-cell hole needs 4 cells; a domino or two 1-cell holes need 6 | `results/holes_n18.txt`; `results/maxhole.txt` | smallest n with k ≥ 1 is 4, with k ≥ 2 is 6, with hole area ≥ 2 is 6 | BACKED |
| 85–86 | row sums of T(n,H) give a(n) | `results/triangle.txt` | row sums ×40 | BACKED |
| 127 | terms 1–18 match A006770 | `fixtures/b006770.txt` (lines ≤ 18 are OEIS's; 19–20 ours, `docs/external-anchors.md`) | banked vs OEIS ×18; `gate-bfiles` | BACKED |
| 131–133 | T(n,n) = 3^{n−1}, one cell per row | `docs/proofs/T-n-nm1.md` | ×40 | BACKED |
| 133–135 | H > n/2: T = P_{n−H}(n)·3^{3H−2n−1}, P_k integer-valued of degree k with leading coefficient 25^k/k! | `docs/proofs/diagonal-law.md` | integrality at every banked in-onset cell, k ≤ 19; leading coefficient of each refit P_k, k ≤ 18, the 25 read from the sentence | BACKED |
| 135 | P_k explicitly known for k ≤ 19 | `orchestrator/sweep.go` `maxDiagKMax` | the sentence's 19 == the constant | BACKED |
| 136 | fitted against computed values and verified against values from later rows | the 171 real-swept cells beyond the two fit cells, k ≤ 18; `docs/paper1-reproducibility.md` §6, §8 | as above | **SCOPE.** True for k ≤ 18. P_19's diagonal has two in-onset real cells, T(39,20) and T(40,21), and both fit it; no later row exists. The Undertow re-derivation from short cells is a consistency check on those two values, not a holdout. |
| 136–137 | P_k can be fixed after computing the 3k-th row | `docs/main-paper-audit-2026-08-18.md` §2.2 | with 25^k/k! fixed, rows 2k+1..3k pin P_k and predict every later banked in-onset cell, k ≤ 13 | BACKED, given the previous sentence: see A4 |
| 160 | shaded cells can be computed using formulas | — | shaded ⇔ H > n/2, all 78 cells | BACKED |
| 164–168 | new one-sided, free, bilateral, asymmetric and non-polyomino counts; few polyplets are polyominoes; one-sided → a(n)/4, free → a(n)/8 | `results/b0*_upload.txt`; `fixtures/b000105.txt` | tables ×92; non-polyomino = free − A000105 (n = 18..32); polyominoes under 1 in 1000 of free; 4·one-sided/a(n) − 1 and 8·free/a(n) − 1 positive, decreasing two steps apart (they alternate by parity), under 10⁻⁶ at the last row | BACKED |
| 220–222 | bilateral + asymmetric = free | — | ×15 | BACKED |
| 226–229 | holes counted in the transfer matrix by the Euler characteristic through n = 18; Redelmeier flood-fill checked n ≤ 14 | `results/holes_n18.txt` (`tma_holes`, `cpp/tma/euler.h`; dalby copy identical); `results/holes_n14.txt` (`g2 --holes`); headers in the files | the sentences' 18 and 14 == the files' reach; the files agree on every (n,k) with n ≤ 14; hole rows sum to a(n); `gate-tma` check H | BACKED |
| 289 | a(n)^{1/n} → λ ≈ 7.11, checkable from Table 1 | `results/series-analysis-da.md`; `results/concatenation-upper-bound.md` | a(m+n) ≥ a(m)a(n) on the table | **SCOPE.** The table gives a(40)^{1/40} = 6.2208 and a(40)/a(39) = 6.9352; 7.11 is an extrapolation of the ratios. The comment block above the sentence has the numbers and anchors. Cite-or-drop, your item 5. |
| 294–296 | Redelmeier used to extend a(n) and to confirm; only through n = 22 | as 47 and 51–52 | as 51–52 | BACKED |
| 298–302 | the transfer matrix: frozen left side, previous-column constraints, top and bottom flags, connectivity, cells remaining | `core/signature.h`, `core/transition.h`, the prune at `core/signature.h:123-174`; `docs/paper1-engine-chapter.md` §0 | the engine gates | BACKED |
| 304–345 | the T(n,n−1) derivation: three options per single cell; one doubled row; domino or split, a gap of three cannot be spanned; n−3 interior rows; 16 and 4·1+1·5 per interior joiner; 2·5 at the ends; (25n−45)·3^{n−4} | `docs/proofs/T-n-nm1.md`; `docs/main-paper-audit-2026-08-18.md` §2.1 | every fixed polyplet of size ≤ 8 enumerated (Redelmeier); for n = 4..8 the interior-domino, interior-split, end-domino and end-split counts and the zero for gap ≥ 3 each equal the paper's coefficient, read from its formula, times (n−3)·3^{n−4} or 3^{n−4}; the total ×37 | BACKED |

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

`docs/paper1-reproducibility.md` is the assembled source material — every
claim, the number it rests on, the command that regenerates it, the gate that
pins it, and the limit past which it must not be pushed, all regenerated from
banked artifacts rather than copied from notes. Also `docs/acceptance-queue.md`
items 2-4. This is the section a stranger reads first under a repo release.

## B2. `MATERIAL READY` The engine chapter

Methods currently has three paragraphs. `docs/paper1-engine-chapter.md`
(2026-08-06, **updated 2026-09-04** at jasonp's direction) is the source:
every component with a code anchor, which kernel produced which term, the
per-term cost ledger a(26)–a(41), the a(41) route, and the 2026-09-02 audit's
list of engine sentences not to write.

## B3. `OPEN` The paper has no bibliography

Zero `\cite`, no `thebibliography`. Under the P disclosure the machine does the
novelty search and the citations, so this is assembled work, not his:
Redelmeier, Klarner-Rivest, Jensen, Barequet-Ben-Shachar, Bacher, Madras, and
the OEIS entries. Anything un-findable goes to `papers/MISSING.md`.

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
whose stated guard tests integrality only (`AUDIT-2026-09-02.md:44-80`, M1).
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

---

# C. Results in the repo but not in the paper

2026-08-05, ordered by how much machinery is needed to follow the
**statement** — not by importance. Numbering is stable; do not renumber.

## C1. `MATERIAL READY` Validation architecture — see B1

`HANDOFF.md`, `results/strip-engine.md`, `paper/polyplets-report.tex:485`.
Every production run re-derives all smaller terms; Redelmeier confirms to
n=22; an independent strip transfer-matrix engine sharing no enumeration code
confirms T(n,H) for H≤14 across all n≤40 (469 cells, 0 mismatches). Also the
tier system (computed twice / computed once / composed with pinned formulas).
Prose only, no math. Biggest hole in the report right now.

## C2. `OPEN` Fekete's lower bound: λ ≥ a(40)^(1/40) = 6.2208

`results/concatenation-upper-bound.md`. Supermultiplicativity, one sentence,
and it puts a floor under the "λ≈7.11" remark.

## C3. `OPEN` The growth-rate paragraph is a stub

`paper/polyplets-report.tex:200`, `results/series-analysis-da.md`. Ratio fit
with a confluent term Δ₁=½ gives λ≈7.111, θ≈−1.02, matching the universal 2-D
lattice-animal θ=−1; differential approximants independently give λ=7.110(1),
θ=−1.000(1). The report currently says "λ≈7.11, checkable from Table 1."

**Added 2026-08-06:** the ratio limit is not just an assumption — `a(n+1)/a(n)
→ λ` is a **theorem** for site animals on the king lattice (Madras 1999,
Thm 2.2 / Cor 3.6; his §3.1(f) spread-out lattice at M=1 with the sup norm
*is* the king lattice). One sentence, and it licenses the whole ratio-fit
paragraph instead of leaving it as a numerical hope.

## C4. `OPEN` Where the 25 in the T(n,n−1) derivation comes from: 25 = 16 + 9

`results/defect-gas.md`. The derivation in the report already computes 16
(domino joiner) + 9 (split joiner). The defect-gas note shows that "split" is
exactly the two-cell cluster weight and that the same bookkeeping generates
every P_k. One paragraph, and it makes the hand derivation the k=1 case of a
machine.

## C5. `OPEN` T(n,n−2) in closed form

`docs/proofs/T-n-nm2-and-general.md`. T(n,n−2) = ½(625n²−2459n+1134)·3^{n−7}
for n≥5, proved in the same style as the n−1 case (one row of 3, or two rows
of 2), brute-verified n=4..8 and against the triangle to n=20. Natural next
paragraph after the one already written.

## C6. `DEFERRED 2026-09-04` The hole-fill bijection

`results/hole-fill-interior-cell-identity.md`. An n-cell polyplet with one
area-1 hole ↔ (hole-free (n+1)-cell polyplet, choice of interior cell). Exact,
provable, three sentences, and it sits directly under the existing hole table.

## C7. `DEFERRED 2026-09-04` Maximum enclosed hole area: M(n) = ⌊((n−2)²+4)/8⌋

`results/maxhole-proof.md`, `results/maxhole.txt`. Exact by enumeration to
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

`results/component-stratification.md`. Polyplets split by number of
rook-connected components. C(n,1)=A001168 (fixed polyominoes) and C(n,n)=A001168
*also*, via a clean bijection — edge-isolated king animals are polyominoes on
the 45°-rotated sublattice. The distribution peaks near c≈n/2: the typical
polyplet is ~n/2 tiny pieces joined at corners, which is the mechanism behind
λ≈7.11 ≫ 4.06. Triangle not in OEIS.

## C9. `OPEN` Directed king animals as a closed-form anchor

`results/directed-king-animals.md`, `results/directed-cone-anchor.md`.
Bacher's directed king animals have GF ¼((1+t)/√(1−6t+t²)−1) and growth
exactly 3+2√2 ≈ 5.8284. Filtering the enumeration down to them reproduces
A047781 exactly — validation against a *formula* rather than a second
enumeration, available at any n.

## C10. `OPEN` How the height of a typical polyplet grows

`results/nu-exponent.md`, `results/height-distribution-collapse.md`. mean_H/n
falls monotonically 0.745 (n=4) → 0.379 (n=40): growing but sublinear height,
neither fixed-small-H nor n/2. Plus a universal limit shape under rescaling.
State qualitatively — both notes were explicitly narrowed to drop the ν
exponent claim.

## C11. `DEFERRED 2026-09-04` Hole-free polyplets grow strictly slower, exponentially so

`results/hole-free-growth-constant.md`. The hole-free fraction decays
exponentially, not polynomially: a hole is an entropic gain, not a rare
accident. Qualitative only — the note forbids quoting λ₀≈6.94.
**Revised 2026-08-06: this is a corollary of Madras 1999's pattern theorem**
(take the pattern "eight neighbours present, centre absent"; hole-free animals
contain zero translates, hence are exponentially rare), so print it as a cited
consequence, not a measurement. The measured ratio λ₀/λ ≈ 0.978 is the part
that is ours, and it is n ≤ 18 data.

## C12. `OPEN` A rigorous two-sided bracket: 6.543 ≤ λ ≤ 9.3154

`results/strip-mu-certificates.md`, `docs/proofs/polyplet-upper-bound.md`,
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

`results/dmirror-diagonals.md`, `paper/polyplets-report.tex:648`. d(S,S+k) is
quasi-polynomial in S with period 2 and degree k per parity class. Still
conjectural — the last unproved law — which is itself worth saying in print.

## C15. `OPEN` The same law holds on every row-local lattice

`docs/proofs/universal-diagonal-law.md`, `results/hex-diagonal-law.md`.
T(H+k,H) = q_k(H)·b^H where b is the number of up-neighbours: b=1 square, b=2
hex, b=3 king. The report's 3^{n−1} is the b=3 instance of a theorem. Proved,
all three instances machine-checked.

## C16. `OPEN` The triangle mod 3

`results/ternary-spine.md`. The whole diagonal family's mod-3 behaviour is
governed by one algebraic series: the unique W ∈ 𝔽₃[[t]] with W(0)=1 solving
W³ = W² + t. 15/15 checks including a 342-cell check against the banked
triangle. Compact statement; the derivation is where it starts costing.

## C17. `DEFERRED 2026-09-04` The maximum number of holes: `n - ceil(2*sqrt(n)) + 1`

`results/maxhole-closed-form.md`. This is **A248333**, with a construction
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
  (`results/triangle-snf.md`, `results/open-conjectures.md` C1).
- **The v₅ denominator law** (`results/v5-denominator-law.md`) — already demoted
  to a closed door on its own merits.
- **Convex polyplets by area** (`docs/proofs/convex-mirage.md`,
  `results/convex-anisotropic.md`) — q-series, empirically non-D-finite.
- **The differential-approximant methodology** behind item 3 (the numbers it
  produces are in scope; the method is not).
