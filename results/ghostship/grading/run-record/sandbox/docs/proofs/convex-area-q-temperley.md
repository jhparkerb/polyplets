# The area statistic on convex king animals is Temperley-solvable:
# an explicit q-series form for the full (width, height, area) GF

Date: 2026-08-15 (autonomous session 04). Builds on the proven functional
equation of `docs/proofs/convex-box-kernel.md` (s03). Companion scripts:
`experiments/s04_qfe_check.py`, `experiments/s04_q_temperley.py`.

**Theorem (established here).** Let f(w,h;n) be the number of convex king
animals (HV-convex polyplets) with bounding box exactly w×h and n cells, and

    F(x,y,q) = Σ f(w,h;n) x^w y^h q^n .

Then F is given by an explicit finite expression in four q-adically
convergent q-series (stated in §3): a Temperley-style solution of the same
combinatorial functional-equation system whose q=1 specialization was solved
by the kernel method in s03. In particular the area statistic — proven
empirically intractable as a counting sequence (convex-mirage: no
P-recurrence of order ≤6/deg ≤5 on 38 terms) — nevertheless has a CLOSED
q-SERIES FORM. The same derivation with the two king boundary terms dropped
solves convex polyominoes by area (control), reproducing OEIS A067675 and
A067676 to 50 terms.

## 1. The q-deformed functional equation [proved; validated exactly]

