> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** Adjudication of
> phase 5 of the L-trim campaign — the ladder's last rung. Read with
> `phase-5-cuts.md` and `phase-5-defense.md`.

# Phase 5 — words and phrases. The ruling.

**Forty-two of forty-three proposals are applied; P5.L1.6 is RETAINED, the
defender's verdict upheld.** At instance level: forty-five applied, one
retained. It is the campaign's only RETAIN across all five phases, which is
exactly the level a retain should first appear at — this is the one phase whose
edits reword rather than delete, so it is the one phase where a cut can shift a
claim without removing it. Every ruling here was made against the post-phase-4
tree by reading all six papers in full and by a mechanical pass: all forty-five
applied old-texts occur byte-exact, exactly once (`apply-phase-5.py --check`,
exit 0), every replacement is strictly fewer words, and the splice hygiene,
pin, cite-key and no-growth guards all pass. The defender's load-bearing
ledger correction (the `$\nu$` collision) is verified and adopted below; this
adjudication adds one of its own.

| id | paper | target | disposition |
|---|---|---|---|
| P5.L1.1 | L1 | "close enough to be worth stating plainly" trailer | removed |
| P5.L1.2 | L1 | "and the engine of everything after it" | removed |
| P5.L1.3 | L1 | "We state ... honestly" self-appraisal | reworded |
| P5.L1.4 | L1 | `\label{rem:newton}`, defined and never referenced | removed |
| P5.L1.5 | L1 | "turns out to cost" → "costs" | reworded |
| P5.L1.6 | L1 | "--- the load-bearing feature ---" aside | **RETAINED** |
| P5.L1.7 | L1 | "each is ... and each is" anaphora | reworded |
| P5.L1.8 | L1 | "determine $q_k$ outright" | removed |
| P5.L1.9 | L1 | "rather than take it on trust" | removed |
| P5.L1.10 | L1 | remark title "..., and that matters" | removed |
| P5.L1.11 | L1 | remark title "worth stating once" | removed |
| P5.L2.1 | L2 | "worth pausing on, because" + "emphatically" | reworded |
| P5.L2.2 | L2 | "with nothing to spare" | removed |
| P5.L2.3 | L2 | "and no further" after "through $y^{17}$" | removed |
| P5.L2.4 | L2 | "we state them with that provenance ..." | removed |
| P5.L2.5 | L2 | "and it is the easy half" | removed |
| P5.L2.6 | L2 | "genuinely different" | removed |
| P5.L2.7 | L2 | "and the open problem is stated at the end" | removed |
| P5.L2.8 | L2 | "so there is no runaway" | removed |
| P5.L3.1 | L3 | footnote "Worth one sentence because" | reworded |
| P5.L3.2 | L3 | "worth stating ... organising idea of the paper" | removed |
| P5.L3.3 | L3 | "worth separating them, because" → colon | reworded |
| P5.L3.4 | L3 | "rather than merely careful" | removed |
| P5.L3.5 | L3 | "The value of this is that it is" → "It is" | reworded |
| P5.L3.6a | L3 | "decisively" (abstract) | removed |
| P5.L3.6b | L3 | "genuinely uncertain" | removed |
| P5.L3.6c | L3 | "precisely what" | removed |
| P5.L3.6d | L3 | "no effect at all" → "no effect" | removed |
| P5.L4.1 | L4 | "and we should say so before saying what is different" | removed |
| P5.L4.2 | L4 | "as though it were ours" | removed |
| P5.L4.3 | L4 | "worth being exact about why" → colon | reworded |
| P5.L4.4 | L4 | "genuinely different instrument" | removed |
| P5.L5.1 | L5 | "turns out to hold" → "holds" | reworded |
| P5.L5.2 | L5 | "in the first place" after "never" | removed |
| P5.L5.3 | L5 | "--- the whole job is those two" | removed |
| P5.L5.4 | L5 | "both are worth stating because" | reworded |
| P5.L5.5 | L5 | "So $\nu$ is not an artefact ..." (phase-4 carry) | reworded |
| P5.L5.6 | L5 | "and the correction is instructive" | removed |
| P5.L5.7 | L5 | "A free by-product" → "A by-product" | reworded |
| P5.L6.1 | L6 | "quite different creatures" | removed |
| P5.L6.2 | L6 | "--- the law is there and the first two terms hide it" | reworded |
| P5.L6.3 | L6 | "stabilise perfectly well" | removed |
| P5.L6.4 | L6 | paragraph title "A refutation worth recording." | reworded |
| P5.L6.5 | L6 | "and no more" after "exactly as explicit" | removed |
| P5.L6.6 | L6 | "and no better bound exists" after "sharp" | removed |
| P5.L6.7 | L6 | "and resolving it is the sharpest thing here" | removed |

## The retain, ruled here

