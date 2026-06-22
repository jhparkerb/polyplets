# Growth constant and critical exponent (series analysis)

From the a(n) series (A006770, n=1..19) and Free(n) (A030222, n=1..19), assuming
the standard form a(n) ~ C·λⁿ·nᶿ for 2D lattice animals. Method: successive
ratios r(n)=a(n)/a(n-1) ~ λ(1+θ/n); linear fit of r(n) vs 1/n (intercept λ,
slope λθ) plus the first-order extrapolant n·r(n)−(n−1)·r(n−1) → λ.

## Results
- **λ_king ≈ 7.10** (extrapolant: 7.099, 7.100, 7.101 — well converged;
  linear-fit intercept 7.095). Fixed and free agree (7.10 vs 7.11), as they must.
- **θ ≈ −0.95** (fixed −0.93, free −0.97), **consistent with the believed
  θ = −1** for two-dimensional lattice animals.

## Honesty
- Short series (~19 terms) ⇒ ~2–3 significant figures on λ, and θ only roughly
  pinned (but clearly near −1, not 0 or −2). More terms (a(20)+) tighten both.
- This estimates λ/θ; it does not prove them. It is the standard ratio-analysis;
  proper differential-approximant analysis would give tighter bars but needs a
  longer series than we have.
- TODO at write-up: compare λ_king ≈ 7.10 against any published king-lattice /
  polyplet growth-constant estimate (don't assert novelty for the constant).

## Rigorous bounds (the sandwich around the numerical estimate)
The ratio analysis ESTIMATES λ ≈ 7.10; it proves nothing. Two rigorous bounds
bracket it:
- **Lower:** a(n) is supermultiplicative (king-adjacent concatenation), so
  a(n)^{1/n} increases to λ ⇒ λ ≥ a(20)^{1/20} ≈ **5.6** (loose; the sequence
  approaches λ slowly from below, which is why the ratios already read ~6.5–6.6).
- **Upper:** the spanning-tree / direction-labelled-tree overcount gives
  λ ≤ **7⁷/6⁶ = 17.6529** (the king analogue of the classic 3³/2²=6.75 polyomino
  tree bound). Proof in `docs/lambda-bound.md` (branch explore/theorem-lambda-bound).

So **5.6 ≤ λ_king ≤ 17.65 rigorously, ≈ 7.10 numerically.** The upper bound is
~2.5× the estimate; a Klarner–Rivest twig refinement (it sharpens 6.75 → 4.65 for
polyominoes) is the path to tighten it.
