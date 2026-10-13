# a(21)

a(21) = 6954084405510437

Computed on dalby, column kernel at revision `35eb9e1`, finished
2026-06-29T07:29:44-04:00 after 129,023 s (35.8 h) of wall. Every height was
enumerated, including H = 21, whose value is the closed form
T(21,21) = 3^20 = 3486784401.

Files: `triangle.txt` (a(n) for n = 1..21), `perheight/h{1..21}.out` (the
rows T(n,H) for each height H), `frontier_profile.txt`.

Checks:

- a(1)..a(19) match the A006770 b-file; a(20) matches `results/ns_a20/`.
- Heights 1..17 were also computed on ayr; the seventeen per-height files are
  byte-identical to dalby's.
- a(21)/a(20) = 6.78068.

Heights 18..21 were computed once at this time. Row 21 was later recomputed
in full by the Redelmeier enumerator (`results/redelmeier_row22/`), which
shares no counting logic with this program, and agrees.
