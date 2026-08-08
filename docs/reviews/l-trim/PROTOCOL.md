> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** This is the
> working agreement for a review campaign, not a result.

# The L-paper trim campaign

Two agents argue about every line of the six L papers. One argues for removal,
one argues for retention, and neither of them touches a `.tex` file. This
directory is where the argument happens.

jasonp's rule, stated at the outset:

> One agent will make an argument to remove sections, results, paragraphs,
> sentences, words (in that order) and the other agent will accept that as a
> principled argument and react accordingly depending on whether it can
> successfully argue to retain the content. In no case shall the document get
> larger except temporarily.

## The two roles

**CUTTER.** Proposes removals, and must argue for each one. "This is verbose"
is not an argument; the argument names what the reader loses and why that is
worth less than the space. The cutter has no quota — it is not trying to hit a
percentage, and a phase in which it proposes nothing for a given paper is a
legitimate outcome.

**DEFENDER.** Reads every proposal as a principled argument made in good faith,
and concedes the ones it cannot beat. Conceding is the expected case, not a
failure; the defender is not the papers' lawyer, it is the reader's. Its
rebuttals name the specific reader who is harmed and the specific thing that
reader can no longer do.

Neither agent edits a manuscript. They read the papers and they write the
ledger files below. Application is a separate, single-writer step, so that two
agents can never hold the same file open.

## The ladder, and what a phase is

Five phases, in this order, each one covering all six papers before the next
begins. **One pass per level — the cutter proposes once, the defender answers
once, the adjudicator rules, the edits land, the phase commits.** No iteration
inside a phase.

| phase | granularity |
|---|---|
| 1 | sections |
| 2 | results — theorems, propositions, lemmas, corollaries, remarks |
| 3 | paragraphs |
| 4 | sentences |
| 5 | words and phrases within a sentence |

Each phase is one commit covering all six papers, so that a mistake can be
located in time and reverted whole. That is the entire reason for the phase
structure and it is why no phase may be split or merged.

## Adjudication

Claude adjudicates, **with a slight bias toward removal**: where the defence is
arguable but not decisive, the content goes. A decisive defence is one that
names a concrete loss — a step of a proof that stops following, a number a
reader cannot reproduce, a hypothesis that stops being checkable. A defence
that appeals to tone, symmetry, completeness-for-its-own-sake, or "a reader
might wonder" is not decisive.

Contested rulings are logged in `phase-N-verdict.md` with the reasoning, so
that jasonp can overturn any one of them by reading a single file.

## What is off limits

These are not open to argument. The cutter may not propose them and a proposal
that reaches them is a bug in the campaign, not a close call.

1. **The disclosure blocks.** `\Ldisclosure` and its per-result verification
   ledger, in every paper. The ledger is required to be per result and not in
   aggregate (`docs/publication-split.md` §1); shortening it *is* aggregating
   it. Compressing a ledger entry is removing a disclosure.
2. **The draft banners**, including L2's novelty-unchecked banner and L6's
   compute-gated banner. Those two banners are the reason those two papers are
   safe to have written at all.
3. **Attribution.** L5's Gouyou-Beauchamps and Leroux citations, in all three
   places (`docs/publication-split.md` §5, N3 collision). Attribution is never
   redundant, no matter how many times the same name appears.
4. **Results that another paper cites.** L1's universal law (cited by P2) and
   L3's λ bracket, 6.543 ≤ λ ≤ 9.3154 (cited by P3). Their statements stay and
   their constants stay exact.
5. **Every file outside the six.** `technical-report.tex` is jasonp's prose and
   is read-only to the machine. `polyplets-report.tex`, `shared/`, and
   `verify_l_papers.py` are out of scope. `scripts/l_trim_gate.sh` enforces
   this with checksums.

## Standing defences the defender should raise, and the cutter should expect

Not immunities — arguments that usually win, drawn from what this project has
already learned about pruning its own prose.

- **Evidence and closed doors survive.** A measurement that warrants a claim,
  and a record of an approach that was tried and failed, are the two things
  that cannot be recovered by re-deriving them later. Prune the claim, not its
  warrant.
- **Exact constants survive verbatim.** λ ≤ 9.3154 is not 9.3153 and is not
  "about 9.32". `verify_l_papers.py` checks these and will block the commit,
  but the argument should never get that far.
- **A hedge that scopes a claim is load-bearing.** "at order and degree ≤ 24 on
  700 terms" is not padding around "not D-finite"; it is the difference between
  a measurement and a false theorem.

And the standing cuts the cutter should look for first:

- **Aphoristic closers.** A section that ends by restating its own point in a
  more memorable way ends one sentence too late. Same for the paired-dash aside
  that exists for rhythm.
- **Restatement across the seam.** A result stated in the introduction, again
  before its proof, and again in the conclusion, is stated twice too often.
- **Scaffolding prose.** "In this section we will", "It is worth noting that",
  "Before proceeding, observe that". The paper is not a lecture.

## Amendments — 2026-08-07, after phase 2's adjudication, before its application

Adopted at jasonp's direction after the first running of this campaign produced
a history that misstated itself: a five-concern commit titled for one of them,
a STATE file describing gate checks that did not yet exist, a verdict deferring
a repair inside the commit that performed it. The branch was rebuilt to remove
those mistakes; these rules exist so it stays removed.

