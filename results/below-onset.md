# Below the onset: the diagonal formula's error term

The diagonal formula `T(n, n-k) = P_k(n)·3^(n-1-3k)` is a theorem for
`n ≥ 2k+1` (`docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`). The
line `n = 2k+1` is its **onset**, the first row at fixed `k` from which the
formula holds. This file records what happens below it. Results and grades:
a column's below-onset content is `k+1` integers (proved); the depth-1
defect comes from cluster families alone, with an algebraic quartic
generating function derived by the kernel method (proved on the walk side,
verified at 19 exact triangle entries, in Lean at all orders), and every
depth-1 constant follows from it (derived); the onset is sharp for every
`k` (proved, mod 3); depths 2, 3, 4 close the same way (exact, 74 entries);
the asymptotics at depths 1 to 7 (measured); the amplitude family is one
constant `α = 50/81` (derived under four stated assumptions); the bivariate
depth function has no closed form (theorem); the near-onset layer has width
about `k^0.4` (measured, downgraded on review); `P_1..P_9` follow from
cluster weights alone (exact). Every number is printed by the named script
unless the text says otherwise.

## 1. Definitions and the exact frame

Level `k = n - H`. Depth `j = 2k+1-n ≥ 1` counts rows below the onset, so
`n = 2k+1-j`, `H = k+1-j`; depth 1 is the row `n = 2H`. The defect is

```
D_j(k) = T(n, n-k) - P_k(n)·3^(n-1-3k),   n = 2k+1-j,
```

an exact rational for `k ≤ 19`, the reach of the stored `P_k`
(`orchestrator/sweep.go`, `diagCoeffTable`; `P_19` was fitted with no value
withheld). The formula reproduces every computed entry at or above the
onset, 380 of them (`experiments/defect_below_onset.py`).

Step 4 of the diagonal-law proof gives `[y^k] F = R_k(z)/(1-3z)^(k+1)`,
`R_k ∈ ℤ[z]`, `deg R_k ≤ 2k+1`; Step 5 splits off a correction polynomial
`D(z)` of degree at most `k`. The whole below-onset part of column `k` is the
`k+1` coefficients of `D(z)`:

```
D_j(k) = [z^(k+1-j)] D(z),        D_1(k) = lead(R_k) / (-3)^(k+1).      (I)
```

`experiments/depth1_gap_walk.py` verifies (I) with no `P_k`: `R_k` fitted
from the computed column alone is uniquely determined for `k ≤ 13`, integer,
with `lead(R_k)` equal to the first-principles values of
`experiments/spine_deeper.py` at `k ≤ 5`. With the level-9 assembly of §10:

```
lead(R_0..R_5) = 1, 4, -80, 1753, -40928, 987355
lead(R_6..R_9) = -24323825, 607833256, -15348306104, 390644841751
```

## 2. How the formula fails: exactness stops, accuracy does not

Correct leading digits of `T(n, n-k)` given by the formula at depth `j`
(`experiments/law_below_onset.py`):

| j \ k | 8 | 11 | 14 | 17 | 19 |
|---|---|---|---|---|---|
| 1 | 5.1 | 7.2 | 9.2 | 11.2 | 12.6 |
| 2 | 3.6 | 5.5 | 7.5 | 9.4 | 10.7 |
| 4 | 1.3 | 3.1 | 4.9 | 6.7 | 7.9 |
| 6 | -0.8 | 1.2 | 2.9 | 4.6 | 5.7 |
| 8 | -5.4 | -0.6 | 1.3 | 2.8 | 3.9 |

The relative error behaves as `C·(0.21)^k·(25)^j`. The defect is positive
throughout: the formula underestimates.

**Limit shape.** With `x = H/k`, `(1/k)·ln((T - formula)/T)` converges as
`g(x) + c(x)/k` (`experiments/defect_collapse.py`, Richardson in `1/k` over
`k = 10..19`, residuals about `1e-3` for `x ≥ 0.3`):

| x = H/k | g(x) | c(x) | digits at k=19 | at k=40 |
|---|---|---|---|---|
| 0.35 | -0.2232 | 4.14 | 1.8 | 3.9 |
| 0.50 | -0.3326 | 1.73 | 2.7 | 5.8 |
| 0.65 | -0.5416 | 0.66 | 4.5 | 9.4 |
| 0.80 | -0.8587 | 0.21 | 7.1 | 14.9 |
| 0.95 | -1.3084 | -0.07 | 10.8 | 22.7 |

`g(x) < 0` at every `x` tested down to 0.10, so at fixed `H/k` the relative
error decays exponentially in `k`; at `x ≤ 0.2` residuals reach 0.03 and
`c(x)` exceeds 20, so "no crossing" is resolved only for `x ≥ 0.3`. Along
`H` at fixed `k` the defect ratios decline smoothly to zero at the onset,
ratio-of-ratios 0.75 at `k = 13` and 0.82 at `k = 19`
(`experiments/defect_in_H.py`).

**No algebraic structure at reach.** In `k` at fixed depth
(`experiments/defect_structure.py`): C-finite to order 8 and P-finite to
`(r,d) = (4,4)`, last two points withheld, nothing at `j = 1..12`, while the
control `25^k/k!·(k²+3)` is found at `(1,3)`. The fuller search
(`experiments/defect_pfinite_full.py`, exact rational nullspace, last two
points withheld and required to be predicted, two equations of slack):

| sequence | result |
|---|---|
| `poly(k)·3^k` | found `(1,2)` |
| `9^k` | found `(1,0)` |
| `binom(2k,k)(9/4)^k` | found `(1,1)` |
| hash noise | none |
| `D_1(k)`, 18 points | none to `r=1: d≤5; r=2: d≤3; r=3: d≤1; r=4: d≤1` |
| `D_2(k)`, 18 points | none, same envelope |
| `D_3(k)`, 17 points | none to `r=1: d≤5; r=2: d≤2; r=3: d≤1` |
| `D_1(k)/[binom(2k,k)(9/4)^k]` | none, same as `D_1` |

The third control has exactly the measured asymptotics `9^k/√(πk)`, so the
search was not blind to that shape; the nulls were correct as scoped, `D_1`
being P-finite at order 35 (§3). `D_1/[binom(2k,k)(9/4)^k]` reads 0.0913508
at `k = 19` against `√6/27 = 0.0907218`.

## 3. Depth 1 is algebraic, with every constant derived

### 3.1 The defect from cluster families alone

