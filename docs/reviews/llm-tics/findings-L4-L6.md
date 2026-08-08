> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** Findings
> ledger for the LLM-tic sweep over L4, L5, L6. Catalog and hard constraints:
> `catalog.md` in this directory. Every candidate noticed is logged, kept or
> not, per the low-bar instruction.

# Findings — L4, L5, L6

| paper | found | fixed | kept |
|-------|-------|-------|------|
| L4-not-dfinite.tex | 12 | 3 | 9 |
| L5-convex-king-animals.tex | 12 | 2 | 10 |
| L6-perimeter-gradings.tex | 11 | 4 | 7 |
| total | 35 | 9 | 26 |

Verifier after all edits: `paper/verify_l_papers.py` — all 326 checks passed,
all 20 RED controls fired. No reversals were needed. Grep for class-B focal
vocabulary (delve/tapestry/robust/pivotal/underscore/...) returned zero hits
in all three papers.

## L4-not-dfinite.tex

**T.L4.1 — D (elegant variation) — FIXED.**
OLD: `whole dichotomy argument, and it dies the instant the coefficients are analytic,`
NEW: `whole dichotomy argument, and it fails the instant the coefficients are analytic,`
The abstract's parallel sentence says "fails the instant"; "dies" was a rotated
synonym for the same event.

**T.L4.2 — G (decorative one-off metaphor) — FIXED.**
OLD: `and the extra variable turns out to be where a proof can get a grip.`
NEW: `and the extra variable turns out to be what makes a proof possible.`

**T.L4.3 — C (cleft padding around a plain verb) — FIXED.**
OLD: `and it is what makes the proof cheap to transport.`
NEW: `and it makes the proof cheap to transport.`
No contrastive emphasis lost; the causal claim is unchanged.

**T.L4.4 — A — KEPT.** "The obstruction is arithmetic rather than topological
or analytic" (abstract). Load-bearing classification; Table `tab:three` is
built on exactly this three-way split.

**T.L4.5 — A — KEPT.** "That is a real limit of the method, not a gap in the
exposition." Load-bearing epistemic contrast: the reader must know the $D_A$
ceiling is intrinsic, not an omission.

**T.L4.6 — A — KEPT.** "It is a data-hygiene flag, not a mathematical
anomaly" (footnote on the excluded $H=11$ entry). Load-bearing: says what kind
of problem the exclusion is.

**T.L4.7 — I (hedge) — KEPT.** "which as far as we can tell is new in this
neighbourhood." Single hedge, required by the paper's own no-"first" policy
(its sec:related); epistemic substance.

