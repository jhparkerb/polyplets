# L-paper readability rules

Rules 1–9 are derived from jasonp's edits to L2; 10–14 from the issues those
edits pointed at, generalised across all seven papers; 15–17 from his rulings
on the coinage sweep of `L-coinage-candidates.md`.

## Sentence and paragraph

1. **Define before asserting.** State the object, then the fact about it.
2. **Front-load the dependency list.** One sentence naming what the paper
   assumes, early, instead of dependencies arriving over four sections.
3. **Provenance is not a finding.** No "originally verified through $y^{17}$",
   no "an earlier version of this work", no emphasised *Derived*.
4. **A coinage that needs defending is the wrong coinage.** Name the thing, or
   introduce the term once with a definition and a citation.
5. **Captions caption.** No claims, no controls, no asides.
6. **State the fact, not its shadow.** "whose residue is not 1" → "is 2".
7. **No importance-talk.** Not "carries everything below", "does all the work",
   "the load-bearing triviality".
8. **No transition sentences that only announce a turn.** Give the fact that the
   turn was leading to.
9. **Nothing undefined at point of use.**

## Structure and titles

10. **Titles name a topic, not a verdict, and carry no second clause.** The
    "X, and Y" title almost always has the argument in Y; the argument belongs
    in the body, where it is supported. Same for "Why X is cheap", "The guesser
    is powered", "And then it is not".
11. **The ledger states warrant; the body does not restate it.** `\Ldisclosure`
    already says what is proved, certified or measured. A body paragraph
    re-arguing it is duplication with two places to drift.
12. **Novelty is a status, not an argument.** Name what was searched, name what
    was found, point at the record. Do not explain what absence does or does not
    prove — it appeared in four papers as near-identical epistemology.
13. **Identical text in two papers belongs in `shared/`.** Five papers carried a
    character-identical draft banner in their own preambles;
    `\firstdraftbanner` now holds it, for the reason the disclosure blocks are
    centralised: seven copies drift, and no paper should be able to soften a
    shared statement by editing its own.
14. **No sentence defending the paper against an imagined objection.** "A reader
    who distrusts one can use the other", "a reader who doubts … is doubting
    something this paper does not prove", "we record rather than bury".

15. **"Law" needs an extraordinary warrant.** It sounds pompous. Five things
    carried it; only the diagonal law and the height-diagonal law, both
    theorems, kept it. Prefer the plain name — formula, identity, bound, check,
    or the numbered theorem.
16. **Use the literature's phrasing for a class the literature already names.**
    "animals on the king lattice" (Bacher), "staircase polygons", "square
    lattice" — not our compressions "king animals", "staircase animals", "rook
    lattice". A compression that survives must be defined at first use against
    the cited phrase, as L1 does for polyplets.
17. **Engine artefacts keep their names.** frozen-successor-array kernel,
    production column-sweep kernel, compiled-evaluation leaf and surface,
    parent-direction string: the names match the reproduction section and the
    repo, so a reader can find the code they name. This is the one place a bare
    coinage is doing work outside the prose.

## Naming decisions applied

| name | disposition |
|---|---|
| king animals | → **polyplets** (L1, L2, L4; L3's "a polyplet, or king animal" gloss kept as the first-use definition) |
| Bacher's directed / multi-directed king animals | → "directed animals on the king lattice" (L3 prose and comparison table) |
| convex king animal | → **convex polyplet**, retitling L5 and L7; first-use definition names the king lattice |
| staircase animal | → **staircase polyplet**, defined at first use as the king-lattice analogue of the parallelogram polyominoes |
| rook lattice | → square lattice (L3, L6; L6 already defines "square" as rook-connected) |
| activation law | → Theorem, *the activation boundary* (L2) |
| onset law / triangular law | → the onset formula (L6) |
| floor law | → the floor identity (L6) |
| denominator law | → the denominator formula (L6) |
| king law | → the king bound (L6) |
| nullity law | → the nullity check (L5) |
| periodic law | → the periodic extension (L1) |
| "no closed law claimed" | → no closed form claimed (L2, twice) |
| positive / negative control | kept — standard in statistics, ML evaluation and experimental science; the enumeration literature does the same check and calls it cross-checking against known values, so define at first use |
| null control | → described by what it is: a fifth arm on a series with no algebraic equation to find (L5, three sites). The term has no currency in any field searched |
| grand form | → **product form** (L1 Thm C, propagated to L2) |
| the ladder | L2 §3 → "Three coefficient identities"; L3's Lean-chain sense removed, μ_H sense kept |
| spine | kept — defined locus |
| sleeve zeros | kept — defined at first use |
| defect gas | kept in L1 where it is defined; L2 points at L1 instead of using it bare |
| area wild / perimeter tame | removed from L5's subtitle and section titles |

Companion papers are cited as "companion paper L*n*" plus title, never "the
companion paper".

## Structural changes these rules forced

- **L5 split into L5 + L7.** The subdominant exponential and the amplitude ratio
  were a second paper's worth of apparatus behind a leading term L5 settles in
  three pages.
- **L3 gained an Open problems section**, which had been hiding inside
  "Comparison, and what is open".
- **L7 gained an Introduction**; it had opened on its dependency list.