In the Step 4 degree count, total degree `2k+1` is attained only when every
cluster row has exactly 2 cells, so the top coefficient assembles from the
all-pairs families of the gap walk (§4). With `S(y) = Σ W(2^ℓ) y^ℓ`,
`B(y) = 1 + Σ W^b(2^ℓ) y^ℓ`, `P̂(y) = Σ W^p(2^ℓ) y^ℓ` (interior,
bottom-edge, pure; top-edge equals bottom-edge by palindromy),

```
D_1(k) = [y^k] ( P̂(y) - B(y)² / (3 + S(y)) ).                        (II)
```

`experiments/depth1_gap_walk.py` computes the three families by the walk of
`experiments/allpairs_kernel.py` (new start and end vectors for the boundary
and pure variants), validates them against every enumerated weight
(interior `ℓ ≤ 8`; boundary and pure `ℓ ≤ 5`, plus a fresh `ℓ = 6` enumeration, `W^b(2⁶) = 2703074`, `W^p(2⁶) = 517701`), and checks
(II) against the exact defect at all 19 entries `k ≤ 19`. With no `P_k`
needed, `k = 200` takes 42 s; the series is positive with denominators
exactly `3^(k+1)`. The numerators `4, 80, 1753, 40928, 987355, …` were not
in the OEIS on 2026-08-09. (II) is derived from the proved chain identity
plus the tightness observation, machine-verified, and not yet written as a
standalone proof; §3.3 rests on it.

### 3.2 The quartic

Write `N(x) = Σ N_k x^k`, `N_0 = 0`, `N_k = 3^(k+1) D_1(k)`, so
`N = 3F_1(3x)`. The `N_k` are integers: `N_k = 3^(k+1)T(2k,k) - P_k(2k)`, and
`P_k` takes the integer values `T(n,n-k)·3^(3k+1-n)` at the `k+1` consecutive
integers `n = 2k+1..3k+1`, hence integer values on all of `ℤ`.
`experiments/depth1_minpoly.py` finds the minimal box by a mod-`p` dimension
scan (nothing below `deg_W = 4`, `deg_x = 8`) and solves it exactly over `ℚ`,
an irreducible quartic with coprime integer coefficients:

```
Φ(x,W) =   (27x-1)²(2187x⁶-5751x⁵+5502x⁴+3486x³-4329x²+449x+392)·W⁴
         + (27x-1)²(2916x⁶-7155x⁵+9636x⁴+54x³-4284x²+877x+420)·W³
         + 3(27x-1)(13122x⁷-29403x⁶+50193x⁵-14487x⁴-15039x³+5790x²+1640x-48)·W²
         + (27x-1)(8748x⁷-16767x⁶+36045x⁵-18573x⁴-7197x³+5076x²+1148x-16)·W
         + x(19683x⁷-30618x⁶+89667x⁵-63720x⁴-4920x³+16560x²+2736x-64)
```

`Φ(x, N(x)) = 0` through `x^200`; the fit used orders 0..56, so 144 orders
were not used in it.

**Derived** (`experiments/severance_w2_kernel.py`; gate
`experiments/severance_w2_gate.py`, negative control fires) by the kernel
method, the standard technique for a functional equation with a catalytic
variable. The polynomial `D(u) = u² - y(1+u+u²)²` whose vanishing the method
exploits factors into two quadratic branches in `s = √y`, small roots in
`ℚ(s)[A,B]`, `A² = (1-3s)(1+s)`, `B² = (1+3s)(1-s)`; the branch point `1-3s`
is Φ's `27x-1`. Two analyticity conditions per small root, the `[u³]`
self-consistency and `J(1)` fix the boundary unknowns in a `6×6` system;
(II) assembles `F_1 = c₀+c₁A+c₂B+c₃AB`, whose degree-4 norm is `Φ`
coefficient by coefficient after `y = 3x`, `W = 3F₁+1`. No series data
enters; the gate confirms exact equality and annihilation to `x^80`.

### 3.3 The onset is sharp for every k (proved 2026-09-05)

Modulo 3 the quartic factors:

```
Φ(x, W) ≡ 2 (W-1)³ ((1+x)W - x)        in F_3[x, W].                 (III)
```

`F_3[[x]]` is an integral domain, so the reduction `N̄` of `N` kills one
factor. `N̄ = 1` would need `N_1 ≡ 0`, and `N_1 = 4`. So `(1+x)N̄ = x`,
`N̄ = Σ_{k≥1} (-1)^(k+1) x^k`, `N_k ≡ (-1)^(k+1) (mod 3)`, `3 ∤ N_k`, hence

```
D_1(k) ≠ 0   for every k ≥ 1.
```

The formula fails at `n = 2k` for every `k ≥ 1`: (III) plus one integer. It
also makes "denominator exactly `3^(k+1)`" a consequence. Gate
`experiments/depth1_sharpness.py` (45 s) rebuilds `D_1` to `k = 200` from
the walk alone and checks integrality, annihilation through `x^200`, (III),
the branch selection and the congruence; its negative control fires on a
perturbed `Φ` and on a perturbed series.

### 3.4 The constants

At `x = 1/27` the leading coefficient of `Φ` vanishes to order 2 and nowhere
else. With `W = V/v`, `v = √(1-27x)`, the order-0 part is `(27V²-2)²`: two
sheets crossing at `V₀ = √6/9`, first Taylor step a quadratic with roots
`-439/1584 ∓ 23√3/792`, later steps linear. The measured `a` selects the
physical sheet (the other gives `0.0657…`); `C_1` is sheet-independent.

| quantity | derived | measured independently (`experiments/depth1_asymptotics.py`, K = 200) |
|---|---|---|
| growth rate | `27` in `x`, i.e. `9` per `k` | 9 |
| exponent | `(1-27x)^(-1/2)`, i.e. `k^(-1/2)` | `θ = -1/2 ± 1.5e-10` |
| amplitude | `C_1 = V₀/(3√π) = √6/(27√π)` | relative `1.6e-17` (order spread `1.2e-13`) |
| amplitude², `θ`-free | `A² = 2/243` | from `[y^k]F_1²`: `3.4e-15` |
| `1/k` coefficient | `a = -1/8 - V₂/(2V₀) = 3293/92928 - 3251√3/185856 = 0.005138939956706…` | measured - exact = `4.7e-17` |

So `D_1(k) = C_1·9^k·k^(-1/2)(1 + a/k + O(k^(-2)))`. `a` is small because
`3293/92928 ≈ 0.03544` and `3251√3/185856 ≈ 0.03030` nearly cancel, and it
lies in `ℚ(√3)`, outside every field the `k ≤ 19` recognition of §6
searched.

