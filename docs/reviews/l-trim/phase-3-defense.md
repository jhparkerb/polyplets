> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** DEFENDER's
> phase-3 ledger for the L-trim campaign. Verdicts on `phase-3-cuts.md`'s sixteen
> proposals; no `.tex` file was touched. Every anchor excerpt was re-verified
> verbatim against the post-phase-2 tree at 20bb8a2 and every distinctive anchor
> prefix greps to exactly one occurrence in its paper.

# Phase 3 — paragraphs. DEFENDER's verdicts.

**Sixteen proposals, sixteen concessions, no retains.** Three ship with a
residue: P3.L2.3's (the cutter's, endorsed as written), P3.L5.1's (the cutter's,
endorsed with the exact text below), and P3.L6.1's (new — the cutter proposed
none, and one is needed). Seven of the cutter's factual claims are wrong and are
corrected on the record below; none of the seven changes a verdict, but per the
standing rule a right cut with a wrong reason must be re-argued correctly, and
two of the corrections matter to later phases.

The concession I am least comfortable with is P3.L6.1 taken without its residue;
with the residue I am not uncomfortable. The runner-up is P3.L5.1's loss of
"That entry carries no asymptotic," argued at its entry.

---

## L1-diagonal-law.tex

### P3.L1.1 — the introduction's three "worth flagging" paragraphs — CONCEDE

Every substantive claim of restatement checks out, sentence by sentence:

- Par. 1: abstract has "The onset $H \ge k+1$ is proved, not observed" (L1:79)
  and "$k+1$ enumerated values of a diagonal now \emph{determine} it, which
  turns a fitted formula into a proved one" (L1:84–85); Step 4 closes "The
  onset is therefore not an artifact of the method" (L1:393); §machine opens
  with the tool derivation near-verbatim (L1:718–721); "a theorem rather than a
  test" is verbatim in `cor:two` (L1:590).
- Par. 2: "None of them uses the value of $b$" (L1:284); the three instances
  are the abstract's closing sentence of paragraph 1 (L1:81–82) and
  Example~`ex:instances`; §spine opens with the same prime-and-scalar sentence
  (L1:665–666).
- Par. 3: the abstract's final paragraph carries the polyiamond point including
  the measurement hedge (L1:93–96), and §polyiamond's opening re-derives the
  orientation obstruction in full, including "there is no single step set $D$
  to count" (L1:818–821).

No labels or `\cite` in the range (verified: zero in lines 124–146), so no
back-reference is possible. The run goes whole; the fallback lead-in rewording
is moot.

**Cutter error 1.** "Both labels are referenced from at least three surviving
sites each" is false for `sec:spine`: its surviving references are exactly two,
L1:244 and L1:471 (the third, L1:138, is inside the cut). `sec:polyiamond` does
have three (L1:226, 908, 933). Nothing dangles either way — the labels are
section labels on surviving sections and outbound `\ref`s in a removed range
dangle nothing — so the conclusion stands; the count does not.

### P3.L1.2 — the `tab:machine` follow-up on rational coefficients — CONCEDE

Verified: `rem:newton` (L1:409–420) states, as its whole point, integer values
without integer coefficients and $k!\,P_k \in \Z[n]$, and even prints the king
$625/2$ example. The excerpt is L1's only `\ref{rem:newton}` (grep: label at
410, ref at 764, nothing else) — confirmed, and the unreferenced-label listing
for phase 5 is correct. $\tfrac{32}{3}\cdot 3! = 64$ is checkable arithmetic on
row 3 of the printed table, not banked evidence. This is the P1.L4.2 precedent
exactly: what is removed is an interpretation of surviving data. Conceded.

### P3.L1.3 — §a308359's closing "Two things are worth noting" — CONCEDE

Verified: the corollary's proof already contains "validity from
$n \ge 2k+1 = 5$ --- exactly the range the conjecture states" (L1:786–787), and
rows 3–4 of `tab:machine` are the square $k=3,4$ rows, present two pages
earlier. "Presumably read off data" is a guess about Mathar's method, and the
rows-3-and-4 sentence is a suggestion about someone else's OEIS entry. Both
`\ref`s (`thm:A`, `tab:machine`) are massively multiply referenced. Conceded.

---

## L2-ternary-spine.tex

### P3.L2.1 — the "coincidence or shadow" closer — CONCEDE

