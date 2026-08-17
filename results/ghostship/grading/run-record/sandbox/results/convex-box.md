# Convex king animals: the perimeter statistic is the tractable one

Date: 2026-08-15 (autonomous session 01). Companion to
`docs/proofs/convex-mirage.md`, which established that the **area** statistic
on convex king animals (HV-convex polyplets) is empirically non-D-finite.
This note establishes what **is** tractable in the family: the
**bounding-box/semiperimeter statistic is algebraic** (an explicit closed-form
GF with the same radicand √(1−4t) as classical convex polyominoes), and the
**area statistic restricted to any fixed height is rational** with cyclotomic
denominators. Convexity IS the classical tractability lever here too — by
perimeter, exactly as for polyominoes; the mirage was only ever about area.

## Objects and statistic

Convex king animal = sequence of row intervals [l_i, r_i], l valley-unimodal,
r mountain-unimodal, consecutive rows within king reach (l' ≤ r+1, r' ≥ l−1);
same model as `experiments/convex_tm.py` (validated there vs brute force).
f(w,h) = number of translation classes with bounding box exactly w × h.
Semiperimeter statistic: a(s) = Σ_{w+h=s} f(w,h), s ≥ 2.

Tool: `experiments/convex_box.py` (interval DP for g(w,h) = counts inside a
width-w frame; f = second difference in w). Validated three ways:
1. exact match with direct subset brute force (king-connectivity + HV-convex
   + touch-all-4-sides) on all boxes with wh ≤ 16 (`out_convex_box_14.txt`);
2. transpose symmetry f(w,h) = f(h,w) for all computed w,h ≤ 38;
3. **literature control**: the polyomino-adjacency mode (king reach → column
   overlap) reproduces A005436 (convex polyominoes by semiperimeter) on all
   16 fetched reference terms (`out_control_polyomino.txt`), and the ansatz
   fitter run on that control recovers the classical Delest–Viennot GF
   (1−4t)²F = t²(1−6t+11t²−4t³) − 4t⁴√(1−4t) exactly (`out_ansatz_control.txt`).

## The sequence (NEW, not in OEIS)

a(s), s = 2..39, from pure DP (`out_convex_box_38.txt`, `king_semiperim_38.txt`):

```
1, 2, 9, 36, 154, 668, 2916, 12740, 55570, 241692, 1047604, 4524464,
19470660, 83500968, 356923968, 1520962956, 6462604898, 27385953724,
115760525316, 488181510848, 2054285046316, 8627071911816, 36161710424024,
151311476669320, 632094578750484, 2636484792140888, 10981037255552776,
45674599082396640, 189738142469481640, 787255032236740832, ...
```

## Main result: the semiperimeter GF is algebraic

F(t) = Σ_{s≥2} a(s) t^s satisfies (found by exact holdout-validated fitting,
`experiments/gf_algebraic.py`, 30-coefficient holdout, `out_gf_algebraic_200.txt`):

P2·F² + P1·F + P0 = 0 with
- P2 = (2+t)(1−4t)⁴ = 2 − 31t + 176t² − 416t³ + 256t⁴ + 256t⁵
- P1 = −4t² + 52t³ − 252t⁴ + 554t⁵ − 520t⁶ + 96t⁷ + 128t⁸
- P0 = 2t⁴ − 21t⁵ + 88t⁶ − 196t⁷ + 242t⁸ − 119t⁹ + 72t¹⁰ + 16t¹¹

Discriminant P1² − 4·P0·P2 = 4t⁶(1−4t)⁵(1+2t)⁴ (`out_closed_form2.txt`), so
**only √(1−4t) appears** — the same radicand as classical convex polyominoes —
and after cancellations the closed form is

```
        t²(2 − 10t + 14t² − 5t³ − 4t⁴) − t³(1+2t)²·√(1−4t)
F(t) =  ---------------------------------------------------
                        (2+t)(1−4t)²
```

Verification (`out_final_verify.txt`): the series of this expression matches
**all 38 pure-DP terms** exactly, and all 200 recurrence-extended terms
(`out_closed_form_verify.txt`). Status: firm empirically (fitted with deep
exact holdouts at every stage); a bijective/kernel-method proof is open but
the classical convex-polyomino perimeter machinery is the obvious route.

