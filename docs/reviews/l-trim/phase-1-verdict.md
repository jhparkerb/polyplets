> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** Adjudication of
> phase 1 of the L-trim campaign. Read with `phase-1-cuts.md` (the proposals) and
> `phase-1-defense.md` (the verdicts on them).

# Phase 1 — sections. The ruling.

**All nine proposals are applied.** Eight were conceded outright by the
defender, one (P1.L2.1) conceded with a salvage. There were no RETAIN verdicts
to adjudicate and no anchor defects to repair, so the adjudication reduced to
three things: confirming the anchors independently, ruling on the one proposal
the defender asked me to overturn, and correcting the salvage text.

| id | paper | section removed | lines | words |
|---|---|---|---|---|
| P1.L1.1 | L1 | How to read the rest | 14 | ~106 |
| P1.L2.1 | L2 | What is proved | 37 | ~269 |
| P1.L3.1 | L3 | Two things this paper also reports | 18 | ~158 |
| P1.L4.1 | L4 | What is gained, and what is given up | 25 | ~215 |
| P1.L4.2 | L4 | The growth rate, for calibration | 8 | ~61 |
| P1.L4.3 | L4 | One resonance, unexplored | 10 | ~83 |
| P1.L5.1 | L5 | What is proved, and what is measured | 30 | ~226 |
| P1.L5.2 | L5 | The reading | 13 | ~108 |
| P1.L6.1 | L6 | Status of these claims | 25 | ~174 |

Seven of the nine are one defect: a paper that tells the reader what it is
about to prove, proves it, and tells the reader what it proved. The other two —
L5's "What is proved, and what is measured" and L6's "Status of these claims" —
are body-section copies of the paper's own `\Ldisclosure` verification ledger.
The ledger is off limits and is the copy that survives; the duplicate printed
nine pages later is the one that goes. That is the right way round: the ledger
is the disclosure the authorship split actually requires, and a second copy in
the body is not a second disclosure, it is a paraphrase that can drift from the
one that counts.

## Anchors, checked a third time

Every anchor was checked by the cutter, by the defender, and independently here
before anything was applied. All nine open on their sectioning command, close
on a blank line, and are preceded by a blank line, so each deletion leaves
exactly one blank separator and no environment boundary is crossed. Two ranges
define a `\label` — `thm:spine-informal` (L2) and `sec:status` (L6) — and a
tree-wide grep returns only their own definitions.

The trap in L6 is real and is handled: `\label{sec:novelty}` at line 644 is
referenced from the compute-gated draft banner at line 56, which is off limits.
It sits two lines past the anchor's end. The applier stops at 642 and promotes
`\subsection{Novelty}` to `\section{Novelty}`; a cut that ran to 657 would
dangle the banner's reference and fail gate check 2.

## The one I was asked to overturn: P1.L4.2

The defender conceded §"The growth rate, for calibration" but named it the
concession it was least comfortable with, on the ground that it is the only
range of the nine holding a cross-check on the paper's banked data rather than
a restatement — deg ψ_H growing at ≈ 2.7 ≈ √λ is weak evidence that the banked
G_H are not garbage, and this project's standing rule is that evidence
survives.

**Ruling: cut, and this is the single most overturnable ruling in the phase.**

The evidence is not what is being removed. The ten degrees 1, 2, 4, 9, 29, 68,
181, 462, 1254, 3289 are printed in full at L4 line 353 and survive; what goes
is one observation computed from them. The subsection's own closing sentence
disclaims load-bearing status — the theorem takes unboundedness from Northcott,
not from measured growth — and the exclusion boxes rest on the mod-2^61−1
certificates. The data-hygiene check that does real work in this paper is the
H = 11 footnote at 356–361, a different check, untouched.

Against the standing rule I weigh this: what is lost is an *interpretation* of
surviving data, and a reader who wants the ratio can take it from line 353. If
jasonp disagrees, the range comes back with `git show` on this phase's commit —
which is what the per-phase commits are for.

