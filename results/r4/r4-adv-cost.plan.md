# r4-adv-cost — plan

**Question, one sentence.** Of every load-bearing number filed in round 4
tonight, which were measured, which were extrapolated from something measured,
and which were asserted — and where does the label on the tin not match what is
inside?

**Standing constraint.** No compute anywhere. Read-only ssh to dalby/ayr for
logs and source. Audit only; never generate.

## Steps, in order

1. Read the governing docs: `docs/triangle-round4.md`,
   `docs/skeptical-reader-standard.md`, `docs/r3-job-dispatch.md`.
   → produces: the rules I score against.
2. Read the five deliverables under audit end to end:
   `results/r4/r4-perf.md`, `r4-inv.md`, `r4-a.md`, `r4-lean.md`,
   `r4-spinbuild.md`, plus `results/triangle-r3-spin.md` and
   `results/triangle-r3-synthesis.md`.
   → produces: a raw inventory of every load-bearing figure with the lane's own
   provenance label.
3. Pull the measured record: `~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log`
   on dalby, read-only. Re-derive marginal slopes, walls, RSS myself.
   → produces: the ground truth column of the provenance table. Any lane
   number that disagrees with the log is a finding.
4. Audit r4-perf's 15x sharding factor, the bandwidth-bound claim, the 28%
   marginal-slope reconciliation, and lever multiplication overlap.
   → produces: verdicts, and a statement of what measurement would settle each.
5. Audit the INV-8 repricing (22.6 thread-days / 9.4 GiB) against the borrowed
   40 ns/slot anchor and r4-spinbuild §3's warning. Determine whether re-pricing
   from a measured ns_per_transition moves it by an order or a factor.
6. Recheck r4-a's bit budget arithmetic (k = 4 + 1 held out from C_H(40) < 2^112)
   by hand. Round 3 caught a 13-primes-for-103-bits slip in this exact class.
7. Audit r4-lean's 5-7 session estimate: what the crux probe actually
   established versus what is priced on nothing.
8. Audit the lead: silent caps, narrowing dispatches, unstateable framings, the
   two gates built without independent review, the wave composition, and the
   correction written into `results/triangle-r3-synthesis.md`.
9. File the deliverable: provenance table, ranked decision-changing claims,
   settled-but-not list, job requests for anything only measurement can settle.

## What would make me stop

- A number I cannot trace to a log, a script, or a stated derivation gets
  marked NOT ESTABLISHED and I move on; I do not reconstruct it.
- If dalby is unreachable read-only, step 3 is marked NOT ESTABLISHED and every
  verdict depending on the log is downgraded, not guessed.
- I do not run compute to settle anything. A number that needs measurement
  becomes a job request row naming the decision it changes.
