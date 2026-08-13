# r4-perf — progress

ABOUT TO: step 1-3, read r4-a.md, PROVENANCE, ladder gate, and the engine source at 48ac108
DONE: steps 1-3 -> engine read line by line; key finding: (m0,m1) == (1,0) on
every successor except the single fresh-colour one (cutcount_b1.cpp:154,159,171
vs 172), so ~90% of edges need no multiply and no reduction at all.
ABOUT TO: step 4, read the live dalby modp log
DONE: step 4 -> H=15 modp wall 2065.1 s, peak_rss 2,420,292 KB; H=16 in flight,
13/41 columns at 2074.9 s, steady ~175 s/column -> ~7,200 s projected.
ABOUT TO: step 5, settle the Succ out[12] bound by case analysis
DONE: step 5 -> b <= floor((H+1)/2), so ns <= floor((H+1)/2)+2; out[12] is SAFE
through H=20 and overflows at H=21. Reproduces the source's own "<= 9 for H<=16"
comment as a loose bound (true value 8).
ABOUT TO: step 6-8, write the lever list, the reprice table, the patch, the job
request and the queue rows into results/r4/r4-perf.md
DONE: patch -> experiments/tristruct/r4_perf_fastmodp.patch (200 lines,
`patch --dry-run -p1` clean against a fresh `git show 48ac108` copy; NEVER built,
NEVER run).
DONE: steps 6-8 -> results/r4/r4-perf.md filed complete (5 sections + NOT
ESTABLISHED); queue rows R4-P1..R4-P4 appended to results/r4/queue.md.
FILED. Nothing outstanding.
