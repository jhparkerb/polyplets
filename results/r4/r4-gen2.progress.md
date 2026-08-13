# r4-gen2 progress

ABOUT TO: step 1 — read r4-gen.md, queue.md, r4-adv-ind.md, r4-adv-cost.md,
and the two named sections of results/triangle-r3-synthesis.md
DONE: step 1 -> all read; do-not-repeat list = R4-G1..G23, R4-A1..A5,
R4-P1..P4, R4-INV-1..4, R4-SB1..3, R4-AI1..7, R4-AC2..7, R4-LEAN-1..4.

ABOUT TO: step 2 — read-only ssh to dalby for tonight's spin/perf logs
DONE: step 2 -> receipts now EXIST (they did not when r4-adv-cost filed).
  dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log  H=16 landed
    wall_s=6864.1 peak_rss_mb=7040.8 ; four extra H=13 prime runs
  dalby:~/src/pm-b1-perf/experiments/tristruct/r4_perf_job1.log
    patched H=13/14/15 = 146.8 / 485.8 / 1840.7 s
  dalby:~/src/pm-b1-perf/experiments/tristruct/r4_spin_m16.log
    m=1..16 wall_s=88.6 peak_rss_mb=90.7 compared=640 mismatch=0
  dalby:~/src/pm-b1-perf/experiments/tristruct/r4_spin_gates.log  12/12/4 mutants
  measured maxstates per H == ADV-I4 census exactly at H=12..16
  ayr idle (load 0.04, 77 GiB free); dalby idle, 121 GiB free, 563 GB disk

ABOUT TO: step 3 — read cutcount_b1.cpp.59e90660 payload/state structure to
ground the evaluation-vs-coefficient-vector row
DONE: step 3 -> Payload = 3*(Nmax+1) I256 slots (c0, c1, A(1)) per state, dense;
  states discovered lazily in unordered_map but saturate to the full census;
  dead all-zero-payload states are materialized and never pruned;
  the H<=16 cap at lines 316/381 is NOT a key-width limit (H=21 needs 110 of 128 bits).

ABOUT TO: step 4 — write rows into results/r4/r4-gen2.md
DONE: step 4 -> results/r4/r4-gen2.md written (sections 0-5 + NOT ESTABLISHED)

ABOUT TO: step 5/6 — append rows R4-G2-1..25 to results/r4/queue.md
DONE: steps 5/6 -> 25 rows appended and re-read out of the file (25/25 present,
no id collision with R4-A/P/INV/SB/AI/AC/LEAN/L/G lanes). Four filed CLOSED
with their kills (G2-6, G2-10, G2-11, G2-24); G2-25 is the second-pass row.
Stale/subsumed audit is §5 of the deliverable.

LANE COMPLETE.
