# r4-lean2 plan — author the next increment of the definition-level proof

**Question, one sentence:** now that the funnel crux is retired, which increment
of the (a)-theorem most reduces remaining risk, and what is it as real,
compilable Lean source with a fail-closed GREEN/RED gate?

**Standing label:** I run no compute. No `lake`, no `lean`, no `lake env lean`,
on any machine. Every Lean artifact I produce is UNCOMPILED until the lead
builds it.

## Steps

1. Read the inherited state off disk: `results/r4/r4-lean.md` (done),
   `results/triangle-r3-l3-proofscope.md` (done), `results/r4/r4-adv-cost.md` §5,
   `experiments/tristruct/r4_lean_funnel_probe.{lean,sh,log}`,
   `polyplets/Polyplets/{Defs,Finite,Compute}.lean`.
   Produces: an accurate picture of what compiled and what the probe left open.

2. Choose the increment, defend the choice in one paragraph against the
   adversary's charge that the encoding layer is unpriced and unattacked.
   Produces: §1 of the deliverable.

3. Verify every Mathlib identifier I intend to use against the vendored tree
   (grep, per `docs/lean-environment.md` §4). No identifier goes in the source
   unread. Produces: an identifier ledger in the deliverable.

4. Author the Lean source. Design against r3-L5's failure mode: named `sorry`
   holes rather than confident prose, each with a comment saying exactly what it
   must discharge, so the compile tells us which holes are real rather than
   burying nine errors at six sites.
   Produces: `experiments/tristruct/r4_lean2_<purpose>.lean` (UNCOMPILED).

5. Author the gate script in the shape of `r4_lean_funnel_probe.sh`:
   silence-is-success GREEN, plus at least one RED mutation that must fail to
   elaborate. Produces: `experiments/tristruct/r4_lean2_<purpose>.sh`.

6. Price the increments so an adversary cannot call it "priced on nothing":
   line counts, dependency counts, and the one measured anchor (the funnel
   probe: 9.6 s, 5.5 GB, ~230 lines). Anything I cannot price = NOT ESTABLISHED.
   Produces: §4-5 of the deliverable + queue rows.

## What would make me stop

- If the funnel probe's actual source shows the crux lemma was weaker than the
  lead's summary (e.g. `sorry`-carrying, or `Unstranded` assumed away), I stop
  and report that first — the increment choice depends on it.
- If the increment I pick turns out to depend on a Mathlib API that does not
  exist in the vendored v4.31.0 tree, I stop, file NOT ESTABLISHED, and pick
  the next-riskiest increment rather than inventing an identifier.
- I stop at "source + gate written", per the brief. I do not compile.
