# Head-check: banked fixed-height GFs vs the exact triangle, n <= 40

Date: 2026-07-31. The banked `G_H(x) = P_H/Q_H` (`results/fixed_height_gfs.txt`,
H = 1..11, recurrence orders 1, 3, 7, 15, 42, 106, 278, 711, 1897, 5005, 13381)
had never been re-expanded against the finished triangle. Tool:
`experiments/gf_head_check.py` (exact integer series division; `Q_H[0] = 1`, so
no fractions arise). Motivated by the H=11 entry, banked `validated=False` and
flagged anomalous in [anisotropic-not-dfinite.md](anisotropic-not-dfinite.md).

```
python3 experiments/gf_head_check.py
```

Method: only the first 41 coefficients of `P_H` and `Q_H` are parsed (heads of a
12 MB line), since tail terms beyond `x^40` provably cannot influence a
coefficient `<= 40`. Convention confirmed as `G_H = sum_n T(n,H) x^n` with no
offset: H=1 is `x/(1-x)` (T(n,1)=1), H=2 reproduces T(3,2)=10, and every series
vanishes below `x^H` (`low0` column) as exact-height counting requires.

## Result: all 11 heights match, cell for cell

| H | order | validated | cells compared (n=H..40) | match | first mismatch |
|---|-------|-----------|--------------------------|-------|----------------|
| 1 | 1 | True | 40 | 40 | - |
| 2 | 3 | True | 39 | 39 | - |
| 3 | 7 | True | 38 | 38 | - |
| 4 | 15 | True | 37 | 37 | - |
| 5 | 42 | True | 36 | 36 | - |
| 6 | 106 | True | 35 | 35 | - |
| 7 | 278 | True | 34 | 34 | - |
| 8 | 711 | True | 33 | 33 | - |
| 9 | 1897 | True | 32 | 32 | - |
| 10 | 5005 | True | 31 | 31 | - |
| **11** | **13381** | **False** | **30** | **30** | **-** |

385 cells compared, 385 exact agreements, zero mismatches; below-`x^H`
vanishing holds at every height. Runtime 0.04s.

## Sanity control (so a clean pass means something)

Two scratch GF files (scratchpad, not `results/`), both fed to the same
comparator:

- **truncation control** — all 11 blocks cut to 41 coefficients: still PASSES,
  confirming the head-slicing is sound (tails cannot reach the head);
- **corruption control** — the same file with `P_11[20] += 1` and `Q_5[7] += 1`:
  FAILS at exactly the predicted places, `H=5` first mismatch `n=12` (= 7+5,
  the first coefficient the perturbed `Q` term can reach) and `H=11` first
  mismatch `n=20`, exit status 1.

The comparator is therefore not vacuous, and it fails closed (nonzero exit on
any mismatch, missing triangle cell, or parse surprise).

## Conclusion — carefully scoped

The **head** of the banked H=11 generating function is now confirmed against the
exact triangle for every `n <= 40`. **This does not clear the `validated=False`
flag.** The anomaly recorded in
[anisotropic-not-dfinite.md](anisotropic-not-dfinite.md) is about the *full
rational function* — `Q_11` shares no roots with `Q_9 Q_10` mod p, inconsistent
with the atom law that holds at every validated level — and a head-check is
structurally incapable of touching it: 30 coefficients against a
(13381 + 13381)-coefficient rational function is a wildly underdetermined
constraint. What is now known is narrower and worth having: *if* the H=11 entry
is wrong, it is wrong in the tail, not in the range where the triangle exists.

**That conditional resolved on 2026-09-05, and the H=11 entry is wrong.** See
"H=11 refuted" below. Its exclusion from the psi-ladder certificates was, and
remains, correct.

For H = 1..10 the head-check is a genuine (if weak) independent corroboration of
the mod-p + Berlekamp-Massey + CRT recovery: the triangle comes from the
enumeration engines, the GFs from the transfer-matrix/BM pipeline, and they
agree on 355 cells.

## mu_11 provenance (grade check)

