# a(25)

    a(25) = 14994811325186658577

Computed 2026-07-02 on dalby at revision `54d41fc`. Heights 1..16
enumerated; heights 17..25 from the closed forms P_0..P_8 (`diagonalCell`
cases 0..8 in `orchestrator/sweep.go`). T(25,17) was the first cell P_8
predicted outside the n = 17..24 range it was fitted on.

Files: `swept_rows.txt` (the enumerated T(n,H), H = 3..16, n = 1..25; the
source data for the P_9 and P_10 derivations), `provenance.txt` and
`provenance_triangle.txt` (which cells were enumerated and which came from a
closed form; the H = 17 row is marked `?` there because the file was
generated before the check below).

## Checks

1. Height 17 enumerated on ayr (x86, gcc; the production run was ARM, clang)
   at the same revision, 45,841.5 s of wall on 30 cores:
   T(25,17) = 187767529262410933, equal to P_8's prediction.
2. Heights 3..16 re-enumerated on dalby with a 128-bit counter (the
   production run used 64-bit, which is exact only to a(25)). All fourteen
   rows are identical to `swept_rows.txt`.
3. Heights 3..16 for n ≤ 17 enumerated by the Redelmeier program
   (`build/g2 square8`), which shares no code with the transfer matrix: all
   119 cells agree.

Heights 1 and 2 and the diagonals k = 0, 1, 2 are proved closed forms
(`docs/proofs/`); k = 3..7 were checked against enumerated cells in the
a(23) and a(24) runs.