The abstract's second paragraph delivers the thesis in full: "We explain both
facts from one object. Modulo $3$ ... $W^3 = W^2 + t$ ... Everything follows."
(L2:77–81). This is the aphoristic closer in its pure form and the standing cut
applies. No collateral (verified: none). Conceded.

### P3.L2.2 — §ladder's conditionality summary — CONCEDE

Verified word for word: the `\Ldisclosure` entry (L2:52–55) states the same
conditionality per result — "conditional on the diagonal law (itself a theorem,
companion paper L1) together with the coefficient ladder ... none of it is
empirical input any more" — and §ladder's own opening (L2:222–223) plus the
three per-item "Derived" provenance lines state it again. The phase-1 precedent
(the disclosure is the copy that survives; a body paraphrase is the one that
drifts) applies directly. Conceded.

### P3.L2.3 — §lift's closing justification — CONCEDE, cutter's residue endorsed

The residue is mandatory and correctly identified: the `\Ldisclosure` ledger
covers `thm:snf-3power`, the propositions, the five conditional theorems,
`thm:deficit2`, §sleeve and novelty — and **not §lift** (verified against
L2:46–66). "These three are measured, not proved." is the only hedge separating
the three displayed congruences from the paper's proved results. It ships
verbatim, as its own paragraph.

The justification half is stated elsewhere as claimed: the sleeve open problem
ends "it is the open remainder of the Witt-vector tower that
\S\ref{sec:lift} starts" (L2:517–519), and the middle bullet of §lift has "the
tower telescopes through the same series rather than producing a new object at
each level" (L2:532–533). Conceded with the residue.

**Cutter error 2.** "\S\ref{sec:lift} is referenced from the sleeve open
problem and the abstract" — the second reference is not in the abstract, which
mentions the tower with no `\ref`; it is in the "individual exponents" open
problem (L2:566). Both references point into the section, which survives, so
the conclusion stands; the location does not.

---

## L3-lambda-bounds.tex

### P3.L3.1 — the "power iteration is not a proof" paragraph — CONCEDE

