# Cross-lattice control: falsification verdicts on the triangle-hunt survivors

2026-08-11, Proposer 4 (cross-lattice control) of the triangle-structure
hunt (`docs/triangle-structure-team-brief.md`). Scripts under
`experiments/tristruct/`: `xlat_enum.cpp` (independent Redelmeier
enumerator, king/square/tri — crosschecked in
`results/triangle-hunt-enumerator-crosscheck.md`, zero mismatches),
`xlat_striptm.py` (independent column transfer matrix for square and
triangular lattices, exact ints), `xlat_verdicts.py` (order/period
measurements), `xlat_gf2factor.py` (mod-2 mechanism). Data:
`experiments/tristruct/data/square_col_tm_n140.txt`,
`data/tri_col_tm_n140.txt` (exact-height columns H ≤ 5, n ≤ 140).

**Role.** Not a proposer of king relations: a falsification service. Any
relation with a real mechanism should have an analogue on a neighbouring
lattice, where published counts nobody here produced settle it; and the
team's fitting procedure, run where the answer is published, is either
exposed or exonerated.

## Data provenance (everything is at least two-source)

- Square and triangular columns come from a column transfer matrix written
  from the lattice definition only (no repo kernel consulted), and are
  cross-checked cell-for-cell against this proposer's independent
  Redelmeier enumerator (`build/xlat_enum`, a different algorithm): 60/60
  square cells (H ≤ 5, n ≤ 14) and 64/64 tri cells (n ≤ 16) match.
- Row sums of the enumerator match published totals: square = **A001168**
  (fixed polyominoes, 12 terms compared), tri = **A001420** (fixed
  polyiamonds, 14 terms compared).
- The square H = 3 column IS published: **A335606** (fixed n-ominoes with
  convex-hull width 3, R. J. Mathar 2020; width there = height here by
  x↔y transpose symmetry of fixed counts). All 31 published terms
  (n ≤ 33) match the TM column exactly.
- The square H = 4 column and both tri columns are not in OEIS (searched
  2026-08-11: `1,12,68,282,1027,3468,11132,34558` and
  `2,12,46,142,376,914,2132,4852` return nothing); for those the two
  independent in-house sources above are the evidence.

## Procedure exoneration (the strongest single fact here)

The same fit-low/predict-high procedure that found the king survivors,
applied blind to the square H = 3 column, returns an order-14
constant-coefficient recurrence with coefficients
`[5,-6,-4,8,1,2,-8,0,-1,9,-2,-1,-3,1]` (fitted on the first 28 terms, 110
holdout terms exact). A335606's published recurrence is **identical,
coefficient for coefficient**. The procedure, run where the answer is
published, recovers the published answer — it does not manufacture
relations, and it contradicts no published count anywhere in this exercise.

## Verdict table: the four machine-sweep survivors

The four Wave-0 sweep survivors (later culled KNOWN-COINCIDENT by
`known.py`), tested for lattice analogues. King columns are the banked
triangle (H = 3,4 real-sweep provenance at every n); square/tri as above.
All arithmetic exact; "EXACT" periods come from cycle detection on the
verified recurrence's residue state, not from a finite window.

| survivor (king) | square analogue | tri analogue | verdict |
|---|---|---|---|
| S4: T(n,3) has order-7 C-finite recurrence | order **14** (= published A335606 recurrence), 110 holdout terms | order **23**, 91 holdout terms | **LATTICE-GENERIC** (mechanism: rational strip GF). King's order 7 is the banked column order (`results/triangle-structure.md` §1: orders 3,7,15,42,106) — restatement, as the lead's prior said |
| S2: T(n,3) mod 2 eventually periodic, period 4 | periodic, but period **62** | periodic, period **1** (≡ 0 for n ≥ 4) | periodicity itself is **GENERIC** (a theorem for any C-finite integer sequence, zero information); the tiny period is **KING-SPECIFIC** — see mechanism below |
| S1: T(n,3) mod 4 period 8 | period **868** | period **682** | same split: existence generic, smallness king-specific |
| S3: T(n,4) mod 2 period 4 | period **4**, and the residue word is **identical**: T(n,4) odd ⟺ n ≡ 0 (mod 4), on both lattices (king n ≤ 40 banked; square n ≤ 140 exact) | tri: window n ≤ 140 shows pre=6, period 14 (no verified recurrence for tri H=4, order > 45) | **LATTICE-GENERIC, shared mechanism** — see the involution note below. NOT king structure |

