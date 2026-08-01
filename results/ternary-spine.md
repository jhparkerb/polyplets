# The Ternary Spine: a closed-form mod-3 law for the height triangle

2026-07-12 (with jasonp; the SNF thread pushed to completion). Verifier:
`experiments/ternary_spine.py` — **15/15 checks green**, including a 342-cell
mass check against the banked triangle.

## Summary

The mod-3 structure of the height triangle's diagonal family is governed by a
single algebraic series: the unique root $W \in \mathbb F_3[[t]]$, $W(0)=1$, of
the cubic
$$\boxed{\,W^3 = W^2 + t\,}$$
("the spine cubic"). From it: a base-3 digit-product formula for the triangle
mod 3, closed forms for every column's first nonzero entry, and a **complete
proof of the Smith-normal-form count** $\lceil (N{-}1)/3\rceil$ — modulo an
explicit, finitely-verified conditionality ladder stated below. The cubic also
lifts 3-adically: $H^3 - H^2 \equiv 25t \pmod{27}$ with the level-3 correction
again expressed in $W$ — the tower telescopes through the same series.

## Setup and unconditional steps

The diagonal law (the paper's empirically-exact machinery, holdout-validated
$k\le17$): for each $k$ there is a degree-$k$ polynomial $P_k$ with
$T(n,n{-}k) = P_k(n)\,3^{\,n-1-3k}$ for $n \ge 2k{+}1$, and cumulants linear in
$n$, equivalently
$$\textstyle\sum_k P_k(n)\,y^k \;=\; G(y)\,H(y)^n .$$

- **Proposition 1 (Pólya).** Each $P_k$ is integer-valued: the window
  $[2k{+}1,\,3k{+}1]$ contains $k{+}1$ consecutive integers where
  $P_k(n) = T(n,n{-}k)\cdot 3^{3k+1-n}$ is a count times a nonnegative power of
  3, and a degree-$k$ polynomial integral at $k{+}1$ consecutive integers is
  integer-valued everywhere.
- **Proposition 2.** $G = \sum_k P_k(0)y^k$ and $H = \big(\sum_k P_k(1)y^k\big)/G$
  are **integer** power series (constant term 1; geometric-series inversion).
  $H$ is the per-row transfer series of the defect gas — $h_1 = 25$ is the
  paper's "25 single-defect species"; $H = 1, 25, 208, 1483, 20688, 130208,\dots$
  is itself a candidate new integer sequence.

## The conditionality ladder (all three rungs now symbolic — see upgrades below)

- $(\star a)$ $G \equiv 1 \pmod 9$ — verified: $v_3(G_j) \ge 2$, $j \le 17$.
  **UPGRADE 2026-07-12: DERIVED** — boundary-cluster residue formula for $G$
  + boundary valuation lemma + an identity of the mod-9 cubic
  (`results/defect-gas.md`).
- $(\star b)$ $H \equiv W \pmod 3$ — verified on all 18 known coefficients, and
  the resulting digit formula reproduces **all 342 in-regime banked triangle
  cells mod 3** using nothing but the cubic. **UPGRADE 2026-07-12: DERIVED**
  from the defect gas (`results/defect-gas.md`): the master equation
  $H = 1 + \sum_c \hat W_c u^{k_c} H^{-(k_c+\ell_c)}$ plus the valuation lemma
  ($k \ge \ell$ per cluster $\Rightarrow$ only the bare pair-row survives mod 3)
  gives $H^3 = H^2 + u$ over $\mathbb F_3$ as an all-orders statement — the
  cubic is the gas of bare pair-rows. The mod-9 lift $H^3 \equiv H^2 + 7u$ and
  a finite explicit mod-27 equation come from the same lemma.
- $(\star c)$ $S := (H^3 - H(t^3))/3$ satisfies $S \equiv t^2 + tW \pmod 3$ —
  **PROVED 2026-07-13** (`results/defect-gas.md`): from the mod-9 cubic alone,
  $H(t^3) \equiv H^2 + 25t - 3t^2 - 3tW \pmod 9$ (uniqueness of the cubic's
  fixed point + a three-line 𝔽₃ cancellation). The entire ladder
  $(\star a,b,c)$ is now symbolic — no empirical input remains.

## Theorems (under the law + ladder)

**T1 (digit product).** Writing $n = \sum_i n_i 3^i$ in base 3,
$$P_k(n) \bmod 3 \;=\; [y^k]\ \prod_i W\!\big(y^{3^i}\big)^{n_i}.$$
*Proof.* $F_n \equiv H^n \equiv W^n \pmod 3$ by $(\star a),(\star b)$, and
Frobenius over $\mathbb F_3$: $W^{3^i}(y) = W(y^{3^i})$. ∎