**P5.L1.6 — RETAINED, and the protocol's removal bias does not reach it.** The
sentence is L1's "Everything happens in $\Q[[y]]$, $y$-adically: no analysis,
no convergence question, and --- the load-bearing feature --- no weight
enumeration, so the proof covers all $k$ at once." The cutter's own argument
concedes the mechanism: the aside ranks the three features, and post-cut the
"so" clause scopes over the whole list by adjacency. I weighed that against the
bias by asking whether the diffused reading is *true*. It is not: exactness and
the absence of convergence questions come from the $y$-adic setting and do not
give all-$k$ coverage — the development's own $k \le 18$ production pinning is
the demonstration, since it consumes weight cards and is per-level for
precisely that reason (one named `native_decide` leaf per weight card, per the
disclosure ledger). The all-$k$ coverage is caused by the third item alone, and
the aside is the sentence's only statement of that attribution. That is a
causal claim redistributed, not a phrase shortened; under this phase's bar an
edit that shifts attribution is out of bounds, not a close call. The defence
also names the concrete reader: whoever re-runs the four moves under a modified
hypothesis — open problem 3's periodic extension asks for exactly that — must
know which feature has to survive for the conclusion to survive. And no
equal-or-shorter rewording keeps the attribution; re-attaching the consequence
costs the span it saves. The bias breaks arguable defences; this one is
decisive. jasonp can overturn by deleting the five words; the applier carries
the sentence as a MUST_SURVIVE guard so an overturn is a deliberate act.

## The other close calls

**P5.L2.8 and P5.L3.6a — the cutter's other two self-flagged items, conceded,
and the concessions are endorsed on the defender's stated grounds, both
re-verified here.** L2.8's dropped "so there is no runaway" is an
interpretation of numbers that survive in the same sentence ("tops out at $3$,
well under the all-$n$ ceiling of $5$"), the exact P1.L4.2 precedent. L3.6a is
the instructive contrast with the retain, and the defender drew it correctly:
dropping "decisively" diffuses an inference over both findings, and there the
diffusion is *accurate* — §gap attributes separately (diffuseness kills
per-type tuning, growth kills the larger window), and the em-dash clause "so
it is not a local defect ..." survives attached to the growth finding. In L1.6
the diffusion misattributes; here it completes. Same test, opposite verdicts,
both right.

**The four hedge-adjacent instances, each re-read in place.** P5.L2.3: "through
$y^{17}$" *is* the dataset bound and claims nothing beyond it; "and no further"
is its restatement, and the ladder's current provenance (derived, with per-rung
"(Originally: ...)" records) is untouched. P5.L6.5: "exactly" precedes the cut
span and survives, closing both directions, and the operative hedge — "this
paper does not call it a closed form" — survives in the same sentence, matching
the disclosure ledger word for word; the applier asserts the post-splice
sentence verbatim. P5.L1.3: the epistemic content is "measured", which
survives, followed by the untouched verification scope (six lattices, two
routes, proved and Lean-checked for $b=3$, measured for $b=1,2$); "honestly" is
the self-appraisal phase 4 removed from L3 (P4.L3.3). P5.L4.2: the surviving
sentence still names the owners, keeps `\cite[Lemma~9]{bmr2002}` in place, and
states the refusal to re-derive; the posture is restated at §related and in the
disclosure ledger, and `bmr2002` stays at 8 occurrences (verified by grep).

**The eight largest edits, spot-checked for meaning preservation** (by tokens
removed: L5.5 −22, L3.2 −13, L2.4 −12, L6.2 −11, L4.1 −10, L1.1 −9, L2.7 −9,
L4.3 −8/L6.7 −8): each surviving claim was traced to its warrant. L5.5 is the
phase-4 carry brought exactly as endorsed — the cut sentence restates
Proposition `prop:split`, proved immediately above, and the splice un-strands
"Measured," into a complete paragraph-opening sentence. L3.2's "in a strict
sense" survives and the strict sense is then stated in full. L2.4's provenance
claim ("derived from the cluster master equation") survives verbatim one clause
earlier. L6.2's aside restates the sentence's own causal clause, and the
two-word spend ("The law" for "It") keeps the predictor's antecedent explicit —
the only edit in the phase that buys words back, and it buys the right thing.
L4.1's "saying so" is performed by the two sentences that follow. L1.1's
closeness claim is made as content in the next paragraph. L2.7's signpost
points four paragraphs down to a titled `openproblem` environment; "No law is
claimed" survives verbatim, matching the `\Ldisclosure` wording. L4.3 and
L6.7's colons deliver what the cut clauses announce.

## Independent checks that mattered

- **All 45 applied old-texts byte-exact and unique**, and every post-splice
  text unique, asserted by `apply-phase-5.py --check` (exit 0). The applier
  carries the strings verbatim — real newlines, real backslashes, no escape
  convention — so the cuts file's `\n` rule and its P5.L5.5 trap cannot reach
  the tree.