Corollaries:
- **P-recurrences** (holdout-validated on all 38 DP terms, incl. 8 fresh
  ~20-digit terms predicted before the confirming DP run landed —
  `out_recurrence_scan.txt`, `out_recurrence_extend.txt`): minimal order 4 with
  cubic coefficients; also order 5/deg 2 and order 7/deg 1.
- **Asymptotics**: dominant singularity t=1/4, double pole from the rational
  part (R = 2−10t+14t²−5t³−4t⁴ has R(1/4) = 9/32 ≠ 0):
  a(s) = (s/128)·4^s·(1+o(1)); the radical part contributes
  −(1/64)(2s+1)·C(2s,s)·(1+o(1)) ~ −(√s/(32√π))·4^s at the next order.
  Growth constant exactly 4 (vs area growth μ ≈ 3.129 — different statistic).
- The characteristic roots of the recurrences (4, 4, −2, −1/2 + spurious
  172/97) reflect exactly the singularities of the closed form
  (`out_char_roots.txt`).

## Fixed-height slices

**Box rows are polynomial**: for each h, f(w,h) is a polynomial in w of degree
2h−2 valid for ALL w ≥ 1 (`out_row_polynomials.txt`, exact fits validated on
w ≤ 38):
- f(w,1) = 1
- f(w,2) = 2w² − 1
- f(w,3) = w⁴ + (2/3)w³ − (1/2)w² − (13/6)w + 2
- f(w,4) = (17/90)w⁶ + (17/30)w⁵ + (17/36)w⁴ − (4/3)w³ − (29/180)w² + (49/15)w − 2
- f(w,5) = (1/56)w⁸ + (41/315)w⁷ + (16/45)w⁶ + (8/45)w⁵ − (11/18)w⁴ + (173/180)w³ + (4379/2520)w² − (1583/420)w + 2

**Fixed-height area GFs are rational** (the tractable slice of the area
statistic itself; `out_area_fixed_height.txt`, exact rational fits with
holdout): with A_H(q) = Σ_animals of height exactly H q^{area},
- A_1 = q/(1−q)
- A_2 = q²(3−q)/(1−q)³   (i.e. exactly n²−1 animals of area n)
- A_3 = q³(7+2q+3q²−4q³+2q⁴) / ((1−q)⁴(1−q³))
- A_4 = num / ((1−q)⁴(1−q³)²(1−q⁴))  (denominator factored in
  `out_area_slices_check.txt`; = (1−q)⁷(1+q)(1+q+q²)²(1+q²))

Cross-check: Σ_{H≤12} A_H coefficients reproduce the banked convex-mirage area
sequence 1,4,16,61,221,766,… exactly for n ≤ 12 (`out_area_slices_check.txt`).
The growing cyclotomic denominators (new factors (1−q^H)-style at each height)
are precisely the Temperley-type mechanism that makes the full area GF a
q-series — this makes convex-mirage's "q-series nature" concrete and
stratified: **area = rational on every height slice; the non-D-finiteness
lives only in the infinite sum over heights.**

## OEIS (queries logged in reports/session-01.md)

- semiperimeter a(s): NOT in OEIS (JSON search returned null).
- box diagonal f(n,n) = 1, 7, 90, 1398, 23020, 386774, 6539320, …: NOT in OEIS.
- Both are staged OEIS candidates (with A005436 as the polyomino-analog anchor).

## Receipts

`experiments/convex_box.py` (DP + brute validation), `experiments/fit_recurrence.py`,
`experiments/gf_algebraic.py`, `experiments/ansatz_fit.py`;
outputs: `out_convex_box_14.txt`, `out_convex_box_38.txt`, `out_control_polyomino.txt`,
`out_control_30.txt`, `out_ansatz_control.txt`, `out_gf_algebraic_200.txt`,
`out_closed_form2.txt`, `out_final_form.txt`, `out_final_verify.txt`,
`out_recurrence_scan.txt`, `out_recurrence_extend.txt`, `out_row_polynomials.txt`,
`out_area_fixed_height.txt`, `out_area_slices_check.txt`;
series: `king_semiperim_38.txt`, `king_semiperim_200.txt`, `control_semiperim_30.txt`.