`experiments/mu_H_from_atoms.py` parses **every** `Q:` block of
`results/fixed_height_gfs.txt`, including H=11, and bisects for the smallest
positive root — so the `mu_11 = 6.1158` printed in
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md) does, as banked,
derive from the `validated=False` denominator. But the number itself is **not**
tainted: `cpp/strip_mu.cpp` (`build/strip_mu`) computes `mu_H` by Perron power
iteration on the height-H king connectivity transfer matrix and never reads the
GF file at all. Re-run today, `./build/strip_mu 10 11` gives
`mu_10 = 5.9916958, mu_11 = 6.1158416` in 10.3s — identical to the GF-root value
to all printed digits, and `cpp/strip_mu_kink.cpp` is a third, structurally
different (cell-at-a-time) engine that also reproduces it. So the `mu_11` rung
of the lower-bound ladder stands on an independent construction; only its
attribution needs care. Note that this agreement pins one root of `Q_11` (the
dominant pole) and says nothing about the other 13380 — it is not evidence
against the root-structure anomaly.

## H=11 refuted (2026-09-05): a CRT wraparound

The banked H=11 entry is wrong, not merely unvalidated. The recovery tool
(`gf/modp_recover.py`, deleted in `91bdcdc`; `git show 91bdcdc^:gf/modp_recover.py`)
lifted the H=11 coefficients by CRT from a fixed pool of 133 primes below 2^31,
whose modulus half `M/2` has 1241 digits. The true coefficients grow at 0.097
digits per degree at every validated height (H=9: 184 digits at degree 1897;
H=10: 486 at 5005), so at degree 13381 they reach about 1299 digits. The pool
was about six primes short, and the banked block shows it: 370 of its 26764
coefficients sit within 10% of `M/2`, the largest at 0.999 of it, while at H=10
none comes within 10%.

The proof is the pipeline's own soundness gate run on the banked entry,
`experiments/gf_h11_validate.py`: expand `Q_11 * B_11` and compare with `P_11`
coefficient by coefficient modulo a fresh prime (1073741789, outside the pool),
with `B_11(n)` from `build/gf_modp`, `n = 0..26792`. **First mismatch at
`n = 8170`**, so the first bad coefficient is at degree 8159, where the
coefficient profile crosses the 133-prime ceiling. The same script on the
validated H=8 and H=9 blocks (`gf_h11_validate.py 8`) reports no mismatch, and
its RED control (`--perturb 355`, adding 1 to one `Q` coefficient) fails at that
degree plus H exactly. Engine sweep 884.8 s, comparison 1.1 s.

What survives: the `psi`-ladder certificates, which read `validated=True` blocks
only; `mu_11`, because at `x = 1/6.1158416` the tail from degree 8159 contributes
`10^-5177` to `Q_11(x)` against `10^-32` for the head, so the bisection in
`experiments/mu_H_from_atoms.py` cannot see it; and `order = 13381` with
`deg N_11 = 8838`, the Berlekamp-Massey order agreed across all 133 primes before
the lift. What does not survive is any use of the H=11 `P` or `Q` coefficients.
The bank header and the H=11 line carry `refuted=2026-09-05
first_bad_degree=8159`; the four parsers (`gf_head_check.py`,
`anisotropic_dfinite.py`, `atom_degrees.py`, `verify_claims.py`) key on
`validated=True` or `order=` and were re-run green. The "no shared roots with
`Q_9 Q_10`" observation was a restatement of the wraparound: a wrapped lift is
an essentially random integer polynomial.

**Re-recovery, priced and not launched.** Calibration on gympie, output to
scratch, compared against the bank:

| H | primes | wall | CPU-s | workers | `M/2` digits | coeff digits | matches bank |
|---|--------|------|-------|---------|--------------|--------------|--------------|
| 8 | 40 | 4.9s | 26.2 | 10 | 373 | 72 | yes, exactly |
| 9 | 40 | 42.3s | 252 | 10 | 373 | 184 | yes, exactly |
| 10 | 57 | 870.8s | 4065 | 8 | 532 | 486 | yes, exactly |

The H=11 per-prime sweep at `N = 26792` is 884.8 s single-threaded at 248 MB; the
adaptive pool grows from 133 to 194 primes, 47.7 CPU-hours, plus a serial
38-minute order search: about 6.4 h wall on gympie (10 workers, 2.5 GB) or 2.5 h
on ayr (32 cores, 8 GB). The tool checkpoints every (H, N, prime) sweep, so a
killed run resumes at the cost of one sweep. If it is run:
`experiments/anisotropic_dfinite.py` asserts the validated height set is 1..10
and its expected-degree table stops at H=10, so a validated H=11 breaks that
gate (run from `paper/verify_claims.py`) until `deg psi_11` is added.

```
git show 91bdcdc^:gf/modp_recover.py > experiments/modp_recover.py
POLY_MAX_WORKERS=10 python3 experiments/modp_recover.py 11 11 194 <outfile>
```