**Why `ρ ≈ 14.41` (§4) does not appear.** `P̂`, `B`, `S` each diverge at
`y = 1/ρ`, inside `|y| < 1/9`, but in `P̂ - B²/(3+S)` the pole cancels: the
spectral projection of an isolated eigenvalue is rank one, so the residues
factorize; the series grows at 9 (ratio times `√(k/(k-1))` = 8.999978 at
`k = 50`). **Closed door:** every factor of `disc_W Φ` has degree at most
10, and `ρ` has no minimal polynomial of degree at most 10 (PSLQ, §4), so
`ρ` is provably not on the curve. What survives is the walk's bulk edge,
mass `9 = 3²` per pair-row, the origin of the per-cell rate 3 of §6. The two terms of (II) are
the two terms of the earlier discarded-term decomposition
(`results/closed-doors.md`); its cancellation is this rank-one residue
cancellation.

**P-finite after all.** `experiments/depth1_recurrence.py` derives from `Φ`
the order-4 ODE (coefficient degrees 29..36) and the recurrence
`Σ_{s=-32..3} q_s(n) N_{n+s} = 0`, `deg q_s ≤ 4`: order 35, degree 4,
verified in exact integers at 56 positions.

**Other lattices.** Nothing above is king-specific except the constants.
`experiments/depth1_parametric.py` runs the construction with the drift set
as a parameter and closes depth 1 on the square and hexagonal lattices
(`docs/proofs/universal-diagonal-law.md`).

## 4. The all-pairs gap walk

All-pairs cluster weights `W(2^ℓ)` are weighted paths of a two-class walk
(`experiments/allpairs_kernel.py`): state `(g, c)`, `g` the gap between the
pair's cells, class `J` (one component) or `P` (two pending). The `P` bulk
is the `(1,2,3,2,1)` walk on steps `-2..+2`, mass 9; `J` adds weight-8 long
jumps to `(g′, P)` and weight-8 resets to `(1, J)`; ends: `J` pays `g+3` for
`g ≤ 2` and 6 for `g ≥ 3`, `P` finishes only at `g ≤ 2`. Reproduces the
direct enumeration for `ℓ ≤ 8`. Dominant eigenvalue of the truncated
operator, stable across `gmax = 30..140`, truncation error about `κ^gmax`:

```
ρ ≈ 14.41,   decay rate κ ≈ 0.421
```

The eigenvector is a localized mode `f(g) ~ κ^g` with
`ρ = κ² + 2κ + 3 + 2/κ + 1/κ²` and the `P` component on the plateau
`8 S_J/(ρ - 9)`. Since `ρ > 9` the growth is a boundary-localized
eigenvalue, not essential spectrum, which is why the family has a clean
growth constant and no C-finite recurrence. Two significant figures is the
honest size for `ρ`; a 37-digit expansion is reproducible at any `gmax`.
**Closed door:** the boundary system plus the quartic tail relation imply
`ρ` is algebraic, but PSLQ refutes every candidate of degree at most 10 with
coefficients at most `1e10` (two plausible low-precision fits were
truncation noise); eliminating about 15 boundary unknowns against the
quartic would give the minimal polynomial, expected degree above 20, not
done. Single-row weights are `(2s+1)²` exactly (proved); multi-row weights
have no closed form and no C-finite recurrence.

## 5. Depths 2, 3 and 4

Grade every cluster type `(s_1..s_ℓ)` by its excess `e = Σ(s_i - 2)`. The
coefficient `[z^(k+1-j)]` of the correction polynomial draws only on
families of total excess at most `j-1`, assembled through the chain identity
with binomial `(1-3z)` corrections (identity (C)/(D) in
`experiments/severance_w3_depths.py`; at `j = 1` it is (II)). Excess, not
rows of size 3, bounds the class: depth 3 needs the one-4-row family, depth
4 needs one-5-row, `4+3` and `3+3+3`. No triangle data and no `P_k` enter.

Family tables: Python row-transfer DP for `e ≤ 2`; `e = 3` at `K = 19` by
`cpp/severance_w3_families.cpp` (`build/severance_w3_families`, exact
`__int128`, 146 s), `results/severance_w3_families_K19_e3.txt`. Gate
`experiments/severance_w3_gate.py` (negative control fires; the triangle
side is assembled from the enumerated entries and the stored `P_k`, which
the candidate never touches):

```
depth 1: 19 entries match exactly (k = 1..19)
depth 2: 18 entries match exactly (k = 2..19)
depth 3: 17 entries match exactly (k = 3..19)
depth 4: 16 entries match exactly (k = 4..19)
```

Family validation: 31 types with 4 known weights each, exact; aggregated
`(k,e)` values against `results/severance_w1_weights_k9.txt` exact, all
four families, `e ≤ 3`; the `e = 0` series equals the depth-1 families to
`ℓ ≤ 9`; C++ against Python at three `(K, emax)` corners; span-cap
independence; fresh enumerations past every table at `k = 11` (five values,
`e ≤ 3`) and `k = 10` (`(5,2⁶)` pure = 41507430, `(3,3,3,2⁴)` pure =
424773396). First depth-4 values:

```
D_4(4..7) = 1400566/6561, 75221426/19683, 1199562484/19683, 51621741496/59049
```

Python family DP on dalby, one core: `(K, emax) = (19,1)` 5.6 s, `(27,1)`
20 s, `(60,1)` 395 s, `(15,2)` 73 s, `(19,2)` 214 s, `(23,2)` 516 s,
`(11,3)` 290 s. `experiments/severance_w3_modp.py` computes `D_j(k)` mod `p`
at 7.4× the exact path's speed.

## 6. The asymptotics at depths 1 to 7, measured

`experiments/onset_defect_nine.py`, `experiments/defect_nine_exponent.py`,
`experiments/defect_controls.py`, on the exact defects for `k ≤ 19`, in
mpmath at 60 digits. The naive estimator `L_k = k(D_k/D_{k-1}/9 - 1) → θ`
carries a systematic error up to 0.02 in `θ` and 0.03 in the rate against a
control whose correction series does not terminate: read naively, `θ`
drifts low with `j` and the rate falls to 8.98, 8.91, 8.77 at `j = 3, 4, 5`,
and a control with the right `θ` and rate reproduces both drifts. Below:
Richardson to order 3, the matched control's offset subtracted, the bar set
by that control at the same data length. The matched control assumes
`θ_j = j - 3/2`, so this is self-consistency, not independent confirmation.

