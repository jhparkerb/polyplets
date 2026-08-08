> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** CUTTER's phase-2
> ledger for the L-trim campaign. Proposals, not edits; no `.tex` file was
> touched. All line numbers are against the post-phase-1 tree at 895d85f, re-read
> from disk.

# Phase 2 — results. CUTTER's proposals.

Twelve proposals: L1 three, L2 three, L3 two, **L4 none**, L5 three, L6 one. Two
patterns account for ten of them. The first is a numbered result whose statement
is already made, in full, as prose somewhere else in the same paper — L3's
`prop:fekete` is the introduction's own sentence set in a proposition
environment fifty lines later, and L1's `thm:D` is a theorem whose statement,
proof and number all belong to `cor:lead`, to the point where the corollary's
title has to say so. The second is an `\begin{openproblem}` that restates, at the
back of the paper, a wall the paper already described where it hit it; four of
those, in four different papers. The strongest single proposal is **P2.L1.1**:
L1's `\begin{lemma}[finiteness]` is stated, proved, and then never used — no
`\ref`, no prose invocation, and none of the diagonal law's five proof steps
appeals to it.

**L4 gets nothing this phase, and that is a finding, not an omission.** Its nine
results are `lem:alg`, `lem:mono`, `lem:northcott`, `thm:dichotomy`,
`thm:main`, `cor:transport`, and four open problems; every one is either invoked
by name in a later proof or is the paper's scope hedge. I looked hardest at
`lem:northcott` (used once, in `thm:main`'s proof, so nominally inlineable) and
at `\begin{openproblem}[extend past $\Q(x)$]` (which restates §Klazar's bold
ceiling sentence). The first is `\ref`'d twice, including from
`\begin{openproblem}[quantitative Northcott]`, and inlining a ten-line Northcott
argument into `thm:main`'s six-line proof makes the proof worse; the second is
the only place the paper poses $D_A$-finiteness as an open *question* rather
than as a limit on its own method. I expect to lose both and am not spending the
defender's time on them.

Two corrections from phase 1 are applied throughout. Every proposal's collateral
field now names **back-references into the range** — prose elsewhere that points
at the removed content and would be left dangling — as well as references out of
it; that is what P2.L1.3, P2.L1.2 and P2.L3.1 each turn on. And every residue is
checked against `scripts/l_trim_gate.sh`'s frozen list
(`technical-report.tex`, `polyplets-report.tex`, `shared/disclosure.tex`,
`shared/preamble.tex`, `shared/refs.bib`, `verify_l_papers.py`) before being
recommended: **no proposal below has residue outside the six manuscripts.** I
also read `verify_l_papers.py` in full and checked each range against the strings
it greps; L2 and L5 have no verifier exposure at all, and the L1 and L6 ranges
touch none of the checked constants. The one range I would have proposed and did
not on those grounds is named in the L1 deferrals.

---

## L1-diagonal-law.tex

### P2.L1.1 — remove `\begin{lemma}[finiteness]` and its proof

- **anchor**: lines 259–272, `\begin{lemma}[finiteness]` through `\end{proof}`
  (the line before the blank preceding `\section{The diagonal law}` at 274)
- **size**: 14 lines, ~93 words
- **excerpt**:

```
\begin{lemma}[finiteness]
\label{lem:finite}
  [...]
\eqref{eq:elllek}.
\end{proof}
```

- **argument**: A lemma that is stated, proved in six lines, and then never used.
  The five steps of Theorem~\ref{thm:A}'s proof are Lemma~\ref{lem:sep},
  Proposition~\ref{prop:chain}, Proposition~\ref{prop:rational}, the partial
  fractions, and the integrality count; not one of them appeals to finiteness of
  the weights or to the count of cluster types, and none of them cites this
  lemma. Neither does Theorem~\ref{thm:B}, whose valuation count runs over
  cluster types without needing them to be finitely many at each surplus. What
  the reader loses is the reassurance that the sums $\sum_c$ appearing in
  Proposition~\ref{prop:chain} are finite at each order in $y$ — and that
  reassurance is already delivered where it is actually needed, twice: the
  paragraph introducing the decomposition (241–244) says $\ell_c \le k_c$ is
  "what bounds the degree in Step~4", and Proposition~\ref{prop:rational}'s proof
  re-derives the only finiteness fact the argument uses ("it is
  \eqref{eq:elllek} four times") from scratch rather than from this lemma. The
  $2^{k-1}$ composition count is the one datum unique to the range; nothing in
  the paper uses it, and no table or theorem quotes it. Fourteen lines for an
  unreferenced restatement of \eqref{eq:elllek} is the clearest case in this
  phase.
- **collateral**: one `\label` in the range, `\label{lem:finite}`. Grepped the
  whole tree: **zero references** — the only hit is its own definition. No
  `\cite`, no `\ref` out. **Back-references into the range: none.** The one
  string that looks like one, line 200's "Conditions (R) and (U) are finiteness
  bookkeeping", is about the definition's hypotheses and stands without the
  lemma. Nothing in `verify_l_papers.py` reads this text (its L1 checks are the
  king diagonals, the A308359 corollary and the pair weights, all elsewhere).

### P2.L1.2 — demote `\begin{theorem}[degree and leading coefficient]` to a sentence

- **anchor**: lines 444–448, `\begin{theorem}[degree and leading coefficient]`
  through `\end{theorem}`. Plus the two residue edits below, both inside L1.
- **size**: 5 lines, ~25 words removed; replacement is ~35 words in place of the
  ~22-word forward pointer it displaces, so the net is about −5 lines and −12
  words.
- **excerpt**:

```
\begin{theorem}[degree and leading coefficient]
\label{thm:D}
  [...]
In particular $[n^1]P_1 = \Wp$.
\end{theorem}
```

- **argument**: One statement currently carries two numbers. Theorem~\ref{thm:D}
  states $\deg q_k = k$ and $[n^k]P_k = \Wp^k/k!$ and gives no proof;
  Corollary~\ref{cor:lead} states the same two facts and proves them; and the
  paper is reduced to titling the corollary
  `[leading coefficient; Theorem~\ref{thm:D}]` to tell the reader they are the
  same thing. Section~\ref{sec:sharp} additionally opens by asserting it in
  prose — "The bound is attained, and the leading coefficient is a single
  enumerable constant of the lattice" — so the claim is made three times in two
  sections before it is proved once, in a third. What the reader loses is a
  numbered handle in the section where the result is motivated. That is worth
  less than the ambiguity it costs: a reader citing "the leading-coefficient
  result" of this paper cannot tell which number to use, and the two numbers
  cannot be reconciled without reading both.

  I am explicit that the gain here is structural rather than volumetric — about
  a dozen words. It is a phase-2 proposal because a duplicate numbered result is
  exactly what this phase is for, not because it saves space.

  **Replacement text** for lines 450–451, which currently read
  "The proof is a corollary of the grand form and is given in /
  Section~\ref{sec:grand} (Corollary~\ref{cor:lead}); it is written out for the":

  > Precisely: $\deg q_k = k$ exactly, the coefficient of $n^k$ in $P_k$ is
  > $\Wp^{\,k}/k!$, and in particular $[n^1]P_1 = \Wp$. That is
  > Corollary~\ref{cor:lead}, proved in Section~\ref{sec:grand} once the grand
  > form is available; it is written out for the

  Line 452 onward ("king lattice in full, and the argument is uniform…") is
  unchanged, so the honest-position paragraph and its six-lattice measurement
  survive intact.
- **collateral**: one `\label` in the range, `\label{thm:D}`, **`\ref`'d twice,
  both inside L1 and both requiring a residue edit**:
  - line 421, in `\begin{remark}[integer values, not integer coefficients]`:
    "since by Theorem~\ref{thm:D} the leading one is" → "since by
    Corollary~\ref{cor:lead} the leading one is";
  - line 611, the corollary's own optional title:
    `\begin{corollary}[leading coefficient; Theorem~\ref{thm:D}]` →
    `\begin{corollary}[leading coefficient]`.

  Leaving either unedited is a dangling `\ref` and blocks the phase commit. No
  `\cite` in the range. Refs out of the range are to `sec:grand` and `cor:lead`,
  both defined elsewhere and both `\ref`'d elsewhere (`cor:lead` from line 880,
  §Formalization). `verify_l_papers.py` computes the leading coefficients from
  its own table (lines 325–333) and does not grep the paper for them; the strings
  it does grep in L1 — the king $k=2$ form, and "58"/"114"/"57" — are outside
  this range.

### P2.L1.3 — remove `\begin{openproblem}[onset sharpness in general]`

- **anchor**: lines 906–913, `\begin{openproblem}[onset sharpness in general]`
  through `\end{openproblem}`. Plus the residue edit at line 503, inside L1.
- **size**: 8 lines, ~79 words
- **excerpt**:

```
\begin{openproblem}[onset sharpness in general]
Theorem~\ref{thm:A} proves validity from $n = 2k+1$. Prove that the formula fails
  [...]
weight family is not C-finite.
\end{openproblem}
```

- **argument**: Every clause of this open problem is in the "Onset sharpness"
  paragraph of §\ref{sec:sharp} (494–504), four hundred lines earlier, and the
  paragraph is the fuller of the two. Both state validity from $n = 2k+1$; both
  say the failure at $n = 2k$ is a non-cancellation statement needing
  $\deg D = k$; both give the verification range, all banked king data through
  $k \le 17$ and ab initio from the weight table for $k \le 5$; both name the
  blocked route as a rational generating function for the top coefficient of
  $R_k$, obstructed because the all-pairs weight family is not C-finite. The
  paragraph adds two things the open problem does not — the leading coefficients
  $1, 4, -80, 1753, -40928, 987355$ that witness $\deg R_k = 2k+1$, and the
  refutation point $\ell = 16$ — so the evidence and the closed door both live
  in the copy that stays. The only text unique to the open problem is the
  imperative "Prove that the formula fails at $n = 2k$ for every $k$", and the
  paragraph already says "It is not proved for all $k$" and calls it open in the
  next sentence.

  What the reader loses is one of four entries in §\ref{sec:open}, so a reader
  scanning that section for work to do sees three problems instead of four. The
  three that remain — cluster-weight closed forms, the cumulants from the
  weights, and the periodic law — are each stated only there.
- **collateral**: no `\label` in the range. No `\cite`. One `\ref` out, to
  `thm:A`, defined elsewhere and `\ref`'d many times. **Back-reference into the
  range: line 503**, "We record onset sharpness as an open problem
  (Section~\ref{sec:open}) and note that". Residue edit, inside L1:

  > We record it as open and note that

  With that edit `\label{sec:open}` (line 904) has no remaining `\ref`. That is
  harmless — an unreferenced label is not an undefined reference, and the gate
  checks only the latter — but the label should stay, since §\ref{sec:open} is
  still a real section. Nothing in `verify_l_papers.py` reads this text.

**Deferred, not proposed.**
1. `\begin{remark}[$4, 9, 25$ are not squares, and that matters]` (475–492)
   duplicates part of `\begin{remark}[the statement is exactly sharp]` (710–721).
   **It is a hard gate blocker and I am not proposing either half**:
   `verify_l_papers.py:495` asserts `"58" in src and "114" in src and "57" in
   src`, and $58$ appears in L1 only inside `rem:notsquares`. Cutting it turns
   the verifier red, which is gate failure 3. Recorded so that no later phase
   walks into it.
2. `\begin{openproblem}[the periodic law]` (929–933) is the same pattern as
   P2.L1.3 against §\ref{sec:polyiamond}'s closing paragraph, but it is not the
   same cut: the paragraph states the period-2 polyiamond case and the open
   problem states the general period-$q$ one. It generalises rather than
   repeats, so I let it stand.
3. `\begin{remark}[a name collision worth stating once]` (216–227). Eighty
   percent of it is disambiguation the reader can get elsewhere, but the OEIS
   filing trap — polyiamonds indexed under "the 2-dimensional hexagonal lattice"
   — is a documented hazard for anyone checking the paper's sequence claims
   against the database, and that is a closed door in the protocol's sense.
   Load-bearing core.
4. The phase-1 gas-picture deferral: §"The gas picture" contains no result
   environments at all, only two tables and a paragraph. Nothing in scope this
   phase.

---

## L2-ternary-spine.tex

### P2.L2.1 — demote `\begin{remark}[the automaton]` to one sentence

- **anchor**: lines 284–292, `\begin{remark}[the automaton]` through
  `\end{remark}`
- **size**: 9 lines, ~64 words; replacement ~28 words, so about −6 lines
- **excerpt**:

```
\begin{remark}[the automaton]
$W$ is algebraic over $\F_3(t)$, so by Christol's
  [...]
consulted.
\end{remark}
```

- **argument**: The remark has three moves and the paper makes two of them
  elsewhere. Christol's theorem as the bridge from "algebraic over $\F_3$" to
  "$3$-automatic" is stated in §\ref{sec:novelty} (148–151) in almost the same
  words — "Christol's theorem, which is what makes ``algebraic over $\F_3$'' and
  ``$3$-automatic'' the same statement" — and §\ref{sec:novelty} is protected
  text I cannot touch, so that copy is the one that survives by construction.
  The abstract states the conclusion ("so the triangle mod $3$ is $3$-automatic
  and the automaton is explicit"). The third move, "to read $T(n,H) \bmod 3$,
  expand $n$ in base $3$ and multiply one factor per digit", is a prose
  paraphrase of the display in Theorem~\ref{thm:digit} four lines above it. What
  is left that only lives here is the two citations, and those must survive the
  cut — hence a demotion rather than a removal.

  **Replacement text**, placed immediately after Theorem~\ref{thm:digit}'s proof:

  > $W$ is algebraic over $\F_3(t)$, so by Christol's
  > theorem~\cite{christol1980} the array is $3$-automatic~\cite{allouche2003},
  > and Theorem~\ref{thm:digit} is its automaton written out for the
  > two-dimensional case.

  The reader loses the gloss on what Christol's theorem says and the closing
  "Nothing about the animals is consulted", which is the protocol's aphoristic
  closer.
- **collateral**: no `\label` in the range, so nothing can `\ref` it. Two
  `\cite`s, `christol1980` and `allouche2003`, and **line 286/288 are their only
  occurrences in the file** — both must be carried into the replacement or the
  bibliography loses two entries and the paper loses an attribution. The
  replacement above keeps both. One `\ref` out, to `thm:digit`, kept.
  **Back-references into the range: none** — no prose elsewhere points at "the
  automaton". `verify_l_papers.py` does not check L2 at all.

### P2.L2.2 — remove `\begin{remark}[why one per three]`

- **anchor**: lines 440–447, `\begin{remark}[why one per three]` through
  `\end{remark}`
- **size**: 8 lines, ~77 words
- **excerpt**:

```
\begin{remark}[why one per three]
The $\lceil\cdot/3\rceil$ is the activation slope $3/2$ against the diagonal, and
  [...]
phenomena. They are one, and it is the cubic.
\end{remark}
```

- **argument**: The remark offers to explain where the $\lceil (N-1)/3 \rceil$
  comes from, and the explanation is already the last display of
  Theorem~\ref{thm:snf}'s proof, ten lines above: nullity
  $= \#\{H \le N : \lfloor 3H/2 \rfloor > N\} = \lceil (N-1)/3 \rceil$, with
  the activation map $H \mapsto \lfloor 3H/2 \rfloor$ named explicitly. A reader
  who has just read that proof is told nothing new by "the
  $\lceil\cdot/3\rceil$ is the activation slope $3/2$ against the diagonal".

  The rest is worse than redundant. It appeals to "the atom factorisation" and to
  the columns factoring "as products of three consecutive atoms" — an object
  this paper never defines, never uses and never returns to; atoms are L4's
  $\psi_H$, in a different paper, under a different name. So a reader who takes
  the remark seriously is sent looking for something that is not here. The
  closing sentence, "The SNF count, the atom factorisation and the $3$-adic
  exponents are not three phenomena. They are one, and it is the cubic", is the
  protocol's aphoristic closer with an undefined term inside it. What the reader
  loses is an assertion that three things are the same, one of which the paper
  has not introduced.
- **collateral**: no `\label` in the range, no `\cite`, no `\ref` out. **No
  back-references in** — nothing elsewhere in L2 mentions the atom
  factorisation, and the phrase "one per three" appears only here and in
  `tab:snfcount`'s caption, which stands on its own. `verify_l_papers.py` does
  not check L2.

### P2.L2.3 — remove `\begin{openproblem}[is $H$ known?]`

- **anchor**: lines 583–587, `\begin{openproblem}[is $H$ known?]` through
  `\end{openproblem}`. Plus the residue edit at lines 214–215, inside L2.
- **size**: 5 lines, ~42 words; residue adds ~10, so about −4 lines and −32 words
- **excerpt**:

```
\begin{openproblem}[is $H$ known?]
$H = 1, 25, 208, 1483, 20688, 130208, \dots$ is the per-row transfer series of
  [...]
it against the OEIS~\cite{oeis} or anywhere else (\S\ref{sec:novelty}).
\end{openproblem}
```

- **argument**: §\ref{sec:setup} already prints the series and asks the question,
  in consecutive sentences at 211–215: "$H$ begins $1, 25, 208, 1483, 20688,
  130208, \dots$ and is the per-row transfer series of the underlying defect
  gas… Whether $H$ itself is a known sequence is one of the things the missing
  novelty sweep would settle." The open problem repeats the six terms, repeats
  the description "the per-row transfer series of the defect gas", and repeats
  the question. It is the shortest round trip between a statement and its
  restatement anywhere in these six papers.

  What the reader loses is the `\cite{oeis}`, which is why this is a removal plus
  a residue rather than a plain removal. **Replacement text** for lines 214–215,
  currently "Whether $H$ itself is a known sequence is one of the things the
  missing novelty sweep would settle.":

  > Whether $H$ itself is a known sequence --- it has not been checked against
  > the OEIS~\cite{oeis} or anywhere else --- is one of the things the missing
  > novelty sweep would settle.

  L2 keeps three open problems, each stated only in §Open problems.
- **collateral**: no `\label` in the range. One `\cite`, `oeis`, and **line 586
  is its only occurrence in the file** — without the residue edit the key
  disappears from the bibliography. One `\ref` out, to `sec:novelty`, which is
  protected text and is `\ref`'d twice more (the `\Ldisclosure` ledger at line 65
  and the draft banner's sibling), so `sec:novelty` is unaffected either way.
  **Back-references into the range: none.** `verify_l_papers.py` does not check
  L2.

---

## L3-lambda-bounds.tex

### P2.L3.1 — remove `\begin{proposition}[existence, and terms are floors]`

- **anchor**: lines 166–170, `\begin{proposition}[existence, and terms are
  floors]` through `\end{proposition}`. Plus the residue edit at line 172, inside
  L3.
- **size**: 5 lines, ~20 words, plus a 7-word residue sentence, so about −6 lines
- **excerpt**:

```
\begin{proposition}[existence, and terms are floors]
\label{prop:fekete}
  [...]
$n$.
\end{proposition}
```

- **argument**: The proposition has no proof and its statement is the
  introduction's own sentence, fifty lines earlier and with more in it. Line
  116–119: "gives $a(m)a(n) \le a(m+n)$; Fekete's lemma then makes
  $\lambda := \lim_n a(n)^{1/n}$ exist, with $a(n) \le \lambda^n$ for every $n$
  --- so every enumerated term is a floor on $\lambda$ and never an
  approximation to it." That is all three clauses of the proposition, plus the
  gloss that gives the proposition its title. Nothing in the paper `\ref`s it,
  and the `\Ldisclosure` ledger's entry for the existence of $\lambda$ names the
  Lean theorems directly rather than the proposition, so the ledger is unaffected.

  What the reader loses is a numbered anchor for the paper's standing hypothesis.
  That is worth less than five lines here because the Lean sentence that follows
  the proposition is the part doing real work — it records that the whole ladder
  is formalized generically, which is a verification fact and stays — and it
  reads perfectly as the continuation of §Preliminaries' definition.

  **Residue**: line 172 currently opens "This is Fekete's lemma on $\log a$. The
  ladder --- supermultiplicativity, the". With the proposition gone, "This" has
  no antecedent. Delete that first sentence, so the paragraph begins "The ladder
  --- supermultiplicativity, the existence of the limit, the per-term
  inequality, and the resulting lower bound --- is formalized in Lean~4…". The
  supermultiplicativity statement itself is not lost: it is in the introduction,
  in the abstract, and named in the ledger.
- **collateral**: one `\label` in the range, `\label{prop:fekete}`. Grepped the
  whole tree: **zero references.** No `\cite`, no `\ref` out. **Back-reference
  into the range: line 172's "This is Fekete's lemma on $\log a$."**, handled by
  the residue above; that is the only one — the other two "Fekete" hits are the
  `\Ldisclosure` ledger (line 41, protected, no `\ref`) and the introduction
  (line 116), neither of which points at the proposition. `verify_l_papers.py`'s
  L3 checks read `tab:ladder`, the bracket strings, `5^5/4^4`, the two upper
  certificates and the rook control — all outside this range.

### P2.L3.2 — remove `\begin{openproblem}[the missing concatenation lemma]`

- **anchor**: lines 725–730, `\begin{openproblem}[the missing concatenation
  lemma]` through `\end{openproblem}`
- **size**: 6 lines, ~51 words
- **excerpt**:

```
\begin{openproblem}[the missing concatenation lemma]
Find a connected split of a lattice animal into two pieces with sizes prescribed
  [...]
consequence is why it should be expected to be hard.
\end{openproblem}
```

- **argument**: §\ref{sec:gap}'s closing paragraph, "An independent route, also
  closed" (667–677), states the same problem with its measurement attached and
  is strictly the better copy. It gives the target ($\lambda \le 7.745$ from
  Barequet–Ben-Shachar–Osegueda's quasi-submultiplicativity with $a(40)$ known),
  the exact obstruction (the lexicographic split shatters a king comb into about
  $n/4$ components — measured — so reassembly costs $n^{\Theta(n)}$, and the
  connected centroid split cannot prescribe the halves' sizes to within $O(1)$),
  and the reason to expect it to be hard (the same lemma would improve the
  published polyomino record from $4.5252$ to $4.3828$). The open problem restates
  the ask, the $7.745$ and the hardness argument, and adds only the phrase
  "with $\mathrm{poly}(n)$ reassembly information" — which is the negation of the
  $n^{\Theta(n)}$ the paragraph already measured.

  What the reader loses is the third of L3's three open problems. The two that
  remain are the ones a reader would act on: bring the upper bound below $8$, and
  certify further rungs.
- **collateral**: no `\label` in the range, no `\cite`, no `\ref` out. **No
  back-references in**: §\ref{sec:gap}'s paragraph does not point forward at the
  open problem, and `tab:repro`'s row for "the concatenation route" cites
  `results/concatenation-upper-bound.md`, not this environment.
  `verify_l_papers.py` does not read it.

**Deferred, not proposed.** `\begin{openproblem}[certify further rungs]`
(718–723) is two thirds duplicate — §\ref{sec:precision} (379–382) already has
the $192$-bit accumulators, the $35$~GB and the $+0.05$ per rung — but the last
sentence is not duplicated anywhere and is the part that matters: the ladder
converges to $\lambda$, so the lower side can in principle be pushed arbitrarily
close, at a measured $3.5\times$ cost per rung. Trimming it to that sentence
would save perhaps twenty words and cost the reader the only statement in the
paper that the lower bound is not intrinsically capped. Not worth the argument.

---

## L4-not-dfinite.tex

**No result-level proposals.** All nine of L4's results are load-bearing:
`lem:alg`, `lem:mono` and `lem:northcott` are the three ingredients
`thm:dichotomy` consumes by name, `cor:transport` is what the paper calls its
more useful half, and the four open problems are each stated only in §Open
problems — including `[the isotropic sequence]`, which is a scope hedge on what
Theorem~\ref{thm:main} does *not* say and is exactly the kind of hedge the
protocol protects. The two I considered and rejected are argued in the summary
above.

---

## L5-convex-king-animals.tex

### P2.L5.1 — demote `\begin{remark}[the square-lattice analogue is classical]` into §\ref{sec:related}

- **anchor**: lines 397–405, `\begin{remark}[the square-lattice analogue is
  classical]` through `\end{remark}`. Plus the residue edit in §\ref{sec:related},
  inside L5.
- **size**: 9 lines, ~76 words; residue adds ~11 words to an existing paragraph,
  so about −8 lines and −65 words
- **excerpt**:

```
\begin{remark}[the square-lattice analogue is classical]
Convex polyominoes by area grow at $2.30914\dots$~\cite{bender1974} and the
  [...]
rather than for two particular ones.
\end{remark}
```

- **argument**: This is my phase-1 deferral, and it is a duplicate of
  §\ref{sec:related}'s paragraph "The square-lattice analogue" (1095–1100) claim
  for claim: Bender's $2.30914$; the parallelogram subclass \oeis{A006958}
  sharing it; therefore Proposition~\ref{prop:squeeze}'s conclusion could have
  been read off the solved models one lattice over; therefore the contribution is
  the generality. Four claims, twice, seven hundred lines apart.

  It is a demotion and not a removal because one thing in the remark is **not**
  duplicated and must survive: the measurement "$2.309138593330495$, flat from
  $n = 100$ to $n = 400$". That is this project's own value for the
  *parallelogram* subclass \oeis{A006958}, and it is not the same object as the
  $121$-digit control value in §"$\mu$, $\theta$, and the amplitude", which is
  HV-convex polyominoes \oeis{A067675}. It is the square-lattice instance of the
  squeeze, measured, and evidence survives.

  **Replacement text** for §\ref{sec:related}'s paragraph, which currently reads
  "Bender's $2.30914$~\cite{bender1974} for convex polyominoes by area, and the
  parallelogram subclass \oeis{A006958} sharing it, mean that…":

  > Bender's $2.30914$~\cite{bender1974} for convex polyominoes by area, and the
  > parallelogram subclass \oeis{A006958} sharing it --- measured here at
  > $2.309138593330495$, flat from $n = 100$ to $n = 400$ --- mean that…

  The rest of that paragraph is unchanged. What the reader loses is a second
  telling, in §\ref{sec:squeeze}, of a point §\ref{sec:related} exists to make.
- **collateral**: no `\label` in the range, so nothing can `\ref` it. One
  `\cite`, `bender1974`, which occurs three more times in the file (line 129 in
  the introduction, line 542 in the amplitude subsection, line 1095 in
  §\ref{sec:related}), so the key survives; the replacement keeps it in place at
  1095 regardless. One `\ref` out, to `prop:squeeze`, defined elsewhere and
  `\ref`'d eleven times. **Back-references into the range: none** — nothing
  points at this remark. `verify_l_papers.py` does not check L5 at all.

### P2.L5.2 — demote `\begin{corollary}[$\mu$ by shooting]` to a sentence

- **anchor**: lines 958–965, `\begin{corollary}[$\mu$ by shooting]` through
  `\end{corollary}`
- **size**: 8 lines, ~52 words; replacement ~34 words, so about −5 lines
- **excerpt**:

```
\begin{corollary}[$\mu$ by shooting]
\label{cor:shoot}
  [...]
extrapolation for $200$.
\end{corollary}
```

- **argument**: This is a wall-clock timing in a corollary environment. Nothing
  in it is deduced from Proposition~\ref{prop:phi} in the way a corollary is
  deduced from a proposition: it reports an operation count, a digit count and
  $1.6$ seconds on one core. A reader who cites "Corollary 2 of this paper" is
  citing a benchmark. The paper is careful everywhere else about exactly this
  distinction — §"What is proved, and what is measured" made it the organising
  question until phase 1 removed it as a duplicate of the ledger, and the ledger
  itself sorts every item into proved, rigorous-in-one-direction, measured or
  conjectured. A measurement numbered as a corollary is the one place the paper
  does not follow its own rule.

  **Replacement text**, in place of the environment:

  > Shooting on that recurrence computes $\mu$ in $O(h_{\max})$ operations, with
  > no series and no extrapolation: it reproduces all $199$ banked digits,
  > continues past them, and reaches $987$ digits in $1.6$ seconds on one core,
  > against a $700$-term enumeration plus extrapolation for $200$.

  Every number survives, including the $987$ digits the abstract also quotes.
  What the reader loses is the environment and its number.
- **collateral**: one `\label` in the range, `\label{cor:shoot}`. Grepped the
  whole tree: **zero references.** No `\cite`, no `\ref` out. **Back-references
  into the range**: line 119 (the abstract) says "The same recurrence computes
  $\mu$ by shooting --- $987$ digits in $1.6$ seconds", and line 1092
  (§\ref{sec:related}) credits "the eigenvector recurrence and the shooting
  method (Proposition~\ref{prop:phi})". Neither names the corollary and neither
  needs editing — the abstract's claim is preserved verbatim by the replacement,
  and §\ref{sec:related} already points at `prop:phi`, which is where the
  shooting method is actually derived. `verify_l_papers.py` does not check L5.

### P2.L5.3 — remove `\begin{openproblem}[the arithmetic of $\mu$]`

- **anchor**: lines 1120–1123, `\begin{openproblem}[the arithmetic of $\mu$]`
  through `\end{openproblem}`
- **size**: 4 lines, ~15 words
- **excerpt**:

```
\begin{openproblem}[the arithmetic of $\mu$]
Is $\mu$ irrational? Transcendental? \S\ref{sec:exclusions} excludes boxes and
  [...]
nothing more.
\end{openproblem}
```

- **argument**: The paper already declines to claim anything about $\mu$'s
  arithmetic, twice, in the two sections where the question arises. §"Is $\mu$
  algebraic? Not in the searched box" closes: "We do not claim $\mu$ is
  irrational, and no argument here bears on it." §"Is $r$ algebraic?" opens its
  second paragraph: "There is no proof that $\mu$ is irrational, let alone
  transcendental, so $\Q(\mu)$ is a field of unknown degree." The open problem
  turns those into a two-word question and points back at the section that
  already said it. What the reader loses is the marking of "is $\mu$ irrational"
  as an open problem rather than as a disclaimer — and both existing statements
  are unambiguous that nothing is known, which is the same information.

  **This is my weakest proposal in the ledger** and I say so rather than let the
  defender find it: fifteen words, and the counter-argument that a famous open
  question deserves a numbered slot is not unreasonable. I propose it because L5
  keeps three open problems either way, and the three that remain — a sharp
  asymptotic, non-D-finiteness as a theorem, and the block series $T$ — are all
  problems this project could actually attack, where this one is a wish.
- **collateral**: no `\label` in the range, no `\cite`. One `\ref` out, to
  `sec:exclusions`, defined elsewhere and `\ref`'d from the `\Ldisclosure` ledger
  (protected, unaffected). **No back-references in.** `verify_l_papers.py` does
  not check L5.

**Deferred, not proposed.**
1. `\begin{corollary}[every banked term is a floor]` (336–345). Its content is
   Lemma~\ref{lem:supermul}'s "equals $\sup_n M(n)^{1/n}$" instantiated at one
   value of $n$, and demoting it to two sentences would save five lines. I let it
   stand because the number it carries, $M(700)^{1/700} = 3.12340450886853853211
   \dots$, is the paper's only rigorous lower bound on $\mu$ — everything else
   about $\mu$ in this paper is extrapolation — and the sentence after it
   ("The digits past $3.12$ in the extrapolated value remain extrapolation") is
   the boundary between the two. That distinction is this project's standing
   discipline and it deserves a numbered slot.
2. `\begin{openproblem}[a sharp asymptotic, for anything in this family]`
   (1113–1118) restates §"What the split does not buy", which is the same
   pattern as P2.L1.3 and P2.L3.2. I am not proposing it: it is the paper's
   headline open problem, `\ref`'d from `conj:sharp`'s own discussion, and
   removing the top item from a §Open problems list is a different and larger
   claim than removing a duplicated third item.
3. `\begin{remark}[the coefficients are themselves evidence]` (645–650) is six
   lines and is an independent check on the algebraicity verdict — the $(19,3)$
   P-recurrence's sixty-digit coefficients against the quartic's five-digit ones.
   Evidence.
4. `\subsubsection*{A worked rejection}` and `prop:polya`'s scaffolding
   paragraph were flagged by the defender for phases 3–4 and are not touched
   here.

---

## L6-perimeter-gradings.tex

### P2.L6.1 — remove `\begin{openproblem}[the higher tips]`

- **anchor**: lines 650–653, `\begin{openproblem}[the higher tips]` through
  `\end{openproblem}`
- **size**: 4 lines, ~27 words
- **excerpt**:

```
\begin{openproblem}[the higher tips]
The tip family is $\phi_1, \phi_2$ for corner indices $1, 2$, and $\phi_3$ is
  [...]
\emph{not} the answer at index $3$ (\S\ref{sec:tips}). What is?
\end{openproblem}
```

- **argument**: §\ref{sec:tips} closes (530–534) with exactly this content and
  labels it deliberately: "the two corner types in this problem are the first two
  members of one family: a unimodular corner gives $\phi_1 = P(x)$, and the
  index-$2$ diamond tip gives $\phi_2$. The natural guess --- $\phi_m$ for index
  $m$ --- is \textbf{false} at $m = 3$, and is recorded here as a closed door
  rather than left as a suggestion." The open problem repeats the family, repeats
  that $\phi_3$ is not the answer, points back at §\ref{sec:tips} for the reason,
  and adds the two words "What is?". The closed door — which is the part that
  cannot be recovered by re-deriving it — is in the copy that stays, and it is
  the copy that says $m = 3$ was actually tried.

  What the reader loses is two words of ask. L6 keeps three open problems, and
  the three that remain are the ones with content of their own: proving the
  degree and onset, the rationality of the two-variable generating function, and
  the hull factorisation in general.
- **collateral**: no `\label` in the range, no `\cite`. One `\ref` out, to
  `sec:tips`, and **line 652 is the only `\ref{sec:tips}` in the file** — after
  the cut `\label{sec:tips}` (486) has no references. Harmless: an unreferenced
  label is not an undefined reference and the gate checks only the latter. The
  label should stay, since §\ref{sec:tips} is a real subsection.
  **Back-references into the range: none** — §\ref{sec:tips}'s closing paragraph
  does not point forward at the open problem. Checked against
  `verify_l_papers.py`'s L6 function: it greps for the min-end constants
  $1, 6, 22, 68, 187, 470, 1106$ and rebuilds the $p \le 48$ census; none of
  those strings is in this range.

**Deferred, not proposed.** L6 has exactly one non-open-problem result,
`\begin{proposition}\label{prop:kct}` ($k = 2c + t$), and it is the only proved
thing in the paper — the `\Ldisclosure` ledger's first entry, and the reason a
pruned enumerator can be called exact. The phase-1 recentred-basis deferral
turns out to contain no result environments, so there is nothing in it for this
phase; its half-sentence that self-declares "not a new fact" is sentence-scale
and belongs to phase 4.
