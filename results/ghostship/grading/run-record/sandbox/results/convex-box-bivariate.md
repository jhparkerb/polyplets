# The bivariate box GF of convex king animals is algebraic (explicit closed form)

Date: 2026-08-15 (autonomous session 02). Continues `results/convex-box.md`
(session 01: univariate semiperimeter GF). Everything below is exact-arithmetic
computation with holdout validation; proofs remain open (see end).

## Main result

Let f(w,h) = number of convex king animals (HV-convex polyplets) with bounding
box exactly w × h, and F(x,y) = Σ_{w,h≥1} f(w,h) x^w y^h. Then F is ALGEBRAIC:

    F(x,y) = − [ M(x,y) + 2x²y²(1+x+y)²·√Δ ] / ( 2·K·Δ² )

with

    Δ = (1−x−y)² − 4xy          (the classical staircase radicand)
    K = x + y + xy              (the "king kernel" factor)
    M = A1/Δ², an explicit symmetric integer polynomial of degree 8:
    M = −2xy(x+y) + (6y³+8xy²... ) — full coefficient list in out_s02_KM.txt:
        -2xy^2 -2x^2y +6xy^3 +8x^2y^2 +6x^3y -6xy^4 -8x^2y^3 -8x^3y^2 -6x^4y
        +2xy^5 +6x^3y^3 +2x^5y +2x^2y^5 +2x^3y^4 +2x^4y^3 +2x^5y^2
        +2x^3y^5 -4x^4y^4 +2x^5y^3

Equivalently A2 F² + A1 F + A0 = 0 with A2 = Δ⁴K, A1 = Δ²M,
A0 = (M² − Δ·S²)/(4K) where S = 2x²y²(1+x+y)²  (all three are integer
polynomials; full coefficients in `out_s02_bivar_eq_king_D2.json`).

Evidence chain (receipts):
- fitted by modular linear algebra + rational reconstruction on series
  coefficients i+j ≤ 32; nullspace dimension exactly 1 (unique equation at
  degrees (10,14,18)); EXACT bigint holdout on ALL 780 table coefficients
  i+j ≤ 38 — zero residues (`out_s02_bivar_king.txt`).
- discriminant A1² − 4A2A0 = Δ⁵ · (2x²y²(1+x+y)²)² computed and square-part
  extracted exactly (`out_s02_bivar_analysis.txt`); radical form verified as
  series identity 2A2F + A1 = −SΔ²√Δ through total degree 30
  (`out_s02_closed_form.txt`); A2/Δ⁴ = K and A1/Δ² = M exact
  (`out_s02_KM.txt`).
- specialization x=y=t annihilates the 200-term univariate series and
  reproduces session 01's closed form exactly:
  −M(t,t) = 2t³(2−10t+14t²−5t³−4t⁴), K(t,t) = t(2+t), Δ(t,t) = 1−4t,
  (1+x+y) → (1+2t). The mystery factors of session 01 are explained:
  (2+t) is the diagonal shadow of K = x+y+xy, and (1+2t)² of (1+x+y)².

## Control (literature anchor)

The same pipeline on convex POLYOMINOES (adjacency mode of the validated DP)
finds the unique quadratic at degrees (8,12,16), holdout-exact to i+j≤34,
with A2 = Δ⁴ (K = 1) and discriminant 64x⁴y⁴Δ⁵
(`out_s02_bivar_control.txt`, `out_s02_control_structure.txt`) — the
classical Lin–Chang/Bousquet-Mélou anisotropic structure. So the ENTIRE
structural difference king vs. polyomino at box level is:
denominator kernel K = x+y+xy (vs 1) and radical weight (1+x+y)² (vs 4).

## Exact coefficient formula (Delest–Viennot analog)

Because (2+t)F(t,t) has pure (1−4t) denominators, the twisted combination
b(s) := 2a(s) + a(s−1) has a closed form. For s ≥ 5, with n = s−3:

    2a(s) + a(s−1)  =  (18s+49)·4^(s−5)  −  (9n²−3n−1)/(2n−1) · C(2n,n)

verified exactly on all 195 available terms s=5..199
(`out_s02_exact_formula.txt`). Compare Delest–Viennot for convex polyominoes:
p(n+2) = (2n+11)4^n − 4(2n+1)C(2n,n). The (2+t) kernel factor is why the
king analog lives on 2a(s)+a(s−1) rather than a(s) itself.
b(s) = 2,5,20,81,344,1490,… is NOT in OEIS.

