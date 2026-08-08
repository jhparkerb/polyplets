# LLM-tic sweep findings: L1, L2, L3

> Authored by Claude at jasonp's direction, 2026-08-08. Catalog and hard
> constraints: `catalog.md` beside this file. Gates after all edits:
> `paper/verify_l_papers.py` all 326 checks passed (20 RED controls, all
> fired); `scripts/l_trim_gate.sh check` clear.

Counts (found / fixed / kept): **L1 14 / 6 / 8 . L2 8 / 3 / 5 . L3 14 / 6 / 8
. total 36 / 15 / 21.**

Grep sweep result: zero hits on the entire class-B focal wordlist, zero
editorializing -ing trailers, zero hedging doubles -- the trim campaign already
took those. What remained was a formulaic-expression spike (the cleft
"is what makes / are what make", ten sites across the three papers; the pure
wordiness cases are fixed below, the focus-bearing ones kept), plus scattered
rhythm and metaphor items.

## L1-diagonal-law.tex -- 14 found, 6 fixed, 8 kept

- **T.L1.1** (A/cleft, S1) FIXED.
  OLD: `Stratifying by height does not repair that. What it does is expose structure the row sums hide.`
  NEW: `Stratifying by height does not repair that; it exposes structure the row sums hide.`
- **T.L1.2** (C/cleft, S2) FIXED.
  OLD: `it is what makes a row with a single cell a cut, which is Lemma~\ref{lem:sep}`
  NEW: `it makes a row with a single cell a cut, which is Lemma~\ref{lem:sep}`
- **T.L1.3** (F/G rhythm-only fragment, rem:names) FIXED -- deleted whole; the
  remark's title and preceding sentences already state the collision.
  OLD: `Two names, crossed. ` NEW: (deleted)
- **T.L1.4** (C/cleft, proof of prop:chain) FIXED.
  OLD: `are what make it exact rather than an inequality.`
  NEW: `make it exact rather than an inequality.`
- **T.L1.5** (D elegant variation, S5: "moves" for the Steps the paragraphs
  are named after) FIXED.
  OLD: `We sketch the four moves;` NEW: `We sketch the four steps;`
- **T.L1.6** (C/cleft, grand form Step 2) FIXED.
  OLD: `This is the fact that makes the resummation exact rather than asymptotic.`
  NEW: `This fact makes the resummation exact rather than asymptotic.`
- **T.L1.7** (A, abstract) KEPT: `The onset $H \ge k+1$ is proved, not
  observed.` -- epistemic substance, exactly the disclosure the split requires.
- **T.L1.8** (G, S2) KEPT: `the load-bearing triviality of this paper` --
  "load-bearing" is consistent house vocabulary (three sites across L1/L3),
  not a one-off metaphor.
- **T.L1.9** (D, S2) KEPT: triad `what bounds the degree ... what makes the
  onset ... what collapses the mod-$p$ series` -- three real consequences,
  each with a pointer to where it is used.
- **T.L1.10** (A/F, S5) KEPT: `no analysis, no convergence question, and ---
  the load-bearing feature --- no weight enumeration` -- the list is
  substantive and the aside marks which item drives the all-$k$ claim.
- **T.L1.11** (G, S1.1) KEPT: `the nearest published relative` / `That
  relative` -- used twice consistently; renaming would be elegant variation.
- **T.L1.12** (G, S6) KEPT: `is where quantifying over lattices pays off` --
  ordinary idiom, one plain clause.
- **T.L1.13** (A, S8 polyiamonds) KEPT: `This is not a technicality that a
  little more care would remove.` -- substantive claim that the failure is
  essential, backed by the next sentence's counts.
- **T.L1.14** (A, S7) KEPT: `checks rather than results, and they are the
  reason to believe the rest` -- epistemic substance about the table's roles.

## L2-ternary-spine.tex -- 8 found, 3 fixed, 5 kept

- **T.L2.1** (E significance inflation + G, abstract) FIXED.
  OLD: `Read as an integer matrix, this triangle has a striking property: \emph{its entire integer content sits at the single prime $3$}.`
  NEW: `Read as an integer matrix, \emph{the triangle's entire integer content sits at the single prime $3$}.`
