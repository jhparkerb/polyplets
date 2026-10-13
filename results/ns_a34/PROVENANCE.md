# a(34)

a(34) = 515316838423862758858377704

Computed 2026-07-04 on dalby (80 cores) at revision `d1b6bcb` (P_15 newly
wired) by `scripts/term.sh 34`, production transfer matrix, 128-bit counter,
13,316.7 s of wall, peak RSS 6.44 GB. Heights 3..18 enumerated (H = 18 took
9336 s, H = 17 2376 s, H = 16 722 s); heights 1, 2 and 19..34 from the
closed forms P_0..P_15.

Files: `triangle.txt`, `perheight/h{1..34}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 34 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(33) match
  `results/ns_a{21..33}`.
- Growth: a(34)/a(33) = 6.9048.
- The whole run was repeated on ayr (x86_64, 32 cores, about 13.5 h) at the
  same revision; the triangle for n = 1..34 is byte-identical, including
  T(34,18). Same program, different machine, instruction set and toolchain.

T(34,18) = 23288787870043631158670332 lies on the k = 16 diagonal. P_16 is
fitted from T(33,17) and T(34,18), so this cell is an input to P_16 rather
than a check of it; the first cell P_16 predicts is T(35,19).
