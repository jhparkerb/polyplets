# Certified mu_H — exact rational lower bounds on the strip growth constants

Date: 2026-07-31. Companion to
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md) (the numbers and
the lambda claim) and [strip-mu-engine-resumption.md](strip-mu-engine-resumption.md)
(the engines). This note covers only the **certificate**: what upgrades a
power-iteration `mu_H` from a floating-point value to a machine-checkable
rational, and the H<=11 receipts.

Tool: `cpp/strip_mu_cert.cpp` -> `build/strip_mu_cert` (`make build/strip_mu_cert`).
Receipts: [strip_mu_certificates.log](strip_mu_certificates.log).
Self-test gate: `make gate-strip-cert` (also in `make gates` and `make ns-gate-fast`).

## What a certificate is

The `mu_H` in the banked ladder are floating-point outputs of a bisection over a
power iteration. Nothing in that chain is checkable after the fact: rerun it on
another box, get another set of last digits, and there is no artifact a reader can
audit. A **certificate** replaces the chain with a finite object plus a finite
integer computation:

> a nonnegative, nonzero integer vector `v` and a rational `x = den/num` such
> that `(M(x) v)_i >= v_i` holds for every state `i`, verified in exact integer
> arithmetic.

Anyone can re-run the check. It is a proof, not a measurement.

## The three inequalities

**1. Collatz-Wielandt (the spectral half).** Let `A` be a nonnegative matrix and
`v >= 0`, `v != 0`, with `A v >= v` componentwise. `A` is monotone, so
`A^k v >= v` for all `k`; picking any `i` with `v_i > 0` gives
`||A^k||_inf >= v_i / ||v||_inf`, and therefore
`rho(A) = lim_k ||A^k||^(1/k) >= 1`. Neither positivity of `v` nor irreducibility
of `A` is needed for this direction — only the lower half of the two-sided
Collatz-Wielandt formula (Horn & Johnson, *Matrix Analysis* 2nd ed., §8.1;
Berman & Plemmons, *Nonnegative Matrices in the Mathematical Sciences*, Ch. 2),
whose upper half we never use.

**2. Monotonicity in x (the transfer half).** `M(x)` is the height-`<=H` king
connectivity transfer operator, with entries `x^(cells placed)` — nonnegative and
strictly increasing in `x`. `rho` is monotone in the entries of a nonnegative
matrix, so `rho(M(x))` is increasing, and `x*` (where `rho = 1`) is the radius of
convergence of the height-`<=H` strip generating function, with `mu_H = 1/x*`.
Hence

    rho(M(x)) >= 1   ==>   x >= x*   ==>   mu_H = 1/x* >= 1/x.

Putting the two together: an exactly-checked `M(den/num) v >= v` certifies
`mu_H >= num/den`.

**3. Subfamily containment (the lambda half).** Height-`<=H` polyplets are a
subfamily of all polyplets, so `T_{<=H}(n) <= a(n)` for every `n` and
`mu_H <= lambda`. That argument — not anything in this tool — is what makes a
certified `mu_H` a certified `lambda` lower bound; it lives in
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md). Every row below
therefore also reads `lambda >= <certified value>`.

## The H<=11 certificates

`den = 10^7` throughout; the certified value is `mu_H` floored to 7 decimals, and
every one of these passed on the **first** candidate numerator (no step-down).
`mu_H (float)` is the power-iteration value the search phase produced, and it
reproduces the banked ladder to all quoted digits.

| H | certified `mu_H >=` | num / 10^7 | states | `mu_H` (float) | banked | wall |
|---|---|---|---|---|---|---|
|  2 | 2.4142135 | 24142135 |     3 | 2.414213562 | 2.4142136 |    0.0s |
|  3 | 3.4437183 | 34437183 |     8 | 3.443718375 | 3.4437184 |    0.0s |
|  4 | 4.1823214 | 41823214 |    20 | 4.182321413 | 4.1823214 |    0.0s |
|  5 | 4.7178012 | 47178012 |    50 | 4.717801291 | 4.7178013 |    0.0s |
|  6 | 5.1153244 | 51153244 |   126 | 5.115324460 | 5.1153245 |    0.1s |
|  7 | 5.4178476 | 54178476 |   322 | 5.417847610 | 5.4178476 |    0.8s |
|  8 | 5.6533727 | 56533727 |   834 | 5.653372762 | 5.6533728 |    3.2s |
|  9 | 5.8404579 | 58404579 |  2187 | 5.840457941 | 5.8404579 |   11.2s |
| 10 | 5.9916957 | 59916957 |  5797 | 5.991695792 | 5.9916958 |   36.2s |
| 11 | 6.1158416 | 61158416 | 15510 | 6.115841628 | 6.1158416 |  120.9s |

(`H=2` is the independent anchor: `mu_2 = 1 + sqrt(2) = 2.41421356...`.)

Vector checksums (SHA-256 over the states sorted by their raw signature bytes,
each followed by its 16-byte little-endian value) are in the receipt log, one line
per certificate, alongside `git`, `host`, `states`, `vbits` and wall time.

## How the tool works

Two phases, and only the second one is load-bearing.

- **Phase 1 (float, a search).** Warm-started bisection on `x` for
  `rho(M(x)) = 1`, using the same cell-at-a-time column sweep as
  `cpp/strip_mu_kink.cpp` — the production `kinkStageTransition` from
  `core/kink.h`, copied verbatim. Output: an approximate `x*` and an approximate
  Perron vector. **Nothing here enters the proof**; it only proposes a candidate.