- **T.L2.2** (C/cleft, S1.2) FIXED.
  OLD: `Christol's theorem, which is what makes ``algebraic over $\F_3$'' and ``$3$-automatic'' the same statement`
  NEW: `Christol's theorem, which makes ``algebraic over $\F_3$'' and ``$3$-automatic'' the same statement`
- **T.L2.3** (C/cleft, S2) FIXED.
  OLD: `Equation~\eqref{eq:grand} is what makes this paper possible:`
  NEW: `Equation~\eqref{eq:grand} makes this paper possible:`
- **T.L2.4** (A, S1.1) KEPT: `That is not hard to explain ... What is harder,
  and what this paper is about, is the second observation` -- the easy/hard
  contrast structures the whole paper; load-bearing.
- **T.L2.5** (G/A, ladder star-b) KEPT: `the gas of bare pair rows rather than
  a numerical coincidence` -- "gas" is the project's coined term
  (results/defect-gas.md); the contrast is epistemic.
- **T.L2.6** (G, S4) KEPT: `a rational parametrisation that does all the
  computational work below` -- already the plain statement.
- **T.L2.7** (A, S8 opener) KEPT: `The cubic does not stop at $\F_3$.` --
  one-line statement of the section's content (the lift), not a flourish.
- **T.L2.8** (H/A, S7 sleeve zeros) KEPT: `This section is measurement. No law
  is claimed.` -- required epistemic disclosure, not scaffolding.

## L3-lambda-bounds.tex -- 14 found, 6 fixed, 8 kept

- **T.L3.1** (F rhythm dash + repetition, abstract) FIXED.
  OLD: `beats the best previously published lower bound --- and beats it with a certificate, where that value was numerical.`
  NEW: `beats the best previously published lower bound, with a certificate where that value was numerical.`
- **T.L3.2** (G one-off metaphor, S3.5) FIXED.
  OLD: `The lever with teeth is the number of decimal digits`
  NEW: `The lever that works is the number of decimal digits`
- **T.L3.3** (E editorializing, S3.5) FIXED.
  OLD: `The behaviour under deliberate crippling is the reassuring measurement here.`
  NEW: `Deliberate crippling measures the flooring loss directly.`
- **T.L3.4** (C/cleft, S4.4) FIXED.
  OLD: `Two details are what make \eqref{eq:split} beat the generic version`
  NEW: `Two details make \eqref{eq:split} beat the generic version`
- **T.L3.5** (C/cleft, S5) FIXED.
  OLD: `The same wall is what saturated the window lever in Table~\ref{tab:rd}.`
  NEW: `The same wall saturated the window lever in Table~\ref{tab:rd}.`
- **T.L3.6** (C precious predicate, S6) FIXED.
  OLD: `against their $11\%$ is the eight-neighbour penalty made quantitative.`
  NEW: `against their $11\%$ quantifies the eight-neighbour penalty.`
- **T.L3.7** (A, S1) KEPT: `a floor on $\lambda$ and never an approximation to
  it` -- the direction of the inequality is the content.
- **T.L3.8** (A, footnote to thm:main) KEPT: `a bound should round away from
  the truth, not toward it` -- states the rounding rule the footnote exists
  to state.
- **T.L3.9** (A, S3.5) KEPT: `The binding constraint at large $H$ is not time
  and not convergence. It is that the eigenvector's dynamic range grows
  faster than the arithmetic ceiling.` -- rules out the two expected
  constraints before naming the real one; load-bearing contrast.
- **T.L3.10** (A, S3.7) KEPT: `Two caveats we record rather than bury.` --
  epistemic disclosure stance, same register as the \Ldisclosure ledger.
- **T.L3.11** (G, S3.3/S3.4) KEPT: `Overflow is loud.` and heading `The
  checker has to be able to say no` -- house fail-loud / RED-first vocabulary
  (docs/engineering-standards.md).
- **T.L3.12** (A, S4.3) KEPT: `the looseness is not a resolution problem. It
  is the \emph{case routing}` -- substantive diagnosis, each half measured.
- **T.L3.13** (G, S5 heading) KEPT: `Where the remaining gap lives` --
  ordinary idiom; the section literally locates the looseness.
- **T.L3.14** (G, S4.2) KEPT: `the control that kills them` -- ordinary math
  idiom ("this kills the term").

## Reversals

None. No edit had to be reverted; both gates passed on the first post-edit run.