| j | θ_j | j - 3/2 | rate |
|---|---|---|---|
| 1 | -0.5000 ± 0.0010 | -0.5 | 8.999998 ± 2.2e-05 |
| 2 | +0.5000 ± 0.0025 | +0.5 | 9.000000 ± 2.1e-03 |
| 3 | +1.5002 ± 0.0065 | +1.5 | 8.9988 ± 5.6e-03 |
| 4 | +2.5006 ± 0.0110 | +2.5 | 8.9945 ± 8.9e-03 |
| 5 | +3.4974 ± 0.0130 | +3.5 | 9.0395 ± 5.1e-02 |
| 6 | +4.4999 ± 0.0090 | +4.5 | 9.0025 ± 7.2e-02 |
| 7 | +5.4983 ± 0.0385 | +5.5 | not resolved |

**Amplitude** (`experiments/defect_amplitude.py`,
`experiments/defect_amplitude_family.py`; bars from four non-terminating
control flavors: smooth `1/k`, geometric tail, `1/k^1.5`, `log k/k`):

```
C_1 = 0.05118432,   control-backed bar 3e-07 relative;   √6/(27√π) is 5e-08 away
```

Contamination is bounded: the data's order-to-order step falls about 50×
between orders 2 and 5 where a half-power or log contaminant falls about
5×, and `ε = 5e-04` in `1 + ε/k^1.5` already overshoots. The recognition is
unique over all `√m/(n√π)`, `m ≤ 200`, `n ≤ 400`, within `1e-06`. A
relative error `ε` in `C_1` makes `k·B_k` (below) diverge linearly, and the
Richardson order-spread stays flat to `ε ≈ 1e-08`:

| ε | 1e-09 | 1e-08 | 3e-08 | 1e-07 | 1e-06 | 1e-05 |
|---|---|---|---|---|---|---|
| spread / baseline | 1.0 | 1.1 | 1.3 | 2.1 | 12.4 | 114.8 |

So `C_1` holds to about `1e-07` relative from data, conditional on
`θ = -1/2` (run at the shell; no script prints it).

**The family across depths.** With `A_j = C_j·Γ(j-1/2)`,
`R_j = A_j/A_1·(81/25)^(j-1)`:

| j | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| measured | 1.000000 | 1.000001 | 1.499785 | 2.498812 | 4.370843 | 7.866341 | 14.441622 |
| `binom(2j-2,j-1)/2^(j-1)` | 1 | 1 | 3/2 | 5/2 | 35/8 | 63/8 | 231/16 |
| bar | 5.5e-07 | 1.8e-04 | 4.1e-04 | 1.1e-03 | 2.9e-03 | 6.2e-03 | 1.1e-02 |
| rationals `q ≤ 32` inside bar | 1 | 1 | 3/2 only | 5/2 only | 8 | 18 | 20 |

At `j = 3, 4` the binomial value is the only rational with denominator at
most 32 inside the bar. At `j = 5, 6, 7` many fit, among them 118/27, 118/15
and 130/9, and at `j = 5` the value 118/27 = 4.370370 is closer to the
measurement than 35/8 = 4.375. (The source text said the binomial value is
inside the bar at `j = 5, 6, 7`; its own table has 35/8 off by `4.2e-03`
against a bar of `2.9e-03` and 63/8 off by `8.7e-03` against `6.2e-03`, and
the later bivariate note said 35/8 sits outside the bar at `j = 5`. The bars
are conditional on `θ_j`: `|d ln C/dθ| ≈ 4.9`, so relaxing `θ` by its
interval widens them about 20×, when even `j = 3` admits 19/13, 22/15,
25/17.) The measurement supports the family for `j ≤ 4` only; §7 derives
it. The `k·B_k` construction at `j = 2` with `C_2 = A_1·(25/81)/Γ(3/2)`
converges to `a_2 = 0.6851`, orders 3 to 5 agreeing to `4e-05`; a wrong
25/81 would diverge.

**The `1/k` coefficient from data** (`experiments/second_term.py`,
`experiments/second_term_recognise.py`). With
`B_k = D_1(k)·9^(-k)·k^(1/2)/C_1 - 1`, `k·B_k → a`:

```
a = 0.005139 ± 0.000033    (shell rescaling of the control; the script prints ± 2.0e-02)
```

526 rationals with `q ≤ 4000` lie inside the tighter bar, so recognition at
`k ≤ 19` is impossible. `|a| = 0.0051` means the bare leading term is
already accurate to `3e-04` relative at `k = 19`. The central binomial
`binom(2k,k)/4^k` has `a = -1/8`, twenty-four times larger and of the
opposite sign, so `D_1(k)` is not a constant times `binom(2k,k)(9/4)^k`.

**Per lattice cell the rate is 3.** On the depth-`j` line `9^k = 3^(n+j-1)`,
so `D_j(k) ≈ C_j·3^(j-1)·3^n·k^(j-3/2)`: at fixed depth the defect grows
like the number `T(n,n) = 3^(n-1)` of maximally thin animals of the same
cell count. The reading `9 = 3²` is the same fact in another variable: on
any lattice with onset `n = 2k+1`, `g^n = (g²)^k·g^(1-j)`, so no statistic
in such a triangle separates the readings. The per-cell one is simpler; 9
exceeds every strip constant `μ_H` (they climb to `λ ≈ 7.11`), and nothing
in the strip spectrum sits within 2% of 3 for `H ≤ 7` either
(`experiments/spectral_edge.py`; `results/closed-doors.md`). On the square
lattice `T_sq(n,n) = 1`, and `experiments/square_defect_rate.py` on
`results/bbox_square4_n21.txt` (`n ≤ 21`) finds `T_sq(n,n-k)` a polynomial
of degree exactly `k`, first valid at exactly `n = 2k+1`, for `k = 0..5`,
with depth-1 defect

```
T_sq(2k,k) - poly = +1, -1, +1, -1, +1     (k = 1..5)
```

No growth, and a sign alternation the king lattice lacks; since `1 = 1²`
this confirms the per-cell reading without discriminating it.
`experiments/depth1_parametric.py` later derived `D_1 = (-1)^(k+1)` there.

