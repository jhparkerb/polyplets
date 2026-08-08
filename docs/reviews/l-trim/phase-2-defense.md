> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** DEFENDER's
> phase-2 ledger for the L-trim campaign. Verdicts on the CUTTER's twelve
> result-level proposals; no `.tex` file and no `verify_l_papers.py` was touched.
> All line numbers re-read from the post-phase-1 tree at 895d85f.

# Phase 2 — results. DEFENDER's verdicts.

Twelve proposals, twelve rulings: **ten CONCEDE, two CONCEDE WITH SALVAGE, zero
RETAIN.**

**No ANCHOR DEFECTS in the twelve primary ranges.** Every one opens on its
`\begin{...}` and closes on its matching `\end{...}`, verified line by line
against the files on disk. Three notes for the applier, none of which changes a
verdict:

1. **Two residue anchors are off by one line, in the same direction.** P2.L1.3's
   residue sentence begins with "We record" at the end of **line 502**, not on
   503; P2.L2.3's residue sentence begins with "Whether" at the end of **line
   213**, not on 214. An applier that edits only the named line leaves half a
   sentence behind. Both are wrap artifacts and both are named precisely below.
2. **Every removal in this phase leaves a double blank line**, because a result
   environment sits between two blanks where phase 1's sections sat between a
   blank and a sectioning command. Harmless in LaTeX — consecutive blanks are one
   `\par` — but if the applier wants phase 1's "exactly one blank separator"
   invariant it should take one adjacent blank with each range.
3. **Every theorem-like environment in these papers shares one counter**
   (`shared/preamble.tex` 36–46: `proposition`, `lemma`, `corollary`,
   `definition`, `example`, `remark`, `conjecture`, `openproblem` are all
   `[theorem]`). So each removal renumbers everything after it in that paper. I
   grepped all six manuscripts for a hard-coded result number in prose and found
   none — every cross-reference is a `\ref`. The only hits are `\cite[Lemma~9]`
   into Bousquet-Mélou–Rechnitzer (L4) and L5's header comment block, which names
   `results/hv-growth-sandwich.md`'s numbering, not L5's (`lem:blocks` prints as
   Lemma 3, not Lemma 1 — checked in `L5-convex-king-animals.aux`). The N3
   Gouyou-Beauchamps attribution is enforced by `\cite` placement in prose, not
   by number, so it is unaffected.

**The one proposal I am overturning in part is P2.L1.1**, the cutter's own
"clearest case in this phase". Its supporting claim is false: `prop:rational`'s
proof does **not** re-derive the finiteness fact the argument uses, it re-derives
a *degree* bound. Nothing else in L1 establishes that the four `\sum_c` in
Proposition~\ref{prop:chain} are formal power series. The environment and its
proof still go; one sentence has to stay, and I have written it.

**The second salvage, P2.L5.2, is a three-word repair**: the cutter's
replacement drops "to arbitrary precision", which is the scope of the whole
claim and the entire point of the contrast with the 700-term extrapolation.

**One structural finding the ledger is missing entirely, reported in full in
"The verifier premise" below.** The cutter checked every range against
`verify_l_papers.py` and never mentions `scripts/l_trim_gate.sh` **check 6**,
`constants` — a separate exact-literal grep of eight strings, added to the gate
precisely because `verify_l_papers.py`'s substring tests are weak. I re-derived
all eight against the current tree. No phase-2 range trips it. But check 6, not
`verify_l_papers.py:495`, is what actually blocks the L1 deferral the cutter
deferred for the wrong reason.

---

## L1-diagonal-law.tex

### P2.L1.1 — remove `\begin{lemma}[finiteness]` and its proof

- **verdict**: **CONCEDE WITH SALVAGE**
- **anchor check**: confirmed **lines 259–272**. Line 258 is blank (it follows
  `\end{itemize}` at 257), line 259 is `\begin{lemma}[finiteness]`, line 260 is
  `\label{lem:finite}`, line 263 is `\end{lemma}`, line 265 is `\begin{proof}`,
  line 272 is `\end{proof}`, line 273 is blank, line 274 is
  `\section{The diagonal law}`. 14 lines.
- **collateral check**: confirmed and extended. `\label{lem:finite}` has zero
  references tree-wide (only its own definition, `L1-diagonal-law.tex:260`). No
  `\cite`. I also checked for a *prose* invocation, which a `\ref` grep would
  miss: `grep -n 'finite\|Finite'` over L1 returns 106, 107, 188, 190, 193, 200,
  259, 260, 261, 268, 269, 501, 912 — the only ones outside the range are the
  (R)/(U) definitions, line 200's "finiteness bookkeeping", and two occurrences
  of "not C-finite", which is a different word. **No prose invokes the lemma.**
  The `2^{k-1}` composition count is quoted nowhere: line 547's "compositions of
  $k$" is the exponential-formula sense in §`sec:grand`, a different object.
  Gate check 6 pins no literal in this range.
