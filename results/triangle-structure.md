# The Atom Ledger: dependency structure of the polyplet triangle T(n,H)

Date: 2026-07-10 (analysis snapshot; a(36) is now also banked at `results/ns_a36/` —
one more holdout row available, structural conclusions unchanged). Data: the banked
35-row triangle `results/ns_a35/perheight/h{H}.out`
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

**Restated honestly at the close (AUDIT-2026-07-30 S4).** The percentages
above are cell counts that credit each P_k diagonal as a second source for
every cell in its onset — including the cells that diagonal itself produced.
Over the closed n<=40 triangle (820 cells): doc-style union **90.7%**, honest
cells **67.6%** (P_k credited only on really-swept cells), strip alone
**50.4%**. And cells are the flattering denominator — by MASS the strip run
as banked (H<=14 **and n<=36**) touches no cell of rows 37-40, so it
second-sources 0% of a(37)-a(40). The N=40 extension launched 2026-07-30
covers H<=14 on those rows: 53.8% / 50.8% / 47.9% / 45.0% of a(37)-a(40).
Full table: `results/strip-engine.md`.

## 5. The lever

Don't fit the middle atoms — **compute** them: an independent naive strip
transfer matrix (connectivity-partition states, zero shared enumeration with
the kink kernel) computes C_H(n) directly; one validated
strip column second-sources the whole T column via the differencing identity.
(Scope, as built: disjoint from the kink kernel, but the connectivity rule
itself is the same union-find as `core/transition.h` — see the Independence
section of `results/strip-engine.md`.)
Cheap for H up to ~12–14 (state-count measurement pending). This is the same
conclusion as the a(23)-era note — the residual validation gap closes only by
independent reimplementation — but now with the exact coverage arithmetic and
the atom factorization showing *why* nothing cheaper can exist.

## 6. Why no bounded stencil can exist — the root-separation theorem

The stencil hunts didn't need to be run: the atom structure *proves* their
emptiness, for every polynomial degree and every factorial/exponential
coefficient class at once.

**Ingredients (measured):** atoms q_1..q_4 are squarefree (gcd(q,q')=1) and
pairwise coprime, so p_H = q_H q_{H-1} q_{H-2} is squarefree and
T_H(n) = Σ_λ c_λ λ^n over distinct roots. Minimality of the measured orders
(1,3,7,15) forces every c_λ ≠ 0 — if any root were absent the minimal
recurrence would be shorter. (For H ≥ 5 the same is the structural
expectation; a dropped root would only dent the bound, not break it.)

**Subsumption:** in a finite-stencil relation, coefficients built from
factorials of integer linear forms in (n,H) enter only via ratios of shifted
factorials, and m!/(m−r)! is a polynomial of degree r; fixed exponentials
cancel to constants. So "polynomial coefficients in (n,H)" is the whole class.

**Theorem.** Any relation Σ_{j≤J,δ} p_{jδ}(n,H)·T(n−j,H−δ) = 0 with
polynomial coefficients, holding for all n at a window of columns, has
depth J ≥ deg q_{H_top}, where H_top is the highest column whose coefficient
face is not identically zero.

*Proof.* Specialize H (coefficients become polynomials in n). Let λ be a root
of q_{H_top}. By coprimality, λ appears in columns H_top, H_top+1, H_top+2
only — of these only H_top is in the stencil. The λ^n-component of the
relation is therefore Σ_j p_{j}(n)·c_λ·λ^{n−j} = 0, i.e.
Σ_j p_j(n)·λ^{−j} = 0: one CONSTANT-coefficient linear condition on
(p_0,…,p_J) over C(n). Over all deg q_{H_top} distinct roots this is a
Vandermonde system: if J+1 ≤ deg q_{H_top} it forces the whole H_top face to
vanish. Recurse downward. ∎  (Galois conjugation extends this to any
algebraic constant field.)

**Consequences.** Any relation touching column 5 needs depth ≥ 29; column 6
≥ 68. Even the true depth-29 relation for C_5 (its own atom recurrence) has
zero testable holdout from 35 rows. The brute-force sweeps
(triangle_relations2/3.py) are instances J ≤ 4, degree ≤ 6 of a statement now
proved for all J < 29 and all degrees.

**The exact escape hatches** (everything the theorem does not forbid):
1. *Unbounded stencils* — the diagonal exp-recurrence
   k·P_k = Σ_{j≤k} j(a_j+b_j n)P_{k−j} has depth growing with k. Exists,
   deployed (scripts/derive_pk_fast.py).
2. *Directions of non-constant column composition* — a diagonal (k = n−H
   fixed) mixes an unbounded set of atoms as n grows, so root-separation
   does not apply; that is exactly why the P_k closed forms can exist. Any
   undiscovered relation must live in this class: transformed coordinates
   whose stencil support crosses columns.
3. *Non-holonomic coefficients* (n^n, q^{n²}) — outside any usable class.

Together with §3, the search space is now closed: column/row-direction
finite relations are provably impossible; diagonal-direction structure is
the only open ground, and P_k already occupies its first floor.
