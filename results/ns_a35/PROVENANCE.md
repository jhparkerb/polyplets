# a(35)

a(35) = 3561147281381782175236253062

Computed 2026-07-10 on two machines, each enumerating its heights against
its own disk, driven by `scripts/run_height_subset.sh`: dalby (ARM, 80
cores, revision `b8f13d41`) ran heights 1, 2 and 19..35, that is the
enumerated H = 19 plus every closed-form height, in 25,112.2 s of wall
(peak RSS 372 MB); ayr (x86_64, 32 cores, revision `d6e5679`, which
differs from `b8f13d41` only in docs and scripts) ran heights 3..18 in
19,831.6 s (peak RSS 339 MB). Production transfer matrix, 128-bit counter,
`--overlap-heights 35`, 1 GiB per worker on dalby and 1.5 GiB on ayr,
checkpoints every 300 s. P_16 was not wired at this revision, so H = 19 was
enumerated; heights 20..35 came from P_0..P_15.

Files: `triangle.txt`, `perheight/h{1..35}.out`.

Checks:

- All 35 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(34) match
  `results/ns_a{21..34}` (a(22)..a(25) by their recorded values, as those
  directories hold no two-column triangle).
- Growth: a(35)/a(34) = 6.9106.

T(35,19) = 121081244529132538941157409 is enumerated and is the first cell
P_16 (fitted from T(33,17) and T(34,18)) predicts; P_16 reproduces it, and
`orchestrator/diag_p16_test.go` holds the cell out of the fit and checks
that. The two machines ran different heights, so this run is not a
cross-machine repeat of any cell.