- **argument**: The cutter is right that the environment does not earn fourteen
  lines and right that no step of Theorem~\ref{thm:A} or Theorem~\ref{thm:B}
  cites it. It is wrong about what is left behind.

  The claim that "Proposition~\ref{prop:rational}'s proof re-derives the only
  finiteness fact the argument uses" does not survive reading that proof. It
  reads: "Only the degree count needs saying, and it is \eqref{eq:elllek} four
  times", and it then bounds the $z$-degree of $E_b$, $E_t$, $\sigma^m$ and the
  pure part. That is a statement about **degrees**, not about **cardinalities**.
  Likewise line 241–244 says \eqref{eq:elllek} "bounds the degree in Step~4".
  \eqref{eq:elllek} is $\ell_c \le k_c$: it bounds a cluster's *length* by its
  *surplus*. It does not say there are finitely many types of a given surplus,
  and it says nothing at all about a weight being a finite number.

  The concrete loss is at Proposition~\ref{prop:chain} (lines 329–334), which
  states four displays built from `\sum_c W_c y^{k_c} z^{\ell_c+1}`,
  `\sum_c W^b_c \dots`, `\sum_c W^t_c \dots` and `\sum_c W^p_c \dots`, "all sums
  over cluster types $c$", and whose proof then says "Summing the geometric
  series in $S$ gives the identity". For those to be elements of $\Z[[y,z]]$ at
  all you need each $W_c$ finite and finitely many $c$ at each surplus, and after
  an unreplaced cut **the paper never says either**. The reader harmed is the one
  checking that $F$ — the object every coefficient extraction in Theorem~\ref{thm:A}
  runs on — exists. They would have to rebuild the $x$-spread argument from (R)
  and (U) themselves. That is "a step of a proof that stops following" in
  PROTOCOL's sense.

  It is not, however, worth fourteen lines and a numbered environment. The
  argument is one clause.
- **salvage**: replace the range with the following, inserted where the lemma
  stood (immediately after the weights `itemize` closes at 257, one blank line
  between):

  ```
  All four weight families are finite, and each surplus admits only finitely
  many cluster types: by (R) and (U) a connected set of cells has bounded
  $x$-spread, so clusters of bounded surplus range over finitely many
  configurations once $x$-translation is quotiented out. The sums in
  Proposition~\ref{prop:chain} are therefore formal power series.
  ```

  Compile check, against the destination file: no macro at all beyond ordinary
  math mode; `prop:chain` is defined in L1 at line 329 and is already `\ref`'d
  within L1, so the forward reference resolves in the same document. Hypotheses
  carried: the finiteness is derived from (R) and (U), exactly as the removed
  proof derives it, and (R)/(U) are defined at L1 188–190, well before this
  point. Numbers carried: none are lost that anything uses — the $2^{k-1}$
  composition count is deliberately dropped, per the collateral check above.
  ~55 words and 5 wrapped lines against 14 lines and ~93 words: net about −9
  lines.

### P2.L1.2 — demote `\begin{theorem}[degree and leading coefficient]` to a sentence

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 444–448**. 443 blank, 444
  `\begin{theorem}[degree and leading coefficient]`, 445 `\label{thm:D}`, 446–447
  the statement, 448 `\end{theorem}`, 449 blank. The replacement target is
  confirmed too: line 450 is "The proof is a corollary of the grand form and is
  given in", 451 is "Section~\ref{sec:grand} (Corollary~\ref{cor:lead}); it is
  written out for the", 452 begins "king lattice in full", unchanged.
- **collateral check**: confirmed exactly. `\ref{thm:D}` occurs at **421** and
  **611** and nowhere else in the tree; both residue edits as specified are
  mandatory, and either one omitted is a dangling `\ref` that gate check 2
  catches. I checked one thing the cutter did not: **`thm:D` is not in the
  `\Ldisclosure` ledger.** L1's ledger (lines 42–66) has entries for
  `thm:A`, `thm:B`, `thm:C`, `tab:machine` and `cor:a308359` — no entry for
  `thm:D`. So no protected block is touched, and the paper's own verification
  ledger already declines to treat this as a result with a warrant of its own.
  `cor:lead` survives with references at 451 and 880. Gate check 6 pins no
  literal in this range (`\Wp = 58` is at 481, `\Wp = 57` at 482 and 712, all
  outside).
- **argument**: Conceded, and the cutter has understated its own case. The two
  statements are not merely equivalent, they are word-for-word the same
  conclusion: `thm:D` says "$\deg q_k = k$ exactly, and the coefficient of $n^k$
  in $P_k$ is $\Wp^{\,k}/k!$"; `cor:lead` (611–616) ends "$[n^k]P_k = \Wp^{\,k}/k!$
  and $\deg P_k = k$", and $\deg P_k = \deg q_k$ by \eqref{eq:qk}'s substitution.
  One of them has a proof. The one with no proof is the one that had to be
  cross-titled to tell the reader they are the same.

  I looked for the loss and cannot find one. There is no list of theorems, no
  hard-coded "Theorem D" in prose, and no external document that could cite it —
  L1's protected result under PROTOCOL §4 is the universal law (`thm:A`), which
  is untouched. The ledger's silence on `thm:D` settles it.
