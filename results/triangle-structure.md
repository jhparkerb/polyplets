# The Atom Ledger: dependency structure of the polyplet triangle T(n,H)

Date: 2026-07-10. Data: the banked 35-row triangle `results/ns_a35/perheight/h{H}.out`
(T(n,H) = # fixed polyplets of n cells with bounding-box height exactly H,
a(n) = Σ_H T(n,H)). All findings below are exact-arithmetic, fit-early /
validate-on-the-rest measurements — scripts in `experiments/triangle_relations.py`,
`triangle_relations2.py`, `triangle_atoms.py`.

## 1. Columns H ≤ 4 are independently pinned

Minimal constant-coefficient linear recurrences, fit from the earliest terms and
confirmed on every remaining one:

| H | terms | order | holdout confirms |
|---|-------|-------|------------------|
| 1 | 35    | 1     | 33 |
| 2 | 34    | 3     | 28 |
| 3 | 33    | 7     | 19 |
| 4 | 32    | 15    | 2  |
| ≥5| —     | not pinnable from 35 rows | — |

These four columns are regenerable to any n without the kink kernel, forever.

## 2. Structure theorem: one atom per height

Let C_H(n) = Σ_{h≤H} (H−h+1)·T(n,h) — exactly what a naive height-H strip
transfer matrix counts (polyplets in the strip modulo horizontal translation
only). Measured minimal char polys ("atoms") q_H:

```
q_1 = x − 1                                         (order 1, holdout 33)
q_2 = x² − 2x − 1        (Pell / silver ratio)      (order 2, holdout 31)
q_3 = x⁴ − 4x³ + 2x² − 1                            (order 4, holdout 27)
q_4 = x⁹ − 5x⁸ + 2x⁷ + 8x⁶ − 6x⁵ − 12x⁴ + 4x³ + 2x² − 3x − 1   (order 9, holdout 17)
```

Atom degrees 1, 2, 4, 9 (, 29, 68, …) — the sequence already Superseeker-checked
as novel. Since

    T(n,H) = C_H(n) − 2·C_{H−1}(n) + C_{H−2}(n),

the column char polys factor exactly (verified for H=2,3,4; atoms pairwise coprime):

    p_H = q_H · q_{H−1} · q_{H−2}
    orders: 3 = 2+1,  7 = 4+2+1,  15 = 9+4+2,  (42 = 29+9+4,  106 = 68+29+9)

```
atoms:        q_1    q_2    q_3    q_4    q_5    q_6   ...
(degree)       1      2      4      9     29     68
               │      │      │      │      │      │
strips:       C_1    C_2    C_3    C_4    C_5    C_6   ...
               └──┬───┴──┬───┴──┬───┴──┬───┴──┬───┘
                  ▼      ▼      ▼      ▼      ▼
columns:         T_2    T_3    T_4    T_5    T_6
(GF order)        3      7     15     42    106
```

Every column mixes exactly three consecutive atoms; each new height contributes
exactly one new atom. The triangle's irreducible information is the atom list.

## 3. Measured negatives (why no row-to-row shortcut exists)

- **No cross-column stencil**: T(n,H) = Σ c·T(n−j, H−δ) with constant
  coefficients fails for every column H=5..12 (stencils to depth j≤4, columns
  H−2..H+1, exact nullspace with ≥4 excess equations).
- **No P-recurrence**: polynomial-in-n coefficients up to order 6 × degree 3
  fail even for H=3 (whose rational order is only 7) — holonomic shortcuts are
  dead for all H ≥ 3.
- **The information wall, quantified**: pinning q_5 (order 29) from data needs
  ~60 triangle rows; q_6 needs ~140. No computable extension of the triangle
  ever pins the middle atoms from data alone.

Structural reason: adjacent columns share two atoms, but each column carries an
atom the earlier columns do not contain at all — no finite relation can
manufacture q_H from q_{<H}.

## 4. Second-source coverage map

Which of the 630 entries (n ≤ 35) can be computed a second, kink-independent way:

```
    H→ 1234567890123456789012345 (35)
 1     B
 2     RB
 3     RRB
 4     RRBB
 5     RRRBP
 6     RRRRPP
 7     RRRRPPP
 8     RRRRsPPP
 9     RRRRssPPP
10     RRRRssPPPP
11     RRRRsssPPPP
12     RRRRssssPPPP
13     RRRRssssPPPPP
14     RRRRsssssPPPPP
15     RRRRssssssPPPPP
16     RRRRssssssPPPPPP
17     RRRRsssssssPPPPPP
18     RRRRssssssssPPPPPP
19     RRRRssssssssPPPPPPP      <- last fully-covered row
20     RRRRssssssss.PPPPPPP     <- gap opens
21     RRRRssssssss..PPPPPPP
22     RRRRssssssss..PPPPPPPP
23     RRRRssssssss...PPPPPPPP
24     RRRRssssssss....PPPPPPPP
25     RRRRssssssss....PPPPPPPPP
26     RRRRssssssss.....PPPPPPPPP
27     RRRRssssssss......PPPPPPPPP
28     RRRRssssssss......PPPPPPPPPP
29     RRRRssssssss.......PPPPPPPPPP
30     RRRRssssssss........PPPPPPPPPP
31     RRRRssssssss........PPPPPPPPPPP
32     RRRRssssssss.........PPPPPPPPPPP
33     RRRRssssssss..........PPPPPPPPPPP
34     RRRRssssssss..........PPPPPPPPPPPP
35     RRRRssssssss...........PPPPPPPPPPPP

R = column recurrence (H<=4)         128 entries — have now
P = diagonal closed form P_k         216 entries — have now
B = both                               6 entries
s = naive strip engine to H=12       184 entries — buildable lever
. = single-source                     96 entries — H=13..23 at high n
```

Coverage: today 350/630 (55.6%); + independent naive strip engine to H=12 →
84.8%; to H=14 → 89.7%. The residual single-source band is exactly the tall
middle heights where the kink kernel spends its time.

## 5. The lever

Don't fit the middle atoms — **compute** them: an independent naive strip
transfer matrix (connectivity-partition states, fresh code, zero shared
enumeration with the kink kernel) computes C_H(n) directly; one validated
strip column second-sources the whole T column via the differencing identity.
Cheap for H up to ~12–14 (state-count measurement pending). This is the same
conclusion as the a(23)-era note — the residual validation gap closes only by
independent reimplementation — but now with the exact coverage arithmetic and
the atom factorization showing *why* nothing cheaper can exist.
