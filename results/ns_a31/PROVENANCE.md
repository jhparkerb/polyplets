# a(31)

a(31) = 1569631619081324581014300

Computed 2026-07-03 on dalby (80 cores) at revision `2ce164b` by
`scripts/term.sh 31`, production transfer matrix, 128-bit counter,
10,003.1 s of wall, peak RSS 5.9 GB. Heights 3..18 enumerated (H = 18 took
6827 s, H = 17 1838 s; `cost_profile_dalby.tsv`); heights 1, 2 and 19..31
from the closed forms P_0..P_12.

Files: `triangle.txt`, `perheight/h{1..31}.out`, `cost_profile_dalby.tsv`.

Checks:

- All 31 heights present exactly once in the combine.
- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(30) match
  `results/b006770_upload.txt`.
- Growth: a(31)/a(30) = 6.8853.

The enumerated heights were computed once, by one program.
