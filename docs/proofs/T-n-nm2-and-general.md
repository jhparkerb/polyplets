# Proof: T(n, n−2), and the general height-diagonal structure

Companion to `T-n-nm1.md`. T(n,H) = fixed king-animals (polyplets) of n cells,
bounding-box height exactly H. Here: the second sub-diagonal H = n−2, and the
general T(n, n−k).

## 1. T(n, n−2) — the exact form

$$T(n,n{-}2)=\tfrac12\,(625\,n^{2}-2459\,n+1134)\cdot 3^{\,n-7},\qquad n\ge 5$$

(n=4 boundary: T(4,2)=27.) Verified against exhaustive enumeration of all
fixed king-animals for n=4…8 and against all 16 triangle values n=5…20.

### Decomposition (excess = 2 cells over the n−2 rows)

Height n−2 with n cells forces either one row of 3 (Case A) or two rows of
2 (Case B). Brute force confirms `T = A + B` exactly. Connectivity is the same
local condition as `T-n-nm1.md` (every consecutive row pair shares a king-edge),
and the count is again a product of per-transition weights (single→single = 3)
with gadgets at the defect rows, summed over placements.

**Case A — one triple (a single defect ⇒ linear):** an interior triple's two
internal gaps are each 1 or 2 (gap ≥3 ⇒ an unbridgeable cell ⇒ disconnected).
Summing over gap-type and the two neighbor offsets:

| gaps | (1,1) tromino | (1,2)/(2,1) split | (2,2) | interior | boundary |
|---|---|---|---|---|---|
| configs | 5·5 = 25 | 6²−5² = 11 each | 2 | 49 | 5+1+1+0 = 7 |

$$A=\big[49(n{-}4)+2\cdot 7\cdot 3\big]\,3^{\,n-5}=(49n-154)\,3^{\,n-5}.$$

**Case B — two doubles.** Each double is the `T-n-nm1` double-gadget (interior
25, boundary 5; gap 1 or 2 with a bridge). Two sub-cases:

- separated (non-adjacent rows ⇒ two *independent* defects ⇒ quadratic):
  `B_sep = ½(625n²−5375n+11700)·3^(n−7)`, leading 25²/2!.
- adjacent (consecutive rows ⇒ one *compound* defect ⇒ linear): joint gadget
  weights 339 (interior pair) / 66 (boundary pair),
  `B_adj = (1017n−3897)·3^(n−7)`.

All four pieces match the brute force exactly (n=4…8). Summing:

$$A + B_{\text{sep}} + B_{\text{adj}} = \tfrac12(625n^{2}-2459n+1134)\,3^{\,n-7}. \qquad\blacksquare$$

## 2. The general diagonal T(n, n−k)

**Form (proven structure):** for each fixed k,
`T(n,n−k) = P_k(n)·3^(n−1−3k)` with P_k a degree-k polynomial, valid in the
bulk n ≥ 2k+1 (below that, boundary terms). The k=0,1,2 cases are proven from
first principles (the single-cell chain, `T-n-nm1.md`, §1); the leading
coefficient is 25ᵏ/k! — verified exactly for k=0…6 from the triangle, and
proved for all k in `product-form.md`.

**Why a single structure — the defect gas.** The excess-k cells form *defect
clusters* (maximal runs of multi-cell rows) placed on the n-row chain; clusters
are independent except for adjacency, so the bivariate generating function over
(rows, excess) is exponential in the number of rows. Concretely, writing
`S(y) = Σ_k P_k(n) yᵏ`, the data gives log S(y) linear in n at every
order k=1…6:

| k | coeff of yᵏ in log S = a_k + n·b_k |
|---|---|
| 1 | 25 n − 45 |
| 2 | −(209/2) n − 891/2 |
| 3 | (4474/3) n − 10350 |
| 4 | −(22701/4) n − 846963/4 |
| 5 | 16144 n − 3781134 |
| 6 | (15126941/3) n − 119091015 |

