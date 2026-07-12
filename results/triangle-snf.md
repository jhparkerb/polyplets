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

### (A2) is PROVED — and it proves the lower half of (A)

- **(A2) `P_k` is integer-valued (hence 3-integral). PROVED** (given the diagonal
  closed form, i.e. `P_k` is a degree-`k` polynomial for `n≥2k+1`). The window
  `[2k+1, 3k+1]` is **exactly `k+1` consecutive integers**, and on it
  `P_k(n)=T(n,n-k)·3^{\,3k+1-n}` is (nonneg count)·(nonneg power of 3) `= ` an
  integer. A degree-`k` polynomial integer at `k+1` consecutive integers is
  integer-valued everywhere (Pólya) — despite the `25^k/k!` leading coefficient,
  exactly like a binomial. Verified `P_k(n)∈ℤ` for all `n∈[-5,40]`, `k≤15`.
- **Lower half of (A) now rigorous:** for `n<⌊3H/2⌋`, the pure exponent
  `3H-2n-1 ≥ 1` (elementary) and `v₃(P_k(n)) ≥ 0` (A2) give `v₃(T(n,H)) ≥ 1` — the
  column really is `≡0 mod 3` below the boundary.

### What remains (conjectural)
- **(A1b) Activation:** the two "just-switched-on" entries are coprime to 3 —
  `3∤T(3k+1,2k+1)` and `3∤T(3k,2k)` (equivalently `v₃(P_k(3k+1))=0`,
  `v₃(P_k(3k))=1`). Verified `k≤11`. This is the upper half of (A): it makes the
  column nonzero exactly at `n=⌊3H/2⌋`.
- **(B) Independence:** the activated columns (`⌊3H/2⌋≤N`) are linearly independent
  mod 3. Verified `N≤36`.

So the `⌈(N-1)/3⌉` count is now: **lower half of (A) proved**, and it reduces to
**(A1b)** (two explicit entries coprime to 3) plus **(B)** (mod-3 independence).

## Still open

- Prove (A1b) and (B).
- A formula for the individual exponents `e_i(N)` (the full 3-adic invariant
  factors, not just count/sum) — the mod-3 rank gives the count but not the higher
  3-adic structure; still no closed form.