## Row structure: N_h(x), and session 01's leading-coefficient OPEN resolved

R_h(x) = Σ_w f(w,h)x^w = N_h(x)/(1−x)^(2h−1); integer polynomials N_h of
degree 2h−1 extracted for h ≤ 18 with all higher coefficients verified zero
(`out_s02_rowgf.txt`) — this extends session 01's "f(w,h) is polynomial in w
of degree 2h−2 for all w≥1" from h≤5 to h≤18.

- N_h(1) = (2h−2)!·[leading coeff of f(·,h)] = 1,4,24,136,720,3624,… is
  OEIS **A153337** ("zig-zag [= king] paths from top to bottom of a
  (2n−1)×(2n−1) square"), closed form
      N_h(1) = h·4^(h−1) − 2(h−1)·C(2h−2,h−1),
  matching all 18 computed values (`out_s02_fingerprints.txt`). Hence

      lead_h = [h·4^(h−1) − 2(h−1)·C(2h−2,h−1)] / (2h−2)!

  resolving session 01's unidentified 1, 2, 1, 17/90, 1/56, …
  (Structurally: the w→∞ box count is dominated by choosing a top and a
  bottom king-path profile — a zig-zag-path count is exactly the right
  object; a bijective proof is a nice open exercise.)
- Parity fingerprints (empirical, all computable h):
  N_{2k}(−1) = (−1)^(k+1)·4·N_k(1) (k ≤ 9) — a half-height self-similarity;
  N_{2k+1}(−1) = (−1)^k·(2k+1)·4^k (k ≤ 8, h=1 exceptional).

## Independent verification of session 01 (fresh code, definitional)

`experiments/s02_brute.py`: raw 2^(wh) subset enumeration (BFS king
connectivity, definitional row/column-convexity — none of the DP's
phase/reach machinery) for all boxes wh ≤ 16, plus an interval-DFS
enumerator (column-convexity pruning, BFS at leaves) for larger boxes.
All banked f(w,h) with wh≤16 confirmed; a(s) confirmed for s = 2..10
(a(10) = 55570 needs boxes up to 5×5/4×6; `out_s02_brute_verify.txt`,
`out_s02_brute_s10.txt`).

## Open items handed forward

1. PROVE the bivariate closed form (kernel method: the shape
   F = −(M + S√Δ)/(2KΔ²) with K = x+y+xy is exactly what a
   two-catalytic-variable Temperley/Bousquet-Mélou festoon decomposition
   would produce; K is presumably the kernel of the column-adding operator).
   This would subsume session 01's open proof of the univariate form.
2. Bijective/analytic proof that lead_h·(2h−2)! = A153337 (king-path pairs).
3. Explain N_{2k}(−1) = ±4N_k(1) (suggests a −1-evaluation ↔ height-halving
   symmetry, perhaps via a q→−1/cyclic-sieving argument on the box DP).
4. f(−w,h) probe (Ehrhart-style reciprocity): no clean match found against
   king or polyomino tables (`out_s02_reciprocity_probe.txt`); h=7 gives
   f(−4,7)=0 — if a reciprocity exists it involves sign patterns/zeros, not
   a simple table shift. Inconclusive, not a dead end.

## Receipts

Scripts: `experiments/s02_brute.py`, `s02_rowgf.py`, `s02_bivar_fit2.py`
(+ superseded first draft `s02_bivar_fit.py`), `s02_bivar_analyze.py`,
`s02_closed_form.py`.
Outputs: `out_s02_brute_verify.txt`, `out_s02_brute_s10.txt`,
`out_s02_rowgf.txt`, `out_s02_fingerprints.txt`, `out_s02_bivar_king.txt`,
`out_s02_bivar_control.txt`, `out_s02_bivar_analysis.txt`,
`out_s02_closed_form.txt`, `out_s02_KM.txt`, `out_s02_control_structure.txt`,
`out_s02_exact_formula.txt`, `out_s02_reciprocity_probe.txt`,
`out_s02_bivar_eq_king_D2.json`, `out_s02_bivar_eq_control_D2.json`.
