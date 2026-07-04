# Related polyplet sequences extended to n=23

**Date:** 2026-07-04. **Method:** Burnside combine of Fixed (A006770) with
90°/180°/mirror fixed-point counts. **Source:** symmetric fixed-point counts
`runs/sym23/{r90,r180,hmirror,dmirror}.out` from `sym_extend 23` on ayr
(rev 3ffeed2, r90 wall 0.2s, dmirror 9084s, hmirror 15047s, r180 2552s, all
rc=0). Combined by `scripts/derive_related.py runs/sym23`; Fixed from
`results/ns_a30/triangle.txt`, free polyominoes (A000105) from
`fixtures/b000105.txt`.

**Validation:** all **95** overlapping terms match the known OEIS values
(`oeis/A030222,A030233,A030234,A030235,A194596.txt`); Burnside numerators
divisible as required (Free/8, OneSided/4, (H+D)/2); asym = free − bilateral
identity holds at every n. R90 fixed points are structurally zero for
n ≢ 0,1 (mod 4) — so R90(22)=R90(23)=0 is correct, not missing (nonzero R90
data reaches only n=21). This lands the related-sequence thread at its symcount
ceiling (n≈23, per the symcount_fast wall).

## New terms (n=20–23; known OEIS terminated at n=19)

Burnside:
Free = (Fixed + 2·R90 + R180 + 2·H + 2·D)/8, OneSided = (Fixed + 2·R90 + R180)/4,
Bilateral = (H + D)/2, Asym = Free − Bilateral, FreeNonPoly = Free − A000105.

| n | A030222 free | A030233 one-sided | A030234 bilateral | A030235 asym | A194596 free-non-poly |
|---|---|---|---|---|---|
| 20 | 128196711128365 | 256393397108358 | 25148372 | 128196685979993 | 128193840456415 |
| 21 | 869260590388450 | 1738521118535082 | 62241818 | 869260528146632 | 869249467327772 |
| 22 | 5906916748001325 | 11813833328245848 | 167756802 | 5906916580244523 | 5906873556143637 |
| 23 | 40218657830371643 | 80437315244081648 | 416661638 | 40218657413710005 | 40218489783363915 |

## Follow-up (jasonp's call — publishing)
- Generate full OEIS-format b-files for all five (b030222 currently prepped only
  to n=19 in `results/b030222_upload.txt`; the other four have none yet).
- Superseeker/OEIS submission is jasonp-triggered, not sent from here.
