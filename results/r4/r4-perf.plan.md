# r4-perf — plan

**Question, one sentence.** How much faster and smaller can the B1 residue
engine be made without changing what it counts, and what is the ordered, costed
list of levers?

## Steps, in order

1. Read `results/r4/r4-a.md` in full (esp. §2 gap list incl. `Succ out[12]`
   bound and the `H>16` guard, §3 job request, §4 cost model + u32 payload).
   -> notes; the cost model I will reprice against.
2. Read `results/cutcount_b1/PROVENANCE.md` and
   `results/triangle-r3-ladder-gate.md` -> the measured exact-payload anchors
   (walls, 8,143 B/window marginal slope, H=12..16).
3. Read the engine line by line: `git show 48ac108:cpp/cutcount_b1.cpp`
   (`run_height_modp`, `run_height`, `successors`, `canon`, `shifted`,
   `gather`) and the gate `git show 48ac108:tests/gate_cutcount_b1.py`.
   Cross-check against the `second-source` branch working tree.
   -> a precise statement of the inner loop, the per-slot work, and the
   container traffic.
4. Read the live dalby log `~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log`
   (read-only ssh) -> the freshest residue walls and RSS, quoted verbatim.
5. Settle the `Succ out[12]` bound: derive the true max successor count from
   `successors()` structure; if not airtight, name the cheapest probe.
   -> deliverable §3.
6. Price each lever: modular reduction (Montgomery/Barrett + delayed
   reduction), container (flat open-addressed + inline payload), sharding
   across cores, SIMD over area slots, plus levers I find in the code
   (candidates to check: payload trimming to reachable area range, key packing,
   successor dedup, transition precomputation/table caching, prime choice,
   two-pass sizing to avoid rehash, arena allocation, batching by column).
   Each labelled MEASURED/EXTRAPOLATED/ASSERTED with the reasoning, LOC+hours,
   semantics risk (by construction vs by intent), and overlap with levers above.
   -> deliverable §1.
7. Reprice H=17..20 under as-is / cheap-only / everything, wall per prime and
   peak RAM, against ayr (78 GB/32c) and dalby (126 GB/80c/564 GB NVMe).
   -> deliverable §2.
8. Write one dispatch-ready job request (§4) and >=2 queue rows different in
   kind (§5); append rows to `results/r4/queue.md`.

## What each step produces
Steps 1-4 produce facts in the progress file and quoted numbers in the
deliverable. Steps 5-8 produce the four numbered deliverable sections.

## What would make me stop
- The engine source at 48ac108 is not readable / diverges from what the brief
  describes -> file the discrepancy, stop, report.
- The inner-loop reading contradicts the "reduction dominates" inference ->
  do not stop; reprice the list with reduction demoted and say so.
- Any step that would require running compute -> stop that step, file a job
  request instead. I run no compute anywhere.
