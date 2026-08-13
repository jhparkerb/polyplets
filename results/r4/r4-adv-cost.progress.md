# r4-adv-cost — progress

ABOUT TO: step 1 — read governing docs (round4 brief, skeptical-reader standard)
DONE: step 1 -> both read; scoring rules and no-compute constraint fixed
ABOUT TO: step 2 — read the five r4 deliverables plus r3-spin and r3-synthesis
DONE: step 2 -> r4-perf.md, r4-a.md, r4-inv.md, r4-spinbuild.md, r4-lean.md read
  in full; r3-synthesis CORRECTION section read; queue tail read.
ABOUT TO: step 3 — pull dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log
DONE: step 3 -> log read (H=12..15 done, H=16 at column 27/41 at 00:07).
  Re-derived: walls 53.2/188.2/599.5/2065.1 s; RSS 117624/358556/979596/2420292 KB;
  totals 1123.1/1196.5/1125.7/944.4 B/window; marginal slopes 1235.9/1088.5/851.2.
  r4-perf's two slopes reproduce exactly; it dropped the H=12 point, whose slope
  (1235.9) STRENGTHENS its monotone-decline claim. H=16 projection: my re-derive
  from cols 13->27 gives ~6,850-6,950 s against r4-perf's ~7,200.
  New anchor nobody extracted: 1,172 ns/state-stage, 703 ns/transition,
  8.6 ns/slot-op = 26 cycles = one non-pipelined udiv. Confirms r4-perf's thesis.
ABOUT TO: step 4 — audit r4-perf's 15x sharding, bandwidth-bound, 28% slope, overlap
DONE: step 4 -> four verdicts. Sharding is NOT load-bearing for the H=19 go/no-go
  (L5+L6 alone put it at 5.7-9.1 days). Loop measured at 2.56 GB/s = ~1/4 of the
  single-core roof, so bandwidth-boundedness is ASSERTED not established.
  L5's 288 B decomposition sums to 256. dalby read-only: Neoverse-N1, 80 cores,
  ONE NUMA node, 116 GiB available — unclaimed by any lane, favourable to L7.
ABOUT TO: step 6 (out of order, cheap) — recheck the bit-budget arithmetic
DONE: step 6 -> a(40) = 106 bits confirmed off results/triangle.txt; 41*a(40) =
  110.842 bits, so "< 2^112" is correct and one bit loose. Exact prime products:
  4x31-bit = 124.000 OK (k=4+1=5 CORRECT); 7 u16 primes = 111.991 OK (barely);
  **14 u8 primes = 108.249 bits < 110.842 — INSUFFICIENT.** r4-perf's "14+1=15"
  is wrong, r4-a's "16 runs" is right. Round-3 defect class reproduced.
ABOUT TO: step 5 — reprice INV-8 from a measured ns_per_transition
DONE: step 5 -> ORDER, not factor. 22.6 thread-days implies 1,640 ns/transition
  for a 12-byte two-lane-add kernel, against B1-modp's MEASURED 703 ns/transition
  moving 328 B through 82 udivs. Reductio. Bracket 6.6-33 thread-hours for
  m=18..21. Factor 16-82 overstated, in INV-8's FAVOUR. Op count re-chained by
  hand (W(m), t_m, 5043*m*W(m)) and clean; the constant is the defect.
ABOUT TO: step 7 — audit r4-lean's 5-7 session estimate
DONE: step 7 -> probe log read (9.61 s, 5.5 GB, exit 0, 0 output lines, axiom pin
  matched, gate B mutant rejected at the designed site). Read the probe's
  statements for vacuity: not vacuous. Worked D1 independently: it does follow.
  Crux ESTABLISHED. Increments 3-6 priced on nothing, by the lane's own
  admission. "6-16 min" estimate vs 9.61 s measured drove a wall-breach claim
  that was not one.
ABOUT TO: step 8 — audit the lead
DONE: step 8 -> four findings. (1) The synthesis CORRECTION propagates 22.6
  thread-days and calls it "double-sourced" when only the multiplicand was.
  (2) No receipt on any box for the perf-patch or spin-engine gate claims; no
  build/r4_spin_engine anywhere; PERF-JOB-1 not run (correctly — prerequisite
  still live). Commit juxtaposes the repricing with a gate that by construction
  cannot see the patched path. (3) Lean escalation: RAM breach real, wall breach
  did not exist. (4) Framing: r4-perf's three-scenario table has no cell for the
  middle case that will actually happen.
ABOUT TO: step 9 — file the deliverable and the queue rows
DONE: step 9 -> results/r4/r4-adv-cost.md filed (11 sections: provenance table of
  44 load-bearing numbers, ranked decision-changing list, settled-but-not list,
  lead audit, ADV-JOB-1, and a "where a lane was right" section).
  Seven rows appended to results/r4/queue.md: R4-AC1..R4-AC7.

FILED. Nothing held in context that is not on disk.
