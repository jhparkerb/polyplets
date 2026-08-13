# r4-inv plan

**Question (one sentence):** Is round 3's INV-8 — the spin-basis mod-2 count of
T(40,H) at H=20 and H=21 — actually buildable and dispatchable, and what does
one bit per cell buy a skeptical referee?

## Steps

1. Read the four named inputs: `results/triangle-r3-involution.md` (done),
   `results/triangle-r3-synthesis.md`, `results/triangle-r3-l4-quotient.md`,
   `results/cutcount_b1/PROVENANCE.md` + the recovered rows. Also
   `results/triangle-r3-l6-wildcard.md` (source of the spin-basis pricing) and
   the round-3 queue row INV-8 itself.
   Produces: an accurate statement of what the spin basis IS.
2. Reconstruct the state-count arithmetic (54,608,393 / 131,836,323) from the
   definition, on paper/by hand-checkable closed form. Confirm or refute the
   0.3 GiB figure and name the assumption it rests on.
   Produces: deliverable section 1 (buildability + arithmetic + entry ticket).
3. Answer the forced-parity/independence question head on, and test INV-8
   against the two-horn obstruction. If it does not escape, close negative
   here and go straight to successors.
   Produces: deliverable section 2.
4. Design the gate battery against the recovered exact rows C<H>.out
   (H<=16, n<=40) — cells, REDs including one the structural self-checks
   provably cannot see, fail-closed exit contract.
   Produces: deliverable section 3.
5. Write the build plan and the JOB REQUEST for the first dispatchable
   increment, all numbers labelled MEASURED / EXTRAPOLATED / ASSERTED, with a
   box recommendation and a reason.
   Produces: deliverable section 4 + a queue row.
6. Write the "what one bit is worth" section for the skeptical reader.
   Produces: deliverable section 5.
7. File >=2 successor queue rows, different in kind.

## What would make me stop

- If the spin basis as defined cannot decide connectivity at all (i.e. it
  counts something other than connected animals and no cancellation identity
  repairs it), stop at step 3 and file the closure + successors.
- If the 54.6M state count turns out to be for a different object than
  T(n,H) (e.g. the wrong cut orientation, or not fixed-H), stop and say so.
- If no gate battery can be built because the recovered rows are not per-
  height T(n,H), stop at step 4 and say the oracle does not apply.

## Hard constraints

No compute of any kind on any machine. Read-only ssh only. Numbers I cannot
measure are marked NOT ESTABLISHED, not estimated.

## Revision 1 (appended, reason stated)

**Reason:** step 1 turned up `results/triangle-r3-spin.md` — an untracked
wave-5 round-3 scout file, written 21:18 on 2026-08-12, i.e. after the
synthesis (20:26) and after the last write to the round-3 queue (21:09).
It already answers "is INV-8 buildable" with verified state counts, a
CORRECTED geometry (the 0.3 GiB / cut-20 premise in my brief is false for
king animals), a desk-validated pipeline, a measured RED battery, and a
full job request SPIN-JOB-1. Its five queue rows SPIN-1..5 never reached
`results/triangle-r3-queue.md`, so round 4 inherited the stale pricing.

**Revised steps:** 2 becomes "audit the spin file's arithmetic off disk and
state what is still unmeasured" rather than "reconstruct it"; 4 (the
oracle-based gate battery) and 5 (job request) become the lane's actual new
content, since round 3's battery topped out at 28 cells at n<=7 and the
recovered rows give 640 cells at production scale; a new step 2b prices the
q!=2 siblings from a derivation round 3 left ASSERTED.