Mark each row of length k' by q^{k'} (area = Σ row lengths). Every transition
sum of the s03 system (proof doc §1) is an identity in a free variable z
evaluated at z = s; marking by q replaces each new-row monomial s^{k'} by
(qs)^{k'}, i.e. evaluates the SAME identities at z = qs, while the
catalytic extractions G(1) := Σ_k g_k and G'(1) := Σ_k k g_k (coefficients
of the previous row) are unchanged. Hence, with z := qs:

    F00(s) = xyz/(1-xz) + y F00(z)/(1-xz)^2
    F10(s) = y Bq[F00](s) + y Cq[F10](s),        F01 = F10 (mirror)
    F11(s) = y D1q[F00](s) + 2y D2q[F10](s) + y L3q[F11](s)
    F(x,y,q) = F00(1) + 2 F10(1) + F11(1)

    Bq[G](s) = (G(z)-zG(1))/((z-1)(1-xz)) + [king] xzG(1)/(1-xz)
    Cq[G](s) = z(G(z)-G(1))/((z-1)(1-xz)) + [king] xzG(1)/(1-xz)
    L3q[G](s) = [z^2 G(z) - z^2 G(1) - z(z-1)G'(1)]/(z-1)^2
    D2q[G](s) = L3q[G](s) - z(G(z)-G(1))/(z-1)
    D1q[G](s) = [G(z) - z^2 G(1) - z(z-1)(G'(1)-2G(1))]/(z-1)^2

(polyomino control: drop the two [king] boundary terms). Initial state:
Σ_{k≥1} x^k y (qs)^k = xyz/(1-xz).

VALIDATION: `s04_qfe_check.py` implements the raw area-marked transitions
(no operator algebra) and reproduces the ground-truth joint table f(w,h;n)
for ALL w,h ≤ 10, every n, king AND polyomino modes
(`out_s04_qfe_check.txt`). The ground truth itself (`s04_area_truth.py`,
`out_s04_area_truth.txt`) is doubly computed: definitional subset brute
force (HV-convexity + connectivity + 4-side touching, boxes wh ≤ 16) and
the s01-validated interval DP with area marking; cross-checked per-area,
plus q=1 marginal = banked f(w,h) and area marginal = banked area sequences.

Uniqueness: as at q=1, the system determines the y^h coefficients of all
F_ph from the y^{h-1} coefficients, so it has exactly one power-series
solution — the combinatorial one.

## 2. Why the kernel method dies and iteration survives

At q=1 the unknown F10(s) appears at the SAME argument s on both sides and
the kernel (s-1)(1-xs)-ys can be cancelled at its root s0(x,y) — algebraic.
For q ≠ 1 the equation couples F10(s) to F10(qs): a q-difference equation.
No fixed substitution kills the kernel; instead, iterating s → qs and using
that every iteration step carries a factor y AND gains q-valuation (each
new row costs ≥1 cell) gives q-adically convergent solutions — the
Temperley/Bousquet-Mélou mechanism that produces q-Bessel-type series for
convex polyominoes by area. This is the precise structural sense in which
area is "q-series-hard while perimeter is algebraic": the q=1 limit of the
series below is singular term-by-term (denominators (1-q^j)), and only the
sum degenerates to the algebraic kernel solution.

## 3. The explicit solution [proved; every step machine-validated]

Opening phase (identical for king and polyomino: king constraints are
inactive in phase (0,0); this subfamily = stack polyominoes, A001523):

    F00(z) = Σ_{n≥0} x y^{n+1} q^{n+1} z
             · Π_{j=1}^{n} (1-xq^j z)^{-2} · (1-xq^{n+1} z)^{-1}

Staircase phase. Write the C-operator part of (E1q) as
Cq[F10](s) = R(z)F10(z) + T(z)F10(1) with

    R(z) = z/((z-1)(1-xz)),
    T(z) = (xz(z-1)-z)/((z-1)(1-xz))   [king; control: -z/((z-1)(1-xz))]

and A1(s) := y Bq[F00](s). Iterating s → qs:

    F10(s) = Σ_{n≥0} y^n Π_{j=1}^{n} R(q^j s) · [A1(q^n s) + y T(q^{n+1}s) F10(1)]
           = α(s) + β(s) F10(1),

α, β explicit q-series (the products Π R(q^j s) =
q^{n(n+1)/2} s^n / Π_{j=1}^{n} (q^j s-1)(1-xq^j s) have q-valuation
n(n+1)/2: convergence). Setting s = 1:

    F10(1) = α(1) / (1 - β(1))          [Temperley ratio]

Closing phase. (E2q) reads F11(s) = A2(s) + y U(z)F11(z)
- y V1(z)F11(1) - y V2(z)F11'(1) with U(z)=V1(z)=z^2/(z-1)^2,
V2(z)=z/(z-1), A2 = y D1q[F00] + 2y D2q[F10]. Iterating:

    F11(s) = Σ_{n≥0} y^n Π_{j=1}^{n} U(q^j s)
             · [A2(q^n s) - y V1(q^{n+1}s) F11(1) - y V2(q^{n+1}s) F11'(1)]

Evaluating at s = 1+ε (dual numbers, ε² = 0; all inverted quantities are
units in Q[[q]] since (z-1) is only ever inverted at z = q^m(1+ε), m ≥ 1)
gives a 2×2 linear system for (F11(1), F11'(1)) with determinant 1 + O(q),
hence invertible. Assembly: F = F00(1) + 2F10(1) + F11(1).

Substitution legitimacy is the trivial half of s03 §2: all substitution
points are q^m(1+ε) and every series is q-adically convergent with
valuations growing linearly-to-quadratically in the iteration index; only
finitely many terms contribute below any q^N.

## 4. Machine verification (`s04_q_temperley.py`, exact Fractions)

- Joint check: for (x,y) ∈ {(1,1),(2,1),(1,3),(3,2)}, [q^n] of the
  assembled solution equals Σ_{w,h} f(w,h;n) x^w y^h from the ground-truth
  table for all n ≤ 10, king AND polyomino modes (`out_s04_q_temperley.txt`).
- Area sequence: at x=y=1 the formula reproduces the banked 30-term
  convex-mirage sequence, and matches an independent fresh 50-term
  transfer-matrix run (`convex_tm.py 50`) on ALL 50 terms
  (`out_s04_predict50.txt`, `out_s04_tm50.txt`);
  a(50) = 5736473632219682585431462.
- Literature anchor: control at x=y=1 matches OEIS A067675 (convex
  polyominoes by area) AND the directed subfamily F00(1)+F10(1) matches
  A067676 (directed convex by area), 50/50 terms each, against their
  b-files (`out_s04_oeis_control.txt`).
- Fixed-height slices: exact y-interpolation of F(1,y,q) recovers s01's
  banked rational A_H(q) for H ≤ 4, all 15 computed coefficients
  (`out_s04_fixed_height_check.txt`).
- Subfamily identifications: F00 = stacks (A001523, both modes identical —
  machine-checked); king F00(1)+F10(1) = directed-convex king animals by
  area, NOT in OEIS (new; 50 exact terms available).

## 5. Corollaries

1. **Fixed-height rationality is a theorem.** [y^H]F is a FINITE sum
   (iteration depth ≤ H in each phase) of products of rational functions of
   q and x with denominators from {(q^j s-1), (1-xq^j s), (z-1)} at s=1:
   each A_H(x,q) is rational in x,q with denominator a product of
   (1-q^j)- and (1-xq^j)-type factors; at x=1, cyclotomic — exactly the
   structure s01 observed empirically (A_2, A_3, A_4).
2. **The tractability boundary is now fully mapped.** Semiperimeter/box:
   algebraic (s03 kernel proof). Area: explicit q-series (this doc), q=1
   limit singular term-by-term, counting sequence empirically non-D-finite
   (convex-mirage). Both facts now flow from ONE functional equation.
3. The king/polyomino difference remains ONLY the two boundary terms in
   Bq/Cq — the q-deformation does not disturb s03's structural finding.

## Receipts

`experiments/s04_area_truth.py` → `out_s04_area_truth.txt`, `.json`;
`experiments/s04_qfe_check.py` → `out_s04_qfe_check.txt`;
`experiments/s04_q_temperley.py` → `out_s04_q_temperley.txt`;
`out_s04_predict50.txt`, `out_s04_tm50.txt`, `out_s04_oeis_control.txt`,
`out_s04_fixed_height_check.txt`, `experiments/s04_subfamilies.py` →
`out_s04_subfamilies.txt`.
