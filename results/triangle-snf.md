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
  - **(B) Independence:** the activated columns (`⌊3H/2⌋≤N`) are linearly
    independent mod 3 (equivalently, the null space has no vector off the zero
    columns).

### Proof skeleton for (A) — reduced to two clean facts about `P_k`
Diagonal form `T(n,n-k)=P_k(n)·3^{n-1-3k}` (valid `n≥2k+1`, which covers the
boundary), so with `k=n-H`:
$$v_3\big(T(n,H)\big) \;=\; (3H-2n-1) \;+\; v_3\big(P_{n-H}(n)\big).$$
- **`n<⌊3H/2⌋`:** the pure exponent `3H-2n-1 ≥ 1` (elementary), and by **(A2)**
  `v₃(P_k(n)) ≥ 0`, so `v₃(T) ≥ 1`. ✓
- **`n=⌊3H/2⌋`:** by **(A1b)**, `H` odd ⟹ `n=3k+1`, exponent `0`, `v₃(P_k)=0`;
  `H` even ⟹ `n=3k`, exponent `-1`, `v₃(P_k)=1`. Either way `v₃(T)=0`. ✓

So (A) — hence the `⌈(N-1)/3⌉` count, modulo (B) — follows from two number-theoretic
facts about the cumulant polynomials `P_k(n)=[y^k]\exp\sum_j(a_j+b_j n)y^j`
(leading coeff `25^k/k!`), **both verified `k≤17`/`k≤11`:**
- **(A2) 3-integrality:** `v₃(P_k(n)) ≥ 0` for every integer `n≥2k+1` — i.e. `P_k`
  maps integers to 3-adic integers despite the `k!` denominator. Equivalent form:
  `3^{\,n-1-3k} \mid T(n,n-k)` for `n>3k+1` (the diagonal-`k` counts acquire growing
  3-divisibility).
- **(A1b) Boundary units:** the activation entries are coprime to 3:
  `3∤T(3k+1,2k+1)` and `3∤T(3k,2k)` (equivalently `v₃(P_k(3k+1))=0`, `v₃(P_k(3k))=1`).

## Still open

- **Prove (A2) and (A1b)** (concrete 3-adic facts about the `P_k`; the cumulant
  form + Legendre `v₃(k!)=(k-s₃(k))/2` are the tools) and **(B)** the mod-3
  independence of activated columns. That closes the `⌈(N-1)/3⌉` count from first
  principles.
- A formula for the individual exponents `e_i(N)` (the full 3-adic invariant
  factors, not just count/sum) — the mod-3 rank gives the count but not the higher
  3-adic structure; still no closed form.
