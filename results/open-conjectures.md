# Open conjectures & theorems-to-prove (collaboration menu)

2026-07-11. Fresh targets surfaced from the banked data, plus two already-set-up
theorems. Each is crisp and checkable; the first two are new this session.

## NEW conjectures (strong numerical evidence)

### C1. "SNF is a 3-group" is PROVED (was mis-stated as a hard determinant identity)
$T(n,H)=0$ for $H>n$ (an $n$-cell animal has height $\le n$), so $T_N$ is
**lower-triangular** and $\det T_N=\prod_n T(n,n)=\prod_n 3^{\,n-1}=3^{N(N-1)/2}$ is
immediate — not a conjecture. What it buys for free (settling
`results/triangle-snf.md`'s first open bullet): the determinant is a pure 3-power,
the Smith invariant factors form a divisibility chain $d_1\mid\cdots\mid d_N$ with
$\prod d_i=|\det|$, so any prime $q\ne3$ dividing some $d_i$ would divide $d_N$ hence
$|\det|$ — impossible. **Therefore every invariant factor is a power of 3 and the
cokernel is a finite 3-group.** Done, for all $N$.
- **RESOLVED 2026-07-12:** the $\lceil(N-1)/3\rceil$ count is now a **theorem**
  (modulo the diagonal law + the renewal/defect-gas chain formalism — the
  ladder $(\star a,b,c)$ is derived, not assumed: `results/defect-gas.md`,
  upgrade 2026-07-12/13) — the mod-3 diagonal family is governed by the spine
  cubic $W^3 = W^2 + t$ over $\mathbb F_3$, the activation entries evaluate in
  closed form by Lagrange inversion, and echelon independence finishes. See
  `results/ternary-spine.md` (proof chain + 15/15 verifier). Remaining open
  there: individual exponents $e_i(N)$ still have no formula (the mod-9/27
  lifts are the attack).

### C2. A006770 is strictly log-convex
$$a(n)^2 < a(n-1)\,a(n+1)\qquad(n\ge3),$$
i.e. the ratios $a(n)/a(n-1)$ strictly increase to $\lambda$. Verified on the full
banked sequence $n\le40$ (zero violations; re-checked 2026-07-31 against
`results/triangle.txt` row sums). Consequence if proved: each ratio is a rigorous
lower bound on $\lambda$ (so $a(40)/a(39)=6.935\le\lambda$). Companions: one-sided A030233, free
A030222, asymmetric A030235 are log-convex past small $n$; **the bilateral count
A030234 is NOT** — log-convexity fails at every even $n$, a parity effect worth its
own look. (Exact witness lists for every companion, plus the family-wide
ratio-sequence sweep and two more converse kills — onset sharpness to $k\le13$,
k!-minimality refuted — in `results/converse-sweep.md`, 2026-07-31.)
- **Margin structure (measured 2026-07-31):** the violation margin
  $a(n{-}1)a(n{+}1)/a(n)^2 - 1$ tracks $-\theta/n^2$ exactly: $n^2\cdot$margin
  climbs smoothly $0.89 \to 0.97$ over $n = 5..39$, consistent with
  $\theta = -1.000(1)$ from the differential approximants. The margin is
  structural, not marginal — so a *refutation* of C2 (a violating term) would
  contradict the entire smooth-asymptotics picture and has no finite-certificate
  route short of exhibiting a term past $a(40)$; both directions are gated on
  proof-grade control of the correction structure, which nothing currently
  provides. The affirmative injection route below remains the only path that
  sidesteps asymptotics entirely.
- **Ratio sequence is NOT log-convex — THEOREM (jasonp's question, settled
  2026-07-31):** $r(n) = a(n)/a(n{-}1)$ is strictly log-*concave* at every
  testable index: $r(n)^2 > r(n{-}1)r(n{+}1)$, i.e.
  $a(n)^3 a(n{-}2) > a(n{-}1)^3 a(n{+}1)$, holds for **all** $n = 3..39$ (exact
  integer arithmetic on the banked terms). Witness at $n=3$ needs only
  $20^3\cdot1 = 8000 > 7040 = 4^3\cdot110$ — terms that are two-algorithm
  verified and Lean-kernel-proved (`a_1..a_6`), so the refutation is
  certificate-grade. Together with C2 this is the coherent picture
  $r(n) \approx \lambda(1 - 1/n)$: ratios increase (C2, conjectural), at
  decreasing pace (log-concavity, witnessed everywhere measurable); the
  all-$n$ log-concavity statement is C2's conjecture-grade mirror, gated on
  the same correction-structure control.
- **Attack:** log-convexity of animal counts is genuinely hard; the natural route is
  an injection $\mathcal A_{n-1}\times\mathcal A_{n+1}\hookrightarrow\mathcal A_n
  \times\mathcal A_n$ (or a total-positivity property of the transfer matrix). No
  clean injection is known for lattice animals — finding one would be the theorem.

## Theorems already set up (to prove together)

### T3. Max enclosed hole area $M(n)=\mathrm{round}((n-2)^2/8)$
Reduced (`results/maxhole-proof.md`) to one lemma: a king-connected closed curve
enclosing a single hole of diagonal extent $h_a\times h_m$ uses $\ge h_a+h_m+2$
cells. Construction (diamond ring) done for $n\equiv0\bmod4$; the lemma is a
winding-number / discrete-Jordan-curve count. Both sub-lemmas verified on ~2400
shapes.

### T4. $N_k(\pm1)=(\pm2)^k$ for the diagonal-mirror numerators
The paper conjectures the dmirror diagonal GF $G_k=N_k/((1-x)^{k+1}(1+x)^k)$ has
$N_k(\pm1)=(\pm2)^k$ for $k\ge1$ (observed, never imposed on the fit).
**Reduced 2026-07-31** (`results/dmirror-diagonals.md`): via partial
fractions, $N_k(1)=2^k$ ⟺ each parity class has leading coefficient
$S^k/k!$ (banked), and $N_k(-1)=(-2)^k$ ⟺
$\mathrm{lead}(P^{even}_k-P^{odd}_k)=(-1)^k/(k-1)!$ (verified exactly
k=1..5). So T4 = "each of the two ground-state spines carries defect
density 1" -- the combinatorial identity to prove is about leading
coefficients, not numerator boundary values.

## Also-rans (probed, not clean)
- SNF individual exponents $e_i(N)$: no evident closed form (largest and count are
  clean; the middle ones are not). Superseded framing: C1 is the right handle.
- Atom degrees $1,2,4,9,29,68,181,462,1254,3289$ (strip-GF denominator degrees):
  no low-order constant-coefficient recurrence; ratios drift to $\sim2.65$.
