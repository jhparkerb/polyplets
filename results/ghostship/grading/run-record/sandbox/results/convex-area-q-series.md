# The area statistic on convex king animals: closed q-series form

Session 04 result. Full derivation + verification: `docs/proofs/convex-area-q-temperley.md`.

## What was established

The problem statement's target — "the area statistic on convex king animals
resists a closed form" — is now resolved in the precise sense available:

- There is NO closed form of the classical kind (algebraic / D-finite):
  convex-mirage's empirical negative stands, and s01–s03 located the
  boundary (box/semiperimeter statistics are algebraic, proven by kernel
  method).
- There IS a closed q-series form: the full generating function
  F(x,y,q) = Σ f(w,h;n) x^w y^h q^n is an explicit finite combination of
  four q-adically convergent q-series (Temperley solution of the s03
  functional equation, q-deformed by area). Coefficient extraction is
  exact and fast (50 terms in 2 s), and every structural fact observed
  since s01 (fixed-height rationality, cyclotomic denominators, the
  algebraic q=1 limit) degenerates from it.

This is the same status as the classical convex-polyomino area problem
(Bousquet-Mélou's q-Bessel forms) — and indeed the identical pipeline with
the two king boundary terms dropped reproduces the literature sequences
A067675/A067676 to 50 terms each.

## Key formulas (see proof doc for operator definitions; z = qs)

    F00(z)  = Σ_{n≥0} x y^{n+1} q^{n+1} z Π_{j=1}^{n}(1-xq^j z)^{-2} (1-xq^{n+1}z)^{-1}
    F10(1)  = α(1)/(1-β(1))         α, β explicit (Π R(q^j s) products)
    F11(1)  from a 2×2 unit-determinant linear system (dual numbers at s=1)
    F(x,y,q) = F00(1) + 2 F10(1) + F11(1)

## Sequences (x = y = 1; 50 exact terms each in receipts)

Convex king animals by area (= convex-mirage sequence, extended 30 → 50
terms, formula vs independent transfer matrix, all 50 match; NOT in OEIS):

    1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111, ...
    a(50) = 5736473632219682585431462

Directed-convex king animals by area (NEW sequence, NOT in OEIS; the area
q-analog of s03's A014300 semiperimeter identification):

    1, 3, 10, 33, 107, 342, 1084, 3417, 10737, 33675, 105505, 330353, ...

Stacks (phase (0,0), king = polyomino, OEIS A001523 — new interpretation:
the king constraints are vacuous on this subfamily):

    1, 2, 4, 8, 15, 27, 47, 79, 130, 209, 330, 512, ...

Controls anchored to OEIS b-files (50/50 terms): A067675 (convex
polyominoes by area), A067676 (directed convex polyominoes by area).

## Also in this session

The single residual caveat in s03's kernel-method theorem (mod-p
certification of the closed-form identification) was removed by an exact
rational rerun of the 84 specializations: the box/semiperimeter closed form
is now proven over Q with no modular hypothesis
(`out_s04_exact_close.txt`; addendum in `docs/proofs/convex-box-kernel.md`).

## Open

- Extract the q → 1 asymptotics (μ ≈ 3.12894) from the q-series (saddle
  point / dominant-singularity analysis of α/(1-β)) — would make the growth
  constant exact.
- Simplify α, β, and the 2×2 system into named q-Bessel-type functions
  (Bousquet-Mélou normal form) for the paper.
- Prove non-D-finiteness of the area sequence (currently empirical).
