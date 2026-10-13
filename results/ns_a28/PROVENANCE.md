# a(28)

a(28) = 4824589228356722264087

Computed 2026-07-02 on ayr at revision `7e28071`, 32 cores, 11,723.8 s of
wall, 353,201.8 cpu-s, peak RSS 786.9 MB, 128-bit counter. Heights 3..15
enumerated; heights 1, 2 and 16..28 from the closed forms P_0..P_12. The
a(29) run was on dalby at the same time.

Files: `triangle.txt`, `perheight/h{1..28}.out`, `cost_profile_ayr.tsv`.

Checks:

- All 28 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(27) match
  `results/ns_a2{1..7}`.
- Growth: a(28)/a(27) = 6.8616.
