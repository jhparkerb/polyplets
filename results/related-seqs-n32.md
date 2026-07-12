# Related polyplet sequences to n=32 (n=34 for one-sided)

2026-07-05. Extends `results/related-seqs-n24.md` (same Burnside identities,
same combiner `scripts/derive_related.py`) using:

- Fixed = A006770 to n=34 (`results/ns_a34/triangle.txt` row sums);
- r90, r180, hmirror to n=34 (`runs/sym34/`, symtm on gympie/dalby);
- dmirror to n=32 (`runs/sym32/dmirror.out`, Shrink Ray strip farm: dalby
  S=26..32 + ayr S=25..1, both `b358e39`; coverage-checked sum
  `scripts/dmirror_sum.py 32`; prefix-matches runs/sym24 and runs/sym28
  exactly). D(32) = 2156235549286.

Validation: derive_related.py checks all 95 known OEIS terms across the five
sequences and asserts the /4 and /8 Burnside divisibilities at every n.
Confidence: inherits A006770's tiers -- T1 through n=19, T2 (single-algorithm,
multiply decorrelated) n=20..33; A030233(34) inherits a(34)'s T2- grade.

Reach: A030233 to n=34; the other four (need D) to n=32. **UPDATE: dmirror(33)
landed** and the four D-dependent terms at n=33 are banked (T3) — see
`results/related-seqs-n33.md`. (Original:) n=33 for the
D-dependent four requires dmirror(33) = dalby's strip farm plus the
P_4 closed forms for S>=29 -- those terms will be conjecture-assisted (T3),
comment-only for OEIS.

## New terms n=25..32 (n=20..24 in related-seqs-n24.md)

| n | A030222 free | A030233 one-sided | A030234 bilateral | A030235 asym | A194596 free-non-poly |
|---|---|---|---|---|---|
| 25 | 1874351417444073722 | 3748702832087014098 | 2801133346 | 1874351414642940376 | 1874348860217028958 |
| 26 | 12825939237386225482 | 25651878467205504568 | 7566946396 | 12825939229819279086 | 12825929238297403407 |
| 27 | 87890849023826053192 | 175781698028751634291 | 18900472093 | 87890849004925581099 | 87890809870815114705 |
| 28 | 603073653588819503780 | 1206147307126536440324 | 51102567236 | 603073653537716936544 | 603073500077718909177 |
| 29 | 4143141225805220756331 | 8286282451482505589564 | 127935923098 | 4143141225677284833233 | 4143140623183267694353 |
| 30 | 28496153390059675197641 | 56992306779773178547095 | 346171848187 | 28496153389713503349454 | 28496151021712637626389 |
| 31 | 196203952385726340537921 | 392407904770584270738465 | 868410337377 | 196203952384857930200544 | 196203943068019810549971 |
| 32 | 1352275497184284183618433 | 2704550994366217058008641 | 2351309228225 | 1352275497181932874390208 | 1352275460489267191905554 |

A030233 continues: a(33) = 18657870495104684580672401,
a(34) = 128829209605977867230343869 (T2- via A006770(34)).

## P_k dividend (same farm)

The completed farm pinned P_4-odd (S=23 strip) and forward-confirmed P_5
(exp fit unchanged, witnesses 4 -> 6); see results/dmirror-diagonals.md.

OEIS staging: `oeis/A03022*.txt`, `oeis/A194596.txt`, b-files
`results/b*_upload.txt`. Submission is jasonp's.