Full measurement table (orders, all moduli 2,3,4,8, preperiods):
`experiments/tristruct/data/xlat_verdicts_out.txt`. Notables: king
T(n,3) periods mod 2/4/8 are 4/8/16 and T(n,4) gives 4/16/32 — a clean
2-adic tower; square's are 62/868/1736 (H=3) and 4/94488/1322832 (H=4);
mod 3 the king H=4 and square H=3 columns both have period 85280.

## Mechanism notes

**Why king's periods are tiny (S1/S2): total unipotency mod 2.**
Characteristic polynomials of the verified recurrences factored over GF(2)
(`xlat_gf2factor.py`):

| column | chi mod 2 |
|---|---|
| king T(n,3), r=7 | (x+1)^7 — fully unipotent |
| king T(n,4), r=15 | (x+1)^15 — fully unipotent |
| square T(n,3), r=14 | (x+1)^6 · (x³+x²+1) · (x⁵+x³+x²+x+1) |
| square T(n,4), r=39 | (x+1)^20 · (x²+x+1)² · (x³+x²+1) · (x⁵+x³+x²+x+1) · (x⁷+x+1) |
| tri T(n,3), r=23 | x³ · (x+1)^10 · (x^10+x^7+x^6+x^5+x³+x²+1) |

A fully unipotent companion matrix mod 2 forces period a power of 2 (≤
2^⌈log2 r⌉); a primitive degree-d factor forces a factor of 2^d − 1 into
the period (square H=3's observed 62 = 2·31 is the degree-5 factor's order;
its degree-3 factor's order 7 is killed by the initial vector). So the
king-specific content of S1/S2 is precisely: **both king column
characteristic polynomials are ≡ (x+1)^r mod 2**. That is a real, clean
2-adic fact about the king strip transfer matrices — but it is a property
of the banked column GFs, i.e. more resolution on KNOWN-COINCIDENT
material, not an independent check on a(40). (And it does not persist:
see the q_5 factorization below — unipotency is an H ≤ 4 accident.)

**Why S3 transfers verbatim: the rotation involution.** 180° rotation is a
symmetry of both lattices, preserves n and box height, and acts on
translation classes with orbits of size 1 or 2; hence T(n,H) ≡
#{centrosymmetric animals} (mod 2) on ANY such lattice. The parity of
T(n,H) is really the parity of a much smaller symmetric-animal count —
which is why identical residue words can appear on different lattices. S3
is the H = 4 instance. This is the same mechanism family as proposer 2's
proved parity theorem (`results/triangle-hunt-klein-parity.md`), reached
independently; their midline-reflection version is the proved, stronger
statement.

## The other proposers' filed relations, tested cross-lattice

`experiments/tristruct/xlat_proposer_checks.py` (output:
`experiments/tristruct/data/xlat_proposer_checks_out.txt`).

**P2's parity theorem** (`results/triangle-hunt-klein-parity.md`: T(n,H)
even for n odd, H even) — **TRANSFERS, 0 violations in 310 cells**: square
all-H enumerator cells n ≤ 14 (21 region cells), tri n ≤ 16 (16), square TM
H = 2,4 to n = 140 (137), tri TM H = 2,4 to n = 140 (136), all even. This
is what a proof-backed mechanism looks like under lattice change: the
midline-reflection involution is a symmetry of both lattices (of tri
exactly when H is even, which is the region), so the theorem carries with
its proof. Verdict: **mechanism confirmed, lattice-generic**.