- **replacement text — passes the phase-1 standard.** Checked clause by clause:
  it compiles in L1 (`\Wp` is defined at L1 line 23, which is the destination
  file, and `\ref{cor:lead}` and `\ref{sec:grand}` are both L1 labels); it
  carries all three of the original's claims, including the "In particular
  $[n^1]P_1 = \Wp$" that a demotion could easily have dropped; and it inherits
  the same ambient hypothesis the theorem had, since it sits in §`sec:sharp`
  under the same "row-local lattice with drift count $b$" that
  Theorem~\ref{thm:A} sets up. One stylistic note, not a defect: "Precisely:"
  now points back across `\begin{definition}[the pair weight]` to §`sec:sharp`'s
  opening sentence at 434–435. It reads, because the intervening definition
  defines the constant that sentence names, but if the applier wants it tighter,
  "Precisely" → "The bound is attained at every $k$:" costs four words and
  removes the reach-back.

### P2.L1.3 — remove `\begin{openproblem}[onset sharpness in general]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 906–913**. 903 `\section{Open problems}`,
  904 `\label{sec:open}`, 905 blank, 906 `\begin{openproblem}[onset sharpness in
  general]`, 913 `\end{openproblem}`, 914 blank, 915 the next open problem.
  **Residue anchor is off by one**: the sentence to be rewritten is "We record /
  onset sharpness as an open problem (Section~\ref{sec:open}) and note that",
  and "We record" is the last two words of **line 502**, not of 503. The edit is
  therefore: leave 502 through "gap." and replace its trailing "We record" plus
  all of line 503 with "We record it as open and note that". Line 504
  ("Corollary~\ref{cor:a308359} uses it only as a control, never as an input.")
  is unchanged.
- **collateral check**: confirmed. No `\label` in 906–913; one outgoing `\ref` to
  `thm:A`. After the residue edit `\label{sec:open}` (904) has no reference —
  `grep -n 'sec:open'` returns 503 and 904 only — and the cutter is right that an
  unreferenced label is not an undefined reference: gate check 2 greps the log
  for "undefined", which an orphaned `\label` never produces. The label should
  stay. Gate check 6 pins no literal here.
- **argument**: Conceded. I checked the §`sec:sharp` paragraph (494–504) clause
  by clause against the open problem and the containment is total: validity from
  $n = 2k+1$ (494–495), failure at $n = 2k$ as a non-cancellation statement
  needing $\deg D = k$ (495–496), all banked king data through $k \le 17$
  (496–497), ab initio from the weight table for $k \le 5$ (498), the blocked
  route as a rational generating function for the top coefficient (500–501), the
  obstruction that the all-pairs weight family is not C-finite (501). The
  paragraph additionally holds the leading coefficients $1, 4, -80, 1753,
  -40928, 987355$ and the refutation point $\ell = 16$, and the open problem
  holds neither. The evidence and the closed door are both in the surviving copy.
  The only unique text is the imperative, and 499 already says "It is not proved
  for all $k$" with the residue supplying "and we record it as open".

---

## L2-ternary-spine.tex

### P2.L2.1 — demote `\begin{remark}[the automaton]` to one sentence

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 284–292**. 282 `\end{proof}` (of
  Theorem~\ref{thm:digit}), 283 blank, 284 `\begin{remark}[the automaton]`, 292
  `\end{remark}`, 293 blank, 294 `\section{The spine}`. The insertion point named
  by the cutter ("immediately after Theorem~\ref{thm:digit}'s proof") is exactly
  where the range sits.
- **collateral check**: confirmed, and this is the one that matters. `grep -n`
  over L2 returns `christol1980` **only at 286** and `allouche2003` **only at
  288**, both inside the range. No `\label`, so nothing can `\ref` the remark;
  one outgoing `\ref` to `thm:digit`, kept by the replacement. No back-reference
  in — "automaton" appears at 87 (abstract), 288 and 150 (§`sec:novelty`), and
  none of them points at this environment. **Neither gate check would catch the
  loss**: check 2 greps the log for "undefined", and dropping the last `\cite` of
  a key that still exists in `refs.bib` produces no undefined citation at all —
  BibTeX silently omits the entry. The replacement text is the only thing
  standing between this cut and two lost attributions, which is why I verified
  it by hand rather than trusting the gate.
- **argument**: Conceded. Verified both duplications: line 87 of the abstract is
  "so the triangle mod $3$ is $3$-automatic and the automaton is explicit", and
  §`sec:novelty` 148–151 is "Christol's theorem, which is what makes ``algebraic
  over $\F_3$'' and ``$3$-automatic'' the same statement". "Nothing about the
  animals is consulted" is the aphoristic closer PROTOCOL names.

  The one loss worth pricing is the reading recipe — "to read $T(n,H) \bmod 3$,
  expand $n$ in base $3$ and multiply one factor per digit" — which is the only
  sentence in L2 that translates Theorem~\ref{thm:digit} from $P_k(n)$ back to
  the triangle $T(n,H)$ a reader actually has. It is one substitution away:
  \eqref{eq:law} at L2 163 gives $T(n, n-k) = P_k(n)\cdot 3^{\,n-1-3k}$, in the
  paper's own §Setup. One substitution is not a step that stops following, and
  PROTOCOL is explicit that "a reader might wonder" is not decisive. Conceded.