i.e. `S(y) = A(y)·e^{n·B(y)}`, `B(y)=Σ b_k yᵏ`, `A(y)=e^{Σ a_k yᵏ}`. The
linearity is the *defect-gas signature* (each row independently may seed a
cluster → e^{nB}; A is the boundary correction). This is the general T(n,n−k)
statement; B(y) and A(y) are fixed by the cluster combinatorics (the k=1,2
gadgets are their low-order terms). B(y), A(y) are not obviously elementary in
the first 6 terms — an open question whether they are algebraic.

## 3. Status / use

- k=0 (the single-cell chain), k=1 (`T-n-nm1.md`) and k=2 (§1) are proved
  from first principles and checked against the triangle by the engine gates.
- The law for general k is `diagonal-law.md`; each P_k is then determined
  from two in-onset entries (`product-form.md`), and the engine's formula table
  holds k ≤ 19.

`T(n,n−k)` holds for `n ≥ 2k+1`; the engine falls back to a real sweep when
`maxn < 2k+1`.

## 4. The defect gas is a partition structure (the proof skeleton for all k)

Brute-forcing the cluster decomposition of height-(n−k) animals (a *cluster*
= a maximal run of consecutive multi-cell rows; its *excess* = Σ(cells−1)) makes
the general structure concrete. For k=3 the cluster-excess multisets that occur
are exactly

$$\{3\},\quad \{2,1\},\quad \{1,1,1\}\ =\ \text{the partitions of }3,$$

and nothing else (verified n=5…9). In general:

> An animal of excess k has defect clusters whose excesses form a partition
> λ ⊢ k. A partition with p parts = p non-adjacent clusters placed on the
> n-chain ⇒ a contribution of degree p in n. Hence `deg P_k = k` (from
> λ=1ᵏ), leading coefficient `c_1^k/k! = 25^k/k!` (k separated doubles), and
> `P_k = Σ_{λ⊢k} (∏ cluster weights)·(placement polynomial)`.

This is the exponential formula for a cluster gas — it is *why*
`S(y)=A(y)e^{nB(y)}`, with B(y) = the single-cluster (connected) generating
function. The proven single-cluster weights so far (excess j, summed over
cluster types):

**Single-row defects are squares.** A single row of e+1 cells (excess e, span 1)
has boundary weight 2e+3 and interior weight (2e+3)² — verified e=1,2,3 (double
5/25, triple 7/49, quad 9/81). This *closes the span-1 sub-family of the cluster
GF for all excess*: `Σ_e (2e+3)² yᵉ` is rational. (Interior = boundary² because
the two neighbor sides are independent, each contributing the 2e+3
single-neighbor factor.)

Proven single-cluster interior weights by (excess e, span s) (brute force):

| e \ s | 1 (single row) | 2 (two adj rows) | 3 | 4 |
|---|---|---|---|---|
| 1 | 25 | — | — | — |
| 2 | 49 | 339 | — | — |
| 3 | 81 | 1860 | 4778 | — |
| 4 | 121 | 7311 | 45226 | — |

- Span 1 (single row) = `(2e+3)²` — closed, verified e=1…4 (25,49,81,121). The
  boundary weight is `2e+3`. The partition structure reappears at k=4 (multisets
  {4},{3,1},{2,2},{2,1,1} — partitions of 4, those that fit the rows).
- Multi-span columns show no recognizable closed form so far. A focused local
  gadget enumerator (single | multi | multi | single, wide column window — a
  too-narrow window silently *under*-counts, so it must be validated against the
  exhaustive brute force, which it now is) extends span-2 to Wi(e,2) = 339,
  1860, 7311, 25080 (e=2…5). Normalized by 3ᵉ these are 37.7, 68.9, 90.3, 103.2
  — increasing and decelerating (so ~C·3ᵉ asymptotically, i.e. a *sum* of
  geometric terms / rational GF), but no low-order linear recurrence fits 4
  points, and span-3 (4778, 45226) has even fewer. A span-s cluster of excess e
  is a coupled stack of s adjacent multi-cell rows — the genuine combinatorial
  core of B(y), still open.

**State of the hunt:** the span-1 column is closed ((2e+3)²); the multi-span
columns need either many more points (push the validated enumerator to e=8–10
per span and fit a rational GF) or a structural insight into the inter-row
coupling. Until then, each fixed k is provable by cataloguing its (finitely
many) cluster weights and assembling over partitions — k=0,1,2 done, k=3,4
catalogued.

