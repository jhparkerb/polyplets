# a(30)

a(30) = 227969227118066423789154

Computed 2026-07-03 on dalby (ARM Neoverse-N1, 80 cores) at revision
`d1554bd`, 3711 s of wall, 128-bit counter. This was the first term
computed with the production transfer matrix (`--kernel kink`), after it
had matched the earlier column kernel cell by cell at n = 29. Options:
`--counter u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain 0.05`.
Peak RSS about 76 MB. Heights 3..17 enumerated, H = 17 being 45% of the
wall; heights 1, 2 and 18..30 from the closed forms P_0..P_12.

Files: `triangle.txt`, `perheight/h{1..30}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 30 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(29) match
  `results/ns_a2{1..9}`.
- Growth: a(30)/a(29) = 6.8779.
- Height 17 was started on ayr (x86-64) with the column kernel as a
  cross-check of both machine and kernel; the first column's frontier count
  matched (65791). This record does not say whether it finished.

T(30,17) = 9142099138689979555656 (enumerated) is a point on the k = 13
diagonal, whose closed form was not yet known; T(30,18) =
5455070058849476986528 came from P_12.
