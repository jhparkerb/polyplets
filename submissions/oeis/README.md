# OEIS submission staging — 4 novel king-lattice (polyplet) sequences

Staged drafts in OEIS internal format (`%I %S %T %U %N %C %F %H %e %Y %K %O %A`)
plus a b-file per sequence. **Nothing here is submitted.** jasonp pushes the actual
submission to oeis.org; Claude only preps and stages.

All four are king-move polyplet (A006770) statistics, 4-connected-background
("topological-dual") hole convention. Established cross-reference identities (NOT
resubmitted — these are known): max-hole AREA = A001971-shifted, max-perimeter =
A001168, min-perimeter = A027709. Total fixed polyplet count = A006770.

## Status table

| # | sequence | dir | terms (confirmed) | offset | keyword | status |
|---|----------|-----|-------------------|--------|---------|--------|
| 1 | Hole-free polyplet count | `1-holefree/` | 18 (n=1..18) | 1,2 | nonn,hard | READY — Superseeker-confirmed novel (2026-06-19) |
| 2 | One-hole polyplet count | `2-onehole/` | 15 (n=4..18) | 4,2 | nonn,hard | READY — Superseeker-confirmed novel (2026-06-19) |
| 3 | Square-bounding-box count | `3-square-bbox/` | 16 (n=1..16) | 1,2 | nonn,hard,more | READY — generated + marginal-verified to n=16 (ayr split run) 2026-06-22; Superseeker novelty check still owed |
| 4 | Max-distinct-holes count | `4-max-holes/` | 30 (n=1..30) | 1,6 | nonn,easy | READY — proven closed form; A337601 overlap is coincidence (see below) |

## Per-sequence detail and provenance

### 1. Hole-free (`1-holefree/draft.txt`, `b-holefree.txt`)
- Terms 1,4,20,109,622,...,16503616943998 for n=1..18.
- Source: `oeis/draft-A0-holefree.txt` + `oeis/b-draft-A0-holefree.txt` (master).
  Backing data is column k=0 of the hole triangle (`oeis/b-draft-hole-triangle.txt`).
- Provenance: column transfer matrix (thread #28), byte-identical to per-animal
  background flood (n<=14); row sums == A006770; n=15..18 cross-ISA confirmed
  (clang/ARM vs gcc/x86). Largest CONFIRMED n = 18.
- Novelty: Superseeker CLEAR (2026-06-19), full T001-T115 transform battery.

### 2. One-hole (`2-onehole/draft.txt`, `b-onehole.txt`)
- Terms 1,16,166,1456,...,4970078092354 for n=4..18.
- Source: `oeis/draft-A1-onehole.txt` + `oeis/b-draft-A1-onehole.txt` (master).
  Backing data is column k=1 of the hole triangle.
- Provenance: same engine as #1; n=15..18 cross-ISA confirmed. Largest CONFIRMED n = 18.
- Novelty: Superseeker CLEAR (2026-06-19).

### 3. Square bounding box (`3-square-bbox/draft.txt`, `b-square-bbox.txt`)
- Terms 1,2,6,36,148,882,4648,27025,159490,951160,5803942,35903114,223968746,1411623422,
  8978749222,57490061438 for n=1..16.
- Definition: fixed n-cell polyplets whose minimal bounding box is square (w == h).
- Provenance: generated 2026-06-22 by Redelmeier enumeration (`build/g2 square8 N --per-box`),
  binning each fixed polyplet by bounding-box (w,h) and summing the w==h diagonal. n=1..14
  on gympie; n=15,16 via a 20-worker `--split` run on ayr (scripts/bbox_split.sh,
  bbox_combine.py). The FULL (w,h) marginal was verified term-by-term == A006770(n)
  through n=16 (the engine's own gate). Explicit enumeration, so terms get exponentially
  harder; n>=17 (3.3e12 animals) wants a wider/longer split. Largest CONFIRMED n = 16.
- Novelty: **Superseeker check still owed.** The earlier "verified vs OEIS" log note was
  only a plain prefix search, not a transform battery. Ready-to-send lookup body:
  `lookup 1 2 6 36 148 882 4648 27025 159490 951160 5803942 35903114 223968746 1411623422 8978749222 57490061438`

### 4. Max distinct holes (`4-max-holes/draft.txt`, `b-max-holes.txt`)
- Terms 0,0,0,1,1,2,2,3,4,4,5,6,6,7,8,9,9,10,11,12,... (n=1..30 in the b-file).
- Source: `oeis/draft-maxholecount.txt` on branch `explore/theorem-multihole`;
  b-file regenerated here from the proven formula.
- Definition: max number of bounded 4-connected complement components over n-cell
  polyplets. **Proven closed form** a(n) = n + 1 - A027709(n)/2 (Pick's theorem on
  the even sublattice / min-perimeter polyomino); brute-verified n<=9, formula exact
  for all n, so the b-file extends cleanly to n=30. Keyword `easy`.
- A337601 is NOT the polyomino max-holes analogue — it counts coprime triples
  (verified against oeis.org 2026-07-16; an earlier draft mischaracterized it from a
  prefix-search hit). The overlap is numeric coincidence: a(n) = A337601(n-1) for
  n=1..12, diverging at a(13)=6 vs A337601(12)=8. The honest polyomino cross-ref is
  A118797 (cells in smallest polyomino with n holes; A118797(1)=7 = the holey
  heptomino, brute-confirmed, vs the 4-cell diamond here). No OEIS entry exists for
  max-holes-of-an-n-omino itself.
- Novelty: Superseeker-checked novel (per oeis/README provenance; prefix matched only
  unrelated short sequences before extension).

## Status summary
All four sequences are staged with draft + b-file. Sequences 1, 2, 4 are
submission-ready (Superseeker-confirmed novel). Sequence 3 (square bounding box) is now
generated and marginal-verified through n=14; the one remaining step before submission is
a Superseeker novelty pass (lookup string in the section above) — jasonp sends it.