**Predictive check.** `experiments/defect_holdout.py` fits the amplitude on
`k ≤ 14` only, recovering `√6/(27√π)` to `2.0e-06` (not re-audited under the
control suite), then predicts entries it never saw: correct digits of
`T(2k,k)` for `k = 15..19` are 9.9, 10.5, 11.2, 11.9, 12.6 from the formula
alone and 13.2, 13.9, 14.6, 15.3, 16.0 with the defect estimate, a flat
+3.4. It certifies no integer, and for `n = 41` every entry with `k ≤ 19`
is at or above the onset.

## 7. The depth family is one constant: α = 50/81

### 7.1 The master identity

For cluster types with surplus `k_c = Σ(s_i-1)`, `ℓ_c` rows and excess
`e_c = k_c - ℓ_c`, every monomial `y^k z^ℓ` of the chain identity is
`Y^k t^e` under `Y = yz`, `t = 1/z`. With the excess-graded aggregates `Ŝ`,
`B̂`, `P̂` of `severance_w3_depths.families`, the chain telescopes:

```
G(Y,t) = P̂(Y,t) + B̂(Y,t)² / (t - 3 - Ŝ(Y,t)),                        (M)
D_j(k) = [Y^k t^(j-1)] G,      valid for j-1 ≤ k.                       (M′)
```

The formula part of `R_k` reaches only `t`-powers `≥ k+1`, and a type of
excess `e` has `k ≥ e+1`, so the grading is legitimate.
`experiments/ridgeline_master.py`: (M′) reproduces the depth-1 to depth-4
series at all 74 exact entries with `k ≤ 19`; its `t^0` slice is (II) at
`k = 1..19`; perturbing one excess-1 pure weight by `+1` breaks it. Depth is
a marker for cluster excess, a perturbation of the gap walk's row transfer.

### 7.2 The family in its natural normalization

`D_j(k) ~ C_j 9^k k^(j-3/2)` gives `F_j(Y) ~ C_j Γ(j-1/2)(1-9Y)^(-(j-1/2))`,
one scaling variable `τ = t/(1-9Y)`. At fixed chain length `L`
(`experiments/ridgeline_scaling.py`, checked term by term for `M ≤ 4`),
`G/t ~ C_1 Σ_L (9Y)^L L^(-1/2) 𝒜(tL)`, `𝒜(ξ) = Σ_M (C_(M+1)/C_1) ξ^M`. If
the dominant singularity is a square-root branch point whose location moves
analytically with `t`, `1 - 9Y_c(t) = αt + O(t²)`, exponent fixed, then

```
C_(M+1) = C_1 α^M / M!,      𝒜(ξ) = exp(αξ),                            (*)
```

i.e. depth `M+1` is the `M`-th derivative of depth 1 up to less singular
terms. With `α = 50/81`, (*) is the measured family:

| j | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| `2^(j-1)/(j-1)!` | 1 | 2 | 2 | 4/3 | 2/3 | 4/15 | 8/105 |
| times `Γ(j-1/2)/Γ(1/2)` | 1 | 1 | 3/2 | 5/2 | 35/8 | 63/8 | 231/16 |
| `binom(2j-2,j-1)/2^(j-1)`, §6 | 1 | 1 | 3/2 | 5/2 | 35/8 | 63/8 | 231/16 |

The central binomials were the `Γ(j-1/2)` weighting in disguise, and
`j = 5` is 35/8. The rival 118/27 came from scanning the `Γ`-weighted
quantity; in the natural normalization it is 1888/2835 and needs `α` to
change to 0.6171206 at `M = 4` alone. The depths sum to
`Σ_j A_j t^(j-1) = (√6/27)/√(1 - 50t/81)`.

### 7.3 α, derived by a finite count

`α = dλ/dt` at `(Y,t) = (1/9, 0)`, `λ` the zero-momentum eigenvalue of the
row transfer. At `t = 0` only 2-cell rows survive and the bulk critical mode
is two pending components far apart, each taking one king step: mass
`3 × 3 = 9`, critical at `9Y = 1`. At first order in `t` exactly one row is
a 3-cell row, costing `Y² t`, and the next 2-cell row must resolve what it
leaves: `λ = 9Y + Y² t Σ/9`, so

```
1 - 9Y_c = t Σ/729,     α = Σ/729,
Σ = Σ over 3-cell rows R out of the bulk state of (# 2-cell rows after R).
```

`experiments/ridgeline_vertex.py` counts both with
`severance_w3_depths.transitions`, the vetted row transfer (a row is legal
iff every pending block of the previous row has a cell adjacent to it):

```
2-cell rows out of the bulk state = 9    at every gap G = 8..14
Σ = 450                                  at every G = 10..14 and at span caps G+6, G+12
α = 450/729 = 50/81 exactly
```

The trap: a 3-cell row may leave three pending blocks, and one cell of the
next row can be adjacent to two of them, so a 2-cell row still closes it;
filtering intermediates to two blocks loses 72 of the 450 and gives 14/27
(`Σ = 378`). Deleting one entry of the 3-cell row table gives 438;
restoring it returns 450.

### 7.4 Verification

| quantity | value | script |
|---|---|---|
| (M′) vs (C)/(D), depths 1–4, `k ≤ 19` | 74/74 exact | `ridgeline_master.py` |
| (M) at `t^0` vs (II) | `k = 1..19` exact | `ridgeline_master.py` |
| one perturbed excess-1 weight | breaks the identity | `ridgeline_master.py` |
| `C_1` from `D_1`, `k ≤ 60` | 0.0511843184401, relative `2.46e-12` from `√6/(27√π)` | `ridgeline_scaling.py 60 1` |
| `α_1`, amplitude form, `k ≤ 60` | 0.617283951065, `7.25e-10` from 50/81 | `ridgeline_scaling.py 60 1` |
| `α_1`, derivative form, `k ≤ 60` | 0.61728395128067, `1.07e-09` from 50/81 | `ridgeline_scaling.py 60 1` |
| `α_1, α_2`, `k ≤ 29` | 0.61728401849, 0.61728123436; deviations `1.10e-07`, `-4.40e-06`; calibrated bias `2.7e-06`, `5.8e-06` | `ridgeline_scaling.py 29 2` |
| `α_3`, `k ≤ 19` | 0.61725242246, `-5.11e-05` from 50/81; calibrated bias `1.1e-04` | `ridgeline_scaling.py 19 3` |
| `Σ`, `α` | 450, 50/81 exactly | `ridgeline_vertex.py` |

