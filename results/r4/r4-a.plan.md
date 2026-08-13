# r4-a plan (SCOUT, R4-1)

**Question, one sentence:** Does the committed `--modp` mode in
`git show 7b13137:cpp/cutcount_b1.cpp` already provide the residue-payload
binary that round 3's LG-JOB-1 was blocked on, and if so what exactly still has
to be authored before an H=17..19 residue ladder can launch on ayr/dalby?

## Steps

1. Read `results/cutcount_b1/PROVENANCE.md` — establish what the recovered run
   is and which source produced it. Produces: provenance facts for §1.
2. Read `results/triangle-r3-ladder-gate.md` §2/§3/§4 — the LG-JOB-1 field
   block format, the per-height RAM/wall table, the gate battery and REDs.
   Produces: the template and the measured anchors for §3.
3. Read `results/triangle-r3-synthesis.md` — the round verdict and ledger, so
   I do not re-derive its conclusions. Produces: context only.
4. Dump the three sources to the scratch tree under experiments/tristruct and
   diff them: 7b13137 vs 48ac108 vs the banked 59e90660. Produces: exact line
   numbers for `run_height_modp` and the fail-closed exits.
5. Read `run_height_modp` line by line against the exact-payload path: shared
   stencil/transition functions, self-checks ([q^0]=0, q=1 binomial), row
   output format vs what `--assemble` parses, exit codes. Produces: §1 verdict.
6. Read `git show second-source:scripts/run_cutcount_b1_calib.sh` and the
   `gate-cutcount-b1` gate script on that branch. Produces: the exact build and
   run command lines for the job request, and the gate controls.
7. Read `results/cutcount_b1/calib_run.log` for the measured anchors (bytes,
   windows, wall). Produces: MEASURED labels for §3.
8. Compose the gap list §2 (diff-sized items, CRT assembly, RED-D held-out
   prime, 8-bit vs 16-bit prime), the LG-JOB-1R field block §3, and the
   H=17..19 impact §4.
9. Append successor rows + the R4-1 closing row to results/r4/queue.md.

## What would make me stop

- `run_height_modp` is absent or stubbed in 7b13137 → verdict is NO, file the
  gap list as an authoring spec instead and stop.
- The banked rows' source and 7b13137 differ in the transition kernel (not just
  the removed function) → the modp path is not the same code path; escalate to
  the lead rather than filing a job request.
- Any number I cannot find in a log on disk → NOT ESTABLISHED, no estimate.

## Hard constraints on me

No compute of any kind. No writes outside my three files, my scripts under
experiments/tristruct/r4_a_*, and one appended block in results/r4/queue.md.
