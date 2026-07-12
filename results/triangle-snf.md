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

## Resolved / reduced (2026-07-11)

- **SNF ⊆ 3-powers: PROVED (trivially).** `T(n,H)=0` for `H>n`, so `T_N` is
  lower-triangular and `det T_N = ∏ T(n,n) = ∏ 3^{n-1} = 3^{N(N-1)/2}` — a pure
  3-power. Invariant factors form a chain `d_1|…|d_N` with `∏d_i=|det|`, so any
  prime `q≠3` dividing some `d_i` divides `d_N` hence `det` — impossible. Every
  invariant factor is a 3-power; the cokernel is a finite 3-group. (For all `N`.)

- **Nontrivial-factor count `⌈(N-1)/3⌉`: REDUCED to a clean activation law.**
  Since the factors are 3-powers, the count `= N − rank(T_N mod 3) =
  nullity(T_N mod 3)`. Computed: the mod-3 null space is spanned by exactly the
  **zero columns** — column `H` of `T_N` that is `≡0 mod 3` in all rows `n≤N`.
  A column first becomes nonzero mod 3 at row
  $$f(H) = \lfloor 3H/2 \rfloor \qquad(\text{verified }H\le24,\ \text{i.e.}\
  \min\{n:3\nmid T(n,H)\}=\lfloor3H/2\rfloor).$$
  So column `H` is a zero column iff `⌊3H/2⌋>N`, and
  `#{H≤N : ⌊3H/2⌋>N} = ⌈(N-1)/3⌉` (elementary; proved algebraically). Hence the
  count reduces to **two claims, both verified to N=36:**
  - **(A) Activation:** `v₃(T(n,H)) ≥ 1` for `n<⌊3H/2⌋`, and `=0` at `n=⌊3H/2⌋`.
    Via the diagonal form `T(n,n-k)=P_k(n)·3^{n-1-3k}` (valid `n≥2k+1`, which holds
    at the boundary since `H=⌊2n/3⌋≥(n+1)/2`), this is
    `v₃(T(n,H)) = (3H-2n-1) + v₃(P_{n-H}(n))` — a statement about the 3-adic
    valuation of the cumulant-law polynomials `P_k` (leading coeff `25^k/k!`,
    `v₃ = -v₃(k!)`).
  - **(B) Independence:** the activated columns (`⌊3H/2⌋≤N`) are linearly
    independent mod 3 (equivalently, the null space has no vector off the zero
    columns).

## Still open

- Prove (A) and (B) — that finishes the `⌈(N-1)/3⌉` count from first principles.
- A formula for the individual exponents `e_i(N)` (the sorted 3-adic invariant
  factors, not just their count/sum) — the mod-3 rank gives the count but not the
  higher 3-adic structure; still no closed form.
