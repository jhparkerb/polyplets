# a(39)

a(39) = 8182864667276277865830132493466

Computed 2026-07-24/25 on dalby (ARM Ampere Altra, 80 cores) at revision
`0057f2c5` by `FRONTIER_LEVERS=1 scripts/term.sh 39`, the first run with
zstd-compressed frontier files (64-record frames) and map outputs routed to
`/dev/shm` with a fallback to disk when a round is too large
(`docs/engine-record.md`): 39,957 s of wall, 2,070,672 cpu-s, peak RSS
1516 MB. Heights 3..20 enumerated; heights 1, 2 and 21..39 from the closed
forms P_k, k = 39 − H ≤ 18, H = 21 being P_18's first use. Disk peak
174.5 GB (`rundir_size.log`); `/dev/shm` held up to 42 GB, and 189 rounds
fell back to disk. The H = 20 columns took about 3500 s each at the same
127-128 M-record frontier as the a(38) run's 5500 s.

Files: `triangle.txt`, `perheight/h{1..39}.out`, `rundir_size.log`.

Checks:

- a(1)..a(20) match `fixtures/b006770.txt`; a(21) and a(26)..a(38) match the
  earlier triangles.
- T(39,39) = 3^38 and T(39,38) = 930·3^35 with 930 = P_1(39).
- This run's H = 20 enumeration reproduces the a(38) run's T(38,20) =
  39207474138446972682720171554 with the changed file formats.
- Growth: a(39)/a(38) = 6.9308.

T(39,20) = 305997488346556404027895440838 is enumerated and is the first of
the two cells needed to fit P_19; the second is T(40,21).
