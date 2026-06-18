# HANDOFF — a(19) of A006770, independent confirmation in progress

Polyomino project at `/Users/jasonp/src/polyominoes` (read `method-a19.md` and
`RESULTS.md` first). We are independently confirming a(19) of OEIS A006770 (fixed
polyplets / king-move animals): the value **151,609,203,011,580** was produced by
two decorrelated Redelmeier generation campaigns, and a column transfer-matrix
engine (`cpp/tma/`) is recounting it by a different algorithm as the final check.

That transfer-matrix run is in progress **ON AYR** (`ssh ayr`; working dir
`~/poly-tma`). Heights 1–16 are done (checkpoint files
`~/poly-tma/runs/tma-a19/h1.txt`..`h16.txt`, format `"n count"` = byHeight[H][n]).
Heights 17/18/19 run as three parallel jobs writing
`~/poly-tma/runs/tma-a19/h17.out`, `h18.out`, `h19.out` (same format) when each
finishes.

## Your job

1. **Check progress** (do NOT poll with sleep loops; check on request or when
   work completes):
   ```
   ssh ayr 'cd ~/poly-tma; pgrep -xc tma; for H in 17 18 19; do
     [ -s runs/tma-a19/h$H.out ] && echo "H$H done" || echo "H$H running"; done'
   ```
2. **Assemble** when all of h17/18/19.out are non-empty: a(n) = sum over H=1..19
   of byHeight[H][n], reading h1-16.txt + h17/18/19.out (sum the counts per n).
3. **Verify:** a(n) must equal A006770 (`fixtures/b006770.txt`) for n=1..18, and
   a(19) must equal **151,609,203,011,580**. Report any mismatch loudly (a low
   value would indicate the size-budget prune was inadmissible; a mismatch
   anywhere is a stop-everything event).
4. **On full match:** a(19) is confirmed by two independent algorithms. Update
   `RESULTS.md` R1 accordingly, finalize `method-a19.md`'s status line, and
   prepare the OEIS b-file (n=1..19) plus submission text citing both methods and
   the cross-checks (clang/ARM + GCC/x86, ASan/TSan clean, per-height marginals
   match the generation engine). Then tell the user it's ready to submit.

## Notes

- gympie (the local machine, 24 GB) is free; ayr has 78 GB so no OOM.
- Build with `make build/tma` (needs `-pthread`, C++20).
- The user is jasonp — give bare commands, no operational hand-holding; don't run
  destructive git/rm commands or kill processes without confirming; for
  background work, rely on completion notifications rather than sleep-polling.
- The discarded variable-width memory experiment is preserved as
  `variable-width-rows.patch` (reverted from the tree; not needed for this run).
