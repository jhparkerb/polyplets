# a(24)

    a(24) = 2194666793369310473

Computed 2026-07-01 on dalby at revision `5fadde3` (clang-19 build).
Heights 1..15 came from a run of the same revision on 2026-06-30; height 16
was enumerated in this run (80 cores, 1 GiB per worker, 4870.3 s of wall,
peak RSS 628.8 MB); heights 1, 2 and 17..24 were filled from the closed
forms for k = n − H ≤ 7, which had been checked against enumerated cells
through a(23). Heights 1 and 2 were recomputed in this run and matched the
earlier files.

Files: `triangle.txt` (T(n,H), n = 1..24), `a_n.txt` (a(1)..a(24)).

## Checks

- a(1)..a(23) reproduce every earlier value (`build/ns/combine --compare`
  against `fixtures/b006770.txt`, which ends at a(20), and by hand against
  `results/ns_a23/RESULT.md` for a(21)..a(23)).
- T(24,16) = 42594477635772598, the new enumerated cell, equals the value
  predicted for it before the run from the k = 8 pattern in
  `results/diagonal-formula.md` (leading coefficient 25^8/8! and the
  quadratic sum-of-roots pattern).
- Growth: a(22)/a(21) = 6.7953, a(23)/a(22) = 6.8087, a(24)/a(23) = 6.8210.

## P_8

With T(24,16), P_8 in T(n,n−8) = P_8(n)·3^(n−25) is determined from its
eight enumerated points n = 17..24, and the fit reproduces all eight. It is
wired as case 8 of `diagonalCell` in `orchestrator/sweep.go` (big-integer
Horner evaluation) and pinned by `TestHeightNm2Formula` in
`orchestrator/heightnm2_test.go`, which also records its prediction for
T(25,17); that cell was enumerated in the a(25) run and agrees
(`results/ns_a25/RESULT.md`).
