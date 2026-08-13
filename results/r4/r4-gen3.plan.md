# r4-gen3 plan

Question: what attacks the *mission statement* rather than the recount — the
proof half nobody has priced, the failure modes of a(40) that no lane is
attacking, and the constraints on a(40) that live outside this campaign?

Steps, in order:

1. Read `results/r4/queue.md`, `results/r4/r4-gen.md`, the closed-doors
   sections of `results/triangle-r3-synthesis.md`, and skim
   `results/r4/r4-adv-ind.md`, `results/r4/r4-adv-cost.md`. Also
   `results/r4/r4-gen2.plan.md`/`.md` as it appears, to steer away.
   Produces: a do-not-repeat list at the head of the deliverable.
2. Direction 1 — the proof half. Read `results/r4/r4-lean.md` and
   `results/triangle-r3-l3-proofscope.md` for what (a)/(b)/(c) mean here and
   what was explicitly not attempted. Then price the (b)->(c) gap options:
   verified extraction, certifying run with per-column proof objects, a
   small auditable checker, translation validation of one production column,
   proof-carrying output. Produces: rows R4-G3nn with cost class + kill.
3. Direction 2 — adversarial "total confidence". Establish off disk what the
   a(40) production run actually consists of: which engine binary, which
   shards, what combine step, what checkpoint/resume path, what accumulator
   widths. Read code and run records only (no compute). Then enumerate
   failure modes and rank probability x undetectability.
   Produces: the ranked table, the largest section of the deliverable.
4. Direction 3 — outside constraints. OEIS cross-refs already in repo,
   published values at any n or H, growth-constant bounds, asymptotic
   consistency, related-sequence identities the project holds. Which would
   catch a 1% error, a one-digit error, a single-shard-sized error?
   Produces: rows with the size of error each would catch.
5. Rows I can kill myself get filed WITH the kill, as I go.
6. Append every row to `results/r4/queue.md`, append-only.

Stop conditions: >= 20 rows filed, direction 2 ranked, queue appended. No
compute anywhere, nothing on gympie; read-only ssh to dalby/ayr only if a
number cannot be had off disk.
