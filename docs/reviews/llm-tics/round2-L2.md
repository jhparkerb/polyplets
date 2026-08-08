> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.**

# Round 2, phase 1 (pilot): L2-ternary-spine.tex

What I was trying to do: read L2 paragraph by paragraph and re-express each one
as connected prose rather than a stack of separate assertions. The dominant
defect was cadence — short declaratives set as their own sentences or their own
paragraphs ("Everything follows.", "That is unconditional.", "This section is
measurement. No law is claimed.", "Its residue is not $1$.") and paired-dash
asides used to give a sentence a beat. The repair in almost every case was
subordination: the punch line becomes a clause of the sentence it belongs to,
the aside becomes an appositive or a relative clause, and consecutive sentences
about one thing become one sentence with a conjunction or a semicolon. I did not
delete content and did not weaken any hedge; where a short sentence was carrying
an epistemic disclosure I kept the disclosure and gave it a syntactic home
instead of a paragraph of its own. Nothing in math mode, no constant, no
`\cite`/`\ref`/`\label`, no banner, no disclosure block, and no theorem,
proposition or definition statement was touched. 34 paragraphs/passages
rewritten; the file went 3538 → 3588 words (ceiling 3700).

## Abstract

```
triangle's entire integer content sits at the single prime $3$}. Every invariant factor of every leading $N \times N$ block is a
power of $3$, and the number of nontrivial ones is exactly
```
→
```
triangle's entire integer content sits at the single prime $3$}: every
invariant factor of every leading $N \times N$ block is a
power of $3$, and the number of nontrivial ones is exactly
```
The second sentence is the content of the first; a colon says so.

```
We explain both facts from one object. Modulo $3$ the triangle's diagonal
```
→
```
Both facts come from one object. Modulo $3$ the triangle's diagonal
```
Drops the announcing "we explain"; the paper then does it.

```
an Artin--Schreier-like cubic. Everything follows. Writing $n$ in base $3$ as
$\sum_i n_i3^i$, the diagonal polynomials satisfy the digit product
```
→
```
an Artin--Schreier-like cubic, from which everything below follows. Writing $n$
in base $3$ as $\sum_i n_i3^i$, the diagonal polynomials satisfy the digit
product
```
"Everything follows." was the worst single beat in the paper; same claim, now a
relative clause on the cubic it is about.

```
$H$ vanishes identically modulo $3$ until row $\lfloor 3H/2\rfloor$ and is
nonzero there --- an \emph{activation law} whose two boundary cases we evaluate
in closed form by Lagrange--B\"urmann, using the accident that in characteristic
$3$ the relevant correction term vanishes identically. The activation rows are
strictly increasing, which puts the activated columns in echelon position and
gives the Smith normal form count.
```
→
```
$H$ vanishes identically modulo $3$ until row $\lfloor 3H/2\rfloor$, where it is
nonzero; we call this the \emph{activation law} and evaluate its two boundary
cases in closed form by Lagrange--B\"urmann, using the accident that in
characteristic $3$ the relevant correction term vanishes identically. Because
the activation rows are strictly increasing, the activated columns sit in
echelon position, and that gives the Smith normal form count.
```
Dash-aside becomes a named definition; the second sentence's "which" chain
becomes an explicit because-clause.

```
report the exceptions --- \emph{sleeve zeros}, cells where the $3$-adic valuation
spikes above its generic value --- as a complete census for $n \le 40$ with no
```
→
```
report the exceptions, the \emph{sleeve zeros} where the $3$-adic valuation
spikes above its generic value, as a complete census for $n \le 40$ with no
```
Appositive instead of a paired dash; the definition is unchanged.

```
Finally, the cubic lifts: $H^3 - H^2 \equiv 25t \pmod{27}$, with the constant
$25$ being the pair-row weight of the underlying cluster gas, and the level-$3$
```
→
```
Finally the cubic lifts: $H^3 - H^2 \equiv 25t \pmod{27}$, where the constant
$25$ is the pair-row weight of the underlying cluster gas, and the level-$3$
```
"with X being" → a finite verb.

## §1.1 The observation

```
Take the height triangle of the king lattice --- $T(n,H)$, the number of fixed
king animals with $n$ cells and bounding box of height exactly $H$ --- and read
its leading $N \times N$ block as an integer matrix. Compute the Smith normal
form. Every invariant factor is a power of $3$.
```
→
```
Take the height triangle of the king lattice, whose entry $T(n,H)$ counts the
fixed king animals with $n$ cells and bounding box of height exactly $H$, read
its leading $N \times N$ block as an integer matrix, and compute the Smith
normal form: every invariant factor is a power of $3$.
```
Three imperatives and a punch line become one instruction with its result; the
parenthetical definition becomes a relative clause.

```
That is not hard to explain, and \S\ref{sec:snf3} does it in two lines. What is
harder, and what this paper is about, is the second observation: the number of
\emph{nontrivial} invariant factors --- those with exponent $> 0$ --- is exactly
$\lceil (N-1)/3\rceil$:
```
→
```
That is not hard to explain, and \S\ref{sec:snf3} does it in two lines. The
harder fact, and the subject of this paper, is the second observation, that the
number of \emph{nontrivial} invariant factors, those with exponent $> 0$, is
exactly $\lceil (N-1)/3\rceil$:
```
Round 1 kept this as load-bearing (T.L2.4) and the easy/hard contrast is intact;
only the "what is X ... is Y" cleft frame and the dash-aside are gone.

## §1.2 Novelty status

```
\textbf{Unchecked.} This project has run six literature sweeps; they covered the
diagonal law, haruspicy and non-D-finiteness, the staircase squeeze, HV-convex
king animals, and the growth-constant upper bound. \emph{None of them touched
the material in this paper.}
```
→
```
\textbf{Unchecked.} This project has run six literature sweeps, covering the
diagonal law, haruspicy and non-D-finiteness, the staircase squeeze, HV-convex
king animals, and the growth-constant upper bound; \emph{none of them touched
the material in this paper.}
```
Emphasis and disclosure force unchanged; the sweep list is now subordinate to
the sentence whose point is that none of it applies.

```
curves, which is where a cubic of this shape lives. Neither is a claim of
priority. Nothing in this paper is asserted to be new, and the paper should not
be circulated until a sweep in the style of the earlier six has been run.
```
→
```
curves, which is where a cubic of this shape lives. Neither of those amounts to
a claim of priority: nothing in this paper is asserted to be new, and the paper
should not be circulated until a sweep in the style of the earlier six has been
run.
```
The two disclaimers are one thought; the colon makes the second explain the
first. Both assertions survive verbatim in force.

## §2 Setup

```
Both are proved in the companion paper. Equation~\eqref{eq:grand} makes this
paper possible: it turns statements about infinitely many polynomials into
statements about two power series.
The spine cubic below is theirs too: the companion paper's universal spine
theorem gives the same curve for every prime $p$ dividing the base, provided
the pair weight is nonzero modulo $p$, after rescaling $t$ by that weight.
Here $p = 3$ and $25 \equiv 1 \pmod 3$, so no rescaling is visible.
```
→
```
Both are proved in the companion paper, and the present one rests on them
throughout: \eqref{eq:grand} turns statements about infinitely many polynomials
into statements about two power series, while the same paper's universal spine
theorem supplies the cubic below, giving one and the same curve for every prime
$p$ dividing the base, provided the pair weight is nonzero modulo $p$ and $t$ is
rescaled by that weight. Here $p = 3$ and $25 \equiv 1 \pmod 3$, so no rescaling
is visible.
```
Three separate attributions to the companion paper become one sentence that
attributes both borrowings at once. The proviso (nonzero pair weight, rescaled
$t$) is unchanged.

```
The leading coefficient of $P_k$ is $25^k/k!$ --- not an integer. Integer-valuedness without integer
coefficients is the binomial situation, and the window in the proof is exactly
$k+1$ wide.
```
→
```
The leading coefficient of $P_k$ is $25^k/k!$, which is not an integer;
integer-valuedness without integer coefficients is the binomial situation, and
the window used in the proof is exactly $k+1$ wide.
```
Dash-fragment becomes a relative clause.

```
single-defect species, which is the pair weight of the companion paper. Whether
$H$ itself is a known sequence, unchecked against the OEIS~\cite{oeis} or
anywhere else, is one of the things the missing novelty sweep would settle.
```
→
```
single-defect species, which is the pair weight of the companion paper. We have
not checked $H$ against the OEIS~\cite{oeis} or anywhere else, so whether it is
a known sequence is one of the things the missing novelty sweep would settle.
```
The "unchecked" disclosure was buried in an interpolated modifier; it is now the
main clause and says who did not check. Same epistemic content, stated harder.

## §3 The ladder

```
Three coefficient identities carry everything below. When this line of work
started they were empirical --- verified through $y^{17}$. They
are now all three derived from the cluster master equation.
```
→
```
Three coefficient identities carry everything below. When this line of work
started they were empirical, verified through $y^{17}$, and all three are now
derived from the cluster master equation.
```
The then/now contrast is one sentence, so the reader does not have to hold it
across a full stop.

```
  valuation lemma --- every cluster has surplus at least its length, so only the
  bare pair row survives modulo $3$. That is an all-orders statement, and it is
  what makes the cubic \emph{the gas of bare pair rows} rather than a numerical
  coincidence.
```
→
```
  valuation lemma, since every cluster has surplus at least its length, so that
  only the bare pair row survives modulo $3$. Being an all-orders statement, it
  identifies the cubic as \emph{the gas of bare pair rows} rather than a
  numerical coincidence.
```
De-clefts "it is what makes" (round 1 kept the whole item for its epistemic
contrast, which is untouched: gas-of-bare-pair-rows *rather than* coincidence).

## §4 The spine cubic

```
Uniqueness and existence are immediate by Hensel-style coefficient extraction:
the cubic is $W^2(W-1) = t$, and $W = 1 + \dots$ makes each successive
coefficient determined. The cubic is Artin--Schreier-like, and $W$ is algebraic
over $\F_3(t)$ of degree $3$.

It has a rational parametrisation that does all the computational work below:
```
→
```
Existence and uniqueness are immediate by Hensel-style coefficient extraction,
since in the form $W^2(W-1) = t$ the cubic determines each successive
coefficient of $W = 1 + \dots$ in turn. It is Artin--Schreier-like, and $W$ is
algebraic over $\F_3(t)$ of degree $3$. It also has a rational parametrisation
that does all the computational work below:
```
"makes each successive coefficient determined" was a passive contortion; the
one-sentence paragraph joins the paragraph it belongs to.

## §5 The spine

```
$n = \lfloor 3H/2\rfloor$ the \emph{spine} of column $H$: it is the first entry
of that column that is not divisible by $3$. The two parities need separate
```
→
```
$n = \lfloor 3H/2\rfloor$ the \emph{spine} of column $H$; it is the first entry
of that column not divisible by $3$, and the two parities need separate
```
One sentence for the definition and its consequence.

```
The correction factor in \eqref{eq:LB} is identically $1$.
```
→
```
The correction factor in \eqref{eq:LB} is therefore identically $1$.
```
Marks it as the conclusion of the display above rather than a fresh assertion.

```
By \eqref{eq:LB} again --- correction term $1$ --- and \eqref{eq:param},
```
→
```
By \eqref{eq:LB} again, whose correction term is $1$, together with
\eqref{eq:param},
```
Last paired-dash aside in the file.

```
The self-similarity is verified for $m \le 5$ and the congruence
$P_k(3k)\equiv3\pmod 9$ for all $k \le 17$ against the enumerated triangle.
```
→
```
We have verified the self-similarity for $m \le 5$, and the congruence
$P_k(3k)\equiv3\pmod 9$ for all $k \le 17$, against the enumerated triangle.
```
Agentless passive with an ambiguous second conjunct; now says who verified what,
and the commas disambiguate the coordination. Scope unchanged.

## §6 The Smith normal form

```
That is unconditional.
```
→
```
That much is unconditional; counting the nontrivial factors, which is the next
theorem, needs the activation law and with it the ladder of \S\ref{sec:ladder}.
```
The disclosure survives ("unconditional" is exactly what `\Ldisclosure` claims
for Theorem~\ref{thm:snf-3power}) and now connects to the theorem that follows.
The added half-sentence is a statement about this paper's own dependency graph:
Theorem~\ref{thm:snf} invokes Theorem~\ref{thm:activation}, which invokes the
two spine theorems, which use the ladder — the same conditionality the
disclosure block records. See "Judgment calls".

```
Verified directly on the enumerated matrix for every $N \le 36$, reproducing
Table~\ref{tab:snfcount} and the full exponent lists.
```
→
```
We have verified this directly on the enumerated matrix for every $N \le 36$,
reproducing Table~\ref{tab:snfcount} and the full exponent lists.
```
Verbless fragment becomes a sentence; scope ($N \le 36$) unchanged.

## §7 Reading along rows

```
Everything above reads down columns. Reading along rows gives a picture that is
equivalent where it overlaps and different where it does not.
```
→
```
Everything above reads down columns; reading along rows gives a picture that is
equivalent where the two overlap and different where they do not.
```
Antecedent of "it" was ambiguous; the contrast is one sentence.

```
the spine in row $n$ means $n < \lfloor 3H/2\rfloor$, which is the same region
Theorem~\ref{thm:activation} proves zero. The two statements are transposes of
one fact.
```
→
```
the spine in row $n$ means $n < \lfloor 3H/2\rfloor$, the same region
Theorem~\ref{thm:activation} proves zero, so the two statements are transposes
of one fact.
```
Punch line becomes the consequence clause it actually is.

```
earlier: the deficit-$2$ cell. Its residue is not $1$.
```
→
```
earlier, at the deficit-$2$ cell, whose residue is not $1$.
```
Two fragments folded in; the negative ("not $1$") is retained because the point
is that this case breaks the pattern.

## §8 Sleeve zeros

```
This section is measurement. No law is claimed.

A cell to the left of the spine in row $n$ carries a forced deficit
$d := 3k+1-n$. Generically $\vthree(P_k(n)) = d$ exactly --- the cell is a unit
at that valuation --- and a \emph{sleeve zero} is a cell where
$\vthree(P_k(n)) > d$, an excess divisibility with no evident cause.
```
→
```
This section is measurement, and no law is claimed. A cell to the left of the
spine in row $n$ carries a forced deficit $d := 3k+1-n$, and generically
$\vthree(P_k(n)) = d$ exactly, so that the cell is a unit at that valuation; a
\emph{sleeve zero} is a cell where $\vthree(P_k(n)) > d$, an excess divisibility
with no evident cause.
```
Both halves of the required disclosure survive with the same force, in one
sentence at the head of the paragraph it governs rather than as a two-beat
paragraph of its own. Dash-aside becomes a result clause.

```
The census is complete for the project's data, $n \le 40$. It reads valuations
off the enumerated triangle through
$\vthree(P_k(n)) = \vthree(T(n,n-k)) + d$, so it needs no fitted $P_k$ --- which
matters, because the fitted ones stop at $k = 17$ while the proved regime
$n \ge 2k+1$ reaches further.
```
→
```
The census is complete for the project's data, $n \le 40$, and reads valuations
off the enumerated triangle through
$\vthree(P_k(n)) = \vthree(T(n,n-k)) + d$, so that no fitted $P_k$ is needed.
That matters, because the fitted ones stop at $k = 17$ while the proved regime
$n \ge 2k+1$ reaches further.
```
The trailing "--- which matters, because ..." was a run-on with an aside; it is
now its own sentence, which is what it wanted to be.

```
Two observations the final rows add. The $k = 16$ diagonal spikes in three
consecutive rows, $n = 36, 37, 38$, and again at $n = 40$, skipping only
$n = 39$ --- which is itself the only wholly zero-free sleeve after $n = 31$. And
the excess $\vthree - d$ in the new rows tops out at $3$, well under the
```
→
```
The final rows add two observations. The $k = 16$ diagonal spikes in three
consecutive rows, $n = 36, 37, 38$, and again at $n = 40$, skipping only
$n = 39$, which is itself the only wholly zero-free sleeve after $n = 31$; and
the excess $\vthree - d$ in the new rows tops out at $3$, well under the
```
Inverted verbless opener repaired; the "And ..." sentence-opener becomes the
second limb of the pair the paragraph announced.

```
tabulate them, and it is the open remainder of the Witt-vector tower that
\S\ref{sec:lift} starts.
```
→
```
tabulate them, and it is the open remainder of the Witt-vector tower begun in
\S\ref{sec:lift}.
```
De-clefts inside an `openproblem` body; the problem statement is unchanged.

## §9 The 3-adic lift

```
The cubic does not stop at $\F_3$.
```
→
```
The cubic does not stop at $\F_3$, and the two levels above it repeat it:
```
Round 1 kept this line (T.L2.7) as a one-line statement of the section's
content; it now leads grammatically into the list that supplies that content,
instead of standing alone as a paragraph.

```
  $3$-adic levels, with the constant being exactly the pair weight $25$
```
→
```
  $3$-adic levels, the constant being exactly the pair weight $25$
```
```
  level-$3$ correction is again $W$ --- the tower telescopes through the same
```
→
```
  level-$3$ correction is again $W$, so the tower telescopes through the same
```
Dash becomes the causal connective it was standing in for.

## §11 Open problems

```
determinant fixes their sum at $N(N-1)/2$. The individual exponents $e_i(N)$ are
not known. The mod-$3$ rank gives the count but says nothing about the higher
$3$-adic structure; the lifts of \S\ref{sec:lift} are the natural attack.
```
→
```
determinant fixes their sum at $N(N-1)/2$, but the individual exponents
$e_i(N)$ are not known, the mod-$3$ rank giving the count and saying nothing
about the higher $3$-adic structure; the lifts of \S\ref{sec:lift} are the
natural attack.
```
Three stacked assertions become one sentence in which the "but" and the reason
are visible. "Not known" is unchanged.

```
The general spine theorem gives one cubic per prime dividing the drift count.
For polyhexes that is $p = 2$, with the same curve. Does the polyhex triangle
have a mod-$2$ arithmetic as rich as this one --- a digit product, an activation
law, a Smith normal form count? Nothing here forbids it and nobody has looked.
```
→
```
The general spine theorem gives one cubic per prime dividing the drift count,
which for polyhexes is $p = 2$, with the same curve. Does the polyhex triangle
have a mod-$2$ arithmetic as rich as this one, with a digit product, an
activation law and a Smith normal form count? Nothing here forbids it and nobody
has looked.
```
The three items are three real things, so the list stays; only the dash frame
goes. "Nothing here forbids it and nobody has looked" is left exactly as it is —
it is the honest status line of the problem.

## Kept, and why

- **`This half needs only the law, not the ladder.`** (proof of
  Theorem~\ref{thm:activation}) — epistemic contrastive negation of the
  load-bearing kind: it records that the lower half of the activation law is
  unconditional on the ladder, which is exactly the split `\Ldisclosure`
  asserts. Untouched.
- **`These three are measured, not proved.`** (§\ref{sec:lift}) — the required
  disclosure for the lift observations. It is also the one remaining
  short-declarative "punch" in the file, and it should stay one: the whole point
  is that it is unmissable. Untouched.
- **`This section is measurement, and no law is claimed.`** — kept in full
  force, only rejoined to its paragraph.
- **The easy/hard contrast in §1.1** — kept as content ("That is not hard to
  explain ... The harder fact ..."); only the cleft syntax around it changed.
- **`the gas of bare pair rows` rather than a numerical coincidence** — the
  coined term is house vocabulary (results/defect-gas.md) and the contrast is
  epistemic; only the cleft verb changed.
- **`Nothing here forbids it and nobody has looked.`** — a status disclosure,
  and in the register jasonp's own prose uses.
- **`\draftbanner`, `\Ldisclosure`, the header comment block, every theorem /
  proposition / definition statement, every table, all math, all cites/refs/
  labels, the pinned literal `1, 25, 208, 1483, 20688, 130208`** — untouched by
  construction.
- **The `Also found:` item in §\ref{sec:lift}** — a list entry, and list entries
  are allowed to be elliptical; rewriting it would have been fussier than the
  original.

## Judgment calls

1. **The added clause after "That much is unconditional."** This is the only
   place I wrote a sentence that was not in the original: "counting the
   nontrivial factors, which is the next theorem, needs the activation law and
   with it the ladder of \S\ref{sec:ladder}." I believe it is true (that is the
   dependency chain, and `\Ldisclosure` lists Theorem~\ref{thm:snf} as
   conditional on the diagonal law together with the ladder), and it gives the
   orphan sentence something to attach to. But it is a new assertion about the
   paper's logical structure, and if you would rather have no new sentences at
   all, cut everything after the semicolon and the paragraph still reads.
2. **"Both facts come from one object."** I dropped "We explain". The claim is
   now flatly that they have a common source rather than that we will explain
   them from one; in context (the next sentences do the explaining) I judged
   that stronger and equally honest, but it is a shade of difference.
3. **The §2 merge.** Folding three attributions to the companion paper into one
   long sentence is the biggest structural change in the file, and it produces a
   47-word sentence. It reads like a paper to me; it may read like a wall to
   you.
4. **"We have verified" twice.** L2 mostly avoids first person for verification
   claims and uses agentless passives. I changed two of them because verbless
   fragments ("Verified directly on ...") are themselves a machine tell, but
   this makes the paper's voice slightly less uniform than it was. Worth a
   decision before phase 2, since every L paper has these.
5. **Where I flinched:** the proof interiors. Proof prose in L2 is full of very
   short sentences ("Then M.", "Suppose first M.", "Either way M.") and I left
   all of them alone, on the grounds that this is how proofs are written in the
   corpus too. That is a real reason, but it also means the mean-sentence-length
   number cannot move much, and I did not want to inflate proofs to chase it.

## Measurements

```
before  L2-ternary-spine.tex  2289  contrast-neg 0.87  cleft 0.87  serves-as 0.00  dash-aside 1.31  scaffold 0.00  punch 3.93  mean-len 18.3
after   L2-ternary-spine.tex  2345  contrast-neg 0.85  cleft 0.00  serves-as 0.00  dash-aside 0.00  scaffold 0.00  punch 0.43  mean-len 22.3
```

Published-corpus p90 ceilings: contrast-neg 0.35, cleft 0.15, dash-aside 0.30,
punch 0.95. Cleft, dash-aside and punch are inside the band; punch's single
remaining hit is `These three are measured, not proved.` Contrast-neg is at
0.85, i.e. two hits in 2345 prose words, and both are the load-bearing
disclosures listed above — the density metric cannot distinguish them from
rhetorical contrast, and removing them would cost epistemic content, so they
stand. Mean sentence length rose 18.3 → 22.3 but not to 25; see judgment call 5.

Word count 3588 (was 3538; ceiling 3700, gate baseline 4123). Gates after the
edits: `make -C paper L2-ternary-spine.pdf` clean; `paper/verify_l_papers.py`
all 326 checks passed, 20 RED controls all fired; `scripts/l_trim_gate.sh
check 5` "clear to commit".
