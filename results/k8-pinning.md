# Pinning the k=8 height-diagonal (P₈)

`T(n, n-k) = P_k(n)·3^(n-1-3k)`, P_k degree k, valid n ≥ 2k+1. Computed by
`scripts/pin_diagonal_k8.py` (exact rational arithmetic on the a(23) triangle).

## Results

1. **Leading-coefficient conjecture confirmed.** `[nᵏ]P_k = 25ᵏ/k!` holds
   *exactly* for k=3..7 (and k=0,1,2 are proven), with every available swept
   point lying on the fitted polynomial. 8 confirmations — a robust pattern.

2. **The "leading-coeff + k points" method is validated.** Fixing the leading
   coefficient and fitting the remaining k coefficients from only k swept points
   reproduces the *known* P₇ exactly and predicts the held-out swept rows
   T(22,15), T(23,16). So one fewer data point is needed than a blind fit.

3. **k=8 pins the instant a(24) lands.** We have 7 swept points for P₈
   (T(n,n-8), n=17..23); a degree-8 polynomial with leading coeff fixed has 8
   free unknowns — **short by exactly one**. The missing point is **T(24,16)**
   (n=24, h=16), which the a(24) sweep produces. No shortcut avoids a(24) for a
   *certified* pin.

4. **Falsifiable early prediction.** The sum-of-roots `s_k = -c_{k-1}/c_k` is
   itself quadratic in k (2nd differences constant at 0.334): s = 3.934, 6.403,
   9.206, 12.344, 15.816, 19.622 for k=2..7. This shortcut **passes a
   one-term-ahead self-test**: fitting the quadratic on k=2..6 only predicts s₇
   exactly, and the resulting P₇ predicts the held-out high rows. Applying it to
   k=8 (s₈ = 23.763) yields a provisional P₈ and the prediction

   > **T(24,16) = 42 594 477 635 772 598**

   When the a(24) run sweeps H=16, equality confirms the k=8 extrapolation in a
   single number; inequality refutes the sum-of-roots shortcut (the certified
   pin via a(24)'s actual T(24,16) is unaffected either way).

## Consequence for the a(25) ladder

With k=8 in hand, a(25) injects heights 17–25 and **sweeps only H ≤ 16** (peak
swept H16 instead of H17), the ~2.4× dominant-height saving behind the
a(24)→a(25) ladder. The ladder is therefore: run a(24) (k≤7, peak H16) → read
T(24,16), pin P₈ (and confirm it equals 42 594 477 635 772 598) → run a(25)
(k≤8, peak H16). `orchestrator/sweep.go diagonalCell` gets a `case 8` once the
pinned P₈ coefficients are in hand.
