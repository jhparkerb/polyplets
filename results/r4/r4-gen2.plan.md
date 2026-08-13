# r4-gen2 plan

Question: what new ideas does tonight's evidence make askable — the 207x cost
overprice, the bandwidth-bound kernel, and a second validated engine — that
round 3's picture foreclosed?

Steps, in order:

1. Read the prior generator's rows (`r4-gen.md`), the queue, and tonight's two
   audits (`r4-adv-ind.md`, `r4-adv-cost.md`). Produces: a do-not-repeat list.
   -> also skim the two named sections of `results/triangle-r3-synthesis.md`.
2. Skim the three tonight deliverables that produced the new facts
   (`r4-spinbuild.md`, `r4-perf.md`, `r4-lean.md`) for the measured numbers, so
   my rows are priced against measurements and not against the void estimates.
   Produces: a table of live measured numbers.
3. Generate rows in three families — (a) model-counted quantities standing in
   for measured ones, (b) bandwidth/out-of-core levers, (c) what a second
   validated engine makes askable — plus anything else. Each row: id `R4-G2<n>`,
   one-line idea, honest prior, cheapest kill, entry-ticket levels cleared.
   Rows I can kill from disk get filed WITH the kill. Target >= 20.
   Produces: `results/r4/r4-gen2.md` sections, appended as written.
4. Audit the queue for rows priced against the now-void INV-8 cost model and
   against the round-3 bandwidth-blind lever vocabulary; mark stale/subsumed.
   Produces: a STALE section in the deliverable + queue rows.
5. Second pass: what do my own rows share? File as a row.
6. Append all rows to `results/r4/queue.md` (append only).

Stop conditions: 20+ rows filed with kills and the queue audit filed. No
compute anywhere; read-only ssh only if a number cannot be had off disk.
