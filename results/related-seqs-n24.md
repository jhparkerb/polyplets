# Related polyplet sequences extended to n=24

**Date:** 2026-07-04. **Method:** Burnside combine of Fixed (A006770) with
90°/180°/mirror fixed-point counts. **Source:** symmetric fixed-point counts
`runs/sym24/{r90,r180,hmirror,dmirror}.out` from `sym_extend 24` on dalby
(rev 799f80d, threaded: r90 ~0s, r180 6410s, hmirror 973s, dmirror 519s, all
rc=0). Combined by `scripts/derive_related.py runs/sym24`; Fixed from
`results/ns_a30/triangle.txt`, free polyominoes (A000105) from
`fixtures/b000105.txt`. (n=23 was the prior extent, from the ayr `sym_extend 23`
run; superseded here.)

**Threading note:** `sym_extend.sh` originally single-threaded the mirror types
(hmirror ~15047s / ~4.2h on one core at n=23, the actual frontier pole). They
parallelize over roots, so they were threaded (validated numerically identical
to the banked n=23 counts, hmirror 166s vs 15047s ≈ 90×). This made n=24 a
~2.2h job instead of ~half a day.

**Validation:** all **95** overlapping terms match the known OEIS values
(`oeis/A030222,A030233,A030234,A030235,A194596.txt`); Burnside numerators
divisible as required (Free/8, OneSided/4, (H+D)/2); asym = free − bilateral
identity holds at every n. R90 fixed points are structurally zero for
n ≢ 0,1 (mod 4) — R90(24)=9995 (24 ≡ 0) is the next nonzero after n=21;
R90(22)=R90(23)=0 correct. Extends the related-sequence thread to n=24 (each
frontier term costs ~2.6× the last on symcount_fast).

## New terms (n=20–24; known OEIS terminated at n=19)

Burnside:
Free = (Fixed + 2·R90 + R180 + 2·H + 2·D)/8, OneSided = (Fixed + 2·R90 + R180)/4,
Bilateral = (H + D)/2, Asym = Free − Bilateral, FreeNonPoly = Free − A000105.

| n | A030222 free | A030233 one-sided | A030234 bilateral | A030235 asym | A194596 free-non-poly |
|---|---|---|---|---|---|
| 20 | 128196711128365 | 256393397108358 | 25148372 | 128196685979993 | 128193840456415 |
| 21 | 869260590388450 | 1738521118535082 | 62241818 | 869260528146632 | 869249467327772 |
| 22 | 5906916748001325 | 11813833328245848 | 167756802 | 5906916580244523 | 5906873556143637 |
| 23 | 40218657830371643 | 80437315244081648 | 416661638 | 40218657413710005 | 40218489783363915 |
| 24 | 274333350132318510 | 548666699140240976 | 1124396044 | 274333349007922466 | 274332695132618107 |

## Follow-up (jasonp's call — publishing)
> **UPDATE:** these follow-ups are DONE — b-files for all six are staged
> (`results/b*_upload.txt`), and the related series were extended well past n=24
> (A030233 to n=34; the four D-dependent to n=32/33). See related-seqs-n32/n33.md.
- Generate full OEIS-format b-files for all five (b030222 currently prepped only
  to n=19 in `results/b030222_upload.txt`; the other four have none yet).
- Superseeker/OEIS submission is jasonp-triggered, not sent from here.
- Further extension: `sym_extend 25` is feasible (~2.6× ≈ 5-6h threaded) if a
  longer related series is wanted; symcount_fast has no efficient symmetric
  engine past this, so cost keeps climbing ~2.6×/term.
