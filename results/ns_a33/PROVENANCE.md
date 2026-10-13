# a(33)

a(33) = 74631481980411777590683952

Computed 2026-07-04 on dalby (80 cores) at revision `dcd7da4` (P_14 newly
wired) by `scripts/term.sh 33`, production transfer matrix, 128-bit counter,
12,200.3 s of wall, peak RSS 6.02 GB. Heights 3..18 enumerated (H = 18 took
8478 s, H = 17 2214 s, H = 16 676 s); heights 1, 2 and 19..33 from the
closed forms P_0..P_14.

Files: `triangle.txt`, `perheight/h{1..33}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 33 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(32) match
  `results/ns_a{21..32}`.
- T(33,18) = 2965403643769893816836542, the top enumerated cell, equals
  P_15(33)/3^13. P_15 had been derived but deliberately not wired, so this
  cell is an independent check of it.
- Growth: a(33)/a(32) = 6.8987.

The enumerated heights were computed once, by one program.
