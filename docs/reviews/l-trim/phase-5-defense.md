> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** DEFENDER's
> phase-5 ledger for the L-trim campaign. Verdicts on `phase-5-cuts.md`'s
> forty-three proposals (forty-six instances); no `.tex` file was touched.
> Every OLD was matched byte-exact against the post-phase-4 tree by a
> mechanical pass (`scratchpad/defend_p5.py`, session-local): all forty-six
> occur exactly once in their files, every NEW is strictly fewer words, no OLD
> contains a `\cite`, and all eight pinned literals — re-read from
> `l_trim_gate.sh`'s CONSTANTS block, not from the cuts file's summary of it —
> survive in all six post-splice files. Splice hygiene (double spaces,
> space-before-punctuation, sentence-start capitalisation) was checked at all
> forty-six boundaries: clean.

# Phase 5 — words and phrases. DEFENDER's verdicts.

**Forty-three proposals: forty-two conceded, one retained (P5.L1.6). At
instance level: forty-five conceded, one retained.** No residues. One applier
trap found and disarmed below (P5.L5.5's OLD contains `$\nu$`, which collides
with the ledger's literal-`\n` convention), and one advisory miscount in the
cuts file's housekeeping is corrected. No conceded NEW could be improved at
equal or shorter length; no alternates are supplied.

Phase 5's bar is exact meaning preservation, so every instance got the same
three questions: does the NEW state the same claim, at the same scope, with
the same epistemic status? Is any dropped word a hedge, a dataset bound, an
attribution, or an evidential marker whose loss upgrades or re-scopes what
survives? And does the splice leave the sentence mechanically whole? The one
RETAIN fails the first question: the cut re-scopes a causal claim rather than
shortening it. The cutter's three self-flagged weak items are each ruled on
merits below; two concede and one is the retain.

---

## L1-diagonal-law.tex

### P5.L1.1 — "which is close enough to be worth stating plainly" — CONCEDE

OLD unique; splice ends the sentence at "relative." before the blank line.
The dropped clause claims the relative is close; the very next paragraph
states the closeness as content — "That is the same statement shape as ours
--- fix a defect parameter, get polynomial times exponential" — with both
`\cite`s untouched. Self-justifying trailer whose substance survives in
stronger form. Same claim, same scope.

### P5.L1.2 — "and the engine of everything after it" — CONCEDE

OLD unique; `\ref{lem:sep}` present in both OLD and NEW, so the reference
count is unchanged (grep: `lem:sep` referenced at the sentence and consumed
in the chain-identity proof; nothing dangles). The dropped phrase is an
importance ranking, and the paper demonstrates the lemma's role where it is
used — Proposition~`prop:chain`'s proof opens "By Lemma~\ref{lem:sep} every
animal decomposes \emph{uniquely}". The claim that (L) yields the cut lemma
survives verbatim.

### P5.L1.3 — "We state the measured position honestly:" — CONCEDE

OLD unique; NEW "The measured position:" opens the sentence capitalised,
splice clean. "Honestly" is self-appraisal — phase 4 removed L3's "honestly"
closer (P4.L3.3) on identical ground — and the epistemic content is the word
"measured", which survives, followed by the full verification scope
(six lattices, two routes, proved and Lean-checked for $b=3$, measured for
$b=1,2$) untouched. The hedge stays; only the self-endorsement goes.

### P5.L1.4 — delete `\label{rem:newton}` — CONCEDE

The phase-3/phase-4 carry, discharged. Verified independently, repo-wide:
`grep -rn "rem:newton"` over all `.tex`, `.py`, `.md` and `.sh` files outside
this ledger directory returns exactly one hit — the definition at L1:385.
In particular `verify_l_papers.py` (frozen, reads the papers) contains no
occurrence, in code or comment, so no check can go hunting for it; gate
check 2 counts `\ref`/`\cite`, and no `\ref{rem:newton}` exists anywhere to
dangle. OLD includes the trailing newline, so the remark's `\begin` line
joins directly to its body with no blank line left. A defined, unreferenced
label is dead weight; no reader can lose a target that nothing points to.

### P5.L1.5 — "turns out to cost" → "costs" — CONCEDE

OLD unique. Discovery-narrative inflation; the costed fact is identical and
is proved (Corollary~`cor:two`) two sections later. No scope moves.

### P5.L1.6 — "--- the load-bearing feature ---" — **RETAIN**

The cutter's first self-flagged weak item, and it is the phase's one
meaning shift. The sentence is: "Everything happens in $\Q[[y]]$,
$y$-adically: no analysis, no convergence question, and --- the load-bearing
feature --- no weight enumeration, so the proof covers all $k$ at once."
Post-cut, the "so" clause scopes over the whole three-item list; the original
ties the all-$k$ coverage to the third item alone. Those are different causal
claims, and the diffused one is the less accurate: exactness and the absence
of convergence questions come from the $y$-adic setting, while coverage of
all $k$ at once comes specifically from never enumerating weights — a proof
that consumed weight cards would be per-$k$, which is exactly what the
$k \le 18$ Lean production pinning is (conditional, per-level, one named
leaf per weight card, per the disclosure ledger). The cutter's own argument
concedes the mechanism: "the aside ranks the three features, which the 'so'
clause only implies by adjacency" — and an adjacency implicature is not the
same claim at the same epistemic status. The reader harmed is concrete: the
one who re-runs the four moves under a modified hypothesis — open problem 3's
periodic extension asks for precisely that — and must know which feature has
to survive the modification for the all-$k$ conclusion to survive with it.
No equal-or-shorter rewording preserves the attribution: "the load-bearing
one" saves nothing, and re-attaching the consequence ("which is why the proof
covers all $k$") requires extending the span at no saving. Under the phase's
own rule — any meaning shift, however slight, is a RETAIN — this stays.

### P5.L1.7 — "each is elementary and each is exact per order" — CONCEDE

OLD unique. Anaphora collapsed to a conjunction; the same two properties are
predicated of the same four moves. Nothing rescopes.

### P5.L1.8 — "determine $q_k$ outright" — CONCEDE

OLD unique. "Determine" is already total: $k+1$ values (or two, via
`cor:two`) fix the polynomial, and the sentence's own arithmetic says so.

### P5.L1.9 — "rather than take it on trust" — CONCEDE

OLD unique. The dropped phrase is the negation of "wants to check this";
the checking instructions (guarded `\#print axioms`, the enumerable trusted
surface) are untouched. Same reader, same instruction.

### P5.L1.10 — remark title "…, and that matters" — CONCEDE

OLD unique (the only other bracketed remark titles in L1 are "a name
collision…", "integer values, not integer coefficients", "scope", "the
statement is exactly sharp" — no collision). The title edit is at L1:437 and
the `\Wp = 58` pin at L1:443; the pin's line is byte-identical post-splice,
verified, as is the second L1 pin `\Wp = 57` one line below it. The remark
itself — erratum, recount, the congruence that survives, the closed form —
is phase-2-protected and untouched; "and that matters" is an applause cue
whose substance the body carries ("What survives is the weaker congruence
used in Section~\ref{sec:spine}"). Note: the cuts file says the title sits
"five lines above" the pin; it is six. Advisory, immaterial.

### P5.L1.11 — remark title "worth stating once" — CONCEDE

OLD unique. Same tic as P5.L1.10; the body performs the disambiguation the
title promises, both OEIS references intact.

## L2-ternary-spine.tex

### P5.L2.1 — "worth pausing on… emphatically" — CONCEDE

OLD unique; NEW opens the paragraph capitalised, splice clean. The
mathematical content — $25^k/k!$, not an integer — is verbatim, and the
paragraph's remaining two sentences still tie it to the proposition
(binomial situation, window exactly $k+1$ wide). Scaffolding plus
intensifier; no claim moves.

### P5.L2.2 — "with nothing to spare" — CONCEDE

OLD unique. The sentence's own "exactly $k+1$ wide" already closes both
directions; the dropped phrase is the second statement of the same tightness.

### P5.L2.3 — "and no further" — CONCEDE

OLD unique. "Verified through $y^{17}$" states the dataset bound; "and no
further" restates it. The scope hedge is the bound itself, which survives
verbatim — nothing is upgraded, since "through $y^{17}$" claims nothing
beyond $y^{17}$. This ledger's scoping-qualifier pass looked hardest here:
the surviving sentence still reads as history ("When this line of work
started they were empirical"), and the current provenance (derived, with the
"(Originally: …)" records per rung) is untouched.

### P5.L2.4 — "and we state them with that provenance rather than the older one" — CONCEDE

OLD unique; splice ends the sentence at "master equation." cleanly. Pure
meta-commentary about the presentation; the provenance claim ("now all three
derived from the cluster master equation") and each rung's original-status
record survive verbatim. The disclosure ledger's "none of it is empirical
input any more" keeps its warrant.

### P5.L2.5 — "and it is the easy half" — CONCEDE

OLD unique. The load-bearing word is "unconditional", which survives; the
easy/hard contrast is the intro's ("That is not hard to explain, and
\S\ref{sec:snf3} does it in two lines. What is harder…") — restatement
across the seam at phrase grain, the protocol's named cut.

### P5.L2.6 — "genuinely different" — CONCEDE

OLD unique. Intensifier; the row/column contrast is then exhibited.

### P5.L2.7 — "and the open problem is stated at the end" — CONCEDE

OLD unique. The signpost points four paragraphs down inside the same short
section, where `openproblem[the deficit-$d$ unit formulas]` sits in a titled
environment no reader can miss. The disclosure-grade claim — "No law is
claimed" — survives verbatim and continues to match the `\Ldisclosure`
ledger's "no closed law claimed". Nothing epistemic moves.

### P5.L2.8 — "so there is no runaway" — CONCEDE

The cutter's second self-flagged weak item; ruled on merits, and it
concedes. The dropped clause is an interpretation of numbers that survive in
the same sentence — "tops out at $3$, well under the all-$n$ ceiling of $5$
(at $k=8$, $n=17$)" — and "well under" already carries the reading the
clause performs. The precedent is exact: P1.L4.2 cut an interpretation of
surviving data by adjudication, with the data printed in full. What a reader
loses is a paraphrase; the measurement, its ceiling, and its location all
stay. Splice clean, parenthesis closed by the period.

## L3-lambda-bounds.tex

### P5.L3.1 — footnote "Worth one sentence because" — CONCEDE

OLD unique; NEW opens the footnote capitalised. The tic phase 4 removed as
P4.L6.1, here in footnote position; the warrant ("Easy to get backwards")
and the whole rounding explanation — including the 9.3154-not-9.3153
discipline the gate pins — survive untouched. Both L3 pins verified present
post-splice (`6.543` and `9.3154`, multiple occurrences each).

### P5.L3.2 — "that is worth stating, because it is the organising idea of the paper" — CONCEDE

OLD unique. Self-description; the strict sense is then stated in full
(nothing to trust: no search, no solver, no unrepeatable run; finite object
plus finite check). "In a strict sense" survives, which is the load-bearing
scoping of the word "certificates".

### P5.L3.3 — "and it is worth separating them, because" → colon — CONCEDE

OLD unique; the colon performs the announced separation. The three
paragraphs (1), (2), (3) do the separating; the sentence's surviving halves
state the same tool/object split.

### P5.L3.4 — "rather than merely careful" — CONCEDE

OLD unique. Rhetorical contrast; the three named things (downward rounding,
safe restriction, loud overflow) and their arguments are untouched, and
"sound" is the claim the paragraphs then earn.

### P5.L3.5 — "The value of this is that it is" → "It is" — CONCEDE

OLD unique; NEW opens the paragraph capitalised. The framing clause promises
a value the colon-clause then states concretely ("strip spectra and row-sum
ratios share no data and no algorithm"). "It" resolves to the estimate, the
previous paragraph's subject; no ambiguity introduced. The section's
this-is-measurement banner (its opening sentence) is untouched.

### P5.L3.6a — "and, decisively, that it" — CONCEDE

The cutter's third self-flagged weak item; ruled on merits, and it concedes
— and the contrast with the retained P5.L1.6 is worth stating. Here the
inference marker survives attached to the right clause: "and that it
\emph{grows with $n$} --- so it is not a local defect that a larger window
or per-type tuning could remove". Moreover the diffused attribution is
*accurate*: both findings carry the inference — diffuseness kills per-type
tuning, growth kills the larger window — and §gap's body makes each
attribution separately ("There is no small set of bad types to
hand-engineer"; "A purely \emph{local} over-count would be constant in
$n$"). In L1.6 the diffusion misattributes; here it completes. "Decisively"
is evidential emphasis whose work the em-dash clause does.

### P5.L3.6b — "genuinely uncertain" — CONCEDE

OLD unique. Intensifier; the caveat's scope (Richardson $7.41$ vs two-point
$6.64$–$6.71$, ladder too short) survives verbatim, as does the closing
sentence insulating the rigorous lower bound from all of it.

### P5.L3.6c — "is precisely what" — CONCEDE

OLD unique. Intensifier; the sentence's claim and its
`\cite{klarnerRivest1973}` (later in the same sentence, outside the OLD) are
untouched.

### P5.L3.6d — "no effect at all" → "no effect" — CONCEDE

OLD unique. "No effect" is already absolute, and the evidence sentence
following (identical 185-type closure, identical $9.4022$, all four
orderings) is the claim's warrant and survives. The parenthetical scope
hedge ("In Bui's richer multi-type systems this is a real lever; here it is
not") stays.

## L4-not-dfinite.tex

### P5.L4.1 — "and we should say so before saying what is different" — CONCEDE

OLD unique. Self-referential scaffolding; the saying-so is performed by the
next two sentences, which state the shared opening and cite
`\cite[Lemma~9]{bmr2002}` by name. The attribution posture the sentence
gestures at is enacted, not lost.

### P5.L4.2 — "as though it were ours" — CONCEDE

OLD unique. The attribution-adjacent case, checked hardest in this paper:
the surviving sentence still reads "That step is due to Bousquet-M\'elou and
Rechnitzer~\cite[Lemma~9]{bmr2002} and we cite it rather than re-deriving
it." — ownership stated, citation in place, the refusal to re-derive
explicit. The dropped phrase restates what "cite rather than re-derive"
commits to; borrowed work cannot read as native through it. The same posture
is restated at §related ("Step~1 is theirs and dates to 2002") and in the
disclosure ledger. `bmr2002` count unchanged (8).

### P5.L4.3 — "and it is worth being exact about why" → colon — CONCEDE

OLD unique. The colon delivers the announced exactness; the reason itself —
the degree-comparison step dying under analytic coefficients — is verbatim,
and the bolded scope sentence ("not-D-finite over $\Q(x)$ and does not
extend to $D_A$-finite") survives as the paragraph's close.

### P5.L4.4 — "a genuinely different instrument" — CONCEDE

OLD unique. Intensifier; the aside's content — full-text search could catch
an unadvertised Northcott — survives, and the searches' epistemic banner
("establishes no collision found… cannot establish absence") is untouched.

## L5-convex-king-animals.tex

### P5.L5.1 — "it turns out to hold" → "it holds" — CONCEDE

OLD unique. Same inflation as P5.L1.5; claim and downstream consequence
clause identical.

### P5.L5.2 — "in the first place" — CONCEDE

OLD unique. "Never" already covers it; the wild/tame claim is unchanged.

### P5.L5.3 — "--- the whole job is those two" — CONCEDE

OLD unique. Dash aside restating the sentence's own "trapped between $M$ and
$A$ term by term, so nothing has to be proved about the individual classes".
Restatement inside one sentence; nothing scopes.

### P5.L5.4 — "both are worth stating because" — CONCEDE

OLD unique. The scaffolding goes, the substantive claim ("they are what
makes the negative rigorous") survives with matching grammar, and both
warrant paragraphs (nesting boxes; full rank mod $p$ is rigorous in this
direction) are untouched.

### P5.L5.5 — "So $\nu$ is not an artefact…" → "Measured," — CONCEDE, with an applier correction

The phase-4 carry, brought exactly as the phase-4 verdict endorsed: the
sentence restates Proposition~`prop:split`, proved immediately above ($\lim
D_{\mathrm{desc}}(n)^{1/n} = \nu$ for an explicitly counted half), and phase
4 declined the cut only because it would strand "Measured,". The rewording
un-strands it: post-splice the paragraph reads "Measured, [the quote block's
$\nu$] to $153$ trusted digits by the conservative extrapolation and $242$
by Prony's method" — a complete sentence opening capitalised at a paragraph
break. Conceded on the phase-4 reasoning.

**Applier correction, load-bearing.** This OLD contains `$\nu$` — the bytes
backslash-`n`-`u` — and the cuts file's convention ("a literal `\n` in
OLD/NEW stands for the tree's actual newline; unescape before matching")
is self-contradictory here: a naive unescape corrupts `$\nu$` into a real
newline plus `u`, the corrupted OLD matches nothing, and under amendment 3
the applier writes nothing — fail-closed, but the edit is silently lost or
the phase blocks. The intended newline is the single one between "of an" and
"explicitly"; `$\nu$` is byte-exact. The applier must take this instance's
OLD with exactly that one line break (this ledger's mechanical pass did, and
the OLD then occurs exactly once). No other instance is affected: a sweep of
all forty-six OLD/NEW strings for backslash-`n`-followed-by-lowercase finds
only this one.

### P5.L5.6 — "and the correction is instructive" — CONCEDE

OLD unique. Self-appraisal; the erratum's operative sentence ("That reading
is wrong:") survives verbatim, table and correction following unchanged.
Consistent with the phase-4 standard: the correction of record is the
content, the advertisement of it is not.

### P5.L5.7 — "A free by-product" → "A by-product" — CONCEDE

OLD unique. Doubled qualifier: the sentence itself then prices the by-product
("the same run's $\mu$ jumps from $51$ trusted digits to $200$" — same run,
no extra cost), so "free" is stated twice and survives once, in numbers. The
204/199-digit and 153-digit measurement claims nearby are untouched, and
L5's pin (`3.12340450886853853211`, L5:335) is nowhere near any edit —
verified byte-identical post-splice.

## L6-perimeter-gradings.tex

### P5.L6.1 — "quite different creatures" — CONCEDE

OLD unique. Intensifier; the display that follows (linear vs $\sqrt n$ step
function) is the difference, stated exactly.

### P5.L6.2 — "--- the law is there and the first two terms hide it. It predicts" — CONCEDE

OLD unique. The aside restates the sentence's own causal clause — "have
onsets $2$ and $3$ against the law's $3$ and $4$, which is exactly why
scanning the whole sequence $2,3,6,9,13,18$ found nothing" — with the
deviation and its consequence both already stated. NEW's two-word spend
("The law" for "It") keeps the predictor's antecedent explicit once the
aside goes; the predictions ($24$, $31$) and their §k6 test survive
verbatim. Net shorter, no ambiguity, no scope change.

### P5.L6.3 — "stabilise perfectly well" — CONCEDE

OLD unique. "Perfectly well" adds nothing to "stabilise"; the refutation of
the parity story is the fact, which survives, and the attainability rule
plus its class-by-class check are untouched.

### P5.L6.4 — paragraph title "A refutation worth recording." — CONCEDE

OLD unique. Same title tic as P5.L1.10/11. The refutation itself — A120452
wrong at its seventh term, $23$ for $24$, with the convergence rule and the
wider confirming run — is untouched.

### P5.L6.5 — "and no more" — CONCEDE

OLD unique, and this one is hedge-adjacent so it got the full pass:
"exactly", which precedes the OLD span and survives, closes both directions
of "as explicit as $P(x)$ itself"; and the operative hedge — "this paper
does not call it a closed form" — survives in the same sentence, matching
the disclosure ledger's "It is \emph{not} a closed form" word for word. The
doubled qualifier goes; the ceiling stays.

### P5.L6.6 — "and no better bound exists" — CONCEDE

OLD unique. "Sharp" and "no better bound exists" are one claim twice; the
warrant — equality attained in all $672$ cells — survives in the same
sentence, and L6's pin (`1, 6, 22, 68, 187, 470, 1106`) sits far from any
edit, verified present post-splice at both its comma form and table row.

### P5.L6.7 — "and resolving it is the sharpest thing here" — CONCEDE

OLD unique. Abstract self-appraisal, the tic phase 4 removed from bodies
(P4.L3.4's cousin); the resolution itself — tangent cones, $\phi_2$, one
family — follows the colon unchanged, and the compute-gated banner and §k6
are off the table entirely.

---

## Corrections to the cuts ledger

1. **P5.L5.5's `\n` convention collision** — the substantive one, detailed
   at the entry: OLD contains `$\nu$`, so "unescape every literal `\n`"
   corrupts the anchor. The applier must unescape only the line break
   between "of an" and "explicitly". Verified: this is the sole OLD or NEW
   in the phase containing backslash-`n` before a lowercase letter that is
   not a line break.
2. **P5.L1.10's "five lines above the pin"** — the title is at L1:437, the
   `\Wp = 58` pin at L1:443: six lines. Advisory; the pin's line is
   byte-identical post-splice either way.

The cuts file's remaining housekeeping verified as stated: `rem:newton`
defined once and referenced nowhere (repo-wide grep including
`verify_l_papers.py` and all comments); no `\cite` in any OLD;
`christol1980`/`allouche2003`/`oeis`/`hardyRamanujan1918` nowhere near any
edit; all eight CONSTANTS present in every post-splice file; the three
single-occurrence pins located by content (L1:443, L4:320, L5:335) and
untouched.

## Carried forward

- The `rem:newton` carry is discharged by P5.L1.4.
- Still standing from earlier phases, none touched here: L5's `tab:perim`
  row 3 warrant gap (phase 1); L5's stale header comment block and
  `verify_l_papers.py`'s stale comment at `:273` (post-campaign, file
  frozen).
- If the adjudicator overrules the P5.L1.6 retain, the cut is mechanically
  clean (OLD unique, splice verified here); the disagreement is entirely
  about the "so" clause's scope, and this ledger's entry is the record of
  what the reader loses.
