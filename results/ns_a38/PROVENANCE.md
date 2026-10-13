# a(38)

a(38) = 1180654489101178485738417779914

Computed 2026-07-23/24 on dalby (ARM Ampere Altra, 80 cores) at revision
`8ce1bc5c` by `scripts/term.sh 38`: 56,994 s of wall, 1,783,598 cpu-s, peak
RSS 971 MB. Heights 3..20 enumerated (the first run to enumerate H = 20);
heights 1, 2 and 21..38 from the closed forms P_k, k = 38 − H ≤ 17. Disk
peak 221.5 GB (`rundir_size.log`). At H = 20 the frontier peaked at 127.3 M
records, 2.8 times H = 19's 45.3 M; the peak columns took about 5500 s each
with roughly 14 effective cores, the rest lost to disk stalls on the NVMe
mirror.

Files: `triangle.txt`, `perheight/h{1..38}.out`, `rundir_size.log`.

Checks:

- a(1)..a(20) match `fixtures/b006770.txt`; a(21) and a(26)..a(37) match the
  earlier triangles.
- T(38,38) = 3^37 and T(38,37) = 905·3^34 with 905 = P_1(38).
- The enumerated T(37,20) = 4956437442714322066925263218 equals the P_17
  value the a(37) run used for that cell: P_17's first check on a cell
  outside its fit.
- Growth: a(38)/a(37) = 6.9261.

With T(37,19) and T(38,20) both enumerated, P_18 was derived
(`scripts/derive_pk_fast.py 18`; leading coefficient 25^18/18!,
integer-valued) and wired as `diagCoeffTable[18]`, tested in
`orchestrator/diag_p18_test.go`.
