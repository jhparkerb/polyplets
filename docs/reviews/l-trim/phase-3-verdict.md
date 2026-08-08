> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** Adjudication of
> phase 3 of the L-trim campaign. Read with `phase-3-cuts.md` and
> `phase-3-defense.md`.

# Phase 3 — paragraphs. The ruling.

**All sixteen proposals are applied.** Sixteen concessions, no retains, three
residues — two proposed by the cutter and endorsed by the defender, one found by
the defender itself. Every excerpt, every claimed restatement home, and all
three residues were independently re-checked here against the post-phase-2 tree
at 20bb8a2 before ruling; the checks that mattered are recorded below. The
defender's seven factual corrections to the cutter all verified; this
adjudication adds three of its own, one of which an applier pasting the cutter's
excerpt would have tripped over.

| id | paper | target | disposition |
|---|---|---|---|
| P3.L1.1 | L1 | intro's three "worth flagging" paragraphs + lead-in | removed |
| P3.L1.2 | L1 | `tab:machine` follow-up on rational coefficients | removed |
| P3.L1.3 | L1 | §a308359's "Two things are worth noting" closer | removed |
| P3.L2.1 | L2 | §intro's "coincidence or shadow" closer | removed |
| P3.L2.2 | L2 | §ladder's conditionality summary | removed |
| P3.L2.3 | L2 | §lift's closing justification | removed, **residue** |
| P3.L3.1 | L3 | "power iteration is not a proof" paragraph | removed |
| P3.L3.2 | L3 | "Before the method that worked" lead-in | removed |
| P3.L3.3 | L3 | "supersedes" paragraph after `tab:compare` | removed |
| P3.L4.1 | L4 | intro's mechanism-sketch paragraph | removed |
| P3.L4.2 | L4 | §transport's closing "By contrast" paragraph | removed |
| P3.L4.3 | L4 | "side effect worth recording" paragraph | removed |
| P3.L5.1 | L5 | "by-product" paragraph in §"What the squeeze settles" | removed, **residue** |
| P3.L5.2 | L5 | second paragraph of the worked PSLQ rejection | removed |
| P3.L6.1 | L6 | intro's "What the two ends give" paragraph | removed, **residue** |
| P3.L6.2 | L6 | "So the two lattices" recap after `tab:sq4min` | removed |

One pattern accounts for most of the phase, as the cutter said it would:
restatement across the seam, at paragraph grain. The independent spot-checks
concentrated on the three residues and on P3.L4.3, the one cut that looks like
a closed door — and there the defender's analysis holds: "the atom" has exactly
one body occurrence in L4, the "earlier root-separation argument" is presented
nowhere in the paper, and nothing downstream consumes that paragraph's version
of all-roots-activity (`tab:irrboxes` needs only $[\Q(\mu_H):\Q] = \deg\psi_H$
from the preceding paragraph; §new-root-content derives every-root-active from
the lowest-terms certificates). A closed door the reader cannot identify is not
a record; the record lives in `results/triangle-structure.md`.

## The residue texts that ship

This verdict, not the cuts or defense files, is the authority on shipped text.

**P3.L2.3** — the removed paragraph is replaced in place, between its two
untouched blank lines, by the single-sentence paragraph:

```
These three are measured, not proved.
```

Verified here: the `\Ldisclosure` ledger (L2:46–66) covers `thm:snf-3power`,
the propositions, the five conditional theorems, `thm:deficit2`, §sleeve and
novelty — and not §lift. This sentence is the only hedge separating the three
displayed congruences from the paper's proved results, and a hedge that scopes
a claim is load-bearing.

**P3.L5.1** — at the first Definition (L5:151), the parenthetical

```
(OEIS \oeis{A225114})
```

becomes

```
(OEIS \oeis{A225114}, the skew shapes with no empty row or column)
```

so the identification a partition-literate reader orients by survives where the
object is defined. The anchor occurs exactly once in L5 (the `tab:fourrungs`
occurrence lacks the "OEIS" prefix). Verified here that $\mu$ is *defined* as
$\lim M(n)^{1/n}$ in `prop:squeeze`'s proof with A225114 as $M(n)$, and the 204
digits sit in `tab:fourrungs` with the stronger reproduces-and-continues
caption; the paragraph's only unreplaced content is a remark about the current
state of a database entry.

**P3.L6.1** — at L6:153, the phrase

```
on the model of the height grading
```

becomes

```
on the model of a companion paper's height grading
```