**T2 (odd spine).** $T(3k{+}1,\,2k{+}1) \equiv 1 \pmod 3$ for all $k$.
*Proof.* This entry has exponent $n{-}1{-}3k = 0$, so it equals
$P_k(3k{+}1) \equiv [t^k]W^{3k+1} \pmod 3$. Parametrize the cubic rationally:
$$t = \frac{x}{(1-x)^3},\qquad W = \frac1{1-x}$$
(check: $W^3 - W^2 = (1-x)^{-3}\big(1-(1-x)\big) = t$). Lagrange–Bürmann with
$x = t\varphi(x)$, $\varphi = (1-x)^3$:
$$[t^k]F(x(t)) = [x^k]\,F(x)\,\varphi(x)^k\Big(1 - \tfrac{x\varphi'}{\varphi}\Big),$$
valid over any ring — and in characteristic 3, $\varphi' = -3(1-x)^2 = 0$. With
$F = (1-x)^{-(3k+1)}$:
$$[t^k]W^{3k+1} = [x^k]\,(1-x)^{-(3k+1)}(1-x)^{3k} = [x^k](1-x)^{-1} = 1.\ ∎$$

**T3 (even spine).** $P_k(3k) \equiv 3 \pmod 9$ for all $k\ge1$; hence
$T(3k,2k) = P_k(3k)/3 \equiv 1 \pmod 3$.
*Proof.* $H^3 = H(t^3) + 3S$ (definition of $S$; integrality is the classical
$H^3 \equiv H(t^3) \bmod 3$). For $3\nmid k$:
$H^{3k} \equiv H(t^3)^k + 3kS\,H(t^3)^{k-1} \pmod 9$; the first term has only
exponents divisible by 3, so $[t^k]$ kills it, and with $(\star a)$, $(\star c)$,
and $W(t^3) = W^2 + t = W^3$:
$$P_k(3k) \equiv 3k\,[t^k]\,(t^2{+}tW)\,W^{3k-3} \pmod 9 .$$
By the same Lagrange–Bürmann (correction term again 1):
$$[t^k](t^2{+}tW)W^{3k-3} = [x^k]\Big(x^2(1-x)^{-3} + x(1-x)^{-1}\Big)
   = \binom{k}{2} + 1,$$
and for $3\nmid k$: $k\big(\binom k2{+}1\big) \equiv k\cdot k \equiv 1 \pmod 3$.
So $P_k(3k) \equiv 3 \pmod 9$. For $3 \mid k$, write $k = 3m$: the middle
binomial term now carries $3\cdot3m \equiv 0 \pmod 9$, giving the
**self-similarity**
$$P_{3m}(9m) \;\equiv\; [t^{3m}]\,H(t^3)^{3m} \;=\; [\tau^m]H(\tau)^{3m}
   \;\equiv\; P_m(3m) \pmod 9,$$
and induction on $v_3(k)$ finishes. ∎  (Verified: $P_k(3k) \equiv 3 \bmod 9$
for all $k \le 17$; self-similarity checked $m \le 5$.)

**T4 (activation law).** Column $H$ of the triangle is $\equiv 0 \pmod 3$ for
all $n < \lfloor 3H/2\rfloor$ and $\not\equiv 0$ at $n = \lfloor 3H/2\rfloor$.
*Proof.* Below: exponent $3H-2n-1 \ge 1$ and $v_3(P_k(n)) \ge 0$ (Prop. 1) —
this half needs only the law, no ladder. At the boundary: $H$ odd is T2, $H$
even is T3. ∎

**T5 (Smith normal form count).** For every $N$, the SNF of
$T_N = [T(i,j)]_{i,j\le N}$ is $\mathrm{diag}(3^{e_1},\dots,3^{e_N})$ with
**exactly $\lceil (N{-}1)/3\rceil$ nontrivial entries**.
*Proof.* All invariant factors are 3-powers (lower-triangularity ⇒
$\det = 3^{N(N-1)/2}$ ⇒ divisibility chain; unconditional). The count is
$\mathrm{nullity}(T_N \bmod 3)$. By T4 the activation rows
$f(H) = \lfloor 3H/2\rfloor$ are strictly increasing, so the activated columns
($f(H)\le N$) are in echelon position — linearly independent — while the
non-activated columns are identically zero in $T_N$. Hence nullity
$= \#\{H \le N : \lfloor 3H/2\rfloor > N\} = \lceil (N{-}1)/3\rceil$
(elementary). ∎  (Verified directly on the banked matrix for all $N \le 36$.)

## Bonus depth (measured, not yet proved)

- $H^3 - H^2 \equiv 25t \pmod{27}$ — the spine cubic lifts two more 3-adic
  levels with the exact defect-species constant 25 ($25 \equiv 7 \bmod 9$,
  $\equiv 1 \bmod 3$).
- $(H^3 - H^2 - 25t)/27 \equiv t\,\big(W(t^3)-1\big) \pmod 3$ — the level-3
  correction is again $W$: the 3-adic tower of $H$ telescopes through the same
  series. (Also found: $(H(t^3)-H^2-t)/3 \equiv -(t+t^2+tW) \bmod 3$.)

## Falsifiable predictions (future terms)

**All confirmed 2026-07-31 against the banked a(40) triangle**
(`results/triangle.txt`, checked cell-by-cell):

- $T(37,25) \equiv 1 \pmod 3$ (odd spine, $k=12$) and $T(n,H) \equiv 0 \pmod 3$
  for all $37$-cell in-regime cells above the spine. **CONFIRMED** — spine cell
  $\equiv 1$; all of $T(37,H)$ for $H = 26..37$ and $T(n,25)$ for $n < 37$
  vanish mod 3.
- $T(39,26) \equiv 1 \pmod 3$ and $P_{13}(39) \equiv 3 \pmod 9$ (even spine).
  **CONFIRMED** — $T(39,26) \equiv 1 \pmod 3$, so $P_{13}(39) = 3\,T(39,26)
  \equiv 3 \pmod 9$; row-39 above-spine cells ($H = 27..39$) all vanish mod 3.
- Every future in-regime triangle cell mod 3 via T1's digit product.

## Row reading (jasonp's observation) and the sleeve zeros

Reading along rows instead of down columns:

- **The spine is also the LAST nonzero of its row.** Right of the spine in row
  $n$ means $n < \lfloor 3H/2\rfloor$ — the same proved zero region as "above
  the spine in column $H$"; the two statements are transposes of one fact.
- **Rows $n \equiv 2 \pmod 3$ have no spine cell.** Their last nonzero is the
  deficit-2 cell, and empirically it is ALWAYS $\equiv 2$:
  $$T(3m{+}2,\,2m{+}1) \equiv 2 \pmod 3\qquad(v_3(P_k(3k{-}1)) = 2,\ \text{unit }2,\ k=m{+}1).$$
  **PROVED 2026-07-15** (`experiments/deficit2_proof.py`): the family GF
  $D(v) = \sum_m P_{m+1}(3m{+}2)v^m$ is a diagonal of $G\,H^n$; formal
  Lagrange–Bürmann over $\mathbb Z/27$ plus the parametrization $v = u/H^3$
  turn the claim $D = 5 + 18v/(1-v)$ into a rational identity on the mod-27
  master curve $E(H,u) = 0$, decided by exact polynomial division ($E$ monic
  in $H$; remainder $\equiv 0$). So the last-nonzero residue of row $n$
  provably cycles $1,1,2$ with $n \bmod 3$ — the full row-reading picture is
  now theorem-grade (same conditional frame as the ladder: gas-derived
  master equation + boundary residue). The diagonal-family method (LB to the
  curve, then division) is reusable for any $(n,k)$-linear-family congruence.
- **Sleeve zeros are valuation spikes.** A band cell left of the spine carries
  forced deficit $d = 3k{+}1{-}n$; generically $v_3(P_k(n)) = d$ exactly (the
  cell is a unit there) and a ZERO marks excess divisibility
  $v_3(P_k(n)) > d$. Census (jasonp): first row with two zeros left of the
  spine is $n=19$ ($v_3(P_7(19))=4>3$, $v_3(P_9(19))=10>9$); first adjacent
  pair $n=30$; first three-in-total $n=35$; first three-in-a-row $n=36$. A
  closed law for these spikes (the deficit-$d$ unit formulas, $d \ge 2$) is
  the open remainder of the Witt tower.
- **Census extended to the final data, $n \le 40$ (2026-07-31).**
  `experiments/sleeve_zero_census.py` (`python3 experiments/sleeve_zero_census.py`)
  sweeps the sleeve of row $n$ — $k$ from $\lfloor(n{-}1)/3\rfloor+1$ (first $k$
  with $d\ge1$) to the law's reach $k_{\max}=\lfloor(n{-}1)/2\rfloor$ — and reads
  the valuation off the banked triangle via $v_3(P_k(n)) = v_3(T(n,n{-}k)) + d$,
  so it needs no fitted $P_k$ (which stop at $k=17$). It reproduces the census
  above exactly at $n\le36$, including the two $n=19$ valuations. New rows:

  | $n$ | sleeve zeros $(k: d \to v_3(P_k(n)))$ | count | longest run |
  |---|---|---|---|
  | 37 | $13\!: 3\to5$, $16\!: 12\to13$, $17\!: 15\to18$ | 3 | 2 |
  | 38 | $16\!: 11\to13$ | 1 | 1 |
  | 39 | — | 0 | 0 |
  | 40 | $16\!: 9\to10$, $18\!: 15\to18$, $19\!: 18\to21$ | 3 | 2 |

  **No new record events.** Rows 37 and 40 tie the three-in-total record (first
  set at $n=35$) and each contain an adjacent pair, but nothing reaches
  four-in-total or four-in-a-row, and $n=36$'s three-in-a-row still stands alone.
  So the four "firsts" above are final for this project's data. Two observations
  the extra rows add: the $k=16$ diagonal spikes in *three consecutive rows*
  $n=36,37,38$ and again at $n=40$, skipping only $n=39$ — which is itself the
  only wholly zero-free sleeve after $n=31$; and the excess $v_3-d$ in the new
  rows tops out at $3$ ($k=17$ at $n=37$; $k=18$ and $k=19$ at $n=40$), well under
  the all-$n$ ceiling of $5$ ($k=8$ at $n=17$), so no runaway. The $k=18,19$
  cells sit past the fitted range but inside the proved regime ($n \ge 2k+1$), so
  their valuations follow from the shape theorem plus the exact triangle.

### The frontier-parity law (jasonp, from the two staircases)

The law's diagonal reach in row $n$ is $k_{\max}(n)=\lfloor(n{-}1)/2\rfloor$, which
STALLS at even $n$ — the dashed boundary steps down without the band widening.
Diagonal $k$ gets its two fit points at $n=2k{+}1,2k{+}2$ and its first holdout only
at $n=2k{+}3$. Hence: a frontier term at even $n=2k{+}2$ has its top real-swept cell
on a fit-only, uncheckable diagonal (the \tiertwominus{} situation — $a(34)$ with
$P_{16}$, $a(36)$ with $P_{17}$; the exposed cells sit in the inner corners of the
dashed staircase), while a frontier at odd $n=2k{+}3$ is self-certifying (its top
cell IS the first holdout — $a(35)$ certifying $P_{16}$). Even frontiers mint the
tier asterisk; odd frontiers retire it. Same motif as the spine staircase: the
flat steps ($n\equiv2\bmod3$ for the spine, even $n$ for the law boundary) are
where the unproved/exposed cells live.

## Honest accounting

- **Unconditional:** Prop. 1–2, the lower half of T4, the 3-power SNF fact, the
  echelon/counting reductions, and the Lagrange-inversion identities about $W$
  itself ($[t^k]W^{3k+1}=1$ etc. — these are theorems about the cubic, full stop).
- **Conditional on the diagonal law**: everything quantified over all $k$.
  **UPGRADE 2026-07-12: the law's SHAPE is now a THEOREM**
  (`docs/proofs/diagonal-law.md`): polynomial × 3-power, deg ≤ k, onset
  n ≥ 2k+1, P_k integer-valued — proved via the defect-gas chain identity +
  partial fractions. What remains empirical is only the specific fitted P_k
  values for k ≤ 17 (k ≤ 3 re-derived from cluster weights, exact).
- **Conditional on the ladder $(\star a,b,c)$:** finitely many coefficient
  identities (verified through $y^{17}$; the digit formula then re-verified on
  342 independent triangle cells). **$(\star b)$ is now derived** from the
  defect-gas master equation + valuation lemma (`results/defect-gas.md`,
  2026-07-12), conditional only on the law + renewal formalism; $(\star a)$
  likewise derived (boundary weights), $(\star c)$ verified to $t^{300}$ on the
  explicit mod-27 fixed point — the ladder as an empirical input is retired.
- Naming: the cubic $W^3 = W^2+t$ is Artin–Schreier-like; $H\bmod 3$ being
  algebraic makes the triangle mod 3 3-automatic (Christol), and T1 is the
  automaton made explicit.

Companions: `results/triangle-snf.md` (the SNF thread this resolves),
`results/diagonal-closed-forms.md`, `results/triangle-structure.md` (Atom
Ledger; the "everything at prime 3" phenomenon now has its generating object).
