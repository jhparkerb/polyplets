# Integer structure of T(n,H): Smith normal form is all 3-powers

Date: 2026-07-10. `T(n,H)` height triangle as an integer matrix (rows n, cols H,
n,H=1..N). Smith normal form computed via sympy on the banked triangle.

## Result

**Every invariant factor is a pure power of 3**, for all N=4..14 checked. So over
ℤ, `T ~ diag(3^{e_1},…,3^{e_N})` under unimodular row/col ops, and the cokernel
`ℤ^N / T·ℤ^N` is a finite abelian **3-group**. The triangle's entire integer
content lives at the single prime 3.

The number of **nontrivial** invariant factors (exponent > 0) is exactly
**`⌈(N−1)/3⌉`**:

| N | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| #nontrivial | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 |

3-exponents (nontrivial), by N: 4:[6]; 5:[1,9]; 6:[5,10]; 7:[6,15]; 8:[2,8,18];
9:[4,13,19]; 10:[7,14,24]; 11:[1,12,16,26]; 12:[3,14,22,27]; 13:[6,16,23,33];
14:[1,9,20,25,36]. Sum of exponents = `N(N−1)/2` = det 3-exponent
(`= Σ(n−1)`, since diag `T(n,n)=3^{n−1}`). ✓

## Reading

- **Mostly unimodular**: ~`2N/3` of the invariant factors are 1; the 3-adic
  content is a rank-`⌈(N−1)/3⌉` block. The matrix is "simple" integrally except
  for a slowly-growing 3-adic core.
- **The `/3` is the atom structure.** Columns factor as three-consecutive-atom
  products `p_H = q_H q_{H−1} q_{H−2}` (results/triangle-structure.md); the
  nontrivial-factor count grows one per three columns — same `/3`. The SNF, the
  Atom Ledger, and the 3-adic thread (`3^{n−1}` king chain, diagonal `3^{3k+1}`,
  production band `3^{3k+2}`) are one phenomenon: everything is at prime 3.

## Open

- Prove SNF ⊆ 3-powers in general (the matrix's minors are all 3-smooth?).
- Is there a formula for the individual exponents `e_i(N)`? (Not obvious from the
  lists above; the largest and the count are clean, the middle ones less so.)
