> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** Adjudication of
> phase 4 of the L-trim campaign. Read with `phase-4-cuts.md` and
> `phase-4-defense.md`.

# Phase 4 — sentences. The ruling.

**All twenty-two proposals are applied.** Twenty-two concessions, no retains,
no residues. Both agents agreeing on everything makes the adjudication's whole
value the independent re-check, so every excerpt, every claimed surviving home,
the one scope-hedge cut (P4.L2.2), the one check-7-adjacent splice (P4.L5.3)
and every collateral count was re-verified here against the post-phase-3 tree
at 9d05633 before ruling — by reading all six papers in full and by a
mechanical pass over the cuts file (every fenced excerpt matched against its
paper, exact and whitespace-normalised; every long backtick context quotation
likewise). The checks that mattered are recorded below. The defender's four
ledger corrections all verified; this adjudication adds two of its own, one of
which corrects a correction.

| id | paper | target | disposition |
|---|---|---|---|
| P4.L1.1 | L1 | §priorart's "not unheard of" closer | removed |
| P4.L1.2 | L1 | gas-picture paragraph's self-justifying lead-in | removed |
| P4.L1.3 | L1 | §machine's "small computation" topic sentence | removed |
| P4.L1.4 | L1 | §polyiamond's "doing real work" closer | removed |
| P4.L2.1 | L2 | abstract's "telescopes" closer | removed |
| P4.L2.2 | L2 | intro's "Not mostly" emphasis fragment | removed |
| P4.L2.3 | L2 | "The count is the content." | removed |
| P4.L2.4 | L2 | Lagrange–Bürmann "accident" closer | removed |
| P4.L2.5 | L2 | deficit-2 "reusable part" closer | removed |
| P4.L3.1 | L3 | ladder table's "honest parts" topic sentence | removed |
| P4.L3.2 | L3 | "A checker that cannot fail is not a checker." | removed |
| P4.L3.3 | L3 | crippling paragraph's "honestly" closer | removed |
| P4.L3.4 | L3 | two-engine self-appraising closer | removed |
| P4.L3.5 | L3 | §gap's findings-preview sentence | removed |
| P4.L3.6 | L3 | "\emph{Per-type tuning is dead.}" | removed |
| P4.L4.1 | L4 | BMR walkthrough's proof re-derivation | removed |
| P4.L4.2 | L4 | "That is a ceiling on the method." | removed |
| P4.L5.1 | L5 | "Read informally" proof-preview run | removed |
| P4.L5.2 | L5 | dangling "mirage" opener of §perimeter | removed |
| P4.L5.3 | L5 | "entire role" restatement after `lem:stacks` | removed |
| P4.L6.1 | L6 | "worth one sentence" lead-in | removed |
| P4.L6.2 | L6 | A120452 refutation's closing epigram | removed |

Two patterns account for the phase, as the cutter said: aphoristic closers and
scaffolding topic sentences, with the remainder restatement across the seam at
sentence grain. Three proposals are phase-3 deferrals brought as specified
(P4.L4.1, P4.L5.1, P4.L5.2), and each honours the boundary phase 3 drew — the
BMR head and lemma statement stay, the squeeze paragraph's unique
trapped-between-$M$-and-$A$ content stays, and the mirage opener goes as a
removal rather than the rewording phase 3 could not perform.

## The close calls, ruled here

**P4.L2.2 — the one excerpt that is a scope hedge.** "Not mostly; every one, at
every $N$ anyone has computed" scopes the SNF observation as empirical, and a
hedge that scopes a claim is load-bearing — so this got the hardest look of the
phase. It concedes on the defender's ground, which I verified clause by clause:
`thm:snf-3power` (L2 §snf3) proves the scoped statement unconditionally for
every $N$ by the two-line determinant argument, and the very next line of the
intro says so ("§snf3 does it in two lines"), so the surviving unqualified
sentence is *proved*, not overstated — the protocol's test is the difference
between a measurement and a false theorem, and here there is no false theorem
to prevent. The empirical dataset size survives at both of its working homes,
verified: "Verified directly on the enumerated matrix for every $N \le 36$"
(L2:425) and the `\Ldisclosure` ledger's "every $N \le 36$ for the Smith
normal form". Removed.

**P4.L3.1 — the cutter's self-conceded weakest.** The question is whether the
announcement "these two features are the honest parts" is load-bearing over the
two feature sentences themselves. It is not: feature 1 arrives with "because a
certificate states what is \emph{proved}" and feature 2 with "Clamping can only
lower the certified value; it can never falsify it" — the disclosure framing is
re-supplied at each feature, in stronger form. The content phase 3's cutter
called decisive when it declined to bring this paragraph — a reader squaring
the certified $2.4142135$ against $\mu_2 = 2.4142136$, without which the first
rung reads as a typo — survives whole; I re-read the post-cut paragraph and it
opens on exactly that comparison. Under the protocol's standard, a defence of
the announcement alone appeals to reading posture, not to a number, a proof
step, or a checkable hypothesis. Removed, with the bias doing its job.

