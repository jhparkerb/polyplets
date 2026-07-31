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
  (modulo the diagonal law + a finitely-verified ladder) — the mod-3 diagonal
  family is governed by the spine cubic $W^3 = W^2 + t$ over $\mathbb F_3$, the
  activation entries evaluate in closed form by Lagrange inversion, and echelon
  independence finishes. See `results/ternary-spine.md` (proof chain + 15/15
  verifier). Remaining open there: prove the ladder itself; individual exponents
  $e_i(N)$ still have no formula (the mod-9/27 lifts are the attack).

### C2. A006770 is strictly log-convex
$$a(n)^2 < a(n-1)\,a(n+1)\qquad(n\ge3),$$
i.e. the ratios $a(n)/a(n-1)$ strictly increase to $\lambda$. Verified on the full
banked sequence $n\le40$ (zero violations; re-checked 2026-07-31 against
`results/triangle.txt` row sums). Consequence if proved: each ratio is a rigorous
lower bound on $\lambda$ (so $a(40)/a(39)=6.935\le\lambda$). Companions: one-sided A030233, free
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
