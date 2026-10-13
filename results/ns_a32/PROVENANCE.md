# a(32)

a(32) = 10818203977457804418974036

Computed 2026-07-03 on dalby (80 cores) at revision `3ffeed2b` (P_13 newly
wired) by `scripts/term.sh 32`, production transfer matrix, 128-bit counter,
10,945.3 s of wall, peak RSS 5.78 GB. Heights 3..18 enumerated (H = 18 took
7516 s, H = 17 2010 s); heights 1, 2 and 19..32 from the closed forms
P_0..P_13. Without P_13 the run would have had to enumerate H = 19.

Files: `triangle.txt`, `perheight/h{1..32}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 32 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(31) match
  `results/ns_a31/triangle.txt`.
- Growth: a(32)/a(31) = 6.8922.

The enumerated heights were computed once, by one program.
