# r4-gen7 progress

DONE: plan -> results/r4/r4-gen7.plan.md
ABOUT TO: step 1 -- read charter + queue index + predecessors r4-gen{,2,3,4,5}, harvest row ids
DONE: step 1 -> do-not-repeat list built; nearest prior art is R4-G2-17/18/19/20/21/22, R4-G3-12/13, R4-G5-17, R4-G4* ; gen6 is live on the oracle angle
ABOUT TO: step 2 -- verify the four instrument premises in my own brief off disk
DONE: step 2 -> THREE OF FOUR PREMISES FAIL. cross-ISA byte-identity NOT DONE (P4 is a proposal, r4-spinproj §3.5; r4-spinbuild:416 calls it "optional"); B1 flood-fill validation NOT DONE (r4_indoracle_brute.py has no .log anywhere, JOB-IND-1 unrun); brute force reaches n<=8 not n<=10 (r4_spin_reference_gympie.log grower totals stop at 23592). Spin 88.6 s / 640 cells / 90.7 MB IS real and dalby-measured. Filed as R4-G7-00.
DONE: read-only ssh dalby -> r4_spin_m21.log is LIVE and growing (06:27); spin_m16.txt + 4 gate outputs banked in ~/src/pm-b1-perf/results/r4/
DONE: read gather()/successors() in results/cutcount_b1/cutcount_b1.cpp.59e90660:128-170 and the Mutant enum in r4_spin_engine.cpp:324-362
ABOUT TO: step 3/4 -- write rows into results/r4/r4-gen7.md, killing in place where desk arithmetic suffices
DONE: step 3/4 -> 24 rows filed in results/r4/r4-gen7.md, 6 of them CLOSED WITH THE KILL at filing
ABOUT TO: step 5 -- second pass on what my own rows share
DONE: step 5 -> §5 written
ABOUT TO: step 6 -- append 24 rows to results/r4/queue.md
DONE: step 6 -> appended, queue row count 166 -> 190