- **`rem:newton` re-verified repo-wide before P5.L1.4**: one occurrence
  outside this ledger directory — the definition at L1:385 — across all
  `.tex`, `.py`, `.sh` and `.md`, including `verify_l_papers.py`. Gate check 2
  has nothing to dangle. The applier's old spans all three lines of the remark
  opening, so the neighbours' join (no blank line left) is asserted, and a
  MUST_VANISH guard asserts the string `rem:newton` leaves L1 entirely.
- **Pins located by content, not ledger line numbers**: `\Wp = 58` sits six
  lines below P5.L1.10's title edit with its line byte-identical post-splice;
  the ψ-degree list and the 204-digit floor are nowhere near any edit. All
  eight CONSTANTS of `l_trim_gate.sh` are asserted post-splice by the applier.
- **No `\cite` in any old, and the per-paper cite-key sets are computed from
  the text and asserted unchanged** — `christol1980`/`allouche2003`/`oeis`
  (L2) and `hardyRamanujan1918` (L5), each a sole occurrence, are in no edit's
  neighbourhood.
- **Sentence capitalisation at every paragraph-opening splice** (L1.3, L2.1,
  L3.1, L3.5, L5.5) is asserted twice: statically on the replacement string
  and contextually against the post-splice neighbourhood.
- **Word deltas, measured**: L1 −38, L2 −48, L3 −41, L4 −24, L5 −47, L6 −32;
  −230 in total, 31,569 → 31,339 (−0.73% this phase, −9.8% from baseline).

## Corrections applied to the ledger

1. **P5.L5.5's `$\nu$` / literal-`\n` collision — the defender's finding,
   verified and adopted.** The cuts file's "unescape every literal `\n`"
   convention corrupts this old-text's `$\nu$` (backslash-n-u) into a newline
   plus `u`, after which the anchor matches nothing. Swept all forty-five
   applied old/new strings here: the only backslash-`n` bytes that are not
   tree newlines are that one `$\nu$`. The applier's remedy is stronger than a
   special case — it abolishes the unescaping convention entirely and carries
   every string verbatim, so the class of bug cannot recur.
2. **P5.L1.10 "five lines above the pin" — the defender's advisory
   correction, confirmed**: title at L1:437, `\Wp = 58` at L1:443, six lines.
   Immaterial; the pin's line is byte-identical post-splice.
3. **Both ledgers' word counts are dash-blind** (this adjudication). The cuts
   file's "~235 words" and its per-proposal counts treat "---" as not a word;
   the gate's monotone check and this applier count whitespace-delimited
   tokens, by which the phase removes 230 (with the retained P5.L1.6's 5 not
   taken). No verdict changes — the discrepancy is systematic and small — but
   the phase-4 rule applies: counts in these ledgers are trusted only when
   measured, and the measured figures above are the record.

## Carried forward — the campaign's residual list

The ladder ends here, so this section gathers everything any phase deferred
past the campaign, in one place.

- **L5 `tab:perim` row 3 states a dir4-by-area exclusion verdict nothing in
  L5 warrants** (phase 1): `sec:exclusions` tests the HV-convex king series
  and the polyomino control, never dir4. A warrant gap in a live claim, for
  jasonp or whoever audits L5 next. Not a trim.
- **`verify_l_papers.py`'s stale comment at `:273`** ("the paper says ~2.7
  per level") — post-campaign only; the file is frozen and the comment reads
  no `.tex` (phases 1–2).
- **L5's header comment block** names results by numbers that no longer match
  the compiled numbering — post-campaign comment hygiene (phase 2).
- **`make gates` is red on `gate-citations`**: five citations to ayr_pmin48
  paths from `fb5a0d4`/`f333ec1`, earlier on 2026-08-07; files untouched by
  this campaign (STATE).
- **The other ~30 `tests/gate_*.py` are unaudited** for assertions that
  cannot fail; offered to jasonp as a read-only audit, not yet run (STATE).
- **Five kill-matrix sites remain VACUOUS by design** (`pw.*`,
  `a308.linear-ctrl`): closed integer arithmetic over literals inside the
  frozen verifier, no reachable input, guarded by the freeze checksum;
  recorded, not repaired (STATE).
- **The paper-level gates the banners carry are untouched and outstanding**:
  L6's §k6 placeholder and its four live predictions await the k=6 run (with
  the named consequence if item 3 fails), and L2's and L6's novelty sweeps
  have not been run. These gate submission, not the trim.
- **Every line number in every ledger is stale after this phase.** The three
  single-occurrence pins in particular must be located by content — `\Wp =
  58`, the ψ-degree list, `3.12340450886853853211` — never by a quoted line.
- **Discharged this phase, for the record**: `rem:newton` (phase-3 carry) by
  P5.L1.4, and the stranded-"Measured," rewording (phase-4 carry) by P5.L5.5.
  Nothing deferred by any phase remains unaddressed except as listed above.
