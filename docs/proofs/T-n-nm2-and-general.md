# Proof: T(n, n−2), and the general height-diagonal structure

Companion to `T-n-nm1.md`. T(n,H) = fixed king-animals (polyplets) of n cells,
bounding-box height exactly H. Here: the second sub-diagonal H = n−2, and the
general T(n, n−k).

## 1. T(n, n−2) — the exact form

$$T(n,n{-}2)=\tfrac12\,(625\,n^{2}-2459\,n+1134)\cdot 3^{\,n-7},\qquad n\ge 5$$

(n=4 boundary: T(4,2)=27.) Verified against **exhaustive enumeration** of all
fixed king-animals for n=4…8 and against all 16 triangle values n=5…20.

### Decomposition (excess = 2 cells over the n−2 rows)

Height n−2 with n cells forces either **one row of 3** (Case A) or **two rows of
2** (Case B). Brute force confirms `T = A + B` exactly. Connectivity is the same
local condition as `T-n-nm1.md` (every consecutive row pair shares a king-edge),
and the count is again a product of per-transition weights (single→single = 3)
with **gadgets at the defect rows**, summed over placements.

**Case A — one triple (a single defect ⇒ linear):** an interior triple's two
internal gaps are each 1 or 2 (gap ≥3 ⇒ an unbridgeable cell ⇒ disconnected).
Summing over gap-type and the two neighbour offsets:

| gaps | (1,1) tromino | (1,2)/(2,1) split | (2,2) | **interior** | boundary |
|---|---|---|---|---|---|
| configs | 5·5 = 25 | 6²−5² = 11 each | 2 | **49** | 5+1+1+0 = **7** |

$$A=\big[49(n{-}4)+2\cdot 7\cdot 3\big]\,3^{\,n-5}=(49n-154)\,3^{\,n-5}.$$

**Case B — two doubles.** Each double is the `T-n-nm1` double-gadget (interior
25, boundary 5; gap 1 or 2 with a bridge). Two sub-cases:

- **separated** (non-adjacent rows ⇒ two *independent* defects ⇒ quadratic):
  `B_sep = ½(625n²−5375n+11700)·3^(n−7)`, leading 25²/2!.
- **adjacent** (consecutive rows ⇒ one *compound* defect ⇒ linear): joint gadget
  weights 339 (interior pair) / 66 (boundary pair),
  `B_adj = (1017n−3897)·3^(n−7)`.

All four pieces match the brute force exactly (n=4…8). Summing:

$$A + B_{\text{sep}} + B_{\text{adj}} = \tfrac12(625n^{2}-2459n+1134)\,3^{\,n-7}. \qquad\blacksquare$$

## 2. The general diagonal T(n, n−k)

**Form (proven structure):** for each fixed k,
`T(n,n−k) = P_k(n)·3^(n−1−3k)` with **P_k a degree-k polynomial**, valid in the
bulk **n ≥ 2k+1** (below that, boundary terms). The k=0,1,2 cases are proven from
first principles (A1, C1, §1); the leading coefficient is **25ᵏ/k!** — verified
exactly for k=0…6 from the triangle.

**Why a single structure — the defect gas.** The excess-k cells form *defect
clusters* (maximal runs of multi-cell rows) placed on the n-row chain; clusters
are independent except for adjacency, so the bivariate generating function over
(rows, excess) is **exponential in the number of rows**. Concretely, writing
`S(y) = Σ_k P_k(n) yᵏ`, the data gives **log S(y) exactly linear in n** at every
order k=1…6:

| k | coeff of yᵏ in log S = a_k + n·b_k |
|---|---|
| 1 | 25 n − 45 |
| 2 | −(209/2) n − 891/2 |
| 3 | (4474/3) n − 10350 |
| 4 | −(22701/4) n − 846963/4 |
| 5 | 16144 n − 3781134 |
| 6 | (15126941/3) n − 119091015 |

i.e. `S(y) = A(y)·e^{n·B(y)}`, `B(y)=Σ b_k yᵏ`, `A(y)=e^{Σ a_k yᵏ}`. The linearity
is the *defect-gas signature* (each row independently may seed a cluster → e^{nB};
A is the boundary correction). This is the general T(n,n−k) statement; B(y) and
A(y) are fixed by the cluster combinatorics (the k=1,2 gadgets are their low-order
terms). B(y), A(y) are not obviously elementary in the first 6 terms — an open
question whether they are algebraic.

## 3. Status / use

- **Proven & engine-ready (gated against the triangle):** k=0 (A1), k=1 (C1),
  **k=2 (§1)** → frees the top **three** heights of every run.
- **Exact from data, not yet first-principles-proven:** k=3…6 (P_k pinned, leading
  25ᵏ/k! confirmed). These would free the top **seven** heights — a large frontier
  win — once the defect-gas proof is written for general k (the method of §1
  extends; the bookkeeping grows). Until then they serve as cross-checks, not the
  record path.

**Validity reminder for wiring:** `T(n,n−k)` holds for `n ≥ 2k+1`; the engine must
fall back to a real sweep when `maxn < 2k+1` (irrelevant at the frontier, where
maxn ≥ 20 ≫ 2k+1 for the small k we free).
