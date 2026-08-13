# r4-lean plan

**Question (one sentence):** What exactly has to be proved, in what order, for
the definition-level theorem (r3's L3-5) to close the chartered
"both engines share a misconception about what is being counted" objection for
the swept cells, and what is the smallest first increment a lead can dispatch a
build for tonight?

## Steps

1. Read the three r3 inputs off disk: `results/triangle-r3-l3-proofscope.md`,
   `results/triangle-r3-synthesis.md` (the "prove the rule instead of varying
   it" section), `results/triangle-r3-l5-constraint.md` + the r3 ledger entry
   on its failed compile. Produces: my own statement of (a)/(b)/(c) and of the
   9-errors-at-6-sites lesson. NO re-derivation of the scoping doc.
2. Read `polyplets/Polyplets/Compute.lean` around `Tc_eq_T` (~line 207) and
   whatever it depends on. Produces: a verified answer to "how much of (a) is
   already committed and sorry-free" — checked, not inherited from r3's
   "half of it" claim.
3. Inventory the existing connectivity/path/Finset machinery in the
   development (grep the 77 project files) and in Mathlib (scoped greps per
   `docs/lean-environment.md` §4 only — no filesystem-wide scans). Produces:
   for each skeleton lemma, "Mathlib has it, named X" vs "must be authored".
   Also produces the calibration candidates: existing inductions of the same
   shape already carried in this development.
4. Read `HolesUpper.lean`'s MoatBound pattern — the named fallback (conditional
   theorem on a stated hypothesis). Produces: the exact shape of the fallback
   and whether it really applies here.
5. Write the dependency graph for (a): each lemma's precise Lean statement,
   deps, Mathlib-or-authored, difficulty. Identify the load-bearing induction
   and say what makes it hard.
6. Answer the calibration question: cheapest diagnostic of whether the
   load-bearing induction is a day or a month.
7. Sequence the increments; write increment 1 small enough for gympie tonight
   (1 GB/core, 2 cores, 10 min) or say it is not.
8. Check whether a Lean toolchain exists on ayr and dalby (read-only ssh —
   `ls`, no builds). Produces: the box field of the job request. CHECK, do not
   assume.
9. Author increment-1 Lean source (UNCOMPILED, labelled as such everywhere),
   file the job request block, write the referee-facing (a)+(b) paragraph,
   append >=2 successor queue rows different in kind.

## What each step produces
Every step appends to `results/r4/r4-lean.md` the moment it has a result.

## What would make me stop

- If step 2 shows `Tc_eq_T` already is (a) in full, the deliverable collapses
  to "(a) is done, here is what remains for (b)" and I stop early and say so.
- If step 3 finds Mathlib has no usable Finset/graph connectivity API at all
  for this shape, I stop the skeleton and file the fallback conditional
  theorem as the primary route instead, with that finding as the reason.
- I run NO compute of any kind. No `lake build`, no `lake env lean`, no Lean
  invocation on any machine, gympie included. Everything I write that has not
  been compiled by the lead is labelled UNCOMPILED. If I find myself wanting a
  build to answer a question, that becomes a job request, not a command.
