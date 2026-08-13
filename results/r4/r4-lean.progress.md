# r4-lean progress

DONE: read docs/triangle-round4.md, docs/lean-environment.md
DONE: write results/r4/r4-lean.plan.md
DONE: step 1 — read triangle-r3-l3-proofscope.md, triangle-r3-l5-constraint.md,
      triangle-r3-synthesis.md §"prove the rule instead of varying it"
DONE: step 2 — read Compute.lean in full, plus Defs.lean and Finite.lean.
      FINDING (contradicts r3): Tc_eq_T is not "half of (a)" — zero frontier
      content. But Finite.lean:61-76 `exists_adj_cross_of_reflTransGen` IS a
      committed sorry-free cut/path-splitting induction over ReflTransGen on
      Finset (ℤ × ℤ) — i.e. the calibration anchor r3 §7 said did not exist.
DONE: step 3 — Mathlib/project greps. Key hits: Relation.ReflTransGen.lift'
      (Logic/Relation.lean:737), .mono (703), .swap/reflTransGen_swap (746,751),
      cases_head (477), reflTransGen_closed (742); SimpleGraph.Walk
      takeUntil/dropUntil (Walk/Decomp.lean:35,78). Project: no Setoid/
      Finpartition use outside Symmetry.lean; GapWalk* is PowerSeries, not
      planar geometry (r3 right about that).
DONE: step 4 — read HolesUpper.lean:376-391 MoatBound conditional pattern.
DONE: step 8 — read-only ssh. ayr: x86_64, 76 GB free, 319 GB disk, repo on
      branch second-source, NO elan/lean/lake. dalby: aarch64, 125 GB, repo on
      master with .lake/packages sources but NO build and NO elan/lean/lake.
      gympie: warm — 7.0G mathlib .olean + 2.5G project build.
      => Lean is gympie-only today.
DONE: step 5 — dependency graph filed in results/r4/r4-lean.md §1.
ABOUT TO: step 9a — author the increment-1 probe file
      experiments/tristruct/r4_lean_funnel_probe.lean (UNCOMPILED).
DONE: step 9a — authored experiments/tristruct/r4_lean_funnel_probe.lean
      (UNCOMPILED) and experiments/tristruct/r4_lean_funnel_probe.sh
      (fail-closed, gate A silent-elaboration + gate B RED mutant).
DONE: steps 5-7,9 — results/r4/r4-lean.md complete (§0 corrections, §1 lemma
      graph, §2 calibration, §3 sequenced increments, §4 job request
      R4-LEAN-JOB-1, §5 referee paragraph, §6 successors, §7 NOT ESTABLISHED).
DONE: appended queue rows R4-LEAN-1..4 to results/r4/queue.md.
DONE: filed. No compute was run by this agent on any machine.