- **Phase 2 (exact, the proof).** Scale the float vector to integers with the
  largest entry at `2^vbits`, set `num = floor(mu_float * 10^7)`, and check
  `M(10^7/num) v >= v` in `unsigned __int128`. If any state fails, the tool
  searches for the largest `num` that does pass — the check is monotone in `num`
  (smaller `num` means larger `x`, and every entry of `M(x)` is nondecreasing in
  `x`), so it brackets by doubling and bisects, ~`2*log2(gap)` sweeps rather than
  hundreds. The winning numerator is re-verified last, so the receipt describes
  the rational actually certified. A failure is never absorbed into a tolerance.

  One vector serves the whole search: lowering `num` moves `x` by parts in 1e8,
  far below anything the exact check resolves, and a single fixed `v` makes the
  receipt's checksum unambiguous.

Three things make the exact phase sound rather than merely careful:

- **Every rounding is downward.** Each of the `H` stages is a nonnegative linear
  map (hence monotone) and the "cell placed" branch contributes
  `floor(val * 10^7 / num) <= val * x`. So the computed vector is `<=` the true
  `M(x) v` componentwise, and a check that passes on the computed vector passes
  on the exact product. The "no cell" branch has weight 1 and is copied exactly.
- **Restriction is safe.** Only the finite support `S` of the converged
  eigenvector is held; mass leaving `S` is dropped. That certifies the principal
  submatrix `M_S`, and `rho(M_S) <= rho(M)` — a PASS on `M_S` implies a PASS on
  `M`. (Entries that quantize to 0 are likewise harmless: Collatz-Wielandt needs
  only `v >= 0`, `v != 0`, and every state is still checked.)
- **Overflow is loud.** Every multiply and add is guarded against `2^126` and a
  trip is a FAIL with the state named, never a silent wrap. `--vbits` is
  auto-sized to `126 - ceil(digits*log2 10) - 6` and an explicit larger value is
  refused. Measured headroom at H<=11: the largest value ever held is 96.7 bits
  against the 96-bit vector ceiling, i.e. merges add 0.7 bits.

## RED-first self-test (`--selftest`, `make gate-strip-cert`)

The checker has to be able to say no, so the gate makes it:

- **A.** `mu_2 = 1 + sqrt(2)`, so `24142/10000` must PASS — it does.
- **B.** `24143/10000` exceeds `mu_2`, so it must FAIL — it does, and the receipt
  names the offending state and prints `lhs < rhs` in full integers.
- **C.** One entry of a *passing* vector is multiplied by `2^30`; the check must
  reject it — it does, naming the state.
- **D.** The all-zero vector satisfies `A v >= v` vacuously and would certify
  *every* rational; it must be refused — it is.

Bad arguments are refused rather than clamped: an out-of-range `H`, or a
`--vbits` above the arithmetic's headroom, exits 2 with the valid range printed.

## Honest scope

- What is certified is the inequality `mu_H >= num/den`, given that `M(x)` is the
  strip transfer operator. The operator itself is trusted, not certified here: it
  is the production kink kernel (`make ns-gate-kink`, `ns-gate-kink-column`), and
  the resulting `mu_H` are cross-checked against the fixed-height GF roots for
  `H<=11` (`results/fixed_height_gfs.txt`, `experiments/mu_H_from_atoms.py`).
- The certified digits are a floor, so `2.4142135` for `H=2` is the certificate
  even though `mu_2 = 2.4142136` to 7 places. Certificates state what is *proved*.
- Precision budget: the eigenvector's dynamic range grows steeply and unevenly
  with H (measured: 24.1 bits at H=8, 39.7 at H=9, 44.8 at H=10, 52.5 at H=11 —
  increments +15.6, +5.1, +7.7), while `vbits` is fixed at 96 by the 2^126
  arithmetic ceiling. The smallest entries must survive the per-stage
  flooring, so at large H the tool may have to lower `num` a little. That costs
  last digits, not validity, and the receipt records `attempts` (sweeps) and the
  numerator actually certified.

  Measured, by deliberately crippling the precision: `--vbits 55` at H=10 (the
  smallest entry becomes ~2^10 instead of ~2^51) makes the first candidate fail
  at 4 states with `min_ratio = 0.99994` — the binding state is short by **one
  unit in the last place**, so the flooring loss is O(1) ulp, not O(H). The
  bracket-and-bisect then lands on `59916466/10^7` in 20 sweeps, at a total wall
  indistinguishable from the single-sweep full-precision run: the search is
  essentially free, and the cost of the crippling shows up honestly as lost
  digits (`5.9916466` instead of `5.9916957`), never as a wrong claim.

  Continuing the last two increments puts the H=14 range near 76 bits, leaving
  the smallest entries around 2^20 at `vbits = 96` — far better conditioned than
  the `--vbits 55` stress case. That extrapolation is loose (the H=8->9 increment
  was 15.6 bits), but the failure mode is bounded: if the range runs ahead of it,
  the search absorbs the difference as lost digits, not as a wrong claim.
- `H >= 12` is not certified yet. `H=14` (`mu_14 = 6.3800344`) is the interesting
  one — it is the ladder's current top — and is a ~1.5h single-threaded job,
  scheduled separately. Per-H cost measured here is ~3.3x (H=9: 11.2s,
  H=10: 36.2s, H=11: 120.9s on gympie), extrapolating to ~70 min at H=14 and
  consistent with the banked `strip_mu_kink` H=14 float solve at 4851s
  (`results/strip_mu_H14.log`); peak RSS is 15 MB at H=11, so memory is a
  non-issue.

## Reproduce

    make build/strip_mu_cert
    ./build/strip_mu_cert --selftest                       # RED-first gate
    ./build/strip_mu_cert 2 11                             # H<=11, ~3.5 min

Receipts append to `results/strip_mu_certificates.log` (override with `--log`).
The H=14 run is a separately scheduled single-threaded ~1.5h job with its own
runner (cost basis and kill/resume notes in the header):

    scripts/run_strip_mu_cert_h14.sh