- **replacement text — passes.** `\F_3` is used throughout L2 (251, 256, 279),
  `\cite{christol1980}` and `\cite{allouche2003}` are the two keys that had to
  survive and both are present, `\ref{thm:digit}` resolves within L2. No
  hypothesis is dropped: the original's antecedent is "$W$ is algebraic over
  $\F_3(t)$" and the replacement opens with the identical clause. ~28 words for
  ~64.

### P2.L2.2 — remove `\begin{remark}[why one per three]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 440–447**. 439 blank, 440
  `\begin{remark}[why one per three]`, 447 `\end{remark}`, 448 blank, 449
  `\section{Reading along rows}`.
- **collateral check**: confirmed, and the decisive one is the cutter's own
  point turned into a measurement. `grep -n 'atom' L2-ternary-spine.tex` returns
  **exactly two hits, 443 and 445 — both inside the range.** "Atom" is used twice
  in this paper and defined zero times. No `\label`, no `\cite`, no outgoing
  `\ref`, no back-reference in. `verify_l_papers.py` does not read L2; gate check
  6's L2 literal is the $H$ series, which is at 211 and 584, not here.
- **argument**: Conceded without reservation, and this is the strongest of the
  twelve. The explanation the remark offers is the last display of
  Theorem~\ref{thm:snf}'s proof, at 432–437: `nullity` $= \#\{H \le N :
  \lfloor 3H/2\rfloor > N\} = \lceil (N-1)/3 \rceil$, with $H \mapsto \lfloor
  3H/2\rfloor$ named and its strict monotonicity used, ten lines above. The
  remainder asserts an identification with an "atom factorisation" that this
  paper never introduces, and closes on an epigram that contains the undefined
  term. Removing an assertion whose subject is undefined is not a loss.

### P2.L2.3 — remove `\begin{openproblem}[is $H$ known?]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 583–587**. 582 blank, 583
  `\begin{openproblem}[is $H$ known?]`, 586 the `\cite{oeis}` line, 587
  `\end{openproblem}`, 588 blank. **Residue anchor is off by one**: the sentence
  to be rewritten is "Whether / $H$ itself is a known sequence is one of the
  things the missing novelty sweep / would settle.", and "Whether" is the last
  word of **line 213**, not the first word of 214. The edit spans 213's trailing
  "Whether" through 215.
- **collateral check**: confirmed. `\cite{oeis}` occurs **only at 586** in L2 —
  same silent-loss exposure as P2.L2.1, and the residue is the only thing that
  carries it. One outgoing `\ref` to `sec:novelty`, which is also `\ref`'d from
  the `\Ldisclosure` ledger and is unaffected. No back-references in.
  **Gate check 6, re-derived**: the pinned literal
  `1, 25, 208, 1483, 20688, 130208` occurs at **211 and 584**. This cut removes
  584 and leaves 211, so the count drops 2 → 1, which check 6 explicitly permits
  ("a count that merely drops is a legitimate cut of a duplicate occurrence").
  Green. The cutter did not check this and got lucky by one occurrence.
- **argument**: Conceded. Lines 211–215 print the same six terms, give the same
  description ("the per-row transfer series of the underlying defect gas"), and
  ask the same question, 370 lines earlier. The residue is correct to hold the
  "not checked against the OEIS or anywhere else" disclosure rather than the
  "candidate new integer sequence" claim: under L2's own novelty-unchecked
  banner the disclosure is the load-bearing half and the claim is the one the
  banner asks the paper not to make.
- **replacement text — passes.** `\cite{oeis}` carried; compiles in L2; no
  hypothesis to carry; the pointer to §`sec:novelty` is dropped, but the
  surviving clause "one of the things the missing novelty sweep would settle" is
  the same pointer in prose and `sec:novelty` retains its other references. One
  stylistic note, not a defect: the replacement inserts a `---` aside into a
  sentence, which is the construction PROTOCOL lists among the standing cuts;
  "Whether $H$ itself is a known sequence, unchecked against the OEIS~\cite{oeis}
  or anywhere else, is one of the things…" costs one word less and avoids it.

---

## L3-lambda-bounds.tex

### P2.L3.1 — remove `\begin{proposition}[existence, and terms are floors]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 166–170**. 164 `\end{definition}`, 165
  blank, 166 `\begin{proposition}[existence, and terms are floors]`, 167
  `\label{prop:fekete}`, 168–169 the statement, 170 `\end{proposition}`, 171
  blank, 172 "This is Fekete's lemma on $\log a$. The ladder --- ". The residue
  target is correct as stated: the sentence to delete opens and closes on 172,
  which is the only residue anchor in this phase that needs no correction.
- **collateral check**: confirmed. `\label{prop:fekete}` has zero references
  tree-wide. No `\cite`, no outgoing `\ref`. **Gate check 3, re-derived from the
  code rather than from a string grep — and this is the one place in the phase
  where the cutter's method could have missed something.**
  `check_l3_ladder()` at `verify_l_papers.py:104` does
  `body = src.split(r"\label{tab:ladder}")[0]` and then requires **exactly 16
  rows** matching `\s*(\d+)\s*&\s*…&\s*…&\s*…&\s*(\d+)\s*&` in that prefix.
  `\label{tab:ladder}` is at L3 line 284, so **this range is inside the parsed
  prefix**: a cut of text before line 284 that happened to match the row regex
  would change the row count and turn the verifier red without touching a single
  constant. I checked 166–172: **no `&` appears anywhere in the range**, so no
  line can match. Green. The other L3 checks read `5^5/4^4`, `9.3154`, `9.4117`,
  `\lambda_{\text{polyomino}} \le 4` and the two bracket displays, all outside.
  Gate check 6's two L3 literals, `6.543` and `9.3154`, occur at twelve and ten
  lines respectively, none of them in this range.
