> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** Phase 5 of the
> L-trim campaign: words and phrases within a sentence. CUTTER's proposals, for
> the defender and then adjudication. Read with `PROTOCOL.md` and the four prior
> verdicts; the tree argued against is post-phase-4 (`l-trim` HEAD).

# Phase 5 — words and phrases. The proposals.

The unit is the intra-sentence edit: a word or phrase dropped, or a phrase
reworded to a strictly shorter one, with the sentence's claim identical. This is
the only phase in which rewording is allowed, and the bar applied throughout is
exact meaning-preservation — nothing here weakens, broadens, or re-scopes a
claim. The prey is what the protocol's standing-cuts list predicts at this
grain: self-justifying scaffolding ("worth stating because", "worth pausing
on"), intensifiers ("genuinely", "quite", "emphatically", "perfectly well"),
doubled qualifiers ("sharp and no better bound exists", "exactly as explicit
... and no more"), inflated verbs ("turns out to cost" → "costs"), and
paired-dash asides that restate the clause they hang from.

**43 proposals, 46 instances, ~235 words.** Every paper has proposals; none is
finished at this grain. All 46 OLD strings were verified mechanically against
the current tree (`scratchpad/check_p5.py`, re-runnable): each occurs exactly
once in its file, each NEW is strictly fewer words, no OLD contains a `\cite`,
no pinned constant from `l_trim_gate.sh`'s CONSTANTS block sits inside any OLD,
all eight pins are present in every post-splice file, and a splice-hygiene scan
found no double space and no space-before-punctuation at any boundary. The
three single-occurrence pins (`\Wp = 58` at L1:443, the ψ-degree list at
L4:320, the 204-digit floor's `3.12340450886853853211` at L5:335) are nowhere
near any edit.

## Conventions for the applier

- `OLD` is verbatim and unique in its file; assert count == 1 before writing,
  write nothing on any failure (amendment 3).
- A literal `\n` in OLD/NEW stands for the tree's actual newline at that point;
  unescape before matching. Everything else is byte-exact, backslashes included.
- Empty NEW = pure deletion. Splices may leave a source line longer than the
  file's usual wrap; that is accepted — do not rewrap.
- One edit (`P5.L1.4`) removes a `\label`; no edit touches any other macro,
  environment, `\cite`, or math token. `P5.L1.2`'s OLD and NEW both contain
  `\ref{lem:sep}`, so that reference count is unchanged.

## L1 — 11 proposals, ~43 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L1.1 | `paper/L1-diagonal-law.tex` | `cite the nearest published relative, which is close\nenough to be worth stating plainly.` | `cite the nearest published relative.` | Self-justifying trailer; the relative IS then stated plainly, in the next paragraph. Claim (we cite the nearest relative) identical. |
| P5.L1.2 | `paper/L1-diagonal-law.tex` | `which is Lemma~\ref{lem:sep} and the engine of\neverything after it.` | `which is Lemma~\ref{lem:sep}.` | "Engine of everything after it" is an importance-amplifier; the pointer to the lemma, the load-bearing part, survives. `\ref{lem:sep}` kept. |
| P5.L1.3 | `paper/L1-diagonal-law.tex` | `We state the measured position honestly:` | `The measured position:` | "We state ... honestly" is self-appraisal (phase 4 removed L3's "honestly" closer on the same ground); the position itself follows unchanged. |
| P5.L1.4 | `paper/L1-diagonal-law.tex` | `\label{rem:newton}\n` | | The phase-3/phase-4 carry: label defined at L1:385, referenced nowhere (verified by grep across all six papers and shared/ — sole occurrence is the definition). OLD includes the trailing newline so no blank line is left. |
| P5.L1.5 | `paper/L1-diagonal-law.tex` | `each new $k$ turns out to cost exactly two new rational constants.` | `each new $k$ costs exactly two new rational constants.` | "Turns out to" is discovery-narrative inflation; the costed fact is identical and is proved two sections later. |
| P5.L1.6 | `paper/L1-diagonal-law.tex` | `and --- the load-bearing feature --- no weight enumeration` | `and no weight enumeration` | Paired-dash aside for emphasis; the very next clause ("so the proof covers all $k$ at once") attaches the consequence to this item. Self-conceded weakest in L1 — the aside ranks the three features, which the "so" clause only implies by adjacency. |
| P5.L1.7 | `paper/L1-diagonal-law.tex` | `each is elementary and\neach is exact per order.` | `each is elementary and exact per order.` | Anaphora for rhythm; conjunction states the same two properties of the same four moves. |
| P5.L1.8 | `paper/L1-diagonal-law.tex` | `to determine $q_k$ outright.` | `to determine $q_k$.` | "Determine" already means determine outright. |
| P5.L1.9 | `paper/L1-diagonal-law.tex` | `A reader who wants to check this rather than take it on trust should note` | `A reader who wants to check this should note` | "Rather than take it on trust" is the negation of the clause it follows; the checking instructions are untouched. |
| P5.L1.10 | `paper/L1-diagonal-law.tex` | `\begin{remark}[$4, 9, 25$ are not squares, and that matters]` | `\begin{remark}[$4, 9, 25$ are not squares]` | Title's "and that matters" is an applause cue; the remark's body (the erratum, the recount, the congruence that survives) is what matters and is untouched. The remark itself is phase-2-protected and this touches only its optional title, five lines above the `\Wp = 58` pin. |
| P5.L1.11 | `paper/L1-diagonal-law.tex` | `\begin{remark}[a name collision worth stating once]` | `\begin{remark}[a name collision]` | Same tic as P5.L1.10: "worth stating once" justifies the remark's existence, which the body does better. |

## L2 — 8 proposals, ~48 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L2.1 | `paper/L2-ternary-spine.tex` | `The proposition is worth pausing on, because the leading coefficient of $P_k$ is\n$25^k/k!$ --- emphatically not an integer.` | `The leading coefficient of $P_k$ is $25^k/k!$ --- not an integer.` | "Worth pausing on, because" is lecture scaffolding and "emphatically" an intensifier; the mathematical content ($25^k/k!$, not an integer) is verbatim. |
| P5.L2.2 | `paper/L2-ternary-spine.tex` | `$k+1$ wide, with nothing to spare.` | `$k+1$ wide.` | "Exactly $k+1$ wide" (the sentence's own earlier words) already says there is nothing to spare. |
| P5.L2.3 | `paper/L2-ternary-spine.tex` | `--- verified through $y^{17}$ and no further.` | `--- verified through $y^{17}$.` | "Through $y^{17}$" states the bound; "and no further" restates it. The dataset scope survives verbatim. |
| P5.L2.4 | `paper/L2-ternary-spine.tex` | `master equation, and we state them\nwith that provenance rather than the older one.` | `master equation.` | Meta-commentary about the presentation; the provenance itself ("derived from the cluster master equation") and each rung's "(Originally: ...)" record are untouched. |
| P5.L2.5 | `paper/L2-ternary-spine.tex` | `That is unconditional and it is the easy half.` | `That is unconditional.` | The load-bearing hedge (unconditional, vs the conditional theorems) survives; "the easy half" duplicates the intro's "not hard to explain ... What is harder". Restatement across the seam at phrase grain. |
| P5.L2.6 | `paper/L2-ternary-spine.tex` | `genuinely different where it does not.` | `different where it does not.` | Intensifier. |
| P5.L2.7 | `paper/L2-ternary-spine.tex` | `No law is claimed and the open problem is stated at\nthe end.` | `No law is claimed.` | The second clause is a signpost to something four paragraphs down in the same short section; the disclosure-grade claim ("no law is claimed") survives verbatim, matching the `\Ldisclosure` ledger's wording. |
| P5.L2.8 | `paper/L2-ternary-spine.tex` | `(at $k=8$, $n=17$), so there is no runaway.` | `(at $k=8$, $n=17$).` | "Tops out at $3$, well under the all-$n$ ceiling of $5$" already states, with numbers, what "no runaway" says without them. Self-conceded weaker item: the dropped clause is an interpretation, but of data that survives in the same sentence — the P1.L4.2 precedent. |

## L3 — 6 proposals (9 instances), ~41 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L3.1 | `paper/L3-lambda-bounds.tex` | `\footnote{Worth one sentence because it is easy to get\nbackwards.` | `\footnote{Easy to get backwards.` | "Worth one sentence because" is the tic phase 4 removed as P4.L6.1; the warrant ("easy to get backwards") and the whole rounding explanation survive. |
| P5.L3.2 | `paper/L3-lambda-bounds.tex` | `in a strict sense that is worth stating,\nbecause it is the organising idea of the paper.` | `in a strict sense.` | Self-description ("organising idea of the paper") plus "worth stating" scaffolding; the strict sense is then stated, in full, in the sentences that follow. |
| P5.L3.3 | `paper/L3-lambda-bounds.tex` | `three facts, and it is worth\nseparating them, because only` | `three facts: only` | "Worth separating them, because" announces the separation the colon performs. |
| P5.L3.4 | `paper/L3-lambda-bounds.tex` | `make that sound rather than merely careful.` | `make that sound.` | The sound/careful contrast is rhetorical; the three named things and their arguments are untouched. |
| P5.L3.5 | `paper/L3-lambda-bounds.tex` | `The value of this is that it is \emph{structurally} independent:` | `It is \emph{structurally} independent:` | "The value of this is that" frames a claim the colon-clause then makes concretely (shares no data and no algorithm). |
| P5.L3.6a | `paper/L3-lambda-bounds.tex` | `and, decisively, that it` | `and that it` | Intensifier group. Self-conceded weaker item: "decisively" marks which measurement carries the inference, but the abstract's own "— so it is not a local defect" clause carries that inference explicitly. |
| P5.L3.6b | `paper/L3-lambda-bounds.tex` | `is genuinely uncertain:` | `is uncertain:` | Intensifier; the caveat's scope (Richardson 7.41 vs two-point 6.64–6.71) survives verbatim. |
| P5.L3.6c | `paper/L3-lambda-bounds.tex` | `is precisely what the Klarner--Rivest` | `is what the Klarner--Rivest` | Intensifier; the `\cite` follows later in the sentence and is untouched. |
| P5.L3.6d | `paper/L3-lambda-bounds.tex` | `has \emph{no effect at all} here.` | `has \emph{no effect} here.` | "No effect" is already absolute; "at all" is emphasis inside the `\emph`. |

## L4 — 4 proposals, ~24 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L4.1 | `paper/L4-not-dfinite.tex` | `starts the same way, and we should\nsay so before saying what is different.` | `starts the same way.` | Self-referential scaffolding; the saying-so happens in the next two sentences, which cite BMR by name and survive whole. |
| P5.L4.2 | `paper/L4-not-dfinite.tex` | `we cite it rather\nthan re-deriving it as though it were ours.` | `we cite it rather than re-deriving it.` | "As though it were ours" restates what "cite rather than re-derive" already commits to. The attribution sentence, its `\cite[Lemma~9]{bmr2002}`, and its position are untouched. |
| P5.L4.3 | `paper/L4-not-dfinite.tex` | `cannot\nfollow, and it is worth being exact about why: the step` | `cannot follow: the step` | "Worth being exact about why" announces the exactness the colon delivers; the reason itself (the degree-comparison step dying under analytic coefficients) is verbatim. |
| P5.L4.4 | `paper/L4-not-dfinite.tex` | `--- a genuinely different instrument` | `--- a different instrument` | Intensifier; the aside's content (full-text search could catch an unadvertised Northcott) survives. |

L4 is otherwise the tightest of the six at this grain, consistent with it
keeping every result in phase 2: four small tics and nothing else brought.

## L5 — 7 proposals, ~46 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L5.1 | `paper/L5-convex-king-animals.tex` | `and it turns out to hold for both\nlattices,` | `and it holds for both lattices,` | "Turns out to" inflation; the claim and its downstream consequence clause are identical. |
| P5.L5.2 | `paper/L5-convex-king-animals.tex` | `the area side was never tractable in the first place.` | `the area side was never tractable.` | "Never" already covers "in the first place". |
| P5.L5.3 | `paper/L5-convex-king-animals.tex` | `about the\nindividual classes --- the whole job is those two.` | `about the individual classes.` | Dash aside restating the clause it hangs from ("nothing has to be proved about the individual classes" + the sentence's earlier "trapped between $M$ and $A$"). |
| P5.L5.4 | `paper/L5-convex-king-animals.tex` | `and both are\nworth stating because they are what makes` | `and they are what makes` | "Worth stating because" scaffolding; the substantive claim (these two are what makes the negative rigorous) survives, as do both paragraphs. |
| P5.L5.5 | `paper/L5-convex-king-animals.tex` | `So $\nu$ is not an artefact of an extrapolation: it is the growth constant of an\nexplicitly counted half of the series. Measured,` | `Measured,` | The phase-4 carry, brought as endorsed: the sentence restates Proposition~`prop:split` (proved immediately above — $\lim D_{\mathrm{desc}}(n)^{1/n} = \nu$ for an explicitly counted half) and cutting it alone would strand "Measured," — so this is the rewording phase 4 deferred. Post-splice the paragraph reads "Measured, $\nu = 2.514\dots$ to $153$ trusted digits...", a complete sentence. |
| P5.L5.6 | `paper/L5-convex-king-animals.tex` | `That reading\nis wrong, and the correction is instructive:` | `That reading is wrong:` | "Instructive" is self-appraisal; the correction follows either way, table and all. The erratum content ("That reading is wrong") survives verbatim. |
| P5.L5.7 | `paper/L5-convex-king-animals.tex` | `A free by-product of the split:` | `A by-product of the split:` | Doubled qualifier: a by-product is free by definition, and the sentence goes on to say what it cost (nothing) in numbers — 51 digits to 200. |

## L6 — 7 proposals, ~32 words

| id | file | OLD | NEW | argument |
|---|---|---|---|---|
| P5.L6.1 | `paper/L6-perimeter-gradings.tex` | `are quite different creatures:` | `are different creatures:` | Intensifier; the display that follows shows how different. |
| P5.L6.2 | `paper/L6-perimeter-gradings.tex` | `found nothing --- the law\nis there and the first two terms hide it. It predicts` | `found nothing. The law predicts` | The dash aside restates the sentence's own "which is exactly why scanning ... found nothing". NEW spends two words ("The law" for "It") to keep the predictor's antecedent explicit after the aside goes — net −9 and no ambiguity introduced. |
| P5.L6.3 | `paper/L6-perimeter-gradings.tex` | `odd-$p$ rows\nstabilise perfectly well.` | `odd-$p$ rows stabilise.` | "Perfectly well" adds nothing to "stabilise"; the refutation of the parity story is the fact, which survives. |
| P5.L6.4 | `paper/L6-perimeter-gradings.tex` | `\paragraph{A refutation worth recording.}` | `\paragraph{A refutation.}` | Title-level "worth recording" scaffolding, same tic as P5.L1.10/11. The refutation itself (A120452 wrong at its seventh term) is off this proposal's table entirely. |
| P5.L6.5 | `paper/L6-perimeter-gradings.tex` | `as explicit\nas $P(x)$ itself and no more, and` | `as explicit as $P(x)$ itself, and` | "Exactly as explicit ... and no more" is a doubled qualifier; "exactly" (kept, it precedes the OLD span) already closes both directions. The not-a-closed-form hedge survives verbatim. |
| P5.L6.6 | `paper/L6-perimeter-gradings.tex` | `--- so it is sharp and no better bound exists.` | `--- so it is sharp.` | "Sharp" and "no better bound exists" are the same claim twice; the warrant (equality attained in all 672 cells) survives in the same sentence. |
| P5.L6.7 | `paper/L6-perimeter-gradings.tex` | `an apparent exception, and resolving it is the sharpest thing here:\neach` | `an apparent exception: each` | Abstract self-appraisal ("the sharpest thing here"), the tic phase 4 removed from bodies; the resolution itself — tangent cones, $\phi_2$, one family — follows the colon unchanged. |

## Considered and not brought

- **L6's "costs a fixed two units of defect to buy"** — §k6 names this exact
  sentence as the one that comes out if item 3 fails ("the sentence about
  periodicities costing two units of defect apiece"). A cross-referenced
  sentence inside a compute-gate's failure plan is structure, not prose.
- **L6 §k6 and §novelty in their entirety, both draft banners, every
  `\Ldisclosure`** — off limits, not argued.
- **L2's "striking property" (abstract)** — "striking" is the observation the
  paper exists to explain; in the topic sentence of an abstract that is
  motivation, not padding.
- **L3's "the reassuring measurement here"** — "reassuring" is appraisal, but
  the sentence is the crippling paragraph's topic and every candidate rewording
  either kept the word count or changed what the measurement is claimed to
  reassure about. Declined on the meaning-preservation bar.
- **L3's "roughly $2\log_2(\text{gap})$ sweeps rather than hundreds"** — the
  contrast carries measured scale, not emphasis.
- **L5's "which is worth more here than sharpness"** — records the design
  choice (elementary bound over Hardy–Ramanujan, to keep the squeeze free of
  analytic input). A justified trade-off is a closed door's cousin; it stays.
- **L1's "and they are the reason to believe the rest"** (after
  `tab:machine`) — names the evidentiary role of the two check rows; dropping
  it would leave the rows present but their function unstated.
- **L1's remark title "the statement is exactly sharp"** — "exactly sharp" is
  deliberate (sharp on both branches, neither vacuous), not a doubled
  qualifier.

## Housekeeping, for the defender and the applier

- **`rem:newton` (P5.L1.4)**: the only `\label` touched anywhere. Verified
  here: defined once (L1:385), zero `\ref{rem:newton}` in any of the six
  papers or `shared/`. Gate check 2 cannot fire; no reader loses a target.
- **No `\cite` appears in any OLD**; `christol1980`/`allouche2003`/`oeis`
  (L2's sole-occurrence keys) and `hardyRamanujan1918` (L5's) are in no
  proposal's neighbourhood. Check 7 is untouched by construction.
- **Pins**: all eight CONSTANTS re-grepped in each post-splice file by the
  checker — present. The three single-occurrence pins were located by content
  before proposing (L1:443, L4:320, L5:335 in the current tree) and no edit is
  within its paragraph except P5.L1.10, which edits a remark *title* five
  lines above L1's pin and leaves the pin's line byte-identical.
- **Self-conceded weakest three**, for the defender's attention: P5.L1.6 (the
  aside ranks the three features; adjacency only implies it), P5.L2.8 (drops
  an interpretive clause, though its numbers survive in-sentence), P5.L3.6a
  ("decisively" marks evidential weight in an abstract).
- Verification script: `check_p5.py` (scratchpad, session-local; its edit
  list is byte-identical to this ledger's). Uniqueness, strict shortening,
  splice hygiene and pin survival all pass, 46 of 46.
