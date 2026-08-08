> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** DEFENDER's
> phase-1 ledger for the L-trim campaign. Verdicts on the CUTTER's proposals; no
> `.tex` file was touched.

# Phase 1 — sections. DEFENDER's verdicts.

Nine proposals, nine rulings: **eight CONCEDE, one CONCEDE WITH SALVAGE, zero
RETAIN.** The salvage is P1.L2.1, where the cutter correctly identified the L1
attribution as the one real loss in the range and correctly priced it at one
sentence rather than thirty-seven lines; I have written the sentence and pinned
the insertion point. **No ANCHOR DEFECTS.** All nine end lines are the blank line
immediately before the next sectioning command, verified line by line; a cut that
stops where the anchor says stops in the right place in every case. Two collateral
corrections to the cutter's ledger, both about what the *applier* does afterward
rather than about the ranges themselves: P1.L4.1 leaves a dangling back-reference
in L4 §transport (line 466, "the lightness claim in the introduction") that must
be repointed, and P1.L4.2's suggested remedy — rewording a comment in
`verify_l_papers.py` — **would break the commit gate**, because that file is in
`l_trim_gate.sh`'s `FROZEN` list and is checksummed by check 5. It must be left
alone.

If you overturn only one, overturn **P1.L4.2** (§"The growth rate, for
calibration"). It is the only range in the nine whose content is a cross-check on
the paper's own banked data rather than a restatement of something said elsewhere:
nothing else in L4 says the ψ-degrees grow at the rate a transfer-matrix frontier
would predict. I concede it because the subsection's own last sentence disclaims
load-bearing status and because the degrees are printed in full eight lines
earlier so a reader can recompute the ratio — but that is the closest thing to a
warrant in the set, and it is the concession I am least comfortable with.

---

## P1.L1.1 — remove §"How to read the rest"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 177–190. Line 177 is
  `\subsection{How to read the rest}`, line 189 is the last prose line
  ("...says how to re-run everything."), line 190 is blank, line 191 is
  `\section{Row-local lattices}`. 14 lines. Line 176 is already blank, so the cut
  leaves exactly one blank line before the section head.
- **collateral check**: confirmed. No `\label`, no `\cite` in 177–190; the range
  is outgoing `\ref`s only, and removing a `\ref` cannot dangle anything. I
  verified the two glosses the cutter says survive: line 525 carries "each new $k$
  turns out to cost exactly two new rational constants" at the head of
  §`sec:grand`, and line 745 carries "converts enumeration into proof" at the head
  of §`sec:machine`. No residue.
- **argument**: The cutter is right that this is `\tableofcontents` in prose,
  seventy-eight lines after the real one, and right that the only two glosses
  carrying information beyond the section titles are restated verbatim at the head
  of the sections they gloss. Nothing in the range is a number, a hedge, a warrant
  or an attribution. The A308359 corollary — the one thing here a reader might
  want signposted — is already named in the prior-art subsection at 173–175, which
  survives.

## P1.L2.1 — remove §"What is proved"

- **verdict**: CONCEDE WITH SALVAGE
- **anchor check**: confirmed lines 142–178. Line 142 is
  `\subsection{What is proved}`, line 177 is `\end{itemize}`, line 178 is blank,
  line 179 is `\subsection{Novelty status}` with `\label{sec:novelty}` on line
  180. 37 lines. The `theorem` and `itemize` environments both open and close
  inside the range; no environment boundary is crossed. **The cut must stop at
  178**: line 180's `sec:novelty` is `\ref`'d from the off-limits `\Ldisclosure`
  ledger (line 65) and from the open problem at 619.
- **collateral check**: confirmed. `\label{thm:spine-informal}` (145) is the only
  label in the range; `grep -rn "thm:spine-informal"` over the tree returns its own
  definition and the cutter's ledger, nothing else. No `\cite`. All outgoing
  `\ref`s (`thm:digit`, `thm:oddspine`, `thm:evenspine`, `thm:activation`,
  `thm:snf`, `thm:deficit2`, `sec:lift`) resolve outside the range.
- **argument**: The theorem at 144–149 is the `\begin{definition}` at 284–286 plus
  the grand form, and the six bullets are the abstract's paragraphs 2–5 with a
  `\ref` each; the `\Ldisclosure` ledger (46–66) names the same six theorems
  individually *and* says what warrants each, which strictly dominates the bullet
  list. The cutter named the one real loss itself — the framing at 151–156, which
  is the only place in L2 that credits the lattice-independent cubic to the
  companion paper. I ran the grep: `grep -n "companion"` in L2 returns line 53
  (the ledger, attributing the *diagonal law* to L1), 154 (inside the range), 209
  (attributing the diagonal law and grand form), 246 and 643. **None of the
  survivors attributes the cubic.** After the cut, §"The spine cubic and the digit
  product" introduces $W$ by bare `\begin{definition}` with no pointer to L1 at
  all, and a reader would reasonably take the cubic for L2's own result. An
  attribution that disappears is a concrete loss, so the range does not go
  unreplaced — but it is worth one sentence, exactly as the cutter priced it, not
  thirty-seven lines, because the warrant for the cubic is internal to L2 via
  $(\star b)$ at 263–270.
- **salvage**:
  - **exact text** (two sentences, appended to the existing paragraph, no new
    blank line):

    ```
    The companion paper also proves the mod-$p$ statement behind this one: for
    any row-local lattice with drift count $b$ and any prime $p \mid b$, the same
    cubic appears with the pair weight as its only scaling. Here we take the
    instance $p = 3$, $w = 25 \bmod 3 = 1$.
    ```

  - **exact insertion point**: `paper/L2-ternary-spine.tex`, §`sec:setup`,
    immediately after "…statements about two power series." at the end of line
    211, inside the same paragraph, before the blank line 212. (This is the
    paragraph that already ends "Both are proved in the companion paper.
    Equation~\eqref{eq:grand} is what makes this paper possible…", so all three
    companion-paper takings end up adjacent.)
  - **delta**: the salvage is 3 wrapped lines and ~50 words, replacing 37 lines
    and ~269 words. Net **−34 lines, ~−219 words**. The claim is checked against
    L1's Theorem~\ref{thm:B} (L1 lines 695–707: "Let $p$ be a prime dividing $b$,
    and let $w := \Wp \bmod p$… the curve does not depend on the lattice") and
    L1 line 737, which gives $p=3$, $w = 25 \bmod 3 = 1$ for the king lattice, so
    the numbers in the salvage are L1's own.

## P1.L3.1 — remove §"Two things this paper also reports"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 158–175. Line 158 is the subsection head, line
  174 ends "…rather than after further effort.", line 175 is blank, line 176 is
  `\section{Preliminaries}`. 18 lines.
- **collateral check**: confirmed, with one refinement. No `\label`, no `\cite`;
  outgoing `\ref`s to `sec:estimate` (432) and `sec:gap` (645), both alive
  elsewhere. Refinement to the cutter's argument, which does not change the
  verdict: the abstract carries the negative result (last paragraph, "the
  over-count is diffuse (median slack $1.144$, maximum $1.222$) and, decisively,
  that it *grows with $n$*") but it does **not** carry the independent strip-spectra
  estimate — the abstract never mentions $\mu_H$ extrapolation. The cutter's "the
  abstract's last two paragraphs say both a third time" is half right.
- **argument**: The refinement above is not a loss, because §`sec:estimate`
  (431–454) carries the estimate in full and with more than the range has: the
  eight-value ladder $9.54,\dots,7.29$, the exponent $p \to 1$, the structural-
  independence sentence verbatim, and two caveats (the under-converged count-ratio
  route, and the $7.41$ vs $6.64$–$6.71$ extrapolation spread) that the range
  omits entirely. Every figure in the range — $7.11$, $31\%$, $152$ recurrences —
  appears with its warrant at 431–454 and 644–695. What goes is advance notice,
  which is not a concrete loss. No residue.

## P1.L4.1 — remove §"What is gained, and what is given up"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 162–186. Line 162 is the subsection head, line
  185 ends "…rather than leave it for a referee.", line 186 is blank, line 187 is
  `\section{Ingredients}`. 25 lines. Three `\paragraph` units, all opened and
  closed inside.
- **collateral check**: **the cutter missed one.** Line 466, in §`sec:transport`,
  reads "That difference is the actual content of the lightness claim **in the
  introduction**, and it is why we think the transport statement is the more
  useful half of this paper." `grep -n "lightness" L4-not-dfinite.tex` returns
  three hits: 164 (inside the range), 466, and 507. After the cut there is no
  lightness claim in the introduction — the claim moves to the abstract, at lines
  79–82 ("The proof uses only integer counts, rationality of each height slice,
  and a strictly increasing bounded family of slice growth constants. It therefore
  applies verbatim to…"). **Applier residue: change "in the introduction" to "in
  the abstract" on line 466.** Same length, no growth. Otherwise confirmed: no
  `\label` in range; `\cite{bmr2002}` survives eleven times over; `sec:transport`
  and `sec:effective` both defined outside.
- **argument**: All three paragraphs are previews. Lightness → §`sec:transport`
  (436–468), which lists the three hypotheses as a numbered enumerate and gives
  the `bmr2002` contrast at greater length. Effectivity → §`sec:effective` opens
  at 420–423 with the same two sentences. Given-up → §"Klazar 2003, and the
  ceiling on our method" (510–530), ending in bold. The $\Q(x)$ hedge is the one
  thing here that must not vanish, and it does not: it survives at the abstract
  (91–93), in bold at 529–530, and in `\begin{openproblem}[extend past $\Q(x)$]`
  (587–590). Three deep after the cut. Conceded.

## P1.L4.2 — remove §"The growth rate, for calibration"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 425–432. Line 423 closes `\end{table}` for
  `tab:irrboxes`, line 424 is blank, line 425 is the subsection head, line 431
  ends "…rather than from any measured growth.", line 432 is blank, line 433 is
  `\section{Transport to other families}`. 8 lines. The cut does not touch the
  table.
- **collateral check**: **the cutter's remedy is wrong and would block the phase
  commit.** The cutter is right that `verify_l_papers.py:221–224` computes from its
  own `PSI_DEGREES` constant and never reads the `.tex`, so gate check 3 (verify)
  stays green — I read the code and confirm it. But it then says "the comment on
  line 221 should be reworded in the same commit", and
  `scripts/l_trim_gate.sh` lists `paper/verify_l_papers.py` in `FROZEN` and check 5
  fails on any byte change to a frozen file. **The applier must NOT touch
  `verify_l_papers.py`.** The comment on line 221 ("the paper says ~2.7 per level")
  goes stale and stays stale until after the campaign; that is a note for the
  post-campaign sweep, not for this commit. No `\label` or `\cite` in the range;
  the single outgoing `\ref{thm:main}` resolves at 121.
- **argument**: This is the weakest of the nine and I say so with the cutter. What
  the range holds that nothing else in L4 holds is a consistency check on the
  banked data — deg $\psi_H$ growing at $\approx 2.7 \approx \sqrt\lambda$ is
  weak evidence that the banked $G_H$ are not garbage, and that is the shape of
  thing the protocol's "evidence survives" defence protects. I concede anyway, on
  two grounds. First, it warrants nothing: the range's own final sentence says the
  theorem takes unboundedness from Northcott and not from measured growth, and the
  exclusion boxes rest on the mod-$2^{61}-1$ certificates, not on the rate.
  Second, the number is reproducible: the ten degrees $1, 2, 4, 9, 29, 68, 181,
  462, 1254, 3289$ are printed at line 353, so a reader who wants the ratio can
  take it. The data-hygiene check that actually does work in this paper is the
  $H=11$ footnote (356–361), which is a different check (shared roots with
  $Q_9Q_{10}$) and survives untouched.

## P1.L4.3 — remove §"One resonance, unexplored"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 568–577. Line 566 ends the preceding
  subsection ("…and we do not write ``first''."), 567 blank, 568 is the subsection
  head, 576 ends "…as far as we know nobody has looked.", 577 is blank, 578 is
  `\section{Open problems}`. 10 lines.
- **collateral check**: confirmed. No `\label`, no `\ref`, no `\cite` in the range
  — Klazar's Theorem 4 is named in bare prose. `klazar2003` survives at `tab:three`
  (line 145) and its own subsection at 510–530 discusses Klazar's Theorem 1 in
  detail, so the attribution is untouched. Nothing in `verify_l_papers.py` reads it.
- **argument**: I looked for the closed-door defence and it is not available: this
  records an approach *not* taken, not one tried and abandoned, so nothing was
  spent that would have to be spent again. It is not an attribution — L2 is neither
  cited nor credited in the range, the mod-3 cubic is referred to anonymously as
  "the king height triangle". It is not prior art, not a collision, and not a
  method borrowed or rejected, so it does not do §related's job. And the paper's
  own §Open problems, four items immediately below, declines to promote it. No
  concrete loss. Conceded.

## P1.L5.1 — remove §"What is proved, and what is measured"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 154–183. Line 154 is the subsection head, line
  182 ends "…than is known about the first.", line 183 is blank, line 184 is
  `\section{The class and its transfer structure}`. 30 lines. Four `\paragraph`
  units, all inside; the `\begin{definition}` above closes at line 152, outside.
- **collateral check**: confirmed. No `\label`, no `\cite`. All eight outgoing
  `\ref`s are also `\ref`'d from the `\Ldisclosure` block, which is off limits and
  unaffected. I checked the Gouyou-Beauchamps/Leroux gate specifically, because the
  draft banner (47–53) makes it a named survival condition: the attribution lives
  at `rem:attr1` (269), `rem:attr2` (952) and §`sec:related` (1120), and
  `grep -n "delestViennot1984"` returns 129, 509, 701, 1145 — none of the five in
  the range. All survive.
- **argument**: The cutter's four-row table is accurate; I checked each row against
  lines 48–78 and the ledger dominates the duplicate in every one, additionally
  naming the Lean theorems, the axiom footprint `[propext, Quot.sound]`, the four
  control arms and the conditionality of `prop:ratio`. I chased the two items in
  the range that are *not* in the ledger and both are covered in the body: "every
  enumerated staircase term is a rigorous floor under $\mu$" is
  `\begin{corollary}[every banked term is a floor]` at 366–368 and the abstract at
  111; "the Prony spectra" as measurement is §"The Prony spectrum" at 830–858,
  which says "every $\lambda_i$ is measured in one solve" and prints negative
  controls required to fail. The closing sentence at 180–182 is word-for-word at
  878–881, inside the stronger statement it belongs to. No residue.

## P1.L5.2 — remove §"The reading"

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 690–702. Line 688 ends §"The nullity law",
  689 blank, 690 is `\subsection{The reading}`, 701 ends "…the tractable
  statistic~\cite{delestViennot1984}.", 702 is blank, 703 is
  `\subsection{Column-convex: solved, and already known}`. 13 lines.
- **collateral check**: confirmed. No `\label`, no `\ref`. `delestViennot1984`
  survives at 129, 509 (`tab:controls`, the algebraic positive-control arm) and
  1145 (§related's Perimeter paragraph), so the bib key and the attribution both
  hold.
- **argument**: Paragraph 1's four facts are `tab:perim` (639–655) read aloud —
  the two verdicts, the two minimal boxes $(2,9)$ and $(4,22)$, and the identical
  area verdicts are all in the table's own columns, and the paragraphs at 657–673
  give the exclusions with their holdout counts. Paragraph 2 is the third arrival
  of "area wild, perimeter tame", after the subtitle, the introduction at 135–138
  (which calls it "the organising fact of this paper") and the abstract. I did find
  one clause with no home elsewhere — "both being excluded in the same boxes",
  comparing the dir4 and HV-convex area exclusions — and it does not save the
  range, because the paper never supports it: §`sec:exclusions` and `tab:excl`
  test only the HV-convex king series and the polyomino control, never the dir4
  subclass, so the clause is an unwarranted assertion rather than a measurement
  that would be lost. `tab:perim` already gives a reader the "changes nothing about
  tractability" reading directly from its two identical area rows.

## P1.L6.1 — remove §"Status of these claims", promoting §"Novelty" to a section

- **verdict**: CONCEDE
- **anchor check**: confirmed lines 618–642. Line 616 ends §`sec:k6` ("…the honest
  reason this paper is not finished."), 617 blank, 618 is
  `\section{Status of these claims}` with `\label{sec:status}` on 619, 641 is the
  "Not computed" `\paragraph`, 642 is blank, 643 is `\subsection{Novelty}` with
  `\label{sec:novelty}` on 644. 25 lines. **The promotion is mandatory, not
  optional**: §Status's only subsection is Novelty, so if 643 stays a
  `\subsection` after its parent section is gone it attaches to §`sec:k6` instead,
  and the paper's structure quietly changes. Line 643 becomes `\section{Novelty}`;
  line 644 is untouched.
- **collateral check**: confirmed, and I re-ran the one that matters.
  `grep -n "sec:novelty" paper/L6-perimeter-gradings.tex` returns exactly two
  lines: 56 (the compute-gated draft banner, off limits) and 644 (the definition).
  644 is outside the anchor. A cut that runs to 657 instead of 642 dangles the
  banner's `\ref` and fails gate check 2. `grep -rn "sec:status"` over the tree
  returns only line 619 and the cutter's own ledger. No `\cite` in range;
  `prop:kct` (163), `tab:maxend` (209) and `sec:k6` (589) all defined outside.
- **argument**: The cutter's four-row table holds up line for line against the
  ledger at 58–78; this is the most literal duplication in the six papers. I chased
  the two items in the range that the ledger does not carry verbatim. (i) "they are
  the reason a pruned enumerator can be called exact rather than heuristic" — the
  body does better at 185–186, where the prune is *validated* ("pruned counts match
  an independent brute-force census cell for cell on both lattices, the prune is
  confirmed to change nothing against an unpruned…") rather than merely asserted.
  (ii) the contrast with the companion paper's proved degree bound and proved sharp
  onset — carried at 141–145 ("the perimeter grading is more universal in
  *content* at the max end while the height grading… is cleaner in *form*, being a
  proved plain polynomial with a proved sharp onset") and again in
  `\begin{openproblem}[prove the degree and the onset]` at 660–666, which adds the
  mechanism ("a single-cell row is a cut"). Three statements go to two. The compute
  gate is untouched: §`sec:k6`, the banner and §`sec:novelty` are all outside.

## For later phases

- L4 line 466: "…and it is why we think the transport statement is the more useful half of this paper" — an editorial ranking of the paper's own halves. Phase 3/4.
- L4 §related line 545–546: "We name these so that this section rests on the arithmetic neighbourhood being mapped, rather than on absence" — restates the emphasised sentence eighteen lines below it. Phase 3.
- L3 line 433: "This subsection is measurement, not proof, and is used nowhere above" — the `\Ldisclosure` ledger already says exactly this about the $7.11$ estimate. Phase 4.
- L2 lines 227–230: "The proposition is worth pausing on, because…" — scaffolding opener on `prop:polya`. Phase 3/4.
- L5 line 630: "It means nothing." — aphoristic closer on §"A worked rejection". Phase 4.
- L5 `tab:perim` row 3: the dir4-by-area verdict has no supporting exclusion data anywhere in the paper; §`sec:exclusions` tests only the HV-convex king series and the polyomino control. Not a trim — a warrant gap, for whoever audits claims next.
- L1 lines 636–688 and L5 lines 427–435 / 610–630: the cutter's own deferrals, correctly deferred; carry them into phases 2 and 3.
- Post-campaign, after the frozen-file gate is lifted: `paper/verify_l_papers.py:221` comment goes stale if P1.L4.2 lands.
