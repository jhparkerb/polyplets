# T3 — the L¹ diamond is the exact max-hole optimum: M(4r) = 2r²−2r+1

**Setup.** A *polyplet* is a finite king(8)-connected set P ⊂ ℤ². With the
4-connected-background convention, a *hole* of P is a bounded 4-connected component of
ℤ²∖P. Let **M(n)** = the maximum size of a single hole over all n-cell polyplets.

**Theorem.** For every r ≥ 1, `M(4r) = 2r² − 2r + 1`, achieved by the L¹ sphere
`{(x,y) : |x|+|y| = r}` (a king-cycle of 4r cells) enclosing the L¹ ball
`{|x|+|y| ≤ r−1}`.

Confirmed by exact enumeration through r=4: M(4)=1, M(8)=5, M(12)=13, M(16)=25
(`results/maxhole.txt`).

## The rotated coordinates

Write `u = x+y`, `v = x−y`. Two facts drive everything:

1. **Every king step changes (u,v) by total ℓ¹-length exactly 2.** For a step
   (Δx,Δy) ∈ {−1,0,1}²∖{0}, `|Δu|+|Δv| = |Δx+Δy| + |Δx−Δy| = 2·max(|Δx|,|Δy|) = 2`.
2. **The diamond is an axis-aligned box in (u,v).** Since `|x|+|y| = max(|u|,|v|)`, the
   ball `|x|+|y| ≤ m` is exactly `{|u| ≤ m, |v| ≤ m}` on the sublattice `u ≡ v (mod 2)`
   (every cell has `u+v = 2x` even).

## Lower bound (construction)

The sphere `S_r = {|x|+|y| = r}` has exactly 4r cells, is a simple king-cycle
(consecutive boundary cells differ by a (∓1,±1) king move), and separates its interior
ball `B_{r−1} = {|x|+|y| ≤ r−1}` from ∞ (any 4-path out must cross `|x|+|y| = r` ⊂ P).
`B_{r−1}` is 4-connected and bounded, hence a hole, with
`|B_{r−1}| = 2(r−1)² + 2(r−1) + 1 = 2r² − 2r + 1`. So `M(4r) ≥ 2r² − 2r + 1`.

## Upper bound

Let P be any 4r-cell polyplet with a hole H. Put
`A = max_H u, B = min_H u, C = max_H v, D = min_H v`, and `a = A−B, c = C−D` (the
(u,v)-extents of H).

**(i) Wall length ≥ a + c + 4.** By the discrete Jordan-curve theorem, P contains a
simple closed king-cycle C enclosing H (the inner boundary ring of P around H), with
`|C| ≤ |P| = 4r`. Enclosure forces C to reach one step past H along u: the cell h ∈ H
with `u(h) = A` has a 4-neighbour at `u = A+1`; that neighbour is not in H (H stops at
A) and cannot be background (h would then 4-connect to it and thus escape), so it is in
P, on the ring C — giving `max_u C ≥ A+1`. Symmetrically `min_u C ≤ B−1`,
`max_v C ≥ C+1`, `min_v C ≤ D−1`. Hence the cycle's extents satisfy
`W_u(C) ≥ a+2` and `W_v(C) ≥ c+2`.
Now use fact 1: summing over the closed cycle,
`2|C| = Σ(|Δu|+|Δv|) = Σ|Δu| + Σ|Δv| ≥ 2·W_u(C) + 2·W_v(C)` (a closed walk of u-range
W_u has total |Δu|-variation ≥ 2W_u). Therefore
`|C| ≥ W_u(C) + W_v(C) ≥ (a+2) + (c+2) = a + c + 4`, and
`4r = |P| ≥ |C| ≥ a + c + 4`, i.e. **a + c ≤ 4r − 4.**

**(ii) Hole ≤ box ≤ diamond.** H lies in its (u,v) bounding box `[B,A]×[D,C]`, an
(a+1)×(c+1) grid; its cells lie on the even sublattice `u ≡ v (mod 2)`, so
`|H| ≤ ⌈(a+1)(c+1)/2⌉`. With `a + c ≤ 4r − 4`, i.e. `(a+1)+(c+1) ≤ 4r − 2`, AM–GM gives
`(a+1)(c+1) ≤ (2r−1)²`, so
`|H| ≤ ⌈(2r−1)²/2⌉ = ⌈(4r²−4r+1)/2⌉ = 2r² − 2r + 1`. ∎

**Equality** forces `a+1 = c+1 = 2r−1` (square box) and H to fill the box on the even
sublattice — exactly the diamond `B_{r−1}`, with wall the sphere `S_r`. So the diamond
is the *unique* optimum (up to translation), and M(4r) = 2r²−2r+1.

## All n at once (T5): M(n) = ⌈⌊(n−2)²/4⌋/2⌉

Nothing above used n ≡ 0 (mod 4) until the final AM–GM. For **any** n the same two steps
give the *exact* maximum hole:

- **Upper bound.** `a + c ≤ n − 4` (step i, unchanged), so with `p = a+1, q = c+1`,
  `p + q ≤ n − 2` and `|H| ≤ ⌈pq/2⌉`. The max of `pq` over positive integers with
  `p + q ≤ S` is `⌊S²/4⌋` (balanced split), so `|H| ≤ ⌈⌊(n−2)²/4⌋/2⌉`.
- **Lower bound.** The balanced rectangular L¹-diamond — the (u,v)-box of sides
  `⌊(n−2)/2⌋ × ⌈(n−2)/2⌉` on the even sublattice — is enclosed by its rook-outer
  boundary, a single king-loop of **exactly n** cells (tight, by the same saturation),
  enclosing `⌈⌊(n−2)²/4⌋/2⌉` cells. (The only n where the loop uses fewer than n cells is
  **n=5**, where M(5)=M(4)=1 is flat and the 5th cell is necessarily wasted.) Verified by
  explicit construction + flood-fill for all n=4..40 in `experiments/maxhole_formula.py`.

Hence, for all `n ≥ 4`, `M(n) = ⌈⌊(n−2)²/4⌋/2⌉`, i.e. by residue
`M(4r)=2r²−2r+1, M(4r+1)=2r²−r, M(4r+2)=2r², M(4r+3)=2r²+r` — matching every
exactly-enumerated value (`results/maxhole.txt`, n=4..16). This **closes T5** (the full
maxhole sequence in closed form) and predicts M(20)=41, M(24)=61, …; a candidate OEIS
formula and a paper result (the discrete exact isoperimetric law).

## Remarks

- The whole proof is elementary except the one invocation of the discrete Jordan-curve
  theorem (a polyplet enclosing a hole contains a simple king-cycle around it) — a
  standard digital-topology fact.
- **The engine of the bound is fact 1** (`|Δu|+|Δv| = 2` per king step), which makes
  king-perimeter linear in the (u,v) extents and pins the constant exactly. The same
  identity gives, for ANY n, `a + c ≤ n − 4`, hence the general bound
  `M(n) ≤ ⌈((n−2)/2)²/2⌉`-type estimate — tight at n = 4r, and the off-diamond values
  (M(5)=1,…,M(15)=21) are where the box-rounding and the `n ≢ 0 (mod 4)` wall slack
  bite (the T5 "exact M(n) for all n" question).
- This is the discrete, exact counterpart to the asymptotic isoperimetric statement
  (Busemann's isoperimetrix / Strang) cited in the paper: there the L¹ ball is optimal
  in the scaling limit; here it is optimal *exactly* at every perimeter 4r.
