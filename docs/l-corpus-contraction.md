> **NOTE: authored by Claude at jasonp's direction, 2026-08-23.** The record of
> the L-paper contraction, executed the same day it was proposed. It supersedes
> the per-paper rows of `docs/publication-split.md` §3 and the numbering
> narrative in `paper/README.md`; both have been updated to match. Nothing here
> is a research result.

# The L-paper contraction

jasonp asked whether the L papers were truly worth the time spent, whether each
deserved its own write-up, and how to condense. This is the answer, and what
was done about it.

## What the assessment found

**Ten papers, 108 pages, 33,067 words of prose, sixteen days of drafting.** The
manuscripts themselves were cheap: 36 commits between 2026-08-07 and 08-23. The
process around them was not.

| | |
|---|---|
| the `l-trim` adversarial campaign's ledger | **52,175 words** — longer than the corpus it reviewed |
| what five phases of it removed | 34,758 → 31,339 words, **−9.8%** |
| the rate | about 15 words of ledger per word cut |
| verdicts | 89 concessions, **one** RETAIN |
| `llm-tics` readability ledger | 10,468 words, five rounds |

The trim ladder ran *within* each paper, so it was structurally unable to
propose the one cut that mattered: deleting a section because another paper
already had it. Five phases of cutter-versus-defender never once looked across
a paper boundary, and the duplication that survived them is what this
contraction removed in a day.

**And nobody had read any of it.** All ten disclosure blocks read *"Human
verification: none, as of this draft."* The L scheme was priced at about eight
hours of jasonp's reading — his only job on that side being to read a statement
and decide to release it — and sixteen days in, that number was still zero on
every paper. jasonp's own account of why: *"we keep coming up with new but not
necessarily novel or interesting results right on the cusp of something great."*

**Three of the ten carried their weight** — L3, L4 and the law half of L1. The
three with clean novelty verdicts, which is not a coincidence.

## The seven moves

| | move | pages | why |
|---|---|---|---|
| **L3** λ bounds | kept as is | 13 | Both ends certified and re-runnable; no published upper bound existed; the lower end beats the published record where that value was numerical |
| **L4** not D-finite | kept as is | 10 | Unconditional, cheap, transports verbatim to polyominoes, polyhexes and polyiamonds |
| **L2 → L1** | merged, as Part II | 24 → **23** | L1's abstract already sold L2's spine cubic as its own third consequence; every L2 theorem was conditional on L1's Theorems A and C; L2 cited L1 eight times and spent its whole Setup restating the two results it imported |
| **L7 → L5** | merged | 25 → **21** | L7 called itself the companion in its first paragraph, restated L5's definition and four-block table verbatim — `tab:blocks` label collision included — quoted three L5 results without reproof, and was advertised in L5's abstract |
| **L10 → L8** | merged | 16 → **15** | jasonp's 08-22 ruling was "L8 absorbs the Undertow material", and absorb meant this. L10 spent about two of its seven pages restating L8's law, frame and square-lattice check; L8 carried zero `\cite` keys and L10 carried the near neighbour the priority pass found |
| **L6** | inverted and contracted | 13 → **14** | The minimum end leads, being the half the priority pass left whole; the maximum end now opens by saying it is the king analogue of a published theorem. The standalone "k = 6 verdict" section is dissolved into the four claims it decides |
| **L9** | withdrawn | 7 → **0** | Its own ledger: *novelty none claimed, and a collision found*; the load-bearing step is a reading of C++; "that any program computes the sum" is not addressed. Folded into `docs/proofs/cutcount-identity.md`, which was better than it in every part except one — the doc predated the 08-18 priority pass, so L9's FK/Potts finding is now its §9 |

**Ten papers, 108 pages → six papers, 96 pages.** Prose 33,067 → 30,405 words.

Every merged manuscript builds with zero undefined references and
`paper/verify_l_papers.py`'s 336 checks stay green, 23 RED controls firing.

## Two things the estimate got wrong

**L6 was estimated at ~8 pages and came out at 14.** The estimate was wrong, not
the execution. What makes L6 long is evidence and closed doors — the six dead
readings in "Doors closed", the coefficient triangle, the recentred basis — and
neither gets cut. The inversion and the reframing were the real content of that
move; the page count was never going to fall much without deleting results.

**The proposal said "five papers" in prose and listed six in its own table.**
Six is right: L1, L3, L4, L5, L6, L8.

## What the merges fixed on the way

- **L1** — L2's `\vthree` macro was defined in the file that no longer exists,
  which `pdflatex` caught. And "the spine" meant two different things across the
  boundary: Part I's universal curve, and Part II's first non-divisible cell of
  a column, now "the spine of a column".
- **L5** — the Gouyou-Beauchamps and Leroux attribution that
  `docs/publication-split.md` requires in three places came out better than it
  went in. The split had forced *four* placements numbered as two separate
  "k of 2" pairs, so both files said "2 of 2" and neither counted to three. One
  file, three placements, counted 1-2-3.
- **L8** — L10's abstract ended "we have run no priority pass", false since
  08-23 when the pass ran and found something. Gone with the abstract that
  carried it.

## The coverage measurement this produced

Merging the corpus made it worth asking what any of it is checked by.
`results/l-paper-verifier-coverage.md`: **74 of 531 numeric literals are read by
any check.** L5 and L8 are 0 of 144 and 0 of 69. The tool is
`tests/l_paper_coverage_audit.py`, 80 seconds for the whole corpus.

## What was also closed

- **The `llm-tics` readability campaign.** Round 5 reached the verdict itself:
  four of six tracked constructions are at zero across the corpus, dash-asides
  are 0.16/1k against the P control's 0.40, and the two that remain are carrying
  epistemic status rather than habit. `docs/reviews/llm-tics/PLAN.md` says
  closed.
- **`scripts/l_trim_gate.sh`.** **Deleted.** Campaign-scoped and never wired
  into `make`; it stood between a phase and a commit, and there are no more
  phases. Two of the six manuscripts its baseline names are gone, and
  `paper/verify_l_papers.py` had to leave its checksummed `FROZEN` list to admit
  the coverage audit, so it had been red at `HEAD` for a stale-baseline reason
  since before `docs/reviews/llm-tics/round5-L6.md` recorded it. Its check 7 —
  the one that caught an attribution vanishing when a paper drops its last
  `\cite` of a key — was run by hand over this contraction instead, and found
  one: Blöte–Nightingale 1982, now carried in the proof doc.

## What was decided not to do

**The short-rook certified brackets are not an eleventh paper.**
`docs/state-2026-08-23.md` §5 priced them as "the material of a separate short
paper". They are a section of L3, which is already the certificate paper:
making the certificate program lattice-parametric turns its two-sided bracket
into a family of them. That is a stronger L3, not a thinner L11.

**Of the five priced runs in `docs/state-2026-08-23.md` §5, none changes a
sentence in any L paper.** The five terms, the census past H = 17 and the H = 13
rank test are ladder and reach work, and the ladder closed at a(41). c₆ on the
main-diagonal spine is a day of compute to settle a judgement call about a
family no paper claims.