## The salvage, corrected

P1.L2.1's range holds the only sentence in L2 that credits the spine cubic to
the companion paper. `grep -n "companion"` over L2 confirms it: the survivors
at 53, 209, 246 and 643 attribute the diagonal law, the grand form and the
pair weight, and **none of them attributes the cubic**. After an unreplaced cut
a reader would meet W by bare `\begin{definition}` and reasonably take the
cubic for L2's own result. An attribution that disappears is a concrete loss,
so the salvage is warranted.

The defender's draft salvage is not the text that ships. It reads "for any
row-local lattice with drift count b and any prime p | b, the same cubic
appears" — which drops L1's `w ≠ 0` hypothesis. L1's Theorem~\ref{thm:B} says
that if w = 0 the mod-p triangle is trivial in the band, so the sentence as
drafted is false in exactly the case L1 carves out. PROTOCOL's standing defence
is explicit that a hedge scoping a claim is load-bearing, and this campaign is
not going to introduce a false statement while removing true ones.

Two further defects in the draft, both of which would have failed the gate or
confused a reader:

1. It uses `\Wp`, a macro defined at **L1 line 23 and nowhere else** — not in
   `shared/preamble.tex`. In L2 it is an undefined control sequence and the
   compile dies.
2. It refers to L1's `thm:B` by `\ref`, which is a label in another document.
   That is a dangling reference and gate check 2 blocks the commit on it.

Shipped text, appended to the existing §setup paragraph after "…statements
about two power series." (L2 line 211):

```
The spine cubic below is theirs too: the companion paper's universal spine
theorem gives the same curve for every prime $p$ dividing the base, provided
the pair weight is nonzero modulo $p$, after rescaling $t$ by that weight.
Here $p = 3$ and $25 \equiv 1 \pmod 3$, so no rescaling is visible.
```

Both numbers are L2's own: the pair weight 25 is established at L2 lines
244–246 ("its first coefficient 25 … is the pair weight of the companion
paper"), outside the cut, and 25 ≡ 1 mod 3 is already stated at line 576. No
new macro, no cross-document `\ref`, and the hypothesis is carried. Three
wrapped lines and ~52 words replacing 37 lines and ~269 words: net −34 lines.

## Applier residues

1. **L4 line 466** — "the actual content of the lightness claim **in the
   introduction**" → "**in the abstract**". The defender caught this; the
   cutter missed it. After P1.L4.1 there is no lightness claim in the
   introduction, and the claim's surviving home is the abstract at 79–82. Also
   shorter by four characters.
2. **L6 line 643** — `\subsection{Novelty}` → `\section{Novelty}`. Mandatory,
   not cosmetic: Novelty is §Status's only subsection, so left alone it
   re-parents to §k6 and the paper's structure changes silently.
3. **`paper/verify_l_papers.py` is NOT touched.** The cutter proposed rewording
   the stale comment at line 221 ("the paper says ~2.7 per level") in this same
   commit. That file is in `l_trim_gate.sh`'s `FROZEN` list and check 5 fails on
   any byte change, so the proposal would have blocked its own phase. The
   assertion there computes from the script's own `PSI_DEGREES` constant and
   never reads the `.tex`, so nothing breaks; the comment goes stale and is
   listed below for the post-campaign sweep.

## Carried forward, not trimmed

One finding from this phase is not a trim and is logged here because it would
otherwise be lost. **L5's `tab:perim` row 3 states a dir4-by-area exclusion
verdict that nothing in the paper supports** — §`sec:exclusions` and `tab:excl`
test the HV-convex king series and the polyomino control, never the dir4
subclass. The defender found it while chasing whether P1.L5.2's "both being
excluded in the same boxes" clause had a home; it does not, which is why that
clause was not a reason to keep the range. This is a warrant gap in a live
claim, for jasonp or whoever audits L5's claims next. It is not this campaign's
to fix.

Post-campaign, after the frozen-file gate lifts: `verify_l_papers.py:221`'s
comment.
