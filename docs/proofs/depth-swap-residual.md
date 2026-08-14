# The staircase residual below onset is a defect combination

2026-08-14. Proves the identity `experiments/depth_swap_anchors.py` measures,
and on which `results/depth-swap-anchors.md` rests. Three lines, once the right
two facts are put next to each other; the point is that neither of them is new.

## Statement

Fix `k >= 1` and `H >= 1`, and write `j = k+1-H` for the depth below the
staircase's onset. With `D_j(k)` the below-onset defect of
`results/onset-defect-law.md` (`D_j(k) := T - law` at depth `j`, and
`D_j(k) := 0` for `j <= 0`),

> **Theorem.**
> `T(H+1+k, H+1) - sum_{i=0..k} mu_i T(H+k-i, H)
>    = D_{j-1}(k) - sum_{i=0..j-1} mu_i D_{j-i}(k-i).`

At `j <= 0` both sides vanish and this is the staircase itself. At `j = 1` it
reads `R = -3 D_1(k)`, which is `results/severance-w1-anchor-cut.md`'s
`lead(R_k) = (-3)^(k+1) D_1(k)` seen through the staircase.

## The two inputs

**(I) The P-staircase is a polynomial identity.** For every `k`,

    P_k(n+1) = sum_{i=0..k} mu_i 3^(2i-1) P_{k-i}(n-i)

as polynomials in `n` — *not* a statement about counts, and so carrying no
onset condition. Both sides have degree `<= k` (the shape theorem,
`docs/proofs/diagonal-law.md`, Lean), so agreement at `k+1` points forces it
everywhere; `scripts/gen_grand_pin.py` emits it per level as `Pstair{k}` and
discharges it by `ring`, and its numeric oracle checks it at `k+2` points.
`experiments/depth_swap_anchors.py --pstair` checks 1026 instances spanning
both sides of onset and into negative `n`, mismatches 0.

**(II) The diagonal law is exact at and above onset.** `T(n,n-k) =
P_k(n)·3^(n-1-3k)` for `n >= 2k+1` (`docs/proofs/diagonal-law.md`, proved), and
`D_j(k)` is *defined* as the amount by which that fails below it. So writing
`L(k,n) := P_k(n)·3^(n-1-3k)` for the law value at any `n`, and `Ď(k,H)` for
the defect of the level-`k` cell in column `H`,

    T(H+k, H) = L(k, H+k) + Ď(k,H),        Ď(k,H) = D_{k+1-H}(k),

with `Ď(k,H) = 0` whenever `H >= k+1`.

## Proof

The law values satisfy the staircase identically. Put `n = H+k` in (I) and
multiply by `3^(H-2k)`:

    3^(H-2k) P_k(H+k+1) = sum_i mu_i 3^(H-2k+2i-1) P_{k-i}(H+k-i).

The left side is `P_k(H+1+k)·3^((H+1+k)-1-3k) = L(k, H+1+k)`, the law value of
the cell `T(H+1+k, H+1)`. The `i`-th right-hand term is
`mu_i P_{k-i}(H+k-i)·3^((H+k-i)-1-3(k-i)) = mu_i L(k-i, H+k-i)`, the law value
of the cell `T(H+k-i, H)`, which sits on level `k-i`. So

    L(k, H+1+k) = sum_{i=0..k} mu_i L(k-i, H+k-i)      for every H.     (*)

Now substitute (II) into the residual and cancel (*):

    R(k,H) = [L(k,H+1+k) + Ď(k,H+1)] - sum_i mu_i [L(k-i,H+k-i) + Ď(k-i,H)]
           = Ď(k,H+1) - sum_{i=0..k} mu_i Ď(k-i,H).

Finally `Ď(k,H+1) = D_{k-H}(k) = D_{j-1}(k)`, and `Ď(k-i,H) = D_{(k-i)+1-H}(k-i)
= D_{j-i}(k-i)`, which vanishes once `i >= j`. ∎

## What this does and does not settle

- It settles the *shape* of the residual: measuring it at 54 instances is no
  longer the evidence, it is a check on the arithmetic.
- It says nothing about how `D_j` is computed. The claim that `D_j` is
  available ab initio — from bounded-excess cluster weights, with no banked
  cell and no wired `P_k` — is `results/onset-defect-depths234.md`'s, resting
  on `experiments/severance_w3_depths.py`, and remains single-sourced. jasonp's
  condition (2026-08-14) is that the depth-`j` identity be re-derived
  independently of that script before cells pinned this way count as shored up.
- (*) holds for every `H`, including `H` where the law itself is invalid. That
  is not a contradiction: `L` is a polynomial expression that continues to
  satisfy the recursion wherever it is *evaluated*, while `T` stops agreeing
  with it. The defect terms are exactly that discrepancy.