Every `α_M` deviation is within the estimator's bias, measured on synthetic
families obeying (*) exactly with a `1 + c₁/k + c₂/k²` correction of
realistic size: depth 2 fixes `α` to `1.1e-09` relative, depth 3 to
`4.4e-06`, depth 4 to `5.1e-05` against a bias envelope of `1.1e-04`. The
departure 118/27 would demand at `M = 4` is `2.65e-04`: a factor of 5.2
over the largest deviation seen at `k ≤ 19`, 29.8 at `k ≤ 25`, 60.1 at
`k ≤ 29`. The derivative form is the sharp estimator: dividing `D_(M+1)(k)`
by `(α^M/M!)·9^(-M)·(k+M)!/k!·D_1(k+M)` removes `9^k`, `k^(M-1/2)` and part
of the `1/k` structure.

### 7.5 What is assumed

Derived: (M)/(M′); "moving square-root branch point, fixed exponent" ⟹ (*)
⟹ the binomial family; `Σ = 450`, hence `α = 50/81`. Assumed:

1. The exponent stays exactly `-1/2` for small `t > 0`. Evidence: the bulk
   dispersion `K(u) = (1+u+u²)²/u²`, `u` marking the gap, has `K(1) = 9`,
   `K′(1) = 0` (`K(u) = K(1/u)`) and `(log K)″(1) = 4/3`, printed
   symbolically; a nondegenerate quadratic minimum gives the Gaussian
   transverse integral and `(1-9Y)^(-1/2)`, and an analytic perturbation
   keeps it nondegenerate, so `t` moves the minimum's height (`α`) but not
   the exponent. Plus `θ_j = j-3/2` measured at `j ≤ 7`. Missing: the step
   from the dispersion to the assembled `G`.
2. `Y_c(t)` is analytic at `t = 0`. Each order in `t` adds finitely many
   families; convergence not proved.
3. The `ρ`-cancellation persists at every order in `t`. Rate 9 is measured
   at every `j ≤ 6`, derived at `j = 1` only.
4. The bookkeeping behind `α = Σ/729`, a flat zero-momentum projection in
   the delocalized sector. `J` carries the rank-one long jump whose
   zero-momentum row sum diverges with the span cap (the localized `ρ`), and
   the local class transfer `[[9,0],[-18,9]]` is a Jordan block at the
   critical eigenvalue, where a naive first-order perturbation is
   ill-defined. Evidence: of the 450 excursions, 450 land in `P` and 0 in
   `J` at every `G = 10..13`, so the vertex acts wholly inside `P`, a
   translation-invariant walk of mass 9 whose flat mode is the critical
   mode; and the derived constant matches a measurement good to `1.1e-09`.
   Unproved: the passage from "the zero-momentum mass shifts by `Y² t Σ/9`"
   to "the branch point of `G` moves by `αt` with its exponent intact",
   which is assumption 1 again.

Verified, not derived: `α_M` constant over `M = 1, 2, 3` within bias. The
family at `j = 5, 6, 7` is a prediction; the case against 118/27 is
structural and does not answer someone who rejects the law's form. The
enumeration, not the prose, is the claim: a plausible filter gave 14/27 and
looked self-consistent until checked. The conjecture that every fixed depth
is algebraic on a curve with branch point `1/27` stands refined: each slice
keeps its singularity at `Y = 1/9`, and the exponent `-(j-1/2)` is how the
moving branch point of the resummed `G(Y,t)` looks after expansion in `t`
at fixed `Y`. The scaling function is a square root, not Airy, because
`(log K)″(1) ≠ 0`; whether that also fixes the layer exponent of §9 is not
established.

## 8. The bivariate function has no closed form

With `G(y,t) = Σ_j t^j F_j(y)`, `F_j(y) = Σ_k D_j(k) y^k`:
`G(y,t) = t·F(yt, 1/t)`, `F(y,z) = Σ_k y^k D_k(z)` the below-onset column
generating function; depth slicing reads its anti-diagonals.

**Theorem.** `G(y,t)` is not D-finite, hence not algebraic. The strip
generating function `Σ_n T(n,H) x^n` has all but finitely many terms below
the onset, so it is a fixed-height section of `F` plus a polynomial, which
does not move a radius of convergence; the strip growth constants `μ_H` have
algebraic degree tending to infinity (`results/anisotropic-not-dfinite.md`;
atom degrees 1, 2, 4, 9, 29, 68, 181, 462, …), while a D-finite bivariate
function has sections whose singularities have bounded degree.

**Empirical shadow** (`experiments/severance_w4_field.py`, mod-`p` scan at
`K = 110`, 16 rows withheld): depth 1 has minimal box
`(deg_y, deg_W) = (8,4)`; depth 2 has no relation with `deg_W ≤ 4` to
`deg_y = 18` and none with `deg_W ≤ 6` to `deg_y = 12`, as an inalgebraic
`G` forces; the hypothesis that all depths lie in `ℚ(s)[A,B]` is refuted.

**What survives** is the dominant-singularity data,
`Σ_j A_j t^j = (√6/27)·t/√(1 - 50t/81)`, branch at `t = 81/50`, which §7
derives. On 2026-08-10 the excess-4 table was priced out of reach (Python
`families(12, emax=4)` over 130 s, C++ at 10 threads `families(16, emax=4)`
over 200 s, `k ≈ 30` days for one point); the later record
(`results/undertow.md`, 2026-08-23) is `families 21 4` on dalby, 8 threads,
4 h 54 m, 18,743 MB peak, giving exact `D_5` to `k ≤ 21`. Sharpening `R_5`
from data needs `D_5(k)` to `k ≈ 28..30`, which no table reaches.

## 9. The near-onset layer

The family and the per-depth singularity combine into the formal
resummation `(√6/27)·(1 - 9z - (50/81)t)^(-1/2)`, i.e.

```
D_j(k) ≈ (√6/27)·binom(2N,N)/4^N·binom(N,k)·9^k·(50/81)^(j-1),   N = k+j-1.
```

It does not hold globally (`experiments/defect_bivariate.py`): slope per
unit `k` of `ln D_measured - ln D_predicted` in bands of `x = H/k`:

| x band | 0.85–1.00 | 0.70–0.85 | 0.55–0.70 | 0.40–0.55 | 0.25–0.40 | 0.10–0.25 |
|---|---|---|---|---|---|---|
| slope per k | -0.009 | -0.077 | -0.201 | -0.398 | -0.677 | -1.146 |

The amplitudes are asymptotic in `k` at fixed `j`, and the resummation needs
`j ~ k(1-x)`. Predicting `g(x)` from it fails: `g(0.35) = +0.66` against the
measured `-0.22`.