The defender's own finding, and it is required, not nice: I verified that
`companion` occurs nowhere in L6 outside the removed range, that the first open
problem (L6:636) asserts "The height grading has a proof (polynomial times
exponential, degree $\le k$, sharp onset $2k+1$)" with no statement anywhere in
the post-cut paper of where that proof lives, and that L6:153 becomes the first
occurrence of "height grading" with no antecedent. The `tab:coefftri` caption's
"height-diagonal law" (L6:310) names the law but locates nothing. A claim of
the form "X has a proof" whose proof the reader cannot locate is a hypothesis
that stops being checkable — the protocol's own test — so without the three
words the cut would strand the pointer exactly as the defender said. The anchor
occurs exactly once in L6.

## Corrections applied to the ledger

The defender's seven, each re-verified here rather than taken on trust; all
confirmed, none verdict-changing:

1. **P3.L1.1** — `sec:spine` has two surviving `\ref`s (L1:244, 471), not
   "three-plus"; `sec:polyiamond` has three. Nothing dangles either way.
2. **P3.L2.3** — the second `\S\ref{sec:lift}` reference is in the "individual
   exponents" open problem (L2:566), not the abstract. Both point into the
   surviving section.
3. **P3.L4.2** — `bmr2002` occurs nine times in L4; eight sites survive the
   cut, not the cutter's seven. Confirmed by grep. Check 7 has more margin than
   claimed.
4. **P3.L4.3** — the pin at L4:329 is about fifty lines above the excerpt, not
   seventeen. Untouched either way.
5. **P3.L5.1** — `\oeis{A225114}` occurs at six sites; five survive (L5:151,
   385, 829, 1104, 1119), not the cutter's four.
6. **P3.L6.1** — "lattice-independence failing at the first nontrivial term"
   is not in L6's abstract; its surviving homes are §tips' diamond paragraph
   and the min-end tables. The concession stands on those homes.
7. **P3.L6.2** — the exact string `1, 4, 14, 40, 105` survives at two sites
   (L6:408, 492); the convergence paragraph (L6:439) prints it unspaced.
   Material to anyone auditing by `grep -F`, immaterial to the gate.

Three further corrections from this adjudication:

8. **P3.L6.1's excerpt is not byte-exact, the only one of sixteen.** The cuts
   file prints the paragraph re-wrapped — "more universal / in \emph{content}"
   where the tree has "more / universal in \emph{content}". Measured here: the
   excerpt as printed occurs zero times in L6; whitespace-normalised it occurs
   exactly once, so the cut is unambiguous. The defender's header claim that
   "every anchor excerpt was re-verified verbatim against the post-phase-2
   tree" is false at this one entry. The applier anchors on the tree's actual
   line-wrapping, which is amendment 3 doing the job it exists for.
9. **The cutter's housekeeping counts "two excerpts" carrying a paper's only
   `\ref` to a label; it is one.** P3.L1.2's `\ref{rem:newton}` is the sole
   such site (grep: label at L1:410, ref at L1:764, nothing else). Every other
   `\ref` in every excerpt — `sec:spine`, `sec:polyiamond`, `thm:A`,
   `tab:machine` — has surviving references. One label goes unreferenced this
   phase, not two.
10. **Both ledgers place L3's soundness argument "immediately" after
    P3.L3.1's site.** §exact ("Why the exact phase is sound", L3:290) is two
    subsections later, past the ladder theorem and its table. Immaterial — the
    cut relies on the argument existing, not on its adjacency — recorded so the
    ledger does not overstate what was checked.

Gate accounting, confirmed independently: L3's `6.543` runs fourteen
occurrences, the cut takes two, and the two the verifier reads (abstract
bracket, ladder top rung) are untouched; `\cite{bacher2015}` is not in any
excerpt; no other pinned literal or cite key is within any cut range; L6's
comma-form pin `1, 6, 22, 68, 187, 470, 1106` sits at L6:427 (the defender's
L6:417 is the `&`-separated table row — advisory, untouched either way).

## Carried forward

- **`rem:newton` (L1) is a defined, unreferenced label after this phase.** The
  defender's phase-5 note, endorsed: legal, gate-clean, listed for the phase-5
  sweep.
- **The cutter's phase-4 deferrals**, carried so they are not lost: the middle
  sentences of L4's BMR proof-walkthrough in §related (head and tail stay);
  the duplicated fattens/shears/thins sentence in L5's "Read informally"
  paragraph; L5 §perimeter's dangling "The mirage refines cleanly" opener
  (wording repair, phase 4/5).
- Still standing from earlier phases: L5's `tab:perim` row 3 warrant gap
  (phase 1); L5's stale header comment block and `verify_l_papers.py`'s stale
  comment (post-campaign).
- The three single-occurrence pinned constants (`\Wp = 58` in L1, the ψ-degree
  list in L4, the 204-digit floor in L5) are all untouched this phase; their
  line numbers shift with the cuts and any later phase must locate them by
  content, not by the numbers quoted in older ledgers.
