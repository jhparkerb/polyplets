# r4-adv-ind — plan

**Question (one sentence):** Are round 4's routes independent of the production
transfer-matrix engines in the sense that matters — a shared misconception about
*what is being counted* could not pass through both and show up as agreement —
and does the banked T(40,15)+T(40,16) recount actually rest on such a route?

**Standing verdict default:** "this smuggles the frontier rule back in".
Hostility ranks; it does not exclude.

**Two levels every route must clear:**
- L1 semantic: where is connectedness *defined* in this route, and could the
  hypothesised misconception reproduce there?
- L2 algorithmic: name the failure mode the route exhibits if its rule is wrong,
  and argue it is disjoint from union-find-over-a-frontier's failure mode.

## Steps

1. Read the banked artifact: `results/cutcount_b1/PROVENANCE.md`, the source
   `cutcount_b1.cpp.59e90660`, and the rows. Produce: verdict on "never decides
   connectivity" read off the *source*, not the prose. → deliverable §1
2. Re-read `results/triangle-r3-adv-independence.md` with the rows committed.
   Produce: is the state-census concession fatal / survivable / under-stated.
   → deliverable §1
3. Audit `results/r4/r4-inv.md` §2 common-mode claims (height second difference;
   forced parity not clearing B1). Establish or refute each. Produce: effect on
   the standing of banked H=15,16. → deliverable §2
4. Audit the two gate batteries built tonight without review: `r4-perf.md`
   seven gates incl. three REDs, and `r4-spinbuild.md` GATE 0 / GATE 1 rook
   mutant. Question: does each battery contain a control that *sees* the error
   class advertised? Round 3 measured that state censuses cannot see symmetric
   stencil errors at all. → deliverable §3
5. Audit `results/r4/r4-lean.md` + `results/triangle-r3-l3-proofscope.md`: the
   (a)+(b) closure claim, the "retroactively upgrades every same-rule agreement"
   sentence, and the `stateOf` correction. → deliverable §4
6. Per live route, one sentence a skeptical reader accepts and one they reject,
   in the route's own terms. → deliverable §5
7. Ranked list of independence claims that would not survive a referee; explicit
   statement of what the banked 21.64% does and does not settle; roll of
   lanes whose own honesty pre-empted me. → deliverable §6,§7,§8
8. Append successor/job rows to `results/r4/queue.md`.

## What each step produces
Each is a numbered section appended to `results/r4/r4-adv-ind.md` the moment it
exists, with caveats attached inline.

## What would make me stop
- The `cutcount_b1` source is not readable locally → file a job request for the
  dalby copy, mark §1 NOT ESTABLISHED, continue to §2.
- Any claim I cannot check off disk is marked NOT ESTABLISHED rather than
  reasoned to a verdict.

## Hard constraints
No compute anywhere, nothing on gympie beyond reading files. Read-only ssh
permitted. I write only my four files plus appended queue rows.
