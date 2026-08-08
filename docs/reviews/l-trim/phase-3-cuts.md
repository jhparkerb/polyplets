> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** CUTTER's phase-3
> ledger for the L-trim campaign. Proposals, not edits; no `.tex` file was
> touched. Line numbers are advisory (amendment 3), read against the
> post-phase-2 tree at 20bb8a2; the verbatim excerpt is the authority.

# Phase 3 — paragraphs. CUTTER's proposals.

Sixteen proposals: L1 three, L2 three, L3 three, L4 three, L5 two, L6 two. One
pattern accounts for eleven of them: **restatement across the seam**, where a
fact has a working home — the place a proof establishes it or a table displays
it — and one or two further homes that only re-announce it. The largest single
proposal is P3.L1.1, an introduction run whose three paragraphs each preview,
near verbatim, a statement the abstract already makes and the body later makes
again where it is used. The remainder are the other two standing cuts:
scaffolding lead-ins and aphoristic closers.

Housekeeping, applied throughout:

- Every excerpt was checked against `scripts/l_trim_gate.sh`'s pin list. Two
  proposals touch a pinned literal and both leave its count well above zero:
  P3.L3.3 removes two of L3's fourteen `6.543` occurrences (the verifier's own
  checks at `verify_l_papers.py:190-193` read the abstract and the ladder,
  untouched); P3.L6.2 removes none of L6's pins (`1, 4, 14, 40, 105` is not
  pinned and occurs at three other sites). The three single-occurrence pins at
  L1:468, L4:329, L5:340 are nowhere near any excerpt.
- Every excerpt was checked for `\cite` keys against check 7. One proposal
  (P3.L4.2) contains a `\cite`, of `bmr2002`, which occurs at seven other sites
  in L4. No key leaves any paper.
- Two excerpts contain the paper's **only** `\ref` to a label (noted per
  proposal). An unreferenced label is legal and passes the gate; it is listed
  so the phase-5 sweep knows.
- Each excerpt sits between blank lines; the applier should take one adjacent
  blank with each removal, per phase 2's one-separator invariant.
- No proposal has residue outside the six manuscripts.

Not brought, with reasons, at the end.

---

## L1-diagonal-law.tex

### P3.L1.1 — remove the introduction's three "worth flagging" paragraphs and their lead-in

- **anchor**: begins `Three things about that statement are worth flagging`,
  ends `(Section~\ref{sec:polyiamond}) and do not dress it as a theorem.`
  (lines 124–146, a contiguous run: lead-in plus three `\paragraph`s)
- **size**: 23 lines, ~226 words
- **excerpt**:

```
Three things about that statement are worth flagging before the proof.

\paragraph{The onset is proved, not fitted.} $H \ge k+1$ --- equivalently
$n \ge 2k+1$ in the other coordinate --- comes out of the argument, as exactly
the reach of a correction polynomial whose degree is bounded by a triviality
about cluster rows. It is not read off data and then hoped for. This is what
makes the law useful as a \emph{tool}: because the degree is $\le k$ and the
onset is $\ge k+1$, any $k+1$ enumerated in-onset values determine $q_k$
outright, and every further value is a theorem rather than a test.

\paragraph{The class, not the lattice, is the object.} The proof never uses
$b=3$, or symmetry of the step set, or any arithmetic particular to a lattice.
The square lattice is the degenerate case $b=1$; polyhexes are $b=2$; king
animals are $b=3$. Getting all three from one argument is not economy for its own
sake --- it is what makes the mod-$p$ result of Section~\ref{sec:spine} possible,
since there the lattice's only contributions are a prime and a scalar.

\paragraph{Where it stops is informative.} Polyiamonds are not in the class, and
for a reason that is easy to state: a triangular cell's three neighbours depend
on whether the triangle points up or down, so the adjacency is not
translation-invariant and there is no single step set to count. The law
nevertheless appears to hold with a period-2 correction. We report that as data
(Section~\ref{sec:polyiamond}) and do not dress it as a theorem.
```

