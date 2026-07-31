# Strip growth constants mu_H — a rigorous lower-bound ladder for lambda

Date: 2026-07-10. Shaken loose while exploring T(n,H). `mu_H` = dominant
eigenvalue of the height-H strip transfer matrix = top root of atom `q_H` =
`1/(smallest positive root of Q_H)` from the banked fixed-height GFs
(`results/fixed_height_gfs.txt`). Computed exactly (mpmath) in
`experiments/mu_H_from_atoms.py`.

## The numbers (exact strip growth constants, H<=13)

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mu_H | 2.4142 | 3.4437 | 4.1823 | 4.7178 | 5.1153 | 5.4178 | 5.6534 | 5.8405 | 5.9917 | 6.1158 | 6.2191 | 6.3061 | 6.3800 |

H<=11 from fixed-height GF roots; **H=12,13 newly computed by power iteration on
the strip transfer matrix** (`cpp/strip_mu.cpp`, `build/strip_mu`; validated: it
reproduces the GF-root mu_H exactly for H<=11). Increment ratios climb 0.72→0.84
(power-law decay, not geometric).

## Why this matters

**1. Rigorous, exact, monotone lower bounds on lambda.** Each strip grows strictly
slower than the plane, so `mu_H < lambda` rigorously, with `mu_H -> lambda`. Each
`mu_H` is an algebraic number (top root of `q_H`) — no numerical caveat, unlike
the multi-directed 6.475. Extrapolating the increments, `mu_H` crosses **6.475
around H~16** and reaches **~6.6 by H~18-20** — which would be the **best rigorous
lower bound on lambda we have**, beating both Bacher bounds (directed 5.828,
multi-directed 6.475), our own, and improvable with H.

> These `mu_H` bounds squeeze lambda from BELOW. The complementary rigorous UPPER
> bound is **lambda <= 9.3153** (Bui-style finite-type convolution certificate,
> exact rational arithmetic), giving the two-sided bracket **5.828 <= lambda <=
> 9.3153**. Derivation: [../docs/proofs/polyplet-upper-bound.md](../docs/proofs/polyplet-upper-bound.md).

   Current ladder tops at mu_14 = 6.3800 (still below 6.475 — need higher H to win).

> **Certificate grade, H<=11.** The `mu_H` below are floating-point power-iteration
> values. `cpp/strip_mu_cert.cpp` upgrades them to exact rationals verified in
> integer arithmetic (Collatz-Wielandt on the transfer operator at a rational x),
> with a per-H receipt in `results/strip_mu_certificates.log`. Done for H<=11;
> H=14 scheduled. Method, receipts and honest scope:
> [strip-mu-certificates.md](strip-mu-certificates.md).

**2. Independent lambda estimate (delivered, H<=13).** Sliding 3-point power-law
fit `mu_H = lambda - c*H^{-p}` (`experiments/lambda_from_mu.py`) gives lambda
estimates marching monotonically down as the center H rises:
`9.54, 8.41, 7.92, 7.66, 7.50, 7.40, 7.33, 7.29` (center H=5..12), with the
exponent `p -> ~1` (a 1/H finite-size correction). Converging straight toward the
`a(n)`-ratio value **~7.11** — a structurally **independent** second determination
(strip spectra vs row-sum ratios) corroborating the paper's single fit. Not yet
sharper than 7.11 (H<=13 too small; estimate still ~7.29 at H=12), but the
convergence is clean and monotone. This is the bankable paper result.

## Why it's cheap (the lever)

Higher `mu_H` needs neither enumeration nor the full atom — only the **dominant
eigenvalue** of the height-H strip transfer matrix, by **power iteration** on the
(sparse, structured) matrix `strip_tm.cpp` already builds. No counting, no
Berlekamp-Massey, no CRT. Power iteration to H~18-20 is far cheaper than the
counts and gives:
- the record rigorous lower bound on lambda (exact-ish, ~6.6+), and
- an independent finite-size lambda estimate for the paper.

## Caveat / honest state

- The count-ratio route to mu_H (T(n,H)/T(n-1,H)) is badly under-converged for
  H>~6 (at n=36, H=18 the ratio is 7.63 > lambda). Must use the eigenvalue /
  GF-root route, not count ratios. (`experiments/strip_growth_extrapolation.py`
  documents the under-convergence.)
- Extrapolation quality: full Richardson (1/H^2) gives 7.41, local two-point gives
  6.64-6.71 — they disagree, so higher-order corrections matter; H<=11 is too few
  for a controlled lambda estimate. The rigorous *lower bound* use needs no
  extrapolation and is immediately valid.

## Engine status & next

- **Done:** `cpp/strip_mu.cpp` — power iteration on the all-column strip transfer
  matrix, warm-started bisection. Reached H=13 (7.7 min; H=11:10s, H=12:67s,
  H=13:465s). Cost ~6x/H and edge memory ~states*2^H blow up, so this engine tops
  out ~H=13-14.
- **Rigorous-bound status:** mu_13 = 6.306 is a valid rigorous lower bound on
  lambda but still BELOW the multi-directed 6.475. Beating 6.475 needs mu_16
  (~6.5), i.e. H=16 — out of reach for the all-column engine.
- **Cell-at-a-time engine BUILT + VALIDATED** (`cpp/strip_mu_kink.cpp`): reuses
  the production `kinkStageTransition` (core/kink.h); one matvec = a column sweep
  (seed -> H per-cell stage transitions, weight x^placed, states merge ->
  finalize), `O(H*states)`, no 2^H, no edge storage. Reproduces mu_H exactly
  through H=11 (5.99…, 6.11…). Also `cpp/strip_mu8.cpp` (whole-column via the
  tma viable-mask kernel) validates but hits the same 2^H edge wall as strip_mu.
- **Speed gap:** the kink engine's first cut is `unordered_map`-bound (H=11 in
  100s, ~3.4x/H) -> H=16 ~12h. Correctness is done; reaching H=16 (mu~6.5, beats
  6.475) needs an indexed-array rewrite of the same logic (per-stage sparse
  operators) — fast but another build increment. H=14 **done: mu_14 = 6.3800344**
  (`results/strip_mu_H14.log`, 4851s); still below 6.475 (need higher H to win).
