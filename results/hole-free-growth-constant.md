# The hole-free growth constant λ₀: simple-connectivity is exponentially costly

2026-07-11 (research during the a(22) fleet run). `experiments/holefree_growth.py`
on the banked hole distribution `results/holes_n18.txt` (g2 `--holes`, n≤18, exact).

## Question

The height/diagonal structure of the triangle is well mapped, and polyplets are
confirmed to sit in the 2D lattice-animal universality class (extent exponent
ν≈0.64, [[nu-exponent]]; growth θ≈−1). Open, unanalysed here: does the **hole-free**
(simply-connected) sub-class A₀(n) share the full growth constant λ≈7.11, or grow
strictly slower? I.e. is a hole a *polynomially* rare accident or an *exponential*
entropic gain? `polyplet-zoo.md` only noted the fraction at a single n (73.4% at 18).

## Result — λ₀ < λ, hole-free fraction decays purely exponentially

From A₀(n) (holes=0), A₁(n) (one hole), and a(n)=ΣA_k, n≤18:

| quantity | growth constant | θ (finite-size) | method |
|---|---|---|---|
| a(n) total | **λ ≈ 7.096** | −0.93 (→ universal −1) | Domb-Sykes + Richardson + log-linear fit |
| A₀(n) hole-free | **λ₀ ≈ 6.94** | −0.93 (same) | same |
| gap λ − λ₀ | **≈ 0.157** | | |

Two independent, mutually confirming facts make λ₀ < λ robust despite n≤18:

1. **The hole-free fraction A₀/a decays as a clean geometric ρⁿ.** log(A₀/a) vs n
   is linear to 5 decimals (second difference ≈ 1×10⁻⁵ across n=12..18), slope
   −0.0222/cell → **ρ = 0.9779 per cell**. A shared growth constant would give a
   *sub-exponential* (polynomial) fraction; the fit is unambiguously exponential.
2. **ρ equals λ₀/λ.** Measured per-cell fraction decay 0.97800 vs the fitted
   λ₀/λ = 0.97789 — agreement to four decimals. So the two constants and the
   fraction decay are one consistent picture: **A₀ ~ λ₀ⁿ, a ~ λⁿ, A₀/a ~ (λ₀/λ)ⁿ.**

The **ratio λ₀/λ = 0.978 is pinned** by (1) even though the absolute λ, λ₀ carry
finite-size uncertainty (~±0.02 at n≤18): whatever the true λ, the hole-free class
runs a constant factor 0.978 per cell behind it.

## Reading

- **Simple-connectivity is exponentially costly: ~2.2% of the per-cell entropy.**
  Almost every large polyplet has a hole; the hole-free ones are suppressed by
  (0.978)ⁿ, not by a mere power of n. Being simply-connected forbids a positive
  density of local configurations, and that ban compounds multiplicatively.
- **Same correction exponent θ ≈ −0.93 for both classes** — hole-free polyplets sit
  in the same universality class (same θ→−1), differing only in the non-universal
  growth constant. Clean separation of universal (θ, ν) from non-universal (λ, λ₀).
- **Holes are extensive.** Mean hole count per cell climbs monotonically
  (0.0132 → 0.0160 → 0.0176 at n=10/14/18), heading to a positive constant: a
  typical large polyplet has ~c·n holes (the lattice-animal pattern-theorem picture).
  The one- and two-hole classes A₁, A₂ approach λ from finite-size (their individual
  constants are not pinnable at n≤18; A₁'s ratio is still descending through 7.08).

## Caveats

- n≤18 is short for a growth constant. **λ₀ ≈ 6.94 is ±~0.02**; the *ratio* λ₀/λ =
  0.978 and the *exponential* nature are the robust, quotable outputs, not the third
  digit of λ₀. A handful more terms (production TM `--holes` to n≈22, cheap; or when
  the fleet frees) would tighten λ₀ and test whether the gap is exactly constant.
- This is the polyplet analogue of the (believed) polyomino behaviour that
  simply-connected polyominoes grow strictly slower than λ≈4.06; not claiming the
  polyomino literature here, only measuring it directly for king animals.

## Novelty / provenance

Not previously computed in-project: `polyplet-zoo.md` reported only the n=18 fraction
snapshot ("falling as n grows"); no growth-constant. Complements the diagonal closed
forms (height structure) and [[nu-exponent]] (extent) with a **topological**
growth-constant. Data `results/holes_n18.txt`; script `experiments/holefree_growth.py`.
