ABOUT TO: step 1 — read triangle-round4.md, triangle-r3-spin.md, r4-spinbuild.md, r4-inv.md, r4-adv-cost.md
DONE: step 1a -> docs/triangle-round4.md read (write-ahead rule, box specs)
DONE: step 2 -> pulled r4_spin_m16.log + r4_spin_gates.log from dalby (read-only ssh); 15 per-m heartbeats present with states=/wall_s=/peak_rss_mb=
NOTE: states(m) = 7,17,41,99,239,577,1393,3363,8119,19601,47321,114243,275807,665857,1607521,3880899 -- exact half-companion Pell, s(m)=2s(m-1)+s(m-2), 14/14 confirmations, zero residual
ABOUT TO: step 1b/3 -> read triangle-r3-spin.md (m->H map, Pell window chain), r4-inv.md, r4-spinbuild.md sec3, r4-adv-cost.md sec2
DONE: step 2b -> pulled ~/src/pm-b1-perf/results/r4/spin_m16.txt.metrics from dalby. KEY: ns_per_transition FLAT 13.9645/13.9583/13.9880/14.0690/13.9719/13.9707 for m=11..16 (verify-rank off above m=10). bytes_per_state 24.50 at m=16 -> asymptote 24.
DONE: step 2c -> oracle dir dalby ~/src/polyominoes/results/cutcount_b1/rows contains C1.out..C16.out ONLY. NO oracle at H=17..21.
NOTE: transitions/state is EXACTLY LINEAR in m: 679.00,742.5,805.9,869.3,932.8,996.2 at m=11..16, slope 63.44 per m, intercept -18.84, residual <0.1% on all six.
NOTE: states(m) = t_{m+1} (companion Pell), matches triangle-r3-spin sec1 table exactly: t_18=9369319 ... t_22=318281039.
ABOUT TO: step 4/5 -> build projection table m=17..21 (transitions x 13.97 ns; RAM at 24 B/state), go/no-go
DONE: step 4 -> projection built. transitions(m) = states(m)*(63.4314m - 18.703), five consecutive second-differences all 63.431 (5 s.f.). Wall m=18..21 = 9402 s = 2.61 thread-hours at 13.9707 ns/transition. Peak RSS m=21 = 7.12 GiB.
DONE: step 6 -> B1 oracle is C1..C16 only: ZERO oracle cells at H=17..21. BUT banked triangle results/ns_a40/perheight/h20.out,h21.out are real-sweep for all n=1..40 -> 41 nontrivial comparison cells at the two target heights, and comparing against T (not C) bypasses r4-spinbuild sec3(j) common-mode.
ABOUT TO: step 7/8 -> write deliverable results/r4/r4-spinproj.md and append queue rows
DONE: step 7 -> deliverable filed at results/r4/r4-spinproj.md
DONE: step 8 -> six rows appended to results/r4/queue.md (R4-SPINPROJ-0..4 + JOB-1); JOB-0 and JOB-1 field blocks in deliverable sec5
