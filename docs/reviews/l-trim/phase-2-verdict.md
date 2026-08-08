> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** Adjudication of
> phase 2 of the L-trim campaign. Read with `phase-2-cuts.md` and
> `phase-2-defense.md`.

# Phase 2 — results. The ruling.

**All twelve proposals are applied.** Ten were conceded outright, two conceded
with a salvage, none retained. jasonp's scope for this phase was "anything the
cutter can win", and the cutter won twelve and declined to bring anything
against L4 at all.

| id | paper | result | disposition |
|---|---|---|---|
| P2.L1.1 | L1 | `lemma[finiteness]` | removed, **salvaged** |
| P2.L1.2 | L1 | `theorem[degree and leading coefficient]` (`thm:D`) | demoted to prose |
| P2.L1.3 | L1 | `openproblem[onset sharpness in general]` | removed |
| P2.L2.1 | L2 | `remark[the automaton]` | demoted to one sentence |
| P2.L2.2 | L2 | `remark[why one per three]` | removed |
| P2.L2.3 | L2 | `openproblem[is $H$ known?]` | removed |
| P2.L3.1 | L3 | `proposition[existence, and terms are floors]` | removed |
| P2.L3.2 | L3 | `openproblem[the missing concatenation lemma]` | removed |
| P2.L5.1 | L5 | `remark[the square-lattice analogue is classical]` | demoted into §related |
| P2.L5.2 | L5 | `corollary[$\mu$ by shooting]` | demoted, **salvaged** |
| P2.L5.3 | L5 | `openproblem[the arithmetic of $\mu$]` | removed |
| P2.L6.1 | L6 | `openproblem[the higher tips]` | removed |

