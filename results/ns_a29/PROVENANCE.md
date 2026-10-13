# a(29)

a(29) = 33145129805782422061325

Computed 2026-07-02 on dalby at revision `7e28071`, 80 cores, 26,202.2 s of
wall, 1,960,646.8 cpu-s, peak RSS 1647.1 MB, 128-bit counter. Heights 3..16
enumerated; heights 1, 2 and 17..29 from the closed forms P_0..P_12. The
a(28) run was on ayr at the same time.

Files: `triangle.txt`, `perheight/h{1..29}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 29 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(28) match
  `results/ns_a2{1..8}`.
- Growth: a(29)/a(28) = 6.8700.
