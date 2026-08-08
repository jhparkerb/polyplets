> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** CUTTER's phase-4
> ledger for the L-trim campaign. Proposals, not edits; no `.tex` file was
> touched. Line numbers are advisory (amendment 3), read against the
> post-phase-3 working tree; the verbatim excerpt is the authority.

# Phase 4 — sentences. CUTTER's proposals.

Twenty-two proposals: L1 four, L2 five, L3 six, L4 two, L5 three, L6 two. The
dominant patterns are the two PROTOCOL names first: **aphoristic closers** (a
paragraph or section restating its own point in a more memorable final
sentence — eight proposals) and **scaffolding topic sentences** that justify a
paragraph's existence before letting it speak ("worth one paragraph because",
"worth one sentence, because" — four proposals). The remainder are restatement
across the seam at sentence grain, where a fact's working home is the abstract,
a subsection title, a lemma statement, or an adjacent sentence.

Phase-3's three deferrals are all picked up: the fattens/shears/thins run in
L5's "Read informally" paragraph (P4.L5.1), the dangling "mirage" opener in L5
§perimeter (P4.L5.2 — resolved by removal, which is phase 4's unit, rather than
by rewording, which is phase 5's), and the middle sentences of the BMR
proof-walkthrough (P4.L4.1 — the walkthrough is in **L4** §related, not L6; the
phase-3 ledger and verdict both place it there, and the L6 label in this
phase's brief is a transcription slip).

Housekeeping, applied throughout:

- Every excerpt was checked against `scripts/l_trim_gate.sh`'s pin list
  (8 literals). **No proposal contains any pinned literal.** The
  single-occurrence pins — `\Wp = 58` (L1, `rem:notsquares`), the ψ-degree list
  (L4 §effective), the 204-digit floor `3.12340450886853853211` (L5,
  `cor:floor`) — were each located by content in the current tree and are
  nowhere near any excerpt. P4.L3.5's *paragraph* contains `6.543` and `9.3154`
  in its first sentence, which stays; the cut sentence has no numerals.
- Every excerpt was checked for `\cite` keys against check 7. **No proposal
  removes any `\cite` occurrence at all** (grep over every excerpt: zero
  matches). `hardyRamanujan1918` sits one sentence after P4.L5.3's excerpt and
  survives; `bmr2002` occurs 8 times in L4 and P4.L4.1's run contains none of
  them.
- `\ref`s inside excerpts, each grep-counted: `cor:two` (P4.L1.2) survives at
  two sites (L1 §machine, twice); `thm:A` (P4.L1.4) at ~15 sites;
  `lem:stacks` (P4.L5.3) at 9+ sites. No label's reference count drops to
  zero; no label is defined in any excerpt.
- No excerpt is a whole paragraph. Two proposals take the last run of a
  paragraph (P4.L4.1, P4.L5.1); the rest take one sentence with neighbours
  surviving on at least one side. Mid-paragraph removals splice with a single
  space; end-of-paragraph removals end at the surviving sentence's period.
- The off-limits list was respected: no disclosure block, no banner, no
  attribution site, no `rem:notsquares`, nothing in L6 §k6/§novelty (both
  banner-referenced).

Considered and not brought, with reasons, at the end.

---

## L1-diagonal-law.tex

### P4.L1.1 — remove §priorart's "not unheard of" closer

- **anchor**: the final sentence of the Barequet–Shalah comparison paragraph.
  Preceding context: `...quantifies over every
row-local lattice instead, and is proved once for all of them.` Following
  context: blank line, then `The one place where our theorem settles`.
- **excerpt**:

```
The phenomenon is
not unheard of and we do not present it as such.
```

- **argument**: aphoristic closer restating, fourteen lines later in the same
  subsection, the posture the subsection already fixed in stronger and more
  precise words: "We do not claim to be first, because absence is not a
  database result" (L1:131). The intervening paragraph has meanwhile *shown*
  the phenomenon is not unheard of, by stating the polycube relative in full
  with both citations. The reader loses a restatement of a posture whose
  binding statement, and whose evidence, both survive within the same
  subsection. The no-first-claim discipline is untouched — this is its echo,
  not its statement.
- **collateral**: none — no labels, refs, cites, pinned constants. Verified
  "not unheard of" occurs nowhere else in L1.

### P4.L1.2 — remove the gas-picture paragraph's self-justifying lead-in

- **anchor**: first sentence under `\subsection{The gas picture, and why the
  shape is what it is}`. Following context: `Write
$F(n,u) = \sum_k P_k(n)u^k$ with $P_0 = 1$,`.
- **excerpt**:

```
Corollary~\ref{cor:two} has a physical reading that is worth one paragraph
because it explains the shape rather than merely deriving it.
```

- **argument**: scaffolding prose in PROTOCOL's named form — a sentence whose
  content is "the following paragraph deserves to exist". The subsection title
  already announces both the reading ("the gas picture") and the why ("why the
  shape is what it is"); the paragraph's first working sentence ("Write
  $F(n,u) = \dots$") opens cleanly. The reader loses the explicit tie to
  `cor:two`, but the paragraph's own third sentence ties the reading to
  Theorem~C, which is the object the gas picture actually reads.
- **collateral**: `\ref{cor:two}` — the label survives with two references in
  §machine (L1:694, 697), grep-confirmed. No cites, no pinned constants.

### P4.L1.3 — remove §machine's "small computation" topic sentence

- **anchor**: first sentence of the enumeration-cost paragraph. Preceding
  context: `Corollary~\ref{cor:two}, just two --- to determine $q_k$
outright.` plus blank line. Following context: `A surplus-budgeted row
transfer, parametric in the`.
- **excerpt**:

```
Supplying those values is a small computation, not a large one, and it does not
require enumerating animals.
```

- **argument**: both of its claims are restated inside the same paragraph at
  the point where they are earned: "The cost therefore depends on $k$ and $H$,
  not on the number of animals" carries "does not require enumerating animals"
  with its reason attached, and the description of the transfer (state = one
  row's cells plus surplus) is what "small, not large" means. The paragraph
  currently announces its conclusion, derives it, then states it again;
  removing the announcement leaves announce-free derivation plus conclusion.
  The reader loses nothing checkable.
- **collateral**: none.

### P4.L1.4 — remove §polyiamond's "doing real work" closer

- **anchor**: the section's final sentence. Preceding context: `and we state
the periodic law as an
extension rather than a result.` Following context: blank line, then
  `\section{Formalization}`.
- **excerpt**:

```
What the polyiamond case does establish is that
hypothesis (U) is doing real work in Theorem~\ref{thm:A} and is not merely
convenient.
```

- **argument**: aphoristic closer restating the section's opening paragraph,
  which already says it at the point of failure and with the mechanism: "This
  is not a technicality that a little more care would remove" (L1:788),
  directly after exhibiting *why* (U) fails (orientation-dependent adjacency,
  no single step set). The reader loses the section-final restatement of a
  point made, with its evidence, at the section's start. The hedged status of
  the periodic extension ("extension rather than a result") survives untouched
  in the preceding sentence.
- **collateral**: `\ref{thm:A}` — ~15 surviving references, grep-confirmed. No
  cites, no pinned constants.

---

## L2-ternary-spine.tex

### P4.L2.1 — remove the abstract's "telescopes" closer

- **anchor**: final sentence of the abstract. Preceding context: `and the
level-$3$
correction is again $W$.` Following context: `\end{abstract}`.
- **excerpt**:

```
The $3$-adic tower telescopes through one series.
```

- **argument**: restatement at two lines' distance. The immediately preceding
  clause — "the level-$3$ correction is again $W$" — is the same fact, and the
  body's §lift bullet states it in the identical image with more content: "the
  tower telescopes through the same series rather than producing a new object
  at each level" (L2:525–526). Within one abstract paragraph the fact is
  stated, then restated more memorably; the second copy is the one PROTOCOL's
  standing cut names. The reader loses an epigram whose literal content sits
  one clause earlier.
- **collateral**: none. The measured-not-proved status of the lifts is carried
  by the disclosure and by the §lift hedge (phase-3's P3.L2.3 residue), both
  untouched.

### P4.L2.2 — remove the intro's "Not mostly" emphasis fragment

- **anchor**: end of §"The observation"'s first paragraph. Preceding context:
  `Compute the Smith normal
form. Every invariant factor is a power of $3$.` Following context: blank
  line, then `That is not hard to explain,`.
- **excerpt**:

```
Not mostly; every one, at every
$N$ anyone has computed.
```

- **argument**: pure rhetorical emphasis. The preceding sentence states the
  fact in full ("Every invariant factor is a power of $3$"), and the empirical
  scope "at every $N$ anyone has computed" does no epistemic work in this
  paper: Theorem~`thm:snf-3power` proves the statement unconditionally for
  every $N$, two sections later and flagged as such in the very next line
  ("§snf3 does it in two lines"). A scope hedge is load-bearing when it is
  the difference between a measurement and a theorem; here the theorem exists,
  so the hedge is dressing on an observation the paper immediately proves. The
  reader loses cadence, not content.
- **collateral**: none.

### P4.L2.3 — remove "The count is the content."

- **anchor**: the one-line bridge between `thm:snf-3power`'s proof and
  `thm:snf`. Preceding context (same line): `That is unconditional and it is
  the easy half.` Following context: blank line, then `\begin{theorem}` /
  `\label{thm:snf}`.
- **excerpt**:

```
The count is the content.
```

- **argument**: the epigram half of a two-sentence bridge whose first half
  survives. The easy/hard framing is the introduction's, stated there at full
  length: "That is not hard to explain, and §snf3 does it in two lines. What
  is harder, and what this paper is about, is the second observation"
  (L2:119–121). "The count is the content" is that framing restated as a
  maxim at the seam between the two theorems; the surviving first sentence
  ("...it is the easy half") already re-orients the reader toward the hard
  half. Only the sentence is proposed, not the paragraph — the bridge itself
  stays.
- **collateral**: none.

### P4.L2.4 — remove the Lagrange–Bürmann "accident" closer

- **anchor**: end of the paragraph deriving $\varphi'(x) = 0$ in
  characteristic 3. Preceding context: `The correction factor in
\eqref{eq:LB} is identically $1$.` Following context: blank line, then
  `\begin{theorem}[odd spine]`.
- **excerpt**:

```
That accident is what
makes the following two computations one line each rather than a page.
```

- **argument**: the abstract already sells this exact point — "using the
  accident that in characteristic $3$ the relevant correction term vanishes
  identically" (L2:90–91) — and the preceding sentence states the mathematical
  fact the proofs consume. The one-line proofs then demonstrate their own
  brevity two inches down the page; a sentence promising that they will be
  short is a preview of something the reader is about to see. What is lost is
  the word "accident" at the point of use; it survives in the abstract, where
  the framing belongs.
- **collateral**: none.

### P4.L2.5 — remove the deficit-2 section's "reusable part" closer

- **anchor**: final sentence of the paragraph after `thm:deficit2`'s proof.
  Preceding context: `the two
spine theorems supply the first two cases and Theorem~\ref{thm:deficit2} the
third.` Following context: blank line, then `\section{Sleeve zeros}`.
- **excerpt**:

```
The method --- Lagrange--B\"urmann onto the master curve, then exact
division --- applies to any congruence for a family linear in $(n,k)$, and is
the reusable part.
```

- **argument**: a generality claim about the method that the paper neither
  uses nor verifies — no second congruence is attacked with it, and "any
  congruence for a family linear in $(n,k)$" is asserted, not demonstrated.
  The proof's Method paragraph already exhibits the pipeline explicitly
  (Lagrange–Bürmann over $\Z/27$, parametrisation, exact division), so a
  reader who wants to reuse it has the worked instance; what this sentence
  adds is an unhedged reach claim plus a paired-dash aside plus a
  self-appraisal ("the reusable part"), in a paper whose banner demands claims
  be read as "what we can prove". Pruning it makes the paper's claim
  discipline more uniform.
- **collateral**: `\ref{thm:deficit2}` is in the *preceding* sentence, which
  survives; the excerpt itself has no refs, cites or pinned constants.

---

## L3-lambda-bounds.tex

### P4.L3.1 — remove the ladder table's "honest parts" topic sentence

- **anchor**: first sentence of the paragraph after `tab:ladder`. Preceding
  context: `$\mu_2 = 1 + \sqrt2 = 2.41421356\dots$` then `\label{tab:ladder}`,
  `\end{table}`, blank line. Following context: `The certified value is the
floor: at $H = 2$`.
- **excerpt**:

```
Two features of the table are the honest parts and deserve to be read as such.
```

- **argument**: scaffolding topic sentence ("deserve to be read as such" is an
  instruction about reading, not a fact about the table). The two features
  follow immediately, each carried by its own sentence with its own
  explanation; the paragraph loses only the announcement that there will be
  two of them. I concede this is the weakest cut in this ledger — the
  sentence does flag that what follows is disclosure, not defect — but the
  phase-3 defence of this paragraph rested on the $2.4142135$/$2.4142136$
  content, which survives whole, and the "honest" framing is re-supplied by
  the sentences themselves ("because a certificate states what is
  \emph{proved}").
- **collateral**: none — the pinned `6.543` sites (abstract, ladder rung) are
  elsewhere; this sentence has no numerals.

### P4.L3.2 — remove "A checker that cannot fail is not a checker."

- **anchor**: opening sentence of §selftest's body. Preceding context:
  `\subsection{The checker has to be able to say no}` and
  `\label{sec:selftest}`, blank line. Following context (same line): `Four
  self-tests run as a gate:`.
- **excerpt**:

```
A checker that cannot fail is not a checker.
```

- **argument**: the subsection title, four lines up, is this sentence — "The
  checker has to be able to say no" — and the body then opens with its maxim
  form before getting to the four tests. Restatement across the smallest seam
  in the six papers: a title and its first sentence saying the same thing. The
  surviving "Four self-tests run as a gate:" opens the list cleanly, and the
  paragraph after the list ("Test~D is the one that matters most...") carries
  the substantive point about un-seeable failure modes untouched.
- **collateral**: none.

### P4.L3.3 — remove the crippling paragraph's "honestly" closer

- **anchor**: final sentence of §precision's deliberate-crippling paragraph.
  Preceding context: `lands on a slightly weaker rational in twenty sweeps,
at a wall time indistinguishable from the full-precision run.` Following
  context: blank line, then `\subsection{Honest scope}`.
- **excerpt**:

```
The cost of the
crippling shows up honestly as lost digits and never as a wrong claim.
```

- **argument**: restatement across the seam of a soundness fact stated where
  it is proved: "Clamping can only lower the certified value; it can never
  falsify it" (L3:280–281, closing the ladder-table paragraph), which is
  itself a consequence of §exact's downward-rounding argument. The crippling
  measurement's content — four failing states, one-ulp shortfall, $O(1)$ not
  $O(H)$ flooring loss, bracket-and-bisect recovery — all survives; what goes
  is the moral drawn from it, which is the general soundness claim the paper
  has already made twice with its mechanism. The evidence stays; the third
  copy of its interpretation goes.
- **collateral**: none.

### P4.L3.4 — remove the two-engine paragraph's self-appraising closer

- **anchor**: final sentence of §honest's second paragraph. Preceding context:
  `same numerator, same state
count, same minimum ratio to all nine printed digits.` Following context:
  blank line, then `\subsection{An independent estimate`.
- **excerpt**:

```
That is a cross-validation
of the operator by two implementations, which is the strongest statement
available short of certifying the operator itself.
```

- **argument**: the sentence names what the reader just watched ("two engines
  were run against each other ... reproduce the receipts field for field" —
  that *is* cross-validation by two implementations, stated in the surviving
  sentence) and appends a self-appraisal ("the strongest statement available")
  whose scoping content — the operator is trusted, not certified — is the
  previous paragraph's explicit job (L3:385–386, "The operator itself is
  trusted, not certified here"). The honest-scope hedge survives at full
  strength in its own paragraph; this is its echo with a superlative attached.
- **collateral**: none.

### P4.L3.5 — remove §gap's findings-preview sentence

- **anchor**: middle of §gap's opening paragraph. Preceding context: `This
section measures where that looseness
sits.` Following context (same paragraph): `Everything here is measurement
against brute-force counts.`
- **excerpt**:

```
The finding is that it does not sit anywhere: it is diffuse, it compounds
with $n$, and it is therefore not reachable by the levers one would try next.
```

- **argument**: the section's four `\paragraph`s each deliver one clause of
  this preview under a heading that names it ("Diffuse, not concentrated", "It
  grows with $n$", "What that rules out"), and the abstract's final paragraph
  states the whole finding at the same resolution: "the over-count is diffuse
  (median slack $1.144$, maximum $1.222$) and, decisively, that it \emph{grows
  with $n$} --- so it is not a local defect..." (L3:97–102). Announce,
  measure, re-announce — the phase-1 defect at sentence grain. The surviving
  neighbours keep both load-bearing pieces: what the section does ("measures
  where that looseness sits") and its evidentiary status ("Everything here is
  measurement against brute-force counts").
- **collateral**: none in the excerpt. The paragraph's first sentence, which
  contains the pinned `6.543` and `9.3154`, is untouched — noted so the
  applier anchors on the middle sentence exactly.

### P4.L3.6 — remove "\emph{Per-type tuning is dead.}"

- **anchor**: final sentence of §gap's `\paragraph{Diffuse, not
  concentrated.}` block. Preceding context: `There is no small set of bad
types to hand-engineer: fixing the worst four
barely moves the bound.` Following context: blank line, then `\paragraph{It
grows with $n$.}`.
- **excerpt**:

```
\emph{Per-type tuning is dead.}
```

- **argument**: the aphoristic closer in its purest form in these six papers —
  the preceding sentence states the operational fact ("no small set of bad
  types to hand-engineer: fixing the worst four barely moves the bound") and
  this italicised epigram restates it as a slogan. The closed door itself —
  the slack audit's numbers, the identification of the loosest types, the
  measured futility of fixing them — survives in full; PROTOCOL's rule is
  prune the claim's echo, not its warrant, and the warrant is the surviving
  sentence.
- **collateral**: none.

---

## L4-not-dfinite.tex

### P4.L4.1 — remove the BMR walkthrough's proof re-derivation (phase-3 deferral)

- **anchor**: the last two sentences of §related's first paragraph
  ("Bousquet-Mélou and Rechnitzer 2002"). Preceding context: `and $P$ is the
union of the pole sets of the $S_n$, then $P$ has only finitely many limit points.`
  Following context: blank line, then `Side by side:`.
- **excerpt**:

```
Their proof extracts the coefficient of $u^n$ from the ODE to get
$a_0(q,n)S_n = a_1(q,n)S_{n-1} + \dots$, so $S_n$ has denominator dividing
$I(q)\prod_m a_0(q,m)$; a limit point $\ell$ produces $(q_i,n_i)$ with
$q_i \to \ell$, $n_i \to \infty$ and $a_0(q_i,n_i) = 0$, and dividing
$a_0 = \sum_k b_k(q)n^k$ by $n_i^d$ in the limit gives $b_d(\ell) = 0$. Every
limit point is a root of one fixed polynomial.
```

- **argument**: this is the phase-3 deferral, brought as specified: the head
  (where their Lemma 9 is and is not cited in the haruspicy papers) and the
  statement ("Stated in their notation: ...finitely many limit points") both
  stay; what goes is a line-by-line re-derivation of *their* proof, which
  `tab:sidebyside`'s mechanism row compresses to its essence eight lines below
  ("asymptotic in $n$: divide by $n^d$, take the limit, hit the leading
  coefficient") and which is available in full from the citation this paper
  makes eight times. L4's banner posture needs the reader to know what BMR's
  lemma *says* and where it *lives* — both survive — not to have their
  argument reperformed. The closing sentence of the run is the walkthrough's
  own epigram and falls with it; the kept statement already gives the
  conclusion ("finitely many limit points").
- **collateral**: no `\cite` in the run (`bmr2002`'s 8 occurrences are all
  outside it, grep-confirmed — the head's citations are prose "(from~[4])"
  quotations, also kept). No labels, refs or pinned constants; the ψ-degree
  pin is in §effective, far away.

### P4.L4.2 — remove "That is a ceiling on the method."

- **anchor**: end of §related's Klazar paragraph. Preceding context: the bold
  sentence `\textbf{Theorem~\ref{thm:main} is not-D-finite over $\Q(x)$ and
does
not extend to $D_A$-finite.}` Following context: blank line, then
  `\subsection{Arithmetic neighbours}`.
- **excerpt**:

```
That is a ceiling on the method.
```

- **argument**: third statement within the paper and second within the
  subsection. The subsection's own title is "Klazar 2003, and the ceiling on
  our method"; the abstract's final paragraph closes "That is a real limit of
  the method, not a gap in the exposition"; and the bold sentence this echo
  trails states the ceiling itself, precisely scoped. The scope hedge — the
  result is over $\Q(x)$ and stops at $D_A$-finite — is the bold sentence and
  survives verbatim; only its six-word reverberation goes.
- **collateral**: none in the excerpt (`\ref{thm:main}` is in the surviving
  bold sentence).

---

## L5-convex-king-animals.tex

### P4.L5.1 — remove the "Read informally" paragraph's proof-preview run (phase-3 deferral)

- **anchor**: the last three sentences of the paragraph after
  `prop:squeeze`'s statement. Preceding context: `so nothing has to be proved
about the
individual classes --- the whole job is those two.` Following context: blank
  line, then `\begin{lemma}[three-block factorisation]`.
- **excerpt**:

```
One direction is free. For
the other, read an HV-convex animal left to right: it fattens, then shears, then
thins. The shearing middle is a staircase animal and the two ends are stacks;
stacks are too few to carry an exponential, and the middle has a rate at all
because two staircase animals glue end to end without waste.
```

- **argument**: the phase-3 deferral, brought with the boundary phase 3 drew:
  the paragraph's unique content — "every intermediate class is trapped
  between $M$ and $A$ term by term, so nothing has to be proved about the
  individual classes --- the whole job is those two", the proof's actual map —
  survives as the paragraph's new close. Every clause of the removed run has a
  named home on the same two pages: fattens/shears/thins is the abstract,
  nearly verbatim (L5:106–108, "Reading an HV-convex animal left to right, it
  fattens, shears, then thins; the shearing middle is a staircase animal and
  the two ends are stacks, which are too few to move an exponential");
  middle-is-staircase/ends-are-stacks is `lem:blocks`'s statement and
  `lem:stacks`'s title, both directly below; "too few to carry an exponential"
  is `lem:stacks`'s title again ("hence sub-exponential"); "glue end to end
  without waste" is `lem:supermul`; and "one direction is free" is the one
  line of `prop:squeeze`'s proof it paraphrases ("staircase $\subseteq
  \mathcal C \subseteq$ HV-convex gives $M(n) \le \mathcal C(n) \le A(n)$
  termwise"). The reader loses a prose preview of three lemma statements that
  begin two inches lower.
- **collateral**: none — no labels, refs, cites; the `cor:floor` pin is
  outside the paragraph. The abstract's copy of the image is the surviving
  one and is untouched.

### P4.L5.2 — remove the dangling "mirage" opener of §perimeter (phase-3 deferral)

- **anchor**: first sentence of §"Perimeter is tame". Preceding context:
  `\section{Perimeter is tame}` and `\label{sec:perimeter}`, blank line.
  Following context (same line): `By \emph{semiperimeter}`.
- **excerpt**:

```
The mirage refines cleanly when the statistic changes.
```

- **argument**: phase 3 flagged this as a wording repair and deferred it here;
  removal, phase 4's unit, resolves it outright. "The mirage" is a term the
  paper never defines — grep confirms its only occurrences in L5 are this
  sentence and the header comment's pointer to
  `docs/proofs/convex-mirage.md`, a repository document the reader does not
  have. A sentence whose subject refers to nothing in the text conveys nothing
  to its reader; the paragraph's surviving opener ("By \emph{semiperimeter}
  --- ... --- the same class is not merely D-finite but algebraic") is
  self-contained under the section title, which carries the frame. This cut
  loses nothing and repairs a defect.
- **collateral**: none.

### P4.L5.3 — remove the "entire role" restatement after `lem:stacks`'s proof

- **anchor**: middle sentence of the paragraph after Part 2's proof.
  Preceding context: `$\sqrt n \log n$ is $o(n)$, so however many stacks
there are, they carry no exponential.` Following context (same paragraph):
  `Hardy and
Ramanujan~\cite{hardyRamanujan1918} would give`.
- **excerpt**:

```
That is Lemma~\ref{lem:stacks}'s entire
role --- the outer blocks are counted only to be discarded.
```

- **argument**: third statement of the lemma's role within one page. Before
  the proof: "The lemma is two claims bolted together ... Only the second is
  used downstream" (L5:264–266). Immediately before this sentence: "Only the
  exponent matters: ... however many stacks there are, they carry no
  exponential." This sentence restates both, with a paired-dash aside. The
  surviving neighbours keep the paragraph's two jobs — the mathematical point
  (only the exponent matters) and the closed-door justification for the crude
  bound (the Hardy–Ramanujan sentence, untouched, with its citation).
- **collateral**: `\ref{lem:stacks}` — 9+ surviving references,
  grep-confirmed. `\cite{hardyRamanujan1918}` is in the *following* sentence,
  which survives; check 7 unaffected.

---

## L6-perimeter-gradings.tex

### P4.L6.1 — remove the "worth one sentence" lead-in

- **anchor**: first sentence of the quasi-polynomiality paragraph in
  §"The classes, and the triangular onset law". Preceding context: `It
predicts $\mathrm{onset}(6) = 24$
and $\mathrm{onset}(7) = 31$.` plus blank line. Following context: `$k = 3$
carries a genuine period-$2$ term on \emph{both}`.
- **excerpt**:

```
Quasi-polynomiality itself is worth one sentence, because it was the question
that started this.
```

- **argument**: scaffolding in PROTOCOL's named form — a sentence justifying
  the next sentence's existence, plus a piece of project history ("the
  question that started this") that is repository narrative, not a claim of
  the paper. The working sentence follows immediately and stands alone: "$k =
  3$ carries a genuine period-$2$ term on \emph{both} lattices, so
  quasi-polynomiality is intrinsic to the perimeter grading and not a
  square-lattice artefact." Nothing downstream refers to what started the
  investigation; the reader loses only the paper telling them the next
  sentence is worth reading.
- **collateral**: none.

### P4.L6.2 — remove the A120452 refutation's closing epigram

- **anchor**: final sentence of `\paragraph{A refutation worth recording.}`.
  Preceding context: `So A120452 is wrong at its seventh term: $23$, where
the correct value is
$24$.` Following context: blank line, then `\paragraph{The tip series has a
name.}`.
- **excerpt**:

```
A six-term coincidence, and the kind that only a computation past the
match can catch.
```

- **argument**: aphoristic closer. The refutation itself — the paragraph's
  reason for existing, and a genuine closed door — survives complete: the
  $g^4$ prediction $1384$ against the measured $1388$, the convergence rule
  that certifies the measurement, the wider confirming run, and the verdict
  with both numbers ("wrong at its seventh term: $23$, where the correct value
  is $24$"). The removed sentence is the moral drawn afterward, restating "a
  six-term prefix matches" (the paragraph's own second sentence) as a
  cautionary maxim. Prune the claim's echo, keep the warrant; the warrant is
  everything before it.
- **collateral**: none — `\oeis{A120452}` occurs twice in the surviving part
  of the same paragraph; the L6 pin `1, 6, 22, 68, 187, 470, 1106` is in
  §min's tables, untouched.

---

## Considered and not brought

- **L4, "Step~1 is theirs and dates to 2002. We cite it inside the proof
  rather than presenting the derivation as self-contained."** (after
  `tab:sidebyside`): a third statement of the attribution posture (§shape's
  prose and the table's "identical, and cited to them" row are the other two),
  and on restatement grounds it would go — but it is *attribution* posture,
  and this project's rule is that attribution is never redundant. L4's
  disclosure and search record are built on saying the credit three times
  rather than once. Not brought, on the same ground that protects L5's three
  attribution sites.
- **L6, "That contrast is the paper's title."** (end of §min's onset
  paragraph): an epigram by form, but phase 3's verdict cited this sentence's
  paragraph as the surviving home for two cuts (P3.L6.1, P3.L6.2). Cutting the
  sentence that holds the two ends together would thin a home two prior
  rulings lean on. Not brought.
- **L6, "each successive prime-power periodicity costs a fixed two units of
  defect to buy"**: §k6 — banner-referenced and off limits — names this
  sentence explicitly as the one that "comes out" if item 3 fails (L6:600–601).
  It is a live prediction wired to the compute gate; cutting it now would
  falsify §k6's pointer. Off the table.
- **L1, the `eq:elllek` "load-bearing triviality" sentence** (L1:217–220): it
  is a forward map of the proof, naming the three places a two-character
  inequality does work. A reader loses the reason the triviality is displayed
  and numbered; each later use site cites the equation but none lists the
  set. The defence is decisive; not spending a proposal on it.
- **L2, "The cubic does not stop at $\F_3$."** (§lift opener): seven words of
  orientation before a bullet list that needs a topic sentence; cutting it
  would have the section open on `\begin{itemize}`. Not worth the residue.
- **L5, "A negative from a guesser means nothing without a positive
  control."** (§"The guesser is powered"): superficially the twin of
  P4.L3.2, but here the subsection title ("powered") does not restate the
  sentence — the sentence *explains* the title's statistical sense. A reader
  who does not know the term loses the subsection's point. Retained.
- **L5, "So $\nu$ is not an artefact of an extrapolation: ..."** (after
  `prop:split`): interpretive, but cutting it strands the following
  "Measured," fragment without a subject — the repair is a rewording, which
  is phase 5's business. Flagged for phase 5.
- **L6, "That is exactly as explicit as $P(x)$ itself and no more, and this
  paper does not call it a closed form."**: body echo of a disclosure line,
  but it is the hedge at the point of identification, and the banked
  conclusion this paper leans on (φ₂ is an eta quotient, *not* a closed form)
  is exactly what it scopes. A hedge that scopes a claim is load-bearing. Not
  brought.
- **L1, `rem:notsquares`** and everything in it: ruled off in phase 2's
  verdict and by this phase's brief. Not probed.
- **L2, the cite-carrier paragraphs** (`christol1980`/`allouche2003`/`oeis`
  sole sites): off the table on gate grounds, as in phase 3.