- **argument**: Conceded. Lines 116–119 of the introduction state all three
  clauses and one more: "gives $a(m)a(n) \le a(m+n)$; Fekete's lemma then makes
  $\lambda := \lim_n a(n)^{1/n}$ exist, with $a(n) \le \lambda^n$ for every $n$
  --- so every enumerated term is a floor on $\lambda$ and never an
  approximation to it." The final clause is the proposition's own title, set as
  prose. The proposition has no proof, so nothing recoverable is lost with it,
  and the `\Ldisclosure` entry for the existence of $\lambda$ (lines 40–44) names
  `a_supermul`, `lambda_tendsto`, `a_le_lambda_pow` and `lambda_le` directly, so
  the protected ledger does not point at the environment.

  The residue deletes "This is Fekete's lemma on $\log a$." — the only place the
  paper says *which function* Fekete is applied to. I considered defending those
  four words and will not: line 116 names Fekete, the sequence is stated
  supermultiplicative in the same sentence, and taking the log is the standard
  and only application. If jasonp wants it anyway it costs four words in the
  introduction ("Fekete's lemma, applied to $\log a$, then makes"), and that is a
  preference, not a defence.

### P2.L3.2 — remove `\begin{openproblem}[the missing concatenation lemma]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 725–730**. 723 `\end{openproblem}` (of
  `[certify further rungs]`), 724 blank, 725 `\begin{openproblem}[the missing
  concatenation lemma]`, 730 `\end{openproblem}`, 731 blank, 732
  `\section{Reproduction}`. The surviving copy is confirmed at **667–677**,
  §`sec:gap`'s `\paragraph{An independent route, also closed.}`.
- **collateral check**: confirmed. No `\label`, no `\cite`, no outgoing `\ref`
  in the range; nothing points at it. Gate check 6's L3 literals are untouched.
- **argument**: Conceded. I read 667–677 against the open problem and the
  surviving copy is strictly larger on every clause: the target
  $\lambda \le 7.745$ with $a(40)$ known and the parenthetical that degree 4
  yields nothing (668–671); the measured obstruction, "their lexicographic split
  shatters a king comb into about $n/4$ components --- measured --- so the
  reassembly code costs $n^{\Theta(n)}$" (672–674); the centroid-split failure to
  prescribe sizes to within $O(1)$ (674–675); and the hardness transfer, "the
  missing lemma would also improve the published polyomino record from $4.5252$
  to $4.3828$, so it is known-hard rather than merely unattempted" (676–677).
  The open problem's only unique phrase, "with $\mathrm{poly}(n)$ reassembly
  information", is the negation of a quantity the paragraph measured. Both the
  measurement and the closed door survive, which is what PROTOCOL's standing
  defence actually protects.

---

## L4-not-dfinite.tex

No proposals, and I agree with the cutter's reasoning for the two it considered.
I spot-checked `lem:northcott`: it is `\ref`'d twice, including from
`\begin{openproblem}[quantitative Northcott]`, so it is not the sole-use lemma a
grep for one reference would suggest. Nothing to rule on.

---

## L5-convex-king-animals.tex

### P2.L5.1 — demote `\begin{remark}[the square-lattice analogue is classical]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 397–405**. 395 `\end{table}` (of
  `tab:fourrungs`), 396 blank, 397 `\begin{remark}[the square-lattice analogue is
  classical]`, 405 `\end{remark}`, 406 blank, 407 `\section{Area is wild}`. The
  residue target is confirmed at **1095–1100**,
  `\paragraph{The square-lattice analogue.}`, opening exactly as the cutter
  quotes it.
- **collateral check**: confirmed. No `\label`. `\cite{bender1974}` at 398 inside
  the range, and also at 129, 542 and 1095 outside it, so the key cannot be lost
  even if the replacement were dropped. One outgoing `\ref` to `prop:squeeze`,
  defined elsewhere. No back-references in. `verify_l_papers.py` never opens L5
  — I confirmed from `main()` at line 506, which calls only the L3, L4, L1 and L6
  checks. Gate check 6's L5 literal is `3.12340450886853853211`, which occurs
  **once, at line 340**, inside the deferred `\begin{corollary}[every banked term
  is a floor]` — outside all three L5 ranges, and a standing reason no later
  phase may take that corollary without relocating the literal first.
- **argument**: Conceded. The duplication is claim for claim, as stated: Bender's
  $2.30914$, the parallelogram subclass \oeis{A006958} sharing it,
  Proposition~\ref{prop:squeeze}'s conclusion being readable off the solved
  models one lattice over, and the contribution being the generality. The
  surviving copy closes "It is the generality --- every intermediate class, on a
  lattice where nothing is solved --- that is the contribution", which is the
  removed remark's last sentence in different words. The cutter is right that the
  one thing not duplicated is the measurement, and right that it is a different
  object from the $121$-digit HV-convex \oeis{A067675} control.
