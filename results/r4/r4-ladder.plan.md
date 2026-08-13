# r4-ladder — plan

**Question (one sentence):** What is the real plan for H=17, 18 and 19 —
22.20% of a(40) — now that the fast-modp lever has been measured at 1.12x at
H=15 and is declining with height?

## Steps

1. Read `results/r4/r4-perf.md` in full (lever list, H=17..20 table under three
   scenarios, §4.2 bandwidth-boundedness). → notes.
2. Read `results/r4/r4-a.md` §2 (gap list, `H>16` guard, `Succ out[12]` bound)
   and §4. → notes, and the exact quoted words of the successor-bound claim.
3. Read `results/r4/r4-adv-cost.md` §§3-4 (prime budget, bit target) and
   `results/cutcount_b1/PROVENANCE.md`. → prime count, provenance of the
   recovered rows.
4. Read the actual B1 source on dalby (read-only ssh) — the successor
   generator, the `H>16` guard, the key packing, the payload type — enough to
   settle §3 by argument rather than by citation. → the decisive code lines.
5. Re-derive the cost table for H=17,18,19 from tonight's MEASURED walls
   (H=12..16) and RSS: fit the growth ratio, report residuals, apply the
   measured 1.12x (and its declining trend) not the predicted factor, multiply
   by 16 primes. → deliverable §1.
6. Re-rank the levers under a bandwidth-bound model: does payload narrowing
   invert above the division fix? What falsifies the inversion? Container
   rewrite and cache blocking reconsidered. → deliverable §2.
7. Settle the successor bound: `floor((H+1)/2)` vs `floor((H+3)/2)`. Airtight
   argument if the code supports one; otherwise name the cheapest decisive
   probe (a static assert / instrumented count run, not a full height).
   → deliverable §3.
8. Stage the ladder: height order, prime order, RED at each stage, abort
   condition, and — plainly — what the correctness evidence is above H=16 where
   the recovered oracle stops. → deliverable §4.
9. File one ready-to-dispatch job request (full field block) and >=2 successor
   queue rows different in kind. → deliverable §5, `results/r4/queue.md`.

## What each step produces

Steps 1-4 produce notes and quoted anchors in the progress file; steps 5-9 each
append a numbered section to `results/r4/r4-ladder.md` as it is finished.

## What would make me stop

- If the B1 source on dalby contradicts the measured-wall table's provenance
  (i.e. the walls were not measured on the code I am costing), I stop and file
  that as the finding rather than extrapolating.
- If the successor bound cannot be settled by reading the generator, I stop
  trying to settle it and file the cheapest decisive probe instead — I do not
  run it.
- No compute anywhere. Need a number → job request row.
