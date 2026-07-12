# Open conjectures & theorems-to-prove (collaboration menu)

2026-07-11. Fresh targets surfaced from the banked data, plus two already-set-up
theorems. Each is crisp and checkable; the first two are new this session.

## NEW conjectures (strong numerical evidence)

### C1. The height-triangle determinant is a pure power of 3
For the $N\times N$ matrix $T=[\,T(i,j)\,]_{1\le i,j\le N}$ (height triangle,
$T(n,H)$),
$$\det T_N \;=\; \pm\,3^{\,N(N-1)/2}.$$
Verified $N\le18$ (exact; `experiments/`... via sympy). **This one identity implies
the whole "everything at prime 3" structure** (`results/triangle-snf.md`): the Smith
invariant factors form a divisibility chain $d_1\mid d_2\mid\cdots\mid d_N$, so if
$\prod d_i=|\det|$ is a pure 3-power, every $d_i$ is a 3-power — hence the cokernel
$\mathbb Z^N/T_N\mathbb Z^N$ is a finite 3-group. The exponent
$N(N-1)/2=\sum_{n\le N}(n-1)$ is exactly the 3-valuation of the diagonal
$\prod_n T(n,n)=\prod_n 3^{\,n-1}$.
- **Attack:** show $T_N$ is unimodular over $\mathbb Z_p$ for every $p\ne3$
  (equivalently $\det\not\equiv0\bmod p$), and that its Smith form over $\mathbb Z_3$
  has diagonal $3^{e_i}$ with $\sum e_i=N(N-1)/2$. The "why 3": each row of a
  height-$H$ animal is one cell drifting by $\{-1,0,+1\}$ (three choices), the source
  of the $T(H,H)=3^{H-1}$ diagonal and, plausibly, of a base-3 factorization of the
  whole triangle.

### C2. A006770 is strictly log-convex
$$a(n)^2 < a(n-1)\,a(n+1)\qquad(n\ge3),$$
i.e. the ratios $a(n)/a(n-1)$ strictly increase to $\lambda$. Verified $n\le36$
(zero violations). Consequence if proved: each ratio is a rigorous lower bound on
$\lambda$ (so $a(36)/a(35)=6.916\le\lambda$). Companions: one-sided A030233, free
A030222, asymmetric A030235 are log-convex past small $n$; **the bilateral count
A030234 is NOT** — log-convexity fails at every even $n$, a parity effect worth its
own look.
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
$N_k(\pm1)=(\pm2)^k$ for $k\ge1$ (observed, never imposed on the fit). Proving it is
the "two ground states / two species per odd footprint" combinatorial identity.

## Also-rans (probed, not clean)
- SNF individual exponents $e_i(N)$: no evident closed form (largest and count are
  clean; the middle ones are not). Superseded framing: C1 is the right handle.
- Atom degrees $1,2,4,9,29,68,181,462,1254,3289$ (strip-GF denominator degrees):
  no low-order constant-coefficient recurrence; ratios drift to $\sim2.65$.