**Consequence.** Proving any fixed k is *mechanical*: catalogue that k's cluster
weights (a finite enumeration, the §1 method per cluster type) and assemble over
partitions. k=0,1,2 done; k=3 is decomposed (above) and one catalog step from
proven. The *open* prize remains closing B(y) in elementary/algebraic form —
the single-cluster GF — which would deliver every k at once; the cluster weights
25, 388, … are its (positive-integer) building blocks and a better target for
pattern-recognition than B(y)'s signed rationals.

## 5. Closing B(y): what was tried

We tried to close B(y) in two normalisations. The first is the constant-excess
diagonal `S(y)=Σ_k P_k(n)yᵏ = A(y)e^{nB(y)}`. `P_k` needs `n≥2k+1`, so the a(21)
triangle pins `b_1…b_6` outright and `b_7` only with the proven `25ᵏ/k!` leading
coefficient assumed, seven terms in all: `B(y) = 25y − (209/2)y² + (4474/3)y³ −
(22701/4)y⁴ + 16144y⁵ + (15126941/3)y⁶ − (687296991/7)y⁷ + …`. Both `e^{B(y)}`
and `A(y)` land in `ℤ[[y]]`, which checks every rational `a_k, b_k`: `e^B =
1,25,208,1483,20688,130208,5519404,36500568,…` and `A =
1,−45,567,−5490,73035,641466,−44582436,1539013905,…`. The second is the
fixed-height per-row ratio `λ_raw(y)=Z_N/Z_{N−1}`, `Z_N(y)=Σ_e T(N+e,N)yᵉ`, the
wide slice (T(20,8) exists where the diagonal T(n,n−8) would need n=25); `λ_raw`
converges in N and gives nine converged terms from the same a(21) data: `λ_raw =
3, 25/3, 833/27, 32708/243, 1426141/2187, 66608903/19683, 1088429260/59049,
55307294057/531441, 2888944079197/4782969, 462665755865681/129140163`
(denominators are pure powers of 3), with `b_raw_k=[yᵏ]log λ_raw = 25/9, 347/54,
51274/2187, 2737861/26244, 3381871/6561, 1446596374/531441,
168016103639/11160261, 3295403161157/38263752, 1762540314602707/3486784401`.
OEIS and Superseeker lookups were empty for every integer sequence tried: the
interior cluster weights (339, 1860, 7311, 25080), the `e^B` coefficients, the
`A(y)` coefficients and the `λ_raw` numerators. Equation guessing, algebraic
`P(f,y)=0` and linear ODE `Σ pⱼ(y)f⁽ʲ⁾=0` in every form with fewer unknowns than
data points, returned the trivial solution only, on 8 terms of `e^B` and `A` and
on 10 terms of `λ_raw`; the simplest forms (algebraic of degree (2,2),
second-order ODE of degree 2) are excluded outright. The a(40) per-height data
(`results/ns_a40/`) extends the `λ_raw` slice to 18 converged terms, the first 9
reproducing the values above with denominators still pure powers of 3, and the
same search at that ceiling (algebraic up to deg_f 8 × deg_y 1, linear ODEs up
to order 4, on `λ_raw` and on `log λ_raw`) again returns only the trivial
solution. The extractor is `experiments/braw_from_data.py [NMAX]` (log
`build/braw_a40.log`); it reads the per-height files in `results/ns_a40/`, or a
matching `results/ns_a{NMAX}/` tree.

The data ceiling: `b_raw_k` converges only for `N≳k+1` while `Z_N` is known
only to order `21−N`, so within a(21) the two collide at k=9 (k=10 would need
N≥12 with order ≥10). So B(y) shows no algebraic or D-finite closed form of any
complexity reachable from the available terms, in either normalisation, and
the 18-term search says this is not a shortage of data; it is evidence that
B(y) is non-D-finite. Polyomino growth series are routinely non-D-finite, and
the full polyomino generating function is conjectured to be. Going further
would mean driving the engine into the tall-strip, high-excess region
(H≈14–18) for a high-degree fit. The diagonal formulas already free the
expensive top heights, and closing B(y) would only formula-free the cheap low
heights, so it is a pure-math open question, not on the a(n) path.