**The scaling variable** (`experiments/boundary_layer.py`; residual over 168
computed entries below the onset, `k = 4..19`, every depth with `H ≥ 2`).
Two families, scored by how tightly the residual collapses onto one curve
and each calibrated on synthetic surfaces built exactly in that family:

| family | control floor | best measured score |
|---|---|---|
| A: `f(j/k^p)`, a layer of width `k^p` | 0.0212 | 0.0224 |
| B: `k^q·φ(j/k)`, large deviation | 0.0270 | 0.0496 |

A reaches its floor; B does not, so the large-deviation form is excluded.
Exponent `p = 0.385`, interval `[0.345, 0.485]` where the score stays within
15% of the best; calibration surfaces at `p = 0.35, 0.40, 0.45, 0.60` return
0.325, 0.390, 0.440, 0.590, so the scan cannot separate 0.45 from 0.50.

| candidate | score / best |
|---|---|
| p = 2/5 | 1.05 |
| p = 1/2 (Gaussian) | 1.18 |
| p = 2/3 (Airy) | 1.90 |
| p = 1 (no layer) | 5.17 |

Airy and no-layer are excluded robustly. The best-fit value is fragile and
1/2 is not excluded: resampling returns 0.44 dropping `k < 8`, 0.315 keeping
`j ≤ 5`, 0.275 keeping `u ≤ 2`, 0.44 and 0.425 at 16 and 24 bins. The
defensible statement is `p ≈ 0.4`, with 2/3 and 1 excluded. The curve
`f(u) = 0.612·u(1-u)`, `u = j/k^0.385`, is withdrawn: its rms 0.147 was
measured against a range of 16.91 dominated by the `u > 1` tail, and inside
the layer (31 entries, `u < 1`) the residuals run +0.007 to +0.10 where the
curve says 0.10 to 0.15; refitting on the interior gives `c = 0.063`. Real
is the sign structure: small and positive inside, negative and growing
outside, crossing near `u ≈ 1`, i.e. `j ≈ k^0.4` (at `k = 19`, `j ≲ 3`,
near where §6 loses uniqueness; suggestive only). At fixed `x = H/k`,
`u ≈ k^0.615·(1-x) → ∞`, so `g(x)` lives in the tail and the data reaches
only `u = 5.8`. The interval, `c` and the resampling figures were computed
off-script; the script prints none of them. (Two adversarial reviews on
2026-08-09 found one failure mode across this theme: numbers computed at the
shell and quoted at a precision no script reproduces. Every such number
above is marked.)

## 10. P_1..P_9 from cluster weights, with no enumerated entry

Weights: `cpp/severance_w1.cpp` (`build/severance_w1`, exact `__int128`
with overflow check), all 511 compositions to surplus 9 in
`results/severance_w1_weights_k9.txt` (`k ≤ 8` in
`results/severance_w1_weights_k8.txt`). Assembly
`experiments/severance_w1_assemble.py`, exact fractions through the chain
identity: the derived `P_k` equals the stored table coefficient by
coefficient for `k = 1..9`, reproduces 3 computed in-onset entries per
level, `deg R_k = 2k+1` throughout. Gate `experiments/severance_w1_gate.py`
(negative control fires 23 assertions): per-composition values exact at
`k ≤ 5`; fresh level-6 enumerations (`(7,)` full; `(4,4)`, `(3,5)` boundary
and pure fresh, interior against the earlier 8.4 h and 3.7 h Python values);
completeness, reference order, reversal symmetry and single-row closed forms
at every level to 9. `k = 9` ran on dalby: 66 min, 16 threads, 53 GB peak.
`k = 10` was declined on memory: peak RSS passes dalby's 125 GB, the tail
being one stack whose state map alone is tens of GB; extending needs a
state-space reduction, not cores.

**Coverage as of 2026-08-09.** With `P_k` from weights for `k ≤ 9`, the
strip engine for `H ≤ 14` and depths `j ≤ 4`: rows `n ≤ 24` covered end to
end by two independent programs; rows 25..33 formula-covered except for the
two entries per level at `n = 2k+1, 2k+2` that determine `P_10..P_18`; rows
34..40 needed `P_19` and beyond. The later record (`results/undertow.md`,
`results/confidence.md`) determines levels 19 to 21 from entries below the
onset using these `D_j`, which is what `a(41)` rests on.

## 11. Lean

Gate `make gate-notary` (sorry/axiom grep plus `lake build`; axiom audits
are `#guard_msgs` blocks in the modules). Status of record
`polyplets/PROOF-STATUS.md`; modules under `polyplets/Polyplets/`. Axioms
`propext, Classical.choice, Quot.sound`, plus `Lean.ofReduceBool` where
`native_decide` is used, audited per theorem.

- `GapWalkBridge.lean`: walk = enumeration at `ℓ ≤ 3` for interior,
  boundary and pure weights; the 36 depth identities of
  `DepthAssembly.lean` unconditional; (II) on walk-built series equals the
  depth-1 values at `k ≤ 8` (`f1_matches_depth1`); walk = C++ table at
  `k ≤ 19` (`walk_table_19`).
- `DepthOneConstants.lean`, over any characteristic-0 field with `s2² = 2`,
  `s3² = 3`, plus `ℝ`: `phiC4 = (27x-1)²·g`, `g(1/27) = 7929856/19683 ≠ 0`;
  `Ψ(v, wv) = Φ((1-v²)/27, w)` polynomial;
  `Ψ(0,V) = (7929856/14348907)(27V²-2)²`, `27V₀² = 2`, `(V₀/3)² = 2/243`;
  `Ψ(v, V₀+V₁v+V₂v²) = v⁴·Q₄(v)` explicit, nonzero pivot;
  `a = -1/8 - V₂/(2V₀) = 3293/92928 - 3251√3/185856`.
- `DepthOneSeries.lean`: walk `N(x)` = the numerators to `k ≤ 19`;
  `Φ(x, N(x)) ≡ 0 mod x^61` in exact rationals (`phi_annihilates`).
- `GapWalkRows.lean`, `GapWalkCanon.lean`, `GapWalkTrunc.lean`:
  `walkFamiliesCap_exact`, every gap cap `M ≥ 2L+3` emits the same family
  triples as `walkFamilies L`, so the `k ≤ 19` and `k ≤ 8` results bind the
  exact walk. Standard axioms.
