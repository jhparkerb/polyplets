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

**Comparison base:** `paper/technical-report.tex` at 2026-08-23 — abstract
through a(40), the a(n) table, the T(n,H) block with the T(n,n) / T(n,n-1) /
grand-form paragraphs, one-sided / free / bilateral / asymmetric / A194596
tables, the hole table, a one-line growth-rate remark, three Methods
paragraphs, an empty Reproducibility section, and **no bibliography**.

The mechanical state is good and is gated: `paper/verify_technical_report.py`
is 781 checks green, and `tests/gate_p_paper_verifier.py` establishes that 199
of the paper's 200 numeric literals are actually read by one of them.

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

# A. Corrections — things the paper says now

From `docs/main-paper-audit-2026-08-18.md`, which changed nothing.

## A1. `OPEN` "$\lambda \approx 7.11$, checkable from Table~\ref{tab:an}"

2026-09-04: comment block with the numbers and anchors placed above the
sentence in `paper/technical-report.tex`; the growth-rate sentence itself is
unchanged (item 5 of the finish list, cite-or-drop).

A reader who checks gets neither number: `a(40)^(1/40) = 6.2208` (the Fekete
floor) and `a(40)/a(39) = 6.9352`. 7.11 comes from extrapolating the ratio
sequence. The sentence invites a check that fails; naming the operation costs
one clause. Audit §2.3.

## A2. `DONE` The abstract's provenance sentence, in both directions

2026-09-04: comment block placed above the sentence in
`paper/technical-report.tex` — per-term second-source table from
`AUDIT-2026-09-02.md:126-175`, the re-derivation record per run, and the M2
overstatement to avoid. **Abstract rewritten and declared DONE 2026-09-04**:
a(19) Redelmeier, a(20)–a(23) swept, a(24)–a(40) composed for the tall
heights; Redelmeier agreement to 22; Motley confirmation scoped to H ≤ 19;
a(41) not mentioned. Verifier 781 green, compiles. The comment block above the
sentence is now stale and stays until he says to pull it.

It says 23-35 twice and a(36)-a(40) once. The run records show every run
recomputes the whole triangle up to its own n, so **a(36) was computed five
times, a(37) four, a(38) three, a(39) twice, and only a(40) once** — four
terms' worth of corroboration given away. In the other direction, "twice" for
23-35 was the same engine and the same connectivity rule on two machines and
two instruction sets: the independence is hardware and ISA, not method, and the
OEIS entry's own comment is more careful than the abstract. Audit §2.4.

## A3. `STALE` `P_k` known for `k <= 19`

Was: the pinned range on record is `k <= 18`. Since Undertow the wired table
reaches `k = 19` (`orchestrator/sweep.go:2306`, `maxDiagKMax = 19`), so the
paper's 19 is correct. What remains true is that `P_19` has no holdout
(`docs/paper1-reproducibility.md:154-155`). Item C13.

## A4. `OPEN` Keep the two `P_k` sentences adjacent

"Fixed after computing the 3k-th row" is correct *because* the previous
sentence supplies the leading coefficient `25^k/k!`. Separated, it reads off by
one. Audit §2.2.

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
