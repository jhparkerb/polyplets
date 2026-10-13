# a(22), a(23)

    a(22) = 47255332844367680
    a(23) = 321749260511448732

Computed 2026-06-30 by the column-sweep transfer-matrix engine, split across
two machines: heights 1..16 on ayr, heights 17..23 on dalby. Height 18 was
the longest; heights 19..23 were filled from the closed forms for the
diagonals k = n − H ≤ 4.

Files: `a_n.txt` (a(1)..a(23)), `triangle.txt` (T(n,H)), `bfile.txt`.

## Checks

- a(20) and a(21) reproduce `results/ns_a21/` exactly, and the sequence
  matches A006770 through a(21).
- The closed forms for k = 5 and 6 (`diagonalCell` in `orchestrator/sweep.go`,
  commit `066f0ba`) reproduce the enumerated rows at H = 18 and 17 for
  n = 21, 22, 23; for example T(23,18) = 619065902379384 and
  T(23,17) = 1821918690703296.
- Heights 17 and 18, the two most expensive enumerated heights, were
  recomputed on ayr (x86-64; the production run was on dalby, ARM) on
  2026-07-01, 82,146 s of wall. Every value for n = 17..23 at both heights is
  identical to dalby's.
- Growth: a(22)/a(21) = 6.7953, a(23)/a(22) = 6.8087.

## P_7

With n = 15..23 enumerated at the k = 7 diagonal (nine points), the
polynomial P_7 in T(n,n−7) = P_7(n)·3^(n−22)/5040 is determined, with leading
coefficient 25^7/7!. It reproduces the enumerated T(22,15) =
1035856891052731 and T(23,16) = 4492550651512074. Its numerator
coefficients, degree 7 down to 0:

    6103515625, −119765625000, 812310625000, −2839739579250, 5194366339015,
    −1878923357430, −6841564107480, 7756630081200

These overflow int64 at every n where they are used, so the k = 7 closed
form is evaluated with big integers.