- **replacement text — passes.** `\cite{bender1974}` and `\oeis{}` are both
  already in the destination paragraph, so nothing new is introduced; the
  measurement is carried verbatim, both the value $2.309138593330495$ and its
  range "flat from $n = 100$ to $n = 400$", and the aside attaches to the
  parallelogram subclass, which is the object measured. Stylistic note, not a
  defect: the result is two `---` asides in a six-line paragraph, the second
  inside the first's sentence. Parentheses read better and cost nothing:
  "…the parallelogram subclass \oeis{A006958} sharing it (measured here at
  $2.309138593330495$, flat from $n = 100$ to $n = 400$), mean that…".

### P2.L5.2 — demote `\begin{corollary}[$\mu$ by shooting]` to a sentence

- **verdict**: **CONCEDE WITH SALVAGE**
- **anchor check**: confirmed **lines 958–965**. 956 `\end{proof}` (of
  `prop:phi`), 957 blank, 958 `\begin{corollary}[$\mu$ by shooting]`, 959
  `\label{cor:shoot}`, 965 `\end{corollary}`, 966 blank, 967
  `\begin{proposition}[the ratio]`.
- **collateral check**: confirmed. `\label{cor:shoot}` has zero references
  tree-wide. No `\cite`, no outgoing `\ref`. Both back-references are correctly
  identified and neither needs an edit: the abstract at **118–120** says "The
  same recurrence computes $\mu$ by shooting --- $987$ digits in $1.6$ seconds,
  with no series and no extrapolation", naming no environment, and §`sec:related`
  at **1092** credits "the eigenvector recurrence and the shooting method
  (Proposition~\ref{prop:phi})", pointing at the proposition and not the
  corollary. `cor:shoot` prints as Corollary 17 (`L5-convex-king-animals.aux:78`);
  removing it renumbers 18 onward, and nothing in any of the six papers refers to
  an L5 result by number.
- **argument**: Conceded, and the cutter's framing is the right one. The
  environment reports an operation count, a digit count, a wall-clock and a core
  count; nothing in it is deduced from Proposition~\ref{prop:phi} in the sense
  that makes a corollary a corollary. The paper's whole organising discipline —
  the `\Ldisclosure` ledger sorting every item into proved, rigorous-in-one-
  direction, measured or conjectured — is contradicted exactly once, here.
  Demoting it to prose is the paper agreeing with itself.
- **salvage**: the cutter's replacement drops **"to arbitrary precision"**, which
  is not decoration. The original claim is that shooting computes $\mu$ *to
  arbitrary precision* in $O(h_{\max})$ operations; without the scope, the
  $O(h_{\max})$ is a cost with no stated target and the contrast with "a $700$-term
  enumeration plus extrapolation for $200$" — which *is* precision-capped — loses
  its point. That is a hedge that scopes a claim, and PROTOCOL protects those.
  Ship this instead, three words longer:

  ```
  Shooting on that recurrence computes $\mu$ to arbitrary precision in
  $O(h_{\max})$ operations, with no series and no extrapolation: it reproduces
  all $199$ banked digits, continues past them, and reaches $987$ digits in
  $1.6$ seconds on one core, against a $700$-term enumeration plus extrapolation
  for $200$.
  ```

  Compile check: `$h_{\max}$` is used in the surrounding subsection and needs no
  macro; no `\ref`, no `\cite`, nothing document-specific. Numbers carried:
  $O(h_{\max})$, $199$, $987$, $1.6$ seconds, one core, $700$, $200$ — all seven,
  including the $987$ and $1.6$ the abstract also quotes at 118–120, so the two
  statements still agree. The `\textbf{}` emphasis is dropped deliberately: it
  was setting a benchmark in bold inside a corollary, which is the thing being
  fixed.

### P2.L5.3 — remove `\begin{openproblem}[the arithmetic of $\mu$]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 1120–1123**. 1118 `\end{openproblem}` (of
  `[a sharp asymptotic…]`), 1119 blank, 1120
  `\begin{openproblem}[the arithmetic of $\mu$]`, 1123 `\end{openproblem}`, 1124
  blank, 1125 `\begin{openproblem}[non-D-finiteness as a theorem]`.
- **collateral check**: confirmed. No `\label`, no `\cite`; one outgoing `\ref`
  to `sec:exclusions`, which is also `\ref`'d from the protected `\Ldisclosure`
  ledger and is unaffected. No back-references in. No verifier or gate-6
  exposure.
- **argument**: Conceded, and the cutter is right to call it the weakest
  proposal. I verified both surviving statements: line 577, "We do not claim
  $\mu$ is irrational, and no argument here bears on it", and line 1066, "There
  is no proof that $\mu$ is irrational, let alone transcendental, so $\Q(\mu)$ is
  a field of unknown degree". Between them they say everything the open problem
  says, in the two sections where a reader would meet the question.

  The one available defence is that a disclaimer and an open problem are
  different speech acts, and that removing it costs a reader scanning
  §Open problems the arithmetic of $\mu$ entirely. I do not get to make that
  argument here, having declined it in P2.L1.3 and P2.L6.1 where it is the same
  argument with the same shape. Fifteen words, no unique content, conceded.