1. **Confidence in a checker is a demonstrated kill, never a count.** "All N
   checks passed" is the fallacy the substring bug lived behind — 318 also
   "passed" while six of twelve corruptions sailed through. A check is trusted
   only if a specific corruption has been watched turning it red: a RED control
   corrupting the computed value for a recomputation check, a manuscript
   mutation for a text check. The kill matrix in `tests/gate_l_paper_verifier.py`
   pairs every check site in `verify_l_papers.py` with its kill; a site nothing
   can turn red is vacuous, and is a finding that triggers the documented
   unfreeze procedure, not a quiet patch. Gates and ledgers quote kill rates;
   a bare pass-count is never cited as confidence.

2. **Commit discipline.** One concern per commit. A phase's ledgers, applier,
   edits and STATE update land in one commit. An out-of-band repair gets its
   own commit, placed before the phase that depends on it. No committed file
   may state something false about the tree it sits in — STATE.md describes
   the commit that contains it, never a hoped-for future.

3. **Anchors are content-addressed.** The verbatim excerpt is the authority;
   line numbers are advisory. An applier asserts on every expected text before
   writing anything, and a single failed assertion writes nothing at all
   (the `apply-phase-1.py` model). The verdict, not the cuts file, is the
   authority on what text ships.

4. **Context hygiene.** The cutter, defender and adjudicator run as fresh
   subagents that read PROTOCOL, the papers and the prior ledgers from disk,
   write only their own ledger file, and return a summary of at most 20 lines.
   The driving session never loads paper contents or the cuts/defense files
   into its own context: it reads verdicts, runs the applier and the gate, and
   commits. STATE.md is the resume state; no agent is kept alive to be
   "resumed by message". Model policy, jasonp's direction of 2026-08-07:
   every campaign agent runs on Fable.

5. **No load-bearing counts in this file.** Numbers that drift as the campaign
   runs — check counts, word totals — live in the ledgers and in STATE.md,
   stamped with the phase at which they were measured.

## Files in this directory

| file | written by | contents |
|---|---|---|
| `PROTOCOL.md` | — | this file, the working agreement |
| `baseline.tsv` | `l_trim_gate.sh baseline` | pre-campaign word counts and frozen-file checksums |
| `phase-N-cuts.md` | CUTTER | numbered proposals, each with file, anchor, verbatim excerpt, argument |
| `phase-N-defense.md` | DEFENDER | one verdict per proposal: CONCEDE or RETAIN, with the argument |
| `phase-N-verdict.md` | Claude | the ruling on each proposal, and what was applied |

A proposal is identified as `PN.paper.k` — `P3.L5.7` is the seventh paragraph
proposal against L5. The identifier is stable across all three files so that a
line in the verdict can be traced back to the argument that produced it.

**The ledger is kept, not swept.** Every `phase-N-*.md` is committed with the
phase whose edits it justifies, and none of them is deleted when the campaign
ends. jasonp's call, and the reason is the campaign's whole purpose: a commit
that removes a paragraph is only auditable if the argument that removed it sits
in the same commit. The trim runs on a branch, so the ledger costs nothing on
`master` until he decides otherwise.

## The commit gate

`scripts/l_trim_gate.sh check N` runs before every phase commit and blocks it
on any of seven failures: a paper that does not compile, an undefined `\ref` or
`\cite` anywhere in a log, a `verify_l_papers.py` failure, a paper that grew in
words since baseline, a frozen file that changed, a pinned load-bearing constant
whose occurrence count drops to zero, or a `\cite` key leaving any paper's set.
Of the first five, the three that can catch a silent error — growth,
frozen-file modification, and dangling references — were RED-tested against
deliberate breakage before the campaign started. Checks 6 and 7 were added
during phase 2's argument, because that argument showed what the first five
could not catch, and were RED-tested the same way before being trusted.

### `verify_l_papers.py` was deliberately unfrozen once, between phase 2's adjudication and its application

The freeze exists so a trim agent cannot quiet a check that is inconvenient.
It was lifted exactly once, by jasonp's instruction, and the reason is recorded
here because an undocumented change to a frozen file is indistinguishable from
the thing the freeze prevents.

Phase 2's argument turned up that the verifier asserted "the manuscript prints
X" with `str(X) in src` — substring containment — at three sites.
`tests/gate_l_paper_verifier.py` measured what that let through: six of twelve
deliberate manuscript corruptions undetected, wrong-digit typos among them. The
file carried thirteen RED controls and none of them was on a text assertion, so
nothing had ever established that those checks could fail.

jasonp's ruling: fix it, and fix it **retroactively**. The takeaway he asked to
have on the record is that **verifiers, tests and linters are engineered to a
higher standard than the content they protect** — a paper with an error is
caught by its checker, and a checker with an error is caught by nobody.

What was done, in order: the mutation gate was written first and failed first;
the three sites were repaired to match a number as a number, a list as a list
and a joint claim as a co-occurrence; the gate went to twelve of twelve; the
repaired verifier was re-run against every tree the broken one had blessed —
pre-campaign `9cebd90`, phase 0, phase 1, and the working tree — and all four
pass; and the frozen checksum was re-baselined to the repaired file. The gate
now runs in `make gates` as `gate-l-paper-verifier`.

The freeze is back on. Any further change to that file needs the same treatment.

Nothing in this campaign is pushed. Publishing is jasonp's call.
