# Boundary-push probe #2/#4: intrinsic complexity of the T(n,H) slicings

**2026-07-02.** `experiments/recurrence_probe.py` on existing data (triangle
through n=24 + a25 swept rows, H3–16 to n=25). Measures the minimal
constant-coefficient (C-finite) linear-recurrence order of each slicing of the
triangle — the *intrinsic* complexity of that direction, independent of our
representation.

## Result

**Diagonal slicing `T(n, n-k)` vs n — order = 2k+1, exactly, linear in k:**

| k | 0 | 1 | 2 | 3 | 4… |
|---|---|---|---|---|---|
| min order | 1 | 3 | 5 | 7 | ≥9 (data-limited) |

Root is 3 (all multiplicity) → `poly_{2k}(n)·3^n`. This *recovers the known
closed-form structure exactly* (P_k has degree 2k) — the probe is calibrated.

**Row slicing `T(n, H)` vs n — order grows fast; determined cases:**

| H | 2 | 3 | 4… |
|---|---|---|---|
| min order | 3 | 7 | ≥11 (data-limited) |
| dominant root μ_H | 2.4142 = 1+√2 | 3.4437 | ↗ |

μ_H are the finite-strip growth constants, climbing toward λ≈7.1 as H→∞
(μ_2 = 1+√2 is exact). Order jumps 3→7 from H2→H3 and blows past our data
ceiling by H4 — the row direction is high-complexity (plausibly exponential in H;
under-determined beyond H3).

## Interpretation (what it means for pushing the boundary)

1. **The diagonal is provably the low-complexity direction** — order *linear*
   in k (2k+1) vs the row direction's fast growth. This quantifies *why* the
   √λ diagonal sweep + closed-form P_k work, and says no simple re-slicing beats
   it: the diagonal aligns with the 3^n geometric structure, rows do not.
2. **The closed-form frontier is a linear treadmill.** Extending the closed-form
   region by one diagonal (k→k+1) costs 2 more coefficients (order 2k+1→2k+3),
   needing 2 more data points — which arrive from ~1 more computed term each.
   So closed forms advance ~one diagonal per computed term; they shave a
   fixed-width slab off the top, they do **not** collapse the exponential bulk.
   (Matches the a26–a30 plan's "circular data" observation for P_11/P_12/P_13.)
3. **Therefore the real lever is orthogonal to slicing.** The row-direction
   complexity that grows (probably) exponentially in H *is* the frontier size.
   Attacking it needs a smaller *representation of the frontier itself*, not a
   better direction — which is exactly the tensor-network / MPS probe (#1,
   `experiments/frontier_svd/`). This probe elevates that experiment: slicing
   tricks are near-exhausted, frontier compression is where a breakthrough
   would have to come from.

## Caveats / honest limits

- Orders past ~11 are lower bounds (need more n per H than we have).
- Only *linear* slicings n−H=const were tested against long data runs; exotic
  statistics (perimeter, column count, spectral coordinates) aren't in the
  triangle and would need fresh enumeration to probe — an open door, not tested.
- C-finite only; a P-finite (polynomial-coefficient) recurrence could be lower
  order for the rows, untested here.
