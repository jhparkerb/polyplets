# Component-count stratification of polyplets

Date: 2026-07-10. `experiments/component_stratification.py`. `C(n,c)` = # fixed
polyplets of n cells with exactly `c` edge-connected (rook) components. A
polyplet's edge-components are polyominoes joined only at corners.

## The triangle (n=1..9), exact

| n\c | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | | | | | | | | |
| 2 | 2 | 2 | | | | | | | |
| 3 | 6 | 8 | 6 | | | | | | |
| 4 | 19 | 36 | 36 | 19 | | | | | |
| 5 | 63 | 156 | 200 | 156 | 63 | | | | |
| 6 | 216 | 660 | 1038 | 1040 | 662 | 216 | | | |
| 7 | 760 | 2752 | 5142 | 6236 | 5166 | 2776 | 760 | | |
| 8 | 2725 | 11390 | 24620 | 34962 | 35097 | 24860 | 11562 | 2725 | |
| 9 | 9910 | 46936 | 115050 | 186860 | 218824 | 188612 | 116936 | 47944 | 9910 |

## Validated + surprises

- `Σ_c C(n,c) = A006770` (all polyplets) ✓; `C(n,1) = A001168` (fixed
  polyominoes = single edge-component) ✓. Enumerator sound.
- **`C(n,n) = A001168` too** — fixed polyominoes on BOTH edges of the triangle.
  `c=n` = every cell edge-isolated ⇒ the animal is held together purely by
  diagonal contacts. Diagonal neighbours share checkerboard colour, so such an
  animal is one-colour cells connected by diagonal adjacency = **a polyomino on
  the 45°-rotated sublattice**. So edge-isolated king animals ↔ polyominoes,
  giving `C(n,n)=A001168`. (Clean bijection.)
- Distribution **peaks near `c≈n/2`** (near-symmetric but not exactly). So the
  *typical* polyplet is highly fragmented — ~n/2 small pieces joined at corners.
  The polyomino fraction `C(n,1)/a(n)` is ~1% at n=9 and shrinking.

## Why this matters (#4's actual question)

The fragmentation is the mechanism behind `λ_polyplet ≈ 7.11 ≫ λ_polyomino ≈
4.06`: `a(n)` is dominated by many-piece corner-assemblies, not near-polyominoes.
A `a(n)`-from-A001168 corner-gluing composition formula would formalize this —
the deeper #4 goal (species-style composition of polyomino pieces under
corner-contact constraints; hard because contacts are geometrically constrained,
not free).

## OEIS / prior art (sonnet-checked 2026-07-10)

- `C(n,c)` triangle (row- and antidiagonal-flattened): **NOT in OEIS**. Interior
  columns c=2 (`2,8,36,156,660,…`) and c=3 (`6,36,200,1038,…`): **NOT in OEIS**.
  Novel; good submission candidate (rows→A006770, edges→A001168 as cross-refs).
- Prior art for the bijection: **A364928** (Achterberg 2023, "corner-connected
  polyominoes"), comment: *"Corner-connected polyominoes are in one-to-one
  correspondence with ordinary polyominoes."* But A364928 is the **free** case
  (↔ A000105). Our **fixed** statement `C(n,n)=A001168` is the fixed analogue and
  is not separately recorded. Standard term for the object: "pseudo-polyomino /
  polyking / polyplet."
- No literature decomposes king animals by edge-component count → `C(n,c)` is
  unpublished.

## Mean component count ≈ (n+1)/2 (task #8)

`mean_c(n) = Σ_c c·C(n,c) / a(n)`: **`1, 1.5, 2, 2.5, 3`** for n=1..5 (exactly
`(n+1)/2`), then `3.501, 4.003, 4.506, 5.009` (n=6..9) — a tiny positive drift
above `(n+1)/2`. So a typical polyplet has ~`n/2` edge-components averaging
**~2 cells each**. This quantifies the fragmentation that makes
`λ_polyplet ≈ 7.11 ≫ λ_polyomino ≈ 4.06`: `a(n)` is dominated by the huge
multiplicity of corner-gluings of tiny pieces, not near-polyominoes.

The `≈(n+1)/2` mean reflects the triangle being **near-symmetric under
`c ↔ n+1−c`** (exact at the edges: both = A001168; the interior asymmetry drives
the small drift). Not an exact law — `Σ_c c·C(6,c) = 13416 ≠ 13412 = (7/2)a(6)`.

## The composition a(n) = f(A001168): hard, structural conclusion

Task #8's ambition — write `a(n)` as a species-style composition of polyomino
pieces (A001168) joined at corners — does NOT close to a clean formula. The
corner-gluing is **geometrically constrained** (pieces can't overlap, corner
contacts have specific adjacency, the whole must be king-connected), so it is
NOT free composition; no `a(n) = f(A001168)` GF relation follows. The tractable,
banked outputs are the `C(n,c)` triangle itself + the mean-`(n+1)/2` /
component-size-2 fragmentation statement. The full composition remains open
(hard), consistent with polyplet counts being non-D-finite.