Two patterns account for ten. Six are a numbered result whose statement is
already made in full as prose elsewhere in the same paper. Four are an
`openproblem` restating, at the back, a wall the paper already described where
it hit it. The one that is neither pattern is L5's `corollary[$\mu$ by
shooting]`, which is a wall-clock benchmark in a corollary environment — the
single place L5 breaks the sorting discipline its own `\Ldisclosure` ledger
imposes. Demoting it is the paper agreeing with itself.

**L4 keeps every result and that is a finding.** All nine are consumed by name
in a later proof or are the paper's scope hedge. The cutter argued out the two
plausible candidates rather than bringing them, and the defender spot-checked
the weaker of the two independently.

## The cutter's argument was wrong on P2.L1.1

The cutter called `lemma[finiteness]` its clearest case, on the ground that
`prop:rational`'s proof "re-derives the only finiteness fact the argument uses".
It does not. That proof re-derives a **degree** bound — "it is
\eqref{eq:elllek} four times" — and `\eqref{eq:elllek}` is $\ell_c \le k_c$,
which bounds a cluster's length by its surplus. It says nothing about how many
cluster types exist at a given surplus, and nothing about a weight being finite.

The conclusion survives, the reasoning does not. `prop:chain` states four
displays built from sums over cluster types and its proof sums a geometric
series in them; for those to be elements of $\Z[[y,z]]$ you need each weight
finite and finitely many types per surplus, and after an unreplaced cut L1 never
says either. That is a step of a proof that stops following, so the environment
goes and one sentence stays. The defender wrote it, deriving the finiteness from
(R) and (U) exactly as the removed proof did; five wrapped lines for fourteen.

This is the second phase running in which a cut was right and its stated reason
was wrong. Both times the defender caught it. That is the argument working as
designed, and it is the reason a phase is two agents and not one.

## Corrections applied to the ledger

1. **Two residue anchors were off by one, both in the same direction.** L1's
   sentence begins "We record" at the end of line **502**, not 503; L2's begins
   "Whether" at the end of line **213**, not 214. An applier trusting the cutter
   would have left half a sentence in two papers. The applier uses
   content-addressed replacement, not line numbers, for every residue.
2. **P2.L5.2's replacement dropped "to arbitrary precision."** The original
   claim is that shooting computes $\mu$ *to arbitrary precision* in
   $O(h_{\max})$ operations; without the scope, the cost has no target and the
   contrast with a precision-capped 700-term extrapolation collapses. A hedge
   that scopes a claim is load-bearing. The defender's three-words-longer text
   ships.
3. **Double blank lines.** A result environment sits between two blanks where
   phase 1's sections sat between a blank and a sectioning command, so a bare
   deletion leaves two. Harmless in LaTeX, but phase 1 established a
   one-separator invariant and the applier keeps it by taking one adjacent blank
   with each removal.
4. **Two stylistic alternates adopted**, both from the defender, both shorter
   and both removing a paired-dash aside — the construction PROTOCOL lists among
   the standing cuts. L2's residue becomes "unchecked against the OEIS … or
   anywhere else" rather than a dash aside; L5's measurement enters §related in
   parentheses rather than as a second dash aside inside the first one's
   sentence.

I declined the defender's third stylistic offer, on P2.L1.2's "Precisely:"
reach-back. Its alternative costs four words and the campaign does not spend
words on a reading that already works.

## The notsquares premise: the cutter was right, for none of its reasons

The cutter deferred L1's `remark[$4,9,25$ are not squares]` claiming
`verify_l_papers.py:495` would go red. I checked and it would not: that assert
is a substring test on the whole file, and "58" is satisfied by the `6558`
inside the six-lattice table at L1:639, with "114" at 714 and "57" at 712. So
the stated reason is false.

The remark must nonetheless stay, for three reasons the ledger never found and
the defender did:

1. **It is referenced twice** — L1:716 and L1:918 — and I confirmed both. Line
   716 sits *inside the remark the cutter called its duplicate*: the sharpness
   remark **derives** its odd-$p$ and $p=2$ statements from this one's closed
   form. It depends on it; it does not repeat it. Cutting dangles two `\ref`s.
2. **The content is disjoint.** It carries an erratum — an earlier version of
   this work published one of the wrong numbers, with the cause named — plus the
   closed form $\Wp(b) = b^3 - b(b+1)/2 + 4$ that `verify_l_papers.py`
   reimplements, and an explicit refusal to present that closed form as a
   result. A correction of record is the least recoverable text in these papers.
3. **It is a hard gate blocker, at check 6 rather than check 3.** `\Wp = 58`
   occurs exactly once in L1, at line 481, inside the remark.

So the deferral stands. No later phase should take this remark, and the reason
is now on the record correctly.

## Two gate checks added this phase

Both were prompted by findings in this phase's argument, and both were
RED-tested against deliberate breakage before being trusted.

**Check 6, `constants`.** `verify_l_papers.py` asserts a paper still prints a
number with `str(d) in src` — substring containment against the whole file.
Measured: delete the L4 line printing all ten ψ-degrees and the check at
`verify_l_papers.py:204` stays green, because "1", "2", "4" and "9" match
anywhere and the rest recur elsewhere in the file. The same shape is at `:448`
and `:495`. That file is frozen for the campaign, so check 6 pins eight
load-bearing literals by exact `grep -F` in the paper that owns each. Four occur
exactly once. A count that drops is permitted — that is a legitimate cut of a
duplicate, and P2.L2.3 takes L2's $H$ series from two occurrences to one — but a
count of zero fails.

**Check 7, `citations`.** The defender's finding, and the largest silent risk in
this phase: dropping the *last* `\cite` of a key produces no undefined citation
anywhere. The key still exists in `refs.bib`, BibTeX omits the entry, the paper
compiles clean, and an attribution disappears with no warning. `christol1980`,
`allouche2003` and `oeis` occur exactly once each in L2, and this phase cuts all
three ranges. Check 7 pins each paper's `\cite`-key set against the pre-campaign
tree at 9cebd90 and fails if any key leaves. PROTOCOL is explicit that
attribution is never redundant, so a lost key is always a failure and never a
trim. Phase 1 lost none; verified retroactively.

## Carried forward

- `verify_l_papers.py`'s three weak substring checks (`:204`, `:448`, `:495`).
  This verdict deferred them post-campaign as frozen; **jasonp overruled that
  between adjudication and application** — repaired under the campaign's one
  documented unfreeze (PROTOCOL records it), RED-first via
  `tests/gate_l_paper_verifier.py`, re-verified against every tree the broken
  verifier had blessed, checksum re-baselined. The stale comment (now `:273`)
  does remain post-campaign.
- L5's `tab:perim` row 3, still unwarranted. Carried from phase 1.
- L5's header comment block names L5 results by numbers that no longer match the
  compiled numbering. Comment hygiene, post-campaign.
- Three single-occurrence constants now sit at L1:481, L4:329 and L5:340. Any
  later phase going near those lines must relocate the literal first, or check 6
  blocks the commit.