- `GapWalkStacks.lean`, `GapWalkPeel.lean`, `GapWalkEnds.lean`,
  `GapWalkBij.lean`: `walkFamilies_configs`, every emitted triple is
  `(V ℓ ℓ, Vᵗ ℓ ℓ, Vp ℓ ℓ)` for every `L`. Literal values past enumeration
  reach, no `native_decide`: `V 4 4 = 68314`, `V 5 5 = 981085`,
  `V 6 6 = 14115141`; `Vᵗ 4 4 = 13103`, `Vᵗ 5 5 = 187965`,
  `Vᵗ 6 6 = 2703074`; `Vp 4 4 = 2515`, `Vp 5 5 = 36021`, `Vp 6 6 = 517701`.
- `DepthOneKernelPhi.lean`: `phi_annihilates_exact`, `Φ(x, N(x)) = 0` in
  `ℚ⟦x⟧` at every order, proved inside `ℚ[X,a,b]/(a²-AA, b²-BB)` by
  machine-generated `linear_combination` certificates, standard axioms.
  `phi_annihilates_of_exact` re-derives the `mod x^61` result from it under
  the explicit hypothesis `hbridge` (`truncL 61 Nexact = nSeries 60`), that
  the closed form is the walk's enumeration at all orders.

**Two boundaries, neither unfinished work.** (1) The all-orders tie between
walk and triangle, identity (I), is `hbridge` and the general-`k`
factorization lemma of `Diagonal.lean`; it reduces to a closed form for the
single-cluster generating function `B(y)`, and there is none: 18 converged
terms from the `a(40)` triangle (9 at `a(21)`) admit no algebraic or
D-finite relation at reachable complexity (`experiments/braw_from_data.py`;
`docs/proofs/T-n-nm2-and-general.md` §5). The tie stays exact at finite
order: Lean at `k ≤ 8`, two programs at `k ≤ 19`, annihilation to order 60.
(2) The analytic transfer from branch data to `k^(-1/2)` and `√π` is
real-analytic, without Mathlib support, and out of scope. Separately,
`docs/lean-below-onset-scope.md` records that using the below-onset
identity to determine a level (F1) and substituting a corrected entry for
an onset entry (F2) are not stated in Lean.

## Open problems

- Prove the defect asymptotics at general depth: assumptions 1 to 4 of
  §7.5. Item 4 is self-contained: redo the first-order perturbation with
  the left and right critical vectors of the `(J,P)` transfer.
- Write (II) as a standalone proof; §3.3 rests on it.
- `ψ″(0)`, the `O(t²)` motion of the branch point, by the vertex method one
  order up; a consistency target, not a gap.
- Is `D_2` algebraic? No relation with `deg_W ≤ 6` to `deg_y = 12`.
- `g(x)` is unexplained; whether the scaling function of §7 and the layer
  exponent of §9 are the same object.
- The minimal polynomial of `ρ`; closed forms for multi-row cluster
  weights and for `B(y)`; `P_k` from weights past `k = 9` (needs a
  state-space reduction in the stack DP).
- In Lean: discharge `hbridge` to a chosen finite order; fixed-`k` cases
  `k = 3, 4` in `Diagonal.lean`; F1 and F2 of
  `docs/lean-below-onset-scope.md`.

## Reproduce

Python 3 scripts, run from the repository root, seconds each unless noted;
`experiments/slope2_law_vs_truth.py` supplies `read_pk`, `read_tri`, `law`.

```
python3 experiments/defect_below_onset.py; python3 experiments/law_below_onset.py
python3 experiments/defect_collapse.py; python3 experiments/defect_structure.py; python3 experiments/defect_in_H.py
python3 experiments/defect_pfinite_full.py
python3 experiments/onset_defect_nine.py; python3 experiments/defect_nine_exponent.py; python3 experiments/defect_controls.py
python3 experiments/defect_amplitude.py; python3 experiments/defect_amplitude_family.py
python3 experiments/second_term.py; python3 experiments/second_term_recognise.py
python3 experiments/square_defect_rate.py; python3 experiments/spectral_edge.py; python3 experiments/defect_holdout.py
python3 experiments/depth1_gap_walk.py                # 42 s
python3 experiments/depth1_minpoly.py; python3 experiments/depth1_asymptotics.py; python3 experiments/depth1_recurrence.py
python3 experiments/depth1_sharpness.py               # 45 s
python3 experiments/depth1_parametric.py
make gate-severance-w1 gate-severance-w2 gate-severance-w3 gate-notary
build/severance_w3_families 19 3                      # 146 s, results/severance_w3_families_K19_e3.txt
python3 experiments/severance_w3_modp.py; python3 experiments/severance_w4_field.py
python3 experiments/ridgeline_master.py; python3 experiments/ridgeline_vertex.py
python3 experiments/ridgeline_dump_families.py 60 1   # 395 s; writes results/severance_w3_families_K60_e1.txt
python3 experiments/ridgeline_scaling.py 60 1         # 4 s with the cache; also 29 2 and 19 3
python3 experiments/defect_bivariate.py; python3 experiments/boundary_layer.py
python3 experiments/allpairs_kernel.py                # ρ at any gmax
```

`severance_w3_depths._load_table` scans only `K_table < 40`; the `K = 60`
cache is read by `ridgeline_master.load_families` and reproduces the
uncached run exactly. Data formats:
`results/ns_a40/perheight/h{H}.out` is `n count`;
`results/bbox_square4_n21.txt` is `n H W count`, both orientations;
`results/bbox_polyplets_n17_exact.txt` is `H W n count`. `P_k` is stored in
`orchestrator/sweep.go` (`diagCoeffTable`) with coefficients descending and
a denominator; ascending evaluation fails loudly.

## Sources

- `results/onset-defect-law.md` (deleted 2026-09-06; its content is above)
- `results/onset-defect-depth1-closed.md` (deleted 2026-09-06; its content is above)
- `results/onset-defect-depths234.md` (deleted 2026-09-06; its content is above)
- `results/onset-defect-crossover.md` (deleted 2026-09-06; its content is above)
- `results/ridgeline-depth-amplitudes.md` (deleted 2026-09-06; its content is above)
- `results/depth-tower-bivariate-dead-end.md` (deleted 2026-09-06; its content is above)
- `results/diagonal-law-below-onset.md` (deleted 2026-09-06; its content is above)
- `results/allpairs-kernel.md` (deleted 2026-09-06; its content is above)
- `results/severance-w1-anchor-cut.md` (deleted 2026-09-06; its content is above)
- `results/notary-depth1-lean.md` (deleted 2026-09-06; its content is above)
- `docs/onset-defect-handoff.md` (deleted 2026-09-06; its content is above)