**P3's atom ladder** (`results/triangle-hunt-atoms-ab-initio.md`: strip
counts C_H have one-atom annihilators, and exact-height column order =
d_H + d_{H−1} + d_{H−2}; king 3=2+1, 7=4+2+1, 15=9+4+2):

| lattice | ord C_H, H=1..4 | additivity |
|---|---|---|
| king (banked) | 1, 2, 4, 9 | 7 = 4+2+1, 15 = 9+4+2 ✓ |
| square | 1, 3, 10, 26 | **14 = 10+3+1 ✓, 39 = 26+10+3 ✓** |
| tri | 1, 7, 17, >45 | **23 ≠ 17+7+1 = 25 — FAILS by 2** |

Verdict: the one-atom / additive-order mechanism is **lattice-generic on
king and square, but NOT universal** — on the triangular lattice a
degree-2 cancellation occurs at H = 3 (the three-atom product shares a
factor, or the numerator cancels one). Two consequences for the team:
(i) additivity holding on king is a genuine verified fact about the king
atoms (P3 proved coprimality there), not an automatic consequence of the
second-difference construction — tri is the counterexample; (ii) P3's
purity claim should not be assumed for other lattices without checking.

**King mod-2 unipotency dies at H = 5** (settled using P3's ab-initio
atoms `experiments/tristruct/data/p3_atoms_q.txt`, reduced mod 2 with
`xlat_gf2factor.py` machinery): q_1..q_4 are all ≡ (x+1)^deg mod 2 —
consistent with the fully unipotent H = 3,4 columns above — but
q_5 mod 2 = x²·(x+1)⁹·(x²+x+1)·(x⁷+x⁶+1)·(x⁹+x⁷+x⁵+x⁴+x³+x²+1), with
non-unipotent factors of odd multiplicative order up to lcm 194691, and
q_6 is likewise not unipotent. So "every king column is fully unipotent
mod 2" is FALSE: the tiny 2-power periods behind S1/S2 are an H ≤ 4
accident, not king-wide structure (barring initial-vector cancellations,
untestable in-grid since the H = 5 recurrence has no in-grid instances —
`results/triangle-hunt-atoms-ab-initio.md`). This closes the last route by
which the sweep survivors could have been a fragment of something deep.

## Independence fields (for the table itself)

- **Bits of independent check on a(40): 0.** This deliverable proposes no
  king relation; it classifies the existing survivors. (They were already
  culled; the classification tells the refuters *why* the cull was right,
  and which residue of king-specific content is real.)
- **Input footprint:** king columns H = 3,4, n ≤ 40 (validation only —
  used to name the survivors being tested, not to derive anything).
- **Derivation independence:** square/tri data derived blind from the
  lattice definitions (own enumerator + own TM, mutually cross-checked);
  published anchors A001168, A001420, A335606.
- **Rule independence:** fully — neither the enumerator nor the TM shares
  code or connectivity rule with any repo engine.

## Negatives

- Square H = 4 and tri H = 3, 4 exact-height columns are not in OEIS; the
  cross-lattice check for those rests on two in-house independent sources
  (enumerator + TM), not on published data.
- Tri H = 4 has no C-finite recurrence of order ≤ 45 detectable from 135
  terms; its TM order is simply larger. Nothing was found to contradict
  C-finiteness (which is guaranteed by the TM's existence).
- Mod-3 periods for square H=4 and tri H=3 exceed the 10^7 cycle-detection
  cap; existence is guaranteed, size undetermined — not pursued (no bearing
  on the verdicts).
- No relation proposed by this role: after the survivors resolved into
  generic-mechanism + known-coincident king residue, no cross-lattice
  transfer candidate with nonzero a(40) check-value remained. The brief
  explicitly prices this outcome ("the table is a deliverable in its own
  right").