---

## L6-perimeter-gradings.tex

### P2.L6.1 — remove `\begin{openproblem}[the higher tips]`

- **verdict**: CONCEDE
- **anchor check**: confirmed **lines 650–653**. 648 `\end{openproblem}` (of
  `[is the two-variable generating function rational?]`), 649 blank, 650
  `\begin{openproblem}[the higher tips]`, 653 `\end{openproblem}`, 654 blank, 655
  `\begin{openproblem}[the hull factorisation]`. The surviving copy is confirmed
  at **530–534**, §`sec:tips`'s closing paragraph.
- **collateral check**: confirmed. No `\label`, no `\cite`.
  `grep -n 'sec:tips'` returns exactly **486** (the `\label`) and **652**, so the
  cut leaves the label unreferenced — harmless, for the reason given under
  P2.L1.3, and the label should stay. **Gate check 3, re-derived from the code**:
  `check_l6_min_end()` reads the census cold and greps the source for the seven
  stabilised constants $1, 6, 22, 68, 187, 470, 1106$; those occur at L6 lines
  **417 and 427**, both outside this range. **Gate check 6, re-derived**: the
  pinned literal `1, 6, 22, 68, 187, 470, 1106` occurs at **427**, also outside.
  Green on both.
- **argument**: Conceded. §`sec:tips` 530–534 has the whole content and labels it
  deliberately as a closed door: the two corner types as the first two members of
  one family, $\phi_1 = P(x)$ for a unimodular corner, $\phi_2$ for the index-$2$
  diamond tip, and "the natural guess --- $\phi_m$ for index $m$ --- is
  \textbf{false} at $m = 3$, and is recorded here as a closed door rather than
  left as a suggestion". The surviving copy is the one that says $m = 3$ was
  actually tried, which is the half PROTOCOL protects; the open problem adds "What
  is?".

---

## Noted for later phases

Not argued for, not proposed, and not this phase's to touch. A bare list.

- L1 200: "Conditions (R) and (U) are finiteness bookkeeping" — sits four lines
  from P2.L1.1's salvage sentence and says a weaker version of it.
- L1 241–244: "Inequality~\eqref{eq:elllek} is the load-bearing triviality of
  this paper" — three-clause self-appraisal.
- L1 434–435 against P2.L1.2's replacement: the section opener and the
  "Precisely:" sentence now state the same thing two paragraphs apart.
- L1 453–457: "We state the measured position honestly" — scaffolding opener on a
  paragraph whose content is the six-lattice measurement.
- L2 82–86 against 270–273: the abstract prints the digit-product display in full
  and Theorem~\ref{thm:digit} prints the same display again.
- L3 138–145: the $9.3154$-not-$9.3153$ footnote opens "Worth one sentence
  because it is easy to get backwards" and then runs seven lines. The constants
  are protected; the framing sentence is not.
- L3 291 and 379: "$6.543$ against a float $6.5465$" printed twice, ninety lines
  apart.
- L3 147–148: "Both halves are \emph{certificates} in a strict sense that is
  worth stating, because it is the organising idea of the paper."
- L5 8–20: the header comment names L5 results by numbers that do not match the
  compiled numbering (`lem:blocks` prints as Lemma 3). Comment hygiene,
  post-campaign, not a manuscript edit.
- Carried from phase 1 and still open: `verify_l_papers.py:221`'s stale comment,
  post-campaign; and L5 `tab:perim` row 3's dir4-by-area exclusion verdict, which
  nothing in L5 warrants. Neither is this campaign's to fix.

---

## The verifier premise

### (a) `\begin{remark}[$4, 9, 25$ are not squares, and that matters]`

**It should not have been proposed on the merits, and it is not a duplicate of
`\begin{remark}[the statement is exactly sharp]`.** The deferral reached the
right answer for the wrong reason, three times over.

1. **It is referenced, twice.** `grep -n 'rem:notsquares'` returns 476 (the
   `\label`), **716** and **918**. Line 716 is *inside the alleged duplicate*:
   the sharpness remark says "Two further consequences of
   Remark~\ref{rem:notsquares}'s closed form, for interval $D$…" and then derives
   $w \equiv 4$ at odd $p \mid b$ and $w \equiv \lfloor b/2 \rfloor \pmod 2$ at
   $p = 2$ from it. The second remark **depends on** the first; it does not
   repeat it. Line 918 is `\begin{openproblem}[closed forms for multi-row cluster
   weights]`, which asks for a generalisation of "Remark~\ref{rem:notsquares}'s
   $\Wp(b)$ for interval $D$". Cutting the remark dangles both and fails gate
   check 2.
