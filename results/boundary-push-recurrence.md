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

Root is 3 (all multiplicity) → `poly(n)·3^n`.

**CORRECTION 2026-07-10 (experiments/Pk_explicit.py, exact fit):** the eventual
closed form is `T(n,n−k) = P_k(n)·3^n` with **degree(P_k) = k, order k+1**, onset
`n = k+2` — NOT degree 2k. Verified trivially for k=1: `T(n,n−1)/3^n` has constant
first difference `25/81`, i.e. exactly linear (`T(n,n−1)=5(5n−9)·3^{n−4}`, n≥3).
The `2k+1` above is the minimal recurrence fitting the FULL diagonal **including
the pre-onset transient point** at `n=k+1` (the `H=1` bar, which disobeys the
closed form); absorbing that transient inflates the order, and the original note
mis-read degree `2k` off it. Real degrees k=1..5: **1,2,3,4,5**. Leading coeff
~`5^{2k}`, denom (Newton basis) `3^{3k+1}` (results/production-matrix-probe.md).

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
   region by one diagonal (k→k+1) costs **1 more coefficient** (degree k→k+1, per
   the 2026-07-10 correction above — NOT 2). Closed forms still shave only a
   fixed-width slab off the top and do **not** collapse the exponential bulk, but
   the per-diagonal cost is half what this note originally claimed — worth
   re-checking against the a26–a30 plan's data economics (task: does that plan
   assume degree 2k and thus over-provision witnesses?).
3. **Therefore the real lever is orthogonal to slicing.** The row-direction
   complexity that grows (probably) exponentially in H *is* the frontier size.
   Attacking it needs a smaller *representation of the frontier itself*, not a
   better direction — which is exactly the tensor-network / MPS probe (#1,
   `experiments/frontier_svd/`). This probe elevates that experiment: slicing
   tricks are near-exhausted, frontier compression is where a breakthrough
   would have to come from.

## Follow-up: is there a 2D accelerator? (`holonomic2d_probe.py`) — NO

Pushed the idea further rather than discarding it: searched for a joint 2D
P-recursive relation `sum c[i,j,d,e] n^d H^e T(n-i,H-j) = 0` (fit on n≤maxn-2,
required to verify on held-out largest-n cells, mod-p). **None exists** up to
shifts (4,3) and coefficient degrees (3 in n, 2 in H).

Meaning: T(n,H) is **not 2D-holonomic** — there is no global "compute the
expensive frontier cell from its cheaper neighbours" recurrence. The 1-D slices
are each holonomic (diagonal = closed form; row = high-order C-finite) but they
do not knit into a joint D-finite structure. This *rigorously bounds* the
recurrence/GF family of accelerators: the diagonal closed forms are essentially
all of it. Confirms the remaining hope must attack the frontier representation
itself (tensor-network / MPS), which is orthogonal to holonomy.

## Caveats / honest limits

- Orders past ~11 are lower bounds (need more n per H than we have).
- Only *linear* slicings n−H=const were tested against long data runs; exotic
  statistics (perimeter, column count, spectral coordinates) aren't in the
  triangle and would need fresh enumeration to probe — an open door, not tested.
- C-finite only; a P-finite (polynomial-coefficient) recurrence could be lower
  order for the rows, untested here.