**T.L4.8 — G — KEPT.** "Two facts about the family do all the work." Ordinary
math idiom (same family as L6's "Two mechanisms do the work"); not the "heavy
lifting" tic.

**T.L4.9 — C (cleft) — KEPT.** "Strictness is what rules out cancellation
there." The cleft is contrastive: strictness, as opposed to mere
monotonicity, is the needed ingredient.

**T.L4.10 — G — KEPT.** Caption "The shared opening, and where the two
arguments part company." Ordinary idiom, paired deliberately with "shared
opening"; the caption's contrast is the table's content.

**T.L4.11 — G/C — KEPT.** "The lightness of the remaining hypotheses is what
we claim." The cleft carries the theirs/ours contrast set up by "Step 1 is
theirs"; a plain rewrite loses that scope statement.

**T.L4.12 — F (dash aside) — KEPT.** "--- a one-variable
non-P-recursiveness proof looked like it might be arithmetic, and it is not
---". Content-bearing aside (records a checked negative), not rhythm.

## L5-convex-king-animals.tex

**T.L5.1 — C (cleft, with number-agreement clunk) — FIXED.**
OLD: `Two things make this one test rather than a $25\times25$ sweep, and they are what makes the negative rigorous.`
NEW: `Two things make this one test rather than a $25\times25$ sweep, and they are why the negative is rigorous.`

**T.L5.2 — H ("worth noting" family) — FIXED.**
OLD: `Two things about that entry are worth recording, since it carries no derivation.`
NEW: `Two things about that entry are recorded here, since it carries no derivation.`
Plain statement of what the paper then does.

**T.L5.3 — C — KEPT.** Title subtitle "one growth constant serves every class
in between". Transitive "serves" = suffices for; not the "serves as" copula
tic, and the title is high-risk to touch.

**T.L5.4 — D (triad) — KEPT.** "it fattens, shears, then thins" (abstract).
Three real phases: the triad is the three-block decomposition itself.

**T.L5.5 — A — KEPT.** "Convexity is a perimeter lever, not an area lever"
(abstract). The paper's thesis; load-bearing contrast.

**T.L5.6 — A — KEPT.** "the same class is not merely D-finite but algebraic."
Mathematical substance: algebraic is a strict strengthening of D-finite.

**T.L5.7 — G — KEPT.** "which is what stops the join from smuggling in
information." Precise, load-bearing for the injectivity proof: the point is
that no covert side data rides along with the join.

**T.L5.8 — G — KEPT.** "The lemma is two claims bolted together." Mild
metaphor doing real work: the lemma literally conjoins a bijection and a
bound, and only one is used downstream.

**T.L5.9 — A — KEPT.** "It is not: it is Proposition prop:squeeze, and the
four-cone condition is not special." Load-bearing correction of the
bijection mirage; the negation is the finding.

**T.L5.10 — C (cleft) — KEPT.** "A fifth arm --- the null control --- is what
makes any positive verdict in this paper trustworthy." Emphasis on the null
control specifically; contrast with the four gate arms.

**T.L5.11 — C (double-what cleft) — KEPT.** "What (eq:ratio) settles is what
a closed form would have to look like" (and the sibling "What (eq:ratio)
contributes is..."). The plain rewrite would open the sentence with a bare
equation number, which is worse typography; claim unchanged either way.

**T.L5.12 — G — KEPT.** "the staircase animals already carry all of the
exponential entropy" / "carry no exponential" / "bought by the phase split".
Established house vocabulary (carry/weight, cost/buy) used consistently
across the L papers, not one-off decoration.

## L6-perimeter-gradings.tex

**T.L6.1 — G + D (decorative metaphor, elegant variation) — FIXED.**
OLD: `boundary curves of that interval are different creatures:`
NEW: `boundary curves of that interval differ in kind:`
The abstract's parallel phrase is "a different kind of object"; "creatures"
was a rotated decorative variant.

**T.L6.2 — H (scaffolding filler) — FIXED.**
OLD: `coarse label and what is really happening is that each successive prime-power periodicity costs a fixed two units of defect to buy.`
NEW: `coarse label and each successive prime-power periodicity costs a fixed two units of defect.`
"what is really happening is that" deleted whole; "costs ... to buy"
deduplicated. The sec:k6 cross-reference to "periodicities costing two units
of defect apiece" still matches.

**T.L6.3 — A (contrastive negation as setup) — FIXED.**
OLD: `The non-attained columns are not structureless --- they are quadratic in $p$, fitted exactly with holdouts:`
NEW: `The non-attained columns are quadratic in $p$, fitted exactly with holdouts:`
The plain statement already conveys the structure; the negation was
rhetorical wind-up.

**T.L6.4 — C (cleft) — FIXED.**
OLD: `The hexagon is what confirms that this was a general argument and not a fact about boxes.`
NEW: `The hexagon confirms that this was a general argument and not a fact about boxes.`
The load-bearing not-contrast is retained; only the cleft went.

**T.L6.5 — A — KEPT.** "What decides whether a column stabilises at all is
not parity but attainability" (abstract). The finding itself: parity is the
refuted hypothesis, tested and wrong.

**T.L6.6 — A — KEPT.** "It is tempting to call that a parity effect, and it
is wrong, because the square lattice's odd-p rows stabilise." Load-bearing:
records a specific refuted reading with its refuting fact.

**T.L6.7 — A — KEPT.** "All four residue classes stabilise here, not just the
even ones." Real contrast with the king lattice, where the odd classes fail.

**T.L6.8 — A (paragraph pair) — KEPT.** "The square lattice's diamond looks
like an exception." / "And then it is not." The narrative reversal is the
finding (tangent-cone order ideals subsume P(x)); not rhythm.

**T.L6.9 — G (anthropomorphism) — KEPT.** "the two ends want different
indices." Ordinary math informal usage; states the indexing fact.

**T.L6.10 — G — KEPT.** "each was an attractive story and each is dead"
("Doors closed"). "Story"/"door" is the section's established device, used
consistently ("closed door" recurs in sec:tips); plain and load-bearing.

**T.L6.11 — C (cleft) — KEPT.** "k = 6 is what makes it a law or kills it."
Contrastive emphasis on k=6's deciding role; the compute-gate rationale.
(The disclosure block's "they are what make every measured value in this
paper trustworthy" is inside the Ldisclosure block and off-limits regardless.)
