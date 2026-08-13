# r4-gen5 plan

**Question (one sentence):** What do the campaign's partial confirmation routes
for row 40 of T(n,H) *compose* to — arithmetically (do combined constraints pin
a cell no single route pins), epistemically (what is the joint referee-facing
statement), and adversarially (what error passes every route at once)?

## Steps

1. Read charter + queue + predecessors r4-gen, r4-gen2, r4-gen3 (kill list, so I
   file successors not repeats). Read r4-adv-ind.md for the correlated-error
   substrate, r4-ladder.md / r4-spinproj.md / r4-a.md for what each route
   actually covers. Product: a coverage table of row 40 by route.
   Also read results/triangle-r3-synthesis.md closed doors + three floors.
2. Direction 1 — arithmetic composition. Work the row-sum subtraction argument
   precisely: which subsets of row 40 does "sum equals a(40)" close, and what
   makes it circular. Then CRT-across-rule-classes, residue+interval, and the
   other cross-constraints (Grand anchors, diagonal law, growth bounds, spin
   mod 2). Product: rows R4-G5xx, each with prior + cheapest kill; self-kills
   filed with the kill.
3. Direction 2 — epistemic composition. Write the joint sentence over row 40
   given per-cell states {exact-two-source, modular-only, single-source+proved
   rule, unconfirmed}. Then rank cheap additions by how much they improve that
   sentence. Product: the sentence, plus rows for the top additions.
4. Direction 3 — failure-mode composition (the ranked deliverable). Enumerate
   errors that would pass every route simultaneously; rank by
   P(error) x P(undetected). Product: ranked rows.
5. Second pass: what do MY OWN rows share — the correlated-failure story of
   this deliverable itself. Product: a closing section.
6. Append all rows to results/r4/queue.md (append only).

## What each step produces
Steps 2-4 each append a section to results/r4/gen5 deliverable
`results/r4/r4-gen5.md`. Step 6 appends one line per row to queue.md.

## What would make me stop
- Filing >= 20 rows across the three directions with direction 3 ranked.
- Discovering that a direction is fully covered by a predecessor: then I file a
  kill/subsume note against their row rather than a duplicate, and move on.
- HARD: no compute anywhere. Read-only ssh only if needed for a fact.