Verified: the introduction's organising paragraph (L3:147–156) covers every
clause — eigenvalue solver ("trust a search, an eigenvalue solver, a
floating-point convergence criterion"), unrepeatable run, finite object plus
finite integer computation, searches not part of the proof. The excerpt
contains no numerals, labels, refs or cites (verified). §exact follows
immediately with the soundness argument. Conceded.

### P3.L3.2 — the "Before the method that worked" lead-in — CONCEDE

Scaffolding as charged. The subsection title (L3:492) carries the verdict, the
first content sentence stands alone cleanly, and the instructive reason is
delivered in the case-routing paragraph after `tab:generic` (L3:522–525).
Conceded.

### P3.L3.3 — the "supersedes" paragraph after `tab:compare` — CONCEDE

Verified: the abstract states the precise sense (L3:84–87, "beats it with a
certificate, where that value was numerical"), and `tab:compare` types both
Bacher rows against the certified row directly above this paragraph. The pin
accounting is confirmed independently: fourteen `6.543` occurrences in L3, two
in the excerpt (L3:694, 696), twelve surviving including the two the verifier
reads (`verify_l_papers.py:190–195` checks the abstract bracket, the theorem's
exact rationals, and the ladder top rung — all untouched). `\cite{bacher2015}`
is not in the excerpt (survives at L3:123, 681–682). `6.4752` is not pinned and
survives twice. The hedged priority claim's removal makes the paper's own
discipline ("we do not claim to be first", L3:127–128) uniform. Conceded.

---

## L4-not-dfinite.tex

### P3.L4.1 — the introduction's mechanism-sketch paragraph — CONCEDE

The four statements are where the cutter says they are: abstract (L4:72–76),
this sketch, `thm:dichotomy`'s proof (L4:284–300), and `tab:sidebyside`'s
mechanism row (L4:464). One shading for the record: the abstract gives the
vanishing-coefficient step as its conclusion ("would force those degrees to be
bounded by the $x$-degree of its annihilating operator") rather than its
mechanism, so "at the same resolution" slightly overstates; the mechanism's
pre-proof homes after the cut are the side-by-side's "lower faces regular at
$1/\mu_{H_0}$, so $c_0$ vanishes there; degree comparison over $\Q$" and the
"what is tracked" row. That is a preview lost one section before the full
proof, which is not a decisive loss under the protocol. No `\cite` in the range
(Northcott cited at `lem:northcott`, L4:257), pin at L4:329 untouched.
Conceded.

### P3.L4.2 — §transport's closing "By contrast" paragraph — CONCEDE

Verified: `tab:sidebyside`'s "input needed" row (L4:466) and the §related
verdict "The lightness of the remaining hypotheses is what we claim" (L4:475)
both carry the contrast; the preceding paragraph carries the operational
content (L4:423). The phase-1 residue ("in the abstract", L4:433) sits inside
this paragraph and removing the repaired paragraph whole leaves no stale claim
— confirmed. The one named loss, "cyclotomic factors from $k$-sections", is a
fact about BMR's method, recoverable from a citation that survives amply.
Conceded.

**Cutter error 3.** "`bmr2002` ... occurs at seven other sites in L4" — it
occurs at eight (L4:44, 132, 144, 275, 459, 518, 525, 533). Error in the safe
direction; check 7 passes with more margin than claimed.

### P3.L4.3 — the "side effect worth recording" paragraph — CONCEDE

Verified in full, and this is the cut whose argument most needed checking,
because it looks like a closed door and the standing defence says closed doors
survive. It does not apply here: "the atom" has exactly one body occurrence in
L4 (L4:378; the others are a header comment and a script filename in
`tab:repro`), "an earlier root-separation argument" is presented nowhere in the
paper, and nothing downstream consumes this paragraph's version of
all-roots-activity — `tab:irrboxes` needs only $[\Q(\mu_H):\Q] = \deg\psi_H$
from the preceding paragraph, and §new-root-content derives every-root-active
from the lowest-terms certificates (L4:331–333). A closed door the reader
cannot identify is not a record; the record lives intelligibly in
`results/triangle-structure.md`. Conceded.

**Cutter error 4.** "The pin at L4:329 is seventeen lines above" — it is about
fifty lines above the excerpt (329 against 379). Line numbers are advisory
(amendment 3) and the pin is untouched either way; noted so the applier trusts
the excerpt, not the arithmetic.

---

## L5-convex-king-animals.tex

### P3.L5.1 — the "by-product" paragraph — CONCEDE, cutter's residue endorsed

Verified: $\mu$ is *defined* as $\lim M(n)^{1/n}$ in `prop:squeeze`'s proof
(L5:348) with A225114 identified as $M(n)$ in the first Definition (L5:151),
and the 204 digits sit in `tab:fourrungs` (L5:385) with a caption making the
stronger reproduces-and-continues statement. The residue is right and ships as
the cutter wrote it — at L5:151, extend the parenthetical to:

```
(OEIS \oeis{A225114}, the skew shapes with no empty row or column)
```

The genuinely lost sentence is "That entry carries no asymptotic." — a
statement about the current state of a database entry, dated the day it is
printed, and not a warrant for anything in the paper. I concede it and log it
as the runner-up discomfort: it is the one sentence saying the 204-digit
measurement adds something to the public record.

**Cutter error 5.** "`\oeis{A225114}` ... appears at four other sites" — five:
L5:151, 385, 829, 1104, and 1119 (the "block series $T$" open problem, which
the cutter missed). Safe direction; no reference thins to zero.

### P3.L5.2 — the second paragraph of the worked PSLQ rejection — CONCEDE

Verified: the capacity rule is stated as the operating discipline at the
section opening (L5:537–541) and applied in `tab:pslq`'s caption (L5:558–561),
and the surviving first paragraph refutes the cubic on its own twice over —
disagreement at the 19th digit against 199 trusted, and membership in a box
PSLQ already searched — while printing the degree and height ($3$,
$3.4\times10^4$) from which the stated rule reproduces the $\approx 18$-digit
capacity in one line. The closed door (the wrong cubic, on the record with its
cause) survives intact in the first paragraph. "The whole ballgame" and "It
means nothing" are the closers the standing cuts name. Conceded.

---

## L6-perimeter-gradings.tex

### P3.L6.1 — the "What the two ends give" paragraph — CONCEDE, with a required residue

The restatements check out: the abstract's paragraphs two and three carry the
max-end and min-end summaries, the linear-against-triangular contrast has its
earned home at L6:453–455 ("That contrast is the paper's title"), and the
proved-versus-interpolated comparison survives verbatim in the first open
problem (L6:636–638).

**Cutter error 6** (a shading, logged because the cutter claimed "every
clause"): "lattice-independence failing at the first nontrivial term" is *not*
in the abstract. Its working homes are §tips' diamond paragraph ("$18$ against
$14$", L6:504) and the `tab:mincoeffs`/`tab:sq4min` pair, so the fact survives
the cut — but by one home fewer than argued, and P3.L6.2 removes another. The
concession stands on the surviving homes, not on the cutter's count.

**The residue, and why it is required rather than nice.** The cutter correctly
reports that this range holds L6's only occurrence of "companion paper"
(grep confirmed: L6:144 and nowhere else) and calls it "a pointer, not an
attribution". Correct on the protocol category — no `\cite`, no external
credit — but the pointer is load-bearing for a checkable claim: after the cut,
L6 asserts "The height grading has a proof (polynomial times exponential,
degree $\le k$, sharp onset $2k+1$)" in its first open problem (L6:636) with no
statement anywhere in the paper of where that proof lives, and the term "height
grading" first appears at L6:153 with no antecedent. A claim of the form "X has
a proof" whose proof the reader cannot locate is a hypothesis that stops being
checkable, which is the protocol's own test. The repair is three words at the
first surviving occurrence, L6:153: replace

```
on the model of the height grading
```

with

```
on the model of a companion paper's height grading
```

Net for the proposal with residue: −84 + 3 words. Conceded on those terms.

### P3.L6.2 — the "So the two lattices" recap after `tab:sq4min` — CONCEDE

Verified: the max-end half is `tab:maxend`'s caption near-verbatim
(L6:206–209), and the min-end half is §tips' diamond paragraph with its cause
(L6:503–504) — note both series in the recap are the per-hull free-removal
series, and §tips is precisely their home. `1, 4, 14, 40, 105` is not pinned
(L6's pin is `1, 6, 22, 68, 187, 470, 1106`, at L6:417, untouched — verified
against `l_trim_gate.sh`'s CONSTANTS block), and `1, 4, 18, 60, 187` survives
at L6:503. Conceded.

**Cutter error 7.** "The string survives at three other sites (the $q_4$
definition, the convergence paragraph, §tips)" — as an exact string it survives
at two (L6:408, 492); the convergence paragraph (L6:439) prints it *unspaced*,
`1,4,14,40,105,252,574`. The values survive at three sites, the grep-able
literal at two. Immaterial to the gate (not pinned), material to anyone
auditing by `grep -F`.

---

## Summary for the adjudicator

| id | verdict | residue |
|---|---|---|
| P3.L1.1 | CONCEDE | none |
| P3.L1.2 | CONCEDE | none |
| P3.L1.3 | CONCEDE | none |
| P3.L2.1 | CONCEDE | none |
| P3.L2.2 | CONCEDE | none |
| P3.L2.3 | CONCEDE | cutter's, endorsed: keep "These three are measured, not proved." as its own paragraph |
| P3.L3.1 | CONCEDE | none |
| P3.L3.2 | CONCEDE | none |
| P3.L3.3 | CONCEDE | none |
| P3.L4.1 | CONCEDE | none |
| P3.L4.2 | CONCEDE | none |
| P3.L4.3 | CONCEDE | none |
| P3.L5.1 | CONCEDE | cutter's, endorsed: extend the L5:151 parenthetical as quoted above |
| P3.L5.2 | CONCEDE | none |
| P3.L6.1 | CONCEDE | **new, required**: "a companion paper's height grading" at L6:153, as quoted above |
| P3.L6.2 | CONCEDE | none |

Cutter factual errors, none verdict-changing: (1) P3.L1.1 `sec:spine` has two
surviving references, not three-plus; (2) P3.L2.3's second `sec:lift` reference
is in the open problems, not the abstract; (3) P3.L4.2 `bmr2002` survives at
eight sites, not seven; (4) P3.L4.3's pin-distance "seventeen lines" is about
fifty; (5) P3.L5.1 A225114 survives at five sites, not four; (6) P3.L6.1
"every clause is in the abstract" overstates — the min-end divergence clause is
not there; (7) P3.L6.2's third surviving site holds the unspaced variant of the
literal.

For the phase-5 sweep, carried from the cutter and confirmed here: after this
phase `rem:newton` (L1) is a defined, unreferenced label.