**P4.L5.3 — the check-7-adjacent splice.** Verified by grep:
`hardyRamanujan1918` is that key's sole occurrence in L5 (count: 1), so a
sloppy splice here is the exact failure mode gate check 7 exists for. The
excerpt boundary ends at "discarded." and the citation opens the *following*
sentence; the applier pins the boundary by including the surviving "Hardy and
/ Ramanujan~\cite{hardyRamanujan1918} would give" in both the matched and the
replacement text, so the splice cannot land anywhere else and the key's count
is asserted unchanged after every edit. The role statement's surviving home
was verified verbatim at L5:264–266 ("The lemma is two claims bolted together
... Only the second is used downstream").

## Independent checks that mattered

- **All 22 excerpts byte-exact and unique**, re-measured mechanically here
  (exact count 1 and whitespace-normalised count 1, all 22) — the defender's
  headline claim holds.
- **P4.L4.1's run contains no `\cite`**: `bmr2002` occurs 8 times in L4, zero
  in the excerpt; the head's "(from~[4])"/"(from~[6])" are quoted prose. The
  kept statement ends "...has only finitely many limit points", so the lemma's
  conclusion survives with its statement; the mechanism row of
  `tab:sidebyside` (L4:444) carries the compressed proof shape.
- **P4.L2.5 removes an unverified reach claim** ("applies to any congruence
  for a family linear in $(n,k)$") — checked that neither of L2's open
  problems consumes the method's generality; this cut tightens the banner
  discipline rather than testing it.
- **Ref accounting, all by grep**: `cor:two` 3→2 (survivors at L1:694, 697,
  both in §machine), `thm:A` 16→15, `lem:stacks` 11→10, `thm:deficit2` 3→3
  (none in any excerpt). No label's reference count reaches zero; no label is
  defined in any excerpt. The applier additionally asserts, dynamically, that
  no `\ref` key present before the edits is absent after.
- **Pins**: all eight of `l_trim_gate.sh`'s CONSTANTS re-read from the script
  itself and grepped in the post-cut text by the applier. L3's `6.543` (12
  occurrences) and `9.3154` sit in P4.L3.5's *paragraph* but in its untouched
  first sentence; the excerpt has no numerals. L6's septuple survives at both
  its comma form (L6:419) and its table row.
- **Sole-warrant sweep**: for each cut sentence, the claim it interprets was
  traced to a surviving warrant — every one named in the ledgers checked out,
  and none of the 22 is the only statement of a bound, precision, dataset
  size, or machine context.

## Corrections applied to the ledger

The defender's four, each re-verified here rather than taken on trust:

1. **P4.L6.2 / `\oeis` macro count** — confirmed by grep: the macro occurs
   once in L6 (L6:506); L6:507 and L6:511 are bare text "A120452". The
   cutter's "occurs twice" is wrong as written; safety conclusion unaffected.
2. **P4.L3.1 attribution** — confirmed against `phase-3-cuts.md`: the
   2.4142135/2.4142136 argument sits in the phase-3 *cutter's*
   considered-and-not-brought list; the phase-3 defender never ruled on that
   paragraph.
3. **Re-wrapped context quotations** — confirmed in direction; corrected in
   count below (correction 5).
4. **Advisory line numbers off by one** — both confirmed: the no-first-claim
   sentence is at L1:132, the trusted-not-certified sentence at L3:386–387.

Two further corrections from this adjudication:

5. **The defender's correction 3 understates its own finding.** It names
   three context quotations as re-wrapped relative to the tree. Measured
   mechanically here: **twenty** of the cuts file's long backtick context
   quotations wrap differently from the tree (each matching exactly once when
   whitespace-normalised), and P4.L1.1's preceding context carries a literal
   "..." elision, so as printed it does not match even normalised. Re-wrapping
   is the cuts file's default for context quotes, not a three-entry exception.
   The applier consequence is unchanged — excerpts are the anchor authority
   and all 22 are byte-exact — but a correction that itself needed correcting
   is worth the line: counts in these ledgers are trusted only when measured.
6. **P4.L1.2's defence miscounts a sentence.** The defender places "Then
   Theorem~\ref{thm:C} says exactly that..." as "the surviving paragraph's
   own third sentence"; it is the surviving paragraph's *second* sentence
   (third of the pre-cut paragraph, which is what the cutter correctly
   wrote). Immaterial to the concession — the tie to Theorem C survives
   either way.

## Carried forward

- **The cutter's phase-5 flag, endorsed**: L5's "So $\nu$ is not an artefact
  of an extrapolation..." is interpretive, but cutting it strands the
  following "Measured," fragment without a subject; the repair is a rewording
  and belongs to phase 5.
- **`rem:newton` (L1)** remains a defined, unreferenced label — phase-3
  carry, listed for the phase-5 sweep.
- Still standing from earlier phases: L5's `tab:perim` row 3 warrant gap
  (phase 1); L5's stale header comment block and `verify_l_papers.py`'s stale
  comment at `:273` (post-campaign, file frozen).
- The three single-occurrence pinned constants (`\Wp = 58` in L1, the
  ψ-degree list in L4, the 204-digit floor in L5) are untouched this phase;
  their line numbers shift again with these cuts and any later phase must
  locate them by content.
- L2's cite-carrier paragraphs (`christol1980`/`allouche2003`/`oeis` sole
  sites) remain off the table on gate grounds.
