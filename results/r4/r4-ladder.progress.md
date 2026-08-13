# r4-ladder — progress

ABOUT TO: step 1-3, read r4-perf.md, r4-a.md, r4-adv-cost.md, PROVENANCE.md
DONE: step 1-3 -> notes in context; anchors: measured walls H=12..16, c(H)
      geometric mean 1.0743, 944 B/w as-is, prime counts u32 4+1 / u16 7+1 /
      u8 15+1, disagreement floor((H+1)/2) [r4-perf §3] vs floor((H+3)/2)
      [r4-a §2.2].

ABOUT TO: step 4, read the B1 source (successors + gather + key packing) and
      the r4_perf_job1.log on dalby, read-only ssh.
DONE: step 4 -> patched walls MEASURED 146.8 / 485.8 / 1840.7 s, cmp_failures=0.
      Baseline H=16 MEASURED 6864.1 s / 7,209,816 KB. Patched tree already has
      SUCC_MAX=16 + fail-closed abort and `H > 24` at line 457; exact mode still
      capped at `H > 16 || Nmax > 60` at line 465. Read `successors`/`gather`
      from results/cutcount_b1/cutcount_b1.cpp.59e90660.

DONE: step 5 (cost table) -> log-linear fit g=1.06917, residuals within 3.9%.
DONE: step 7 (successor bound) -> derived b <= floor((H-1)/2), one tighter than
      r4-perf and two tighter than r4-a; out[12] safe through H=22.

ABOUT TO: steps 5-9, write results/r4/r4-ladder.md and append queue rows.
DONE: steps 5-9 -> results/r4/r4-ladder.md filed (§0-§6 + NOT ESTABLISHED);
      5 queue rows R4-L1..R4-L5 appended to results/r4/queue.md.
      No compute run anywhere. Lane complete.
