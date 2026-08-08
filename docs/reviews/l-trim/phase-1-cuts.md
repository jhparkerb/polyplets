> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** CUTTER's phase-1
> ledger for the L-trim campaign. Proposals, not edits; no `.tex` file was touched.

# Phase 1 — sections. CUTTER's proposals.

Nine proposals, against all six papers: L1 one, L2 one, L3 one, L4 three, L5 two,
L6 one. Seven of the nine are the same defect in six different costumes — a paper
that tells the reader what it is about to prove, proves it, and then tells the
reader what it proved, so that a result is stated in the abstract, again in an
intro subsection that enumerates it by label, and a third time where it actually
lives. The strongest is **P1.L6.1**: L6's `\section{Status of these claims}` is a
second copy of its own `\Ldisclosure` verification ledger, in places sentence for
sentence ("They are what make every measured value here trustworthy" against the
ledger's "they are what make every measured value in this paper trustworthy").
The ledger is off limits and stays; the copy printed nine pages later is the one
that should go. Two of the nine (P1.L4.2, P1.L4.3) are small and I flag them as
the weakest of the set rather than dressing them up.

All nine anchors were grep-checked for collateral. Only two of the nine ranges
define a `\label` at all, and neither label is referenced anywhere in the tree.

---

## L1-diagonal-law.tex

### P1.L1.1 — remove §"How to read the rest"

- **anchor**: lines 177–190, `\subsection{How to read the rest}` through the line
  before `\section{Row-local lattices}` (line 191)
- **size**: 14 lines, ~106 words
- **excerpt**:

```
\subsection{How to read the rest}
Section~\ref{sec:class} defines the class and pins its three instances.
  [...]
Section~\ref{sec:formal} records the Lean development, and
Section~\ref{sec:repro} says how to re-run everything.
```

- **argument**: The subsection walks the reader through all ten remaining
  sections in order, one clause each. The paper prints `\tableofcontents` at line
  99 — seventy-eight lines earlier — which is the same ten items in the same
  order, with page numbers the prose cannot supply. What the reader loses is the
  one-clause gloss on each title, and the titles are already self-describing
  ("The diagonal law", "Sharpness", "The universal spine", "Where the theorem
  stops: polyiamonds"). The two glosses that carry more than the title does — that
  the grand form is "what makes each successive diagonal cost two new rational
  constants" and that §machine is "the tool" — are both restated at the head of
  the section they describe (lines 523–525, "each new $k$ turns out to cost
  exactly two new rational constants"; line 745, "converts enumeration into
  proof"). So the
  net loss is a paraphrase of a table of contents that the same page already
  prints, and the space is worth more as the first thing a reader meets after the
  prior-art subsection.
- **collateral**: no `\label` in the range. Outgoing `\ref`s only —
  `sec:class`, `sec:A`, `sec:sharp`, `sec:grand`, `sec:spine`, `sec:machine`,
  `sec:a308359`, `sec:polyiamond`, `sec:formal`, `sec:repro` — all ten defined
  outside the range and all ten `\ref`'d from elsewhere in the paper as well
  (`sec:spine` at 138, `sec:polyiamond` at 146 and 240, `sec:open` chain intact).
  No `\cite` in the range. Nothing in `verify_l_papers.py` reads this text.

**Deferred, not proposed.** §"The gas picture, and why the shape is what it is"
(636–688) opens with a paragraph that re-derives the shape of $P_k$ in physical
language after Corollary~\ref{cor:two} has already derived it algebraically, but
the subsection also holds `tab:cumulants` and `tab:weights`, both of which are
`\ref`'d from the open problems (935, 929). Load-bearing core; the paragraph is
phase 3's.

---

## L2-ternary-spine.tex

### P1.L2.1 — remove §"What is proved"

- **anchor**: lines 142–178, `\subsection{What is proved}` through the line
  before `\subsection{Novelty status}` (line 179)
- **size**: 37 lines, ~269 words
- **excerpt**:

```
\subsection{What is proved}
\begin{theorem}[the spine cubic]
  [...]
  correction is again $W$ (\S\ref{sec:lift}).
\end{itemize}
```

- **argument**: The subsection is a theorem environment plus a six-item bulleted
  list, and every one of the seven statements appears twice more. The theorem
  ("$H$ is the unique root $W \in \F_3[[t]]$ with $W(0)=1$ of $W^3 = W^2+t$") is
  the `\begin{definition}` at line 284 verbatim, and the abstract states it too.
  The six bullets — digit product, spine closed forms, activation law, SNF count,
  the $1,1,2$ row cycle, the $3$-adic lift — are the abstract's paragraphs 2
  through 5 in list form, and each is stated a third time as its own numbered
  theorem. The reader loses a labelled index into the paper's own results, which
  the `\tableofcontents` and the `\Ldisclosure` ledger both already supply: the
  ledger names `thm:digit`, `thm:oddspine`, `thm:evenspine`, `thm:activation`,
  `thm:snf` and `thm:deficit2` individually and says what warrants each, which is
  strictly more information than the bullet list carries.

  The one thing here that is not said elsewhere is the framing paragraph at
  150–158: that this cubic is the $p=3$, $w=1$ instance of a lattice-independent
  theorem proved in the companion paper. That is a real loss and I name it. It is
  worth less than 37 lines because §\ref{sec:setup} (192–212) already opens by
  taking the diagonal law and the grand form from the companion paper ("Both are
  proved in the companion paper"), and because the ladder's $(\star b)$ (265–271)
  derives $H \equiv W \pmod 3$ from the master equation *inside this paper* — so
  the spine cubic does not depend on the pointer for its warrant. If the defender
  wants the L1 attribution kept, one sentence appended to §\ref{sec:setup} buys
  it back at a cost of one line rather than thirty-seven.
- **collateral**: one `\label` in the range, `\label{thm:spine-informal}` (line
  145). Grepped the whole tree: it is **never referenced** — the only hit is its
  own definition. No `\cite` in the range. Outgoing `\ref`s to `thm:digit`,
  `thm:oddspine`, `thm:evenspine`, `thm:activation`, `thm:snf`,
  `thm:deficit2`, `sec:lift`, all defined outside and all `\ref`'d elsewhere.
  `\label{sec:novelty}` is at line 180, **outside** the range, and survives — it is
  `\ref`'d from the `\Ldisclosure` ledger (line 65), which is off limits, and
  from `\begin{openproblem}[is $H$ known?]` (line 619), so the cut must not
  creep past line 178.

---

## L3-lambda-bounds.tex

### P1.L3.1 — remove §"Two things this paper also reports"

- **anchor**: lines 158–175, `\subsection{Two things this paper also reports}`
  through the line before `\section{Preliminaries}` (line 176)
- **size**: 18 lines, ~158 words
- **excerpt**:

```
\subsection{Two things this paper also reports}
First, an independent estimate. The certified ladder's floating-point companion
  [...]
gap, which is what makes it worth publishing alongside the bound rather than
after further effort.
```

- **argument**: Two paragraphs, each an advance summary of a section that then
  says the same thing in full. Paragraph 1 says the $\mu_H$ extrapolation is
  "structurally independent of the term ratios: strip spectra against row sums"
  and converges toward $7.11$; §\ref{sec:estimate} (431–454) says "it is
  \emph{structurally} independent: strip spectra and row-sum ratios share no data
  and no algorithm" and gives the actual sequence. Paragraph 2 says the $31\%$
  gap is diffuse, grows with $n$, and so is out of reach of larger windows and
  per-type tuning; §\ref{sec:gap} (644–695) opens "The finding is that it does not
  sit anywhere: it is diffuse, it compounds with $n$, and it is therefore not
  reachable by the levers one would try next" and then measures all of it. The
  abstract's last two paragraphs say both a third time. What the reader loses is
  advance notice that the paper contains a measurement section and a negative
  result — which the table of contents gives by title ("Where the remaining gap
  lives"). No number, no measurement and no scoping hedge is unique to this
  range; every figure in it ($7.11$, $31\%$, $152$ recurrences) is restated with
  its warrant where the work is done.
- **collateral**: no `\label` in the range. No `\cite`. Outgoing `\ref`s to
  `sec:estimate` and `sec:gap`, both defined outside the range (432, 645) and
  both `\ref`'d elsewhere: `sec:gap` from the `\Ldisclosure` ledger (61), from
  `\begin{openproblem}[the real target]` (730) and from `tab:repro` (768);
  `sec:estimate` from `tab:repro` (763).
  Nothing in `verify_l_papers.py` parses this range — its L3 checks read the
  bracket string at line 94 and the certificate rationals at 622, both outside.

---

## L4-not-dfinite.tex

### P1.L4.1 — remove §"What is gained, and what is given up"

- **anchor**: lines 162–186, `\subsection{What is gained, and what is given up}`
  through the line before `\section{Ingredients}` (line 187)
- **size**: 25 lines, ~215 words
- **excerpt**:

```
\subsection{What is gained, and what is given up}
\paragraph{Gained: lightness.} The hypotheses are integer counts, per-height
  [...]
theorem is not-D-finite over $\Q(x)$ and stops there. We state this rather than
leave it for a referee.
```

- **argument**: Three paragraphs, each of which is the topic sentence of a later
  section, and each of which the abstract also carries. "Gained: lightness" is
  §\ref{sec:transport}, which restates the three hypotheses as a numbered list,
  contrasts them with \cite{bmr2002}'s per-family denominator analysis, and then
  says outright "That difference is the actual content of the lightness claim in
  the introduction" — a sentence that exists only to point back at the paragraph
  I am proposing to cut. "Gained: effectivity" is the opening of
  §\ref{sec:effective} ("Theorem~\ref{thm:main} is qualitative.
  Theorem~\ref{thm:dichotomy} is not: it applies at a single height"), plus the
  two box tables. "Given up: the larger class" is §"Klazar 2003, and the ceiling
  on our method" (510–530), which makes the identical argument at greater length
  and ends with it **in bold**.

  The hedge in paragraph 3 is load-bearing — it is the difference between
  not-D-finite over $\Q(x)$ and a false claim about $D_A$-finite — and I would not
  propose removing it if this were its only home. It is not: the abstract states
  it ("the result is not-D-finite over $\Q(x)$ and does \emph{not} extend to
  Klazar's larger $D_A$-finite class"), §related states it in bold, and
  `\begin{openproblem}[extend past $\Q(x)$]` states it a fourth time. The scope
  survives three deep after the cut. The reader loses a preview of the
  gained/given-up ledger; the space is worth more because the same reader meets
  all three items again within eight pages, at the point where each is actually
  supported.
- **collateral**: no `\label` in the range. `\cite{bmr2002}` appears twice inside
  and eleven times in the file, so the bib key survives. Outgoing `\ref`s to
  `sec:transport` (433) and `sec:effective` (339), both defined outside and both
  `\ref`'d elsewhere. `verify_l_papers.py`'s L4 checks read the $\psi$-degrees and
  the box tables (lines 346–423), none of it in this range.

### P1.L4.2 — remove §"The growth rate, for calibration"

- **anchor**: lines 425–432, `\subsection{The growth rate, for calibration}`
  through the line before `\section{Transport to other families}` (line 433)
- **size**: 8 lines, ~61 words
- **excerpt**:

```
\subsection{The growth rate, for calibration}
$\deg\psi_H$ grows by a factor of about $2.7$ per level, which is close to
  [...]
not an input: Theorem~\ref{thm:main} needs unboundedness, and gets it from
Northcott rather than from any measured growth.
```

- **argument**: A whole subsection whose final sentence tells the reader to
  disregard it: "This is an observation about rate, not an input:
  Theorem~\ref{thm:main} needs unboundedness, and gets it from Northcott rather
  than from any measured growth." It warrants nothing in the paper. It is not a
  closed door — nothing was tried and abandoned — and it is not the warrant for
  any claim, by its own statement. What the reader loses is a plausibility check
  that the banked $\psi$-degrees behave the way a transfer-matrix frontier should
  ($2.7 \approx \sqrt\lambda$), which is a mild reason to believe the banked
  $G_H$ are not garbage. I name that as the loss and judge it worth less than a
  numbered subsection, because the $\psi$-degrees carry a much stronger warrant
  eight lines earlier: they are certified modulo $2^{61}-1$, every $\psi_H$ is
  squarefree, every $P_H/Q_H$ is in lowest terms, and the $H=11$ entry that
  *failed* the structural expectation is flagged and excluded in a footnote
  (359–361). A reader who wants to know the data is sane has that footnote,
  which is evidence; this subsection is a coincidence of two decimals.

  This and P1.L4.3 are the two weakest proposals in this ledger and I say so
  rather than letting the defender discover it.
- **collateral**: no `\label` in the range. No `\cite`. One outgoing `\ref` to
  `thm:main` (121), defined outside and `\ref`'d nine times elsewhere.
  `verify_l_papers.py:221–224` has a check whose *comment* says "the paper says
  ~2.7 per level" — but the assertion computes from the script's own
  `PSI_DEGREES` constant and does not read the `.tex` at all, so the gate does
  not break. It does leave that comment orphaned; if this is applied, the
  comment on line 221 should be reworded in the same commit.

### P1.L4.3 — remove §"One resonance, unexplored"

- **anchor**: lines 568–577, `\subsection{One resonance, unexplored}` through the
  line before `\section{Open problems}` (line 578)
- **size**: 10 lines, ~83 words
- **excerpt**:

```
\subsection{One resonance, unexplored}
Klazar's Theorem~4 shows that two of his sequences are $P$-recursive modulo
  [...]
combinatorics, same shape of answer. Whether the mechanisms are related is open,
and as far as we know nobody has looked.
```

- **argument**: The subsection sits inside §\ref{sec:related}, whose job is to
  map the literature the paper touches. This item maps nothing: Klazar's
  Theorem 4 is not a collision, not prior art for anything claimed here, and not
  a method the paper borrows or rejects. It observes that L2's mod-$3$ cubic and
  Klazar's mod-$2^k$ $P$-recursiveness have the same shape, and then says the
  connection is unexamined. What the reader loses is one un-attempted research
  suggestion. It is worth less than ten lines because the paper's §Open problems
  is immediately below it and does *not* list this among its four — so the paper
  itself has already declined to promote it — and because unlike the closed doors
  elsewhere in this project (which record an approach tried and failed, and so
  cannot be recovered by re-deriving them), nothing was spent here that would
  have to be spent again. The neighbouring subsections in §related earn their
  place by different means: "Arithmetic neighbours" names the nearest published
  relatives, and "What the searches established" is the search record itself.
- **collateral**: no `\label` in the range. No `\cite` — Klazar's Theorem 4 is
  named in prose without a `\cite` command, so `klazar2003`, whose only `\cite`
  in the file is `tab:three` at line 145, is untouched. No outgoing `\ref`.
  Nothing in `verify_l_papers.py` reads it.

---

## L5-convex-king-animals.tex

### P1.L5.1 — remove §"What is proved, and what is measured"

- **anchor**: lines 154–183, `\subsection{What is proved, and what is measured}`
  through the line before `\section{The class and its transfer structure}`
  (line 184)
- **size**: 30 lines, ~226 words
- **excerpt**:

```
\subsection{What is proved, and what is measured}
We are careful throughout about which is which, because this paper contains a
  [...]
exponential as a theorem is asking for strictly more than is known about the
first.
```

- **argument**: This is a second copy of the paper's own `\Ldisclosure` ledger,
  printed one page after the first. Its four headings — Proved / Rigorous in one
  direction / Measured / Conjectured — partition exactly the same results the
  ledger partitions, in the same order, with the same verdicts:

  | this subsection | the ledger (lines 48–78) |
  |---|---|
  | "the squeeze and its three lemmas… proved" | "Proposition~\ref{prop:squeeze} … and Lemmas~\ref{lem:blocks}, \ref{lem:stacks}, \ref{lem:supermul} — proved below" |
  | "Full column rank modulo a prime proves full column rank over $\Q$, so excluding a box is rigorous" | "rigorous in the direction claimed: full column rank modulo a prime is a proof of full rank over $\Q$" |
  | "$\mu$ and its digit count; $\theta = 0$; the amplitudes… None of these is a theorem" | "$\mu$ to 199 digits, $\theta = 0$, the amplitudes — labelled measurement" |
  | "Exactly one thing (Conjecture~\ref{conj:sharp})" | "Conjecture~\ref{conj:sharp} — \textbf{a conjecture}" |

  The ledger is off limits under PROTOCOL §1 and stays exactly as it is; this
  proposal touches only the duplicate. The reader loses nothing that the ledger
  does not carry with strictly more detail — the ledger additionally names the
  Lean theorems, the axiom footprint, the control arms and the conditionality of
  Proposition~\ref{prop:ratio}, none of which is in the duplicate. The one
  sentence here that is not in the ledger — "asking for the second exponential as
  a theorem is asking for strictly more than is known about the first" — is
  repeated word for word at line 879, in §"What the split does not buy", where it
  belongs.
- **collateral**: no `\label` in the range. No `\cite`. Outgoing `\ref`s to
  `prop:squeeze`, `lem:T`, `prop:split`, `prop:mirror`, `prop:phi`,
  `prop:ratio`, `conj:sharp`, `sec:exclusions` — all defined outside and all
  `\ref`'d elsewhere (each is `\ref`'d from the `\Ldisclosure` block itself,
  which is unaffected). The Gouyou-Beauchamps/Leroux attribution appears at
  `rem:attr1` (269), `rem:attr2` (952) and §\ref{sec:related} (1120), none of
  them in this range — all three survive untouched.

### P1.L5.2 — remove §"The reading"

- **anchor**: lines 690–702, `\subsection{The reading}` through the line before
  `\subsection{Column-convex: solved, and already known}` (line 703)
- **size**: 13 lines, ~108 words
- **excerpt**:

```
\subsection{The reading}
So the two classes sit one step apart in the same hierarchy: HV-convex
  [...]
and the amplitude. That is the same shape of answer the classical theory gives
for why perimeter is the tractable statistic~\cite{delestViennot1984}.
```

- **argument**: A section-closing restatement of the section it closes. Its first
  paragraph gives four facts — HV-convex is quadratic, dir4 is quartic, the
  four-cone restriction raises algebraic degree $2 \to 4$ and $t$-degree $9 \to
  22$, and by area both are excluded in the same boxes — and all four are in
  `tab:perim` (639–655) and the two paragraphs immediately above it, which print
  the minimal boxes $(2,9)$ and $(4,22)$ explicitly and state the exclusions with
  their holdout counts. Its second paragraph is the paper's thesis sentence
  ("area wild, perimeter tame") arriving for the third time: the subtitle says it
  ("Area is wild, perimeter is tame"), the introduction says it and calls it "the
  organising fact of this paper" (135–138), and the abstract says it ("Convexity
  is a perimeter lever, not an area lever"). What the reader loses is a paragraph
  that restates the section's point in a more memorable way — which is the closer
  pattern the protocol names as a standing cut. No number, no measurement and no
  exclusion box is unique to the range.
- **collateral**: no `\label` in the range. `\cite{delestViennot1984}` appears
  once inside and four times in the file (introduction 129, `tab:controls`
  509, §related 1145), so the bib key survives. No outgoing `\ref`. Nothing in
  `verify_l_papers.py` parses this text.

**Deferred, not proposed.** Two things in L5 look cuttable at section scale and
are not. (i) `\subsubsection*{A worked rejection}` (610–630) restates the PSLQ
capacity discipline a third time, but it is a specific refuted candidate closed
form with the digit at which it fails — a closed door, and closed doors survive.
(ii) `\begin{remark}[the square-lattice analogue is classical]` (427–435) is a
near-duplicate of §\ref{sec:related}'s "The square-lattice analogue" paragraph
(1138–1143), but a remark is a *result* and belongs to phase 2, not here.

---

## L6-perimeter-gradings.tex

### P1.L6.1 — remove §"Status of these claims", promoting §"Novelty" to a section

- **anchor**: lines 618–642, `\section{Status of these claims}` through the line
  before `\subsection{Novelty}` (line 643). The applier must additionally change
  line 643 from `\subsection{Novelty}` to `\section{Novelty}`; `\label{sec:novelty}`
  on line 644 is unchanged and must survive.
- **size**: 25 lines, ~174 words
- **excerpt**:

```
\section{Status of these claims}
\label{sec:status}
  [...]
tip series, whose fourth power reproduces every measured diamond term.
\paragraph{Not computed.} $k = 6$ (\S\ref{sec:k6}).
```

- **argument**: Of the six papers, this is the most literal duplication of a
  disclosure ledger by a body section. Set the two side by side:

  | §Status (618–642) | `\Ldisclosure` (58–78) |
  |---|---|
  | "Proposition~\ref{prop:kct} ($k = 2c+t$) and the monotonicity that licenses the search prune. They are what make every measured value here trustworthy" | "The identity $k = 2c + t$ and the monotonicity that licenses the search prune — \textbf{proved}, and they are what make every measured value in this paper trustworthy" |
  | "Everything in Table~\ref{tab:maxend}: the degree bound and the onset are read off the data, not derived" | "The formulae of Tables~\ref{tab:maxend} and~\ref{tab:mincoeffs} — \textbf{measured and interpolated, not proved}. Degrees and onsets are read off data, not derived" |
  | "the predicted cyclotomic denominators, confirmed by exact division; the king min-end constants, fourteen of fourteen…; the tip series, whose fourth power reproduces every measured diamond term" | "each predicted cyclotomic denominator is confirmed by exact division…; The king min-end constants — …fourteen of fourteen exact…; The tip series identification…" |
  | "\textbf{Not computed.} $k = 6$ (\S\ref{sec:k6})" | "$k = 6$ — \textbf{not yet computed}. See \S\ref{sec:k6}" |

  The ledger is off limits and is the copy that must stay. The reader loses one
  thing the ledger does not carry: the sentence contrasting this paper's
  interpolated status with the companion paper's proved degree bound and proved
  sharp onset ("This is the opposite of the height-diagonal law of the companion
  paper… and stating that contrast plainly is more useful than blurring it").
  That contrast is not lost from the paper — the introduction makes it at 141–145
  ("the perimeter grading is more universal in \emph{content} at the max end
  while the height grading… is cleaner in \emph{form}, being a proved plain
  polynomial with a proved sharp onset") and `\begin{openproblem}[prove the
  degree and the onset]` (660–666) makes it a third time with the mechanism ("a
  single-cell row is a cut"). Three statements go to two.

  This cut does not touch the compute gate: §\ref{sec:k6}, the draft banner and
  §\ref{sec:novelty} are all outside the range and all survive, and the
  "Not computed" line's job is done by §\ref{sec:k6} itself, which is a whole
  section saying exactly that.
- **collateral**: one `\label` in the range, `\label{sec:status}` (line 619).
  Grepped the whole tree: **never referenced** — the only hit is its own
  definition. No `\cite`. Outgoing `\ref`s to `prop:kct` (163), `tab:maxend`
  (209) and `sec:k6` (589), all defined outside and all `\ref`'d elsewhere.
  **The one thing that can break this proposal**: `\label{sec:novelty}` (644) is
  currently a subsection *of* the removed section, and it is `\ref`'d from the
  draft banner (line 56) — off-limits text, and the only reference to it in the
  file. It is outside the anchor and must be promoted rather than removed; if
  the applier deletes through line 657 instead of 642, the compute-gated banner
  gets a dangling `\ref` and the phase commit is blocked.

**Deferred, not proposed.** §"The recentred basis is nonnegative integers"
(326–345) half-declares itself known ("this is the known leading diagonal in
integer form, not a new fact"), but the nonnegativity observation itself is fresh
data and pairs directly with §"Doors closed"'s "The numerators are not
nonnegative". Load-bearing core.