- **argument**: every sentence here is a third statement of a fact with two
  better homes. Paragraph 1: the abstract says "The onset $H \ge k+1$ is
  proved, not observed" and "$k+1$ enumerated values of a diagonal now
  *determine* it, which turns a fitted formula into a proved one"; the body
  proves the onset at Step 4 and closes with "The onset is therefore not an
  artifact of the method"; §machine opens by re-deriving the tool use ("it
  suffices to enumerate $k+1$ in-onset values ... to determine $q_k$
  outright"), and "a theorem rather than a test" recurs verbatim in
  `cor:two`. Paragraph 2: the abstract says "three instances of one theorem";
  line 284 says "None of them uses the value of $b$" where the proof starts;
  §spine opens "The mod-$p$ behaviour of the law is where quantifying over
  lattices pays off. The answer is one curve; the lattice contributes only a
  prime and a scalar" — the same sentence as this paragraph's close. Paragraph
  3: the abstract's final paragraph makes the polyiamond point in full,
  including "which we report as measurement rather than theorem", and
  §polyiamond's opening re-derives the orientation obstruction in the same
  words ("the up/down orientation alternates along a row, so the adjacency is
  parity-dependent rather than translation-invariant"). The reader loses a
  preview sitting between the theorem's blockquote and §priorart; every
  previewed fact is in the abstract one page earlier at the same resolution,
  and each is re-encountered in the body exactly where it is used. This is the
  phase-1 defect (announce, prove, re-announce) at paragraph grain.
- **collateral**: no labels defined, no `\cite`, no pinned constants. Two
  `\ref`s out of the range (`sec:spine`, `sec:polyiamond`); both labels are
  referenced from at least three surviving sites each, so nothing dangles
  either way. No back-references into the range anywhere in the paper.
- **fallback residue**: the proposal is one run because the lead-in counts its
  paragraphs. If the defender saves exactly one paragraph, the lead-in must be
  retained reworded as `Two things about that statement are worth flagging
  before the proof.` — and correspondingly `One thing ... is worth flagging`
  if two are saved. No residue is needed if the run goes whole.

### P3.L1.2 — remove the `tab:machine` follow-up on rational coefficients

- **anchor**: begins `Coefficients are rational rather than integral, which is
  the shape`, ends `$\tfrac{32}{3}\cdot 3! = 64$.` (lines 763–765)
- **size**: 3 lines, ~22 words
- **excerpt**:

```
Coefficients are rational rather than integral, which is the shape
Remark~\ref{rem:newton} predicts: $k!\,P_k \in \Z[n]$, and
$\tfrac{32}{3}\cdot 3! = 64$.
```

- **argument**: `rem:newton` (§A) already states, as its whole point, that
  $P_k$ is integer-valued with non-integer coefficients and that
  $k!\,P_k \in \Z[n]$ is the right statement. This paragraph restates that
  across the seam and adds one multiplication a reader can do from the printed
  table ($\tfrac{32}{3}\cdot 3! = 64$ is arithmetic on displayed data, not
  banked evidence — nothing here needs a machine or survives only by being
  recorded). What the reader loses is a pointer from the table back to the
  remark; what the paper loses by keeping it is a second home for a statement
  whose first home is a named, numbered remark.
- **collateral**: contains the paper's **only** `\ref{rem:newton}`; the label's
  definition survives and becomes unreferenced (legal, gate-clean; listed for
  the phase-5 sweep). No `\cite`, no pinned constants, no back-references.

### P3.L1.3 — remove §a308359's closing "Two things are worth noting" paragraph

- **anchor**: begins `Two things are worth noting beyond the corollary itself.`,
  ends `come from --- rows 3 and 4 of Table~\ref{tab:machine}.` (lines 809–812)
- **size**: 4 lines, ~46 words
- **excerpt**:

```
Two things are worth noting beyond the corollary itself. The onset in the
conjecture, ``$n \ge 5$'', was presumably read off data; Theorem~\ref{thm:A}
gives $2k+1$ for every $k$, proved, which is where the next diagonals of that
entry come from --- rows 3 and 4 of Table~\ref{tab:machine}.
```

- **argument**: the corollary's own proof already makes the substantive point
  in-line: "validity from $n \ge 2k+1 = 5$ --- exactly the range the conjecture
  states". That the entry's onset was empirical while ours is proved is a
  paraphrase of that sentence plus a guess about Mathar's method ("presumably").
  The pointer to rows 3 and 4 duplicates `tab:machine`'s own existence — those
  rows sit in the table marked at $b=1$, $k=3,4$, two pages earlier. The
  paragraph also ends on the paired-dash aside PROTOCOL lists among the
  standing cuts. What the reader loses: the one explicit sentence tying rows
  3–4 to A308359's future diagonals. That is a suggestion about someone else's
  OEIS entry, not a claim of this paper, and it is worth less than the space.
- **collateral**: `\ref{thm:A}` and `\ref{tab:machine}`, both referenced from
  many surviving sites. No labels defined, no `\cite`, no pinned constants, no
  back-references.

---

## L2-ternary-spine.tex

### P3.L2.1 — remove the "coincidence or shadow" closer of §intro

- **anchor**: begins `A pattern like that is either a coincidence of small
  numbers`, ends `It is the second, and the something is a cubic.`
  (lines 139–140)
- **size**: 2 lines, ~27 words
- **excerpt**:

```
A pattern like that is either a coincidence of small numbers or a shadow of
something. It is the second, and the something is a cubic.
```

- **argument**: this is the aphoristic closer in its pure form — the section's
  point ("we explain both facts from one object", a cubic) restated in a more
  memorable way. The abstract's second paragraph already says exactly what the
  something is: "Modulo $3$ the triangle's diagonal generating series is the
  unique root ... of $W^3 = W^2 + t$ ... Everything follows." The reader loses
  a rhythm beat between `tab:snfcount` and §novelty; the thesis it carries is
  the abstract's, verbatim, and the body delivers it at §setup and §spine.
- **collateral**: none — no labels, refs, cites or pinned constants; no
  back-references.

### P3.L2.2 — remove §ladder's conditionality summary paragraph

- **anchor**: begins `So the conditionality of this paper is: the diagonal law`,
  ends `coefficient identity remains as an input.` (lines 245–247)
- **size**: 3 lines, ~29 words
- **excerpt**:

```
So the conditionality of this paper is: the diagonal law and the grand form
(theorems), and the gas-derived master equation. No finitely-verified
coefficient identity remains as an input.
```

- **argument**: this is a body copy of the `\Ldisclosure` ledger, which states
  per result: "conditional on the diagonal law (itself a theorem, companion
  paper L1) together with the coefficient ladder of §\ref{sec:ladder}. Every
  rung of that ladder has been derived symbolically from the cluster master
  equation; none of it is empirical input any more." §ladder's own opening
  paragraph says it a second time ("They are now all three derived from the
  cluster master equation, and we state them with that provenance rather than
  the older one"), and each `(\star)` item carries its own "Derived"
  provenance line. Phase 1 set the precedent (P1.L5.1, P1.L6.1): the
  disclosure is the copy that survives and a body paraphrase of it is the one
  that goes, because a paraphrase can drift from the copy that counts. The
  reader loses a three-line recap of the section they have just read.
- **collateral**: none.

### P3.L2.3 — remove §lift's closing justification, keeping its hedge

- **anchor**: begins `These three are measured, not proved. They are stated
  because`, ends `the same question asked one level at a time.`
  (lines 539–542)
- **size**: 4 lines, ~48 words cut, ~7 retained
- **excerpt**:

```
These three are measured, not proved. They are stated because the pattern ---
one series governing every level --- is what an eventual Witt-vector treatment
would have to explain, and because the deficit-$d$ open problem above is
presumably the same question asked one level at a time.
```

- **residue (required)**: retain the first sentence verbatim, as its own
  paragraph: `These three are measured, not proved.` The `\Ldisclosure` ledger
  does not cover §lift, so this hedge is the only thing separating the three
  displayed congruences from the paper's proved results; it is load-bearing
  and must survive.
- **argument**: the justification half is stated already. The sleeve-zeros open
  problem, twenty lines earlier, closes with "it is the open remainder of the
  Witt-vector tower that §\ref{sec:lift} starts" — the Witt-vector framing and
  the identification with the deficit-$d$ question are both there. The middle
  bullet of §lift itself says "the tower telescopes through the same series
  rather than producing a new object at each level", which is the "one series
  governing every level" observation in its home position. What remains here
  is a paired-dash aside and two "presumably"-grade speculations the paper has
  already made once each. The reader loses nothing checkable.
- **collateral**: `\S\ref{sec:lift}` is referenced from the sleeve open problem
  and the abstract — both references are *into the section*, not into this
  paragraph, and survive. No labels, cites or pinned constants in the excerpt.

---

## L3-lambda-bounds.tex

### P3.L3.1 — remove the post-definition "power iteration is not a proof" paragraph

- **anchor**: begins `The point of insisting on this is that a power iteration
  is not a`, ends `and anyone can re-run the second part.` (lines 232–236)
- **size**: 5 lines, ~57 words
- **excerpt**:

```
The point of insisting on this is that a power iteration is not a proof. Re-run a
bisection over a power iteration on another machine and one gets a different set
of last digits, with no artifact anyone can audit. A certificate replaces the
whole chain with a finite object and a finite integer computation, and anyone can
re-run the second part.
```

- **argument**: restatement across the seam of the introduction's organising
  paragraph, which says the same thing at greater precision and for both
  halves at once: "Neither half asks the reader to trust a search, an
  eigenvalue solver, a floating-point convergence criterion, or a run that
  cannot be repeated. Each half is a finite object ... plus a finite integer
  or rational computation that checks a system of inequalities against it. The
  searches that *found* those objects were floating-point and are not part of
  the proof." Every clause of the excerpt maps onto a clause of that
  paragraph. The reader loses a re-justification of Definition~`def:cert`
  thirty lines after the justification; the definition's content is unaffected
  and §exact immediately explains what makes the check sound.
- **collateral**: none — no labels, refs, cites; no pinned constants (the
  excerpt has no numerals at all); no back-references.

### P3.L3.2 — remove the "Before the method that worked" lead-in

- **anchor**: begins `Before the method that worked, the method that did not,`,
  ends `since the reason is instructive.` (lines 494–495)
- **size**: 2 lines, ~15 words
- **excerpt**:

```
Before the method that worked, the method that did not, since the reason is
instructive.
```

- **argument**: scaffolding prose — a throat-clear announcing what the
  subsection is about to do. Its subsection's own title, "The generic
  decomposition is worse than the crude bound", states the negative result
  and its flavour; the first content sentence ("A generic twig decomposition
  was built and verified against brute force") starts cleanly without it, and
  the instructive reason is delivered where it belongs, in the case-routing
  paragraph after `tab:generic`. The reader loses a sentence whose entire
  content is "this section exists".
- **collateral**: none.

### P3.L3.3 — remove the "supersedes" paragraph after `tab:compare`

- **anchor**: begins `The certified $6.543$ supersedes both of Bacher's lower`,
  ends `to beat it with a certificate.` (lines 694–697)
- **size**: 4 lines, ~46 words
- **excerpt**:

```
The certified $6.543$ supersedes both of Bacher's lower bounds, and it is worth
being precise about the sense in which it does: the multi-directed $6.4752$ is a
numerical value, and $6.543$ is the first value we know of to beat it with a
certificate.
```

- **argument**: third statement. The abstract: "The top rung,
  $\mu_{17} \ge 6.543$, beats the best previously published lower bound ---
  and beats it with a certificate, where that value was numerical." The table
  it follows: `tab:compare`'s rows print both of Bacher's values with their
  `kind` column (`closed form`, `numerical`) directly above the certified
  $6.543$ (`exact rational certificate`), so the precise sense of the
  supersession is displayed, typed, one inch up the page. The paragraph adds
  only the phrase "the first value we know of", a hedged priority claim in a
  paper that elsewhere declines priority claims on principle ("we do not claim
  to be first, because absence is not a database result"); pruning it makes
  the paper's claim discipline more uniform, not less.
- **collateral**: contains the pinned constant `6.543` twice; twelve
  occurrences survive, including the two the verifier reads (abstract bracket,
  top rung), so check 6 passes with margin. `\cite{bacher2015}` is **not** in
  the excerpt (the table row carries it, and it also appears in the
  introduction), so check 7 is untouched. No labels or refs.

---

## L4-not-dfinite.tex

### P3.L4.1 — remove the introduction's mechanism-sketch paragraph

- **anchor**: begins `Ours tracks \emph{one} distinguished pole per slice ---
  the singularity`, ends `algebraic integers of bounded house.`
  (lines 151–158)
- **size**: 8 lines, ~88 words
- **excerpt**:

```
Ours tracks \emph{one} distinguished pole per slice --- the singularity
$x = 1/\mu_H$ at the radius of convergence --- and asks about its degree over
$\Q$. If the lower slices are all regular there, the recurrence forces the
leading coefficient to vanish at $1/\mu_H$; but a nonzero rational polynomial of
degree $\le D$ cannot vanish at an algebraic number of degree $> D$. So a
D-finite $F$ caps $[\Q(\mu_H):\Q]$ at all but finitely many heights. Northcott
says that cap is impossible, because the $\mu_H$ are infinitely many distinct
algebraic integers of bounded house.
```

- **argument**: this argument is stated four times in L4: the abstract's second
  paragraph gives it in full ("Each $\mu_H$ is an algebraic integer all of
  whose conjugates are at most $\mu_H$ in modulus, so Northcott finiteness
  forces the algebraic degrees ... to be unbounded. Against that, a D-finite
  $F$ would force those degrees to be bounded ... Contradiction."); this
  sketch repeats it; `thm:dichotomy` and `thm:main` prove it; and
  `tab:sidebyside`'s "mechanism" row states it a fourth time, clause for
  clause ("at a single level: lower faces regular at $1/\mu_{H_0}$, so $c_0$
  vanishes there; degree comparison over $\Q$"). Of the four, this is the copy
  with the least claim to its position: the abstract is the summary contract,
  the theorems are the content, the side-by-side is the comparison the
  §related section turns on. After the cut, §"The shape of the argument" still
  does its named job — the shared opening cited to \cite{bmr2002}, the
  three-routes table naming ours "arithmetic: degree and house" — and the
  reader who wants the mechanism ahead of §2 has it in the abstract at the
  same resolution.
- **collateral**: no labels defined, no `\cite` (Northcott is named but cited
  at `lem:northcott`), no pinned constants (L4's pin at line 329 is the
  ψ-degree list in §effective, untouched). No back-references into the range.

### P3.L4.2 — remove §transport's closing "By contrast" paragraph

- **anchor**: begins `By contrast, \cite{bmr2002}'s route needs an explicit
  combinatorial`, ends `the more useful half of this paper.` (lines 430–434)
- **size**: 5 lines, ~57 words
- **excerpt**:

```
By contrast, \cite{bmr2002}'s route needs an explicit combinatorial description
of the denominators --- cyclotomic factors from $k$-sections, in their case --- to
be redone for each new family. That difference is the actual content of the
lightness claim in the abstract, and it is why we think the transport
statement is the more useful half of this paper.
```

- **argument**: the contrast is carried twice elsewhere, both times in
  §related, which is the section built to carry it: `tab:sidebyside`'s
  "input needed" row ("an explicit combinatorial description of the
  denominators, per family" against "Perron--Frobenius monotonicity plus any
  crude growth bound"), and the prose verdict "The lightness of the remaining
  hypotheses is what we claim." The preceding §transport paragraph already
  does the operational work ("The only per-family work is item~3, and both
  halves of it are cheap..."). What this paragraph adds is a self-appraisal
  ("why we think the transport statement is the more useful half of this
  paper") and an explicit pointer at the abstract — glue between two
  statements that both survive. The one concrete loss is the parenthetical
  that BMR's denominators are "cyclotomic factors from $k$-sections"; that is
  a detail of *their* method, recoverable from the citation that survives
  seven times over. Note: this paragraph contains phase 1's applier residue
  ("in the abstract"); removing the repaired paragraph whole is a further cut,
  not a revert, and leaves no stale claim behind.
- **collateral**: `\cite{bmr2002}` — seven other occurrences in L4, so check 7
  passes. No labels, no refs, no pinned constants, no back-references.

### P3.L4.3 — remove the "side effect worth recording" paragraph in §effective

- **anchor**: begins `A side effect is worth recording: irreducibility together
  with`, ends `argument needed is not needed at these levels.`
  (lines 379–382)
- **size**: 4 lines, ~46 words
- **excerpt**:

```
A side effect is worth recording: irreducibility together with positivity of the
dominant root means, by Galois conjugation, that \emph{every} root of the atom is
active in $T(n,H)$. So the minimality ingredient that an earlier root-separation
argument needed is not needed at these levels.
```

- **argument**: the paragraph is addressed to a reader this paper never
  creates. "The atom" is undefined in L4 — its only body occurrence is here
  (the term belongs to `results/triangle-structure.md`'s Atom Ledger; the only
  other trace is a script name in `tab:repro`) — and "an earlier
  root-separation argument" is repository history the paper never presents, so
  the news that its ingredient is now unnecessary refers to nothing in the
  text. Nor does anything downstream use all-roots-activity from *this*
  source: `tab:irrboxes` needs only $[\Q(\mu_H):\Q] = \deg\psi_H$, established
  in the preceding paragraph, and §new-root-content derives activity of every
  root from the lowest-terms certificates ("every $P_H/Q_H$ is in lowest
  terms, so every root is active"). The closed-door record this paragraph
  gestures at lives, in full, in the repository results file where a
  repo-reading auditor will find it; in the paper it is two sentences of
  dangling jargon.
- **collateral**: none — no labels, refs, cites, pinned constants, or
  back-references. The pin at L4:329 is seventeen lines above and untouched.

---

## L5-convex-king-animals.tex

### P3.L5.1 — remove the "by-product" paragraph of §"What the squeeze settles"

- **anchor**: begins `A by-product: \oeis{A225114}, the staircase king animals`,
  ends `That entry carries no asymptotic.` (lines 375–377)
- **size**: 3 lines, ~34 words
- **excerpt**:

```
A by-product: \oeis{A225114}, the staircase king animals (equivalently skew
shapes with no empty row or column), has growth constant $\mu$ too, measured
here to $204$ digits. That entry carries no asymptotic.
```

- **argument**: everything load-bearing here is already on the page. That the
  staircase class grows at $\mu$ is not a by-product of the squeeze — it is
  the *definition* of $\mu$ in the squeeze's proof ($\mu = \lim M(n)^{1/n}$,
  Lemma~`lem:supermul`), with A225114 identified as $M(n)$ in the paper's
  first Definition. The 204 digits appear in `tab:fourrungs`, in the row
  directly below this paragraph, with a caption that makes the stronger
  statement (the staircase value reproduces every HV-convex digit and
  continues past them). What the reader loses is the OEIS-facing gloss —
  "that entry carries no asymptotic" and the skew-shape synonym. The first is
  a remark about a database entry, not about the mathematics; the second is
  worth keeping and the residue keeps it.
- **residue (recommended)**: in the Definition (line ~151), extend the existing
  parenthetical from `(OEIS \oeis{A225114})` to
  `(OEIS \oeis{A225114}, the skew shapes with no empty row or column)`, so the
  identification a partition-literate reader uses to orient survives at the
  place the object is defined. Net −3 lines, −25 words with the residue.
- **collateral**: `\oeis{A225114}` is a formatting macro, not a `\cite`; the
  string appears at four other sites (Definition, `tab:fourrungs`, Kurkov
  paragraph, open problem), so no reference thins to zero. The pinned constant
  at L5:340 (`3.12340450886853853211`, in `cor:floor`) is untouched. No
  labels, refs or back-references.

### P3.L5.2 — remove the second paragraph of the worked PSLQ rejection

- **anchor**: begins `This is the capacity artifact in its natural habitat.`,
  ends `solver will find this polynomial. It means nothing.` (lines 584–589)
- **size**: 6 lines, ~70 words
- **excerpt**:

```
This is the capacity artifact in its natural habitat. A degree-$3$ relation of
height $\sim3\times10^4$ can absorb about $4\log_{10}(3.4\times10^4) \approx 18$
digits of input, so \emph{any} $16$-to-$18$-digit decimal admits such a cubic.
The number of digits fed to an integer-relation search is the whole ballgame,
and anyone with a $16$-digit $\mu$ and a cubic solver will find this polynomial.
It means nothing.
```

- **argument**: the capacity principle is stated twice before this paragraph
  and once after. §"Is $\mu$ algebraic?" opens with it as the operating rule
  ("a hit is reported as REJECTED-ARTIFACT unless
  $(d{+}1)\log_{10}(\text{height})$ is well below half the trusted digit
  count, because PSLQ always returns *something* once the unknowns can absorb
  the input precision"), and `tab:pslq`'s caption applies it to a live row
  ("capacity $125$--$142$ against $121$ trusted digits. That is the reason
  the capacity test exists."). The worked rejection's *first* paragraph —
  which stays whole — already refutes the cubic on its own: the digits
  disagree at the 19th place against 199 trusted, and the cubic sits inside a
  box PSLQ already searched and rejected. What this second paragraph does is
  re-teach the general lesson with this instance's numbers plugged in. The
  reader loses the plugged-in arithmetic ($4\log_{10}(3.4\times10^4) \approx
  18$) and the epigram pair ("the whole ballgame", "It means nothing") — the
  first is one application of a formula the paper has already given twice, the
  second is the closer PROTOCOL's standing cuts name.
- **collateral**: none — no labels, refs, cites or pinned constants; the
  cubic, its root, and the 18-digit agreement all sit in the surviving first
  paragraph, so the closed door (the wrong cubic, on the record with its
  cause) survives intact.

---

## L6-perimeter-gradings.tex

### P3.L6.1 — remove the introduction's "What the two ends give" paragraph

- **anchor**: begins `\paragraph{What the two ends give.} At the maximum end,`,
  ends `polynomial with a proved sharp onset.` (lines 137–144)
- **size**: 8 lines, ~84 words
- **excerpt**:

```
\paragraph{What the two ends give.} At the maximum end, quasi-polynomials with a
triangular onset law and an unexpected amount of lattice-independence. At the
minimum end, eventually constant classes with a \emph{linear} onset law, and
lattice-independence failing at the first nontrivial term. Neither end dominates
the other, and the honest summary is that the perimeter grading is more universal
in \emph{content} at the max end while the height grading --- the subject of a
companion paper --- is cleaner in \emph{form}, being a proved plain polynomial
with a proved sharp onset.
```

- **argument**: sentences one and two are the abstract's paragraphs two and
  three compressed — every clause (quasi-polynomials, triangular onset,
  lattice-independence through $k=5$; eventually constant, linear onset,
  king/square divergence) is in the abstract at greater length, and the
  linear-versus-triangular contrast recurs in the body at its earned position
  ("both are *linear* in the defect, against the maximum end's triangular
  $\binom{k+1}{2}+3$. That contrast is the paper's title."). Sentences three
  and four are a comparative self-appraisal whose factual content — the height
  grading is proved where this grading is interpolated — survives verbatim in
  the first open problem ("The height grading has a proof (polynomial times
  exponential, degree $\le k$, sharp onset $2k+1$) because a single-cell row
  is a cut"). The one thing lost outright is L6's only occurrence of the
  phrase "companion paper" — a pointer, not an attribution (no `\cite`, no
  protocol-protected credit); the open problem's description of the height
  grading is what a reader actually needs at the point of comparison.
- **collateral**: no labels, refs, cites or pinned constants; no
  back-references. Confirmed by grep: `companion` occurs nowhere else in L6,
  which is noted above as a named loss, not discovered later.

### P3.L6.2 — remove the "So the two lattices" recap after `tab:sq4min`

- **anchor**: begins `So the two lattices agree at the maximum end on period,`,
  ends `against $1, 4, 18, 60, 187$ on square.` (lines 561–564)
- **size**: 4 lines, ~40 words
- **excerpt**:

```
So the two lattices agree at the maximum end on period, degree, onset and
leading coefficient, and disagree at the minimum end from the very first
nontrivial constant: $1, 4, 14, 40, 105$ on king against $1, 4, 18, 60, 187$ on
square.
```

- **argument**: a section-closing recap, each half of which sits verbatim in a
  caption or paragraph that survives. The max-end half is `tab:maxend`'s
  caption ("Period, degree, onset and leading coefficient agree on the square
  and king lattices at every $k \le 5$; sub-leading coefficients do not").
  The min-end half is §tips' diamond paragraph, which prints the same
  divergence at the same term with its cause ("It gives $1, 4, 18, 60, 187,
  524$, not $P(x)^4$ --- larger from $j = 2$ on, $18$ against $14$"), and the
  abstract's min-end paragraph. The reader loses the one sentence that holds
  both halves at once; the paper's title, abstract and the "contrast is the
  paper's title" sentence all already do that job. This is restatement across
  the seam in the classic position — the last paragraph before a section
  break, summarising the two sections above it.
- **collateral**: no labels, refs or cites. `1, 4, 14, 40, 105` is not on the
  pin list (L6's pin is `1, 6, 22, 68, 187, 470, 1106`, untouched) and the
  string survives at three other sites (the $q_4$ definition, the
  convergence paragraph, §tips); `1, 4, 18, 60, 187` survives in §tips. No
  back-references.

---

## Considered and not brought

- **L2, the `prop:polya` commentary** ("The proposition is worth pausing on
  ... nothing to spare"): the only place L2 states that $P_k$'s coefficients
  are non-integers, which stops a reader from "strengthening" the valuation
  arguments with integer coefficients they don't have. Unique content, hedge
  work; retained.
- **L2, the cite-carrier paragraphs** (Christol/Allouche after `thm:digit`;
  the $H$-series paragraph with `\cite{oeis}`): each carries the sole
  occurrence of `\cite` keys check 7 pins, and both are phase-2 residues.
  Off the table on gate grounds before any argument.
- **L1, `rem:notsquares`**: on the record in phase 2's verdict as ruled to
  stay; not brought, per that ruling.
- **L3, the table-reading paragraph** ("Two features of the table are the
  honest parts..."): a reader comparing the certified $2.4142135$ against
  $\mu_2 = 1+\sqrt2 = 2.4142136$ would otherwise read the ladder's first rung
  as a typo; that is a number a reader cannot otherwise square, so the
  defence is decisive and I am not spending a proposal on it.
- **L4, the BMR proof-walkthrough in §related**: the middle sentences
  re-derive their Lemma 9 in detail that `tab:sidebyside` compresses, but the
  paragraph's head and tail (where the lemma is and is not cited in the
  haruspicy papers; its statement) are scholarly content this paper's banner
  posture needs. A sentence-level trim; deferred to phase 4.
- **L5, the "Read informally" paragraph after `prop:squeeze`**: its
  fattens/shears/thins sentence duplicates the abstract nearly verbatim, but
  the paragraph also carries "every intermediate class is trapped between $M$
  and $A$ term by term, so nothing has to be proved about the individual
  classes", which is the proof's actual map. Sentence-level; deferred to
  phase 4.
- **L5, §perimeter's opening words "The mirage refines cleanly"**: "the
  mirage" is a dangling term (defined only in repo docs), but the paragraph
  defines semiperimeter for everything after it. A wording repair for phase
  4/5, flagged here so it is not lost.
- **L6, §k6 and §novelty, whole**: banner-referenced (the draft banner points
  into both); off limits in spirit and not probed.