2. **The content is disjoint.** `rem:notsquares` (475–492) carries three things
   that appear nowhere else in L1: the erratum — "an earlier version of this work
   published one of the wrong numbers", with the cause named (the earlier
   computation capped the column gap at $2$, which is correct only when
   $\max|dx| \le 1$) — which is a closed door and a correction of record, the
   least recoverable kind of text in these papers; the closed form
   $\Wp(b) = b^3 - b(b+1)/2 + 4$ for interval step sets, verified $b \le 8$ by
   gadget count and $b \le 5$ end to end, which `verify_l_papers.py:486`
   reimplements as `Wpair_interval` and checks against $4, 9, 25, 58, 114$; and
   the explicit refusal to present that closed form as a result. The sharpness
   remark (710–721) carries Theorem~\ref{thm:B}'s two witnesses as *congruences*
   ($57 \equiv 0 \pmod 3$, $114 \equiv 4 \pmod 5$). The only overlap is that the
   integers $57$ and $114$ occur in both, as counts in one and residues in the
   other.
3. **It is a hard gate blocker, but not at the check the cutter named.** The
   ledger says `verify_l_papers.py:495` blocks it. That check is
   `ok("58" in src and "114" in src and "57" in src, …)` — a substring test on
   the whole file — and the strings survive elsewhere: "58" inside **`6558`** in
   the six-lattice table at line 639, "114" at 714 and "57" at 712, both in the
   sharpness remark. The verifier would stay green. What actually blocks it is
   **`scripts/l_trim_gate.sh` check 6**, which pins the exact literal
   `\Wp = 58` and requires a nonzero count: `grep -Fn` returns **one hit, line
   481, inside the remark**. Cutting it takes the count to zero and the gate
   says "constants L1-diagonal-law.tex no longer prints: \Wp = 58".

My recommendation for a later pass: leave it. If jasonp wants it shortened, the
only losable text is the last clause of the second paragraph ("exactly three
members of the class are objects anyone studies, and all three are in
Table~\ref{tab:instances}"), which is sentence-scale and belongs to phase 4, and
even that leaves `\Wp = 58` and both incoming `\ref`s in place.

### (b) Every verifier-exposure claim in the ledger, re-derived from the code

I read `verify_l_papers.py` and `scripts/l_trim_gate.sh` in full rather than
grepping for strings. Four findings.

**1. The ledger's claims about `verify_l_papers.py` are all correct, and its
method is not.** `main()` at line 506 calls `check_l3_ladder`,
`check_l3_constants`, `check_l4_boxes`, `check_l4_mu_agrees_with_l3`,
`check_l1_king_diagonals`, `check_l1_a308359`, `check_l1_pair_weights` and
`check_l6_min_end`. **L2 and L5 are never opened**, so "no verifier exposure at
all" is right for both. The L1 checks read the king triangle, A308359 and the
pair weights; the L6 check reads the min-end census. None of their greps falls
in a phase-2 range.

**2. The ledger never mentions gate check 6, which is a second and stronger
constants check.** `scripts/l_trim_gate.sh` runs six checks, not five; check 6,
`constants`, greps eight exact literals with `grep -Fc` and fails on a count of
zero. Its own header comment says why it exists: measured 2026-08-07, deleting
the line of L4 that prints all ten ψ-degrees leaves `verify_l_papers.py:204`
green, and "58" at `:495` is satisfied by the "6558" in a table. This is the
check that governs constants in this campaign. I re-derived all eight against
the current tree:

| literal | occurrences | in a phase-2 range? |
|---|---|---|
| L1 `\Wp = 58` | 481 | no (in the deferred `rem:notsquares`) |
| L1 `\Wp = 57` | 482, 712 | no |
| L2 `1, 25, 208, 1483, 20688, 130208` | 211, 584 | **584 is in P2.L2.3** — count 2 → 1, permitted |
| L3 `6.543` | 12 lines | no |
| L3 `9.3154` | 10 lines | no |
| L4 `1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289` | 329 | no (L4 has no proposals) |
| L5 `3.12340450886853853211` | 340 | no (in the deferred `cor:floor`) |
| L6 `1, 6, 22, 68, 187, 470, 1106` | 427 | no |

**No phase-2 proposal trips check 6.** Three of the eight literals are
single-occurrence — L1 `\Wp = 58`, L4's ψ-degrees, L5's $M(700)^{1/700}$ — and
any later phase that goes near lines 481, 329 or 340 must relocate the literal
first.

**3. One check reads structure, not constants, and one phase-2 range is inside
it.** `check_l3_ladder` parses `src.split(r"\label{tab:ladder}")[0]` — everything
before L3 line 284 — and asserts exactly 16 rows match its row regex. A cut
anywhere in L3's first 284 lines that removed or altered a matching row would
turn the verifier red without touching any constant, and a string-grep method
cannot see that. P2.L3.1's range (166–170, plus the 172 residue) is inside that
prefix; it contains no `&`, so no line can match and the count is unchanged.
Green — but by inspection of the parser, not by luck.

**4. Neither gate check can catch a lost bibliography entry, which is the
largest silent risk in this phase.** Check 2 greps the compile log for
"undefined". Removing the *last* `\cite{christol1980}` from L2 produces no
undefined citation — the key still exists in `refs.bib`, BibTeX simply omits the
entry, the paper compiles clean, and the attribution disappears with no warning
anywhere in the gate. `christol1980`, `allouche2003` and `oeis` each occur
exactly once in L2, all three inside proposed ranges. I verified both
replacement texts carry them, character by character; nothing downstream will.
